#!/usr/bin/env python3
"""
Улучшенный генератор PDF с применением принципов качественной типографики.
Использует WeasyPrint с максимально возможными улучшениями.
"""

import re
from pathlib import Path

import markdown
from weasyprint import CSS, HTML


def convert_md_to_pdf_improved(md_file_path, output_pdf_path):
    """Конвертирует markdown файл в PDF с улучшенной типографикой."""

    # Читаем markdown файл
    with open(md_file_path, encoding="utf-8") as f:
        md_content = f.read()

    # Конвертируем markdown в HTML
    html_content = markdown.markdown(md_content, extensions=["tables", "fenced_code"])

    # Улучшаем типографику
    html_content = improve_typography(html_content)

    # CSS стили с принципами Брингхерста
    css_styles = """
    @page {
        size: A4;
        margin: 15mm;
        font-family: "SF Pro Text", "Segoe UI", "Roboto", "Inter", sans-serif;

        @top-center {
            content: "Rick.ai Security Documentation";
            font-size: 9pt;
            color: #757575;
        }

        @bottom-center {
            content: counter(page);
            font-size: 9pt;
            color: #757575;
        }
    }

    * {
        box-sizing: border-box;
    }

    body {
        font-family: "SF Pro Text", "Segoe UI", "Roboto", "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 11pt;
        line-height: 1.45; /* 120-145% от размера шрифта */
        color: #292929; /* Высокий контраст 7:1 */
        margin: 0;
        padding: 0;
        max-width: 180mm; /* Оптимальная мера строки */
        orphans: 3; /* Минимум строк внизу страницы */
        widows: 3;  /* Минимум строк вверху страницы */
    }

    /* Модульная сетка: все отступы кратны 3.5mm (≈12px при 300dpi) */
    h1, h2, h3, h4, h5, h6 {
        font-family: "SF Pro Text", "Segoe UI", "Roboto", sans-serif;
        font-weight: 600;
        color: #292929;
        line-height: 1.2; /* Плотный интерлиньяж для заголовков */
        margin-top: 7mm;
        margin-bottom: 3.5mm;
        break-after: avoid; /* Избегаем разрывов после заголовков */
    }

    h1 {
        font-size: 18pt;
        margin-top: 0;
        margin-bottom: 7mm;
        font-weight: 700;
    }

    h2 {
        font-size: 14pt;
        margin-top: 10.5mm;
        font-weight: 600;
    }

    h3 {
        font-size: 12pt;
        margin-top: 7mm;
        font-weight: 600;
    }

    h4 {
        font-size: 11pt;
        font-weight: 600;
    }

    p {
        margin: 0 0 3.5mm 0;
        text-align: justify;
        hyphens: auto; /* Автоматические переносы */
        break-inside: avoid; /* Избегаем разрывов внутри абзацев */
    }

    /* Правильные отступы для списков */
    ul, ol {
        margin: 3.5mm 0;
        padding-left: 7mm;
    }

    li {
        margin-bottom: 1.75mm;
        break-inside: avoid;
    }

    /* Таблицы с модульными отступами */
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 7mm 0;
        font-size: 10pt;
        break-inside: avoid;
    }

    th, td {
        padding: 1.75mm 3.5mm;
        border: 0.5pt solid #E6E6E6;
        text-align: left;
        vertical-align: top;
        break-inside: avoid;
    }

    th {
        background-color: #f8f9fa;
        font-weight: 600;
        font-size: 9pt;
    }

    /* Блочные элементы */
    blockquote {
        margin: 7mm 0;
        padding-left: 7mm;
        border-left: 1mm solid #03A87C;
        font-style: italic;
        color: #757575;
    }

    code {
        font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas, monospace;
        font-size: 9pt;
        background-color: #f5f5f5;
        padding: 1pt 2pt;
        border-radius: 1pt;
    }

    pre {
        background-color: #f5f5f5;
        padding: 3.5mm;
        border-radius: 2pt;
        font-size: 9pt;
        overflow: hidden;
        margin: 7mm 0;
        break-inside: avoid;
    }

    /* Специальная подсветка для ключевых блоков */
    .key-principle {
        background-color: rgba(3, 168, 124, 0.05);
        border-left: 1.5mm solid #03A87C;
        padding: 3.5mm;
        margin: 7mm 0;
        break-inside: avoid;
    }

    .key-principle strong {
        color: #03A87C;
        font-weight: 600;
    }

    /* Улучшения для русского текста */
    .nowrap {
        white-space: nowrap;
    }

    /* Контрастные акценты */
    strong {
        font-weight: 600;
        color: #292929;
    }

    /* Вторичный текст с правильным контрастом */
    .secondary-text {
        color: #757575; /* 4.5:1 контраст */
        font-size: 10pt;
    }

    /* Улучшения для таблиц с данными */
    .data-table th {
        background-color: #03A87C;
        color: white;
        font-weight: 600;
    }

    .data-table td code {
        background-color: rgba(3, 168, 124, 0.1);
        color: #03A87C;
        font-weight: 500;
    }
    """

    # Создаем полный HTML документ
    full_html = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Информация о безопасности Rick.ai для прохождения проверки корпоративных служб безопасности</title>
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

    print(f"PDF создан: {output_pdf_path}")


def improve_typography(html_content):
    """Улучшает типографику HTML контента согласно принципам Брингхерста."""

    # Правильные русские кавычки
    html_content = re.sub(r'"([^"]*)"', r"«\1»", html_content)

    # Длинное тире вместо дефисов
    html_content = html_content.replace("--", "—")
    html_content = html_content.replace(" - ", " — ")

    # Выделяем ключевые принципы специальным классом
    html_content = re.sub(
        r"<p><strong>Ключевой принцип:([^<]*)</strong>([^<]*)</p>",
        r'<div class="key-principle"><strong>Ключевой принцип:\1</strong>\2</div>',
        html_content,
        flags=re.DOTALL,
    )

    # Добавляем класс для таблиц с данными
    html_content = re.sub(r"<table>", r'<table class="data-table">', html_content)

    # Улучшаем отображение схемы потока данных
    html_content = re.sub(
        r"<p><strong>Схема потока данных:</strong>([^<]*)</p>",
        r'<div class="key-principle"><strong>Схема потока данных:</strong>\1</div>',
        html_content,
    )

    # Добавляем неразрывность для важных конструкций
    html_content = re.sub(r"(\d+)\s+(лет|года|дней)", r"\1&nbsp;\2", html_content)
    html_content = re.sub(r"(ст\.)\s+(\d+)", r"\1&nbsp;\2", html_content)
    html_content = re.sub(r"(п\.)\s+(\d+)", r"\1&nbsp;\2", html_content)
    html_content = re.sub(r"(ч\.)\s+(\d+)", r"\1&nbsp;\2", html_content)

    # Исправляем уже существующие неправильные пробелы в юридических ссылках
    html_content = re.sub(r"ст\.\s+(\d+)", r"ст.&nbsp;\1", html_content)
    html_content = re.sub(r"п\.\s+(\d+)", r"п.&nbsp;\1", html_content)
    html_content = re.sub(r"ч\.\s+(\d+)", r"ч.&nbsp;\1", html_content)

    return html_content


def main():
    """Основная функция."""
    md_file = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/when_security_asked_about_user_data RU.md"
    pdf_file = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_Improved.pdf"

    if not Path(md_file).exists():
        print(f"Файл не найден: {md_file}")
        return

    convert_md_to_pdf_improved(md_file, pdf_file)
    print("PDF документ с улучшенной типографикой создан!")


if __name__ == "__main__":
    main()
