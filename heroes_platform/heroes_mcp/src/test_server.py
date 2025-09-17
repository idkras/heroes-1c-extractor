#!/usr/bin/env python3
"""
Test script for MCP server
"""

import json
import subprocess
import time


def test_mcp_server():
    """Test MCP server with proper JSON-RPC sequence"""

    # Start the server process
    process = subprocess.Popen(
        ["python3", "mcp_server_standard.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        # Test 1: Initialize
        print("=== Test 1: Initialize ===")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0"},
            },
        }

        print(f"Sending: {json.dumps(init_request)}")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()

        # Read response
        response = process.stdout.readline()
        print(f"Received: {response.strip()}")

        # Wait a bit
        time.sleep(1)

        # Test 2: Send initialized notification
        print("\n=== Test 2: Initialized notification ===")
        init_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {},
        }

        print(f"Sending: {json.dumps(init_notification)}")
        process.stdin.write(json.dumps(init_notification) + "\n")
        process.stdin.flush()

        # Wait a bit
        time.sleep(1)

        # Test 3: List tools
        print("\n=== Test 3: List tools ===")
        list_tools_request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}

        print(f"Sending: {json.dumps(list_tools_request)}")
        process.stdin.write(json.dumps(list_tools_request) + "\n")
        process.stdin.flush()

        # Read response
        response = process.stdout.readline()
        print(f"Received: {response.strip()}")

        # Test 4: Call a tool
        print("\n=== Test 4: Call tool ===")
        call_tool_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "standards_management",
                "arguments": {"command": "get_standards"},
            },
        }

        print(f"Sending: {json.dumps(call_tool_request)}")
        process.stdin.write(json.dumps(call_tool_request) + "\n")
        process.stdin.flush()

        # Read response
        response = process.stdout.readline()
        print(f"Received: {response.strip()}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        process.terminate()
        process.wait()
        print("\n=== Test completed ===")


if __name__ == "__main__":
    test_mcp_server()
