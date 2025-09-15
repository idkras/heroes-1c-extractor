"""
Версионированный класс для работы с файлами.

Представляет собой расширение OptimizedFileOperations с интегрированной
поддержкой автоматического версионирования.

Автор: AI Assistant
Дата: 20 мая 2025
"""

import os
import json
from typing import Any, Dict, List, Optional, Union, Tuple, Callable

# Импортируем базовый класс для файловых операций
try:
    from advising_platform.src.core.optimized_file_operations import OptimizedFileOperations
except ImportError:
    try:
        from src.core.optimized_file_operations import OptimizedFileOperations
    except ImportError:
        from optimized_file_operations import OptimizedFileOperations

from .version_manager import VersionManager
from .version_decorators import VersionContext


class VersionedFileOperations:
    """
    Класс для работы с файлами с поддержкой автоматического версионирования.
    
    Расширяет функциональность OptimizedFileOperations, добавляя автоматическое
    создание версий файлов при их изменении и поддержку журнала изменений.
    
    Примеры использования:
    
    ```python
    # Базовое использование
    from advising_platform.src.core.versioning import VersionedFileOperations
    
    VersionedFileOperations.write_file("file.txt", "Новое содержимое", author="John Doe", reason="Обновление документа")
    
    # Использование с контекстным менеджером авторства
    from advising_platform.src.core.versioning import VersionContext, VersionedFileOperations
    
    with VersionContext(author="Jane Smith", reason="Массовое обновление"):
        VersionedFileOperations.write_file("file1.txt", "Содержимое 1")
        VersionedFileOperations.write_file("file2.txt", "Содержимое 2")
    ```
    """
    
    # Глобальный менеджер версий
    _version_manager = None
    
    # Настройки по умолчанию
    _default_author = "Система"
    _default_reason = "Автоматическое обновление"
    _base_dir = "."
    
    @classmethod
    def configure(
        cls, 
        base_dir: str = ".",
        default_author: str = "Система",
        default_reason: str = "Автоматическое обновление"
    ):
        """
        Конфигурирует глобальные настройки версионирования.
        
        Args:
            base_dir: Базовая директория для файловых операций
            default_author: Автор изменений по умолчанию
            default_reason: Причина изменений по умолчанию
        """
        cls._base_dir = base_dir
        cls._default_author = default_author
        cls._default_reason = default_reason
        cls._version_manager = VersionManager(base_dir=base_dir)
    
    @classmethod
    def get_version_manager(cls) -> VersionManager:
        """
        Получает глобальный менеджер версий.
        
        Returns:
            VersionManager: Экземпляр менеджера версий
        """
        if cls._version_manager is None:
            cls._version_manager = VersionManager(base_dir=cls._base_dir)
        return cls._version_manager
    
    @classmethod
    def get_author_from_context(cls) -> str:
        """
        Получает автора из текущего контекста VersionContext или использует значение по умолчанию.
        
        Returns:
            str: Автор изменений
        """
        return VersionContext.get_current_author() or cls._default_author
    
    @classmethod
    def get_reason_from_context(cls) -> str:
        """
        Получает причину из текущего контекста VersionContext или использует значение по умолчанию.
        
        Returns:
            str: Причина изменений
        """
        return VersionContext.get_current_reason() or cls._default_reason
    
    @classmethod
    def create_version_after_write(
        cls, 
        file_path: str, 
        author: Optional[str] = None,
        reason: Optional[str] = None
    ) -> bool:
        """
        Создает версию файла после записи.
        
        Args:
            file_path: Путь к файлу
            author: Автор изменений (если None, берется из контекста)
            reason: Причина изменений (если None, берется из контекста)
            
        Returns:
            bool: True, если создание версии успешно, иначе False
        """
        if not os.path.exists(file_path):
            return False
        
        # Используем автор и причину из параметров или контекста
        author = author or cls.get_author_from_context()
        reason = reason or cls.get_reason_from_context()
        
        try:
            version_manager = cls.get_version_manager()
            version_manager.create_new_version(file_path, author, reason)
            return True
        except Exception as e:
            print(f"Ошибка при создании версии для {file_path}: {e}")
            return False
    
    @classmethod
    def write_file(
        cls, 
        path: str, 
        content: str, 
        ensure_cache_sync: bool = True, 
        create_backup: bool = True,
        author: Optional[str] = None,
        reason: Optional[str] = None
    ) -> bool:
        """
        Безопасная запись в файл с версионированием.
        
        Args:
            path: Путь к файлу
            content: Содержимое для записи
            ensure_cache_sync: Проверять синхронизацию с кешем после записи
            create_backup: Создавать резервную копию перед записью
            author: Автор изменений (по умолчанию берется из контекста)
            reason: Причина изменений (по умолчанию берется из контекста)
            
        Returns:
            bool: True, если запись успешна, иначе False
        """
        # Используем базовый метод для записи
        result = OptimizedFileOperations.write_file(path, content, ensure_cache_sync, create_backup)
        
        # Если запись успешна, создаем версию
        if result:
            cls.create_version_after_write(path, author, reason)
        
        return result
    
    @classmethod
    def read_file(
        cls, 
        path: str, 
        ensure_cache_sync: bool = True
    ) -> Optional[str]:
        """
        Безопасное чтение файла.
        
        Args:
            path: Путь к файлу
            ensure_cache_sync: Проверять синхронизацию с кешем перед чтением
            
        Returns:
            str: Содержимое файла или None, если файл не существует или произошла ошибка
        """
        # Просто используем базовый метод для чтения (без версионирования)
        result = OptimizedFileOperations.read_file(path, ensure_cache_sync)
        # Если результат - кортеж (успех, содержимое), извлекаем содержимое
        if isinstance(result, tuple) and len(result) == 2:
            success, content = result
            return content if success else None
        return result
    
    @classmethod
    def write_json(
        cls, 
        path: str, 
        data: Any, 
        ensure_cache_sync: bool = True, 
        create_backup: bool = True,
        indent: int = 2,
        author: Optional[str] = None,
        reason: Optional[str] = None
    ) -> bool:
        """
        Безопасная запись JSON-данных в файл с версионированием.
        
        Args:
            path: Путь к файлу
            data: Данные для сериализации в JSON
            ensure_cache_sync: Проверять синхронизацию с кешем после записи
            create_backup: Создавать резервную копию перед записью
            indent: Отступ для форматирования JSON
            author: Автор изменений (по умолчанию берется из контекста)
            reason: Причина изменений (по умолчанию берется из контекста)
            
        Returns:
            bool: True, если запись успешна, иначе False
        """
        # Используем базовый метод для записи JSON
        result = OptimizedFileOperations.write_json(path, data, ensure_cache_sync, create_backup, indent)
        
        # Если запись успешна, создаем версию
        if result:
            cls.create_version_after_write(path, author, reason)
        
        return result
    
    @classmethod
    def read_json(
        cls, 
        path: str, 
        ensure_cache_sync: bool = True
    ) -> Optional[Any]:
        """
        Безопасное чтение JSON-файла.
        
        Args:
            path: Путь к файлу
            ensure_cache_sync: Проверять синхронизацию с кешем перед чтением
            
        Returns:
            Any: Данные из JSON или None, если файл не существует или произошла ошибка
        """
        # Просто используем базовый метод для чтения JSON (без версионирования)
        result = OptimizedFileOperations.read_json(path, ensure_cache_sync)
        # Если результат - кортеж (успех, данные), извлекаем данные
        if isinstance(result, tuple) and len(result) == 2:
            success, data = result
            return data if success else None
        return result
    
    @classmethod
    def append_to_file(
        cls, 
        path: str, 
        content: str,
        ensure_cache_sync: bool = True,
        author: Optional[str] = None,
        reason: Optional[str] = None
    ) -> bool:
        """
        Безопасное добавление содержимого в конец файла с версионированием.
        
        Args:
            path: Путь к файлу
            content: Содержимое для добавления
            ensure_cache_sync: Проверять синхронизацию с кешем после записи
            author: Автор изменений (по умолчанию берется из контекста)
            reason: Причина изменений (по умолчанию берется из контекста)
            
        Returns:
            bool: True, если добавление успешно, иначе False
        """
        # Если файл существует, читаем его содержимое
        current_content = cls.read_file(path, ensure_cache_sync)
        
        if current_content is not None:
            # Добавляем новое содержимое
            new_content = current_content + content
            
            # Записываем обновленное содержимое
            return cls.write_file(path, new_content, ensure_cache_sync, True, author, reason)
        else:
            # Если файл не существует, создаем его с новым содержимым
            return cls.write_file(path, content, ensure_cache_sync, False, author, reason)
    
    @classmethod
    def update_json_file(
        cls, 
        path: str, 
        update_data: Dict[str, Any],
        create_if_not_exists: bool = True,
        ensure_cache_sync: bool = True,
        author: Optional[str] = None,
        reason: Optional[str] = None
    ) -> bool:
        """
        Обновляет существующий JSON-файл заданными данными с версионированием.
        
        Args:
            path: Путь к файлу
            update_data: Словарь с данными для обновления
            create_if_not_exists: Создать файл, если он не существует
            ensure_cache_sync: Проверять синхронизацию с кешем
            author: Автор изменений (по умолчанию берется из контекста)
            reason: Причина изменений (по умолчанию берется из контекста)
            
        Returns:
            bool: True, если обновление успешно, иначе False
        """
        # Загружаем существующие данные или создаем новый словарь
        current_data = cls.read_json(path, ensure_cache_sync)
        
        if current_data is None:
            if create_if_not_exists:
                current_data = {}
            else:
                return False
        
        # Обновляем данные
        if isinstance(current_data, dict):
            current_data.update(update_data)
        else:
            print(f"Ошибка: файл {path} содержит не словарь, а {type(current_data)}")
            return False
        
        # Записываем обновленные данные
        return cls.write_json(path, current_data, ensure_cache_sync, True, 2, author, reason)
    
    @classmethod
    def get_version_history(cls, file_path: str, as_markdown: bool = True) -> str:
        """
        Получает историю версий файла.
        
        Args:
            file_path: Путь к файлу
            as_markdown: Вернуть историю в формате Markdown (иначе в формате TSV)
            
        Returns:
            str: Текст истории версий
        """
        version_manager = cls.get_version_manager()
        
        if as_markdown:
            return version_manager.export_changelog_to_markdown(file_path)
        else:
            return version_manager.export_changelog_to_tsv(file_path)
    
    @classmethod
    def create_version(
        cls, 
        file_path: str, 
        author: Optional[str] = None,
        reason: Optional[str] = None
    ) -> bool:
        """
        Принудительно создает новую версию файла.
        
        Args:
            file_path: Путь к файлу
            author: Автор изменений (по умолчанию берется из контекста)
            reason: Причина изменений (по умолчанию берется из контекста)
            
        Returns:
            bool: True, если создание версии успешно, иначе False
        """
        return cls.create_version_after_write(file_path, author, reason)