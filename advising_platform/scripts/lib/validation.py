#!/usr/bin/env python3
"""
Библиотека для валидации стандартов и документов.

Содержит комплекс инструментов для проверки соответствия документов
установленным стандартам, включая проверку имен файлов, форматирования,
метаданных и защищенных разделов.

Использование:
  from scripts.lib.validation import validate_filename, validate_protected_sections
  
  # Проверка имени файла
  is_valid, reasons = validate_filename('example.md')
  
  # Проверка защищенных разделов
  is_valid, errors, warnings = validate_protected_sections('example.md')
"""

__version__ = '1.0.0'
__author__ = 'AI Assistant'
__updated__ = '14 may 2025'
__status__ = 'active'

import os
import re
import json
from typing import Dict, List, Tuple, Optional, Union, Any, Pattern

# Регулярное выражение для проверки соответствия имени файла стандарту TaskMaster
FILENAME_PATTERN = r'^(\d+)\.(\d+)\s+([a-z\s\-\_]+)\s+(\d{1,2}\s+[a-z]+\s+\d{4})\s+(\d{4})\s+([a-z]{2,4})\s+by\s+([a-z\s]+)\.md$'

# Регулярные выражения для поиска защищенных разделов
PROTECTED_BEGIN = r'<!--\s*🔒\s*PROTECTED\s*SECTION:\s*BEGIN\s*-->'
PROTECTED_END = r'<!--\s*🔒\s*PROTECTED\s*SECTION:\s*END\s*-->'

# Обязательные метаданные, которые должны быть в защищенном разделе
REQUIRED_METADATA = [
    'updated',
    'version',
    'status'
]

# Дополнительные метаданные, которые могут быть в защищенном разделе
OPTIONAL_METADATA = [
    'based on',
    'previous version',
    'integrated',
    'author'
]

def validate_filename(filename: str) -> Tuple[bool, List[str]]:
    """
    Проверяет, соответствует ли имя файла стандарту TaskMaster.
    
    Args:
        filename: Имя файла для проверки
        
    Returns:
        Кортеж, содержащий:
        - Булево значение, указывающее на соответствие стандарту
        - Список причин несоответствия (если есть)
        
    Example:
        >>> is_valid, reasons = validate_filename("0.1 registry standard 14 may 2025 0350 cet by ai assistant.md")
        >>> is_valid
        True
    """
    reasons = []
    
    # Особые случаи для имен файлов
    special_filenames = [
        "0.0 task master 10 may 2226 cet by ilya krasinsky.md"
    ]
    
    # Если файл в списке исключений, пропускаем проверку шаблона
    if filename in special_filenames:
        # Проверка регистра символов (исключения применяются только к шаблону, но не к регистру)
        if not filename.islower():
            reasons.append("Имя файла содержит заглавные буквы")
        return len(reasons) == 0, reasons
    
    # Проверка на соответствие шаблону
    match = re.match(FILENAME_PATTERN, filename, re.IGNORECASE)
    if not match:
        reasons.append("Имя файла не соответствует шаблону [раздел].[подраздел] [тип] [дата] [время] [часовой пояс] by [автор].md")
        return False, reasons
    
    # Проверка регистра символов
    if not filename.islower():
        reasons.append("Имя файла содержит заглавные буквы")
    
    # Проверка даты и времени
    date_part = match.group(4)
    time_part = match.group(5)
    timezone_part = match.group(6)
    
    # Проверка формата даты (должен быть DD month YYYY)
    date_match = re.match(r'^\d{1,2}\s+[a-z]+\s+\d{4}$', date_part, re.IGNORECASE)
    if not date_match:
        reasons.append(f"Неверный формат даты: '{date_part}'. Ожидается: 'DD month YYYY'")
    
    # Проверка формата времени (должен быть HHMM)
    time_match = re.match(r'^\d{4}$', time_part)
    if not time_match:
        reasons.append(f"Неверный формат времени: '{time_part}'. Ожидается: 'HHMM'")
    
    # Проверка часового пояса
    if timezone_part.lower() not in ['cet', 'utc', 'et', 'pt']:
        reasons.append(f"Неизвестный часовой пояс: '{timezone_part}'. Рекомендуемые: 'cet', 'utc'")
    
    return len(reasons) == 0, reasons

def validate_protected_sections(file_path: str) -> Tuple[bool, List[str], List[str]]:
    """
    Проверяет защищенные разделы в файле.
    
    Args:
        file_path: Путь к файлу для проверки
            
    Returns:
        Кортеж из трех элементов:
        - Булево значение, указывающее на успешность проверки
        - Список ошибок (если есть)
        - Список предупреждений (если есть)
            
    Raises:
        FileNotFoundError: Если указанный файл не существует
            
    Example:
        >>> is_valid, errors, warnings = validate_protected_sections("example.md")
        >>> if not is_valid:
        ...     print(f"Found {len(errors)} errors")
    """
    errors = []
    warnings = []
    
    # Проверка существования файла
    if not os.path.exists(file_path):
        errors.append(f"Файл {file_path} не существует")
        return False, errors, warnings
    
    # Проверка markdown файла
    if not file_path.endswith('.md'):
        warnings.append(f"Файл {file_path} не является markdown файлом")
        return True, errors, warnings
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Поиск начала и конца защищенных разделов
        begin_matches = list(re.finditer(PROTECTED_BEGIN, content, re.IGNORECASE))
        end_matches = list(re.finditer(PROTECTED_END, content, re.IGNORECASE))
        
        # Проверка наличия защищенных разделов
        if not begin_matches:
            errors.append(f"В файле {file_path} не найдено начало защищенного раздела")
            return False, errors, warnings
            
        if not end_matches:
            errors.append(f"В файле {file_path} не найдено окончание защищенного раздела")
            return False, errors, warnings
            
        # Проверка соответствия количества маркеров начала и конца
        if len(begin_matches) != len(end_matches):
            errors.append(f"В файле {file_path} количество маркеров начала ({len(begin_matches)}) не соответствует количеству маркеров конца ({len(end_matches)})")
            return False, errors, warnings
        
        # Проверка правильного порядка маркеров (начало должно быть перед концом)
        for i in range(len(begin_matches)):
            begin_pos = begin_matches[i].start()
            end_pos = end_matches[i].start()
            
            if begin_pos >= end_pos:
                errors.append(f"В файле {file_path} маркер начала защищенного раздела находится после маркера конца")
                return False, errors, warnings
        
        # Проверка содержимого первого защищенного раздела (метаданные)
        if begin_matches:
            protected_content = content[begin_matches[0].end():end_matches[0].start()].strip()
            # Проверка обязательных метаданных
            for metadata in REQUIRED_METADATA:
                if not re.search(rf'{metadata}:', protected_content, re.IGNORECASE):
                    errors.append(f"В файле {file_path} отсутствует обязательное поле '{metadata}' в защищенном разделе")
            
            # Проверка регистра полей метаданных (должны быть в нижнем регистре)
            metadata_lines = protected_content.split('\n')
            for line in metadata_lines:
                if ':' in line:
                    field = line.split(':', 1)[0].strip()
                    if not field.islower():
                        errors.append(f"В файле {file_path} поле '{field}' должно быть в нижнем регистре")
        
        # Проверка лицензии (должна быть в защищенном разделе)
        license_begin = None
        
        if len(begin_matches) >= 2:
            # Проверяем последний защищенный раздел на наличие лицензии
            last_protected_content = content[begin_matches[-1].end():end_matches[-1].start()].strip()
            if "лицензия" in last_protected_content.lower() or "license" in last_protected_content.lower():
                license_begin = begin_matches[-1]
        
        if not license_begin:
            warnings.append(f"В файле {file_path} не найден защищенный раздел с лицензией")
        
        return len(errors) == 0, errors, warnings
        
    except Exception as e:
        errors.append(f"Ошибка при проверке файла {file_path}: {str(e)}")
        return False, errors, warnings

def scan_directory(directory: str, validator_func: Any, recursive: bool = False) -> Dict[str, Any]:
    """
    Сканирует директорию на наличие markdown файлов и проверяет их с помощью указанного валидатора.
    
    Args:
        directory: Путь к директории для сканирования
        validator_func: Функция валидации, принимающая путь к файлу
        recursive: Рекурсивный поиск во вложенных директориях
        
    Returns:
        Dict с результатами проверки
    """
    results = {"valid": [], "invalid": {}}
    
    for root, dirs, files in os.walk(directory):
        # Если не рекурсивный поиск, пропускаем вложенные директории
        if not recursive and root != directory:
            continue
        
        # Находим все markdown файлы
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                
                if validator_func == validate_filename:
                    is_valid, reasons = validator_func(file)
                    if is_valid:
                        results["valid"].append(file_path)
                    else:
                        results["invalid"][file_path] = reasons
                elif validator_func == validate_protected_sections:
                    is_valid, errors, warnings = validator_func(file_path)
                    if is_valid:
                        results["valid"].append(file_path)
                    else:
                        results["invalid"][file_path] = {
                            "errors": errors,
                            "warnings": warnings
                        }
    
    return results

def validate_case_in_headers(file_path: str) -> Tuple[bool, List[str]]:
    """
    Проверяет наличие заглавных букв в заголовках документа.
    
    Args:
        file_path: Путь к файлу для проверки
        
    Returns:
        Кортеж из двух элементов:
        - Булево значение, указывающее, все ли заголовки в нижнем регистре
        - Список заголовков с заглавными буквами
    """
    errors = []
    
    # Проверка существования файла
    if not os.path.exists(file_path):
        errors.append(f"Файл {file_path} не существует")
        return False, errors
    
    # Проверка markdown файла
    if not file_path.endswith('.md'):
        return True, []  # Не markdown файл, пропускаем
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ищем все заголовки (строки, начинающиеся с #)
        header_pattern = r'^(#{1,6})\s+(.+)$'
        headers = re.findall(header_pattern, content, re.MULTILINE)
        
        for level, header_text in headers:
            # Игнорируем заголовки в защищенных секциях
            in_protected = False
            protected_begin_pos = [m.start() for m in re.finditer(PROTECTED_BEGIN, content, re.IGNORECASE)]
            protected_end_pos = [m.start() for m in re.finditer(PROTECTED_END, content, re.IGNORECASE)]
            
            header_pos = content.find(level + ' ' + header_text)
            for i in range(len(protected_begin_pos)):
                if i < len(protected_end_pos) and protected_begin_pos[i] < header_pos < protected_end_pos[i]:
                    in_protected = True
                    break
            
            if in_protected:
                continue
            
            # Особые случаи, которые нужно разрешить:
            # 1. Заголовки с эмодзи и специальными символами
            # 2. Заголовки с числами в начале (например, '1. Заголовок')
            # 3. Заголовки со скобками (например, 'Заголовок (комментарий)')
            # 4. Заголовки на других языках (например, русском)
            
            # Если заголовок начинается с числа и точки, обрабатываем особым образом
            if re.match(r'^\d+\.\s', header_text):
                # Удаляем начальное число и точку
                text_after_number = re.sub(r'^\d+\.\s', '', header_text)
                # Проверяем остаток
                if text_after_number.strip():
                    header_to_check = text_after_number
                else:
                    continue  # Заголовок только из числа, игнорируем
            else:
                header_to_check = header_text
            
            # Удаляем эмодзи и другие специальные символы
            clean_header = re.sub(r'[^\w\s\(\)\[\]]', '', header_to_check)
            
            # Удаляем содержимое скобок (как круглых, так и квадратных)
            clean_header = re.sub(r'\([^)]*\)', '', clean_header)
            clean_header = re.sub(r'\[[^\]]*\]', '', clean_header)
            
            # Удаляем лишние пробелы
            clean_header = clean_header.strip()
            
            # Проверяем, содержит ли заголовок буквы латинского алфавита
            latin_letters = ''.join(c for c in clean_header if c.isalpha() and 'a' <= c.lower() <= 'z')
            
            # Если заголовок содержит латинские буквы и есть заглавные буквы
            if latin_letters and latin_letters != latin_letters.lower():
                # Исключения для технических терминов, которые принято писать с заглавной буквы
                technical_terms = [
                    "API", "URL", "HTML", "JSON", "HTTP", "XML", "REST",
                    "SQL", "NoSQL", "OAuth", "JWT", "WebSocket", "GraphQL",
                    "Workflow", "Action Plan", "CI/CD", "DevOps", "TaskMaster",
                    "Auto", "Output"
                ]
                
                # Особые случаи для обработки
                special_terms = [
                    "Task Master", "TaskMaster", "Auto-", "Output", 
                    "Registry Standard", "JTBD", "ProductHeroes",
                    "Registry", "Goal Map", "Closed Loop Incident Resolution",
                    "CLIR", "Advising", "AI", "Context", "Customer Development",
                    "CET", "End-to-End", "Page Object", "App Actions",
                    "Agile", "Follow-up", "Shadowing", "Rick.ai", "Pull",
                    "@heroesGPT_bot", "Release Notes", "Enterprise Suite"
                ]
                
                contains_tech_term = False
                for term in special_terms:
                    if term in header_text:
                        contains_tech_term = True
                        break
                
                # Если заголовок содержит квадратные скобки, разрешаем заглавные буквы внутри них
                if re.search(r'\[[^\]]*[A-Z][^\]]*\]', header_text):
                    contains_tech_term = True
                
                # Если не нашли специальные термины и не нашли квадратные скобки, проверяем технические термины
                if not contains_tech_term:
                    for term in technical_terms:
                        if term.lower() in clean_header.lower():
                            term_pos = clean_header.lower().find(term.lower())
                            term_end = term_pos + len(term)
                            
                            # Проверяем, что термин не является частью другого слова
                            if (term_pos == 0 or not clean_header[term_pos-1].isalpha()) and \
                               (term_end == len(clean_header) or not clean_header[term_end].isalpha()):
                                contains_tech_term = True
                                break
                
                # Особые случаи: акронимы и технические термины
                if not all(c.isupper() for c in latin_letters) and latin_letters.upper() != latin_letters and not contains_tech_term:
                    errors.append(f"Заголовок '{header_text}' содержит заглавные буквы")
    
    except Exception as e:
        errors.append(f"Ошибка при проверке файла {file_path}: {str(e)}")
    
    return len(errors) == 0, errors

def validate_header_structure(file_path: str, template_file: str) -> Tuple[bool, List[str]]:
    """
    Проверяет соответствие структуры заголовков в документе заданному шаблону.
    
    Args:
        file_path: Путь к проверяемому файлу
        template_file: Путь к файлу-шаблону со структурой заголовков
        
    Returns:
        Кортеж из двух элементов:
        - Булево значение, указывающее на соответствие структуры
        - Список несоответствий
    """
    errors = []
    
    # Проверка существования файлов
    if not os.path.exists(file_path):
        errors.append(f"Файл {file_path} не существует")
        return False, errors
    
    if not os.path.exists(template_file):
        errors.append(f"Файл шаблона {template_file} не существует")
        return False, errors
    
    # Извлечение заголовков из файлов
    try:
        # Из проверяемого файла
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        file_headers = extract_headers(content)
        
        # Из файла-шаблона
        with open(template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()
            
        template_headers = extract_headers(template_content)
        
        # Проверка соответствия структуры
        if len(file_headers) == 0:
            errors.append(f"В файле {file_path} не найдены заголовки")
            return False, errors
        
        if len(template_headers) == 0:
            errors.append(f"В файле шаблона {template_file} не найдены заголовки")
            return False, errors
        
        # Проверка наличия всех обязательных заголовков из шаблона
        for level, header_text in template_headers:
            # Проверяем, есть ли заголовок с таким же уровнем и текстом в проверяемом файле
            found = False
            for file_level, file_header_text in file_headers:
                # Сравниваем без учета регистра и специальных символов
                if level == file_level and clean_header_text(header_text) == clean_header_text(file_header_text):
                    found = True
                    break
            
            if not found:
                errors.append(f"Обязательный заголовок '{header_text}' уровня {level} не найден в файле {file_path}")
    
    except Exception as e:
        errors.append(f"Ошибка при проверке структуры файла {file_path}: {str(e)}")
    
    return len(errors) == 0, errors

def extract_headers(content: str) -> List[Tuple[str, str]]:
    """
    Извлекает заголовки из контента markdown.
    
    Args:
        content: Текст markdown документа
        
    Returns:
        Список кортежей (уровень_заголовка, текст_заголовка)
    """
    header_pattern = r'^(#{1,6})\s+(.+)$'
    headers = re.findall(header_pattern, content, re.MULTILINE)
    return headers

def clean_header_text(header_text: str) -> str:
    """
    Очищает текст заголовка для сравнения, удаляя специальные символы и приводя к нижнему регистру.
    
    Args:
        header_text: Текст заголовка
        
    Returns:
        Очищенный текст заголовка
    """
    # Удаляем эмодзи и другие специальные символы
    clean_text = re.sub(r'[^\w\s]', '', header_text)
    # Приводим к нижнему регистру и удаляем лишние пробелы
    clean_text = clean_text.lower().strip()
    return clean_text