#!/usr/bin/env python3
"""
Скрипт для проверки на дублирование файлов и инструментов.
Используется при создании новых файлов для предотвращения дублирования функциональности.
"""

import os
import re
import sys
import argparse
import difflib
from collections import defaultdict

def get_file_summary(path):
    """Получает краткую информацию о файле."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Извлекаем первые 10 строк для анализа
        first_lines = '\n'.join(content.split('\n')[:10])
        
        # Ищем описание файла, если есть
        description_match = re.search(r'"""(.+?)"""', content, re.DOTALL)
        description = description_match.group(1).strip() if description_match else ""
        
        # Ищем определения функций и классов
        functions = re.findall(r'def\s+(\w+)', content)
        classes = re.findall(r'class\s+(\w+)', content)
        
        return {
            'path': path,
            'name': os.path.basename(path),
            'first_lines': first_lines,
            'description': description,
            'functions': functions,
            'classes': classes,
            'content': content
        }
    except Exception as e:
        print(f"Ошибка при анализе файла {path}: {e}")
        return None

def find_similar_files(file_info, all_files, threshold=0.7):
    """Находит похожие файлы на основе содержимого."""
    similar_files = []
    
    for other_file in all_files:
        if file_info['path'] == other_file['path']:
            continue
        
        # Сравниваем функциональность
        func_similarity = len(set(file_info['functions']) & set(other_file['functions'])) / len(set(file_info['functions']) | set(other_file['functions'])) if (file_info['functions'] and other_file['functions']) else 0
        
        # Сравниваем описания
        if file_info['description'] and other_file['description']:
            description_similarity = difflib.SequenceMatcher(None, file_info['description'], other_file['description']).ratio()
        else:
            description_similarity = 0
        
        # Общая похожесть
        similarity = max(func_similarity, description_similarity)
        
        if similarity > threshold:
            similar_files.append({
                'path': other_file['path'],
                'similarity': similarity,
                'reason': f"функций: {func_similarity:.2f}, описания: {description_similarity:.2f}"
            })
    
    return similar_files

def find_files_by_extension(root_dir, extensions):
    """Находит все файлы с указанными расширениями."""
    result = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                result.append(os.path.join(root, file))
    return result

def get_all_file_info(root_dir, extensions):
    """Получает информацию о всех файлах заданных типов."""
    file_paths = find_files_by_extension(root_dir, extensions)
    return [get_file_summary(path) for path in file_paths if path]

def find_similar_functionality(input_path, root_dir='.', extensions=None, threshold=0.6):
    """
    Находит файлы с похожей функциональностью.
    
    Args:
        input_path: Путь к проверяемому файлу
        root_dir: Корневая директория для поиска
        extensions: Список расширений файлов для проверки
        threshold: Порог сходства
    
    Returns:
        Список похожих файлов
    """
    if extensions is None:
        extensions = ['.py', '.js', '.sh']
    
    # Получаем информацию о проверяемом файле
    file_info = get_file_summary(input_path)
    if not file_info:
        return []
    
    # Получаем информацию о всех файлах
    all_files = get_all_file_info(root_dir, extensions)
    
    # Находим похожие файлы
    return find_similar_files(file_info, all_files, threshold)

def suggest_modifications(file_info, similar_files):
    """Предлагает модификации для предотвращения дублирования."""
    if not similar_files:
        return "Дублирование не обнаружено. Файл можно создавать."
    
    suggestions = ["Обнаружено возможное дублирование функциональности с существующими файлами:"]
    
    for i, similar in enumerate(similar_files, 1):
        suggestions.append(f"{i}. {similar['path']} (сходство: {similar['similarity']:.2f}, {similar['reason']})")
    
    suggestions.append("\nРекомендации:")
    suggestions.append("1. Рассмотрите возможность модификации существующих файлов вместо создания нового")
    suggestions.append("2. Если создание нового файла необходимо, убедитесь, что его функциональность не дублирует существующую")
    suggestions.append("3. Изучите существующие файлы, чтобы понять, какие части можно переиспользовать")
    
    return "\n".join(suggestions)

def check_standards_compliance(file_info):
    """Проверяет соответствие стандартам."""
    issues = []
    
    # Проверяем наличие документации
    if not file_info['description']:
        issues.append("Отсутствует описание файла в формате документационных строк (docstring)")
    
    # Проверяем соответствие имени файла стандартам
    if not re.match(r'^[a-z][a-z0-9_]*\.[a-z]+$', file_info['name']):
        issues.append(f"Имя файла '{file_info['name']}' не соответствует стандарту именования (snake_case)")
    
    # Проверяем наличие указания на стандарт
    if 'based on:' not in file_info['content'].lower() and 'standard' in file_info['path'].lower():
        issues.append("Отсутствует указание на базовый стандарт (строка 'based on:')")
    
    return issues if issues else None

def main():
    parser = argparse.ArgumentParser(description='Проверка файла на дублирование функциональности')
    parser.add_argument('file', help='Путь к проверяемому файлу')
    parser.add_argument('--dir', default='.', help='Корневая директория для поиска')
    parser.add_argument('--ext', nargs='+', default=['.py', '.js', '.sh'], help='Расширения файлов для проверки')
    parser.add_argument('--threshold', type=float, default=0.6, help='Порог сходства (0-1)')
    
    args = parser.parse_args()
    
    print(f"Проверка файла на дублирование: {args.file}")
    
    file_info = get_file_summary(args.file)
    if not file_info:
        print("Не удалось получить информацию о файле")
        return 1
    
    # Проверяем стандарты
    issues = check_standards_compliance(file_info)
    if issues:
        print("\nВыявлены проблемы соответствия стандартам:")
        for issue in issues:
            print(f"- {issue}")
        print()
    
    # Ищем дублирование
    similar_files = find_similar_functionality(args.file, args.dir, args.ext, args.threshold)
    
    # Выводим рекомендации
    print(suggest_modifications(file_info, similar_files))
    
    return 0 if not similar_files else 1

if __name__ == "__main__":
    sys.exit(main())