"""
Модуль валидации задач и других рабочих элементов.

Предоставляет набор проверок для валидации задач, инцидентов, гипотез и стандартов
перед их созданием или обновлением.

Автор: AI Assistant
Дата: 20 мая 2025
"""

import re
import os
import datetime
from typing import List, Dict, Any, Optional, Tuple, Union

# Импорт необходимых модулей
try:
    from advising_platform.src.core.registry.task_registry import (
        WorkItemType, WorkItemStatus
    )
except ImportError as e:
    raise ImportError(f"Ошибка при импорте модулей: {e}")


class TaskValidator:
    """
    Валидатор задач и других рабочих элементов.
    
    Предоставляет методы для проверки корректности данных задач, инцидентов,
    гипотез и стандартов перед их созданием или обновлением.
    """
    
    @staticmethod
    def validate_title(title: str) -> List[str]:
        """
        Валидирует заголовок элемента.
        
        Args:
            title: Заголовок элемента
            
        Returns:
            Список сообщений об ошибках (пустой список, если ошибок нет)
        """
        errors = []
        
        # Проверка на пустой заголовок
        if not title:
            errors.append("Не указан заголовок элемента")
            return errors
        
        # Проверка длины заголовка
        if len(title) < 3:
            errors.append("Заголовок элемента слишком короткий (минимум 3 символа)")
        elif len(title) > 200:
            errors.append("Заголовок элемента слишком длинный (максимум 200 символов)")
        
        # Проверка на недопустимые символы
        if any(char in title for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']):
            errors.append("Заголовок содержит недопустимые символы (/, \\, :, *, ?, \", <, >, |)")
        
        # Проверка на начало с цифры (рекомендация, не ошибка)
        if title[0].isdigit():
            errors.append("Заголовок начинается с цифры (рекомендуется начинать с буквы)")
        
        # Проверка на наличие заглавных букв (рекомендация, не ошибка)
        if title[0].islower():
            errors.append("Первая буква заголовка строчная (рекомендуется использовать заглавную)")
        
        # Проверка на знаки препинания в конце (рекомендация, не ошибка)
        if title[-1] in ['.', ',', ':', ';', '!', '?']:
            errors.append("Заголовок заканчивается знаком препинания (рекомендуется убрать)")
        
        return errors
    
    @staticmethod
    def validate_description(description: str, type: WorkItemType) -> List[str]:
        """
        Валидирует описание элемента.
        
        Args:
            description: Описание элемента
            type: Тип элемента
            
        Returns:
            Список сообщений об ошибках (пустой список, если ошибок нет)
        """
        errors = []
        
        # Для некоторых типов элементов описание обязательно
        if type in [WorkItemType.TASK, WorkItemType.INCIDENT, WorkItemType.HYPOTHESIS]:
            if not description:
                errors.append(f"Для элемента типа {type.value} необходимо указать описание")
                return errors
            
            # Проверка длины описания
            if len(description) < 10:
                errors.append("Описание элемента слишком короткое (минимум 10 символов)")
            elif len(description) > 10000:
                errors.append("Описание элемента слишком длинное (максимум 10000 символов)")
        
        return errors
    
    @staticmethod
    def validate_file_path(file_path: Optional[str], type: WorkItemType) -> List[str]:
        """
        Валидирует путь к файлу элемента.
        
        Args:
            file_path: Путь к файлу
            type: Тип элемента
            
        Returns:
            Список сообщений об ошибках (пустой список, если ошибок нет)
        """
        errors = []
        
        # Если путь не указан, то ошибок нет
        if not file_path:
            return errors
        
        # Проверка на существование файла
        if os.path.exists(file_path):
            # Если файл существует, проверяем, что это не директория
            if os.path.isdir(file_path):
                errors.append(f"Путь {file_path} указывает на директорию, а не на файл")
        else:
            # Проверка директории, в которой должен быть создан файл
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                errors.append(f"Директория {directory} не существует")
        
        # Проверка расширения файла
        if type in [WorkItemType.TASK, WorkItemType.INCIDENT, WorkItemType.HYPOTHESIS, WorkItemType.STANDARD]:
            if not file_path.endswith(".md"):
                errors.append(f"Для элемента типа {type.value} файл должен иметь расширение .md")
        
        return errors
    
    @staticmethod
    def validate_due_date(due_date: Optional[float], type: WorkItemType) -> List[str]:
        """
        Валидирует срок выполнения элемента.
        
        Args:
            due_date: Срок выполнения (timestamp)
            type: Тип элемента
            
        Returns:
            Список сообщений об ошибках (пустой список, если ошибок нет)
        """
        errors = []
        
        # Если срок не указан, то ошибок нет
        if not due_date:
            return errors
        
        # Проверка, что срок не в прошлом
        now = datetime.datetime.now().timestamp()
        if due_date < now:
            errors.append("Срок выполнения уже прошел")
        
        # Проверка, что срок не слишком далеко в будущем (больше года)
        one_year_from_now = (datetime.datetime.now() + datetime.timedelta(days=365)).timestamp()
        if due_date > one_year_from_now:
            errors.append("Срок выполнения более года от текущей даты")
        
        return errors
    
    @staticmethod
    def validate_tags(tags: Optional[List[str]]) -> List[str]:
        """
        Валидирует теги элемента.
        
        Args:
            tags: Список тегов
            
        Returns:
            Список сообщений об ошибках (пустой список, если ошибок нет)
        """
        errors = []
        
        # Если теги не указаны, то ошибок нет
        if not tags:
            return errors
        
        # Проверка на дубликаты
        if len(tags) != len(set(tags)):
            errors.append("В списке тегов есть дубликаты")
        
        # Проверка формата тегов
        for tag in tags:
            # Тег должен быть непустой строкой
            if not tag:
                errors.append("Один из тегов пустой")
                continue
                
            # Тег должен содержать только буквы, цифры и дефисы
            if not re.match(r'^[a-zA-Z0-9-]+$', tag):
                errors.append(f"Тег '{tag}' содержит недопустимые символы (разрешены только буквы, цифры и дефисы)")
            
            # Тег не должен быть слишком длинным
            if len(tag) > 50:
                errors.append(f"Тег '{tag}' слишком длинный (максимум 50 символов)")
        
        return errors
    
    @staticmethod
    def validate_status(status: Optional[WorkItemStatus], type: WorkItemType) -> List[str]:
        """
        Валидирует статус элемента.
        
        Args:
            status: Статус элемента
            type: Тип элемента
            
        Returns:
            Список сообщений об ошибках (пустой список, если ошибок нет)
        """
        errors = []
        
        # Если статус не указан, то ошибок нет
        if not status:
            return errors
        
        # Проверка статуса для разных типов элементов
        if type == WorkItemType.STANDARD and status == WorkItemStatus.IN_PROGRESS:
            errors.append(f"Для стандарта недопустим статус '{status.value}'")
        
        return errors
    
    @staticmethod
    def validate_all(
        type: WorkItemType,
        title: str,
        description: Optional[str] = None,
        status: Optional[WorkItemStatus] = None,
        file_path: Optional[str] = None,
        due_date: Optional[float] = None,
        tags: Optional[List[str]] = None
    ) -> List[str]:
        """
        Валидирует все данные элемента.
        
        Args:
            type: Тип элемента
            title: Заголовок
            description: Описание
            status: Статус
            file_path: Путь к файлу
            due_date: Срок выполнения
            tags: Теги
            
        Returns:
            Список сообщений об ошибках (пустой список, если ошибок нет)
        """
        errors = []
        
        # Валидация заголовка
        errors.extend(TaskValidator.validate_title(title))
        
        # Валидация описания
        if description is not None:
            errors.extend(TaskValidator.validate_description(description, type))
        
        # Валидация пути к файлу
        if file_path is not None:
            errors.extend(TaskValidator.validate_file_path(file_path, type))
        
        # Валидация срока выполнения
        if due_date is not None:
            errors.extend(TaskValidator.validate_due_date(due_date, type))
        
        # Валидация тегов
        if tags is not None:
            errors.extend(TaskValidator.validate_tags(tags))
        
        # Валидация статуса
        if status is not None:
            errors.extend(TaskValidator.validate_status(status, type))
        
        return errors