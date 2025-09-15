#!/usr/bin/env python3
"""
Скрипт для перемещения JSON-файлов с результатами тестов в структурированную директорию.

Этот скрипт:
1. Копирует JSON-файлы с результатами тестов в advising_platform/data/test_results
2. Создает файлы-переадресации в корневом каталоге для обратной совместимости
3. Логирует информацию о миграции файлов
"""

import os
import json
import shutil
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='data_migration.log'
)
logger = logging.getLogger('json_migration')

# Конфигурация путей
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
TARGET_DIR = os.path.join(ROOT_DIR, 'advising_platform', 'data', 'test_results')

# Файлы для миграции
FILES_TO_MIGRATE = [
    'bidirectional_sync_test_results.json',
    'cache_validation_report.json'
]

def create_redirect_file(original_path, new_path):
    """
    Создает файл-переадресацию в JSON формате для обратной совместимости.
    
    Args:
        original_path: Путь к исходному файлу
        new_path: Путь к новому расположению файла
    """
    redirect_content = {
        "redirect": {
            "original_path": original_path,
            "new_path": new_path,
            "migration_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "description": "Этот файл был перемещен в структурированную директорию. Используйте новый путь для доступа к актуальным данным."
        }
    }
    
    redirect_path = os.path.join(ROOT_DIR, original_path)
    try:
        with open(redirect_path, 'w', encoding='utf-8') as f:
            json.dump(redirect_content, f, ensure_ascii=False, indent=2)
        logger.info(f"Создан файл-переадресация: {redirect_path}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при создании файла-переадресации {redirect_path}: {e}")
        return False

def migrate_file(filename):
    """
    Перемещает файл в целевую директорию и создаёт файл-переадресацию.
    
    Args:
        filename: Имя файла для миграции
    
    Returns:
        bool: True в случае успеха, False при ошибке
    """
    source_path = os.path.join(ROOT_DIR, filename)
    target_path = os.path.join(TARGET_DIR, filename)
    
    # Проверяем, существует ли исходный файл
    if not os.path.exists(source_path):
        logger.warning(f"Исходный файл не существует: {source_path}")
        return False
    
    try:
        # Создаем целевую директорию, если она не существует
        os.makedirs(TARGET_DIR, exist_ok=True)
        
        # Копируем файл
        shutil.copy2(source_path, target_path)
        logger.info(f"Файл {filename} скопирован в {target_path}")
        
        # Создаем файл-переадресацию
        relative_target_path = os.path.relpath(target_path, ROOT_DIR)
        create_redirect_file(filename, relative_target_path)
        
        return True
    except Exception as e:
        logger.error(f"Ошибка при миграции файла {filename}: {e}")
        return False

def main():
    """
    Основная функция миграции файлов.
    """
    logger.info("Начало миграции JSON-файлов")
    
    success_count = 0
    for filename in FILES_TO_MIGRATE:
        if migrate_file(filename):
            success_count += 1
    
    logger.info(f"Миграция завершена. Успешно обработано: {success_count}/{len(FILES_TO_MIGRATE)} файлов")
    print(f"Миграция завершена. Успешно обработано: {success_count}/{len(FILES_TO_MIGRATE)} файлов")

if __name__ == "__main__":
    main()