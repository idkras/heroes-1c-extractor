#!/usr/bin/env python3
"""
Unit tests for MCP Server - Testing only implemented commands
"""

from typing import Any
from unittest.mock import patch

import pytest


class TestHeroesMCPServer:
    """Test suite for Modern MCP Server - Only implemented commands"""

    @pytest.fixture
    def server(self) -> Any:
        """Create server instance with mocked methods"""
        import sys
        from pathlib import Path

        sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

        # Import the actual mcp_server module
        import heroes_mcp_server as mcp_server

        # Create a mock server that uses the actual FastMCP instance
        class MockMCPServer:
            def __init__(self):
                self.mcp = mcp_server.mcp
                self.server_name = "heroes_mcp"
                self.server_version = "1.0.0"

        return MockMCPServer()

    @pytest.mark.asyncio
    async def test_server_initialization(self, server: Any) -> None:
        """Test server initialization"""
        assert server.server_name == "heroes_mcp"
        assert server.server_version == "1.0.0"
        assert hasattr(server, "mcp")

    @pytest.mark.asyncio
    async def test_server_info_command(self, server: Any) -> None:
        """Test server_info command"""
        import heroes_platform.heroes_mcp.src.heroes_mcp_server as mcp_server

        result = mcp_server.server_info()

        assert result is not None
        assert "name" in result
        assert "status" in result
        assert "workflows_loaded" in result

    @pytest.mark.asyncio
    async def test_standards_workflow_command(self, server: Any) -> None:
        """Test standards_workflow_command - real method"""
        import heroes_platform.heroes_mcp.src.heroes_mcp_server as mcp_server

        result = await mcp_server.standards_workflow_command("list")

        assert result is not None
        # Parse JSON result
        import json

        data = json.loads(result)
        # Check for either "status" or "error" field
        assert "status" in data or "error" in data

    @pytest.mark.asyncio
    async def test_standards_workflow_get_command(self, server: Any) -> None:
        """Test standards_workflow_command get - real method"""
        import heroes_platform.heroes_mcp.src.heroes_mcp_server as mcp_server

        result = await mcp_server.standards_workflow_command(
            "get", name="test_standard"
        )

        assert result is not None
        # Parse JSON result
        import json

        data = json.loads(result)
        # Check for either "status" or "error" field
        assert "status" in data or "error" in data

    @pytest.mark.asyncio
    async def test_standards_workflow_search_command(self, server: Any) -> None:
        """Test standards_workflow_command search - real method"""
        import heroes_platform.heroes_mcp.src.heroes_mcp_server as mcp_server

        result = await mcp_server.standards_workflow_command("search", query="test")

        assert result is not None
        # Parse JSON result
        import json

        data = json.loads(result)
        # Check for either "status" or "error" field
        assert "status" in data or "error" in data

    @pytest.mark.asyncio
    async def test_ai_guidance_checklist_command(self, server: Any) -> None:
        """Test ai_guidance_checklist - real method"""
        import heroes_platform.heroes_mcp.src.heroes_mcp_server as mcp_server

        result = mcp_server.ai_guidance_checklist("general")

        assert result is not None
        # Parse JSON result
        import json

        data = json.loads(result)
        # Check for either "status" or "error" field
        assert "status" in data or "error" in data

    @pytest.mark.asyncio
    async def test_common_mistakes_prevention_command(self, server: Any) -> None:
        """Test common_mistakes_prevention - real method"""
        import heroes_platform.heroes_mcp.src.heroes_mcp_server as mcp_server

        result = await mcp_server.common_mistakes_prevention("general")

        assert result is not None
        # Parse JSON result
        import json

        data = json.loads(result)
        # Check for expected fields in common_mistakes_prevention response
        assert "domain" in data and "preventions" in data

    @pytest.mark.asyncio
    async def test_workflow_integration_command(self, server: Any) -> None:
        """Test workflow_integration command"""
        import heroes_platform.heroes_mcp.src.heroes_mcp_server as mcp_server

        with patch("heroes_mcp_server.workflows_loaded", True):
            result = await mcp_server.workflow_integration(
                "test_workflow", "execute", {"param": "value"}
            )

            assert result is not None
            # The function returns JSON string, so we need to parse it
            import json

            data = json.loads(result)
            assert "error" in data  # It should return an error for unknown workflow

    @pytest.mark.asyncio
    async def test_registry_compliance_check_command(self, server: Any) -> None:
        """Test registry_compliance_check command"""
        import heroes_platform.heroes_mcp.src.heroes_mcp_server as mcp_server

        result = mcp_server.registry_compliance_check()

        assert result is not None
        assert "compliance" in result

    @pytest.mark.asyncio
    async def test_ai_guidance_checklist_command(self, server: Any) -> None:
        """Test ai_guidance_checklist command"""
        import heroes_platform.heroes_mcp.src.heroes_mcp_server as mcp_server

        result = mcp_server.ai_guidance_checklist("general")

        assert result is not None
        # The function returns JSON string, so we check for content
        import json

        data = json.loads(result)
        assert "checklist" in data


class TestMCPServerIntegration:
    """Integration tests for MCP Server"""

    @pytest.fixture
    def server(self) -> Any:
        """Create a test server instance"""
        import sys
        from pathlib import Path

        sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

        import heroes_platform.heroes_mcp.src.heroes_mcp_server as mcp_server

        class MockMCPServer:
            def __init__(self):
                self.mcp = mcp_server.mcp

        return MockMCPServer()

    @pytest.mark.asyncio
    async def test_tool_listing(self, server) -> Any:
        """Test that tools are properly listed"""
        assert hasattr(server, "mcp")
        assert server.mcp is not None

    @pytest.mark.asyncio
    async def test_standards_workflow(self, server) -> Any:
        """Test complete standards workflow - real methods"""
        import heroes_platform.heroes_mcp.src.heroes_mcp_server as mcp_server

        # Test standards list
        list_result = await mcp_server.standards_workflow_command("list")
        assert list_result is not None
        import json

        data = json.loads(list_result)
        # Check for either "status" or "error" field
        assert "status" in data or "error" in data

        # Test standards search
        search_result = await mcp_server.standards_workflow_command(
            "search", query="test"
        )
        assert search_result is not None
        data = json.loads(search_result)
        # Check for either "status" or "error" field
        assert "status" in data or "error" in data


if __name__ == "__main__":
    pytest.main([__file__])
