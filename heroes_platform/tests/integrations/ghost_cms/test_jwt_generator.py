"""
Tests for Ghost JWT Generator
"""

import pytest

from src.integrations.ghost_cms.jwt_generator import GhostJWTGenerator


class TestGhostJWTGenerator:
    """Test cases for GhostJWTGenerator"""

    def setup_method(self):
        """Setup test fixtures"""
        self.generator = GhostJWTGenerator()

    def test_generate_jwt_v5_0(self):
        """Test JWT generation for API v5.0"""
        api_key = "test_id:test_secret_hex"
        token = self.generator.generate_jwt(api_key, "v5.0")

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_jwt_v2(self):
        """Test JWT generation for API v2"""
        api_key = "test_id:test_secret_hex"
        token = self.generator.generate_jwt(api_key, "v2")

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_invalid_api_key_format(self):
        """Test JWT generation with invalid API key format"""
        api_key = "invalid_format"

        with pytest.raises(ValueError, match="Admin key must be in 'id:secret' format"):
            self.generator.generate_jwt(api_key)

    def test_validate_jwt(self):
        """Test JWT validation"""
        api_key = "test_id:test_secret_hex"
        token = self.generator.generate_jwt(api_key)

        assert self.generator.validate_jwt(token) is True

    def test_get_token_info(self):
        """Test token info extraction"""
        api_key = "test_id:test_secret_hex"
        token = self.generator.generate_jwt(api_key, "v5.0")

        info = self.generator.get_token_info(token)

        assert info is not None
        assert "audience" in info
        assert "issued_at" in info
        assert "expires_at" in info
        assert info["audience"] == "/admin/"  # v5.0 audience
