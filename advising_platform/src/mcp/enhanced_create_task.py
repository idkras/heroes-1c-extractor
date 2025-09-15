#!/usr/bin/env python3
"""
Enhanced Create Task с Protocol Completion
Автономная реализация для задачи T034
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/home/runner/workspace')

def enhanced_create_task(request):
    """Создание задачи с Protocol Completion."""
    
    start_time = datetime.now()
    
    try:
        title = request.get("title", "")
        description = request.get("description", "")
        priority = request.get("priority", "normal")
        assignee = request.get("assignee", "@ai_assistant")
        
        print(f"🔌 MCP ОПЕРАЦИЯ НАЧАТА: create-task")
        print(f"📥 Параметры: title='{title}', priority={priority}")
        
        # Валидация входных данных
        if not title:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            result = {
                "success": False,
                "error": "Требуется заголовок задачи",
                "task_id": None
            }
            
            print(f"❌ MCP ОПЕРАЦИЯ ЗАВЕРШЕНА С ОШИБКОЙ")
            print(f"⏰ Время выполнения: {duration:.1f}мс")
            print(f"📤 Результат: Отсутствует заголовок")
            
            return result
        
        # Создаем задачу
        task_id = create_task_in_todo(title, description, priority, assignee)
        
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        result = {
            "success": True,
            "task_id": task_id,
            "title": title,
            "priority": priority,
            "assignee": assignee,
            "processing_time_ms": duration,
            "message": f"Задача {task_id} успешно создана"
        }
        
        # Protocol Completion: отчет об успехе
        print(f"✅ MCP ОПЕРАЦИЯ ЗАВЕРШЕНА УСПЕШНО")
        print(f"⏰ Время выполнения: {duration:.1f}мс")
        print(f"🆔 ID задачи: {task_id}")
        print(f"📝 Заголовок: {title}")
        print(f"🎯 Приоритет: {priority}")
        print(f"👤 Исполнитель: {assignee}")
        
        # Предлагаем следующие шаги
        suggest_task_next_steps(task_id, priority)
        
        return result
        
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        result = {
            "success": False,
            "error": str(e),
            "task_id": None,
            "message": "Ошибка при создании задачи"
        }
        
        print(f"❌ MCP ОПЕРАЦИЯ ЗАВЕРШЕНА С ОШИБКОЙ")
        print(f"⏰ Время выполнения: {duration:.1f}мс")
        print(f"🚨 Ошибка: {str(e)}")
        
        return result

def create_task_in_todo(title: str, description: str, priority: str, assignee: str) -> str:
    """Создает задачу в todo.md."""
    
    todo_path = Path("/home/runner/workspace/[todo · incidents]/todo.md")
    
    if not todo_path.exists():
        raise FileNotFoundError("todo.md не найден")
    
    # Читаем текущий todo.md
    with open(todo_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Определяем следующий номер задачи
    task_numbers = []
    lines = content.split('\n')
    for line in lines:
        if '**T0' in line and '**' in line:
            try:
                start = line.find('**T') + 3
                end = line.find('**', start)
                if end > start:
                    task_num = int(line[start:end])
                    task_numbers.append(task_num)
            except:
                continue
    
    next_task_num = max(task_numbers) + 1 if task_numbers else 35
    task_id = f"T{next_task_num:03d}"
    
    # Генерируем уникальный ID
    date_str = datetime.now().strftime("%-d %b %Y")
    task_unique_id = f"{date_str} .{next_task_num:03d}"
    due_date = datetime.now().strftime("%-d %b %Y")
    
    # Определяем секцию по приоритету
    if priority.upper() == "ALARM":
        section_marker = '<summary>🚨 ASAP Приоритет</summary>'
    elif priority.upper() == "HIGH":
        section_marker = '<summary>📋 Высокий приоритет</summary>'
    else:
        section_marker = '<summary>📝 Обычные задачи</summary>'
    
    # Создаем новую задачу
    new_task = f"""
- [ ] **{task_id}** {title} · {assignee} · до {due_date}
  **ID**: {task_unique_id}
  **output**: {description or 'Задача выполнена согласно требованиям'}
  **outcome**: результат автоматически создан через MCP команду
"""
    
    # Находим нужную секцию и добавляем задачу
    section_start = content.find(section_marker)
    if section_start == -1:
        # Если секции нет, добавляем в конец
        new_content = content + new_task
    else:
        section_end = content.find('</details>', section_start)
        if section_end == -1:
            new_content = content + new_task
        else:
            new_content = content[:section_end] + new_task + "\n" + content[section_end:]
    
    # Обновляем статистику
    active_tasks = len([line for line in new_content.split('\n') if '- [ ] **T' in line])
    stats_start = new_content.find('- **Активных задач**:')
    if stats_start != -1:
        stats_end = new_content.find('\n', stats_start)
        if stats_end != -1:
            new_stats = f"- **Активных задач**: {active_tasks}"
            new_content = new_content[:stats_start] + new_stats + new_content[stats_end:]
    
    # Сохраняем обновленный todo.md
    with open(todo_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return task_id

def suggest_task_next_steps(task_id: str, priority: str):
    """Предлагает следующие шаги для созданной задачи."""
    
    print(f"\n🎯 СЛЕДУЮЩИЕ ШАГИ ДЛЯ ЗАДАЧИ {task_id}:")
    
    if priority.upper() == "ALARM":
        print("🚨 КРИТИЧЕСКИЙ ПРИОРИТЕТ!")
        print("• Немедленно приступить к выполнению")
        print("• Мониторить прогресс каждые 30 минут")
    elif priority.upper() == "HIGH":
        print("📋 Высокий приоритет")
        print("• Запланировать выполнение в течение дня")
        print("• Проверить зависимости от других задач")
    else:
        print("📝 Обычный приоритет")
        print("• Включить в еженедельное планирование")
        print("• Оценить требуемые ресурсы")
    
    print(f"• Валидировать задачу через validate-compliance")
    print(f"• Создать подзадачи при необходимости")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        request_data = json.loads(sys.argv[1])
        result = enhanced_create_task(request_data)
        print("\n" + "="*60)
        print("РЕЗУЛЬТАТ СОЗДАНИЯ ЗАДАЧИ:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Enhanced Create Task с Protocol Completion")
        print("Использование: python enhanced_create_task.py '{\"title\": \"Название задачи\", \"description\": \"Описание\", \"priority\": \"high\"}'")