"""
Integration tests for Telegram integration in MCP server
"""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

# Add the correct path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

SERVER_PATH = (Path(__file__).parent.parent.parent / "src" / "mcp_server.py").resolve()


class TestTelegramIntegration:
    """Test Telegram integration functionality"""

    def test_telegram_get_credentials(self):
        """Test getting Telegram credentials from Mac Keychain"""
        # Mock the keychain commands
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = "test_api_id\ntest_api_id\ntest_api_id\n"
            mock_run.return_value.returncode = 0

            # Test the function
            from heroes_mcp.src.heroes_mcp_server import telegram_manager

            credentials = telegram_manager.get_credentials()

            # Should return credentials if all three values are provided
            assert credentials is not None
            assert isinstance(credentials, dict)
            assert "api_id" in credentials
            assert "api_hash" in credentials
            assert "session_string" in credentials

    def test_telegram_test_connection(self):
        """Test Telegram connection testing"""
        # Mock the credentials
        with patch("mcp_server.telegram_manager.get_credentials") as mock_creds:
            mock_creds.return_value = None

            # Test the function
            from heroes_mcp.src.heroes_mcp_server import telegram_test_connection

            result = telegram_test_connection()

            assert "No credentials available" in result

    def test_telegram_get_chats(self):
        """Test getting Telegram chats"""
        # Mock the credentials
        with patch("mcp_server.telegram_manager.get_credentials") as mock_creds:
            mock_creds.return_value = None

            # Test the function
            from heroes_mcp.src.heroes_mcp_server import telegram_get_chats

            result = telegram_get_chats()

            assert "No credentials available" in result

    def test_telegram_search_chats(self):
        """Test searching Telegram chats"""
        # Mock the credentials
        with patch("mcp_server.telegram_manager.get_credentials") as mock_creds:
            mock_creds.return_value = None

            # Test the function
            from heroes_mcp.src.heroes_mcp_server import telegram_search_chats

            result = telegram_search_chats("test")

            assert "No credentials available" in result

    def test_telegram_export_chat(self):
        """Test exporting chat messages"""
        # Mock the credentials
        with patch("mcp_server.telegram_manager.get_credentials") as mock_creds:
            mock_creds.return_value = None

            # Test the function
            from heroes_mcp.src.heroes_mcp_server import telegram_export_chat

            result = telegram_export_chat(12345)

            assert "No credentials available" in result


class TestTelegramKeychainManager:
    """Test Telegram Keychain Manager"""

    def test_keychain_command_success(self):
        """Test successful keychain command execution"""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = "test_value\n"
            mock_run.return_value.returncode = 0

            from heroes_mcp.src.heroes_mcp_server import TelegramKeychainManager

            manager = TelegramKeychainManager()
            result = manager._run_keychain_command("test command")

            assert result == "test_value"

    def test_keychain_command_failure(self):
        """Test failed keychain command execution"""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, "test command")

            from heroes_mcp.src.heroes_mcp_server import TelegramKeychainManager

            manager = TelegramKeychainManager()
            result = manager._run_keychain_command("test command")

            assert result == ""
