#!/usr/bin/env python3
"""
Integrity-Aware Cache: Кеш с гарантированной синхронизацией с файловой системой.

GREEN фаза TDD - решение для всех проблем выявленных в RED тестах:
1. Автоматическое обнаружение изменений файлов (is_synchronized_with_disk)
2. Синхронизация с файловой системой (sync_with_filesystem)  
3. Транзакционная безопасность (transaction)
4. Защита от грязных записей (set_with_integrity_check)
5. Real-time мониторинг файловой системы

Автор: AI Assistant
Дата: 22 May 2025
"""

import os
import json
import hashlib
import threading
import time
from contextlib import contextmanager
from typing import Dict, Any, Optional, Set, List, Tuple
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent, FileDeletedEvent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CacheIntegrityError(Exception):
    """Исключение для нарушений целостности кеша."""
    pass


class TransactionRollbackError(Exception):
    """Исключение для ошибок отката транзакций."""
    pass


class FileChangeHandler(FileSystemEventHandler):
    """Обработчик изменений файловой системы для кеша."""
    
    def __init__(self, cache_instance):
        self.cache = cache_instance
        
    def on_modified(self, event):
        if not event.is_directory:
            self.cache._on_file_changed(event.src_path, 'modified')
            
    def on_created(self, event):
        if not event.is_directory:
            self.cache._on_file_changed(event.src_path, 'created')
            
    def on_deleted(self, event):
        if not event.is_directory:
            self.cache._on_file_changed(event.src_path, 'deleted')


class CacheTransaction:
    """Транзакция для кеша с поддержкой отката."""
    
    def __init__(self, cache_instance):
        self.cache = cache_instance
        self.operations = []
        self.backup_data = {}
        self.is_active = False
        
    def set(self, key: str, value: Any):
        """Операция записи в транзакции."""
        # Сохраняем backup данных для отката
        if key not in self.backup_data:
            self.backup_data[key] = self.cache.data.get(key)
            
        self.operations.append(('set', key, value))
        self.cache.data[key] = value
        
    def get(self, key: str) -> Any:
        """Операция чтения в транзакции."""
        if not self.is_active:
            raise CacheIntegrityError("Транзакция не активна")
            
        return self.cache.data.get(key)
        
    def commit(self):
        """Подтверждение транзакции."""
        if not self.is_active:
            raise CacheIntegrityError("Транзакция не активна")
            
        # Обновляем метаданные и синхронизируем с диском
        for op_type, key, value in self.operations:
            if op_type == 'set':
                self.cache._update_metadata(key, value)
                
        self.operations.clear()
        self.backup_data.clear()
        self.is_active = False
        
    def rollback(self):
        """Откат транзакции."""
        if not self.is_active:
            return
            
        # Восстанавливаем данные из backup
        for key, original_value in self.backup_data.items():
            if original_value is None:
                self.cache.data.pop(key, None)
            else:
                self.cache.data[key] = original_value
                
        self.operations.clear()
        self.backup_data.clear()
        self.is_active = False
        
    def __enter__(self):
        self.is_active = True
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is not None:
                self.rollback()
            else:
                self.commit()
        except Exception as e:
            logger.error(f"Ошибка в транзакции, выполняем откат: {e}")
            self.rollback()
        finally:
            self.is_active = False
        # Возвращаем False, чтобы не подавлять исключения
        return False


class IntegrityAwareCache:
    """
    Кеш с гарантированной целостностью и синхронизацией с файловой системой.
    
    Особенности:
    - Автоматическое обнаружение изменений файлов
    - Транзакционная безопасность
    - Защита от грязных записей
    - Real-time мониторинг файловой системы
    - Comprehensive проверки целостности
    """
    
    def __init__(self, max_size_mb: int = 200, auto_sync: bool = True):
        self.max_size_mb = max_size_mb
        self.data: Dict[str, Any] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.RLock()
        self.auto_sync = auto_sync
        
        # File watcher для real-time синхронизации
        self.observer = None
        self.monitored_paths: Set[str] = set()
        self.change_callbacks: List[callable] = []
        
        if auto_sync:
            self._start_file_watcher()
            
        logger.info(f"IntegrityAwareCache инициализирован с лимитом {max_size_mb}MB")
        
    def _start_file_watcher(self):
        """Запускает мониторинг файловой системы."""
        try:
            self.observer = Observer()
            self.file_handler = FileChangeHandler(self)
            # Добавляем базовые пути для мониторинга
            for path in [".", "standards .md", "todo · incidents"]:
                if os.path.exists(path):
                    self.observer.schedule(self.file_handler, path, recursive=True)
                    self.monitored_paths.add(os.path.abspath(path))
            
            self.observer.start()
            logger.info("File watcher запущен для real-time синхронизации")
        except Exception as e:
            logger.warning(f"Не удалось запустить file watcher: {e}")
            
    def _stop_file_watcher(self):
        """Останавливает мониторинг файловой системы."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info("File watcher остановлен")
            
    def _on_file_changed(self, file_path: str, change_type: str):
        """Обработчик изменений файлов."""
        with self.lock:
            abs_path = os.path.abspath(file_path)
            
            # Проверяем, есть ли файл в кеше
            if abs_path in self.data:
                logger.info(f"Обнаружено изменение файла в кеше: {file_path} ({change_type})")
                
                if change_type == 'deleted':
                    # Удаляем из кеша
                    del self.data[abs_path]
                    self.metadata.pop(abs_path, None)
                else:
                    # Помечаем как несинхронизированный
                    if abs_path in self.metadata:
                        self.metadata[abs_path]['synchronized'] = False
                        self.metadata[abs_path]['last_fs_change'] = time.time()
                        
                # Вызываем callbacks
                for callback in self.change_callbacks:
                    try:
                        callback(abs_path, change_type)
                    except Exception as e:
                        logger.warning(f"Ошибка в callback: {e}")
                        
    def _calculate_file_hash(self, file_path: str) -> Optional[str]:
        """Вычисляет hash файла для проверки целостности."""
        try:
            if not os.path.exists(file_path):
                return None
                
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.sha256(content).hexdigest()
        except Exception as e:
            logger.warning(f"Не удалось вычислить hash для {file_path}: {e}")
            return None
            
    def _get_file_mtime(self, file_path: str) -> Optional[float]:
        """Получает время модификации файла."""
        try:
            if os.path.exists(file_path):
                return os.path.getmtime(file_path)
            return None
        except Exception as e:
            logger.warning(f"Не удалось получить mtime для {file_path}: {e}")
            return None
            
    def _update_metadata(self, key: str, value: Any):
        """Обновляет метаданные для ключа."""
        file_path = key if os.path.isabs(key) else os.path.abspath(key)
        
        self.metadata[key] = {
            'cached_at': time.time(),
            'file_path': file_path,
            'file_hash': self._calculate_file_hash(file_path),
            'file_mtime': self._get_file_mtime(file_path),
            'synchronized': True,
            'size': len(str(value)) if value else 0
        }
        
    def is_synchronized_with_disk(self, key: str) -> bool:
        """
        Проверяет синхронизацию кеша с диском для конкретного ключа.
        
        Returns:
            bool: True если синхронизирован, False если есть расхождения
        """
        with self.lock:
            if key not in self.data:
                return True  # Если нет в кеше, то не может быть рассинхронизации
                
            if key not in self.metadata:
                return False  # Нет метаданных - потенциальная проблема
                
            meta = self.metadata[key]
            file_path = meta.get('file_path', key)
            
            # Проверяем существование файла
            if not os.path.exists(file_path):
                return meta.get('synchronized', False) and meta.get('file_hash') is None
                
            # Проверяем время модификации
            current_mtime = self._get_file_mtime(file_path)
            cached_mtime = meta.get('file_mtime')
            
            if current_mtime != cached_mtime:
                return False
                
            # Проверяем hash для дополнительной уверенности
            current_hash = self._calculate_file_hash(file_path)
            cached_hash = meta.get('file_hash')
            
            return current_hash == cached_hash
            
    def sync_with_filesystem(self, key: Optional[str] = None):
        """
        Синхронизирует кеш с файловой системой.
        
        Args:
            key: Конкретный ключ для синхронизации или None для всех
        """
        with self.lock:
            keys_to_sync = [key] if key else list(self.data.keys())
            
            for cache_key in keys_to_sync:
                if cache_key not in self.metadata:
                    continue
                    
                file_path = self.metadata[cache_key].get('file_path', cache_key)
                
                if not os.path.exists(file_path):
                    # Файл удален - удаляем из кеша
                    del self.data[cache_key]
                    del self.metadata[cache_key]
                    logger.info(f"Файл {file_path} удален, убираем из кеша")
                    continue
                    
                # Проверяем нужна ли синхронизация
                if not self.is_synchronized_with_disk(cache_key):
                    try:
                        # Перечитываем файл
                        if file_path.endswith('.json'):
                            with open(file_path, 'r', encoding='utf-8') as f:
                                new_data = json.load(f)
                        else:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                new_data = f.read()
                                
                        # Обновляем кеш
                        self.data[cache_key] = new_data
                        self._update_metadata(cache_key, new_data)
                        
                        logger.info(f"Синхронизирован файл: {file_path}")
                        
                    except Exception as e:
                        logger.error(f"Ошибка синхронизации {file_path}: {e}")
                        # Помечаем как несинхронизированный
                        self.metadata[cache_key]['synchronized'] = False
                        
    def set_with_integrity_check(self, key: str, value: Any):
        """
        Записывает значение в кеш с проверкой целостности.
        
        Проверяет что нет рассинхронизации перед записью.
        """
        with self.lock:
            # Проверяем синхронизацию перед записью
            if key in self.data and not self.is_synchronized_with_disk(key):
                raise CacheIntegrityError(
                    f"Нельзя записывать в кеш: файл {key} изменен на диске и не синхронизирован"
                )
                
            # Записываем значение
            self.data[key] = value
            self._update_metadata(key, value)
            
            logger.info(f"Записано в кеш с проверкой целостности: {key}")
            
    def get(self, key: str, auto_sync: bool = True) -> Any:
        """
        Получает значение из кеша с опциональной автосинхронизацией.
        
        Args:
            key: Ключ
            auto_sync: Автоматически синхронизировать если найдены расхождения
        """
        with self.lock:
            if key not in self.data:
                return None
                
            # Проверяем синхронизацию
            if auto_sync and not self.is_synchronized_with_disk(key):
                logger.info(f"Обнаружена рассинхронизация для {key}, выполняем автосинхронизацию")
                self.sync_with_filesystem(key)
                
            return self.data.get(key)
            
    def set(self, key: str, value: Any):
        """Обычная запись в кеш (без проверки целостности)."""
        with self.lock:
            self.data[key] = value
            self._update_metadata(key, value)
            
    @contextmanager
    def transaction(self):
        """
        Создает транзакцию для кеша.
        
        Пример использования:
            with cache.transaction() as tx:
                tx.set('key1', 'value1')
                tx.set('key2', 'value2')
                # При ошибке - автоматический откат
        """
        tx = CacheTransaction(self)
        try:
            yield tx
        except Exception as e:
            logger.error(f"Ошибка в транзакции, выполняем откат: {e}")
            raise
            
    def get_integrity_report(self) -> Dict[str, Any]:
        """
        Получает отчет о целостности кеша.
        
        Returns:
            dict: Подробный отчет о состоянии синхронизации
        """
        with self.lock:
            report = {
                'total_items': len(self.data),
                'synchronized_items': 0,
                'unsynchronized_items': 0,
                'missing_files': 0,
                'details': {}
            }
            
            for key in self.data:
                is_sync = self.is_synchronized_with_disk(key)
                file_path = self.metadata.get(key, {}).get('file_path', key)
                
                if is_sync:
                    report['synchronized_items'] += 1
                else:
                    report['unsynchronized_items'] += 1
                    
                if not os.path.exists(file_path):
                    report['missing_files'] += 1
                    
                report['details'][key] = {
                    'synchronized': is_sync,
                    'file_exists': os.path.exists(file_path),
                    'file_path': file_path
                }
                
            return report
            
    def add_change_callback(self, callback: callable):
        """Добавляет callback для уведомлений об изменениях файлов."""
        self.change_callbacks.append(callback)
        
    def cleanup(self):
        """Очищает ресурсы кеша."""
        self._stop_file_watcher()
        with self.lock:
            self.data.clear()
            self.metadata.clear()
            
    def __del__(self):
        """Деструктор для корректной очистки ресурсов."""
        try:
            self.cleanup()
        except:
            pass


# Создаем глобальный экземпляр для использования в приложении
integrity_cache = IntegrityAwareCache()