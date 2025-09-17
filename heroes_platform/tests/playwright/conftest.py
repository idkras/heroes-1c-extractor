"""
Playwright Test Configuration
"""

import pytest
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright


@pytest.fixture(scope="session")
async def browser():
    """Create a browser instance for the test session."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        yield browser
        await browser.close()


@pytest.fixture
async def page(browser):
    """Create a new page for each test."""
    page = await browser.new_page()
    yield page
    await page.close()


@pytest.fixture
def screenshot_dir():
    """Get the screenshot directory."""
    return Path(__file__).parent.parent.parent / "output_screenshot"


@pytest.fixture
def test_data():
    """Test data for different scenarios."""
    return {
        "rickai_docs": {
            "url": "https://idkras.github.io/rickai-docs/technical/adjust_appmetrica_integration/",
            "expected_elements": [
                ".md-header",
                ".md-nav--primary", 
                ".md-content",
                "details[open]",
                "pre code",
                "table"
            ],
            "critical_defects": [
                "vertical_text_rendering",
                "overlapping_elements",
                "broken_css_layout"
            ]
        }
    }
