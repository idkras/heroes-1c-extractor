#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль для форматирования задач и инцидентов согласно стандартам Task Master и Ticket Standard.

Основные функции:
1. Форматирование задач с уникальными ID (DD MMM YYYY .XXX)
2. Применение абсолютных приоритетов (ALARM, ASAP, BLOCKER, RESEARCH, SMALL TASK, EXCITER)
3. Нумерация задач (T001, T002) и инцидентов (I001, I002)
4. Использование abstract адресов вместо физических путей
"""

import os
import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

class Priority(Enum):
    """Абсолютные приоритеты согласно Task Master стандарту."""
    ALARM = "ALARM"           # Критическая ситуация
    ASAP = "ASAP"            # As Soon As Possible
    BLOCKER = "BLOCKER"       # Блокирует развитие проекта
    RESEARCH = "RESEARCH"     # Исследование
    SMALL_TASK = "SMALL TASK" # Малая задача (до 2 часов)
    EXCITER = "EXCITER"       # Улучшение

class Status(Enum):
    """Статусы задач согласно Process Task Standard."""
    BACKLOG = "Backlog"       # [ ] не начато
    TODO = "To Do"           # [ ] запланировано
    IN_PROGRESS = "In Progress"  # [/] в процессе
    REVIEW = "Review"        # на проверке/ревью
    DONE = "Done"           # [x] выполнено
    REJECTED = "Rejected"    # [-] отменено

@dataclass
class TaskData:
    """Структура данных задачи согласно новому формату."""
    number: str                    # T001, T002, etc.
    unique_id: str                # DD MMM YYYY .XXX
    title: str                    # Заголовок
    status: Status               # Статус выполнения
    priority: Priority           # Абсолютный приоритет
    deadline: Optional[str] = None  # DD mmmm YYYY, HH:MM TZ
    assignee: Optional[str] = None  # @имя_фамилия
    description: Optional[str] = None  # Развернутое описание
    acceptance_criteria: List[str] = None  # Критерии приемки
    complexity: Optional[str] = None  # XS, S, M, L, XL, XXL
    tags: List[str] = None        # #теги
    related_tasks: List[str] = None  # Связанные задачи
    observers: List[str] = None    # Наблюдатели
    
    def __post_init__(self):
        if self.acceptance_criteria is None:
            self.acceptance_criteria = []
        if self.tags is None:
            self.tags = []
        if self.related_tasks is None:
            self.related_tasks = []
        if self.observers is None:
            self.observers = []

@dataclass
class IncidentData:
    """Структура данных инцидента."""
    number: str                    # I001, I002, etc.
    title: str                    # Заголовок инцидента
    priority: Priority           # Абсолютный приоритет
    status: str                  # Зафиксирован, В работе, Решен
    impact: str                  # Влияние на систему
    description: str             # Описание проблемы
    five_why_analysis: List[str] = None  # 5-why анализ
    created_at: Optional[str] = None     # Время создания
    
    def __post_init__(self):
        if self.five_why_analysis is None:
            self.five_why_analysis = []

class TaskFormatter:
    """Класс для форматирования задач и инцидентов."""
    
    def __init__(self):
        """Инициализация форматировщика."""
        # Пути используют abstract адреса, а не физические
        self.todo_path = "[todo · incidents]/todo.md"
        self.incidents_path = "[todo · incidents]/ai.incidents.md" 
        self.standards_path = "[standards .md]"
        
        # Кеш для быстрого доступа к задачам и инцидентам
        self.tasks_cache = {}
        self.incidents_cache = {}
        
        # Счетчики для нумерации
        self.task_counter = 0
        self.incident_counter = 0
        
    def generate_unique_id(self, date: datetime = None) -> str:
        """
        Генерирует уникальный идентификатор задачи в формате DD MMM YYYY .XXX.
        
        Args:
            date: Дата для генерации ID (по умолчанию - текущая)
            
        Returns:
            str: Уникальный идентификатор
        """
        if date is None:
            date = datetime.now()
        
        # Базовый формат: "22 may 2025"
        base_id = date.strftime("%d %b %Y").lower()
        
        # Находим последний номер для этой даты
        existing_ids = self._get_existing_ids_for_date(base_id)
        next_number = len(existing_ids) + 1
        
        return f"{base_id} .{next_number:03d}"
    
    def generate_task_number(self) -> str:
        """
        Генерирует номер задачи в формате T001, T002, etc.
        
        Returns:
            str: Номер задачи
        """
        self.task_counter += 1
        return f"T{self.task_counter:03d}"
    
    def generate_incident_number(self) -> str:
        """
        Генерирует номер инцидента в формате I001, I002, etc.
        
        Returns:
            str: Номер инцидента
        """
        self.incident_counter += 1
        return f"I{self.incident_counter:03d}"
    
    def format_task_markdown(self, task: TaskData) -> str:
        """
        Форматирует задачу в Markdown согласно новому стандарту.
        
        Args:
            task: Данные задачи
            
        Returns:
            str: Отформатированная задача в Markdown
        """
        # Маркер статуса
        status_marker = self._get_status_marker(task.status)
        
        # Основная строка задачи
        title_line = f"- {status_marker} **[{task.number}]** {task.title} [{task.priority.value}]"
        
        # Добавляем ответственного и дедлайн в основную строку
        if task.assignee:
            title_line += f" · {task.assignee}"
        if task.deadline:
            title_line += f" · до {task.deadline}"
        
        lines = [title_line]
        
        # Уникальный идентификатор
        lines.append(f"  **ID**: {task.unique_id}")
        
        # Описание
        if task.description:
            lines.append(f"  **Описание**: {task.description}")
        
        # Критерии приемки
        if task.acceptance_criteria:
            lines.append("  **Критерии приемки**:")
            for criterion in task.acceptance_criteria:
                lines.append(f"  - [ ] {criterion}")
        
        # Сложность
        if task.complexity:
            lines.append(f"  **Сложность**: {task.complexity}")
        
        # Теги
        if task.tags:
            tags_str = " ".join(f"#{tag}" for tag in task.tags)
            lines.append(f"  **Теги**: {tags_str}")
        
        # Связанные задачи
        if task.related_tasks:
            related_str = ", ".join(task.related_tasks)
            lines.append(f"  **Связанные задачи**: {related_str}")
        
        # Наблюдатели
        if task.observers:
            observers_str = ", ".join(task.observers)
            lines.append(f"  **Наблюдатели**: {observers_str}")
        
        return "\n".join(lines)
    
    def format_incident_markdown(self, incident: IncidentData) -> str:
        """
        Форматирует инцидент в Markdown согласно стандарту.
        
        Args:
            incident: Данные инцидента
            
        Returns:
            str: Отформатированный инцидент в Markdown
        """
        lines = []
        
        # Заголовок инцидента
        timestamp = incident.created_at or datetime.now().strftime("%d %B %Y %H:%M")
        lines.append(f"## {timestamp} - {incident.title}")
        lines.append("")
        
        # Метаданные
        lines.append(f"**Номер инцидента**: {incident.number}")
        lines.append(f"**Приоритет**: {incident.priority.value}")
        lines.append(f"**Статус**: {incident.status}")
        lines.append(f"**Влияние**: {incident.impact}")
        lines.append("")
        
        # Описание
        lines.append(f"**Описание**: {incident.description}")
        lines.append("")
        
        # 5-why анализ
        if incident.five_why_analysis:
            lines.append("**5 почему разбор**:")
            for i, why in enumerate(incident.five_why_analysis, 1):
                lines.append(f"{i}. **Почему**: {why}")
            lines.append("")
        
        return "\n".join(lines)
    
    def parse_existing_tasks(self, content: str) -> List[TaskData]:
        """
        Парсит существующие задачи из содержимого todo.md.
        
        Args:
            content: Содержимое файла todo.md
            
        Returns:
            List[TaskData]: Список задач
        """
        tasks = []
        lines = content.split('\n')
        
        # Ищем строки с задачами
        task_pattern = r'^- \[([ x/\-])\] (.+)$'
        
        for line in lines:
            match = re.match(task_pattern, line.strip())
            if match:
                status_char = match.group(1)
                task_text = match.group(2)
                
                # Парсим задачу
                task = self._parse_task_line(status_char, task_text)
                if task:
                    tasks.append(task)
        
        return tasks
    
    def update_all_tasks_format(self) -> Dict[str, Any]:
        """
        Обновляет формат всех задач в todo.md согласно новому стандарту.
        
        Returns:
            Dict[str, Any]: Результат обновления
        """
        try:
            # Читаем текущий файл todo.md
            if not os.path.exists(self.todo_path):
                return {"success": False, "error": "Файл todo.md не найден"}
            
            with open(self.todo_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Парсим существующие задачи
            existing_tasks = self.parse_existing_tasks(content)
            
            # Инициализируем счетчики
            self.task_counter = 0
            formatted_tasks = []
            
            # Форматируем каждую задачу
            for task in existing_tasks:
                # Присваиваем номер, если его нет
                if not task.number:
                    task.number = self.generate_task_number()
                
                # Присваиваем уникальный ID, если его нет
                if not task.unique_id:
                    task.unique_id = self.generate_unique_id()
                
                # Форматируем задачу
                formatted_task = self.format_task_markdown(task)
                formatted_tasks.append(formatted_task)
                
                # Добавляем в кеш
                self.tasks_cache[task.number] = task
            
            # Создаем новое содержимое файла
            new_content = self._create_new_todo_content(formatted_tasks)
            
            # Создаем резервную копию
            backup_path = f"{self.todo_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Записываем обновленный файл
            with open(self.todo_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return {
                "success": True,
                "updated_tasks": len(formatted_tasks),
                "backup_path": backup_path,
                "tasks_cache_size": len(self.tasks_cache)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_existing_ids_for_date(self, base_id: str) -> List[str]:
        """Получает существующие ID для заданной даты."""
        # Пока возвращаем пустой список, в будущем можно сканировать файлы
        return []
    
    def _get_status_marker(self, status: Status) -> str:
        """Преобразует статус в маркер для Markdown."""
        markers = {
            Status.BACKLOG: "[ ]",
            Status.TODO: "[ ]", 
            Status.IN_PROGRESS: "[/]",
            Status.REVIEW: "[?]",
            Status.DONE: "[x]",
            Status.REJECTED: "[-]"
        }
        return markers.get(status, "[ ]")
    
    def _parse_task_line(self, status_char: str, task_text: str) -> Optional[TaskData]:
        """Парсит строку задачи."""
        try:
            # Определяем статус
            status_mapping = {
                ' ': Status.TODO,
                'x': Status.DONE,
                '/': Status.IN_PROGRESS,
                '-': Status.REJECTED
            }
            status = status_mapping.get(status_char, Status.TODO)
            
            # Извлекаем номер задачи (если есть)
            number_match = re.search(r'\*\*\[([T]\d{3})\]\*\*', task_text)
            number = number_match.group(1) if number_match else ""
            
            # Извлекаем приоритет
            priority_match = re.search(r'\[(ALARM|ASAP|BLOCKER|RESEARCH|SMALL TASK|EXCITER)\]', task_text)
            priority_str = priority_match.group(1) if priority_match else "RESEARCH"
            priority = Priority(priority_str)
            
            # Извлекаем заголовок (убираем номер и приоритет)
            title = task_text
            if number_match:
                title = title.replace(number_match.group(0), "").strip()
            if priority_match:
                title = title.replace(priority_match.group(0), "").strip()
            
            return TaskData(
                number=number,
                unique_id="",  # Будет сгенерирован позже
                title=title,
                status=status,
                priority=priority
            )
            
        except Exception as e:
            print(f"Ошибка при парсинге задачи '{task_text}': {e}")
            return None
    
    def _create_new_todo_content(self, formatted_tasks: List[str]) -> str:
        """Создает новое содержимое файла todo.md."""
        lines = []
        
        # Заголовок и статистика
        lines.append("# 📋 Задачи и проекты")
        lines.append("")
        lines.append("## 📊 Статистика задач")
        lines.append("")
        
        # Подсчитываем статистику
        total_tasks = len(self.tasks_cache)
        open_tasks = sum(1 for task in self.tasks_cache.values() 
                        if task.status in [Status.BACKLOG, Status.TODO, Status.IN_PROGRESS])
        completed_tasks = sum(1 for task in self.tasks_cache.values() 
                             if task.status == Status.DONE)
        
        lines.append(f"- **Всего задач**: {total_tasks}")
        lines.append(f"- **Открытых**: {open_tasks}")
        lines.append(f"- **Выполненных**: {completed_tasks}")
        lines.append(f"- **Последнее обновление**: {datetime.now().strftime('%d %B %Y, %H:%M CET')}")
        lines.append("")
        
        # Активные задачи
        lines.append("## 🎯 Активные задачи")
        lines.append("")
        
        for task_markdown in formatted_tasks:
            lines.append(task_markdown)
            lines.append("")
        
        return "\n".join(lines)

def main():
    """Функция для тестирования форматировщика."""
    formatter = TaskFormatter()
    
    print("🎯 Тестирование форматировщика задач...")
    
    # Тестовая задача
    test_task = TaskData(
        number="T001",
        unique_id="22 may 2025 .001",
        title="Внедрить систему нумерации задач согласно Task Master стандарту",
        status=Status.IN_PROGRESS,
        priority=Priority.ASAP,
        deadline="25 мая 2025, 18:00 CET",
        assignee="@ai_assistant",
        description="Реализовать полную систему нумерации и форматирования задач",
        acceptance_criteria=[
            "Все задачи имеют уникальные номера T001, T002, etc.",
            "Применены абсолютные приоритеты ALARM/ASAP/BLOCKER/etc.",
            "Создан кеш для быстрого доступа к задачам"
        ],
        complexity="L",
        tags=["tdd", "task-master", "formatting"]
    )
    
    # Форматируем задачу
    formatted = formatter.format_task_markdown(test_task)
    print("✅ Отформатированная задача:")
    print(formatted)
    print()
    
    # Тестовый инцидент
    test_incident = IncidentData(
        number="I001",
        title="Потеряна система abstract адресов",
        priority=Priority.BLOCKER,
        status="В работе",
        impact="Блокирует работу с логическими ссылками",
        description="Система abstract адресов была потеряна, нужно восстановить",
        five_why_analysis=[
            "Почему потеряна система? - Код был рефакторен без сохранения функциональности",
            "Почему не сохранили? - Не было резервных копий критической функциональности",
            "Почему нет резервных копий? - Отсутствует процедура бэкапа перед рефакторингом",
            "Почему нет процедуры? - Не было создано стандарта для рефакторинга",
            "Почему нет стандарта? - Недооценили важность абстрактных адресов"
        ]
    )
    
    formatted_incident = formatter.format_incident_markdown(test_incident)
    print("✅ Отформатированный инцидент:")
    print(formatted_incident)

if __name__ == "__main__":
    main()