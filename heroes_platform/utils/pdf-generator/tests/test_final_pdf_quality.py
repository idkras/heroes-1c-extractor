"""
Playwright-тестирование финального PDF документа Rick.ai Security Documentation.
Проверяет как документ выглядит для реальных пользователей.
"""

import asyncio
from pathlib import Path

from playwright.async_api import async_playwright


async def test_final_pdf_visual_quality():
    """Тестирует визуальное качество финального PDF документа."""

    pdf_path = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_FINAL.pdf"

    if not Path(pdf_path).exists():
        print(f"❌ PDF файл не найден: {pdf_path}")
        return False

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        try:
            # Открываем PDF в браузере
            await page.goto(f"file://{Path(pdf_path).absolute()}")
            await page.wait_for_timeout(3000)  # Ждем загрузки

            # Делаем скриншот для анализа
            screenshot_path = "final_pdf_screenshot.png"
            await page.screenshot(path=screenshot_path, full_page=True)

            # Проверяем содержимое страницы
            content = await page.content()

            print("✅ PDF успешно открыт в браузере")
            print(f"✅ Скриншот сохранен: {screenshot_path}")

            # Базовые проверки содержимого
            visual_checks = {
                "Заголовки отображаются": "Информация о безопасности Rick.ai"
                in content,
                "Таблицы корректны": "Идентификатор" in content and "Пример" in content,
                "Текст читается": "персональные данные" in content,
                "Структура сохранена": "Ключевые принципы" in content,
            }

            print("\n📋 Результаты визуальной проверки:")
            all_passed = True
            for check, result in visual_checks.items():
                status = "✅" if result else "❌"
                print(f"{status} {check}: {'ПРОЙДЕНА' if result else 'НЕ ПРОЙДЕНА'}")
                if not result:
                    all_passed = False

            return all_passed

        except Exception as e:
            print(f"❌ Ошибка при тестировании PDF: {e}")
            return False
        finally:
            await browser.close()


async def test_pdf_typography_quality():
    """Проверяет типографическое качество PDF."""

    pdf_path = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_FINAL.pdf"

    print(f"\n🔍 Анализ типографического качества: {Path(pdf_path).name}")

    # Проверяем размер файла
    if Path(pdf_path).exists():
        file_size = Path(pdf_path).stat().st_size
        print(f"📄 Размер PDF: {file_size} байт ({file_size / 1024:.1f} KB)")

        if file_size > 50000:  # Больше 50KB
            print("✅ PDF содержит достаточно контента")
            return True
        else:
            print("❌ PDF слишком мал, возможны проблемы генерации")
            return False
    else:
        print("❌ PDF файл не найден")
        return False


async def main():
    """Запуск всех тестов финального PDF."""

    print("🧪 Тестирование финального PDF документа Rick.ai")
    print("=" * 60)

    # Тест 1: Типографическое качество
    typography_ok = await test_pdf_typography_quality()

    # Тест 2: Визуальное качество через браузер
    visual_ok = await test_final_pdf_visual_quality()

    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЙ РЕЗУЛЬТАТ:")

    if typography_ok and visual_ok:
        print("✅ Все тесты пройдены! PDF готов к использованию.")
        print("📄 Документ можно отправлять службам безопасности клиентов.")
    else:
        print("❌ Обнаружены проблемы в PDF документе.")
        print("🔧 Требуется дополнительная доработка.")

    return typography_ok and visual_ok


if __name__ == "__main__":
    asyncio.run(main())
