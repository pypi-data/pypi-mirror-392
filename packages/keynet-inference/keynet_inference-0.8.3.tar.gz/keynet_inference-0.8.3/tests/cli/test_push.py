"""Inference push 명령어 테스트."""

import tempfile
from unittest.mock import MagicMock, patch

from keynet_inference.cli.commands.push import handle_push
from keynet_inference.clients.models import DockerCommand, RuntimeUploadKeyResponse


def test_push_validates_python_syntax():
    """push는 먼저 Python 구문을 검증해야 함."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("def broken(\n")  # 잘못된 구문
        f.flush()

        args = MagicMock()
        args.file = f.name
        args.requirements = None
        args.base_image = None

        result = handle_push(args)

        assert result == 1  # 실패해야 함


def test_push_requires_keynet_function_decorator():
    """push는 @keynet_function 데코레이터를 요구해야 함."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("def main(args):\n    pass\n")  # 데코레이터 없음
        f.flush()

        args = MagicMock()
        args.file = f.name
        args.requirements = None
        args.base_image = None

        result = handle_push(args)

        assert result == 1  # 실패해야 함


def test_push_extracts_function_name():
    """push는 데코레이터에서 함수 이름을 추출해야 함."""
    code = """
from keynet_inference import keynet_function

@keynet_function(name="my_function", description="Test my_function")
def main(args):
    return "result"
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()

        args = MagicMock()
        args.file = f.name
        args.requirements = None
        args.base_image = None
        args.context = "."
        args.dockerfile = None
        args.no_cache = False
        args.platform = None

        with patch(
            "keynet_inference.cli.commands.push.InferenceDockerClient"
        ) as mock_docker:
            with patch(
                "keynet_inference.cli.commands.push.InferenceBackendClient"
            ) as mock_backend:
                with patch(
                    "keynet_inference.cli.commands.push.ConfigManager"
                ) as mock_config:
                    mock_config.return_value.get_server_url.return_value = (
                        "https://api.test.com"
                    )
                    mock_config.return_value.get_api_token.return_value = "test-token"
                    mock_config.return_value.get_username.return_value = "testuser"
                    mock_config.return_value.get_harbor_credentials.return_value = {
                        "url": "harbor.test.com",
                        "username": "user",
                        "password": "pass",
                    }

                    # 백엔드 응답 모킹
                    mock_backend.return_value.request_runtime_upload.return_value = RuntimeUploadKeyResponse(
                        id=1,
                        uploadKey="test-upload-key-123",
                        command=DockerCommand(
                            tag="docker tag <IMAGE> harbor.test.com/project/runtime:tag",
                            push="docker push harbor.test.com/project/runtime:tag",
                        ),
                    )

                    # Docker 빌드 모킹
                    mock_docker.return_value.build_runtime_image.return_value = (
                        "sha256:abc123"
                    )
                    mock_docker.return_value.tag_image.return_value = (
                        "harbor.test.com/project/runtime:tag"
                    )
                    mock_docker.return_value.push_image.return_value = None
                    mock_docker.return_value.login_to_registry.return_value = None

                    result = handle_push(args)

                    # 성공해야 함
                    assert result == 0
                    # build_runtime_image가 호출되었는지 확인
                    assert mock_docker.return_value.build_runtime_image.called


def test_push_base_image_priority_cli_first():
    """Base image 우선순위: CLI argument가 최우선."""
    code = """
from keynet_inference import keynet_function

@keynet_function(
    name="my_function",
    description="Test my_function",
    base_image="openwhisk/action-python-v3.10:latest"
)
def main(args):
    return "result"
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()

        args = MagicMock()
        args.file = f.name
        args.requirements = None
        args.base_image = "openwhisk/action-python-v3.12:latest"  # CLI arg
        args.context = "."
        args.dockerfile = None
        args.no_cache = False
        args.platform = None

        with patch(
            "keynet_inference.cli.commands.push.InferenceDockerClient"
        ) as mock_docker:
            with patch(
                "keynet_inference.cli.commands.push.InferenceBackendClient"
            ) as mock_backend:
                with patch(
                    "keynet_inference.cli.commands.push.ConfigManager"
                ) as mock_config:
                    mock_config.return_value.get_server_url.return_value = (
                        "https://api.test.com"
                    )
                    mock_config.return_value.get_api_token.return_value = "test-token"
                    mock_config.return_value.get_username.return_value = "testuser"
                    mock_config.return_value.get_harbor_credentials.return_value = {
                        "url": "harbor.test.com",
                        "username": "user",
                        "password": "pass",
                    }

                    mock_backend.return_value.request_runtime_upload.return_value = RuntimeUploadKeyResponse(
                        id=1,
                        uploadKey="test-upload-key-123",
                        command=DockerCommand(
                            tag="docker tag <IMAGE> harbor.test.com/project/runtime:tag",
                            push="docker push harbor.test.com/project/runtime:tag",
                        ),
                    )

                    # Docker 빌드 모킹
                    mock_docker.return_value.build_runtime_image.return_value = (
                        "sha256:abc123"
                    )
                    mock_docker.return_value.tag_image.return_value = (
                        "harbor.test.com/project/runtime:tag"
                    )
                    mock_docker.return_value.push_image.return_value = None
                    mock_docker.return_value.login_to_registry.return_value = None

                    result = handle_push(args)

                    # 성공해야 함
                    assert result == 0

                    # CLI base_image가 우선되어야 함
                    call_kwargs = (
                        mock_docker.return_value.build_runtime_image.call_args.kwargs
                    )
                    assert (
                        call_kwargs["base_image"]
                        == "openwhisk/action-python-v3.12:latest"
                    )
