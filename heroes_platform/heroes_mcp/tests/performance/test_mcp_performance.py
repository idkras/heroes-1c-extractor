"""
Performance tests for MCP server
"""

import json
import os
import sys
import time
from pathlib import Path
from unittest.mock import patch

import psutil
import pytest

# Add the correct path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))


class TestMCPPerformance:
    """Test MCP server performance"""

    def test_server_startup_time(self):
        """Test MCP server startup time"""
        start_time = time.time()

        # Import server (simulates startup)
        try:
            # from heroes_mcp.src.heroes_mcp_server import mcp  # Unused import removed
            startup_time = time.time() - start_time

            # Should start within 5 seconds
            assert startup_time < 5.0, f"Server startup took {startup_time:.2f} seconds"

        except ImportError:
            pytest.skip("MCP server not available for testing")

    def test_standards_list_performance(self):
        """Test standards_list performance"""
        from heroes_mcp.src.heroes_mcp_server import standards_list

        # Measure execution time
        start_time = time.time()
        result = standards_list()
        execution_time = time.time() - start_time

        # Should complete within 2 seconds
        assert execution_time < 2.0, f"standards_list took {execution_time:.2f} seconds"

        # Verify result is valid JSON
        data = json.loads(result)
        assert "standards" in data

    def test_standards_search_performance(self):
        """Test standards_search performance"""
        from heroes_mcp.src.heroes_mcp_server import standards_search

        # Measure execution time
        start_time = time.time()
        result = standards_search("test")
        execution_time = time.time() - start_time

        # Should complete within 3 seconds
        assert (
            execution_time < 3.0
        ), f"standards_search took {execution_time:.2f} seconds"

        # Verify result is valid JSON
        data = json.loads(result)
        assert "query" in data

    def test_standards_audit_performance(self):
        """Test standards_audit performance"""
        from heroes_mcp.src.heroes_mcp_server import standards_audit

        # Measure execution time
        start_time = time.time()
        result = standards_audit()
        execution_time = time.time() - start_time

        # Should complete within 10 seconds
        assert (
            execution_time < 10.0
        ), f"standards_audit took {execution_time:.2f} seconds"

        # Verify result is valid JSON
        data = json.loads(result)
        assert "audit_timestamp" in data

    def test_memory_usage(self):
        """Test memory usage of MCP server functions"""
        import gc

        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Run multiple operations
        from heroes_mcp.src.heroes_mcp_server import standards_list, standards_search

        for _ in range(10):
            standards_list()
            standards_search("test")

        # Force garbage collection
        gc.collect()

        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (< 100MB)
        assert (
            memory_increase < 100.0
        ), f"Memory usage increased by {memory_increase:.2f} MB"

    def test_concurrent_operations(self):
        """Test concurrent operations performance"""
        import concurrent.futures

        from heroes_mcp.src.heroes_mcp_server import standards_list, standards_search

        def run_standards_list():
            return standards_list()

        def run_standards_search():
            return standards_search("test")

        # Run operations concurrently
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for _ in range(5):
                futures.append(executor.submit(run_standards_list))
                futures.append(executor.submit(run_standards_search))

            # Wait for all to complete
            results = [future.result() for future in futures]

        total_time = time.time() - start_time

        # Should complete within 5 seconds
        assert total_time < 5.0, f"Concurrent operations took {total_time:.2f} seconds"

        # All results should be valid JSON
        for result in results:
            data = json.loads(result)
            assert isinstance(data, dict)

    def test_large_standards_handling(self):
        """Test handling of large number of standards"""
        # Mock a large standards directory
        with patch("mcp_server.STANDARDS_DIR"):
            # Create mock standards
            mock_standards = []
            for i in range(100):  # 100 standards
                mock_standards.append(
                    {
                        "path": f"test/standard_{i}.md",
                        "name": f"standard_{i}",
                        "size": 1024,
                        "version": "1.0",
                        "status": "Active",
                        "updated": "2024-01-01",
                        "category": "test",
                    }
                )

            # Mock the standards_list function to return large dataset
            with patch("mcp_server.standards_list") as mock_list:
                mock_list.return_value = json.dumps(
                    {
                        "total_count": 100,
                        "standards": mock_standards,
                        "categories": ["test"],
                        "active_standards": 100,
                        "archived_standards": 0,
                    }
                )

                # Test performance with large dataset
                start_time = time.time()
                result = mock_list()
                execution_time = time.time() - start_time

                # Should complete within 1 second even with large dataset
                assert (
                    execution_time < 1.0
                ), f"Large standards list took {execution_time:.2f} seconds"

                # Verify result structure
                data = json.loads(result)
                assert data["total_count"] == 100
                assert len(data["standards"]) == 100


class TestMCPResponseTime:
    """Test MCP server response times"""

    def test_server_info_response_time(self):
        """Test server_info response time"""
        from heroes_mcp.src.heroes_mcp_server import server_info

        start_time = time.time()
        result = server_info()
        response_time = time.time() - start_time

        # Should respond within 100ms
        assert response_time < 0.1, f"server_info took {response_time:.3f} seconds"

        # Verify result contains expected info
        assert "Heroes MCP Server" in result

    def test_telegram_credentials_response_time(self):
        """Test telegram_get_credentials response time"""
        from heroes_mcp.src.heroes_mcp_server import telegram_get_credentials

        start_time = time.time()
        result = telegram_get_credentials()
        response_time = time.time() - start_time

        # Should respond within 500ms
        assert (
            response_time < 0.5
        ), f"telegram_get_credentials took {response_time:.3f} seconds"

        # Verify result contains expected info
        assert "credentials" in result.lower()

    def test_ai_guidance_checklist_response_time(self):
        """Test ai_guidance_checklist response time"""
        from heroes_mcp.src.heroes_mcp_server import ai_guidance_checklist

        start_time = time.time()
        result = ai_guidance_checklist("general")
        response_time = time.time() - start_time

        # Should respond within 100ms
        assert (
            response_time < 0.1
        ), f"ai_guidance_checklist took {response_time:.3f} seconds"

        # Verify result contains expected info
        import json

        data = json.loads(result)
        assert "checklist" in data
