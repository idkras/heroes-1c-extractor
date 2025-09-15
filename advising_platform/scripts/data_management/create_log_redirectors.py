#!/usr/bin/env python3
"""
Скрипт для создания файлов-переадресаций для журналов логов.

Создает простые текстовые файлы с информацией о новом расположении логов.
"""

import os
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='advising_platform/data/logs/redirector_creation.log'
)
logger = logging.getLogger('log_redirectors')

# Конфигурация путей
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
LOG_FILES = [
    'cache_validation.log',
    'todo_validation.log',
    'directory_move.log',
    'data_migration.log'
]

def create_redirector(log_file):
    """
    Создает файл-переадресацию для лог-файла.
    
    Args:
        log_file: Имя лог-файла
    
    Returns:
        bool: True в случае успеха, False при ошибке
    """
    redirector_path = os.path.join(ROOT_DIR, log_file)
    target_path = os.path.join('advising_platform', 'data', 'logs', log_file)
    
    # Проверяем, нужно ли создавать переадресацию
    if os.path.exists(redirector_path):
        logger.info(f"Файл {redirector_path} уже существует, пропускаем")
        return False
    
    redirector_content = f"""# Файл перемещен
# {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Этот файл был перемещен в новое расположение в рамках реорганизации проекта.

Новый путь: {target_path}

Для доступа к актуальным логам используйте новый путь.
"""
    
    try:
        with open(redirector_path, 'w', encoding='utf-8') as f:
            f.write(redirector_content)
        logger.info(f"Создан файл-переадресация для {log_file}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при создании файла-переадресации для {log_file}: {e}")
        return False

def main():
    """
    Основная функция скрипта.
    """
    logger.info("Начало создания переадресаций для лог-файлов")
    
    success_count = 0
    for log_file in LOG_FILES:
        if create_redirector(log_file):
            success_count += 1
    
    logger.info(f"Создание переадресаций завершено. Успешно: {success_count}/{len(LOG_FILES)}")
    print(f"Создание переадресаций завершено. Успешно: {success_count}/{len(LOG_FILES)}")

if __name__ == "__main__":
    main()