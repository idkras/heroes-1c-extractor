#!/usr/bin/env python3
"""
Утилита для валидации стандартов TaskMaster.

Проверяет соответствие стандартов правилам именования и форматирования.
Поддерживает проверку одного файла или всех файлов в директории.

Примеры использования:
    python scripts/validate_standard.py advising\ standards\ .md/0.1\ registry\ standard\ 14\ may\ 2025\ 0350\ cet\ by\ ai\ assistant.md
    python scripts/validate_standard.py --dir "advising standards .md" --recursive
"""

__version__ = '1.0.0'
__author__ = 'AI Assistant'
__updated__ = '14 may 2025'
__status__ = 'active'

import os
import sys
import argparse
import json
from typing import Dict, List, Tuple, Any, Optional

# Добавляем путь к корневой директории проекта для импорта модулей
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Импортируем библиотеку валидации
try:
    from scripts.lib.validation import (
        validate_filename,
        validate_protected_sections,
        validate_case_in_headers,
        scan_directory
    )
except ImportError as e:
    print(f"Ошибка импорта библиотеки валидации: {e}")
    print("Убедитесь, что файл scripts/lib/validation.py существует")
    sys.exit(1)

def validate_file(file_path: str, verbose: bool = False) -> Dict[str, Any]:
    """
    Полная валидация файла стандарта.
    
    Args:
        file_path: Путь к файлу для проверки
        verbose: Подробный вывод результатов
        
    Returns:
        Dict с результатами проверки
    """
    results = {
        "file_path": file_path,
        "filename_valid": False,
        "protected_sections_valid": False,
        "headers_case_valid": False,
        "overall_valid": False,
        "errors": []
    }
    
    # Проверка существования файла
    if not os.path.exists(file_path):
        results["errors"].append(f"Файл {file_path} не существует")
        return results
    
    # Проверка имени файла
    filename = os.path.basename(file_path)
    is_valid_name, name_reasons = validate_filename(filename)
    results["filename_valid"] = is_valid_name
    
    if not is_valid_name:
        results["errors"].extend([f"Ошибка в имени файла: {reason}" for reason in name_reasons])
    
    # Проверка защищенных разделов
    is_valid_sections, section_errors, section_warnings = validate_protected_sections(file_path)
    results["protected_sections_valid"] = is_valid_sections
    
    if not is_valid_sections:
        results["errors"].extend([f"Ошибка в защищенных разделах: {error}" for error in section_errors])
    
    if section_warnings:
        results["warnings"] = section_warnings
    
    # Проверка регистра в заголовках
    is_valid_case, case_errors = validate_case_in_headers(file_path)
    results["headers_case_valid"] = is_valid_case
    
    if not is_valid_case:
        results["errors"].extend([f"Ошибка в регистре заголовков: {error}" for error in case_errors])
    
    # Общий результат валидации
    results["overall_valid"] = is_valid_name and is_valid_sections and is_valid_case
    
    # Подробный вывод результатов
    if verbose:
        print(f"\nПроверка файла: {file_path}")
        print(f"  Имя файла: {'✅' if is_valid_name else '❌'}")
        if not is_valid_name:
            for reason in name_reasons:
                print(f"    - {reason}")
        
        print(f"  Защищенные разделы: {'✅' if is_valid_sections else '❌'}")
        if not is_valid_sections:
            for error in section_errors:
                print(f"    - {error}")
        
        if section_warnings:
            print("  Предупреждения:")
            for warning in section_warnings:
                print(f"    - {warning}")
        
        print(f"  Регистр заголовков: {'✅' if is_valid_case else '❌'}")
        if not is_valid_case:
            for error in case_errors:
                print(f"    - {error}")
        
        print(f"  Общий результат: {'✅' if results['overall_valid'] else '❌'}")
    
    return results

def validate_directory(directory: str, recursive: bool = False, verbose: bool = False) -> Dict[str, Any]:
    """
    Валидация всех файлов в директории.
    
    Args:
        directory: Путь к директории для сканирования
        recursive: Рекурсивный поиск во вложенных директориях
        verbose: Подробный вывод результатов
        
    Returns:
        Dict с результатами проверки
    """
    results = {
        "directory": directory,
        "recursive": recursive,
        "valid_files": [],
        "invalid_files": {},
        "summary": {
            "total_files": 0,
            "valid_files": 0,
            "invalid_files": 0,
            "percentage_valid": 0
        }
    }
    
    # Проверяем все файлы в директории
    for root, dirs, files in os.walk(directory):
        # Если не рекурсивный поиск, пропускаем вложенные директории
        if not recursive and root != directory:
            continue
        
        # Находим все markdown файлы
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                
                # Валидируем файл
                file_result = validate_file(file_path, verbose)
                
                # Обновляем результаты
                if file_result["overall_valid"]:
                    results["valid_files"].append(file_path)
                else:
                    results["invalid_files"][file_path] = file_result["errors"]
    
    # Расчет статистики
    results["summary"]["total_files"] = len(results["valid_files"]) + len(results["invalid_files"])
    results["summary"]["valid_files"] = len(results["valid_files"])
    results["summary"]["invalid_files"] = len(results["invalid_files"])
    
    if results["summary"]["total_files"] > 0:
        results["summary"]["percentage_valid"] = (results["summary"]["valid_files"] / results["summary"]["total_files"]) * 100
    
    # Вывод итоговой статистики
    if verbose:
        print("\nИтоговая статистика:")
        print(f"  Всего файлов: {results['summary']['total_files']}")
        print(f"  Валидных файлов: {results['summary']['valid_files']} "
              f"({results['summary']['percentage_valid']:.1f}%)")
        print(f"  Невалидных файлов: {results['summary']['invalid_files']}")
        
        if results["invalid_files"]:
            print("\nСписок файлов с ошибками:")
            for file_path, errors in results["invalid_files"].items():
                print(f"  - {file_path}")
                for error in errors:
                    print(f"    • {error}")
    
    return results

def main():
    """Основная функция программы."""
    parser = argparse.ArgumentParser(description='Валидация стандартов TaskMaster')
    
    # Настройка аргументов
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('file', nargs='?', help='Путь к файлу для проверки')
    group.add_argument('--dir', help='Путь к директории для проверки')
    
    parser.add_argument('--recursive', '-r', action='store_true', 
                        help='Рекурсивный поиск во вложенных директориях')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Подробный вывод результатов')
    parser.add_argument('--json', '-j', action='store_true',
                        help='Вывод результатов в формате JSON')
    
    args = parser.parse_args()
    
    # Определяем режим работы
    results = None
    
    if args.file:
        # Режим проверки одного файла
        results = validate_file(args.file, args.verbose)
    elif args.dir:
        # Режим проверки директории
        results = validate_directory(args.dir, args.recursive, args.verbose)
    
    # Вывод результатов в JSON
    if args.json and results:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    
    # Успешное завершение, если все проверки прошли успешно
    if args.file and results and results["overall_valid"]:
        sys.exit(0)
    elif args.dir and results and results["summary"]["invalid_files"] == 0:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()