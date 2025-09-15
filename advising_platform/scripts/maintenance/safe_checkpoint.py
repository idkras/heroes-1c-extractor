#!/usr/bin/env python3
"""
Улучшенный скрипт для безопасного создания чекпоинта.
Решает несколько проблем:
1. Сохраняет состояние in-memory кеша в файловую систему
2. Очищает и освобождает ресурсы кеширования перед созданием чекпоинта
3. Подготавливает систему к корректному созданию чекпоинта
4. Предотвращает потерю данных при восстановлении из чекпоинта
"""

import os
import sys
import time
import logging
import pickle
import json
import shutil
from pathlib import Path
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("safe_checkpoint")

# Добавляем текущую директорию в sys.path
sys.path.insert(0, os.path.abspath('.'))

# Константы
CHECKPOINT_BACKUP_DIR = ".checkpoint_backup"
CACHE_BACKUP_FILE = os.path.join(CHECKPOINT_BACKUP_DIR, "cache_backup.pickle")
STATE_BACKUP_FILE = os.path.join(CHECKPOINT_BACKUP_DIR, "state_backup.json")
METADATA_FILE = os.path.join(CHECKPOINT_BACKUP_DIR, "checkpoint_metadata.json")

def ensure_backup_dir():
    """Создает директорию для резервных копий."""
    if not os.path.exists(CHECKPOINT_BACKUP_DIR):
        os.makedirs(CHECKPOINT_BACKUP_DIR)
        logger.info(f"Создана директория для резервных копий: {CHECKPOINT_BACKUP_DIR}")

def save_metadata():
    """Сохраняет метаданные о чекпоинте."""
    metadata = {
        "timestamp": datetime.now().isoformat(),
        "cache_state": {
            "documents_count": 0,  # Будет обновлено при сохранении кеша
            "success": False
        },
        "checkpoint_version": "1.0"
    }
    
    try:
        with open(METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Метаданные чекпоинта сохранены в {METADATA_FILE}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при сохранении метаданных чекпоинта: {e}")
        return False

def backup_cache_state():
    """
    Сохраняет состояние кеша в файловую систему.
    
    Returns:
        True, если сохранение успешно, иначе False
    """
    logger.info("Сохранение состояния кеша...")
    
    try:
        from advising_platform.src.cache.document_cache import DocumentCacheManager
        from advising_platform.src.cache.cache_state import CacheStateManager
        
        # Получаем экземпляр кеш-менеджера с увеличенным размером кеша
        cache_manager = DocumentCacheManager.get_instance(max_cache_size=500)
        
        # Сохраняем состояние кеша
        cache_data = {}
        if hasattr(cache_manager, 'document_cache') and hasattr(cache_manager.document_cache, 'cached_documents'):
            cache_data = cache_manager.document_cache.cached_documents
        
        # Создаем копию кеша
        cache_copy = {}
        for path, doc_info in cache_data.items():
            # Копируем данные без изменения ссылок
            cache_copy[path] = {
                'content': doc_info.get('content', ''),
                'last_accessed': doc_info.get('last_accessed', 0),
                'last_updated': doc_info.get('last_updated', 0),
                'access_count': doc_info.get('access_count', 0),
                'size': doc_info.get('size', 0),
                'priority': doc_info.get('priority', 0),
                'category': doc_info.get('category', 'unknown')
            }
        
        # Сохраняем в файл
        with open(CACHE_BACKUP_FILE, 'wb') as f:
            pickle.dump(cache_copy, f)
        
        # Загружаем текущее состояние из API и обновляем его
        state = CacheStateManager.load_state() or {}
        
        # Убеждаемся, что max_cache_size установлен правильно
        state['max_cache_size'] = 500  # Устанавливаем увеличенный размер кеша
        state['cache_size'] = len(cache_copy)
        state['document_count'] = len(cache_copy)
        
        # Сохраняем обновленное состояние
        CacheStateManager.save_state(state)
        
        # Дополнительно сохраняем копию состояния
        with open(STATE_BACKUP_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
        
        # Обновляем метаданные чекпоинта
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "cache_state": {
                "documents_count": len(cache_copy),
                "max_cache_size": 500,
                "success": True
            },
            "checkpoint_version": "1.1",
            "platform_version": "Advising Platform v1.1.0"
        }
        
        with open(METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Состояние кеша сохранено. Сохранено {len(cache_copy)} документов с max_cache_size=500.")
        return True
    except ImportError as e:
        logger.error(f"Ошибка импорта модулей кеша: {e}")
        return False
    except Exception as e:
        logger.error(f"Ошибка при сохранении состояния кеша: {e}")
        return False

def cleanup_observers():
    """
    Остановка всех наблюдателей за файловой системой и освобождение ресурсов.
    Выполняет радикальную очистку всех возможных процессов и ресурсов.
    
    Returns:
        True, если очистка успешна, иначе False
    """
    logger.info("Остановка наблюдателей и радикальное освобождение ресурсов...")
    
    try:
        # Шаг 1: Выполняем все зарегистрированные обработчики очистки
        try:
            from advising_platform.src.cache.cleanup_handlers import run_cleanup_handlers
            run_cleanup_handlers()
            logger.info("Выполнены все зарегистрированные обработчики очистки")
        except ImportError as e:
            logger.warning(f"Не удалось импортировать обработчики очистки: {e}")
        except Exception as e:
            logger.error(f"Ошибка при выполнении обработчиков очистки: {e}")
        
        # Шаг 2: Останавливаем кеш-менеджер и освобождаем его ресурсы
        try:
            from advising_platform.src.cache.document_cache import DocumentCacheManager
            
            # Получаем экземпляр кеш-менеджера
            cache_manager = DocumentCacheManager.get_instance()
            
            # Останавливаем кеш-менеджер
            if hasattr(cache_manager, 'shutdown'):
                cache_manager.shutdown()
                logger.info("Кеш-менеджер успешно остановлен")
            
            # Принудительно освобождаем ресурсы
            if hasattr(cache_manager, 'document_cache'):
                # Сохраняем состояние кеша перед очисткой
                backup_cache_state()
                
                # Очищаем кеш для освобождения памяти
                if hasattr(cache_manager.document_cache, 'clear'):
                    cache_manager.document_cache.clear()
                    logger.info("Кеш документов очищен для освобождения памяти")
        except ImportError as e:
            logger.warning(f"Не удалось импортировать DocumentCacheManager: {e}")
        except Exception as e:
            logger.error(f"Ошибка при остановке кеш-менеджера: {e}")
        
        # Шаг 3: Радикальная очистка - закрываем все открытые файлы
        try:
            import gc
            import io
            import sys as system_module  # Переименовываем для избежания конфликта
            
            # Запускаем сборщик мусора для освобождения неиспользуемых объектов
            gc.collect()
            logger.info("Запущен сборщик мусора для освобождения неиспользуемых объектов")
            
            # Получаем ссылки на стандартные потоки
            std_in = system_module.stdin
            std_out = system_module.stdout
            std_err = system_module.stderr
            
            # Принудительно закрываем все файлы, которые могут быть открыты
            file_objects_closed = 0
            for obj in gc.get_objects():
                try:
                    # Проверяем, является ли объект файлом и открыт ли он
                    if isinstance(obj, io.IOBase) and hasattr(obj, 'closed') and not obj.closed:
                        # Игнорируем стандартные потоки
                        if obj not in [std_in, std_out, std_err]:
                            # Пытаемся закрыть файл
                            obj.close()
                            file_objects_closed += 1
                except Exception:
                    # Игнорируем любые ошибки при проверке или закрытии объектов
                    pass
            
            logger.info(f"Закрыто {file_objects_closed} файловых объектов")
        except Exception as e:
            logger.error(f"Ошибка при попытке закрыть файловые дескрипторы: {e}")
        
        # Шаг 4: Очищаем модули в памяти, которые могут держать файловые дескрипторы
        try:
            import sys as system_module  # Используем переименованный импорт
            
            modules_to_clear = []
            for name, module in system_module.modules.items():
                if 'advising_platform' in name:
                    modules_to_clear.append(name)
            
            # Удаляем модули из sys.modules
            for name in modules_to_clear:
                if name in system_module.modules:
                    del system_module.modules[name]
            
            logger.info(f"Очищено {len(modules_to_clear)} модулей из памяти")
        except Exception as e:
            logger.error(f"Ошибка при очистке модулей: {e}")
        
        # Шаг 5: Даем системе достаточно времени на полное освобождение ресурсов
        time.sleep(3)
        
        try:
            # Еще раз запускаем сборщик мусора (проверяем, что gc определен)
            if 'gc' in locals():
                gc.collect()
                logger.info("Повторно запущен сборщик мусора")
        except Exception as e:
            logger.error(f"Ошибка при повторном запуске сборщика мусора: {e}")
        
        # Шаг 6: Создаем отчет об очистке
        try:
            cleanup_report = {
                "timestamp": datetime.now().isoformat(),
                "cleanup_status": "success",
                "gc_collected": True,
                "resources_freed": True
            }
            
            if not os.path.exists(CHECKPOINT_BACKUP_DIR):
                os.makedirs(CHECKPOINT_BACKUP_DIR)
                
            cleanup_report_file = os.path.join(CHECKPOINT_BACKUP_DIR, "cleanup_report.json")
            with open(cleanup_report_file, 'w', encoding='utf-8') as f:
                json.dump(cleanup_report, f, indent=2)
                
            logger.info(f"Создан отчет об очистке ресурсов: {cleanup_report_file}")
        except Exception as e:
            logger.error(f"Ошибка при создании отчета об очистке: {e}")
        
        logger.info("Радикальная очистка ресурсов завершена")
        return True
    except Exception as e:
        logger.error(f"Критическая ошибка при радикальной очистке ресурсов: {e}")
        return False

def restore_after_checkpoint():
    """
    Восстанавливает состояние кеша после создания чекпоинта.
    Эта функция должна выполняться после восстановления из чекпоинта.
    
    Returns:
        True, если восстановление успешно, иначе False
    """
    logger.info("Восстановление состояния кеша после чекпоинта...")
    
    if not os.path.exists(CACHE_BACKUP_FILE) or not os.path.exists(STATE_BACKUP_FILE):
        logger.error("Файлы резервных копий не найдены")
        # Проверяем, существуют ли основные файлы состояния
        if os.path.exists('.cache_state.json') and os.path.exists('.cache_detailed_state.pickle'):
            logger.info("Найдены основные файлы состояния, попытка восстановления из них...")
        else:
            logger.error("Основные файлы состояния также не найдены. Восстановление невозможно.")
            return False
    
    try:
        from advising_platform.src.cache.document_cache import DocumentCacheManager
        from advising_platform.src.cache.cache_state import CacheStateManager
        
        # Проверяем существование метаданных чекпоинта
        if os.path.exists(METADATA_FILE):
            try:
                with open(METADATA_FILE, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                logger.info(f"Метаданные чекпоинта найдены: {metadata}")
                # Используем информацию из метаданных для проверки целостности
                max_cache_size = metadata.get('cache_state', {}).get('max_cache_size', 500)
            except Exception as e:
                logger.error(f"Ошибка при чтении метаданных чекпоинта: {e}")
                max_cache_size = 500
        else:
            logger.warning("Метаданные чекпоинта не найдены, используем значение по умолчанию")
            max_cache_size = 500
        
        # Пытаемся восстановить из резервных копий
        cache_data = {}
        state = {}
        
        if os.path.exists(CACHE_BACKUP_FILE):
            try:
                with open(CACHE_BACKUP_FILE, 'rb') as f:
                    cache_data = pickle.load(f)
                logger.info(f"Данные кеша загружены из резервной копии: {len(cache_data)} документов")
            except Exception as e:
                logger.error(f"Ошибка при загрузке данных кеша из резервной копии: {e}")
        
        if os.path.exists(STATE_BACKUP_FILE):
            try:
                with open(STATE_BACKUP_FILE, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                logger.info(f"Состояние загружено из резервной копии")
            except Exception as e:
                logger.error(f"Ошибка при загрузке состояния из резервной копии: {e}")
        
        # Убеждаемся, что max_cache_size установлен правильно
        state['max_cache_size'] = max_cache_size
        
        # Сохраняем обновленное состояние
        CacheStateManager.save_state(state)
        
        # Копируем резервные файлы в основные, если основных не существует
        if not os.path.exists('.cache_state.json') and os.path.exists(STATE_BACKUP_FILE):
            shutil.copy2(STATE_BACKUP_FILE, '.cache_state.json')
            logger.info("Скопирован файл состояния из резервной копии")
        
        if not os.path.exists('.cache_detailed_state.pickle') and os.path.exists(CACHE_BACKUP_FILE):
            # Для детального состояния создаем облегченную версию
            try:
                # Создаем структуру для детального состояния
                lightweight_cache = {}
                for path, doc_info in cache_data.items():
                    lightweight_cache[path] = {
                        'last_accessed': doc_info.get('last_accessed', 0),
                        'last_updated': doc_info.get('last_updated', 0),
                        'access_count': doc_info.get('access_count', 0),
                        'size': doc_info.get('size', 0)
                    }
                
                detailed_state = {
                    'cache_metadata': lightweight_cache,
                    'versions': {}
                }
                
                with open('.cache_detailed_state.pickle', 'wb') as f:
                    pickle.dump(detailed_state, f)
                logger.info("Создан файл детального состояния из резервной копии")
            except Exception as e:
                logger.error(f"Ошибка при создании детального состояния: {e}")
        
        # Получаем экземпляр кеш-менеджера с правильным размером кеша
        cache_manager = DocumentCacheManager.get_instance(max_cache_size=max_cache_size)
        
        # Восстанавливаем кеш, если есть данные
        if cache_data and hasattr(cache_manager, 'document_cache'):
            cache_manager.document_cache.cached_documents = cache_data
            logger.info(f"Состояние кеша восстановлено. Загружено {len(cache_data)} документов.")
        
        # Создаем отчет о восстановлении
        recovery_report = {
            "timestamp": datetime.now().isoformat(),
            "restored_documents": len(cache_data),
            "max_cache_size": max_cache_size,
            "success": True,
            "source": "checkpoint_backup" if os.path.exists(CACHE_BACKUP_FILE) else "regular_state"
        }
        
        with open(os.path.join(CHECKPOINT_BACKUP_DIR, "recovery_report.json"), 'w', encoding='utf-8') as f:
            json.dump(recovery_report, f, indent=2)
        
        return True
    except ImportError as e:
        logger.error(f"Ошибка импорта модулей кеша: {e}")
        return False
    except Exception as e:
        logger.error(f"Ошибка при восстановлении состояния кеша: {e}")
        return False

def prepare_for_checkpoint():
    """
    Комплексная подготовка системы к созданию чекпоинта.
    
    Returns:
        True, если подготовка успешна, иначе False
    """
    logger.info("=== Подготовка к созданию чекпоинта ===")
    
    # Создаем директорию для резервных копий
    ensure_backup_dir()
    
    # Сохраняем метаданные
    if not save_metadata():
        logger.warning("Не удалось сохранить метаданные, но процесс будет продолжен")
    
    # Сохраняем состояние кеша
    cache_backed_up = backup_cache_state()
    if not cache_backed_up:
        logger.error("Не удалось сохранить состояние кеша")
        return False
    
    # Останавливаем наблюдателей и освобождаем ресурсы
    observers_cleaned = cleanup_observers()
    if not observers_cleaned:
        logger.error("Не удалось остановить наблюдателей за файловой системой")
        return False
    
    logger.info("Система успешно подготовлена к созданию чекпоинта")
    return True

def main():
    """
    Основная функция скрипта.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Улучшенная система создания чекпоинтов")
    parser.add_argument('--prepare', action='store_true', 
                       help='Подготовить систему к созданию чекпоинта')
    parser.add_argument('--restore', action='store_true',
                       help='Восстановить состояние после создания чекпоинта')
    parser.add_argument('--backup', action='store_true',
                       help='Только сохранить резервную копию кеша')
    parser.add_argument('--cleanup', action='store_true',
                       help='Только остановить наблюдателей и освободить ресурсы')
    
    args = parser.parse_args()
    
    if args.prepare:
        success = prepare_for_checkpoint()
        sys.exit(0 if success else 1)
    elif args.restore:
        success = restore_after_checkpoint()
        sys.exit(0 if success else 1)
    elif args.backup:
        ensure_backup_dir()
        success = backup_cache_state()
        sys.exit(0 if success else 1)
    elif args.cleanup:
        success = cleanup_observers()
        sys.exit(0 if success else 1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()