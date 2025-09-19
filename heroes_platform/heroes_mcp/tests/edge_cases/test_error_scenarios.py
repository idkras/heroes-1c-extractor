#!/usr/bin/env python3
"""
Edge Cases and Error Scenarios Tests for MCP Server

Тестирование граничных случаев и сценариев ошибок для MCP сервера.
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from cross_check.test_cursor_integration import CursorCrossChecker
from quality.test_mcp_commands_quality import MCPCommandQualityTester


class EdgeCaseTester:
    """Tester for edge cases and error scenarios"""

    def __init__(self):
        self.quality_tester = MCPCommandQualityTester()
        self.cross_checker = CursorCrossChecker()
        self.server_path = Path(__file__).parent.parent.parent / "src" / "mcp_server.py"

    async def test_large_data_handling(self) -> dict[str, Any]:
        """Test handling of large data volumes"""

        # Test with large standard name
        large_standard_name = "a" * 1000
        result = await self.cross_checker.test_command_in_cursor(
            "standards_get", {"standard_name": large_standard_name}
        )

        # Should handle gracefully, not crash
        assert result["success"] or "error" in str(result["result_preview"]).lower()

        return {"test": "large_data_handling", "passed": True, "result": result}

    async def test_malformed_inputs(self) -> dict[str, Any]:
        """Test handling of malformed inputs"""

        # Test with None values
        result_none = await self.cross_checker.test_command_in_cursor(
            "standards_get", {"standard_name": None}
        )

        # Test with empty string
        result_empty = await self.cross_checker.test_command_in_cursor(
            "standards_get", {"standard_name": ""}
        )

        # Test with special characters
        result_special = await self.cross_checker.test_command_in_cursor(
            "standards_get", {"standard_name": "!@#$%^&*()"}
        )

        # All should handle gracefully
        results = [result_none, result_empty, result_special]
        all_handled = all(
            r["success"] or "error" in str(r["result_preview"]).lower() for r in results
        )

        return {"test": "malformed_inputs", "passed": all_handled, "results": results}

    async def test_concurrent_requests(self) -> dict[str, Any]:
        """Test handling of concurrent requests"""

        async def make_request(command_name: str, arguments: dict) -> dict:
            return await self.cross_checker.test_command_in_cursor(
                command_name, arguments
            )

        # Make multiple concurrent requests
        tasks = [
            make_request("standards_list", {}),
            make_request(
                "standards_get",
                {"standard_name": "0.0 task master 10 may 2226 cet by ilya krasinsky"},
            ),
            make_request("standards_search", {"query": "task"}),
            make_request(
                "workflow_integration",
                {"workflow_name": "standards", "action": "status"},
            ),
            make_request("registry_compliance_check", {}),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check that all requests completed (even if some failed)
        all_completed = all(not isinstance(r, Exception) for r in results)

        return {
            "test": "concurrent_requests",
            "passed": all_completed,
            "results": results,
        }

    async def test_server_stress(self) -> dict[str, Any]:
        """Test server under stress conditions"""

        start_time = time.time()

        # Make many rapid requests
        requests = []
        for i in range(10):
            requests.append(
                self.cross_checker.test_command_in_cursor("standards_list", {})
            )

        results = await asyncio.gather(*requests, return_exceptions=True)

        end_time = time.time()
        total_time = end_time - start_time

        # Check performance and stability
        successful_requests = sum(1 for r in results if not isinstance(r, Exception))
        avg_time_per_request = total_time / len(requests)

        # Should complete within reasonable time and maintain stability
        performance_ok = avg_time_per_request < 2.0  # Less than 2 seconds per request
        stability_ok = (
            successful_requests >= len(requests) * 0.8
        )  # At least 80% success

        return {
            "test": "server_stress",
            "passed": performance_ok and stability_ok,
            "total_time": total_time,
            "avg_time_per_request": avg_time_per_request,
            "successful_requests": successful_requests,
            "total_requests": len(requests),
        }

    async def test_invalid_json_rpc(self) -> dict[str, Any]:
        """Test handling of invalid JSON-RPC requests"""

        # Test with malformed JSON
        malformed_json = (
            '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {'
        )

        try:
            result = subprocess.run(
                [sys.executable, str(self.server_path)],
                input=malformed_json,
                capture_output=True,
                text=True,
                timeout=10,
            )

            # Should handle gracefully, not crash
            handled_gracefully = result.returncode == 0

            return {
                "test": "invalid_json_rpc",
                "passed": handled_gracefully,
                "returncode": result.returncode,
                "stderr": result.stderr[:200] if result.stderr else None,
            }

        except Exception as e:
            return {"test": "invalid_json_rpc", "passed": False, "error": str(e)}

    async def run_all_edge_case_tests(self) -> dict[str, Any]:
        """Run all edge case tests"""

        print("🔍 Starting Edge Cases and Error Scenarios Tests...")

        tests = [
            self.test_large_data_handling(),
            self.test_malformed_inputs(),
            self.test_concurrent_requests(),
            self.test_server_stress(),
            self.test_invalid_json_rpc(),
        ]

        results = await asyncio.gather(*tests, return_exceptions=True)

        # Process results
        test_results = {}
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                test_results[f"test_{i}"] = {"passed": False, "error": str(result)}
            else:
                test_results[result["test"]] = result

        # Calculate overall success
        passed_tests = sum(1 for r in test_results.values() if r.get("passed", False))
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

        print("📊 Edge Cases Test Results:")
        print(f"Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")

        for test_name, result in test_results.items():
            status = "✅ PASSED" if result.get("passed", False) else "❌ FAILED"
            print(f"  {test_name}: {status}")

        return {
            "success_rate": success_rate,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "results": test_results,
        }


async def main():
    """Main entry point"""
    tester = EdgeCaseTester()
    results = await tester.run_all_edge_case_tests()

    if results["success_rate"] >= 80:
        print("🎉 Edge cases tests PASSED - Server handles errors gracefully!")
    else:
        print("⚠️ Edge cases tests FAILED - Server needs improvement in error handling")


if __name__ == "__main__":
    asyncio.run(main())
