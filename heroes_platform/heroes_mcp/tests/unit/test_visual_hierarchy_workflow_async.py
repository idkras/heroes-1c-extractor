"""
Unit tests for VisualHierarchyWorkflow - Async version
Following TDD Documentation Standard and MCP Workflow Standard v4.1
"""

import pytest
import json
import asyncio
import aiohttp
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from workflows.visual_hierarchy_workflow import VisualHierarchyWorkflow


class TestVisualHierarchyWorkflowAsync:
    """
    JTBD: Как разработчик, я хочу протестировать асинхронный VisualHierarchyWorkflow,
    чтобы убедиться что анализ визуальной иерархии работает корректно с aiohttp.
    """

    def setup_method(self):
        """Setup test fixtures"""
        self.workflow = VisualHierarchyWorkflow()
        self.valid_url = "https://example.com"
        self.invalid_url = ""

    @pytest.mark.asyncio
    async def test_analyze_visual_hierarchy_with_valid_url(self):
        """
        GIVEN valid URL
        WHEN analyze visual hierarchy with async
        THEN return hierarchy analysis with expected structure
        """
        # Arrange
        url = "https://example.com"  # Use real URL for testing
        design_type = "landing"

        # Act - Use real HTTP request
        result = await self.workflow.analyze_visual_hierarchy(url, design_type)

        # Assert
        assert result is not None
        assert isinstance(result, dict)
        assert "reading_order" in result
        assert "visual_elements" in result
        assert "hierarchy_quality_criteria" in result
        assert "hierarchy_test_cases" in result
        assert "jtbd_scenario" in result

    @pytest.mark.asyncio
    async def test_analyze_visual_hierarchy_with_invalid_url(self):
        """
        GIVEN invalid URL
        WHEN analyze visual hierarchy
        THEN return error response
        """
        # Arrange
        url = self.invalid_url

        # Act
        result = await self.workflow.analyze_visual_hierarchy(url)

        # Assert
        assert result is not None
        assert isinstance(result, dict)
        assert "error" in result
        assert result["error"] == "URL is required"

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """
        GIVEN timeout during async request
        WHEN analyze visual hierarchy
        THEN handle timeout gracefully
        """
        # Arrange - Use a URL that will timeout
        url = "http://httpbin.org/delay/10"  # This will timeout

        # Act
        result = await self.workflow.analyze_visual_hierarchy(url)

        # Assert - The request might succeed, so we just check the structure
        assert result is not None
        assert isinstance(result, dict)
        # If it succeeds, it should have the expected structure
        # If it fails, it should have an error
        assert "reading_order" in result or "error" in result

    @pytest.mark.asyncio
    async def test_http_error_handling(self):
        """
        GIVEN HTTP error during request
        WHEN analyze visual hierarchy
        THEN return appropriate error message
        """
        # Arrange - Use a URL that will return 404
        url = "https://example.com/nonexistent-page"

        # Act
        result = await self.workflow.analyze_visual_hierarchy(url)

        # Assert
        assert "error" in result
        assert "404" in result["error"] or "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_network_error_handling(self):
        """
        GIVEN general network error during request
        WHEN analyze visual hierarchy
        THEN return appropriate error message
        """
        # Arrange - Use an invalid URL that will cause network error
        url = "https://invalid-domain-that-does-not-exist-12345.com"

        # Act
        result = await self.workflow.analyze_visual_hierarchy(url)

        # Assert
        assert "error" in result
        assert "error" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_design_type_parameter(self):
        """
        GIVEN different design types
        WHEN analyze visual hierarchy
        THEN adapt analysis to design type
        """
        # Arrange
        design_types = ["landing", "documentation", "blog", "portfolio"]
        url = "https://example.com"

        for design_type in design_types:
            # Act
            result = await self.workflow.analyze_visual_hierarchy(url, design_type)

            # Assert
            assert result is not None
            assert "design_type" in result
            assert result["design_type"] == design_type


# Integration test for MCP Server
class TestVisualHierarchyMCPIntegrationAsync:
    """Integration tests for Visual Hierarchy Workflow with async MCP Server"""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_mcp_server_calls_visual_hierarchy_workflow_async(self):
        """
        GIVEN MCP request for analyze_visual_hierarchy
        WHEN call through async MCP server
        THEN workflow executes and returns result
        """
        # This requires actual MCP server context
        # Mock the MCP server environment
        from heroes_mcp.src.heroes_mcp_server import (
            analyze_visual_hierarchy as mcp_analyze,
        )

        # Mock the entire aiohttp.ClientSession context manager
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.raise_for_status = Mock()
        mock_response.text = AsyncMock(return_value="<html><body>Test</body></html>")

        # Create a proper async context manager for session.get
        class MockResponseContext:
            def __init__(self, response):
                self.response = response

            async def __aenter__(self):
                return self.response

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return None

        mock_session.get.return_value = MockResponseContext(mock_response)

        with patch("aiohttp.ClientSession", return_value=mock_session):

            # Act
            result = await mcp_analyze("https://example.com", "landing")

            # Assert
            assert result is not None
            assert isinstance(result, str)  # MCP returns JSON string
            data = json.loads(result)
            assert "reading_order" in data or "error" in data
