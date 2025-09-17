#!/usr/bin/env python3
"""
Unit tests for CrossCheckWorkflow

JTBD: Как тестировщик, я хочу проверить все аспекты cross-check workflow,
чтобы гарантировать корректную работу валидации результатов.

Согласно TDD Documentation Standard.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

# Import the workflow to test
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "workflows"))
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "workflows"))
from cross_check_workflow import CrossCheckWorkflow


class TestCrossCheckWorkflow:
    """
    Unit tests for CrossCheckWorkflow

    Согласно TDD Documentation Standard:
    - Тесты покрывают все методы workflow класса
    - Мокируются внешние зависимости
    - Проверяется корректность возвращаемых данных
    - Тестируются граничные случаи и ошибки
    """

    def setup_method(self):
        """Setup test environment"""
        self.workflow = CrossCheckWorkflow()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Cleanup test environment"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_file(self, content: str, filename: str = "test.txt") -> str:
        """Create a test file with given content"""
        file_path = os.path.join(self.temp_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

    @pytest.mark.asyncio
    async def test_execute_with_valid_file(self):
        """Test cross-check with valid file"""
        # Arrange
        content = "This is a valid test content with multiple lines.\nIt has good formatting and sufficient length."
        file_path = self.create_test_file(content)

        # Act
        result = await self.workflow.execute(file_path)

        # Assert
        assert result["cross_check_status"] == "passed"
        assert result["cross_check_score"] >= 80
        assert "File is empty" not in result["cross_check_issues"]
        assert "Content too short" not in result["cross_check_issues"]
        assert "Poor formatting" not in result["cross_check_issues"]
        assert result["result_id"] == "cross_check_test"

    @pytest.mark.asyncio
    async def test_execute_with_empty_file(self):
        """Test cross-check with empty file"""
        # Arrange
        file_path = self.create_test_file("")

        # Act
        result = await self.workflow.execute(file_path)

        # Assert
        assert result["cross_check_status"] == "failed"
        assert "File is empty" in result["cross_check_issues"]
        assert result["cross_check_score"] < 80

    @pytest.mark.asyncio
    async def test_execute_with_short_content(self):
        """Test cross-check with short content"""
        # Arrange
        file_path = self.create_test_file("Short")

        # Act
        result = await self.workflow.execute(file_path)

        # Assert
        assert result["cross_check_status"] == "failed"
        assert "Content too short" in result["cross_check_issues"]
        assert result["cross_check_score"] < 80

    @pytest.mark.asyncio
    async def test_execute_with_poor_formatting(self):
        """Test cross-check with poor formatting"""
        # Arrange
        content = "This is content without proper formatting or line breaks."
        file_path = self.create_test_file(content)

        # Act
        result = await self.workflow.execute(file_path)

        # Assert
        assert result["cross_check_status"] == "failed"
        assert "Poor formatting" in result["cross_check_issues"]
        assert result["cross_check_score"] < 80

    @pytest.mark.asyncio
    async def test_execute_with_valid_json(self):
        """Test cross-check with valid JSON file"""
        # Arrange
        json_content = json.dumps(
            {
                "test": "data",
                "number": 42,
                "description": "This is a longer JSON content to meet the minimum length requirement for cross-check validation",
                "items": ["item1", "item2", "item3"],
                "nested": {"key": "value", "another_key": "another_value"},
            }
        )
        file_path = self.create_test_file(json_content, "test.json")

        # Act
        result = await self.workflow.execute(file_path)

        # Assert
        assert result["cross_check_status"] == "passed"
        assert "Invalid JSON format" not in result["cross_check_issues"]
        assert result["user_preview"]["format"] == "json"

    @pytest.mark.asyncio
    async def test_execute_with_invalid_json(self):
        """Test cross-check with invalid JSON file"""
        # Arrange
        invalid_json = '{"test": "data", "number": 42,}'  # Trailing comma
        file_path = self.create_test_file(invalid_json, "test.json")

        # Act
        result = await self.workflow.execute(file_path)

        # Assert
        assert result["cross_check_status"] == "failed"
        assert "Invalid JSON format" in result["cross_check_issues"]

    @pytest.mark.asyncio
    async def test_execute_with_error_indicators(self):
        """Test cross-check with error indicators"""
        # Arrange
        content = "This content contains error messages.\nError: Something went wrong.\nAnother error occurred."
        file_path = self.create_test_file(content)

        # Act
        result = await self.workflow.execute(file_path)

        # Assert
        # Should still pass if not too many errors
        assert result["cross_check_status"] == "passed"

    @pytest.mark.asyncio
    async def test_execute_with_many_errors(self):
        """Test cross-check with many error indicators"""
        # Arrange
        error_lines = ["Error: " + str(i) for i in range(15)]
        content = "\n".join(error_lines)
        file_path = self.create_test_file(content)

        # Act
        result = await self.workflow.execute(file_path)

        # Assert
        assert result["cross_check_status"] == "failed"
        assert "Contains too many error indicators" in result["cross_check_issues"]

    @pytest.mark.asyncio
    async def test_execute_with_reference_comparison(self):
        """Test cross-check with reference file comparison"""
        # Arrange
        content = "This is the main content for testing with sufficient length to pass all checks.\nIt has multiple lines and good formatting."
        file_path = self.create_test_file(content, "main.txt")

        ref_content = "This is the reference content for testing with sufficient length to pass all checks.\nIt has multiple lines and good formatting."
        ref_path = self.create_test_file(ref_content, "reference.txt")

        # Act
        result = await self.workflow.execute(file_path, ref_path)

        # Assert
        assert result["cross_check_status"] == "passed"
        # Should pass because length difference is small

    @pytest.mark.asyncio
    async def test_execute_with_different_reference(self):
        """Test cross-check with significantly different reference"""
        # Arrange
        content = "This is a content with sufficient length to pass basic checks but will be compared to a much longer reference."
        file_path = self.create_test_file(content, "main.txt")

        ref_content = (
            "This is a much longer reference content that will cause a significant difference in length when compared to the main content. "
            * 50
        )
        ref_path = self.create_test_file(ref_content, "reference.txt")

        # Act
        result = await self.workflow.execute(file_path, ref_path)

        # Assert
        assert "Significant difference from reference" in result["cross_check_issues"]

    @pytest.mark.asyncio
    async def test_execute_with_nonexistent_file(self):
        """Test cross-check with non-existent file"""
        # Arrange
        nonexistent_path = os.path.join(self.temp_dir, "nonexistent.txt")

        # Act
        result = await self.workflow.execute(nonexistent_path)

        # Assert
        assert result["cross_check_status"] == "failed"
        assert "Result file not found" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_with_empty_path(self):
        """Test cross-check with empty path"""
        # Arrange
        empty_path = ""

        # Act
        result = await self.workflow.execute(empty_path)

        # Assert
        assert result["cross_check_status"] == "failed"
        assert "Result path is required" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_with_nonexistent_reference(self):
        """Test cross-check with non-existent reference file"""
        # Arrange
        content = "Main content with sufficient length to pass all checks.\nIt has multiple lines and good formatting."
        file_path = self.create_test_file(content, "main.txt")
        nonexistent_ref = os.path.join(self.temp_dir, "nonexistent_ref.txt")

        # Act
        result = await self.workflow.execute(file_path, nonexistent_ref)

        # Assert
        # Should still pass because reference is optional
        assert result["cross_check_status"] == "passed"

    @pytest.mark.asyncio
    async def test_execute_with_different_check_types(self):
        """Test cross-check with different check types"""
        # Arrange
        content = "This is a valid test content with multiple lines.\nIt has good formatting and sufficient length."
        file_path = self.create_test_file(content)

        # Act & Assert for different check types
        for check_type in ["basic", "comprehensive", "strict"]:
            result = await self.workflow.execute(file_path, check_type=check_type)
            assert result["check_type"] == check_type
            assert result["cross_check_status"] == "passed"

    def test_create_error_response(self):
        """Test error response creation"""
        # Arrange
        error_message = "Test error message"

        # Act
        result = self.workflow._create_error_response(error_message)

        # Assert
        assert result["error"] == error_message
        assert result["cross_check_status"] == "failed"
        assert result["evidence_links"] == []
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_execute_with_file_read_error(self):
        """Test cross-check with file read error"""
        # Arrange
        file_path = self.create_test_file("test content")

        # Mock Path.read_text to raise exception
        with patch(
            "pathlib.Path.read_text", side_effect=PermissionError("Permission denied")
        ):
            # Act
            result = await self.workflow.execute(file_path)

            # Assert
            assert result["cross_check_status"] == "failed"
            assert "Error reading file" in result["cross_check_issues"][0]

    @pytest.mark.asyncio
    async def test_execute_with_reference_read_error(self):
        """Test cross-check with reference file read error"""
        # Arrange
        content = "Main content with sufficient length to pass all checks.\nIt has multiple lines and good formatting."
        file_path = self.create_test_file(content, "main.txt")
        ref_path = self.create_test_file("Reference content", "reference.txt")

        # Mock Path.read_text to raise exception for reference file only
        original_read_text = Path.read_text

        def mock_read_text(self, *args, **kwargs):
            if str(self) == str(ref_path):
                raise PermissionError("Permission denied")
            return original_read_text(self, *args, **kwargs)

        with patch("pathlib.Path.read_text", mock_read_text):
            # Act
            result = await self.workflow.execute(file_path, ref_path)

            # Assert
            assert "Error reading reference" in result["cross_check_issues"][0]


if __name__ == "__main__":
    pytest.main([__file__])
