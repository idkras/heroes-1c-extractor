#!/usr/bin/env python3
"""
Компонент атомарных операций для транзакционного менеджера.

Цель: Выделить атомарные операции из большого transaction_manager.py
для упрощения и модуляризации кода.

Автор: AI Assistant
Дата: 22 May 2025
"""

import os
import json
import tempfile
import logging
from typing import Dict, Any, Optional, Tuple, Union
from .file_locks import GlobalLockManager
from .cache_entries import CacheEntry, CacheStorage

logger = logging.getLogger(__name__)


class AtomicFileOperations:
    """
    Атомарные операции с файлами с обеспечением согласованности с кешем.
    """
    
    def __init__(self, cache_storage: Optional[CacheStorage] = None):
        """
        Инициализация атомарных операций.
        
        Args:
            cache_storage: Хранилище кеша
        """
        self.cache_storage = cache_storage or CacheStorage()
    
    @classmethod
    def read_json(cls, file_path: str) -> Tuple[bool, Optional[Any]]:
        """
        Атомарное чтение JSON файла.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Кортеж (успех, данные)
        """
        if not os.path.exists(file_path):
            return False, None
        
        with GlobalLockManager.get_file_lock(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.debug(f"Прочитан JSON файл: {file_path}")
                return True, data
            except Exception as e:
                logger.error(f"Ошибка чтения JSON файла {file_path}: {e}")
                return False, None
    
    @classmethod
    def write_json(
        cls, 
        file_path: str, 
        data: Any, 
        backup: bool = True,
        create_dirs: bool = True
    ) -> bool:
        """
        Атомарная запись JSON файла.
        
        Args:
            file_path: Путь к файлу
            data: Данные для записи
            backup: Создавать резервную копию
            create_dirs: Создавать директории
            
        Returns:
            True, если операция успешна
        """
        with GlobalLockManager.get_file_lock(file_path):
            try:
                # Создаем директории если нужно
                if create_dirs:
                    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
                
                # Создаем резервную копию
                backup_path = None
                if backup and os.path.exists(file_path):
                    backup_path = file_path + '.backup'
                    import shutil
                    shutil.copy2(file_path, backup_path)
                
                # Атомарная запись через временный файл
                temp_path = file_path + '.tmp'
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                # Атомарное переименование
                if os.name == 'nt':  # Windows
                    if os.path.exists(file_path):
                        os.replace(temp_path, file_path)
                    else:
                        os.rename(temp_path, file_path)
                else:  # Unix
                    os.rename(temp_path, file_path)
                
                logger.debug(f"Записан JSON файл: {file_path}")
                return True
                
            except Exception as e:
                logger.error(f"Ошибка записи JSON файла {file_path}: {e}")
                # Восстанавливаем из резервной копии при ошибке
                if backup_path and os.path.exists(backup_path):
                    try:
                        import shutil
                        shutil.copy2(backup_path, file_path)
                        logger.info(f"Восстановлен файл из резервной копии: {file_path}")
                    except:
                        pass
                return False
    
    def read_with_cache(self, file_path: str) -> Tuple[bool, Optional[Any]]:
        """
        Чтение файла с использованием кеша.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Кортеж (успех, данные)
        """
        # Проверяем кеш
        cache_entry = self.cache_storage.get_entry(file_path)
        if cache_entry and cache_entry.is_valid():
            # Читаем из файла, так как кеш актуален
            return self.read_json(file_path)
        
        # Читаем файл и обновляем кеш
        success, data = self.read_json(file_path)
        if success:
            new_entry = CacheEntry.from_file(file_path)
            if new_entry:
                self.cache_storage.set_entry(file_path, new_entry)
        
        return success, data
    
    def write_with_cache(
        self, 
        file_path: str, 
        data: Any, 
        **kwargs
    ) -> bool:
        """
        Запись файла с обновлением кеша.
        
        Args:
            file_path: Путь к файлу
            data: Данные для записи
            **kwargs: Дополнительные параметры для write_json
            
        Returns:
            True, если операция успешна
        """
        success = self.write_json(file_path, data, **kwargs)
        if success:
            # Обновляем кеш
            new_entry = CacheEntry.from_file(file_path)
            if new_entry:
                self.cache_storage.set_entry(file_path, new_entry)
        
        return success
    
    def copy_file(self, source: str, destination: str) -> bool:
        """
        Атомарное копирование файла.
        
        Args:
            source: Исходный файл
            destination: Файл назначения
            
        Returns:
            True, если операция успешна
        """
        if not os.path.exists(source):
            return False
        
        # Получаем блокировки для обоих файлов
        with GlobalLockManager.get_file_lock(source):
            with GlobalLockManager.get_file_lock(destination):
                try:
                    import shutil
                    
                    # Создаем директории если нужно
                    os.makedirs(os.path.dirname(os.path.abspath(destination)), exist_ok=True)
                    
                    # Копируем через временный файл
                    temp_path = destination + '.tmp'
                    shutil.copy2(source, temp_path)
                    
                    # Атомарное переименование
                    if os.name == 'nt':
                        if os.path.exists(destination):
                            os.replace(temp_path, destination)
                        else:
                            os.rename(temp_path, destination)
                    else:
                        os.rename(temp_path, destination)
                    
                    # Обновляем кеш
                    new_entry = CacheEntry.from_file(destination)
                    if new_entry:
                        self.cache_storage.set_entry(destination, new_entry)
                    
                    logger.debug(f"Скопирован файл: {source} -> {destination}")
                    return True
                    
                except Exception as e:
                    logger.error(f"Ошибка копирования файла {source} -> {destination}: {e}")
                    return False
    
    def delete_file(self, file_path: str) -> bool:
        """
        Атомарное удаление файла.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            True, если операция успешна
        """
        if not os.path.exists(file_path):
            return True  # Файл уже не существует
        
        with GlobalLockManager.get_file_lock(file_path):
            try:
                os.remove(file_path)
                
                # Удаляем из кеша
                self.cache_storage.remove_entry(file_path)
                
                logger.debug(f"Удален файл: {file_path}")
                return True
                
            except Exception as e:
                logger.error(f"Ошибка удаления файла {file_path}: {e}")
                return False
    
    def file_exists(self, file_path: str, use_cache: bool = True) -> bool:
        """
        Проверка существования файла с использованием кеша.
        
        Args:
            file_path: Путь к файлу
            use_cache: Использовать кеш
            
        Returns:
            True, если файл существует
        """
        if use_cache:
            cache_entry = self.cache_storage.get_entry(file_path)
            if cache_entry and cache_entry.is_valid():
                return True
        
        return os.path.exists(file_path)
    
    def get_file_size(self, file_path: str, use_cache: bool = True) -> Optional[int]:
        """
        Получение размера файла с использованием кеша.
        
        Args:
            file_path: Путь к файлу
            use_cache: Использовать кеш
            
        Returns:
            Размер файла в байтах или None
        """
        if use_cache:
            cache_entry = self.cache_storage.get_entry(file_path)
            if cache_entry and cache_entry.is_valid():
                return cache_entry.size
        
        try:
            return os.path.getsize(file_path)
        except (IOError, OSError):
            return None