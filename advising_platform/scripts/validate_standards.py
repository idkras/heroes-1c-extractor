#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Инструмент для расширенной проверки стандартов на соответствие требованиям.
Анализирует форматирование, структуру, содержание и метаданные стандартов.
"""

import os
import re
import sys
import json
import logging
import argparse
from datetime import datetime
import concurrent.futures
from collections import Counter

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scripts/validate_standards.log')
    ]
)

logger = logging.getLogger('validate_standards')

# Константы
STANDARDS_DIR = "advising standards.md"
ARCHIVE_DIR = os.path.join(STANDARDS_DIR, "archive AI never use")

class StandardValidator:
    """Класс для проверки стандартов на соответствие требованиям."""
    
    def __init__(self, include_archived=False):
        """
        Инициализирует валидатор стандартов.
        
        Args:
            include_archived: Включать ли архивные стандарты в проверку
        """
        self.include_archived = include_archived
        
        # Определяем правила проверки
        self.rules = {
            "filename_format": {
                "pattern": r"^(\d+(\.\d+)?) .+ by \d+ [a-zA-Z]+ \d{4}( \d{4})? CET by .+\.md$",
                "message": "Имя файла должно соответствовать формату: '[номер].[подномер] [название] by [дата] [время] CET by [автор].md'"
            },
            "headers_structure": {
                "patterns": [
                    r"^# ",  # Заголовок первого уровня
                    r"^## "  # Заголовок второго уровня
                ],
                "message": "Документ должен содержать как минимум один заголовок первого уровня и один заголовок второго уровня"
            },
            "license_section": {
                "pattern": r"(?i)(лицензия|license)",
                "message": "Документ должен содержать раздел с лицензией"
            },
            "task_master_authors": {
                "task_master_pattern": r"0\. task master",
                "authors_patterns": [
                    r"(?:Илья Красинский|Ilya Krasinsky)",
                    r"(?:Дмитрий Карасев|Dmitry Karasev)"
                ],
                "message": "Task Master стандарт должен содержать упоминание обоих авторов: Ильи Красинского и Дмитрия Карасева"
            },
            "derivative_authors": {
                "not_task_master_pattern": r"^(?!.*0\. task master).*$",
                "required_author": r"(?:Илья Красинский|Ilya Krasinsky)",
                "forbidden_author": r"(?:Дмитрий Карасев|Dmitry Karasev)",
                "message": "Производные стандарты должны содержать упоминание только Ильи Красинского, без упоминания Дмитрия Карасева"
            },
            "markdown_links": {
                "pattern": r"\[([^\]]+)\]\(([^)]+)\)",
                "message": "Проверка корректности markdown-ссылок"
            },
            "tables_format": {
                "pattern": r"\|.*\|.*\|\n\|[\s-]*\|[\s-]*\|",
                "message": "Проверка корректности форматирования таблиц"
            },
            "code_blocks": {
                "pattern": r"```[a-z]*\n[\s\S]*?\n```",
                "message": "Проверка корректности блоков кода"
            },
            "image_references": {
                "pattern": r"!\[([^\]]*)\]\(([^)]+)\)",
                "message": "Проверка корректности ссылок на изображения"
            }
        }
    
    def validate_file(self, file_path):
        """
        Проверяет соответствие файла стандарта требованиям.
        
        Args:
            file_path: Путь к файлу стандарта
        
        Returns:
            Dict с результатами проверки
        """
        # Проверяем, что файл существует
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return {
                "file_path": file_path,
                "is_valid": False,
                "error": "Файл не найден",
                "validation_date": datetime.now().isoformat()
            }
        
        # Проверяем, что это markdown-файл
        if not file_path.endswith('.md'):
            return {
                "file_path": file_path,
                "is_valid": False,
                "error": "Файл не является markdown-документом",
                "validation_date": datetime.now().isoformat()
            }
        
        # Проверяем архивный статус
        is_archived = "archive AI never use" in file_path
        
        if is_archived and not self.include_archived:
            return {
                "file_path": file_path,
                "is_valid": None,
                "error": "Файл находится в архиве и исключен из проверки",
                "is_archived": True,
                "validation_date": datetime.now().isoformat()
            }
        
        try:
            # Извлекаем имя файла
            filename = os.path.basename(file_path)
            
            # Считываем содержимое файла
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Проводим все проверки
            validation_results = {}
            
            # Проверка формата имени файла
            validation_results["filename_format"] = self._validate_filename_format(filename)
            
            # Проверка структуры заголовков
            validation_results["headers_structure"] = self._validate_headers_structure(content)
            
            # Проверка наличия раздела с лицензией
            validation_results["license_section"] = self._validate_license_section(content)
            
            # Проверка авторов в зависимости от типа стандарта
            validation_results["authors"] = self._validate_authors(filename, content)
            
            # Расширенные проверки содержимого
            validation_results["links"] = self._validate_markdown_links(content)
            validation_results["tables"] = self._validate_tables(content)
            validation_results["code_blocks"] = self._validate_code_blocks(content)
            validation_results["images"] = self._validate_images(content, file_path)
            
            # Расширенный анализ содержимого
            validation_results["content_analysis"] = self._analyze_content(content)
            
            # Общий статус валидации
            is_valid = all(result.get("valid", False) for result in validation_results.values())
            
            # Формируем итоговый результат
            result = {
                "file_path": file_path,
                "filename": filename,
                "is_valid": is_valid,
                "is_archived": is_archived,
                "validation_date": datetime.now().isoformat(),
                "results": validation_results
            }
            
            return result
        
        except Exception as e:
            logger.error(f"Ошибка при проверке файла {file_path}: {e}", exc_info=True)
            return {
                "file_path": file_path,
                "is_valid": False,
                "error": str(e),
                "validation_date": datetime.now().isoformat()
            }
    
    def validate_all(self, max_workers=None):
        """
        Проверяет все стандарты в директории.
        
        Args:
            max_workers: Максимальное количество параллельных потоков
        
        Returns:
            Dict с результатами проверки для всех файлов
        """
        all_files = []
        
        # Собираем все файлы стандартов
        for root, _, files in os.walk(STANDARDS_DIR):
            # Пропускаем архивную директорию, если не включена
            if "archive AI never use" in root and not self.include_archived:
                continue
            
            for file in files:
                if file.endswith('.md'):
                    all_files.append(os.path.join(root, file))
        
        logger.info(f"Найдено {len(all_files)} файлов стандартов для проверки")
        
        # Проверяем файлы параллельно для ускорения
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {executor.submit(self.validate_file, file): file for file in all_files}
            
            for future in concurrent.futures.as_completed(future_to_file):
                file = future_to_file[future]
                try:
                    result = future.result()
                    results[file] = result
                except Exception as e:
                    logger.error(f"Ошибка при проверке файла {file}: {e}", exc_info=True)
                    results[file] = {
                        "file_path": file,
                        "is_valid": False,
                        "error": str(e),
                        "validation_date": datetime.now().isoformat()
                    }
        
        return results
    
    def _validate_filename_format(self, filename):
        """Проверяет формат имени файла."""
        rule = self.rules["filename_format"]
        is_valid = bool(re.match(rule["pattern"], filename))
        
        return {
            "valid": is_valid,
            "check": "filename_format",
            "expected": "[номер].[подномер] [название] by [дата] [время] CET by [автор].md",
            "actual": filename,
            "message": "Имя файла соответствует стандарту" if is_valid else rule["message"]
        }
    
    def _validate_headers_structure(self, content):
        """Проверяет структуру заголовков в документе."""
        rule = self.rules["headers_structure"]
        checks = []
        
        for i, pattern in enumerate(rule["patterns"]):
            found = bool(re.search(pattern, content, re.MULTILINE))
            checks.append({
                "level": i + 1,
                "found": found
            })
        
        is_valid = all(check["found"] for check in checks)
        
        return {
            "valid": is_valid,
            "check": "headers_structure",
            "checks": checks,
            "message": "Структура заголовков соответствует стандарту" if is_valid else rule["message"]
        }
    
    def _validate_license_section(self, content):
        """Проверяет наличие раздела с лицензией."""
        rule = self.rules["license_section"]
        is_valid = bool(re.search(rule["pattern"], content, re.MULTILINE))
        
        return {
            "valid": is_valid,
            "check": "license_section",
            "message": "Раздел с лицензией найден" if is_valid else rule["message"]
        }
    
    def _validate_authors(self, filename, content):
        """Проверяет правильность указания авторов в зависимости от типа стандарта."""
        is_task_master = bool(re.search(self.rules["task_master_authors"]["task_master_pattern"], filename, re.IGNORECASE))
        
        if is_task_master:
            # Проверка для Task Master стандарта
            rule = self.rules["task_master_authors"]
            authors_found = []
            
            for i, pattern in enumerate(rule["authors_patterns"]):
                found = bool(re.search(pattern, content, re.IGNORECASE))
                authors_found.append({
                    "author": pattern,
                    "found": found
                })
            
            is_valid = all(author["found"] for author in authors_found)
            
            return {
                "valid": is_valid,
                "check": "authors",
                "is_task_master": True,
                "authors_found": authors_found,
                "message": "Авторы указаны корректно" if is_valid else rule["message"]
            }
        else:
            # Проверка для производных стандартов
            rule = self.rules["derivative_authors"]
            
            required_found = bool(re.search(rule["required_author"], content, re.IGNORECASE))
            forbidden_found = bool(re.search(rule["forbidden_author"], content, re.IGNORECASE))
            
            is_valid = required_found and not forbidden_found
            
            return {
                "valid": is_valid,
                "check": "authors",
                "is_task_master": False,
                "required_author_found": required_found,
                "forbidden_author_found": forbidden_found,
                "message": "Авторы указаны корректно" if is_valid else rule["message"]
            }
    
    def _validate_markdown_links(self, content):
        """Проверяет корректность markdown-ссылок."""
        rule = self.rules["markdown_links"]
        pattern = rule["pattern"]
        
        # Находим все ссылки
        links = re.findall(pattern, content)
        
        # Проверяем каждую ссылку
        valid_links = []
        invalid_links = []
        
        for text, url in links:
            # Проверяем базовую корректность URL
            url_valid = (
                not url.isspace() and                            # URL не должен быть пустым
                not (url.startswith("http") and " " in url) and  # В URL не должно быть пробелов
                not url.endswith("..")                           # URL не должен заканчиваться точками
            )
            
            if url_valid:
                valid_links.append({"text": text, "url": url})
            else:
                invalid_links.append({"text": text, "url": url})
        
        is_valid = len(invalid_links) == 0
        
        return {
            "valid": is_valid,
            "check": "markdown_links",
            "total_links": len(links),
            "valid_links": len(valid_links),
            "invalid_links": invalid_links,
            "message": f"Все ссылки ({len(links)}) корректны" if is_valid else f"Найдено {len(invalid_links)} некорректных ссылок из {len(links)}"
        }
    
    def _validate_tables(self, content):
        """Проверяет корректность форматирования таблиц."""
        rule = self.rules["tables_format"]
        
        # Находим все таблицы
        tables = re.findall(rule["pattern"], content)
        
        # Для каждой таблицы проверяем соответствие формату
        valid_tables = []
        invalid_tables = []
        
        for table in tables:
            # Проверяем наличие строки-разделителя
            lines = table.strip().split('\n')
            
            if len(lines) >= 2:
                header_line = lines[0]
                separator_line = lines[1]
                
                # Проверяем, что количество столбцов совпадает
                header_cols = header_line.count('|') - 1
                separator_cols = separator_line.count('|') - 1
                
                if header_cols == separator_cols and all('-' in col for col in separator_line.split('|')[1:-1]):
                    valid_tables.append(table)
                else:
                    invalid_tables.append(table)
            else:
                invalid_tables.append(table)
        
        is_valid = len(invalid_tables) == 0
        
        return {
            "valid": is_valid,
            "check": "tables_format",
            "total_tables": len(tables),
            "valid_tables": len(valid_tables),
            "invalid_tables_count": len(invalid_tables),
            "message": f"Все таблицы ({len(tables)}) корректны" if is_valid else f"Найдено {len(invalid_tables)} некорректных таблиц из {len(tables)}"
        }
    
    def _validate_code_blocks(self, content):
        """Проверяет корректность блоков кода."""
        rule = self.rules["code_blocks"]
        
        # Находим все блоки кода
        code_blocks = re.findall(rule["pattern"], content)
        
        # Для каждого блока проверяем баланс тройных кавычек
        valid_blocks = []
        invalid_blocks = []
        
        for block in code_blocks:
            # Проверяем, что блок начинается и заканчивается тройными кавычками
            if block.startswith('```') and block.endswith('```'):
                valid_blocks.append(block)
            else:
                invalid_blocks.append(block)
        
        is_valid = len(invalid_blocks) == 0
        
        return {
            "valid": is_valid,
            "check": "code_blocks",
            "total_blocks": len(code_blocks),
            "valid_blocks": len(valid_blocks),
            "invalid_blocks_count": len(invalid_blocks),
            "message": f"Все блоки кода ({len(code_blocks)}) корректны" if is_valid else f"Найдено {len(invalid_blocks)} некорректных блоков кода из {len(code_blocks)}"
        }
    
    def _validate_images(self, content, file_path):
        """Проверяет корректность ссылок на изображения."""
        rule = self.rules["image_references"]
        
        # Находим все ссылки на изображения
        images = re.findall(rule["pattern"], content)
        
        # Проверяем каждую ссылку
        valid_images = []
        invalid_images = []
        
        for alt_text, image_path in images:
            # Проверяем базовую корректность пути
            base_path = os.path.dirname(file_path)
            
            if image_path.startswith('http'):
                # Для внешних URL проверяем базовую структуру
                is_valid = not image_path.isspace() and ' ' not in image_path
            else:
                # Для локальных путей проверяем существование файла
                full_image_path = os.path.normpath(os.path.join(base_path, image_path))
                is_valid = os.path.exists(full_image_path) and os.path.isfile(full_image_path)
            
            if is_valid:
                valid_images.append({"alt_text": alt_text, "path": image_path})
            else:
                invalid_images.append({"alt_text": alt_text, "path": image_path})
        
        is_valid = len(invalid_images) == 0
        
        return {
            "valid": is_valid,
            "check": "image_references",
            "total_images": len(images),
            "valid_images": len(valid_images),
            "invalid_images": invalid_images,
            "message": f"Все ссылки на изображения ({len(images)}) корректны" if is_valid else f"Найдено {len(invalid_images)} некорректных ссылок на изображения из {len(images)}"
        }
    
    def _analyze_content(self, content):
        """Проводит расширенный анализ содержимого."""
        # Подсчет символов, слов и строк
        char_count = len(content)
        word_count = len(re.findall(r'\w+', content))
        line_count = len(content.split('\n'))
        
        # Определение языка (русский/английский)
        cyrillic_chars = len(re.findall(r'[а-яА-ЯёЁ]', content))
        latin_chars = len(re.findall(r'[a-zA-Z]', content))
        
        if cyrillic_chars > latin_chars:
            primary_language = "russian"
            language_ratio = f"{cyrillic_chars}:{latin_chars}"
        else:
            primary_language = "english"
            language_ratio = f"{latin_chars}:{cyrillic_chars}"
        
        # Анализ структуры документа
        headings_level1 = len(re.findall(r'^# ', content, re.MULTILINE))
        headings_level2 = len(re.findall(r'^## ', content, re.MULTILINE))
        headings_level3 = len(re.findall(r'^### ', content, re.MULTILINE))
        
        # Анализ форматирования
        bold_text = len(re.findall(r'\*\*[^*]+\*\*', content))
        italic_text = len(re.findall(r'\*[^*]+\*', content))
        
        # Анализ списков
        ordered_lists = len(re.findall(r'^(\d+\.)\s', content, re.MULTILINE))
        unordered_lists = len(re.findall(r'^(-|\*|\+)\s', content, re.MULTILINE))
        
        # Частотный анализ слов (топ 10)
        words = re.findall(r'\b\w+\b', content.lower())
        word_counter = Counter(words)
        top_words = word_counter.most_common(10)
        
        return {
            "valid": True,  # Анализ не влияет на валидность
            "check": "content_analysis",
            "statistics": {
                "char_count": char_count,
                "word_count": word_count,
                "line_count": line_count,
                "primary_language": primary_language,
                "language_ratio": language_ratio
            },
            "structure": {
                "headings_level1": headings_level1,
                "headings_level2": headings_level2,
                "headings_level3": headings_level3,
                "bold_text": bold_text,
                "italic_text": italic_text,
                "ordered_lists": ordered_lists,
                "unordered_lists": unordered_lists
            },
            "frequent_words": top_words
        }

def generate_report(validation_results, output_format='json'):
    """
    Генерирует отчет о проверке стандартов.
    
    Args:
        validation_results: Результаты проверки
        output_format: Формат вывода (json, markdown, html)
    
    Returns:
        Строка с отчетом в указанном формате
    """
    # Подсчитываем статистику
    total_files = len(validation_results)
    valid_files = sum(1 for result in validation_results.values() if result.get('is_valid'))
    archived_files = sum(1 for result in validation_results.values() if result.get('is_archived'))
    
    # Группируем результаты по типам ошибок
    error_types = {}
    
    for file_path, result in validation_results.items():
        if not result.get('is_valid') and 'results' in result:
            for check, check_result in result['results'].items():
                if not check_result.get('valid'):
                    if check not in error_types:
                        error_types[check] = []
                    
                    error_types[check].append({
                        'file_path': file_path,
                        'message': check_result.get('message', 'Неизвестная ошибка')
                    })
    
    # Формируем отчет в зависимости от формата
    if output_format == 'json':
        report_data = {
            'summary': {
                'total_files': total_files,
                'valid_files': valid_files,
                'invalid_files': total_files - valid_files,
                'archived_files': archived_files,
                'validation_date': datetime.now().isoformat()
            },
            'error_types': error_types,
            'details': validation_results
        }
        
        return json.dumps(report_data, indent=2, ensure_ascii=False)
    
    elif output_format == 'markdown':
        # Формируем отчет в markdown
        report = [
            "# Отчет о проверке стандартов\n",
            f"**Дата проверки:** {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n",
            "## Сводка\n",
            f"- **Всего файлов:** {total_files}",
            f"- **Корректных файлов:** {valid_files} ({valid_files/total_files*100:.1f}%)",
            f"- **Файлов с ошибками:** {total_files - valid_files} ({(total_files - valid_files)/total_files*100:.1f}%)",
            f"- **Архивных файлов:** {archived_files}\n",
        ]
        
        if error_types:
            report.append("## Типы ошибок\n")
            
            for error_type, errors in error_types.items():
                report.append(f"### {error_type} ({len(errors)})\n")
                
                for error in errors:
                    file_name = os.path.basename(error['file_path'])
                    report.append(f"- **{file_name}:** {error['message']}")
                
                report.append("")
        
        return "\n".join(report)
    
    elif output_format == 'html':
        # Формируем отчет в виде HTML
        html = [
            "<!DOCTYPE html>",
            "<html lang='ru'>",
            "<head>",
            "    <meta charset='UTF-8'>",
            "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            "    <title>Отчет о проверке стандартов</title>",
            "    <style>",
            "        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0 auto; max-width: 800px; padding: 20px; }",
            "        h1 { color: #333; }",
            "        h2 { color: #555; margin-top: 20px; }",
            "        h3 { color: #777; margin-top: 15px; }",
            "        .summary { background-color: #f5f5f5; padding: 15px; border-radius: 5px; }",
            "        .file-error { margin-bottom: 5px; }",
            "        .error-count { color: #e74c3c; font-weight: bold; }",
            "        .success-rate { color: #2ecc71; font-weight: bold; }",
            "    </style>",
            "</head>",
            "<body>",
            "    <h1>Отчет о проверке стандартов</h1>",
            f"    <p><strong>Дата проверки:</strong> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</p>",
            "    <div class='summary'>",
            "        <h2>Сводка</h2>",
            f"        <p><strong>Всего файлов:</strong> {total_files}</p>",
            f"        <p><strong>Корректных файлов:</strong> <span class='success-rate'>{valid_files} ({valid_files/total_files*100:.1f}%)</span></p>",
            f"        <p><strong>Файлов с ошибками:</strong> <span class='error-count'>{total_files - valid_files} ({(total_files - valid_files)/total_files*100:.1f}%)</span></p>",
            f"        <p><strong>Архивных файлов:</strong> {archived_files}</p>",
            "    </div>"
        ]
        
        if error_types:
            html.append("    <h2>Типы ошибок</h2>")
            
            for error_type, errors in error_types.items():
                html.append(f"    <h3>{error_type} (<span class='error-count'>{len(errors)}</span>)</h3>")
                html.append("    <ul>")
                
                for error in errors:
                    file_name = os.path.basename(error['file_path'])
                    html.append(f"        <li class='file-error'><strong>{file_name}:</strong> {error['message']}</li>")
                
                html.append("    </ul>")
        
        html.extend([
            "</body>",
            "</html>"
        ])
        
        return "\n".join(html)
    
    else:
        return f"Неподдерживаемый формат отчета: {output_format}"

def main():
    """Основная функция программы."""
    parser = argparse.ArgumentParser(description='Расширенная проверка стандартов')
    parser.add_argument('--include-archived', action='store_true', 
                        help='Включать архивные стандарты в проверку')
    parser.add_argument('--format', choices=['json', 'markdown', 'html'], default='markdown',
                        help='Формат вывода отчета')
    parser.add_argument('--output', default=None,
                        help='Путь для сохранения отчета (по умолчанию выводится в консоль)')
    parser.add_argument('--file', default=None,
                        help='Путь к конкретному файлу для проверки (по умолчанию проверяются все файлы)')
    
    args = parser.parse_args()
    
    # Создаем экземпляр валидатора
    validator = StandardValidator(include_archived=args.include_archived)
    
    # Проверяем стандарты
    if args.file:
        # Проверяем один конкретный файл
        result = {args.file: validator.validate_file(args.file)}
    else:
        # Проверяем все файлы
        result = validator.validate_all()
    
    # Генерируем отчет
    report = generate_report(result, output_format=args.format)
    
    # Выводим или сохраняем отчет
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Отчет сохранен в {args.output}")
    else:
        print(report)

if __name__ == "__main__":
    main()