#!/usr/bin/env python3
"""
Скрипт для обновления формата задач в todo.md
и архивации выполненных задач.

Автоматизирует следующие процессы:
1. Архивация выполненных задач
2. Обновление формата оставшихся задач по новому стандарту
"""

import re
import os
from datetime import datetime

# Файлы для обработки
TODO_FILE = '../../[todo · incidents]/todo.md'
ARCHIVE_FILE = '../../[todo · incidents]/todo.archive.md'
BACKUP_FILE = f'../../[todo · incidents]/todo.md.bak_{datetime.now().strftime("%d%b%Y").lower()}'

# Логические идентификаторы документов
TODO_LOGICAL_ID = "task:todo"
ARCHIVE_LOGICAL_ID = "task:todo.archive"

# Регулярные выражения для поиска задач
COMPLETED_TASK_PATTERN = r'- \[x\] \*\*(.*?)\*\*.*?$\n(?:(?:  - .*?$\n)*)'
INCOMPLETE_TASK_PATTERN = r'- \[ \] \*\*(.*?)\*\*(?:\s\|\s@(.*?)\s\|\sдо\s(.*?))?$\n(?:(?:  - .*?$\n)*)'
INCOMPLETE_UPDATED_PATTERN = r'- \[ \] \*\*(.*?)\*\*\s\[(.*?)\]\s·\s@(.*?)\s·\sдо\s(.*?)$\n\*\*цель\*\*:.*?(?:\n(?:\*\*.*?\*\*:(?:(?:\n.*?)+))+)'

# Новый формат задач с исправленным отступом
NEW_INCOMPLETE_UPDATED_PATTERN = r'- \[ \] \*\*(.*?)\*\*\s\[(.*?)\]\s·\s@(.*?)\s·\sдо\s(.*?)$\n\*\*цель\*\*:.*?(?:\n(?:\*\*.*?\*\*:(?:(?:\n- .*?)*)+))'

def backup_todo_file():
    """Создает резервную копию файла todo.md"""
    print(f"Создание резервной копии {TODO_FILE} в {BACKUP_FILE}...")
    with open(TODO_FILE, 'r', encoding='utf-8') as src:
        with open(BACKUP_FILE, 'w', encoding='utf-8') as dest:
            dest.write(src.read())
    print(f"Резервная копия создана: {BACKUP_FILE}")

def archive_completed_tasks():
    """Архивирует выполненные задачи из todo.md в todo.archive.md"""
    print("Архивация выполненных задач...")
    
    # Чтение файла todo.md
    with open(TODO_FILE, 'r', encoding='utf-8') as f:
        todo_content = f.read()
    
    # Подготовка архивного файла
    archive_header = f"# Архив задач\nЗадачи, перенесенные из todo.md {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
    
    if os.path.exists(ARCHIVE_FILE):
        with open(ARCHIVE_FILE, 'r', encoding='utf-8') as f:
            archive_content = f.read()
    else:
        archive_content = archive_header
    
    # Поиск выполненных задач
    completed_tasks = re.findall(COMPLETED_TASK_PATTERN, todo_content, re.MULTILINE | re.DOTALL)
    
    # Если нет выполненных задач, выходим
    if not completed_tasks:
        print("Выполненных задач не найдено.")
        return todo_content
    
    # Добавление выполненных задач в архив
    new_archive_content = archive_content
    if not archive_content.startswith("# Архив задач"):
        new_archive_content = archive_header + archive_content
    
    # Добавление секции с новыми архивированными задачами
    new_tasks_section = f"## Архивировано {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
    
    # Копирование выполненных задач в архив
    for task_match in re.finditer(COMPLETED_TASK_PATTERN, todo_content, re.MULTILINE | re.DOTALL):
        new_tasks_section += task_match.group(0) + "\n"
    
    new_archive_content = new_archive_content + new_tasks_section
    
    # Запись обновленного архива
    with open(ARCHIVE_FILE, 'w', encoding='utf-8') as f:
        f.write(new_archive_content)
    
    # Удаление выполненных задач из todo.md
    new_todo_content = re.sub(COMPLETED_TASK_PATTERN, '', todo_content, flags=re.MULTILINE | re.DOTALL)
    
    # Убираем лишние пустые строки
    new_todo_content = re.sub(r'\n{3,}', '\n\n', new_todo_content)
    
    print(f"Архивировано задач: {len(completed_tasks)}")
    return new_todo_content

def update_task_format(match):
    """Обновляет формат задачи по новому стандарту"""
    title = match.group(1)
    assignee = match.group(2) if match.group(2) else "ai assistant"
    deadline = match.group(3) if match.group(3) else ""
    
    # Извлекаем приоритет из заголовка, если есть
    priority_match = re.search(r'\[(.*?)\]', title)
    priority = priority_match.group(1).lower() if priority_match else "small task"
    title = re.sub(r'\s*\[.*?\]\s*', '', title).strip()
    
    lines = match.group(0).split('\n')
    
    # Находим цель, задачи и требования
    goal = ""
    tasks = []
    requirements = []
    
    for line in lines[1:]:
        line = line.strip()
        if line.startswith("- _Цель_:"):
            goal = line.replace("- _Цель_:", "").strip()
        elif line.startswith("- _Задачи_:"):
            tasks_text = line.replace("- _Задачи_:", "").strip()
            # Разбиваем задачи по нумерации "(N)"
            task_items = re.findall(r'\((\d+)\)(.*?)(?=\(\d+\)|$)', tasks_text)
            for _, task in task_items:
                tasks.append(task.strip().rstrip(';').strip())
        elif "етод" in line and line.startswith("- _"):
            # Строка с методом обычно содержит требования
            method = line.split(":", 1)[1].strip()
            requirements.append(method)
        elif line.startswith("- ") and not line.startswith("- _"):
            # Это может быть отдельная подзадача или требование
            if any(keyword in line.lower() for keyword in ["должен", "требуется", "необходимо"]):
                requirements.append(line[2:].strip())
            else:
                tasks.append(line[2:].strip())
    
    # Формируем новый формат задачи
    new_task = f"- [ ] **{title}** [{priority}] · @{assignee.lower()}"
    if deadline:
        new_task += f" · до {deadline}"
    new_task += "\n"
    
    # Добавляем цель
    new_task += f"**цель**: {goal if goal else 'необходимо заполнить'}\n"
    
    # Добавляем dod/result
    new_task += "**dod · result**: \n"
    for task in tasks[:3]:  # Используем первые 3 задачи как критерии результата
        new_task += f"- завершено: {task}\n"
    
    # Добавляем подзадачи
    new_task += "**подзадачи**: \n"
    for task in tasks:
        new_task += f"- [ ] {task}\n"
    
    # Добавляем требования
    new_task += "**требования**:\n"
    for req in requirements:
        new_task += f"- {req}\n"
    
    return new_task

def update_remaining_tasks(todo_content):
    """Обновляет формат оставшихся задач по новому стандарту"""
    print("Обновление формата оставшихся задач...")
    
    # Пропускаем уже обновленные задачи
    def replacement(match):
        # Проверяем, уже обновлена ли задача
        if re.search(r'\*\*цель\*\*:', match.group(0)):
            return match.group(0)  # Оставляем как есть
        else:
            return update_task_format(match)
    
    # Обновляем формат задач
    updated_content = re.sub(INCOMPLETE_TASK_PATTERN, replacement, todo_content, flags=re.MULTILINE | re.DOTALL)
    
    # Удаляем лишние пустые строки
    updated_content = re.sub(r'\n{3,}', '\n\n', updated_content)
    
    # Добавляем пустую строку между задачами для улучшения читабельности
    updated_content = re.sub(r'(\n\*\*требования\*\*:(?:\n- .*?)*\n)(?=- \[ \])', r'\1\n', updated_content)
    
    return updated_content

def main():
    """Основная функция скрипта"""
    # Создаем резервную копию
    backup_todo_file()
    
    # Чтение файла todo.md
    with open(TODO_FILE, 'r', encoding='utf-8') as f:
        todo_content = f.read()
    
    # Архивация выполненных задач
    updated_content = archive_completed_tasks()
    
    # Обновление формата оставшихся задач
    final_content = update_remaining_tasks(updated_content)
    
    # Запись обновленного файла todo.md
    with open(TODO_FILE, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print("Обработка завершена успешно!")

if __name__ == "__main__":
    main()