"""
Integration tests for Visual Hierarchy Workflow with MCP Server
Following TDD Documentation Standard - RED Phase
"""

import json
import os
import sys
from unittest.mock import patch

import pytest

# Add parent directory to path for imports
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


class TestVisualHierarchyMCPIntegration:
    """
    JTBD: Как разработчик, я хочу протестировать интеграцию Visual Hierarchy Workflow с MCP сервером,
    чтобы убедиться что команда работает корректно через MCP протокол.
    """

    @pytest.mark.integration
    def test_mcp_tool_registration(self):
        """
        GIVEN MCP server with visual hierarchy workflow
        WHEN server initializes
        THEN analyze_visual_hierarchy tool is registered
        """
        # This should FAIL - tool not yet properly integrated
        from heroes_mcp.src.heroes_mcp_server import mcp

        # Get registered tools
        tools = mcp.list_tools()
        tool_names = [tool.name for tool in tools]

        # Assert
        assert "analyze_visual_hierarchy" in tool_names

    @pytest.mark.integration
    def test_mcp_tool_schema(self):
        """
        GIVEN analyze_visual_hierarchy MCP tool
        WHEN check tool schema
        THEN schema matches expected parameters
        """
        # This should FAIL initially
        from heroes_mcp.src.heroes_mcp_server import mcp

        # Find the tool
        tools = mcp.list_tools()
        visual_tool = next(
            (t for t in tools if t.name == "analyze_visual_hierarchy"), None
        )

        # Assert tool exists
        assert visual_tool is not None

        # Check schema
        assert visual_tool.description is not None
        assert "визуальную иерархию" in visual_tool.description

        # Check parameters
        params = visual_tool.inputSchema
        assert "url" in params["properties"]
        assert "design_type" in params["properties"]
        assert params["properties"]["url"]["type"] == "string"
        assert params["properties"]["design_type"]["type"] == "string"

    @pytest.mark.integration
    async def test_mcp_call_with_valid_url(self):
        """
        GIVEN MCP server with analyze_visual_hierarchy
        WHEN call tool with valid URL
        THEN return visual hierarchy analysis
        """
        # This should FAIL initially
        from heroes_mcp.src.heroes_mcp_server import analyze_visual_hierarchy

        # Mock the workflow to avoid actual network calls
        with patch(
            "workflows.visual_hierarchy_workflow.VisualHierarchyWorkflow.analyze_visual_hierarchy"
        ) as mock_analyze:
            mock_analyze.return_value = {
                "reading_order": [{"step": 1, "element": "Header"}],
                "visual_elements": {"typography": {}},
                "hierarchy_quality_criteria": {},
                "hierarchy_test_cases": {},
                "jtbd_scenario": {},
            }

            # Act
            result = analyze_visual_hierarchy("https://example.com", "landing")

            # Assert
            assert result is not None
            assert isinstance(result, str)
            data = json.loads(result)
            assert "reading_order" in data

    @pytest.mark.integration
    async def test_mcp_call_with_invalid_url(self):
        """
        GIVEN MCP server with analyze_visual_hierarchy
        WHEN call tool with invalid URL
        THEN return error response
        """
        # This should FAIL initially
        from heroes_mcp.src.heroes_mcp_server import analyze_visual_hierarchy

        # Act
        result = analyze_visual_hierarchy("", "landing")

        # Assert
        assert result is not None
        data = json.loads(result)
        assert "error" in data
        assert data["error"] == "URL is required"

    @pytest.mark.integration
    def test_workflow_instance_sharing(self):
        """
        GIVEN MCP server
        WHEN multiple calls to analyze_visual_hierarchy
        THEN same workflow instance is used (singleton pattern)
        """
        # This should FAIL initially
        from heroes_mcp.src.heroes_mcp_server import visual_hierarchy_workflow

        # Assert workflow instance exists
        assert visual_hierarchy_workflow is not None

        # Make multiple calls and ensure same instance
        with patch.object(
            visual_hierarchy_workflow, "analyze_visual_hierarchy"
        ) as mock_method:
            mock_method.return_value = {"test": "data"}

            from heroes_mcp.src.heroes_mcp_server import analyze_visual_hierarchy

            # Call multiple times
            analyze_visual_hierarchy("https://example1.com")
            analyze_visual_hierarchy("https://example2.com")

            # Should be called on same instance
            assert mock_method.call_count == 2

    @pytest.mark.integration
    def test_error_propagation(self):
        """
        GIVEN workflow that raises exception
        WHEN call through MCP
        THEN error is properly propagated and formatted
        """
        # This should FAIL initially
        from heroes_mcp.src.heroes_mcp_server import analyze_visual_hierarchy

        with patch(
            "workflows.visual_hierarchy_workflow.VisualHierarchyWorkflow.analyze_visual_hierarchy"
        ) as mock_analyze:
            mock_analyze.side_effect = ValueError("Test error")

            # Act
            result = analyze_visual_hierarchy("https://example.com")

            # Assert
            assert result is not None
            data = json.loads(result)
            assert "error" in data
            assert "Test error" in str(data["error"])

    @pytest.mark.integration
    def test_json_serialization(self):
        """
        GIVEN workflow returns complex data structure
        WHEN serialize through MCP
        THEN all data is properly JSON serialized
        """
        # This should FAIL initially
        from heroes_mcp.src.heroes_mcp_server import analyze_visual_hierarchy

        with patch(
            "workflows.visual_hierarchy_workflow.VisualHierarchyWorkflow.analyze_visual_hierarchy"
        ) as mock_analyze:
            # Return complex nested structure
            mock_analyze.return_value = {
                "reading_order": [
                    {"step": 1, "element": "Header", "nested": {"key": "value"}}
                ],
                "visual_elements": {
                    "typography": {
                        "fonts": ["Arial", "Helvetica"],
                        "sizes": {"h1": 32, "h2": 24},
                    }
                },
                "test_cases": [{"id": "test_1", "status": "pending", "data": None}],
            }

            # Act
            result = analyze_visual_hierarchy("https://example.com")

            # Assert - should be valid JSON
            assert result is not None
            data = json.loads(result)  # Should not raise
            assert isinstance(data, dict)
            assert data["reading_order"][0]["nested"]["key"] == "value"
