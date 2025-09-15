#!/usr/bin/env python3
"""
Скрипт для сравнения фактической структуры файлов с документированной.
Помогает поддерживать актуальность документации структуры проекта.
"""

import sys
import re
import os
from collections import defaultdict

def extract_paths_from_markdown(md_file):
    """Извлекает пути к файлам из markdown документа."""
    paths = []
    link_pattern = re.compile(r'\[.*?\]\((.*?)\)')
    file_pattern = re.compile(r'`(.*?\.md)`')
    
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Извлекаем ссылки [текст](путь)
            links = link_pattern.findall(content)
            for link in links:
                if link.endswith('.md'):
                    # Декодируем URL-кодированные символы
                    decoded_link = link.replace('%20', ' ')
                    paths.append(decoded_link)
            
            # Извлекаем упоминания файлов в обратных кавычках
            files = file_pattern.findall(content)
            paths.extend(files)
    except Exception as e:
        print(f"Ошибка при чтении файла {md_file}: {e}")
    
    return paths

def get_actual_structure(structure_file):
    """Получает список фактических файлов из текстового файла."""
    actual_files = []
    try:
        with open(structure_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.endswith('.md'):
                    # Убираем префикс './' если есть
                    normalized_path = line[2:] if line.startswith('./') else line
                    actual_files.append(normalized_path)
    except Exception as e:
        print(f"Ошибка при чтении файла {structure_file}: {e}")
    
    return actual_files

def compare_structures(actual_files, documented_files):
    """Сравнивает фактическую и документированную структуру файлов."""
    actual_set = set(actual_files)
    documented_set = set(documented_files)
    
    missing_in_docs = actual_set - documented_set
    not_exists = documented_set - actual_set
    
    return {
        'missing_in_docs': sorted(list(missing_in_docs)),
        'not_exists': sorted(list(not_exists))
    }

def print_report(comparison):
    """Выводит отчет о сравнении структур."""
    print("\n=== ОТЧЕТ О СРАВНЕНИИ СТРУКТУРЫ ФАЙЛОВ ===\n")
    
    print("Файлы, отсутствующие в документации (требуется добавить):")
    if comparison['missing_in_docs']:
        for file in comparison['missing_in_docs']:
            print(f"  - {file}")
    else:
        print("  Все файлы документированы.")
    
    print("\nФайлы, упомянутые в документации, но не существующие (требуется исправить):")
    if comparison['not_exists']:
        for file in comparison['not_exists']:
            print(f"  - {file}")
    else:
        print("  Все документированные файлы существуют.")
    
    # Статистика
    total_actual = len(comparison['missing_in_docs']) + (
        len(comparison['not_exists']) - len(comparison['not_exists']))
    total_documented = len(comparison['not_exists']) + (
        len(comparison['missing_in_docs']) - len(comparison['missing_in_docs']))
    
    if total_actual > 0:
        accuracy = (1 - len(comparison['missing_in_docs']) / total_actual) * 100
        print(f"\nТочность документации: {accuracy:.1f}%")
    
    if comparison['missing_in_docs'] or comparison['not_exists']:
        print("\nРекомендуемые действия:")
        if comparison['missing_in_docs']:
            print("  1. Обновите project_structure.md, добавив отсутствующие файлы")
        if comparison['not_exists']:
            print("  2. Исправьте ссылки на несуществующие файлы в документации")
        print("  3. Запустите скрипт повторно после внесения изменений")
    else:
        print("\nДокументация соответствует фактической структуре файлов.")

def main():
    if len(sys.argv) != 3:
        print("Использование: python compare_structure.py structure_file.txt project_structure.md")
        sys.exit(1)
    
    structure_file = sys.argv[1]
    markdown_file = sys.argv[2]
    
    if not os.path.exists(structure_file):
        print(f"Файл {structure_file} не найден.")
        sys.exit(1)
    
    if not os.path.exists(markdown_file):
        print(f"Файл {markdown_file} не найден.")
        sys.exit(1)
    
    actual_files = get_actual_structure(structure_file)
    documented_files = extract_paths_from_markdown(markdown_file)
    
    comparison = compare_structures(actual_files, documented_files)
    print_report(comparison)

if __name__ == "__main__":
    main()