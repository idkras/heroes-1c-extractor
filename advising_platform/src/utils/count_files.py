#!/usr/bin/env python3
"""
Простой скрипт для быстрого подсчета файлов в папках [standards .md], [todo · incidents] и других
"""

import os
from pathlib import Path
import time

def count_files_by_category():
    """Подсчитывает количество файлов по категориям."""
    start_time = time.time()
    
    # Счетчики для статистики
    stats = {
        'standards': 0,
        'todo': 0,
        'incidents': 0,
        'other': 0,
        'total': 0,
    }
    
    # Проверяем существование директорий
    standards_dir = Path('[standards .md]')
    todo_incidents_dir = Path('[todo · incidents]')
    
    # Подсчитываем стандарты
    if standards_dir.exists():
        for root, dirs, files in os.walk(standards_dir):
            stats['standards'] += len(files)
            stats['total'] += len(files)
    
    # Подсчитываем задачи и инциденты
    if todo_incidents_dir.exists():
        for root, dirs, files in os.walk(todo_incidents_dir):
            for file in files:
                file_path = Path(root) / file
                file_path_str = str(file_path)
                
                if 'todo' in file_path_str.lower():
                    stats['todo'] += 1
                elif 'incident' in file_path_str.lower():
                    stats['incidents'] += 1
                else:
                    stats['other'] += 1
                
                stats['total'] += 1
    
    # Подсчитываем общее количество документов
    total_documents = 0
    for root, dirs, files in os.walk('.'):
        # Пропускаем скрытые директории
        if any(part.startswith('.') for part in Path(root).parts):
            continue
        
        # Пропускаем директорию node_modules
        if 'node_modules' in Path(root).parts:
            continue
        
        # Пропускаем директорию __pycache__
        if '__pycache__' in Path(root).parts:
            continue
        
        total_documents += len(files)
    
    stats['other_total'] = total_documents - stats['standards'] - stats['todo'] - stats['incidents']
    
    # Выводим результаты
    print("\n======== СТАТИСТИКА ФАЙЛОВ ========")
    print(f"Стандарты: {stats['standards']} файлов")
    print(f"Задачи: {stats['todo']} файлов")
    print(f"Инциденты: {stats['incidents']} файлов")
    print(f"Другие документы (в основных директориях): {stats['other']} файлов")
    print(f"Всего документов в основных директориях: {stats['total']} файлов")
    print(f"Всего файлов в проекте: {total_documents} файлов")
    
    print(f"\nВремя выполнения: {time.time() - start_time:.2f} секунд")
    
    return stats

def count_files_in_cache():
    """Подсчитывает количество файлов в кеше."""
    cache_state_file = ".cache_state.json"
    cache_detailed_state_file = ".cache_detailed_state.pickle"
    
    if not os.path.exists(cache_state_file) or not os.path.exists(cache_detailed_state_file):
        print("\n======== СТАТИСТИКА КЕША ========")
        print("Файлы состояния кеша не найдены.")
        return
    
    import json
    import pickle
    
    # Загружаем состояние кеша
    try:
        with open(cache_state_file, 'r', encoding='utf-8') as f:
            cache_state = json.load(f)
        
        with open(cache_detailed_state_file, 'rb') as f:
            detailed_state = pickle.load(f)
        
        # Подсчитываем количество документов в кеше
        cache_size = len(detailed_state) if isinstance(detailed_state, dict) else 0
        
        # Подсчитываем документы по категориям
        standards_count = 0
        todo_count = 0
        incidents_count = 0
        other_count = 0
        
        for key, entry in detailed_state.items():
            if not isinstance(entry, dict) or 'path' not in entry:
                continue
            
            path = entry['path']
            if '[standards .md]' in path:
                standards_count += 1
            elif '[todo · incidents]' in path and 'todo' in path.lower():
                todo_count += 1
            elif '[todo · incidents]' in path and 'incident' in path.lower():
                incidents_count += 1
            else:
                other_count += 1
        
        print("\n======== СТАТИСТИКА КЕША ========")
        print(f"Всего документов в кеше: {cache_size}")
        print(f"Стандарты: {standards_count} файлов")
        print(f"Задачи: {todo_count} файлов")
        print(f"Инциденты: {incidents_count} файлов")
        print(f"Другие документы: {other_count} файлов")
        
        # Выводим информацию о рассинхронизации
        disk_stats = count_files_by_category()
        
        print("\n======== РАССИНХРОНИЗАЦИЯ ========")
        print(f"Стандарты: {disk_stats['standards'] - standards_count} файлов отсутствуют в кеше")
        print(f"Задачи: {disk_stats['todo'] - todo_count} файлов отсутствуют в кеше")
        print(f"Инциденты: {disk_stats['incidents'] - incidents_count} файлов отсутствуют в кеше")
        print(f"Другие документы: не определено")
    
    except Exception as e:
        print(f"Ошибка при загрузке состояния кеша: {e}")

if __name__ == "__main__":
    count_files_by_category()
    count_files_in_cache()