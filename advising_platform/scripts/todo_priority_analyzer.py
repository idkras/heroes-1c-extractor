#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для анализа и приоритизации задач в todo.md.

Анализирует содержимое todo.md, отслеживает изменения в стандартах и обновлениях,
добавляет метки приоритетов и автоматически сортирует задачи по важности.
Также учитывает инциденты и связи между задачами.
"""

import os
import re
import sys
import datetime
import argparse
from typing import List, Dict, Tuple, Set, Optional
from collections import defaultdict

# Константы
TODO_FILE = "todo.md"
INCIDENT_DIR = "incidents"
STANDARDS_DIR = "advising standards .md"

# Приоритеты задач
PRIORITY_CRITICAL = "🔴"  # Критический приоритет
PRIORITY_HIGH = "🟠"      # Высокий приоритет
PRIORITY_MEDIUM = "🟡"    # Средний приоритет
PRIORITY_LOW = "🟢"       # Низкий приоритет
PRIORITY_INFO = "🔵"      # Информационный приоритет

# Стандартные метки
MARK_DONE = "[x]"         # Выполнено
MARK_PENDING = "[ ]"      # Ожидает выполнения
MARK_IN_PROGRESS = "[-]"  # В процессе выполнения

# Регулярные выражения
RE_TASK = re.compile(r'^-\s+(\[[\sx-]\])\s+(.*?)(\s+\(([\w-]+)\))?$')
RE_INCIDENT_REF = re.compile(r'инцидент\s+(\d{8}-\d{2})')
RE_SECTION_HEADER = re.compile(r'^#{1,4}\s+(.+)$')
RE_STANDARD_REF = re.compile(r'standard:(\w+)')
RE_PRIORITY_MARKER = re.compile(r'^(🔴|🟠|🟡|🟢|🔵)\s+')

class TodoItem:
    """Класс для представления элемента задачи."""
    
    def __init__(self, line: str, line_number: int, section: str = ""):
        """
        Инициализирует элемент задачи.
        
        Args:
            line: Строка с задачей
            line_number: Номер строки в файле
            section: Раздел, к которому относится задача
        """
        self.original_line = line
        self.line_number = line_number
        self.section = section
        self.priority = self._extract_priority(line)
        self.line_without_priority = self._remove_priority(line)
        
        # Извлекаем состояние, описание и теги из строки
        match = RE_TASK.match(self.line_without_priority)
        if match:
            self.state = match.group(1)
            self.description = match.group(2).strip()
            self.tag = match.group(4) if match.group(4) else ""
        else:
            self.state = "[ ]"
            self.description = self.line_without_priority.strip()
            self.tag = ""
        
        # Извлекаем ссылки на инциденты
        self.incident_refs = self._extract_incident_refs()
        # Извлекаем ссылки на стандарты
        self.standard_refs = self._extract_standard_refs()
        
        # Вычисляем базовый приоритет
        if not self.priority:
            self.priority = self._calculate_base_priority()
    
    def _extract_priority(self, line: str) -> str:
        """Извлекает маркер приоритета из строки."""
        match = RE_PRIORITY_MARKER.match(line)
        return match.group(1) if match else ""
    
    def _remove_priority(self, line: str) -> str:
        """Удаляет маркер приоритета из строки."""
        return RE_PRIORITY_MARKER.sub("", line)
    
    def _calculate_base_priority(self) -> str:
        """Вычисляет базовый приоритет на основе содержимого задачи."""
        if self.state == MARK_DONE:
            return PRIORITY_INFO  # Выполненные задачи имеют информационный приоритет
        
        # Задачи связанные с инцидентами имеют высокий приоритет
        if self.incident_refs:
            return PRIORITY_HIGH
        
        # Задачи связанные с основными стандартами имеют средний приоритет
        if any(ref in ["task_master", "registry", "incident"] for ref in self.standard_refs):
            return PRIORITY_MEDIUM
        
        # По умолчанию - низкий приоритет
        return PRIORITY_LOW
    
    def _extract_incident_refs(self) -> List[str]:
        """Извлекает ссылки на инциденты из описания задачи."""
        return RE_INCIDENT_REF.findall(self.description)
    
    def _extract_standard_refs(self) -> List[str]:
        """Извлекает ссылки на стандарты из описания задачи."""
        return RE_STANDARD_REF.findall(self.description)
    
    def update_priority(self, incident_priorities: Dict[str, str], 
                        standard_priorities: Dict[str, str]) -> None:
        """
        Обновляет приоритет задачи на основе связанных инцидентов и стандартов.
        
        Args:
            incident_priorities: Словарь приоритетов инцидентов
            standard_priorities: Словарь приоритетов стандартов
        """
        # По умолчанию используем базовый приоритет
        new_priority = self._calculate_base_priority()
        
        # Если задача связана с инцидентами, учитываем их приоритеты
        for incident_id in self.incident_refs:
            if incident_id in incident_priorities:
                incident_priority = incident_priorities[incident_id]
                # Используем самый высокий приоритет из связанных инцидентов
                if _priority_value(incident_priority) > _priority_value(new_priority):
                    new_priority = incident_priority
        
        # Если задача связана со стандартами, учитываем их приоритеты
        for standard_id in self.standard_refs:
            if standard_id in standard_priorities:
                standard_priority = standard_priorities[standard_id]
                # Для стандартов приоритет ниже, чем для инцидентов
                if (_priority_value(standard_priority) > _priority_value(new_priority) and
                    new_priority != PRIORITY_CRITICAL):
                    new_priority = standard_priority
        
        # Обновляем приоритет только если он отличается от текущего
        if new_priority != self.priority:
            self.priority = new_priority
    
    def to_string(self) -> str:
        """Преобразует элемент задачи в строку для записи в файл."""
        if self.state == MARK_DONE:
            # Для выполненных задач не добавляем приоритет
            return self.line_without_priority
        else:
            # Для невыполненных задач добавляем приоритет
            # Удаляем возможные предыдущие маркеры приоритета
            task_text = self.line_without_priority.strip()
            
            # Проверяем, начинается ли строка с "- [ ]"
            if task_text.startswith("- [ ]"):
                # Вставляем приоритет после "- [ ]"
                return f"- {self.priority} [ ] {task_text[5:].strip()}"
            else:
                # Добавляем приоритет в начало строки
                return f"{self.priority} {task_text}"
    
    def __str__(self) -> str:
        return self.to_string()

class TodoAnalyzer:
    """Класс для анализа и обновления todo.md."""
    
    def __init__(self, todo_file: str = TODO_FILE):
        """
        Инициализирует анализатор todo.md.
        
        Args:
            todo_file: Путь к файлу todo.md
        """
        self.todo_file = todo_file
        self.content = []
        self.sections = {}
        self.tasks = []
        self.incident_priorities = {}
        self.standard_priorities = {}
        
        # Загружаем содержимое файла
        self.load_content()
        # Анализируем структуру todo.md
        self.analyze_structure()
        # Загружаем информацию об инцидентах
        self.load_incident_priorities()
        # Загружаем информацию о стандартах
        self.load_standard_priorities()
    
    def load_content(self) -> None:
        """Загружает содержимое файла todo.md."""
        try:
            with open(self.todo_file, 'r', encoding='utf-8') as file:
                self.content = file.readlines()
        except FileNotFoundError:
            print(f"Файл {self.todo_file} не найден.")
            sys.exit(1)
    
    def analyze_structure(self) -> None:
        """Анализирует структуру файла todo.md."""
        current_section = ""
        
        for i, line in enumerate(self.content):
            # Проверяем, является ли строка заголовком раздела
            section_match = RE_SECTION_HEADER.match(line)
            if section_match:
                current_section = section_match.group(1).strip()
                self.sections[i] = current_section
                continue
            
            # Проверяем, является ли строка элементом списка (задачей)
            if line.strip().startswith("- "):
                task_item = TodoItem(line, i, current_section)
                self.tasks.append(task_item)
    
    def load_incident_priorities(self) -> None:
        """Загружает приоритеты инцидентов из файлов инцидентов."""
        if not os.path.isdir(INCIDENT_DIR):
            print(f"Директория {INCIDENT_DIR} не найдена.")
            return
        
        for filename in os.listdir(INCIDENT_DIR):
            if not filename.endswith(".md"):
                continue
            
            incident_id = filename.replace(".md", "")
            if "-" not in incident_id:
                continue
            
            file_path = os.path.join(INCIDENT_DIR, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                    # Ищем строку с приоритетом
                    priority_match = re.search(r'\*\*Приоритет\*\*:\s+(\w+)', content)
                    if priority_match:
                        priority_text = priority_match.group(1).lower()
                        
                        # Преобразуем текстовый приоритет в маркер
                        if priority_text == "критический":
                            self.incident_priorities[incident_id] = PRIORITY_CRITICAL
                        elif priority_text == "высокий":
                            self.incident_priorities[incident_id] = PRIORITY_HIGH
                        elif priority_text == "средний":
                            self.incident_priorities[incident_id] = PRIORITY_MEDIUM
                        elif priority_text == "низкий":
                            self.incident_priorities[incident_id] = PRIORITY_LOW
                        else:
                            self.incident_priorities[incident_id] = PRIORITY_MEDIUM
                    else:
                        # Если приоритет не указан, используем средний
                        self.incident_priorities[incident_id] = PRIORITY_MEDIUM
            except Exception as e:
                print(f"Ошибка при обработке инцидента {incident_id}: {e}")
    
    def load_standard_priorities(self) -> None:
        """Загружает приоритеты стандартов на основе их категорий."""
        if not os.path.isdir(STANDARDS_DIR):
            print(f"Директория {STANDARDS_DIR} не найдена.")
            return
        
        # Категоризация стандартов по номерам
        for filename in os.listdir(STANDARDS_DIR):
            if not filename.endswith(".md"):
                continue
            
            # Извлекаем номер стандарта (например, 0.1, 1.2, и т.д.)
            number_match = re.match(r'(\d+\.\d+)\s+(.+?)(?:\s+\d{1,2}\s+\w+\s+\d{4})', filename)
            if not number_match:
                continue
            
            standard_number = number_match.group(1)
            standard_name = number_match.group(2).strip()
            
            # Удаляем пробелы и специальные символы для создания идентификатора
            standard_id = re.sub(r'[^a-zA-Z0-9_]', '_', standard_name.lower())
            standard_id = re.sub(r'_+', '_', standard_id)
            
            # Определяем приоритет на основе категории стандарта
            if standard_number.startswith("0."):
                # Основополагающие стандарты имеют высокий приоритет
                self.standard_priorities[standard_id] = PRIORITY_HIGH
            elif standard_number.startswith("1."):
                # Обязательные рабочие стандарты имеют средний приоритет
                self.standard_priorities[standard_id] = PRIORITY_MEDIUM
            else:
                # Остальные стандарты имеют низкий приоритет
                self.standard_priorities[standard_id] = PRIORITY_LOW
    
    def update_task_priorities(self) -> None:
        """Обновляет приоритеты всех задач."""
        for task in self.tasks:
            task.update_priority(self.incident_priorities, self.standard_priorities)
    
    def sort_tasks_by_section(self) -> Dict[str, List[TodoItem]]:
        """
        Сортирует задачи по разделам и приоритетам.
        
        Returns:
            Словарь разделов с отсортированными задачами
        """
        tasks_by_section = defaultdict(list)
        
        for task in self.tasks:
            tasks_by_section[task.section].append(task)
        
        # Сортируем задачи в каждом разделе по приоритету
        for section in tasks_by_section:
            tasks_by_section[section] = sorted(
                tasks_by_section[section],
                key=lambda t: (_priority_value(t.priority), t.state != MARK_DONE)
            )
        
        return tasks_by_section
    
    def generate_updated_content(self) -> List[str]:
        """
        Генерирует обновленное содержимое todo.md.
        
        Returns:
            Список строк с обновленным содержимым
        """
        updated_content = self.content.copy()
        tasks_by_section = self.sort_tasks_by_section()
        
        # Для каждого раздела организуем задачи по приоритетам
        for section_line_num, section_name in self.sections.items():
            # Находим все задачи в текущем разделе
            section_tasks = tasks_by_section.get(section_name, [])
            if not section_tasks:
                continue
            
            # Находим все строки задач в текущем разделе
            task_line_nums = [task.line_number for task in section_tasks]
            
            # Находим начало и конец блока задач
            start_line = min(task_line_nums)
            end_line = max(task_line_nums)
            
            # Заменяем этот блок отсортированными задачами
            new_task_block = []
            for task in section_tasks:
                task_str = task.to_string()
                # Убедимся, что каждая задача оканчивается переносом строки
                if not task_str.endswith('\n'):
                    task_str += '\n'
                new_task_block.append(task_str)
            
            updated_content[start_line:end_line+1] = new_task_block
        
        return updated_content
    
    def save_updated_content(self, updated_content: List[str]) -> None:
        """
        Сохраняет обновленное содержимое в файл todo.md.
        
        Args:
            updated_content: Список строк с обновленным содержимым
        """
        # Создаем резервную копию текущего файла
        backup_file = f"{self.todo_file}.bak"
        try:
            with open(backup_file, 'w', encoding='utf-8') as file:
                file.writelines(self.content)
            
            # Записываем обновленное содержимое
            with open(self.todo_file, 'w', encoding='utf-8') as file:
                file.writelines(updated_content)
            
            print(f"Файл {self.todo_file} успешно обновлен.")
        except Exception as e:
            print(f"Ошибка при обновлении файла: {e}")
    
    def run(self) -> None:
        """Запускает процесс анализа и обновления todo.md."""
        # Обновляем приоритеты задач
        self.update_task_priorities()
        
        # Генерируем обновленное содержимое
        updated_content = self.generate_updated_content()
        
        # Сохраняем обновленное содержимое
        self.save_updated_content(updated_content)
        
        # Выводим статистику
        self._print_statistics()
    
    def _print_statistics(self) -> None:
        """Выводит статистику по задачам."""
        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for task in self.tasks if task.state == MARK_DONE)
        pending_tasks = sum(1 for task in self.tasks if task.state == MARK_PENDING)
        in_progress_tasks = sum(1 for task in self.tasks if task.state == MARK_IN_PROGRESS)
        
        critical_tasks = sum(1 for task in self.tasks if task.priority == PRIORITY_CRITICAL)
        high_tasks = sum(1 for task in self.tasks if task.priority == PRIORITY_HIGH)
        medium_tasks = sum(1 for task in self.tasks if task.priority == PRIORITY_MEDIUM)
        low_tasks = sum(1 for task in self.tasks if task.priority == PRIORITY_LOW)
        
        print("\n=== Статистика задач ===")
        print(f"Всего задач: {total_tasks}")
        print(f"Выполнено: {completed_tasks} ({completed_tasks/total_tasks*100:.1f}%)")
        print(f"В процессе: {in_progress_tasks} ({in_progress_tasks/total_tasks*100:.1f}%)")
        print(f"Ожидает выполнения: {pending_tasks} ({pending_tasks/total_tasks*100:.1f}%)")
        print("\nРаспределение по приоритетам:")
        print(f"{PRIORITY_CRITICAL} Критический: {critical_tasks}")
        print(f"{PRIORITY_HIGH} Высокий: {high_tasks}")
        print(f"{PRIORITY_MEDIUM} Средний: {medium_tasks}")
        print(f"{PRIORITY_LOW} Низкий: {low_tasks}")
        
        # Выводим информацию о задачах, связанных с инцидентами
        incident_tasks = [task for task in self.tasks if task.incident_refs]
        if incident_tasks:
            print("\nЗадачи, связанные с инцидентами:")
            for task in incident_tasks:
                if task.state != MARK_DONE:
                    incidents_str = ", ".join(task.incident_refs)
                    print(f"{task.priority} {task.description} (инциденты: {incidents_str})")

def _priority_value(priority: str) -> int:
    """
    Преобразует приоритет в числовое значение для сортировки.
    
    Args:
        priority: Маркер приоритета
    
    Returns:
        Числовое значение приоритета
    """
    priority_map = {
        PRIORITY_CRITICAL: 4,
        PRIORITY_HIGH: 3,
        PRIORITY_MEDIUM: 2,
        PRIORITY_LOW: 1,
        PRIORITY_INFO: 0
    }
    return priority_map.get(priority, 0)

def main():
    """Основная функция."""
    parser = argparse.ArgumentParser(description="Скрипт для анализа и обновления todo.md")
    parser.add_argument("--todo-file", default=TODO_FILE, help="Путь к файлу todo.md")
    args = parser.parse_args()
    
    analyzer = TodoAnalyzer(args.todo_file)
    analyzer.run()

if __name__ == "__main__":
    main()