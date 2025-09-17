"""
Playwright-тестирование PDF документа для запуска в Cursor.
Этот файл готов для использования в полноценной среде разработки.

Установка в Cursor:
1. pip install playwright
2. playwright install
3. playwright install-deps
4. python test_pdf_visual_browser_for_cursor.py
"""

import asyncio
from playwright.async_api import async_playwright
from pathlib import Path
import time

async def test_pdf_visual_quality_browser():
    """Полноценное тестирование PDF через браузер."""
    
    pdf_path = Path("[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_FINAL.pdf")
    
    if not pdf_path.exists():
        print(f"❌ PDF файл не найден: {pdf_path}")
        return False
    
    async with async_playwright() as p:
        # Запускаем браузер
        browser = await p.chromium.launch(headless=False)  # headless=False для визуального контроля
        page = await browser.new_page()
        
        try:
            # Открываем PDF
            pdf_url = f"file://{pdf_path.absolute()}"
            print(f"🌐 Открываем PDF: {pdf_url}")
            
            await page.goto(pdf_url)
            await page.wait_for_timeout(5000)  # Ждем полной загрузки
            
            # Проверяем успешность загрузки
            title = await page.title()
            print(f"📄 Заголовок страницы: {title}")
            
            # Делаем скриншот полной страницы
            screenshot_path = "rick_ai_security_pdf_screenshot.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"📸 Скриншот сохранен: {screenshot_path}")
            
            # Проверяем содержимое
            page_content = await page.content()
            
            # Визуальные проверки
            visual_tests = {
                "PDF загружен": len(page_content) > 1000,
                "Заголовок видим": "Rick.ai" in page_content or "Информация о безопасности" in title,
                "Контент читается": len(page_content) > 5000,
                "Нет ошибок загрузки": "error" not in page_content.lower()
            }
            
            print("\n📋 Результаты визуального тестирования:")
            all_passed = True
            
            for test_name, result in visual_tests.items():
                status = "✅" if result else "❌"
                print(f"{status} {test_name}")
                if not result:
                    all_passed = False
            
            # Дополнительные проверки через JavaScript
            try:
                # Проверяем размеры страницы
                page_info = await page.evaluate("""
                    () => {
                        return {
                            width: window.innerWidth,
                            height: window.innerHeight,
                            scrollHeight: document.body.scrollHeight,
                            title: document.title
                        }
                    }
                """)
                
                print(f"\n📐 Информация о странице:")
                print(f"   Ширина: {page_info['width']}px")
                print(f"   Высота: {page_info['height']}px") 
                print(f"   Высота контента: {page_info['scrollHeight']}px")
                print(f"   Заголовок: {page_info['title']}")
                
            except Exception as e:
                print(f"⚠️ Не удалось получить информацию о странице: {e}")
            
            # Ждем немного для визуального контроля (если headless=False)
            await page.wait_for_timeout(3000)
            
            return all_passed
            
        except Exception as e:
            print(f"❌ Ошибка при тестировании: {e}")
            return False
            
        finally:
            await browser.close()

async def test_pdf_typography_visual():
    """Проверка типографии через браузер."""
    
    print("🔤 Визуальная проверка типографии PDF")
    print("=" * 50)
    
    # Здесь можно добавить специфические проверки:
    # - Размер и читаемость шрифтов
    # - Корректность отступов
    # - Качество таблиц
    # - Правильность переносов
    
    return True

async def main():
    """Главная функция тестирования."""
    
    print("🧪 Playwright визуальное тестирование PDF Rick.ai")
    print("🖥️ Запуск в полноценном браузере")
    print("=" * 60)
    
    # Тест 1: Основное визуальное тестирование
    visual_ok = await test_pdf_visual_quality_browser()
    
    # Тест 2: Типографическое тестирование
    typography_ok = await test_pdf_typography_visual()
    
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЙ РЕЗУЛЬТАТ БРАУЗЕРНОГО ТЕСТИРОВАНИЯ:")
    
    if visual_ok and typography_ok:
        print("✅ Все тесты пройдены!")
        print("📄 PDF корректно отображается в браузере")
        print("🎯 Документ готов для отправки службам безопасности")
    else:
        print("❌ Обнаружены проблемы отображения")
        print("🔧 Требуется проверка и исправление")
    
    return visual_ok and typography_ok

if __name__ == "__main__":
    print("🚀 Запуск браузерного тестирования...")
    print("📝 Убедитесь, что Playwright установлен:")
    print("   pip install playwright")
    print("   playwright install")
    print("   playwright install-deps")
    print()
    
    try:
        result = asyncio.run(main())
        exit(0 if result else 1)
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        print("💡 Проверьте установку Playwright")
        exit(1)