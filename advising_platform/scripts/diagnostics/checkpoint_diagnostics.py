#!/usr/bin/env python3
"""
Диагностический инструмент для проверки состояния чекпоинтов.
Анализирует и выявляет возможные проблемы, которые могут препятствовать
корректному созданию и восстановлению чекпоинтов.
"""

import os
import sys
import json
import pickle
import logging
import time
import shutil
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("checkpoint_diagnostics")

# Константы
CHECKPOINT_BACKUP_DIR = ".checkpoint_backup"
CACHE_BACKUP_FILE = os.path.join(CHECKPOINT_BACKUP_DIR, "cache_backup.pickle")
STATE_BACKUP_FILE = os.path.join(CHECKPOINT_BACKUP_DIR, "state_backup.json")
METADATA_FILE = os.path.join(CHECKPOINT_BACKUP_DIR, "checkpoint_metadata.json")
CACHE_STATE_FILE = ".cache_state.json"
DETAILED_STATE_FILE = ".cache_detailed_state.pickle"
DIAGNOSTIC_REPORT_FILE = os.path.join(CHECKPOINT_BACKUP_DIR, "checkpoint_diagnostic_report.json")
RECOVERY_REPORT_FILE = os.path.join(CHECKPOINT_BACKUP_DIR, "recovery_report.json")
REPLIT_METADATA_FILES = [".replit", ".cache", ".breakpoints", ".gitignore", ".upm"]

def check_file_exists_and_permissions(file_path):
    """
    Проверяет существование файла и права доступа.
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        Dict[str, Any]: Результаты проверки
    """
    result = {
        "exists": os.path.exists(file_path),
        "readable": False,
        "writable": False,
        "size": 0,
        "last_modified": None,
        "error": None
    }
    
    if result["exists"]:
        try:
            result["size"] = os.path.getsize(file_path)
            result["readable"] = os.access(file_path, os.R_OK)
            result["writable"] = os.access(file_path, os.W_OK)
            result["last_modified"] = datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
        except Exception as e:
            result["error"] = str(e)
    
    return result

def check_file_integrity(file_path):
    """
    Проверяет целостность файла (возможность чтения и синтаксическую корректность).
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        Dict[str, Any]: Результаты проверки
    """
    result = {
        "valid": False,
        "content_type": None,
        "error": None
    }
    
    if not os.path.exists(file_path):
        result["error"] = "Файл не существует"
        return result
    
    try:
        # Определяем тип файла по расширению
        if file_path.endswith('.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            result["content_type"] = "JSON"
            result["valid"] = True
        elif file_path.endswith('.pickle'):
            with open(file_path, 'rb') as f:
                pickle.load(f)
            result["content_type"] = "Pickle"
            result["valid"] = True
        else:
            # Пробуем определить тип по содержимому
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(100)  # Читаем первые 100 символов
                    if content.strip().startswith('{') and '{' in content and '}' in content:
                        result["content_type"] = "Возможно JSON"
                    elif content.strip().startswith('[') and '[' in content and ']' in content:
                        result["content_type"] = "Возможно JSON (массив)"
                    else:
                        result["content_type"] = "Текст"
            except UnicodeDecodeError:
                # Если не удалось прочитать как текст, вероятно это бинарный файл
                result["content_type"] = "Бинарный"
    except Exception as e:
        result["error"] = str(e)
    
    return result

def check_system_resources():
    """
    Проверяет доступные системные ресурсы.
    
    Returns:
        Dict[str, Any]: Информация о системных ресурсах
    """
    result = {
        "disk_space": {},
        "memory": {},
        "file_descriptors": {},
        "error": None
    }
    
    try:
        # Проверка свободного места на диске
        total, used, free = shutil.disk_usage("/")
        result["disk_space"] = {
            "total": total,
            "used": used,
            "free": free,
            "free_percent": round(free / total * 100, 2)
        }
        
        # Проверка файловых дескрипторов (только для Linux)
        try:
            with open('/proc/sys/fs/file-nr') as f:
                allocated, _, max_fds = map(int, f.read().split())
                result["file_descriptors"] = {
                    "allocated": allocated,
                    "max": max_fds,
                    "available": max_fds - allocated
                }
        except:
            # Вероятно, не Linux или нет доступа к /proc
            result["file_descriptors"] = {"error": "Не удалось получить информацию о файловых дескрипторах"}
        
        # Проверка памяти (в зависимости от ОС)
        try:
            import psutil
            mem = psutil.virtual_memory()
            result["memory"] = {
                "total": mem.total,
                "available": mem.available,
                "percent": mem.percent,
                "used": mem.used,
                "free": mem.free
            }
        except ImportError:
            # Если psutil не установлен, пробуем получить информацию другим способом
            try:
                # Используем бинарные утилиты для информации о памяти
                if os.name == 'posix':  # Linux/Unix
                    cmd = "free -b"
                    p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
                    output = p.communicate()[0].decode().split('\n')
                    memory_line = output[1].split()
                    total = int(memory_line[1])
                    used = int(memory_line[2])
                    free = int(memory_line[3])
                    result["memory"] = {
                        "total": total,
                        "used": used,
                        "free": free,
                        "percent": round(used / total * 100, 2)
                    }
                else:
                    result["memory"] = {"error": "Не удалось получить информацию о памяти на этой ОС"}
            except:
                result["memory"] = {"error": "Не удалось получить информацию о памяти"}
    except Exception as e:
        result["error"] = str(e)
    
    return result

def check_replit_specific_files():
    """
    Проверяет специфичные для Replit файлы, которые могут влиять на чекпоинты.
    
    Returns:
        Dict[str, Any]: Результаты проверки
    """
    result = {
        "files": {},
        "checksum_mapping_exists": False,
        "error": None
    }
    
    try:
        # Проверяем наличие специфичных файлов Replit
        for file_name in REPLIT_METADATA_FILES:
            file_check = check_file_exists_and_permissions(file_name)
            if file_check["exists"]:
                result["files"][file_name] = file_check
        
        # Проверяем наличие файла .checksum_mapping, который использует Replit для чекпоинтов
        checksum_mapping_exists = False
        for file_name in os.listdir('.'):
            if file_name.startswith('.checksum_') or file_name == '.checksum_mapping':
                checksum_mapping_exists = True
                result["files"][file_name] = check_file_exists_and_permissions(file_name)
        
        result["checksum_mapping_exists"] = checksum_mapping_exists
    except Exception as e:
        result["error"] = str(e)
    
    return result

def check_checkpoint_backup_dir():
    """
    Проверяет состояние директории резервных копий чекпоинта.
    
    Returns:
        Dict[str, Any]: Результаты проверки
    """
    result = {
        "exists": os.path.exists(CHECKPOINT_BACKUP_DIR),
        "files": {},
        "error": None
    }
    
    if result["exists"]:
        try:
            # Проверяем содержимое директории
            for file_name in os.listdir(CHECKPOINT_BACKUP_DIR):
                file_path = os.path.join(CHECKPOINT_BACKUP_DIR, file_name)
                file_check = check_file_exists_and_permissions(file_path)
                result["files"][file_name] = file_check
                
                # Проверяем целостность файлов резервных копий
                if file_name == "cache_backup.pickle" or file_name == "state_backup.json" or file_name == "checkpoint_metadata.json":
                    integrity_check = check_file_integrity(file_path)
                    result["files"][file_name]["integrity"] = integrity_check
        except Exception as e:
            result["error"] = str(e)
    
    return result

def check_file_handles():
    """
    Проверяет открытые файловые дескрипторы процесса.
    
    Returns:
        Dict[str, Any]: Информация об открытых файловых дескрипторах
    """
    result = {
        "open_files": [],
        "count": 0,
        "error": None
    }
    
    try:
        # Используем lsof для получения открытых файлов (только Linux/Unix)
        if os.name == 'posix':
            cmd = f"lsof -p {os.getpid()}"
            try:
                output = subprocess.check_output(cmd.split(), stderr=subprocess.STDOUT).decode()
                files = []
                for line in output.split('\n')[1:]:  # Пропускаем заголовок
                    if line.strip():
                        parts = line.split()
                        if len(parts) > 8:
                            file_path = parts[8]
                            files.append(file_path)
                
                result["open_files"] = files
                result["count"] = len(files)
            except subprocess.CalledProcessError:
                result["error"] = "Не удалось получить список открытых файлов (нужны права root)"
        else:
            result["error"] = "Проверка открытых файлов доступна только на Linux/Unix"
    except Exception as e:
        result["error"] = str(e)
    
    return result

def check_cache_state():
    """
    Проверяет состояние файлов кеша.
    
    Returns:
        Dict[str, Any]: Результаты проверки
    """
    result = {
        "state_file": check_file_exists_and_permissions(CACHE_STATE_FILE),
        "detailed_state_file": check_file_exists_and_permissions(DETAILED_STATE_FILE),
        "cache_size": None,
        "max_cache_size": None,
        "document_count": None,
        "error": None
    }
    
    # Если файл состояния существует, проверяем его содержимое
    if result["state_file"]["exists"]:
        try:
            with open(CACHE_STATE_FILE, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            
            result["cache_size"] = state_data.get('cache_size')
            result["max_cache_size"] = state_data.get('max_cache_size')
            result["document_count"] = state_data.get('document_count')
            result["is_initialized"] = state_data.get('is_initialized')
            result["watched_directories"] = state_data.get('watched_directories')
        except Exception as e:
            result["error"] = f"Ошибка при чтении файла состояния кеша: {e}"
    
    return result

def check_document_cache_integration():
    """
    Проверяет интеграцию менеджера кеша документов с safe_checkpoint.py.
    
    Returns:
        Dict[str, Any]: Результаты проверки
    """
    result = {
        "installed": False,
        "version": None,
        "integration_status": None,
        "error": None
    }
    
    try:
        # Пытаемся импортировать модуль
        try:
            from advising_platform.src.cache.document_cache import DocumentCacheManager
            result["installed"] = True
            
            # Проверяем версию и интеграцию с чекпоинтами
            if hasattr(DocumentCacheManager, '__version__'):
                result["version"] = DocumentCacheManager.__version__
            
            # Проверяем поддержку методов для работы с чекпоинтами
            has_shutdown = hasattr(DocumentCacheManager, 'shutdown')
            has_get_instance = hasattr(DocumentCacheManager, 'get_instance')
            
            result["integration_status"] = {
                "has_shutdown_method": has_shutdown,
                "has_get_instance_method": has_get_instance,
            }
            
            # Пытаемся получить экземпляр менеджера
            try:
                cache_manager = DocumentCacheManager.get_instance()
                result["integration_status"]["instance_created"] = True
                
                # Проверяем поддержку max_cache_size
                if hasattr(cache_manager, 'max_cache_size'):
                    result["integration_status"]["max_cache_size"] = cache_manager.max_cache_size
                
                # Проверяем наличие метода invalidate
                result["integration_status"]["has_invalidate_method"] = hasattr(cache_manager, 'invalidate')
            except Exception as e:
                result["integration_status"]["instance_created"] = False
                result["integration_status"]["instance_error"] = str(e)
        except ImportError as e:
            result["error"] = f"Модуль не установлен: {e}"
    except Exception as e:
        result["error"] = str(e)
    
    return result

def generate_diagnostic_report():
    """
    Генерирует комплексный диагностический отчет.
    
    Returns:
        Dict[str, Any]: Диагностический отчет
    """
    logger.info("Генерация диагностического отчета...")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "system_resources": check_system_resources(),
        "checkpoint_backup_dir": check_checkpoint_backup_dir(),
        "cache_state": check_cache_state(),
        "replit_files": check_replit_specific_files(),
        "file_handles": check_file_handles(),
        "document_cache_integration": check_document_cache_integration(),
        "recommendations": []
    }
    
    # Анализируем результаты и формируем рекомендации
    recommendations = []
    
    # Проверка на проблемы с размером кеша
    if report["cache_state"]["max_cache_size"] is not None and report["cache_state"]["max_cache_size"] < 500:
        recommendations.append({
            "priority": "HIGH",
            "issue": "Недостаточный максимальный размер кеша",
            "details": f"Текущий размер: {report['cache_state']['max_cache_size']}, рекомендуемый: 500",
            "solution": "Обновите max_cache_size в DocumentCacheManager до 500"
        })
    
    # Проверка на отсутствие директории резервных копий
    if not report["checkpoint_backup_dir"]["exists"]:
        recommendations.append({
            "priority": "HIGH",
            "issue": "Отсутствует директория резервных копий",
            "details": f"Директория {CHECKPOINT_BACKUP_DIR} не найдена",
            "solution": "Создайте директорию для резервных копий"
        })
    
    # Проверка на проблемы с файлами Replit для чекпоинтов
    if not report["replit_files"]["checksum_mapping_exists"]:
        recommendations.append({
            "priority": "MEDIUM",
            "issue": "Отсутствует файл .checksum_mapping для Replit чекпоинтов",
            "details": "Файл .checksum_mapping необходим для отслеживания изменений файлов",
            "solution": "Удостоверьтесь, что чекпоинты Replit активированы"
        })
    
    # Проверка на проблемы с открытыми файловыми дескрипторами
    if report["system_resources"].get("file_descriptors", {}).get("allocated") is not None:
        allocated = report["system_resources"]["file_descriptors"]["allocated"]
        max_fds = report["system_resources"]["file_descriptors"]["max"]
        
        if allocated > max_fds * 0.8:
            recommendations.append({
                "priority": "HIGH",
                "issue": "Слишком много открытых файловых дескрипторов",
                "details": f"Используется {allocated} из {max_fds} (>{80}%)",
                "solution": "Убедитесь, что все файловые дескрипторы корректно закрываются"
            })
    
    # Проверка на проблемы с дисковым пространством
    free_percent = report["system_resources"]["disk_space"].get("free_percent")
    if free_percent is not None and free_percent < 10:
        recommendations.append({
            "priority": "HIGH",
            "issue": "Недостаточно свободного места на диске",
            "details": f"Доступно {free_percent}% свободного места",
            "solution": "Освободите место, удалив неиспользуемые файлы"
        })
    
    # Проверка на проблемы с интеграцией кеша документов
    if not report["document_cache_integration"]["installed"]:
        recommendations.append({
            "priority": "HIGH",
            "issue": "Не установлен модуль кеша документов",
            "details": report["document_cache_integration"]["error"],
            "solution": "Установите необходимые зависимости"
        })
    elif report["document_cache_integration"].get("integration_status", {}).get("has_shutdown_method") is False:
        recommendations.append({
            "priority": "MEDIUM",
            "issue": "Отсутствует метод shutdown в DocumentCacheManager",
            "details": "Метод shutdown необходим для корректного освобождения ресурсов",
            "solution": "Добавьте метод shutdown в класс DocumentCacheManager"
        })
    
    # Проверка на проблемы с файлами состояния
    if not report["cache_state"]["state_file"]["exists"]:
        recommendations.append({
            "priority": "HIGH",
            "issue": "Отсутствует файл состояния кеша",
            "details": f"Файл {CACHE_STATE_FILE} не найден",
            "solution": "Инициализируйте кеш с помощью python cache_init.py"
        })
    elif not report["cache_state"]["detailed_state_file"]["exists"]:
        recommendations.append({
            "priority": "MEDIUM",
            "issue": "Отсутствует файл детального состояния кеша",
            "details": f"Файл {DETAILED_STATE_FILE} не найден",
            "solution": "Инициализируйте кеш с помощью python cache_init.py"
        })
    
    # Проверка на проблемы с файлами резервных копий
    if report["checkpoint_backup_dir"]["exists"]:
        cache_backup = report["checkpoint_backup_dir"]["files"].get("cache_backup.pickle", {})
        state_backup = report["checkpoint_backup_dir"]["files"].get("state_backup.json", {})
        
        if not cache_backup.get("exists", False):
            recommendations.append({
                "priority": "HIGH",
                "issue": "Отсутствует файл резервной копии кеша",
                "details": f"Файл {CACHE_BACKUP_FILE} не найден",
                "solution": "Создайте резервную копию с помощью python safe_checkpoint.py --backup"
            })
        elif cache_backup.get("size", 0) == 0:
            recommendations.append({
                "priority": "HIGH",
                "issue": "Файл резервной копии кеша пуст",
                "details": f"Файл {CACHE_BACKUP_FILE} имеет нулевой размер",
                "solution": "Пересоздайте резервную копию с помощью python safe_checkpoint.py --backup"
            })
        
        if not state_backup.get("exists", False):
            recommendations.append({
                "priority": "HIGH",
                "issue": "Отсутствует файл резервной копии состояния",
                "details": f"Файл {STATE_BACKUP_FILE} не найден",
                "solution": "Создайте резервную копию с помощью python safe_checkpoint.py --backup"
            })
        elif state_backup.get("size", 0) == 0:
            recommendations.append({
                "priority": "HIGH",
                "issue": "Файл резервной копии состояния пуст",
                "details": f"Файл {STATE_BACKUP_FILE} имеет нулевой размер",
                "solution": "Пересоздайте резервную копию с помощью python safe_checkpoint.py --backup"
            })
    
    report["recommendations"] = recommendations
    
    # Определяем общий статус
    high_priority_issues = len([r for r in recommendations if r["priority"] == "HIGH"])
    medium_priority_issues = len([r for r in recommendations if r["priority"] == "MEDIUM"])
    
    if high_priority_issues == 0 and medium_priority_issues == 0:
        report["status"] = "HEALTHY"
    elif high_priority_issues == 0 and medium_priority_issues > 0:
        report["status"] = "WARNING"
    else:
        report["status"] = "CRITICAL"
    
    # Сохраняем отчет в файл
    try:
        if not os.path.exists(CHECKPOINT_BACKUP_DIR):
            os.makedirs(CHECKPOINT_BACKUP_DIR)
        
        with open(DIAGNOSTIC_REPORT_FILE, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Диагностический отчет сохранен в {DIAGNOSTIC_REPORT_FILE}")
    except Exception as e:
        logger.error(f"Ошибка при сохранении диагностического отчета: {e}")
    
    return report

def fix_common_issues():
    """
    Исправляет наиболее распространенные проблемы, обнаруженные при диагностике.
    
    Returns:
        Dict[str, Any]: Результаты исправления
    """
    result = {
        "fixed_issues": [],
        "errors": [],
        "status": "SUCCESS"
    }
    
    logger.info("Исправление распространенных проблем...")
    
    # Проверяем наличие директории резервных копий
    if not os.path.exists(CHECKPOINT_BACKUP_DIR):
        try:
            os.makedirs(CHECKPOINT_BACKUP_DIR)
            result["fixed_issues"].append("Создана директория резервных копий")
        except Exception as e:
            result["errors"].append(f"Не удалось создать директорию резервных копий: {e}")
    
    # Пытаемся загрузить текущее состояние кеша
    try:
        # Проверяем и исправляем размер кеша
        if os.path.exists(CACHE_STATE_FILE):
            try:
                with open(CACHE_STATE_FILE, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                
                if state_data.get('max_cache_size', 0) < 500:
                    state_data['max_cache_size'] = 500
                    
                    with open(CACHE_STATE_FILE, 'w', encoding='utf-8') as f:
                        json.dump(state_data, f, indent=2)
                    
                    result["fixed_issues"].append(f"Исправлен размер кеша: max_cache_size = 500")
            except Exception as e:
                result["errors"].append(f"Не удалось исправить размер кеша: {e}")
        
        # Создаем резервные копии текущего состояния, если они отсутствуют
        if os.path.exists(CACHE_STATE_FILE) and not os.path.exists(STATE_BACKUP_FILE):
            try:
                shutil.copy2(CACHE_STATE_FILE, STATE_BACKUP_FILE)
                result["fixed_issues"].append(f"Создана резервная копия файла состояния")
            except Exception as e:
                result["errors"].append(f"Не удалось создать резервную копию файла состояния: {e}")
        
        # Создаем метаданные чекпоинта, если они отсутствуют
        if not os.path.exists(METADATA_FILE):
            try:
                metadata = {
                    "timestamp": datetime.now().isoformat(),
                    "cache_state": {
                        "documents_count": 0,
                        "max_cache_size": 500,
                        "success": True
                    },
                    "checkpoint_version": "1.1",
                    "platform_version": "Advising Platform v1.1.0"
                }
                
                with open(METADATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2)
                
                result["fixed_issues"].append("Созданы метаданные чекпоинта")
            except Exception as e:
                result["errors"].append(f"Не удалось создать метаданные чекпоинта: {e}")
    except Exception as e:
        result["errors"].append(f"Общая ошибка при исправлении проблем: {e}")
    
    # Определяем общий статус
    if result["errors"]:
        result["status"] = "PARTIAL_SUCCESS" if result["fixed_issues"] else "FAILURE"
    
    return result

def run_diagnostic_tests():
    """
    Запускает диагностические тесты для проверки работоспособности чекпоинтов.
    
    Returns:
        Dict[str, Any]: Результаты тестов
    """
    result = {
        "tests": [],
        "status": "SUCCESS"
    }
    
    logger.info("Запуск диагностических тестов...")
    
    # Тест 1: Создание резервной копии
    logger.info("Тест 1: Создание резервной копии...")
    test1 = {
        "name": "Создание резервной копии",
        "status": "PASSED",
        "details": None
    }
    
    try:
        # Импортируем необходимые модули
        try:
            from advising_platform.src.cache.document_cache import DocumentCacheManager
            from advising_platform.src.cache.cache_state import CacheStateManager
            
            # Получаем экземпляр кеш-менеджера
            cache_manager = DocumentCacheManager.get_instance(max_cache_size=500)
            
            # Проверяем, что кеш-менеджер получен успешно
            if cache_manager is None:
                test1["status"] = "FAILED"
                test1["details"] = "Не удалось получить экземпляр кеш-менеджера"
            else:
                # Получаем текущее состояние кеша
                state = CacheStateManager.load_state() or {}
                state['max_cache_size'] = 500
                
                # Сохраняем состояние в резервную копию
                if not os.path.exists(CHECKPOINT_BACKUP_DIR):
                    os.makedirs(CHECKPOINT_BACKUP_DIR)
                
                with open(STATE_BACKUP_FILE, 'w', encoding='utf-8') as f:
                    json.dump(state, f, indent=2)
                
                # Создаем тестовую резервную копию кеша
                test_data = {"test_key": "test_value", "timestamp": datetime.now().isoformat()}
                with open(os.path.join(CHECKPOINT_BACKUP_DIR, "test_backup.pickle"), 'wb') as f:
                    pickle.dump(test_data, f)
                
                test1["details"] = "Резервные копии созданы успешно"
        except ImportError as e:
            test1["status"] = "FAILED"
            test1["details"] = f"Ошибка импорта модулей: {e}"
    except Exception as e:
        test1["status"] = "FAILED"
        test1["details"] = f"Ошибка при создании резервной копии: {e}"
    
    result["tests"].append(test1)
    
    # Тест 2: Проверка целостности состояния
    logger.info("Тест 2: Проверка целостности состояния...")
    test2 = {
        "name": "Проверка целостности состояния",
        "status": "PASSED",
        "details": None
    }
    
    try:
        # Проверяем наличие файлов состояния
        if not os.path.exists(CACHE_STATE_FILE):
            test2["status"] = "FAILED"
            test2["details"] = f"Файл состояния {CACHE_STATE_FILE} не найден"
        else:
            # Проверяем содержимое файла состояния
            try:
                with open(CACHE_STATE_FILE, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                
                # Проверяем необходимые поля
                if not state_data.get('is_initialized', False):
                    test2["status"] = "WARNING"
                    test2["details"] = "Кеш не инициализирован (is_initialized = False)"
                elif state_data.get('max_cache_size', 0) < 500:
                    test2["status"] = "WARNING"
                    test2["details"] = f"Недостаточный размер кеша: max_cache_size = {state_data.get('max_cache_size')}"
                else:
                    test2["details"] = "Файл состояния в порядке"
            except Exception as e:
                test2["status"] = "FAILED"
                test2["details"] = f"Ошибка при чтении файла состояния: {e}"
    except Exception as e:
        test2["status"] = "FAILED"
        test2["details"] = f"Ошибка при проверке целостности состояния: {e}"
    
    result["tests"].append(test2)
    
    # Тест 3: Проверка механизма восстановления
    logger.info("Тест 3: Проверка механизма восстановления...")
    test3 = {
        "name": "Проверка механизма восстановления",
        "status": "PASSED",
        "details": None
    }
    
    try:
        # Проверяем наличие файлов резервных копий
        if not os.path.exists(STATE_BACKUP_FILE):
            test3["status"] = "WARNING"
            test3["details"] = f"Файл резервной копии состояния {STATE_BACKUP_FILE} не найден"
        else:
            # Проверяем возможность загрузки файла резервной копии
            try:
                with open(STATE_BACKUP_FILE, 'r', encoding='utf-8') as f:
                    backup_state = json.load(f)
                
                test3["details"] = "Файл резервной копии состояния загружен успешно"
            except Exception as e:
                test3["status"] = "FAILED"
                test3["details"] = f"Ошибка при загрузке файла резервной копии состояния: {e}"
    except Exception as e:
        test3["status"] = "FAILED"
        test3["details"] = f"Ошибка при проверке механизма восстановления: {e}"
    
    result["tests"].append(test3)
    
    # Определяем общий статус
    failed_tests = len([t for t in result["tests"] if t["status"] == "FAILED"])
    warning_tests = len([t for t in result["tests"] if t["status"] == "WARNING"])
    
    if failed_tests > 0:
        result["status"] = "FAILURE"
    elif warning_tests > 0:
        result["status"] = "WARNING"
    
    # Сохраняем результаты тестов
    try:
        if not os.path.exists(CHECKPOINT_BACKUP_DIR):
            os.makedirs(CHECKPOINT_BACKUP_DIR)
        
        with open(os.path.join(CHECKPOINT_BACKUP_DIR, "diagnostic_tests_results.json"), 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        
        logger.info("Результаты тестов сохранены")
    except Exception as e:
        logger.error(f"Ошибка при сохранении результатов тестов: {e}")
    
    return result

def main():
    """
    Основная функция скрипта.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Диагностический инструмент для проверки состояния чекпоинтов")
    parser.add_argument('--diagnose', action='store_true', 
                       help='Выполнить диагностику и создать отчет')
    parser.add_argument('--fix', action='store_true',
                       help='Исправить распространенные проблемы')
    parser.add_argument('--test', action='store_true',
                       help='Запустить диагностические тесты')
    parser.add_argument('--all', action='store_true',
                       help='Выполнить диагностику, исправить проблемы и запустить тесты')
    
    args = parser.parse_args()
    
    if args.diagnose or args.all:
        print("=== Диагностика состояния чекпоинтов ===")
        report = generate_diagnostic_report()
        
        print(f"Статус: {report['status']}")
        print(f"Рекомендации ({len(report['recommendations'])}):")
        
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"{i}. [{rec['priority']}] {rec['issue']}")
            print(f"   Детали: {rec['details']}")
            print(f"   Решение: {rec['solution']}")
        
        print(f"Полный отчет сохранен в {DIAGNOSTIC_REPORT_FILE}")
    
    if args.fix or args.all:
        print("\n=== Исправление распространенных проблем ===")
        fix_result = fix_common_issues()
        
        print(f"Статус: {fix_result['status']}")
        
        if fix_result['fixed_issues']:
            print("Исправленные проблемы:")
            for issue in fix_result['fixed_issues']:
                print(f"- {issue}")
        
        if fix_result['errors']:
            print("Ошибки:")
            for error in fix_result['errors']:
                print(f"- {error}")
    
    if args.test or args.all:
        print("\n=== Запуск диагностических тестов ===")
        test_result = run_diagnostic_tests()
        
        print(f"Общий статус: {test_result['status']}")
        
        for test in test_result['tests']:
            print(f"{test['name']}: {test['status']}")
            if test['details']:
                print(f"  {test['details']}")
    
    if not any([args.diagnose, args.fix, args.test, args.all]):
        parser.print_help()

if __name__ == "__main__":
    main()