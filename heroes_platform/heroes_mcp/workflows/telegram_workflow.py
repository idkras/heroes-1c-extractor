#!/usr/bin/env python3
"""
Telegram Workflow for MCP Server
Handles Telegram operations using telegram-mcp integration
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class TelegramWorkflow:
    """Telegram workflow for MCP server"""

    def __init__(self) -> None:
        """Initialize Telegram workflow"""
        # Use relative path to telegram-mcp in current project
        self.telegram_mcp_path = Path("telegram-mcp/")
        self.session_file = self.telegram_mcp_path / "session.json"
        self.cache: dict[str, Any] = {}
        self.cache_ttl = 300  # 5 minutes

    async def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute Telegram workflow command"""
        command = arguments.get("command", "")

        try:
            if command == "validate_telegram_session":
                return await self.validate_telegram_session(arguments)
            elif command == "get_telegram_chats":
                return await self.get_telegram_chats(arguments)
            elif command == "extract_chat_messages":
                return await self.extract_chat_messages(arguments)
            elif command == "export_chat_to_md":
                return await self.export_chat_to_md(arguments)
            elif command == "get_unread_messages":
                return await self.get_unread_messages(arguments)
            elif command == "analyze_channel_activity":
                return await self.analyze_channel_activity(arguments)
            elif command == "setup_telegram_session":
                return await self.setup_telegram_session(arguments)
            else:
                return {"success": False, "error": f"Unknown command: {command}"}
        except Exception as e:
            return {"success": False, "error": f"Telegram workflow error: {str(e)}"}

    async def validate_telegram_session(
        self, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate Telegram session using telegram-mcp"""
        try:
            start_time = time.time()

            # Check if telegram-mcp is available
            if not self.telegram_mcp_path.exists():
                return {
                    "success": False,
                    "error": "telegram-mcp not found. Please ensure it's installed in heroes-platform/telegram-mcp/",
                }

            # Test connection by getting chats
            result = await self._run_telegram_mcp_command(
                "get_chats", {"page": 1, "page_size": 1}
            )
            execution_time = time.time() - start_time

            if result["success"]:
                return {
                    "success": True,
                    "data": {
                        "session_valid": True,
                        "telegram_mcp_available": True,
                        "execution_time": round(execution_time, 2),
                    },
                }
            else:
                return {
                    "success": False,
                    "error": f"Session validation failed: {result['error']}",
                    "data": {
                        "session_valid": False,
                        "telegram_mcp_available": True,
                        "execution_time": round(execution_time, 2),
                    },
                }

        except Exception as e:
            execution_time = time.time() - start_time if "start_time" in locals() else 0
            return {
                "success": False,
                "error": f"Session validation failed: {str(e)}",
                "data": {
                    "session_valid": False,
                    "telegram_mcp_available": False,
                    "execution_time": round(execution_time, 2),
                },
            }

    async def get_telegram_chats(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Get list of all Telegram chats using telegram-mcp"""
        try:
            start_time = time.time()
            page = arguments.get("page", 1)
            page_size = arguments.get("page_size", 50)

            result = await self._run_telegram_mcp_command(
                "get_chats", {"page": page, "page_size": page_size}
            )
            execution_time = time.time() - start_time

            if result["success"]:
                # Parse the output to extract chat information
                chats_data: list[Any] = []
                lines = result["data"].split("\n")

                for line in lines:
                    if line.strip() and "ID:" in line:
                        try:
                            # Extract chat ID and name from line
                            parts = line.split(" - ")
                            if len(parts) >= 2:
                                chat_id = parts[0].replace("ID:", "").strip()
                                chat_name = parts[1].strip()
                                chats_data.append(
                                    {
                                        "id": chat_id,
                                        "name": chat_name,
                                        "type": (
                                            "channel"
                                            if chat_id.startswith("-100")
                                            else "chat"
                                        ),
                                    }
                                )
                        except Exception as e:
                            logger.warning(
                                f"Failed to parse chat line: {line}, error: {e}"
                            )

                return {
                    "success": True,
                    "data": {
                        "chats": chats_data,
                        "total_count": len(chats_data),
                        "page": page,
                        "page_size": page_size,
                        "execution_time": round(execution_time, 2),
                    },
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to get chats: {result['error']}",
                    "execution_time": round(execution_time, 2),
                }

        except Exception as e:
            execution_time = time.time() - start_time if "start_time" in locals() else 0
            return {
                "success": False,
                "error": f"Error getting chats: {str(e)}",
                "execution_time": round(execution_time, 2),
            }

    async def extract_chat_messages(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Extract messages from a specific chat"""
        try:
            start_time = time.time()
            chat_id = arguments.get("chat_id")
            limit = arguments.get("limit", 10)

            if not chat_id:
                return {"success": False, "error": "chat_id is required"}

            result = await self._run_telegram_mcp_command(
                "get_messages", {"chat_id": chat_id, "limit": limit}
            )
            execution_time = time.time() - start_time

            if result["success"]:
                return {
                    "success": True,
                    "data": {
                        "chat_id": chat_id,
                        "messages": result["data"],
                        "limit": limit,
                        "execution_time": round(execution_time, 2),
                    },
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to extract messages: {result['error']}",
                    "execution_time": round(execution_time, 2),
                }

        except Exception as e:
            execution_time = time.time() - start_time if "start_time" in locals() else 0
            return {
                "success": False,
                "error": f"Error extracting messages: {str(e)}",
                "execution_time": round(execution_time, 2),
            }

    async def export_chat_to_md(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Export chat messages to markdown format"""
        try:
            start_time = time.time()
            chat_id = arguments.get("chat_id")
            limit = arguments.get("limit", 50)

            if not chat_id:
                return {"success": False, "error": "chat_id is required"}

            # Get messages first
            messages_result = await self.extract_chat_messages(
                {"chat_id": chat_id, "limit": limit}
            )

            if not messages_result["success"]:
                return messages_result

            # Convert to markdown
            markdown_content = self._convert_messages_to_markdown(
                messages_result["data"]["messages"], chat_id
            )

            execution_time = time.time() - start_time

            return {
                "success": True,
                "data": {
                    "chat_id": chat_id,
                    "markdown_content": markdown_content,
                    "limit": limit,
                    "execution_time": round(execution_time, 2),
                },
            }

        except Exception as e:
            execution_time = time.time() - start_time if "start_time" in locals() else 0
            return {
                "success": False,
                "error": f"Error exporting chat: {str(e)}",
                "execution_time": round(execution_time, 2),
            }

    async def get_unread_messages(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Get unread messages from chats"""
        try:
            start_time = time.time()
            limit = arguments.get("limit", 20)

            result = await self._run_telegram_mcp_command(
                "get_unread", {"limit": limit}
            )
            execution_time = time.time() - start_time

            if result["success"]:
                return {
                    "success": True,
                    "data": {
                        "unread_messages": result["data"],
                        "limit": limit,
                        "execution_time": round(execution_time, 2),
                    },
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to get unread messages: {result['error']}",
                    "execution_time": round(execution_time, 2),
                }

        except Exception as e:
            execution_time = time.time() - start_time if "start_time" in locals() else 0
            return {
                "success": False,
                "error": f"Error getting unread messages: {str(e)}",
                "execution_time": round(execution_time, 2),
            }

    async def analyze_channel_activity(
        self, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze channel activity and engagement"""
        try:
            start_time = time.time()
            chat_id = arguments.get("chat_id")
            days = arguments.get("days", 7)

            if not chat_id:
                return {"success": False, "error": "chat_id is required"}

            # Get messages for analysis
            messages_result = await self.extract_chat_messages(
                {"chat_id": chat_id, "limit": 100}  # Get more messages for analysis
            )

            if not messages_result["success"]:
                return messages_result

            # Analyze activity
            analysis = self._analyze_messages_activity(
                messages_result["data"]["messages"], days
            )

            execution_time = time.time() - start_time

            return {
                "success": True,
                "data": {
                    "chat_id": chat_id,
                    "analysis": analysis,
                    "days": days,
                    "execution_time": round(execution_time, 2),
                },
            }

        except Exception as e:
            execution_time = time.time() - start_time if "start_time" in locals() else 0
            return {
                "success": False,
                "error": f"Error analyzing channel activity: {str(e)}",
                "execution_time": round(execution_time, 2),
            }

    async def setup_telegram_session(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Setup Telegram session"""
        try:
            start_time = time.time()

            # Check if session file exists
            if self.session_file.exists():
                return {
                    "success": True,
                    "data": {
                        "session_exists": True,
                        "session_file": str(self.session_file),
                        "message": "Session already exists",
                        "execution_time": round(time.time() - start_time, 2),
                    },
                }

            # Initialize session
            result = await self._run_telegram_mcp_command("init_session", {})
            execution_time = time.time() - start_time

            if result["success"]:
                return {
                    "success": True,
                    "data": {
                        "session_created": True,
                        "session_file": str(self.session_file),
                        "message": "Session initialized successfully",
                        "execution_time": round(execution_time, 2),
                    },
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to setup session: {result['error']}",
                    "execution_time": round(execution_time, 2),
                }

        except Exception as e:
            execution_time = time.time() - start_time if "start_time" in locals() else 0
            return {
                "success": False,
                "error": f"Error setting up session: {str(e)}",
                "execution_time": round(execution_time, 2),
            }

    async def _run_telegram_mcp_command(
        self, command: str, args: dict[str, Any]
    ) -> dict[str, Any]:
        """Run telegram-mcp command with error handling"""
        try:
            # Prepare command
            cmd = [
                "python3",
                str(self.telegram_mcp_path / "main.py"),
                command,
                json.dumps(args),
            ]

            # Run command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.telegram_mcp_path),
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                return {"success": True, "data": stdout.decode().strip()}
            else:
                return {
                    "success": False,
                    "error": stderr.decode().strip() or "Unknown error",
                }

        except Exception as e:
            return {"success": False, "error": f"Command execution failed: {str(e)}"}

    def _convert_messages_to_markdown(self, messages: str, chat_id: str) -> str:
        """Convert messages to markdown format"""
        try:
            # Simple conversion - can be enhanced
            lines = messages.split("\n")
            markdown_lines = [f"# Chat Export - {chat_id}\n"]

            for line in lines:
                if line.strip():
                    markdown_lines.append(f"- {line}")

            return "\n".join(markdown_lines)
        except Exception as e:
            logger.error(f"Error converting to markdown: {e}")
            return f"# Chat Export - {chat_id}\n\nError converting messages: {str(e)}"

    def _analyze_messages_activity(self, messages: str, days: int) -> dict[str, Any]:
        """Analyze message activity patterns"""
        try:
            lines = messages.split("\n")
            total_messages = len([line for line in lines if line.strip()])

            return {
                "total_messages": total_messages,
                "average_per_day": round(total_messages / days, 2),
                "analysis_period_days": days,
                "activity_level": (
                    "high"
                    if total_messages > 50
                    else "medium"
                    if total_messages > 20
                    else "low"
                ),
            }
        except Exception as e:
            logger.error(f"Error analyzing activity: {e}")
            return {"error": f"Analysis failed: {str(e)}", "total_messages": 0}
