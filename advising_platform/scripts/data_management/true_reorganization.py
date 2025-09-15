#!/usr/bin/env python3
"""
Скрипт для фактической реорганизации файловой структуры.

Этот скрипт физически перемещает файлы и директории из корня проекта
в соответствующие места в advising_platform с сохранением обратной совместимости.
"""

import os
import sys
import shutil
import datetime
import argparse
import logging
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set

# Настройка логирования
log_dir = os.path.join('data', 'logs')
os.makedirs(log_dir, exist_ok=True)

log_filename = f"file_reorganization_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(log_dir, log_filename))
    ]
)
logger = logging.getLogger(__name__)

# Директории для перемещения
DIRS_TO_MOVE = [
    'scripts',
    'hooks',
    'server',
    'docs',
    'templates',
    'tests',
    'data',
    'doc_changes',
    'examples',
    'git_logs'
]

# Файлы для перемещения с указанием целевой директории
FILES_TO_MOVE = {
    'process_incidents.py': 'advising_platform/scripts/incidents',
    'test_bidirectional_sync.py': 'advising_platform/scripts/tests'
}

# Файлы, которые должны остаться в корне
ROOT_FILES = [
    '.context_cache_state.json',
    '.env.example',
    '.gitignore',
    '.replit',
    '.roomodes',
    '.taskmasterconfig',
    '.windsurfrules',
    'bidirectional_sync_test_results.json',
    'cache_validation.log',
    'cache_validation_report.json',
    'data_migration.log',
    'directory_move.log',
    'document_registry.json',
    'generated-icon.png',
    'package.json',
    'package-lock.json',
    'pyproject.toml',
    'todo_validation.log',
    'uv.lock'
]

# Директории, которые должны остаться в корне
ROOT_DIRS = [
    '.git',
    '.cache',
    '.config',
    '.cursor',
    '.local',
    '.pythonlibs',
    '.roo',
    '.upm',
    '[projects]',
    '[projects] dmitry zaruta',
    '[standards .md]',
    '[todo · incidents]',
    'attached_assets',
    'backups',
    'node_modules',
    '__pycache__',
    'advising_platform',
    'src_backup_20250515_050822',
    'src_backup_20250515_051303'
]


def create_backup(dirs_to_backup: List[str], files_to_backup: List[str]) -> str:
    """
    Создает резервную копию директорий и файлов.
    
    Args:
        dirs_to_backup: Список директорий для резервного копирования
        files_to_backup: Список файлов для резервного копирования
        
    Returns:
        Путь к директории с резервной копией
    """
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f'backup_relocation_{timestamp}'
    os.makedirs(backup_dir, exist_ok=True)
    
    logger.info(f"Создание резервной копии в {backup_dir}")
    
    # Копирование директорий
    for dir_name in dirs_to_backup:
        if os.path.exists(dir_name) and os.path.isdir(dir_name):
            backup_path = os.path.join(backup_dir, dir_name)
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            logger.info(f"Копирование директории {dir_name} в {backup_path}")
            shutil.copytree(dir_name, backup_path)
    
    # Копирование файлов
    for file_name in files_to_backup:
        if os.path.exists(file_name) and os.path.isfile(file_name):
            backup_path = os.path.join(backup_dir, file_name)
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            logger.info(f"Копирование файла {file_name} в {backup_path}")
            shutil.copy2(file_name, backup_path)
    
    logger.info(f"Резервная копия создана в {backup_dir}")
    return backup_dir


def create_python_redirect(original_path: str, target_path: str) -> None:
    """
    Создает Python файл-редирект.
    
    Args:
        original_path: Исходный путь к файлу
        target_path: Целевой путь к файлу
    """
    module_name = os.path.splitext(os.path.basename(original_path))[0]
    target_import_path = os.path.splitext(target_path)[0].replace('/', '.')
    
    redirect_content = f'''import sys
import os

print("Перенаправление на {target_path}...")

# Добавляем путь к директории проекта в sys.path
sys.path.insert(0, os.path.abspath("."))

# Импортируем и запускаем модуль
from {target_import_path} import {module_name}

if __name__ == "__main__":
    {module_name}.main()
'''
    
    with open(original_path, 'w', encoding='utf-8') as f:
        f.write(redirect_content)
    
    logger.info(f"Создан Python редирект {original_path} -> {target_path}")


def move_directory(source_dir: str, target_dir: str) -> None:
    """
    Перемещает директорию с сохранением структуры.
    
    Args:
        source_dir: Исходная директория
        target_dir: Целевая директория
    """
    if not os.path.exists(source_dir):
        logger.warning(f"Исходная директория не существует: {source_dir}")
        return
    
    logger.info(f"Перемещение директории {source_dir} -> {target_dir}")
    
    # Создаем целевую директорию, если она не существует
    os.makedirs(target_dir, exist_ok=True)
    
    # Перемещаем содержимое директории
    for item in os.listdir(source_dir):
        source_item = os.path.join(source_dir, item)
        target_item = os.path.join(target_dir, item)
        
        if os.path.isdir(source_item):
            # Рекурсивно копируем директорию
            shutil.copytree(source_item, target_item, dirs_exist_ok=True)
            logger.info(f"Скопирована директория {source_item} -> {target_item}")
        else:
            # Копируем файл
            shutil.copy2(source_item, target_item)
            logger.info(f"Скопирован файл {source_item} -> {target_item}")
    
    # Удаляем исходную директорию
    if os.path.exists(source_dir) and source_dir != target_dir:
        logger.info(f"Удаление исходной директории {source_dir}")
        shutil.rmtree(source_dir)


def move_file(source_file: str, target_file: str, create_redirect: bool = True) -> None:
    """
    Перемещает файл с созданием редиректа.
    
    Args:
        source_file: Исходный файл
        target_file: Целевой файл
        create_redirect: Создавать ли редирект
    """
    if not os.path.exists(source_file):
        logger.warning(f"Исходный файл не существует: {source_file}")
        return
    
    logger.info(f"Перемещение файла {source_file} -> {target_file}")
    
    # Создаем директорию для целевого файла, если она не существует
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    
    # Копируем файл
    shutil.copy2(source_file, target_file)
    logger.info(f"Скопирован файл {source_file} -> {target_file}")
    
    # Создаем редирект, если нужно
    if create_redirect:
        if source_file.endswith('.py'):
            create_python_redirect(source_file, target_file)
        else:
            redirect_content = f'''# Файл перемещен
# {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Этот файл был перемещен в новое расположение в рамках реорганизации проекта.

Новый путь: {target_file}

Для доступа к актуальным данным используйте новый путь.
'''
            with open(source_file, 'w', encoding='utf-8') as f:
                f.write(redirect_content)
            
            logger.info(f"Создан текстовый редирект {source_file} -> {target_file}")


def reorganize_file_structure(dry_run: bool = False) -> None:
    """
    Реорганизует файловую структуру.
    
    Args:
        dry_run: Если True, то только выводит что будет сделано, без реальных изменений
    """
    logger.info("Начало реорганизации файловой структуры")
    
    if dry_run:
        logger.info("РЕЖИМ СИМУЛЯЦИИ - Изменения не будут применены")
    
    # Создаем резервную копию
    if not dry_run:
        backup_dir = create_backup(DIRS_TO_MOVE, list(FILES_TO_MOVE.keys()))
        logger.info(f"Резервная копия создана в {backup_dir}")
    
    # Перемещаем директории
    for dir_name in DIRS_TO_MOVE:
        if os.path.exists(dir_name) and os.path.isdir(dir_name):
            target_dir = os.path.join('advising_platform', dir_name)
            
            if dry_run:
                logger.info(f"[DRY RUN] Будет перемещена директория {dir_name} -> {target_dir}")
            else:
                move_directory(dir_name, target_dir)
    
    # Перемещаем файлы
    for source_file, target_dir in FILES_TO_MOVE.items():
        if os.path.exists(source_file) and os.path.isfile(source_file):
            target_file = os.path.join(target_dir, os.path.basename(source_file))
            
            if dry_run:
                logger.info(f"[DRY RUN] Будет перемещен файл {source_file} -> {target_file}")
            else:
                move_file(source_file, target_file)
    
    logger.info("Реорганизация файловой структуры завершена")


def main():
    """Основная функция скрипта."""
    parser = argparse.ArgumentParser(description='Реорганизация файловой структуры проекта')
    parser.add_argument('--dry-run', action='store_true',
                      help='Режим симуляции - только вывод планируемых действий без реальных изменений')
    
    args = parser.parse_args()
    
    logger.info("Запуск скрипта реорганизации файловой структуры")
    
    try:
        reorganize_file_structure(dry_run=args.dry_run)
        logger.info("Скрипт успешно завершил работу")
    except Exception as e:
        logger.error(f"Ошибка при выполнении скрипта: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())