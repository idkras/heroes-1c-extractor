#!/usr/bin/env python3
"""
Tests for Todo Parser Module

Тесты для модуля парсинга todo файлов согласно TDD принципам.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import json

# Import the module to test
import sys

sys.path.append(str(Path(__file__).parent.parent / "src"))

from todo_parser import TodoParser, TodoValidator, TodoCriterion, TodoRelease


class TestTodoCriterion:
    """Тесты для класса TodoCriterion"""

    def test_todo_criterion_creation(self):
        """Тест создания критерия"""
        criterion = TodoCriterion(
            text="Test criterion", is_completed=True, line_number=10
        )

        assert criterion.text == "Test criterion"
        assert criterion.is_completed is True
        assert criterion.line_number == 10

    def test_todo_criterion_not_completed(self):
        """Тест критерия не выполненного"""
        criterion = TodoCriterion(
            text="Not completed criterion", is_completed=False, line_number=15
        )

        assert criterion.is_completed is False


class TestTodoRelease:
    """Тесты для класса TodoRelease"""

    def test_todo_release_creation(self):
        """Тест создания релиза"""
        criteria = [
            TodoCriterion("Criterion 1", True, 1),
            TodoCriterion("Criterion 2", False, 2),
        ]

        release = TodoRelease(
            name="РЕЛИЗ 1",
            content="Test content",
            criteria=criteria,
            start_line=1,
            end_line=10,
        )

        assert release.name == "РЕЛИЗ 1"
        assert release.content == "Test content"
        assert len(release.criteria) == 2
        assert release.start_line == 1
        assert release.end_line == 10


class TestTodoParser:
    """Тесты для класса TodoParser"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.parser = TodoParser()
        self.test_todo_content = """
# Test Todo File

## 📋 **РЕЛИЗ 0: Test Release (30 минут)**

**✅ Критерии успеха (ПЕРЕПЛАНИРОВАНЫ):**

- [x] **Test criterion 1:** This is completed
- [ ] **Test criterion 2:** This is not completed
- [x] **Test criterion 3:** This is also completed

---

## 🚀 **РЕЛИЗ 1: Another Test Release (2 часа)**

**✅ Критерии успеха (ПЕРЕПЛАНИРОВАНЫ):**

- [x] **Release 1 criterion 1:** Completed
- [ ] **Release 1 criterion 2:** Not completed
"""

    def test_parser_initialization(self):
        """Тест инициализации парсера"""
        assert hasattr(self.parser, "release_patterns")
        assert hasattr(self.parser, "criteria_pattern")
        assert hasattr(self.parser, "criteria_section_pattern")

    def test_extract_criteria_from_content(self):
        """Тест извлечения критериев из контента"""
        # Тестируем извлечение критериев из одного релиза
        release_content = """
## 📋 **РЕЛИЗ 0: Test Release (30 минут)**

**✅ Критерии успеха (ПЕРЕПЛАНИРОВАНЫ):**

- [x] **Test criterion 1:** This is completed
- [ ] **Test criterion 2:** This is not completed
- [x] **Test criterion 3:** This is also completed
"""
        criteria = self.parser._extract_criteria(release_content)

        assert len(criteria) == 3  # 3 критерия из одного релиза

        # Проверяем первый критерий
        assert criteria[0].text == "**Test criterion 1:** This is completed"
        assert criteria[0].is_completed is True

        # Проверяем второй критерий
        assert criteria[1].text == "**Test criterion 2:** This is not completed"
        assert criteria[1].is_completed is False

    def test_parse_file_with_temp_file(self):
        """Тест парсинга файла с временным файлом"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(self.test_todo_content)
            temp_file_path = Path(f.name)

        try:
            releases = self.parser.parse_file(temp_file_path)

            assert "РЕЛИЗ 0: Test Release (30 минут)" in releases
            assert "РЕЛИЗ 1: Another Test Release (2 часа)" in releases

            # Проверяем Release 0
            release_0 = releases["РЕЛИЗ 0: Test Release (30 минут)"]
            assert len(release_0.criteria) == 3
            assert release_0.criteria[0].is_completed is True
            assert release_0.criteria[1].is_completed is False

            # Проверяем Release 1
            release_1 = releases["РЕЛИЗ 1: Another Test Release (2 часа)"]
            assert len(release_1.criteria) == 2
            assert release_1.criteria[0].is_completed is True
            assert release_1.criteria[1].is_completed is False

        finally:
            temp_file_path.unlink()

    def test_get_release_criteria_specific_release(self):
        """Тест получения критериев для конкретного релиза"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(self.test_todo_content)
            temp_file_path = Path(f.name)

        try:
            criteria = self.parser.get_release_criteria(
                temp_file_path, "РЕЛИЗ 0: Test Release (30 минут)"
            )

            assert len(criteria) == 3
            assert criteria[0].text == "**Test criterion 1:** This is completed"
            assert criteria[0].is_completed is True

        finally:
            temp_file_path.unlink()

    def test_get_release_criteria_not_found(self):
        """Тест получения критериев для несуществующего релиза"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(self.test_todo_content)
            temp_file_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="Release 'NONEXISTENT' not found"):
                self.parser.get_release_criteria(temp_file_path, "NONEXISTENT")
        finally:
            temp_file_path.unlink()

    def test_parse_file_not_found(self):
        """Тест парсинга несуществующего файла"""
        with pytest.raises(FileNotFoundError):
            self.parser.parse_file(Path("nonexistent_file.md"))


class TestTodoValidator:
    """Тесты для класса TodoValidator"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.parser = TodoParser()
        self.validator = TodoValidator(self.parser)
        self.test_todo_content = """
# Test Todo File

## 📋 **РЕЛИЗ 0: Test Release (30 минут)**

**✅ Критерии успеха (ПЕРЕПЛАНИРОВАНЫ):**

- [x] **Test criterion 1:** This is completed
- [ ] **Test criterion 2:** This is not completed
- [x] **Test criterion 3:** This is also completed
"""

    def test_validator_initialization(self):
        """Тест инициализации валидатора"""
        assert self.validator.parser == self.parser

    def test_validate_release_success(self):
        """Тест успешной валидации релиза"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(self.test_todo_content)
            temp_file_path = Path(f.name)

        try:
            result = self.validator.validate_release(
                temp_file_path, "РЕЛИЗ 0: Test Release (30 минут)"
            )

            # 2 из 3 критериев выполнены = 66.67%, что меньше 80% для "passed"
            assert result["validation_status"] == "failed"
            assert result["todo_file_parsed"] is True
            assert result["success_criteria_found"] == 3
            assert result["validation_score"] == pytest.approx(66.67, rel=0.01)
            assert result["release_name"] == "РЕЛИЗ 0: Test Release (30 минут)"
            assert len(result["criteria_validation"]) == 3

            # Проверяем критерии
            criteria_validation = result["criteria_validation"]
            assert criteria_validation[0]["status"] == "passed"
            assert criteria_validation[1]["status"] == "failed"
            assert criteria_validation[2]["status"] == "passed"

        finally:
            temp_file_path.unlink()

    def test_validate_release_not_found(self):
        """Тест валидации несуществующего релиза"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(self.test_todo_content)
            temp_file_path = Path(f.name)

        try:
            result = self.validator.validate_release(temp_file_path, "NONEXISTENT")

            assert result["validation_status"] == "failed"
            assert result["todo_file_parsed"] is False
            assert result["success_criteria_found"] == 0
            assert result["validation_score"] == 0
            assert "error" in result

        finally:
            temp_file_path.unlink()

    def test_validate_release_file_not_found(self):
        """Тест валидации с несуществующим файлом"""
        result = self.validator.validate_release(Path("nonexistent.md"), "РЕЛИЗ 0")

        assert result["validation_status"] == "failed"
        assert result["todo_file_parsed"] is False
        assert result["success_criteria_found"] == 0
        assert result["validation_score"] == 0
        assert "error" in result

    def test_validate_release_all_completed(self):
        """Тест валидации релиза где все критерии выполнены"""
        all_completed_content = """
# Test Todo File

## 📋 **РЕЛИЗ 0: Test Release (30 минут)**

**✅ Критерии успеха (ПЕРЕПЛАНИРОВАНЫ):**

- [x] **Test criterion 1:** This is completed
- [x] **Test criterion 2:** This is also completed
- [x] **Test criterion 3:** This is also completed
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(all_completed_content)
            temp_file_path = Path(f.name)

        try:
            result = self.validator.validate_release(
                temp_file_path, "РЕЛИЗ 0: Test Release (30 минут)"
            )

            assert result["validation_status"] == "passed"
            assert result["validation_score"] == 100.0
            assert result["success_criteria_found"] == 3

            # Все критерии должны быть passed
            for criterion in result["criteria_validation"]:
                assert criterion["status"] == "passed"

        finally:
            temp_file_path.unlink()


class TestIntegration:
    """Интеграционные тесты"""

    def test_full_workflow(self):
        """Тест полного workflow парсинга и валидации"""
        parser = TodoParser()
        validator = TodoValidator(parser)

        test_content = """
# Integration Test

## 📋 **РЕЛИЗ 0: Integration Test (30 минут)**

**✅ Критерии успеха:**

- [x] **Criterion 1:** Completed
- [ ] **Criterion 2:** Not completed
- [x] **Criterion 3:** Completed

---

## 🚀 **РЕЛИЗ 1: Another Test (2 часа)**

**✅ Критерии успеха:**

- [x] **Release 1 Criterion 1:** Completed
- [ ] **Release 1 Criterion 2:** Not completed
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(test_content)
            temp_file_path = Path(f.name)

        try:
            # Парсим файл
            releases = parser.parse_file(temp_file_path)
            assert len(releases) == 2

            # Валидируем Release 0 (2 из 3 выполнены = 66.67% < 80%)
            result_0 = validator.validate_release(
                temp_file_path, "РЕЛИЗ 0: Integration Test (30 минут)"
            )
            assert result_0["validation_status"] == "failed"
            assert result_0["validation_score"] == pytest.approx(66.67, rel=0.01)

            # Валидируем Release 1 (1 из 2 выполнены = 50% < 80%)
            result_1 = validator.validate_release(
                temp_file_path, "РЕЛИЗ 1: Another Test (2 часа)"
            )
            assert result_1["validation_status"] == "failed"
            assert result_1["validation_score"] == 50.0

        finally:
            temp_file_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__])
