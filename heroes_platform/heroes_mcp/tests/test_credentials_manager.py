#!/usr/bin/env python3
"""
Tests for Credentials Manager
TDD Documentation Standard v2.5 Compliance

JTBD: Как QA инженер, я хочу тестировать CredentialsManager,
чтобы обеспечить надежность и безопасность управления секретами.

Testing Pyramid Compliance:
- Unit Tests: Изолированные функции
- Integration Tests: Взаимодействие компонентов
- E2E Tests: Полный workflow
"""

import pytest
import os
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Import the module to test
import sys

sys.path.append("src")
from shared.credentials_manager import (
    CredentialsManager,
    CredentialConfig,
    CredentialResult,
    get_credential,
    store_credential,
)


class TestCredentialConfig:
    """Unit tests for CredentialConfig dataclass"""

    def test_credential_config_creation(self):
        """Test CredentialConfig creation with all fields"""
        config = CredentialConfig(
            name="Test API Key",
            source="keychain",
            key="test_api_key",
            fallback_sources=["env", "file"],
            validation_rules={"type": "str", "min_length": 10},
        )

        assert config.name == "Test API Key"
        assert config.source == "keychain"
        assert config.key == "test_api_key"
        assert config.fallback_sources == ["env", "file"]
        assert config.validation_rules == {"type": "str", "min_length": 10}

    def test_credential_config_defaults(self):
        """Test CredentialConfig creation with defaults"""
        config = CredentialConfig(name="Test API Key", source="env", key="test_key")

        assert config.fallback_sources is None
        assert config.validation_rules is None


class TestCredentialResult:
    """Unit tests for CredentialResult dataclass"""

    def test_credential_result_success(self):
        """Test successful CredentialResult creation"""
        result = CredentialResult(
            success=True,
            value="test_value",
            source="keychain",
            metadata={"method": "mac_keychain"},
        )

        assert result.success is True
        assert result.value == "test_value"
        assert result.source == "keychain"
        assert result.error is None
        assert result.metadata == {"method": "mac_keychain"}

    def test_credential_result_error(self):
        """Test error CredentialResult creation"""
        result = CredentialResult(
            success=False, error="Credential not found", source="keychain"
        )

        assert result.success is False
        assert result.value is None
        assert result.error == "Credential not found"
        assert result.source == "keychain"


class TestCredentialsManager:
    """Unit tests for CredentialsManager class"""

    @pytest.fixture
    def credentials_manager(self):
        """Create a fresh CredentialsManager instance for each test"""
        return CredentialsManager()

    def test_credentials_manager_initialization(self, credentials_manager):
        """Test CredentialsManager initialization"""
        assert credentials_manager._cache == {}
        assert len(credentials_manager._configs) > 0
        assert "telegram_api_id" in credentials_manager._configs
        assert "openai_api_key" in credentials_manager._configs

    def test_get_credential_unknown(self, credentials_manager):
        """Test getting unknown credential"""
        result = credentials_manager.get_credential("unknown_credential")

        assert result.success is False
        assert "Unknown credential" in result.error

    @patch("subprocess.run")
    def test_get_from_keychain_success(self, mock_run, credentials_manager):
        """Test successful keychain credential retrieval"""
        # Mock successful subprocess run
        mock_result = Mock()
        mock_result.stdout = "test_value\n"
        mock_run.return_value = mock_result

        config = CredentialConfig(
            name="Test Key",
            source="keychain",
            key="test_key",
            validation_rules={"type": "str", "min_length": 1},
        )

        result = credentials_manager._get_from_keychain(config)

        assert result.success is True
        assert result.value == "test_value"
        assert result.source == "keychain"
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_get_from_keychain_failure(self, mock_run, credentials_manager):
        """Test failed keychain credential retrieval"""
        # Mock failed subprocess run
        mock_run.side_effect = subprocess.CalledProcessError(1, "security")

        config = CredentialConfig(name="Test Key", source="keychain", key="test_key")

        result = credentials_manager._get_from_keychain(config)

        assert result.success is False
        assert "Credential not found" in result.error

    @patch.dict(os.environ, {"TEST_API_KEY": "test_value"})
    def test_get_from_env_success(self, credentials_manager):
        """Test successful environment variable retrieval"""
        config = CredentialConfig(
            name="Test API Key",
            source="env",
            key="test_api_key",
            validation_rules={"type": "str", "min_length": 1},
        )

        result = credentials_manager._get_from_env(config)

        assert result.success is True
        assert result.value == "test_value"
        assert result.source == "env"

    @patch.dict(os.environ, {}, clear=True)
    def test_get_from_env_failure(self, credentials_manager):
        """Test failed environment variable retrieval"""
        config = CredentialConfig(name="Test API Key", source="env", key="test_api_key")

        result = credentials_manager._get_from_env(config)

        assert result.success is False
        assert "Environment variable" in result.error

    @patch.dict(os.environ, {"GITHUB_ACTIONS": "true", "TEST_API_KEY": "test_value"})
    def test_get_from_github_secrets_success(self, credentials_manager):
        """Test successful GitHub secrets retrieval"""
        config = CredentialConfig(
            name="Test API Key",
            source="github_secrets",
            key="test_api_key",
            validation_rules={"type": "str", "min_length": 1},
        )

        result = credentials_manager._get_from_github_secrets(config)

        assert result.success is True
        assert result.value == "test_value"
        assert result.source == "github_secrets"

    @patch.dict(os.environ, {}, clear=True)
    def test_get_from_github_secrets_not_github_actions(self, credentials_manager):
        """Test GitHub secrets retrieval when not in GitHub Actions"""
        config = CredentialConfig(
            name="Test API Key", source="github_secrets", key="test_api_key"
        )

        result = credentials_manager._get_from_github_secrets(config)

        assert result.success is False
        assert "Not running in GitHub Actions" in result.error

    def test_get_from_file_success(self, credentials_manager, tmp_path):
        """Test successful file credential retrieval"""
        # Create temporary file in .heroes directory
        heroes_dir = tmp_path / ".heroes"
        heroes_dir.mkdir()
        test_file = heroes_dir / "test_key.txt"
        test_file.write_text("test_value")

        with patch("pathlib.Path.home", return_value=tmp_path):
            config = CredentialConfig(
                name="Test Key",
                source="file",
                key="test_key",
                validation_rules={"type": "str", "min_length": 1},
            )

            result = credentials_manager._get_from_file(config)

            assert result.success is True
            assert result.value == "test_value"
            assert result.source == "file"

    def test_get_from_file_not_found(self, credentials_manager, tmp_path):
        """Test file credential retrieval when file doesn't exist"""
        with patch("pathlib.Path.home", return_value=tmp_path):
            config = CredentialConfig(
                name="Test Key", source="file", key="nonexistent_key"
            )

            result = credentials_manager._get_from_file(config)

            assert result.success is False
            assert "File not found" in result.error

    def test_validate_credential_success(self, credentials_manager):
        """Test successful credential validation"""
        config = CredentialConfig(
            name="Test Key",
            source="keychain",
            key="test_key",
            validation_rules={"type": "str", "min_length": 5, "max_length": 10},
        )

        result = credentials_manager._validate_credential(config, "test_value")
        assert result is True

    def test_validate_credential_int_type(self, credentials_manager):
        """Test integer credential validation"""
        config = CredentialConfig(
            name="Test Key",
            source="keychain",
            key="test_key",
            validation_rules={"type": "int"},
        )

        assert credentials_manager._validate_credential(config, "123") is True
        assert credentials_manager._validate_credential(config, "abc") is False

    def test_validate_credential_length(self, credentials_manager):
        """Test length validation"""
        config = CredentialConfig(
            name="Test Key",
            source="keychain",
            key="test_key",
            validation_rules={"min_length": 5, "max_length": 10},
        )

        assert credentials_manager._validate_credential(config, "test_value") is True
        assert credentials_manager._validate_credential(config, "test") is False
        assert (
            credentials_manager._validate_credential(config, "test_value_too_long")
            is False
        )

    def test_validate_credential_prefix(self, credentials_manager):
        """Test prefix validation"""
        config = CredentialConfig(
            name="Test Key",
            source="keychain",
            key="test_key",
            validation_rules={"prefix": "sk-"},
        )

        assert credentials_manager._validate_credential(config, "sk-test123") is True
        assert credentials_manager._validate_credential(config, "test123") is False

    def test_get_credential_with_cache(self, credentials_manager):
        """Test credential retrieval with caching"""
        # Mock successful keychain retrieval
        with patch.object(credentials_manager, "_get_from_keychain") as mock_keychain:
            mock_keychain.return_value = CredentialResult(
                success=True, value="cached_value", source="keychain"
            )

            # First call - should hit keychain
            result1 = credentials_manager.get_credential("telegram_api_id")
            assert result1.success is True
            assert result1.value == "cached_value"

            # Second call - should hit cache
            result2 = credentials_manager.get_credential("telegram_api_id")
            assert result2.success is True
            assert result2.value == "cached_value"

            # Should only call keychain once
            assert mock_keychain.call_count == 1

    def test_clear_cache(self, credentials_manager):
        """Test cache clearing"""
        # Add something to cache
        credentials_manager._cache["test"] = CredentialResult(
            success=True, value="test"
        )
        assert len(credentials_manager._cache) == 1

        credentials_manager.clear_cache()
        assert len(credentials_manager._cache) == 0

    def test_get_all_credentials(self, credentials_manager):
        """Test getting all configured credentials"""
        results = credentials_manager.get_all_credentials()

        assert isinstance(results, dict)
        assert len(results) > 0
        assert all(isinstance(v, CredentialResult) for v in results.values())

    def test_test_credentials(self, credentials_manager):
        """Test credential testing functionality"""
        results = credentials_manager.test_credentials()

        assert isinstance(results, dict)
        assert len(results) > 0
        assert all(isinstance(v, bool) for v in results.values())


class TestIntegrationCredentialsManager:
    """Integration tests for CredentialsManager"""

    @pytest.fixture
    def credentials_manager(self):
        """Create a fresh CredentialsManager instance for each test"""
        return CredentialsManager()

    def test_fallback_chain_keychain_to_env(self, credentials_manager):
        """Test fallback chain from keychain to env"""
        # Mock keychain failure
        with patch.object(credentials_manager, "_get_from_keychain") as mock_keychain:
            mock_keychain.return_value = CredentialResult(
                success=False, error="Not found in keychain"
            )

            # Mock env success
            with patch.object(credentials_manager, "_get_from_env") as mock_env:
                mock_env.return_value = CredentialResult(
                    success=True, value="env_value", source="env"
                )

                result = credentials_manager.get_credential("telegram_api_id")

                assert result.success is True
                assert result.value == "env_value"
                assert result.source == "env"

    def test_fallback_chain_all_fail(self, credentials_manager):
        """Test fallback chain when all sources fail"""
        # Mock all sources to fail
        with patch.object(credentials_manager, "_get_from_keychain") as mock_keychain:
            mock_keychain.return_value = CredentialResult(
                success=False, error="Keychain failed"
            )

            with patch.object(credentials_manager, "_get_from_env") as mock_env:
                mock_env.return_value = CredentialResult(
                    success=False, error="Env failed"
                )

                result = credentials_manager.get_credential("telegram_api_id")

                assert result.success is False
                assert "Failed to get" in result.error

    @patch("subprocess.run")
    def test_store_credential_keychain(self, mock_run, credentials_manager):
        """Test storing credential in keychain"""
        # Mock successful subprocess run
        mock_run.return_value = Mock()

        # Use a valid credential value that passes validation
        result = credentials_manager.store_credential(
            "telegram_api_id", "12345", "keychain"
        )

        assert result is True
        assert mock_run.call_count == 2  # Delete + store

    def test_store_credential_env(self, credentials_manager):
        """Test storing credential in environment"""
        result = credentials_manager.store_credential("telegram_api_id", "12345", "env")

        assert result is True
        assert os.environ.get("TELEGRAM_API_ID") == "12345"

    def test_store_credential_invalid(self, credentials_manager):
        """Test storing invalid credential"""
        result = credentials_manager.store_credential("telegram_api_id", "", "keychain")

        assert result is False


class TestE2ECredentialsManager:
    """End-to-End tests for CredentialsManager"""

    @pytest.fixture
    def temp_credentials_dir(self, tmp_path):
        """Create temporary credentials directory"""
        creds_dir = tmp_path / ".heroes"
        creds_dir.mkdir()
        return creds_dir

    def test_full_workflow_file_source(self, temp_credentials_dir):
        """Test full workflow with file source"""
        with patch("pathlib.Path.home", return_value=temp_credentials_dir.parent):
            # Create credential file
            cred_file = temp_credentials_dir / "test_key.txt"
            cred_file.write_text("test_value")

            # Test retrieval - need to add test_key to configs first
            from shared.credentials_manager import credentials_manager

            credentials_manager._configs["test_key"] = CredentialConfig(
                name="Test Key", source="file", key="test_key"
            )

            result = get_credential("test_key")
            assert result == "test_value"

    def test_full_workflow_env_source(self):
        """Test full workflow with environment source"""
        with patch.dict(os.environ, {"TEST_API_KEY": "env_value"}):
            # Test retrieval - need to add test_api_key to configs first
            from shared.credentials_manager import credentials_manager

            credentials_manager._configs["test_api_key"] = CredentialConfig(
                name="Test API Key", source="env", key="test_api_key"
            )

            result = get_credential("test_api_key")
            assert result == "env_value"

    def test_full_workflow_store_and_retrieve(self, temp_credentials_dir):
        """Test full workflow: store and retrieve"""
        with patch("pathlib.Path.home", return_value=temp_credentials_dir.parent):
            # Add test_key to configs first
            from shared.credentials_manager import credentials_manager

            credentials_manager._configs["test_key"] = CredentialConfig(
                name="Test Key", source="file", key="test_key"
            )

            # Store credential
            success = store_credential("test_key", "stored_value", "file")
            assert success is True

            # Clear cache to force re-read
            credentials_manager.clear_cache()

            # Retrieve credential
            result = get_credential("test_key")
            assert result == "stored_value"


class TestSecurityCredentialsManager:
    """Security tests for CredentialsManager"""

    def test_credential_validation_injection_prevention(self):
        """Test prevention of credential injection attacks"""
        manager = CredentialsManager()

        # Test SQL injection attempt
        malicious_input = "'; DROP TABLE users; --"
        config = CredentialConfig(
            name="Test",
            source="keychain",
            key="test",
            validation_rules={"type": "str", "pattern": r"^[a-zA-Z0-9_-]+$"},
        )

        result = manager._validate_credential(config, malicious_input)
        assert result is False

    def test_credential_validation_xss_prevention(self):
        """Test prevention of XSS in credential values"""
        manager = CredentialsManager()

        # Test XSS attempt
        xss_input = "<script>alert('xss')</script>"
        config = CredentialConfig(
            name="Test",
            source="keychain",
            key="test",
            validation_rules={"type": "str", "pattern": r"^[a-zA-Z0-9\s]+$"},
        )

        result = manager._validate_credential(config, xss_input)
        assert result is False

    def test_credential_source_validation(self):
        """Test validation of credential sources"""
        manager = CredentialsManager()

        # Test unknown source
        result = manager._get_from_source(
            CredentialConfig(name="Test", source="unknown", key="test"), "unknown"
        )

        assert result.success is False
        assert "Unknown source" in result.error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
