#!/usr/bin/env python3
"""
Современный PDF генератор с поддержкой русской типографики
Использует Playwright для качественного рендеринга и современные CSS принципы
"""

import asyncio
import re

import markdown
from playwright.async_api import async_playwright


class ModernPDFGenerator:
    """Современный генератор PDF с поддержкой русской типографики"""

    def __init__(self):
        self.extensions = [
            "markdown.extensions.extra",
            "markdown.extensions.codehilite",
            "markdown.extensions.toc",
            "markdown.extensions.smarty",
            "markdown.extensions.nl2br",
            "markdown.extensions.sane_lists",
        ]

    async def convert_md_to_pdf(self, md_file_path: str, output_pdf_path: str) -> dict:
        """Конвертирует markdown в PDF с современной типографикой"""

        # Читаем markdown файл
        with open(md_file_path, encoding="utf-8") as f:
            md_content = f.read()

        # Предобработка markdown
        md_content = self._preprocess_markdown(md_content)

        # Конвертируем в HTML
        html_content = markdown.markdown(md_content, extensions=self.extensions)

        # Постобработка HTML
        html_content = self._postprocess_html(html_content)

        # Создаем полный HTML документ
        full_html = self._create_full_html(html_content)

        # Генерируем PDF через Playwright
        result = await self._generate_pdf_with_playwright(full_html, output_pdf_path)

        return result

    def _preprocess_markdown(self, content: str) -> str:
        """Предобработка markdown для улучшения качества"""

        # Исправляем неправильные разделители таблиц
        content = re.sub(r"———————[-—]+", "|", content)

        # Убираем лишние пробелы
        content = re.sub(r"\s{3,}", " ", content)

        # Исправляем пробелы в номерах ФЗ
        content = re.sub(r"ФЗ-\s+(\d+)", r"ФЗ-\1", content)

        # Улучшаем таблицы
        content = self._improve_tables(content)

        return content

    def _improve_tables(self, content: str) -> str:
        """Улучшает структуру таблиц"""

        # Находим таблицы и улучшаем их
        table_pattern = r"(\|.*\|[\r\n]+)(\|[\s\-:]+\|[\r\n]+)(\|.*\|[\r\n]+)"

        def improve_table(match):
            header = match.group(1).strip()
            separator = match.group(2).strip()
            content_rows = match.group(3).strip()

            # Улучшаем разделитель
            separator = separator.replace(":", "")
            separator = re.sub(r"[^|\-]", "-", separator)

            return f"{header}\n{separator}\n{content_rows}\n"

        content = re.sub(table_pattern, improve_table, content, flags=re.MULTILINE)

        return content

    def _postprocess_html(self, html_content: str) -> str:
        """Постобработка HTML для улучшения отображения"""

        # Улучшаем details блоки
        html_content = self._enhance_details_blocks(html_content)

        # Улучшаем таблицы
        html_content = self._enhance_tables(html_content)

        # Улучшаем код блоки
        html_content = self._enhance_code_blocks(html_content)

        return html_content

    def _enhance_details_blocks(self, html_content: str) -> str:
        """Улучшает отображение details блоков"""

        # Заменяем details на стилизованные div'ы
        html_content = re.sub(
            r"<details[^>]*>", '<div class="details-block">', html_content
        )

        html_content = re.sub(
            r"<summary[^>]*>(.*?)</summary>",
            r'<div class="details-summary">\1</div>',
            html_content,
        )

        html_content = html_content.replace("</details>", "</div>")

        return html_content

    def _enhance_tables(self, html_content: str) -> str:
        """Улучшает отображение таблиц"""

        # Добавляем классы для таблиц
        html_content = re.sub(r"<table>", '<table class="modern-table">', html_content)

        # Улучшаем заголовки таблиц
        html_content = re.sub(
            r"<th[^>]*>(.*?)</th>", r'<th class="table-header">\1</th>', html_content
        )

        return html_content

    def _enhance_code_blocks(self, html_content: str) -> str:
        """Улучшает отображение блоков кода"""

        # Добавляем классы для блоков кода
        html_content = re.sub(
            r"<pre><code[^>]*>",
            '<pre class="code-block"><code class="code-content">',
            html_content,
        )

        html_content = html_content.replace("</code></pre>", "</code></pre>")

        return html_content

    def _create_full_html(self, html_content: str) -> str:
        """Создает полный HTML документ с современными стилями"""

        css_styles = """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

            :root {
                --primary-color: #2563eb;
                --text-primary: #1f2937;
                --text-secondary: #6b7280;
                --border-color: #e5e7eb;
                --background-light: #f9fafb;
                --code-background: #f3f4f6;

                --font-size-base: 16px;
                --line-height-base: 1.6;
                --spacing-unit: 8px;
            }

            * {
                box-sizing: border-box;
            }

            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: var(--font-size-base);
                line-height: var(--line-height-base);
                color: var(--text-primary);
                margin: 0;
                padding: 0;
                background: white;
                max-width: 800px;
                margin: 0 auto;
                padding: 40px 20px;
            }

            /* Заголовки */
            h1, h2, h3, h4, h5, h6 {
                font-weight: 600;
                line-height: 1.3;
                margin-top: 32px;
                margin-bottom: 16px;
                color: var(--text-primary);
            }

            h1 {
                font-size: 2.5rem;
                margin-top: 0;
                text-align: center;
                border-bottom: 3px solid var(--primary-color);
                padding-bottom: 16px;
            }

            h2 {
                font-size: 2rem;
                border-bottom: 2px solid var(--border-color);
                padding-bottom: 8px;
            }

            h3 {
                font-size: 1.5rem;
            }

            h4 {
                font-size: 1.25rem;
            }

            /* Параграфы и списки */
            p {
                margin: 0 0 16px 0;
                text-align: justify;
                hyphens: auto;
            }

            ul, ol {
                margin: 16px 0;
                padding-left: 24px;
            }

            li {
                margin-bottom: 8px;
            }

            /* Таблицы */
            .modern-table {
                width: 100%;
                border-collapse: collapse;
                margin: 24px 0;
                font-size: 14px;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                overflow: hidden;
            }

            .table-header {
                background-color: var(--primary-color);
                color: white;
                font-weight: 600;
                padding: 16px 12px;
                text-align: left;
                border: none;
            }

            .modern-table td {
                padding: 12px;
                border-bottom: 1px solid var(--border-color);
                vertical-align: top;
                word-wrap: break-word;
                max-width: 200px;
            }

            .modern-table tr:nth-child(even) {
                background-color: var(--background-light);
            }

            .modern-table tr:hover {
                background-color: #f0f9ff;
            }

            /* Details блоки */
            .details-block {
                margin: 24px 0;
                border: 1px solid var(--border-color);
                border-radius: 8px;
                overflow: hidden;
            }

            .details-summary {
                background-color: var(--background-light);
                padding: 16px;
                font-weight: 600;
                cursor: pointer;
                border-bottom: 1px solid var(--border-color);
                color: var(--primary-color);
            }

            .details-block > div:not(.details-summary) {
                padding: 16px;
            }

            /* Код блоки */
            .code-block {
                background-color: var(--code-background);
                border: 1px solid var(--border-color);
                border-radius: 6px;
                padding: 16px;
                margin: 16px 0;
                overflow-x: auto;
                font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Courier New', monospace;
                font-size: 14px;
                line-height: 1.4;
            }

            .code-content {
                background: none;
                padding: 0;
                margin: 0;
                border: none;
                border-radius: 0;
            }

            /* Inline код */
            code:not(.code-content) {
                background-color: var(--code-background);
                padding: 4px 6px;
                border-radius: 4px;
                font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Courier New', monospace;
                font-size: 0.9em;
                color: #dc2626;
            }

            /* Блоки цитат */
            blockquote {
                margin: 24px 0;
                padding: 16px 24px;
                border-left: 4px solid var(--primary-color);
                background-color: var(--background-light);
                font-style: italic;
                color: var(--text-secondary);
            }

            /* Ссылки */
            a {
                color: var(--primary-color);
                text-decoration: none;
                border-bottom: 1px solid transparent;
                transition: border-bottom-color 0.2s;
            }

            a:hover {
                border-bottom-color: var(--primary-color);
            }

            /* Горизонтальные линии */
            hr {
                border: none;
                border-top: 2px solid var(--border-color);
                margin: 32px 0;
            }

            /* Адаптивность для печати */
            @media print {
                body {
                    max-width: none;
                    padding: 20px;
                }

                .modern-table {
                    box-shadow: none;
                    border: 1px solid #000;
                }

                .details-block {
                    border: 1px solid #000;
                }
            }
        </style>
        """

        return f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>VipAvenue Adjust AppMetrica Integration</title>
            {css_styles}
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """

    async def _generate_pdf_with_playwright(
        self, html_content: str, output_pdf_path: str
    ) -> dict:
        """Генерирует PDF через Playwright для максимального качества"""

        try:
            async with async_playwright() as p:
                # Запускаем браузер
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-gpu",
                        "--no-first-run",
                        "--no-zygote",
                        "--single-process",
                    ],
                )

                # Создаем новую страницу
                page = await browser.new_page()

                # Устанавливаем размер страницы A4
                await page.set_viewport_size({"width": 1200, "height": 1600})

                # Загружаем HTML контент
                await page.set_content(html_content, wait_until="networkidle")

                # Ждем загрузки шрифтов
                await page.wait_for_timeout(2000)

                # Генерируем PDF
                await page.pdf(
                    path=output_pdf_path,
                    format="A4",
                    margin={
                        "top": "20mm",
                        "right": "20mm",
                        "bottom": "20mm",
                        "left": "20mm",
                    },
                    print_background=True,
                    prefer_css_page_size=True,
                )

                await browser.close()

                return {
                    "success": True,
                    "output_path": output_pdf_path,
                    "message": "PDF успешно создан с современной типографикой",
                }

        except Exception as e:
            return {"success": False, "error": f"Ошибка генерации PDF: {str(e)}"}


# Функция для удобного использования
async def convert_md_to_pdf_modern(md_file_path: str, output_pdf_path: str) -> dict:
    """Удобная функция для конвертации markdown в PDF"""
    generator = ModernPDFGenerator()
    return await generator.convert_md_to_pdf(md_file_path, output_pdf_path)


# Синхронная версия для совместимости
def convert_md_to_pdf_modern_sync(md_file_path: str, output_pdf_path: str) -> dict:
    """Синхронная версия конвертации"""
    return asyncio.run(convert_md_to_pdf_modern(md_file_path, output_pdf_path))
