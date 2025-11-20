"""BaseBackendClient 테스트."""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from keynet_core.clients import (
    AuthenticationError,
    BackendAPIError,
    BaseBackendClient,
    NetworkError,
    ServerError,
    ValidationError,
)


# 테스트용 구체 클래스
class TestBackendClient(BaseBackendClient):
    """테스트용 BackendClient"""

    def custom_endpoint(self) -> dict:
        """테스트용 커스텀 엔드포인트"""
        response = self._request("GET", "/test/endpoint")
        return response.json()


def test_base_backend_client_initialization():
    """BaseBackendClient 초기화."""
    with patch("keynet_core.clients.backend.httpx.Client"):
        client = TestBackendClient(
            base_url="https://api.example.com", api_key="test-key"
        )

        assert client.base_url == "https://api.example.com"
        assert client.api_key == "test-key"


def test_context_manager():
    """Context manager로 사용 가능."""
    with patch("keynet_core.clients.backend.httpx.Client") as mock_httpx:
        mock_client = MagicMock()
        mock_httpx.return_value = mock_client

        with TestBackendClient(
            base_url="https://api.example.com", api_key="test-key"
        ) as client:
            assert client is not None

        # close() 호출 확인
        mock_client.close.assert_called_once()


def test_request_success():
    """성공적인 HTTP 요청."""
    with patch("keynet_core.clients.backend.httpx.Client") as mock_httpx:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": "test"}
        mock_client.request.return_value = mock_response
        mock_httpx.return_value = mock_client

        client = TestBackendClient(
            base_url="https://api.example.com", api_key="test-key"
        )
        result = client.custom_endpoint()

        assert result == {"data": "test"}
        mock_client.request.assert_called_once_with(
            "GET", "https://api.example.com/test/endpoint"
        )


def test_request_authentication_error():
    """401/403 응답 시 AuthenticationError 발생."""
    with patch("keynet_core.clients.backend.httpx.Client") as mock_httpx:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 401
        error = httpx.HTTPStatusError(
            "Unauthorized", request=MagicMock(), response=mock_response
        )
        mock_client.request.side_effect = error
        mock_httpx.return_value = mock_client

        client = TestBackendClient(
            base_url="https://api.example.com", api_key="test-key"
        )

        with pytest.raises(AuthenticationError):
            client.custom_endpoint()


def test_request_validation_error():
    """400/422 응답 시 ValidationError 발생."""
    with patch("keynet_core.clients.backend.httpx.Client") as mock_httpx:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 400
        error = httpx.HTTPStatusError(
            "Bad Request", request=MagicMock(), response=mock_response
        )
        mock_client.request.side_effect = error
        mock_httpx.return_value = mock_client

        client = TestBackendClient(
            base_url="https://api.example.com", api_key="test-key"
        )

        with pytest.raises(ValidationError):
            client.custom_endpoint()


def test_request_server_error():
    """5xx 응답 시 ServerError 발생."""
    with patch("keynet_core.clients.backend.httpx.Client") as mock_httpx:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 500
        error = httpx.HTTPStatusError(
            "Internal Server Error", request=MagicMock(), response=mock_response
        )
        mock_client.request.side_effect = error
        mock_httpx.return_value = mock_client

        client = TestBackendClient(
            base_url="https://api.example.com", api_key="test-key"
        )

        with pytest.raises(ServerError):
            client.custom_endpoint()


def test_request_network_error():
    """네트워크 에러 시 NetworkError 발생."""
    with patch("keynet_core.clients.backend.httpx.Client") as mock_httpx:
        mock_client = MagicMock()
        mock_client.request.side_effect = httpx.RequestError("Connection failed")
        mock_httpx.return_value = mock_client

        client = TestBackendClient(
            base_url="https://api.example.com", api_key="test-key"
        )

        with pytest.raises(NetworkError):
            client.custom_endpoint()


def test_error_hierarchy():
    """에러 클래스 계층 구조 확인."""
    # BackendAPIError -> Exception
    backend_error = BackendAPIError("test")
    assert isinstance(backend_error, BackendAPIError)
    assert isinstance(backend_error, Exception)

    # AuthenticationError -> BackendAPIError -> Exception
    auth_error = AuthenticationError("test")
    assert isinstance(auth_error, AuthenticationError)
    assert isinstance(auth_error, BackendAPIError)
    assert isinstance(auth_error, Exception)

    # ValidationError -> BackendAPIError -> Exception
    validation_error = ValidationError("test")
    assert isinstance(validation_error, ValidationError)
    assert isinstance(validation_error, BackendAPIError)
    assert isinstance(validation_error, Exception)

    # NetworkError -> BackendAPIError -> Exception
    network_error = NetworkError("test")
    assert isinstance(network_error, NetworkError)
    assert isinstance(network_error, BackendAPIError)
    assert isinstance(network_error, Exception)

    # ServerError -> BackendAPIError -> Exception
    server_error = ServerError("test")
    assert isinstance(server_error, ServerError)
    assert isinstance(server_error, BackendAPIError)
    assert isinstance(server_error, Exception)
