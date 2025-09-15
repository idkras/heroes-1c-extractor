#!/usr/bin/env python3
"""
Скрипт для автоматической архивации выполненных задач из todo.md в todo.archive.md,
используя абстрактные идентификаторы через API.
Поддерживает компактность и читаемость файла todo.md.
"""

import re
import os
import sys
import requests
from datetime import datetime

# Добавляем путь к директории скриптов в PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), 'document_tools'))

# Пытаемся импортировать модуль для работы с абстрактными идентификаторами
try:
    from abstract_links_tool import get_document, make_api_request
    ABSTRACT_API_AVAILABLE = True
except ImportError:
    print("Модуль abstract_links_tool недоступен. Используем прямой доступ к файлам.")
    ABSTRACT_API_AVAILABLE = False
    
    def make_api_request(endpoint, params=None, headers=None):
        """Заглушка для функции make_api_request в случае недоступности модуля."""
        try:
            url = f"{API_BASE_URL}/{endpoint}"
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Ошибка API запроса: {e}")
            return None

# Файлы для работы (резервные пути)
TODO_FILE = "../[todo · incidents]/todo.md" 
ARCHIVE_FILE = "../[todo · incidents]/todo.archive.md"

# Логические идентификаторы документов
TODO_LOGICAL_ID = "task:todo"
ARCHIVE_LOGICAL_ID = "task:todo.archive"

# URL API-сервера (по умолчанию)
API_BASE_URL = "http://localhost:5001/api"

def read_file(filename, use_abstract=True):
    """Читает содержимое файла, используя абстрактные идентификаторы, если возможно."""
    if use_abstract and ABSTRACT_API_AVAILABLE:
        if filename == TODO_FILE:
            logical_id = TODO_LOGICAL_ID
        elif filename == ARCHIVE_FILE:
            logical_id = ARCHIVE_LOGICAL_ID
        else:
            logical_id = None
        
        if logical_id:
            try:
                # Используем API для получения документа по логическому идентификатору
                response = make_api_request(f"abstract/document/{logical_id}")
                if response and "content" in response:
                    return response["content"]
            except Exception as e:
                print(f"Ошибка при получении документа через API: {e}")
    
    # Резервный вариант - прямое чтение файла
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Ошибка при чтении файла {filename}: {e}")
        return None

def write_file(filename, content, use_abstract=True):
    """Записывает содержимое в файл, используя абстрактные идентификаторы, если возможно."""
    if use_abstract and ABSTRACT_API_AVAILABLE:
        if filename == TODO_FILE:
            logical_id = TODO_LOGICAL_ID
        elif filename == ARCHIVE_FILE:
            logical_id = ARCHIVE_LOGICAL_ID
        else:
            logical_id = None
        
        if logical_id:
            try:
                # Получаем информацию о документе, чтобы узнать его настоящий путь
                response = make_api_request(f"abstract/document/{logical_id}")
                if response and "path" in response:
                    real_path = response["path"]
                    try:
                        with open(real_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"Файл успешно обновлен через логический идентификатор: {logical_id}")
                        return True
                    except Exception as e:
                        print(f"Ошибка при записи по пути {real_path}: {e}")
            except Exception as e:
                print(f"Ошибка при использовании API для записи: {e}")
    
    # Резервный вариант - прямая запись в файл
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Ошибка при записи в файл {filename}: {e}")
        return False

def parse_todo_file(content):
    """Разбирает файл todo.md на заголовок и задачи."""
    # Находим метаданные и правила (все до '## 🔜 Следующие действия')
    header_match = re.search(r'^(.*?## 🔜 Следующие действия)', content, re.DOTALL)
    if not header_match:
        print("Не удалось найти раздел '## 🔜 Следующие действия'")
        return None, None
    
    header = header_match.group(1)
    tasks = content[header_match.start() + len(header):]
    
    return header, tasks

def extract_completed_tasks(tasks):
    """
    Извлекает выполненные задачи и разделяет их по разделам.
    Возвращает список выполненных задач и обновленное содержимое задач.
    """
    completed_tasks = []
    current_section = "Общие задачи"
    current_priority = "P2"
    
    # Разделяем на строки
    lines = tasks.split('\n')
    updated_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Определяем текущий раздел
        section_match = re.match(r'^###\s+(.+?)\s*(\[P\d\])?', line)
        if section_match:
            current_section = section_match.group(1).strip()
            current_priority = section_match.group(2) if section_match.group(2) else "P2"
        
        # Проверяем, является ли строка выполненной задачей (поддерживаем оба формата: с 🟢 и без)
        task_match = re.match(r'^-\s+(?:🟢\s+)?\[x\]\s+(.+?)\s*(\(\d+.*?\))?$', line)
        if task_match:
            task_text = task_match.group(1).strip()
            completion_date = task_match.group(2) if task_match.group(2) else f"({datetime.now().strftime('%d %b %Y')})"
            
            # Собираем все связанные строки задачи (описание, результаты и т.д.)
            task_lines = [f"- ✅ {task_text} {completion_date}"]
            j = i + 1
            
            # Собираем подпункты задачи, пока не дойдем до следующей задачи или раздела
            while j < len(lines) and (lines[j].startswith('  - ') or lines[j].startswith('🟢 - ') or lines[j].strip() == ''):
                # Если это результат, добавляем его к задаче
                if '📝 Результат:' in lines[j]:
                    # Удаляем 🟢 если есть
                    clean_line = lines[j].replace('🟢 - ', '  - ')
                    task_lines.append(clean_line.replace('  - 📝 Результат:', '  - Результат:'))
                # Для других подпунктов, которые нужно сохранить в архиве
                elif any(marker in lines[j] for marker in ['✅', '📝 Результат:']):
                    task_lines.append(lines[j].replace('🟢 - ', '  - '))
                elif lines[j].startswith('  - _'):
                    # Добавляем подпункты нового формата
                    task_lines.append(lines[j])
                j += 1
            
            # Добавляем задачу в список выполненных
            completed_tasks.append({
                'section': current_section,
                'priority': current_priority,
                'task': '\n'.join(task_lines)
            })
            
            # Пропускаем обработанные строки задачи
            i = j - 1
        else:
            # Сохраняем строку в обновленном содержимом
            updated_lines.append(line)
        
        i += 1
    
    return completed_tasks, '\n'.join(updated_lines)

def update_archive_file(archive_content, completed_tasks):
    """Обновляет файл архива, добавляя новые завершенные задачи."""
    today = datetime.now().strftime("%d %B %Y")
    
    # Если файл архива пуст или не содержит раздела текущей даты, добавляем его
    if not archive_content or f"#### Выполнено {today}:" not in archive_content:
        # Находим раздел с текущей неделей или создаем его
        week_start = (datetime.now().day // 7) * 7 + 1
        week_end = min(week_start + 6, 31)  # Примерный конец недели
        current_week_section = f"### Неделя {week_start}-{week_end} мая 2025"
        
        if current_week_section not in archive_content:
            # Добавляем раздел текущей недели после раздела текущего месяца
            month_section = "## 📅 Май 2025"
            if month_section in archive_content:
                parts = archive_content.split(month_section)
                archive_content = f"{parts[0]}{month_section}\n\n{current_week_section}\n\n#### Выполнено {today}:\n{parts[1]}"
            else:
                # Если нет раздела текущего месяца, добавляем его
                archive_content += f"\n\n## 📅 Май 2025\n\n{current_week_section}\n\n#### Выполнено {today}:\n"
        else:
            # Если раздел текущей недели уже есть, но нет раздела текущей даты
            parts = archive_content.split(current_week_section)
            archive_content = f"{parts[0]}{current_week_section}\n\n#### Выполнено {today}:\n{parts[1]}"
    
    # Добавляем задачи в раздел текущей даты
    tasks_by_section = {}
    for task in completed_tasks:
        section = task['section']
        if section not in tasks_by_section:
            tasks_by_section[section] = []
        tasks_by_section[section].append(task['task'])
    
    # Формируем обновленное содержимое архива
    if f"#### Выполнено {today}:" in archive_content:
        # Если раздел текущей даты уже существует, добавляем задачи в него
        parts = archive_content.split(f"#### Выполнено {today}:")
        new_tasks = ""
        
        for section, tasks in tasks_by_section.items():
            if section != "Общие задачи":
                new_tasks += f"\n**{section}**:\n"
            new_tasks += '\n'.join(tasks) + '\n'
        
        # Объединяем части
        if len(parts) > 1:
            # Проверяем, есть ли уже содержимое после метки даты
            if parts[1].strip():
                archive_content = f"{parts[0]}#### Выполнено {today}:{new_tasks}{parts[1]}"
            else:
                archive_content = f"{parts[0]}#### Выполнено {today}:{new_tasks}"
        else:
            archive_content += new_tasks
    
    return archive_content

def update_metadata(content):
    """Обновляет метаданные файла с текущей датой и версией."""
    today = datetime.now().strftime("%d May %Y, %H:%M CET")
    
    # Обновляем строку с датой обновления
    updated_pattern = r'updated: .*'
    if re.search(updated_pattern, content):
        content = re.sub(updated_pattern, f'updated: {today} by AI Assistant', content)
    
    return content

def main():
    """Основная функция скрипта."""
    print("Начинаем архивацию выполненных задач...")
    
    # Чтение файлов
    todo_content = read_file(TODO_FILE)
    archive_content = read_file(ARCHIVE_FILE)
    
    if not todo_content or not archive_content:
        print("Ошибка: не удалось прочитать файлы")
        return
    
    # Разбираем todo.md
    header, tasks = parse_todo_file(todo_content)
    if not header or not tasks:
        print("Ошибка: не удалось разобрать структуру todo.md")
        return
    
    # Извлекаем выполненные задачи
    completed_tasks, updated_tasks = extract_completed_tasks(tasks)
    
    if not completed_tasks:
        print("Нет выполненных задач для архивации")
        return
    
    print(f"Найдено {len(completed_tasks)} выполненных задач")
    
    # Обновляем файл архива
    updated_archive = update_archive_file(archive_content, completed_tasks)
    
    # Обновляем метаданные файлов
    updated_archive = update_metadata(updated_archive)
    updated_todo = update_metadata(header + updated_tasks)
    
    # Записываем обновленные файлы
    if write_file(ARCHIVE_FILE, updated_archive):
        print(f"Файл {ARCHIVE_FILE} успешно обновлен")
    
    if write_file(TODO_FILE, updated_todo):
        print(f"Файл {TODO_FILE} успешно обновлен")
    
    print("Архивация завершена успешно")

if __name__ == "__main__":
    main()