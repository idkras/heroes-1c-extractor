#!/usr/bin/env python3
"""
Integration tests for CocoIndex commands

Тесты интеграции для CocoIndex команд.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


class TestCocoIndexCommands:
    """Test class for CocoIndex commands integration"""

    def __init__(self):
        self.server_path = Path(__file__).parent.parent.parent / "src" / "mcp_server.py"

    def test_cocoindex_search_existing_files(self) -> dict[str, Any]:
        """Test cocoindex_search_existing_files command"""

        # Prepare JSON-RPC requests sequence
        initialize_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"},
            },
        }

        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {},
        }

        tools_call_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "cocoindex_search_existing_files",
                "arguments": {"query": "test", "confidence_threshold": 0.6},
            },
        }

        # Send requests sequence to server
        input_data = (
            json.dumps(initialize_request)
            + "\n"
            + json.dumps(initialized_notification)
            + "\n"
            + json.dumps(tools_call_request)
            + "\n"
        )

        try:
            result = subprocess.run(
                [sys.executable, str(self.server_path)],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Parse response
            if result.returncode == 0 and result.stdout:
                lines = result.stdout.strip().split("\n")
                for line in lines:
                    if line.startswith('{"jsonrpc"'):
                        response = json.loads(line)
                        if response.get("id") == 2 and "result" in response:
                            return {
                                "test": "cocoindex_search_existing_files",
                                "passed": True,
                                "result": response["result"],
                            }

            return {
                "test": "cocoindex_search_existing_files",
                "passed": False,
                "error": "No valid response received",
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

        except Exception as e:
            return {
                "test": "cocoindex_search_existing_files",
                "passed": False,
                "error": str(e),
            }

    def test_cocoindex_validate_file_creation(self) -> dict[str, Any]:
        """Test cocoindex_validate_file_creation command"""

        # Prepare JSON-RPC requests sequence
        initialize_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"},
            },
        }

        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {},
        }

        tools_call_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "cocoindex_validate_file_creation",
                "arguments": {
                    "file_path": "test_file.py",
                    "content": "def test_function():\n    pass",
                },
            },
        }

        # Send requests sequence to server
        input_data = (
            json.dumps(initialize_request)
            + "\n"
            + json.dumps(initialized_notification)
            + "\n"
            + json.dumps(tools_call_request)
            + "\n"
        )

        try:
            result = subprocess.run(
                [sys.executable, str(self.server_path)],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Parse response
            if result.returncode == 0 and result.stdout:
                lines = result.stdout.strip().split("\n")
                for line in lines:
                    if line.startswith('{"jsonrpc"'):
                        response = json.loads(line)
                        if response.get("id") == 2 and "result" in response:
                            return {
                                "test": "cocoindex_validate_file_creation",
                                "passed": True,
                                "result": response["result"],
                            }

            return {
                "test": "cocoindex_validate_file_creation",
                "passed": False,
                "error": "No valid response received",
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

        except Exception as e:
            return {
                "test": "cocoindex_validate_file_creation",
                "passed": False,
                "error": str(e),
            }

    def test_cocoindex_get_functionality_map(self) -> dict[str, Any]:
        """Test cocoindex_get_functionality_map command"""

        # Prepare JSON-RPC requests sequence
        initialize_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"},
            },
        }

        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {},
        }

        tools_call_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "cocoindex_get_functionality_map", "arguments": {}},
        }

        # Send requests sequence to server
        input_data = (
            json.dumps(initialize_request)
            + "\n"
            + json.dumps(initialized_notification)
            + "\n"
            + json.dumps(tools_call_request)
            + "\n"
        )

        try:
            result = subprocess.run(
                [sys.executable, str(self.server_path)],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Parse response
            if result.returncode == 0 and result.stdout:
                lines = result.stdout.strip().split("\n")
                for line in lines:
                    if line.startswith('{"jsonrpc"'):
                        response = json.loads(line)
                        if response.get("id") == 2 and "result" in response:
                            return {
                                "test": "cocoindex_get_functionality_map",
                                "passed": True,
                                "result": response["result"],
                            }

            return {
                "test": "cocoindex_get_functionality_map",
                "passed": False,
                "error": "No valid response received",
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

        except Exception as e:
            return {
                "test": "cocoindex_get_functionality_map",
                "passed": False,
                "error": str(e),
            }

    def test_cocoindex_analyze_duplicates(self) -> dict[str, Any]:
        """Test cocoindex_analyze_duplicates command"""

        # Prepare JSON-RPC requests sequence
        initialize_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"},
            },
        }

        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {},
        }

        tools_call_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "cocoindex_analyze_duplicates", "arguments": {}},
        }

        # Send requests sequence to server
        input_data = (
            json.dumps(initialize_request)
            + "\n"
            + json.dumps(initialized_notification)
            + "\n"
            + json.dumps(tools_call_request)
            + "\n"
        )

        try:
            result = subprocess.run(
                [sys.executable, str(self.server_path)],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Parse response
            if result.returncode == 0 and result.stdout:
                lines = result.stdout.strip().split("\n")
                for line in lines:
                    if line.startswith('{"jsonrpc"'):
                        response = json.loads(line)
                        if response.get("id") == 2 and "result" in response:
                            return {
                                "test": "cocoindex_analyze_duplicates",
                                "passed": True,
                                "result": response["result"],
                            }

            return {
                "test": "cocoindex_analyze_duplicates",
                "passed": False,
                "error": "No valid response received",
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

        except Exception as e:
            return {
                "test": "cocoindex_analyze_duplicates",
                "passed": False,
                "error": str(e),
            }

    def run_all_tests(self) -> dict[str, Any]:
        """Run all CocoIndex command tests"""

        print("🔍 Testing CocoIndex Commands Integration...")

        tests = [
            self.test_cocoindex_search_existing_files(),
            self.test_cocoindex_validate_file_creation(),
            self.test_cocoindex_get_functionality_map(),
            self.test_cocoindex_analyze_duplicates(),
        ]

        # Process results
        passed_tests = sum(1 for test in tests if test.get("passed", False))
        total_tests = len(tests)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

        print("📊 CocoIndex Commands Test Results:")
        print(f"Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")

        for test in tests:
            status = "✅ PASSED" if test.get("passed", False) else "❌ FAILED"
            print(f"  {test['test']}: {status}")
            if not test.get("passed", False):
                print(f"    Error: {test.get('error', 'Unknown error')}")

        return {
            "success_rate": success_rate,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "results": tests,
        }


def main():
    """Main entry point"""
    tester = TestCocoIndexCommands()
    results = tester.run_all_tests()

    if results["success_rate"] >= 80:
        print("🎉 CocoIndex commands integration tests PASSED!")
    else:
        print("⚠️ CocoIndex commands integration tests FAILED!")


if __name__ == "__main__":
    main()
