#!/usr/bin/env python3
"""
Генератор PDF документа из markdown файла Rick.ai security documentation.
Создает простой PDF без лишнего форматирования.
"""

import markdown
from weasyprint import HTML, CSS
from pathlib import Path

def convert_md_to_pdf(md_file_path, output_pdf_path):
    """Конвертирует markdown файл в PDF с простым форматированием."""
    
    # Читаем markdown файл
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Конвертируем markdown в HTML
    html_content = markdown.markdown(
        md_content, 
        extensions=['tables', 'nl2br']
    )
    
    # Создаем полный HTML документ с оптимизированным CSS
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Информация о безопасности Rick.ai</title>
        <style>
            /* Используем системные шрифты, близкие к Fira Sans */
            
            body {{
                font-family: 'SF Pro Text', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Liberation Sans', sans-serif;
                font-size: 11pt;
                line-height: 1.5;
                margin: 0;
                padding: 0;
                color: #2c2c2c;
                max-width: 100%;
                text-rendering: optimizeLegibility;
                -webkit-font-smoothing: antialiased;
            }}
            
            h1 {{
                font-size: 17pt;
                font-weight: 600;
                margin: 0 0 8pt 0;
                line-height: 1.2;
                page-break-after: avoid;
                color: #1a1a1a;
            }}
            
            h2 {{
                font-size: 13.5pt;
                font-weight: 600;
                margin: 10pt 0 5pt 0;
                line-height: 1.2;
                page-break-after: avoid;
                color: #1a1a1a;
            }}
            
            h3 {{
                font-size: 11.5pt;
                font-weight: 500;
                margin: 8pt 0 4pt 0;
                line-height: 1.2;
                page-break-after: avoid;
                color: #1a1a1a;
            }}
            
            p {{
                margin: 0 0 4pt 0;
                text-align: left;
                hyphens: auto;
                word-spacing: normal;
            }}
            
            em {{
                font-style: italic;
                color: #666;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 6pt 0;
                font-size: 9.5pt;
                table-layout: auto;
                page-break-inside: avoid;
                font-family: 'SF Pro Text', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Liberation Sans', sans-serif;
            }}
            
            /* Специальные стили для таблицы с идентификаторами */
            table:first-of-type {{
                table-layout: auto;
            }}
            
            table:first-of-type th:first-child,
            table:first-of-type td:first-child {{
                width: 18%;
                min-width: 80pt;
            }}
            
            table:first-of-type th:nth-child(2),
            table:first-of-type td:nth-child(2) {{
                width: 22%;
                min-width: 100pt;
            }}
            
            table:first-of-type th:nth-child(3),
            table:first-of-type td:nth-child(3) {{
                width: 60%;
            }}
            
            /* Стили для таблицы принципов обработки */
            table:nth-of-type(2) th:first-child,
            table:nth-of-type(2) td:first-child {{
                width: 18%;
                min-width: 80pt;
            }}
            
            table:nth-of-type(2) th:nth-child(2),
            table:nth-of-type(2) td:nth-child(2) {{
                width: 82%;
            }}
            
            th, td {{
                border: 1px solid #bbb;
                padding: 7pt 9pt;
                text-align: left;
                vertical-align: top;
                word-wrap: break-word;
                overflow-wrap: break-word;
                hyphens: auto;
                line-height: 1.5;
            }}
            
            th {{
                background-color: #f5f5f5;
                font-weight: 600;
                font-size: 9.5pt;
                line-height: 1.4;
                color: #1a1a1a;
            }}
            
            td {{
                text-align: left;
                word-spacing: normal;
                font-size: 9.5pt;
            }}
            
            strong {{
                font-weight: bold;
            }}
            
            ul, ol {{
                margin: 4pt 0 4pt 16pt;
                padding: 0;
            }}
            
            li {{
                margin: 1pt 0;
                line-height: 1.2;
            }}
            
            code {{
                font-family: 'Courier New', monospace;
                background-color: #f8f8f8;
                padding: 1pt 2pt;
                border-radius: 2pt;
                font-size: 8pt;
            }}
            
            @page {{
                size: A4;
                margin: 12mm 12mm;
            }}
            
            /* Избегаем разрыва страниц внутри списков */
            ul, ol {{
                page-break-inside: avoid;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Генерируем PDF
    HTML(string=full_html).write_pdf(output_pdf_path)
    print(f"PDF создан: {output_pdf_path}")

def main():
    """Основная функция."""
    md_file = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/when_security_asked_about_user_data RU.md"
    pdf_file = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation.pdf"
    
    # Используем улучшенную версию генератора
    from generate_pdf_improved import convert_md_to_pdf_improved
    
    if not Path(md_file).exists():
        print(f"Файл не найден: {md_file}")
        return
    
    convert_md_to_pdf_improved(md_file, pdf_file)
    print("PDF документ с улучшенной типографикой создан!")

if __name__ == "__main__":
    main()