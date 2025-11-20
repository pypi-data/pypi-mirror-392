"""RuntimeUploadKeyResponse 모델 테스트."""

from keynet_inference.clients.models import RuntimeUploadKeyResponse


def test_runtime_upload_key_response_basic():
    """RuntimeUploadKeyResponse 기본 필드 테스트."""
    data = {
        "uploadKey": "test-upload-key-123",
        "tagCommand": "docker tag <IMAGE> harbor.example.com/project/runtime:tag",
        "pushCommand": "docker push harbor.example.com/project/runtime:tag",
    }

    response = RuntimeUploadKeyResponse(**data)

    assert response.upload_key == "test-upload-key-123"
    assert (
        response.tag_command
        == "docker tag <IMAGE> harbor.example.com/project/runtime:tag"
    )
    assert response.push_command == "docker push harbor.example.com/project/runtime:tag"


def test_runtime_upload_key_response_camel_case_aliases():
    """CamelCase 필드명도 처리 가능."""
    data = {
        "uploadKey": "key123",
        "tagCommand": "docker tag test",
        "pushCommand": "docker push test",
    }

    response = RuntimeUploadKeyResponse(**data)

    # Python snake_case로 접근
    assert response.upload_key == "key123"
    assert response.tag_command == "docker tag test"
    assert response.push_command == "docker push test"


def test_get_image_reference():
    """get_image_reference()는 pushCommand에서 이미지 레퍼런스를 추출."""
    data = {
        "uploadKey": "abc123",
        "tagCommand": "docker tag <IMAGE> harbor.example.com/runtime/abc123:latest",
        "pushCommand": "docker push harbor.example.com/runtime/abc123:latest",
    }

    response = RuntimeUploadKeyResponse(**data)
    image_ref = response.get_image_reference()

    assert image_ref == "harbor.example.com/runtime/abc123:latest"


def test_get_registry_credentials():
    """get_registry_credentials()는 레지스트리 URL과 uploadKey 반환."""
    data = {
        "uploadKey": "xyz789",
        "tagCommand": "docker tag <IMAGE> harbor.aiplatform.re.kr/runtime/xyz789:v1",
        "pushCommand": "docker push harbor.aiplatform.re.kr/runtime/xyz789:v1",
    }

    response = RuntimeUploadKeyResponse(**data)
    registry_url, username, password = response.get_registry_credentials()

    assert registry_url == "harbor.aiplatform.re.kr"
    assert username == "xyz789"
    assert password == "xyz789"
