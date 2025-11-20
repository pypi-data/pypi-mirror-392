"""
Command Line Interface for keynet-inference.

This module provides CLI commands for OpenWhisk function management.
"""

import argparse
import sys

# Use shared login/logout from keynet-core
from keynet_core.cli.commands import handle_login as _core_login
from keynet_core.cli.commands import handle_logout as _core_logout
from keynet_inference.cli.commands import setup_push_parser


def _setup_login_parser(subparsers: argparse._SubParsersAction) -> None:
    """Set up login parser with app-training path."""
    parser = subparsers.add_parser(
        "login",
        help="Login to keynet server",
        description="Authenticate with keynet server and store credentials",
    )
    parser.add_argument(
        "server_url",
        type=str,
        nargs="?",
        help="Server URL (e.g., https://api.example.com)",
    )
    parser.add_argument(
        "--username",
        type=str,
        help="Email address (will prompt if not provided)",
    )

    def handle_login_with_path(args: argparse.Namespace) -> int:
        """Wrapper to inject app-training path."""
        args.app_path = "app-training"
        return _core_login(args)

    parser.set_defaults(func=handle_login_with_path)


def _setup_logout_parser(subparsers: argparse._SubParsersAction) -> None:
    """Set up logout parser."""
    parser = subparsers.add_parser(
        "logout",
        help="Logout and clear credentials",
        description="Remove stored credentials from local configuration",
    )
    parser.set_defaults(func=_core_logout)


def main() -> int:
    """
    Main entry point for keynet-inference CLI.

    Returns:
        Exit code (0 for success, non-zero for error)

    """
    parser = argparse.ArgumentParser(
        prog="keynet-inference",
        description="Keynet Inference - OpenWhisk 런타임 관리 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
    # Keynet 서버 로그인
    keynet-inference login https://api.example.com

    # 함수 푸시 (OpenWhisk 런타임 빌드 및 Harbor 푸시)
    keynet-inference push function.py

    # requirements.txt 지정
    keynet-inference push function.py --requirements requirements.txt

    # Base image 지정
    keynet-inference push function.py --base-image openwhisk/action-python-v3.11:latest

    # 로그아웃
    keynet-inference logout

자세한 정보:
    각 명령어의 자세한 사용법은 다음과 같이 확인하세요:
    keynet-inference <command> --help
        """,
    )

    # Create subparsers
    subparsers = parser.add_subparsers(
        dest="command",
        help="사용 가능한 명령어",
        required=False,
    )

    # Setup command parsers
    _setup_login_parser(subparsers)
    _setup_logout_parser(subparsers)
    setup_push_parser(subparsers)

    # Parse arguments
    args = parser.parse_args()

    # Execute command
    if not args.command:
        parser.print_help()
        return 0

    # All commands have .func attribute set by set_defaults()
    if hasattr(args, "func"):
        return args.func(args)

    # Should never reach here
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
