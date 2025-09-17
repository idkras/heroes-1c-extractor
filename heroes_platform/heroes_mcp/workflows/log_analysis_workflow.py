#!/usr/bin/env python3
"""
Log Analysis Workflow

JTBD: Как AI Agent, я хочу анализировать логи выполнения команд для выявления брака в цепочке,
чтобы найти корневые причины проблем

Согласно MCP Workflow Standard v2.3 и TDD Documentation Standard
"""

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class LogAnalysisInput:
    """Входные данные для анализа логов"""

    log_file_path: str
    time_range: str = ""
    command_chain: str = ""


@dataclass
class LogAnalysisResult:
    """Результат анализа логов"""

    log_analysis_id: str
    execution_chain_status: str
    failure_point: Optional[dict[str, Any]] = None
    command_execution_flow: Optional[list[dict[str, Any]]] = None
    bottlenecks: Optional[list[dict[str, Any]]] = None
    error_count: int = 0
    warning_count: int = 0
    file_size: int = 0
    analysis_summary: Optional[dict[str, Any]] = None


class LogAnalysisWorkflow:
    """
    Workflow для анализа логов выполнения команд

    Согласно MCP Workflow Standard:
    - Атомарные операции ≤20 строк
    - Reflection checkpoints
    - Структурированный вывод
    - Обработка ошибок
    """

    async def analyze_execution_logs(
        self, input_data: LogAnalysisInput
    ) -> LogAnalysisResult:
        """
        Анализирует логи выполнения команд

        Args:
            input_data: Входные данные для анализа

        Returns:
            LogAnalysisResult: Результат анализа
        """
        try:
            # [reflection] Атомарная операция 1: Валидация входных данных
            await self._validate_input(input_data)

            # [reflection] Атомарная операция 2: Чтение файла логов
            content = await self._read_log_file(input_data.log_file_path)

            # [reflection] Атомарная операция 3: Анализ ошибок
            error_analysis = await self._analyze_errors(content)

            # [reflection] Атомарная операция 4: Анализ цепочки выполнения
            execution_analysis = await self._analyze_execution_chain(content)

            # [reflection] Атомарная операция 5: Формирование результата
            return await self._build_result(
                error_analysis, execution_analysis, len(content)
            )

        except Exception as e:
            logger.error(f"Error in analyze_execution_logs: {e}")
            raise e

    async def _validate_input(self, input_data: LogAnalysisInput) -> None:
        """Валидация входных данных - атомарная операция ≤20 строк"""
        if not input_data.log_file_path or not input_data.log_file_path.strip():
            raise ValueError("Log file path is required")

        log_file = Path(input_data.log_file_path.strip())
        if not log_file.exists():
            raise FileNotFoundError(f"Log file not found: {input_data.log_file_path}")

    async def _read_log_file(self, log_file_path: str) -> str:
        """Чтение файла логов - атомарная операция ≤20 строк"""
        log_file = Path(log_file_path)
        try:
            content = log_file.read_text(encoding="utf-8")
            return content
        except Exception as e:
            raise OSError(f"Error reading log file: {str(e)}")

    async def _analyze_errors(self, content: str) -> dict[str, Any]:
        """Анализ ошибок в логах - атомарная операция ≤20 строк"""
        # Исключаем строки, которые содержат "no errors" или подобные
        error_lines = [
            line
            for line in content.split("\n")
            if ("error" in line.lower() or "exception" in line.lower())
            and "no error" not in line.lower()
        ]
        warning_lines = [
            line for line in content.split("\n") if "warning" in line.lower()
        ]

        failure_point = None
        if error_lines:
            failure_point = {
                "command": "unknown",
                "timestamp": "unknown",
                "error": error_lines[0],
                "root_cause": "Error in execution chain",
            }

        return {
            "error_lines": error_lines,
            "warning_lines": warning_lines,
            "failure_point": failure_point,
            "error_count": len(error_lines),
            "warning_count": len(warning_lines),
        }

    async def _analyze_execution_chain(self, content: str) -> dict[str, Any]:
        """Анализ цепочки выполнения - атомарная операция ≤20 строк"""
        command_execution_flow = []
        bottlenecks = []

        # Анализ по ключевым словам
        if "heroes_gpt_workflow" in content:
            command_execution_flow.append(
                {
                    "command": "mcp_server.heroes_gpt_workflow",
                    "status": "success" if "error" not in content else "failed",
                    "duration": "estimated",
                }
            )

        if "file_output_manager" in content:
            command_execution_flow.append(
                {
                    "command": "file_output_manager.generate_analysis_markdown",
                    "status": "success" if "error" not in content else "failed",
                    "duration": "estimated",
                }
            )

        return {
            "command_execution_flow": command_execution_flow,
            "bottlenecks": bottlenecks,
        }

    async def _build_result(
        self,
        error_analysis: dict[str, Any],
        execution_analysis: dict[str, Any],
        file_size: int,
    ) -> LogAnalysisResult:
        """Формирование результата - атомарная операция ≤20 строк"""
        failure_point = error_analysis.get("failure_point")
        execution_chain_status = "failed" if failure_point else "success"

        analysis_summary = {
            "status": execution_chain_status,
            "critical_issues": error_analysis.get("error_count", 0),
            "performance_issues": len(execution_analysis.get("bottlenecks", [])),
            "total_commands": len(execution_analysis.get("command_execution_flow", [])),
        }

        return LogAnalysisResult(
            log_analysis_id=f"LA_{time.strftime('%Y%m%d_%H%M%S')}",
            execution_chain_status=execution_chain_status,
            failure_point=failure_point,
            command_execution_flow=execution_analysis.get("command_execution_flow"),
            bottlenecks=execution_analysis.get("bottlenecks"),
            error_count=error_analysis.get("error_count", 0),
            warning_count=error_analysis.get("warning_count", 0),
            file_size=file_size,
            analysis_summary=analysis_summary,
        )
