#!/usr/bin/env python3
"""
Финальный PDF генератор с комплексным исправлением всех типографических проблем.
Исправляет: узкие колонки, неструктурированные абзацы, кавычки, тире, неразрывные пробелы, переносы.
"""

import re
from pathlib import Path

import markdown
from weasyprint import CSS, HTML


def convert_md_to_pdf_comprehensive(md_file_path, output_pdf_path):
    """Создает PDF с комплексно исправленной типографикой."""

    with open(md_file_path, encoding="utf-8") as f:
        md_content = f.read()

    # Комплексная обработка типографики
    md_content = comprehensive_typography_fix(md_content)

    # Конвертируем в HTML
    html_content = markdown.markdown(md_content, extensions=["tables", "fenced_code"])

    # Улучшаем HTML структуру
    html_content = enhance_html_comprehensive(html_content)

    # CSS с исправлением всех проблем
    css_styles = """
    @page {
        size: A4;
        margin: 18mm 20mm 20mm 20mm;

        @top-center {
            content: "Rick.ai Security Documentation";
            font-size: 8pt;
            color: #666666;
        }

        @bottom-center {
            content: counter(page);
            font-size: 8pt;
            color: #666666;
        }
    }

    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        font-size: 11pt;
        line-height: 1.5;
        color: #2d2d2d;
        margin: 0;
        padding: 0;

        /* ИСПРАВЛЕНИЕ: Оптимальная ширина для чтения 65-75 символов */
        max-width: 165mm;

        /* ИСПРАВЛЕНИЕ: Профессиональная типографика */
        hyphens: auto;
        word-spacing: normal;
        letter-spacing: normal;
        text-align: left;
        text-rendering: optimizeLegibility;
        font-feature-settings: "kern" 1, "liga" 1;
        font-variant-ligatures: common-ligatures;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-weight: 600;
        color: #1a1a1a;
        line-height: 1.3;
        margin-top: 24pt;
        margin-bottom: 8pt;
        page-break-after: avoid;
        background: none;
        letter-spacing: -0.01em;
    }

    h1 {
        font-size: 20pt;
        margin-top: 0;
        margin-bottom: 16pt;
        text-align: center;
        font-weight: 700;
        line-height: 1.2;
    }

    h2 {
        font-size: 16pt;
        margin-top: 32pt;
        margin-bottom: 12pt;
        border-bottom: 1pt solid #cccccc;
        padding-bottom: 4pt;
    }

    h3 {
        font-size: 13pt;
        margin-top: 24pt;
        margin-bottom: 8pt;
    }

    /* ИСПРАВЛЕНИЕ: Структурированные абзацы */
    p {
        margin: 0 0 12pt 0;
        text-align: left;

        /* Контроль переносов и разрывов */
        orphans: 2;
        widows: 3;
        page-break-inside: avoid;

        /* Оптимальное выравнивание */
        text-indent: 0;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }

    /* Первый абзац после заголовка */
    h1 + p, h2 + p, h3 + p, h4 + p {
        margin-top: 0;
    }

    /* ИСПРАВЛЕНИЕ: Улучшенные списки */
    ul, ol {
        margin: 12pt 0;
        padding-left: 20pt;
        line-height: 1.4;
    }

    li {
        margin-bottom: 6pt;
        page-break-inside: avoid;
        text-align: left;
    }

    li ul, li ol {
        margin: 6pt 0;
    }

    /* ИСПРАВЛЕНИЕ: Профессиональные таблицы */
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 16pt 0;
        font-size: 10pt;
        page-break-inside: avoid;
        line-height: 1.3;
    }

    th, td {
        padding: 8pt 10pt;
        border: 0.5pt solid #999999;
        text-align: left;
        vertical-align: top;
        word-wrap: break-word;
        hyphens: auto;
    }

    th {
        background-color: #f8f8f8;
        color: #2d2d2d;
        font-weight: 600;
        font-size: 9pt;
    }

    blockquote {
        margin: 16pt 0;
        padding: 12pt 16pt;
        border-left: 3pt solid #cccccc;
        background-color: rgba(0, 0, 0, 0.02);
        font-style: italic;
        color: #555555;
        page-break-inside: avoid;
    }

    code {
        font-family: "SF Mono", Monaco, "Cascadia Code", "Courier New", monospace;
        font-size: 9pt;
        background-color: #f5f5f5;
        padding: 2pt 4pt;
        border-radius: 2pt;
        word-wrap: break-word;
    }

    pre {
        background-color: #f5f5f5;
        padding: 12pt;
        font-family: "SF Mono", Monaco, "Cascadia Code", "Courier New", monospace;
        font-size: 9pt;
        margin: 16pt 0;
        page-break-inside: avoid;
        border-radius: 3pt;
        line-height: 1.4;
        overflow-wrap: break-word;
    }

    /* ИСПРАВЛЕНИЕ: Ключевые принципы без зеленого оформления */
    .key-principle {
        background-color: rgba(45, 45, 45, 0.04);
        border-left: 4pt solid #999999;
        padding: 12pt 16pt;
        margin: 16pt 0;
        page-break-inside: avoid;
        border-radius: 0 4pt 4pt 0;
        line-height: 1.4;
    }

    .key-principle strong {
        color: #2d2d2d;
        font-weight: 600;
    }

    strong, b {
        font-weight: 600;
        color: #1a1a1a;
    }

    em, i {
        font-style: italic;
    }

    /* ИСПРАВЛЕНИЕ: Структурированные длинные тексты */
    .structured-section {
        margin: 16pt 0;
    }

    .structured-section p {
        margin-bottom: 8pt;
        max-width: 160mm;
    }

    /* Неразрывные пробелы */
    .nowrap {
        white-space: nowrap;
    }
    """

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

    HTML(string=full_html).write_pdf(
        output_pdf_path, stylesheets=[CSS(string=css_styles)]
    )

    print(f"PDF с комплексно исправленной типографикой создан: {output_pdf_path}")


def comprehensive_typography_fix(text):
    """Комплексное исправление всех типографических проблем."""

    # 1. ИСПРАВЛЕНИЕ: Правильные русские кавычки
    text = re.sub(r'"([^"]*)"', r"«\1»", text)
    text = re.sub(r"'([^']*)'", r"‹\1›", text)

    # 2. ИСПРАВЛЕНИЕ: Правильные тире
    text = text.replace("--", "—")
    text = re.sub(r"\s+-\s+", " — ", text)
    text = re.sub(r"([а-яё])\s+-\s+([а-яё])", r"\1 — \2", text, flags=re.IGNORECASE)

    # Короткое тире для диапазонов
    text = re.sub(r"(\d+)-(\d+)", r"\1–\2", text)

    # 3. ИСПРАВЛЕНИЕ: 15 правил неразрывных пробелов
    nbsp = "\u00a0"

    # Числительные с единицами времени
    text = re.sub(
        r"(\d+)\s+(лет|года|год|дней|день|часов|час|минут|минута)",
        rf"\1{nbsp}\2",
        text,
        flags=re.IGNORECASE,
    )

    # Единицы измерения
    text = re.sub(
        r"(\d+)\s+(км|м|см|мм|кг|г|мг|л|мл)", rf"\1{nbsp}\2", text, flags=re.IGNORECASE
    )

    # Сокращения с номерами
    text = re.sub(
        r"(ст\.|п\.|ч\.|абз\.|рис\.|табл\.|гл\.)\s+(\d+)", rf"\1{nbsp}\2", text
    )
    text = re.sub(r"(№|No\.)\s+(\d+)", rf"\1{nbsp}\2", text)

    # Инициалы
    text = re.sub(
        r"([А-ЯЁ]\.)\s+([А-ЯЁ]\.)\s+([А-ЯЁ][а-яё]+)", rf"\1{nbsp}\2{nbsp}\3", text
    )
    text = re.sub(r"([А-ЯЁ]\.)\s+([А-ЯЁ][а-яё]+)", rf"\1{nbsp}\2", text)

    # Предлоги и союзы
    text = re.sub(
        r"\s+(а|и|в|к|с|о|у|за|на|до|от|по|для|при|без|под|над|про|через)\s+",
        rf" \1{nbsp}",
        text,
    )

    # Частицы
    text = re.sub(r"\s+(не|ни|же|ли|бы|ль)\s+", rf"{nbsp}\1 ", text)

    # Валюты и суммы
    text = re.sub(r"(\d+)\s+(руб\.|р\.|долл\.|€|\$)", rf"\1{nbsp}\2", text)

    # Процентные значения
    text = re.sub(r"(\d+)\s+(%|процент)", rf"\1{nbsp}\2", text)

    # Время
    text = re.sub(r"(\d+):(\d+)", r"\1:\2", text)

    # 4. ИСПРАВЛЕНИЕ: Убираем неправильные переносы
    text = re.sub(r"([а-яё])-\s+([а-яё])", r"\1\2", text, flags=re.IGNORECASE)
    text = re.sub(r"([а-яё])-\n([а-яё])", r"\1\2", text, flags=re.IGNORECASE)

    # 5. ИСПРАВЛЕНИЕ: Нормализация пробелов
    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r"^\s+|\s+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)

    # 6. ИСПРАВЛЕНИЕ: Многоточие
    text = re.sub(r"\.{3,}", "…", text)

    return text


def enhance_html_comprehensive(html_content):
    """Комплексное улучшение HTML структуры."""

    # ИСПРАВЛЕНИЕ: Ключевые принципы без зеленого оформления
    html_content = re.sub(
        r"<p><strong>Ключевой принцип:([^<]*)</strong>([^<]*)</p>",
        r'<div class="key-principle"><strong>Ключевой принцип:\1</strong>\2</div>',
        html_content,
        flags=re.DOTALL,
    )

    html_content = re.sub(
        r"<p><strong>Схема потока данных:</strong>([^<]*)</p>",
        r'<div class="key-principle"><strong>Схема потока данных:</strong>\1</div>',
        html_content,
    )

    # ИСПРАВЛЕНИЕ: Структурирование длинных абзацев
    html_content = re.sub(
        r"<p>([^<]{300,})</p>",
        lambda m: structure_long_paragraph_comprehensive(m.group(1)),
        html_content,
    )

    return html_content


def structure_long_paragraph_comprehensive(text):
    """Структурирует длинные абзацы по предложениям."""

    # Разбиваем по предложениям
    sentences = re.split(r"([.!?]+)", text)

    if len(sentences) <= 6:  # Короткий абзац
        return f"<p>{text}</p>"

    # Длинный абзац - структурируем
    result = '<div class="structured-section">'
    current_paragraph = ""
    sentence_count = 0

    for i in range(0, len(sentences), 2):
        if i < len(sentences):
            sentence = sentences[i].strip()
            punctuation = sentences[i + 1] if i + 1 < len(sentences) else ""

            if sentence:
                current_paragraph += sentence + punctuation + " "
                sentence_count += 1

                # Разбиваем на абзацы по 2-3 предложения
                if sentence_count >= 3 or len(current_paragraph) > 200:
                    result += f"<p>{current_paragraph.strip()}</p>"
                    current_paragraph = ""
                    sentence_count = 0

    if current_paragraph.strip():
        result += f"<p>{current_paragraph.strip()}</p>"

    result += "</div>"
    return result


def main():
    """Основная функция."""
    md_file = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/when_security_asked_about_user_data RU.md"
    pdf_file = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_Comprehensive.pdf"

    if not Path(md_file).exists():
        print(f"Файл не найден: {md_file}")
        return

    convert_md_to_pdf_comprehensive(md_file, pdf_file)
    print("PDF документ с комплексно исправленной типографикой создан!")


if __name__ == "__main__":
    main()
