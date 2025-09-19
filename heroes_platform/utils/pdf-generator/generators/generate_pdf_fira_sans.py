#!/usr/bin/env python3
"""
PDF генератор с шрифтом Fira Sans через встроенные веб-шрифты.
Исправляет все выявленные проблемы типографики.
"""

import re
from pathlib import Path

import markdown
from weasyprint import CSS, HTML


def convert_md_to_pdf_fira_sans(md_file_path, output_pdf_path):
    """Создает PDF с шрифтом Fira Sans и исправленной типографикой."""

    # Читаем markdown файл
    with open(md_file_path, encoding="utf-8") as f:
        md_content = f.read()

    # Конвертируем markdown в HTML
    html_content = markdown.markdown(md_content, extensions=["tables", "fenced_code"])

    # Улучшаем типографику
    html_content = improve_typography_fixed(html_content)

    # CSS с Fira Sans через Google Fonts + fallback на системные шрифты
    css_styles = """
    @import url('https://fonts.googleapis.com/css2?family=Fira+Sans:wght@300;400;500;600;700&display=swap');

    @page {
        size: A4;
        margin: 20mm;

        @top-center {
            content: "Rick.ai Security Documentation";
            font-size: 8pt;
            color: #666666;
            font-family: "Fira Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }

        @bottom-center {
            content: counter(page);
            font-size: 8pt;
            color: #666666;
            font-family: "Fira Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }
    }

    * {
        box-sizing: border-box;
    }

    body {
        /* ИСПРАВЛЕНИЕ: Используем Fira Sans с правильным fallback */
        font-family: "Fira Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        font-size: 11pt;
        line-height: 1.45;
        color: #2d2d2d;
        margin: 0;
        padding: 0;

        /* ИСПРАВЛЕНИЕ: Оптимальная мера строки для чтения */
        max-width: 170mm;

        /* ИСПРАВЛЕНИЕ: Контроль переносов и пробелов */
        hyphens: auto;
        word-spacing: normal;
        letter-spacing: normal;
        text-align: left;
    }

    /* ИСПРАВЛЕНИЕ: Заголовки с Fira Sans без цветного оформления */
    h1, h2, h3, h4, h5, h6 {
        font-family: "Fira Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-weight: 600;
        color: #1a1a1a;
        line-height: 1.3;
        margin-top: 18pt;
        margin-bottom: 6pt;
        page-break-after: avoid;

        /* Убираем все цветные фоны */
        background: none;
        background-color: transparent;
    }

    h1 {
        font-size: 18pt;
        margin-top: 0;
        margin-bottom: 12pt;
        text-align: center;
        font-weight: 700;
    }

    h2 {
        font-size: 14pt;
        margin-top: 24pt;
        border-bottom: 1pt solid #cccccc;
        padding-bottom: 3pt;
        font-weight: 600;
    }

    h3 {
        font-size: 12pt;
        margin-top: 18pt;
        font-weight: 600;
    }

    h4 {
        font-size: 11pt;
        font-weight: 500;
    }

    /* ИСПРАВЛЕНИЕ: Правильные абзацы без дырок */
    p {
        margin: 0 0 8pt 0;
        text-align: left;
        word-spacing: normal;
        letter-spacing: normal;

        /* Контроль сирот и вдов */
        orphans: 2;
        widows: 2;
        page-break-inside: avoid;
    }

    /* ИСПРАВЛЕНИЕ: Списки с правильными отступами */
    ul, ol {
        margin: 8pt 0;
        padding-left: 18pt;
    }

    li {
        margin-bottom: 4pt;
        page-break-inside: avoid;
    }

    /* ИСПРАВЛЕНИЕ: Таблицы без зеленого оформления */
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 12pt 0;
        font-size: 10pt;
        page-break-inside: avoid;
    }

    th, td {
        padding: 6pt 8pt;
        border: 0.5pt solid #999999;
        text-align: left;
        vertical-align: top;
        word-wrap: break-word;
        font-family: "Fira Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    th {
        font-weight: 600;
        font-size: 9pt;

        /* ИСПРАВЛЕНИЕ: Убираем зеленый фон */
        background-color: #f8f8f8;
        color: #2d2d2d;
    }

    /* Блочные элементы */
    blockquote {
        margin: 12pt 0;
        padding-left: 12pt;
        border-left: 2pt solid #cccccc;
        font-style: italic;
        color: #555555;
    }

    code {
        font-family: "Fira Code", "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas, "Courier New", monospace;
        font-size: 9pt;
        background-color: #f5f5f5;
        padding: 2pt 3pt;
        word-wrap: break-word;
        border-radius: 2pt;
    }

    pre {
        background-color: #f5f5f5;
        padding: 8pt;
        font-family: "Fira Code", "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas, "Courier New", monospace;
        font-size: 9pt;
        overflow: hidden;
        margin: 12pt 0;
        page-break-inside: avoid;
        word-wrap: break-word;
        border-radius: 3pt;
    }

    /* ИСПРАВЛЕНИЕ: Ключевые принципы с деликатным оформлением */
    .key-principle {
        background-color: rgba(45, 45, 45, 0.03);
        border-left: 3pt solid #999999;
        padding: 8pt;
        margin: 12pt 0;
        page-break-inside: avoid;
        border-radius: 0 3pt 3pt 0;
    }

    .key-principle strong {
        color: #2d2d2d;
        font-weight: 600;
    }

    /* Выделения */
    strong, b {
        font-weight: 600;
        color: #1a1a1a;
    }

    em, i {
        font-style: italic;
    }

    /* Специальные стили для русского текста */
    .nowrap {
        white-space: nowrap;
    }

    /* Улучшения читаемости */
    .highlight {
        background-color: rgba(255, 255, 0, 0.1);
        padding: 1pt 2pt;
    }

    /* Микротипографика */
    .small-caps {
        font-variant: small-caps;
        letter-spacing: 0.05em;
    }
    """

    # Создаем полный HTML документ
    full_html = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Информация о безопасности Rick.ai</title>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    # Генерируем PDF
    HTML(string=full_html).write_pdf(
        output_pdf_path, stylesheets=[CSS(string=css_styles)], optimize_images=True
    )

    print(f"PDF с Fira Sans создан: {output_pdf_path}")


def improve_typography_fixed(html_content):
    """Исправляет типографику с учетом всех проблем."""

    # Правильные русские кавычки
    html_content = re.sub(r'"([^"]*)"', r"«\1»", html_content)

    # ИСПРАВЛЕНИЕ: Правильное тире
    html_content = html_content.replace("--", "—")
    html_content = html_content.replace(" - ", " — ")

    # ИСПРАВЛЕНИЕ: Убираем зеленое оформление ключевых принципов
    html_content = re.sub(
        r"<p><strong>Ключевой принцип:([^<]*)</strong>([^<]*)</p>",
        r'<div class="key-principle"><strong>Ключевой принцип:\1</strong>\2</div>',
        html_content,
        flags=re.DOTALL,
    )

    # ИСПРАВЛЕНИЕ: Схема потока данных
    html_content = re.sub(
        r"<p><strong>Схема потока данных:</strong>([^<]*)</p>",
        r'<div class="key-principle"><strong>Схема потока данных:</strong>\1</div>',
        html_content,
    )

    # ИСПРАВЛЕНИЕ: Правильные неразрывные пробелы
    nbsp = "\u00a0"
    html_content = re.sub(r"(\d+)\s+(лет|года|дней)", rf"\1{nbsp}\2", html_content)
    html_content = re.sub(r"(ст\.)\s+(\d+)", rf"\1{nbsp}\2", html_content)
    html_content = re.sub(r"(п\.)\s+(\d+)", rf"\1{nbsp}\2", html_content)
    html_content = re.sub(r"(ч\.)\s+(\d+)", rf"\1{nbsp}\2", html_content)

    # ИСПРАВЛЕНИЕ: Убираем проблемные переносы
    html_content = re.sub(r"-\s+([а-яё])", r"\1", html_content, flags=re.IGNORECASE)

    # ИСПРАВЛЕНИЕ: Нормализуем множественные пробелы
    html_content = re.sub(r"\s{2,}", " ", html_content)

    return html_content


def main():
    """Основная функция."""
    md_file = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/when_security_asked_about_user_data RU.md"
    pdf_file = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_Fira_Sans.pdf"

    if not Path(md_file).exists():
        print(f"Файл не найден: {md_file}")
        return

    convert_md_to_pdf_fira_sans(md_file, pdf_file)
    print("PDF документ с шрифтом Fira Sans создан!")


if __name__ == "__main__":
    main()
