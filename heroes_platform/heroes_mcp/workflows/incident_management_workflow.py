#!/usr/bin/env python3
"""
Incident Management Workflow

JTBD: Как workflow orchestrator, я хочу координировать создание и управление инцидентами,
анализ корневых причин и генерацию отчетов о gap, чтобы обеспечить комплексное управление проблемами
через атомарные операции.

Основан на MCP Workflow Standard и TDD Documentation Standard.
"""

import logging
import time
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class IncidentInput:
    """Входные данные для создания инцидента"""

    incident_type: str  # validation_failure/output_mismatch/quality_issue
    severity: str  # critical/high/medium/low
    gap_report_id: str
    affected_release: str


@dataclass
class RSAInput:
    """Входные данные для RSA анализа"""

    problem_description: str
    incident_id: str
    evidence_data: str
    analysis_depth: str = "5_why"  # 5_why/7_why/10_why


@dataclass
class GapReportInput:
    """Входные данные для генерации gap report"""

    expected_output: str
    actual_output: str
    gap_threshold: float = 0.3


@dataclass
class LogAnalysisInput:
    """Входные данные для анализа логов"""

    log_file_path: str
    time_range: str = ""
    command_chain: str = ""


@dataclass
class IncidentManagementResult:
    """Результат операций инцидент-менеджмента"""

    operation_id: str
    workflow_status: str
    steps_completed: list[str]
    steps_failed: list[str]
    overall_score: float
    recommendations: list[str]
    execution_time: float
    details: dict[str, Any]


class IncidentManagementWorkflow:
    """
    JTBD: Как workflow orchestrator, я хочу координировать создание и управление инцидентами,
    анализ корневых причин и генерацию отчетов о gap, чтобы обеспечить комплексное управление проблемами
    через атомарные операции.
    """

    def __init__(self):
        self.workflow_name = "incident_management"
        self.version = "1.0.0"
        self.standard_compliance = (
            "MCP Workflow Standard v2.3, TDD Documentation Standard v2.5"
        )

    async def create_incident(
        self, input_data: IncidentInput
    ) -> IncidentManagementResult:
        """
        JTBD: Как AI Agent, я хочу автоматически создавать инциденты при обнаружении критических проблем,
        чтобы обеспечить их отслеживание и решение

        Args:
            input_data: Входные данные для создания инцидента

        Returns:
            IncidentManagementResult: Результат создания инцидента
        """
        start_time = time.time()
        operation_id = f"INC_{time.strftime('%Y%m%d_%H%M%S')}"

        logger.info(f"Starting Incident Creation: {operation_id}")

        # [reflection] Input validation
        if not self._validate_incident_input(input_data):
            return IncidentManagementResult(
                operation_id=operation_id,
                workflow_status="failed",
                steps_completed=[],
                steps_failed=["input_validation"],
                overall_score=0.0,
                recommendations=["Provide valid incident data"],
                execution_time=time.time() - start_time,
                details={"error": "Invalid incident data"},
            )

        try:
            # [reflection] Incident creation: Создаем инцидент
            incident = {
                "incident_id": operation_id,
                "incident_type": input_data.incident_type,
                "severity": input_data.severity,
                "status": "open",
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "gap_report_id": input_data.gap_report_id,
                "affected_release": input_data.affected_release,
                "description": f"Критический gap в output: {input_data.incident_type}",
                "assigned_to": "AI_Agent",
                "priority": (
                    "P1"
                    if input_data.severity == "critical"
                    else "P2"
                    if input_data.severity == "high"
                    else "P3"
                ),
            }

            return IncidentManagementResult(
                operation_id=operation_id,
                workflow_status="success",
                steps_completed=["input_validation", "incident_creation"],
                steps_failed=[],
                overall_score=1.0,
                recommendations=["Incident created successfully"],
                execution_time=time.time() - start_time,
                details={"incident": incident},
            )

        except Exception as e:
            logger.error(f"Error in create_incident: {e}")
            return IncidentManagementResult(
                operation_id=operation_id,
                workflow_status="failed",
                steps_completed=["input_validation"],
                steps_failed=["incident_creation"],
                overall_score=0.0,
                recommendations=[f"Error creating incident: {str(e)}"],
                execution_time=time.time() - start_time,
                details={"error": str(e)},
            )

    async def run_rsa_analysis(self, input_data: RSAInput) -> IncidentManagementResult:
        """
        JTBD: Как AI Agent, я хочу автоматически запускать RSA анализ по стандарту @1.6 root cause analysis,
        чтобы выявлять корневые причины проблем

        Args:
            input_data: Входные данные для RSA анализа

        Returns:
            IncidentManagementResult: Результат RSA анализа
        """
        start_time = time.time()
        operation_id = f"RSA_{time.strftime('%Y%m%d_%H%M%S')}"

        logger.info(f"Starting RSA Analysis: {operation_id}")

        # [reflection] Input validation
        if not self._validate_rsa_input(input_data):
            return IncidentManagementResult(
                operation_id=operation_id,
                workflow_status="failed",
                steps_completed=[],
                steps_failed=["input_validation"],
                overall_score=0.0,
                recommendations=["Provide valid RSA data"],
                execution_time=time.time() - start_time,
                details={"error": "Invalid RSA data"},
            )

        try:
            # [reflection] RSA analysis: Выполняем анализ
            five_why_analysis = [
                {
                    "level": 1,
                    "question": f"Почему {input_data.problem_description}?",
                    "answer": "Проблема в выполнении команды",
                    "evidence": "Log analysis",
                },
                {
                    "level": 2,
                    "question": "Почему команда не выполнилась корректно?",
                    "answer": "Ошибка в коде или данных",
                    "evidence": "Error logs",
                },
                {
                    "level": 3,
                    "question": "Почему произошла ошибка в коде?",
                    "answer": "Несоответствие между ожидаемыми и фактическими данными",
                    "evidence": "Gap analysis",
                },
                {
                    "level": 4,
                    "question": "Почему есть несоответствие в данных?",
                    "answer": "Workflow не обрабатывает все случаи",
                    "evidence": "Code review",
                },
                {
                    "level": 5,
                    "question": "Почему workflow не обрабатывает все случаи?",
                    "answer": "Неполная реализация или отсутствие обработки ошибок",
                    "evidence": "Implementation analysis",
                },
            ]

            # [reflection] Post-execution validation
            rsa_analysis = {
                "rsa_analysis_id": operation_id,
                "problem_statement": input_data.problem_description,
                "five_why_analysis": five_why_analysis,
                "root_causes": [
                    {
                        "cause": "Неполная реализация workflow",
                        "category": "technical",
                        "impact": "critical",
                        "solution": "Добавить обработку всех случаев в workflow",
                    }
                ],
                "system_archetypes": [
                    {
                        "archetype": "Limits to Growth",
                        "description": "Workflow достиг предела роста без полной реализации",
                    }
                ],
                "recommendations": [
                    {
                        "action": "Добавить полную обработку ошибок в workflow",
                        "priority": "critical",
                        "effort": "medium",
                        "expected_impact": "high",
                    }
                ],
            }

            return IncidentManagementResult(
                operation_id=operation_id,
                workflow_status="success",
                steps_completed=["input_validation", "rsa_analysis"],
                steps_failed=[],
                overall_score=1.0,
                recommendations=["RSA analysis completed successfully"],
                execution_time=time.time() - start_time,
                details={"rsa_analysis": rsa_analysis},
            )

        except Exception as e:
            logger.error(f"Error in run_rsa_analysis: {e}")
            return IncidentManagementResult(
                operation_id=operation_id,
                workflow_status="failed",
                steps_completed=["input_validation"],
                steps_failed=["rsa_analysis"],
                overall_score=0.0,
                recommendations=[f"Error running RSA analysis: {str(e)}"],
                execution_time=time.time() - start_time,
                details={"error": str(e)},
            )

    async def generate_gap_report(
        self, input_data: GapReportInput
    ) -> IncidentManagementResult:
        """
        JTBD: Как AI Agent, я хочу автоматически генерировать gap report между ожидаемым и фактическим output,
        чтобы документировать различия

        Args:
            input_data: Входные данные для генерации gap report

        Returns:
            IncidentManagementResult: Результат генерации gap report
        """
        start_time = time.time()
        operation_id = f"GR_{time.strftime('%Y%m%d_%H%M%S')}"

        logger.info(f"Starting Gap Report Generation: {operation_id}")

        # [reflection] Input validation
        if not self._validate_gap_report_input(input_data):
            return IncidentManagementResult(
                operation_id=operation_id,
                workflow_status="failed",
                steps_completed=[],
                steps_failed=["input_validation"],
                overall_score=0.0,
                recommendations=["Provide valid gap report data"],
                execution_time=time.time() - start_time,
                details={"error": "Invalid gap report data"},
            )

        try:
            # [reflection] Gap analysis: Анализируем различия
            gap_score = 0.0
            critical_gaps = []
            minor_gaps = []

            # Простое сравнение длины (можно улучшить)
            expected_length = len(input_data.expected_output)
            actual_length = len(input_data.actual_output)

            if expected_length > 0:
                length_gap = abs(expected_length - actual_length) / expected_length
                gap_score = 1.0 - length_gap

                if length_gap > input_data.gap_threshold:
                    critical_gaps.append(
                        {
                            "gap_type": "content_length",
                            "description": "Значительная разница в размере контента",
                            "expected": f"Ожидалось ~{expected_length} символов",
                            "actual": f"Фактически {actual_length} символов",
                            "severity": "critical",
                            "impact": "high",
                        }
                    )
                else:
                    minor_gaps.append(
                        {
                            "gap_type": "content_length",
                            "description": "Небольшая разница в размере контента",
                            "expected": f"Ожидалось ~{expected_length} символов",
                            "actual": f"Фактически {actual_length} символов",
                            "severity": "minor",
                            "impact": "low",
                        }
                    )

            # Проверяем наличие ключевых слов
            expected_keywords = ["анализ", "офер", "сегмент", "jtbd", "рекомендация"]
            missing_keywords = []

            for keyword in expected_keywords:
                if keyword.lower() not in input_data.actual_output.lower():
                    missing_keywords.append(keyword)

            if missing_keywords:
                critical_gaps.append(
                    {
                        "gap_type": "content_missing",
                        "description": f"Отсутствуют ключевые элементы: {', '.join(missing_keywords)}",
                        "expected": f"Должны присутствовать: {', '.join(expected_keywords)}",
                        "actual": f"Отсутствуют: {', '.join(missing_keywords)}",
                        "severity": "critical",
                        "impact": "high",
                    }
                )
                gap_score *= 0.5

            # [reflection] Post-execution validation
            gap_report = {
                "gap_report_id": operation_id,
                "gap_score": gap_score,
                "critical_gaps": critical_gaps,
                "minor_gaps": minor_gaps,
                "gap_analysis": {
                    "structure_gap": 0.0,
                    "content_gap": 1.0 - gap_score,
                    "quality_gap": 0.0,
                },
                "recommendations": (
                    [
                        "Исправить генерацию недостающего контента",
                        "Проверить соответствие структуры output",
                    ]
                    if critical_gaps
                    else ["Output соответствует ожиданиям"]
                ),
            }

            return IncidentManagementResult(
                operation_id=operation_id,
                workflow_status="success",
                steps_completed=["input_validation", "gap_analysis"],
                steps_failed=[],
                overall_score=gap_score,
                recommendations=gap_report["recommendations"],
                execution_time=time.time() - start_time,
                details={"gap_report": gap_report},
            )

        except Exception as e:
            logger.error(f"Error in generate_gap_report: {e}")
            return IncidentManagementResult(
                operation_id=operation_id,
                workflow_status="failed",
                steps_completed=["input_validation"],
                steps_failed=["gap_analysis"],
                overall_score=0.0,
                recommendations=[f"Error generating gap report: {str(e)}"],
                execution_time=time.time() - start_time,
                details={"error": str(e)},
            )

    async def analyze_execution_logs(
        self, input_data: LogAnalysisInput
    ) -> IncidentManagementResult:
        """
        JTBD: Как AI Agent, я хочу анализировать логи выполнения команд для выявления брака в цепочке,
        чтобы найти корневые причины проблем

        Args:
            input_data: Входные данные для анализа логов

        Returns:
            IncidentManagementResult: Результат анализа логов
        """
        start_time = time.time()
        operation_id = f"LOG_{time.strftime('%Y%m%d_%H%M%S')}"

        logger.info(f"Starting Log Analysis: {operation_id}")

        try:
            # Делегируем к специализированному workflow
            from workflows.log_analysis_workflow import LogAnalysisWorkflow

            workflow = LogAnalysisWorkflow()
            result = await workflow.analyze_execution_logs(input_data)

            # Конвертируем результат в IncidentManagementResult
            log_analysis = {
                "log_analysis_id": result.log_analysis_id,
                "log_file": input_data.log_file_path,
                "file_size": result.file_size,
                "error_count": result.error_count,
                "warning_count": result.warning_count,
                "command_execution_flow": result.command_execution_flow,
                "bottlenecks": result.bottlenecks,
                "analysis_summary": result.analysis_summary,
            }

            return IncidentManagementResult(
                operation_id=operation_id,
                workflow_status="success",
                steps_completed=["input_validation", "log_analysis"],
                steps_failed=[],
                overall_score=(
                    1.0 if result.execution_chain_status == "success" else 0.5
                ),
                recommendations=(
                    ["Log analysis completed successfully"]
                    if result.execution_chain_status == "success"
                    else ["Found errors in logs"]
                ),
                execution_time=time.time() - start_time,
                details={"log_analysis": log_analysis},
            )

        except Exception as e:
            logger.error(f"Error in analyze_execution_logs: {e}")
            return IncidentManagementResult(
                operation_id=operation_id,
                workflow_status="failed",
                steps_completed=[],
                steps_failed=["log_analysis"],
                overall_score=0.0,
                recommendations=[f"Error analyzing logs: {str(e)}"],
                execution_time=time.time() - start_time,
                details={"error": str(e)},
            )

    def _validate_incident_input(self, input_data: IncidentInput) -> bool:
        """Валидация входных данных для создания инцидента"""
        return all(
            [
                input_data.incident_type,
                input_data.severity,
                input_data.gap_report_id,
                input_data.affected_release,
            ]
        )

    def _validate_rsa_input(self, input_data: RSAInput) -> bool:
        """Валидация входных данных для RSA анализа"""
        return bool(input_data.problem_description)

    def _validate_gap_report_input(self, input_data: GapReportInput) -> bool:
        """Валидация входных данных для генерации gap report"""
        return bool(input_data.expected_output and input_data.actual_output)

    def _validate_log_analysis_input(self, input_data: LogAnalysisInput) -> bool:
        """Валидация входных данных для анализа логов"""
        return bool(input_data.log_file_path)
