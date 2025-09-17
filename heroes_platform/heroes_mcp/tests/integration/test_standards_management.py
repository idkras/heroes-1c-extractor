"""
Integration tests for Standards Management in MCP server
"""

import json
import sys
from pathlib import Path

import pytest

# Add the correct path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))


class TestStandardsManagement:
    """Test Standards Management functionality"""

    def test_standards_list(self):
        """Test listing standards"""
        from heroes_mcp.src.heroes_mcp_server import standards_list

        result = standards_list()

        # Parse JSON result
        data = json.loads(result)

        # Check structure
        assert "standards" in data
        assert "total_count" in data
        assert "categories" in data
        assert isinstance(data["standards"], list)
        assert isinstance(data["total_count"], int)
        assert isinstance(data["categories"], list)

    def test_standards_get_existing(self):
        """Test getting existing standard"""
        # First get list to find an existing standard
        from heroes_mcp.src.heroes_mcp_server import standards_get, standards_list

        list_result = standards_list()
        list_data = json.loads(list_result)

        if list_data["standards"]:
            # Get first standard
            first_standard = list_data["standards"][0]["name"]
            result = standards_get(first_standard)

            # Parse JSON result
            data = json.loads(result)

            # Check structure
            assert "standard_name" in data
            assert "content" in data
            assert "path" in data
            assert isinstance(data["content"], str)
            assert len(data["content"]) > 0
        else:
            pytest.skip("No standards found for testing")

    def test_standards_get_nonexistent(self):
        """Test getting non-existent standard"""
        from heroes_mcp.src.heroes_mcp_server import standards_get

        result = standards_get("nonexistent_standard_12345")

        # Parse JSON result
        data = json.loads(result)

        # Should return error
        assert "error" in data
        assert "not found" in data["error"].lower()

    def test_standards_search(self):
        """Test searching standards"""
        from heroes_mcp.src.heroes_mcp_server import standards_search

        result = standards_search("standard")

        # Parse JSON result
        data = json.loads(result)

        # Check structure
        assert "query" in data
        assert "total_found" in data
        assert "results" in data
        assert data["query"] == "standard"
        assert isinstance(data["total_found"], int)
        assert isinstance(data["results"], list)

    def test_standards_search_empty_query(self):
        """Test searching with empty query"""
        from heroes_mcp.src.heroes_mcp_server import standards_search

        result = standards_search("")

        # Parse JSON result
        data = json.loads(result)

        # Should return error
        assert "error" in data
        assert "required" in data["error"].lower()

    def test_standards_validate(self):
        """Test validating standard"""
        # First get list to find an existing standard
        from heroes_mcp.src.heroes_mcp_server import standards_list, standards_validate

        list_result = standards_list()
        list_data = json.loads(list_result)

        if list_data["standards"]:
            # Get first standard
            first_standard = list_data["standards"][0]["name"]
            result = standards_validate(first_standard)

            # Parse JSON result
            data = json.loads(result)

            # Check structure
            assert "standard_name" in data
            assert "is_valid" in data
            assert "errors" in data
            assert "warnings" in data
            assert "checks_passed" in data
            assert "checks_failed" in data
            assert isinstance(data["is_valid"], bool)
            assert isinstance(data["errors"], list)
            assert isinstance(data["warnings"], list)
        else:
            pytest.skip("No standards found for testing")

    def test_standards_audit(self):
        """Test auditing standards"""
        from heroes_mcp.src.heroes_mcp_server import standards_audit

        result = standards_audit()

        # Parse JSON result
        data = json.loads(result)

        # Check structure
        assert "audit_timestamp" in data
        assert "total_standards" in data
        assert "audit_summary" in data
        assert "standards_by_category" in data
        assert "validation_details" in data
        assert "recommendations" in data
        assert isinstance(data["total_standards"], int)
        assert isinstance(data["audit_summary"], dict)
        assert isinstance(data["standards_by_category"], dict)
        assert isinstance(data["validation_details"], list)
        assert isinstance(data["recommendations"], list)

    def test_standards_create(self):
        """Test creating new standard"""
        from heroes_mcp.src.heroes_mcp_server import standards_create

        result = standards_create(
            standard_name="test_standard_creation",
            category="test",
            description="Test standard for testing",
            template="basic",
        )

        # Parse JSON result
        data = json.loads(result)

        # Check structure
        assert "success" in data
        assert "standard_name" in data
        assert "file_path" in data
        assert "category" in data
        assert data["success"] is True
        assert data["standard_name"] == "test_standard_creation"
        assert data["category"] == "test"

    def test_standards_create_duplicate(self):
        """Test creating duplicate standard"""
        from heroes_mcp.src.heroes_mcp_server import standards_create

        # Create first time
        standards_create(
            standard_name="test_duplicate_standard",
            category="test",
            description="Test standard for duplicate testing",
            template="basic",
        )

        # Try to create again
        result = standards_create(
            standard_name="test_duplicate_standard",
            category="test",
            description="Test standard for duplicate testing",
            template="basic",
        )

        # Parse JSON result
        data = json.loads(result)

        # Should return error
        assert "error" in data
        assert "already exists" in data["error"].lower()

    def test_standards_update(self):
        """Test updating standard"""
        # First create a standard
        from heroes_mcp.src.heroes_mcp_server import standards_create, standards_update

        standards_create(
            standard_name="test_update_standard",
            category="test",
            description="Test standard for update testing",
            template="basic",
        )

        # Update it
        result = standards_update(
            standard_name="test_update_standard",
            update_type="version",
            update_notes="Test update",
        )

        # Parse JSON result
        data = json.loads(result)

        # Check structure
        assert "success" in data
        assert "standard_name" in data
        assert "old_version" in data
        assert "new_version" in data
        assert data["success"] is True
        assert data["standard_name"] == "test_update_standard"

    def test_standards_archive(self):
        """Test archiving standard"""
        # First create a standard
        from heroes_mcp.src.heroes_mcp_server import standards_archive, standards_create

        standards_create(
            standard_name="test_archive_standard",
            category="test",
            description="Test standard for archive testing",
            template="basic",
        )

        # Archive it
        result = standards_archive(
            standard_name="test_archive_standard",
            reason="Test archiving",
            replacement_standard="None",
        )

        # Parse JSON result
        data = json.loads(result)

        # Check structure
        assert "success" in data
        assert "standard_name" in data
        assert "reason" in data
        assert "replacement_standard" in data
        assert data["success"] is True
        assert data["standard_name"] == "test_archive_standard"
        assert data["reason"] == "Test archiving"
