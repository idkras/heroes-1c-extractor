"""
Скрипт для проверки дублирующих файлов задач и инцидентов.
Также проверяет архивные файлы стандартов.

Автор: AI Assistant
Дата: 20 мая 2025
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Set

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("duplicate_checker")

# Пути к директориям
STANDARDS_DIR = "[standards .md]"
TASKS_DIR = "projects/tasks"
INCIDENTS_DIR = "[todo · incidents]/ai.incidents"
TODO_FILE = "[todo · incidents]/todo.md"
AI_INCIDENTS_FILE = "[todo · incidents]/ai.incidents.md"
REGISTRY_FILE = "registry.json"

def load_registry() -> Dict:
    """
    Загружает реестр задач и инцидентов.
    
    Returns:
        Dict: Реестр задач и инцидентов
    """
    if os.path.exists(REGISTRY_FILE):
        try:
            with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка при загрузке реестра: {e}")
    
    return {}

def check_tasks_in_todo_vs_files() -> Tuple[int, List[str], List[str]]:
    """
    Проверяет соответствие между задачами в todo.md и отдельными файлами задач.
    
    Returns:
        Tuple: Количество задач в todo.md, список задач, найденных только в todo.md,
               список задач, найденных только в отдельных файлах
    """
    print("\n=== ПРОВЕРКА ЗАДАЧ В TODO.MD И ОТДЕЛЬНЫХ ФАЙЛАХ ===")
    
    # Получаем задачи из todo.md
    todo_tasks = []
    if os.path.exists(TODO_FILE):
        try:
            with open(TODO_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Ищем задачи по формату "- [ ]" или "- [x]"
                task_pattern = r'- \[([ x])\] \*\*([^*]+)\*\*'
                matches = re.findall(task_pattern, content)
                
                for status, title in matches:
                    todo_tasks.append({
                        "title": title.strip(),
                        "status": "done" if status == "x" else "open",
                        "in_todo": True
                    })
        except Exception as e:
            logger.error(f"Ошибка при чтении todo.md: {e}")
    
    # Получаем задачи из отдельных файлов
    file_tasks = []
    if os.path.exists(TASKS_DIR):
        try:
            for file_path in Path(TASKS_DIR).glob("*.md"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    
                    # Извлекаем заголовок (первая строка, начинающаяся с #)
                    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
                    if title_match:
                        title = title_match.group(1).strip()
                        file_tasks.append({
                            "title": title,
                            "path": str(file_path),
                            "in_file": True
                        })
        except Exception as e:
            logger.error(f"Ошибка при чтении файлов задач: {e}")
    
    # Находим задачи, которые есть только в todo.md
    only_in_todo = []
    for todo_task in todo_tasks:
        found = False
        for file_task in file_tasks:
            if todo_task["title"].lower() in file_task["title"].lower() or file_task["title"].lower() in todo_task["title"].lower():
                found = True
                break
        
        if not found:
            only_in_todo.append(todo_task["title"])
    
    # Находим задачи, которые есть только в отдельных файлах
    only_in_files = []
    for file_task in file_tasks:
        found = False
        for todo_task in todo_tasks:
            if todo_task["title"].lower() in file_task["title"].lower() or file_task["title"].lower() in todo_task["title"].lower():
                found = True
                break
        
        if not found:
            only_in_files.append((file_task["title"], file_task["path"]))
    
    # Выводим результаты
    print(f"Всего задач в todo.md: {len(todo_tasks)}")
    print(f"Всего задач в отдельных файлах: {len(file_tasks)}")
    
    print(f"\nЗадачи, которые есть только в todo.md: {len(only_in_todo)}")
    for i, task in enumerate(only_in_todo[:10], 1):
        print(f"  {i}. {task}")
    
    if len(only_in_todo) > 10:
        print(f"  ... и еще {len(only_in_todo) - 10} задач")
    
    print(f"\nЗадачи, которые есть только в отдельных файлах: {len(only_in_files)}")
    for i, (task, path) in enumerate(only_in_files[:10], 1):
        print(f"  {i}. {task} - {path}")
    
    if len(only_in_files) > 10:
        print(f"  ... и еще {len(only_in_files) - 10} задач")
    
    return len(todo_tasks), only_in_todo, [f[0] for f in only_in_files]

def check_incidents_in_file_vs_directories() -> Tuple[int, List[str], List[str]]:
    """
    Проверяет соответствие между инцидентами в ai.incidents.md и отдельными файлами инцидентов.
    
    Returns:
        Tuple: Количество инцидентов в ai.incidents.md, список инцидентов, найденных только в ai.incidents.md,
               список инцидентов, найденных только в отдельных файлах
    """
    print("\n=== ПРОВЕРКА ИНЦИДЕНТОВ В AI.INCIDENTS.MD И ОТДЕЛЬНЫХ ФАЙЛАХ ===")
    
    # Получаем инциденты из ai.incidents.md
    file_incidents = []
    if os.path.exists(AI_INCIDENTS_FILE):
        try:
            with open(AI_INCIDENTS_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Ищем инциденты по формату "## YYYY-MM-DD - Название инцидента"
                incident_pattern = r'## (\d{4}-\d{2}-\d{2}) - ([^\n]+)'
                matches = re.findall(incident_pattern, content)
                
                for date, title in matches:
                    file_incidents.append({
                        "title": title.strip(),
                        "date": date,
                        "in_file": True
                    })
        except Exception as e:
            logger.error(f"Ошибка при чтении ai.incidents.md: {e}")
    
    # Получаем инциденты из отдельных файлов
    dir_incidents = []
    if os.path.exists(INCIDENTS_DIR):
        try:
            for file_path in Path(INCIDENTS_DIR).glob("*.md"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    
                    # Извлекаем заголовок (первая строка, начинающаяся с #)
                    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
                    if title_match:
                        title = title_match.group(1).strip()
                        dir_incidents.append({
                            "title": title,
                            "path": str(file_path),
                            "in_dir": True
                        })
        except Exception as e:
            logger.error(f"Ошибка при чтении файлов инцидентов: {e}")
    
    # Находим инциденты, которые есть только в ai.incidents.md
    only_in_file = []
    for file_incident in file_incidents:
        found = False
        for dir_incident in dir_incidents:
            if file_incident["title"].lower() in dir_incident["title"].lower() or dir_incident["title"].lower() in file_incident["title"].lower():
                found = True
                break
        
        if not found:
            only_in_file.append(file_incident["title"])
    
    # Находим инциденты, которые есть только в отдельных файлах
    only_in_dir = []
    for dir_incident in dir_incidents:
        found = False
        for file_incident in file_incidents:
            if file_incident["title"].lower() in dir_incident["title"].lower() or dir_incident["title"].lower() in file_incident["title"].lower():
                found = True
                break
        
        if not found:
            only_in_dir.append((dir_incident["title"], dir_incident["path"]))
    
    # Выводим результаты
    print(f"Всего инцидентов в ai.incidents.md: {len(file_incidents)}")
    print(f"Всего инцидентов в отдельных файлах: {len(dir_incidents)}")
    
    print(f"\nИнциденты, которые есть только в ai.incidents.md: {len(only_in_file)}")
    for i, incident in enumerate(only_in_file[:10], 1):
        print(f"  {i}. {incident}")
    
    if len(only_in_file) > 10:
        print(f"  ... и еще {len(only_in_file) - 10} инцидентов")
    
    print(f"\nИнциденты, которые есть только в отдельных файлах: {len(only_in_dir)}")
    for i, (incident, path) in enumerate(only_in_dir[:10], 1):
        print(f"  {i}. {incident} - {path}")
    
    if len(only_in_dir) > 10:
        print(f"  ... и еще {len(only_in_dir) - 10} инцидентов")
    
    return len(file_incidents), only_in_file, [i[0] for i in only_in_dir]

def check_duplicate_tasks() -> List[Tuple[str, List[str]]]:
    """
    Проверяет наличие дублирующихся задач.
    
    Returns:
        List[Tuple[str, List[str]]]: Список дублирующихся задач с их путями
    """
    print("\n=== ПРОВЕРКА ДУБЛИРУЮЩИХСЯ ЗАДАЧ ===")
    
    # Получаем все задачи из отдельных файлов
    tasks = {}
    duplicates = []
    
    if os.path.exists(TASKS_DIR):
        try:
            for file_path in Path(TASKS_DIR).glob("*.md"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    
                    # Извлекаем заголовок
                    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
                    if title_match:
                        title = title_match.group(1).strip()
                        
                        # Проверяем, есть ли уже такая задача
                        title_lower = title.lower()
                        if title_lower in tasks:
                            # Добавляем путь к списку путей для этого заголовка
                            tasks[title_lower].append(str(file_path))
                        else:
                            tasks[title_lower] = [str(file_path)]
        except Exception as e:
            logger.error(f"Ошибка при чтении файлов задач: {e}")
    
    # Находим дублирующиеся задачи
    for title, paths in tasks.items():
        if len(paths) > 1:
            duplicates.append((title, paths))
    
    # Выводим результаты
    if duplicates:
        print(f"Найдено {len(duplicates)} дублирующихся задач:")
        for i, (title, paths) in enumerate(duplicates, 1):
            print(f"  {i}. {title}:")
            for path in paths:
                print(f"     - {path}")
    else:
        print("Дублирующихся задач не найдено.")
    
    return duplicates

def check_duplicate_incidents() -> List[Tuple[str, List[str]]]:
    """
    Проверяет наличие дублирующихся инцидентов.
    
    Returns:
        List[Tuple[str, List[str]]]: Список дублирующихся инцидентов с их путями
    """
    print("\n=== ПРОВЕРКА ДУБЛИРУЮЩИХСЯ ИНЦИДЕНТОВ ===")
    
    # Получаем все инциденты из отдельных файлов
    incidents = {}
    duplicates = []
    
    if os.path.exists(INCIDENTS_DIR):
        try:
            for file_path in Path(INCIDENTS_DIR).glob("*.md"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    
                    # Извлекаем заголовок
                    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
                    if title_match:
                        title = title_match.group(1).strip()
                        
                        # Проверяем, есть ли уже такой инцидент
                        title_lower = title.lower()
                        if title_lower in incidents:
                            # Добавляем путь к списку путей для этого заголовка
                            incidents[title_lower].append(str(file_path))
                        else:
                            incidents[title_lower] = [str(file_path)]
        except Exception as e:
            logger.error(f"Ошибка при чтении файлов инцидентов: {e}")
    
    # Находим дублирующиеся инциденты
    for title, paths in incidents.items():
        if len(paths) > 1:
            duplicates.append((title, paths))
    
    # Выводим результаты
    if duplicates:
        print(f"Найдено {len(duplicates)} дублирующихся инцидентов:")
        for i, (title, paths) in enumerate(duplicates, 1):
            print(f"  {i}. {title}:")
            for path in paths:
                print(f"     - {path}")
    else:
        print("Дублирующихся инцидентов не найдено.")
    
    return duplicates

def check_archive_standards() -> Tuple[int, int, List[str]]:
    """
    Проверяет архивные стандарты и подсчитывает количество активных стандартов.
    
    Returns:
        Tuple: Количество активных стандартов, количество архивных стандартов, список архивных директорий
    """
    print("\n=== ПРОВЕРКА АРХИВНЫХ СТАНДАРТОВ ===")
    
    # Счетчики стандартов
    active_standards = 0
    archive_standards = 0
    archive_dirs = []
    
    # Рекурсивная функция для подсчета файлов в директории
    def count_files_recursively(path, is_archive=False):
        nonlocal active_standards, archive_standards
        
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            
            if os.path.isdir(item_path):
                # Проверяем, является ли директория архивной
                is_dir_archive = is_archive or item.lower() in ["archive", "[archive]", "архив", "архивные", "old", "backup", "backups", "rename_backups"]
                
                if is_dir_archive and not any(a == item_path for a in archive_dirs):
                    archive_dirs.append(item_path)
                
                # Рекурсивно обрабатываем поддиректорию
                count_files_recursively(item_path, is_dir_archive)
            elif os.path.isfile(item_path) and item_path.endswith(".md"):
                # Подсчитываем стандарты
                if is_archive:
                    archive_standards += 1
                else:
                    active_standards += 1
    
    # Подсчитываем стандарты
    if os.path.exists(STANDARDS_DIR):
        count_files_recursively(STANDARDS_DIR)
    
    # Выводим результаты
    print(f"Всего активных стандартов: {active_standards}")
    print(f"Всего архивных стандартов: {archive_standards}")
    
    print("\nАрхивные директории:")
    for i, dir_path in enumerate(archive_dirs, 1):
        print(f"  {i}. {dir_path}")
    
    return active_standards, archive_standards, archive_dirs

def suggest_actions(
    todo_tasks: int,
    only_in_todo: List[str],
    only_in_task_files: List[str],
    incidents_in_file: int,
    only_in_incidents_file: List[str],
    only_in_incident_files: List[str],
    duplicate_tasks: List[Tuple[str, List[str]]],
    duplicate_incidents: List[Tuple[str, List[str]]],
    active_standards: int,
    archive_standards: int
) -> None:
    """
    Предлагает действия на основе результатов проверки.
    
    Args:
        todo_tasks: Количество задач в todo.md
        only_in_todo: Список задач, найденных только в todo.md
        only_in_task_files: Список задач, найденных только в отдельных файлах
        incidents_in_file: Количество инцидентов в ai.incidents.md
        only_in_incidents_file: Список инцидентов, найденных только в ai.incidents.md
        only_in_incident_files: Список инцидентов, найденных только в отдельных файлах
        duplicate_tasks: Список дублирующихся задач
        duplicate_incidents: Список дублирующихся инцидентов
        active_standards: Количество активных стандартов
        archive_standards: Количество архивных стандартов
    """
    print("\n" + "="*80)
    print("РЕКОМЕНДУЕМЫЕ ДЕЙСТВИЯ")
    print("="*80)
    
    # Обработка задач
    if only_in_task_files:
        print("\n1. Задачи, которые нужно добавить в todo.md:")
        for i, task in enumerate(only_in_task_files[:5], 1):
            print(f"  {i}. {task}")
        if len(only_in_task_files) > 5:
            print(f"  ... и еще {len(only_in_task_files) - 5} задач")
    
    if duplicate_tasks:
        print("\n2. Задачи, требующие дедупликации:")
        for i, (title, paths) in enumerate(duplicate_tasks, 1):
            print(f"  {i}. {title}")
        print("  Рекомендуется оставить только по одному файлу для каждой задачи")
    
    # Обработка инцидентов
    if only_in_incident_files:
        print("\n3. Инциденты, которые нужно добавить в ai.incidents.md:")
        for i, incident in enumerate(only_in_incident_files[:5], 1):
            print(f"  {i}. {incident}")
        if len(only_in_incident_files) > 5:
            print(f"  ... и еще {len(only_in_incident_files) - 5} инцидентов")
    
    if duplicate_incidents:
        print("\n4. Инциденты, требующие дедупликации:")
        for i, (title, paths) in enumerate(duplicate_incidents, 1):
            print(f"  {i}. {title}")
        print("  Рекомендуется оставить только по одному файлу для каждого инцидента")
    
    # Обработка стандартов
    if active_standards > 40:
        print(f"\n5. Слишком много активных стандартов: {active_standards}")
        print("  Рекомендуется проверить стандарты и архивировать устаревшие")
        print("  Оптимальное количество активных стандартов: не более 40")
    
    print("\n" + "="*80)

def main():
    """
    Основная функция скрипта.
    """
    print("\n" + "="*80)
    print("ПРОВЕРКА ДУБЛИРУЮЩИХ ФАЙЛОВ ЗАДАЧ И ИНЦИДЕНТОВ")
    print("="*80)
    
    # Проверяем реестр
    registry = load_registry()
    print(f"Записей в реестре: {len(registry)}")
    
    # Проверяем задачи в todo.md и отдельных файлах
    todo_tasks, only_in_todo, only_in_task_files = check_tasks_in_todo_vs_files()
    
    # Проверяем инциденты в ai.incidents.md и отдельных файлах
    incidents_in_file, only_in_incidents_file, only_in_incident_files = check_incidents_in_file_vs_directories()
    
    # Проверяем дублирующиеся задачи
    duplicate_tasks = check_duplicate_tasks()
    
    # Проверяем дублирующиеся инциденты
    duplicate_incidents = check_duplicate_incidents()
    
    # Проверяем архивные стандарты
    active_standards, archive_standards, archive_dirs = check_archive_standards()
    
    # Предлагаем действия
    suggest_actions(
        todo_tasks,
        only_in_todo,
        only_in_task_files,
        incidents_in_file,
        only_in_incidents_file,
        only_in_incident_files,
        duplicate_tasks,
        duplicate_incidents,
        active_standards,
        archive_standards
    )

if __name__ == "__main__":
    main()