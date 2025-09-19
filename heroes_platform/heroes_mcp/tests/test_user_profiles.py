#!/usr/bin/env python3
"""
Unit tests for user profiles system

TDD Documentation Standard v2.5 Compliance:
- Atomic Functions Architecture (≤20 строк на функцию)
- Security First (валидация всех входных данных)
- Modern Python Development (type hints, dataclasses)
- Testing Pyramid Compliance (unit, integration, e2e)
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.credentials_manager import CredentialResult, CredentialsManager


class TestUserProfiles:
    """Test user profiles functionality"""

    def test_profile_detection_from_env(self):
        """Test profile detection from HEROES_PROFILE environment variable"""
        with patch.dict(os.environ, {"HEROES_PROFILE": "lisa"}):
            manager = CredentialsManager()
            assert manager.get_current_profile() == "lisa"

    def test_profile_detection_from_user(self):
        """Test profile detection from USER environment variable"""
        with patch.dict(os.environ, {"USER": "ilyakrasinsky"}):
            manager = CredentialsManager()
            assert manager.get_current_profile() == "ik"

    def test_profile_switching(self):
        """Test manual profile switching"""
        manager = CredentialsManager()
        original_profile = manager.get_current_profile()

        # Switch to lisa
        manager.set_profile("lisa")
        assert manager.get_current_profile() == "lisa"

        # Switch back
        manager.set_profile("ik")
        assert manager.get_current_profile() == "ik"

    def test_invalid_profile_raises_error(self):
        """Test that invalid profile raises ValueError"""
        manager = CredentialsManager()
        with pytest.raises(ValueError, match="Unknown profile: invalid"):
            manager.set_profile("invalid")

    @patch("subprocess.run")
    def test_ik_profile_keychain_access(self, mock_run):
        """Test ik profile uses correct keychain command"""
        mock_run.return_value = MagicMock(returncode=0, stdout="test_value")

        manager = CredentialsManager()
        manager.set_profile("ik")

        result = manager.get_credential("telegram_api_id")

        # Verify correct command was called (first call should be keychain access)
        assert mock_run.call_count >= 1
        first_call_args = mock_run.call_args_list[0][0][0]
        assert '-l "ik_tg_api_id"' in first_call_args

    @patch("subprocess.run")
    def test_lisa_profile_keychain_access(self, mock_run):
        """Test lisa profile uses correct keychain command"""
        mock_run.return_value = MagicMock(returncode=0, stdout="test_value")

        manager = CredentialsManager()
        manager.set_profile("lisa")

        result = manager.get_credential("telegram_api_id")

        # Verify correct command was called (first call should be keychain access)
        assert mock_run.call_count >= 1
        first_call_args = mock_run.call_args_list[0][0][0]
        assert '-s "lisa_tg_api_key"' in first_call_args
        assert '-a "lisa"' in first_call_args

    def test_cache_clearing_on_profile_switch(self):
        """Test that cache is cleared when switching profiles"""
        manager = CredentialsManager()

        # Add something to cache
        manager._cache["test"] = CredentialResult(success=True, value="test")
        assert "test" in manager._cache

        # Switch profile
        manager.set_profile("lisa")

        # Cache should be cleared
        assert "test" not in manager._cache


if __name__ == "__main__":
    pytest.main([__file__])
