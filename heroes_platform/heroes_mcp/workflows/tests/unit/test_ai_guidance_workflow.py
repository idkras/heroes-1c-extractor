#!/usr/bin/env python3
"""
Unit tests for AI Guidance Workflow

Тесты для проверки функциональности AI Guidance Workflow.
Следует принципам TDD и MCP Workflow Standard v2.3.
"""

import json
import pytest
import sys
from pathlib import Path

# Add workflows directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from ai_guidance_workflow import AIGuidanceWorkflow


class TestAIGuidanceWorkflow:
    """Тесты для AIGuidanceWorkflow"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.workflow = AIGuidanceWorkflow()

    def test_workflow_initialization(self):
        """Тест инициализации workflow"""
        assert self.workflow.workflow_name == "ai_guidance_workflow"
        assert hasattr(self.workflow, "ai_guidance_checklist")
        assert hasattr(self.workflow, "execute")

    def test_ai_guidance_checklist_general(self):
        """Тест создания чеклиста для general типа задачи"""
        result = self.workflow.ai_guidance_checklist("general")

        # Проверяем что результат - валидный JSON
        parsed_result = json.loads(result)

        assert parsed_result["task_type"] == "general"
        assert "checklist" in parsed_result
        assert "total_items" in parsed_result
        assert "guidance_message" in parsed_result
        assert "timestamp" in parsed_result

        # Проверяем структуру чеклиста
        checklist = parsed_result["checklist"]
        assert "pre_execution" in checklist
        assert "during_execution" in checklist
        assert "post_execution" in checklist

        # Проверяем что есть элементы в чеклисте
        assert len(checklist["pre_execution"]) > 0
        assert len(checklist["during_execution"]) > 0
        assert len(checklist["post_execution"]) > 0

    def test_ai_guidance_checklist_development(self):
        """Тест создания чеклиста для development типа задачи"""
        result = self.workflow.ai_guidance_checklist("development")

        parsed_result = json.loads(result)

        assert parsed_result["task_type"] == "development"

        checklist = parsed_result["checklist"]
        assert "pre_development" in checklist
        assert "during_development" in checklist
        assert "post_development" in checklist

        # Проверяем что есть элементы в чеклисте
        assert len(checklist["pre_development"]) > 0
        assert len(checklist["during_development"]) > 0
        assert len(checklist["post_development"]) > 0

    def test_ai_guidance_checklist_analysis(self):
        """Тест создания чеклиста для analysis типа задачи"""
        result = self.workflow.ai_guidance_checklist("analysis")

        parsed_result = json.loads(result)

        assert parsed_result["task_type"] == "analysis"

        checklist = parsed_result["checklist"]
        assert "pre_analysis" in checklist
        assert "during_analysis" in checklist
        assert "post_analysis" in checklist

    def test_ai_guidance_checklist_integration(self):
        """Тест создания чеклиста для integration типа задачи"""
        result = self.workflow.ai_guidance_checklist("integration")

        parsed_result = json.loads(result)

        assert parsed_result["task_type"] == "integration"

        checklist = parsed_result["checklist"]
        assert "pre_integration" in checklist
        assert "during_integration" in checklist
        assert "post_integration" in checklist

    def test_ai_guidance_checklist_empty_task_type(self):
        """Тест обработки пустого типа задачи"""
        result = self.workflow.ai_guidance_checklist("")

        parsed_result = json.loads(result)

        # Должен вернуться general как default
        assert parsed_result["task_type"] == "general"

    def test_ai_guidance_checklist_none_task_type(self):
        """Тест обработки None типа задачи"""
        result = self.workflow.ai_guidance_checklist(None)

        parsed_result = json.loads(result)

        # Должен вернуться general как default
        assert parsed_result["task_type"] == "general"

    def test_ai_guidance_checklist_unknown_task_type(self):
        """Тест обработки неизвестного типа задачи"""
        result = self.workflow.ai_guidance_checklist("unknown_type")

        parsed_result = json.loads(result)

        # Должен вернуться general как fallback
        assert parsed_result["task_type"] == "unknown_type"
        assert "checklist" in parsed_result

    def test_execute_ai_guidance_checklist(self):
        """Тест выполнения workflow через execute метод"""
        arguments = {"command": "ai_guidance_checklist", "task_type": "development"}

        result = self.workflow.execute(arguments)

        assert result["success"] is True
        assert result["command"] == "ai_guidance_checklist"
        assert result["workflow"] == "ai_guidance_workflow"
        assert "result" in result

        # Проверяем что результат содержит валидный JSON
        parsed_result = json.loads(result["result"])
        assert parsed_result["task_type"] == "development"

    def test_execute_unknown_command(self):
        """Тест выполнения неизвестной команды"""
        arguments = {"command": "unknown_command", "task_type": "general"}

        result = self.workflow.execute(arguments)

        assert result["success"] is False
        assert "error" in result
        assert "Unknown command" in result["error"]
        assert result["workflow"] == "ai_guidance_workflow"

    def test_execute_default_command(self):
        """Тест выполнения с командой по умолчанию"""
        arguments = {"task_type": "analysis"}

        result = self.workflow.execute(arguments)

        assert result["success"] is True
        assert result["command"] == "ai_guidance_checklist"

        parsed_result = json.loads(result["result"])
        assert parsed_result["task_type"] == "analysis"

    def test_get_checklists_structure(self):
        """Тест структуры возвращаемых чеклистов"""
        checklists = self.workflow._get_checklists()

        # Проверяем что есть все типы задач
        assert "general" in checklists
        assert "development" in checklists
        assert "analysis" in checklists
        assert "integration" in checklists

        # Проверяем структуру для каждого типа
        for task_type, checklist in checklists.items():
            assert isinstance(checklist, dict)
            assert len(checklist) > 0

            for phase, items in checklist.items():
                assert isinstance(items, list)
                assert len(items) > 0

                # Проверяем что все элементы - строки
                for item in items:
                    assert isinstance(item, str)
                    assert len(item) > 0

    def test_total_items_calculation(self):
        """Тест правильности подсчета общего количества элементов"""
        result = self.workflow.ai_guidance_checklist("general")
        parsed_result = json.loads(result)

        checklist = parsed_result["checklist"]
        expected_total = sum(len(items) for items in checklist.values())

        assert parsed_result["total_items"] == expected_total
