"""
Декораторы для автоматического версионирования файлов.

Предоставляет декораторы для методов OptimizedFileOperations, 
которые добавляют автоматическое версионирование при изменении файлов.

Автор: AI Assistant
Дата: 20 мая 2025
"""

import os
import functools
import inspect
from typing import Any, Callable, Optional, Dict, Type, Union
import datetime

from .version_manager import VersionManager


# Глобальный экземпляр менеджера версий
_version_manager = None


def get_version_manager() -> VersionManager:
    """
    Получает глобальный экземпляр менеджера версий.
    
    Returns:
        Экземпляр VersionManager
    """
    global _version_manager
    if _version_manager is None:
        _version_manager = VersionManager()
    return _version_manager


def with_versioning(author_param: str = "author", reason_param: str = "reason", always_version: bool = False):
    """
    Декоратор для добавления версионирования к методам OptimizedFileOperations.
    
    Args:
        author_param: Имя параметра для автора изменений
        reason_param: Имя параметра для причины изменений
        always_version: Создавать версию даже если параметры автора и причины не указаны
    
    Returns:
        Декорированная функция
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Получаем информацию о параметрах функции
            sig = inspect.signature(func)
            bound_args = sig.bind(self, *args, **kwargs)
            bound_args.apply_defaults()
            
            # Извлекаем параметры
            params = dict(bound_args.arguments)
            file_path = params.get("file_path")
            author = params.get(author_param, "Система")
            reason = params.get(reason_param, "Автоматическое обновление")
            
            # Запоминаем исходный файл для проверки изменений
            if file_path and os.path.exists(file_path):
                try:
                    with open(file_path, "rb") as f:
                        original_content = f.read()
                except (IOError, OSError):
                    original_content = None
            else:
                original_content = None
            
            # Вызываем оригинальную функцию
            result = func(self, *args, **kwargs)
            
            # После успешного выполнения проверяем изменения и создаем версию
            if file_path:
                # Проверяем, что файл существует после выполнения функции
                if os.path.exists(file_path):
                    try:
                        with open(file_path, "rb") as f:
                            new_content = f.read()
                    except (IOError, OSError):
                        new_content = None
                        
                    # Если содержимое изменилось или это новый файл
                    if new_content != original_content:
                        # Проверяем, нужно ли создавать версию
                        if always_version or author != "Система" or reason != "Автоматическое обновление":
                            try:
                                version_manager = get_version_manager()
                                version_manager.create_new_version(file_path, author, reason)
                            except Exception as e:
                                print(f"Ошибка при создании версии для {file_path}: {e}")
            
            return result
        
        return wrapper
    
    return decorator


def auto_version(cls: Type) -> Type:
    """
    Декоратор класса для автоматического добавления версионирования ко всем методам,
    изменяющим файлы.
    
    Args:
        cls: Класс для декорирования
    
    Returns:
        Декорированный класс
    """
    # Список методов, которые изменяют файлы
    modifying_methods = [
        "write",
        "append",
        "write_json",
        "update_json",
        "create",
        "move",
        "copy",
        "delete",
        "rename"
    ]
    
    # Декорируем методы
    for method_name in modifying_methods:
        if hasattr(cls, method_name):
            method = getattr(cls, method_name)
            setattr(cls, method_name, with_versioning()(method))
    
    return cls


def configure_versioning(base_dir: str = "."):
    """
    Настраивает глобальный менеджер версий.
    
    Args:
        base_dir: Базовая директория для хранения архивов и журналов
    """
    global _version_manager
    _version_manager = VersionManager(base_dir=base_dir)


class VersionContext:
    """
    Контекстный менеджер для указания автора и причины изменений.
    
    Пример использования:
    ```python
    with VersionContext(author="John Doe", reason="Исправление ошибки в документе"):
        file_operations.write("path/to/file.md", "Новое содержимое")
    ```
    """
    
    # Используем словарь для хранения текущего контекста
    _context_storage = {"current": {}}
    
    def __init__(self, author: str, reason: str):
        """
        Инициализация контекста версионирования.
        
        Args:
            author: Автор изменений
            reason: Причина изменений
        """
        self.author = author
        self.reason = reason
        self.previous_context = None
    
    def __enter__(self):
        """Сохраняет предыдущий контекст и устанавливает новый."""
        self.previous_context = VersionContext._context_storage["current"].copy()
        
        # Обновляем текущий контекст
        current = VersionContext._context_storage["current"]
        current["author"] = self.author
        current["reason"] = self.reason
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Восстанавливает предыдущий контекст."""
        if self.previous_context is not None:
            VersionContext._context_storage["current"] = self.previous_context
        else:
            VersionContext._context_storage["current"] = {}
    
    @classmethod
    def get_current_author(cls) -> str:
        """JTBD:
Я (разработчик) хочу получить current_author, чтобы использовать эти данные в дальнейших операциях.
         
         Возвращает текущего автора из контекста."""
        return cls._context_storage["current"].get("author", "Система")
    
    @classmethod
    def get_current_reason(cls) -> str:
        """JTBD:
Я (разработчик) хочу получить current_reason, чтобы использовать эти данные в дальнейших операциях.
         
         Возвращает текущую причину из контекста."""
        return cls._context_storage["current"].get("reason", "Автоматическое обновление")