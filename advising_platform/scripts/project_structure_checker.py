#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Инструмент для проверки структуры проекта.

Анализирует структуру каталогов и файлов проекта на соответствие стандартам.
Выявляет дублирующиеся файлы, файлы в неправильных местах и другие проблемы.
Часть стандарта ревизии структуры проекта.
"""

import os
import sys
import re
import argparse
import fnmatch
import hashlib
import json
from typing import Dict, List, Set, Tuple, Optional
from pathlib import Path

# Конфигурация структуры проекта
PROJECT_CONFIG = {
    # Основные каталоги проекта
    "base_dirs": [
        "src",
        "scripts",
        "docs",
        "tests",
        "advising standards .md",
        "projects",
        "incidents"
    ],
    
    # Структура src/
    "src_structure": {
        "api": ["__init__.py", "api_client.py", "server_api.py", "webhook_client.py"],
        "cli": ["__init__.py", "abstract_links_tool.py", "add_logical_id.py", "document_cli.py"],
        "core": ["__init__.py", "document_abstractions.py"],
        "utils": ["__init__.py", "compare_structure.py", "convert_links.py", 
                 "generate_pdf.py", "research_documents.py"],
        "web": ["__init__.py", "server.py", "simple_server.py"]
    },
    
    # Структура scripts/
    "scripts_structure": {
        "lib": ["__init__.py", "validation.py"],
        "document_tools": ["__init__.py"]
    },
    
    # Разрешенные Python-файлы в корне
    "allowed_root_py": [
        # В процессе миграции, эти файлы должны быть перемещены
    ],
    
    # Правила для проверки файлов
    "file_rules": {
        "py_file_pattern": r"\.py$",
        "md_file_pattern": r"\.md$",
        "excluded_dirs": ["__pycache__", ".git", "node_modules", ".cache", 
                         ".pythonlibs", "venv", "env", ".uv", ".venv"],
        "excluded_files": [".gitignore", "README.md", ".env", ".env.example"]
    }
}

def calculate_file_hash(file_path: str) -> str:
    """
    Вычисляет хеш MD5 содержимого файла.
    
    Args:
        file_path: Путь к файлу
    
    Returns:
        Строка с MD5-хешем содержимого
    """
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        print(f"Ошибка при вычислении хеша для {file_path}: {e}")
        return ""

def find_files(root_dir: str, pattern: str, excluded_dirs: List[str] = None) -> List[str]:
    """
    Находит файлы, соответствующие шаблону, исключая указанные каталоги.
    
    Args:
        root_dir: Корневой каталог для поиска
        pattern: Регулярное выражение для фильтрации файлов
        excluded_dirs: Список каталогов, которые нужно исключить из поиска
    
    Returns:
        Список путей к найденным файлам
    """
    if excluded_dirs is None:
        excluded_dirs = PROJECT_CONFIG["file_rules"]["excluded_dirs"]
    
    matches = []
    
    for root, dirnames, filenames in os.walk(root_dir):
        # Исключаем указанные каталоги
        dirnames[:] = [d for d in dirnames if d not in excluded_dirs]
        
        for filename in filenames:
            if re.search(pattern, filename):
                matches.append(os.path.join(root, filename))
    
    return matches

def find_duplicates(files: List[str]) -> Dict[str, List[str]]:
    """
    Находит дублирующиеся файлы на основе их содержимого.
    
    Args:
        files: Список путей к файлам для проверки
    
    Returns:
        Словарь, где ключи - хеши файлов, значения - списки путей к дублирующимся файлам
    """
    hashes = {}
    
    for file_path in files:
        file_hash = calculate_file_hash(file_path)
        if file_hash:
            if file_hash in hashes:
                hashes[file_hash].append(file_path)
            else:
                hashes[file_hash] = [file_path]
    
    # Оставляем только группы дубликатов (более одного файла с одинаковым хешем)
    return {h: files for h, files in hashes.items() if len(files) > 1}

def check_python_files_structure(root_dir: str) -> Tuple[List[str], Dict[str, List[str]]]:
    """
    Проверяет структуру Python-файлов в проекте.
    
    Args:
        root_dir: Корневой каталог проекта
    
    Returns:
        Кортеж с двумя элементами:
        - Список Python-файлов в неправильных местах
        - Словарь дублирующихся Python-файлов
    """
    # Находим все Python-файлы
    py_files = find_files(root_dir, PROJECT_CONFIG["file_rules"]["py_file_pattern"])
    
    # Находим дублирующиеся файлы
    duplicates = find_duplicates(py_files)
    
    # Проверяем файлы в неправильных местах
    misplaced_files = []
    
    for file_path in py_files:
        rel_path = os.path.relpath(file_path, root_dir)
        
        # Проверяем Python-файлы в корне
        if "/" not in rel_path and rel_path not in PROJECT_CONFIG["allowed_root_py"]:
            misplaced_files.append(rel_path)
    
    return misplaced_files, duplicates

def check_docs_structure(root_dir: str) -> Tuple[List[str], Dict[str, List[str]]]:
    """
    Проверяет структуру документации в проекте.
    
    Args:
        root_dir: Корневой каталог проекта
    
    Returns:
        Кортеж с двумя элементами:
        - Список документов в неправильных местах
        - Словарь дублирующихся документов
    """
    # Находим все Markdown-файлы
    md_files = find_files(root_dir, PROJECT_CONFIG["file_rules"]["md_file_pattern"])
    
    # Находим дублирующиеся файлы
    duplicates = find_duplicates(md_files)
    
    # Проверяем файлы в неправильных местах
    misplaced_files = []
    
    for file_path in md_files:
        rel_path = os.path.relpath(file_path, root_dir)
        
        # Проверяем Markdown-файлы в корне (кроме README.md и подобных)
        if "/" not in rel_path and rel_path not in PROJECT_CONFIG["file_rules"]["excluded_files"]:
            misplaced_files.append(rel_path)
    
    return misplaced_files, duplicates

def check_base_structure(root_dir: str) -> List[str]:
    """
    Проверяет наличие основных каталогов проекта.
    
    Args:
        root_dir: Корневой каталог проекта
    
    Returns:
        Список отсутствующих основных каталогов
    """
    missing_dirs = []
    
    for base_dir in PROJECT_CONFIG["base_dirs"]:
        dir_path = os.path.join(root_dir, base_dir)
        if not os.path.isdir(dir_path):
            missing_dirs.append(base_dir)
    
    return missing_dirs

def check_src_structure(root_dir: str) -> Tuple[List[str], List[str]]:
    """
    Проверяет структуру каталога src/.
    
    Args:
        root_dir: Корневой каталог проекта
    
    Returns:
        Кортеж с двумя элементами:
        - Список отсутствующих каталогов
        - Список отсутствующих файлов
    """
    src_dir = os.path.join(root_dir, "src")
    if not os.path.isdir(src_dir):
        return ["src"], []
    
    missing_dirs = []
    missing_files = []
    
    for subdir, expected_files in PROJECT_CONFIG["src_structure"].items():
        subdir_path = os.path.join(src_dir, subdir)
        
        if not os.path.isdir(subdir_path):
            missing_dirs.append(f"src/{subdir}")
            continue
        
        for expected_file in expected_files:
            file_path = os.path.join(subdir_path, expected_file)
            if not os.path.isfile(file_path):
                missing_files.append(f"src/{subdir}/{expected_file}")
    
    return missing_dirs, missing_files

def check_scripts_structure(root_dir: str) -> Tuple[List[str], List[str]]:
    """
    Проверяет структуру каталога scripts/.
    
    Args:
        root_dir: Корневой каталог проекта
    
    Returns:
        Кортеж с двумя элементами:
        - Список отсутствующих каталогов
        - Список отсутствующих файлов
    """
    scripts_dir = os.path.join(root_dir, "scripts")
    if not os.path.isdir(scripts_dir):
        return ["scripts"], []
    
    missing_dirs = []
    missing_files = []
    
    for subdir, expected_files in PROJECT_CONFIG["scripts_structure"].items():
        subdir_path = os.path.join(scripts_dir, subdir)
        
        if not os.path.isdir(subdir_path):
            missing_dirs.append(f"scripts/{subdir}")
            continue
        
        for expected_file in expected_files:
            file_path = os.path.join(subdir_path, expected_file)
            if not os.path.isfile(file_path):
                missing_files.append(f"scripts/{subdir}/{expected_file}")
    
    return missing_dirs, missing_files

def generate_report(root_dir: str) -> Dict:
    """
    Генерирует отчет о проверке структуры проекта.
    
    Args:
        root_dir: Корневой каталог проекта
    
    Returns:
        Словарь с результатами проверки
    """
    report = {
        "timestamp": os.popen("date -u +%Y-%m-%dT%H:%M:%SZ").read().strip(),
        "base_structure": {
            "missing_dirs": check_base_structure(root_dir)
        },
        "src_structure": {},
        "scripts_structure": {},
        "python_files": {},
        "docs_structure": {},
        "summary": {}
    }
    
    # Проверка структуры src/
    missing_src_dirs, missing_src_files = check_src_structure(root_dir)
    report["src_structure"] = {
        "missing_dirs": missing_src_dirs,
        "missing_files": missing_src_files
    }
    
    # Проверка структуры scripts/
    missing_scripts_dirs, missing_scripts_files = check_scripts_structure(root_dir)
    report["scripts_structure"] = {
        "missing_dirs": missing_scripts_dirs,
        "missing_files": missing_scripts_files
    }
    
    # Проверка Python-файлов
    misplaced_py_files, duplicate_py_files = check_python_files_structure(root_dir)
    report["python_files"] = {
        "misplaced_files": misplaced_py_files,
        "duplicate_files": {k: v for k, v in duplicate_py_files.items()}
    }
    
    # Проверка структуры документации
    misplaced_docs, duplicate_docs = check_docs_structure(root_dir)
    report["docs_structure"] = {
        "misplaced_files": misplaced_docs,
        "duplicate_files": {k: v for k, v in duplicate_docs.items()}
    }
    
    # Формируем сводку
    issues_count = (
        len(report["base_structure"]["missing_dirs"]) +
        len(report["src_structure"]["missing_dirs"]) +
        len(report["src_structure"]["missing_files"]) +
        len(report["scripts_structure"]["missing_dirs"]) +
        len(report["scripts_structure"]["missing_files"]) +
        len(report["python_files"]["misplaced_files"]) +
        len(report["python_files"]["duplicate_files"]) +
        len(report["docs_structure"]["misplaced_files"]) +
        len(report["docs_structure"]["duplicate_files"])
    )
    
    report["summary"] = {
        "issues_count": issues_count,
        "has_critical_issues": issues_count > 0
    }
    
    return report

def save_report(report: Dict, output_file: str) -> None:
    """
    Сохраняет отчет в JSON-файл.
    
    Args:
        report: Отчет о проверке структуры проекта
        output_file: Путь к файлу для сохранения отчета
    """
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"Отчет сохранен в {output_file}")
    except Exception as e:
        print(f"Ошибка при сохранении отчета: {e}")

def print_report_summary(report: Dict) -> None:
    """
    Выводит краткую сводку отчета.
    
    Args:
        report: Отчет о проверке структуры проекта
    """
    print("\n=== Сводка проверки структуры проекта ===")
    print(f"Всего проблем: {report['summary']['issues_count']}")
    
    if report["base_structure"]["missing_dirs"]:
        print(f"\nОтсутствуют основные каталоги: {len(report['base_structure']['missing_dirs'])}")
        for dir_name in report["base_structure"]["missing_dirs"]:
            print(f"  - {dir_name}")
    
    if report["src_structure"]["missing_dirs"]:
        print(f"\nОтсутствуют каталоги в src/: {len(report['src_structure']['missing_dirs'])}")
        for dir_name in report["src_structure"]["missing_dirs"][:5]:
            print(f"  - {dir_name}")
        if len(report["src_structure"]["missing_dirs"]) > 5:
            print(f"  - ... и еще {len(report['src_structure']['missing_dirs']) - 5}")
    
    if report["python_files"]["misplaced_files"]:
        print(f"\nPython-файлы в неправильных местах: {len(report['python_files']['misplaced_files'])}")
        for file_name in report["python_files"]["misplaced_files"][:5]:
            print(f"  - {file_name}")
        if len(report["python_files"]["misplaced_files"]) > 5:
            print(f"  - ... и еще {len(report['python_files']['misplaced_files']) - 5}")
    
    if report["python_files"]["duplicate_files"]:
        print(f"\nДублирующиеся Python-файлы: {len(report['python_files']['duplicate_files'])}")
        count = 0
        for hash_val, file_list in report["python_files"]["duplicate_files"].items():
            if count >= 3:
                break
            print(f"  - Группа {count + 1}: {', '.join(file_list[:2])}" + 
                  (f" и еще {len(file_list) - 2}" if len(file_list) > 2 else ""))
            count += 1
        if len(report["python_files"]["duplicate_files"]) > 3:
            print(f"  - ... и еще {len(report['python_files']['duplicate_files']) - 3} групп")
    
    if report["docs_structure"]["duplicate_files"]:
        print(f"\nДублирующиеся документы: {len(report['docs_structure']['duplicate_files'])}")
        count = 0
        for hash_val, file_list in report["docs_structure"]["duplicate_files"].items():
            if count >= 3:
                break
            print(f"  - Группа {count + 1}: {', '.join(file_list[:2])}" + 
                  (f" и еще {len(file_list) - 2}" if len(file_list) > 2 else ""))
            count += 1
        if len(report["docs_structure"]["duplicate_files"]) > 3:
            print(f"  - ... и еще {len(report['docs_structure']['duplicate_files']) - 3} групп")
    
    print("\nДля полной информации смотрите отчет в формате JSON.")

def main():
    """Основная функция."""
    parser = argparse.ArgumentParser(description="Проверка структуры проекта")
    parser.add_argument("--root-dir", default=".", help="Корневой каталог проекта")
    parser.add_argument("--output", default="project_structure_report.json", 
                        help="Путь для сохранения отчета")
    parser.add_argument("--verbose", action="store_true", help="Подробный вывод")
    args = parser.parse_args()
    
    print(f"Проверка структуры проекта в {args.root_dir}")
    
    # Генерируем отчет
    report = generate_report(args.root_dir)
    
    # Сохраняем отчет
    save_report(report, args.output)
    
    # Выводим сводку
    print_report_summary(report)
    
    # Выводим подробную информацию, если запрошено
    if args.verbose:
        print("\n=== Подробный отчет ===")
        print(json.dumps(report, ensure_ascii=False, indent=2))
    
    # Возвращаем статус выхода
    return 0 if report["summary"]["issues_count"] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())