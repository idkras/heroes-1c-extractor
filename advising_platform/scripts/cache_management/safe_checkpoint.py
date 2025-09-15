#!/usr/bin/env python3
"""
Скрипт для безопасного создания чекпоинта.
Очищает ресурсы системы кэширования перед созданием чекпоинта,
что позволяет избежать ошибок из-за открытых файловых дескрипторов и активных потоков.
"""

import os
import sys
import time
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("safe_checkpoint")

# Добавляем корневую директорию проекта в sys.path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from advising_platform.src.cache.cleanup_handlers import cleanup_cache_observers
except ImportError as e:
    logger.error(f"Ошибка импорта: {e}")
    sys.exit(1)

def prepare_for_checkpoint() -> bool:
    """
    Подготавливает систему для безопасного создания чекпоинта.
    Останавливает наблюдателей за файлами и освобождает ресурсы.
    
    Returns:
        True, если подготовка прошла успешно, иначе False
    """
    logger.info("Подготовка к созданию чекпоинта...")
    
    # Очищаем ресурсы системы кэширования
    success = cleanup_cache_observers()
    
    if success:
        logger.info("Система подготовлена к созданию чекпоинта")
    else:
        logger.error("Не удалось подготовить систему к созданию чекпоинта")
    
    # Даем время на освобождение ресурсов
    time.sleep(1)
    
    return success

def main():
    """
    Основная функция скрипта.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Безопасное создание чекпоинта")
    parser.add_argument('--prepare', action='store_true', 
                         help='Подготовить систему к созданию чекпоинта')
    
    args = parser.parse_args()
    
    if args.prepare:
        success = prepare_for_checkpoint()
        print(f"Подготовка к созданию чекпоинта: {'успешно' if success else 'неудачно'}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()