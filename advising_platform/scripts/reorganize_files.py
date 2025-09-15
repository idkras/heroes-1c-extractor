#!/usr/bin/env python3
"""
Скрипт для перемещения файлов из корневого каталога
в соответствующие директории в структуре advising_platform.

Скрипт соответствует стандарту организации кодовой базы (standard:codebase_organization)
и используется для решения проблемы хаоса в корневой директории проекта.
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
import re

# Определение пути к корневой директории проекта
ROOT_DIR = Path(__file__).parent.parent.parent
PROJECT_DIR = Path(__file__).parent.parent

# Создаем словарь с категориями файлов и их целевыми директориями
file_categories = {
    # Инструменты для работы с документами
    "document_tools": {
        "target_dir": PROJECT_DIR / "src/tools/document",
        "files": [
            "abstract_links_cli.py",
            "abstract_links_tool.py",
            "add_logical_id.py",
            "convert_links.py",
            "document_abstractions.py",
            "register_standard_ids.py",
        ]
    },
    # Инструменты для анализа и аудита
    "analysis_tools": {
        "target_dir": PROJECT_DIR / "src/tools/analysis",
        "files": [
            "compare_structure.py",
            "research_documents.py",
            "search_abstractions.py",
        ]
    },
    # Инструменты для интеграции
    "integration_tools": {
        "target_dir": PROJECT_DIR / "src/tools/integration",
        "files": [
            "api_client.py",
            "export_to_gdocs.py",
            "generate_pdf.py",
            "webhook_client.py",
        ]
    },
    # Серверные компоненты
    "server_components": {
        "target_dir": PROJECT_DIR / "src/api",
        "files": [
            "server.py",
            "server_api.py",
            "simple_server.py",
        ]
    },
    # Инструменты для работы с задачами
    "task_tools": {
        "target_dir": PROJECT_DIR / "src/tools/task",
        "files": [
            "update_todo_tasks.py",
        ]
    },
    # Веб-компоненты
    "web_components": {
        "target_dir": PROJECT_DIR / "src/web",
        "files": [
            "api_test.html",
            "index.html",
        ]
    },
    # Статические веб-ресурсы
    "static_components": {
        "target_dir": PROJECT_DIR / "src/web/static",
        "files": [
            "celebrations.js",
            "comments.css",
            "comments.js",
            "tooltip.css",
            "tooltip.js",
            "generated-icon.png",
        ]
    },
    # Документация
    "documentation": {
        "target_dir": PROJECT_DIR / "docs",
        "files": [
            "abstract_links_README.md",
            "abstract_links_example.md",
            "advising_instructions.md",
            "complex_test.md",
            "file_structure_analysis.md",
            "fragment_links_backup.md",
            "fragment_links_example.md",
            "obsolete_files_analysis.md",
            "project_structure.md",
            "README.md",
            "reorganization_plan.md",
            "test_abstract_links.md",
            "test_links.md",
            "test_links_correct.md",
            "todo_backup.md",
            "co-evolution journal.md",
        ]
    },
    # Данные и временные файлы
    "data_files": {
        "target_dir": PROJECT_DIR / "data",
        "files": [
            "document_analysis_results.json",
            "document_registry.json",
            "project_structure_report.json",
            "validation_report.json",
            "tmp_incident.json",
            "tmp_incident2.json",
        ]
    },
    # Скрипты
    "scripts": {
        "target_dir": PROJECT_DIR / "scripts",
        "files": [
            "git_log_commands.sh",
            "scrape_garderob_hypothises.py",
        ]
    },
    # Конфигурационные файлы
    "config_files": {
        "target_dir": PROJECT_DIR / "config",
        "files": [
            # Пока не перемещаем, так как могут быть нужны в корне
            # "package.json",
            # "package-lock.json",
            # "pyproject.toml",
        ]
    },
}

def ensure_directory_exists(directory):
    """
    Проверяет, существует ли директория, и создает ее при необходимости.
    
    Args:
        directory (str or Path): Путь к директории
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Создана директория: {directory}")

def copy_or_move_file(source, destination, move=False):
    """
    Копирует или перемещает файл из одного места в другое.
    
    Args:
        source (str or Path): Путь к исходному файлу
        destination (str or Path): Путь к целевому файлу
        move (bool): Если True - перемещает файл, если False - копирует
        
    Returns:
        bool: True, если операция успешна, иначе False
    """
    try:
        # Проверяем, существует ли целевой файл
        if os.path.exists(destination):
            print(f"Файл уже существует: {destination}")
            return False
        
        # Создаем директорию назначения, если она не существует
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        
        # Копируем или перемещаем файл
        if move:
            shutil.move(source, destination)
            print(f"Перемещен файл: {source} -> {destination}")
        else:
            shutil.copy2(source, destination)
            print(f"Скопирован файл: {source} -> {destination}")
        return True
    except Exception as e:
        print(f"Ошибка при обработке файла {source}: {e}")
        return False

def create_init_files(directory):
    """
    Создает файлы __init__.py в директории и всех ее родительских директориях.
    
    Args:
        directory (str or Path): Путь к директории
    """
    current_dir = Path(directory)
    root_dir = PROJECT_DIR
    
    # Создаем список директорий от текущей до корневой
    dirs_to_process = []
    while current_dir != root_dir.parent:
        dirs_to_process.append(current_dir)
        current_dir = current_dir.parent
        if not str(current_dir).startswith(str(root_dir)):
            break
    
    # Создаем __init__.py в каждой директории
    for dir_path in dirs_to_process:
        init_file = dir_path / "__init__.py"
        if not init_file.exists():
            with open(init_file, 'w') as f:
                f.write('"""\n')
                f.write(f"Модуль {dir_path.name}\n")
                f.write('"""\n')
            print(f"Создан файл: {init_file}")

def update_imports(file_path, original_path):
    """
    Обновляет импорты в файле после его перемещения.
    
    Args:
        file_path (str or Path): Путь к перемещенному файлу
        original_path (str or Path): Исходный путь файла
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        project_name = "advising_platform"
        
        # Создаем относительный путь от нового местоположения до корня проекта
        rel_path = os.path.relpath(PROJECT_DIR, os.path.dirname(file_path))
        
        # Находим импорты, которые могут быть относительными к корню проекта
        imports_pattern = r'(?:from|import)\s+([a-zA-Z0-9_\.]+)'
        imports = re.findall(imports_pattern, content)
        
        # Проверяем, существуют ли импортируемые модули в новой структуре
        for import_path in imports:
            # Пропускаем стандартные библиотеки и абсолютные импорты
            if '.' not in import_path or import_path.startswith(project_name):
                continue
            
            # Проверяем, есть ли соответствующий файл в новой структуре
            parts = import_path.split('.')
            module_path = os.path.join(*parts) + '.py'
            new_module_path = PROJECT_DIR / module_path
            
            if new_module_path.exists():
                # Обновляем импорт
                new_import_path = f"{project_name}." + import_path
                content = content.replace(
                    f'from {import_path}', 
                    f'from {new_import_path}'
                )
                content = content.replace(
                    f'import {import_path}', 
                    f'import {new_import_path}'
                )
                print(f"Обновлен импорт в {file_path}: {import_path} -> {new_import_path}")
        
        # Записываем обновленное содержимое
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    except Exception as e:
        print(f"Ошибка при обновлении импортов в {file_path}: {e}")

def find_duplicate_files():
    """
    Находит дублирующиеся файлы между корневой директорией и структурой проекта.
    
    Returns:
        list: Список кортежей (исходный_файл, целевой_файл) для дублирующихся файлов
    """
    duplicates = []
    for category, info in file_categories.items():
        for file_name in info["files"]:
            source = ROOT_DIR / file_name
            destination = info["target_dir"] / file_name
            
            if source.exists() and destination.exists():
                duplicates.append((source, destination))
    
    return duplicates

def parse_arguments():
    """
    Обрабатывает аргументы командной строки.
    
    Returns:
        argparse.Namespace: Объект с аргументами командной строки
    """
    parser = argparse.ArgumentParser(
        description='Скрипт для перемещения файлов из корневого каталога в структуру проекта',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--mode', 
        choices=['copy', 'move', 'check'], 
        default='copy',
        help='Режим работы: copy - копировать файлы, move - перемещать файлы, check - только проверить'
    )
    
    parser.add_argument(
        '--update-imports', 
        action='store_true',
        help='Обновить импорты в перемещенных файлах'
    )
    
    parser.add_argument(
        '--create-init', 
        action='store_true',
        help='Создать файлы __init__.py в директориях'
    )
    
    parser.add_argument(
        '--find-duplicates', 
        action='store_true',
        help='Найти дублирующиеся файлы'
    )
    
    parser.add_argument(
        '--file-category', 
        choices=list(file_categories.keys()) + ['all'],
        default='all',
        help='Категория файлов для обработки'
    )
    
    return parser.parse_args()

def main():
    """Основная функция скрипта."""
    # Обрабатываем аргументы командной строки
    args = parse_arguments()
    
    # Проверяем существование корневой директории проекта
    if not ROOT_DIR.exists():
        print(f"Ошибка: директория {ROOT_DIR} не найдена.")
        return 1
    
    # Проверяем существование директории проекта
    if not PROJECT_DIR.exists():
        print(f"Ошибка: директория проекта {PROJECT_DIR} не найдена.")
        return 1
    
    # Только поиск дубликатов
    if args.find_duplicates:
        duplicates = find_duplicate_files()
        if duplicates:
            print(f"\nНайдено {len(duplicates)} дублирующихся файлов:")
            for source, dest in duplicates:
                print(f"  {source} <-> {dest}")
        else:
            print("\nДублирующиеся файлы не найдены.")
        return 0
    
    # Обработка в режиме проверки
    if args.mode == 'check':
        print("\nПроверка файлов для перемещения:")
        for category, info in file_categories.items():
            if args.file_category != 'all' and args.file_category != category:
                continue
                
            print(f"\nКатегория: {category}")
            for file_name in info["files"]:
                source = ROOT_DIR / file_name
                destination = info["target_dir"] / file_name
                
                if source.exists():
                    if destination.exists():
                        print(f"  [СУЩЕСТВУЕТ] {file_name}")
                    else:
                        print(f"  [ГОТОВ] {file_name}")
                else:
                    print(f"  [НЕ НАЙДЕН] {file_name}")
        return 0
    
    # Создаем необходимые директории
    for category, info in file_categories.items():
        if args.file_category != 'all' and args.file_category != category:
            continue
            
        ensure_directory_exists(info["target_dir"])
        if args.create_init:
            create_init_files(info["target_dir"])
    
    # Перемещаем файлы
    processed_files = []
    for category, info in file_categories.items():
        if args.file_category != 'all' and args.file_category != category:
            continue
            
        print(f"\nОбработка категории: {category}")
        for file_name in info["files"]:
            source = ROOT_DIR / file_name
            destination = info["target_dir"] / file_name
            
            if source.exists():
                if copy_or_move_file(source, destination, move=(args.mode == 'move')):
                    processed_files.append((source, destination))
            else:
                print(f"Файл не найден: {source}")
    
    # Обновляем импорты в обработанных файлах
    if args.update_imports and processed_files:
        print("\nОбновление импортов в файлах:")
        for original_path, new_path in processed_files:
            update_imports(new_path, original_path)
    
    print("\nОбработка файлов завершена успешно!")
    print(f"Всего обработано файлов: {len(processed_files)}")
    return 0

if __name__ == "__main__":
    sys.exit(main())