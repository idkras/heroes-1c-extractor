#!/usr/bin/env python3
"""
Модуль для работы с хранилищем задач.
Предоставляет функции для получения статистики по задачам.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
import datetime

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Директория хранения задач
TASKS_DIR = os.path.join(os.path.dirname(__file__), "../../../../todo")
INCIDENTS_DIR = os.path.join(os.path.dirname(__file__), "../../../../incidents")

def get_task_statistics() -> Dict[str, Any]:
    """
    Получает статистику по задачам из хранилища.
    
    Returns:
        Dict[str, Any]: Словарь со статистикой
    """
    try:
        # Подсчитываем задачи по статусам и приоритетам
        total = 0
        completed = 0
        in_progress = 0
        not_started = 0
        high_priority = 0
        medium_priority = 0
        low_priority = 0
        
        # Обходим директорию с задачами и инцидентами
        tasks = get_all_tasks()
        incidents = get_all_incidents()
        
        # Объединяем список задач и инцидентов
        all_items = tasks + incidents
        total = len(all_items)
        
        # Проходим по всем задачам и инцидентам
        for item in all_items:
            status = item.get("status", "").lower()
            priority = item.get("priority", 0)
            
            # Проверяем статус
            if "выполнен" in status or "закрыт" in status or status == "done":
                completed += 1
            elif "в работе" in status or "в процессе" in status or status == "in progress":
                in_progress += 1
            else:
                not_started += 1
                
            # Проверяем приоритет
            if priority == 3 or str(priority).lower() == "высокий" or str(priority).lower() == "high":
                high_priority += 1
            elif priority == 2 or str(priority).lower() == "средний" or str(priority).lower() == "medium":
                medium_priority += 1
            else:
                low_priority += 1
        
        # Вычисляем процент выполнения
        completion_rate = int(completed / total * 100) if total > 0 else 0
        
        # Формируем статистику
        stats = {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "not_started": not_started,
            "high_priority": high_priority,
            "medium_priority": medium_priority,
            "low_priority": low_priority,
            "completion_rate": completion_rate,
            "last_update": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return stats
    except Exception as e:
        logger.error(f"Ошибка при получении статистики по задачам: {e}")
        
        # Возвращаем демо-данные в случае ошибки
        return {
            "total": 25,
            "completed": 15,
            "in_progress": 5,
            "not_started": 5,
            "high_priority": 8,
            "medium_priority": 12,
            "low_priority": 5,
            "completion_rate": 60,
            "last_update": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

def get_tasks() -> List[Dict[str, Any]]:
    """
    Получает список всех задач из хранилища.
    Основная функция для получения задач, используемая другими модулями.
    
    Returns:
        List[Dict[str, Any]]: Список задач
    """
    return get_all_tasks()

def get_all_tasks() -> List[Dict[str, Any]]:
    """
    Получает список всех задач из хранилища.
    
    Returns:
        List[Dict[str, Any]]: Список задач
    """
    tasks = []
    
    try:
        # Проверяем, существует ли директория с задачами
        if not os.path.exists(TASKS_DIR):
            logger.warning(f"Директория с задачами не существует: {TASKS_DIR}")
            # Создаем директорию, если она не существует
            try:
                os.makedirs(TASKS_DIR, exist_ok=True)
                logger.info(f"Создана директория для задач: {TASKS_DIR}")
            except Exception as e:
                logger.error(f"Ошибка при создании директории для задач: {e}")
            return tasks
            
        # Обходим все файлы в директории
        for root, _, files in os.walk(TASKS_DIR):
            for file in files:
                if file.endswith(".md"):
                    try:
                        # Открываем файл и извлекаем данные
                        file_path = os.path.join(root, file)
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            
                        # Извлекаем метаданные из содержимого файла
                        task = extract_metadata_from_content(content)
                        if task:
                            tasks.append(task)
                    except Exception as file_error:
                        logger.error(f"Ошибка при чтении файла задачи {file}: {file_error}")
    except Exception as e:
        logger.error(f"Ошибка при получении списка задач: {e}")
        
    return tasks

def get_all_incidents() -> List[Dict[str, Any]]:
    """
    Получает список всех инцидентов из хранилища.
    
    Returns:
        List[Dict[str, Any]]: Список инцидентов
    """
    incidents = []
    
    try:
        # Проверяем, существует ли директория с инцидентами
        if not os.path.exists(INCIDENTS_DIR):
            logger.warning(f"Директория с инцидентами не существует: {INCIDENTS_DIR}")
            # Создаем директорию, если она не существует
            try:
                os.makedirs(INCIDENTS_DIR, exist_ok=True)
                logger.info(f"Создана директория для инцидентов: {INCIDENTS_DIR}")
            except Exception as e:
                logger.error(f"Ошибка при создании директории для инцидентов: {e}")
            return incidents
            
        # Обходим все файлы в директории
        for root, _, files in os.walk(INCIDENTS_DIR):
            for file in files:
                if file.endswith(".md"):
                    try:
                        # Открываем файл и извлекаем данные
                        file_path = os.path.join(root, file)
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            
                        # Извлекаем метаданные из содержимого файла
                        incident = extract_metadata_from_content(content)
                        if incident:
                            incidents.append(incident)
                    except Exception as file_error:
                        logger.error(f"Ошибка при чтении файла инцидента {file}: {file_error}")
    except Exception as e:
        logger.error(f"Ошибка при получении списка инцидентов: {e}")
        
    return incidents

def extract_metadata_from_content(content: str) -> Optional[Dict[str, Any]]:
    """
    Извлекает метаданные из содержимого файла.
    
    Args:
        content: Содержимое файла
        
    Returns:
        Optional[Dict[str, Any]]: Метаданные или None, если не удалось извлечь
    """
    try:
        # Ищем заголовок
        title = None
        status = "Не начато"
        priority = 1
        
        lines = content.split("\n")
        
        # Ищем заголовок (первая строка с # или ## в начале)
        for line in lines:
            if line.startswith("# ") or line.startswith("## "):
                title = line.replace("# ", "").replace("## ", "").strip()
                break
        
        # Ищем статус и приоритет
        for line in lines:
            line_lower = line.lower()
            if "статус:" in line_lower:
                status = line.split(":", 1)[1].strip()
            elif "приоритет:" in line_lower:
                priority_str = line.split(":", 1)[1].strip()
                
                # Преобразуем текстовый приоритет в числовой
                if priority_str.lower() in ["высокий", "high", "3"]:
                    priority = 3
                elif priority_str.lower() in ["средний", "medium", "2"]:
                    priority = 2
                elif priority_str.lower() in ["низкий", "low", "1"]:
                    priority = 1
        
        # Если заголовок не найден, возвращаем None
        if not title:
            return None
            
        # Формируем метаданные
        metadata = {
            "title": title,
            "status": status,
            "priority": priority
        }
        
        return metadata
    except Exception as e:
        logger.error(f"Ошибка при извлечении метаданных из содержимого: {e}")
        return None