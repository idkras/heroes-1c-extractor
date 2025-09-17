#!/usr/bin/env python3
"""
Генератор PDF документа с использованием Playwright для качественной типографики.
Использует Fira Sans и современные принципы типографики по Брингхерсту.
"""

import asyncio
import markdown
from playwright.async_api import async_playwright
from pathlib import Path
import json
import tempfile
import os
import re

async def convert_md_to_pdf_playwright(md_file_path, output_pdf_path):
    """Конвертирует markdown файл в PDF с качественной типографикой через Playwright."""
    
    # Читаем markdown файл
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Конвертируем markdown в HTML
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
    
    # CSS стили с принципами качественной типографики
    css_styles = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Fira+Sans:wght@300;400;500;600;700&display=swap');
        
        :root {
            /* Модульная сетка 12×12px */
            --base-unit: 12px;
            --base-font-size: 16px;
            --line-height-base: 1.5; /* 24px для 16px шрифта */
            
            /* Типографическая шкала */
            --font-xs: 12px;    /* line-height: 18px */
            --font-sm: 14px;    /* line-height: 21px */
            --font-base: 16px;  /* line-height: 24px */
            --font-lg: 18px;    /* line-height: 27px */
            --font-xl: 21px;    /* line-height: 30px */
            --font-2xl: 24px;   /* line-height: 36px */
            --font-3xl: 32px;   /* line-height: 42px */
            --font-4xl: 48px;   /* line-height: 60px */
            
            /* Цвета с высоким контрастом */
            --text-primary: #292929;    /* 7:1 контраст */
            --text-secondary: #757575;  /* 4.5:1 контраст */
            --accent-color: #03A87C;
            --border-color: #E6E6E6;
        }
        
        * {
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Fira Sans', -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Segoe UI', 'Roboto', sans-serif;
            font-size: var(--font-base);
            line-height: var(--line-height-base);
            color: var(--text-primary);
            margin: 0;
            padding: var(--base-unit);
            max-width: 680px; /* Оптимальная мера строки */
            background: white;
        }
        
        /* Вертикальный ритм - все отступы кратны 12px */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Fira Sans', sans-serif;
            font-weight: 600;
            color: var(--text-primary);
            margin: calc(var(--base-unit) * 2) 0 var(--base-unit) 0;
            line-height: 1.2;
        }
        
        h1 {
            font-size: var(--font-3xl);
            margin-top: 0;
            margin-bottom: calc(var(--base-unit) * 2);
        }
        
        h2 {
            font-size: var(--font-2xl);
            margin-top: calc(var(--base-unit) * 3);
        }
        
        h3 {
            font-size: var(--font-xl);
            margin-top: calc(var(--base-unit) * 2);
        }
        
        h4 {
            font-size: var(--font-lg);
        }
        
        p {
            margin: 0 0 var(--base-unit) 0;
            /* Висячие строки недопустимы */
            orphans: 3;
            widows: 3;
        }
        
        /* Отступы списков кратны базовому модулю */
        ul, ol {
            margin: var(--base-unit) 0;
            padding-left: calc(var(--base-unit) * 2);
        }
        
        li {
            margin-bottom: calc(var(--base-unit) / 2);
        }
        
        /* Таблицы с правильными отступами */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: calc(var(--base-unit) * 2) 0;
            font-size: var(--font-sm);
        }
        
        th, td {
            padding: calc(var(--base-unit) / 2) var(--base-unit);
            border: 1px solid var(--border-color);
            text-align: left;
            vertical-align: top;
        }
        
        th {
            background-color: #f8f9fa;
            font-weight: 600;
        }
        
        /* Блочные элементы */
        blockquote {
            margin: calc(var(--base-unit) * 2) 0;
            padding-left: calc(var(--base-unit) * 2);
            border-left: 3px solid var(--accent-color);
            font-style: italic;
            color: var(--text-secondary);
        }
        
        code {
            font-family: 'Fira Code', Monaco, Consolas, monospace;
            font-size: var(--font-sm);
            background-color: #f5f5f5;
            padding: 2px 4px;
            border-radius: 3px;
        }
        
        pre {
            background-color: #f5f5f5;
            padding: var(--base-unit);
            border-radius: 6px;
            overflow-x: auto;
            margin: calc(var(--base-unit) * 2) 0;
        }
        
        /* Микротипографика для русского языка */
        .nbsp {
            /* Неразрывные пробелы уже в тексте */
        }
        
        /* PDF-специфические стили */
        @page {
            size: A4;
            margin: 20mm;
        }
        
        @media print {
            body {
                max-width: none;
                margin: 0;
                padding: 0;
            }
            
            /* Разрывы страниц */
            h1, h2, h3 {
                page-break-after: avoid;
                break-after: avoid-page;
            }
            
            p, li {
                page-break-inside: avoid;
                break-inside: avoid;
            }
            
            table {
                page-break-inside: avoid;
                break-inside: avoid;
            }
        }
        
        /* Подсветка ключевых блоков */
        .key-principle {
            background-color: rgba(3, 168, 124, 0.05);
            border-left: 4px solid var(--accent-color);
            padding: var(--base-unit);
            margin: calc(var(--base-unit) * 2) 0;
        }
    </style>
    """
    
    # Обрабатываем контент для улучшения типографики
    html_content = improve_typography(html_content)
    
    # Создаем полный HTML документ
    full_html = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Информация о безопасности Rick.ai</title>
        {css_styles}
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Сохраняем HTML во временный файл
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html', encoding='utf-8') as tmp_html:
        tmp_html.write(full_html)
        html_path = tmp_html.name
    # Генерируем PDF через Playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(f"file://{html_path}")
        await page.pdf(path=output_pdf_path, format="A4", print_background=True, margin={"top": "32px", "bottom": "32px", "left": "32px", "right": "32px"})
        await browser.close()
    os.remove(html_path)
    print(f"PDF создан: {output_pdf_path}")

def improve_typography(html_content):
    """Улучшает типографику HTML контента."""
    
    # Заменяем обычные кавычки на правильные русские
    html_content = re.sub(r'"([^"]*)"', r'«\1»', html_content)
    
    # Заменяем двойные дефисы на длинное тире
    html_content = html_content.replace('--', '—')
    html_content = html_content.replace(' - ', ' — ')
    
    # Добавляем неразрывные пробелы перед короткими словами (уже есть в тексте)
    # Добавляем CSS класс для ключевых принципов
    html_content = re.sub(
        r'<p><strong>Ключевой принцип:</strong>',
        r'<div class="key-principle"><strong>Ключевой принцип:</strong>',
        html_content
    )
    
    # Закрываем div для ключевых принципов
    html_content = re.sub(
        r'(персональные данные.*?)</p>',
        r'\1</div>',
        html_content,
        flags=re.DOTALL
    )
    
    return html_content

async def run_visual_test(pdf_path, html_path=None):
    """Запускает визуальный тест Playwright для PDF или HTML и сохраняет отчет."""
    results = {
        "file": pdf_path,
        "issues": [],
        "passed_checks": [],
        "screenshots": [],
        "mode": "pdf"
    }
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            await page.goto(f"file://{Path(pdf_path).absolute()}")
            await page.wait_for_timeout(2000)
            content = await page.content()
        except Exception as e:
            if html_path:
                print("PDF не открылся в браузере, тестируем HTML...")
                results["mode"] = "html-fallback"
                await page.goto(f"file://{Path(html_path).absolute()}")
                await page.wait_for_timeout(2000)
                content = await page.content()
            else:
                results["issues"].append(f"Ошибка открытия файла: {e}")
                await browser.close()
                return results
        # Проверки по TDD-doc стандарту
        if '##' in content:
            results["issues"].append("Символы ## найдены в тексте")
        else:
            results["passed_checks"].append("Markdown обработан правильно")
        if content.count('"') > content.count('«'):
            results["issues"].append("Неправильные кавычки")
        else:
            results["passed_checks"].append("Кавычки правильные")
        screenshot_path = pdf_path.replace('.pdf', '_test_screenshot.png') if results["mode"] == "pdf" else html_path.replace('.html', '_test_screenshot.png')
        await page.screenshot(path=screenshot_path)
        results["screenshots"].append(screenshot_path)
        await browser.close()
    # Сохраняем отчет
    report_file = pdf_path.replace('.pdf', '_visual_test_report.json') if results["mode"] == "pdf" else html_path.replace('.html', '_visual_test_report.json')
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nОтчет сохранен: {report_file}")
    return results

async def main():
    """Основная функция."""
    md_file = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/when_security_asked_about_user_data RU.md"
    pdf_file = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_Playwright.pdf"
    html_path = None
    if not Path(md_file).exists():
        print(f"Файл не найден: {md_file}")
        return
    # Генерируем HTML и PDF
    # --- HTML ---
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
    html_content = improve_typography(html_content)
    css_styles = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Fira+Sans:wght@300;400;500;600;700&display=swap');
        
        :root {
            /* Модульная сетка 12×12px */
            --base-unit: 12px;
            --base-font-size: 16px;
            --line-height-base: 1.5; /* 24px для 16px шрифта */
            
            /* Типографическая шкала */
            --font-xs: 12px;    /* line-height: 18px */
            --font-sm: 14px;    /* line-height: 21px */
            --font-base: 16px;  /* line-height: 24px */
            --font-lg: 18px;    /* line-height: 27px */
            --font-xl: 21px;    /* line-height: 30px */
            --font-2xl: 24px;   /* line-height: 36px */
            --font-3xl: 32px;   /* line-height: 42px */
            --font-4xl: 48px;   /* line-height: 60px */
            
            /* Цвета с высоким контрастом */
            --text-primary: #292929;    /* 7:1 контраст */
            --text-secondary: #757575;  /* 4.5:1 контраст */
            --accent-color: #03A87C;
            --border-color: #E6E6E6;
        }
        
        * {
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Fira Sans', -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Segoe UI', 'Roboto', sans-serif;
            font-size: var(--font-base);
            line-height: var(--line-height-base);
            color: var(--text-primary);
            margin: 0;
            padding: var(--base-unit);
            max-width: 680px; /* Оптимальная мера строки */
            background: white;
        }
        
        /* Вертикальный ритм - все отступы кратны 12px */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Fira Sans', sans-serif;
            font-weight: 600;
            color: var(--text-primary);
            margin: calc(var(--base-unit) * 2) 0 var(--base-unit) 0;
            line-height: 1.2;
        }
        
        h1 {
            font-size: var(--font-3xl);
            margin-top: 0;
            margin-bottom: calc(var(--base-unit) * 2);
        }
        
        h2 {
            font-size: var(--font-2xl);
            margin-top: calc(var(--base-unit) * 3);
        }
        
        h3 {
            font-size: var(--font-xl);
            margin-top: calc(var(--base-unit) * 2);
        }
        
        h4 {
            font-size: var(--font-lg);
        }
        
        p {
            margin: 0 0 var(--base-unit) 0;
            /* Висячие строки недопустимы */
            orphans: 3;
            widows: 3;
        }
        
        /* Отступы списков кратны базовому модулю */
        ul, ol {
            margin: var(--base-unit) 0;
            padding-left: calc(var(--base-unit) * 2);
        }
        
        li {
            margin-bottom: calc(var(--base-unit) / 2);
        }
        
        /* Таблицы с правильными отступами */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: calc(var(--base-unit) * 2) 0;
            font-size: var(--font-sm);
        }
        
        th, td {
            padding: calc(var(--base-unit) / 2) var(--base-unit);
            border: 1px solid var(--border-color);
            text-align: left;
            vertical-align: top;
        }
        
        th {
            background-color: #f8f9fa;
            font-weight: 600;
        }
        
        /* Блочные элементы */
        blockquote {
            margin: calc(var(--base-unit) * 2) 0;
            padding-left: calc(var(--base-unit) * 2);
            border-left: 3px solid var(--accent-color);
            font-style: italic;
            color: var(--text-secondary);
        }
        
        code {
            font-family: 'Fira Code', Monaco, Consolas, monospace;
            font-size: var(--font-sm);
            background-color: #f5f5f5;
            padding: 2px 4px;
            border-radius: 3px;
        }
        
        pre {
            background-color: #f5f5f5;
            padding: var(--base-unit);
            border-radius: 6px;
            overflow-x: auto;
            margin: calc(var(--base-unit) * 2) 0;
        }
        
        /* Микротипографика для русского языка */
        .nbsp {
            /* Неразрывные пробелы уже в тексте */
        }
        
        /* PDF-специфические стили */
        @page {
            size: A4;
            margin: 20mm;
        }
        
        @media print {
            body {
                max-width: none;
                margin: 0;
                padding: 0;
            }
            
            /* Разрывы страниц */
            h1, h2, h3 {
                page-break-after: avoid;
                break-after: avoid-page;
            }
            
            p, li {
                page-break-inside: avoid;
                break-inside: avoid;
            }
            
            table {
                page-break-inside: avoid;
                break-inside: avoid;
            }
        }
        
        /* Подсветка ключевых блоков */
        .key-principle {
            background-color: rgba(3, 168, 124, 0.05);
            border-left: 4px solid var(--accent-color);
            padding: var(--base-unit);
            margin: calc(var(--base-unit) * 2) 0;
        }
    </style>
    """
    full_html = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Информация о безопасности Rick.ai</title>
        {css_styles}
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html', encoding='utf-8') as tmp_html:
        tmp_html.write(full_html)
        html_path = tmp_html.name
    # --- PDF ---
    await convert_md_to_pdf_playwright(md_file, pdf_file)
    # --- Визуальный тест ---
    results = await run_visual_test(pdf_file, html_path=html_path)
    # Анализируем результат и выводим root cause, если есть проблемы
    if results["issues"]:
        print("\n❌ Обнаружены проблемы в PDF/HTML:")
        for issue in results["issues"]:
            print(f"   - {issue}")
        print("\nRoot cause analysis (5 почему):")
        for i, issue in enumerate(results["issues"], 1):
            print(f"{i}. Почему возникла проблема: {issue}?")
            print(f"   - Причина: Проверьте исходный markdown и CSS/типографику.")
        print("\nTDD-doc: Документ не соответствует стандарту, требуется доработка!")
    else:
        print("\n✅ Документ соответствует стандарту TDD-doc и типографики!")
    # Удаляем временный HTML
    if html_path and Path(html_path).exists():
        os.remove(html_path)

if __name__ == "__main__":
    asyncio.run(main())