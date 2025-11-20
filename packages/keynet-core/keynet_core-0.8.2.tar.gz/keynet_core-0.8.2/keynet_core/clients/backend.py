"""Backend API 클라이언트 기본 클래스."""

import httpx


# 에러 클래스 계층 구조
class BackendAPIError(Exception):
    """Backend API 에러 베이스 클래스."""

    pass


class AuthenticationError(BackendAPIError):
    """인증 실패 (401/403)."""

    pass


class ValidationError(BackendAPIError):
    """검증 실패 (400/422)."""

    pass


class NetworkError(BackendAPIError):
    """네트워크 연결 실패."""

    pass


class ServerError(BackendAPIError):
    """서버 에러 (5xx)."""

    pass


class BaseBackendClient:
    """
    Backend API 클라이언트 기본 클래스.

    HTTP 클라이언트 초기화, 인증, 에러 처리 등 공통 기능을 제공합니다.
    도메인별 엔드포인트는 하위 클래스에서 구현합니다.

    Examples:
        >>> class MyBackendClient(BaseBackendClient):
        ...     def get_data(self):
        ...         response = self._request("GET", "/api/data")
        ...         return response.json()
        ...
        >>> with MyBackendClient("https://api.example.com", "api-key") as client:
        ...     data = client.get_data()

    """

    def __init__(self, base_url: str, api_key: str, timeout: float = 30.0):
        """
        BaseBackendClient 초기화.

        Args:
            base_url: Backend API URL
            api_key: API 인증 키
            timeout: HTTP 요청 타임아웃 (초)

        """
        self.base_url = base_url
        self.api_key = api_key
        self._client = httpx.Client(
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=httpx.Timeout(timeout),
        )

    def close(self):
        """HTTP 클라이언트 종료."""
        self._client.close()

    def __enter__(self):
        """Context manager 진입."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료."""
        self.close()

    def _request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """
        공통 HTTP 요청 래퍼.

        Args:
            method: HTTP 메서드 (GET, POST 등)
            endpoint: API 엔드포인트 경로
            **kwargs: httpx.Client.request()에 전달할 추가 인자

        Returns:
            httpx.Response: HTTP 응답 객체

        Raises:
            AuthenticationError: 401/403 응답
            ValidationError: 400/422 응답
            ServerError: 5xx 응답
            NetworkError: 네트워크 연결 실패

        """
        try:
            response = self._client.request(
                method, f"{self.base_url}{endpoint}", **kwargs
            )
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e)
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}")

    def _handle_http_error(self, error: httpx.HTTPStatusError) -> None:
        """
        HTTP 에러를 적절한 예외로 변환.

        Args:
            error: httpx.HTTPStatusError

        Raises:
            AuthenticationError: 401/403 응답
            ValidationError: 400/422 응답
            ServerError: 5xx 응답
            BackendAPIError: 기타 HTTP 에러

        """
        status_code = error.response.status_code

        if status_code in (401, 403):
            raise AuthenticationError(f"Authentication failed: {status_code}")
        elif status_code in (400, 422):
            raise ValidationError(f"Validation failed: {status_code}")
        elif 500 <= status_code < 600:
            raise ServerError(f"Server error: {status_code}")
        else:
            raise BackendAPIError(f"API error: {status_code}")
