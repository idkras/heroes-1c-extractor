#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Хук-скрипт для автоматического обновления todo.md при изменении стандартов.

Отслеживает изменения в стандартах и автоматически запускает анализатор todo.md.
Может использоваться в качестве хука Git или как часть процесса валидации стандартов.
"""

import os
import sys
import re
import subprocess
import datetime
import argparse
from typing import List, Optional

# Константы
STANDARDS_DIR = "advising standards .md"
TODO_FILE = "todo.md"
TODO_ANALYZER = "scripts/todo_priority_analyzer.py"

def is_standard_file(file_path: str) -> bool:
    """
    Проверяет, является ли файл стандартом.
    
    Args:
        file_path: Путь к файлу
    
    Returns:
        True если файл является стандартом, False в противном случае
    """
    if not file_path.endswith(".md"):
        return False
    
    is_in_standards_dir = file_path.startswith(STANDARDS_DIR)
    not_in_archive = "/archive/" not in file_path
    has_standard_name_pattern = bool(re.search(r'\d+\.\d+\s+.+\s+\d{1,2}\s+\w+\s+\d{4}', file_path))
    
    return is_in_standards_dir and not_in_archive and has_standard_name_pattern

def get_modified_standards(all_files: bool = False) -> List[str]:
    """
    Получает список измененных файлов стандартов.
    
    Args:
        all_files: Если True, возвращает все файлы стандартов
    
    Returns:
        Список путей к измененным файлам стандартов
    """
    if all_files:
        # Получаем все файлы стандартов
        standards = []
        for root, _, files in os.walk(STANDARDS_DIR):
            for file in files:
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    if is_standard_file(file_path):
                        standards.append(file_path)
        return standards
    else:
        # Получаем измененные файлы из Git
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "--cached"],
                capture_output=True, text=True, check=True
            )
            modified_files = result.stdout.strip().split("\n")
            return [f for f in modified_files if is_standard_file(f)]
        except subprocess.CalledProcessError:
            print("Ошибка при получении измененных файлов из Git.")
            return []
        except FileNotFoundError:
            print("Git не установлен или недоступен.")
            return []

def update_todo_file() -> bool:
    """
    Запускает скрипт анализа и обновления todo.md.
    
    Returns:
        True если обновление успешно, False в случае ошибки
    """
    try:
        result = subprocess.run(
            ["python", TODO_ANALYZER, f"--todo-file={TODO_FILE}"],
            capture_output=True, text=True, check=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при обновлении todo.md: {e}")
        print(f"Вывод: {e.stdout}")
        print(f"Ошибка: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"Скрипт {TODO_ANALYZER} не найден.")
        return False

def add_update_record() -> None:
    """Добавляет запись о последнем обновлении в todo.md."""
    try:
        with open(TODO_FILE, 'r', encoding='utf-8') as file:
            content = file.readlines()
        
        # Текущая дата и время
        now = datetime.datetime.now()
        timestamp = now.strftime("%d %b %Y, %H:%M CET")
        
        # Формируем запись об обновлении
        update_record = f"\n### Сессия {timestamp}\n"
        update_record += "- ✅ Выполнено автоматическое обновление приоритетов задач\n"
        update_record += "- ✅ Проведена проверка связей задач с инцидентами\n"
        update_record += "- ✅ Обновлена статистика выполнения задач\n"
        
        # Находим место для вставки записи (после заголовка "## Журнал обновлений")
        for i, line in enumerate(content):
            if line.startswith("## Журнал обновлений"):
                # Вставляем запись после заголовка
                content.insert(i+1, update_record)
                break
        else:
            # Если заголовок не найден, добавляем в конец файла
            content.append("\n## Журнал обновлений\n")
            content.append(update_record)
        
        # Записываем обновленное содержимое
        with open(TODO_FILE, 'w', encoding='utf-8') as file:
            file.writelines(content)
        
        print(f"Запись об обновлении добавлена в {TODO_FILE}")
    except Exception as e:
        print(f"Ошибка при добавлении записи об обновлении: {e}")

def main():
    """Основная функция."""
    parser = argparse.ArgumentParser(description="Хук для обновления todo.md при изменении стандартов")
    parser.add_argument("--all-files", action="store_true", help="Обработать все файлы стандартов")
    parser.add_argument("--silent", action="store_true", help="Не выводить подробную информацию")
    args = parser.parse_args()
    
    # Получаем список измененных стандартов
    modified_standards = get_modified_standards(args.all_files)
    
    if not modified_standards and not args.all_files:
        if not args.silent:
            print("Изменения стандартов не обнаружены.")
        return 0
    
    if not args.silent:
        print(f"Обнаружены изменения в {len(modified_standards)} файлах стандартов.")
        for file in modified_standards:
            print(f"  - {file}")
    
    # Обновляем todo.md
    success = update_todo_file()
    
    if success:
        # Добавляем запись об обновлении
        add_update_record()
        if not args.silent:
            print("todo.md успешно обновлен.")
        return 0
    else:
        if not args.silent:
            print("Не удалось обновить todo.md.")
        return 1

if __name__ == "__main__":
    sys.exit(main())