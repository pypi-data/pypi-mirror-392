"""OpenWhisk 런타임용 Docker 클라이언트 (BaseDockerClient 상속)."""

from typing import Optional

from keynet_core.clients import BaseDockerClient


class InferenceDockerClient(BaseDockerClient):
    """
    OpenWhisk 런타임용 Docker 클라이언트.

    BaseDockerClient를 상속하여 OpenWhisk 전용 Dockerfile 생성 로직 추가.
    """

    def _generate_dockerfile(self, entrypoint: str, base_image: str) -> str:
        """
        OpenWhisk 런타임용 Dockerfile 생성 (BaseDockerClient의 추상 메서드 구현).

        Args:
            entrypoint: 스크립트 파일명 (OpenWhisk 런타임에서는 사용 안 함)
            base_image: OpenWhisk base image (예: "openwhisk/action-python-v3.12:latest")

        Returns:
            Dockerfile 내용

        Note:
            OpenWhisk 런타임은 간단하게 FROM + pip install만 필요합니다.
            OS 패키지가 필요한 경우 --dockerfile로 커스텀 Dockerfile을 제공하세요.
            entrypoint 파라미터는 BaseDockerClient 인터페이스 호환성을 위해 존재하지만
            OpenWhisk 런타임에서는 사용하지 않습니다.

        """
        return f"""FROM {base_image}

# requirements.txt 복사 및 설치
COPY requirements.txt* ./
RUN if [ -f requirements.txt ]; then \\
    pip install --no-cache-dir -r requirements.txt; \\
    fi
"""

    def build_runtime_image(
        self,
        context_path: str,
        dockerfile_path: Optional[str] = None,
        base_image: str = "openwhisk/action-python-v3.12:latest",
        no_cache: bool = False,
        platform: Optional[str] = None,
    ) -> str:
        """
        OpenWhisk 런타임 이미지를 빌드합니다.

        Args:
            context_path: 빌드 컨텍스트 디렉토리 (requirements.txt 등 포함)
            dockerfile_path: 커스텀 Dockerfile 경로 (선택사항)
            base_image: OpenWhisk base image
            no_cache: 캐시 비활성화
            platform: 플랫폼 지정

        Returns:
            빌드된 이미지 ID

        """
        # 커스텀 Dockerfile이 주어지면 그것을 사용
        if dockerfile_path:
            return self.build_image(
                entrypoint="",  # 커스텀 Dockerfile 사용 시 entrypoint 무시됨
                context_path=context_path,
                dockerfile_path=dockerfile_path,
                no_cache=no_cache,
                platform=platform,
            )

        # 자동 생성 Dockerfile 사용
        return self.build_image(
            entrypoint="",  # OpenWhisk는 entrypoint 사용 안 함
            context_path=context_path,
            base_image=base_image,
            no_cache=no_cache,
            platform=platform,
        )
