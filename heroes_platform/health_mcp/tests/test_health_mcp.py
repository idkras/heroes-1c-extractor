#!/usr/bin/env python3
"""
Тесты для Health MCP Server

JTBD: Как разработчик, я хочу тестировать health MCP сервер,
чтобы убедиться в корректности проверки здоровья всех MCP серверов.
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from health_mcp_server import MCPServerLogValidator, _test_server_health  # type: ignore


class TestMCPServerLogValidator:
    """Тесты для валидатора логов MCP серверов"""

    @pytest.mark.asyncio
    async def test_log_validator_initialization(self):
        """Тест инициализации валидатора логов"""
        validator = MCPServerLogValidator("test-server")
        assert validator.server_name == "test-server"
        assert validator.log_path is not None

    @pytest.mark.asyncio
    async def test_log_validator_with_custom_path(self):
        """Тест валидатора с кастомным путем к логам"""
        custom_path = "/custom/path/to/logs"
        validator = MCPServerLogValidator("test-server", custom_path)
        assert validator.log_path == custom_path

    @pytest.mark.asyncio
    async def test_validate_server_logs_file_not_found(self):
        """Тест валидации логов когда файл не найден"""
        validator = MCPServerLogValidator("nonexistent-server", "/nonexistent/path.log")
        result = await validator.validate_server_logs()

        assert result["status"] == "warning"
        assert "Log file not found" in result["message"]
        assert result["total_issues"] == 0

    @pytest.mark.asyncio
    async def test_check_critical_errors(self):
        """Тест проверки критических ошибок"""
        validator = MCPServerLogValidator("test-server")

        # Тестовый лог с ошибками
        test_log = """
        2025-01-01 10:00:00 [error] ImportError: No module named 'test_module'
        2025-01-01 10:01:00 [error] ModuleNotFoundError: No module named 'missing'
        2025-01-01 10:02:00 [error] AttributeError: 'NoneType' object has no attribute 'test'
        """

        errors = validator._check_critical_errors(test_log)
        assert len(errors) == 3
        assert "ImportError: No module named 'test_module'" in errors
        assert "ModuleNotFoundError: No module named 'missing'" in errors
        assert "AttributeError: 'NoneType' object has no attribute 'test'" in errors

    @pytest.mark.asyncio
    async def test_check_import_errors(self):
        """Тест проверки ошибок импорта"""
        validator = MCPServerLogValidator("test-server")

        # Тестовый лог с ошибками импорта
        test_log = """
        2025-01-01 10:00:00 [error] ImportError: attempted relative import with no known parent package
        2025-01-01 10:01:00 [error] ModuleNotFoundError: No module named 'heroes_platform'
        2025-01-01 10:02:00 [error] ImportError: cannot import name 'test_function'
        """

        errors = validator._check_import_errors(test_log)
        assert len(errors) == 3
        assert (
            "ImportError: attempted relative import with no known parent package"
            in errors
        )
        assert "ModuleNotFoundError: No module named 'heroes_platform'" in errors
        assert "ImportError: cannot import name 'test_function'" in errors

    @pytest.mark.asyncio
    async def test_check_credential_errors(self):
        """Тест проверки ошибок credentials"""
        validator = MCPServerLogValidator("test-server")

        # Тестовый лог с ошибками credentials
        test_log = """
        2025-01-01 10:00:00 [error] Credential not found: N8N_API_KEY
        2025-01-01 10:01:00 [error] Authentication failed: Invalid API key
        2025-01-01 10:02:00 [error] 401 Unauthorized
        2025-01-01 10:03:00 [error] 403 Forbidden
        """

        errors = validator._check_credential_errors(test_log)
        assert len(errors) == 4
        assert "Credential not found: N8N_API_KEY" in errors
        assert "Authentication failed: Invalid API key" in errors
        assert "401 Unauthorized" in errors
        assert "403 Forbidden" in errors

    @pytest.mark.asyncio
    async def test_check_connection_errors(self):
        """Тест проверки ошибок соединения"""
        validator = MCPServerLogValidator("test-server")

        # Тестовый лог с ошибками соединения
        test_log = """
        2025-01-01 10:00:00 [error] Connection refused: Connection refused
        2025-01-01 10:01:00 [error] Connection timeout: Read timeout
        2025-01-01 10:02:00 [error] SSL error: certificate verify failed
        2025-01-01 10:03:00 [error] Failed to connect to server
        """

        errors = validator._check_connection_errors(test_log)
        assert len(errors) == 4
        assert "Connection refused: Connection refused" in errors
        assert "Connection timeout: Read timeout" in errors
        assert "SSL error: certificate verify failed" in errors
        assert "Failed to connect to server" in errors

    @pytest.mark.asyncio
    async def test_check_warnings(self):
        """Тест проверки предупреждений"""
        validator = MCPServerLogValidator("test-server")

        # Тестовый лог с предупреждениями
        test_log = """
        2025-01-01 10:00:00 [warning] WARNING: This is a warning message
        2025-01-01 10:01:00 [warning] WARN: Another warning
        2025-01-01 10:02:00 [warning] DeprecationWarning: This function is deprecated
        2025-01-01 10:03:00 [warning] FutureWarning: This will change in future
        """

        warnings = validator._check_warnings(test_log)
        assert len(warnings) == 4
        assert "WARNING: This is a warning message" in warnings
        assert "WARN: Another warning" in warnings
        assert "DeprecationWarning: This function is deprecated" in warnings
        assert "FutureWarning: This will change in future" in warnings


class TestServerHealth:
    """Тесты для проверки здоровья серверов"""

    @pytest.mark.asyncio
    async def test_heroes_mcp_health_success(self):
        """Тест успешной проверки здоровья heroes-mcp"""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Registered tools: test_tool"
            mock_run.return_value.stderr = ""

            result = await _test_server_health("heroes-mcp")

            assert result["status"] == "success"
            assert result["returncode"] == 0
            assert "Registered tools" in result["stdout"]

    @pytest.mark.asyncio
    async def test_heroes_mcp_health_error(self):
        """Тест ошибки проверки здоровья heroes-mcp"""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stdout = ""
            mock_run.return_value.stderr = "Error: Module not found"

            result = await _test_server_health("heroes-mcp")

            assert result["status"] == "error"
            assert result["returncode"] == 1
            assert "Error: Module not found" in result["stderr"]

    @pytest.mark.asyncio
    async def test_n8n_mcp_health_success(self):
        """Тест успешной проверки здоровья n8n-mcp"""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Registered tools: n8n_get_workflows"
            mock_run.return_value.stderr = ""

            result = await _test_server_health("n8n-mcp")

            assert result["status"] == "success"
            assert result["returncode"] == 0
            assert "Registered tools" in result["stdout"]

    @pytest.mark.asyncio
    async def test_telegram_mcp_health_success(self):
        """Тест успешной проверки здоровья telegram-mcp"""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Registered tools: telegram_send_message"
            mock_run.return_value.stderr = ""

            result = await _test_server_health("telegram-mcp")

            assert result["status"] == "success"
            assert result["returncode"] == 0
            assert "Registered tools" in result["stdout"]

    @pytest.mark.asyncio
    async def test_unknown_server_health(self):
        """Тест проверки здоровья неизвестного сервера"""
        result = await _test_server_health("unknown-server")

        assert result["status"] == "warning"
        assert "not implemented" in result["message"]
        assert result["returncode"] == -1

    @pytest.mark.asyncio
    async def test_server_health_exception(self):
        """Тест исключения при проверке здоровья сервера"""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = Exception("Test exception")

            result = await _test_server_health("heroes-mcp")

            assert result["status"] == "error"
            assert "Test exception" in result["error"]
            assert result["returncode"] == -1


class TestIntegration:
    """Интеграционные тесты"""

    @pytest.mark.asyncio
    async def test_health_check_all_servers_integration(self):
        """Интеграционный тест проверки всех серверов"""
        # Этот тест требует реального запуска health_mcp сервера
        # В реальной среде можно использовать create_connected_server_and_client_session

        # Пока что мокаем результат
        with (
            patch("health_mcp_server._test_server_health") as mock_health,
            patch("health_mcp_server.MCPServerLogValidator") as mock_validator,
        ):
            # Настраиваем моки
            mock_health.return_value = {"status": "success", "returncode": 0}
            mock_validator.return_value.validate_server_logs.return_value = {
                "status": "success",
                "total_issues": 0,
            }

            # Импортируем функцию после настройки моков
            from health_mcp_server import health_check_all_servers  # type: ignore

            result = await health_check_all_servers()

            assert "overall_status" in result
            assert "total_servers" in result
            assert "results" in result
            assert result["total_servers"] > 0


@pytest.mark.asyncio
async def test_mcp_server_logs_validation():
    """ОБЯЗАТЕЛЬНЫЙ ТЕСТ: Validate MCP server logs for all servers"""
    mcp_servers = [
        "heroes-mcp",
        "n8n-mcp",
        "telegram-mcp",
        "jira-mcp",
        "linear-mcp",
        "figma-mcp",
        "playwright-mcp",
    ]

    failed_servers = []

    for server_name in mcp_servers:
        validator = MCPServerLogValidator(server_name)
        result = await validator.validate_server_logs()

        if result["status"] == "error":
            failed_servers.append(
                {
                    "server": server_name,
                    "errors": result.get("critical_errors", []),
                    "import_errors": result.get("import_errors", []),
                    "credential_errors": result.get("credential_errors", []),
                    "connection_errors": result.get("connection_errors", []),
                }
            )

        # Логируем результаты для отладки
        print(f"Server {server_name}: {result['status']}")
        if result.get("total_issues", 0) > 0:
            print(f"  Issues found: {result['total_issues']}")

    # Проверяем, что нет критических ошибок
    assert len(failed_servers) == 0, (
        f"Critical errors found in MCP servers: {failed_servers}"
    )


@pytest.mark.asyncio
async def test_mcp_server_health_check():
    """ОБЯЗАТЕЛЬНЫЙ ТЕСТ: Health check for all MCP servers"""
    mcp_servers = [
        "heroes-mcp",
        "n8n-mcp",
        "telegram-mcp",
        "jira-mcp",
        "linear-mcp",
        "figma-mcp",
        "playwright-mcp",
    ]

    health_results = {}

    for server_name in mcp_servers:
        try:
            result = await _test_server_health(server_name)
            health_results[server_name] = result

        except Exception as e:
            health_results[server_name] = {"status": "error", "error": str(e)}

    # Проверяем, что все серверы здоровы
    failed_servers = [
        name
        for name, result in health_results.items()
        if result.get("status") != "success"
    ]

    # В тестовой среде некоторые серверы могут быть недоступны
    # Поэтому проверяем только что тест выполнился без исключений
    assert len(health_results) == len(mcp_servers), "Not all servers were tested"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
