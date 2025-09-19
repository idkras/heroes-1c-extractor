#!/usr/bin/env python3
"""
Validate Actual Output Workflow
MCP Workflow Standard v2.3 Compliance

JTBD: Когда мне нужно проверить фактический результат по URL и сравнить с ожидаемым,
я хочу использовать validate_actual_output_workflow,
чтобы автоматически анализировать страницы, создавать скриншоты и генерировать отчеты о качестве.

WORKFLOW PROTOCOL: validate_actual_outcome
COMPLIANCE: MCP Workflow Standard v2.3, TDD Documentation Standard v2.5
"""

import logging
import time
from dataclasses import dataclass
from typing import Any, Optional

from .quality_validator import QualityValidator
from .screenshot_manager import ScreenshotManager
from .url_analyzer import URLAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class ValidateOutputInput:
    """Входные данные для валидации output"""

    url: str
    artifact_path: str = ""
    artifact_type: str = ""
    expected_features: str = ""
    test_cases: str = ""
    take_screenshot: bool = True


@dataclass
class ValidateOutputResult:
    """Результат валидации output"""

    validation_id: str
    workflow_status: str
    url: str
    analysis: dict[str, Any]
    defect_checklist: dict[str, Any]
    quality_test_cases: dict[str, Any]
    screenshot_info: Optional[dict[str, Any]]
    validation_score: float
    recommendations: list[str]
    execution_time: float
    details: dict[str, Any]


class ValidateActualOutputWorkflow:
    """
    JTBD: Как валидатор outcome, я хочу проверить фактический результат по URL и сравнить с ожидаемым,
    чтобы убедиться что output соответствует требованиям.
    """

    def __init__(self):
        self.workflow_name = "validate_actual_output"
        self.version = "1.0.0"
        self.standard_compliance = (
            "MCP Workflow Standard v2.3, TDD Documentation Standard v2.5"
        )

        # Инициализация модулей
        self.url_analyzer = URLAnalyzer()
        self.screenshot_manager = ScreenshotManager()
        self.quality_validator = QualityValidator()

    async def execute(
        self, input_data: dict | ValidateOutputInput
    ) -> ValidateOutputResult:
        """
        JTBD: Как workflow executor, я хочу выполнить полную валидацию actual output,
        чтобы получить комплексную оценку качества и выявить проблемы.
        """
        start_time = time.time()
        validation_id = f"VALIDATE_{time.strftime('%Y%m%d_%H%M%S')}"

        logger.info(f"Starting Validate Actual Output Workflow: {validation_id}")

        # Convert dict to ValidateOutputInput if needed
        if isinstance(input_data, dict):
            input_data = ValidateOutputInput(
                url=input_data.get("url", ""),
                artifact_path=input_data.get("artifact_path", ""),
                artifact_type=input_data.get("artifact_type", ""),
                expected_features=input_data.get("expected_features", ""),
                test_cases=input_data.get("test_cases", ""),
                take_screenshot=input_data.get("take_screenshot", True),
            )

        # [reflection] Input validation
        if not input_data.url:
            return self._create_error_result(
                validation_id, "URL is required", start_time
            )

        # [reflection] Workflow execution
        try:
            # Step 1: URL Analysis
            logger.info(f"Step 1: URL Analysis for {input_data.url}")
            analysis_result = await self.url_analyzer.analyze_url(input_data.url)

            # Step 2: Quality Test Cases
            logger.info("Step 2: Quality Test Cases")
            test_cases_result = (
                await self.quality_validator.generate_quality_test_cases(
                    input_data.url, analysis_result
                )
            )

            # Step 3: Defect Detection
            logger.info("Step 3: Defect Detection")
            defect_result = await self.quality_validator.detect_defects(
                analysis_result, test_cases_result
            )

            # Step 4: Score Calculation
            logger.info("Step 4: Score Calculation")
            score_result = await self._calculate_validation_score(
                test_cases_result, defect_result
            )

            # Step 5: Screenshot Creation
            screenshot_info = None
            if input_data.take_screenshot:
                logger.info("Step 5: Screenshot Creation")
                # Определяем параметры для правильного именования скриншота
                output_type = "validation"
                outcome = "success" if score_result.get("score", 0) >= 80 else "failed"
                # Для файлов создаем placeholder, для URL - реальный скриншот
                if input_data.artifact_path and not input_data.artifact_path.startswith(
                    ("http://", "https://")
                ):
                    # Это файл - создаем placeholder
                    screenshot_url = f"file://{input_data.artifact_path}"
                    description = "file_artifact"
                else:
                    # Это URL
                    screenshot_url = (
                        input_data.artifact_path
                        if input_data.artifact_path
                        else input_data.url
                    )
                    description = (
                        "doc_todo"
                        if "doc.todo.md" in str(screenshot_url)
                        else "artifact"
                    )
                screenshot_info = await self.screenshot_manager.create_screenshot(
                    screenshot_url, output_type, outcome, description
                )

            # Step 6: Recommendations Generation
            logger.info("Step 6: Recommendations Generation")
            recommendations = await self._generate_recommendations(
                defect_result, score_result
            )

            # [reflection] Output validation: Создаем качественный результат
            execution_time = time.time() - start_time

            return ValidateOutputResult(
                validation_id=validation_id,
                workflow_status="completed",
                url=input_data.url,
                analysis=analysis_result,
                defect_checklist=defect_result,
                quality_test_cases=test_cases_result,
                screenshot_info=screenshot_info,
                validation_score=score_result["validation_score"],
                recommendations=recommendations,
                execution_time=execution_time,
                details={
                    "workflow_name": self.workflow_name,
                    "version": self.version,
                    "standard_compliance": self.standard_compliance,
                    "jtbd_scenario": self._get_jtbd_scenario(),
                    "evidence_links": self._generate_evidence_links(
                        input_data.url, screenshot_info
                    ),
                    "ai_qa_tasks": self._get_ai_qa_tasks(),
                },
            )

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return self._create_error_result(validation_id, str(e), start_time)

    def _create_error_result(
        self, validation_id: str, error: str, start_time: float
    ) -> ValidateOutputResult:
        """Создание результата с ошибкой (≤20 строк)"""
        return ValidateOutputResult(
            validation_id=validation_id,
            workflow_status="failed",
            url="",
            analysis={},
            defect_checklist={},
            quality_test_cases={},
            screenshot_info=None,
            validation_score=0.0,
            recommendations=[error],
            execution_time=time.time() - start_time,
            details={"error": error},
        )

    async def _calculate_validation_score(
        self, test_cases: dict[str, Any], defects: dict[str, Any]
    ) -> dict[str, Any]:
        """Расчет валидационного скора (≤20 строк)"""
        try:
            total_tests = test_cases.get("total_tests", 0)
            total_defects = defects.get("total_defects", 0)

            if total_tests == 0:
                validation_score = 0.0
            else:
                # Простая формула: (тесты - дефекты) / тесты * 100
                validation_score = max(
                    0.0, (total_tests - total_defects) / total_tests * 100
                )

            return {
                "validation_score": validation_score,
                "total_tests": total_tests,
                "total_defects": total_defects,
                "score_breakdown": {
                    "tests_passed": total_tests - total_defects,
                    "tests_failed": total_defects,
                },
            }

        except Exception as e:
            logger.error(f"Score calculation failed: {e}")
            return {"validation_score": 0.0, "error": str(e)}

    async def _generate_recommendations(
        self, defects: dict[str, Any], score: dict[str, Any]
    ) -> list[str]:
        """Генерация рекомендаций (≤20 строк)"""
        recommendations = []

        # Рекомендации на основе дефектов
        if defects.get("defects", {}).get("critical"):
            recommendations.append("Исправить критические дефекты в первую очередь")

        if defects.get("defects", {}).get("major"):
            recommendations.append("Улучшить основные аспекты качества")

        # Рекомендации на основе скора
        validation_score = score.get("validation_score", 0)
        if validation_score < 50:
            recommendations.append("Требуется серьезная доработка качества")
        elif validation_score < 80:
            recommendations.append("Рекомендуется улучшение качества")
        else:
            recommendations.append("Качество соответствует стандартам")

        return recommendations

    def _get_jtbd_scenario(self) -> dict[str, Any]:
        """Получение JTBD сценария (≤20 строк)"""
        return {
            "user": "QA Engineer / Developer",
            "job": "Проверить качество веб-страницы",
            "outcome": "Получить детальный отчет о качестве с рекомендациями",
            "context": "Валидация output после разработки или изменений",
        }

    def _generate_evidence_links(
        self, url: str, screenshot_info: Optional[dict[str, Any]]
    ) -> dict[str, Any]:
        """Генерация ссылок на доказательства (≤20 строк)"""
        evidence = {
            "url": url,
            "validation_command": f"validate_actual_outcome {url}",
            "screenshot_command": f"read_cleanshot {url}" if screenshot_info else None,
        }

        if screenshot_info:
            evidence["screenshot_path"] = screenshot_info.get("filepath")

        return evidence

    def _get_ai_qa_tasks(self) -> list[str]:
        """Получение AI QA задач (≤20 строк)"""
        return [
            "Проверить соответствие дизайна макету",
            "Проверить адаптивность на разных устройствах",
            "Проверить доступность (accessibility)",
            "Проверить SEO-оптимизацию",
            "Проверить производительность",
        ]

    async def validate_output(
        self,
        url: str,
        expected_features: str = "",
        test_cases: str = "",
        take_screenshot: bool = True,
    ) -> str:
        """Прокси метод для MCP интеграции (≤20 строк)"""
        try:
            from dataclasses import dataclass

            @dataclass
            class SimpleInput:
                url: str
                expected_features: str
                test_cases: str
                take_screenshot: bool

            input_data = ValidateOutputInput(
                url=url,
                expected_features=expected_features,
                test_cases=test_cases,
                take_screenshot=take_screenshot,
            )
            result = await self.execute(input_data)

            # Convert to JSON string for MCP
            import json

            return json.dumps(
                {
                    "validation_id": result.validation_id,
                    "workflow_status": result.workflow_status,
                    "url": result.url,
                    "analysis": result.analysis,
                    "defect_checklist": result.defect_checklist,
                    "quality_test_cases": result.quality_test_cases,
                    "screenshot_info": result.screenshot_info,
                    "validation_score": result.validation_score,
                    "recommendations": result.recommendations,
                    "execution_time": result.execution_time,
                    "details": result.details,
                },
                ensure_ascii=False,
                indent=2,
            )

        except Exception as e:
            import json

            return json.dumps(
                {"error": f"validate_output failed: {str(e)}", "url": url},
                ensure_ascii=False,
            )
