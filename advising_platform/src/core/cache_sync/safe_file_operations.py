"""
Модуль для безопасных операций с файлами, обеспечивающих атомарность и синхронизацию с кешем.

Обеспечивает:
1. Атомарные операции чтения и записи файлов
2. Автоматическую синхронизацию с кешем при изменении файлов
3. Поддержку транзакционных операций с файлами
4. Автоматическое восстановление при сбоях
5. Журналирование операций для отладки
"""

import os
import time
import shutil
import logging
import tempfile
from pathlib import Path
from typing import Tuple, Optional, Dict, Any, List, Callable
from functools import wraps

# Настраиваем логирование
logger = logging.getLogger("safe_file_operations")

# Константы
DEFAULT_ENCODING = 'utf-8'
MAX_RETRIES = 3
RETRY_DELAY = 0.5  # секунды
TEMP_DIR = '.file_operations_temp'


def verify_disk_sync(func):
    """
    Декоратор для проверки синхронизации с кешем до и после операций с файлами.
    
    Args:
        func: Функция для декорирования
        
    Returns:
        Обернутая функция
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Импортируем здесь, чтобы избежать циклических импортов
        from advising_platform.src.core.cache_sync.cache_manager import CacheManager
        
        # Получаем путь к файлу из аргументов функции
        file_path = None
        if len(args) > 0 and isinstance(args[0], str):
            file_path = args[0]
        elif 'path' in kwargs:
            file_path = kwargs['path']
        
        if not file_path:
            logger.warning("Не удалось определить путь к файлу для проверки синхронизации")
            return func(*args, **kwargs)
        
        # Проверяем синхронизацию перед операцией
        try:
            cache_manager = CacheManager.get_instance()
            cache_manager.verify_file_cache_sync(file_path)
        except Exception as e:
            logger.warning(f"Ошибка при проверке синхронизации с кешем перед операцией: {e}")
        
        # Выполняем операцию с файлом
        result = func(*args, **kwargs)
        
        # Проверяем синхронизацию после операции
        try:
            cache_manager = CacheManager.get_instance()
            cache_manager.verify_file_cache_sync(file_path)
        except Exception as e:
            logger.warning(f"Ошибка при проверке синхронизации с кешем после операции: {e}")
        
        return result
    
    return wrapper


class SafeFileOperations:
    """
    Класс для безопасных операций с файлами, обеспечивающих атомарность и синхронизацию с кешем.
    """
    
    @classmethod
    @verify_disk_sync
    def read_file(cls, path: str, encoding: str = DEFAULT_ENCODING, 
                 raise_error: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Безопасное чтение файла с автоматической проверкой синхронизации с кешем.
        
        Args:
            path: Путь к файлу
            encoding: Кодировка файла
            raise_error: Вызывать исключение при ошибке
            
        Returns:
            Tuple[bool, Optional[str]]: (успех, содержимое)
        """
        if not os.path.exists(path):
            message = f"Файл не найден: {path}"
            logger.error(message)
            if raise_error:
                raise FileNotFoundError(message)
            return False, None
        
        try:
            for attempt in range(MAX_RETRIES):
                try:
                    with open(path, 'r', encoding=encoding) as f:
                        content = f.read()
                    logger.debug(f"Файл успешно прочитан: {path}")
                    return True, content
                except (IOError, OSError) as e:
                    if attempt < MAX_RETRIES - 1:
                        logger.warning(f"Ошибка при чтении файла {path} (попытка {attempt+1}/{MAX_RETRIES}): {e}")
                        time.sleep(RETRY_DELAY)
                    else:
                        raise
        except Exception as e:
            message = f"Ошибка при чтении файла {path}: {e}"
            logger.error(message)
            if raise_error:
                raise
            return False, None
    
    @classmethod
    @verify_disk_sync
    def write_file(cls, path: str, content: str, encoding: str = DEFAULT_ENCODING,
                  backup: bool = True, raise_error: bool = False) -> bool:
        """
        Безопасная запись в файл с обеспечением атомарности и синхронизации с кешем.
        
        Args:
            path: Путь к файлу
            content: Содержимое для записи
            encoding: Кодировка файла
            backup: Создавать резервную копию
            raise_error: Вызывать исключение при ошибке
            
        Returns:
            bool: True, если запись успешна, иначе False
        """
        try:
            # Создаем директорию для временных файлов, если её нет
            if not os.path.exists(TEMP_DIR):
                os.makedirs(TEMP_DIR, exist_ok=True)
            
            # Создаем директорию, если её нет
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            
            # Пути к временным файлам
            temp_name = os.path.join(TEMP_DIR, f"{os.path.basename(path)}.{int(time.time())}.tmp")
            backup_name = os.path.join(TEMP_DIR, f"{os.path.basename(path)}.{int(time.time())}.bak")
            
            # Создаем резервную копию, если требуется
            if backup and os.path.exists(path):
                shutil.copy2(path, backup_name)
                logger.debug(f"Создана резервная копия: {backup_name}")
            
            # Записываем содержимое во временный файл
            with open(temp_name, 'w', encoding=encoding) as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())  # Обеспечиваем сброс на диск
            
            # Атомарно заменяем целевой файл временным
            shutil.move(temp_name, path)
            
            logger.debug(f"Файл успешно записан: {path}")
            return True
            
        except Exception as e:
            message = f"Ошибка при записи в файл {path}: {e}"
            logger.error(message)
            
            # Пытаемся восстановить из резервной копии
            if backup and os.path.exists(backup_name):
                try:
                    shutil.move(backup_name, path)
                    logger.info(f"Восстановлен файл {path} из резервной копии")
                except Exception as recover_error:
                    logger.error(f"Ошибка при восстановлении из резервной копии: {recover_error}")
            
            if raise_error:
                raise
            return False
    
    @classmethod
    @verify_disk_sync
    def append_to_file(cls, path: str, content: str, encoding: str = DEFAULT_ENCODING,
                      backup: bool = True, raise_error: bool = False) -> bool:
        """
        Безопасное добавление текста в конец файла.
        
        Args:
            path: Путь к файлу
            content: Содержимое для добавления
            encoding: Кодировка файла
            backup: Создавать резервную копию
            raise_error: Вызывать исключение при ошибке
            
        Returns:
            bool: True, если добавление успешно, иначе False
        """
        # Сначала читаем текущее содержимое
        success, current_content = cls.read_file(path, encoding, raise_error)
        
        if not success:
            # Если файл не существует, создаем его
            if not os.path.exists(path):
                return cls.write_file(path, content, encoding, backup, raise_error)
            return False
        
        # Добавляем новый контент и записываем файл
        new_content = current_content + content
        return cls.write_file(path, new_content, encoding, backup, raise_error)
    
    @classmethod
    @verify_disk_sync
    def insert_into_file(cls, path: str, content: str, position: int, 
                        encoding: str = DEFAULT_ENCODING, backup: bool = True,
                        raise_error: bool = False) -> bool:
        """
        Безопасная вставка текста в указанную позицию файла.
        
        Args:
            path: Путь к файлу
            content: Содержимое для вставки
            position: Позиция для вставки
            encoding: Кодировка файла
            backup: Создавать резервную копию
            raise_error: Вызывать исключение при ошибке
            
        Returns:
            bool: True, если вставка успешна, иначе False
        """
        # Сначала читаем текущее содержимое
        success, current_content = cls.read_file(path, encoding, raise_error)
        
        if not success:
            return False
        
        # Проверяем позицию
        if position < 0 or position > len(current_content):
            message = f"Некорректная позиция для вставки: {position}"
            logger.error(message)
            if raise_error:
                raise ValueError(message)
            return False
        
        # Вставляем текст и записываем файл
        new_content = current_content[:position] + content + current_content[position:]
        return cls.write_file(path, new_content, encoding, backup, raise_error)
    
    @classmethod
    @verify_disk_sync
    def replace_in_file(cls, path: str, old_content: str, new_content: str,
                       encoding: str = DEFAULT_ENCODING, backup: bool = True,
                       raise_error: bool = False) -> bool:
        """
        Безопасная замена текста в файле.
        
        Args:
            path: Путь к файлу
            old_content: Текст для замены
            new_content: Новый текст
            encoding: Кодировка файла
            backup: Создавать резервную копию
            raise_error: Вызывать исключение при ошибке
            
        Returns:
            bool: True, если замена успешна, иначе False
        """
        # Сначала читаем текущее содержимое
        success, current_content = cls.read_file(path, encoding, raise_error)
        
        if not success:
            return False
        
        # Проверяем наличие заменяемого текста
        if old_content not in current_content:
            message = f"Заменяемый текст не найден в файле: {path}"
            logger.error(message)
            if raise_error:
                raise ValueError(message)
            return False
        
        # Заменяем текст и записываем файл
        new_file_content = current_content.replace(old_content, new_content)
        return cls.write_file(path, new_file_content, encoding, backup, raise_error)
    
    @classmethod
    def delete_file(cls, path: str, backup: bool = True, 
                   raise_error: bool = False) -> bool:
        """
        Безопасное удаление файла с возможностью восстановления.
        
        Args:
            path: Путь к файлу
            backup: Создавать резервную копию
            raise_error: Вызывать исключение при ошибке
            
        Returns:
            bool: True, если удаление успешно, иначе False
        """
        if not os.path.exists(path):
            message = f"Файл не найден: {path}"
            logger.error(message)
            if raise_error:
                raise FileNotFoundError(message)
            return False
        
        try:
            # Создаем директорию для временных файлов, если её нет
            if not os.path.exists(TEMP_DIR):
                os.makedirs(TEMP_DIR, exist_ok=True)
            
            # Создаем резервную копию, если требуется
            if backup:
                backup_name = os.path.join(TEMP_DIR, f"{os.path.basename(path)}.{int(time.time())}.bak")
                shutil.copy2(path, backup_name)
                logger.debug(f"Создана резервная копия перед удалением: {backup_name}")
            
            # Удаляем файл
            os.remove(path)
            
            logger.debug(f"Файл успешно удален: {path}")
            return True
            
        except Exception as e:
            message = f"Ошибка при удалении файла {path}: {e}"
            logger.error(message)
            if raise_error:
                raise
            return False
    
    @classmethod
    def move_file(cls, source: str, destination: str, 
                 overwrite: bool = False, backup: bool = True,
                 raise_error: bool = False) -> bool:
        """
        Безопасное перемещение файла.
        
        Args:
            source: Путь к исходному файлу
            destination: Путь назначения
            overwrite: Перезаписывать существующий файл
            backup: Создавать резервную копию
            raise_error: Вызывать исключение при ошибке
            
        Returns:
            bool: True, если перемещение успешно, иначе False
        """
        if not os.path.exists(source):
            message = f"Исходный файл не найден: {source}"
            logger.error(message)
            if raise_error:
                raise FileNotFoundError(message)
            return False
        
        # Проверяем, существует ли файл назначения
        if os.path.exists(destination):
            if not overwrite:
                message = f"Файл назначения уже существует: {destination}"
                logger.error(message)
                if raise_error:
                    raise FileExistsError(message)
                return False
            
            # Если нужна резервная копия, создаем её
            if backup:
                try:
                    # Создаем директорию для временных файлов, если её нет
                    if not os.path.exists(TEMP_DIR):
                        os.makedirs(TEMP_DIR, exist_ok=True)
                    
                    backup_name = os.path.join(TEMP_DIR, f"{os.path.basename(destination)}.{int(time.time())}.bak")
                    shutil.copy2(destination, backup_name)
                    logger.debug(f"Создана резервная копия перед перезаписью: {backup_name}")
                except Exception as e:
                    logger.warning(f"Ошибка при создании резервной копии: {e}")
        
        try:
            # Создаем директорию назначения, если её нет
            os.makedirs(os.path.dirname(os.path.abspath(destination)), exist_ok=True)
            
            # Перемещаем файл
            shutil.move(source, destination)
            
            logger.debug(f"Файл успешно перемещен: {source} -> {destination}")
            return True
            
        except Exception as e:
            message = f"Ошибка при перемещении файла {source} -> {destination}: {e}"
            logger.error(message)
            if raise_error:
                raise
            return False
    
    @classmethod
    def copy_file(cls, source: str, destination: str, 
                 overwrite: bool = False, backup: bool = True,
                 raise_error: bool = False) -> bool:
        """
        Безопасное копирование файла.
        
        Args:
            source: Путь к исходному файлу
            destination: Путь назначения
            overwrite: Перезаписывать существующий файл
            backup: Создавать резервную копию
            raise_error: Вызывать исключение при ошибке
            
        Returns:
            bool: True, если копирование успешно, иначе False
        """
        if not os.path.exists(source):
            message = f"Исходный файл не найден: {source}"
            logger.error(message)
            if raise_error:
                raise FileNotFoundError(message)
            return False
        
        # Проверяем, существует ли файл назначения
        if os.path.exists(destination):
            if not overwrite:
                message = f"Файл назначения уже существует: {destination}"
                logger.error(message)
                if raise_error:
                    raise FileExistsError(message)
                return False
            
            # Если нужна резервная копия, создаем её
            if backup:
                try:
                    # Создаем директорию для временных файлов, если её нет
                    if not os.path.exists(TEMP_DIR):
                        os.makedirs(TEMP_DIR, exist_ok=True)
                    
                    backup_name = os.path.join(TEMP_DIR, f"{os.path.basename(destination)}.{int(time.time())}.bak")
                    shutil.copy2(destination, backup_name)
                    logger.debug(f"Создана резервная копия перед перезаписью: {backup_name}")
                except Exception as e:
                    logger.warning(f"Ошибка при создании резервной копии: {e}")
        
        try:
            # Создаем директорию назначения, если её нет
            os.makedirs(os.path.dirname(os.path.abspath(destination)), exist_ok=True)
            
            # Копируем файл
            shutil.copy2(source, destination)
            
            logger.debug(f"Файл успешно скопирован: {source} -> {destination}")
            return True
            
        except Exception as e:
            message = f"Ошибка при копировании файла {source} -> {destination}: {e}"
            logger.error(message)
            if raise_error:
                raise
            return False
    
    @classmethod
    def create_directory(cls, path: str, raise_error: bool = False) -> bool:
        """
        Безопасное создание директории.
        
        Args:
            path: Путь к директории
            raise_error: Вызывать исключение при ошибке
            
        Returns:
            bool: True, если создание успешно, иначе False
        """
        try:
            os.makedirs(path, exist_ok=True)
            logger.debug(f"Директория успешно создана: {path}")
            return True
        except Exception as e:
            message = f"Ошибка при создании директории {path}: {e}"
            logger.error(message)
            if raise_error:
                raise
            return False
    
    @classmethod
    def list_directory(cls, path: str, pattern: str = None, 
                      recursive: bool = False, raise_error: bool = False) -> List[str]:
        """
        Безопасное получение списка файлов в директории.
        
        Args:
            path: Путь к директории
            pattern: Шаблон для фильтрации файлов
            recursive: Рекурсивный поиск
            raise_error: Вызывать исключение при ошибке
            
        Returns:
            List[str]: Список путей к файлам
        """
        if not os.path.exists(path):
            message = f"Директория не найдена: {path}"
            logger.error(message)
            if raise_error:
                raise FileNotFoundError(message)
            return []
        
        try:
            result = []
            
            if recursive:
                for root, _, files in os.walk(path):
                    for file in files:
                        if pattern is None or Path(file).match(pattern):
                            result.append(os.path.join(root, file))
            else:
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    if os.path.isfile(item_path):
                        if pattern is None or Path(item).match(pattern):
                            result.append(item_path)
            
            return result
        except Exception as e:
            message = f"Ошибка при получении списка файлов в директории {path}: {e}"
            logger.error(message)
            if raise_error:
                raise
            return []
    
    @classmethod
    def check_file_exists(cls, path: str) -> bool:
        """
        Проверяет существование файла.
        
        Args:
            path: Путь к файлу
            
        Returns:
            bool: True, если файл существует, иначе False
        """
        return os.path.isfile(path)
    
    @classmethod
    def check_directory_exists(cls, path: str) -> bool:
        """
        Проверяет существование директории.
        
        Args:
            path: Путь к директории
            
        Returns:
            bool: True, если директория существует, иначе False
        """
        return os.path.isdir(path)
    
    @classmethod
    def get_file_metadata(cls, path: str, raise_error: bool = False) -> Dict[str, Any]:
        """
        Получает метаданные файла.
        
        Args:
            path: Путь к файлу
            raise_error: Вызывать исключение при ошибке
            
        Returns:
            Dict[str, Any]: Метаданные файла
        """
        if not os.path.exists(path):
            message = f"Файл не найден: {path}"
            logger.error(message)
            if raise_error:
                raise FileNotFoundError(message)
            return {}
        
        try:
            stat_info = os.stat(path)
            return {
                "size": stat_info.st_size,
                "created": stat_info.st_ctime,
                "modified": stat_info.st_mtime,
                "accessed": stat_info.st_atime,
                "is_file": os.path.isfile(path),
                "is_directory": os.path.isdir(path),
                "path": os.path.abspath(path),
                "basename": os.path.basename(path),
                "dirname": os.path.dirname(path),
                "extension": os.path.splitext(path)[1],
            }
        except Exception as e:
            message = f"Ошибка при получении метаданных файла {path}: {e}"
            logger.error(message)
            if raise_error:
                raise
            return {}
    
    @classmethod
    def create_temp_file(cls, prefix: str = "temp_", suffix: str = ".tmp",
                        directory: str = None, content: str = None,
                        encoding: str = DEFAULT_ENCODING,
                        raise_error: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Создает временный файл.
        
        Args:
            prefix: Префикс имени файла
            suffix: Суффикс имени файла
            directory: Директория для создания файла
            content: Содержимое файла
            encoding: Кодировка файла
            raise_error: Вызывать исключение при ошибке
            
        Returns:
            Tuple[bool, Optional[str]]: (успех, путь к временному файлу)
        """
        try:
            # Если директория не указана, используем стандартную для временных файлов
            if directory is None:
                if not os.path.exists(TEMP_DIR):
                    os.makedirs(TEMP_DIR, exist_ok=True)
                directory = TEMP_DIR
            
            # Создаем директорию, если её нет
            os.makedirs(directory, exist_ok=True)
            
            # Создаем временный файл
            fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=directory)
            
            # Записываем содержимое, если оно указано
            if content is not None:
                with os.fdopen(fd, 'w', encoding=encoding) as f:
                    f.write(content)
            else:
                os.close(fd)
            
            logger.debug(f"Создан временный файл: {path}")
            return True, path
            
        except Exception as e:
            message = f"Ошибка при создании временного файла: {e}"
            logger.error(message)
            if raise_error:
                raise
            return False, None
    
    @classmethod
    def batch_process_files(cls, files: List[str], process_func: Callable,
                          backup: bool = True, raise_error: bool = False) -> Dict[str, bool]:
        """
        Пакетная обработка файлов.
        
        Args:
            files: Список путей к файлам
            process_func: Функция для обработки файла
            backup: Создавать резервную копию
            raise_error: Вызывать исключение при ошибке
            
        Returns:
            Dict[str, bool]: Словарь {путь_к_файлу: успех}
        """
        results = {}
        
        for file_path in files:
            try:
                # Создаем резервную копию, если требуется
                if backup and os.path.exists(file_path):
                    if not os.path.exists(TEMP_DIR):
                        os.makedirs(TEMP_DIR, exist_ok=True)
                    
                    backup_name = os.path.join(TEMP_DIR, f"{os.path.basename(file_path)}.{int(time.time())}.bak")
                    shutil.copy2(file_path, backup_name)
                    logger.debug(f"Создана резервная копия: {backup_name}")
                
                # Обрабатываем файл
                success = process_func(file_path)
                results[file_path] = success
                
                if not success:
                    logger.warning(f"Обработка файла {file_path} завершилась неудачно")
                    
                    # Восстанавливаем из резервной копии, если требуется
                    if backup and os.path.exists(backup_name):
                        try:
                            shutil.copy2(backup_name, file_path)
                            logger.info(f"Восстановлен файл {file_path} из резервной копии")
                        except Exception as recover_error:
                            logger.error(f"Ошибка при восстановлении из резервной копии: {recover_error}")
                
            except Exception as e:
                message = f"Ошибка при обработке файла {file_path}: {e}"
                logger.error(message)
                results[file_path] = False
                
                if raise_error:
                    raise
        
        return results