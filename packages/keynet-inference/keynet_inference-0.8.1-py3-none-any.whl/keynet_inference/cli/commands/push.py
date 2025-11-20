"""
Push command implementation for inference functions.

Validates Python functions decorated with @keynet_function,
builds OpenWhisk runtime Docker images, and pushes to Harbor registry.

Workflow:
1. Validate Python syntax
2. Extract function name from @keynet_function decorator
3. Determine base image priority (CLI > Decorator > Default)
4. Request uploadKey from Backend API (/v1/actions/runtimes)
5. Build OpenWhisk runtime Docker image
6. Tag and push to Harbor registry
"""

import argparse
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from keynet_core.config import ConfigManager
from keynet_core.parsing import extract_decorator_argument
from keynet_core.validation import PythonSyntaxValidator
from keynet_inference.clients import InferenceBackendClient, InferenceDockerClient
from keynet_inference.clients.models import CreateFunctionRequest

# Default base image (OpenWhisk Python 3.12)
DEFAULT_BASE_IMAGE = "openwhisk/action-python-v3.12:latest"


# Global console instance for rich output
console = Console()


def print_step(step: int, total: int, message: str) -> None:
    """
    Print a step header message with rich formatting.

    Args:
        step: Current step number
        total: Total number of steps
        message: Step description

    """
    console.print(
        f"\n[bold cyan]📋 Step {step}/{total}:[/bold cyan] {message}...",
        highlight=False,
    )


def print_success(message: str) -> None:
    """
    Print a success message with rich formatting.

    Args:
        message: Success message to display

    """
    console.print(f"[bold green]✅[/bold green] {message}", highlight=False)


def setup_push_parser(subparsers: argparse._SubParsersAction) -> None:
    """
    Set up the push command parser.

    Args:
        subparsers: Subparsers action from parent parser

    """
    parser = subparsers.add_parser(
        "push",
        help="Build and push inference function as OpenWhisk runtime Docker image",
        description="Validate, build, and deploy Python functions decorated with @keynet_function",
        epilog="""
Examples:
    # Basic push
    keynet-inference push function.py

    # Specify requirements.txt
    keynet-inference push function.py --requirements requirements.txt

    # Specify base image (highest priority)
    keynet-inference push function.py --base-image openwhisk/action-python-v3.11:latest

    # Specify build context
    keynet-inference push function.py --context ./build

    # Use custom Dockerfile
    keynet-inference push function.py --dockerfile Dockerfile.custom

Base Image Priority:
    1. CLI argument (--base-image) - highest priority
    2. @keynet_function decorator's base_image parameter
    3. Default: openwhisk/action-python-v3.12:latest

Notes:
    - Requires 'keynet-inference login' first
    - Function must have @keynet_function decorator
    - base_image must be OpenWhisk-compatible
        """,
    )

    parser.add_argument(
        "file",
        type=str,
        help="Path to Python file with @keynet_function decorator",
    )

    parser.add_argument(
        "--requirements",
        type=str,
        default=None,
        help="Path to requirements.txt (default: auto-detect)",
    )

    parser.add_argument(
        "--base-image",
        type=str,
        default=None,
        help=f"Docker base image (default: {DEFAULT_BASE_IMAGE}). OpenWhisk-compatible images recommended",
    )

    parser.add_argument(
        "--context",
        type=str,
        default=".",
        help="Build context directory (default: current directory)",
    )

    parser.add_argument(
        "--dockerfile",
        type=str,
        default=None,
        help="Custom Dockerfile path (optional, use when OS packages are needed)",
    )

    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable Docker build cache",
    )

    parser.add_argument(
        "--platform",
        type=str,
        default=None,
        help="Target platform (e.g., linux/amd64)",
    )

    parser.set_defaults(func=handle_push)


def handle_push(args: argparse.Namespace) -> int:
    """
    Handle push command execution.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 = success, 1 = error)

    """
    # Step 1: Check authentication
    print_step(1, 10, "Checking authentication")
    config_manager = ConfigManager()
    server_url = config_manager.get_server_url()
    api_token = config_manager.get_api_token()
    username = config_manager.get_username()

    if not server_url or not api_token:
        print("❌ Not logged in. Run: keynet-inference login <server-url>")
        return 1

    print_success(f"Authenticated: {username or 'unknown'}@{server_url}")

    # Step 2: Validate Python syntax
    print_step(2, 10, "Validating Python syntax")
    file_path = Path(args.file)

    if not file_path.exists():
        print(f"❌ File not found: {args.file}")
        return 1

    validator = PythonSyntaxValidator()
    success, error = validator.validate_file(file_path)

    if not success:
        print(f"❌ Validation failed:\n{error}")
        return 1

    print_success("Validation passed")

    # Step 3: Extract function metadata from @keynet_function decorator
    print_step(3, 10, "Extracting function metadata")

    # Extract name (positional or keyword argument)
    function_name = extract_decorator_argument(
        file_path=args.file,
        decorator_name="keynet_function",
        keyword_arg="name",
    )

    if not function_name:
        # Try positional argument (index 0)
        function_name = extract_decorator_argument(
            file_path=args.file,
            decorator_name="keynet_function",
            argument_index=0,
        )

    if not function_name:
        print(
            "❌ @keynet_function decorator not found or missing function name argument\n"
            "\n"
            "Add decorator to your main function:\n"
            "\n"
            "Example:\n"
            "  from keynet_inference import keynet_function\n"
            "\n"
            "  @keynet_function(name='my_function_name')\n"
            "  def main(args):\n"
            "      return result\n"
        )
        return 1

    print_success(f"Function name: {function_name}")

    # Extract description (required)
    description = extract_decorator_argument(
        file_path=args.file,
        decorator_name="keynet_function",
        keyword_arg="description",
    )

    if not description:
        print(
            "❌ @keynet_function decorator missing required 'description' parameter\n"
            "\n"
            "Example:\n"
            "  from keynet_inference import keynet_function\n"
            "\n"
            "  @keynet_function(\n"
            "      name='my_function_name',\n"
            "      description='Processes images with YOLO detection'\n"
            "  )\n"
            "  def main(args):\n"
            "      return result\n"
        )
        return 1

    print_success(f"Description: {description}")

    # Step 4: Determine base image priority
    print_step(4, 10, "Determining base image")

    # Priority 1: CLI argument
    base_image = args.base_image

    # Priority 2: Decorator's base_image
    if not base_image:
        decorator_base_image = extract_decorator_argument(
            file_path=args.file,
            decorator_name="keynet_function",
            keyword_arg="base_image",
        )
        if decorator_base_image:
            base_image = decorator_base_image
            print(f"   📦 Found base_image in decorator: {base_image}")
    else:
        print(f"   📦 Using CLI base_image: {base_image}")

    # Priority 3: Default
    if not base_image:
        base_image = DEFAULT_BASE_IMAGE
        print(f"   📦 Using default base_image: {base_image}")

    # OpenWhisk compatibility warning
    if not base_image.startswith("openwhisk/"):
        print(f"   ⚠️  Warning: '{base_image}' is not an official OpenWhisk image")
        print("   Non-OpenWhisk images may fail during deployment")

    # Step 5: Request upload key from backend API
    print_step(5, 10, "Requesting upload key")
    backend_client = InferenceBackendClient(server_url, api_token)

    try:
        upload_response = backend_client.request_runtime_upload()
        upload_key = upload_response.upload_key
        tag_command = upload_response.tag_command
        push_command = upload_response.push_command

        print_success(f"Upload key: {upload_key}")
        print(f"   Tag command: {tag_command}")
        print(f"   Push command: {push_command}")

    except Exception as e:
        print(f"❌ Backend API request failed: {e}")
        return 1

    # Step 6: Load Harbor credentials
    print_step(6, 10, "Verifying Harbor credentials")
    harbor_creds = config_manager.get_harbor_credentials()

    if not harbor_creds:
        print("❌ Harbor credentials not found. Run: keynet-inference login")
        return 1

    # Step 7: Build OpenWhisk runtime Docker image
    print_step(7, 10, "Building OpenWhisk runtime image")
    docker_client = InferenceDockerClient(harbor_config=harbor_creds)

    # Verify Harbor login
    if not docker_client.verify_harbor_credentials():
        print("❌ Harbor authentication failed. Check your credentials")
        return 1

    try:
        image_id = docker_client.build_runtime_image(
            context_path=args.context,
            dockerfile_path=args.dockerfile,
            base_image=base_image,
            no_cache=args.no_cache,
            platform=args.platform,
        )
        print_success(f"Built image: {image_id[:12]}")
    except Exception as e:
        print(f"❌ Build failed: {e}")
        return 1

    # Step 8: Tag and push image
    print_step(8, 10, "Tagging and pushing image")

    # Parse tag_command to extract project
    # tag_command example: "docker tag <IMAGE> harbor.example.com/project/runtime:tag"
    try:
        parts = tag_command.split()
        if len(parts) < 4:
            print(f"❌ Invalid tag command format: {tag_command}")
            return 1

        target_image = parts[3]  # "harbor.example.com/project/runtime:tag"
        # Extract project from "harbor.example.com/project/..."
        image_parts = target_image.split("/")
        if len(image_parts) < 2:
            print(f"❌ Cannot extract project from image path: {target_image}")
            return 1

        project = image_parts[1]  # "project"

        # Tag image (BaseDockerClient.tag_image signature: image_id, project, upload_key)
        tagged_image = docker_client.tag_image(
            image_id=image_id, project=project, upload_key=upload_key
        )
        print_success(f"Tagged: {tagged_image}")

        # Push image
        docker_client.push_image(tagged_image)
        print_success(f"Pushed: {tagged_image}")

    except Exception as e:
        print(f"❌ Tag/push failed: {e}")
        return 1

    # Step 9: Upload function code
    print_step(9, 10, "Uploading function code")

    try:
        upload_code_response = backend_client.upload_code(file_path)
        lambda_id = upload_code_response.id
        print_success(f"Code uploaded: Lambda ID {lambda_id}")
        print(f"   File: {upload_code_response.file_name}")
    except Exception as e:
        print(f"❌ Code upload failed: {e}")
        return 1

    # Step 10: Create function entity
    print_step(10, 10, "Creating function entity")

    try:
        create_request = CreateFunctionRequest(
            lambdaId=lambda_id,
            displayName=function_name,
            description=description,
            uploadKey=upload_key,
        )
        function_response = backend_client.create_function(create_request)
        function_id = function_response.id
        print_success(f"Function created: ID {function_id}")
        print(f"   Display name: {function_response.display_name}")
        print(f"   Kind: {function_response.kind}")
    except Exception as e:
        print(f"❌ Function creation failed: {e}")
        return 1

    # Display success summary with rich Panel
    console.print()  # Empty line

    summary_lines = [
        f"[bold]Function:[/bold] {function_name}",
        f"[bold]Description:[/bold] {description}",
        f"[bold]Base Image:[/bold] {base_image}",
        f"[bold]Image:[/bold] {tagged_image}",
        f"[bold]Upload Key:[/bold] {upload_key}",
        f"[bold]Lambda ID:[/bold] {lambda_id}",
        f"[bold]Function ID:[/bold] {function_id}",
    ]

    console.print(
        Panel.fit(
            "\n".join(summary_lines),
            title="[bold green]✨ Push Completed Successfully![/bold green]",
            border_style="green",
        )
    )

    return 0
