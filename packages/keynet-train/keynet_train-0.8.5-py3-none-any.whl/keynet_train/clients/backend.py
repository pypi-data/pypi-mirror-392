"""훈련용 Backend API Client (BaseBackendClient 상속)."""

from keynet_core.clients import (
    AuthenticationError,
    BackendAPIError,
    BaseBackendClient,
    NetworkError,
    ServerError,
    ValidationError,
)
from keynet_train.clients.models import (
    FetchTrainableProjectsResponse,
    UploadKeyRequest,
    UploadKeyResponse,
)

# Re-export 에러 클래스 (backward compatibility)
__all__ = [
    "BackendClient",
    "BackendAPIError",
    "AuthenticationError",
    "ValidationError",
    "NetworkError",
    "ServerError",
]


class BackendClient(BaseBackendClient):
    """
    훈련용 Backend API 클라이언트.

    BaseBackendClient를 상속하여 훈련 전용 엔드포인트 추가.
    """

    def fetch_trainable_projects(
        self, page: int = 0, limit: int = 20
    ) -> FetchTrainableProjectsResponse:
        """
        훈련 가능한 프로젝트 목록 조회.

        Args:
            page: 페이지 번호 (0부터 시작)
            limit: 페이지당 항목 수

        Returns:
            FetchTrainableProjectsResponse: 프로젝트 목록과 페이지네이션 정보

        Raises:
            NetworkError: 네트워크 연결 실패
            AuthenticationError: 인증 실패
            ServerError: 서버 에러

        """
        response = self._request(
            "GET", "/v1/projects/trainable", params={"page": page, "limit": limit}
        )
        return FetchTrainableProjectsResponse(**response.json())

    def request_upload_key(
        self, project_id: int, request: UploadKeyRequest
    ) -> UploadKeyResponse:
        """
        훈련 이미지 업로드 키 발급 요청.

        Args:
            project_id: 프로젝트 ID
            request: UploadKey 요청 정보 (모델명, 하이퍼파라미터)

        Returns:
            UploadKeyResponse: 업로드 키 및 명령어 정보

        Raises:
            NetworkError: 네트워크 연결 실패
            AuthenticationError: 인증 실패
            ValidationError: 요청 검증 실패
            ServerError: 서버 에러

        """
        response = self._request(
            "POST",
            f"/v1/projects/{project_id}/trains/images",
            json=request.model_dump(by_alias=True),
        )
        return UploadKeyResponse(**response.json())
