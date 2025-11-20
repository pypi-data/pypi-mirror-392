"""Inference 백엔드 API 클라이언트 (BaseBackendClient 상속)."""

from pathlib import Path

from keynet_core.clients import BaseBackendClient
from keynet_inference.clients.models import (
    CreateFunctionRequest,
    CreateFunctionResponse,
    RuntimeUploadKeyResponse,
    UploadCodeResponse,
)


class InferenceBackendClient(BaseBackendClient):
    """
    Inference 백엔드 API 클라이언트.

    BaseBackendClient를 상속하여 OpenWhisk 런타임 업로드 엔드포인트 추가.
    """

    def request_runtime_upload(self, runtime_name: str) -> RuntimeUploadKeyResponse:
        """
        런타임 업로드를 위한 uploadKey 요청.

        Args:
            runtime_name: 커스텀 런타임 이름 (예: "object-detection-inference")

        Returns:
            RuntimeUploadKeyResponse: 업로드 키 및 명령어 정보

        Raises:
            AuthenticationError: 인증 실패
            NetworkError: 네트워크 연결 실패
            ServerError: 서버 에러

        """
        # Send request body with camelCase field name
        response = self._request(
            "POST", "/v1/actions/runtimes", json={"runtimeName": runtime_name}
        )
        return RuntimeUploadKeyResponse(**response.json())

    def upload_code(self, file_path: Path) -> UploadCodeResponse:
        """
        백엔드에 함수 코드 파일 업로드.

        Python 함수 파일을 multipart/form-data로
        POST /v1/actions/code 엔드포인트에 전송합니다.

        Args:
            file_path: Python 함수 파일 경로

        Returns:
            UploadCodeResponse (lambda ID, 코드 내용, 파일명 포함)

        Raises:
            AuthenticationError: 인증 실패 (401)
            ValidationError: 파일 형식 오류 (400)
            ServerError: 서버 에러 (500)
            NetworkError: 네트워크 연결 실패

        Example:
            >>> client.upload_code(Path("inference.py"))
            UploadCodeResponse(id=216, code="...", file_name="inference.py")

        """
        with file_path.open("rb") as f:
            files = {"code": (file_path.name, f, "text/x-python")}
            response = self._request("POST", "/v1/actions/code", files=files)

        # 백엔드는 201 Created 반환
        return UploadCodeResponse(**response.json())

    def create_function(self, request: CreateFunctionRequest) -> CreateFunctionResponse:
        """
        백엔드에 함수 엔티티 생성.

        업로드된 코드와 런타임 이미지를 사용하여 함수 엔티티를 생성하기 위해
        POST /v1/actions/cli에 함수 메타데이터를 전송합니다.

        Args:
            request: CreateFunctionRequest (lambdaId, displayName, description 등)

        Returns:
            CreateFunctionResponse (생성된 함수 세부정보 포함)

        Raises:
            AuthenticationError: 인증 실패 (401)
            ValidationError: 요청 데이터 검증 실패 (400, 422)
            ServerError: 서버 에러 (500)
            NetworkError: 네트워크 연결 실패

        Example:
            >>> request = CreateFunctionRequest(
            ...     lambda_id=216,
            ...     display_name="crane-inference",
            ...     description="RTMDET 탐지",
            ...     upload_key="abc123"
            ... )
            >>> client.create_function(request)
            CreateFunctionResponse(id=123, ...)

        """
        response = self._request(
            "POST", "/v1/actions/cli", json=request.model_dump(by_alias=True)
        )

        return CreateFunctionResponse(**response.json())
