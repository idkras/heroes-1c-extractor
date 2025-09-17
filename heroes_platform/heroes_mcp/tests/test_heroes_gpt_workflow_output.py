#!/usr/bin/env python3
"""
TDD Tests for HeroesGPT Workflow File Output Architecture

JTBD: Как тестировщик MCP системы, я хочу убедиться что heroes_gpt_workflow
создает .md файлы в папке клиента и возвращает корректные ссылки,
чтобы гарантировать правильную архитектуру вывода.

Created: 21 August 2025, 17:45 CET by AI Assistant
Based on: TDD Documentation Standard v2.7
"""

import pytest
import os
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from unittest.mock import Mock, patch

# Добавляем src в sys.path для импорта модулей
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from scripts.heroes_gpt_workflow_integration import execute_heroes_gpt_workflow


class TestHeroesGPTWorkflowFileOutput:
    """
    JTBD: Как test suite для heroes_gpt_workflow, я хочу проверить создание файлов,
    чтобы убедиться в соответствии архитектурным требованиям.
    """

    def setup_method(self):
        """
        JTBD: Как setup тест, я хочу подготовить окружение,
        чтобы обеспечить изолированность каждого теста.
        """
        self.test_client_id = "test_client.com"
        self.test_url = "https://test_client.com"
        self.expected_clients_dir = Path("../../[heroes-gpt-bot]/clients")
        self.expected_client_dir = self.expected_clients_dir / self.test_client_id

    def test_heroes_workflow_should_create_md_file_in_client_folder(self):
        """
        RED PHASE TEST - SHOULD FAIL INITIALLY

        JTBD: Как тест создания файла, я хочу проверить что workflow создает .md файл,
        чтобы убедиться в корректности архитектуры вывода.

        Expected Behavior:
        - Должен создать папку клиента если не существует
        - Должен создать .md файл с анализом
        - Должен вернуть путь к созданному файлу
        """
        # Arrange
        workflow_input = {
            "url": self.test_url,
            "analysis_depth": "full",
            "business_context": {},
        }

        # Act
        result = asyncio.run(execute_heroes_gpt_workflow(self.test_url, "full", "{}"))

        # Assert - Файл должен быть создан
        expected_file_pattern = f"*heroes_gpt_analysis*.md"
        client_files = list(self.expected_client_dir.glob(expected_file_pattern))

        assert (
            len(client_files) > 0
        ), f"No analysis file found in {self.expected_client_dir}"

        # Assert - Возвращенный результат должен содержать путь к файлу
        assert "output_file_path" in result, "Result should contain output_file_path"
        assert result["output_file_path"].endswith(".md"), "Output file should be .md"

        # Assert - Файл должен существовать
        output_file = Path(result["output_file_path"])
        assert output_file.exists(), f"Output file {output_file} should exist"

        # Assert - Файл должен содержать анализ
        content = output_file.read_text(encoding="utf-8")
        assert len(content) > 100, "Analysis file should contain substantial content"
        assert (
            "heroes_gpt_analysis" in content.lower()
        ), "File should contain HeroesGPT analysis"

    def test_heroes_workflow_should_return_relative_path_link(self):
        """
        RED PHASE TEST - SHOULD FAIL INITIALLY

        JTBD: Как тест возврата ссылки, я хочу проверить формат возвращаемой ссылки,
        чтобы обеспечить консистентность с проектной структурой.
        """
        # Arrange
        workflow_input = {
            "url": self.test_url,
            "analysis_depth": "quick",
            "business_context": {},
        }

        # Act
        result = asyncio.run(execute_heroes_gpt_workflow(self.test_url, "quick", "{}"))

        # Assert - Путь должен быть относительным от корня проекта
        assert "output_file_path" in result
        file_path = result["output_file_path"]

        assert file_path.startswith(
            "[heroes-gpt-bot]/clients/"
        ), f"File path should start with '[heroes-gpt-bot]/clients/', got: {file_path}"

        assert file_path.endswith(
            ".md"
        ), f"File path should end with '.md', got: {file_path}"

    def test_heroes_workflow_should_create_client_folder_if_not_exists(self):
        """
        RED PHASE TEST - SHOULD FAIL INITIALLY

        JTBD: Как тест создания папки, я хочу проверить автосоздание папки клиента,
        чтобы убедиться в robustness системы.
        """
        # Arrange - убеждаемся что папка клиента не существует
        new_client_id = "new_test_client_" + str(int(datetime.now().timestamp()))
        new_client_dir = self.expected_clients_dir / new_client_id

        # Удаляем папку если существует (cleanup)
        if new_client_dir.exists():
            import shutil

            shutil.rmtree(new_client_dir)

        # Act
        result = asyncio.run(
            execute_heroes_gpt_workflow("newclient.example.com", "full", "{}")
        )

        # Assert - Папка клиента должна быть создана
        assert (
            new_client_dir.exists()
        ), f"Client directory {new_client_dir} should be created"

        # Assert - Файл должен быть в новой папке
        assert "output_file_path" in result
        output_file = Path(result["output_file_path"])
        assert (
            output_file.parent == new_client_dir
        ), f"Output file should be in client directory {new_client_dir}"

    def test_heroes_workflow_should_include_timestamp_in_filename(self):
        """
        RED PHASE TEST - SHOULD FAIL INITIALLY

        JTBD: Как тест именования файлов, я хочу проверить наличие timestamp,
        чтобы обеспечить уникальность и трекинг файлов.
        """
        # Arrange
        test_timestamp = datetime.now()

        # Act
        result = asyncio.run(execute_heroes_gpt_workflow(self.test_url, "full", "{}"))

        # Assert - Имя файла должно содержать timestamp
        assert "output_file_path" in result
        filename = Path(result["output_file_path"]).name

        # Ожидаем формат: "DD MMM YYYY HHMM CET client_analysis_by_heroesGPT.md"
        import re

        timestamp_pattern = r"\d{2}\s+\w{3}\s+\d{4}\s+\d{4}\s+CET"

        assert re.search(
            timestamp_pattern, filename
        ), f"Filename should contain timestamp pattern, got: {filename}"

    def test_heroes_workflow_should_validate_file_content_structure(self):
        """
        RED PHASE TEST - SHOULD FAIL INITIALLY

        JTBD: Как тест валидации контента, я хочу проверить структуру созданного файла,
        чтобы убедиться в соответствии стандарту HeroesGPT.
        """
        # Arrange
        test_url = "structured-test.example.com"

        # Act
        result = asyncio.run(execute_heroes_gpt_workflow(test_url, "full", "{}"))

        # Assert - Файл должен содержать обязательные секции
        assert "output_file_path" in result
        content = Path(result["output_file_path"]).read_text(encoding="utf-8")

        required_sections = [
            "# HeroesGPT Landing Analysis",
            "## Executive Summary",
            "## Deep Segment Research",
            "## Offers Analysis",
            "## Unified Analysis Table",
        ]

        for section in required_sections:
            assert section in content, f"Content should contain section: {section}"

    @pytest.mark.integration
    def test_integration_heroes_workflow_end_to_end_file_creation(self):
        """
        INTEGRATION TEST - RED PHASE

        JTBD: Как интеграционный тест, я хочу проверить полный цикл создания файла,
        чтобы убедиться в работе всей системы от MCP команды до файла.
        """
        # Arrange - реальные данные для интеграционного теста
        real_url = "zipsale.co.uk"

        # Act - вызываем через MCP интерфейс
        from heroes_mcp.src.heroes_mcp_server import heroes_gpt_workflow
        import json

        mcp_result = heroes_gpt_workflow(real_url, "quick", "{}")

        # Parse JSON result
        mcp_data = json.loads(mcp_result)

        # Assert - MCP команда должна вернуть информацию о файле
        assert (
            "output_file_path" in mcp_data or "file_created" in mcp_data
        ), "MCP result should contain file information"

        # Assert - Файл должен быть доступен через файловую систему
        if "output_file_path" in mcp_data:
            file_path = Path(mcp_data["output_file_path"])
            assert file_path.exists(), f"MCP created file should exist: {file_path}"

    def teardown_method(self):
        """
        JTBD: Как cleanup тест, я хочу очистить тестовые файлы,
        чтобы предотвратить загрязнение файловой системы.
        """
        # Cleanup тестовых файлов
        test_patterns = [
            "*test_client*",
            "*test.example.com*",
            "*newclient.example.com*",
            "*structured-test.example.com*",
        ]

        for pattern in test_patterns:
            for file_path in self.expected_clients_dir.glob(f"**/{pattern}"):
                if file_path.is_file():
                    file_path.unlink()
                elif file_path.is_dir():
                    import shutil

                    shutil.rmtree(file_path)


# PROPERTY-BASED TESTING согласно TDD стандарту
class TestHeroesGPTWorkflowProperties:
    """
    JTBD: Как property-based test suite, я хочу проверить инварианты системы,
    чтобы убедиться в корректности для всех входных данных.
    """

    @pytest.mark.hypothesis
    def test_property_all_urls_should_create_valid_files(self):
        """
        PROPERTY-BASED TEST - RED PHASE

        JTBD: Как property test, я хочу проверить что любой валидный URL создает файл,
        чтобы убедиться в robustness системы.
        """
        from hypothesis import given, strategies as st

        # Property: любой валидный URL должен создавать файл
        @given(
            st.text(
                alphabet=st.characters(whitelist_categories=["L", "N"]),
                min_size=3,
                max_size=20,
            )
        )
        def property_url_creates_file(url_part):
            # Arrange
            test_url = f"{url_part}.example.com"

            # Act
            try:
                result = asyncio.run(
                    execute_heroes_gpt_workflow(test_url, "quick", "{}")
                )

                # Assert - файл должен быть создан
                assert "output_file_path" in result
                file_path = Path(result["output_file_path"])
                assert file_path.exists()
                assert file_path.suffix == ".md"

            except Exception as e:
                pytest.fail(f"URL {test_url} should create valid file, but failed: {e}")

        # Запускаем property test
        property_url_creates_file()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
