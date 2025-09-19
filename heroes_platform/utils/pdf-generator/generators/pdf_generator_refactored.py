#!/usr/bin/env python3
"""
Рефакторенный PDF генератор с полной поддержкой markdown.
JTBD: Как современный PDF генератор, я хочу создавать качественные PDF документы,
чтобы пользователи получали читаемые документы с сохранением структуры.
"""

import os
import subprocess
import sys
import tempfile

import markdown


class RefactoredPDFGenerator:
    """
    JTBD: Как современный PDF генератор, я хочу создавать качественные PDF документы,
    чтобы пользователи получали читаемые документы с сохранением структуры.
    """

    def __init__(self):
        """
        JTBD: Как инициализатор, я хочу настроить генератор,
        чтобы обеспечить готовность к созданию PDF документов.
        """
        self.markdown_extensions = [
            "markdown.extensions.extra",  # Все стандартные расширения
            "markdown.extensions.codehilite",  # Подсветка кода
            "markdown.extensions.toc",  # Оглавление
            "markdown.extensions.smarty",  # Умные кавычки и тире
            "markdown.extensions.nl2br",  # Переносы строк
            "markdown.extensions.sane_lists",  # Умные списки
        ]

        self.css_styles = self._get_css_styles()

    def _get_css_styles(self) -> str:
        """
        JTBD: Как провайдер стилей, я хочу предоставить CSS для качественного отображения,
        чтобы обеспечить читаемость и структурированность PDF.
        """
        return """
        @page {
            size: A4;
            margin: 20mm;

            @top-center {
                content: "PDF Document";
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
            font-family: "Times New Roman", "DejaVu Serif", serif;
            font-size: 11pt;
            line-height: 1.5;
            color: #000000;
            text-align: justify;
            hyphens: auto;
            word-spacing: normal;
            letter-spacing: normal;
            margin: 0;
            padding: 0;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: "Times New Roman", "DejaVu Serif", serif;
            font-weight: bold;
            color: #000000;
            line-height: 1.3;
            margin-top: 18pt;
            margin-bottom: 6pt;
            page-break-after: avoid;
        }

        h1 {
            font-size: 18pt;
            margin-top: 0;
            margin-bottom: 12pt;
            text-align: center;
        }

        h2 {
            font-size: 14pt;
            margin-top: 24pt;
            border-bottom: 1pt solid #cccccc;
            padding-bottom: 3pt;
        }

        h3 {
            font-size: 12pt;
            margin-top: 18pt;
        }

        p {
            margin: 0 0 8pt 0;
            text-align: justify;
            orphans: 2;
            widows: 2;
            page-break-inside: avoid;
        }

        ul, ol {
            margin: 8pt 0;
            padding-left: 18pt;
        }

        li {
            margin-bottom: 4pt;
            page-break-inside: avoid;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin: 12pt 0;
            font-size: 10pt;
            page-break-inside: avoid;
            max-width: 150mm;
        }

        th, td {
            padding: 8pt 10pt;
            border: 1pt solid #333333;
            text-align: left;
            vertical-align: top;
            word-wrap: break-word;
            max-width: 150mm;
        }

        th {
            background-color: #f8f8f8;
            color: #000000;
            font-weight: bold;
            font-size: 9pt;
        }

        details {
            margin: 12pt 0;
            padding: 8pt;
            border: 1pt solid #cccccc;
            border-radius: 3pt;
            background-color: #f9f9f9;
        }

        summary {
            font-weight: bold;
            cursor: pointer;
            margin-bottom: 8pt;
            color: #000000;
        }

        blockquote {
            margin: 12pt 0;
            padding-left: 12pt;
            border-left: 2pt solid #cccccc;
            font-style: italic;
            color: #555555;
        }

        code {
            font-family: "Courier New", monospace;
            font-size: 9pt;
            background-color: #f5f5f5;
            padding: 2pt 3pt;
            border-radius: 2pt;
            border: 0.5pt solid #cccccc;
        }

        pre {
            background-color: #f5f5f5;
            padding: 8pt;
            font-family: "Courier New", monospace;
            font-size: 9pt;
            margin: 12pt 0;
            page-break-inside: avoid;
            border-radius: 3pt;
            border: 0.5pt solid #cccccc;
            overflow-x: auto;
        }

        strong, b {
            font-weight: bold;
            color: #000000;
        }

        em, i {
            font-style: italic;
        }

        a {
            color: #0066cc;
            text-decoration: underline;
        }

        img {
            max-width: 100%;
            height: auto;
            page-break-inside: avoid;
        }

        .task-list-item {
            list-style-type: none;
        }

        .task-list-item input[type="checkbox"] {
            margin-right: 8pt;
        }
        """

    def convert_md_to_pdf(self, md_file_path: str, output_pdf_path: str) -> bool:
        """
        JTBD: Как конвертер, я хочу преобразовывать markdown в PDF,
        чтобы обеспечить качественное отображение контента.

        Args:
            md_file_path: Путь к markdown файлу
            output_pdf_path: Путь для сохранения PDF

        Returns:
            bool: True если конвертация успешна
        """
        try:
            # Проверяем доступность pandoc
            if not self._check_pandoc():
                print("pandoc не найден. Устанавливаем...")
                self._install_pandoc()

            # Конвертируем markdown напрямую в PDF через pandoc
            success = self._convert_md_to_pdf_direct(md_file_path, output_pdf_path)

            if success:
                return True
            else:
                # Fallback: конвертируем через HTML
                print("Прямая конвертация не удалась, пробуем через HTML...")
                return self._convert_md_to_pdf_via_html(md_file_path, output_pdf_path)

        except Exception as e:
            print(f"Ошибка конвертации: {e}")
            return False

    def _convert_md_to_pdf_direct(
        self, md_file_path: str, output_pdf_path: str
    ) -> bool:
        """
        JTBD: Как прямой конвертер, я хочу конвертировать markdown в PDF через pandoc,
        чтобы обеспечить максимальное качество и скорость.

        Args:
            md_file_path: Путь к markdown файлу
            output_pdf_path: Путь для сохранения PDF

        Returns:
            bool: True если конвертация успешна
        """
        try:
            # Команда для прямой конвертации markdown в PDF
            cmd = [
                "pandoc",
                md_file_path,
                "-o",
                output_pdf_path,
                "--pdf-engine=prince",  # Используем prince как движок
                "--standalone",
                "--from",
                "markdown+raw_html+task_lists",
                "--to",
                "pdf",
                "--metadata",
                "lang=ru",
            ]

            # Выполняем конвертацию
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"PDF успешно создан через pandoc: {output_pdf_path}")
                return True
            else:
                print(f"Ошибка pandoc: {result.stderr}")
                return False

        except Exception as e:
            print(f"Ошибка при прямой конвертации: {e}")
            return False

    def _convert_md_to_pdf_via_html(
        self, md_file_path: str, output_pdf_path: str
    ) -> bool:
        """
        JTBD: Как fallback конвертер, я хочу конвертировать markdown в PDF через HTML,
        чтобы обеспечить создание PDF даже при проблемах с прямым преобразованием.

        Args:
            md_file_path: Путь к markdown файлу
            output_pdf_path: Путь для сохранения PDF

        Returns:
            bool: True если конвертация успешна
        """
        try:
            # Читаем markdown файл
            with open(md_file_path, encoding="utf-8") as f:
                md_content = f.read()

            # Конвертируем markdown в HTML
            html_content = markdown.markdown(
                md_content, extensions=self.markdown_extensions
            )

            # Улучшаем HTML для details блоков
            html_content = self._enhance_html_content(html_content)

            # Создаем полный HTML документ
            full_html = self._create_full_html(html_content)

            # Создаем временный HTML файл
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".html", delete=False, encoding="utf-8"
            ) as f:
                f.write(full_html)
                temp_html_path = f.name

            try:
                # Конвертируем HTML в PDF используя pandoc
                success = self._convert_html_to_pdf(temp_html_path, output_pdf_path)
                return success

            finally:
                # Удаляем временный HTML файл
                if os.path.exists(temp_html_path):
                    os.unlink(temp_html_path)

        except Exception as e:
            print(f"Ошибка конвертации через HTML: {e}")
            return False

    def _enhance_html_content(self, html_content: str) -> str:
        """
        JTBD: Как улучшитель HTML, я хочу обработать специальные элементы,
        чтобы обеспечить корректное отображение details блоков.

        Args:
            html_content: Исходный HTML контент

        Returns:
            str: Улучшенный HTML контент
        """
        # Обрабатываем details блоки
        html_content = html_content.replace("<details>", "<details open>")

        # Улучшаем таблицы
        html_content = html_content.replace("<table>", '<table class="table">')

        return html_content

    def _create_full_html(self, html_content: str) -> str:
        """
        JTBD: Как создатель HTML документа, я хочу создать полный HTML документ,
        чтобы обеспечить корректное отображение в браузере.

        Args:
            html_content: Основной HTML контент

        Returns:
            str: Полный HTML документ
        """
        return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Document</title>
    <style>
        {self.css_styles}
    </style>
</head>
<body>
    {html_content}
</body>
</html>"""

    def _convert_html_to_pdf(self, html_path: str, pdf_path: str) -> bool:
        """
        JTBD: Как конвертер HTML в PDF, я хочу использовать pandoc,
        чтобы создать качественный PDF документ.

        Args:
            html_path: Путь к HTML файлу
            pdf_path: Путь для сохранения PDF

        Returns:
            bool: True если конвертация успешна
        """
        try:
            # Команда для конвертации HTML в PDF через pandoc
            cmd = [
                "pandoc",
                html_path,
                "-o",
                pdf_path,
                "--pdf-engine=prince",  # Используем prince
                "--standalone",
            ]

            # Выполняем конвертацию
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"PDF успешно создан через pandoc HTML: {pdf_path}")
                return True
            else:
                print(f"Ошибка pandoc HTML: {result.stderr}")
                return False

        except Exception as e:
            print(f"Ошибка при конвертации HTML в PDF: {e}")
            return False

    def _check_pandoc(self) -> bool:
        """
        JTBD: Как проверщик зависимостей, я хочу проверить доступность pandoc,
        чтобы убедиться в возможности создания PDF.

        Returns:
            bool: True если pandoc доступен
        """
        try:
            result = subprocess.run(
                ["pandoc", "--version"], capture_output=True, text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def _install_pandoc(self) -> bool:
        """
        JTBD: Как установщик зависимостей, я хочу установить pandoc,
        чтобы обеспечить возможность создания PDF документов.

        Returns:
            bool: True если установка успешна
        """
        try:
            if sys.platform == "darwin":  # macOS
                cmd = ["brew", "install", "pandoc"]
            elif sys.platform.startswith("linux"):
                cmd = ["sudo", "apt-get", "install", "pandoc"]
            else:
                print("Автоматическая установка не поддерживается для этой ОС")
                return False

            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0

        except Exception as e:
            print(f"Ошибка установки pandoc: {e}")
            return False


def convert_md_to_pdf_refactored(md_file_path: str, output_pdf_path: str) -> bool:
    """
    JTBD: Как функция-обертка, я хочу предоставить простой интерфейс,
    чтобы пользователи могли легко конвертировать markdown в PDF.

    Args:
        md_file_path: Путь к markdown файлу
        output_pdf_path: Путь для сохранения PDF

    Returns:
        bool: True если конвертация успешна
    """
    generator = RefactoredPDFGenerator()
    return generator.convert_md_to_pdf(md_file_path, output_pdf_path)


if __name__ == "__main__":
    # Тестирование генератора
    test_md = """
    # Тестовый документ

    ## Таблица
    | Колонка 1 | Колонка 2 |
    |------------|------------|
    | Значение 1 | Значение 2 |

    ## Details блок
    <details open>
    <summary>Кликните для раскрытия</summary>
    Скрытый контент
    </details>
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(test_md)
        test_md_path = f.name

    try:
        test_pdf_path = test_md_path.replace(".md", ".pdf")
        success = convert_md_to_pdf_refactored(test_md_path, test_pdf_path)

        if success:
            print(f"Тестовый PDF создан: {test_pdf_path}")
        else:
            print("Ошибка создания тестового PDF")

    finally:
        if os.path.exists(test_md_path):
            os.unlink(test_md_path)
        if os.path.exists(test_pdf_path):
            os.unlink(test_pdf_path)
