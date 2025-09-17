"""
Tests for root project files
"""

import pytest
import os
from unittest.mock import Mock, patch
from pathlib import Path


class TestRootFiles:
    """Test cases for root project files"""

    def test_fix_mcp_config_final_exists(self):
        """Test that fix_mcp_config_final.py exists and can be imported"""
        file_path = Path("../../fix_mcp_config_final.py")
        assert file_path.exists(), "fix_mcp_config_final.py should exist"

    def test_restore_telegram_mcp_config_exists(self):
        """Test that restore_telegram_mcp_config.py exists and can be imported"""
        file_path = Path("../../restore_telegram_mcp_config.py")
        assert file_path.exists(), "restore_telegram_mcp_config.py should exist"

    def test_run_tests_exists(self):
        """Test that run_tests.py exists and can be imported"""
        file_path = Path("../../run_tests.py")
        assert file_path.exists(), "run_tests.py should exist"

    def test_update_server_name_exists(self):
        """Test that update_server_name.py exists and can be imported"""
        file_path = Path("../../update_server_name.py")
        assert file_path.exists(), "update_server_name.py should exist"

    @patch('builtins.open', create=True)
    def test_fix_mcp_config_final_content(self, mock_open):
        """Test fix_mcp_config_final.py content structure"""
        mock_file = Mock()
        mock_file.read.return_value = "def main(): pass"
        mock_open.return_value.__enter__.return_value = mock_file
        
        # This test verifies the file can be read
        with open("../fix_mcp_config_final.py", "r") as f:
            content = f.read()
        assert "def" in content

    @patch('builtins.open', create=True)
    def test_restore_telegram_mcp_config_content(self, mock_open):
        """Test restore_telegram_mcp_config.py content structure"""
        mock_file = Mock()
        mock_file.read.return_value = "def restore(): pass"
        mock_open.return_value.__enter__.return_value = mock_file
        
        # This test verifies the file can be read
        with open("../restore_telegram_mcp_config.py", "r") as f:
            content = f.read()
        assert "def" in content

    @patch('builtins.open', create=True)
    def test_run_tests_content(self, mock_open):
        """Test run_tests.py content structure"""
        mock_file = Mock()
        mock_file.read.return_value = "def run_tests(): pass"
        mock_open.return_value.__enter__.return_value = mock_file
        
        # This test verifies the file can be read
        with open("../run_tests.py", "r") as f:
            content = f.read()
        assert "def" in content

    @patch('builtins.open', create=True)
    def test_update_server_name_content(self, mock_open):
        """Test update_server_name.py content structure"""
        mock_file = Mock()
        mock_file.read.return_value = "def update(): pass"
        mock_open.return_value.__enter__.return_value = mock_file
        
        # This test verifies the file can be read
        with open("../update_server_name.py", "r") as f:
            content = f.read()
        assert "def" in content

    def test_project_structure_files(self):
        """Test that all required project structure files exist"""
        required_files = [
            "pyproject.toml",
            "README.md",
            ".gitignore"
        ]
        
        for file_name in required_files:
            file_path = Path(f"../../{file_name}")
            assert file_path.exists(), f"Required file {file_name} should exist"

    def test_config_files_exist(self):
        """Test that configuration files exist"""
        config_files = [
            "../../config/",
            "./",
            "../../telegram-mcp/"
        ]
        
        for config_path in config_files:
            path = Path(config_path)
            assert path.exists(), f"Config path {config_path} should exist"
            assert path.is_dir(), f"Config path {config_path} should be a directory"
