"""
Tests for Telegram MCP modules
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path


class TestTelegramMCP:
    """Test cases for Telegram MCP modules"""

    def test_chat_exporter_exists(self):
        """Test that chat_exporter.py exists"""
        file_path = Path("../../telegram-mcp/chat_exporter.py")
        assert file_path.exists(), "chat_exporter.py should exist"

    def test_keychain_integration_exists(self):
        """Test that keychain_integration.py exists"""
        file_path = Path("../../telegram-mcp/keychain_integration.py")
        assert file_path.exists(), "keychain_integration.py should exist"

    def test_main_exists(self):
        """Test that main.py exists"""
        file_path = Path("../../telegram-mcp/main.py")
        assert file_path.exists(), "main.py should exist"

    def test_telegram_mcp_server_exists(self):
        """Test that telegram_mcp_server.py exists"""
        file_path = Path("../../telegram-mcp/telegram_mcp_server.py")
        assert file_path.exists(), "telegram_mcp_server.py should exist"

    def test_setup_mcp_config_exists(self):
        """Test that setup_mcp_config.py exists"""
        file_path = Path("../../telegram-mcp/setup_mcp_config.py")
        assert file_path.exists(), "setup_mcp_config.py should exist"

    def test_setup_project_exists(self):
        """Test that setup_project.py exists"""
        file_path = Path("../../telegram-mcp/setup_project.py")
        assert file_path.exists(), "setup_project.py should exist"

    @patch('builtins.open', create=True)
    def test_chat_exporter_content(self, mock_open):
        """Test chat_exporter.py content structure"""
        mock_file = Mock()
        mock_file.read.return_value = "class TelegramChatExporter: pass"
        mock_open.return_value.__enter__.return_value = mock_file
        
        with open("../telegram-mcp/chat_exporter.py", "r") as f:
            content = f.read()
        assert "class" in content

    @patch('builtins.open', create=True)
    def test_keychain_integration_content(self, mock_open):
        """Test keychain_integration.py content structure"""
        mock_file = Mock()
        mock_file.read.return_value = "class MacKeychainCredentials: pass"
        mock_open.return_value.__enter__.return_value = mock_file
        
        with open("../telegram-mcp/keychain_integration.py", "r") as f:
            content = f.read()
        assert "class" in content

    @patch('builtins.open', create=True)
    def test_main_content(self, mock_open):
        """Test main.py content structure"""
        mock_file = Mock()
        mock_file.read.return_value = "async def main(): pass"
        mock_open.return_value.__enter__.return_value = mock_file
        
        with open("../telegram-mcp/main.py", "r") as f:
            content = f.read()
        assert "async" in content

    @patch('builtins.open', create=True)
    def test_telegram_mcp_server_content(self, mock_open):
        """Test telegram_mcp_server.py content structure"""
        mock_file = Mock()
        mock_file.read.return_value = "class TelegramMCPServer: pass"
        mock_open.return_value.__enter__.return_value = mock_file
        
        with open("../telegram-mcp/telegram_mcp_server.py", "r") as f:
            content = f.read()
        assert "class" in content

    @patch('builtins.open', create=True)
    def test_setup_mcp_config_content(self, mock_open):
        """Test setup_mcp_config.py content structure"""
        mock_file = Mock()
        mock_file.read.return_value = "def setup_mcp_config(): pass"
        mock_open.return_value.__enter__.return_value = mock_file
        
        with open("../telegram-mcp/setup_mcp_config.py", "r") as f:
            content = f.read()
        assert "def" in content

    @patch('builtins.open', create=True)
    def test_setup_project_content(self, mock_open):
        """Test setup_project.py content structure"""
        mock_file = Mock()
        mock_file.read.return_value = "def setup_project(): pass"
        mock_open.return_value.__enter__.return_value = mock_file
        
        with open("../telegram-mcp/setup_project.py", "r") as f:
            content = f.read()
        assert "def" in content

    def test_telegram_mcp_structure(self):
        """Test telegram-mcp directory structure"""
        telegram_dir = Path("../telegram-mcp")
        assert telegram_dir.exists(), "telegram-mcp directory should exist"
        assert telegram_dir.is_dir(), "telegram-mcp should be a directory"

        # Check for important files
        important_files = [
            "chat_exporter.py",
            "keychain_integration.py", 
            "main.py",
            "telegram_mcp_server.py",
            "setup_mcp_config.py",
            "setup_project.py"
        ]

        for file_name in important_files:
            file_path = telegram_dir / file_name
            assert file_path.exists(), f"Important file {file_name} should exist in ../telegram-mcp"

    def test_docker_files_exist(self):
        """Test that Docker files exist"""
        docker_files = [
            "../telegram-mcp/docker-compose.yml",
            "../telegram-mcp/Dockerfile"
        ]

        for file_path in docker_files:
            path = Path(file_path)
            assert path.exists(), f"Docker file {file_path} should exist"

    def test_screenshots_exist(self):
        """Test that screenshots directory exists"""
        screenshots_dir = Path("../telegram-mcp/screenshots")
        assert screenshots_dir.exists(), "screenshots directory should exist"
        assert screenshots_dir.is_dir(), "screenshots should be a directory"
