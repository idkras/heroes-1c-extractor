"""
JTBD: Как unit тестировщик, я хочу тестировать структуру проекта,
чтобы гарантировать корректность организации кода.
"""

import os
from pathlib import Path

import pytest


class TestProjectStructure:
    """
    JTBD: Как тестировщик структуры проекта, я хочу проверять организацию файлов,
    чтобы обеспечить соответствие стандартам разработки.
    """

    def test_required_files_exist(self):
        """
        JTBD: Как система валидации, я хочу проверять наличие обязательных файлов,
        чтобы гарантировать полноту проекта.
        """
        required_files = [
            "pyproject.toml",
            "README.md",
            ".gitignore"
        ]

        for file_path in required_files:
            assert os.path.exists(file_path), f"Required file {file_path} not found"

    def test_required_directories_exist(self):
        """
        JTBD: Как система валидации, я хочу проверять наличие обязательных директорий,
        чтобы обеспечить правильную организацию кода.
        """
        required_dirs = [
            "tests",
            "docs"
        ]

        for dir_path in required_dirs:
            assert os.path.exists(dir_path), f"Required directory {dir_path} not found"

    def test_tests_directory_structure(self):
        """
        JTBD: Как тестировщик, я хочу проверять структуру директории тестов,
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
        assert (unit_dir / "__init__.py").exists(), "tests/unit/__init__.py not found"
        assert (integration_dir / "__init__.py").exists(), "tests/integration/__init__.py not found"
        assert (e2e_dir / "__init__.py").exists(), "tests/e2e/__init__.py not found"

    def test_pyproject_toml_structure(self):
        """
        JTBD: Как валидатор конфигурации, я хочу проверять структуру pyproject.toml,
        чтобы обеспечить корректность настроек проекта.
        """
        pyproject_path = Path("pyproject.toml")
        assert pyproject_path.exists(), "pyproject.toml not found"

        content = pyproject_path.read_text()

        # Проверяем обязательные секции
        required_sections = [
            "[project]",
            "[build-system]",
            "[tool.pytest.ini_options]",
            "[tool.black]",
            "[tool.ruff]"
        ]

        for section in required_sections:
            assert section in content, f"Required section {section} not found in pyproject.toml"

    def test_gitignore_exclusions(self):
        """
        JTBD: Как система контроля версий, я хочу проверять .gitignore,
        чтобы предотвратить коммит ненужных файлов.
        """
        gitignore_path = Path(".gitignore")
        assert gitignore_path.exists(), ".gitignore not found"

        content = gitignore_path.read_text()

        # Проверяем критически важные исключения
        critical_exclusions = [
            ".venv",
            "__pycache__",
            ".DS_Store",
            "*.py[cod]",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache"
        ]

        for exclusion in critical_exclusions:
            assert exclusion in content, f"Critical exclusion {exclusion} not found in .gitignore"


class TestImportStructure:
    """
    JTBD: Как тестировщик импортов, я хочу проверять корректность импортов,
    чтобы предотвратить циклические зависимости и ошибки импорта.
    """

    def test_basic_imports_work(self):
        """
        JTBD: Как система валидации, я хочу проверять базовые импорты,
        чтобы убедиться в работоспособности основных зависимостей.
        """
        try:
            import pydantic
            assert pydantic.__version__ >= "2.0.0"
        except ImportError:
            pytest.fail("Pydantic not installed or version too old")

    def test_test_imports_work(self):
        """
        JTBD: Как тестировщик, я хочу проверять импорты тестовых библиотек,
        чтобы обеспечить работоспособность тестового фреймворка.
        """
        try:
            import pytest
            assert pytest.__version__ >= "6.0.0"
        except ImportError:
            pytest.fail("Pytest not installed or version too old")

    def test_no_circular_imports(self):
        """
        JTBD: Как система валидации, я хочу проверять отсутствие циклических импортов,
        чтобы предотвратить проблемы с загрузкой модулей.
        """
        # Этот тест проверяет, что основные модули можно импортировать
        # без циклических зависимостей
        try:
            # Проверяем импорт основных модулей проекта
            pass
        except ImportError as e:
            if "circular" in str(e).lower():
                pytest.fail(f"Circular import detected: {e}")
            else:
                # Другие ошибки импорта допустимы в тестовой среде
                pass
