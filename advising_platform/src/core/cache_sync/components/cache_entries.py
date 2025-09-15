#!/usr/bin/env python3
"""
Компонент записей кеша для транзакционного менеджера.

Цель: Выделить логику записей кеша из большого transaction_manager.py
для упрощения и модуляризации кода.

Автор: AI Assistant
Дата: 22 May 2025
"""

import os
import json
import time
import hashlib
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class CacheEntry:
    """
    Запись в кеше файловых метаданных.
    
    Содержит информацию о файле для обеспечения согласованности
    между файловой системой и кешем.
    """
    
    def __init__(
        self,
        file_path: str,
        size: int = 0,
        last_modified: float = 0.0,
        hash_value: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Инициализация записи кеша.
        
        Args:
            file_path: Путь к файлу
            size: Размер файла в байтах
            last_modified: Время последнего изменения
            hash_value: Хеш-значение содержимого
            metadata: Дополнительные метаданные
        """
        self.file_path = file_path
        self.size = size
        self.last_modified = last_modified
        self.hash_value = hash_value
        self.metadata = metadata or {}
        self.cached_at = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует запись в словарь.
        
        Returns:
            Словарь с данными записи
        """
        return {
            "file_path": self.file_path,
            "size": self.size,
            "last_modified": self.last_modified,
            "hash_value": self.hash_value,
            "metadata": self.metadata,
            "cached_at": self.cached_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheEntry':
        """
        Создает запись из словаря.
        
        Args:
            data: Словарь с данными
            
        Returns:
            Запись кеша
        """
        entry = cls(
            file_path=data.get("file_path", ""),
            size=data.get("size", 0),
            last_modified=data.get("last_modified", 0.0),
            hash_value=data.get("hash_value"),
            metadata=data.get("metadata", {})
        )
        entry.cached_at = data.get("cached_at", time.time())
        return entry
    
    @classmethod
    def from_file(cls, file_path: str) -> Optional['CacheEntry']:
        """
        Создает запись кеша на основе файла.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Запись кеша или None, если файл не существует
        """
        if not os.path.exists(file_path):
            return None
        
        try:
            stats = os.stat(file_path)
            
            # Вычисляем хеш файла
            hash_value = None
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                    hash_value = hashlib.sha256(content).hexdigest()
            except Exception as e:
                logger.warning(f"Не удалось вычислить хеш для {file_path}: {e}")
            
            return cls(
                file_path=file_path,
                size=stats.st_size,
                last_modified=stats.st_mtime,
                hash_value=hash_value
            )
        except (IOError, OSError) as e:
            logger.error(f"Ошибка при создании записи кеша для {file_path}: {e}")
            return None
    
    def is_valid(self) -> bool:
        """
        Проверяет актуальность записи кеша.
        
        Returns:
            True, если запись актуальна
        """
        if not os.path.exists(self.file_path):
            return False
        
        try:
            stats = os.stat(self.file_path)
            return (
                stats.st_size == self.size and
                abs(stats.st_mtime - self.last_modified) < 1.0
            )
        except (IOError, OSError):
            return False
    
    def update_from_file(self) -> bool:
        """
        Обновляет запись на основе текущего состояния файла.
        
        Returns:
            True, если обновление успешно
        """
        if not os.path.exists(self.file_path):
            return False
        
        try:
            stats = os.stat(self.file_path)
            self.size = stats.st_size
            self.last_modified = stats.st_mtime
            self.cached_at = time.time()
            
            # Обновляем хеш
            try:
                with open(self.file_path, 'rb') as f:
                    content = f.read()
                    self.hash_value = hashlib.sha256(content).hexdigest()
            except Exception as e:
                logger.warning(f"Не удалось обновить хеш для {self.file_path}: {e}")
            
            return True
        except (IOError, OSError) as e:
            logger.error(f"Ошибка при обновлении записи кеша для {self.file_path}: {e}")
            return False


class CacheStorage:
    """
    Хранилище записей кеша с операциями чтения/записи.
    """
    
    DEFAULT_CACHE_PATH = ".cache_state.json"
    
    def __init__(self, cache_path: Optional[str] = None):
        """
        Инициализация хранилища кеша.
        
        Args:
            cache_path: Путь к файлу кеша
        """
        self.cache_path = cache_path or self.DEFAULT_CACHE_PATH
        self._cache: Dict[str, CacheEntry] = {}
        self._load_cache()
    
    def _load_cache(self) -> bool:
        """
        Загружает кеш из файла.
        
        Returns:
            True, если загрузка успешна
        """
        if not os.path.exists(self.cache_path):
            self._cache = {}
            return True
        
        try:
            with open(self.cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._cache = {}
            for file_path, entry_data in data.items():
                self._cache[file_path] = CacheEntry.from_dict(entry_data)
            
            logger.info(f"Загружено {len(self._cache)} записей кеша из {self.cache_path}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при загрузке кеша из {self.cache_path}: {e}")
            self._cache = {}
            return False
    
    def _save_cache(self) -> bool:
        """
        Сохраняет кеш в файл.
        
        Returns:
            True, если сохранение успешно
        """
        try:
            # Создаем директорию если нужно
            cache_dir = os.path.dirname(self.cache_path)
            if cache_dir:
                os.makedirs(cache_dir, exist_ok=True)
            
            # Конвертируем в словарь
            data = {}
            for file_path, entry in self._cache.items():
                data[file_path] = entry.to_dict()
            
            # Сохраняем атомарно через временный файл
            temp_path = self.cache_path + '.tmp'
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Атомарное переименование
            if os.name == 'nt':  # Windows
                if os.path.exists(self.cache_path):
                    os.replace(temp_path, self.cache_path)
                else:
                    os.rename(temp_path, self.cache_path)
            else:
                os.rename(temp_path, self.cache_path)
            
            logger.debug(f"Сохранено {len(self._cache)} записей кеша в {self.cache_path}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении кеша в {self.cache_path}: {e}")
            return False
    
    def get_entry(self, file_path: str) -> Optional[CacheEntry]:
        """
        Получает запись кеша для файла.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Запись кеша или None
        """
        normalized_path = os.path.abspath(file_path)
        return self._cache.get(normalized_path)
    
    def set_entry(self, file_path: str, entry: CacheEntry) -> bool:
        """
        Устанавливает запись кеша для файла.
        
        Args:
            file_path: Путь к файлу
            entry: Запись кеша
            
        Returns:
            True, если операция успешна
        """
        normalized_path = os.path.abspath(file_path)
        self._cache[normalized_path] = entry
        return self._save_cache()
    
    def remove_entry(self, file_path: str) -> bool:
        """
        Удаляет запись кеша для файла.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            True, если операция успешна
        """
        normalized_path = os.path.abspath(file_path)
        if normalized_path in self._cache:
            del self._cache[normalized_path]
            return self._save_cache()
        return True
    
    def clear(self) -> bool:
        """
        Очищает весь кеш.
        
        Returns:
            True, если операция успешна
        """
        self._cache.clear()
        return self._save_cache()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Получает статистику кеша.
        
        Returns:
            Словарь со статистикой
        """
        valid_entries = 0
        invalid_entries = 0
        
        for entry in self._cache.values():
            if entry.is_valid():
                valid_entries += 1
            else:
                invalid_entries += 1
        
        return {
            "total_entries": len(self._cache),
            "valid_entries": valid_entries,
            "invalid_entries": invalid_entries,
            "cache_file": self.cache_path,
            "cache_exists": os.path.exists(self.cache_path)
        }
    
    def cleanup_invalid_entries(self) -> int:
        """
        Удаляет недействительные записи кеша.
        
        Returns:
            Количество удаленных записей
        """
        invalid_paths = []
        for file_path, entry in self._cache.items():
            if not entry.is_valid():
                invalid_paths.append(file_path)
        
        for file_path in invalid_paths:
            del self._cache[file_path]
        
        if invalid_paths:
            self._save_cache()
            logger.info(f"Удалено {len(invalid_paths)} недействительных записей кеша")
        
        return len(invalid_paths)