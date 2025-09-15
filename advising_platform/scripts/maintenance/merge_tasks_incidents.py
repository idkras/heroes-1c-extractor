#!/usr/bin/env python3
"""
Скрипт для синхронизации отдельных файлов задач и инцидентов с основными файлами.

Этот скрипт позволяет:
1. Собирать задачи из отдельных файлов и добавлять их в todo.md
2. Собирать инциденты из отдельных файлов и добавлять их в ai.incidents.md
3. Обновлять кеш после внесения изменений
4. Архивировать дублирующиеся файлы

Автор: AI Assistant
Дата: 20 мая 2025
"""

import os
import re
import sys
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('merge_tasks_incidents.log')
    ]
)
logger = logging.getLogger("merge_tasks_incidents")

# Пути к директориям и файлам
TODO_FILE = "[todo · incidents]/todo.md"
INCIDENTS_FILE = "[todo · incidents]/ai.incidents.md"
TASKS_DIR = "projects/tasks"
INCIDENTS_DIR = "[todo · incidents]/ai.incidents"
ARCHIVE_DIR = "[todo · incidents]/[archive]"

def ensure_directory_exists(directory: str) -> None:
    """
    Проверяет наличие директории и создает ее при необходимости.
    
    Args:
        directory: Путь к директории
    """
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Создана директория: {directory}")

def collect_tasks_from_files() -> List[Dict[str, str]]:
    """
    Собирает задачи из отдельных файлов.
    
    Returns:
        List[Dict[str, str]]: Список задач с метаданными
    """
    tasks = []
    
    if not os.path.exists(TASKS_DIR):
        logger.warning(f"Директория с задачами не найдена: {TASKS_DIR}")
        return tasks
    
    for file_path in Path(TASKS_DIR).glob("*.md"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Извлекаем заголовок (первую строку, начинающуюся с #)
                title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
                if not title_match:
                    logger.warning(f"Не удалось извлечь заголовок из файла: {file_path}")
                    continue
                
                title = title_match.group(1).strip()
                
                # Определяем статус задачи
                status = "open"
                if re.search(r'статус:.*выполнено|status:.*completed|статус:.*завершено', content, re.IGNORECASE):
                    status = "completed"
                
                # Извлекаем описание (все, что после заголовка до следующего заголовка)
                description = content.split(title_match.group(0), 1)[1].strip()
                
                tasks.append({
                    "title": title,
                    "status": status,
                    "description": description,
                    "file_path": str(file_path)
                })
                
                logger.info(f"Найдена задача: {title} ({status})")
        except Exception as e:
            logger.error(f"Ошибка при обработке файла {file_path}: {e}")
    
    logger.info(f"Найдено {len(tasks)} задач в отдельных файлах")
    return tasks

def collect_incidents_from_files() -> List[Dict[str, str]]:
    """
    Собирает инциденты из отдельных файлов.
    
    Returns:
        List[Dict[str, str]]: Список инцидентов с метаданными
    """
    incidents = []
    
    if not os.path.exists(INCIDENTS_DIR):
        logger.warning(f"Директория с инцидентами не найдена: {INCIDENTS_DIR}")
        return incidents
    
    for file_path in Path(INCIDENTS_DIR).glob("*.md"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Извлекаем заголовок (первую строку, начинающуюся с #)
                title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
                if not title_match:
                    logger.warning(f"Не удалось извлечь заголовок из файла: {file_path}")
                    continue
                
                title = title_match.group(1).strip()
                
                # Определяем статус инцидента
                status = "open"
                if re.search(r'статус:.*закрыт|status:.*closed|статус:.*решен|статус:.*готово', content, re.IGNORECASE):
                    status = "closed"
                
                # Извлекаем описание (все, что после заголовка до следующего заголовка)
                description = content.split(title_match.group(0), 1)[1].strip()
                
                # Извлекаем дату инцидента
                date_match = re.search(r'Дата обнаружения[:\s]*(\d{1,2}[- /.]\d{1,2}[- /.]\d{2,4}|\d{4}[- /.]\d{1,2}[- /.]\d{1,2})', content, re.IGNORECASE)
                date = None
                if date_match:
                    date = date_match.group(1).strip()
                else:
                    # Если дата не указана явно, пытаемся извлечь из имени файла
                    file_date_match = re.search(r'(\d{8}|\d{4}-\d{2}-\d{2})', str(file_path))
                    if file_date_match:
                        date = file_date_match.group(1).strip()
                    else:
                        # Если не удалось найти дату, используем текущую
                        date = datetime.now().strftime("%Y-%m-%d")
                
                incidents.append({
                    "title": title,
                    "status": status,
                    "description": description,
                    "date": date,
                    "file_path": str(file_path)
                })
                
                logger.info(f"Найден инцидент: {title} ({status}, {date})")
        except Exception as e:
            logger.error(f"Ошибка при обработке файла {file_path}: {e}")
    
    logger.info(f"Найдено {len(incidents)} инцидентов в отдельных файлах")
    return incidents

def format_task_for_todo(task: Dict[str, str]) -> str:
    """
    Форматирует задачу для добавления в todo.md.
    
    Args:
        task: Словарь с метаданными задачи
        
    Returns:
        str: Отформатированная задача
    """
    # Базовый формат задачи для todo.md
    checkbox = "x" if task["status"] == "completed" else " "
    
    # Извлекаем приоритет, ответственного и срок, если они указаны
    priority_match = re.search(r'\[(.*?)\]', task["description"])
    priority = f"[{priority_match.group(1)}]" if priority_match else ""
    
    assignee_match = re.search(r'@([a-zA-Z0-9_\- ]+)', task["description"])
    assignee = f"· @{assignee_match.group(1)}" if assignee_match else ""
    
    deadline_match = re.search(r'до (\d{1,2}[- /.]\d{1,2}[- /.]\d{2,4}|\d{4}[- /.]\d{1,2}[- /.]\d{1,2})', task["description"])
    deadline = f"· до {deadline_match.group(1)}" if deadline_match else ""
    
    # Формируем строку задачи
    task_line = f"- [{checkbox}] **{task['title']}** {priority} {assignee} {deadline}\n"
    
    # Извлекаем и добавляем дополнительные детали (цель, DoD, подзадачи)
    goal_match = re.search(r'\*\*цель\*\*:(.+?)(?=\*\*|$)', task["description"], re.DOTALL | re.IGNORECASE)
    goal = f"**цель**: {goal_match.group(1).strip()}\n" if goal_match else ""
    
    dod_match = re.search(r'\*\*dod.*?\*\*:(.+?)(?=\*\*|$)', task["description"], re.DOTALL | re.IGNORECASE)
    dod = f"**dod · result**: {dod_match.group(1).strip()}\n" if dod_match else ""
    
    subtasks_match = re.search(r'\*\*подзадачи\*\*:(.*?)(?=\*\*|$)', task["description"], re.DOTALL | re.IGNORECASE)
    subtasks = ""
    if subtasks_match:
        subtasks = "**подзадачи**:\n"
        for line in subtasks_match.group(1).strip().split('\n'):
            if line.strip():
                subtasks += f"{line.strip()}\n"
    
    requirements_match = re.search(r'\*\*требования\*\*:(.*?)(?=\*\*|$)', task["description"], re.DOTALL | re.IGNORECASE)
    requirements = ""
    if requirements_match:
        requirements = "**требования**:\n"
        for line in requirements_match.group(1).strip().split('\n'):
            if line.strip():
                requirements += f"{line.strip()}\n"
    
    # Собираем все вместе
    formatted_task = task_line
    if goal:
        formatted_task += goal
    if dod:
        formatted_task += dod
    if subtasks:
        formatted_task += subtasks
    if requirements:
        formatted_task += requirements
    
    return formatted_task

def format_incident_for_file(incident: Dict[str, str]) -> str:
    """
    Форматирует инцидент для добавления в ai.incidents.md.
    
    Args:
        incident: Словарь с метаданными инцидента
        
    Returns:
        str: Отформатированный инцидент
    """
    # Форматируем дату инцидента
    try:
        date_str = incident["date"]
        # Пытаемся обработать различные форматы дат
        if "-" in date_str:
            date_parts = date_str.split("-")
            if len(date_parts[0]) == 4:  # YYYY-MM-DD
                date_formatted = date_str
            else:  # DD-MM-YYYY
                date_formatted = f"{date_parts[2]}-{date_parts[1]}-{date_parts[0]}"
        elif "." in date_str:
            date_parts = date_str.split(".")
            date_formatted = f"{date_parts[2]}-{date_parts[1]}-{date_parts[0]}"
        elif "/" in date_str:
            date_parts = date_str.split("/")
            date_formatted = f"{date_parts[2]}-{date_parts[1]}-{date_parts[0]}"
        elif len(date_str) == 8:  # YYYYMMDD
            date_formatted = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        else:
            # Если не удалось распознать формат, используем как есть
            date_formatted = date_str
    except Exception as e:
        logger.error(f"Ошибка при форматировании даты {incident['date']}: {e}")
        date_formatted = incident["date"]
    
    # Базовый формат инцидента
    incident_header = f"## {date_formatted} - {incident['title']}\n\n"
    
    # Добавляем краткое описание (первый абзац)
    description_paragraphs = incident["description"].strip().split("\n\n")
    summary = description_paragraphs[0] if description_paragraphs else ""
    
    # Ищем причины и решения, если они указаны
    causes = ""
    causes_match = re.search(r'## Анализ "5 почему"(.+?)(?=##|$)', incident["description"], re.DOTALL)
    if causes_match:
        causes = f"\n### Причины\n\n{causes_match.group(1).strip()}\n"
    
    solution = ""
    solution_match = re.search(r'## Рекомендации|## Предлагаемое решение(.+?)(?=##|$)', incident["description"], re.DOTALL)
    if solution_match:
        solution = f"\n### Решение\n\n{solution_match.group(1).strip()}\n"
    
    # Собираем все вместе
    formatted_incident = incident_header + summary + causes + solution + "\n"
    
    return formatted_incident

def update_todo_file(tasks: List[Dict[str, str]], dry_run: bool = False) -> bool:
    """
    Обновляет файл todo.md, добавляя задачи из отдельных файлов.
    
    Args:
        tasks: Список задач с метаданными
        dry_run: Режим без внесения изменений (только вывод в лог)
        
    Returns:
        bool: True, если обновление успешно, иначе False
    """
    if not tasks:
        logger.info("Нет задач для добавления в todo.md")
        return True
    
    if not os.path.exists(TODO_FILE):
        logger.error(f"Файл todo.md не найден: {TODO_FILE}")
        return False
    
    try:
        # Читаем содержимое todo.md
        with open(TODO_FILE, 'r', encoding='utf-8') as f:
            todo_content = f.read()
        
        # Проверяем, содержит ли файл нужные разделы
        sections = [
            "## 🚩 Высокоприоритетные задачи (P1)",
            "## 🔄 В работе",
            "## 📝 Бэклог",
            "## 🔜 Следующие действия",
            "## 🔍 Исследования и гипотезы"
        ]
        
        # Определяем раздел для добавления задач (по умолчанию - "Бэклог")
        target_section = "## 📝 Бэклог"
        for section in sections:
            if section in todo_content:
                target_section = section
                break
        
        # Форматируем задачи
        formatted_tasks = []
        for task in tasks:
            formatted_task = format_task_for_todo(task)
            formatted_tasks.append(formatted_task)
        
        # Обновляем todo.md
        if dry_run:
            logger.info(f"[Режим предпросмотра] Будет добавлено {len(tasks)} задач в раздел '{target_section}':")
            for task in formatted_tasks:
                logger.info(f"\n{task}")
            return True
        
        # Находим позицию для вставки
        section_pos = todo_content.find(target_section)
        if section_pos == -1:
            # Если раздел не найден, добавляем в конец файла
            logger.warning(f"Раздел '{target_section}' не найден, задачи будут добавлены в конец файла")
            insert_pos = len(todo_content)
            insert_text = f"\n\n{target_section}\n\n" + "\n\n".join(formatted_tasks) + "\n"
        else:
            # Находим конец заголовка раздела
            next_line_pos = todo_content.find('\n', section_pos)
            if next_line_pos == -1:
                next_line_pos = len(todo_content)
            
            # Вставляем задачи после заголовка
            insert_pos = next_line_pos + 1
            insert_text = "\n" + "\n\n".join(formatted_tasks) + "\n"
        
        # Обновляем файл
        new_content = todo_content[:insert_pos] + insert_text + todo_content[insert_pos:]
        with open(TODO_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        logger.info(f"Добавлено {len(tasks)} задач в todo.md")
        return True
    except Exception as e:
        logger.error(f"Ошибка при обновлении todo.md: {e}")
        return False

def update_incidents_file(incidents: List[Dict[str, str]], dry_run: bool = False) -> bool:
    """
    Обновляет файл ai.incidents.md, добавляя инциденты из отдельных файлов.
    
    Args:
        incidents: Список инцидентов с метаданными
        dry_run: Режим без внесения изменений (только вывод в лог)
        
    Returns:
        bool: True, если обновление успешно, иначе False
    """
    if not incidents:
        logger.info("Нет инцидентов для добавления в ai.incidents.md")
        return True
    
    try:
        # Если файл инцидентов не существует, создаем его
        if not os.path.exists(INCIDENTS_FILE):
            logger.info(f"Файл инцидентов не найден, создаем новый: {INCIDENTS_FILE}")
            
            if not dry_run:
                with open(INCIDENTS_FILE, 'w', encoding='utf-8') as f:
                    f.write("# 🚨 AI Incidents Log\n\nОбновлено: " + datetime.now().strftime("%d %B %Y, %H:%M CET") + "\n\n")
            
            incidents_content = "# 🚨 AI Incidents Log\n\nОбновлено: " + datetime.now().strftime("%d %B %Y, %H:%M CET") + "\n\n"
        else:
            # Читаем содержимое ai.incidents.md
            with open(INCIDENTS_FILE, 'r', encoding='utf-8') as f:
                incidents_content = f.read()
        
        # Форматируем инциденты
        formatted_incidents = []
        for incident in incidents:
            try:
                formatted_incident = format_incident_for_file(incident)
                if formatted_incident and formatted_incident.strip():
                    formatted_incidents.append(formatted_incident)
                else:
                    logger.warning(f"Пустой форматированный инцидент для {incident['title']}")
            except Exception as e:
                logger.error(f"Ошибка при форматировании инцидента {incident['title']}: {e}")
        
        # Обновляем ai.incidents.md
        if dry_run:
            logger.info(f"[Режим предпросмотра] Будет добавлено {len(incidents)} инцидентов в ai.incidents.md:")
            for incident in formatted_incidents:
                logger.info(f"\n{incident}")
            return True
        
        # Находим позицию для вставки (после заголовка и первого параграфа)
        header_end = incidents_content.find('\n\n', incidents_content.find('#'))
        if header_end == -1:
            header_end = len(incidents_content)
        
        # Вставляем инциденты после заголовка
        insert_pos = header_end + 2
        insert_text = "\n".join(formatted_incidents) + "\n"
        
        # Обновляем файл
        new_content = incidents_content[:insert_pos] + insert_text + incidents_content[insert_pos:]
        with open(INCIDENTS_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        logger.info(f"Добавлено {len(incidents)} инцидентов в ai.incidents.md")
        return True
    except Exception as e:
        logger.error(f"Ошибка при обновлении ai.incidents.md: {e}")
        return False

def archive_processed_files(files: List[str], dry_run: bool = False) -> int:
    """
    Архивирует обработанные файлы.
    
    Args:
        files: Список путей к файлам
        dry_run: Режим без внесения изменений (только вывод в лог)
        
    Returns:
        int: Количество архивированных файлов
    """
    if not files:
        logger.info("Нет файлов для архивации")
        return 0
    
    # Проверяем наличие директории архива
    ensure_directory_exists(ARCHIVE_DIR)
    
    # Создаем поддиректорию с текущей датой
    date_dir = os.path.join(ARCHIVE_DIR, datetime.now().strftime("%Y%m%d"))
    ensure_directory_exists(date_dir)
    
    count = 0
    for file_path in files:
        try:
            if not os.path.exists(file_path):
                logger.warning(f"Файл не найден: {file_path}")
                continue
            
            # Определяем путь к архивной копии
            filename = os.path.basename(file_path)
            archive_path = os.path.join(date_dir, filename)
            
            # Архивируем файл
            if dry_run:
                logger.info(f"[Режим предпросмотра] Файл будет архивирован: {file_path} -> {archive_path}")
            else:
                # Копируем файл в архив и удаляем оригинал
                import shutil
                shutil.copy2(file_path, archive_path)
                os.remove(file_path)
                
                logger.info(f"Файл архивирован: {file_path} -> {archive_path}")
            
            count += 1
        except Exception as e:
            logger.error(f"Ошибка при архивации файла {file_path}: {e}")
    
    logger.info(f"Архивировано {count} файлов")
    return count

def update_cache():
    """
    Обновляет кеш после внесения изменений.
    
    Returns:
        bool: True, если обновление успешно, иначе False
    """
    try:
        logger.info("Обновление кеша...")
        
        # Формируем команду для обновления кеша
        cmd = "python sync_verification.py --sync"
        
        # Выполняем команду
        import subprocess
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Кеш успешно обновлен")
            logger.info(result.stdout)
            return True
        else:
            logger.error(f"Ошибка при обновлении кеша: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Исключение при обновлении кеша: {e}")
        return False

def main():
    """Основная функция скрипта."""
    parser = argparse.ArgumentParser(description='Синхронизация задач и инцидентов')
    
    parser.add_argument('--tasks', action='store_true',
                        help='Синхронизировать задачи')
    parser.add_argument('--incidents', action='store_true',
                        help='Синхронизировать инциденты')
    parser.add_argument('--all', action='store_true',
                        help='Синхронизировать задачи и инциденты')
    parser.add_argument('--archive', action='store_true',
                        help='Архивировать обработанные файлы')
    parser.add_argument('--dry-run', action='store_true',
                        help='Режим без внесения изменений (только вывод в лог)')
    parser.add_argument('--update-cache', action='store_true',
                        help='Обновить кеш после синхронизации')
    
    args = parser.parse_args()
    
    # Если не указаны конкретные действия, используем --all
    if not (args.tasks or args.incidents or args.all):
        args.all = True
    
    # Запускаем процесс синхронизации
    logger.info("Запуск синхронизации задач и инцидентов")
    
    # Обработка задач
    task_files = []
    if args.tasks or args.all:
        tasks = collect_tasks_from_files()
        if tasks:
            success = update_todo_file(tasks, args.dry_run)
            if success and not args.dry_run:
                task_files = [task["file_path"] for task in tasks]
    
    # Обработка инцидентов
    incident_files = []
    if args.incidents or args.all:
        incidents = collect_incidents_from_files()
        if incidents:
            success = update_incidents_file(incidents, args.dry_run)
            if success and not args.dry_run:
                incident_files = [incident["file_path"] for incident in incidents]
    
    # Архивация обработанных файлов
    if args.archive and not args.dry_run:
        files_to_archive = task_files + incident_files
        archive_processed_files(files_to_archive, args.dry_run)
    
    # Обновление кеша
    if args.update_cache and not args.dry_run:
        update_cache()
    
    logger.info("Синхронизация завершена")

if __name__ == "__main__":
    main()