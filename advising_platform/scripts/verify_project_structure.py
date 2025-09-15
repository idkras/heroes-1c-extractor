#!/usr/bin/env python3
"""
Скрипт для верификации структуры проектов.
Проверяет наличие всех необходимых файлов и соответствие стандартам именования.
"""

import os
import re
import sys
import argparse
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from datetime import datetime

# Определение типов файлов
REQUIRED_FILES = {
    "context": {
        "pattern": r"^([a-zA-Z0-9\.-]+\.(context)\.md|[a-zA-Z0-9\.-]+\.context\.md)$",
        "example": "domain.context.md",
        "description": "Контекст проекта",
        "required": True
    },
    # В проектах не должно быть next_actions.md
    # next_actions.md должен быть только в корне projects/
    "architecture": {
        "pattern": r"^[a-zA-Z0-9\.-]+_(architecture)\.md$",
        "example": "domain_architecture.md",
        "description": "Архитектура проекта",
        "required": False
    },
    "requirements": {
        "pattern": r"^[a-zA-Z0-9\.-]+_(requirements)\.md$",
        "example": "domain_requirements.md",
        "description": "Требования к проекту",
        "required": False
    },
    "metrics": {
        "pattern": r"^[a-zA-Z0-9\.-]+_(metrics)\.md$",
        "example": "domain_metrics.md",
        "description": "Метрики проекта",
        "required": False
    }
}

# Обязательные разделы в файлах
REQUIRED_SECTIONS = {
    "context": [
        "# ",  # Заголовок
        "updated:",
        "version:",
        "status:",
        "## 🎯 Цели проекта",
        "## 🧩 Текущий контекст и проблемы",
        "## 📊 Ожидаемые результаты",
        "## 🔄 Next Actions"
    ],
    "next_actions": [
        "# ",  # Заголовок
        "updated:",
        "version:",
        "status:",
        "## 📋 Активные задачи и следующие действия",
        "## 📊 Ожидаемые результаты"
    ]
}

def check_file_existence(project_dir: Path) -> Dict[str, List[str]]:
    """
    Проверяет наличие всех необходимых файлов в директории проекта.
    
    Args:
        project_dir: Путь к директории проекта
    
    Returns:
        Словарь с результатами проверки:
        {
            "missing": [список отсутствующих обязательных файлов],
            "incorrect_naming": [список файлов с неправильным именованием],
            "found": [список найденных файлов],
            "optional_missing": [список отсутствующих опциональных файлов]
        }
    """
    results = {
        "missing": [],
        "incorrect_naming": [],
        "found": [],
        "optional_missing": []
    }
    
    # Получение списка файлов в директории
    files = [f.name for f in project_dir.iterdir() if f.is_file() and f.suffix == '.md']
    
    # Проверка наличия каждого типа файла
    for file_type, file_info in REQUIRED_FILES.items():
        pattern = re.compile(file_info["pattern"])
        found = False
        
        for file in files:
            if pattern.match(file):
                results["found"].append((file, file_type))
                found = True
                break
        
        if not found:
            if file_info["required"]:
                results["missing"].append((file_info["example"], file_type))
            else:
                results["optional_missing"].append((file_info["example"], file_type))
    
    # Проверка на наличие файлов .md, не соответствующих стандартам именования
    for file in files:
        valid = False
        for file_type, file_info in REQUIRED_FILES.items():
            pattern = re.compile(file_info["pattern"])
            if pattern.match(file):
                valid = True
                break
        
        if not valid:
            results["incorrect_naming"].append(file)
    
    return results

def check_file_content(file_path: Path, file_type: str) -> Dict[str, List[str]]:
    """
    Проверяет содержимое файла на наличие всех необходимых разделов.
    
    Args:
        file_path: Путь к файлу
        file_type: Тип файла (context, next_actions, etc.)
    
    Returns:
        Словарь с результатами проверки:
        {
            "missing_sections": [список отсутствующих разделов],
            "found_sections": [список найденных разделов]
        }
    """
    results = {
        "missing_sections": [],
        "found_sections": []
    }
    
    if file_type not in REQUIRED_SECTIONS:
        return results
    
    # Чтение содержимого файла
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Ошибка при чтении файла {file_path}: {str(e)}")
        return results
    
    # Проверка наличия каждого обязательного раздела
    for section in REQUIRED_SECTIONS[file_type]:
        if section in content:
            results["found_sections"].append(section)
        else:
            results["missing_sections"].append(section)
    
    return results

def check_project_structure(project_dir) -> Dict:
    """
    Проверяет структуру проекта на соответствие стандартам.
    
    Args:
        project_dir: Путь к директории проекта
    
    Returns:
        Словарь с результатами проверки
    """
    project_path = Path(project_dir) if isinstance(project_dir, str) else project_dir
    if not project_path.exists() or not project_path.is_dir():
        return {"error": f"Директория {project_dir} не существует"}
    
    results = {
        "project": project_dir,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "files": check_file_existence(project_path),
        "content": {}
    }
    
    # Проверка содержимого найденных файлов
    for file, file_type in results["files"]["found"]:
        file_path = project_path / file
        results["content"][file] = check_file_content(file_path, file_type)
    
    return results

def check_root_next_actions(projects_dir: Path) -> Dict:
    """
    Проверяет наличие и правильность next_actions.md в корне директории projects/
    
    Args:
        projects_dir: Путь к директории projects
    
    Returns:
        Словарь с результатами проверки
    """
    results = {
        "exists": False,
        "next_actions_in_projects": []
    }
    
    # Проверка наличия next_actions.md в корне
    root_next_actions = projects_dir / "next_actions.md"
    if root_next_actions.exists() and root_next_actions.is_file():
        results["exists"] = True
    
    # Поиск next_actions.md в папках проектов
    for project_dir in [d for d in projects_dir.iterdir() if d.is_dir()]:
        next_actions_file = project_dir / "next_actions.md"
        if next_actions_file.exists() and next_actions_file.is_file():
            results["next_actions_in_projects"].append(str(next_actions_file))
    
    return results
    
def print_report(results: Dict, verbose: bool = False):
    """
    Выводит отчет о проверке структуры проекта.
    
    Args:
        results: Результаты проверки
        verbose: Подробный вывод
    """
    project = results["project"]
    files = results["files"]
    content = results["content"]
    
    print(f"\n{'='*40}")
    print(f"Отчет о проверке проекта: {project}")
    print(f"Дата проверки: {results['timestamp']}")
    print(f"{'='*40}\n")
    
    # Вывод информации о файлах
    print(f"1. Проверка наличия файлов\n{'-'*30}")
    
    if not files["missing"] and not files["incorrect_naming"]:
        print("✅ Все обязательные файлы присутствуют и соответствуют стандартам именования.")
    else:
        if files["missing"]:
            print("❌ Отсутствуют обязательные файлы:")
            for file, file_type in files["missing"]:
                print(f"   - {file} ({REQUIRED_FILES[file_type]['description']})")
        
        if files["incorrect_naming"]:
            print("⚠️ Файлы с неправильным именованием:")
            for file in files["incorrect_naming"]:
                print(f"   - {file}")
    
    if verbose and files["optional_missing"]:
        print("\n⚠️ Отсутствуют опциональные файлы:")
        for file, file_type in files["optional_missing"]:
            print(f"   - {file} ({REQUIRED_FILES[file_type]['description']})")
    
    if verbose and files["found"]:
        print("\n✅ Найденные файлы:")
        for file, file_type in files["found"]:
            print(f"   - {file} ({REQUIRED_FILES[file_type]['description']})")
    
    # Вывод информации о содержимом файлов
    print(f"\n2. Проверка содержимого файлов\n{'-'*30}")
    
    if not content:
        print("❓ Нет файлов для проверки содержимого.")
    else:
        all_sections_present = True
        
        for file, file_results in content.items():
            missing_sections = file_results.get("missing_sections", [])
            
            if missing_sections:
                all_sections_present = False
                print(f"❌ В файле {file} отсутствуют обязательные разделы:")
                for section in missing_sections:
                    print(f"   - {section}")
            elif verbose:
                print(f"✅ Файл {file} содержит все необходимые разделы.")
        
        if all_sections_present and not verbose:
            print("✅ Все файлы содержат необходимые разделы.")
    
    # Общий вывод
    print(f"\n3. Итоговая оценка\n{'-'*30}")
    
    if not files["missing"] and not files["incorrect_naming"] and all(not file_results.get("missing_sections", []) for file_results in content.values()):
        print("✅ Структура проекта полностью соответствует стандартам.")
    else:
        print("⚠️ Структура проекта требует доработки.")

def main():
    parser = argparse.ArgumentParser(description='Проверка структуры проектов')
    parser.add_argument('projects', nargs='*', help='Директории проектов для проверки (по умолчанию все проекты в директории projects)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Подробный вывод')
    parser.add_argument('--check-root', action='store_true', help='Проверить структуру корневой директории projects/')
    args = parser.parse_args()
    
    projects_dir = Path('projects')
    if not projects_dir.exists() or not projects_dir.is_dir():
        print("Ошибка: директория projects не существует.")
        return 1
    
    # Проверка корневых файлов
    if args.check_root:
        root_check = check_root_next_actions(projects_dir)
        print(f"\n{'='*40}")
        print(f"Проверка корневых файлов в projects/")
        print(f"{'='*40}\n")
        
        if root_check["exists"]:
            print("✅ Файл next_actions.md существует в корне projects/")
        else:
            print("❌ Файл next_actions.md ОТСУТСТВУЕТ в корне projects/")
        
        if root_check["next_actions_in_projects"]:
            print("\n⚠️ Обнаружены next_actions.md внутри директорий проектов (должны быть удалены):")
            for file_path in root_check["next_actions_in_projects"]:
                print(f"   - {file_path}")
        else:
            print("\n✅ Нет next_actions.md внутри директорий проектов")
        print("\n")
    
    # Проверка проектов
    if not args.projects:
        projects = [p for p in projects_dir.iterdir() if p.is_dir()]
    else:
        projects = [Path(p) for p in args.projects]
    
    if not projects:
        print("Не найдено проектов для проверки.")
        return 1
    
    for project in projects:
        results = check_project_structure(project)
        if "error" in results:
            print(f"Ошибка: {results['error']}")
            continue
        
        print_report(results, args.verbose)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())