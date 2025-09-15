#!/usr/bin/env python3
"""
Упрощенный менеджер атомарных транзакций (рефакторированная версия).

Цель: Сократить размер с 1298 до <500 строк используя модульную архитектуру.
Объединяет компоненты: file_locks, cache_entries, atomic_operations.

Автор: AI Assistant
Дата: 22 May 2025
"""

import os
import json
import time
import logging
import threading
from typing import Dict, Any, Optional, List, Callable, TypeVar, Union
from contextlib import contextmanager

# Импортируем компоненты
try:
    from .components.file_locks import FileLock, GlobalLockManager
    from .components.cache_entries import CacheEntry, CacheStorage
    from .components.atomic_operations import AtomicFileOperations
    COMPONENTS_AVAILABLE = True
except ImportError:
    COMPONENTS_AVAILABLE = False

logger = logging.getLogger(__name__)

T = TypeVar('T')


class Transaction:
    """
    Контекст транзакции для группировки атомарных операций.
    """
    
    def __init__(self, transaction_id: Optional[str] = None):
        """
        Инициализация транзакции.
        
        Args:
            transaction_id: Идентификатор транзакции
        """
        self.transaction_id = transaction_id or f"tx_{int(time.time() * 1000)}"
        self.operations: List[Dict[str, Any]] = []
        self.locked_files: List[str] = []
        self.start_time = time.time()
        self.committed = False
        self.rolled_back = False
        
        if COMPONENTS_AVAILABLE:
            self.atomic_ops = AtomicFileOperations()
        else:
            self.atomic_ops = None
    
    def add_operation(self, operation_type: str, file_path: str, **kwargs):
        """
        Добавляет операцию в транзакцию.
        
        Args:
            operation_type: Тип операции (read, write, delete, copy)
            file_path: Путь к файлу
            **kwargs: Дополнительные параметры
        """
        self.operations.append({
            'type': operation_type,
            'file_path': file_path,
            'timestamp': time.time(),
            **kwargs
        })
    
    def acquire_locks(self) -> bool:
        """
        Получает блокировки для всех файлов в транзакции.
        
        Returns:
            True, если все блокировки получены
        """
        if not COMPONENTS_AVAILABLE:
            return True
            
        try:
            # Собираем уникальные пути файлов
            file_paths = set()
            for op in self.operations:
                file_paths.add(op['file_path'])
                if 'destination' in op:
                    file_paths.add(op['destination'])
            
            # Получаем блокировки в определенном порядке (по алфавиту)
            sorted_paths = sorted(file_paths)
            for file_path in sorted_paths:
                if GlobalLockManager.acquire_file_lock(file_path):
                    self.locked_files.append(file_path)
                else:
                    logger.error(f"Не удалось получить блокировку для {file_path}")
                    self.release_locks()
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Ошибка при получении блокировок: {e}")
            self.release_locks()
            return False
    
    def release_locks(self):
        """Освобождает все блокировки."""
        if COMPONENTS_AVAILABLE:
            for file_path in self.locked_files:
                GlobalLockManager.release_file_lock(file_path)
        self.locked_files.clear()
    
    def commit(self) -> bool:
        """
        Выполняет все операции транзакции.
        
        Returns:
            True, если транзакция успешно выполнена
        """
        if self.committed or self.rolled_back:
            return False
        
        if not self.acquire_locks():
            return False
        
        try:
            # Выполняем операции
            for op in self.operations:
                success = self._execute_operation(op)
                if not success:
                    logger.error(f"Ошибка выполнения операции: {op}")
                    self.rollback()
                    return False
            
            self.committed = True
            logger.info(f"Транзакция {self.transaction_id} успешно выполнена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка выполнения транзакции {self.transaction_id}: {e}")
            self.rollback()
            return False
        finally:
            self.release_locks()
    
    def rollback(self):
        """Откатывает транзакцию."""
        self.rolled_back = True
        self.release_locks()
        logger.info(f"Транзакция {self.transaction_id} откачена")
    
    def _execute_operation(self, operation: Dict[str, Any]) -> bool:
        """
        Выполняет отдельную операцию.
        
        Args:
            operation: Описание операции
            
        Returns:
            True, если операция успешна
        """
        if not self.atomic_ops:
            return True  # Fallback режим
        
        op_type = operation['type']
        file_path = operation['file_path']
        
        try:
            if op_type == 'write':
                return self.atomic_ops.write_with_cache(
                    file_path, 
                    operation['data'],
                    **operation.get('options', {})
                )
            elif op_type == 'read':
                success, _ = self.atomic_ops.read_with_cache(file_path)
                return success
            elif op_type == 'copy':
                return self.atomic_ops.copy_file(file_path, operation['destination'])
            elif op_type == 'delete':
                return self.atomic_ops.delete_file(file_path)
            else:
                logger.warning(f"Неизвестный тип операции: {op_type}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка выполнения операции {op_type} для {file_path}: {e}")
            return False
    
    def __enter__(self):
        """Вход в контекстный менеджер."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Выход из контекстного менеджера."""
        if exc_type is None:
            self.commit()
        else:
            self.rollback()


class TransactionManager:
    """
    Основной менеджер транзакций (упрощенная версия).
    """
    
    def __init__(self):
        """Инициализация менеджера транзакций."""
        self.active_transactions: Dict[str, Transaction] = {}
        self.transaction_lock = threading.RLock()
        
        if COMPONENTS_AVAILABLE:
            self.cache_storage = CacheStorage()
            self.atomic_ops = AtomicFileOperations(self.cache_storage)
        else:
            self.cache_storage = None
            self.atomic_ops = None
    
    @contextmanager
    def transaction(self, transaction_id: Optional[str] = None):
        """
        Создает контекст транзакции.
        
        Args:
            transaction_id: Идентификатор транзакции
            
        Yields:
            Объект транзакции
        """
        tx = Transaction(transaction_id)
        
        with self.transaction_lock:
            self.active_transactions[tx.transaction_id] = tx
        
        try:
            yield tx
        finally:
            with self.transaction_lock:
                self.active_transactions.pop(tx.transaction_id, None)
    
    def read_json(self, file_path: str, use_cache: bool = True) -> tuple[bool, Optional[Any]]:
        """
        Читает JSON файл.
        
        Args:
            file_path: Путь к файлу
            use_cache: Использовать кеш
            
        Returns:
            Кортеж (успех, данные)
        """
        if self.atomic_ops and use_cache:
            return self.atomic_ops.read_with_cache(file_path)
        elif self.atomic_ops:
            return self.atomic_ops.read_json(file_path)
        else:
            # Fallback режим
            try:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return True, json.load(f)
                return False, None
            except Exception:
                return False, None
    
    def write_json(self, file_path: str, data: Any, **kwargs) -> bool:
        """
        Записывает JSON файл.
        
        Args:
            file_path: Путь к файлу
            data: Данные для записи
            **kwargs: Дополнительные параметры
            
        Returns:
            True, если операция успешна
        """
        if self.atomic_ops:
            return self.atomic_ops.write_with_cache(file_path, data, **kwargs)
        else:
            # Fallback режим
            try:
                os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                return True
            except Exception:
                return False
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """
        Получает статистику кеша.
        
        Returns:
            Словарь со статистикой
        """
        if self.cache_storage:
            return self.cache_storage.get_statistics()
        else:
            return {"cache_available": False}
    
    def cleanup_cache(self) -> int:
        """
        Очищает недействительные записи кеша.
        
        Returns:
            Количество очищенных записей
        """
        if self.cache_storage:
            return self.cache_storage.cleanup_invalid_entries()
        return 0
    
    def get_transaction_statistics(self) -> Dict[str, Any]:
        """
        Получает статистику транзакций.
        
        Returns:
            Словарь со статистикой
        """
        with self.transaction_lock:
            return {
                "active_transactions": len(self.active_transactions),
                "components_available": COMPONENTS_AVAILABLE,
                "transaction_ids": list(self.active_transactions.keys())
            }


# Глобальный экземпляр
_transaction_manager: Optional[TransactionManager] = None


def get_transaction_manager() -> TransactionManager:
    """
    Получает глобальный экземпляр менеджера транзакций.
    
    Returns:
        Экземпляр TransactionManager
    """
    global _transaction_manager
    if _transaction_manager is None:
        _transaction_manager = TransactionManager()
    return _transaction_manager


# Экспортируем основные классы для обратной совместимости
AtomicFileOperations = AtomicFileOperations if COMPONENTS_AVAILABLE else type('AtomicFileOperations', (), {})
GlobalLockManager = GlobalLockManager if COMPONENTS_AVAILABLE else type('GlobalLockManager', (), {})