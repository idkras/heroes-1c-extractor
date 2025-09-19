"""
Playwright Tests for Rick.ai Documentation
Using Playwright's built-in test runner
"""

import asyncio
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright


async def test_rickai_docs_visual():
    """Run all visual tests for Rick.ai documentation"""

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        url = "https://idkras.github.io/rickai-docs/technical/adjust_appmetrica_integration/"
        output_dir = Path(__file__).parent.parent.parent / "output_screenshot"
        output_dir.mkdir(exist_ok=True)

        results = {"url": url, "tests": [], "screenshots": [], "status": "running"}

        try:
            # Navigate to page
            await page.goto(url, wait_until="networkidle")

            # Wait for CSS to load and apply
            await page.wait_for_timeout(3000)  # 3 seconds delay for CSS

            # Test 1: Header white no shadow
            try:
                header = page.locator(".md-header")
                await header.wait_for()

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

                # Take screenshot - FULL PAGE with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = (
                    output_dir / f"01_header_white_no_shadow_{timestamp}.png"
                )
                await page.screenshot(path=str(screenshot_path), full_page=True)

                test_result = {
                    "name": "header_white_no_shadow",
                    "status": "passed"
                    if "rgb(255, 255, 255)" in background_color
                    and (box_shadow == "none" or "0px" in box_shadow)
                    else "failed",
                    "screenshot": str(screenshot_path),
                    "details": {
                        "background_color": background_color,
                        "box_shadow": box_shadow,
                    },
                }
                results["tests"].append(test_result)
                results["screenshots"].append(str(screenshot_path))

            except Exception as e:
                test_result = {
                    "name": "header_white_no_shadow",
                    "status": "error",
                    "error": str(e),
                }
                results["tests"].append(test_result)

            # Test 2: Left navigation visible
            try:
                nav = page.locator(".md-nav--primary")
                await nav.wait_for()

                is_visible = await nav.is_visible()
                nav_links = await page.locator(".md-nav__link").all()

                position = await nav.evaluate(
                    """
                    (el) => {
                        const style = getComputedStyle(el);
                        return style.position;
                    }
                """
                )

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = (
                    output_dir / f"02_left_navigation_visible_{timestamp}.png"
                )
                await page.screenshot(path=str(screenshot_path), full_page=True)

                test_result = {
                    "name": "left_navigation_visible",
                    "status": "passed"
                    if is_visible and len(nav_links) > 0 and position == "fixed"
                    else "failed",
                    "screenshot": str(screenshot_path),
                    "details": {
                        "visible": is_visible,
                        "links_count": len(nav_links),
                        "position": position,
                    },
                }
                results["tests"].append(test_result)
                results["screenshots"].append(str(screenshot_path))

            except Exception as e:
                test_result = {
                    "name": "left_navigation_visible",
                    "status": "error",
                    "error": str(e),
                }
                results["tests"].append(test_result)

            # Test 3: No vertical text defect
            try:
                vertical_text_elements = await page.evaluate(
                    """
                    () => {
                        const elements = document.querySelectorAll('*');
                        const verticalText = [];

                        for (const el of elements) {
                            const style = getComputedStyle(el);
                            const text = el.textContent;

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

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = (
                    output_dir / f"03_no_vertical_text_defect_{timestamp}.png"
                )
                await page.screenshot(path=str(screenshot_path), full_page=True)

                test_result = {
                    "name": "no_vertical_text_defect",
                    "status": "passed"
                    if len(vertical_text_elements) == 0
                    else "failed",
                    "screenshot": str(screenshot_path),
                    "details": {
                        "vertical_text_count": len(vertical_text_elements),
                        "vertical_text_elements": vertical_text_elements,
                    },
                }
                results["tests"].append(test_result)
                results["screenshots"].append(str(screenshot_path))

            except Exception as e:
                test_result = {
                    "name": "no_vertical_text_defect",
                    "status": "error",
                    "error": str(e),
                }
                results["tests"].append(test_result)

            # Test 4: Content width 70%
            try:
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

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = (
                    output_dir / f"04_content_width_70_percent_{timestamp}.png"
                )
                await page.screenshot(path=str(screenshot_path), full_page=True)

                test_result = {
                    "name": "content_width_70_percent",
                    "status": "passed" if 65 <= content_percentage <= 75 else "failed",
                    "screenshot": str(screenshot_path),
                    "details": {
                        "content_width": content_width,
                        "viewport_width": viewport_width,
                        "content_percentage": content_percentage,
                    },
                }
                results["tests"].append(test_result)
                results["screenshots"].append(str(screenshot_path))

            except Exception as e:
                test_result = {
                    "name": "content_width_70_percent",
                    "status": "error",
                    "error": str(e),
                }
                results["tests"].append(test_result)

            # Test 5: Details sections open
            try:
                all_details = await page.locator("details").all()
                open_details = await page.locator("details[open]").all()

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = (
                    output_dir / f"05_details_sections_open_{timestamp}.png"
                )
                await page.screenshot(path=str(screenshot_path), full_page=True)

                test_result = {
                    "name": "details_sections_open",
                    "status": "passed"
                    if len(all_details) > 0 and len(open_details) == len(all_details)
                    else "failed",
                    "screenshot": str(screenshot_path),
                    "details": {
                        "all_details_count": len(all_details),
                        "open_details_count": len(open_details),
                    },
                }
                results["tests"].append(test_result)
                results["screenshots"].append(str(screenshot_path))

            except Exception as e:
                test_result = {
                    "name": "details_sections_open",
                    "status": "error",
                    "error": str(e),
                }
                results["tests"].append(test_result)

            # Test 6: Font size 15pt
            try:
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

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = output_dir / f"06_font_size_15pt_{timestamp}.png"
                await page.screenshot(path=str(screenshot_path), full_page=True)

                test_result = {
                    "name": "font_size_15pt",
                    "status": "passed" if 10 <= font_size <= 14 else "failed",
                    "screenshot": str(screenshot_path),
                    "details": {"font_size": font_size},
                }
                results["tests"].append(test_result)
                results["screenshots"].append(str(screenshot_path))

            except Exception as e:
                test_result = {
                    "name": "font_size_15pt",
                    "status": "error",
                    "error": str(e),
                }
                results["tests"].append(test_result)

            # Calculate overall status
            passed_tests = sum(
                1 for test in results["tests"] if test["status"] == "passed"
            )
            total_tests = len(results["tests"])

            if passed_tests == total_tests:
                results["status"] = "passed"
            elif passed_tests > 0:
                results["status"] = "partial"
            else:
                results["status"] = "failed"

            results["summary"] = {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": sum(
                    1 for test in results["tests"] if test["status"] == "failed"
                ),
                "error_tests": sum(
                    1 for test in results["tests"] if test["status"] == "error"
                ),
            }

        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)

        finally:
            await browser.close()

        return results


async def main():
    """Run the tests and print results"""
    results = await test_rickai_docs_visual()

    print("=== PLAYWRIGHT VISUAL TESTS RESULTS ===")
    print(f"URL: {results['url']}")
    print(f"Status: {results['status'].upper()}")

    if "summary" in results:
        print(
            f"Tests: {results['summary']['passed_tests']}/{results['summary']['total_tests']} passed"
        )

    print("\nTest Details:")
    for test in results["tests"]:
        status_icon = (
            "✅"
            if test["status"] == "passed"
            else "❌"
            if test["status"] == "failed"
            else "⚠️"
        )
        print(f"{status_icon} {test['name']}: {test['status']}")
        if "details" in test:
            print(f"   Details: {test['details']}")
        if "error" in test:
            print(f"   Error: {test['error']}")

    print(f"\nScreenshots ({len(results['screenshots'])}):")
    for screenshot in results["screenshots"]:
        print(f"  - {screenshot}")

    return results


if __name__ == "__main__":
    asyncio.run(main())
