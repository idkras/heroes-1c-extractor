#!/usr/bin/env python3
"""
Unit tests for Incident Management Workflow

JTBD: Как разработчик, я хочу протестировать incident_management_workflow,
чтобы убедиться в корректности работы всех функций.

Основан на TDD Documentation Standard.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock
from pathlib import Path

# Добавляем путь к workflows в sys.path
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "workflows"))

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "workflows"))
from incident_management_workflow import (
    IncidentManagementWorkflow,
    IncidentInput,
    RSAInput,
    GapReportInput,
    LogAnalysisInput,
)


class TestIncidentManagementWorkflow:
    """Тесты для IncidentManagementWorkflow"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.workflow = IncidentManagementWorkflow()

    @pytest.mark.asyncio
    async def test_create_incident_success(self):
        """GIVEN valid incident data WHEN create_incident THEN return success result"""
        # Arrange
        input_data = IncidentInput(
            incident_type="validation_failure",
            severity="critical",
            gap_report_id="GR_20250101_120000",
            affected_release="v1.0.0",
        )

        # Act
        result = await self.workflow.create_incident(input_data)

        # Assert
        assert result.workflow_status == "success"
        assert result.overall_score == 1.0
        assert "input_validation" in result.steps_completed
        assert "incident_creation" in result.steps_completed
        assert len(result.steps_failed) == 0
        assert "incident" in result.details
        assert result.details["incident"]["incident_type"] == "validation_failure"
        assert result.details["incident"]["severity"] == "critical"

    @pytest.mark.asyncio
    async def test_create_incident_invalid_input(self):
        """GIVEN invalid incident data WHEN create_incident THEN return failure result"""
        # Arrange
        input_data = IncidentInput(
            incident_type="",  # Invalid: empty
            severity="critical",
            gap_report_id="GR_20250101_120000",
            affected_release="v1.0.0",
        )

        # Act
        result = await self.workflow.create_incident(input_data)

        # Assert
        assert result.workflow_status == "failed"
        assert result.overall_score == 0.0
        assert "input_validation" in result.steps_failed
        assert len(result.steps_completed) == 0

    @pytest.mark.asyncio
    async def test_run_rsa_analysis_success(self):
        """GIVEN valid RSA data WHEN run_rsa_analysis THEN return success result"""
        # Arrange
        input_data = RSAInput(
            problem_description="Workflow failed to execute",
            incident_id="INC_20250101_120000",
            evidence_data="Error logs",
            analysis_depth="5_why",
        )

        # Act
        result = await self.workflow.run_rsa_analysis(input_data)

        # Assert
        assert result.workflow_status == "success"
        assert result.overall_score == 1.0
        assert "input_validation" in result.steps_completed
        assert "rsa_analysis" in result.steps_completed
        assert len(result.steps_failed) == 0
        assert "rsa_analysis" in result.details
        assert len(result.details["rsa_analysis"]["five_why_analysis"]) == 5

    @pytest.mark.asyncio
    async def test_run_rsa_analysis_invalid_input(self):
        """GIVEN invalid RSA data WHEN run_rsa_analysis THEN return failure result"""
        # Arrange
        input_data = RSAInput(
            problem_description="",  # Invalid: empty
            incident_id="INC_20250101_120000",
            evidence_data="Error logs",
            analysis_depth="5_why",
        )

        # Act
        result = await self.workflow.run_rsa_analysis(input_data)

        # Assert
        assert result.workflow_status == "failed"
        assert result.overall_score == 0.0
        assert "input_validation" in result.steps_failed
        assert len(result.steps_completed) == 0

    @pytest.mark.asyncio
    async def test_generate_gap_report_success(self):
        """GIVEN valid gap report data WHEN generate_gap_report THEN return success result"""
        # Arrange
        input_data = GapReportInput(
            expected_output="Ожидаемый анализ с ключевыми словами: анализ, офер, сегмент, jtbd, рекомендация",
            actual_output="Фактический анализ с ключевыми словами: анализ, офер, сегмент, jtbd, рекомендация",
            gap_threshold=0.3,
        )

        # Act
        result = await self.workflow.generate_gap_report(input_data)

        # Assert
        assert result.workflow_status == "success"
        assert result.overall_score > 0.5  # Должен быть высокий score
        assert "input_validation" in result.steps_completed
        assert "gap_analysis" in result.steps_completed
        assert len(result.steps_failed) == 0
        assert "gap_report" in result.details
        assert result.details["gap_report"]["gap_score"] > 0.5

    @pytest.mark.asyncio
    async def test_generate_gap_report_critical_gaps(self):
        """GIVEN data with critical gaps WHEN generate_gap_report THEN return low score"""
        # Arrange
        input_data = GapReportInput(
            expected_output="Ожидаемый анализ с ключевыми словами: анализ, офер, сегмент, jtbd, рекомендация",
            actual_output="Короткий текст без ключевых слов",  # Много отсутствующих ключевых слов
            gap_threshold=0.3,
        )

        # Act
        result = await self.workflow.generate_gap_report(input_data)

        # Assert
        assert result.workflow_status == "success"
        assert result.overall_score < 0.5  # Должен быть низкий score
        assert "gap_report" in result.details
        assert len(result.details["gap_report"]["critical_gaps"]) > 0

    @pytest.mark.asyncio
    async def test_generate_gap_report_invalid_input(self):
        """GIVEN invalid gap report data WHEN generate_gap_report THEN return failure result"""
        # Arrange
        input_data = GapReportInput(
            expected_output="",  # Invalid: empty
            actual_output="Фактический анализ",
            gap_threshold=0.3,
        )

        # Act
        result = await self.workflow.generate_gap_report(input_data)

        # Assert
        assert result.workflow_status == "failed"
        assert result.overall_score == 0.0
        assert "input_validation" in result.steps_failed
        assert len(result.steps_completed) == 0

    @pytest.mark.asyncio
    async def test_analyze_execution_logs_success(self):
        """GIVEN valid log file WHEN analyze_execution_logs THEN return success result"""
        # Arrange
        input_data = LogAnalysisInput(
            log_file_path="test_log.txt", time_range="", command_chain=""
        )

        # Mock file content
        mock_content = """
        INFO: heroes_gpt_workflow started
        INFO: file_output_manager.generate_analysis_markdown completed
        INFO: Workflow completed successfully
        """

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.read_text", return_value=mock_content),
        ):

            # Act
            result = await self.workflow.analyze_execution_logs(input_data)

            # Assert
            assert result.workflow_status == "success"
            assert result.overall_score == 1.0  # Нет ошибок
            assert "input_validation" in result.steps_completed
            assert "log_analysis" in result.steps_completed
            assert "log_analysis" in result.steps_completed
            assert len(result.steps_failed) == 0
            assert "log_analysis" in result.details
            assert result.details["log_analysis"]["error_count"] == 0

    @pytest.mark.asyncio
    async def test_analyze_execution_logs_with_errors(self):
        """GIVEN log file with errors WHEN analyze_execution_logs THEN return low score"""
        # Arrange
        input_data = LogAnalysisInput(
            log_file_path="test_log.txt", time_range="", command_chain=""
        )

        # Mock file content with errors
        mock_content = """
        INFO: heroes_gpt_workflow started
        ERROR: Critical error in workflow
        EXCEPTION: Something went wrong
        WARNING: Performance issue detected
        """

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.read_text", return_value=mock_content),
        ):

            # Act
            result = await self.workflow.analyze_execution_logs(input_data)

            # Assert
            assert result.workflow_status == "success"
            assert result.overall_score == 0.5  # Есть ошибки
            assert "log_analysis" in result.details
            assert result.details["log_analysis"]["error_count"] > 0
            assert result.details["log_analysis"]["warning_count"] > 0

    @pytest.mark.asyncio
    async def test_analyze_execution_logs_file_not_found(self):
        """GIVEN non-existent log file WHEN analyze_execution_logs THEN return failure result"""
        # Arrange
        input_data = LogAnalysisInput(
            log_file_path="non_existent_log.txt", time_range="", command_chain=""
        )

        with patch("pathlib.Path.exists", return_value=False):

            # Act
            result = await self.workflow.analyze_execution_logs(input_data)

            # Assert
            assert result.workflow_status == "failed"
            assert result.overall_score == 0.0
            assert "log_analysis" in result.steps_failed
            assert len(result.steps_completed) == 0

    @pytest.mark.asyncio
    async def test_analyze_execution_logs_invalid_input(self):
        """GIVEN invalid log analysis data WHEN analyze_execution_logs THEN return failure result"""
        # Arrange
        input_data = LogAnalysisInput(
            log_file_path="", time_range="", command_chain=""  # Invalid: empty
        )

        # Act
        result = await self.workflow.analyze_execution_logs(input_data)

        # Assert
        assert result.workflow_status == "failed"
        assert result.overall_score == 0.0
        assert "log_analysis" in result.steps_failed
        assert len(result.steps_completed) == 0


class TestIncidentManagementWorkflowValidation:
    """Тесты валидации для IncidentManagementWorkflow"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.workflow = IncidentManagementWorkflow()

    def test_validate_incident_input_valid(self):
        """GIVEN valid incident input WHEN validate THEN return True"""
        # Arrange
        input_data = IncidentInput(
            incident_type="validation_failure",
            severity="critical",
            gap_report_id="GR_20250101_120000",
            affected_release="v1.0.0",
        )

        # Act
        result = self.workflow._validate_incident_input(input_data)

        # Assert
        assert result is True

    def test_validate_incident_input_invalid(self):
        """GIVEN invalid incident input WHEN validate THEN return False"""
        # Arrange
        input_data = IncidentInput(
            incident_type="",  # Invalid: empty
            severity="critical",
            gap_report_id="GR_20250101_120000",
            affected_release="v1.0.0",
        )

        # Act
        result = self.workflow._validate_incident_input(input_data)

        # Assert
        assert result is False

    def test_validate_rsa_input_valid(self):
        """GIVEN valid RSA input WHEN validate THEN return True"""
        # Arrange
        input_data = RSAInput(
            problem_description="Workflow failed",
            incident_id="INC_20250101_120000",
            evidence_data="Error logs",
        )

        # Act
        result = self.workflow._validate_rsa_input(input_data)

        # Assert
        assert result is True

    def test_validate_rsa_input_invalid(self):
        """GIVEN invalid RSA input WHEN validate THEN return False"""
        # Arrange
        input_data = RSAInput(
            problem_description="",  # Invalid: empty
            incident_id="INC_20250101_120000",
            evidence_data="Error logs",
        )

        # Act
        result = self.workflow._validate_rsa_input(input_data)

        # Assert
        assert result is False

    def test_validate_gap_report_input_valid(self):
        """GIVEN valid gap report input WHEN validate THEN return True"""
        # Arrange
        input_data = GapReportInput(
            expected_output="Expected content", actual_output="Actual content"
        )

        # Act
        result = self.workflow._validate_gap_report_input(input_data)

        # Assert
        assert result is True

    def test_validate_gap_report_input_invalid(self):
        """GIVEN invalid gap report input WHEN validate THEN return False"""
        # Arrange
        input_data = GapReportInput(
            expected_output="", actual_output="Actual content"  # Invalid: empty
        )

        # Act
        result = self.workflow._validate_gap_report_input(input_data)

        # Assert
        assert result is False

    def test_validate_log_analysis_input_valid(self):
        """GIVEN valid log analysis input WHEN validate THEN return True"""
        # Arrange
        input_data = LogAnalysisInput(log_file_path="test_log.txt")

        # Act
        result = self.workflow._validate_log_analysis_input(input_data)

        # Assert
        assert result is True

    def test_validate_log_analysis_input_invalid(self):
        """GIVEN invalid log analysis input WHEN validate THEN return False"""
        # Arrange
        input_data = LogAnalysisInput(log_file_path="")  # Invalid: empty

        # Act
        result = self.workflow._validate_log_analysis_input(input_data)

        # Assert
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__])
