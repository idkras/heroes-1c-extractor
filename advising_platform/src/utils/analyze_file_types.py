#!/usr/bin/env python3
"""
Скрипт для анализа статистики по типам файлов в кеше и на диске.

Автор: AI Assistant
Дата: 21 мая 2025
"""

import os
import sys
import json
import logging
import re
from collections import Counter, defaultdict
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('file_type_analyzer')

def load_cache_data():
    """
    Загружает данные кеша из файла .cache_state.json.
    
    Returns:
        dict: Содержимое кеша или пустой словарь в случае ошибки
    """
    cache_file = ".cache_state.json"
    
    if not os.path.exists(cache_file):
        logger.error(f"Файл кеша {cache_file} не найден")
        return {}
    
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
            return cache_data
    except Exception as e:
        logger.error(f"Ошибка при чтении файла кеша: {e}")
        return {}

def get_disk_files():
    """
    Получает список файлов на диске, исключая скрытые и временные файлы.
    
    Returns:
        list: Список путей к файлам
    """
    exclude_dirs = set(['.git', '.cache', '.uv', '__pycache__', 'node_modules', 'venv', '.venv', '.idea', '.vscode'])
    exclude_extensions = set(['.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', '.cache'])
    
    disk_files = []
    
    for root, dirs, files in os.walk('.'):
        # Фильтруем директории, чтобы не обходить исключенные
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
        
        for file in files:
            # Фильтруем исключенные файлы
            ext = os.path.splitext(file)[1]
            if ext in exclude_extensions or file.startswith('.'):
                continue
            
            abs_path = os.path.abspath(os.path.join(root, file))
            rel_path = os.path.relpath(abs_path, '.')
            disk_files.append(rel_path)
    
    return disk_files

def group_by_extension(file_list):
    """
    Группирует список файлов по расширениям.
    
    Args:
        file_list: Список путей к файлам
        
    Returns:
        dict: Словарь {расширение: количество}
    """
    extensions = Counter()
    
    for file_path in file_list:
        ext = os.path.splitext(file_path)[1].lower()
        if ext:
            extensions[ext] += 1
        else:
            extensions['(без расширения)'] += 1
    
    return extensions

def group_by_directory(file_list):
    """
    Группирует список файлов по директориям верхнего уровня.
    
    Args:
        file_list: Список путей к файлам
        
    Returns:
        dict: Словарь {директория: количество}
    """
    directories = Counter()
    
    for file_path in file_list:
        parts = file_path.split(os.sep)
        if len(parts) > 1:
            top_dir = parts[0]
        else:
            top_dir = '(корневая директория)'
        
        directories[top_dir] += 1
    
    return directories

def analyze_file_sizes(file_list):
    """
    Анализирует размеры файлов.
    
    Args:
        file_list: Список путей к файлам
        
    Returns:
        dict: Статистика размеров файлов
    """
    size_stats = {
        'total_size': 0,
        'average_size': 0,
        'max_size': 0,
        'max_size_file': '',
        'size_distribution': {
            '0-1KB': 0,
            '1KB-10KB': 0,
            '10KB-100KB': 0,
            '100KB-1MB': 0,
            '1MB+': 0
        }
    }
    
    valid_files = 0
    
    for file_path in file_list:
        try:
            full_path = os.path.abspath(file_path)
            if os.path.exists(full_path):
                size = os.path.getsize(full_path)
                size_stats['total_size'] += size
                valid_files += 1
                
                if size > size_stats['max_size']:
                    size_stats['max_size'] = size
                    size_stats['max_size_file'] = file_path
                
                # Распределение размеров
                if size < 1024:  # 1KB
                    size_stats['size_distribution']['0-1KB'] += 1
                elif size < 10 * 1024:  # 10KB
                    size_stats['size_distribution']['1KB-10KB'] += 1
                elif size < 100 * 1024:  # 100KB
                    size_stats['size_distribution']['10KB-100KB'] += 1
                elif size < 1024 * 1024:  # 1MB
                    size_stats['size_distribution']['100KB-1MB'] += 1
                else:
                    size_stats['size_distribution']['1MB+'] += 1
        except Exception as e:
            logger.warning(f"Ошибка при получении размера файла {file_path}: {e}")
    
    if valid_files > 0:
        size_stats['average_size'] = size_stats['total_size'] / valid_files
    
    # Преобразуем размеры в человекочитаемый формат
    size_stats['total_size_human'] = format_size(size_stats['total_size'])
    size_stats['average_size_human'] = format_size(size_stats['average_size'])
    size_stats['max_size_human'] = format_size(size_stats['max_size'])
    
    return size_stats

def format_size(size_bytes):
    """
    Форматирует размер в байтах в человекочитаемый формат.
    
    Args:
        size_bytes: Размер в байтах
        
    Returns:
        str: Отформатированный размер
    """
    if size_bytes == 0:
        return "0B"
    
    size_names = ("B", "KB", "MB", "GB", "TB")
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.2f}{size_names[i]}"

def analyze_file_ages(file_list):
    """
    Анализирует возраст файлов.
    
    Args:
        file_list: Список путей к файлам
        
    Returns:
        dict: Статистика возраста файлов
    """
    age_stats = {
        'newest_file': '',
        'newest_file_time': 0,
        'oldest_file': '',
        'oldest_file_time': float('inf'),
        'age_distribution': {
            'сегодня': 0,
            '1-7 дней': 0,
            '8-30 дней': 0,
            'более 30 дней': 0
        }
    }
    
    now = datetime.now().timestamp()
    day_seconds = 24 * 60 * 60
    
    for file_path in file_list:
        try:
            full_path = os.path.abspath(file_path)
            if os.path.exists(full_path):
                mtime = os.path.getmtime(full_path)
                age_seconds = now - mtime
                
                # Самый новый и самый старый файл
                if mtime > age_stats['newest_file_time']:
                    age_stats['newest_file_time'] = mtime
                    age_stats['newest_file'] = file_path
                
                if mtime < age_stats['oldest_file_time']:
                    age_stats['oldest_file_time'] = mtime
                    age_stats['oldest_file'] = file_path
                
                # Распределение по возрасту
                if age_seconds < day_seconds:  # сегодня
                    age_stats['age_distribution']['сегодня'] += 1
                elif age_seconds < 7 * day_seconds:  # 1-7 дней
                    age_stats['age_distribution']['1-7 дней'] += 1
                elif age_seconds < 30 * day_seconds:  # 8-30 дней
                    age_stats['age_distribution']['8-30 дней'] += 1
                else:  # более 30 дней
                    age_stats['age_distribution']['более 30 дней'] += 1
        except Exception as e:
            logger.warning(f"Ошибка при получении времени модификации файла {file_path}: {e}")
    
    # Преобразуем времена в человекочитаемый формат
    if age_stats['newest_file_time'] > 0:
        age_stats['newest_file_time_human'] = datetime.fromtimestamp(
            age_stats['newest_file_time']).strftime('%Y-%m-%d %H:%M:%S')
    else:
        age_stats['newest_file_time_human'] = 'N/A'
    
    if age_stats['oldest_file_time'] < float('inf'):
        age_stats['oldest_file_time_human'] = datetime.fromtimestamp(
            age_stats['oldest_file_time']).strftime('%Y-%m-%d %H:%M:%S')
    else:
        age_stats['oldest_file_time_human'] = 'N/A'
    
    return age_stats

def generate_report(cache_files, disk_files):
    """
    Генерирует отчет о статистике файлов в кеше и на диске.
    
    Args:
        cache_files: Список файлов в кеше
        disk_files: Список файлов на диске
        
    Returns:
        dict: Отчет о статистике
    """
    # Находим файлы, которые есть только в кеше или только на диске
    cache_only = set(cache_files) - set(disk_files)
    disk_only = set(disk_files) - set(cache_files)
    both = set(cache_files) & set(disk_files)
    
    # Собираем статистику по расширениям
    cache_extensions = group_by_extension(cache_files)
    disk_extensions = group_by_extension(disk_files)
    
    # Собираем статистику по директориям
    cache_directories = group_by_directory(cache_files)
    disk_directories = group_by_directory(disk_files)
    
    # Анализируем размеры файлов на диске
    size_stats = analyze_file_sizes(disk_files)
    
    # Анализируем возраст файлов на диске
    age_stats = analyze_file_ages(disk_files)
    
    # Формируем отчет
    report = {
        'summary': {
            'cache_files': len(cache_files),
            'disk_files': len(disk_files),
            'cache_only': len(cache_only),
            'disk_only': len(disk_only),
            'both': len(both),
            'sync_percentage': (len(both) / max(len(set(cache_files) | set(disk_files)), 1)) * 100
        },
        'extensions': {
            'cache': dict(cache_extensions.most_common()),
            'disk': dict(disk_extensions.most_common())
        },
        'directories': {
            'cache': dict(cache_directories.most_common()),
            'disk': dict(disk_directories.most_common())
        },
        'size_stats': size_stats,
        'age_stats': age_stats,
        'sample_files': {
            'cache_only': list(cache_only)[:10],
            'disk_only': list(disk_only)[:10]
        }
    }
    
    return report

def print_report(report):
    """
    Выводит отчет в консоль.
    
    Args:
        report: Отчет о статистике
    """
    print("\n===== СТАТИСТИКА ФАЙЛОВ В КЕШЕ И НА ДИСКЕ =====\n")
    
    # Общая статистика
    print("== ОБЩАЯ СТАТИСТИКА ==")
    print(f"Файлов в кеше: {report['summary']['cache_files']}")
    print(f"Файлов на диске: {report['summary']['disk_files']}")
    print(f"Файлов только в кеше: {report['summary']['cache_only']}")
    print(f"Файлов только на диске: {report['summary']['disk_only']}")
    print(f"Файлов и в кеше, и на диске: {report['summary']['both']}")
    print(f"Степень синхронизации: {report['summary']['sync_percentage']:.2f}%")
    
    # Статистика по расширениям
    print("\n== РАСШИРЕНИЯ ФАЙЛОВ ==")
    print("Топ-10 расширений в кеше:")
    for ext, count in list(report['extensions']['cache'].items())[:10]:
        print(f"  {ext}: {count}")
    
    print("\nТоп-10 расширений на диске:")
    for ext, count in list(report['extensions']['disk'].items())[:10]:
        print(f"  {ext}: {count}")
    
    # Статистика по директориям
    print("\n== ДИРЕКТОРИИ ФАЙЛОВ ==")
    print("Топ-10 директорий в кеше:")
    for dir_name, count in list(report['directories']['cache'].items())[:10]:
        print(f"  {dir_name}: {count}")
    
    print("\nТоп-10 директорий на диске:")
    for dir_name, count in list(report['directories']['disk'].items())[:10]:
        print(f"  {dir_name}: {count}")
    
    # Статистика размеров файлов
    print("\n== РАЗМЕРЫ ФАЙЛОВ НА ДИСКЕ ==")
    print(f"Общий размер: {report['size_stats']['total_size_human']}")
    print(f"Средний размер: {report['size_stats']['average_size_human']}")
    print(f"Максимальный размер: {report['size_stats']['max_size_human']} ({report['size_stats']['max_size_file']})")
    
    print("\nРаспределение размеров:")
    for size_range, count in report['size_stats']['size_distribution'].items():
        print(f"  {size_range}: {count}")
    
    # Статистика возраста файлов
    print("\n== ВОЗРАСТ ФАЙЛОВ НА ДИСКЕ ==")
    print(f"Самый новый файл: {report['age_stats']['newest_file']} ({report['age_stats']['newest_file_time_human']})")
    print(f"Самый старый файл: {report['age_stats']['oldest_file']} ({report['age_stats']['oldest_file_time_human']})")
    
    print("\nРаспределение возраста:")
    for age_range, count in report['age_stats']['age_distribution'].items():
        print(f"  {age_range}: {count}")
    
    # Образцы файлов
    print("\n== ОБРАЗЦЫ ФАЙЛОВ ==")
    print("Примеры файлов только в кеше:")
    for file in report['sample_files']['cache_only']:
        print(f"  {file}")
    
    print("\nПримеры файлов только на диске:")
    for file in report['sample_files']['disk_only']:
        print(f"  {file}")

def main():
    """Основная функция скрипта."""
    logger.info("Запуск анализа статистики файлов в кеше и на диске")
    
    # Загружаем данные кеша
    cache_data = load_cache_data()
    cache_files = list(cache_data.get('files', {}).keys())
    logger.info(f"Загружено {len(cache_files)} файлов из кеша")
    
    # Получаем список файлов на диске
    disk_files = get_disk_files()
    logger.info(f"Найдено {len(disk_files)} файлов на диске")
    
    # Генерируем отчет
    report = generate_report(cache_files, disk_files)
    
    # Выводим отчет
    print_report(report)
    
    # Сохраняем отчет в файл
    try:
        with open('file_stats_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        logger.info("Отчет сохранен в файл file_stats_report.json")
    except Exception as e:
        logger.error(f"Ошибка при сохранении отчета: {e}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())