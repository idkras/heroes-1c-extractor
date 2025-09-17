#!/usr/bin/env python3
"""
Исправленный генератор PDF с устранением всех типографических дефектов.
Специально адаптирован для WeasyPrint с учетом его ограничений.
"""

import markdown
from weasyprint import HTML, CSS
from pathlib import Path
import re

def convert_md_to_pdf_fixed(md_file_path, output_pdf_path):
    """Создает PDF с исправленной типографикой, устраняя все выявленные дефекты."""
    
    # Читаем markdown файл
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Конвертируем markdown в HTML
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
    
    # Улучшаем типографику
    html_content = improve_typography_fixed(html_content)
    
    # CSS с исправлениями всех выявленных проблем
    css_styles = """
    @page {
        size: A4;
        margin: 20mm;
        
        @top-center {
            content: "Rick.ai Security Documentation";
            font-size: 8pt;
            color: #666666;
            font-family: Georgia, serif;
        }
        
        @bottom-center {
            content: counter(page);
            font-size: 8pt;
            color: #666666;
            font-family: Georgia, serif;
        }
    }
    
    * {
        box-sizing: border-box;
    }
    
    body {
        /* Используем системные шрифты без веб-зависимостей */
        font-family: Georgia, "Times New Roman", serif;
        font-size: 10pt;
        line-height: 1.4;
        color: #2d2d2d;
        margin: 0;
        padding: 0;
        
        /* ИСПРАВЛЕНИЕ: Оптимальная мера строки для чтения */
        max-width: 165mm;
        
        /* ИСПРАВЛЕНИЕ: Контроль переносов и пробелов */
        hyphens: manual;
        word-spacing: normal;
        letter-spacing: normal;
        text-align: left;
    }
    
    /* ИСПРАВЛЕНИЕ: Заголовки без зеленых плашек */
    h1, h2, h3, h4, h5, h6 {
        font-family: Georgia, "Times New Roman", serif;
        font-weight: bold;
        color: #1a1a1a;
        line-height: 1.2;
        margin-top: 18pt;
        margin-bottom: 6pt;
        page-break-after: avoid;
        
        /* Убираем все цветные фоны */
        background: none;
        background-color: transparent;
    }
    
    h1 {
        font-size: 16pt;
        margin-top: 0;
        margin-bottom: 12pt;
        text-align: center;
    }
    
    h2 {
        font-size: 13pt;
        margin-top: 24pt;
        border-bottom: 1pt solid #cccccc;
        padding-bottom: 3pt;
    }
    
    h3 {
        font-size: 11pt;
        margin-top: 18pt;
    }
    
    h4 {
        font-size: 10pt;
        font-style: italic;
    }
    
    /* ИСПРАВЛЕНИЕ: Правильные абзацы без дырок */
    p {
        margin: 0 0 6pt 0;
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
        margin: 6pt 0;
        padding-left: 15pt;
    }
    
    li {
        margin-bottom: 3pt;
        page-break-inside: avoid;
    }
    
    /* ИСПРАВЛЕНИЕ: Таблицы без зеленого оформления */
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 12pt 0;
        font-size: 9pt;
        page-break-inside: avoid;
    }
    
    th, td {
        padding: 4pt 6pt;
        border: 0.5pt solid #999999;
        text-align: left;
        vertical-align: top;
        word-wrap: break-word;
    }
    
    th {
        background-color: #f0f0f0;
        font-weight: bold;
        font-size: 8pt;
        
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
        font-family: "Courier New", Courier, monospace;
        font-size: 8pt;
        background-color: #f5f5f5;
        padding: 1pt 2pt;
        word-wrap: break-word;
    }
    
    pre {
        background-color: #f5f5f5;
        padding: 6pt;
        font-family: "Courier New", Courier, monospace;
        font-size: 8pt;
        overflow: hidden;
        margin: 12pt 0;
        page-break-inside: avoid;
        word-wrap: break-word;
    }
    
    /* ИСПРАВЛЕНИЕ: Ключевые принципы без яркого оформления */
    .key-principle {
        background-color: #f9f9f9;
        border-left: 3pt solid #999999;
        padding: 6pt;
        margin: 12pt 0;
        page-break-inside: avoid;
    }
    
    .key-principle strong {
        color: #2d2d2d;
        font-weight: bold;
    }
    
    /* Выделения */
    strong, b {
        font-weight: bold;
        color: #1a1a1a;
    }
    
    em, i {
        font-style: italic;
    }
    
    /* ИСПРАВЛЕНИЕ: Устранение проблем с пустыми страницами */
    .page-break {
        page-break-before: always;
    }
    
    /* Специальные стили для русского текста */
    .nowrap {
        white-space: nowrap;
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
        output_pdf_path,
        stylesheets=[CSS(string=css_styles)],
        optimize_images=True
    )
    
    print(f"Исправленный PDF создан: {output_pdf_path}")

def improve_typography_fixed(html_content):
    """Исправляет типографику с учетом проблем WeasyPrint."""
    
    # Правильные русские кавычки
    html_content = re.sub(r'"([^"]*)"', r'«\1»', html_content)
    
    # ИСПРАВЛЕНИЕ: Правильное тире без проблем переносов
    html_content = html_content.replace('--', '—')
    html_content = html_content.replace(' - ', ' — ')
    
    # ИСПРАВЛЕНИЕ: Убираем зеленое оформление ключевых принципов
    html_content = re.sub(
        r'<p><strong>Ключевой принцип:([^<]*)</strong>([^<]*)</p>',
        r'<div class="key-principle"><strong>Ключевой принцип:\1</strong>\2</div>',
        html_content,
        flags=re.DOTALL
    )
    
    # ИСПРАВЛЕНИЕ: Схема потока данных без зеленого фона
    html_content = re.sub(
        r'<p><strong>Схема потока данных:</strong>([^<]*)</p>',
        r'<div class="key-principle"><strong>Схема потока данных:</strong>\1</div>',
        html_content
    )
    
    # ИСПРАВЛЕНИЕ: Правильные неразрывные пробелы
    nbsp = '\u00A0'
    html_content = re.sub(r'(\d+)\s+(лет|года|дней)', rf'\1{nbsp}\2', html_content)
    html_content = re.sub(r'(ст\.)\s+(\d+)', rf'\1{nbsp}\2', html_content)
    html_content = re.sub(r'(п\.)\s+(\d+)', rf'\1{nbsp}\2', html_content)
    html_content = re.sub(r'(ч\.)\s+(\d+)', rf'\1{nbsp}\2', html_content)
    
    # ИСПРАВЛЕНИЕ: Убираем проблемные переносы в середине текста
    html_content = re.sub(r'-\s+([а-яё])', r'\1', html_content, flags=re.IGNORECASE)
    
    # ИСПРАВЛЕНИЕ: Нормализуем пробелы
    html_content = re.sub(r'\s+', ' ', html_content)
    
    return html_content

def main():
    """Основная функция."""
    md_file = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/when_security_asked_about_user_data RU.md"
    pdf_file = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_Fixed.pdf"
    
    if not Path(md_file).exists():
        print(f"Файл не найден: {md_file}")
        return
    
    convert_md_to_pdf_fixed(md_file, pdf_file)
    print("PDF документ с исправленной типографикой создан!")

if __name__ == "__main__":
    main()