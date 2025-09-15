#!/usr/bin/env python3
"""
Анализ задач в todo.md для массовой архивации.
Определяет дубли, завершенные и частично выполненные задачи.
"""

import re
from pathlib import Path
from typing import Dict, List, Set

def analyze_tasks(todo_path: str = "../[todo · incidents]/todo.md") -> Dict:
    """Анализирует все задачи в todo.md."""
    
    if not Path(todo_path).exists():
        return {"error": f"Файл {todo_path} не найден"}
    
    with open(todo_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Паттерн для поиска задач
    task_pattern = r'- \[([x ])\] \*\*(T\d+)\*\* ([^\n]+)'
    tasks = re.findall(task_pattern, content, re.MULTILINE)
    
    active_tasks = []
    completed_tasks = []
    task_titles = []
    
    for status, task_id, title in tasks:
        task_info = {
            'id': task_id,
            'title': title.strip(),
            'status': 'completed' if status == 'x' else 'active'
        }
        
        if status == 'x':
            completed_tasks.append(task_info)
        else:
            active_tasks.append(task_info)
            
        task_titles.append(title.strip().lower())
    
    # Поиск потенциальных дублей по ключевым словам
    potential_duplicates = []
    keywords = ['исправить', 'обновить', 'создать', 'проверить', 'анализ', 'интеграция']
    
    for keyword in keywords:
        matching_tasks = [t for t in active_tasks if keyword in t['title'].lower()]
        if len(matching_tasks) > 1:
            potential_duplicates.extend(matching_tasks)
    
    return {
        'total_tasks': len(tasks),
        'active_tasks': len(active_tasks),
        'completed_tasks': len(completed_tasks),
        'active_task_list': active_tasks,
        'completed_task_list': completed_tasks,
        'potential_duplicates': potential_duplicates,
        'archivable_count': len(completed_tasks)
    }

def main():
    """Основная функция анализа."""
    print("Анализ задач в todo.md")
    print("=" * 50)
    
    analysis = analyze_tasks()
    
    if 'error' in analysis:
        print(f"Ошибка: {analysis['error']}")
        return
    
    print(f"Всего задач: {analysis['total_tasks']}")
    print(f"Активных задач: {analysis['active_tasks']}")
    print(f"Завершенных задач: {analysis['completed_tasks']}")
    print(f"Потенциальных дублей: {len(analysis['potential_duplicates'])}")
    print(f"Готово к архивации: {analysis['archivable_count']}")
    
    print("\nЗавершенные задачи для архивации:")
    for task in analysis['completed_task_list']:
        print(f"  {task['id']}: {task['title'][:60]}...")
    
    if analysis['potential_duplicates']:
        print("\nПотенциальные дубли:")
        for task in analysis['potential_duplicates'][:5]:
            print(f"  {task['id']}: {task['title'][:60]}...")

if __name__ == "__main__":
    main()