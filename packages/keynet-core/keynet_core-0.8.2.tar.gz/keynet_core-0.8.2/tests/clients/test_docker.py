"""BaseDockerClient 테스트."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from keynet_core.clients import (
    BaseDockerClient,
    BuildError,
    DockerError,
    ImageNotFoundError,
    PushError,
)


# 테스트용 구체 클래스
class TestDockerClient(BaseDockerClient):
    """테스트용 DockerClient"""

    def _generate_dockerfile(self, entrypoint: str, base_image: str) -> str:
        """테스트용 Dockerfile 생성"""
        entrypoint_name = Path(entrypoint).name
        return f"""FROM {base_image}
WORKDIR /workspace
COPY . /workspace/
ENTRYPOINT ["python", "{entrypoint_name}"]"""


def test_base_docker_client_initialization():
    """BaseDockerClient 초기화."""
    harbor_config = {
        "url": "harbor.example.com",
        "username": "testuser",
        "password": "testpass",
    }

    with patch("keynet_core.clients.docker.docker") as mock_docker:
        mock_docker.from_env.return_value = MagicMock()

        client = TestDockerClient(harbor_config)

        assert client._client is not None
        assert client._harbor_url == "harbor.example.com"
        assert client._username == "testuser"
        assert client._password == "testpass"
        mock_docker.from_env.assert_called_once()


def test_build_image():
    """이미지 빌드 (자동 Dockerfile 생성)."""
    harbor_config = {
        "url": "harbor.example.com",
        "username": "testuser",
        "password": "testpass",
    }

    with patch("keynet_core.clients.docker.docker") as mock_docker:
        mock_docker.from_env.return_value = MagicMock()
        client = TestDockerClient(harbor_config)

        # Mock build logs
        mock_build_logs = [
            {"stream": "Step 1/3 : FROM python:3.10"},
            {"aux": {"ID": "sha256:abcd1234"}},
        ]

        with patch.object(client._client, "api") as mock_api:
            mock_api.build.return_value = mock_build_logs

            with patch("keynet_core.clients.docker.Path") as mock_path_class:
                # Mock temp dockerfile path
                mock_temp_file = MagicMock()
                mock_temp_file.name = ".Dockerfile.keynet.tmp"
                mock_temp_file.exists.return_value = True
                mock_path_class.return_value = mock_temp_file

                image_id = client.build_image(
                    entrypoint="train.py",
                    context_path="/tmp/context",
                    base_image="python:3.10",
                )

                assert image_id == "sha256:abcd1234"


def test_tag_image():
    """이미지 태그 생성."""
    harbor_config = {
        "url": "harbor.example.com",
        "username": "testuser",
        "password": "testpass",
    }

    with patch("keynet_core.clients.docker.docker") as mock_docker:
        mock_docker.from_env.return_value = MagicMock()
        client = TestDockerClient(harbor_config)

        mock_image = MagicMock()
        client._client.images.get.return_value = mock_image

        tagged_image = client.tag_image(
            image_id="sha256:abcd1234", project="my-project", upload_key="my-model:v1.0"
        )

        assert tagged_image == "harbor.example.com/my-project/my-model:v1.0"
        mock_image.tag.assert_called_once()


def test_push_image():
    """이미지 푸시."""
    harbor_config = {
        "url": "harbor.example.com",
        "username": "testuser",
        "password": "testpass",
    }

    with patch("keynet_core.clients.docker.docker") as mock_docker:
        mock_docker.from_env.return_value = MagicMock()
        client = TestDockerClient(harbor_config)

        # Mock push stream
        mock_push_stream = [
            {"status": "Pushing", "id": "abc123", "progressDetail": {}},
            {"status": "Pushed", "id": "abc123"},
        ]
        client._client.images.push.return_value = mock_push_stream

        client.push_image("harbor.example.com/project/runtime:v1.0.0")

        # Verify push was called
        client._client.images.push.assert_called_once()


def test_verify_harbor_credentials():
    """Harbor 인증 확인."""
    harbor_config = {
        "url": "https://harbor.example.com/",
        "username": "testuser",
        "password": "testpass",
    }

    with patch("keynet_core.clients.docker.docker") as mock_docker:
        mock_client = MagicMock()
        mock_docker.from_env.return_value = mock_client
        client = TestDockerClient(harbor_config)

        result = client.verify_harbor_credentials()

        assert result is True
        mock_client.login.assert_called_once_with(
            username="testuser", password="testpass", registry="harbor.example.com"
        )


def test_is_available():
    """Docker 사용 가능 확인."""
    with patch("keynet_core.clients.docker.docker") as mock_docker:
        mock_client = MagicMock()
        mock_docker.from_env.return_value = mock_client

        result = TestDockerClient.is_available()

        assert result is True
        mock_docker.from_env.assert_called_once()
        mock_client.ping.assert_called_once()


def test_is_available_failure():
    """Docker가 사용 불가능한 경우."""
    with patch("keynet_core.clients.docker.docker") as mock_docker:
        # Docker 연결 실패
        mock_docker.from_env.side_effect = Exception("Connection failed")

        assert TestDockerClient.is_available() is False
        mock_docker.from_env.assert_called_once()


# 에러 클래스 계층 구조 테스트
def test_docker_error_inheritance():
    """DockerError가 Exception을 상속하는지 확인."""
    error = DockerError("test error")
    assert isinstance(error, Exception)
    assert str(error) == "test error"


def test_build_error_inheritance():
    """BuildError가 DockerError를 상속하는지 확인."""
    error = BuildError("build failed")
    assert isinstance(error, DockerError)
    assert isinstance(error, Exception)
    assert str(error) == "build failed"


def test_image_not_found_error_inheritance():
    """ImageNotFoundError가 DockerError를 상속하는지 확인."""
    error = ImageNotFoundError("image not found")
    assert isinstance(error, DockerError)
    assert isinstance(error, Exception)
    assert str(error) == "image not found"


def test_push_error_inheritance():
    """PushError가 DockerError를 상속하는지 확인."""
    error = PushError("push failed")
    assert isinstance(error, DockerError)
    assert isinstance(error, Exception)
    assert str(error) == "push failed"


def test_error_hierarchy():
    """에러 클래스 계층 구조 확인."""
    # BuildError -> DockerError -> Exception
    build_error = BuildError("test")
    assert isinstance(build_error, BuildError)
    assert isinstance(build_error, DockerError)
    assert isinstance(build_error, Exception)

    # ImageNotFoundError -> DockerError -> Exception
    image_error = ImageNotFoundError("test")
    assert isinstance(image_error, ImageNotFoundError)
    assert isinstance(image_error, DockerError)
    assert isinstance(image_error, Exception)

    # PushError -> DockerError -> Exception
    push_error = PushError("test")
    assert isinstance(push_error, PushError)
    assert isinstance(push_error, DockerError)
    assert isinstance(push_error, Exception)


def test_validate_harbor_config_empty():
    """Harbor 설정 검증: 빈 config."""
    with pytest.raises(ValueError, match="harbor_config"):
        TestDockerClient({})


def test_validate_harbor_config_missing_url():
    """Harbor 설정 검증: url 누락."""
    with pytest.raises(ValueError, match="url"):
        TestDockerClient({"username": "test", "password": "test"})


def test_validate_harbor_config_missing_username():
    """Harbor 설정 검증: username 누락."""
    with pytest.raises(ValueError, match="username"):
        TestDockerClient({"url": "test", "password": "test"})


def test_validate_harbor_config_missing_password():
    """Harbor 설정 검증: password 누락."""
    with pytest.raises(ValueError, match="password"):
        TestDockerClient({"url": "test", "username": "test"})


def test_verify_harbor_credentials_failure():
    """Harbor 인증 실패."""
    harbor_config = {
        "url": "https://harbor.example.com",
        "username": "testuser",
        "password": "wrong_password",
    }

    with patch("keynet_core.clients.docker.docker") as mock_docker:
        mock_client = MagicMock()
        mock_client.login.side_effect = Exception("Authentication failed")
        mock_docker.from_env.return_value = mock_client
        client = TestDockerClient(harbor_config)

        result = client.verify_harbor_credentials()

        assert result is False
