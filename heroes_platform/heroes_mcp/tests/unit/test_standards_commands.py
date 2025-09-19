#!/usr/bin/env python3
"""
Unit tests for Standards MCP Commands
Following TDD Standard with reflection checkpoints
"""

import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

import heroes_mcp_server as mcp_server


class TestStandardsCommands:
    """Unit tests for standards management commands"""

    @pytest.fixture
    def mock_standards_dir(self, tmp_path):
        """Create mock standards directory"""
        standards_dir = tmp_path / "[standards .md]"
        standards_dir.mkdir()

        # Create some test standards
        (standards_dir / "test_standard_1.md").write_text(
            "# Test Standard 1\nContent here"
        )
        (standards_dir / "test_standard_2.md").write_text(
            "# Test Standard 2\nMore content"
        )

        return standards_dir

    @pytest.mark.asyncio
    async def test_standards_list_success(self, mock_standards_dir):
        """
        JTBD: Как тестировщик, я хочу проверить standards_list с reflection checkpoints,
        чтобы обеспечить quality и debugging capability.
        """

        # 🔍 REFLECTION CHECKPOINT 1 - Pre-execution
        print("REFLECTION: Starting standards_list test")
        print("REFLECTION: Expected outcome - list of standards returned")

        # GIVEN - подготовка test data
        mock_workflow = AsyncMock()
        mock_workflow.execute.return_value = {
            "standards": ["test_standard1.md", "test_standard2.md"]
        }

        with (
            patch("heroes_mcp_server.STANDARDS_DIR", mock_standards_dir),
            patch("heroes_mcp_server.standards_workflow_instance", mock_workflow),
        ):
            # WHEN - выполнение MCP command
            result = await mcp_server.standards_workflow_command("list", **{})

            # 🔍 REFLECTION CHECKPOINT 2 - Post-execution
            print(f"REFLECTION: Actual result type: {type(result)}")
            print(f"REFLECTION: Result content preview: {str(result)[:100]}")

            # THEN - проверка результата
            assert result is not None, "REFLECTION: Result should not be None"
            assert "standards" in str(result), (
                "REFLECTION: Result should contain standards"
            )

            # Parse JSON result
            data = json.loads(result)
            assert "standards" in data, "REFLECTION: JSON should contain standards key"
            assert len(data["standards"]) >= 2, (
                "REFLECTION: Should find at least 2 standards"
            )

            # 🔍 REFLECTION CHECKPOINT 3 - Quality validation
            print("REFLECTION: Test completed successfully")
            print("REFLECTION: Quality check - deterministic result achieved")

    @pytest.mark.asyncio
    async def test_standards_list_empty_directory(self, tmp_path):
        """Test standards_list with empty directory"""
        empty_dir = tmp_path / "empty_standards"
        empty_dir.mkdir()

        mock_workflow = AsyncMock()
        mock_workflow.execute.return_value = {"standards": []}

        with (
            patch("heroes_mcp_server.STANDARDS_DIR", empty_dir),
            patch("heroes_mcp_server.standards_workflow_instance", mock_workflow),
        ):
            result = await mcp_server.standards_workflow_command("list", **{})

            data = json.loads(result)
            assert "standards" in data
            assert len(data["standards"]) == 0

    @pytest.mark.asyncio
    async def test_standards_get_existing(self, mock_standards_dir):
        """Test standards_get with existing standard"""
        mock_workflow = AsyncMock()
        mock_workflow.execute.return_value = {
            "content": "# Test Standard 1\n\nThis is a test standard."
        }

        with (
            patch("heroes_mcp_server.STANDARDS_DIR", mock_standards_dir),
            patch("heroes_mcp_server.standards_workflow_instance", mock_workflow),
        ):
            result = await mcp_server.standards_workflow_command(
                "get", name="test_standard_1"
            )

            data = json.loads(result)
            assert "content" in data
            assert "# Test Standard 1" in data["content"]

    @pytest.mark.asyncio
    async def test_standards_get_nonexistent(self, mock_standards_dir):
        """Test standards_get with non-existent standard"""
        mock_workflow = AsyncMock()
        mock_workflow.execute.return_value = {"error": "Standard not found"}

        with (
            patch("heroes_mcp_server.STANDARDS_DIR", mock_standards_dir),
            patch("heroes_mcp_server.standards_workflow_instance", mock_workflow),
        ):
            result = await mcp_server.standards_workflow_command(
                "get", name="nonexistent_standard"
            )

            data = json.loads(result)
            assert "error" in data
            assert "not found" in data["error"].lower()

    @pytest.mark.asyncio
    async def test_standards_search_found(self, mock_standards_dir):
        """Test standards_search with found results"""
        mock_workflow = AsyncMock()
        mock_workflow.execute.return_value = {
            "results": ["test_standard_1.md", "test_standard_2.md"]
        }

        with (
            patch("heroes_mcp_server.STANDARDS_DIR", mock_standards_dir),
            patch("heroes_mcp_server.standards_workflow_instance", mock_workflow),
        ):
            result = await mcp_server.standards_workflow_command(
                "search", query="Test Standard"
            )

            data = json.loads(result)
            assert "results" in data
            assert len(data["results"]) >= 1

    @pytest.mark.asyncio
    async def test_standards_search_not_found(self, mock_standards_dir):
        """Test standards_search with no results"""
        mock_workflow = AsyncMock()
        mock_workflow.execute.return_value = {"results": []}

        with (
            patch("heroes_mcp_server.STANDARDS_DIR", mock_standards_dir),
            patch("heroes_mcp_server.standards_workflow_instance", mock_workflow),
        ):
            result = await mcp_server.standards_workflow_command(
                "search", query="nonexistent_query"
            )

            data = json.loads(result)
            assert "results" in data
            assert len(data["results"]) == 0

    @pytest.mark.asyncio
    async def test_server_info_basic(self):
        """Test server_info command"""
        result = mcp_server.server_info()

        # Should return JSON string
        assert isinstance(result, str)

        # Try to parse as JSON
        try:
            data = json.loads(result)
            assert "name" in data
            assert "status" in data
        except json.JSONDecodeError:
            # Fallback: should contain basic info
            assert "Heroes MCP Server" in result
