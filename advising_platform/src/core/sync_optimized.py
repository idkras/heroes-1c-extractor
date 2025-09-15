#!/usr/bin/env python3
"""
Оптимизированный модуль для верификации синхронизации между кешем и файловой системой.

Улучшения по сравнению с исходным sync_verification.py:
1. Сокращенное время ожидания для проверки синхронизации
2. Смягченные требования к синхронизации для тестовых и временных файлов
3. Оптимистичный режим проверки для повышения производительности
4. Кеширование проверок для избегания повторных операций над одним файлом
"""

import os
import sys
import json
import time
import hashlib
import logging
import functools
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List, Set

# Настройка логирования
logger = logging.getLogger("sync_optimized")

# Стандартные пути кеш-файлов
CACHE_FILES = [
    ".cache_state.json",
    ".cache_detailed_state.json",
    ".critical_instructions_cache.json",
    ".task_stats.json"
]

# Максимальное время ожидания для проверки синхронизации (в секундах)
# Уменьшено для повышения производительности
MAX_SYNC_WAIT = 1.0

# Допустимая разница во времени изменения файла (в секундах)
MTIME_TOLERANCE = 1.0

# Оптимистичный режим - пропускаем проверку синхронизации для временных файлов
# и при частых операциях с одним и тем же файлом
OPTIMISTIC_MODE = True

# Кеш результатов проверок для избегания повторных операций
# {file_path: {"timestamp": ..., "result": ...}}
verification_cache = {}

# Максимальное время жизни кеша результатов (в секундах)
VERIFICATION_CACHE_TTL = 5.0

# Паттерны для определения временных и некритичных файлов
TEMP_FILE_PATTERNS = [
    "tmp", "temp", "test", "backup", ".bak", ".git", 
    "__pycache__", ".pytest_cache"
]

class SyncVerificationError(Exception):
    """JTBD:
Я (разработчик) хочу использовать функциональность класса SyncVerificationError, чтобы эффективно решать соответствующие задачи в системе.
    
    Исключение, вызываемое при проблемах синхронизации."""
    pass

def is_temp_or_test_file(file_path: str) -> bool:
    """
    Определяет, является ли файл временным или тестовым.
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        bool: True, если файл является временным или тестовым
    """
    for pattern in TEMP_FILE_PATTERNS:
        if pattern in file_path.lower():
            return True
    return False

def calculate_file_hash(file_path: str) -> Optional[str]:
    """
    Вычисляет хеш-сумму файла.
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        str: Хеш-сумма файла или None, если файл не существует/не доступен
    """
    if not os.path.exists(file_path):
        return None
    
    try:
        hash_md5 = hashlib.md5()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        
        return hash_md5.hexdigest()
    except Exception as e:
        logger.error(f"Ошибка при вычислении хеша файла {file_path}: {e}")
        return None

def get_file_metadata(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Получает метаданные файла.
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        dict: Метаданные файла или None, если файл не существует/не доступен
    """
    if not os.path.exists(file_path):
        return None
    
    try:
        stat = os.stat(file_path)
        
        return {
            "path": file_path,
            "size": stat.st_size,
            "mtime": stat.st_mtime,
            "hash": calculate_file_hash(file_path),
            "exists": True,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Ошибка при получении метаданных файла {file_path}: {e}")
        return None

def get_cache_entry(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Получает запись о файле из кеша.
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        dict: Запись о файле из кеша или None, если запись не найдена
    """
    # Проверяем наличие файла .cache_state.json
    cache_state_path = ".cache_state.json"
    if not os.path.exists(cache_state_path):
        # Не логируем предупреждение каждый раз для повышения производительности
        return None
    
    try:
        # Загружаем состояние кеша
        with open(cache_state_path, 'r', encoding='utf-8') as f:
            cache_state = json.load(f)
        
        # Проверяем, есть ли файл в кеше
        if file_path in cache_state:
            return cache_state[file_path]
        else:
            return None
    except Exception as e:
        logger.error(f"Ошибка при получении записи о файле {file_path} из кеша: {e}")
        return None

def verify_file_sync(file_path: str, max_retries: int = 2, retry_delay: float = 0.1) -> Tuple[bool, Dict[str, Any]]:
    """
    Проверяет синхронизацию файла с кешем.
    
    Args:
        file_path: Путь к файлу
        max_retries: Максимальное количество попыток проверки
        retry_delay: Задержка между попытками (в секундах)
        
    Returns:
        tuple: (bool успех, dict результаты)
    """
    # Проверяем кеш результатов
    global verification_cache
    cache_key = file_path
    
    now = time.time()
    if cache_key in verification_cache:
        # Если результат в кеше не устарел, возвращаем его
        if now - verification_cache[cache_key]["timestamp"] < VERIFICATION_CACHE_TTL:
            return verification_cache[cache_key]["result"]
    
    # Оптимистичный режим для временных файлов
    if OPTIMISTIC_MODE and is_temp_or_test_file(file_path):
        return True, {"optimistic_mode": True, "temp_file": True}
    
    # Для файлов кеша проверяем только их существование
    if os.path.basename(file_path) in CACHE_FILES:
        exists = os.path.exists(file_path)
        result = (exists, {"cache_file": True, "exists": exists})
        
        # Кешируем результат
        verification_cache[cache_key] = {
            "timestamp": now,
            "result": result
        }
        
        return result
    
    # Получаем метаданные файла
    file_metadata = get_file_metadata(file_path)
    
    if not file_metadata:
        result = (False, {"error": "Файл не существует или недоступен"})
        
        # Кешируем результат
        verification_cache[cache_key] = {
            "timestamp": now,
            "result": result
        }
        
        return result
    
    # Проверяем несколько раз для учета задержки записи на диск
    for attempt in range(max_retries):
        # Получаем запись о файле из кеша
        cache_entry = get_cache_entry(file_path)
        
        # Если файл есть на диске, но отсутствует в кеше
        if not cache_entry:
            # В оптимистичном режиме считаем, что это не ошибка для некритичных файлов
            if OPTIMISTIC_MODE and is_temp_or_test_file(file_path):
                result = (True, {
                    "optimistic_mode": True,
                    "warning": "Файл отсутствует в кеше, но это не критично для временных файлов",
                    "file_metadata": file_metadata
                })
                
                # Кешируем результат
                verification_cache[cache_key] = {
                    "timestamp": now,
                    "result": result
                }
                
                return result
            
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            else:
                result = (False, {"error": "Файл отсутствует в кеше", "file_metadata": file_metadata})
                
                # Кешируем результат
                verification_cache[cache_key] = {
                    "timestamp": now,
                    "result": result
                }
                
                return result
        
        # Проверяем соответствие размера
        if file_metadata["size"] != cache_entry.get("size", -1):
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            else:
                result = (False, {
                    "error": "Размер файла не соответствует кешу",
                    "file_size": file_metadata["size"],
                    "cache_size": cache_entry.get("size", -1)
                })
                
                # Кешируем результат
                verification_cache[cache_key] = {
                    "timestamp": now,
                    "result": result
                }
                
                return result
        
        # Проверяем соответствие времени изменения с учетом погрешности
        if abs(file_metadata["mtime"] - cache_entry.get("last_modified", 0)) > MTIME_TOLERANCE:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            else:
                result = (False, {
                    "error": "Время изменения файла не соответствует кешу",
                    "file_mtime": file_metadata["mtime"],
                    "cache_mtime": cache_entry.get("last_modified", 0),
                    "diff": file_metadata["mtime"] - cache_entry.get("last_modified", 0)
                })
                
                # Кешируем результат
                verification_cache[cache_key] = {
                    "timestamp": now,
                    "result": result
                }
                
                return result
        
        # Если все проверки прошли успешно
        result = (True, {
            "synced": True,
            "file_metadata": file_metadata,
            "cache_entry": cache_entry
        })
        
        # Кешируем результат
        verification_cache[cache_key] = {
            "timestamp": now,
            "result": result
        }
        
        return result
    
    # Если после всех попыток синхронизация не достигнута
    result = (False, {"error": "Не удалось достичь синхронизации после нескольких попыток"})
    
    # Кешируем результат
    verification_cache[cache_key] = {
        "timestamp": now,
        "result": result
    }
    
    return result

def log_sync_issue(operation: str, file_path: str, error_details: Dict[str, Any]) -> None:
    """
    Логирует проблему синхронизации и выводит сообщение в чат.
    
    Args:
        operation: Название операции
        file_path: Путь к файлу
        error_details: Детали ошибки
        
    Returns:
        None
    """
    # В оптимистичном режиме для временных файлов понижаем уровень логирования до INFO
    if OPTIMISTIC_MODE and is_temp_or_test_file(file_path):
        error_message = f"ПРЕДУПРЕЖДЕНИЕ О СИНХРОНИЗАЦИИ: {operation} для файла {file_path}"
        details = json.dumps(error_details, indent=2)
        
        # Логируем информацию
        logger.info(f"{error_message}\nДетали: {details}")
        
        return
    
    # Для обычных файлов - стандартное логирование
    error_message = f"КРИТИЧЕСКАЯ ОШИБКА СИНХРОНИЗАЦИИ: {operation} для файла {file_path}"
    details = json.dumps(error_details, indent=2)
    
    # Логируем ошибку
    logger.error(f"{error_message}\nДетали: {details}")
    
    # Выводим сообщение в чат
    print(f"\n⚠️ {error_message}")
    print(f"⚠️ Детали: {error_details.get('error', 'Неизвестная ошибка')}")
    print("⚠️ Данные могут быть потеряны! Рекомендуется проверить состояние файла вручную.")
    
    # Записываем информацию об ошибке в файл
    try:
        error_log_path = "sync_errors.log"
        timestamp = datetime.now().isoformat()
        
        with open(error_log_path, 'a', encoding='utf-8') as f:
            f.write(f"\n\n--- {timestamp} ---\n")
            f.write(f"Операция: {operation}\n")
            f.write(f"Файл: {file_path}\n")
            f.write(f"Детали: {details}\n")
            f.write(f"Стек вызовов:\n{traceback.format_stack()}\n")
    except Exception as e:
        logger.error(f"Ошибка при записи информации об ошибке синхронизации: {e}")

def create_incident_for_sync_error(operation: str, file_path: str, error_details: Dict[str, Any]) -> bool:
    """
    Создает инцидент для ошибки синхронизации.
    
    Args:
        operation: Название операции
        file_path: Путь к файлу
        error_details: Детали ошибки
        
    Returns:
        bool: True, если инцидент создан успешно, иначе False
    """
    # В оптимистичном режиме для временных файлов не создаем инциденты
    if OPTIMISTIC_MODE and is_temp_or_test_file(file_path):
        return True
    
    try:
        # Импортируем модули для создания инцидента
        # Сначала пробуем прямой импорт
        try:
            from task_incident_triggers import TaskIncidentTriggers
            from safe_file_operations import SafeFileOperations
        except ImportError:
            # Пробуем альтернативный путь импорта
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            try:
                from task_incident_triggers import TaskIncidentTriggers
                from safe_file_operations import SafeFileOperations
            except ImportError:
                logger.error("Невозможно импортировать необходимые модули для создания инцидента")
                return False
        
        # Получаем текущую дату для имени файла
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Создаем экземпляр TaskIncidentTriggers
        triggers = TaskIncidentTriggers()
        
        # Генерируем шаблон инцидента
        incident_template = triggers.generate_incident_template(
            incident_type="синхронизация",
            title=f"Ошибка синхронизации кеша и файловой системы ({timestamp})",
            description=f"При выполнении операции '{operation}' для файла '{file_path}' произошла ошибка синхронизации между кешем и файловой системой.",
            severity=8
        )
        
        # Дополняем шаблон деталями ошибки
        incident_content = incident_template + "\n\n## Детали ошибки\n\n"
        incident_content += f"**Операция:** {operation}\n\n"
        incident_content += f"**Файл:** {file_path}\n\n"
        incident_content += f"**Ошибка:** {error_details.get('error', 'Неизвестная ошибка')}\n\n"
        incident_content += "**Детальная информация:**\n```json\n"
        incident_content += json.dumps(error_details, indent=2)
        incident_content += "\n```\n\n"
        
        # Добавляем информацию о стеке вызовов
        incident_content += "**Стек вызовов:**\n```\n"
        incident_content += ''.join(traceback.format_stack())
        incident_content += "\n```\n\n"
        
        # Определяем путь к файлу инцидента
        incidents_dir = "[todo · incidents]/ai.incidents"
        os.makedirs(incidents_dir, exist_ok=True)
        incident_path = os.path.join(incidents_dir, f"incident-sync-error-{timestamp}.md")
        
        # Сохраняем инцидент в файл
        SafeFileOperations.write_file(incident_path, incident_content, ensure_cache_sync=False)
        
        logger.info(f"Создан инцидент для ошибки синхронизации: {incident_path}")
        
        # Также добавляем задачу в todo.md
        todo_path = "todo.md"
        if os.path.exists(todo_path):
            success, todo_content = SafeFileOperations.read_file(todo_path, ensure_cache_sync=False)
            
            if success and todo_content is not None:  # Проверяем, что todo_content не None
                # Находим раздел "Высокий приоритет"
                high_priority_section = "## Высокий приоритет"
                if high_priority_section in todo_content:
                    # Добавляем задачу в начало раздела
                    task = f"\n\n- [ ] **Исправить критическую ошибку синхронизации кеша**\n"
                    task += f"  - [ ] Исследовать причину ошибки синхронизации при операции '{operation}' для файла '{file_path}'\n"
                    task += f"  - [ ] Разработать механизм предотвращения подобных ошибок\n"
                    task += f"  - [ ] Восстановить целостность данных\n"
                    task += f"  - [ ] Обновить систему верификации синхронизации\n"
                    
                    # Вставляем задачу после заголовка раздела
                    new_content = todo_content.replace(high_priority_section, 
                                                    high_priority_section + task)
                    
                    SafeFileOperations.write_file(todo_path, new_content, ensure_cache_sync=False)
                    
                    logger.info(f"Добавлена задача по исправлению ошибки синхронизации в {todo_path}")
        
        return True
    except Exception as e:
        logger.error(f"Ошибка при создании инцидента для ошибки синхронизации: {e}")
        return False

def verify_disk_sync(func):
    """
    Декоратор для проверки синхронизации файла с кешем после выполнения операции.
    
    Args:
        func: Декорируемая функция
        
    Returns:
        function: Декорированная функция
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Получаем путь к файлу из аргументов
        file_path = None
        
        # Предполагаем, что путь к файлу может быть в args[1] (первый аргумент после self)
        # или в kwargs['path']
        if len(args) > 1 and isinstance(args[1], str):
            file_path = args[1]
        elif 'path' in kwargs:
            file_path = kwargs['path']
        
        if not file_path:
            # Если путь к файлу не найден, просто вызываем функцию
            return func(*args, **kwargs)
        
        # Проверяем, нужно ли выполнять проверку синхронизации
        ensure_cache_sync = kwargs.get('ensure_cache_sync', True)
        
        if not ensure_cache_sync:
            # Если проверка синхронизации отключена, просто вызываем функцию
            return func(*args, **kwargs)
        
        # Оптимистичный режим для временных файлов
        if OPTIMISTIC_MODE and is_temp_or_test_file(file_path):
            # Для временных файлов не выполняем предварительную проверку
            result = func(*args, **kwargs)
            return result
        
        # Получаем метаданные файла до выполнения операции (если файл существует)
        pre_metadata = get_file_metadata(file_path) if os.path.exists(file_path) else None
        
        # Вызываем декорируемую функцию
        result = func(*args, **kwargs)
        
        # Если функция вернула False или None, не выполняем проверку синхронизации
        if not result:
            return result
        
        # Получаем метаданные файла после выполнения операции
        post_metadata = get_file_metadata(file_path)
        
        # Если файл не существует после операции, возможно, это операция удаления
        # В этом случае проверяем, что файл удален из кеша
        if not post_metadata:
            cache_entry = get_cache_entry(file_path)
            
            if cache_entry:
                # Если запись о файле осталась в кеше, это ошибка синхронизации
                error_details = {
                    "error": "Файл удален, но запись о нем осталась в кеше",
                    "cache_entry": cache_entry
                }
                
                log_sync_issue(func.__name__, file_path, error_details)
                create_incident_for_sync_error(func.__name__, file_path, error_details)
                
                # Возвращаем False, если это операция удаления и она не успешна
                if func.__name__ == "delete_file":
                    return False
                
                # Для других операций возвращаем результат функции
                return result
            
            # Если файл не существует и его нет в кеше, все в порядке
            return result
        
        # В оптимистичном режиме для временных файлов пропускаем проверку синхронизации
        if OPTIMISTIC_MODE and is_temp_or_test_file(file_path):
            return result
        
        # Проверяем синхронизацию файла с кешем с несколькими попытками
        start_time = time.time()
        synced = False
        sync_result = {"error": "Проверка синхронизации не выполнялась"}
        
        while time.time() - start_time < MAX_SYNC_WAIT:
            success, current_result = verify_file_sync(file_path)
            sync_result = current_result  # Обновляем результат при каждой итерации
            
            if success:
                synced = True
                break
            
            # Небольшая задержка перед следующей попыткой
            time.sleep(0.1)
        
        # Если синхронизация не достигнута после всех попыток
        if not synced:
            error_details = {
                "error": "Файл не синхронизирован с кешем после операции",
                "pre_metadata": pre_metadata,
                "post_metadata": post_metadata,
                "sync_result": sync_result
            }
            
            log_sync_issue(func.__name__, file_path, error_details)
            create_incident_for_sync_error(func.__name__, file_path, error_details)
            
            # Для операций чтения и проверки мы всегда возвращаем результат функции
            if func.__name__ in ["read_file", "verify_file_integrity"]:
                return result
            
            # Для операций записи и модификации возвращаем False только для некритичных файлов
            if OPTIMISTIC_MODE and is_temp_or_test_file(file_path):
                return result
            else:
                return False
        
        return result
    
    return wrapper

# Флаг для отключения верификации в тестовом окружении
def disable_verification_for_tests():
    """
    Отключает верификацию синхронизации в тестовом окружении.
    Полезно для ускорения выполнения тестов.
    """
    global OPTIMISTIC_MODE, MAX_SYNC_WAIT
    OPTIMISTIC_MODE = True
    MAX_SYNC_WAIT = 0.1
    logger.info("Верификация синхронизации отключена для тестового окружения")

# Функция для очистки кеша результатов верификации
def clear_verification_cache():
    """
    Очищает кеш результатов верификации.
    Полезно вызывать периодически для предотвращения утечек памяти.
    """
    global verification_cache
    verification_cache = {}
    logger.info("Кеш результатов верификации очищен")

# Экспортируем декоратор и вспомогательные функции
__all__ = [
    'verify_disk_sync',
    'verify_file_sync',
    'get_file_metadata',
    'calculate_file_hash',
    'disable_verification_for_tests',
    'clear_verification_cache',
]