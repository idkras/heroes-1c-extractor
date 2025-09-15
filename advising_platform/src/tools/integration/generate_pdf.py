#!/usr/bin/env python3
"""
Конвертер Markdown в PDF
Использует markdown для разбора MD-файла и weasyprint для создания PDF
"""

import argparse
import markdown
import os
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

# CSS стили для улучшения внешнего вида PDF
CSS_STYLES = """
@page {
    margin: 3cm 2cm;
    @top-center {
        content: "Kontur-Extern: Диагностика";
        font-family: Arial, sans-serif;
        font-size: 9pt;
        color: #555;
    }
    @bottom-center {
        content: counter(page);
        font-family: Arial, sans-serif;
        font-size: 9pt;
    }
}

body {
    font-family: Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.5;
    color: #333;
}

h1 {
    font-size: 22pt;
    color: #0056b3;
    margin-top: 1cm;
    margin-bottom: 0.5cm;
    page-break-before: always;
}

h1:first-of-type {
    page-break-before: avoid;
}

h2 {
    font-size: 18pt;
    color: #0069d9;
    margin-top: 0.7cm;
    margin-bottom: 0.3cm;
}

h3 {
    font-size: 14pt;
    color: #007bff;
    margin-top: 0.5cm;
    margin-bottom: 0.2cm;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
}

th, td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}

th {
    background-color: #f2f2f2;
    font-weight: bold;
}

tr:nth-child(even) {
    background-color: #f9f9f9;
}

blockquote {
    border-left: 4px solid #0056b3;
    padding-left: 15px;
    margin-left: 0;
    color: #555;
    font-style: italic;
}

ul, ol {
    margin-bottom: 15px;
}

li {
    margin-bottom: 5px;
}

a {
    color: #0069d9;
    text-decoration: none;
}

code {
    font-family: Consolas, monospace;
    background-color: #f5f5f5;
    padding: 2px 4px;
    border-radius: 3px;
    font-size: 90%;
}

hr {
    border: none;
    height: 1px;
    background-color: #ddd;
    margin: 20px 0;
}

img {
    max-width: 100%;
    margin: 15px 0;
}

.emoji {
    font-size: 120%;
}
"""


def convert_md_to_pdf(md_file, output_pdf, css_string=CSS_STYLES):
    """
    Конвертирует Markdown-файл в PDF с применением CSS-стилей
    
    Args:
        md_file: Путь к Markdown-файлу
        output_pdf: Путь для сохранения PDF
        css_string: CSS стили для форматирования
    """
    # Проверка наличия файла
    if not os.path.exists(md_file):
        print(f"Ошибка: Файл {md_file} не найден.")
        return False
    
    # Читаем содержимое Markdown-файла
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Конвертируем Markdown в HTML
    html_content = markdown.markdown(
        md_content,
        extensions=[
            'markdown.extensions.tables',
            'markdown.extensions.fenced_code',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
            'markdown.extensions.attr_list'
        ]
    )
    
    # Добавляем базовую HTML-структуру
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Kontur-Extern: Стратегическая диагностика</title>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Настройка шрифтов
    font_config = FontConfiguration()
    
    # Создаем PDF
    html = HTML(string=full_html)
    css = CSS(string=css_string, font_config=font_config)
    
    # Рендеринг PDF
    html.write_pdf(
        output_pdf,
        stylesheets=[css],
        font_config=font_config
    )
    
    print(f"PDF успешно создан: {output_pdf}")
    return True


def main():
    """Основная функция для работы из командной строки"""
    parser = argparse.ArgumentParser(description='Конвертер Markdown в PDF')
    parser.add_argument('input_file', help='Путь к Markdown-файлу')
    parser.add_argument(
        '--output', '-o',
        help='Путь для сохранения PDF (по умолчанию - то же имя, но с расширением .pdf)'
    )
    
    args = parser.parse_args()
    
    # Если выходной файл не указан, используем имя входного с другим расширением
    if not args.output:
        args.output = os.path.splitext(args.input_file)[0] + '.pdf'
    
    # Конвертируем файл
    convert_md_to_pdf(args.input_file, args.output)


if __name__ == '__main__':
    main()