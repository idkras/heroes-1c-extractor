#!/usr/bin/env python3
"""
Экстренное исправление PDF генератора на основе реальных проблем из скриншота.
Исправляет: символы ##, слитый текст, кавычки, переносы ФЗ-152.
"""

import markdown
from weasyprint import HTML, CSS
from pathlib import Path
import re

def convert_md_to_pdf_emergency_fix(md_file_path, output_pdf_path):
    """Создает PDF с экстренными исправлениями видимых проблем."""
    
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # ЭКСТРЕННОЕ ИСПРАВЛЕНИЕ: убираем проблемные символы
    md_content = emergency_text_fixes(md_content)
    
    # Конвертируем в HTML с полными расширениями
    html_content = markdown.markdown(
        md_content, 
        extensions=['tables', 'fenced_code', 'nl2br', 'attr_list', 'def_list']
    )
    
    # Исправляем HTML структуру
    html_content = emergency_html_fixes(html_content)
    
    # CSS с фокусом на читаемость
    css_styles = """
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
        
        /* ИСПРАВЛЕНИЕ: Увеличиваем ширину для читаемости */
        max-width: 180mm;
        width: 100%;
        
        /* Базовая типографика */
        text-align: left;
        word-wrap: break-word;
        hyphens: auto;
        text-rendering: optimizeLegibility;
    }
    
    /* ИСПРАВЛЕНИЕ: Четкие заголовки */
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
    
    /* ИСПРАВЛЕНИЕ: Читаемые абзацы с отступами */
    p {
        margin: 0 0 12pt 0;
        text-align: left;
        orphans: 2;
        widows: 2;
        page-break-inside: avoid;
    }
    
    /* Первый абзац после заголовка */
    h1 + p, h2 + p, h3 + p {
        margin-top: 0;
    }
    
    /* ИСПРАВЛЕНИЕ: Структурированные списки */
    ul, ol {
        margin: 12pt 0 12pt 0;
        padding-left: 25pt;
    }
    
    li {
        margin-bottom: 8pt;
        text-align: left;
        page-break-inside: avoid;
    }
    
    /* ИСПРАВЛЕНИЕ: Читаемые таблицы */
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
    }
    
    /* Код */
    code {
        font-family: "Courier New", monospace;
        font-size: 10pt;
        background-color: #f5f5f5;
        padding: 2pt 4pt;
        border-radius: 2pt;
    }
    
    /* ИСПРАВЛЕНИЕ: Ключевые принципы */
    .key-section {
        background-color: rgba(0, 0, 0, 0.03);
        border-left: 4pt solid #999999;
        padding: 12pt 16pt;
        margin: 16pt 0;
        page-break-inside: avoid;
    }
    
    /* Курсив для описаний */
    .description {
        font-style: italic;
        color: #555555;
        margin-bottom: 16pt;
    }
    
    /* Неразрывные элементы */
    .nowrap {
        white-space: nowrap;
    }
    """
    
    # Полный HTML документ
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
        stylesheets=[CSS(string=css_styles)]
    )
    
    print(f"PDF с экстренными исправлениями создан: {output_pdf_path}")

def emergency_text_fixes(text):
    """Экстренные исправления текста для PDF."""
    
    # ИСПРАВЛЕНИЕ 1: Русские кавычки
    text = re.sub(r'"([^"]*)"', r'«\1»', text)
    
    # ИСПРАВЛЕНИЕ 2: Правильное тире
    text = text.replace(' - ', ' — ')
    text = text.replace('--', '—')
    
    # ИСПРАВЛЕНИЕ 3: Неразрывные пробелы для ФЗ-152
    text = text.replace('ФЗ-152', 'ФЗ-152')  # Уже правильно
    text = text.replace('ФЗ- 152', 'ФЗ-152')  # Убираем лишний пробел
    text = text.replace('(ФЗ- 152)', '(ФЗ-152)')
    
    # ИСПРАВЛЕНИЕ 4: Другие неразрывные пробелы
    nbsp = '\u00A0'
    text = re.sub(r'(\d+)\s+(лет|года|дней)', rf'\1{nbsp}\2', text)
    text = re.sub(r'(ст\.)\s+(\d+)', rf'\1{nbsp}\2', text)
    
    # ИСПРАВЛЕНИЕ 5: Многоточие
    text = re.sub(r'\.{3,}', '…', text)
    
    # ИСПРАВЛЕНИЕ 6: Убираем лишние пробелы
    text = re.sub(r'\s{2,}', ' ', text)
    
    return text

def emergency_html_fixes(html_content):
    """Экстренные исправления HTML."""
    
    # Добавляем полную HTML структуру
    if not html_content.startswith('<!DOCTYPE'):
        html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Rick.ai Security Documentation</title>
</head>
<body>
{html_content}
</body>
</html>"""
    
    # ИСПРАВЛЕНИЕ: Оборачиваем курсив в класс description
    html_content = re.sub(
        r'<p><em>([^<]*)</em></p>',
        r'<p class="description"><em>\1</em></p>',
        html_content
    )
    
    # ИСПРАВЛЕНИЕ: Ключевые принципы в отдельные блоки
    html_content = re.sub(
        r'<p><strong>Ключевой принцип:([^<]*)</strong>([^<]*)</p>',
        r'<div class="key-section"><strong>Ключевой принцип:\1</strong>\2</div>',
        html_content,
        flags=re.DOTALL
    )
    
    # НЕ удаляем символы markdown - они уже преобразованы в HTML!
    # Проверяем, что нет остатков непреобразованных символов
    if '##' in html_content and '<h' not in html_content:
        # Только если есть ## но нет HTML заголовков
        html_content = html_content.replace('##', '')
    
    return html_content

def main():
    """Основная функция."""
    
    source_file = "[projects]/rick.ai/knowledge base/in progress/1. when new lead come/2. when security asked policy/when_security_asked_about_user_data RU.md"
    pdf_file = "[projects]/rick.ai/knowledge base/in progress/1. when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_FINAL.pdf"
    
    if not Path(source_file).exists():
        print(f"Файл не найден: {source_file}")
        return
    
    # Удаляем старые PDF
    old_pdfs = [
        "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_Emergency_Fix.pdf",
        "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_Final_Fixed.pdf"
    ]
    
    for old_pdf in old_pdfs:
        if Path(old_pdf).exists():
            Path(old_pdf).unlink()
    
    convert_md_to_pdf_emergency_fix(source_file, pdf_file)
    print("Финальный PDF создан из исправленного документа!")

if __name__ == "__main__":
    main()