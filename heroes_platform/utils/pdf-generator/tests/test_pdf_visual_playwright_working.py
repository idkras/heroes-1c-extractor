#!/usr/bin/env python3
"""
Рабочий Playwright тестер для визуальной проверки PDF документов.
"""

import asyncio
import json
from pathlib import Path

from playwright.async_api import async_playwright


async def test_pdf_with_browser(pdf_path):
    """Тестирует PDF документ через браузер."""

    results = {
        "pdf_file": pdf_path,
        "issues": [],
        "passed_checks": [],
        "screenshots": [],
    }

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                executable_path="/nix/store/chromium-*/bin/chromium"
            )
            page = await browser.new_page()

            # Открываем PDF
            await page.goto(f"file://{Path(pdf_path).absolute()}")
            await page.wait_for_timeout(2000)

            # Получаем содержимое
            content = await page.inner_text("body")

            # Проверки
            if "##" in content:
                results["issues"].append("Символы ## найдены в тексте")
            else:
                results["passed_checks"].append("Markdown обработан правильно")

            if content.count('"') > content.count("«"):
                results["issues"].append("Неправильные кавычки")
            else:
                results["passed_checks"].append("Кавычки правильные")

            # Скриншот
            screenshot_path = pdf_path.replace(".pdf", "_test_screenshot.png")
            await page.screenshot(path=screenshot_path)
            results["screenshots"].append(screenshot_path)

            await browser.close()

    except Exception as e:
        results["error"] = str(e)

    return results


async def main():
    """Запуск теста."""
    pdf_path = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_Emergency_Fix.pdf"

    if not Path(pdf_path).exists():
        print(f"PDF файл не найден: {pdf_path}")
        return

    results = await test_pdf_with_browser(pdf_path)

    print("РЕЗУЛЬТАТЫ ВИЗУАЛЬНОГО ТЕСТИРОВАНИЯ:")
    print("-" * 40)

    for check in results.get("passed_checks", []):
        print(f"✓ {check}")

    for issue in results.get("issues", []):
        print(f"❌ {issue}")

    if "error" in results:
        print(f"Ошибка: {results['error']}")

    # Сохраняем отчет
    report_file = pdf_path.replace(".pdf", "_visual_test_report.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nОтчет сохранен: {report_file}")


if __name__ == "__main__":
    asyncio.run(main())
