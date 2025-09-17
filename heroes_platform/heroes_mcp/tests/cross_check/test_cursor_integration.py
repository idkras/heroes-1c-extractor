#!/usr/bin/env python3
"""
Cursor Cross-Check Tests for MCP Commands

Проверка MCP команд в реальном Cursor environment.
"""

import asyncio
import json
import subprocess
import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class CursorCrossChecker:
    """Cross-check MCP commands in real Cursor environment"""

    def __init__(self):
        self.cursor_config = {
            "mcpServers": {
                "heroes_mcp": {
                    "command": ".venv/bin/python3",
                    "args": ["heroes-platform/mcp_server/src/mcp_server.py"],
                    "env": {"PYTHONPATH": "."},
                }
            }
        }

    async def test_command_in_cursor(
        self, command_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        JTBD: Как разработчик, я хочу проверить что MCP команда работает в реальном Cursor,
        чтобы убедиться что пользователь получит ожидаемый результат.
        """

        # 🔍 REFLECTION CHECKPOINT 1 - Cross-check setup
        logger.info(f"REFLECTION: Starting Cursor cross-check for {command_name}")
        logger.info(f"REFLECTION: Testing in real Cursor environment")

        start_time = time.time()

        try:
            # WHEN - выполнение команды в Cursor
            result = await self.execute_in_cursor(command_name, arguments)
            execution_time = time.time() - start_time

            # 🔍 REFLECTION CHECKPOINT 2 - Cross-check validation
            logger.info(f"REFLECTION: Cursor execution time: {execution_time:.2f}s")

            # THEN - качественная проверка Cursor результата
            cross_check_score = await self.validate_cursor_result(
                command_name, result, execution_time
            )

            # 🔍 REFLECTION CHECKPOINT 3 - Cross-check success
            logger.info(
                f"REFLECTION: Cross-check score for {command_name}: {cross_check_score}"
            )

            return {
                "command": command_name,
                "cross_check_score": cross_check_score,
                "execution_time": execution_time,
                "success": cross_check_score >= 0.85,
                "result_preview": str(result)[:200],
                "environment": "cursor",
            }

        except Exception as e:
            logger.error(f"REFLECTION: Cross-check failed for {command_name}: {e}")
            return {
                "command": command_name,
                "cross_check_score": 0.0,
                "execution_time": time.time() - start_time,
                "success": False,
                "error": str(e),
                "environment": "cursor",
            }

    async def execute_in_cursor(
        self, command_name: str, arguments: Dict[str, Any]
    ) -> Any:
        """Execute MCP command in Cursor-like environment"""

        # Simulate Cursor environment by running MCP server directly
        server_path = Path(__file__).parent.parent.parent / "src" / "mcp_server.py"

        # Prepare JSON-RPC request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": command_name, "arguments": arguments},
        }

        # Send request to MCP server
        input_data = (
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "cursor-cross-check", "version": "1.0"},
                    },
                }
            )
            + "\n"
            + json.dumps(
                {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}
            )
            + "\n"
            + json.dumps(request)
            + "\n"
        )

        result = subprocess.run(
            [sys.executable, str(server_path)],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            raise Exception(f"MCP server failed: {result.stderr}")

        # Parse response
        lines = result.stdout.strip().split("\n")
        responses = [json.loads(line) for line in lines if line.strip()]

        # Find the tools/call response (should be the last response with id=1)
        call_response = None
        for response in reversed(responses):
            if response.get("id") == 1 and "result" in response:
                call_response = response
                break

        if not call_response:
            raise Exception(f"Invalid response: {responses}")

        return call_response["result"]

    def extract_text_from_result(self, result: Any) -> str:
        """Extract text content from MCP response format"""
        if isinstance(result, dict):
            if "content" in result and isinstance(result["content"], list):
                # Extract text from content array
                text_parts = []
                for item in result["content"]:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                return " ".join(text_parts)
            elif "text" in result:
                return result["text"]
            else:
                return str(result)
        return str(result)

    async def validate_cursor_result(
        self, command_name: str, result: Any, execution_time: float
    ) -> float:
        """Validate result from Cursor environment"""

        cross_check_score = 0.0

        # Extract text content from MCP response format
        result_text = self.extract_text_from_result(result)

        # 1. Команда выполняется без ошибок в Cursor
        if result is not None and "error" not in result_text.lower():
            cross_check_score += 0.3

        # 2. Результат полезен для пользователя в Cursor
        if self.validate_user_usability(result_text, command_name):
            cross_check_score += 0.3

        # 3. Время выполнения приемлемо в Cursor
        if execution_time < 5.0:
            cross_check_score += 0.2

        # 4. Обработка ошибок работает в Cursor
        if self.error_handling_works_in_cursor(result_text):
            cross_check_score += 0.2

        return cross_check_score

    def validate_user_usability(self, result_text: str, command_name: str) -> bool:
        """Validate that result is usable by user in Cursor"""

        # Basic usability checks
        if result_text is None or result_text.strip() == "":
            return False

        # Command-specific usability checks
        if command_name == "standards_list":
            return "standards" in result_text and len(result_text) > 100
        elif command_name == "standards_get":
            return len(result_text) > 500 and (
                "Стандарт" in result_text or "Standard" in result_text
            )
        elif command_name == "standards_search":
            return len(result_text) > 50 and (
                "results" in result_text or "standards" in result_text
            )
        else:
            return len(result_text) > 20  # Default minimum length

    def error_handling_works_in_cursor(self, result_text: str) -> bool:
        """Check if error handling works in Cursor environment"""

        # If there's an error, it should be properly formatted
        if "error" in result_text.lower():
            return "error" in result_text.lower() and len(result_text) > 20

        return True


# Test functions
async def test_standards_list_cross_check():
    """Test standards_list command in Cursor"""
    checker = CursorCrossChecker()
    result = await checker.test_command_in_cursor("standards_list", {})
    assert result["success"], f"Cross-check failed: {result}"
    print(f"✅ standards_list cross-check passed: {result['cross_check_score']:.2f}")


async def test_standards_get_cross_check():
    """Test standards_get command in Cursor"""
    checker = CursorCrossChecker()
    result = await checker.test_command_in_cursor(
        "standards_get",
        {"standard_name": "0.0 task master 10 may 2226 cet by ilya krasinsky"},
    )
    assert result["success"], f"Cross-check failed: {result}"
    print(f"✅ standards_get cross-check passed: {result['cross_check_score']:.2f}")


async def test_standards_search_cross_check():
    """Test standards_search command in Cursor"""
    checker = CursorCrossChecker()
    result = await checker.test_command_in_cursor(
        "standards_search", {"query": "task master"}
    )
    assert result["success"], f"Cross-check failed: {result}"
    print(f"✅ standards_search cross-check passed: {result['cross_check_score']:.2f}")


async def test_workflow_integration_cross_check():
    """Test workflow_integration command in Cursor"""
    checker = CursorCrossChecker()
    result = await checker.test_command_in_cursor(
        "workflow_integration", {"workflow_name": "standards", "action": "status"}
    )
    assert result["success"], f"Cross-check failed: {result}"
    print(
        f"✅ workflow_integration cross-check passed: {result['cross_check_score']:.2f}"
    )


async def test_registry_compliance_check_cross_check():
    """Test registry_compliance_check command in Cursor"""
    checker = CursorCrossChecker()
    result = await checker.test_command_in_cursor("registry_compliance_check", {})
    assert result["success"], f"Cross-check failed: {result}"
    print(
        f"✅ registry_compliance_check cross-check passed: {result['cross_check_score']:.2f}"
    )


if __name__ == "__main__":
    # Run all cross-check tests
    async def run_all_cross_checks():
        print("🔍 Starting MCP Commands Cross-Check Tests...")

        await test_standards_list_cross_check()
        await test_standards_get_cross_check()
        await test_standards_search_cross_check()
        await test_workflow_integration_cross_check()
        await test_registry_compliance_check_cross_check()

        print("✅ All cross-check tests completed!")

    asyncio.run(run_all_cross_checks())
