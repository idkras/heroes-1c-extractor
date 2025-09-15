"""
Менеджер атомарных транзакций для операций с файлами и кешем.

Предоставляет механизмы для обеспечения атомарности операций с файлами и их метаданными,
что позволяет избежать гонок данных и обеспечить согласованность между файловой системой и кешем.

Автор: AI Assistant
Дата: 20 мая 2025
"""

import os
import json
import time
import logging
import tempfile
import threading
import functools
import traceback
from typing import Dict, Any, Optional, Tuple, List, Callable, TypeVar, Generic, Union

# Настройка логирования
logger = logging.getLogger("transaction_manager")
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Типы для типизации
T = TypeVar('T')
R = TypeVar('R')


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
    
    def acquire(self, blocking: bool = True) -> bool:
        """
        Получает блокировку.
        
        Args:
            blocking: Блокирующий режим ожидания
            
        Returns:
            True, если блокировка получена, иначе False
        """
        current_thread = threading.current_thread().ident
        
        # Проверяем, имеем ли мы уже блокировку
        if self.owner_thread == current_thread:
            return True
        
        # Пытаемся получить блокировку
        if blocking:
            success = self.lock.acquire(blocking=True, timeout=self.timeout)
        else:
            success = self.lock.acquire(blocking=False)
        
        if success:
            # Запоминаем информацию о блокировке
            self.owner_thread = current_thread
            self.locked = True
            self.acquisition_time = time.time()
            self.acquisition_stack = traceback.format_stack()
            return True
        else:
            # Логируем ошибку, если не удалось получить блокировку
            if blocking:
                logger.warning(f"Таймаут при ожидании блокировки для файла {self.file_path}")
            return False
    
    def release(self):
        """JTBD:
Я (разработчик) хочу использовать функцию release, чтобы эффективно выполнить соответствующую операцию.
         
         Освобождает блокировку."""
        current_thread = threading.current_thread().ident
        
        # Если блокировку владеет другой поток, это ошибка
        if self.owner_thread != current_thread:
            logger.error(f"Попытка освободить блокировку файла {self.file_path}, принадлежащую другому потоку")
            return
        
        # Освобождаем блокировку
        self.lock.release()
        self.locked = False
        self.owner_thread = None
        self.acquisition_time = None
        self.acquisition_stack = None
    
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
            if normalized_path not in cls._file_locks:
                logger.warning(f"Попытка освободить несуществующую блокировку для файла {file_path}")
                return False
            
            lock = cls._file_locks[normalized_path]
            lock.release()
            return True
    
    @classmethod
    def acquire_cache_lock(cls) -> bool:
        """
        Получает блокировку для доступа к кешу.
        
        Returns:
            True, если блокировка получена, иначе False
        """
        return cls._cache_lock.acquire()
    
    @classmethod
    def release_cache_lock(cls) -> bool:
        """
        Освобождает блокировку для доступа к кешу.
        
        Returns:
            True, если блокировка освобождена, иначе False
        """
        try:
            cls._cache_lock.release()
            return True
        except RuntimeError:
            logger.warning("Попытка освободить незахваченную блокировку кеша")
            return False
    
    @classmethod
    def get_lock_statistics(cls) -> Dict[str, Any]:
        """
        Получает статистику блокировок.
        
        Returns:
            Словарь со статистикой
        """
        with cls._locks_lock:
            stats = {
                "total_locks": len(cls._file_locks),
                "active_locks": 0,
                "locks": {}
            }
            
            for path, lock in cls._file_locks.items():
                if lock.locked:
                    stats["active_locks"] += 1
                    stats["locks"][path] = lock.get_owner_info()
            
            return stats
    
    @classmethod
    def cleanup_locks(cls) -> int:
        """
        Очищает все блокировки.
        
        Returns:
            Количество очищенных блокировок
        """
        with cls._locks_lock:
            count = len(cls._file_locks)
            cls._file_locks.clear()
            return count


class Transaction:
    """
    Транзакция для атомарного выполнения операций с файлами и кешем.
    
    Обеспечивает согласованность между файловой системой и кешем, предотвращая
    гонки данных при многопоточной работе.
    """
    
    def __init__(self, files_to_lock: List[str] = None, update_cache: bool = True):
        """
        Инициализация транзакции.
        
        Args:
            files_to_lock: Список файлов для блокировки
            update_cache: Обновлять ли кеш после операций
        """
        self.files_to_lock = files_to_lock or []
        self.update_cache = update_cache
        self.acquired_locks = []
        self.success = False
        self.file_operations = []
        self.cache_operations = []
    
    def __enter__(self):
        """Вход в контекстный менеджер."""
        # Получаем блокировки для всех файлов
        for file_path in self.files_to_lock:
            if GlobalLockManager.acquire_file_lock(file_path):
                self.acquired_locks.append(file_path)
            else:
                # Если не удалось получить какую-то блокировку, освобождаем все полученные
                self._release_locks()
                raise TimeoutError(f"Не удалось получить блокировку для файла {file_path}")
        
        # Если нужно обновлять кеш, получаем блокировку для кеша
        if self.update_cache:
            if not GlobalLockManager.acquire_cache_lock():
                # Если не удалось получить блокировку кеша, освобождаем все полученные
                self._release_locks()
                raise TimeoutError("Не удалось получить блокировку для кеша")
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Выход из контекстного менеджера."""
        try:
            # Если транзакция успешна, выполняем все операции с кешем
            if exc_type is None and self.success:
                for operation in self.cache_operations:
                    try:
                        operation()
                    except Exception as e:
                        logger.error(f"Ошибка при выполнении операции с кешем: {e}")
            
            # Освобождаем блокировки
            self._release_locks()
            
            # Освобождаем блокировку кеша
            if self.update_cache:
                GlobalLockManager.release_cache_lock()
        except Exception as e:
            logger.error(f"Ошибка при завершении транзакции: {e}")
    
    def _release_locks(self):
        """Освобождает все полученные блокировки."""
        for file_path in reversed(self.acquired_locks):
            GlobalLockManager.release_file_lock(file_path)
        
        self.acquired_locks = []
    
    def add_file_operation(self, operation: Callable[[], Any]):
        """
        Добавляет операцию с файлом в транзакцию.
        
        Args:
            operation: Функция для выполнения
        """
        self.file_operations.append(operation)
    
    def add_cache_operation(self, operation: Callable[[], Any]):
        """
        Добавляет операцию с кешем в транзакцию.
        
        Args:
            operation: Функция для выполнения
        """
        self.cache_operations.append(operation)
    
    def execute(self) -> bool:
        """
        Выполняет все операции с файлами в транзакции.
        
        Returns:
            True, если все операции выполнены успешно, иначе False
        """
        try:
            # Выполняем все операции с файлами
            for operation in self.file_operations:
                operation()
            
            # Помечаем транзакцию как успешную
            self.success = True
            return True
        except Exception as e:
            logger.error(f"Ошибка при выполнении транзакции: {e}")
            self.success = False
            return False


class CacheEntry:
    """JTBD:
Я (разработчик) хочу использовать функциональность класса CacheEntry, чтобы эффективно решать соответствующие задачи в системе.
    
    Запись в кеше о файле."""
    
    def __init__(
        self,
        file_path: str,
        size: int,
        last_modified: float,
        hash_value: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Инициализация записи кеша.
        
        Args:
            file_path: Путь к файлу
            size: Размер файла
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
        return cls(
            file_path=data.get("file_path", ""),
            size=data.get("size", 0),
            last_modified=data.get("last_modified", 0.0),
            hash_value=data.get("hash_value"),
            metadata=data.get("metadata", {})
        )


class AtomicFileOperations:
    """
    Атомарные операции с файлами с обеспечением согласованности с кешем.
    
    Предоставляет методы для безопасной работы с файлами, предотвращая
    гонки данных и обеспечивая согласованность между файловой системой и кешем.
    """
    
    # Путь к кешу по умолчанию
    DEFAULT_CACHE_PATH = ".cache_state.json"
    
    @classmethod
    def _get_file_metadata(cls, file_path: str) -> Optional[CacheEntry]:
        """
        Получает метаданные файла.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Запись кеша или None, если файл не существует
        """
        if not os.path.exists(file_path):
            return None
        
        try:
            stats = os.stat(file_path)
            
            return CacheEntry(
                file_path=file_path,
                size=stats.st_size,
                last_modified=stats.st_mtime
            )
        except (IOError, OSError) as e:
            logger.error(f"Ошибка при получении метаданных файла {file_path}: {e}")
            return None
    
    @classmethod
    def _read_cache(cls, cache_path: str = None) -> Dict[str, Dict[str, Any]]:
        """
        Читает кеш из файла.
        
        Args:
            cache_path: Путь к файлу кеша
            
        Returns:
            Словарь с данными кеша
        """
        cache_path = cache_path or cls.DEFAULT_CACHE_PATH
        
        if not os.path.exists(cache_path):
            return {}
        
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Ошибка при чтении кеша из {cache_path}: {e}")
            return {}
    
    @classmethod
    def _write_cache(cls, cache_data: Dict[str, Dict[str, Any]], cache_path: str = None) -> bool:
        """
        Записывает данные в кеш.
        
        Args:
            cache_data: Словарь с данными кеша
            cache_path: Путь к файлу кеша
            
        Returns:
            True, если запись успешна, иначе False
        """
        cache_path = cache_path or cls.DEFAULT_CACHE_PATH
        
        try:
            # Создаем директорию для кеша, если её нет
            os.makedirs(os.path.dirname(os.path.abspath(cache_path)), exist_ok=True)
            
            # Создаем временный файл для атомарной записи
            fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(cache_path)))
            
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    json.dump(cache_data, f, indent=2, ensure_ascii=False)
                
                # Атомарно заменяем файл
                if os.name == "nt" and os.path.exists(cache_path):
                    # На Windows заменяем существующий файл
                    os.replace(temp_path, cache_path)
                else:
                    # На Unix используем rename
                    os.rename(temp_path, cache_path)
                
                return True
            except Exception:
                # В случае ошибки удаляем временный файл
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                raise
        except Exception as e:
            logger.error(f"Ошибка при записи кеша в {cache_path}: {e}")
            return False
    
    @classmethod
    def _update_cache_entry(cls, file_path: str, cache_path: str = None) -> bool:
        """
        Обновляет запись о файле в кеше.
        
        Args:
            file_path: Путь к файлу
            cache_path: Путь к файлу кеша
            
        Returns:
            True, если обновление успешно, иначе False
        """
        # Получаем метаданные файла
        entry = cls._get_file_metadata(file_path)
        if not entry:
            return False
        
        # Читаем кеш
        cache_data = cls._read_cache(cache_path)
        
        # Обновляем запись
        cache_data[file_path] = entry.to_dict()
        
        # Записываем обновленный кеш
        return cls._write_cache(cache_data, cache_path)
    
    @classmethod
    def write_file(
        cls, 
        file_path: str, 
        content: Union[str, bytes], 
        mode: str = "w", 
        encoding: Optional[str] = "utf-8",
        update_cache: bool = True,
        cache_path: str = None
    ) -> bool:
        """
        Атомарная запись в файл с обновлением кеша.
        
        Args:
            file_path: Путь к файлу
            content: Содержимое для записи
            mode: Режим записи
            encoding: Кодировка (для текстового режима)
            update_cache: Обновлять ли кеш
            cache_path: Путь к файлу кеша
            
        Returns:
            True, если запись успешна, иначе False
        """
        # Создаем транзакцию
        with Transaction(files_to_lock=[file_path], update_cache=update_cache) as transaction:
            # Функция для записи в файл
            def write_to_file():
                # Создаем директорию, если её нет
                os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
                
                # Создаем временный файл
                fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(file_path)))
                
                try:
                    # Записываем содержимое во временный файл
                    if "b" in mode:
                        with os.fdopen(fd, mode) as f:
                            f.write(content)
                    else:
                        with os.fdopen(fd, mode, encoding=encoding) as f:
                            f.write(content)
                    
                    # Атомарно заменяем файл
                    if os.name == "nt" and os.path.exists(file_path):
                        # На Windows заменяем существующий файл
                        os.replace(temp_path, file_path)
                    else:
                        # На Unix используем rename
                        os.rename(temp_path, file_path)
                except Exception:
                    # В случае ошибки удаляем временный файл
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                    raise
            
            # Функция для обновления кеша
            def update_cache_entry():
                if update_cache:
                    cls._update_cache_entry(file_path, cache_path)
            
            # Добавляем операции в транзакцию
            transaction.add_file_operation(write_to_file)
            transaction.add_cache_operation(update_cache_entry)
            
            # Выполняем транзакцию
            return transaction.execute()
    
    @classmethod
    def read_file(
        cls, 
        file_path: str, 
        mode: str = "r", 
        encoding: Optional[str] = "utf-8"
    ) -> Tuple[bool, Optional[Union[str, bytes]]]:
        """
        Атомарное чтение файла.
        
        Args:
            file_path: Путь к файлу
            mode: Режим чтения
            encoding: Кодировка (для текстового режима)
            
        Returns:
            Кортеж (успех, содержимое)
        """
        # Получаем блокировку для файла
        with GlobalLockManager.get_file_lock(file_path):
            if not os.path.exists(file_path):
                return False, None
            
            try:
                if "b" in mode:
                    with open(file_path, mode) as f:
                        content = f.read()
                else:
                    with open(file_path, mode, encoding=encoding) as f:
                        content = f.read()
                
                return True, content
            except Exception as e:
                logger.error(f"Ошибка при чтении файла {file_path}: {e}")
                return False, None
    
    @classmethod
    def append_to_file(
        cls, 
        file_path: str, 
        content: Union[str, bytes], 
        mode: str = "a", 
        encoding: Optional[str] = "utf-8",
        update_cache: bool = True,
        cache_path: str = None
    ) -> bool:
        """
        Атомарное добавление в файл с обновлением кеша.
        
        Args:
            file_path: Путь к файлу
            content: Содержимое для добавления
            mode: Режим добавления
            encoding: Кодировка (для текстового режима)
            update_cache: Обновлять ли кеш
            cache_path: Путь к файлу кеша
            
        Returns:
            True, если добавление успешно, иначе False
        """
        # Создаем транзакцию
        with Transaction(files_to_lock=[file_path], update_cache=update_cache) as transaction:
            # Функция для добавления в файл
            def append_to_file():
                # Создаем директорию, если её нет
                os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
                
                # Открываем файл и добавляем содержимое
                if "b" in mode:
                    with open(file_path, mode) as f:
                        f.write(content)
                else:
                    with open(file_path, mode, encoding=encoding) as f:
                        f.write(content)
            
            # Функция для обновления кеша
            def update_cache_entry():
                if update_cache:
                    cls._update_cache_entry(file_path, cache_path)
            
            # Добавляем операции в транзакцию
            transaction.add_file_operation(append_to_file)
            transaction.add_cache_operation(update_cache_entry)
            
            # Выполняем транзакцию
            return transaction.execute()
    
    @classmethod
    def delete_file(
        cls, 
        file_path: str, 
        update_cache: bool = True,
        cache_path: str = None
    ) -> bool:
        """
        Атомарное удаление файла с обновлением кеша.
        
        Args:
            file_path: Путь к файлу
            update_cache: Обновлять ли кеш
            cache_path: Путь к файлу кеша
            
        Returns:
            True, если удаление успешно, иначе False
        """
        # Создаем транзакцию
        with Transaction(files_to_lock=[file_path], update_cache=update_cache) as transaction:
            # Функция для удаления файла
            def delete_file():
                if os.path.exists(file_path):
                    os.unlink(file_path)
            
            # Функция для обновления кеша
            def update_cache_entry():
                if update_cache:
                    # Читаем кеш
                    cache_data = cls._read_cache(cache_path)
                    
                    # Удаляем запись
                    if file_path in cache_data:
                        del cache_data[file_path]
                    
                    # Записываем обновленный кеш
                    cls._write_cache(cache_data, cache_path)
            
            # Добавляем операции в транзакцию
            transaction.add_file_operation(delete_file)
            transaction.add_cache_operation(update_cache_entry)
            
            # Выполняем транзакцию
            return transaction.execute()
    
    @classmethod
    def write_json(
        cls, 
        file_path: str, 
        data: Any, 
        indent: int = 2, 
        ensure_ascii: bool = False,
        update_cache: bool = True,
        cache_path: str = None
    ) -> bool:
        """
        Атомарная запись данных в JSON-файл с обновлением кеша.
        
        Args:
            file_path: Путь к файлу
            data: Данные для записи
            indent: Отступ для форматирования JSON
            ensure_ascii: Экранировать не-ASCII символы
            update_cache: Обновлять ли кеш
            cache_path: Путь к файлу кеша
            
        Returns:
            True, если запись успешна, иначе False
        """
        try:
            # Сериализуем данные в JSON
            json_content = json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)
            
            # Записываем содержимое в файл
            return cls.write_file(
                file_path=file_path, 
                content=json_content, 
                mode="w", 
                encoding="utf-8",
                update_cache=update_cache,
                cache_path=cache_path
            )
        except (TypeError, ValueError) as e:
            logger.error(f"Ошибка при сериализации данных в JSON: {e}")
            return False
    
    @classmethod
    def read_json(
        cls, 
        file_path: str
    ) -> Tuple[bool, Optional[Any]]:
        """
        Атомарное чтение данных из JSON-файла.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Кортеж (успех, данные)
        """
        # Читаем содержимое файла
        success, content = cls.read_file(file_path, mode="r", encoding="utf-8")
        
        if not success or content is None:
            return False, None
        
        try:
            # Десериализуем данные из JSON
            data = json.loads(content)
            return True, data
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка при разборе JSON из файла {file_path}: {e}")
            return False, None
    
    @classmethod
    def update_json(
        cls, 
        file_path: str, 
        update_data: Dict[str, Any], 
        create_if_not_exists: bool = True,
        indent: int = 2, 
        ensure_ascii: bool = False,
        update_cache: bool = True,
        cache_path: str = None
    ) -> bool:
        """
        Атомарное обновление данных в JSON-файле с обновлением кеша.
        
        Args:
            file_path: Путь к файлу
            update_data: Данные для обновления
            create_if_not_exists: Создать файл, если он не существует
            indent: Отступ для форматирования JSON
            ensure_ascii: Экранировать не-ASCII символы
            update_cache: Обновлять ли кеш
            cache_path: Путь к файлу кеша
            
        Returns:
            True, если обновление успешно, иначе False
        """
        # Создаем транзакцию
        with Transaction(files_to_lock=[file_path], update_cache=update_cache) as transaction:
            # Функция для обновления JSON-файла
            def update_json_file():
                # Если файл существует, читаем его содержимое
                if os.path.exists(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            try:
                                data = json.load(f)
                                if not isinstance(data, dict):
                                    raise TypeError("JSON-данные не являются словарем")
                            except json.JSONDecodeError:
                                # Если файл содержит некорректный JSON, заменяем его пустым словарем
                                data = {}
                    except IOError as e:
                        logger.error(f"Ошибка при чтении JSON-файла {file_path}: {e}")
                        raise
                elif create_if_not_exists:
                    # Если файл не существует, создаем пустой словарь
                    data = {}
                else:
                    # Если файл не существует и его не нужно создавать, возвращаем ошибку
                    raise FileNotFoundError(f"Файл {file_path} не существует")
                
                # Обновляем данные
                data.update(update_data)
                
                # Сериализуем данные в JSON
                json_content = json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)
                
                # Создаем директорию, если её нет
                os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
                
                # Создаем временный файл
                fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(file_path)))
                
                try:
                    # Записываем содержимое во временный файл
                    with os.fdopen(fd, "w", encoding="utf-8") as f:
                        f.write(json_content)
                    
                    # Атомарно заменяем файл
                    if os.name == "nt" and os.path.exists(file_path):
                        # На Windows заменяем существующий файл
                        os.replace(temp_path, file_path)
                    else:
                        # На Unix используем rename
                        os.rename(temp_path, file_path)
                except Exception:
                    # В случае ошибки удаляем временный файл
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                    raise
            
            # Функция для обновления кеша
            def update_cache_entry():
                if update_cache:
                    cls._update_cache_entry(file_path, cache_path)
            
            # Добавляем операции в транзакцию
            transaction.add_file_operation(update_json_file)
            transaction.add_cache_operation(update_cache_entry)
            
            # Выполняем транзакцию
            return transaction.execute()
    
    @classmethod
    def batch_update(
        cls, 
        operations: List[Dict[str, Any]],
        update_cache: bool = True,
        cache_path: str = None
    ) -> bool:
        """
        Выполняет пакет операций как единую транзакцию.
        
        Args:
            operations: Список операций
            update_cache: Обновлять ли кеш
            cache_path: Путь к файлу кеша
            
        Returns:
            True, если все операции выполнены успешно, иначе False
        """
        # Собираем все файлы, которые будут затронуты операциями
        files_to_lock = set()
        for op in operations:
            if "file_path" in op:
                files_to_lock.add(op["file_path"])
        
        # Создаем транзакцию
        with Transaction(files_to_lock=list(files_to_lock), update_cache=update_cache) as transaction:
            # Функция для выполнения операций
            def execute_operations():
                for op in operations:
                    op_type = op.get("type")
                    
                    if op_type == "write":
                        # Записываем файл
                        file_path = op.get("file_path")
                        content = op.get("content")
                        mode = op.get("mode", "w")
                        encoding = op.get("encoding", "utf-8")
                        
                        # Создаем директорию, если её нет
                        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
                        
                        # Создаем временный файл
                        fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(file_path)))
                        
                        try:
                            # Записываем содержимое во временный файл
                            if "b" in mode:
                                with os.fdopen(fd, mode) as f:
                                    f.write(content)
                            else:
                                with os.fdopen(fd, mode, encoding=encoding) as f:
                                    f.write(content)
                            
                            # Атомарно заменяем файл
                            if os.name == "nt" and os.path.exists(file_path):
                                # На Windows заменяем существующий файл
                                os.replace(temp_path, file_path)
                            else:
                                # На Unix используем rename
                                os.rename(temp_path, file_path)
                        except Exception:
                            # В случае ошибки удаляем временный файл
                            if os.path.exists(temp_path):
                                os.unlink(temp_path)
                            raise
                    elif op_type == "append":
                        # Добавляем в файл
                        file_path = op.get("file_path")
                        content = op.get("content")
                        mode = op.get("mode", "a")
                        encoding = op.get("encoding", "utf-8")
                        
                        # Создаем директорию, если её нет
                        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
                        
                        # Открываем файл и добавляем содержимое
                        if "b" in mode:
                            with open(file_path, mode) as f:
                                f.write(content)
                        else:
                            with open(file_path, mode, encoding=encoding) as f:
                                f.write(content)
                    elif op_type == "delete":
                        # Удаляем файл
                        file_path = op.get("file_path")
                        
                        if os.path.exists(file_path):
                            os.unlink(file_path)
                    elif op_type == "write_json":
                        # Записываем JSON-файл
                        file_path = op.get("file_path")
                        data = op.get("data")
                        indent = op.get("indent", 2)
                        ensure_ascii = op.get("ensure_ascii", False)
                        
                        # Сериализуем данные в JSON
                        json_content = json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)
                        
                        # Создаем директорию, если её нет
                        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
                        
                        # Создаем временный файл
                        fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(file_path)))
                        
                        try:
                            # Записываем содержимое во временный файл
                            with os.fdopen(fd, "w", encoding="utf-8") as f:
                                f.write(json_content)
                            
                            # Атомарно заменяем файл
                            if os.name == "nt" and os.path.exists(file_path):
                                # На Windows заменяем существующий файл
                                os.replace(temp_path, file_path)
                            else:
                                # На Unix используем rename
                                os.rename(temp_path, file_path)
                        except Exception:
                            # В случае ошибки удаляем временный файл
                            if os.path.exists(temp_path):
                                os.unlink(temp_path)
                            raise
                    elif op_type == "update_json":
                        # Обновляем JSON-файл
                        file_path = op.get("file_path")
                        update_data = op.get("update_data")
                        create_if_not_exists = op.get("create_if_not_exists", True)
                        indent = op.get("indent", 2)
                        ensure_ascii = op.get("ensure_ascii", False)
                        
                        # Если файл существует, читаем его содержимое
                        if os.path.exists(file_path):
                            try:
                                with open(file_path, "r", encoding="utf-8") as f:
                                    try:
                                        data = json.load(f)
                                        if not isinstance(data, dict):
                                            raise TypeError("JSON-данные не являются словарем")
                                    except json.JSONDecodeError:
                                        # Если файл содержит некорректный JSON, заменяем его пустым словарем
                                        data = {}
                            except IOError as e:
                                logger.error(f"Ошибка при чтении JSON-файла {file_path}: {e}")
                                raise
                        elif create_if_not_exists:
                            # Если файл не существует, создаем пустой словарь
                            data = {}
                        else:
                            # Если файл не существует и его не нужно создавать, возвращаем ошибку
                            raise FileNotFoundError(f"Файл {file_path} не существует")
                        
                        # Обновляем данные
                        data.update(update_data)
                        
                        # Сериализуем данные в JSON
                        json_content = json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)
                        
                        # Создаем директорию, если её нет
                        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
                        
                        # Создаем временный файл
                        fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(file_path)))
                        
                        try:
                            # Записываем содержимое во временный файл
                            with os.fdopen(fd, "w", encoding="utf-8") as f:
                                f.write(json_content)
                            
                            # Атомарно заменяем файл
                            if os.name == "nt" and os.path.exists(file_path):
                                # На Windows заменяем существующий файл
                                os.replace(temp_path, file_path)
                            else:
                                # На Unix используем rename
                                os.rename(temp_path, file_path)
                        except Exception:
                            # В случае ошибки удаляем временный файл
                            if os.path.exists(temp_path):
                                os.unlink(temp_path)
                            raise
                    else:
                        # Неизвестный тип операции
                        raise ValueError(f"Неизвестный тип операции: {op_type}")
            
            # Функция для обновления кеша
            def update_cache_entries():
                if update_cache:
                    for op in operations:
                        if "file_path" in op:
                            file_path = op.get("file_path")
                            
                            if op.get("type") == "delete":
                                # Удаляем запись из кеша
                                cache_data = cls._read_cache(cache_path)
                                
                                if file_path in cache_data:
                                    del cache_data[file_path]
                                
                                cls._write_cache(cache_data, cache_path)
                            else:
                                # Обновляем запись в кеше
                                cls._update_cache_entry(file_path, cache_path)
            
            # Добавляем операции в транзакцию
            transaction.add_file_operation(execute_operations)
            transaction.add_cache_operation(update_cache_entries)
            
            # Выполняем транзакцию
            return transaction.execute()


# Декоратор для добавления атомарности операций с файлами
def with_atomic_file_operations(func):
    """
    Декоратор для добавления атомарности операций с файлами.
    
    Args:
        func: Декорируемая функция
        
    Returns:
        Декорированная функция
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """
        JTBD:
        Я (разработчик) хочу использовать функцию wrapper, чтобы эффективно выполнить соответствующую операцию.
        """
        # Получаем список файлов, с которыми будет работать функция
        files_to_lock = []
        
        # Извлекаем параметр file_path из аргументов
        for i, arg in enumerate(args):
            if i > 0 and isinstance(arg, str) and (arg.endswith(".txt") or arg.endswith(".md") or arg.endswith(".json")):
                files_to_lock.append(arg)
        
        for key, value in kwargs.items():
            if (key == "file_path" or key == "path") and isinstance(value, str):
                files_to_lock.append(value)
        
        # Если не удалось определить файлы, выполняем функцию без транзакции
        if not files_to_lock:
            return func(*args, **kwargs)
        
        # Создаем транзакцию
        with Transaction(files_to_lock=files_to_lock) as transaction:
            # Добавляем функцию в транзакцию
            transaction.add_file_operation(lambda: func(*args, **kwargs))
            
            # Выполняем транзакцию
            success = transaction.execute()
            
            if success and transaction.success:
                # Если транзакция успешна, возвращаем результат функции
                return args[0]._last_result if hasattr(args[0], "_last_result") else True
            else:
                # Если транзакция не успешна, возвращаем False
                return False
    
    return wrapper


def main():
    """JTBD:
Я (разработчик) хочу использовать функцию main, чтобы эффективно выполнить соответствующую операцию.
     
     Основная функция модуля."""
    import argparse
    
    # Настройка парсера аргументов
    parser = argparse.ArgumentParser(description="Инструменты для атомарных операций с файлами и кешем")
    
    # Добавляем подкоманды
    subparsers = parser.add_subparsers(dest="command", help="Команда для выполнения")
    
    # Подкоманда для записи файла
    write_parser = subparsers.add_parser("write", help="Записать файл")
    write_parser.add_argument("file_path", help="Путь к файлу")
    write_parser.add_argument("content", help="Содержимое для записи")
    write_parser.add_argument("--no-cache", action="store_true", help="Не обновлять кеш")
    
    # Подкоманда для чтения файла
    read_parser = subparsers.add_parser("read", help="Прочитать файл")
    read_parser.add_argument("file_path", help="Путь к файлу")
    
    # Подкоманда для обновления JSON-файла
    update_json_parser = subparsers.add_parser("update-json", help="Обновить JSON-файл")
    update_json_parser.add_argument("file_path", help="Путь к файлу")
    update_json_parser.add_argument("json_data", help="JSON-данные для обновления")
    update_json_parser.add_argument("--no-cache", action="store_true", help="Не обновлять кеш")
    
    # Подкоманда для чтения JSON-файла
    read_json_parser = subparsers.add_parser("read-json", help="Прочитать JSON-файл")
    read_json_parser.add_argument("file_path", help="Путь к файлу")
    
    # Подкоманда для удаления файла
    delete_parser = subparsers.add_parser("delete", help="Удалить файл")
    delete_parser.add_argument("file_path", help="Путь к файлу")
    delete_parser.add_argument("--no-cache", action="store_true", help="Не обновлять кеш")
    
    # Подкоманда для проверки блокировок
    locks_parser = subparsers.add_parser("locks", help="Получить статистику блокировок")
    
    # Разбор аргументов
    args = parser.parse_args()
    
    # Выполняем команду
    if args.command == "write":
        success = AtomicFileOperations.write_file(
            args.file_path,
            args.content,
            update_cache=not args.no_cache
        )
        print(f"Запись {'успешна' if success else 'не успешна'}")
    
    elif args.command == "read":
        success, content = AtomicFileOperations.read_file(args.file_path)
        if success:
            print(content)
        else:
            print("Ошибка при чтении файла")
    
    elif args.command == "update-json":
        import json
        try:
            json_data = json.loads(args.json_data)
            success = AtomicFileOperations.update_json(
                args.file_path,
                json_data,
                update_cache=not args.no_cache
            )
            print(f"Обновление {'успешно' if success else 'не успешно'}")
        except json.JSONDecodeError:
            print("Ошибка при разборе JSON-данных")
    
    elif args.command == "read-json":
        success, data = AtomicFileOperations.read_json(args.file_path)
        if success:
            import json
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print("Ошибка при чтении JSON-файла")
    
    elif args.command == "delete":
        success = AtomicFileOperations.delete_file(
            args.file_path,
            update_cache=not args.no_cache
        )
        print(f"Удаление {'успешно' if success else 'не успешно'}")
    
    elif args.command == "locks":
        stats = GlobalLockManager.get_lock_statistics()
        print(f"Всего блокировок: {stats['total_locks']}")
        print(f"Активных блокировок: {stats['active_locks']}")
        for path, lock_info in stats['locks'].items():
            print(f"- {path}: {lock_info}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()