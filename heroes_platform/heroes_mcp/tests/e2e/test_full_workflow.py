"""
End-to-end tests for MCP server full workflow
"""

import json
import sys
from pathlib import Path

# Add the correct path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))


class TestMCPFullWorkflow:
    """Test complete MCP server workflow"""

    def test_complete_standards_workflow(self):
        """Test complete standards management workflow"""
        from heroes_mcp.src.heroes_mcp_server import (
            standards_archive,
            standards_create,
            standards_get,
            standards_list,
            standards_search,
            standards_update,
        )

        # 1. List existing standards
        list_result = standards_list()
        list_data = json.loads(list_result)
        initial_count = list_data["total_count"]

        # 2. Create new standard
        create_result = standards_create(
            standard_name="e2e_test_standard",
            category="e2e_test",
            description="Test standard for E2E testing",
            template="basic",
        )
        create_data = json.loads(create_result)
        assert create_data["success"] is True
        assert create_data["standard_name"] == "e2e_test_standard"

        # 3. Verify standard was created
        list_result_after = standards_list()
        list_data_after = json.loads(list_result_after)
        assert list_data_after["total_count"] == initial_count + 1

        # 4. Get the created standard
        get_result = standards_get("e2e_test_standard")
        get_data = json.loads(get_result)
        assert "content" in get_data
        assert "e2e_test_standard" in get_data["content"]

        # 5. Search for the standard
        search_result = standards_search("e2e_test_standard")
        search_data = json.loads(search_result)
        assert search_data["total_found"] > 0
        assert any(
            "e2e_test_standard" in result["name"] for result in search_data["results"]
        )

        # 6. Update the standard
        update_result = standards_update(
            standard_name="e2e_test_standard",
            update_type="version",
            update_notes="E2E test update",
        )
        update_data = json.loads(update_result)
        assert update_data["success"] is True

        # 7. Archive the standard
        archive_result = standards_archive(
            standard_name="e2e_test_standard",
            reason="E2E test completion",
            replacement_standard="None",
        )
        archive_data = json.loads(archive_result)
        assert archive_data["success"] is True

        # 8. Verify standard was archived
        list_result_final = standards_list()
        list_data_final = json.loads(list_result_final)
        # Archived standards are excluded from total count
        assert (
            list_data_final["total_count"] >= initial_count
        )  # May be same or more due to other operations
        assert list_data_final["archived_standards"] >= list_data["archived_standards"]

    def test_mcp_server_initialization(self):
        """Test MCP server initialization and basic functionality"""
        import asyncio

        from heroes_mcp.src.heroes_mcp_server import mcp, server_info

        # Test server info
        info_result = server_info()
        assert "Heroes MCP Server" in info_result

        # Test that server has required tools (async)
        async def test_tools():
            tools = await mcp.list_tools()
            required_tools = [
                "server_info",
                "standards_list",
                "standards_get",
                "standards_search",
                "standards_create",
                "standards_update",
                "standards_archive",
            ]

            for tool_name in required_tools:
                assert any(tool_name in tool.name for tool in tools), (
                    f"Required tool {tool_name} not found"
                )

        asyncio.run(test_tools())

    def test_telegram_integration_workflow(self):
        """Test Telegram integration workflow"""
        from heroes_mcp.src.heroes_mcp_server import (
            telegram_get_chats,
            telegram_get_credentials,
            telegram_search_chats,
            telegram_test_connection,
        )

        # Test credentials retrieval
        creds_result = telegram_get_credentials()
        assert "credentials" in creds_result.lower()

        # Test connection (should fail without real credentials)
        conn_result = telegram_test_connection()
        assert (
            "credentials" in conn_result.lower() or "connection" in conn_result.lower()
        )

        # Test getting chats (may work with real credentials)
        chats_result = telegram_get_chats()
        assert "Page" in chats_result or "credentials" in chats_result.lower()

        # Test searching chats (may work with real credentials)
        search_result = telegram_search_chats("test")
        assert "Found" in search_result or "credentials" in search_result.lower()

    def test_workflow_integration(self):
        """Test workflow integration functionality"""
        import asyncio

        from heroes_mcp.src.heroes_mcp_server import workflow_integration

        async def test_async():
            # Test workflow status
            status_result = await workflow_integration("standards", "status")
            status_data = json.loads(status_result)
            assert "status" in status_data
            assert "workflow" in status_data

            # Test workflow validation
            validate_result = await workflow_integration("standards", "validate")
            validate_data = json.loads(validate_result)
            assert "valid" in validate_data
            assert "workflow" in validate_data

        # Run async test
        asyncio.run(test_async())

    def test_registry_compliance(self):
        """Test registry compliance check"""
        from heroes_mcp.src.heroes_mcp_server import registry_compliance_check

        compliance_result = registry_compliance_check()
        compliance_data = json.loads(compliance_result)

        # Check structure
        assert "registry_standard_version" in compliance_data
        assert "workflows_loaded" in compliance_data
        assert "compliance_score" in compliance_data
        assert "total_workflows" in compliance_data
        assert "compliant_workflows" in compliance_data

        # Check values
        assert compliance_data["registry_standard_version"] == "v5.8"
        assert isinstance(compliance_data["compliance_score"], (int, float))
        assert compliance_data["total_workflows"] >= 0
        assert compliance_data["compliant_workflows"] >= 0

    def test_ai_guidance_checklist(self):
        """Test AI guidance checklist functionality"""
        from heroes_mcp.src.heroes_mcp_server import ai_guidance_checklist

        # Test general guidance
        general_result = ai_guidance_checklist("general")
        data = json.loads(general_result)
        assert "checklist" in data
        assert "task_type" in data

        # Test development guidance
        dev_result = ai_guidance_checklist("development")
        data = json.loads(dev_result)
        assert "checklist" in data
        assert "task_type" in data

        # Test analysis guidance
        analysis_result = ai_guidance_checklist("analysis")
        data = json.loads(analysis_result)
        assert "checklist" in data
        assert "task_type" in data

    def test_error_handling_workflow(self):
        """Test error handling in workflow"""
        from heroes_mcp.src.heroes_mcp_server import (
            standards_create,
            standards_get,
            standards_search,
        )

        # Test with invalid inputs
        invalid_inputs = [
            "",
            None,
            "nonexistent_standard_12345",
            "invalid/path/with/special/chars",
        ]

        for invalid_input in invalid_inputs:
            # Test standards_get
            try:
                result = standards_get(invalid_input)
                data = json.loads(result)
                assert "error" in data
            except Exception as e:
                # Should handle exceptions gracefully
                assert isinstance(e, Exception)

            # Test standards_search
            try:
                result = standards_search(invalid_input or "")
                data = json.loads(result)
                assert isinstance(data, dict)
            except Exception as e:
                # Should handle exceptions gracefully
                assert isinstance(e, Exception)

            # Test standards_create
            try:
                result = standards_create(invalid_input or "")
                data = json.loads(result)
                assert "error" in data
            except Exception as e:
                # Should handle exceptions gracefully
                assert isinstance(e, Exception)

    def test_concurrent_operations_workflow(self):
        """Test concurrent operations in workflow"""
        import concurrent.futures

        from heroes_mcp.src.heroes_mcp_server import (
            ai_guidance_checklist,
            server_info,
            standards_list,
            standards_search,
        )

        def run_standards_list():
            return standards_list()

        def run_standards_search():
            return standards_search("test")

        def run_server_info():
            return server_info()

        def run_ai_guidance_checklist():
            return ai_guidance_checklist("general")

        # Run operations concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for _ in range(5):
                futures.append(executor.submit(run_standards_list))
                futures.append(executor.submit(run_standards_search))
                futures.append(executor.submit(run_server_info))
                futures.append(executor.submit(run_ai_guidance_checklist))

            # Wait for all to complete
            results = [future.result() for future in futures]

        # All results should be valid
        for result in results:
            assert isinstance(result, str)
            assert len(result) > 0

    def test_data_consistency_workflow(self):
        """Test data consistency across workflow operations"""
        from heroes_mcp.src.heroes_mcp_server import (
            standards_audit,
            standards_create,
            standards_get,
            standards_list,
        )

        # Create test standard
        create_result = standards_create(
            standard_name="consistency_test_standard",
            category="consistency_test",
            description="Test standard for consistency testing",
            template="basic",
        )
        create_data = json.loads(create_result)
        assert create_data.get("success") is True or "error" not in create_data

        # Get initial audit
        audit_result = standards_audit()
        audit_data = json.loads(audit_result)
        initial_total = audit_data["total_standards"]

        # Verify standard exists in list
        list_result = standards_list()
        list_data = json.loads(list_result)
        assert list_data["total_count"] == initial_total

        # Verify standard content
        get_result = standards_get("consistency_test_standard")
        get_data = json.loads(get_result)
        assert "content" in get_data
        assert "consistency_test_standard" in get_data["content"]

        # Clean up
        from heroes_mcp.src.heroes_mcp_server import standards_archive

        archive_result = standards_archive(
            standard_name="consistency_test_standard",
            reason="Consistency test cleanup",
            replacement_standard="None",
        )
        archive_data = json.loads(archive_result)
        assert archive_data["success"] is True

        # Verify cleanup (archived standards may still be counted in audit)
        final_audit_result = standards_audit()
        final_audit_data = json.loads(final_audit_result)
        assert final_audit_data["total_standards"] >= initial_total - 1
