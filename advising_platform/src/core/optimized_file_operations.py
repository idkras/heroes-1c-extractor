"""
Улучшенный класс для безопасных операций с файлами с оптимизированной проверкой синхронизации кеша.

Основные улучшения по сравнению с исходным SafeFileOperations:
1. Сокращенное время ожидания для проверки синхронизации
2. Интеллектуальное определение временных и некритичных файлов
3. Кеширование результатов проверок для избегания повторных операций
4. Механизм работы без лишних блокировок для повышения производительности
5. Встроенная поддержка работы с JSON и другими форматами данных
"""

# Импортируем оптимизированный модуль проверки синхронизации
try:
    from src.core.sync_optimized import (
        verify_disk_sync, disable_verification_for_tests, 
        clear_verification_cache, is_temp_or_test_file
    )
    SYNC_VERIFICATION_AVAILABLE = True
except ImportError:
    try:
        from sync_optimized import (
            verify_disk_sync, disable_verification_for_tests, 
            clear_verification_cache, is_temp_or_test_file
        )
        SYNC_VERIFICATION_AVAILABLE = True
    except ImportError:
        # Создаем заглушку декоратора, если модуль не найден
        def verify_disk_sync(func):
            return func
            
        def disable_verification_for_tests():
            pass
            
        def clear_verification_cache():
            pass
            
        def is_temp_or_test_file(file_path):
            return False
            
        SYNC_VERIFICATION_AVAILABLE = False
        print("ВНИМАНИЕ: Модуль sync_optimized не найден. Проверка синхронизации отключена.")

import os
import sys
import json
import time
import shutil
import logging
import tempfile
import threading
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, Set, Callable

# Настройка логирования
logger = logging.getLogger("optimized_file_operations")

# Глобальный механизм блокировки файлов для предотвращения конфликтов
file_locks = {}
file_locks_lock = threading.RLock()

class FileLockManager:
    """JTBD:
Я (разработчик) хочу управлять filelock, чтобы обеспечить корректную работу системы и контролировать использование ресурсов.
    
    Менеджер блокировок файлов для безопасного параллельного доступа."""
    
    @staticmethod
    def acquire_lock(file_path):
        """
        Захватывает блокировку для указанного файла.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            threading.RLock: Объект блокировки
        """
        with file_locks_lock:
            if file_path not in file_locks:
                file_locks[file_path] = threading.RLock()
            
            lock = file_locks[file_path]
            lock.acquire()
            
            return lock
    
    @staticmethod
    def release_lock(file_path):
        """
        Освобождает блокировку для указанного файла.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            bool: True, если блокировка освобождена, иначе False
        """
        with file_locks_lock:
            if file_path not in file_locks:
                logger.warning(f"Попытка освободить несуществующую блокировку для файла {file_path}")
                return False
            
            lock = file_locks[file_path]
            lock.release()
            
            return True
    
    @staticmethod
    def clean_locks():
        """
        Очищает все блокировки.
        
        Returns:
            int: Количество очищенных блокировок
        """
        with file_locks_lock:
            count = len(file_locks)
            file_locks.clear()
            return count

class OptimizedFileOperations:
    """
    Улучшенный класс для безопасных операций с файлами с оптимизированной проверкой синхронизации кеша.
    
    Основные возможности:
    - Запись и чтение текстовых файлов с проверкой целостности
    - Запись и чтение JSON-файлов с поддержкой Unicode
    - Добавление данных в существующие файлы
    - Автоматическое создание резервных копий при изменении
    - Оптимизированная проверка синхронизации с кешем
    - Восстановление из резервных копий при ошибках
    """
    
    # Настройки безопасных операций
    BACKUP_DIR = ".file_backups"
    MAX_BACKUP_AGE_DAYS = 7
    CACHE_FILES = [
        ".cache_state.json",
        ".cache_detailed_state.json",
        ".critical_instructions_cache.json",
        ".task_stats.json",
        ".context_cache_state.json"
    ]
    
    # Оптимистичный режим для работы с временными файлами
    OPTIMISTIC_MODE = True
    
    # Флаг инициализации класса
    _initialized = False
    
    @classmethod
    def setup(cls):
        """
        Инициализирует необходимые директории и настройки.
        
        Returns:
            bool: True, если инициализация успешна, иначе False
        """
        if cls._initialized:
            return True
            
        try:
            # Создаем директорию для резервных копий
            if not os.path.exists(cls.BACKUP_DIR):
                os.makedirs(cls.BACKUP_DIR)
            
            # Очищаем старые резервные копии
            cls.cleanup_old_backups()
            
            # Регистрируем обработчик для очистки при завершении
            import atexit
            atexit.register(cls.cleanup)
            
            cls._initialized = True
            logger.info("OptimizedFileOperations успешно инициализирован")
            return True
        except Exception as e:
            logger.error(f"Ошибка при инициализации OptimizedFileOperations: {e}")
            return False
    
    @classmethod
    def cleanup(cls):
        """
        Выполняет очистку ресурсов при завершении работы.
        
        Returns:
            bool: True, если очистка успешна, иначе False
        """
        try:
            # Очищаем блокировки файлов
            locks_count = FileLockManager.clean_locks()
            
            # Очищаем кеш результатов верификации
            if SYNC_VERIFICATION_AVAILABLE:
                clear_verification_cache()
            
            logger.info(f"OptimizedFileOperations успешно очищен")
            return True
        except Exception as e:
            logger.error(f"Ошибка при очистке OptimizedFileOperations: {e}")
            return False
    
    @classmethod
    def cleanup_old_backups(cls):
        """
        Очищает старые резервные копии файлов.
        
        Returns:
            int: Количество удаленных файлов
        """
        if not os.path.exists(cls.BACKUP_DIR):
            return 0
        
        count = 0
        now = datetime.now()
        cutoff_date = now - timedelta(days=cls.MAX_BACKUP_AGE_DAYS)
        
        for filename in os.listdir(cls.BACKUP_DIR):
            file_path = os.path.join(cls.BACKUP_DIR, filename)
            
            if os.path.isfile(file_path):
                # Извлекаем временную метку из имени файла
                # Формат: original_name.timestamp.bak
                try:
                    parts = filename.split('.')
                    timestamp = float(parts[-2])
                    file_date = datetime.fromtimestamp(timestamp)
                    
                    if file_date < cutoff_date:
                        os.remove(file_path)
                        count += 1
                except (IndexError, ValueError):
                    # Если не удается извлечь временную метку, пропускаем файл
                    continue
        
        logger.info(f"Удалено {count} устаревших резервных копий")
        return count
    
    @classmethod
    def create_backup(cls, file_path):
        """
        Создает резервную копию файла.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            str: Путь к резервной копии или None, если копия не создана
        """
        if not os.path.exists(file_path):
            return None
        
        try:
            # Создаем директорию для резервных копий, если её нет
            if not os.path.exists(cls.BACKUP_DIR):
                os.makedirs(cls.BACKUP_DIR)
            
            # Получаем имя файла и временную метку
            filename = os.path.basename(file_path)
            timestamp = int(time.time())
            
            # Формируем имя резервной копии
            backup_path = os.path.join(cls.BACKUP_DIR, f"{filename}.{timestamp}.bak")
            
            # Копируем файл
            shutil.copy2(file_path, backup_path)
            
            logger.info(f"Создана резервная копия файла {file_path} -> {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Ошибка при создании резервной копии файла {file_path}: {e}")
            return None
    
    @classmethod
    def restore_from_backup(cls, file_path):
        """
        Восстанавливает файл из последней резервной копии.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            bool: True, если восстановление успешно, иначе False
        """
        if not os.path.exists(cls.BACKUP_DIR):
            logger.error(f"Директория резервных копий {cls.BACKUP_DIR} не найдена")
            return False
        
        try:
            # Получаем имя файла
            filename = os.path.basename(file_path)
            
            # Ищем все резервные копии для этого файла
            backups = []
            for backup_file in os.listdir(cls.BACKUP_DIR):
                if backup_file.startswith(filename + ".") and backup_file.endswith(".bak"):
                    backups.append(os.path.join(cls.BACKUP_DIR, backup_file))
            
            if not backups:
                logger.warning(f"Резервные копии для файла {file_path} не найдены")
                return False
            
            # Сортируем по времени создания (последняя будет первой)
            backups.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            # Берем самую свежую копию
            latest_backup = backups[0]
            
            # Восстанавливаем файл
            shutil.copy2(latest_backup, file_path)
            
            logger.info(f"Файл {file_path} восстановлен из резервной копии {latest_backup}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при восстановлении файла {file_path} из резервной копии: {e}")
            return False
    
    @classmethod
    def verify_file_integrity(cls, file_path):
        """
        Проверяет целостность файла и пытается восстановить его при необходимости.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            bool: True, если файл целостен или восстановлен, иначе False
        """
        if not os.path.exists(file_path):
            logger.warning(f"Файл {file_path} не существует")
            return False
        
        try:
            # Проверяем, можно ли открыть файл
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Если файл JSON, проверяем его валидность
            if file_path.endswith('.json'):
                try:
                    json.loads(content)
                except json.JSONDecodeError:
                    logger.warning(f"Файл {file_path} содержит невалидный JSON")
                    
                    # Пытаемся восстановить из резервной копии
                    if cls.restore_from_backup(file_path):
                        return True
                    
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Ошибка при проверке целостности файла {file_path}: {e}")
            
            # Пытаемся восстановить из резервной копии
            if cls.restore_from_backup(file_path):
                return True
            
            return False
    
    @classmethod
    def update_cache_if_needed(cls, file_path):
        """
        Обновляет информацию о файле в кеше, если это необходимо.
        Оптимизированная версия с пропуском обновления для временных файлов.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            bool: True, если обновление выполнено, False если не требуется или произошла ошибка
        """
        # Проверяем, является ли файл кешем
        if os.path.basename(file_path) in cls.CACHE_FILES:
            logger.info(f"Файл {file_path} является кешем, дополнительное обновление не требуется")
            return True
        
        # В оптимистичном режиме пропускаем обновление кеша для временных файлов
        if cls.OPTIMISTIC_MODE and is_temp_or_test_file(file_path):
            logger.info(f"Файл {file_path} является временным, пропускаем обновление кеша")
            return True
        
        try:
            # Проверяем наличие файла .cache_state.json
            cache_state_path = ".cache_state.json"
            if not os.path.exists(cache_state_path):
                logger.info(f"Файл кеша {cache_state_path} не найден, обновление не требуется")
                return True
            
            # Загружаем состояние кеша
            with open(cache_state_path, 'r', encoding='utf-8') as f:
                cache_state = json.load(f)
            
            # Проверяем, есть ли файл в кеше
            if file_path in cache_state:
                # Обновляем информацию о файле в кеше
                cache_state[file_path] = {
                    "last_modified": os.path.getmtime(file_path),
                    "size": os.path.getsize(file_path),
                    "cached_at": time.time()
                }
                
                # Сохраняем обновленный кеш
                with open(cache_state_path, 'w', encoding='utf-8') as f:
                    json.dump(cache_state, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Обновлена информация о файле {file_path} в кеше")
                return True
            else:
                logger.info(f"Файл {file_path} не найден в кеше, обновление не требуется")
                return True
        except Exception as e:
            logger.error(f"Ошибка при обновлении кеша для файла {file_path}: {e}")
            return False
    
    @classmethod
    @verify_disk_sync
    def write_file(cls, path, content, ensure_cache_sync=True, create_backup=True):
        """
        Безопасная запись в файл с обеспечением атомарности и синхронизации с кешем.
        
        Args:
            path: Путь к файлу
            content: Содержимое для записи
            ensure_cache_sync: Проверять синхронизацию с кешем после записи
            create_backup: Создавать резервную копию перед записью
            
        Returns:
            bool: True, если запись успешна, иначе False
        """
        # Инициализируем класс при первом вызове
        if not cls._initialized:
            cls.setup()
        
        # Захватываем блокировку для файла
        lock = FileLockManager.acquire_lock(path)
        
        try:
            # Создаем директорию, если её нет
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            
            # Создаем резервную копию, если требуется
            if create_backup and os.path.exists(path):
                cls.create_backup(path)
            
            # Операции с временным файлом для обеспечения атомарности
            temp_fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(path)))
            
            try:
                # Записываем данные во временный файл
                with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                    f.write(content)
                    f.flush()
                    os.fsync(f.fileno())  # Обеспечиваем сброс на диск
                
                # Атомарно заменяем целевой файл временным
                if os.path.exists(path):
                    # В Windows нельзя переместить файл на место существующего
                    if os.name == 'nt':
                        os.remove(path)
                
                os.replace(temp_path, path)
                
                # Обновляем кеш, если требуется
                if ensure_cache_sync:
                    cls.update_cache_if_needed(path)
                
                logger.info(f"Файл {path} успешно записан")
                return True
            except Exception as e:
                # Удаляем временный файл в случае ошибки
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
                # Восстанавливаем из резервной копии
                if create_backup and os.path.exists(path):
                    cls.restore_from_backup(path)
                
                logger.error(f"Ошибка при записи файла {path}: {e}")
                return False
        except Exception as e:
            logger.error(f"Ошибка при подготовке к записи файла {path}: {e}")
            return False
        finally:
            # Освобождаем блокировку
            FileLockManager.release_lock(path)
    
    @classmethod
    @verify_disk_sync
    def read_file(cls, path, ensure_cache_sync=True):
        """
        Безопасное чтение файла с проверкой целостности.
        
        Args:
            path: Путь к файлу
            ensure_cache_sync: Проверять синхронизацию с кешем после чтения
            
        Returns:
            tuple: (success, content) - True и содержимое файла при успехе, False и None при ошибке
        """
        # Инициализируем класс при первом вызове
        if not cls._initialized:
            cls.setup()
        
        # Захватываем блокировку для файла
        lock = FileLockManager.acquire_lock(path)
        
        try:
            # Проверяем существование файла
            if not os.path.exists(path):
                logger.warning(f"Файл {path} не существует")
                return False, None
            
            try:
                # Читаем содержимое файла
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Обновляем кеш, если требуется
                if ensure_cache_sync:
                    cls.update_cache_if_needed(path)
                
                logger.info(f"Файл {path} успешно прочитан")
                return True, content
            except Exception as e:
                logger.error(f"Ошибка при чтении файла {path}: {e}")
                
                # Проверяем, можно ли восстановить файл
                if cls.verify_file_integrity(path):
                    # Пытаемся прочитать еще раз
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        logger.info(f"Файл {path} успешно прочитан после восстановления")
                        return True, content
                    except Exception as e2:
                        logger.error(f"Ошибка при повторном чтении файла {path} после восстановления: {e2}")
                
                return False, None
        finally:
            # Освобождаем блокировку
            FileLockManager.release_lock(path)
    
    @classmethod
    @verify_disk_sync
    def append_to_file(cls, path, content, ensure_cache_sync=True, create_backup=True):
        """
        Безопасное добавление данных в конец файла.
        
        Args:
            path: Путь к файлу
            content: Содержимое для добавления
            ensure_cache_sync: Проверять синхронизацию с кешем после добавления
            create_backup: Создавать резервную копию перед добавлением
            
        Returns:
            bool: True, если добавление успешно, иначе False
        """
        # Инициализируем класс при первом вызове
        if not cls._initialized:
            cls.setup()
        
        # Захватываем блокировку для файла
        lock = FileLockManager.acquire_lock(path)
        
        try:
            # Если файл не существует, создаем его
            if not os.path.exists(path):
                return cls.write_file(path, content, ensure_cache_sync, False)
            
            # Создаем резервную копию, если требуется
            if create_backup:
                cls.create_backup(path)
            
            # Читаем текущее содержимое файла
            success, current_content = cls.read_file(path, False)
            if not success:
                logger.error(f"Ошибка при чтении файла {path} для добавления данных")
                return False
            
            # Добавляем новое содержимое
            new_content = current_content + content
            
            # Записываем обновленное содержимое
            return cls.write_file(path, new_content, ensure_cache_sync, False)
        finally:
            # Освобождаем блокировку
            FileLockManager.release_lock(path)
    
    @classmethod
    @verify_disk_sync
    def delete_file(cls, path, ensure_cache_sync=True):
        """
        Безопасное удаление файла с созданием резервной копии.
        
        Args:
            path: Путь к файлу
            ensure_cache_sync: Проверять синхронизацию с кешем после удаления
            
        Returns:
            bool: True, если удаление успешно, иначе False
        """
        # Инициализируем класс при первом вызове
        if not cls._initialized:
            cls.setup()
        
        # Захватываем блокировку для файла
        lock = FileLockManager.acquire_lock(path)
        
        try:
            # Проверяем существование файла
            if not os.path.exists(path):
                logger.warning(f"Файл {path} не существует, удаление не требуется")
                return True
            
            try:
                # Создаем резервную копию
                cls.create_backup(path)
                
                # Удаляем файл
                os.remove(path)
                
                # Обновляем кеш, если требуется
                if ensure_cache_sync:
                    cls.update_cache_if_needed(path)
                
                logger.info(f"Файл {path} успешно удален")
                return True
            except Exception as e:
                logger.error(f"Ошибка при удалении файла {path}: {e}")
                return False
        finally:
            # Освобождаем блокировку
            FileLockManager.release_lock(path)
    
    @classmethod
    @verify_disk_sync
    def write_json(cls, path, data, ensure_cache_sync=True, create_backup=True, indent=2):
        """
        Безопасная запись данных в JSON-файл.
        
        Args:
            path: Путь к файлу
            data: Данные для записи (словарь или список)
            ensure_cache_sync: Проверять синхронизацию с кешем после записи
            create_backup: Создавать резервную копию перед записью
            indent: Отступ для форматирования JSON
            
        Returns:
            bool: True, если запись успешна, иначе False
        """
        try:
            # Преобразуем данные в JSON-строку
            json_str = json.dumps(data, ensure_ascii=False, indent=indent)
            
            # Записываем в файл
            return cls.write_file(path, json_str, ensure_cache_sync, create_backup)
        except Exception as e:
            logger.error(f"Ошибка при преобразовании данных в JSON для файла {path}: {e}")
            return False
    
    @classmethod
    @verify_disk_sync
    def read_json(cls, path, ensure_cache_sync=True):
        """
        Безопасное чтение данных из JSON-файла.
        
        Args:
            path: Путь к файлу
            ensure_cache_sync: Проверять синхронизацию с кешем после чтения
            
        Returns:
            tuple: (success, data) - True и данные при успехе, False и None при ошибке
        """
        # Читаем содержимое файла
        success, content = cls.read_file(path, ensure_cache_sync)
        if not success:
            return False, None
        
        try:
            # Преобразуем JSON-строку в данные
            data = json.loads(content)
            return True, data
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка при разборе JSON из файла {path}: {e}")
            
            # Пытаемся восстановить файл
            if cls.restore_from_backup(path):
                logger.info(f"Файл {path} восстановлен из резервной копии, пробуем прочитать снова")
                
                # Пытаемся прочитать еще раз
                success, content = cls.read_file(path, ensure_cache_sync)
                if not success:
                    return False, None
                
                try:
                    data = json.loads(content)
                    return True, data
                except json.JSONDecodeError as e2:
                    logger.error(f"Ошибка при повторном разборе JSON из файла {path} после восстановления: {e2}")
            
            return False, None
        except Exception as e:
            logger.error(f"Неизвестная ошибка при работе с JSON-файлом {path}: {e}")
            return False, None
    
    @classmethod
    def calculate_file_hash(cls, path):
        """
        Вычисляет хеш-сумму файла.
        
        Args:
            path: Путь к файлу
            
        Returns:
            str: MD5-хеш файла или None, если файл не существует
        """
        if not os.path.exists(path):
            return None
        
        try:
            hash_md5 = hashlib.md5()
            
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Ошибка при вычислении хеша файла {path}: {e}")
            return None
    
    @classmethod
    def disable_sync_verification_for_tests(cls):
        """
        Отключает верификацию синхронизации в тестовом окружении.
        Полезно для ускорения выполнения тестов.
        """
        if SYNC_VERIFICATION_AVAILABLE:
            disable_verification_for_tests()
            logger.info("Верификация синхронизации отключена для тестового окружения")
        else:
            logger.warning("Модуль sync_optimized не доступен, отключение верификации невозможно")
        
        # Устанавливаем оптимистичный режим
        cls.OPTIMISTIC_MODE = True

# Инициализируем класс при импорте
OptimizedFileOperations.setup()