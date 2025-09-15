#!/usr/bin/env python3
"""
Скрипт для консолидации оставшихся задач и инцидентов из отдельных файлов в основные файлы.
Находит и архивирует дубликаты файлов.

Автор: AI Assistant
Дата: 21 мая 2025
"""

import os
import re
import shutil
import logging
import hashlib
from typing import List, Dict, Tuple, Set, Any
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='consolidate_remaining.log'
)
logger = logging.getLogger(__name__)

# Пути к файлам
TODO_FILE = "todo/todo.md"
INCIDENTS_FILE = "incidents/ai.incidents.md"
ARCHIVE_DIR = "archive"
TASKS_DIR = "todo"
INCIDENTS_DIR = "incidents"

def ensure_dir_exists(directory: str) -> None:
    """Создает директорию, если она не существует."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Создана директория: {directory}")

def get_file_hash(file_path: str) -> str:
    """Вычисляет хеш содержимого файла."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def find_duplicate_files(directory: str) -> Dict[str, List[str]]:
    """
    Находит дубликаты файлов в указанной директории.
    
    Args:
        directory: Путь к директории
    
    Returns:
        Словарь {хеш: список путей к файлам}
    """
    hashes: Dict[str, List[str]] = {}
    
    for root, _, files in os.walk(directory):
        for filename in files:
            if not filename.endswith(".md"):
                continue
                
            file_path = os.path.join(root, filename)
            file_hash = get_file_hash(file_path)
            
            if file_hash not in hashes:
                hashes[file_hash] = []
            
            hashes[file_hash].append(file_path)
    
    # Оставляем только хеши с более чем одним файлом
    return {h: files for h, files in hashes.items() if len(files) > 1}

def find_tasks_incidents_files() -> Tuple[List[str], List[str]]:
    """
    Находит файлы задач и инцидентов вне основных файлов.
    
    Returns:
        Кортеж (список файлов задач, список файлов инцидентов)
    """
    task_files = []
    incident_files = []
    
    # Ищем файлы задач
    for root, _, files in os.walk("."):
        # Пропускаем директории .git, node_modules, __pycache__ и т.д.
        if any(ignore in root for ignore in [".git", "node_modules", "__pycache__", ARCHIVE_DIR]):
            continue
            
        for filename in files:
            if not filename.endswith(".md"):
                continue
                
            file_path = os.path.join(root, filename)
            
            # Пропускаем основные файлы
            if file_path == TODO_FILE or file_path == INCIDENTS_FILE:
                continue
                
            # Читаем файл и определяем его тип
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                
                # Проверяем, является ли файл задачей или инцидентом
                if "# Задача:" in content or "# Task:" in content:
                    task_files.append(file_path)
                elif "# Инцидент:" in content or "# Incident:" in content:
                    incident_files.append(file_path)
    
    return task_files, incident_files

def extract_task_info(file_path: str) -> Dict[str, str]:
    """
    Извлекает информацию о задаче из файла.
    
    Args:
        file_path: Путь к файлу задачи
    
    Returns:
        Словарь с информацией о задаче
    """
    task_info = {"file_path": file_path}
    
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        
        # Извлекаем название задачи
        title_match = re.search(r"# Задача:(.+)|# Task:(.+)", content)
        if title_match:
            task_info["title"] = (title_match.group(1) or title_match.group(2)).strip()
        else:
            task_info["title"] = os.path.basename(file_path)
        
        # Извлекаем статус задачи
        status_match = re.search(r"Статус:(.+)|Status:(.+)", content)
        if status_match:
            task_info["status"] = (status_match.group(1) or status_match.group(2)).strip()
        else:
            task_info["status"] = "Не начато"
        
        # Извлекаем описание задачи
        task_info["content"] = content
    
    return task_info

def extract_incident_info(file_path: str) -> Dict[str, str]:
    """
    Извлекает информацию об инциденте из файла.
    
    Args:
        file_path: Путь к файлу инцидента
    
    Returns:
        Словарь с информацией об инциденте
    """
    incident_info = {"file_path": file_path}
    
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        
        # Извлекаем название инцидента
        title_match = re.search(r"# Инцидент:(.+)|# Incident:(.+)", content)
        if title_match:
            incident_info["title"] = (title_match.group(1) or title_match.group(2)).strip()
        else:
            incident_info["title"] = os.path.basename(file_path)
        
        # Извлекаем статус инцидента
        status_match = re.search(r"Статус:(.+)|Status:(.+)", content)
        if status_match:
            incident_info["status"] = (status_match.group(1) or status_match.group(2)).strip()
        else:
            incident_info["status"] = "Открыт"
        
        # Извлекаем описание инцидента
        incident_info["content"] = content
    
    return incident_info

def consolidate_tasks(task_files: List[str]) -> int:
    """
    Консолидирует задачи из отдельных файлов в основной файл todo.md.
    
    Args:
        task_files: Список путей к файлам задач
    
    Returns:
        Количество консолидированных задач
    """
    # Создаем директорию для архивации
    archive_dir = os.path.join(ARCHIVE_DIR, "tasks")
    ensure_dir_exists(archive_dir)
    
    # Загружаем основной файл задач
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r", encoding="utf-8", errors="ignore") as f:
            todo_content = f.read()
    else:
        todo_content = "# Задачи\n\n"
        ensure_dir_exists(os.path.dirname(TODO_FILE))
    
    count = 0
    
    # Проходим по всем файлам задач
    for file_path in task_files:
        try:
            # Извлекаем информацию о задаче
            task_info = extract_task_info(file_path)
            
            # Проверяем, есть ли эта задача уже в основном файле
            if f"# Задача: {task_info['title']}" in todo_content or f"# Task: {task_info['title']}" in todo_content:
                logger.info(f"Задача '{task_info['title']}' уже существует в основном файле. Архивируем {file_path}")
            else:
                # Добавляем задачу в основной файл
                todo_content += f"\n\n## {task_info['title']}\n\n{task_info['content']}\n\n"
                count += 1
                logger.info(f"Добавлена задача '{task_info['title']}' из файла {file_path}")
            
            # Архивируем файл
            archive_path = os.path.join(archive_dir, os.path.basename(file_path))
            shutil.move(file_path, archive_path)
            logger.info(f"Файл {file_path} перемещен в {archive_path}")
        except Exception as e:
            logger.error(f"Ошибка при обработке файла {file_path}: {e}")
    
    # Сохраняем обновленный основной файл
    with open(TODO_FILE, "w", encoding="utf-8") as f:
        f.write(todo_content)
    
    return count

def consolidate_incidents(incident_files: List[str]) -> int:
    """
    Консолидирует инциденты из отдельных файлов в основной файл ai.incidents.md.
    
    Args:
        incident_files: Список путей к файлам инцидентов
    
    Returns:
        Количество консолидированных инцидентов
    """
    # Создаем директорию для архивации
    archive_dir = os.path.join(ARCHIVE_DIR, "incidents")
    ensure_dir_exists(archive_dir)
    
    # Загружаем основной файл инцидентов
    if os.path.exists(INCIDENTS_FILE):
        with open(INCIDENTS_FILE, "r", encoding="utf-8", errors="ignore") as f:
            incidents_content = f.read()
    else:
        incidents_content = "# Инциденты\n\n"
        ensure_dir_exists(os.path.dirname(INCIDENTS_FILE))
    
    count = 0
    
    # Проходим по всем файлам инцидентов
    for file_path in incident_files:
        try:
            # Извлекаем информацию об инциденте
            incident_info = extract_incident_info(file_path)
            
            # Проверяем, есть ли этот инцидент уже в основном файле
            if f"# Инцидент: {incident_info['title']}" in incidents_content or f"# Incident: {incident_info['title']}" in incidents_content:
                logger.info(f"Инцидент '{incident_info['title']}' уже существует в основном файле. Архивируем {file_path}")
            else:
                # Добавляем инцидент в основной файл
                incidents_content += f"\n\n## {incident_info['title']}\n\n{incident_info['content']}\n\n"
                count += 1
                logger.info(f"Добавлен инцидент '{incident_info['title']}' из файла {file_path}")
            
            # Архивируем файл
            archive_path = os.path.join(archive_dir, os.path.basename(file_path))
            shutil.move(file_path, archive_path)
            logger.info(f"Файл {file_path} перемещен в {archive_path}")
        except Exception as e:
            logger.error(f"Ошибка при обработке файла {file_path}: {e}")
    
    # Сохраняем обновленный основной файл
    with open(INCIDENTS_FILE, "w", encoding="utf-8") as f:
        f.write(incidents_content)
    
    return count

def archive_duplicates(duplicates: Dict[str, List[str]]) -> int:
    """
    Архивирует дубликаты файлов.
    
    Args:
        duplicates: Словарь {хеш: список путей к файлам}
    
    Returns:
        Количество архивированных файлов
    """
    # Создаем директорию для архивации
    archive_dir = os.path.join(ARCHIVE_DIR, "duplicates")
    ensure_dir_exists(archive_dir)
    
    count = 0
    
    # Проходим по всем группам дубликатов
    for file_hash, files in duplicates.items():
        # Оставляем первый файл
        original = files[0]
        
        # Архивируем остальные файлы
        for file_path in files[1:]:
            try:
                # Создаем уникальное имя файла для архивации
                base_name = os.path.basename(file_path)
                dir_name = os.path.basename(os.path.dirname(file_path))
                archive_name = f"{dir_name}_{base_name}"
                archive_path = os.path.join(archive_dir, archive_name)
                
                # Если файл с таким именем уже существует, добавляем временную метку
                if os.path.exists(archive_path):
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    archive_name = f"{dir_name}_{timestamp}_{base_name}"
                    archive_path = os.path.join(archive_dir, archive_name)
                
                # Архивируем файл
                shutil.move(file_path, archive_path)
                logger.info(f"Дубликат {file_path} перемещен в {archive_path} (оригинал: {original})")
                count += 1
            except Exception as e:
                logger.error(f"Ошибка при архивации дубликата {file_path}: {e}")
    
    return count

def fix_urls_in_report_messages():
    """
    Исправляет URLs в сообщениях отчетов, чтобы они указывали на правильный порт.
    """
    files_to_check = [
        "direct_chat_message.py",
        "demo_all_objects.py",
        "integrate_replit_chat.py"
    ]
    
    replacements = [
        ("http://localhost:5000", "http://0.0.0.0:5000"),
        ("localhost:5000", "0.0.0.0:5000")
    ]
    
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            continue
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            modified = False
            
            for old, new in replacements:
                if old in content:
                    content = content.replace(old, new)
                    modified = True
            
            if modified:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                logger.info(f"Исправлены URLs в файле {file_path}")
        except Exception as e:
            logger.error(f"Ошибка при исправлении URLs в файле {file_path}: {e}")

def update_todo_file_with_summary(tasks_count: int, incidents_count: int, duplicates_count: int) -> None:
    """
    Обновляет файл todo.md с итогами консолидации.
    
    Args:
        tasks_count: Количество консолидированных задач
        incidents_count: Количество консолидированных инцидентов
        duplicates_count: Количество архивированных дубликатов
    """
    if not os.path.exists(TODO_FILE):
        return
        
    with open(TODO_FILE, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    # Формируем отчет
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = f"""
## Отчет о консолидации файлов ({timestamp})

- Консолидировано задач: {tasks_count}
- Консолидировано инцидентов: {incidents_count}
- Архивировано дубликатов: {duplicates_count}

Все отдельные файлы задач и инцидентов были объединены в основные файлы.
Дубликаты были перемещены в архив.
URLs в сообщениях отчетов были исправлены для корректной работы.
"""
    
    # Добавляем отчет в начало файла после заголовка
    if "# Задачи" in content:
        content = content.replace("# Задачи", f"# Задачи\n{report}")
    else:
        content = f"# Задачи\n{report}\n\n{content}"
    
    with open(TODO_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    
    logger.info("Файл todo.md обновлен с отчетом о консолидации")

def main():
    """Основная функция скрипта."""
    print("\n=== КОНСОЛИДАЦИЯ ОСТАВШИХСЯ ЗАДАЧ И ИНЦИДЕНТОВ ===\n")
    
    # Шаг 1: Находим файлы задач и инцидентов
    task_files, incident_files = find_tasks_incidents_files()
    print(f"Найдено файлов задач: {len(task_files)}")
    print(f"Найдено файлов инцидентов: {len(incident_files)}")
    
    # Шаг 2: Находим дубликаты файлов
    duplicates = {}
    for directory in [TASKS_DIR, INCIDENTS_DIR]:
        if os.path.exists(directory):
            dir_duplicates = find_duplicate_files(directory)
            duplicates.update(dir_duplicates)
    
    print(f"Найдено групп дубликатов: {len(duplicates)}")
    
    # Шаг 3: Консолидируем задачи
    tasks_count = consolidate_tasks(task_files)
    print(f"Консолидировано задач: {tasks_count}")
    
    # Шаг 4: Консолидируем инциденты
    incidents_count = consolidate_incidents(incident_files)
    print(f"Консолидировано инцидентов: {incidents_count}")
    
    # Шаг 5: Архивируем дубликаты
    duplicates_count = archive_duplicates(duplicates)
    print(f"Архивировано дубликатов: {duplicates_count}")
    
    # Шаг 6: Исправляем URLs в сообщениях отчетов
    fix_urls_in_report_messages()
    print("URLs в сообщениях отчетов исправлены")
    
    # Шаг 7: Обновляем todo.md с итогами консолидации
    update_todo_file_with_summary(tasks_count, incidents_count, duplicates_count)
    
    print("\n✅ Консолидация успешно завершена!")
    print("📋 Проверьте файл todo.md для просмотра отчета о консолидации")
    
    return 0

if __name__ == "__main__":
    main()