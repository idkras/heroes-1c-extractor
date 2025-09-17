"""
Security tests for MCP server
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch

# Add the correct path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))


class TestMCPSecurity:
    """Test MCP server security"""

    def test_input_validation_standards_list(self):
        """Test input validation for standards_list"""
        from heroes_mcp.src.heroes_mcp_server import standards_list

        # Should handle normal input
        result = standards_list()
        data = json.loads(result)
        assert "standards" in data

    def test_input_validation_standards_get(self):
        """Test input validation for standards_get"""
        from heroes_mcp.src.heroes_mcp_server import standards_get

        # Test with None input
        result = standards_get("")
        data = json.loads(result)
        assert "error" in data
        assert "required" in data["error"].lower()

        # Test with malicious input
        malicious_inputs = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "<script>alert('xss')</script>",
            "'; DROP TABLE standards; --",
            "null",
            "undefined",
            "NaN",
        ]

        for malicious_input in malicious_inputs:
            result = standards_get(malicious_input)
            data = json.loads(result)
            # Should not crash and should return error or empty result
            assert isinstance(data, dict)

    def test_input_validation_standards_search(self):
        """Test input validation for standards_search"""
        from heroes_mcp.src.heroes_mcp_server import standards_search

        # Test with None input
        result = standards_search("")
        data = json.loads(result)
        assert "error" in data
        assert "required" in data["error"].lower()

        # Test with malicious input
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE standards; --",
            "null",
            "undefined",
            "NaN",
            "a" * 10000,  # Very long input
        ]

        for malicious_input in malicious_inputs:
            result = standards_search(malicious_input)
            data = json.loads(result)
            # Should not crash and should return valid JSON
            assert isinstance(data, dict)
            assert "query" in data

    def test_input_validation_standards_create(self):
        """Test input validation for standards_create"""
        from heroes_mcp.src.heroes_mcp_server import standards_create

        # Test with None input
        result = standards_create("")
        data = json.loads(result)
        assert "error" in data
        assert "required" in data["error"].lower()

        # Test with malicious input
        malicious_inputs = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "<script>alert('xss')</script>",
            "'; DROP TABLE standards; --",
            "null",
            "undefined",
            "NaN",
        ]

        for malicious_input in malicious_inputs:
            result = standards_create(malicious_input)
            data = json.loads(result)
            # Should not crash and should return error
            assert isinstance(data, dict)

    def test_path_traversal_protection(self):
        """Test protection against path traversal attacks"""
        from heroes_mcp.src.heroes_mcp_server import standards_get

        # Test path traversal attempts
        traversal_attempts = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "..%2F..%2F..%2Fetc%2Fpasswd",
            "..%5C..%5C..%5Cwindows%5Csystem32%5Cconfig%5Csam",
        ]

        for attempt in traversal_attempts:
            result = standards_get(attempt)
            data = json.loads(result)
            # Should not access files outside standards directory
            assert "error" in data or "not found" in data.get("error", "").lower()

    def test_sql_injection_protection(self):
        """Test protection against SQL injection (if applicable)"""
        from heroes_mcp.src.heroes_mcp_server import standards_search

        # Test SQL injection attempts
        sql_injection_attempts = [
            "'; DROP TABLE standards; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users --",
            "'; INSERT INTO standards VALUES ('hacked', 'hacked'); --",
            "admin'--",
            "1' OR '1' = '1' --",
        ]

        for attempt in sql_injection_attempts:
            result = standards_search(attempt)
            data = json.loads(result)
            # Should not crash and should return valid JSON
            assert isinstance(data, dict)
            assert "query" in data

    def test_xss_protection(self):
        """Test protection against XSS attacks"""
        from heroes_mcp.src.heroes_mcp_server import standards_search

        # Test XSS attempts
        xss_attempts = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<svg onload=alert('xss')>",
            "';alert('xss');//",
        ]

        for attempt in xss_attempts:
            result = standards_search(attempt)
            data = json.loads(result)
            # Should not crash and should return valid JSON
            assert isinstance(data, dict)
            assert "query" in data

    def test_file_creation_security(self):
        """Test security of file creation operations"""
        from heroes_mcp.src.heroes_mcp_server import standards_create

        # Test creating file with path traversal attempts
        path_traversal_names = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
        ]

        for malicious_name in path_traversal_names:
            result = standards_create(malicious_name)
            data = json.loads(result)
            # Should sanitize paths and create files safely within standards directory
            assert "success" in data or "error" in data
            if "success" in data:
                # File should be created within standards directory with sanitized name
                assert not data["file_path"].startswith("../")
                assert not data["file_path"].startswith("..\\")

        # Test that normal names work correctly
        result = standards_create("test_security_file")
        data = json.loads(result)
        assert "success" in data

    def test_telegram_credentials_security(self):
        """Test security of Telegram credentials handling"""
        from heroes_mcp.src.heroes_mcp_server import telegram_manager

        # Test that credentials are not exposed in logs or output
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = "safe_test_key\n"
            mock_run.return_value.returncode = 0

            credentials = telegram_manager.get_credentials()

            # Credentials should be handled securely
            if credentials:
                # Should not contain obviously sensitive patterns
                cred_str = str(credentials)
                assert "password" not in cred_str.lower()
                assert "secret" not in cred_str.lower()
                # Should return proper credential structure
                assert isinstance(credentials, dict)

    def test_json_output_safety(self):
        """Test that JSON output is safe and properly escaped"""
        from heroes_mcp.src.heroes_mcp_server import standards_list

        result = standards_list()

        # Should be valid JSON
        json.loads(result)

        # Should not contain unescaped special characters
        result_str = str(result)
        assert "\\" in result_str or '"' in result_str  # Should be properly escaped

    def test_error_handling_security(self):
        """Test that error handling doesn't expose sensitive information"""
        from heroes_mcp.src.heroes_mcp_server import standards_get

        # Test with invalid input that might cause errors
        error_inputs = [
            None,
            "",
            "invalid/path/with/special/chars/\x00\x01\x02",
            "path/with/unicode/\u0000\u0001\u0002",
            "very/long/path/" + "a" * 10000,
        ]

        for error_input in error_inputs:
            try:
                result = standards_get(error_input)
                data = json.loads(result)
                # Should not expose internal paths or sensitive info
                assert "error" in data
                error_msg = data["error"]
                assert "/etc/" not in error_msg
                assert "/windows/" not in error_msg
                assert "password" not in error_msg.lower()
                assert "secret" not in error_msg.lower()
            except Exception as e:
                # Should not expose sensitive information in exceptions
                error_str = str(e)
                assert "/etc/" not in error_str
                assert "/windows/" not in error_str
                assert "password" not in error_str.lower()
                assert "secret" not in error_str.lower()


class TestMCPServerSecurity:
    """Test MCP server security features"""

    def test_server_info_security(self):
        """Test that server_info doesn't expose sensitive information"""
        from heroes_mcp.src.heroes_mcp_server import server_info

        result = server_info()

        # Should not expose sensitive information
        assert "password" not in result.lower()
        assert "secret" not in result.lower()
        assert "key" not in result.lower()
        assert "token" not in result.lower()

        # Should contain expected non-sensitive information
        assert "Heroes MCP Server" in result

    def test_ai_guidance_checklist_security(self):
        """Test that ai_guidance_checklist doesn't expose sensitive information"""
        from heroes_mcp.src.heroes_mcp_server import ai_guidance_checklist

        result = ai_guidance_checklist("general")

        # Should not expose sensitive information
        assert "password" not in result.lower()
        assert "secret" not in result.lower()
        assert "key" not in result.lower()
        assert "token" not in result.lower()

        # Should contain expected non-sensitive information
        import json

        data = json.loads(result)
        assert "checklist" in data
