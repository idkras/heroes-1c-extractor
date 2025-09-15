#!/usr/bin/env python3
"""
Скрипт для архивации завершенных задач из todo.md в архивный файл.

Выполняет следующие действия:
1. Читает todo.md
2. Находит задачи с отметкой "✓" или "[x]"
3. Перемещает их в файл todo.archive.md с добавлением даты архивации
4. Сохраняет обновленный todo.md без архивированных задач
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Определение корневой директории проекта
ROOT_DIR = Path(__file__).parent.parent.parent.parent.parent

# Пути к файлам
TODO_FILE = ROOT_DIR / "[todo · incidents]/todo.md"
ARCHIVE_FILE = ROOT_DIR / "[todo · incidents]/todo.archive.md"

def parse_todo_file(file_path):
    """
    Разбирает файл todo.md на заголовок и задачи.
    
    Returns:
        tuple: (header, tasks, non_tasks) - заголовок, задачи и остальной контент
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Определяем заголовок (всё до первого раздела с задачами)
        header_end = re.search(r'^##\s+.*?$', content, re.MULTILINE)
        if header_end:
            header = content[:header_end.start()]
            main_content = content[header_end.start():]
        else:
            header = ""
            main_content = content
        
        # Находим задачи и остальной контент
        tasks = []
        non_tasks = []
        
        section = None
        section_content = []
        
        for line in main_content.split('\n'):
            # Новый раздел
            if line.startswith('##'):
                if section is not None:
                    if len(section_content) > 0:
                        if section == 'task':
                            tasks.append((section_title, section_content))
                        else:
                            non_tasks.append((section_title, section_content))
                
                section_title = line
                section_content = []
                
                # Определяем, раздел с задачами или нет
                if re.search(r'##\s+(🔜|Следующие действия|ToDo|Задачи)', line, re.IGNORECASE):
                    section = 'task'
                else:
                    section = 'non-task'
            else:
                section_content.append(line)
        
        # Добавляем последний раздел
        if section is not None and len(section_content) > 0:
            if section == 'task':
                tasks.append((section_title, section_content))
            else:
                non_tasks.append((section_title, section_content))
        
        return (header, tasks, non_tasks)
    
    except Exception as e:
        print(f"Ошибка при разборе файла todo.md: {e}")
        sys.exit(1)

def is_completed_task(line):
    """
    Проверяет, является ли строка завершенной задачей.
    
    Args:
        line (str): Строка для проверки
        
    Returns:
        bool: True, если задача завершена, иначе False
    """
    return (
        (line.strip().startswith("- [x]") or line.strip().startswith("- [X]")) or
        (line.strip().startswith("* [x]") or line.strip().startswith("* [X]")) or
        (line.strip().startswith("✓") or "✓" in line.strip()[:5])
    )

def archive_completed_tasks(tasks):
    """
    Архивирует завершенные задачи.
    
    Args:
        tasks (list): Список кортежей (section_title, section_content)
        
    Returns:
        tuple: (active_tasks, archived_tasks) - активные и архивированные задачи
    """
    active_tasks = []
    archived_tasks = []
    
    for section_title, section_content in tasks:
        active_section_content = []
        archived_section_content = []
        
        for line in section_content:
            if line.strip() and is_completed_task(line):
                archived_section_content.append(line)
            else:
                active_section_content.append(line)
        
        if archived_section_content:
            archived_tasks.append((section_title, archived_section_content))
        
        if active_section_content:
            active_tasks.append((section_title, active_section_content))
    
    return active_tasks, archived_tasks

def save_todo_file(file_path, header, tasks, non_tasks):
    """
    Сохраняет обновленный файл todo.md.
    
    Args:
        file_path (str): Путь к файлу
        header (str): Заголовок файла
        tasks (list): Список кортежей (section_title, section_content) с активными задачами
        non_tasks (list): Список кортежей (section_title, section_content) с остальным контентом
    """
    content = header
    
    # Добавляем разделы с задачами
    for section_title, section_content in tasks:
        content += section_title + '\n'
        content += '\n'.join(section_content) + '\n\n'
    
    # Добавляем остальные разделы
    for section_title, section_content in non_tasks:
        content += section_title + '\n'
        content += '\n'.join(section_content) + '\n\n'
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def update_archive_file(file_path, archived_tasks):
    """
    Обновляет архивный файл, добавляя в него завершенные задачи.
    
    Args:
        file_path (str): Путь к архивному файлу
        archived_tasks (list): Список кортежей (section_title, section_content) с архивированными задачами
    """
    # Создаем заголовок для новых архивированных задач
    now = datetime.now()
    archive_date = now.strftime("%Y-%m-%d %H:%M")
    archive_header = f"## Архивировано {archive_date}\n\n"
    
    # Формируем содержимое для добавления
    content = archive_header
    
    for section_title, section_content in archived_tasks:
        # Удаляем '##' из заголовка раздела и добавляем '###'
        section_name = section_title.strip().lstrip('#').strip()
        content += f"### {section_name}\n"
        content += '\n'.join(section_content) + '\n\n'
    
    # Проверяем, существует ли архивный файл
    if os.path.exists(file_path):
        # Если файл существует, добавляем новое содержимое в начало
        with open(file_path, 'r', encoding='utf-8') as f:
            existing_content = f.read()
        
        content = content + existing_content
    
    # Сохраняем обновленный архивный файл
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    """Основная функция скрипта."""
    print(f"Архивация завершенных задач из {TODO_FILE} в {ARCHIVE_FILE}")
    
    # Разбираем файл todo.md
    header, tasks, non_tasks = parse_todo_file(TODO_FILE)
    
    # Архивируем завершенные задачи
    active_tasks, archived_tasks = archive_completed_tasks(tasks)
    
    # Если есть архивированные задачи
    if archived_tasks:
        # Обновляем архивный файл
        update_archive_file(ARCHIVE_FILE, archived_tasks)
        
        # Сохраняем обновленный todo.md
        save_todo_file(TODO_FILE, header, active_tasks, non_tasks)
        
        print(f"Архивировано {sum(len(content) for _, content in archived_tasks)} завершенных задач")
    else:
        print("Нет завершенных задач для архивации")

if __name__ == "__main__":
    main()