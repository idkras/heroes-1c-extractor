#!/usr/bin/env python3
"""
Скрипт для завершения очистки после реорганизации файловой структуры.
Удаляет избыточные файлы и резервные копии, созданные в процессе миграции.
"""

import os
import sys
import time
import shutil
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Set, Tuple

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cleanup")

def list_backup_directories() -> List[str]:
    """
    Находит все директории с резервными копиями.
    
    Returns:
        Список путей к директориям с резервными копиями
    """
    backup_dirs = []
    
    # Паттерны для поиска резервных копий
    backup_patterns = [
        "backup_", 
        "src_backup_", 
        "_backup"
    ]
    
    for item in os.listdir('.'):
        if os.path.isdir(item):
            for pattern in backup_patterns:
                if pattern in item:
                    backup_dirs.append(item)
                    break
    
    return backup_dirs

def analyze_file_structure() -> Dict[str, List[str]]:
    """
    Анализирует текущую файловую структуру для выявления избыточных файлов.
    
    Returns:
        Словарь с категориями избыточных файлов
    """
    redundant_files = {
        "backup_dirs": list_backup_directories(),
        "obsolete_files": [],
        "temp_files": [],
        "log_files": []
    }
    
    # Список устаревших файлов, которые должны быть перемещены или удалены
    obsolete_file_patterns = [
        ".context_cache_state.json",
        "cache_validation.log",
        "cache_validation_report.json",
        "data_migration.log",
        "directory_move.log",
        "bidirectional_sync_test_results.json",
        "todo_validation.log"
    ]
    
    # Поиск устаревших файлов
    for item in os.listdir('.'):
        if os.path.isfile(item):
            # Проверка на устаревшие файлы
            for pattern in obsolete_file_patterns:
                if pattern in item:
                    redundant_files["obsolete_files"].append(item)
                    break
            
            # Проверка на временные файлы
            if item.endswith('.tmp') or item.endswith('.bak') or item.endswith('.swp'):
                redundant_files["temp_files"].append(item)
            
            # Проверка на лог-файлы
            if item.endswith('.log') and not item in redundant_files["obsolete_files"]:
                redundant_files["log_files"].append(item)
    
    return redundant_files

def clean_backup_directories(backup_dirs: List[str], dry_run: bool = True) -> Tuple[int, int]:
    """
    Удаляет директории с резервными копиями.
    
    Args:
        backup_dirs: Список директорий для удаления
        dry_run: Если True, только симулирует удаление
        
    Returns:
        Кортеж (количество успешно удаленных директорий, количество ошибок)
    """
    success_count = 0
    error_count = 0
    
    for directory in backup_dirs:
        try:
            if dry_run:
                logger.info(f"[DRY RUN] Удаление директории: {directory}")
            else:
                logger.info(f"Удаление директории: {directory}")
                shutil.rmtree(directory)
            success_count += 1
        except Exception as e:
            logger.error(f"Ошибка при удалении директории {directory}: {e}")
            error_count += 1
    
    return success_count, error_count

def clean_obsolete_files(files: List[str], dry_run: bool = True) -> Tuple[int, int]:
    """
    Удаляет устаревшие файлы.
    
    Args:
        files: Список файлов для удаления
        dry_run: Если True, только симулирует удаление
        
    Returns:
        Кортеж (количество успешно удаленных файлов, количество ошибок)
    """
    success_count = 0
    error_count = 0
    
    for file in files:
        try:
            if dry_run:
                logger.info(f"[DRY RUN] Удаление файла: {file}")
            else:
                logger.info(f"Удаление файла: {file}")
                os.remove(file)
            success_count += 1
        except Exception as e:
            logger.error(f"Ошибка при удалении файла {file}: {e}")
            error_count += 1
    
    return success_count, error_count

def archive_log_files(files: List[str], dry_run: bool = True) -> Tuple[int, int]:
    """
    Архивирует лог-файлы в директорию logs.
    
    Args:
        files: Список лог-файлов для архивации
        dry_run: Если True, только симулирует архивацию
        
    Returns:
        Кортеж (количество успешно архивированных файлов, количество ошибок)
    """
    success_count = 0
    error_count = 0
    
    # Создаем директорию для логов, если её нет
    logs_dir = 'advising_platform/logs'
    try:
        if not os.path.exists(logs_dir) and not dry_run:
            os.makedirs(logs_dir)
    except Exception as e:
        logger.error(f"Ошибка при создании директории для логов: {e}")
        return 0, len(files)
    
    # Перемещаем лог-файлы
    for file in files:
        try:
            dest_file = os.path.join(logs_dir, f"{file}_{int(time.time())}")
            if dry_run:
                logger.info(f"[DRY RUN] Перемещение лог-файла: {file} -> {dest_file}")
            else:
                logger.info(f"Перемещение лог-файла: {file} -> {dest_file}")
                shutil.move(file, dest_file)
            success_count += 1
        except Exception as e:
            logger.error(f"Ошибка при перемещении лог-файла {file}: {e}")
            error_count += 1
    
    return success_count, error_count

def main():
    """
    Основная функция скрипта.
    """
    parser = argparse.ArgumentParser(description="Очистка после реорганизации файловой структуры")
    parser.add_argument('--analyze', action='store_true', help='Только анализ без удаления')
    parser.add_argument('--backups', action='store_true', help='Удалить резервные копии')
    parser.add_argument('--obsolete', action='store_true', help='Удалить устаревшие файлы')
    parser.add_argument('--logs', action='store_true', help='Архивировать лог-файлы')
    parser.add_argument('--all', action='store_true', help='Выполнить все операции')
    parser.add_argument('--apply', action='store_true', help='Применить изменения (без этого флага запускается в режиме dry run)')
    
    args = parser.parse_args()
    
    # Анализируем файловую структуру
    logger.info("Анализ файловой структуры...")
    redundant_files = analyze_file_structure()
    
    # Выводим результаты анализа
    logger.info("Результаты анализа:")
    logger.info(f"Директории с резервными копиями: {len(redundant_files['backup_dirs'])}")
    if redundant_files['backup_dirs']:
        for dir in redundant_files['backup_dirs']:
            logger.info(f"  - {dir}")
    
    logger.info(f"Устаревшие файлы: {len(redundant_files['obsolete_files'])}")
    if redundant_files['obsolete_files']:
        for file in redundant_files['obsolete_files']:
            logger.info(f"  - {file}")
    
    logger.info(f"Временные файлы: {len(redundant_files['temp_files'])}")
    if redundant_files['temp_files']:
        for file in redundant_files['temp_files']:
            logger.info(f"  - {file}")
    
    logger.info(f"Лог-файлы: {len(redundant_files['log_files'])}")
    if redundant_files['log_files']:
        for file in redundant_files['log_files']:
            logger.info(f"  - {file}")
    
    # Если указан только флаг --analyze, завершаем работу
    if args.analyze and not any([args.backups, args.obsolete, args.logs, args.all]):
        return
    
    # Режим выполнения (dry run или реальное применение)
    dry_run = not args.apply
    if dry_run:
        logger.info("Запуск в режиме DRY RUN. Изменения не будут применены.")
    else:
        logger.info("Режим применения изменений.")
    
    # Очистка резервных копий
    if args.backups or args.all:
        success, errors = clean_backup_directories(redundant_files['backup_dirs'], dry_run)
        logger.info(f"Удаление резервных копий: {success} успешно, {errors} с ошибками")
    
    # Очистка устаревших файлов
    if args.obsolete or args.all:
        success, errors = clean_obsolete_files(redundant_files['obsolete_files'], dry_run)
        logger.info(f"Удаление устаревших файлов: {success} успешно, {errors} с ошибками")
        
        # Очистка временных файлов
        success, errors = clean_obsolete_files(redundant_files['temp_files'], dry_run)
        logger.info(f"Удаление временных файлов: {success} успешно, {errors} с ошибками")
    
    # Архивация лог-файлов
    if args.logs or args.all:
        success, errors = archive_log_files(redundant_files['log_files'], dry_run)
        logger.info(f"Архивация лог-файлов: {success} успешно, {errors} с ошибками")

if __name__ == "__main__":
    main()