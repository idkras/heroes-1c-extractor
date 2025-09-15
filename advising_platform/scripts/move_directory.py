#!/usr/bin/env python3
"""
Скрипт для безопасного перемещения директорий с соблюдением стандарта управления файловой структурой.
Использует двухэтапный подход: сначала копирование, затем удаление после проверки.

Использование:
    python move_directory.py --source src --target advising_platform/src --mode copy
    # После проверки:
    python move_directory.py --source src --target advising_platform/src --mode cleanup

Соответствует стандарту standard-codebase-file-management.
"""

import os
import sys
import shutil
import argparse
import filecmp
from pathlib import Path
import datetime
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('directory_move.log')
    ]
)
logger = logging.getLogger('directory_mover')

def setup_directories(source, target):
    """
    Проверяет существование исходной директории и создает целевую, если необходимо.
    
    Args:
        source (Path): Путь к исходной директории
        target (Path): Путь к целевой директории
    
    Returns:
        bool: True, если директории готовы, иначе False
    """
    # Проверка существования исходной директории
    if not source.exists() or not source.is_dir():
        logger.error(f"Ошибка: исходная директория {source} не существует или не является директорией")
        return False
        
    # Создание целевой директории, если она не существует
    if not target.exists():
        try:
            target.mkdir(parents=True, exist_ok=True)
            logger.info(f"Создана целевая директория: {target}")
        except Exception as e:
            logger.error(f"Ошибка при создании целевой директории {target}: {e}")
            return False
    
    return True

def create_backup(source):
    """
    Создает резервную копию исходной директории.
    
    Args:
        source (Path): Путь к исходной директории
    
    Returns:
        Path: Путь к резервной копии
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = source.parent / f"{source.name}_backup_{timestamp}"
    
    try:
        shutil.copytree(source, backup_dir)
        logger.info(f"Создана резервная копия: {backup_dir}")
        return backup_dir
    except Exception as e:
        logger.error(f"Ошибка при создании резервной копии: {e}")
        return None

def copy_directory_contents(source, target, ignore_patterns=None):
    """
    Копирует содержимое исходной директории в целевую.
    
    Args:
        source (Path): Путь к исходной директории
        target (Path): Путь к целевой директории
        ignore_patterns (list): Список паттернов файлов, которые нужно игнорировать
    
    Returns:
        int: Количество скопированных файлов
    """
    if ignore_patterns is None:
        ignore_patterns = ['__pycache__', '*.pyc', '*.pyo', '.git', '.svn']
    
    copied_files = 0
    
    for root, dirs, files in os.walk(source):
        # Применяем игнорируемые паттерны
        dirs[:] = [d for d in dirs if not any(p in d for p in ignore_patterns)]
        
        # Относительный путь от исходной директории
        rel_path = os.path.relpath(root, source)
        
        # Создаем соответствующую директорию в целевой папке
        if rel_path == '.':
            target_dir = target
        else:
            target_dir = target / rel_path
            target_dir.mkdir(exist_ok=True)
        
        # Копируем каждый файл
        for file in files:
            if any(p in file for p in ignore_patterns):
                continue
                
            source_file = Path(root) / file
            target_file = target_dir / file
            
            try:
                # Проверяем, существует ли файл в целевой директории
                if target_file.exists():
                    # Сравниваем содержимое
                    if filecmp.cmp(source_file, target_file, shallow=False):
                        logger.info(f"Файл уже существует и идентичен: {target_file}")
                    else:
                        # Создаем резервную копию существующего файла
                        backup_file = target_file.with_name(f"{target_file.name}.bak")
                        shutil.copy2(target_file, backup_file)
                        # Копируем новый файл
                        shutil.copy2(source_file, target_file)
                        logger.info(f"Обновлен файл: {target_file} (создана резервная копия)")
                else:
                    # Копируем файл
                    shutil.copy2(source_file, target_file)
                    logger.info(f"Скопирован файл: {target_file}")
                
                copied_files += 1
            except Exception as e:
                logger.error(f"Ошибка при копировании {source_file} -> {target_file}: {e}")
    
    return copied_files

def update_imports(target_dir, old_prefix, new_prefix):
    """
    Обновляет импорты в скопированных файлах.
    
    Args:
        target_dir (Path): Директория с скопированными файлами
        old_prefix (str): Старый префикс импорта
        new_prefix (str): Новый префикс импорта
    
    Returns:
        int: Количество обновленных файлов
    """
    updated_files = 0
    
    for root, _, files in os.walk(target_dir):
        for file in files:
            if not file.endswith('.py'):
                continue
                
            file_path = Path(root) / file
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Обновляем импорты
                updated_content = content.replace(f"import {old_prefix}", f"import {new_prefix}")
                updated_content = updated_content.replace(f"from {old_prefix}", f"from {new_prefix}")
                
                if content != updated_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    
                    logger.info(f"Обновлены импорты в файле: {file_path}")
                    updated_files += 1
            except Exception as e:
                logger.error(f"Ошибка при обновлении импортов в {file_path}: {e}")
    
    return updated_files

def cleanup_source_directory(source):
    """
    Удаляет исходную директорию после успешного перемещения.
    
    Args:
        source (Path): Путь к исходной директории
    
    Returns:
        bool: True, если директория успешно удалена
    """
    try:
        shutil.rmtree(source)
        logger.info(f"Удалена исходная директория: {source}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при удалении исходной директории {source}: {e}")
        return False

def check_result(source, target):
    """
    Проверяет результат перемещения.
    
    Args:
        source (Path): Путь к исходной директории
        target (Path): Путь к целевой директории
    
    Returns:
        bool: True, если копирование успешно
    """
    # Если исходная директория содержит __init__.py, проверяем его наличие в целевой
    init_py = source / '__init__.py'
    if init_py.exists():
        target_init_py = target / '__init__.py'
        if not target_init_py.exists():
            logger.warning(f"Внимание: в целевой директории отсутствует {target_init_py}")
            return False

    # Подсчитываем количество файлов в исходной и целевой директориях
    source_files = sum(1 for _ in source.glob('**/*') if _.is_file())
    target_files = sum(1 for _ in target.glob('**/*') if _.is_file())
    
    if source_files > target_files:
        logger.warning(f"Внимание: в исходной директории больше файлов ({source_files}) чем в целевой ({target_files})")
        return False
    
    logger.info(f"Проверка успешна: файлов в исходной директории: {source_files}, в целевой: {target_files}")
    return True

def handle_copy_mode(source, target, update_imports_flag):
    """
    Обрабатывает режим копирования.
    
    Args:
        source (Path): Путь к исходной директории
        target (Path): Путь к целевой директории
        update_imports_flag (bool): Флаг обновления импортов
    
    Returns:
        bool: True, если копирование успешно
    """
    # Создаем резервную копию
    backup = create_backup(source)
    if not backup:
        return False
    
    # Копируем содержимое
    copied_files = copy_directory_contents(source, target)
    logger.info(f"Скопировано файлов: {copied_files}")
    
    # Обновляем импорты, если требуется
    if update_imports_flag:
        old_prefix = source.name
        new_prefix = f"advising_platform.{target.relative_to(target.parent.parent).as_posix().replace('/', '.')}"
        updated_files = update_imports(target, old_prefix, new_prefix)
        logger.info(f"Обновлены импорты в {updated_files} файлах")
    
    # Проверяем результат
    success = check_result(source, target)
    
    if success:
        logger.info(
            f"Копирование успешно завершено! Следующие шаги:\n"
            f"1. Проверьте работоспособность системы\n"
            f"2. Запустите скрипт с режимом --mode cleanup для удаления оригинальной директории"
        )
    else:
        logger.warning(
            f"Копирование завершено с предупреждениями. Рекомендации:\n"
            f"1. Проверьте различия между исходной и целевой директориями\n"
            f"2. Исправьте проблемы вручную\n"
            f"3. Повторно запустите скрипт или продолжите вручную"
        )
    
    return success

def handle_cleanup_mode(source):
    """
    Обрабатывает режим очистки.
    
    Args:
        source (Path): Путь к исходной директории
    
    Returns:
        bool: True, если очистка успешна
    """
    # Создаем резервную копию перед удалением
    backup = create_backup(source)
    if not backup:
        return False
    
    # Удаляем исходную директорию
    success = cleanup_source_directory(source)
    
    if success:
        logger.info(
            f"Очистка успешно завершена!\n"
            f"Резервная копия сохранена в: {backup}"
        )
    else:
        logger.error(
            f"Ошибка при очистке исходной директории.\n"
            f"Резервная копия сохранена в: {backup}"
        )
    
    return success

def parse_arguments():
    """
    Обрабатывает аргументы командной строки.
    
    Returns:
        argparse.Namespace: Объект с аргументами командной строки
    """
    parser = argparse.ArgumentParser(
        description='Скрипт для безопасного перемещения директорий',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--source',
        required=True,
        help='Исходная директория для перемещения'
    )
    
    parser.add_argument(
        '--target',
        required=True,
        help='Целевая директория для перемещения'
    )
    
    parser.add_argument(
        '--mode',
        choices=['copy', 'cleanup'],
        default='copy',
        help='Режим работы: copy - копирование, cleanup - удаление оригинала'
    )
    
    parser.add_argument(
        '--update-imports',
        action='store_true',
        help='Обновить импорты в скопированных файлах'
    )
    
    return parser.parse_args()

def main():
    """
    Основная функция скрипта.
    
    Returns:
        int: Код завершения (0 - успех, 1 - ошибка)
    """
    args = parse_arguments()
    
    # Преобразуем пути в объекты Path
    source = Path(args.source)
    target = Path(args.target)
    
    # Проверяем и подготавливаем директории
    if not setup_directories(source, target):
        return 1
    
    # Выполняем операцию в зависимости от режима
    if args.mode == 'copy':
        success = handle_copy_mode(source, target, args.update_imports)
    else:
        success = handle_cleanup_mode(source)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())