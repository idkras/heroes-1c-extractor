#!/usr/bin/env python3
"""
Health Check Test for MCP Server

Проверяет работоспособность MCP сервера и его интеграцию с Cursor.
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

import pytest

# Path configuration
SERVER_PATH = Path(__file__).parent.parent.parent / "src" / "mcp_server.py"


class MCPHealthChecker:
    """Health checker for MCP server"""

    def __init__(self, server_path: Path):
        self.server_path = server_path
        self.process = None

    async def check_server_startup(self) -> bool:
        """Check if server starts correctly"""
        try:
            # Test mode check
            result = subprocess.run(
                [sys.executable, str(self.server_path), "--test"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0 and "Registered tools:" in result.stdout
        except Exception as e:
            print(f"Server startup check failed: {e}")
            return False

    async def check_json_rpc_protocol(self) -> bool:
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
                    "clientInfo": {"name": "health-check", "version": "1.0"},
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

        except Exception as e:
            print(f"JSON-RPC protocol check failed: {e}")
            return False

    async def check_cursor_integration(self) -> bool:
        """Check Cursor integration readiness"""
        try:
            # Check if server can handle Cursor-style requests
            cursor_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": "server_info", "arguments": {}},
            }

            # Send initialize first
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

            # Check if we got a valid response
            lines = result.stdout.strip().split("\n")
            responses = [json.loads(line) for line in lines if line.strip()]

            call_response = next((r for r in responses if r.get("id") == 1), None)
            return call_response is not None and "result" in call_response

        except Exception as e:
            print(f"Cursor integration check failed: {e}")
            return False


@pytest.mark.asyncio
async def test_mcp_server_health():
    """Comprehensive health check for MCP server"""
    checker = MCPHealthChecker(SERVER_PATH)

    # Check 1: Server startup
    startup_ok = await checker.check_server_startup()
    assert startup_ok, "MCP server failed to start in test mode"

    # Check 2: JSON-RPC protocol
    protocol_ok = await checker.check_json_rpc_protocol()
    assert protocol_ok, "MCP server failed JSON-RPC protocol check"

    # Check 3: Cursor integration
    cursor_ok = await checker.check_cursor_integration()
    assert cursor_ok, "MCP server failed Cursor integration check"

    print("✅ All health checks passed!")


@pytest.mark.asyncio
async def test_mcp_server_tools_availability():
    """Check that all required tools are available"""
    MCPHealthChecker(SERVER_PATH)

    # Get tools list
    tools_request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}

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
        + json.dumps(
            {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}
        )
        + "\n"
        + json.dumps(tools_request)
        + "\n"
    )

    result = subprocess.run(
        [sys.executable, str(SERVER_PATH)],
        input=input_data,
        capture_output=True,
        text=True,
        timeout=15,
    )

    assert result.returncode == 0, "Failed to get tools list"

    # Parse response
    lines = result.stdout.strip().split("\n")
    responses = [json.loads(line) for line in lines if line.strip()]

    tools_response = next((r for r in responses if r.get("id") == 2), None)
    assert tools_response is not None, "No tools response received"

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
    assert not missing_tools, f"Missing required tools: {missing_tools}"

    print(f"✅ All {len(required_tools)} required tools are available")


if __name__ == "__main__":
    # Run health checks
    asyncio.run(test_mcp_server_health())
    asyncio.run(test_mcp_server_tools_availability())
