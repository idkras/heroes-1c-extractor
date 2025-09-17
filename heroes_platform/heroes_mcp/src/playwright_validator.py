#!/usr/bin/env python3
"""
Playwright Validator for Real Visual Testing
Validates actual visual appearance of web pages
"""

import asyncio
import json
import time
from typing import Any

from playwright.async_api import async_playwright


class PlaywrightValidator:
    def __init__(self):
        self.browser = None
        self.page = None

    async def validate_page_visual(self, url: str) -> dict[str, Any]:
        """
        Real visual validation using Playwright
        """
        async with async_playwright() as p:
            self.browser = await p.chromium.launch(headless=True)
            self.page = await self.browser.new_page()

            try:
                # Navigate to page
                start_time = time.time()
                await self.page.goto(url, wait_until="networkidle")
                load_time = time.time() - start_time

                # Take screenshot for analysis
                screenshot_path = f"validation_screenshot_{int(time.time())}.png"
                await self.page.screenshot(path=screenshot_path, full_page=True)

                # Analyze visual elements
                analysis = await self._analyze_visual_elements()

                # Check for critical visual defects
                defects = await self._check_visual_defects()

                # Check navigation functionality
                navigation_check = await self._check_navigation()

                # Check content layout
                layout_check = await self._check_content_layout()

                return {
                    "url": url,
                    "load_time": round(load_time, 2),
                    "screenshot_path": screenshot_path,
                    "visual_analysis": analysis,
                    "critical_defects": defects,
                    "navigation_check": navigation_check,
                    "layout_check": layout_check,
                    "timestamp": time.time(),
                }

            finally:
                await self.browser.close()

    async def _analyze_visual_elements(self) -> dict[str, Any]:
        """Analyze visual elements on the page"""
        return {
            "header_visible": await self.page.locator(".md-header").is_visible(),
            "navigation_visible": await self.page.locator(
                ".md-nav--primary"
            ).is_visible(),
            "content_visible": await self.page.locator(".md-content").is_visible(),
            "details_sections": len(await self.page.locator("details").all()),
            "open_details": len(await self.page.locator("details[open]").all()),
            "code_blocks": len(await self.page.locator("pre code").all()),
            "tables": len(await self.page.locator("table").all()),
        }

    async def _check_visual_defects(self) -> list[dict[str, Any]]:
        """Check for critical visual defects"""
        defects = []

        # Check for vertical text rendering (TOC issues)
        vertical_text = await self.page.locator("text=/^[А-ЯЁ]$/").all()
        if vertical_text:
            defects.append(
                {
                    "type": "critical",
                    "description": "Vertical text rendering detected - TOC broken",
                    "count": len(vertical_text),
                    "severity": "critical",
                }
            )

        # Check for overlapping elements
        overlapping = await self.page.evaluate(
            """
            () => {
                const elements = document.querySelectorAll('*');
                const overlaps = [];
                for (let i = 0; i < elements.length; i++) {
                    for (let j = i + 1; j < elements.length; j++) {
                        const rect1 = elements[i].getBoundingClientRect();
                        const rect2 = elements[j].getBoundingClientRect();
                        if (rect1.left < rect2.right && rect1.right > rect2.left &&
                            rect1.top < rect2.bottom && rect1.bottom > rect2.top) {
                            overlaps.push({
                                element1: elements[i].tagName,
                                element2: elements[j].tagName
                            });
                        }
                    }
                }
                return overlaps;
            }
        """
        )

        if overlapping:
            defects.append(
                {
                    "type": "layout",
                    "description": "Overlapping elements detected",
                    "count": len(overlapping),
                    "severity": "major",
                }
            )

        # Check for broken CSS
        broken_css = await self.page.evaluate(
            """
            () => {
                const styles = getComputedStyle(document.body);
                const issues = [];

                // Check if main content has proper width
                const content = document.querySelector('.md-content');
                if (content) {
                    const contentWidth = content.offsetWidth;
                    const viewportWidth = window.innerWidth;
                    if (contentWidth > viewportWidth * 0.9) {
                        issues.push('Content too wide');
                    }
                }

                // Check if navigation is properly positioned
                const nav = document.querySelector('.md-nav--primary');
                if (nav) {
                    const navStyle = getComputedStyle(nav);
                    if (navStyle.position !== 'fixed') {
                        issues.push('Navigation not fixed');
                    }
                }

                return issues;
            }
        """
        )

        if broken_css:
            defects.append(
                {
                    "type": "css",
                    "description": "CSS layout issues detected",
                    "issues": broken_css,
                    "severity": "major",
                }
            )

        return defects

    async def _check_navigation(self) -> dict[str, Any]:
        """Check navigation functionality"""
        nav_links = await self.page.locator(".md-nav__link").all()
        nav_links_count = len(nav_links)

        # Check if navigation links are clickable
        clickable_links = 0
        for link in nav_links:
            if await link.is_visible() and await link.is_enabled():
                clickable_links += 1

        return {
            "total_links": nav_links_count,
            "clickable_links": clickable_links,
            "navigation_working": clickable_links > 0,
        }

    async def _check_content_layout(self) -> dict[str, Any]:
        """Check content layout and positioning"""
        content = await self.page.locator(".md-content")

        if await content.count() > 0:
            content_element = content.first
            bounding_box = await content_element.bounding_box()

            return {
                "content_width": bounding_box["width"],
                "content_height": bounding_box["height"],
                "content_x": bounding_box["x"],
                "content_y": bounding_box["y"],
                "viewport_width": await self.page.evaluate("window.innerWidth"),
                "viewport_height": await self.page.evaluate("window.innerHeight"),
                "content_visible": await content_element.is_visible(),
            }

        return {"error": "Content element not found"}


async def validate_page_with_playwright(url: str) -> str:
    """
    Main function to validate page using Playwright
    Returns JSON string with validation results
    """
    validator = PlaywrightValidator()
    result = await validator.validate_page_visual(url)
    return json.dumps(result, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # Test function
    async def test():
        result = await validate_page_with_playwright(
            "https://idkras.github.io/rickai-docs/technical/adjust_appmetrica_integration/"
        )
        print(result)

    asyncio.run(test())
