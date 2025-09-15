#!/usr/bin/env python3
"""
Скрипт для инициализации системы кэширования.
Используется для настройки кэша с поддержкой обновленной файловой структуры.
"""

import os
import sys
import logging
import argparse
from typing import List, Optional

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("initialize_cache")

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath('.'))

try:
    from advising_platform.src.cache.document_cache import DocumentCacheManager
    from advising_platform.src.sync.core.path_mapper import PathMapper
except ImportError as e:
    logger.error(f"Ошибка импорта: {e}")
    logger.error("Убедитесь, что вы запускаете скрипт из корневой директории проекта")
    sys.exit(1)

def detect_standard_directories() -> List[str]:
    """
    Определяет стандартные директории в проекте.
    
    Returns:
        Список путей к стандартным директориям
    """
    standard_directories = []
    
    # Приоритетные директории
    priority_dirs = [
        '[standards .md]',
        '[todo · incidents]',
        '[projects]'
    ]
    
    # Проверяем существование директорий
    for directory in priority_dirs:
        if os.path.exists(directory):
            standard_directories.append(directory)
            logger.info(f"Обнаружена стандартная директория: {directory}")
    
    # Если не найдено ни одной директории, проверяем в advising_platform
    if not standard_directories:
        advising_platform_dirs = [
            'advising_platform/[standards .md]',
            'advising_platform/[todo · incidents]',
            'advising_platform/[projects]'
        ]
        
        for directory in advising_platform_dirs:
            if os.path.exists(directory):
                standard_directories.append(directory)
                logger.info(f"Обнаружена директория в advising_platform: {directory}")
    
    return standard_directories

def create_path_mapper(directories: List[str]) -> PathMapper:
    """
    Создает и настраивает PathMapper для указанных директорий.
    
    Args:
        directories: Список директорий
    
    Returns:
        Настроенный PathMapper
    """
    path_mapper = PathMapper()
    
    # Регистрируем основные маппинги
    for directory in directories:
        # Определяем логический и физический пути
        if '/' in directory:
            # Директория в advising_platform
            logical_dir = os.path.basename(directory)
            physical_dir = directory
        else:
            # Директория в корне
            logical_dir = directory
            physical_dir = f"./{directory}"
        
        # Регистрируем маппинг
        path_mapper.register_mapping(logical_dir, physical_dir)
        logger.info(f"Зарегистрирован маппинг: {logical_dir} -> {physical_dir}")
    
    return path_mapper

def initialize_cache(directories: Optional[List[str]] = None, max_cache_size: int = 200, force: bool = False) -> None:
    """
    Инициализирует систему кэширования.
    
    Args:
        directories: Список директорий для отслеживания
        max_cache_size: Максимальный размер кэша
    """
    # Если директории не указаны, определяем стандартные
    if directories is None:
        directories = detect_standard_directories()
    
    if not directories:
        logger.error("Не найдено ни одной директории для инициализации кэша")
        return
    
    # Получаем и инициализируем кэш
    try:
        cache_manager = DocumentCacheManager.get_instance(max_cache_size)
        
        # Создаем PathMapper для корректного преобразования путей
        path_mapper = create_path_mapper(directories)
        
        # Инициализируем кэш с указанными директориями
        cache_manager.initialize(directories)
        
        # Выводим статистику
        stats = cache_manager.get_statistics()
        logger.info(f"Статистика кэша после инициализации: {stats}")
        
        logger.info("Система кэширования успешно инициализирована")
        
    except Exception as e:
        logger.error(f"Ошибка при инициализации кэша: {e}")
        logger.exception(e)

def main():
    """
    Основная функция скрипта.
    """
    parser = argparse.ArgumentParser(description="Инициализация системы кэширования")
    parser.add_argument('--directories', '-d', nargs='+', help='Список директорий для отслеживания')
    parser.add_argument('--max-cache-size', '-m', type=int, default=200, help='Максимальный размер кэша')
    
    args = parser.parse_args()
    
    # Инициализируем кэш
    initialize_cache(args.directories, args.max_cache_size)

if __name__ == "__main__":
    main()