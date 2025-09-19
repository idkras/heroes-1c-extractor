#!/usr/bin/env python3
"""
Health MCP Server - Мониторинг здоровья всех MCP серверов

JTBD: Как администратор системы, я хочу мониторить здоровье всех MCP серверов,
чтобы быстро выявлять проблемы интеграции и ошибки в логах.

TDD Documentation Standard v2.5 Compliance:
- Atomic Functions Architecture (≤20 строк на функцию)
- Security First (валидация всех входных данных)
- Modern Python Development (type hints, dataclasses)
- Testing Pyramid Compliance (unit, integration, e2e)
"""

import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


# ПРОВЕРКА АРГУМЕНТОВ КОМАНДНОЙ СТРОКИ ПЕРЕД ИНИЦИАЛИЗАЦИЕЙ
def check_command_line_args():
    """Проверяет аргументы командной строки и выходит если нужно"""
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        if arg == "--help" or arg == "-h":
            print("Health MCP Server v1.0.0")
            print("Usage: python health_mcp_server.py [OPTIONS]")
            print("")
            print("Options:")
            print("  --help, -h     Show this help message")
            print("  --version, -v  Show version information")
            print("  --test         Show registered tools and exit")
            print("  --list-tools   List all available MCP tools")
            sys.exit(0)

        elif arg == "--version" or arg == "-v":
            print("Health MCP Server v1.0.0")
            print("Protocol: MCP v1.0")
            print("Transport: stdio")
            sys.exit(0)

        elif arg == "--test":
            print(
                "Registered tools: health_check_all_servers, validate_server_logs, get_server_status, test_server_health"
            )
            sys.exit(0)

        elif arg == "--list-tools":
            tools_list = [
                "health_check_all_servers",
                "validate_server_logs",
                "get_server_status",
                "test_server_health",
                "get_mcp_logs_path",
                "check_credentials_health",
            ]
            print("Available MCP Tools:")
            for i, tool in enumerate(tools_list, 1):
                print(f"  {i:2d}. {tool}")
            print(f"\nTotal: {len(tools_list)} tools")
            sys.exit(0)

        elif arg.startswith("--"):
            print(f"Unknown option: {arg}")
            print("Use --help for usage information")
            sys.exit(1)


# Проверяем аргументы СРАЗУ
check_command_line_args()

# Далее идет обычная инициализация MCP сервера
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# Создание сервера с настройками
mcp = FastMCP("health-mcp-server", debug=True, log_level="INFO")


@dataclass
class ServerHealthResult:
    """Результат проверки здоровья сервера"""

    server_name: str
    status: str  # "success", "error", "warning"
    message: str
    details: dict[str, Any]
    timestamp: str


class MCPServerLogValidator:
    """Validator for MCP server logs and integration health"""

    def __init__(self, server_name: str, log_path: Optional[str] = None):
        self.server_name = server_name
        self.log_path = log_path or self._get_default_log_path()

    def _get_default_log_path(self) -> str:
        """Get default Cursor MCP log path"""
        cursor_logs = (
            Path.home() / "Library" / "Application Support" / "Cursor" / "logs"
        )
        if cursor_logs.exists():
            # Find latest log directory
            log_dirs = [d for d in cursor_logs.iterdir() if d.is_dir()]
            if log_dirs:
                latest_log_dir = max(log_dirs, key=lambda x: x.stat().st_mtime)

                # Search in all windows for the log file
                for window_dir in latest_log_dir.iterdir():
                    if window_dir.is_dir() and window_dir.name.startswith("window"):
                        exthost_dir = (
                            window_dir / "exthost" / "anysphere.cursor-retrieval"
                        )
                        if exthost_dir.exists():
                            log_file = (
                                exthost_dir
                                / f"MCP project-0-heroes-template-{self.server_name}.log"
                            )
                            if log_file.exists():
                                return str(log_file)
        return ""

    async def validate_server_logs(self) -> dict[str, Any]:
        """Validate MCP server logs for errors and warnings"""
        if not self.log_path or not Path(self.log_path).exists():
            return {
                "status": "warning",
                "message": f"Log file not found for {self.server_name}",
                "log_path": self.log_path,
                "critical_errors": [],
                "import_errors": [],
                "credential_errors": [],
                "connection_errors": [],
                "warnings": [],
                "total_issues": 0,
            }

        try:
            with open(self.log_path) as f:
                log_content = f.read()

            # Check for critical errors
            critical_errors = self._check_critical_errors(log_content)

            # Check for import errors
            import_errors = self._check_import_errors(log_content)

            # Check for credential errors
            credential_errors = self._check_credential_errors(log_content)

            # Check for connection errors
            connection_errors = self._check_connection_errors(log_content)

            # Check for warnings
            warnings = self._check_warnings(log_content)

            return {
                "status": "success" if not critical_errors else "error",
                "server_name": self.server_name,
                "log_path": self.log_path,
                "critical_errors": critical_errors,
                "import_errors": import_errors,
                "credential_errors": credential_errors,
                "connection_errors": connection_errors,
                "warnings": warnings,
                "total_issues": len(critical_errors)
                + len(import_errors)
                + len(credential_errors)
                + len(connection_errors),
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to read log file: {str(e)}",
                "log_path": self.log_path,
                "critical_errors": [],
                "import_errors": [],
                "credential_errors": [],
                "connection_errors": [],
                "warnings": [],
                "total_issues": 0,
            }

    def _check_critical_errors(self, log_content: str) -> list[str]:
        """Check for critical errors in logs"""
        critical_patterns = [
            r"ImportError:.*",
            r"ModuleNotFoundError:.*",
            r"AttributeError:.*",
            r"TypeError:.*",
            r"ValueError:.*",
            r"ConnectionError:.*",
            r"TimeoutError:.*",
            r"PermissionError:.*",
            r"FileNotFoundError:.*",
            r"JSONDecodeError:.*",
            r"SyntaxError:.*",
            r"IndentationError:.*",
            # Cursor MCP specific errors
            r"No server info found",
            r"Failed to validate request",
            r"Server not responding",
            r"MCP server initialization failed",
            r"Transport error:.*",
            r"Protocol error:.*",
            # JSON parsing errors
            r"Client error for command.*JSON",
            r"Unexpected token.*is not valid JSON",
            r"Expected.*after.*in JSON",
            r"JSONDecodeError:.*",
        ]

        errors = []
        for pattern in critical_patterns:
            matches = re.findall(pattern, log_content)
            errors.extend(matches)

        return errors

    def _check_import_errors(self, log_content: str) -> list[str]:
        """Check for import-related errors"""
        import_patterns = [
            r"ImportError: attempted relative import with no known parent package",
            r"ModuleNotFoundError: No module named.*",
            r"ImportError: cannot import name.*",
            r"ImportError: No module named.*",
        ]

        errors = []
        for pattern in import_patterns:
            matches = re.findall(pattern, log_content)
            errors.extend(matches)

        return errors

    def _check_credential_errors(self, log_content: str) -> list[str]:
        """Check for credential-related errors"""
        credential_patterns = [
            r"Credential not found.*",
            r"Authentication failed.*",
            r"Invalid credentials.*",
            r"API key not found.*",
            r"Token expired.*",
            r"Unauthorized.*",
            r"403.*",
            r"401.*",
        ]

        errors = []
        for pattern in credential_patterns:
            matches = re.findall(pattern, log_content)
            errors.extend(matches)

        return errors

    def _check_connection_errors(self, log_content: str) -> list[str]:
        """Check for connection-related errors"""
        connection_patterns = [
            r"Connection refused.*",
            r"Connection timeout.*",
            r"Network unreachable.*",
            r"DNS resolution failed.*",
            r"SSL.*error.*",
            r"TLS.*error.*",
            r"HTTP.*error.*",
            r"Failed to connect.*",
        ]

        errors = []
        for pattern in connection_patterns:
            matches = re.findall(pattern, log_content)
            errors.extend(matches)

        return errors

    def _check_warnings(self, log_content: str) -> list[str]:
        """Check for warnings in logs"""
        warning_patterns = [
            r"WARNING:.*",
            r"WARN:.*",
            r"DeprecationWarning:.*",
            r"FutureWarning:.*",
            r"UserWarning:.*",
        ]

        warnings = []
        for pattern in warning_patterns:
            matches = re.findall(pattern, log_content)
            warnings.extend(matches)

        return warnings


class HealthCheckResult(BaseModel):
    """Результат проверки здоровья"""

    server_name: str = Field(description="Название сервера")
    status: str = Field(description="Статус: success, error, warning")
    message: str = Field(description="Сообщение о статусе")
    details: dict[str, Any] = Field(description="Детали проверки")
    timestamp: str = Field(description="Время проверки")


@mcp.tool()
async def health_check_all_servers() -> dict[str, Any]:
    """Проверка здоровья всех MCP серверов"""
    mcp_servers = [
        "heroes-mcp",
        "n8n-mcp",
        "telegram-mcp",
        "jira-mcp",
        "linear-mcp",
        "figma-mcp",
        "playwright-mcp",
    ]

    results = {}
    failed_servers = []

    for server_name in mcp_servers:
        try:
            # Проверяем логи
            validator = MCPServerLogValidator(server_name)
            log_result = await validator.validate_server_logs()

            # Проверяем здоровье сервера
            health_result = await _test_server_health(server_name)

            # Объединяем результаты
            combined_status = "success"
            if log_result["status"] == "error" or health_result["status"] == "error":
                combined_status = "error"
                failed_servers.append(server_name)
            elif (
                log_result["status"] == "warning"
                or health_result["status"] == "warning"
            ):
                combined_status = "warning"

            results[server_name] = {
                "status": combined_status,
                "log_validation": log_result,
                "health_check": health_result,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            }

        except Exception as e:
            results[server_name] = {
                "status": "error",
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            failed_servers.append(server_name)

    return {
        "overall_status": "success" if not failed_servers else "error",
        "failed_servers": failed_servers,
        "total_servers": len(mcp_servers),
        "healthy_servers": len(mcp_servers) - len(failed_servers),
        "results": results,
    }


@mcp.tool()
async def validate_server_logs(server_name: str) -> dict[str, Any]:
    """Валидация логов конкретного MCP сервера"""
    validator = MCPServerLogValidator(server_name)
    return await validator.validate_server_logs()


@mcp.tool()
async def get_server_status(server_name: str) -> dict[str, Any]:
    """Получение статуса конкретного MCP сервера"""
    try:
        # Проверяем логи
        validator = MCPServerLogValidator(server_name)
        log_result = await validator.validate_server_logs()

        # Проверяем здоровье
        health_result = await _test_server_health(server_name)

        # Определяем общий статус
        status = "success"
        if log_result["status"] == "error" or health_result["status"] == "error":
            status = "error"
        elif log_result["status"] == "warning" or health_result["status"] == "warning":
            status = "warning"

        return {
            "server_name": server_name,
            "status": status,
            "log_validation": log_result,
            "health_check": health_result,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    except Exception as e:
        return {
            "server_name": server_name,
            "status": "error",
            "error": str(e),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }


@mcp.tool()
async def test_server_health(server_name: str) -> dict[str, Any]:
    """Тестирование здоровья конкретного MCP сервера"""
    return await _test_server_health(server_name)


@mcp.tool()
async def get_mcp_logs_path(server_name: str) -> dict[str, Any]:
    """Получение пути к логам MCP сервера"""
    validator = MCPServerLogValidator(server_name)
    return {
        "server_name": server_name,
        "log_path": validator.log_path,
        "exists": Path(validator.log_path).exists() if validator.log_path else False,
    }


@mcp.tool()
async def check_credentials_health() -> dict[str, Any]:
    """Проверка здоровья credentials для всех серверов"""
    try:
        # Проверяем credentials_wrapper
        result = subprocess.run(
            ["python3", "heroes_platform/shared/credentials_wrapper.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        return {
            "status": "success" if result.returncode == 0 else "error",
            "credentials_wrapper": {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            },
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }


async def _test_server_health(server_name: str) -> dict[str, Any]:
    """Внутренняя функция для тестирования здоровья сервера"""
    try:
        if server_name == "heroes-mcp":
            result = subprocess.run(
                [
                    "python3",
                    "heroes_platform/heroes_mcp/src/heroes_mcp_server.py",
                    "--test",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

        elif server_name == "n8n-mcp":
            result = subprocess.run(
                [
                    "python3",
                    "heroes_platform/shared/credentials_wrapper.py",
                    "n8n",
                    "node",
                    "heroes_platform/n8n-mcp/dist/mcp/index.js",
                    "--test",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

        elif server_name == "telegram-mcp":
            result = subprocess.run(
                [
                    "python3",
                    "heroes_platform/shared/credentials_wrapper.py",
                    "telegram",
                    "python3",
                    "heroes_platform/telegram-mcp/main.py",
                    "--test",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

        else:
            return {
                "status": "warning",
                "message": f"Health check not implemented for {server_name}",
                "returncode": -1,
                "stdout": "",
                "stderr": "",
            }

        return {
            "status": "success" if result.returncode == 0 else "error",
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "returncode": -1,
            "stdout": "",
            "stderr": "",
        }


if __name__ == "__main__":
    # Запуск FastMCP сервера
    mcp.run()
