#!/usr/bin/env python3
"""
Скрипт для сравнения состояния кэша с файловой системой.
Используется для выявления и устранения рассинхронизации между кэшем и файловой системой.
"""

import os
import sys
import logging
import argparse
import datetime
from typing import Dict, Any, List, Set, Tuple, Optional

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("compare_cache")

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath('.'))

try:
    from advising_platform.src.cache.document_cache import DocumentCacheManager
    from advising_platform.src.sync.core.path_mapper import PathMapper
except ImportError as e:
    logger.error(f"Ошибка импорта: {e}")
    logger.error("Убедитесь, что вы запускаете скрипт из корневой директории проекта")
    sys.exit(1)

def scan_md_files(directories: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Сканирует указанные директории и возвращает информацию о найденных MD-файлах.
    
    Args:
        directories: Список директорий для сканирования
    
    Returns:
        Словарь с информацией о файлах {путь: {size, mtime, exists}}
    """
    files_info = {}
    
    for directory in directories:
        if not os.path.exists(directory):
            logger.warning(f"Директория не существует: {directory}")
            continue
        
        # Сканируем директорию рекурсивно
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(('.md', '.markdown')):
                    file_path = os.path.join(root, file)
                    
                    try:
                        stat_info = os.stat(file_path)
                        files_info[file_path] = {
                            'size': stat_info.st_size,
                            'mtime': stat_info.st_mtime,
                            'mtime_str': datetime.datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                            'exists': True
                        }
                    except Exception as e:
                        logger.error(f"Ошибка при получении информации о файле {file_path}: {e}")
    
    return files_info

def get_cache_state(cache_manager: DocumentCacheManager) -> Dict[str, Dict[str, Any]]:
    """
    Получает состояние кэша.
    
    Args:
        cache_manager: Менеджер кэша
    
    Returns:
        Словарь с информацией о кэшированных файлах {путь: {content_length, cached}}
    """
    # Получаем статистику кэша
    stats = cache_manager.get_statistics()
    
    # Извлекаем информацию о кэшированных документах
    cache_state = {}
    
    if hasattr(cache_manager, 'document_cache') and hasattr(cache_manager.document_cache, 'cached_documents'):
        for path, doc_info in cache_manager.document_cache.cached_documents.items():
            cache_state[path] = {
                'content_length': len(doc_info.get('content', '')),
                'cached': True,
                'last_accessed': doc_info.get('last_accessed'),
                'last_accessed_str': datetime.datetime.fromtimestamp(doc_info.get('last_accessed', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                'access_count': doc_info.get('access_count', 0)
            }
    
    return cache_state

def compare_cache_with_filesystem(
    cache_manager: DocumentCacheManager,
    directories: List[str],
    path_mapper: Optional[PathMapper] = None
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Сравнивает состояние кэша с файловой системой.
    
    Args:
        cache_manager: Менеджер кэша
        directories: Список директорий для сканирования
        path_mapper: Опциональный PathMapper для преобразования путей
    
    Returns:
        Кортеж из трех списков:
        - Файлы, которые есть в файловой системе, но отсутствуют в кэше
        - Файлы, которые есть в кэше, но отсутствуют в файловой системе
        - Файлы, размер которых отличается между кэшем и файловой системой
    """
    # Сканируем файлы в указанных директориях
    filesystem_files = scan_md_files(directories)
    
    # Получаем состояние кэша
    cache_state = get_cache_state(cache_manager)
    
    # Преобразуем пути в соответствии с PathMapper
    if path_mapper:
        mapped_filesystem_files = {}
        for path, info in filesystem_files.items():
            logical_path = path_mapper.to_logical(path)
            mapped_filesystem_files[logical_path] = info
        filesystem_files = mapped_filesystem_files
    
    # Сравниваем
    missing_in_cache = []
    missing_in_filesystem = []
    size_mismatch = []
    
    # Файлы, отсутствующие в кэше
    for path, info in filesystem_files.items():
        if path not in cache_state:
            missing_in_cache.append({
                'path': path,
                'filesystem_size': info['size'],
                'filesystem_mtime': info['mtime_str']
            })
    
    # Файлы, отсутствующие в файловой системе
    for path, info in cache_state.items():
        # Если путь есть в кэше, но отсутствует в файловой системе
        if path not in filesystem_files:
            # Пробуем преобразовать путь в физический, если используется PathMapper
            physical_path = path_mapper.to_physical(path) if path_mapper else path
            
            # Проверяем существование файла по физическому пути
            if not os.path.exists(physical_path):
                missing_in_filesystem.append({
                    'path': path,
                    'physical_path': physical_path if path_mapper else None,
                    'cache_size': info['content_length'],
                    'last_accessed': info['last_accessed_str'],
                    'access_count': info['access_count']
                })
    
    # Файлы с несоответствием размера
    for path, cache_info in cache_state.items():
        if path in filesystem_files:
            filesystem_info = filesystem_files[path]
            
            # Сравниваем размер
            if cache_info['content_length'] != filesystem_info['size']:
                size_mismatch.append({
                    'path': path,
                    'cache_size': cache_info['content_length'],
                    'filesystem_size': filesystem_info['size'],
                    'difference': cache_info['content_length'] - filesystem_info['size'],
                    'filesystem_mtime': filesystem_info['mtime_str'],
                    'last_accessed': cache_info['last_accessed_str']
                })
    
    return missing_in_cache, missing_in_filesystem, size_mismatch

def print_comparison_results(
    missing_in_cache: List[Dict[str, Any]],
    missing_in_filesystem: List[Dict[str, Any]],
    size_mismatch: List[Dict[str, Any]]
) -> None:
    """
    Выводит результаты сравнения.
    
    Args:
        missing_in_cache: Файлы, отсутствующие в кэше
        missing_in_filesystem: Файлы, отсутствующие в файловой системе
        size_mismatch: Файлы с несоответствием размера
    """
    print("\n" + "=" * 80)
    print(f"РЕЗУЛЬТАТЫ СРАВНЕНИЯ КЭША С ФАЙЛОВОЙ СИСТЕМОЙ")
    print("=" * 80 + "\n")
    
    # Файлы, отсутствующие в кэше
    print(f"\n1. Файлы, отсутствующие в кэше ({len(missing_in_cache)}):")
    if missing_in_cache:
        for idx, item in enumerate(missing_in_cache, 1):
            print(f"  {idx}. {item['path']}")
            print(f"     - Размер: {item['filesystem_size']} байт")
            print(f"     - Изменен: {item['filesystem_mtime']}")
    else:
        print("  Отсутствуют")
    
    # Файлы, отсутствующие в файловой системе
    print(f"\n2. Файлы, отсутствующие в файловой системе ({len(missing_in_filesystem)}):")
    if missing_in_filesystem:
        for idx, item in enumerate(missing_in_filesystem, 1):
            print(f"  {idx}. {item['path']}")
            if item['physical_path']:
                print(f"     - Физический путь: {item['physical_path']}")
            print(f"     - Размер в кэше: {item['cache_size']} байт")
            print(f"     - Последнее обращение: {item['last_accessed']}")
            print(f"     - Количество обращений: {item['access_count']}")
    else:
        print("  Отсутствуют")
    
    # Файлы с несоответствием размера
    print(f"\n3. Файлы с несоответствием размера ({len(size_mismatch)}):")
    if size_mismatch:
        for idx, item in enumerate(size_mismatch, 1):
            print(f"  {idx}. {item['path']}")
            print(f"     - Размер в кэше: {item['cache_size']} байт")
            print(f"     - Размер в файловой системе: {item['filesystem_size']} байт")
            print(f"     - Разница: {item['difference']} байт")
            print(f"     - Изменен: {item['filesystem_mtime']}")
            print(f"     - Последнее обращение: {item['last_accessed']}")
    else:
        print("  Отсутствуют")
    
    print("\n" + "=" * 80)
    
    # Общий итог
    total_issues = len(missing_in_cache) + len(missing_in_filesystem) + len(size_mismatch)
    if total_issues == 0:
        print("\nКэш полностью синхронизирован с файловой системой.")
    else:
        print(f"\nОбнаружено {total_issues} проблем синхронизации.")
    
    print("=" * 80 + "\n")

def fix_cache_issues(
    cache_manager: DocumentCacheManager,
    missing_in_cache: List[Dict[str, Any]],
    missing_in_filesystem: List[Dict[str, Any]],
    fix_mode: str = 'auto'
) -> None:
    """
    Исправляет проблемы синхронизации кэша с файловой системой.
    
    Args:
        cache_manager: Менеджер кэша
        missing_in_cache: Файлы, отсутствующие в кэше
        missing_in_filesystem: Файлы, отсутствующие в файловой системе
        fix_mode: Режим исправления ('auto', 'cache', 'filesystem')
    """
    if fix_mode == 'auto' or fix_mode == 'cache':
        # Исправление отсутствующих в кэше файлов путем их загрузки
        if missing_in_cache:
            print("\nЗагрузка отсутствующих файлов в кэш:")
            for idx, item in enumerate(missing_in_cache, 1):
                try:
                    path = item['path']
                    print(f"  {idx}/{len(missing_in_cache)} Загрузка {path}...")
                    cache_manager.get_document(path)
                    print(f"  ✓ Файл загружен в кэш")
                except Exception as e:
                    print(f"  ✗ Ошибка загрузки файла: {e}")
    
    if fix_mode == 'auto' or fix_mode == 'filesystem':
        # Исправление отсутствующих в файловой системе файлов путем их удаления из кэша
        if missing_in_filesystem:
            print("\nУдаление несуществующих файлов из кэша:")
            for idx, item in enumerate(missing_in_filesystem, 1):
                try:
                    path = item['path']
                    print(f"  {idx}/{len(missing_in_filesystem)} Удаление {path} из кэша...")
                    cache_manager.invalidate(path)
                    print(f"  ✓ Файл удален из кэша")
                except Exception as e:
                    print(f"  ✗ Ошибка удаления файла из кэша: {e}")

def main():
    """
    Основная функция скрипта.
    """
    parser = argparse.ArgumentParser(description="Сравнение состояния кэша с файловой системой")
    parser.add_argument('--directories', '-d', nargs='+', help='Список директорий для сканирования')
    parser.add_argument('--fix', '-f', choices=['auto', 'cache', 'filesystem', 'none'], default='none',
                      help='Режим исправления проблем: auto - автоматически, cache - загрузить отсутствующие в кэше, filesystem - удалить отсутствующие в файловой системе, none - только показать проблемы')
    
    args = parser.parse_args()
    
    # Определяем директории для сканирования
    directories = args.directories
    if not directories:
        # Стандартные директории
        standard_dirs = [
            '[standards .md]',
            '[todo · incidents]',
            '[projects]'
        ]
        
        # Проверяем существование директорий
        directories = [d for d in standard_dirs if os.path.exists(d)]
        
        if not directories:
            # Проверяем в advising_platform
            advising_platform_dirs = [
                'advising_platform/[standards .md]',
                'advising_platform/[todo · incidents]',
                'advising_platform/[projects]'
            ]
            
            directories = [d for d in advising_platform_dirs if os.path.exists(d)]
    
    if not directories:
        logger.error("Не найдено ни одной директории для сканирования")
        return
    
    logger.info(f"Директории для сканирования: {directories}")
    
    # Создаем PathMapper
    path_mapper = PathMapper()
    for directory in directories:
        if '/' in directory:
            # Директория в advising_platform
            logical_dir = os.path.basename(directory)
            physical_dir = directory
        else:
            # Директория в корне
            logical_dir = directory
            physical_dir = f"./{directory}"
        
        path_mapper.register_mapping(logical_dir, physical_dir)
    
    # Получаем менеджер кэша
    try:
        cache_manager = DocumentCacheManager.get_instance()
        
        # Если кэш не инициализирован, инициализируем его
        if not cache_manager.is_initialized:
            logger.info("Кэш не инициализирован, выполняем инициализацию...")
            cache_manager.initialize(directories)
        
        # Сравниваем состояние кэша с файловой системой
        missing_in_cache, missing_in_filesystem, size_mismatch = compare_cache_with_filesystem(
            cache_manager, directories, path_mapper
        )
        
        # Выводим результаты
        print_comparison_results(missing_in_cache, missing_in_filesystem, size_mismatch)
        
        # Исправляем проблемы, если указан соответствующий режим
        if args.fix != 'none':
            fix_cache_issues(cache_manager, missing_in_cache, missing_in_filesystem, args.fix)
            
            # Повторное сравнение после исправления
            if args.fix != 'none':
                print("\nПовторное сравнение после исправления проблем:\n")
                missing_in_cache, missing_in_filesystem, size_mismatch = compare_cache_with_filesystem(
                    cache_manager, directories, path_mapper
                )
                print_comparison_results(missing_in_cache, missing_in_filesystem, size_mismatch)
        
    except Exception as e:
        logger.error(f"Ошибка при работе с кэшем: {e}")
        logger.exception(e)

if __name__ == "__main__":
    main()