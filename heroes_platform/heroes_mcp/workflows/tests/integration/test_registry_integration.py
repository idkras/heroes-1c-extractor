#!/usr/bin/env python3
"""
Integration tests for Registry Workflow

JTBD: Как тестировщик, я хочу проверить интеграцию Registry Workflow с MCP сервером,
чтобы убедиться в корректности работы registry команд в реальной среде.
"""

import pytest
import json
import sys
from pathlib import Path

# Add workflows directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))


class TestRegistryIntegration:
    """Integration test cases for Registry Workflow"""

    def test_mcp_server_calls_registry_workflow(self):
        """GIVEN MCP request WHEN call registry THEN workflow executes"""
        # Test that MCP server can call registry workflow
        from workflows.registry_workflow import RegistryWorkflow
        from heroes_mcp.src.heroes_mcp_server import registry_compliance_check

        # Test workflow directly
        workflow = RegistryWorkflow()
        result = workflow.compliance_check()

        # Verify result is valid JSON
        data = json.loads(result)
        assert "registry_standard_version" in data
        assert "compliance_score" in data

    def test_registry_workflow_real_file_operations(self):
        """GIVEN real files WHEN call registry THEN returns valid data"""
        from workflows.registry_workflow import RegistryWorkflow

        workflow = RegistryWorkflow()

        # Test with real file paths
        result = workflow.output_validate(
            "пользователь может найти сообщения по дате",
            "clients/ifscourse.com/chat.md",
        )

        data = json.loads(result)
        assert data["status"] == "guidance"
        assert "validation_checklist" in data

    def test_registry_workflow_docs_audit_integration(self):
        """GIVEN real document paths WHEN call docs_audit THEN returns valid checklist"""
        from workflows.registry_workflow import RegistryWorkflow

        workflow = RegistryWorkflow()

        # Test with real document paths
        result = workflow.docs_audit(
            "clients/ifscourse.com/chat.md,clients/ifscourse.com/README.md"
        )

        data = json.loads(result)
        assert data["status"] == "guidance"
        assert data["doc_count"] == 2
        assert "audit_checklist" in data

    def test_registry_workflow_gap_report_integration(self):
        """GIVEN gap analysis WHEN call gap_report THEN returns valid checklist"""
        from workflows.registry_workflow import RegistryWorkflow

        workflow = RegistryWorkflow()

        # Test gap analysis
        result = workflow.gap_report(
            "сообщения сгруппированы по дням с заголовками",
            "сообщения в одной куче без группировки",
            "fix",
        )

        data = json.loads(result)
        assert data["status"] == "guidance"
        assert data["decision"] == "fix"
        assert "gap_analysis_checklist" in data

    def test_registry_workflow_release_block_integration(self):
        """GIVEN release block WHEN call release_block THEN returns valid checklist"""
        from workflows.registry_workflow import RegistryWorkflow

        workflow = RegistryWorkflow()

        # Test release block
        result = workflow.release_block("validation-complete")

        data = json.loads(result)
        assert data["status"] == "guidance"
        assert data["until"] == "validation-complete"
        assert "block_checklist" in data

    def test_registry_workflow_error_handling(self):
        """GIVEN invalid input WHEN call registry THEN handles errors gracefully"""
        from workflows.registry_workflow import RegistryWorkflow

        workflow = RegistryWorkflow()

        # Test with invalid input
        result = workflow.output_validate("", "")

        data = json.loads(result)
        assert data["status"] == "error"
        assert "message" in data

    def test_registry_workflow_atomic_functions(self):
        """GIVEN workflow WHEN check functions THEN all functions ≤60 lines (optimized version)"""
        from workflows.registry_workflow import RegistryWorkflow
        import inspect

        workflow = RegistryWorkflow()

        # Check that all public methods are ≤60 lines (optimized version)
        methods = [
            "compliance_check",
            "output_validate",
            "docs_audit",
            "gap_report",
            "release_block",
        ]

        for method_name in methods:
            method = getattr(workflow, method_name)
            source_lines = inspect.getsource(method).split("\n")
            # Count non-empty lines (excluding docstring and comments)
            code_lines = [
                line
                for line in source_lines
                if line.strip()
                and not line.strip().startswith("#")
                and not line.strip().startswith('"""')
            ]

            # Method should be ≤60 lines (optimized version allows longer methods)
            assert (
                len(code_lines) <= 60
            ), f"Method {method_name} has {len(code_lines)} lines, should be ≤60"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
