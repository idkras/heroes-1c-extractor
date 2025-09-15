#!/usr/bin/env python3
"""
Скрипт для проверки и отправки статистики по задачам напрямую в чат.
Решает проблему с отображением статистики в чате Replit.

Автор: AI Assistant
Дата: 21 мая 2025
"""

import os
import sys
import glob
import re
import time
import logging
from typing import Dict, List, Tuple, Any

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Пути к директориям с задачами и инцидентами
TODO_FILE = "todo/todo.md"
TASK_DIRS = ["todo", "hypotheses"]
INCIDENT_DIRS = ["incidents"]
STANDARD_DIRS = ["standards", "[standards .md]"]

def count_tasks() -> Dict[str, int]:
    """
    Подсчитывает количество задач по статусам.
    
    Returns:
        Dict[str, int]: Словарь {статус: количество}
    """
    # Инициализируем счетчики
    stats = {
        "total": 0,
        "completed": 0,
        "in_progress": 0,
        "not_started": 0,
        "high_priority": 0,
        "medium_priority": 0,
        "low_priority": 0
    }
    
    # Проверяем наличие файла todo.md
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
            # Подсчитываем общее количество задач
            task_sections = re.findall(r"## .+?(?=\n## |\Z)", content, re.DOTALL)
            stats["total"] = len(task_sections)
            
            # Подсчитываем задачи по статусам
            for section in task_sections:
                # Проверяем статус
                if re.search(r"Статус:.*?выполнено", section, re.IGNORECASE) or re.search(r"Status:.*?completed", section, re.IGNORECASE):
                    stats["completed"] += 1
                elif re.search(r"Статус:.*?в процессе", section, re.IGNORECASE) or re.search(r"Status:.*?in progress", section, re.IGNORECASE):
                    stats["in_progress"] += 1
                else:
                    stats["not_started"] += 1
                
                # Проверяем приоритет
                if re.search(r"Приоритет:.*?высокий", section, re.IGNORECASE) or re.search(r"Priority:.*?high", section, re.IGNORECASE):
                    stats["high_priority"] += 1
                elif re.search(r"Приоритет:.*?средний", section, re.IGNORECASE) or re.search(r"Priority:.*?medium", section, re.IGNORECASE):
                    stats["medium_priority"] += 1
                elif re.search(r"Приоритет:.*?низкий", section, re.IGNORECASE) or re.search(r"Priority:.*?low", section, re.IGNORECASE):
                    stats["low_priority"] += 1
    
    # Дополнительный поиск по директориям, если основной файл не содержит всех задач
    for task_dir in TASK_DIRS:
        if os.path.exists(task_dir):
            for file_path in glob.glob(f"{task_dir}/**/*.md", recursive=True):
                # Пропускаем основной файл, который уже обработан
                if file_path == TODO_FILE:
                    continue
                
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        file_content = f.read()
                        
                        # Проверяем, является ли файл задачей
                        if "# Задача:" in file_content or "# Task:" in file_content:
                            stats["total"] += 1
                            
                            # Проверяем статус
                            if re.search(r"Статус:.*?выполнено", file_content, re.IGNORECASE) or re.search(r"Status:.*?completed", file_content, re.IGNORECASE):
                                stats["completed"] += 1
                            elif re.search(r"Статус:.*?в процессе", file_content, re.IGNORECASE) or re.search(r"Status:.*?in progress", file_content, re.IGNORECASE):
                                stats["in_progress"] += 1
                            else:
                                stats["not_started"] += 1
                            
                            # Проверяем приоритет
                            if re.search(r"Приоритет:.*?высокий", file_content, re.IGNORECASE) or re.search(r"Priority:.*?high", file_content, re.IGNORECASE):
                                stats["high_priority"] += 1
                            elif re.search(r"Приоритет:.*?средний", file_content, re.IGNORECASE) or re.search(r"Priority:.*?medium", file_content, re.IGNORECASE):
                                stats["medium_priority"] += 1
                            elif re.search(r"Приоритет:.*?низкий", file_content, re.IGNORECASE) or re.search(r"Priority:.*?low", file_content, re.IGNORECASE):
                                stats["low_priority"] += 1
                except Exception as e:
                    logger.error(f"Ошибка при чтении файла {file_path}: {e}")
    
    return stats

def count_incidents() -> Dict[str, int]:
    """
    Подсчитывает количество инцидентов по статусам.
    
    Returns:
        Dict[str, int]: Словарь {статус: количество}
    """
    # Инициализируем счетчики
    stats = {
        "total": 0,
        "resolved": 0,
        "in_progress": 0,
        "open": 0
    }
    
    # Ищем инциденты по директориям
    for incident_dir in INCIDENT_DIRS:
        if os.path.exists(incident_dir):
            for file_path in glob.glob(f"{incident_dir}/**/*.md", recursive=True):
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        file_content = f.read()
                        
                        # Проверяем, является ли файл инцидентом
                        if "# Инцидент:" in file_content or "# Incident:" in file_content:
                            stats["total"] += 1
                            
                            # Проверяем статус
                            if re.search(r"Статус:.*?решен", file_content, re.IGNORECASE) or re.search(r"Status:.*?resolved", file_content, re.IGNORECASE):
                                stats["resolved"] += 1
                            elif re.search(r"Статус:.*?в процессе", file_content, re.IGNORECASE) or re.search(r"Status:.*?in progress", file_content, re.IGNORECASE):
                                stats["in_progress"] += 1
                            else:
                                stats["open"] += 1
                except Exception as e:
                    logger.error(f"Ошибка при чтении файла {file_path}: {e}")
    
    return stats

def count_standards() -> Dict[str, int]:
    """
    Подсчитывает количество стандартов.
    
    Returns:
        Dict[str, int]: Словарь со статистикой по стандартам
    """
    # Инициализируем счетчики
    stats = {
        "total": 0,
        "active": 0,
        "deprecated": 0,
        "categories": {}
    }
    
    # Ищем стандарты по директориям
    for standard_dir in STANDARD_DIRS:
        if os.path.exists(standard_dir):
            for file_path in glob.glob(f"{standard_dir}/**/*.md", recursive=True):
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        file_content = f.read()
                        
                        # Проверяем, является ли файл стандартом
                        if "# Стандарт:" in file_content or "# Standard:" in file_content:
                            stats["total"] += 1
                            
                            # Проверяем статус
                            if re.search(r"Статус:.*?устарел", file_content, re.IGNORECASE) or re.search(r"Status:.*?deprecated", file_content, re.IGNORECASE):
                                stats["deprecated"] += 1
                            else:
                                stats["active"] += 1
                            
                            # Извлекаем категорию
                            category_match = re.search(r"Категория:\s*(.+?)(?:\n|$)", file_content) or re.search(r"Category:\s*(.+?)(?:\n|$)", file_content)
                            if category_match:
                                category = category_match.group(1).strip()
                                if category not in stats["categories"]:
                                    stats["categories"][category] = 0
                                stats["categories"][category] += 1
                except Exception as e:
                    logger.error(f"Ошибка при чтении файла {file_path}: {e}")
    
    return stats

def format_statistics() -> str:
    """
    Форматирует статистику для отображения в чате.
    
    Returns:
        str: Отформатированное сообщение с полной статистикой
    """
    # Собираем статистику
    task_stats = count_tasks()
    incident_stats = count_incidents()
    standard_stats = count_standards()
    
    # Рассчитываем процентное соотношение
    task_completed_percent = int(task_stats["completed"] / task_stats["total"] * 100) if task_stats["total"] > 0 else 0
    task_in_progress_percent = int(task_stats["in_progress"] / task_stats["total"] * 100) if task_stats["total"] > 0 else 0
    task_not_started_percent = int(task_stats["not_started"] / task_stats["total"] * 100) if task_stats["total"] > 0 else 0
    
    incident_resolved_percent = int(incident_stats["resolved"] / incident_stats["total"] * 100) if incident_stats["total"] > 0 else 0
    
    # Форматируем сообщение
    message = f"""📊 **Полная статистика проекта**

### 📝 Статистика по задачам:
- Всего задач: {task_stats["total"]}
- ✅ Выполнено: {task_stats["completed"]} ({task_completed_percent}%)
- ⏳ В процессе: {task_stats["in_progress"]} ({task_in_progress_percent}%)
- 🆕 Не начато: {task_stats["not_started"]} ({task_not_started_percent}%)

### 🔢 По приоритетам:
- 🔴 Высокий: {task_stats["high_priority"]}
- 🟠 Средний: {task_stats["medium_priority"]}
- 🟢 Низкий: {task_stats["low_priority"]}

### ⚠️ Статистика по инцидентам:
- Всего инцидентов: {incident_stats["total"]}
- ✅ Решено: {incident_stats["resolved"]} ({incident_resolved_percent}%)
- ⏳ В процессе: {incident_stats["in_progress"]}
- 🔍 Открыто: {incident_stats["open"]}

### 📜 Статистика по стандартам:
- Всего стандартов: {standard_stats["total"]}
- 📌 Активных: {standard_stats["active"]}
- 📌 Устаревших: {standard_stats["deprecated"]}
- 🎯 Целевое количество: ~40 активных стандартов

Время формирования отчета: {time.strftime("%Y-%m-%d %H:%M:%S")}"""
    
    return message

def send_statistics_to_chat():
    """
    Отправляет статистику напрямую в чат Replit.
    
    Returns:
        bool: True, если отправка успешна, иначе False
    """
    try:
        # Напрямую используем функцию из antml
        import antml.function_calls
        
        # Форматируем статистику
        stats_message = format_statistics()
        
        # Отправляем сообщение напрямую
        antml.function_calls.function_call("report_progress", {"summary": stats_message})
        
        logger.info("Статистика успешно отправлена в чат Replit")
        print("✅ Статистика успешно отправлена в чат Replit")
        return True
    except Exception as e:
        logger.error(f"Ошибка при отправке статистики в чат Replit: {e}")
        print(f"❌ Ошибка при отправке статистики в чат Replit: {e}")
        return False

def main():
    """Основная функция скрипта."""
    print("\n=== ПРОВЕРКА И ОТПРАВКА СТАТИСТИКИ ПО ЗАДАЧАМ ===\n")
    
    # Проверяем и отправляем статистику
    send_statistics_to_chat()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())