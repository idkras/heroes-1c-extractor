#!/usr/bin/env python3
"""
AI Guidance Workflow

Workflow для предоставления AI чеклистов и guidance для предотвращения типичных ошибок.
Следует принципам MCP Workflow Standard v2.3 с атомарными операциями и reflection checkpoints.
"""

import json
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class AIGuidanceWorkflow:
    """
    AI Guidance Workflow - предоставляет чеклисты и guidance для AI агентов

    JTBD: Как guidance system, я хочу дать AI чеклист для проверки,
    чтобы предотвратить типичные ошибки.
    """

    def __init__(self):
        """Инициализация workflow"""
        self.workflow_name = "ai_guidance_workflow"
        logger.info(f"Initialized {self.workflow_name}")

    def ai_guidance_checklist(self, task_type: str = "general") -> str:
        """
        Создает чеклист для AI агента в зависимости от типа задачи

        Args:
            task_type: Тип задачи (general, development, analysis, integration)

        Returns:
            str: JSON строка с чеклистом для AI агента
        """
        try:
            # [reflection] Input validation: Проверяем входные данные
            if not task_type:
                task_type = "general"

            # [reflection] Process validation: Создаем чеклист в зависимости от типа задачи
            checklists = self._get_checklists()

            # [reflection] Output validation: Формируем результат
            checklist = checklists.get(task_type, checklists["general"])

            result = {
                "task_type": task_type,
                "checklist": checklist,
                "total_items": sum(len(items) for items in checklist.values()),
                "guidance_message": "Используйте этот чеклист для проверки качества вашей работы на каждом этапе",
                "timestamp": time.time(),
            }

            return json.dumps(result, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"Error in ai_guidance_checklist: {e}")
            return json.dumps(
                {"error": f"Error generating checklist: {str(e)}"}, ensure_ascii=False
            )

    def _get_checklists(self) -> dict[str, dict[str, list[str]]]:
        """
        Возвращает словарь чеклистов для разных типов задач

        Returns:
            Dict[str, Dict[str, List[str]]]: Словарь чеклистов
        """
        return {
            "general": {
                "pre_execution": [
                    "✅ Понял ли я задачу?",
                    "✅ Есть ли у меня все необходимые данные?",
                    "✅ Знаю ли я критерии успеха?",
                    "✅ Проверил ли я доступы к системам?",
                ],
                "during_execution": [
                    "✅ Следует ли я правильному процессу?",
                    "✅ Проверяю ли я качество на каждом шаге?",
                    "✅ Документирую ли я важные решения?",
                    "✅ Обрабатываю ли я ошибки?",
                ],
                "post_execution": [
                    "✅ Проходит ли результат валидацию?",
                    "✅ Соответствует ли результат требованиям?",
                    "✅ Может ли пользователь использовать результат?",
                    "✅ Обновил ли я связанную документацию?",
                ],
            },
            "development": {
                "pre_development": [
                    "✅ Следует ли я TDD принципам?",
                    "✅ Написал ли я тесты перед кодом?",
                    "✅ Понял ли я архитектурные требования?",
                    "✅ Проверил ли я существующий код?",
                ],
                "during_development": [
                    "✅ Пишу ли я чистый, читаемый код?",
                    "✅ Соблюдаю ли я принципы SOLID?",
                    "✅ Тестирую ли я код на каждом этапе?",
                    "✅ Документирую ли я публичные API?",
                ],
                "post_development": [
                    "✅ Проходят ли все тесты?",
                    "✅ Соответствует ли код стандартам качества?",
                    "✅ Проверил ли я безопасность кода?",
                    "✅ Готов ли код к production?",
                ],
            },
            "analysis": {
                "pre_analysis": [
                    "✅ Понял ли я цель анализа?",
                    "✅ Есть ли у меня качественные данные?",
                    "✅ Определил ли я критерии оценки?",
                    "✅ Проверил ли я источники данных?",
                ],
                "during_analysis": [
                    "✅ Использую ли я правильные методы анализа?",
                    "✅ Проверяю ли я качество данных?",
                    "✅ Документирую ли я процесс анализа?",
                    "✅ Обрабатываю ли я выбросы и аномалии?",
                ],
                "post_analysis": [
                    "✅ Валидны ли результаты анализа?",
                    "✅ Понятны ли выводы пользователю?",
                    "✅ Есть ли actionable insights?",
                    "✅ Документировал ли я ограничения анализа?",
                ],
            },
            "integration": {
                "pre_integration": [
                    "✅ Понял ли я требования интеграции?",
                    "✅ Проверил ли я API документацию?",
                    "✅ Тестировал ли я подключение?",
                    "✅ Подготовил ли я error handling?",
                ],
                "during_integration": [
                    "✅ Следует ли я best practices?",
                    "✅ Обрабатываю ли я ошибки подключения?",
                    "✅ Логирую ли я важные операции?",
                    "✅ Тестирую ли я интеграцию?",
                ],
                "post_integration": [
                    "✅ Работает ли интеграция корректно?",
                    "✅ Обрабатываются ли все edge cases?",
                    "✅ Документировал ли я интеграцию?",
                    "✅ Готов ли к production deployment?",
                ],
            },
        }

    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """
        Выполняет workflow с атомарными операциями

        Args:
            arguments: Аргументы для выполнения workflow

        Returns:
            Dict[str, Any]: Результат выполнения workflow
        """
        try:
            command = arguments.get("command", "ai_guidance_checklist")

            if command == "ai_guidance_checklist":
                task_type = arguments.get("task_type", "general")
                result = self.ai_guidance_checklist(task_type)
                return {
                    "success": True,
                    "command": command,
                    "result": result,
                    "workflow": self.workflow_name,
                }
            else:
                return {
                    "success": False,
                    "error": f"Unknown command: {command}",
                    "workflow": self.workflow_name,
                }

        except Exception as e:
            logger.error(f"Error in execute: {e}")
            return {"success": False, "error": str(e), "workflow": self.workflow_name}
