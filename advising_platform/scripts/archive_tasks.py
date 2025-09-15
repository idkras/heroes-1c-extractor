#!/usr/bin/env python3
"""
Скрипт для архивации завершенных задач.
Автоматически перемещает выполненные задачи из todo.md в todo.archive.md
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path

def archive_completed_tasks():
    """Архивирует завершенные задачи из todo.md в todo.archive.md"""
    
    todo_path = Path("[todo · incidents]/todo.md")
    archive_path = Path("[todo · incidents]/todo.archive.md")
    
    if not todo_path.exists():
        print(f"❌ Файл {todo_path} не найден")
        return False
        
    try:
        # Читаем todo.md
        with open(todo_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Находим завершенные задачи (с [x])
        completed_tasks = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if re.match(r'^\s*-\s*\[x\]', line):
                # Это завершенная задача
                task_block = [line]
                # Собираем все строки задачи до следующей задачи
                j = i + 1
                while j < len(lines) and not re.match(r'^\s*-\s*\[', lines[j]):
                    if lines[j].strip():  # Не пустая строка
                        task_block.append(lines[j])
                    j += 1
                
                completed_tasks.append('\n'.join(task_block))
        
        if completed_tasks:
            # Добавляем в архив
            archive_content = f"\n\n## Архивировано {datetime.now().strftime('%d %B %Y, %H:%M CET')}\n\n"
            archive_content += '\n\n'.join(completed_tasks)
            
            with open(archive_path, 'a', encoding='utf-8') as f:
                f.write(archive_content)
                
            print(f"✅ Архивировано {len(completed_tasks)} задач в {archive_path}")
            return True
        else:
            print("ℹ️ Завершенных задач для архивации не найдено")
            return True
            
    except Exception as e:
        print(f"❌ Ошибка при архивации: {e}")
        return False

if __name__ == "__main__":
    success = archive_completed_tasks()
    sys.exit(0 if success else 1)
