#!/usr/bin/env python3
"""
Исправленный генератор PDF с правильной обработкой markdown структуры.
Решает проблему слитого текста без абзацев и заголовков.
"""

import re
from pathlib import Path

import markdown
from weasyprint import CSS, HTML


def convert_md_to_pdf_fixed(md_file_path, output_pdf_path):
    """Создает PDF с правильной markdown структурой."""

    # Читаем исходный файл
    with open(md_file_path, encoding="utf-8") as f:
        md_content = f.read()

    # Исправляем типографику в markdown
    md_content = fix_markdown_typography(md_content)

    # Конвертируем markdown в HTML с полными расширениями
    html_content = markdown.markdown(
        md_content,
        extensions=[
            "tables",
            "fenced_code",
            "attr_list",
            "def_list",
            "toc",
            "md_in_html",
        ],
        extension_configs={"toc": {"title": "Содержание"}},
    )

    # Оборачиваем в полную HTML структуру
    full_html = create_full_html(html_content)

    # Создаем CSS стили
    css_styles = create_pdf_styles()

    # Создаем PDF
    try:
        HTML(string=full_html).write_pdf(
            output_pdf_path, stylesheets=[CSS(string=css_styles)]
        )
        print(f"PDF создан успешно: {output_pdf_path}")
        return True
    except Exception as e:
        print(f"Ошибка создания PDF: {e}")
        return False


def fix_markdown_typography(text):
    """Исправляет типографические проблемы в markdown."""

    # Убираем лишние пробелы в ФЗ-152
    text = text.replace("ФЗ- 152", "ФЗ-152")
    text = text.replace("(ФЗ- 152)", "(ФЗ-152)")

    # Правильные русские кавычки
    text = re.sub(r'"([^"]*)"', r"«\1»", text)

    # Правильное тире
    text = text.replace(" - ", " — ")
    text = text.replace("--", "—")

    # Неразрывные пробелы
    nbsp = "\u00a0"
    text = re.sub(r"(\d+)\s+(лет|года|дней)", rf"\1{nbsp}\2", text)
    text = re.sub(r"(ст\.)\s+(\d+)", rf"\1{nbsp}\2", text)

    # Многоточие
    text = re.sub(r"\.{3,}", "…", text)

    # Убираем лишние пробелы но сохраняем структуру
    text = re.sub(r"[ \t]+", " ", text)  # Убираем только лишние пробелы/табы
    text = re.sub(r" +\n", "\n", text)  # Убираем пробелы в конце строк

    return text


def create_full_html(content):
    """Создает полную HTML структуру."""

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rick.ai Security Documentation</title>
</head>
<body>
    <main class="document">
        {content}
    </main>
</body>
</html>"""


def create_pdf_styles():
    """Создает CSS стили для PDF."""

    return """
    @page {
        size: A4;
        margin: 20mm 25mm 25mm 25mm;

        @top-center {
            content: "Rick.ai Security Documentation";
            font-size: 9pt;
            color: #666666;
            font-family: Arial, sans-serif;
        }

        @bottom-center {
            content: counter(page);
            font-size: 9pt;
            color: #666666;
        }
    }

    * {
        box-sizing: border-box;
    }

    body {
        font-family: Arial, "Times New Roman", serif;
        font-size: 12pt;
        line-height: 1.6;
        color: #2d2d2d;
        margin: 0;
        padding: 0;
        max-width: 180mm;
        width: 100%;
        text-align: left;
        word-wrap: break-word;
        hyphens: auto;
    }

    .document {
        width: 100%;
    }

    /* Заголовки */
    h1 {
        font-size: 20pt;
        font-weight: bold;
        color: #1a1a1a;
        text-align: center;
        margin: 0 0 20pt 0;
        line-height: 1.3;
        page-break-after: avoid;
    }

    h2 {
        font-size: 16pt;
        font-weight: bold;
        color: #1a1a1a;
        margin: 24pt 0 12pt 0;
        line-height: 1.4;
        page-break-after: avoid;
        border-bottom: 1pt solid #cccccc;
        padding-bottom: 6pt;
    }

    h3 {
        font-size: 14pt;
        font-weight: bold;
        color: #1a1a1a;
        margin: 20pt 0 10pt 0;
        line-height: 1.4;
        page-break-after: avoid;
    }

    h4 {
        font-size: 12pt;
        font-weight: bold;
        color: #1a1a1a;
        margin: 16pt 0 8pt 0;
        page-break-after: avoid;
    }

    /* Абзацы */
    p {
        margin: 0 0 12pt 0;
        text-align: left;
        orphans: 2;
        widows: 2;
        text-indent: 0;
    }

    /* Первый абзац после заголовка */
    h1 + p, h2 + p, h3 + p, h4 + p {
        margin-top: 0;
    }

    /* Списки */
    ul, ol {
        margin: 12pt 0 12pt 0;
        padding-left: 25pt;
    }

    li {
        margin-bottom: 8pt;
        text-align: left;
        page-break-inside: avoid;
    }

    /* Вложенные списки */
    ul ul, ol ol, ul ol, ol ul {
        margin: 6pt 0;
    }

    /* Таблицы */
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 16pt 0;
        font-size: 11pt;
        page-break-inside: avoid;
    }

    th, td {
        padding: 10pt 12pt;
        border: 1pt solid #999999;
        text-align: left;
        vertical-align: top;
        word-wrap: break-word;
    }

    th {
        background-color: #f8f8f8;
        font-weight: bold;
        font-size: 10pt;
    }

    /* Выделения */
    strong, b {
        font-weight: bold;
        color: #1a1a1a;
    }

    em, i {
        font-style: italic;
        color: #444444;
    }

    /* Код */
    code {
        font-family: "Courier New", monospace;
        font-size: 10pt;
        background-color: #f5f5f5;
        padding: 2pt 4pt;
        border-radius: 2pt;
    }

    pre {
        background-color: #f8f8f8;
        border: 1pt solid #ddd;
        border-radius: 4pt;
        padding: 12pt;
        margin: 16pt 0;
        font-family: "Courier New", monospace;
        font-size: 10pt;
        line-height: 1.4;
        overflow-wrap: break-word;
    }

    /* Цитаты */
    blockquote {
        margin: 16pt 20pt;
        padding: 12pt 16pt;
        border-left: 4pt solid #ddd;
        background-color: #f9f9f9;
        font-style: italic;
    }

    /* Горизонтальная линия */
    hr {
        border: none;
        border-top: 1pt solid #ddd;
        margin: 24pt 0;
    }

    /* Специальные классы */
    .description {
        font-style: italic;
        color: #666666;
        margin-bottom: 16pt;
    }

    .key-section {
        background-color: #f8f9fa;
        border-left: 4pt solid #007bff;
        padding: 12pt 16pt;
        margin: 16pt 0;
    }

    /* Контроль разрывов страниц */
    .page-break {
        page-break-before: always;
    }

    .no-break {
        page-break-inside: avoid;
    }

    /* Ссылки */
    a {
        color: #007bff;
        text-decoration: none;
    }

    a:hover {
        text-decoration: underline;
    }
    """


def main():
    """Основная функция."""

    source_file = "[projects]/rick.ai/knowledge base/in progress/1. when new lead come/2. when security asked policy/yandex_metrika_access_technical_justification.md"
    pdf_file = "Rick_ai_Yandex_Metrika_Access_Justification.pdf"

    if not Path(source_file).exists():
        print(f"Файл не найден: {source_file}")
        return

    # Удаляем старые версии
    old_files = [
        "Rick_ai_Security_Documentation_FINAL.pdf",
        "Rick_ai_Security_Documentation_Emergency_Fix.pdf",
    ]

    for old_file in old_files:
        if Path(old_file).exists():
            Path(old_file).unlink()

    success = convert_md_to_pdf_fixed(source_file, pdf_file)

    if success:
        print("PDF с исправленной структурой создан!")
        print(f"Файл: {pdf_file}")
    else:
        print("Ошибка при создании PDF")


if __name__ == "__main__":
    main()
