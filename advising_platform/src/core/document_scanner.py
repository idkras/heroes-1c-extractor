#!/usr/bin/env python3
"""
Модуль для сканирования документов и поиска триггеров.
Обеспечивает извлечение информации из различных типов документов.

Автор: AI Assistant
Дата: 21 мая 2025
"""

import os
import re
import logging
from typing import Dict, List, Set, Tuple, Optional, Any, Union

# Настройка логирования
logger = logging.getLogger("document_scanner")

def scan_file_for_triggers(file_path: str) -> List[str]:
    """
    Сканирует файл на наличие триггеров.
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        List[str]: Список найденных триггеров
    """
    logger.debug(f"Сканирование файла {file_path} на наличие триггеров")
    
    # Проверяем существование файла
    if not os.path.exists(file_path):
        logger.warning(f"Файл {file_path} не существует")
        return []
    
    # Читаем содержимое файла
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        logger.error(f"Ошибка при чтении файла {file_path}: {e}")
        return []
    
    # Список ключевых слов для поиска триггеров
    trigger_keywords = [
        "выполнить анализ",
        "оптимизировать производительность",
        "критическая ошибка",
        "проблема с кешированием",
        "синхронизация данных",
        "устранить дублирование",
        "требуется рефакторинг",
        "исправить баг",
        "улучшить интерфейс",
        "обновить документацию"
    ]
    
    # Ищем триггеры в содержимом файла
    found_triggers = []
    for keyword in trigger_keywords:
        if keyword in content.lower():
            found_triggers.append(keyword)
    
    logger.debug(f"Найдено {len(found_triggers)} триггеров в файле {file_path}")
    return found_triggers

def extract_task_data(file_path: str, content: Optional[str] = None) -> Dict[str, Any]:
    """
    Извлекает данные о задаче из файла.
    
    Args:
        file_path: Путь к файлу
        content: Содержимое файла (опционально)
        
    Returns:
        Dict[str, Any]: Данные о задаче
    """
    logger.debug(f"Извлечение данных о задаче из файла {file_path}")
    
    # Если содержимое не передано, читаем его из файла
    if content is None:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Ошибка при чтении файла {file_path}: {e}")
            return {}
    
    # Извлекаем данные из содержимого файла
    task_data = {}
    
    # Извлекаем заголовок задачи
    title_match = re.search(r'#\s*(.*?)(?=\n|$)', content)
    if title_match:
        task_data["title"] = title_match.group(1).strip()
    
    # Извлекаем описание задачи
    description_match = re.search(r'##\s*Описание\s*\n(.*?)(?=\n##|\n#|$)', content, re.DOTALL)
    if description_match:
        task_data["description"] = description_match.group(1).strip()
    
    # Извлекаем приоритет задачи
    priority_match = re.search(r'##\s*Приоритет\s*\n(.*?)(?=\n##|\n#|$)', content, re.DOTALL)
    if priority_match:
        task_data["priority"] = priority_match.group(1).strip()
    
    # Извлекаем исполнителя задачи
    assignee_match = re.search(r'##\s*Исполнитель\s*\n(.*?)(?=\n##|\n#|$)', content, re.DOTALL)
    if assignee_match:
        task_data["assignee"] = assignee_match.group(1).strip()
    
    # Извлекаем статус задачи
    status_match = re.search(r'##\s*Статус\s*\n(.*?)(?=\n##|\n#|$)', content, re.DOTALL)
    if status_match:
        task_data["status"] = status_match.group(1).strip()
    
    # Если заголовок не найден, пытаемся извлечь его из имени файла
    if "title" not in task_data:
        filename = os.path.basename(file_path)
        task_data["title"] = os.path.splitext(filename)[0].replace('_', ' ').title()
    
    logger.debug(f"Извлечены данные о задаче: {task_data}")
    return task_data

def extract_incident_data(file_path: str, content: Optional[str] = None) -> Dict[str, Any]:
    """
    Извлекает данные об инциденте из файла.
    
    Args:
        file_path: Путь к файлу
        content: Содержимое файла (опционально)
        
    Returns:
        Dict[str, Any]: Данные об инциденте
    """
    logger.debug(f"Извлечение данных об инциденте из файла {file_path}")
    
    # Если содержимое не передано, читаем его из файла
    if content is None:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Ошибка при чтении файла {file_path}: {e}")
            return {}
    
    # Извлекаем данные из содержимого файла
    incident_data = {}
    
    # Извлекаем заголовок инцидента
    title_match = re.search(r'#\s*(?:Инцидент:)?\s*(.*?)(?=\n|$)', content)
    if title_match:
        incident_data["title"] = title_match.group(1).strip()
    
    # Извлекаем описание инцидента
    description_match = re.search(r'##\s*Описание\s*\n(.*?)(?=\n##|\n#|$)', content, re.DOTALL)
    if description_match:
        incident_data["description"] = description_match.group(1).strip()
    
    # Извлекаем серьезность инцидента
    severity_match = re.search(r'##\s*(?:Серьезность|Важность)\s*\n(.*?)(?=\n##|\n#|$)', content, re.DOTALL)
    if severity_match:
        incident_data["severity"] = severity_match.group(1).strip()
    
    # Извлекаем статус инцидента
    status_match = re.search(r'##\s*Статус\s*\n(.*?)(?=\n##|\n#|$)', content, re.DOTALL)
    if status_match:
        incident_data["status"] = status_match.group(1).strip()
    
    # Если заголовок не найден, пытаемся извлечь его из имени файла
    if "title" not in incident_data:
        filename = os.path.basename(file_path)
        incident_data["title"] = os.path.splitext(filename)[0].replace('_', ' ').title()
    
    logger.debug(f"Извлечены данные об инциденте: {incident_data}")
    return incident_data