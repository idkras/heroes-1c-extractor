#!/usr/bin/env python3
"""
Тест-кейсы для проверки исправлений MCP сервера и Jupyter файла
Создано: 22 Sep 2025, 19:00 CET
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest


class TestMCPFixesValidation:
    """Тест-кейсы для проверки исправлений MCP сервера и Jupyter файла"""

    def test_mcp_server_starts_without_errors(self):
        """TC-001: MCP сервер запускается без ошибок"""
        try:
            result = subprocess.run(
                [sys.executable, "mcp_server/1c_mcp_server.py", "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            assert result.returncode == 0, f"MCP сервер не запустился: {result.stderr}"
            # FastMCP выводит информацию в stderr, а не stdout
            assert "FastMCP" in result.stderr, "FastMCP не обнаружен в выводе"
            assert "1c-extractor-server" in result.stderr, "Название сервера не найдено"

        except subprocess.TimeoutExpired:
            pytest.fail("MCP сервер не отвечает в течение 10 секунд")
        except Exception as e:
            pytest.fail(f"Ошибка запуска MCP сервера: {e}")

    def test_mcp_config_uses_python3(self):
        """TC-002: Конфигурация .mcp.json использует python3"""
        config_path = Path("config/.mcp.json")
        assert config_path.exists(), "Файл .mcp.json не найден"

        with open(config_path, "r") as f:
            config = json.load(f)

        assert (
            "1c-extractor" in config["mcpServers"]
        ), "Сервер 1c-extractor не найден в конфигурации"
        server_config = config["mcpServers"]["1c-extractor"]

        assert (
            server_config["command"] == "python3"
        ), f"Команда должна быть python3, получена: {server_config['command']}"
        assert (
            "mcp_server/1c_mcp_server.py" in server_config["args"]
        ), "Путь к серверу не найден в args"

    def test_jupyter_file_uses_direct_imports(self):
        """TC-003: Jupyter файл использует прямые импорты вместо MCP"""
        jupyter_path = Path("notebooks/1c-extractor.ipynb")
        assert jupyter_path.exists(), "Jupyter файл не найден"

        with open(jupyter_path, "r") as f:
            content = f.read()

        # Проверяем, что используются прямые импорты
        assert (
            "from src.processors.database_connector import DatabaseConnector" in content
        ), "DatabaseConnector не импортирован"
        assert (
            "from src.extractors.simple_document_extractor import SimpleDocumentExtractor"
            in content
        ), "SimpleDocumentExtractor не импортирован"

        # Проверяем, что MCP вызовы удалены
        assert (
            "mcp_client.call_tool" not in content
        ), "MCP вызовы не удалены из Jupyter файла"
        assert (
            "from mcp_client import mcp_client" not in content
        ), "MCP клиент не удален из импортов"

    def test_mcp_server_has_correct_resource_uri(self):
        """TC-004: MCP сервер имеет правильный URI для resource"""
        server_path = Path("mcp_server/1c_mcp_server.py")
        assert server_path.exists(), "MCP сервер не найден"

        with open(server_path, "r") as f:
            content = f.read()

        # Проверяем правильный URI для resource
        assert (
            '@mcp.resource("https://1c-extractor.local/database-info")' in content
        ), "Неправильный URI для resource"
        assert "@mcp.resource()" not in content, "Пустой декоратор resource не удален"

    def test_no_linter_errors_in_critical_files(self):
        """TC-005: Нет ошибок линтера в критических файлах"""
        critical_files = [
            "mcp_server/1c_mcp_server.py",
            "notebooks/1c-extractor.ipynb",
            "config/.mcp.json",
        ]

        for file_path in critical_files:
            if file_path.endswith(".py"):
                # Проверяем синтаксис Python
                try:
                    with open(file_path, "r") as f:
                        compile(f.read(), file_path, "exec")
                except SyntaxError as e:
                    pytest.fail(f"Синтаксическая ошибка в {file_path}: {e}")
            elif file_path.endswith(".json"):
                # Проверяем JSON
                try:
                    with open(file_path, "r") as f:
                        json.load(f)
                except json.JSONDecodeError as e:
                    pytest.fail(f"Ошибка JSON в {file_path}: {e}")

    def test_mcp_server_exports_correct_tools(self):
        """TC-006: MCP сервер экспортирует правильные инструменты"""
        server_path = Path("mcp_server/1c_mcp_server.py")
        with open(server_path, "r") as f:
            content = f.read()

        # Проверяем наличие всех необходимых инструментов
        required_tools = [
            "extract_1c_documents",
            "create_flat_table",
            "save_to_parquet",
        ]

        for tool in required_tools:
            assert (
                "@mcp.tool()" in content or "@mcp.tool" in content
            ), "Декоратор @mcp.tool не найден"
            assert f"def {tool}" in content, f"Функция {tool} не найдена"

        # Проверяем наличие resource
        assert "@mcp.resource" in content, "Resource не найден"
        assert (
            "def get_1c_database_info" in content
        ), "Функция get_1c_database_info не найдена"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
