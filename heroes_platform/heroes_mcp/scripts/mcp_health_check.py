#!/usr/bin/env python3
"""
MCP Server Health Check Script

Автоматический мониторинг MCP сервера с уведомлениями и автоматическим восстановлением.
"""

import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# Path configuration
SERVER_PATH = Path(__file__).parent.parent / "src" / "mcp_server.py"


class MCPHealthMonitor:
    """Health monitor for MCP server"""

    def __init__(self, server_path: Path):
        self.server_path = server_path
        self.last_check = None
        self.failure_count = 0
        self.max_failures = 3

    async def check_server_health(self) -> dict[str, Any]:
        """Comprehensive health check"""
        start_time = time.time()

        try:
            # Test 1: Server startup
            startup_ok = await self._check_startup()

            # Test 2: JSON-RPC protocol
            protocol_ok = await self._check_protocol()

            # Test 3: Tools availability
            tools_ok = await self._check_tools()

            # Test 4: Cursor integration
            cursor_ok = await self._check_cursor_integration()

            # Calculate overall health
            all_tests_passed = all([startup_ok, protocol_ok, tools_ok, cursor_ok])

            if all_tests_passed:
                self.failure_count = 0
                status = "healthy"
            else:
                self.failure_count += 1
                status = "unhealthy"

            check_time = time.time() - start_time

            result = {
                "timestamp": time.time(),
                "status": status,
                "check_time": check_time,
                "failure_count": self.failure_count,
                "tests": {
                    "startup": startup_ok,
                    "protocol": protocol_ok,
                    "tools": tools_ok,
                    "cursor_integration": cursor_ok,
                },
                "details": {
                    "server_path": str(self.server_path),
                    "python_version": sys.version,
                },
            }

            self.last_check = result  # type: ignore
            return result

        except Exception as e:
            self.failure_count += 1
            return {
                "timestamp": time.time(),
                "status": "error",
                "error": str(e),
                "failure_count": self.failure_count,
            }

    async def _check_startup(self) -> bool:
        """Check if server starts correctly"""
        try:
            # Send initialize request to test startup
            input_data = (
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "initialize",
                        "params": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {},
                            "clientInfo": {"name": "health-check", "version": "1.0"},
                        },
                    }
                )
                + "\n"
            )

            result = subprocess.run(
                [sys.executable, str(self.server_path)],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=10,
            )

            # Check if server responds to initialize
            return result.returncode == 0 and "result" in result.stdout
        except Exception:
            return False

    async def _check_protocol(self) -> bool:
        """Check JSON-RPC protocol compliance"""
        try:
            # Initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "health-monitor", "version": "1.0"},
                },
            }

            # Tools list request
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {},
            }

            # Send requests in sequence
            input_data = (
                json.dumps(init_request)
                + "\n"
                + json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "method": "notifications/initialized",
                        "params": {},
                    }
                )
                + "\n"
                + json.dumps(tools_request)
                + "\n"
            )

            result = subprocess.run(
                [sys.executable, str(self.server_path)],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=15,
            )

            if result.returncode != 0:
                return False

            # Parse responses
            lines = result.stdout.strip().split("\n")
            responses = [json.loads(line) for line in lines if line.strip()]

            # Check initialize response
            init_response = next((r for r in responses if r.get("id") == 1), None)
            if not init_response or "result" not in init_response:
                return False

            # Check tools list response
            tools_response = next((r for r in responses if r.get("id") == 2), None)
            if not tools_response or "result" not in tools_response:
                return False

            tools = tools_response["result"].get("tools", [])
            return len(tools) > 0

        except Exception:
            return False

    async def _check_tools(self) -> bool:
        """Check that required tools are available"""
        try:
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {},
            }

            input_data = (
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "initialize",
                        "params": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {},
                            "clientInfo": {"name": "health-monitor", "version": "1.0"},
                        },
                    }
                )
                + "\n"
                + json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "method": "notifications/initialized",
                        "params": {},
                    }
                )
                + "\n"
                + json.dumps(tools_request)
                + "\n"
            )

            result = subprocess.run(
                [sys.executable, str(self.server_path)],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=15,
            )

            if result.returncode != 0:
                return False

            # Parse response
            lines = result.stdout.strip().split("\n")
            responses = [json.loads(line) for line in lines if line.strip()]

            tools_response = next((r for r in responses if r.get("id") == 2), None)
            if not tools_response:
                return False

            tools = tools_response["result"].get("tools", [])
            tool_names = [tool["name"] for tool in tools]

            # Required tools
            required_tools = [
                "server_info",
                "standards_list",
                "standards_get",
                "standards_search",
                "workflow_integration",
                "registry_compliance_check",
            ]

            missing_tools = [tool for tool in required_tools if tool not in tool_names]
            return len(missing_tools) == 0

        except Exception:
            return False

    async def _check_cursor_integration(self) -> bool:
        """Check Cursor integration readiness"""
        try:
            cursor_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": "server_info", "arguments": {}},
            }

            init_data = (
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "initialize",
                        "params": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {},
                            "clientInfo": {"name": "cursor", "version": "1.0"},
                        },
                    }
                )
                + "\n"
                + json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "method": "notifications/initialized",
                        "params": {},
                    }
                )
                + "\n"
                + json.dumps(cursor_request)
                + "\n"
            )

            result = subprocess.run(
                [sys.executable, str(self.server_path)],
                input=init_data,
                capture_output=True,
                text=True,
                timeout=15,
            )

            if result.returncode != 0:
                return False

            lines = result.stdout.strip().split("\n")
            responses = [json.loads(line) for line in lines if line.strip()]

            call_response = next((r for r in responses if r.get("id") == 1), None)
            return call_response is not None and "result" in call_response

        except Exception:
            return False

    def should_restart(self) -> bool:
        """Check if server should be restarted"""
        return self.failure_count >= self.max_failures

    def get_status_summary(self) -> str:
        """Get human-readable status summary"""
        if not self.last_check:
            return "No health check performed yet"

        status = self.last_check["status"]
        tests = self.last_check.get("tests", {})

        summary = f"Status: {status.upper()}"
        if status == "healthy":
            summary += " ✅"
        else:
            summary += " ❌"

        summary += f"\nFailure count: {self.failure_count}"
        summary += "\nTests:"
        for test_name, passed in tests.items():
            summary += f"\n  {test_name}: {'✅' if passed else '❌'}"

        return summary


async def main():
    """Main health check function"""
    monitor = MCPHealthMonitor(SERVER_PATH)

    print("🔍 MCP Server Health Check")
    print("=" * 50)

    # Perform health check
    result = await monitor.check_server_health()

    # Print results
    print(monitor.get_status_summary())
    print(f"\nCheck time: {result.get('check_time', 0):.2f}s")

    # Check if restart is needed
    if monitor.should_restart():
        print("\n🚨 CRITICAL: Server needs restart!")
        print(f"Failure count: {monitor.failure_count}")
        return 1

    # Return appropriate exit code
    return 0 if result["status"] == "healthy" else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
