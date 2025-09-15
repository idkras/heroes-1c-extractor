#!/usr/bin/env python3
"""
JTBD:
Я (разработчик) хочу иметь механизм критических секций для синхронизации доступа
к разделяемым ресурсам, чтобы избежать гонок данных в многопоточной среде.

Модуль предоставляет декоратор critical_section и класс CriticalSectionManager
для обеспечения потокобезопасного доступа к разделяемым ресурсам.

Автор: AI Assistant
Дата: 21 мая 2025
"""

import os
import sys
import time
import json
import logging
import threading
import functools
import uuid
from typing import Dict, Any, List, Optional, Callable, Set

logger = logging.getLogger(__name__)

class CriticalSectionManager:
    """
    Менеджер критических секций для синхронизации доступа к разделяемым ресурсам.
    Обеспечивает блокировки на уровне ресурсов для предотвращения гонок данных.
    """
    
    def __init__(self, lock_dir: str = "advising_platform/src/cache/locks"):
        """
        Инициализирует менеджер критических секций.
        
        Args:
            lock_dir: Директория для файлов блокировок
        """
        self.lock_dir = os.path.abspath(lock_dir)
        os.makedirs(self.lock_dir, exist_ok=True)
        
        self._locks = {}  # словарь {имя_ресурса: блокировка}
        self._lock = threading.RLock()  # блокировка для доступа к словарю блокировок
        
        logger.info(f"CriticalSectionManager инициализирован: директория блокировок={self.lock_dir}")
        
    def acquire(self, resource_name: str, timeout: float = -1) -> bool:
        """
        Захватывает блокировку для указанного ресурса.
        
        Args:
            resource_name: Имя ресурса
            timeout: Таймаут в секундах (-1 означает бесконечное ожидание)
            
        Returns:
            True, если блокировка успешно захвачена, иначе False
        """
        with self._lock:
            if resource_name not in self._locks:
                self._locks[resource_name] = threading.RLock()
                
            lock = self._locks[resource_name]
            
        # Пытаемся захватить блокировку
        return lock.acquire(timeout=timeout if timeout >= 0 else None)
        
    def release(self, resource_name: str) -> None:
        """
        Освобождает блокировку для указанного ресурса.
        
        Args:
            resource_name: Имя ресурса
            
        Raises:
            RuntimeError: Если ресурс не был заблокирован
        """
        with self._lock:
            if resource_name not in self._locks:
                raise RuntimeError(f"Ресурс '{resource_name}' не был заблокирован")
                
            lock = self._locks[resource_name]
            
        # Освобождаем блокировку
        lock.release()
        
    def with_lock(self, resource_name: str, timeout: float = -1) -> Callable:
        """
        Декоратор для выполнения функции с блокировкой указанного ресурса.
        
        Args:
            resource_name: Имя ресурса
            timeout: Таймаут в секундах (-1 означает бесконечное ожидание)
            
        Returns:
            Декоратор, выполняющий функцию с блокировкой
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if not self.acquire(resource_name, timeout):
                    raise TimeoutError(f"Не удалось захватить блокировку для ресурса '{resource_name}'")
                    
                try:
                    return func(*args, **kwargs)
                finally:
                    self.release(resource_name)
            return wrapper
        return decorator
        
    def get_locks_info(self) -> Dict[str, Any]:
        """
        Возвращает информацию о текущих блокировках.
        
        Returns:
            Словарь с информацией о блокировках
        """
        with self._lock:
            return {
                "lock_dir": self.lock_dir,
                "active_locks": list(self._locks.keys())
            }
            
    def clear_locks(self) -> None:
        """JTBD:
Я (разработчик) хочу использовать функцию clear_locks, чтобы эффективно выполнить соответствующую операцию.
         
         Очищает все блокировки."""
        with self._lock:
            self._locks.clear()


# Глобальный менеджер критических секций
_critical_section_manager = None


def get_critical_section_manager(lock_dir: Optional[str] = None) -> CriticalSectionManager:
    """
    Возвращает глобальный менеджер критических секций.
    
    Args:
        lock_dir: Директория для файлов блокировок (если None, используется "cache/locks")
        
    Returns:
        Глобальный менеджер критических секций
    """
    global _critical_section_manager
    
    if _critical_section_manager is None:
        _critical_section_manager = CriticalSectionManager(lock_dir or "advising_platform/src/cache/locks")
        
    return _critical_section_manager


def critical_section(func=None, resource_name: Optional[str] = None, timeout: float = -1):
    """
    Декоратор для выполнения функции в критической секции.
    
    Args:
        func: Декорируемая функция
        resource_name: Имя ресурса (если None, используется имя функции)
        timeout: Таймаут в секундах (-1 означает бесконечное ожидание)
        
    Returns:
        Декорированная функция
    """
    if func is None:
        return lambda f: critical_section(f, resource_name, timeout)
        
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Определяем имя ресурса
        res_name = resource_name or f"{func.__module__}.{func.__name__}"
        
        # Получаем менеджер критических секций
        manager = get_critical_section_manager()
        
        # Выполняем функцию с блокировкой
        if not manager.acquire(res_name, timeout):
            raise TimeoutError(f"Не удалось захватить блокировку для ресурса '{res_name}'")
            
        try:
            return func(*args, **kwargs)
        finally:
            manager.release(res_name)
            
    return wrapper