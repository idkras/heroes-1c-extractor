#!/usr/bin/env python3
"""
Модуль для настройки и создания необходимых директорий для работы системы триггеров.
"""

import os
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("directory_setup")

def ensure_directories_exist() -> bool:
    """
    Проверяет наличие и создает необходимые директории для работы системы триггеров.
    
    Returns:
        bool: True, если все директории созданы успешно, иначе False
    """
    try:
        # Список необходимых директорий
        required_directories = [
            "todo",                      # Задачи
            "incidents",                 # Инциденты
            "standards",                 # Стандарты
            "projects",                  # Проекты
            "projects/tasks",            # Задачи в проектах
            "projects/hypotheses",       # Гипотезы
            "archive",                   # Архив
            "archive/tasks",             # Архив задач
            "archive/incidents",         # Архив инцидентов
            "archive/standards",         # Архив стандартов
            "logs",                      # Логи
            "logs/reports"               # Отчеты
        ]
        
        # Создаем каждую директорию
        for directory in required_directories:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Директория {directory} проверена/создана")
        
        # Проверяем наличие основных файлов
        required_files = [
            ("todo/README.md", "# Задачи\n\nВ этой директории хранятся активные задачи системы.\n"),
            ("incidents/README.md", "# Инциденты\n\nВ этой директории хранятся активные инциденты системы.\n"),
            ("standards/README.md", "# Стандарты\n\nВ этой директории хранятся стандарты системы.\n"),
            ("projects/README.md", "# Проекты\n\nВ этой директории хранятся проекты системы.\n"),
            ("todo.md", "# Активные задачи\n\n_Этот файл автоматически обновляется системой._\n\n"),
            ("ai.incidents.md", "# Активные инциденты\n\n_Этот файл автоматически обновляется системой._\n\n")
        ]
        
        # Создаем каждый файл, если он не существует
        for file_path, content in required_files:
            if not os.path.exists(file_path):
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                logger.info(f"Файл {file_path} создан")
            else:
                logger.info(f"Файл {file_path} уже существует")
        
        return True
    except Exception as e:
        logger.error(f"Ошибка при создании директорий: {e}")
        return False

if __name__ == "__main__":
    # Если скрипт запущен напрямую, создаем директории
    ensure_directories_exist()