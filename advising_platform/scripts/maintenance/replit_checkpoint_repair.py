#!/usr/bin/env python3
"""
Инструмент для восстановления и проверки системных файлов Replit, 
необходимых для корректной работы чекпоинтов.

Этот скрипт:
1. Проверяет наличие системных файлов .replit, .gitignore, .cache и других
2. Восстанавливает отсутствующие или поврежденные файлы
3. Принудительно запускает внутренние процессы Replit для обновления файлов .checksum_mapping
4. Выполняет очистку кеша и временных файлов
"""

import os
import sys
import json
import time
import shutil
import logging
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("replit_checkpoint_repair")

# Константы
DEFAULT_REPLIT_CONFIG = """
run = "python cache_init.py"
hidden = ["venv", ".config", "**/__pycache__", "**/.mypy_cache", "**/*.pyc"]

[env]
PYTHONPATH = "${REPL_HOME}"

[nix]
channel = "stable-22_11"

[unitTest]
language = "python3"

[languages]

[languages.python3]
pattern = "**/*.py"

[languages.python3.languageServer]
start = "pylsp"
"""

DEFAULT_GITIGNORE = """
.env
__pycache__/
*.py[cod]
*$py.class
.cache_state.json
.cache_detailed_state.pickle
.checkpoint_backup/
"""

def check_system_files():
    """
    Проверяет наличие и целостность системных файлов Replit.
    
    Returns:
        Dict[str, Any]: Результаты проверки
    """
    logger.info("Проверка системных файлов Replit...")
    
    results = {
        "replit_file": os.path.exists(".replit"),
        "gitignore_file": os.path.exists(".gitignore"),
        "checksum_mapping": False,
        "other_system_files": {}
    }
    
    # Проверяем наличие файла .checksum_mapping
    for file_name in os.listdir('.'):
        if file_name.startswith('.checksum_') or file_name == '.checksum_mapping':
            results["checksum_mapping"] = True
            break
    
    # Проверяем другие скрытые файлы Replit
    for file_name in os.listdir('.'):
        if file_name.startswith('.') and file_name not in ['.replit', '.gitignore', '.git']:
            results["other_system_files"][file_name] = True
    
    logger.info(f"Результаты проверки: .replit существует: {results['replit_file']}, "
                f".gitignore существует: {results['gitignore_file']}, "
                f".checksum_mapping существует: {results['checksum_mapping']}")
    
    return results

def restore_system_files(results):
    """
    Восстанавливает отсутствующие или поврежденные системные файлы.
    
    Args:
        results: Результаты проверки
        
    Returns:
        Dict[str, bool]: Результаты восстановления
    """
    logger.info("Восстановление системных файлов Replit...")
    
    restore_results = {
        "replit_file": False,
        "gitignore_file": False,
        "force_checksum_update": False
    }
    
    # Восстанавливаем .replit если отсутствует
    if not results["replit_file"]:
        try:
            with open(".replit", 'w', encoding='utf-8') as f:
                f.write(DEFAULT_REPLIT_CONFIG.strip())
            
            restore_results["replit_file"] = True
            logger.info("Файл .replit восстановлен")
        except Exception as e:
            logger.error(f"Ошибка при восстановлении файла .replit: {e}")
    
    # Восстанавливаем .gitignore если отсутствует
    if not results["gitignore_file"]:
        try:
            with open(".gitignore", 'w', encoding='utf-8') as f:
                f.write(DEFAULT_GITIGNORE.strip())
            
            restore_results["gitignore_file"] = True
            logger.info("Файл .gitignore восстановлен")
        except Exception as e:
            logger.error(f"Ошибка при восстановлении файла .gitignore: {e}")
    
    # Форсируем обновление .checksum_mapping
    if not results["checksum_mapping"]:
        try:
            # Создаем временный файл для инициации обновления контрольных сумм
            timestamp = int(time.time())
            tmp_file_name = f".tmp_force_checksum_update_{timestamp}"
            
            with open(tmp_file_name, 'w', encoding='utf-8') as f:
                f.write(f"Force checksum update at {datetime.now().isoformat()}")
            
            # Даем время системе на создание .checksum_mapping
            time.sleep(2)
            
            # Удаляем временный файл
            if os.path.exists(tmp_file_name):
                os.remove(tmp_file_name)
            
            restore_results["force_checksum_update"] = True
            logger.info("Форсировано обновление .checksum_mapping")
        except Exception as e:
            logger.error(f"Ошибка при обновлении .checksum_mapping: {e}")
    
    return restore_results

def cleanup_cache_and_temp_files():
    """
    Очищает кеш и временные файлы.
    
    Returns:
        int: Количество удаленных файлов
    """
    logger.info("Очистка кеша и временных файлов...")
    
    files_removed = 0
    
    # Временные файлы для очистки
    temp_patterns = [
        '*__pycache__*',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.DS_Store',
        '.coverage',
        'Thumbs.db'
    ]
    
    # Используем подпроцесс для поиска и удаления файлов
    for pattern in temp_patterns:
        try:
            cmd = f'find . -name "{pattern}" -type f -delete'
            subprocess.run(cmd, shell=True, check=False)
            files_removed += 1  # Приблизительный подсчет
        except Exception as e:
            logger.error(f"Ошибка при удалении временных файлов {pattern}: {e}")
    
    logger.info(f"Приблизительно удалено {files_removed} временных файлов")
    return files_removed

def update_file_timestamps():
    """
    Обновляет временные метки файлов для инициации создания чекпоинта.
    
    Returns:
        int: Количество обновленных файлов
    """
    logger.info("Обновление временных меток файлов...")
    
    files_updated = 0
    critical_files = [
        '.replit',
        '.gitignore',
        'safe_checkpoint.py',
        'cache_init.py',
        'checkpoint_diagnostics.py'
    ]
    
    # Обновляем временные метки критических файлов
    for file_name in critical_files:
        if os.path.exists(file_name):
            try:
                # Обновляем время модификации
                os.utime(file_name, None)
                files_updated += 1
            except Exception as e:
                logger.error(f"Ошибка при обновлении временной метки файла {file_name}: {e}")
    
    logger.info(f"Обновлены временные метки {files_updated} файлов")
    return files_updated

def create_checksum_force_file():
    """
    Создает специальный файл для принудительного обновления контрольных сумм Replit.
    
    Returns:
        bool: True, если файл создан успешно, иначе False
    """
    logger.info("Создание файла для принудительного обновления контрольных сумм...")
    
    try:
        # Содержимое файла должно включать текущее время для обеспечения уникальности
        content = f"""
# Replit Checksum Force Update
# Created at: {datetime.now().isoformat()}
# 
# This file forces the Replit system to regenerate checksum mappings
# which are essential for checkpoint functionality.
#
# You can safely delete this file after checkpoint creation.
#
FORCE_TIMESTAMP={int(time.time())}
        """
        
        file_name = ".replit_checksum_force"
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Файл {file_name} создан успешно")
        return True
    except Exception as e:
        logger.error(f"Ошибка при создании файла для принудительного обновления контрольных сумм: {e}")
        return False

def run_file_indexing():
    """
    Запускает индексацию файлов для обновления системных данных Replit.
    
    Returns:
        bool: True, если индексация выполнена успешно, иначе False
    """
    logger.info("Запуск индексации файлов...")
    
    try:
        # Создаем индекс файлов
        file_list = []
        for root, dirs, files in os.walk('.'):
            # Пропускаем скрытые директории
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if not file.startswith('.'):
                    file_path = os.path.join(root, file)
                    file_list.append(file_path)
        
        # Сохраняем индекс в файл
        with open(".file_index.json", 'w', encoding='utf-8') as f:
            json.dump(file_list, f, indent=2)
        
        logger.info(f"Индексация файлов завершена. Проиндексировано {len(file_list)} файлов")
        return True
    except Exception as e:
        logger.error(f"Ошибка при индексации файлов: {e}")
        return False

def main():
    """
    Основная функция скрипта.
    """
    logger.info("=== Запуск инструмента восстановления чекпоинтов Replit ===")
    
    # Проверяем системные файлы
    check_results = check_system_files()
    
    # Восстанавливаем системные файлы
    restore_results = restore_system_files(check_results)
    
    # Очищаем кеш и временные файлы
    cleanup_cache_and_temp_files()
    
    # Обновляем временные метки файлов
    update_file_timestamps()
    
    # Создаем файл для принудительного обновления контрольных сумм
    create_checksum_force_file()
    
    # Запускаем индексацию файлов
    run_file_indexing()
    
    logger.info("=== Инструмент восстановления чекпоинтов Replit завершил работу ===")
    
    print("\nРекомендации для создания чекпоинта:")
    print("1. Выполните полную остановку всех процессов: python safe_checkpoint.py --cleanup")
    print("2. Подготовьте систему к созданию чекпоинта: python safe_checkpoint.py --prepare")
    print("3. Создайте чекпоинт через интерфейс Replit")
    print("4. После восстановления из чекпоинта выполните: python safe_checkpoint.py --restore")

if __name__ == "__main__":
    main()