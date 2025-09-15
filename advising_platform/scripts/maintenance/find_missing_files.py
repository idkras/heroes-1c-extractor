#!/usr/bin/env python3
"""
Скрипт для поиска конкретных файлов, отсутствующих в кеше.
"""

import os
import pickle
from pathlib import Path

# Пути к файлам состояния кеша
DETAILED_CACHE_STATE_FILE = '.cache_detailed_state.pickle'

def load_cache_files():
    """Загружает пути всех файлов из кеша."""
    try:
        if os.path.exists(DETAILED_CACHE_STATE_FILE):
            with open(DETAILED_CACHE_STATE_FILE, 'rb') as f:
                detailed_state = pickle.load(f)
                
                cache_files = set()
                for entry_key, entry_data in detailed_state.items():
                    if isinstance(entry_data, dict) and 'path' in entry_data:
                        cache_files.add(entry_data['path'])
                
                return cache_files
    except Exception as e:
        print(f"Ошибка загрузки детального состояния кеша: {e}")
    
    return set()

def get_filesystem_files(directories):
    """Получает список всех файлов в указанных директориях."""
    filesystem_files = set()
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            print(f"Директория {directory} не существует")
            continue
        
        for path in dir_path.rglob('*'):
            if path.is_file() and not any(part.startswith('.') for part in path.parts):
                # Исключаем файлы из архивов
                if not 'archive' in str(path):
                    filesystem_files.add(str(path))
    
    return filesystem_files

def find_missing_in_cache(filesystem_files, cache_files):
    """Находит файлы, отсутствующие в кеше."""
    return filesystem_files - cache_files

def main():
    """Основная функция скрипта."""
    # Директории для проверки
    directories = ['[standards .md]', '[todo · incidents]']
    
    # Загружаем файлы из кеша
    cache_files = load_cache_files()
    print(f"Загружено {len(cache_files)} файлов из кеша")
    
    # Получаем файлы из файловой системы
    filesystem_files = get_filesystem_files(directories)
    print(f"Найдено {len(filesystem_files)} файлов в файловой системе (без архивов)")
    
    # Находим файлы, отсутствующие в кеше
    missing_files = find_missing_in_cache(filesystem_files, cache_files)
    
    print(f"\nФайлы, отсутствующие в кеше ({len(missing_files)}):")
    for file in sorted(missing_files):
        print(f"- {file}")
    
    print("\nСтатистика по категориям отсутствующих файлов:")
    standards_count = sum(1 for file in missing_files if "[standards .md]" in file)
    todo_count = sum(1 for file in missing_files if "[todo · incidents]" in file and not "archive" in file)
    
    print(f"- Стандарты: {standards_count} файлов")
    print(f"- Задачи/инциденты: {todo_count} файлов")
    
    # Проверяем, какие файлы из кеша отсутствуют в файловой системе
    extra_files = {f for f in cache_files if f.startswith('[standards .md]') or f.startswith('[todo · incidents]')} - filesystem_files
    
    print(f"\nФайлы в кеше, отсутствующие в файловой системе ({len(extra_files)}):")
    for file in sorted(extra_files):
        print(f"- {file}")

if __name__ == "__main__":
    main()