"""
JTBD: Как тестовая конфигурация, я хочу предоставить общие фикстуры и настройки,
чтобы обеспечить единообразие и переиспользование в тестах.
"""

from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest


@pytest.fixture(scope="session")
def test_environment() -> dict[str, Any]:
    """
    JTBD: Как тестовая среда, я хочу предоставить настройки окружения,
    чтобы обеспечить консистентность тестового окружения.
    """
    return {
        "TESTING": True,
        "DEBUG": False,
        "DATABASE_URL": "sqlite:///:memory:",
        "LOG_LEVEL": "ERROR",
    }


@pytest.fixture
def mock_mcp_server() -> Generator[Mock, None, None]:
    """
    JTBD: Как тестовая фикстура, я хочу предоставить mock MCP сервера,
    чтобы изолировать тесты от внешних зависимостей.
    """
    mock_server = Mock()
    mock_server.start.return_value = True
    mock_server.stop.return_value = True
    mock_server.is_running.return_value = False
    yield mock_server


@pytest.fixture
def sample_project_data() -> dict[str, Any]:
    """
    JTBD: Как тестовая фикстура, я хочу предоставить образцы данных проекта,
    чтобы обеспечить реалистичные тестовые сценарии.
    """
    return {
        "name": "test-project",
        "version": "0.1.0",
        "description": "Test project for TDD validation",
        "author": "Test Author",
        "email": "test@example.com",
    }


@pytest.fixture
def temp_test_dir(tmp_path) -> Generator[str, None, None]:
    """
    JTBD: Как тестовая фикстура, я хочу предоставить временную директорию,
    чтобы обеспечить изоляцию тестовых файлов.
    """
    test_dir = tmp_path / "test_project"
    test_dir.mkdir()
    yield str(test_dir)


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch, test_environment):
    """
    JTBD: Как автоматическая фикстура, я хочу настроить тестовое окружение,
    чтобы обеспечить правильные переменные окружения для всех тестов.
    """
    for key, value in test_environment.items():
        monkeypatch.setenv(key, str(value))


@pytest.fixture
def mock_file_system(tmp_path):
    """
    JTBD: Как тестовая фикстура, я хочу предоставить mock файловой системы,
    чтобы изолировать тесты от реальной файловой системы.
    """
    # Создаем временные файлы для тестирования
    test_file = tmp_path / "test_file.txt"
    test_file.write_text("test content")

    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()

    return {
        "root": str(tmp_path),
        "test_file": str(test_file),
        "test_dir": str(test_dir),
    }


@pytest.fixture
def screenshot_dir(tmp_path) -> Path:
    """Fixture for screenshot directory"""
    screenshot_dir = tmp_path / "screenshots"
    screenshot_dir.mkdir(exist_ok=True)
    return screenshot_dir


@pytest.fixture
def test_data() -> dict[str, Any]:
    """Fixture for test data"""
    return {
        "rickai_docs": {"url": "https://idkras.github.io/rickai-docs/"},
        "ghost_blogs": {"2025": "http://5.75.239.205", "2022_RU": "https://rick.ai"},
    }


@pytest.fixture
async def browser():
    """Fixture for Playwright browser"""
    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            yield browser
            await browser.close()
    except ImportError:
        pytest.skip("Playwright not installed")


@pytest.fixture
async def page(browser):
    """Fixture for Playwright page"""
    if browser is None:
        pytest.skip("Browser not available")
    page = await browser.new_page()
    yield page
    await page.close()
