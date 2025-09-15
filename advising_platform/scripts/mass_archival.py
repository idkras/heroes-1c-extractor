#!/usr/bin/env python3
"""
Скрипт массовой архивации задач в todo.md.
Перемещает завершенные и дублирующиеся задачи в todo.archive.md.
"""

import re
from pathlib import Path
from datetime import datetime

def mass_archive_tasks():
    """Выполняет массовую архивацию задач."""
    
    todo_path = Path("../[todo · incidents]/todo.md")
    archive_path = Path("../[todo · incidents]/todo.archive.md")
    
    if not todo_path.exists():
        print(f"Файл {todo_path} не найден")
        return
    
    with open(todo_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Найдем все выполненные задачи
    completed_pattern = r'- \[x\] \*\*(T\d+)\*\* ([^\n]+(?:\n  [^\n]+)*)'
    completed_tasks = re.findall(completed_pattern, content, re.MULTILINE)
    
    print(f"Найдено завершенных задач: {len(completed_tasks)}")
    
    if completed_tasks:
        # Архивируем завершенные задачи
        with open(archive_path, 'a', encoding='utf-8') as f:
            f.write(f"\n## Массовая архивация - {datetime.now().strftime('%d %B %Y')}\n\n")
            
            for task_id, task_content in completed_tasks:
                f.write(f"- ✅ **{task_id}** {task_content.strip()}\n")
        
        # Удаляем заархивированные задачи из todo.md
        for task_id, task_content in completed_tasks:
            full_task = f"- [x] **{task_id}** {task_content}"
            content = content.replace(full_task, "")
        
        # Очищаем лишние пустые строки
        content = re.sub(r'\n\n\n+', '\n\n', content)
        
        # Сохраняем обновленный todo.md
        with open(todo_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Заархивировано {len(completed_tasks)} завершенных задач")
    else:
        print("Завершенные задачи не найдены")

if __name__ == "__main__":
    print("Массовая архивация задач")
    print("=" * 30)
    mass_archive_tasks()