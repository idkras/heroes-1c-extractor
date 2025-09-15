#!/usr/bin/env python3
"""
Скрипт для валидации структуры стандартов.

Проверяет соответствие между фактической структурой папок в директории standards.md
и описанием структуры в Registry Standard. Генерирует отчет о несоответствиях
и предлагает корректировки.
"""

import os
import re
import glob
import json
from datetime import datetime

# Конфигурация
STANDARDS_DIR = './standards .md'
REGISTRY_STANDARD_PATH = './standards .md/0. core standards/0.1 registry standard 15 may 2025 1320 CET by AI Assistant.md'
OUTPUT_REPORT_PATH = './validation_report.json'

def extract_structure_from_registry_standard(file_path):
    """
    Извлекает описание структуры из Registry Standard.
    
    Args:
        file_path: Путь к файлу Registry Standard
        
    Returns:
        dict: Описание структуры из стандарта
    """
    print(f"Извлечение описания структуры из {file_path}...")
    
    structure = {
        "description": "Структура согласно Registry Standard",
        "folders": [],
        "file_patterns": []
    }
    
    if not os.path.exists(file_path):
        print(f"ОШИБКА: Файл {file_path} не найден!")
        return structure
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ищем описания структуры
        structure_section = re.search(r'#+\s+Структура\s+стандартов.*?(?=#+|$)', 
                                    content, re.DOTALL | re.IGNORECASE)
        
        if not structure_section:
            print("ОШИБКА: Раздел 'Структура стандартов' не найден в Registry Standard")
            return structure
        
        # Извлекаем упоминания папок
        folders = re.findall(r'[`"\'](.*?(?:standards|process|level\d+|core)[^`"\'\n]*)[`"\']', 
                           structure_section.group(0), re.IGNORECASE)
        
        # Извлекаем форматы файлов
        file_patterns = re.findall(r'[`"\']([^`"\']*?\d+\.\d+[^`"\'\n]*?\.md)[`"\']', 
                                 structure_section.group(0), re.IGNORECASE)
        
        structure["folders"] = list(set(folders))
        structure["file_patterns"] = list(set(file_patterns))
        
        print(f"Извлечено папок: {len(structure['folders'])}, шаблонов файлов: {len(structure['file_patterns'])}")
        
        return structure
    
    except Exception as e:
        print(f"Ошибка при извлечении структуры: {e}")
        return structure

def get_actual_structure(directory):
    """
    Получает фактическую структуру папок и файлов.
    
    Args:
        directory: Корневая директория стандартов
        
    Returns:
        dict: Фактическая структура папок и файлов
    """
    print(f"Анализ фактической структуры в {directory}...")
    
    structure = {
        "description": "Фактическая структура папок",
        "folders": [],
        "files": []
    }
    
    if not os.path.exists(directory):
        print(f"ОШИБКА: Директория {directory} не найдена!")
        return structure
    
    try:
        # Получаем все папки
        for root, dirs, files in os.walk(directory):
            rel_path = os.path.relpath(root, directory).replace('\\', '/')
            if rel_path != '.':
                structure["folders"].append(rel_path)
            
            # Получаем все markdown файлы
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(rel_path, file).replace('\\', '/')
                    if file_path.startswith('./'):
                        file_path = file_path[2:]
                    structure["files"].append(file_path)
        
        print(f"Найдено папок: {len(structure['folders'])}, файлов: {len(structure['files'])}")
        
        return structure
    
    except Exception as e:
        print(f"Ошибка при анализе фактической структуры: {e}")
        return structure

def compare_structures(expected, actual):
    """
    Сравнивает ожидаемую и фактическую структуры.
    
    Args:
        expected: Ожидаемая структура из Registry Standard
        actual: Фактическая структура папок и файлов
        
    Returns:
        dict: Результаты сравнения
    """
    print("Сравнение структур...")
    
    results = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "missing_folders": [],
        "unexpected_folders": [],
        "folder_matches": [],
        "file_pattern_matches": [],
        "suggested_corrections": []
    }
    
    # Проверка на соответствие упомянутых папок
    expected_folder_patterns = [re.compile(pattern.replace('*', '.*'), re.IGNORECASE) 
                              for pattern in expected["folders"]]
    
    # Для каждой фактической папки проверяем, соответствует ли она ожидаемым
    for folder in actual["folders"]:
        is_matched = False
        for pattern in expected_folder_patterns:
            if pattern.search(folder):
                results["folder_matches"].append({
                    "actual": folder,
                    "pattern": pattern.pattern
                })
                is_matched = True
                break
        
        if not is_matched:
            results["unexpected_folders"].append(folder)
    
    # Проверяем, что все ожидаемые паттерны папок найдены
    for i, pattern in enumerate(expected_folder_patterns):
        is_matched = False
        for folder in actual["folders"]:
            if pattern.search(folder):
                is_matched = True
                break
        
        if not is_matched:
            results["missing_folders"].append(expected["folders"][i])
    
    # Проверка файловых паттернов
    for file_pattern in expected["file_patterns"]:
        pattern = re.compile(file_pattern.replace('*', '.*'), re.IGNORECASE)
        matches = [file for file in actual["files"] if pattern.search(file)]
        
        results["file_pattern_matches"].append({
            "pattern": file_pattern,
            "matches": matches,
            "match_count": len(matches)
        })
    
    # Формирование рекомендаций
    if results["unexpected_folders"]:
        results["suggested_corrections"].append(
            "Обновить Registry Standard, добавив следующие папки: " + 
            ", ".join([f"'{folder}'" for folder in results["unexpected_folders"]])
        )
    
    if results["missing_folders"]:
        results["suggested_corrections"].append(
            "Удалить или обновить в Registry Standard следующие несуществующие папки: " + 
            ", ".join([f"'{folder}'" for folder in results["missing_folders"]])
        )
    
    # Сортировка фактической структуры для документации
    actual_folders_description = "\n".join(sorted(actual["folders"]))
    results["suggested_corrections"].append(
        f"Обновить раздел 'Структура стандартов' в Registry Standard, включив актуальную структуру папок:\n\n{actual_folders_description}"
    )
    
    # Общий вывод
    print(f"Сравнение завершено. Найдено несоответствий: {len(results['missing_folders']) + len(results['unexpected_folders'])}")
    
    return results

def generate_folder_structure_markdown(directory):
    """
    Генерирует markdown-описание фактической структуры папок.
    
    Args:
        directory: Корневая директория стандартов
        
    Returns:
        str: Markdown-представление структуры папок
    """
    print("Генерация markdown-описания структуры папок...")
    
    if not os.path.exists(directory):
        return f"Директория {directory} не найдена!"
    
    result = []
    
    # Функция для рекурсивного обхода директорий
    def explore_directory(path, indent_level=0):
        dirs = sorted([d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)) and not d.startswith('.')])
        files = sorted([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.endswith('.md')])
        
        for d in dirs:
            result.append("  " * indent_level + f"- **{d}/**")
            explore_directory(os.path.join(path, d), indent_level + 1)
        
        for f in files:
            result.append("  " * indent_level + f"- {f}")
    
    explore_directory(directory)
    
    return "\n".join(result)

def main():
    """Основная функция скрипта."""
    print(f"=== Проверка структуры стандартов ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===")
    
    # Извлечение ожидаемой структуры из Registry Standard
    expected_structure = extract_structure_from_registry_standard(REGISTRY_STANDARD_PATH)
    
    # Получение фактической структуры
    actual_structure = get_actual_structure(STANDARDS_DIR)
    
    # Сравнение структур
    comparison_results = compare_structures(expected_structure, actual_structure)
    
    # Генерация markdown-описания структуры
    markdown_structure = generate_folder_structure_markdown(STANDARDS_DIR)
    comparison_results["markdown_structure"] = markdown_structure
    
    # Сохранение результатов
    with open(OUTPUT_REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(comparison_results, f, ensure_ascii=False, indent=2)
    
    print(f"Отчет сохранен в {OUTPUT_REPORT_PATH}")
    
    # Вывод результатов в консоль
    print("\n=== Результаты проверки ===")
    print(f"Проверено папок: {len(actual_structure['folders'])}")
    print(f"Проверено файлов: {len(actual_structure['files'])}")
    print(f"Несоответствий в структуре: {len(comparison_results['missing_folders']) + len(comparison_results['unexpected_folders'])}")
    
    if comparison_results["unexpected_folders"]:
        print("\nНеожиданные папки (отсутствуют в Registry Standard):")
        for folder in comparison_results["unexpected_folders"]:
            print(f"  - {folder}")
    
    if comparison_results["missing_folders"]:
        print("\nОтсутствующие папки (упомянуты в Registry Standard, но не существуют):")
        for folder in comparison_results["missing_folders"]:
            print(f"  - {folder}")
    
    print("\nРекомендации:")
    for i, suggestion in enumerate(comparison_results["suggested_corrections"], 1):
        print(f"{i}. {suggestion}")
    
    print("\n=== Текущая структура папок ===")
    print(markdown_structure)

if __name__ == "__main__":
    main()