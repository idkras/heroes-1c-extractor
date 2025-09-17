#!/usr/bin/env python3
"""
Тесты для AIGuidanceWorkflow
TDD подход - RED Phase: Написание падающих тестов
"""

import pytest
import sys
import os
from datetime import datetime

# Добавляем путь к модулю
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "workflows"))

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "workflows"))
from ai_guidance_workflow import (
    AIGuidanceWorkflow,
    GuidanceRequest,
    GuidanceResponse,
    GuidanceType,
)


class TestAIGuidanceWorkflow:
    """Тесты для AIGuidanceWorkflow"""

    def setup_method(self):
        """Настройка для каждого теста"""
        self.workflow = AIGuidanceWorkflow()

    def test_workflow_initialization(self):
        """Тест инициализации workflow"""
        assert self.workflow is not None
        assert len(self.workflow.guidance_templates) == 11
        assert GuidanceType.AI_GUIDANCE_CHECKLIST in self.workflow.guidance_templates
        assert (
            GuidanceType.REGISTRY_COMPLIANCE_CHECK in self.workflow.guidance_templates
        )
        assert GuidanceType.VALIDATE_OUTPUT_ARTEFACT in self.workflow.guidance_templates

    def test_ai_guidance_checklist(self):
        """Тест AI Guidance Checklist"""
        request = GuidanceRequest(
            guidance_type=GuidanceType.AI_GUIDANCE_CHECKLIST, task_type="testing"
        )

        response = self.workflow.execute_guidance(request)

        assert response.success is True
        assert response.guidance_type == GuidanceType.AI_GUIDANCE_CHECKLIST
        assert "AI Guidance Checklist для testing" in response.result
        assert "Чеклист проверки AI работы" in response.result
        assert response.reflection_checkpoint is not None

    def test_common_mistakes_prevention(self):
        """Тест Common Mistakes Prevention"""
        request = GuidanceRequest(
            guidance_type=GuidanceType.COMMON_MISTAKES_PREVENTION, domain="python"
        )

        response = self.workflow.execute_guidance(request)

        assert response.success is True
        assert response.guidance_type == GuidanceType.COMMON_MISTAKES_PREVENTION
        assert "Предотвращение типичных ошибок в python" in response.result
        assert "Типичные ошибки и их предотвращение" in response.result

    def test_quality_validation(self):
        """Тест Quality Validation"""
        request = GuidanceRequest(
            guidance_type=GuidanceType.QUALITY_VALIDATION,
            result="test result",
            criteria="performance",
        )

        response = self.workflow.execute_guidance(request)

        assert response.success is True
        assert response.guidance_type == GuidanceType.QUALITY_VALIDATION
        assert "Валидация качества результата" in response.result
        assert "test result" in response.result
        assert "performance" in response.result

    def test_approach_recommendation(self):
        """Тест Approach Recommendation"""
        request = GuidanceRequest(
            guidance_type=GuidanceType.APPROACH_RECOMMENDATION,
            problem="performance issue",
            context="production environment",
        )

        response = self.workflow.execute_guidance(request)

        assert response.success is True
        assert response.guidance_type == GuidanceType.APPROACH_RECOMMENDATION
        assert "Рекомендация подхода к решению" in response.result
        assert "performance issue" in response.result
        assert "production environment" in response.result

    def test_registry_compliance_check(self):
        """Тест Registry Compliance Check"""
        request = GuidanceRequest(guidance_type=GuidanceType.REGISTRY_COMPLIANCE_CHECK)

        response = self.workflow.execute_guidance(request)

        assert response.success is True
        assert response.guidance_type == GuidanceType.REGISTRY_COMPLIANCE_CHECK
        assert "Проверка соответствия Registry Standard" in response.result
        assert "Registry Compliance Check" in response.result

    def test_registry_output_validate(self):
        """Тест Registry Output Validate"""
        request = GuidanceRequest(
            guidance_type=GuidanceType.REGISTRY_OUTPUT_VALIDATE,
            artifact="test_artifact.json",
        )

        response = self.workflow.execute_guidance(request)

        assert response.success is True
        assert response.guidance_type == GuidanceType.REGISTRY_OUTPUT_VALIDATE
        assert "Валидация артефакта: test_artifact.json" in response.result
        assert "Валидация Registry Output" in response.result

    def test_registry_docs_audit(self):
        """Тест Registry Docs Audit"""
        request = GuidanceRequest(
            guidance_type=GuidanceType.REGISTRY_DOCS_AUDIT, paths="/docs, /api"
        )

        response = self.workflow.execute_guidance(request)

        assert response.success is True
        assert response.guidance_type == GuidanceType.REGISTRY_DOCS_AUDIT
        assert "Аудит документации по путям: /docs, /api" in response.result
        assert "Аудит документации Registry" in response.result

    def test_registry_gap_report(self):
        """Тест Registry Gap Report"""
        request = GuidanceRequest(
            guidance_type=GuidanceType.REGISTRY_GAP_REPORT,
            expected="expected behavior",
            actual="actual behavior",
            decision="fix implementation",
        )

        response = self.workflow.execute_guidance(request)

        assert response.success is True
        assert response.guidance_type == GuidanceType.REGISTRY_GAP_REPORT
        assert "expected behavior" in response.result
        assert "actual behavior" in response.result
        assert "fix implementation" in response.result

    def test_registry_release_block(self):
        """Тест Registry Release Block"""
        request = GuidanceRequest(
            guidance_type=GuidanceType.REGISTRY_RELEASE_BLOCK, until="2024-09-10"
        )

        response = self.workflow.execute_guidance(request)

        assert response.success is True
        assert response.guidance_type == GuidanceType.REGISTRY_RELEASE_BLOCK
        assert "Блокировка релиза до: 2024-09-10" in response.result
        assert "Блокировка релиза Registry" in response.result

    def test_validate_output_artefact(self):
        """Тест Validate Output Artefact"""
        request = GuidanceRequest(
            guidance_type=GuidanceType.VALIDATE_OUTPUT_ARTEFACT,
            artefact_path="/path/to/artifact.json",
            artefact_type="analysis",
            quality_criteria="high",
        )

        response = self.workflow.execute_guidance(request)

        assert response.success is True
        assert response.guidance_type == GuidanceType.VALIDATE_OUTPUT_ARTEFACT
        assert "/path/to/artifact.json" in response.result
        assert "analysis" in response.result
        assert "high" in response.result

    def test_validate_actual_outcome(self):
        """Тест Validate Actual Outcome"""
        request = GuidanceRequest(
            guidance_type=GuidanceType.VALIDATE_ACTUAL_OUTCOME,
            url="https://example.com",
            expected_features="login, dashboard",
            test_cases="smoke, regression",
            take_screenshot=True,
        )

        response = self.workflow.execute_guidance(request)

        assert response.success is True
        assert response.guidance_type == GuidanceType.VALIDATE_ACTUAL_OUTCOME
        assert "https://example.com" in response.result
        assert "login, dashboard" in response.result
        assert "smoke, regression" in response.result

    def test_unknown_guidance_type(self):
        """Тест неизвестного типа guidance"""

        # Тестируем обработку неизвестного типа через прямое создание объекта
        class MockRequest:
            def __init__(self):
                self.guidance_type = "unknown_type"
                self.task_type = "test"

        mock_request = MockRequest()

        # Тестируем метод _execute_specific_guidance напрямую
        result = self.workflow._execute_specific_guidance(mock_request, None)

        assert "Unknown guidance type: unknown_type" in result

    def test_reflection_checkpoint_creation(self):
        """Тест создания reflection checkpoint"""
        request = GuidanceRequest(
            guidance_type=GuidanceType.AI_GUIDANCE_CHECKLIST, task_type="test"
        )

        response = self.workflow.execute_guidance(request)

        assert response.reflection_checkpoint is not None
        assert "Reflection Checkpoint" in response.reflection_checkpoint
        assert "AI_GUIDANCE_CHECKLIST" in response.reflection_checkpoint
        assert "✅ Успешно" in response.reflection_checkpoint

    def test_all_guidance_types_exist(self):
        """Тест что все 11 типов guidance существуют"""
        expected_types = [
            GuidanceType.AI_GUIDANCE_CHECKLIST,
            GuidanceType.COMMON_MISTAKES_PREVENTION,
            GuidanceType.QUALITY_VALIDATION,
            GuidanceType.APPROACH_RECOMMENDATION,
            GuidanceType.REGISTRY_COMPLIANCE_CHECK,
            GuidanceType.REGISTRY_OUTPUT_VALIDATE,
            GuidanceType.REGISTRY_DOCS_AUDIT,
            GuidanceType.REGISTRY_GAP_REPORT,
            GuidanceType.REGISTRY_RELEASE_BLOCK,
            GuidanceType.VALIDATE_OUTPUT_ARTEFACT,
            GuidanceType.VALIDATE_ACTUAL_OUTCOME,
        ]

        for guidance_type in expected_types:
            assert guidance_type in self.workflow.guidance_templates
            request = GuidanceRequest(guidance_type=guidance_type)
            response = self.workflow.execute_guidance(request)
            assert response.success is True

    def test_guidance_templates_structure(self):
        """Тест структуры шаблонов guidance"""
        for guidance_type, template_info in self.workflow.guidance_templates.items():
            assert "template" in template_info
            assert "description" in template_info
            assert "jtbd" in template_info
            assert template_info["template"] is not None
            assert template_info["description"] is not None
            assert template_info["jtbd"] is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
