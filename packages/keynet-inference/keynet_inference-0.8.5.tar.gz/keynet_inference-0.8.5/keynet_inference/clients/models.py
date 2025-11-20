"""Inference Backend API 응답 모델."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RuntimeUploadKeyRequest(BaseModel):
    """
    Runtime 업로드 키 요청 모델.

    커스텀 런타임 이미지를 Harbor에 푸시하기 위한 업로드 키를 요청합니다.

    Example:
        {
            "runtimeName": "my-custom-runtime"
        }

    """

    model_config = ConfigDict(populate_by_name=True)

    runtime_name: str = Field(alias="runtimeName")


class DockerCommand(BaseModel):
    """
    Docker 명령어 모델.

    Example:
        {
            "tag": "docker tag <IMAGE> harbor.example.com/project/runtime:tag",
            "push": "docker push harbor.example.com/project/runtime:tag"
        }

    """

    model_config = ConfigDict(populate_by_name=True)

    tag: str
    push: str


class RuntimeUploadKeyResponse(BaseModel):
    """
    Runtime 업로드 키 API 응답 모델.

    OpenWhisk 런타임 이미지를 Harbor 레지스트리에 푸시하기 위한
    업로드 키와 Docker 명령어를 포함합니다.

    Example:
        {
            "id": 196,
            "uploadKey": "unique-key-123",
            "command": {
                "tag": "docker tag <IMAGE> harbor.example.com/project/runtime:tag",
                "push": "docker push harbor.example.com/project/runtime:tag"
            }
        }

    """

    model_config = ConfigDict(populate_by_name=True)

    id: int
    upload_key: str = Field(alias="uploadKey")
    command: DockerCommand

    @property
    def tag_command(self) -> str:
        """Backward compatibility: tagCommand 속성."""
        return self.command.tag

    @property
    def push_command(self) -> str:
        """Backward compatibility: pushCommand 속성."""
        return self.command.push

    def get_image_reference(self) -> str:
        """
        pushCommand에서 이미지 레퍼런스를 추출합니다.

        Returns:
            Full image reference (e.g., "harbor.example.com/runtime/abc123:latest")

        Example:
            >>> response.push_command
            'docker push harbor.example.com/runtime/abc123:latest'
            >>> response.get_image_reference()
            'harbor.example.com/runtime/abc123:latest'

        """
        # Remove "docker push " prefix
        return self.push_command.replace("docker push ", "").strip()

    def get_registry_credentials(self) -> tuple[str, str, str]:
        """
        레지스트리 URL과 인증 정보를 반환합니다.

        Returns:
            Tuple of (registry_url, username, password)
            - registry_url: Harbor 레지스트리 URL (e.g., "harbor.example.com")
            - username: uploadKey (Harbor에서 uploadKey를 username으로 사용)
            - password: uploadKey (Harbor에서 uploadKey를 password로도 사용)

        Example:
            >>> response.get_registry_credentials()
            ('harbor.aiplatform.re.kr', 'xyz789', 'xyz789')

        """
        image_ref = self.get_image_reference()
        # Extract registry URL (everything before the first '/')
        registry_url = image_ref.split("/")[0]
        return registry_url, self.upload_key, self.upload_key


class UploadCodeResponse(BaseModel):
    r"""
    함수 코드 업로드 API 응답 모델.

    /v1/actions/code에 함수 파일 업로드 후 백엔드가 반환하는
    등록된 코드와 ID를 담고 있습니다.

    Example:
        {
            "id": 216,
            "code": "from keynet_inference import keynet_function\n\n@keynet_function...",
            "fileName": "inference.py"
        }

    """

    model_config = ConfigDict(populate_by_name=True)

    id: int
    code: str
    file_name: str = Field(alias="fileName")


class CreateFunctionRequest(BaseModel):
    """
    함수 생성 API 요청 모델.

    업로드된 코드와 런타임 이미지를 사용하여 백엔드에 함수 엔티티를
    생성하기 위한 POST /v1/actions/cli 요청 바디.

    Example:
        {
            "lambdaId": 216,
            "displayName": "crane-inference",
            "description": "RTMDET 기반 크레인 객체 탐지",
            "kind": "BlackBox",
            "parameters": {},
            "uploadKey": "unique-key-123"
        }

    """

    model_config = ConfigDict(populate_by_name=True)

    lambda_id: int = Field(alias="lambdaId")
    display_name: str = Field(alias="displayName")
    description: str
    kind: str = "BlackBox"  # 고정값
    parameters: dict = Field(default_factory=dict)  # 빈 딕셔너리
    upload_key: str = Field(alias="uploadKey")


class CreateFunctionResponse(BaseModel):
    """
    함수 생성 API 응답 모델.

    백엔드에서 함수 엔티티를 성공적으로 생성한 후
    POST /v1/actions/cli의 응답.

    Example:
        {
            "id": 123,
            "displayName": "crane-inference",
            "createdBy": "uuid-string",
            "lambdaId": 216,
            "code": "function code..."
        }

    """

    model_config = ConfigDict(populate_by_name=True)

    id: int
    display_name: str = Field(alias="displayName")
    created_by: UUID = Field(alias="createdBy")
    lambda_id: int = Field(alias="lambdaId")
    code: str
