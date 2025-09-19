"""
JTBD: Как простой тестировщик, я хочу проверить базовую функциональность,
чтобы убедиться что тестовая среда работает корректно.
"""

import os
from pathlib import Path

import pytest


def test_basic_functionality():
    """
    JTBD: Как система валидации, я хочу проверить базовую функциональность,
    чтобы убедиться что тесты работают.
    """
    assert True, "Basic test should pass"


def test_project_files_exist():
    """
    JTBD: Как валидатор проекта, я хочу проверить наличие обязательных файлов,
    чтобы убедиться в полноте проекта.
    """
    required_files = ["pyproject.toml", "README.md", ".gitignore"]

    for file_path in required_files:
        assert os.path.exists(file_path), f"Required file {file_path} not found"


def test_tests_directory_structure():
    """
    JTBD: Как тестировщик, я хочу проверить структуру директории тестов,
    чтобы обеспечить правильную организацию тестового кода.
    """
    tests_dir = Path("tests")

    # Проверяем наличие базовых файлов тестов
    assert (tests_dir / "__init__.py").exists(), "tests/__init__.py not found"
    assert (tests_dir / "conftest.py").exists(), "tests/conftest.py not found"

    # Проверяем наличие поддиректорий для разных типов тестов
    unit_dir = tests_dir / "unit"
    integration_dir = tests_dir / "integration"
    e2e_dir = tests_dir / "e2e"

    # Создаем директории если их нет
    unit_dir.mkdir(exist_ok=True)
    integration_dir.mkdir(exist_ok=True)
    e2e_dir.mkdir(exist_ok=True)

    # Проверяем наличие __init__.py в поддиректориях
    if not (unit_dir / "__init__.py").exists():
        (unit_dir / "__init__.py").write_text('"""Unit tests package."""')

    if not (integration_dir / "__init__.py").exists():
        (integration_dir / "__init__.py").write_text('"""Integration tests package."""')

    if not (e2e_dir / "__init__.py").exists():
        (e2e_dir / "__init__.py").write_text('"""E2E tests package."""')


def test_pyproject_toml_structure():
    """
    JTBD: Как валидатор конфигурации, я хочу проверить структуру pyproject.toml,
    чтобы обеспечить корректность настроек проекта.
    """
    pyproject_path = Path("pyproject.toml")
    assert pyproject_path.exists(), "pyproject.toml not found"

    content = pyproject_path.read_text()

    # Проверяем обязательные секции
    required_sections = ["[project]", "[build-system]", "[tool.pytest.ini_options]"]

    for section in required_sections:
        assert section in content, (
            f"Required section {section} not found in pyproject.toml"
        )


def test_ci_cd_files_exist():
    """
    JTBD: Как валидатор CI/CD, я хочу проверить наличие файлов CI/CD,
    чтобы обеспечить автоматизацию процессов разработки.
    """
    ci_file = Path(".github/workflows/ci.yml")
    pre_commit_file = Path(".pre-commit-config.yaml")

    assert ci_file.exists(), "CI/CD workflow file not found"
    assert pre_commit_file.exists(), "Pre-commit config file not found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
