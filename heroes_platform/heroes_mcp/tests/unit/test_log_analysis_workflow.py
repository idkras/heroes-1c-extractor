#!/usr/bin/env python3
"""
Unit tests for LogAnalysisWorkflow

Согласно TDD Documentation Standard:
- Покрытие ≥90%
- Тестирование всех методов
- Мокирование внешних зависимостей
- Тестирование граничных случаев
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open

# Добавляем путь к workflows в sys.path
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "workflows"))

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "workflows"))
from log_analysis_workflow import (
    LogAnalysisWorkflow,
    LogAnalysisInput,
    LogAnalysisResult,
)


class TestLogAnalysisWorkflow:
    """Тесты для LogAnalysisWorkflow"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.workflow = LogAnalysisWorkflow()

    @pytest.mark.asyncio
    async def test_analyze_execution_logs_success(self):
        """Тест успешного анализа логов"""
        # Создаем временный файл с тестовыми логами
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(
                "Test log content with heroes_gpt_workflow and file_output_manager\n"
            )
            f.write("No errors found\n")
            temp_file = f.name

        try:
            input_data = LogAnalysisInput(
                log_file_path=temp_file, time_range="", command_chain=""
            )

            result = await self.workflow.analyze_execution_logs(input_data)

            assert isinstance(result, LogAnalysisResult)
            assert result.execution_chain_status == "success"
            assert result.error_count == 0
            assert result.warning_count == 0
            assert result.failure_point is None
            assert len(result.command_execution_flow) == 2
            assert result.file_size > 0

        finally:
            os.unlink(temp_file)

    @pytest.mark.asyncio
    async def test_analyze_execution_logs_with_errors(self):
        """Тест анализа логов с ошибками"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Test log content with heroes_gpt_workflow\n")
            f.write("Error: Something went wrong\n")
            f.write("Exception: Test exception\n")
            temp_file = f.name

        try:
            input_data = LogAnalysisInput(
                log_file_path=temp_file, time_range="", command_chain=""
            )

            result = await self.workflow.analyze_execution_logs(input_data)

            assert result.execution_chain_status == "failed"
            assert result.error_count == 2
            assert result.warning_count == 0
            assert result.failure_point is not None
            assert "Error: Something went wrong" in result.failure_point["error"]

        finally:
            os.unlink(temp_file)

    @pytest.mark.asyncio
    async def test_analyze_execution_logs_file_not_found(self):
        """Тест обработки отсутствующего файла"""
        input_data = LogAnalysisInput(
            log_file_path="/nonexistent/file.txt", time_range="", command_chain=""
        )

        with pytest.raises(FileNotFoundError):
            await self.workflow.analyze_execution_logs(input_data)

    @pytest.mark.asyncio
    async def test_analyze_execution_logs_empty_path(self):
        """Тест обработки пустого пути"""
        input_data = LogAnalysisInput(log_file_path="", time_range="", command_chain="")

        with pytest.raises(ValueError, match="Log file path is required"):
            await self.workflow.analyze_execution_logs(input_data)

    @pytest.mark.asyncio
    async def test_validate_input_valid(self):
        """Тест валидации корректных входных данных"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            temp_file = f.name

        try:
            input_data = LogAnalysisInput(log_file_path=temp_file)
            await self.workflow._validate_input(input_data)
            # Не должно вызывать исключений

        finally:
            os.unlink(temp_file)

    @pytest.mark.asyncio
    async def test_validate_input_invalid(self):
        """Тест валидации некорректных входных данных"""
        input_data = LogAnalysisInput(log_file_path="")

        with pytest.raises(ValueError, match="Log file path is required"):
            await self.workflow._validate_input(input_data)

    @pytest.mark.asyncio
    async def test_read_log_file_success(self):
        """Тест успешного чтения файла логов"""
        test_content = "Test log content\nLine 2\nLine 3"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(test_content)
            temp_file = f.name

        try:
            content = await self.workflow._read_log_file(temp_file)
            assert content == test_content

        finally:
            os.unlink(temp_file)

    @pytest.mark.asyncio
    async def test_analyze_errors_no_errors(self):
        """Тест анализа логов без ошибок"""
        content = "Normal log content\nNo errors here\nEverything is fine"

        result = await self.workflow._analyze_errors(content)

        assert result["error_count"] == 0
        assert result["warning_count"] == 0
        assert result["failure_point"] is None

    @pytest.mark.asyncio
    async def test_analyze_errors_with_errors(self):
        """Тест анализа логов с ошибками"""
        content = (
            "Normal log content\nError: Something went wrong\nWarning: Minor issue"
        )

        result = await self.workflow._analyze_errors(content)

        assert result["error_count"] == 1
        assert result["warning_count"] == 1
        assert result["failure_point"] is not None
        assert "Error: Something went wrong" in result["failure_point"]["error"]

    @pytest.mark.asyncio
    async def test_analyze_execution_chain_with_commands(self):
        """Тест анализа цепочки выполнения с командами"""
        content = "heroes_gpt_workflow executed\nfile_output_manager completed"

        result = await self.workflow._analyze_execution_chain(content)

        assert len(result["command_execution_flow"]) == 2
        assert (
            result["command_execution_flow"][0]["command"]
            == "mcp_server.heroes_gpt_workflow"
        )
        assert (
            result["command_execution_flow"][1]["command"]
            == "file_output_manager.generate_analysis_markdown"
        )

    @pytest.mark.asyncio
    async def test_analyze_execution_chain_no_commands(self):
        """Тест анализа цепочки выполнения без команд"""
        content = "Just some random log content"

        result = await self.workflow._analyze_execution_chain(content)

        assert len(result["command_execution_flow"]) == 0
        assert len(result["bottlenecks"]) == 0

    @pytest.mark.asyncio
    async def test_build_result_success(self):
        """Тест формирования результата для успешного выполнения"""
        error_analysis = {
            "error_lines": [],
            "warning_lines": [],
            "failure_point": None,
            "error_count": 0,
            "warning_count": 0,
        }

        execution_analysis = {
            "command_execution_flow": [
                {"command": "test_command", "status": "success", "duration": "1s"}
            ],
            "bottlenecks": [],
        }

        result = await self.workflow._build_result(
            error_analysis, execution_analysis, 100
        )

        assert result.execution_chain_status == "success"
        assert result.error_count == 0
        assert result.warning_count == 0
        assert result.failure_point is None
        assert result.file_size == 100
        assert result.analysis_summary["status"] == "success"

    @pytest.mark.asyncio
    async def test_build_result_failed(self):
        """Тест формирования результата для неуспешного выполнения"""
        error_analysis = {
            "error_lines": ["Error: Test error"],
            "warning_lines": [],
            "failure_point": {"error": "Error: Test error"},
            "error_count": 1,
            "warning_count": 0,
        }

        execution_analysis = {"command_execution_flow": [], "bottlenecks": []}

        result = await self.workflow._build_result(
            error_analysis, execution_analysis, 50
        )

        assert result.execution_chain_status == "failed"
        assert result.error_count == 1
        assert result.warning_count == 0
        assert result.failure_point is not None
        assert result.file_size == 50
        assert result.analysis_summary["status"] == "failed"


class TestLogAnalysisWorkflowValidation:
    """Тесты валидации LogAnalysisWorkflow"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.workflow = LogAnalysisWorkflow()

    @pytest.mark.asyncio
    async def test_input_validation_edge_cases(self):
        """Тест граничных случаев валидации входных данных"""
        # Тест с None
        with pytest.raises(ValueError):
            await self.workflow._validate_input(LogAnalysisInput(log_file_path=None))

        # Тест с пробелами
        with pytest.raises(ValueError):
            await self.workflow._validate_input(LogAnalysisInput(log_file_path="   "))

    @pytest.mark.asyncio
    async def test_error_analysis_edge_cases(self):
        """Тест граничных случаев анализа ошибок"""
        # Пустой контент
        result = await self.workflow._analyze_errors("")
        assert result["error_count"] == 0
        assert result["warning_count"] == 0

        # Контент только с пробелами
        result = await self.workflow._analyze_errors("   \n  \n")
        assert result["error_count"] == 0
        assert result["warning_count"] == 0

        # Смешанный регистр
        content = "ERROR: Test error\nWarning: Test warning\nException: Test exception"
        result = await self.workflow._analyze_errors(content)
        assert result["error_count"] == 2  # ERROR и Exception
        assert result["warning_count"] == 1  # Warning
