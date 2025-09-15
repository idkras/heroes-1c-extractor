#!/usr/bin/env python3
"""
Базовый интерфейс кеша для унификации операций.

Цель: Устранить дублирование функций _load_cache, _save_cache в кодовой базе
и создать единый базовый класс для всех кешей.

Автор: AI Assistant
Дата: 22 May 2025
"""

import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional
import time

logger = logging.getLogger(__name__)


class BaseCacheInterface(ABC):
    """Базовый интерфейс для всех кешей в системе."""
    
    @abstractmethod
    def get(self, key: str) -> Any:
        """Получить значение из кеша."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any) -> bool:
        """Сохранить значение в кеш."""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Очистить кеш."""
        pass
    
    @abstractmethod
    def is_cached(self, key: str) -> bool:
        """Проверить наличие ключа в кеше."""
        pass


class FileBasedCache(BaseCacheInterface):
    """Файловый кеш с унифицированными операциями."""
    
    def __init__(self, cache_file: str, cache_dir: str = "cache"):
        """
        Инициализация файлового кеша.
        
        Args:
            cache_file: Имя файла кеша
            cache_dir: Директория для кеша
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / cache_file
        self._cache: Dict[str, Any] = {}
        self._load_cache()
    
    def _load_cache(self) -> bool:
        """
        Загружает кеш из файла.
        
        Returns:
            True если загрузка успешна
        """
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self._cache = json.load(f)
                logger.info(f"Кеш загружен из {self.cache_file}")
                return True
            else:
                self._cache = {}
                logger.info(f"Создан новый кеш: {self.cache_file}")
                return True
        except Exception as e:
            logger.error(f"Ошибка загрузки кеша {self.cache_file}: {e}")
            self._cache = {}
            return False
    
    def _save_cache(self) -> bool:
        """
        Сохраняет кеш в файл.
        
        Returns:
            True если сохранение успешно
        """
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self._cache, f, ensure_ascii=False, indent=2)
            logger.info(f"Кеш сохранен в {self.cache_file}")
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения кеша {self.cache_file}: {e}")
            return False
    
    def get(self, key: str) -> Any:
        """Получить значение из кеша."""
        return self._cache.get(key)
    
    def set(self, key: str, value: Any) -> bool:
        """Сохранить значение в кеш."""
        try:
            self._cache[key] = value
            return self._save_cache()
        except Exception as e:
            logger.error(f"Ошибка установки значения в кеш {key}: {e}")
            return False
    
    def clear(self) -> bool:
        """Очистить кеш."""
        try:
            self._cache.clear()
            return self._save_cache()
        except Exception as e:
            logger.error(f"Ошибка очистки кеша: {e}")
            return False
    
    def is_cached(self, key: str) -> bool:
        """Проверить наличие ключа в кеше."""
        return key in self._cache
    
    def get_size(self) -> int:
        """Получить размер кеша в байтах."""
        try:
            return self.cache_file.stat().st_size if self.cache_file.exists() else 0
        except:
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику кеша."""
        return {
            'file': str(self.cache_file),
            'size_bytes': self.get_size(),
            'items_count': len(self._cache),
            'exists': self.cache_file.exists(),
            'last_modified': time.ctime(self.cache_file.stat().st_mtime) if self.cache_file.exists() else None
        }


class MemoryCache(BaseCacheInterface):
    """Кеш в оперативной памяти."""
    
    def __init__(self, max_size_mb: int = 200):
        """
        Инициализация кеша в памяти.
        
        Args:
            max_size_mb: Максимальный размер кеша в MB (по умолчанию 200MB)
        """
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self._cache: Dict[str, Any] = {}
        self._access_times: Dict[str, float] = {}
    
    def get(self, key: str) -> Any:
        """Получить значение из кеша."""
        if key in self._cache:
            self._access_times[key] = time.time()
            return self._cache[key]
        return None
    
    def set(self, key: str, value: Any) -> bool:
        """Сохранить значение в кеш."""
        try:
            # Проверяем размер кеша и очищаем при необходимости
            if self._should_cleanup():
                self._cleanup_cache()
            
            self._cache[key] = value
            self._access_times[key] = time.time()
            return True
        except Exception as e:
            logger.error(f"Ошибка установки значения в память кеш {key}: {e}")
            return False
    
    def clear(self) -> bool:
        """Очистить кеш."""
        try:
            self._cache.clear()
            self._access_times.clear()
            return True
        except Exception as e:
            logger.error(f"Ошибка очистки памяти кеша: {e}")
            return False
    
    def is_cached(self, key: str) -> bool:
        """Проверить наличие ключа в кеше."""
        return key in self._cache
    
    def _should_cleanup(self) -> bool:
        """Проверяет, нужна ли очистка кеша."""
        current_size = self._estimate_size()
        return current_size > (self.max_size_bytes * 0.8)  # 80% от лимита
    
    def _cleanup_cache(self):
        """Очищает 20% самых старых записей."""
        if not self._access_times:
            return
        
        # Сортируем по времени доступа
        sorted_keys = sorted(self._access_times.keys(), key=lambda k: self._access_times[k])
        
        # Удаляем 20% самых старых записей
        cleanup_count = max(1, len(sorted_keys) // 5)
        for key in sorted_keys[:cleanup_count]:
            self._cache.pop(key, None)
            self._access_times.pop(key, None)
        
        logger.info(f"Очищено {cleanup_count} записей из кеша")
    
    def _estimate_size(self) -> int:
        """Оценивает размер кеша в байтах."""
        import sys
        total_size = 0
        for key, value in self._cache.items():
            total_size += sys.getsizeof(key) + sys.getsizeof(value)
        return total_size
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику кеша."""
        current_size = self._estimate_size()
        return {
            'type': 'memory',
            'size_bytes': current_size,
            'size_mb': current_size / (1024 * 1024),
            'max_size_mb': self.max_size_bytes / (1024 * 1024),
            'usage_percent': (current_size / self.max_size_bytes) * 100,
            'items_count': len(self._cache),
            'needs_cleanup': self._should_cleanup()
        }