"""ConfigManager 테스트."""

import tempfile
from pathlib import Path

from keynet_core.config import ConfigManager


def test_config_manager_default_path():
    """ConfigManager는 기본 경로를 사용."""
    manager = ConfigManager()

    # XDG 또는 ~/.config/keynet/config.json
    assert manager.config_path.name == "config.json"
    assert "keynet" in str(manager.config_path)


def test_config_manager_custom_path():
    """ConfigManager는 커스텀 경로를 지원."""
    with tempfile.TemporaryDirectory() as tmpdir:
        custom_path = Path(tmpdir) / "custom_config.json"
        manager = ConfigManager(config_path=str(custom_path))

        assert manager.config_path == custom_path


def test_save_and_load_credentials():
    """자격증명 저장 및 로드."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.json"
        manager = ConfigManager(config_path=str(config_path))

        # 자격증명 저장
        manager.save_credentials(
            server_url="https://api.test.com",
            username="testuser",
            api_token="test-token-12345",
            api_token_expires_at="2025-12-31T23:59:59Z",
            harbor={
                "url": "harbor.test.com",
                "username": "harbor_user",
                "password": "harbor_pass",
            },
        )

        # 파일 생성 확인
        assert config_path.exists()

        # 로드 확인
        assert manager.get_server_url() == "https://api.test.com"
        assert manager.get_username() == "testuser"
        assert manager.get_api_token() == "test-token-12345"

        harbor_creds = manager.get_harbor_credentials()
        assert harbor_creds["url"] == "harbor.test.com"
        assert harbor_creds["username"] == "harbor_user"
        assert harbor_creds["password"] == "harbor_pass"


def test_show_config_redacts_secrets():
    """show_config는 민감한 정보를 마스킹."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.json"
        manager = ConfigManager(config_path=str(config_path))

        manager.save_credentials(
            server_url="https://api.test.com",
            username="testuser",
            api_token="very-long-secret-token-12345678",
            api_token_expires_at="2025-12-31T23:59:59Z",
            harbor={
                "url": "harbor.test.com",
                "username": "harbor_user",
                "password": "very-long-harbor-password-abcdef",
            },
        )

        display_config = manager.show_config()

        # API token 마스킹 확인
        assert "..." in display_config["api_token"]
        assert "very-long-secret-token-12345678" not in display_config["api_token"]

        # Harbor password 마스킹 확인
        assert "..." in display_config["harbor"]["password"]
        assert (
            "very-long-harbor-password-abcdef"
            not in display_config["harbor"]["password"]
        )


def test_config_file_permissions():
    """설정 파일은 600 권한으로 저장."""
    import stat

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.json"
        manager = ConfigManager(config_path=str(config_path))

        manager.save_credentials(
            server_url="https://api.test.com",
            username="testuser",
            api_token="test-token",
            api_token_expires_at="2025-12-31T23:59:59Z",
            harbor={"url": "harbor.test.com", "username": "user", "password": "pass"},
        )

        # 파일 권한 확인 (600 = owner read/write only)
        file_stat = config_path.stat()
        permissions = file_stat.st_mode & 0o777

        # 600 권한 확인
        assert permissions == stat.S_IRUSR | stat.S_IWUSR
