"""Train Docker Client - BaseDockerClient 상속"""

from pathlib import Path

from keynet_core.clients import (
    BaseDockerClient,
    BuildError,
    DockerError,
    ImageNotFoundError,
    PushError,
)

# Re-export error classes for backward compatibility
__all__ = [
    "TrainDockerClient",
    "DockerClient",
    "DockerError",
    "BuildError",
    "ImageNotFoundError",
    "PushError",
]


class TrainDockerClient(BaseDockerClient):
    """
    훈련 스크립트용 Docker 클라이언트.

    BaseDockerClient를 상속하여 훈련 전용 Dockerfile 생성 로직 추가.
    Harbor 레지스트리 연동, Rich UI, 상세 에러 처리는 BaseDockerClient에서 제공.
    """

    def _generate_dockerfile(self, entrypoint: str, base_image: str) -> str:
        """
        훈련 스크립트용 Dockerfile 생성.

        Args:
            entrypoint: 훈련 스크립트 파일명 (예: "train.py")
            base_image: Docker base image (예: "python:3.10-slim")

        Returns:
            Dockerfile 내용

        """
        entrypoint_name = Path(entrypoint).name

        return f"""FROM {base_image}
WORKDIR /workspace

# Copy entire build context
COPY . /workspace/

# Install dependencies if requirements.txt exists
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

# Set entrypoint
ENTRYPOINT ["python", "{entrypoint_name}"]
"""


# Backward compatibility
DockerClient = TrainDockerClient
