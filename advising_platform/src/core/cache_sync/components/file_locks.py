#!/usr/bin/env python3
"""
Компонент блокировок файлов для транзакционного менеджера.

Цель: Выделить логику блокировок из большого transaction_manager.py
для упрощения и модуляризации кода.

Автор: AI Assistant
Дата: 22 May 2025
"""

import os
import time
import logging
import threading
import traceback
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class FileLock:
    """
    Обертка вокруг блокировки файла с поддержкой вложенных блокировок и истечения времени ожидания.
    """
    
    def __init__(self, file_path: str, timeout: float = 5.0):
        """
        Инициализация блокировки файла.
        
        Args:
            file_path: Путь к файлу
            timeout: Таймаут ожидания блокировки (в секундах)
        """
        self.file_path = file_path
        self.timeout = timeout
        self.lock = threading.RLock()
        self.owner_thread = None
        self.locked = False
        self.acquisition_time = None
        self.acquisition_stack = None
    
    def acquire(self) -> bool:
        """
        Получает блокировку.
        
        Returns:
            True, если блокировка получена, иначе False
        """
        try:
            if self.lock.acquire(timeout=self.timeout):
                self.locked = True
                self.owner_thread = threading.current_thread().ident
                self.acquisition_time = time.time()
                self.acquisition_stack = ''.join(traceback.format_stack())
                
                logger.debug(f"Блокировка получена для {self.file_path}")
                return True
            else:
                logger.warning(f"Таймаут при получении блокировки для {self.file_path}")
                return False
        except Exception as e:
            logger.error(f"Ошибка при получении блокировки для {self.file_path}: {e}")
            return False
    
    def release(self):
        """Освобождает блокировку."""
        if not self.locked:
            return
        
        # Освобождаем блокировку
        self.lock.release()
        self.locked = False
        self.owner_thread = None
        self.acquisition_time = None
        self.acquisition_stack = None
        
        logger.debug(f"Блокировка освобождена для {self.file_path}")
    
    def __enter__(self):
        """Вход в контекстный менеджер."""
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Выход из контекстного менеджера."""
        self.release()
    
    def get_owner_info(self) -> Dict[str, Any]:
        """
        Получает информацию о владельце блокировки.
        
        Returns:
            Словарь с информацией о владельце
        """
        if not self.locked:
            return {"locked": False}
        
        return {
            "locked": True,
            "owner_thread": self.owner_thread,
            "acquisition_time": self.acquisition_time,
            "elapsed": time.time() - self.acquisition_time if self.acquisition_time else None,
            "acquisition_stack": self.acquisition_stack
        }


class GlobalLockManager:
    """
    Глобальный менеджер блокировок для предотвращения гонок данных.
    """
    
    # Словарь блокировок файлов
    _file_locks: Dict[str, FileLock] = {}
    
    # Блокировка для доступа к словарю блокировок
    _locks_lock = threading.RLock()
    
    # Блокировка для доступа к кешу
    _cache_lock = threading.RLock()
    
    @classmethod
    def get_file_lock(cls, file_path: str, timeout: float = 5.0) -> FileLock:
        """
        Получает блокировку для указанного файла.
        
        Args:
            file_path: Путь к файлу
            timeout: Таймаут ожидания блокировки (в секундах)
            
        Returns:
            Объект блокировки
        """
        # Нормализуем путь
        normalized_path = os.path.abspath(file_path)
        
        with cls._locks_lock:
            if normalized_path not in cls._file_locks:
                cls._file_locks[normalized_path] = FileLock(normalized_path, timeout)
            
            return cls._file_locks[normalized_path]
    
    @classmethod
    def acquire_file_lock(cls, file_path: str, timeout: float = 5.0) -> bool:
        """
        Получает блокировку для указанного файла.
        
        Args:
            file_path: Путь к файлу
            timeout: Таймаут ожидания блокировки (в секундах)
            
        Returns:
            True, если блокировка получена, иначе False
        """
        lock = cls.get_file_lock(file_path, timeout)
        return lock.acquire()
    
    @classmethod
    def release_file_lock(cls, file_path: str) -> bool:
        """
        Освобождает блокировку для указанного файла.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            True, если блокировка освобождена, иначе False
        """
        # Нормализуем путь
        normalized_path = os.path.abspath(file_path)
        
        with cls._locks_lock:
            if normalized_path in cls._file_locks:
                cls._file_locks[normalized_path].release()
                return True
            return False
    
    @classmethod
    def get_cache_lock(cls):
        """
        Получает блокировку для доступа к кешу.
        
        Returns:
            Объект блокировки кеша
        """
        return cls._cache_lock
    
    @classmethod
    def cleanup_locks(cls) -> int:
        """
        Очищает неиспользуемые блокировки.
        
        Returns:
            Количество очищенных блокировок
        """
        cleaned = 0
        with cls._locks_lock:
            # Создаем копию ключей для безопасной итерации
            file_paths = list(cls._file_locks.keys())
            
            for file_path in file_paths:
                lock = cls._file_locks[file_path]
                if not lock.locked:
                    del cls._file_locks[file_path]
                    cleaned += 1
        
        logger.info(f"Очищено {cleaned} неиспользуемых блокировок")
        return cleaned
    
    @classmethod
    def get_lock_statistics(cls) -> Dict[str, Any]:
        """
        Получает статистику блокировок.
        
        Returns:
            Словарь со статистикой
        """
        with cls._locks_lock:
            total_locks = len(cls._file_locks)
            active_locks = sum(1 for lock in cls._file_locks.values() if lock.locked)
            
            return {
                "total_locks": total_locks,
                "active_locks": active_locks,
                "inactive_locks": total_locks - active_locks
            }