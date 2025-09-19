"""
Manual Visual Tests for Rick.ai Documentation
Each test case is linked to a specific screenshot
"""

from pathlib import Path

import pytest
from playwright.async_api import Page


class TestRickAiDocsVisual:
    """Visual validation tests for Rick.ai documentation"""

    @pytest.mark.asyncio
    @pytest.mark.visual
    @pytest.mark.manual
    async def test_header_white_no_shadow(
        self, page: Page, screenshot_dir: Path, test_data: dict
    ):
        """
        Test Case: Header should be white without shadow
        Screenshot: header_white_no_shadow.png
        """
        url = test_data["rickai_docs"]["url"]
        await page.goto(url, wait_until="networkidle")

        # Take screenshot for this test case
        screenshot_path = screenshot_dir / "header_white_no_shadow.png"
        await page.screenshot(path=str(screenshot_path), full_page=False)

        # Check header styling
        header = page.locator(".md-header")
        await header.wait_for()

        # Get computed styles
        background_color = await header.evaluate(
            """
            (el) => {
                const style = getComputedStyle(el);
                return style.backgroundColor;
            }
        """
        )

        box_shadow = await header.evaluate(
            """
            (el) => {
                const style = getComputedStyle(el);
                return style.boxShadow;
            }
        """
        )

        # Assertions
        assert "rgb(255, 255, 255)" in background_color, (
            f"Header should be white, got: {background_color}"
        )
        assert box_shadow == "none" or "0px" in box_shadow, (
            f"Header should have no shadow, got: {box_shadow}"
        )

        print(f"✅ Header test passed - Screenshot: {screenshot_path}")

    @pytest.mark.asyncio
    @pytest.mark.visual
    @pytest.mark.manual
    async def test_left_navigation_visible(
        self, page: Page, screenshot_dir: Path, test_data: dict
    ):
        """
        Test Case: Left navigation should be visible and functional
        Screenshot: left_navigation_visible.png
        """
        url = test_data["rickai_docs"]["url"]
        await page.goto(url, wait_until="networkidle")

        screenshot_path = screenshot_dir / "left_navigation_visible.png"
        await page.screenshot(path=str(screenshot_path), full_page=False)

        # Check left navigation
        nav = page.locator(".md-nav--primary")
        await nav.wait_for()

        is_visible = await nav.is_visible()
        nav_links = await page.locator(".md-nav__link").all()

        # Check navigation positioning
        position = await nav.evaluate(
            """
            (el) => {
                const style = getComputedStyle(el);
                return style.position;
            }
        """
        )

        assert is_visible, "Left navigation should be visible"
        assert len(nav_links) > 0, "Navigation should have links"
        assert position == "fixed", f"Navigation should be fixed, got: {position}"

        print(f"✅ Left navigation test passed - Screenshot: {screenshot_path}")

    @pytest.mark.asyncio
    @pytest.mark.visual
    @pytest.mark.manual
    async def test_no_vertical_text_defect(
        self, page: Page, screenshot_dir: Path, test_data: dict
    ):
        """
        Test Case: No vertical text rendering (TOC defect)
        Screenshot: no_vertical_text_defect.png
        """
        url = test_data["rickai_docs"]["url"]
        await page.goto(url, wait_until="networkidle")

        screenshot_path = screenshot_dir / "no_vertical_text_defect.png"
        await page.screenshot(path=str(screenshot_path), full_page=True)

        # Check for vertical text rendering (critical defect)
        vertical_text_elements = await page.evaluate(
            """
            () => {
                const elements = document.querySelectorAll('*');
                const verticalText = [];

                for (const el of elements) {
                    const style = getComputedStyle(el);
                    const text = el.textContent;

                    // Check for Cyrillic characters in vertical orientation
                    if (text && /[А-ЯЁ]/.test(text)) {
                        const rect = el.getBoundingClientRect();
                        if (rect.height > rect.width * 2) {
                            verticalText.push({
                                text: text.substring(0, 50),
                                element: el.tagName,
                                position: {x: rect.x, y: rect.y}
                            });
                        }
                    }
                }
                return verticalText;
            }
        """
        )

        # This should be empty - no vertical text defects
        assert len(vertical_text_elements) == 0, (
            f"Found vertical text defects: {vertical_text_elements}"
        )

        print(f"✅ No vertical text defect test passed - Screenshot: {screenshot_path}")

    @pytest.mark.asyncio
    @pytest.mark.visual
    @pytest.mark.manual
    async def test_content_width_70_percent(
        self, page: Page, screenshot_dir: Path, test_data: dict
    ):
        """
        Test Case: Main content should be 70% width
        Screenshot: content_width_70_percent.png
        """
        url = test_data["rickai_docs"]["url"]
        await page.goto(url, wait_until="networkidle")

        screenshot_path = screenshot_dir / "content_width_70_percent.png"
        await page.screenshot(path=str(screenshot_path), full_page=False)

        # Check content width
        content = page.locator(".md-content")
        await content.wait_for()

        content_width = await content.evaluate(
            """
            (el) => {
                const rect = el.getBoundingClientRect();
                return rect.width;
            }
        """
        )

        viewport_width = await page.evaluate("window.innerWidth")
        content_percentage = (content_width / viewport_width) * 100

        # Should be approximately 70%
        assert 65 <= content_percentage <= 75, (
            f"Content should be ~70% width, got: {content_percentage:.1f}%"
        )

        print(f"✅ Content width test passed - Screenshot: {screenshot_path}")

    @pytest.mark.asyncio
    @pytest.mark.visual
    @pytest.mark.manual
    async def test_details_sections_open(
        self, page: Page, screenshot_dir: Path, test_data: dict
    ):
        """
        Test Case: All details sections should be open by default
        Screenshot: details_sections_open.png
        """
        url = test_data["rickai_docs"]["url"]
        await page.goto(url, wait_until="networkidle")

        screenshot_path = screenshot_dir / "details_sections_open.png"
        await page.screenshot(path=str(screenshot_path), full_page=True)

        # Count all details sections
        all_details = await page.locator("details").all()
        open_details = await page.locator("details[open]").all()

        # All details should be open
        assert len(all_details) > 0, "Should have details sections"
        assert len(open_details) == len(all_details), (
            f"All details should be open. Found {len(open_details)}/{len(all_details)}"
        )

        print(f"✅ Details sections test passed - Screenshot: {screenshot_path}")

    @pytest.mark.asyncio
    @pytest.mark.visual
    @pytest.mark.manual
    async def test_font_size_15pt(
        self, page: Page, screenshot_dir: Path, test_data: dict
    ):
        """
        Test Case: Main text should be ~15pt (12px)
        Screenshot: font_size_15pt.png
        """
        url = test_data["rickai_docs"]["url"]
        await page.goto(url, wait_until="networkidle")

        screenshot_path = screenshot_dir / "font_size_15pt.png"
        await page.screenshot(path=str(screenshot_path), full_page=False)

        # Check paragraph font size
        paragraph = page.locator(".md-content p").first
        await paragraph.wait_for()

        font_size = await paragraph.evaluate(
            """
            (el) => {
                const style = getComputedStyle(el);
                return parseFloat(style.fontSize);
            }
        """
        )

        # 12px = 15pt approximately
        assert 10 <= font_size <= 14, f"Font size should be ~12px, got: {font_size}px"

        print(f"✅ Font size test passed - Screenshot: {screenshot_path}")

    @pytest.mark.asyncio
    @pytest.mark.visual
    @pytest.mark.manual
    async def test_no_overlapping_elements(
        self, page: Page, screenshot_dir: Path, test_data: dict
    ):
        """
        Test Case: No overlapping elements
        Screenshot: no_overlapping_elements.png
        """
        url = test_data["rickai_docs"]["url"]
        await page.goto(url, wait_until="networkidle")

        screenshot_path = screenshot_dir / "no_overlapping_elements.png"
        await page.screenshot(path=str(screenshot_path), full_page=True)

        # Check for overlapping elements
        overlapping = await page.evaluate(
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

        # Should have minimal overlapping (only expected overlaps)
        assert len(overlapping) <= 5, (
            f"Too many overlapping elements: {len(overlapping)}"
        )

        print(f"✅ No overlapping elements test passed - Screenshot: {screenshot_path}")

    @pytest.mark.asyncio
    @pytest.mark.visual
    @pytest.mark.manual
    async def test_navigation_links_clickable(
        self, page: Page, screenshot_dir: Path, test_data: dict
    ):
        """
        Test Case: Navigation links should be clickable
        Screenshot: navigation_links_clickable.png
        """
        url = test_data["rickai_docs"]["url"]
        await page.goto(url, wait_until="networkidle")

        screenshot_path = screenshot_dir / "navigation_links_clickable.png"
        await page.screenshot(path=str(screenshot_path), full_page=False)

        # Check navigation links
        nav_links = await page.locator(".md-nav__link").all()

        clickable_count = 0
        for link in nav_links:
            if await link.is_visible() and await link.is_enabled():
                clickable_count += 1

        assert clickable_count > 0, "Should have clickable navigation links"
        assert clickable_count >= len(nav_links) * 0.8, (
            f"Most links should be clickable. {clickable_count}/{len(nav_links)}"
        )

        print(f"✅ Navigation links test passed - Screenshot: {screenshot_path}")
