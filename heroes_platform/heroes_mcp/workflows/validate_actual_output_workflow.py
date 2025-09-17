#!/usr/bin/env python3
"""
Validate Actual Output Workflow - Универсальный валидатор артефактов

JTBD: Как валидатор outcome, я хочу проверить любой артефакт (URL, файл, скриншот) и сравнить с ожидаемым,
чтобы убедиться что output соответствует требованиям и зафиксировать результаты для анализа.

Основан на MCP Workflow Standard v2.3 и TDD Documentation Standard v2.5.
Включает логирование выполнения команд и анализ соответствия outcome.
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from .validate_actual_output.workflow import ValidateActualOutputWorkflow as CoreWorkflow

logger = logging.getLogger(__name__)


class ValidateActualOutputWorkflow:
    """
    JTBD: Как валидатор outcome, я хочу проверить любой артефакт и сравнить с ожидаемым,
    чтобы убедиться что output соответствует требованиям.

    Универсальный валидатор с поддержкой:
    - URL анализа
    - Файлов (.md, .txt, .json, .py и др.)
    - Скриншотов
    - Логирования выполнения команд
    - Анализа соответствия outcome
    """

    def __init__(self):
        self.core_workflow = CoreWorkflow()
        self.log_dir = Path("logs/command_execution")
        self.log_dir.mkdir(parents=True, exist_ok=True)

    async def execute(self, input_data) -> dict:
        """
        Универсальный валидатор артефактов с логированием

        Args:
            input_data: ValidateOutputInput объект или словарь с аргументами

        Returns:
            dict: Результат валидации с метаданными выполнения
        """
        try:
            # Логируем начало выполнения
            execution_id = f"VALIDATE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            start_time = time.time()
            
            logger.info(f"Starting validation workflow: {execution_id}")
            
            # Вызываем core workflow (он сам преобразует dict в ValidateOutputInput)
            result = await self.core_workflow.execute(input_data)
            
            # Добавляем метаданные выполнения
            execution_time = time.time() - start_time
            result["execution_metadata"] = {
                "execution_id": execution_id,
                "artifact_type": input_data.get('artifact_type', 'unknown') if isinstance(input_data, dict) else getattr(input_data, 'artifact_type', 'unknown'),
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
                "arguments": {
                    "artifact_path": input_data.get('artifact_path', '') if isinstance(input_data, dict) else getattr(input_data, 'artifact_path', ''),
                    "artifact_type": input_data.get('artifact_type', '') if isinstance(input_data, dict) else getattr(input_data, 'artifact_type', ''),
                    "expected_features": input_data.get('expected_features', '') if isinstance(input_data, dict) else getattr(input_data, 'expected_features', ''),
                    "test_cases": input_data.get('test_cases', '') if isinstance(input_data, dict) else getattr(input_data, 'test_cases', ''),
                    "take_screenshot": input_data.get('take_screenshot', True) if isinstance(input_data, dict) else getattr(input_data, 'take_screenshot', True),
                    "log_execution": input_data.get('log_execution', True) if isinstance(input_data, dict) else getattr(input_data, 'log_execution', True),
                    "url": input_data.get('url', '') if isinstance(input_data, dict) else getattr(input_data, 'url', '')
                }
            }
            
            logger.info(f"Validation workflow completed: {execution_id} in {execution_time:.3f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error in ValidateActualOutputWorkflow: {e}")
            return {
                "error": f"Workflow execution failed: {str(e)}",
                "validation_status": "failed",
                "execution_metadata": {
                    "execution_id": execution_id if 'execution_id' in locals() else "UNKNOWN",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            }
