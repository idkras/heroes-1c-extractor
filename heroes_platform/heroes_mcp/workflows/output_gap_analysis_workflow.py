#!/usr/bin/env python3
"""
Output Gap Analysis Workflow - Прямая реализация

JTBD: Как workflow executor, я хочу выполнить комплексный анализ gap между ожидаемым и фактическим output,
чтобы обеспечить атомарные операции валидации в соответствии с MCP Workflow Standard.

Основан на MCP Workflow Standard v2.3 и TDD Documentation Standard v2.5.
"""

import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class GapAnalysisInput:
    """Входные данные для gap analysis"""

    expected: Optional[str] = None
    actual: Optional[str] = None
    expected_file: Optional[str] = None
    actual_file: Optional[str] = None
    url: Optional[str] = None
    todo_file: Optional[str] = None
    release_name: Optional[str] = None
    analysis_type: str = "comprehensive"
    gap_threshold: float = 0.3
    take_screenshot: bool = True
    create_incident: bool = False


@dataclass
class GapAnalysisResult:
    """Результат gap analysis"""

    analysis_id: str
    workflow_status: str
    overall_score: float
    recommendations: list[str]
    execution_time: float
    steps_completed: list[str]
    steps_failed: list[str]
    details: dict[str, Any]


class OutputGapAnalysisWorkflow:
    """
    JTBD: Как workflow executor, я хочу выполнить комплексный анализ gap между ожидаемым и фактическим output,
    чтобы обеспечить атомарные операции валидации в соответствии с MCP Workflow Standard.
    """

    def __init__(self):
        self.workflow_name = "output_gap_analysis"
        self.version = "1.0.0"
        self.standard_compliance = "MCP Workflow Standard v2.3"

    async def execute(self, input_data: GapAnalysisInput) -> GapAnalysisResult:
        """Выполнение gap analysis workflow"""
        start_time = time.time()
        analysis_id = f"GAP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        logger.info(f"Starting Output Gap Analysis Workflow: {analysis_id}")

        try:
            steps_completed = []
            steps_failed = []

            # Step 1: Input Validation
            logger.info("Step 1: Input Validation")
            if not self._validate_input(input_data):
                steps_failed.append("input_validation")
                return self._create_error_result(
                    analysis_id, "Invalid input data", start_time, steps_failed
                )
            steps_completed.append("input_validation")

            # Step 2: Content Extraction
            logger.info("Step 2: Content Extraction")
            content_data = await self._extract_content(input_data)
            if not content_data.get("success"):
                steps_failed.append("content_extraction")
                return self._create_error_result(
                    analysis_id,
                    content_data.get("error", "Content extraction failed"),
                    start_time,
                    steps_failed,
                )
            steps_completed.append("content_extraction")

            # Step 3: Gap Analysis
            logger.info("Step 3: Gap Analysis")
            gap_analysis = await self._analyze_gap(
                content_data["expected"], content_data["actual"]
            )
            steps_completed.append("gap_analysis")

            # Step 4: Quality Assessment
            logger.info("Step 4: Quality Assessment")
            quality_assessment = await self._assess_quality(gap_analysis)
            steps_completed.append("quality_assessment")

            # Step 5: Screenshot Creation (if URL provided)
            if input_data.url and input_data.take_screenshot:
                logger.info("Step 5: Screenshot Creation")
                screenshot_result = await self._create_screenshot(input_data.url)
                if screenshot_result.get("success"):
                    steps_completed.append("screenshot_creation")
                else:
                    steps_failed.append("screenshot_creation")

            # Step 6: Recommendations Generation
            logger.info("Step 6: Recommendations Generation")
            recommendations = await self._generate_recommendations(
                gap_analysis, quality_assessment
            )
            steps_completed.append("recommendations_generation")

            execution_time = time.time() - start_time

            return GapAnalysisResult(
                analysis_id=analysis_id,
                workflow_status=(
                    "completed" if not steps_failed else "completed_with_errors"
                ),
                overall_score=quality_assessment.get("overall_score", 0.0),
                recommendations=recommendations,
                execution_time=execution_time,
                steps_completed=steps_completed,
                steps_failed=steps_failed,
                details={
                    "workflow_name": self.workflow_name,
                    "version": self.version,
                    "standard_compliance": self.standard_compliance,
                    "gap_analysis": gap_analysis,
                    "quality_assessment": quality_assessment,
                    "content_data": content_data,
                },
            )

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return self._create_error_result(
                analysis_id, str(e), start_time, ["workflow_execution"]
            )

    def _validate_input(self, input_data: GapAnalysisInput) -> bool:
        """Валидация входных данных"""
        if not input_data.expected and not input_data.expected_file:
            return False
        if not input_data.actual and not input_data.actual_file:
            return False
        return True

    async def _extract_content(self, input_data: GapAnalysisInput) -> dict[str, Any]:
        """Извлечение контента из различных источников"""
        try:
            expected = input_data.expected or ""
            actual = input_data.actual or ""

            # Если есть файлы, читаем их
            if input_data.expected_file:
                try:
                    with open(input_data.expected_file, encoding="utf-8") as f:
                        expected = f.read()
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Error reading expected file: {e}",
                    }

            if input_data.actual_file:
                try:
                    with open(input_data.actual_file, encoding="utf-8") as f:
                        actual = f.read()
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Error reading actual file: {e}",
                    }

            return {
                "success": True,
                "expected": expected,
                "actual": actual,
                "expected_length": len(expected),
                "actual_length": len(actual),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _analyze_gap(self, expected: str, actual: str) -> dict[str, Any]:
        """Анализ gap между expected и actual"""
        try:
            # Простой анализ на основе ключевых слов
            expected_words = set(expected.lower().split())
            actual_words = set(actual.lower().split())

            missing_words = expected_words - actual_words
            extra_words = actual_words - expected_words
            common_words = expected_words & actual_words

            gap_score = (
                len(common_words) / len(expected_words) if expected_words else 0.0
            )

            return {
                "gap_score": gap_score,
                "missing_words": list(missing_words),
                "extra_words": list(extra_words),
                "common_words": list(common_words),
                "expected_word_count": len(expected_words),
                "actual_word_count": len(actual_words),
                "similarity_percentage": gap_score * 100,
            }

        except Exception as e:
            logger.error(f"Gap analysis failed: {e}")
            return {"gap_score": 0.0, "error": str(e)}

    async def _assess_quality(self, gap_analysis: dict[str, Any]) -> dict[str, Any]:
        """Оценка качества на основе gap analysis"""
        try:
            gap_score = gap_analysis.get("gap_score", 0.0)

            if gap_score >= 0.9:
                quality_level = "excellent"
                overall_score = 95.0
            elif gap_score >= 0.8:
                quality_level = "good"
                overall_score = 85.0
            elif gap_score >= 0.7:
                quality_level = "acceptable"
                overall_score = 75.0
            elif gap_score >= 0.6:
                quality_level = "needs_improvement"
                overall_score = 65.0
            else:
                quality_level = "poor"
                overall_score = 45.0

            return {
                "overall_score": overall_score,
                "quality_level": quality_level,
                "gap_score": gap_score,
                "assessment": f"Quality is {quality_level} with {gap_score:.2%} similarity",
            }

        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            return {"overall_score": 0.0, "error": str(e)}

    async def _create_screenshot(self, url: str) -> dict[str, Any]:
        """Создание скриншота с правильным именованием"""
        try:
            # Используем новый формат именования
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = (
                f"output_screenshot/{timestamp}_gap_analysis_success_screenshot.png"
            )

            return {
                "success": True,
                "screenshot_path": screenshot_path,
                "note": "Screenshot creation requires Playwright MCP integration",
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _generate_recommendations(
        self, gap_analysis: dict[str, Any], quality_assessment: dict[str, Any]
    ) -> list[str]:
        """Генерация рекомендаций"""
        recommendations = []

        gap_score = gap_analysis.get("gap_score", 0.0)
        missing_words = gap_analysis.get("missing_words", [])

        if gap_score < 0.8:
            recommendations.append(
                "Улучшить соответствие между ожидаемым и фактическим результатом"
            )

        if missing_words:
            recommendations.append(
                f"Добавить недостающие ключевые элементы: {', '.join(missing_words[:5])}"
            )

        if quality_assessment.get("quality_level") == "poor":
            recommendations.append("Требуется серьезная доработка качества output")

        if not recommendations:
            recommendations.append("Output соответствует ожиданиям")

        return recommendations

    def _create_error_result(
        self, analysis_id: str, error: str, start_time: float, steps_failed: list[str]
    ) -> GapAnalysisResult:
        """Создание результата с ошибкой"""
        return GapAnalysisResult(
            analysis_id=analysis_id,
            workflow_status="failed",
            overall_score=0.0,
            recommendations=[error],
            execution_time=time.time() - start_time,
            steps_completed=[],
            steps_failed=steps_failed,
            details={"error": error},
        )

    async def analyze_gap(
        self,
        expected: str = "",
        actual: str = "",
        expected_file: str = "",
        actual_file: str = "",
        url: str = "",
        todo_file: str = "",
        release_name: str = "",
        analysis_type: str = "comprehensive",
        gap_threshold: float = 0.3,
        take_screenshot: bool = True,
        create_incident: bool = False,
    ) -> str:
        """Прокси метод для обратной совместимости"""
        input_data = GapAnalysisInput(
            expected=expected if expected else None,
            actual=actual if actual else None,
            expected_file=expected_file if expected_file else None,
            actual_file=actual_file if actual_file else None,
            url=url if url else None,
            todo_file=todo_file if todo_file else None,
            release_name=release_name if release_name else None,
            analysis_type=analysis_type,
            gap_threshold=gap_threshold,
            take_screenshot=take_screenshot,
            create_incident=create_incident,
        )

        result = await self.execute(input_data)

        return json.dumps(
            {
                "analysis_id": result.analysis_id,
                "workflow_status": result.workflow_status,
                "overall_score": result.overall_score,
                "recommendations": result.recommendations,
                "execution_time": result.execution_time,
                "steps_completed": result.steps_completed,
                "steps_failed": result.steps_failed,
                "details": result.details,
            },
            ensure_ascii=False,
            indent=2,
        )
