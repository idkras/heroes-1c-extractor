#!/usr/bin/env python3
"""
Скрипт для очистки директорий проекта от устаревших и дублирующихся файлов.
Выполняет анализ структуры проекта, сравнивает с эталонной структурой и
предлагает действия по очистке.

Автор: AI Assistant
Дата: 21 мая 2025
"""

import os
import sys
import json
import shutil
import logging
import argparse
from typing import List, Dict, Set, Tuple, Optional, Any

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("cleanup_directories.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Определяем эталонную структуру проекта
REFERENCE_STRUCTURE = {
    "advising_platform": {
        "src": {
            "api": {},
            "cache": {
                "data": {},
                "locks": {}
            },
            "core": {
                "cache_sync": {},
                "registry": {}
            },
            "web": {
                "templates": {},
                "static": {}
            },
        },
        "tests": {}
    },
    "scripts": {
        "maintenance": {},
        "utils": {}
    },
    "docs": {},
    "incidents": {},
    "todo": {},
    "templates": {},
    "archive": {},
    "examples": {},
    "hypotheses": {},
    "tests": {}
}

# Список временных файлов и директорий для очистки
TEMP_FILES_PATTERNS = [
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "__pycache__",
    "*.so",
    "*.o",
    "*.obj",
    "*.tmp",
    "*.bak",
    "*.swp",
    "*.log",
    ".DS_Store",
    "Thumbs.db"
]

# Исключения - файлы и директории, которые нельзя удалять
EXCLUSIONS = [
    ".git",
    ".gitignore",
    "README.md",
    "LICENSE",
    ".env",
    "pyproject.toml",
    "package.json",
    "package-lock.json",
    "node_modules",
    "replit.nix",
    ".replit"
]

class DirectoryCleaner:
    """
    Класс для анализа и очистки директорий проекта.
    """
    
    def __init__(self, root_dir: str, reference_structure: Dict[str, Any],
                dry_run: bool = True, backup: bool = True,
                interactive: bool = True):
        """
        Инициализирует очиститель директорий.
        
        Args:
            root_dir: Корневая директория проекта
            reference_structure: Эталонная структура директорий
            dry_run: Режим симуляции без реального удаления
            backup: Создавать резервные копии удаляемых файлов и директорий
            interactive: Запрашивать подтверждение перед удалением
        """
        self.root_dir = os.path.abspath(root_dir)
        self.reference_structure = reference_structure
        self.dry_run = dry_run
        self.backup = backup
        self.interactive = interactive
        self.backup_dir = os.path.join(self.root_dir, "archive", "cleanup_backup")
        
        # Создаем директорию для резервных копий
        if self.backup and not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir, exist_ok=True)
    
    def analyze_structure(self) -> Tuple[List[str], List[str], List[str]]:
        """
        Анализирует текущую структуру директорий и сравнивает с эталонной.
        
        Returns:
            Tuple[List[str], List[str], List[str]]: Кортеж из трех списков:
                1. Список недостающих директорий
                2. Список лишних директорий
                3. Список директорий, которые нужно переместить
        """
        missing_dirs = []
        extra_dirs = []
        move_candidates = []
        
        # Проверяем все директории в эталонной структуре
        for dir_path, dir_contents in self._walk_reference_structure(self.reference_structure):
            full_path = os.path.join(self.root_dir, dir_path)
            if not os.path.exists(full_path):
                missing_dirs.append(dir_path)
        
        # Проверяем текущие директории в корне
        for item in os.listdir(self.root_dir):
            if item in EXCLUSIONS:
                continue
            
            item_path = os.path.join(self.root_dir, item)
            rel_path = os.path.relpath(item_path, self.root_dir)
            
            # Проверяем, является ли директория частью эталонной структуры
            is_in_reference = False
            for dir_path, _ in self._walk_reference_structure(self.reference_structure):
                if dir_path == rel_path or dir_path.startswith(rel_path + os.sep):
                    is_in_reference = True
                    break
            
            if not is_in_reference:
                if os.path.isdir(item_path):
                    # Проверяем, возможно это директория, которую нужно переместить
                    potential_move = self._find_move_destination(item)
                    if potential_move:
                        move_candidates.append((item, potential_move))
                    else:
                        extra_dirs.append(item)
        
        return missing_dirs, extra_dirs, move_candidates
    
    def _walk_reference_structure(self, structure: Dict[str, Any], 
                                  base_path: str = "") -> List[Tuple[str, Dict[str, Any]]]:
        """
        Рекурсивно обходит эталонную структуру директорий.
        
        Args:
            structure: Словарь со структурой директорий
            base_path: Базовый путь для текущего уровня рекурсии
            
        Returns:
            List[Tuple[str, Dict[str, Any]]]: Список кортежей (путь, содержимое)
        """
        result = []
        
        for name, contents in structure.items():
            current_path = os.path.join(base_path, name) if base_path else name
            result.append((current_path, contents))
            
            if isinstance(contents, dict):
                result.extend(self._walk_reference_structure(contents, current_path))
        
        return result
    
    def _find_move_destination(self, directory: str) -> Optional[str]:
        """
        Ищет потенциальное место назначения для перемещения директории.
        
        Args:
            directory: Имя директории для проверки
            
        Returns:
            Optional[str]: Путь назначения или None
        """
        # Словарь соответствий для типичных директорий
        move_map = {
            "cache": "advising_platform/src/cache",
            "data": "advising_platform/src/cache/data",
            "locks": "advising_platform/src/cache/locks",
            "api": "advising_platform/src/api",
            "web": "advising_platform/src/web",
            "core": "advising_platform/src/core",
            "templates": "advising_platform/src/web/templates",
            "static": "advising_platform/src/web/static"
        }
        
        return move_map.get(directory)
    
    def create_missing_directories(self) -> List[str]:
        """
        Создает недостающие директории из эталонной структуры.
        
        Returns:
            List[str]: Список созданных директорий
        """
        missing_dirs, _, _ = self.analyze_structure()
        created_dirs = []
        
        for dir_path in missing_dirs:
            full_path = os.path.join(self.root_dir, dir_path)
            
            if self.dry_run:
                logger.info(f"[DRY RUN] Создали бы директорию: {full_path}")
                created_dirs.append(dir_path)
            else:
                try:
                    os.makedirs(full_path, exist_ok=True)
                    logger.info(f"Создана директория: {full_path}")
                    created_dirs.append(dir_path)
                except Exception as e:
                    logger.error(f"Ошибка при создании директории {full_path}: {str(e)}")
        
        return created_dirs
    
    def cleanup_extra_directories(self) -> List[str]:
        """
        Удаляет или архивирует лишние директории.
        
        Returns:
            List[str]: Список обработанных директорий
        """
        _, extra_dirs, _ = self.analyze_structure()
        processed_dirs = []
        
        for dir_name in extra_dirs:
            dir_path = os.path.join(self.root_dir, dir_name)
            
            if not os.path.exists(dir_path):
                continue
            
            # Запрашиваем подтверждение, если включен интерактивный режим
            if self.interactive:
                response = input(f"Удалить директорию '{dir_name}'? (y/n/b - удалить/нет/в архив): ")
                if response.lower() not in ['y', 'b']:
                    logger.info(f"Пропущена директория: {dir_path}")
                    continue
                
                # Если выбрано архивирование
                if response.lower() == 'b':
                    self._backup_item(dir_path)
                    continue
            
            if self.dry_run:
                logger.info(f"[DRY RUN] Удалили бы директорию: {dir_path}")
            else:
                if self.backup:
                    self._backup_item(dir_path)
                
                try:
                    if os.path.isdir(dir_path):
                        shutil.rmtree(dir_path)
                    else:
                        os.remove(dir_path)
                    logger.info(f"Удалена директория: {dir_path}")
                except Exception as e:
                    logger.error(f"Ошибка при удалении {dir_path}: {str(e)}")
                    continue
            
            processed_dirs.append(dir_name)
        
        return processed_dirs
    
    def move_directories(self) -> List[Tuple[str, str]]:
        """
        Перемещает директории в соответствующие места согласно эталонной структуре.
        
        Returns:
            List[Tuple[str, str]]: Список кортежей (исходный путь, путь назначения)
        """
        _, _, move_candidates = self.analyze_structure()
        moved_dirs = []
        
        for source, destination in move_candidates:
            source_path = os.path.join(self.root_dir, source)
            dest_path = os.path.join(self.root_dir, destination)
            
            # Запрашиваем подтверждение, если включен интерактивный режим
            if self.interactive:
                response = input(f"Переместить '{source}' в '{destination}'? (y/n): ")
                if response.lower() != 'y':
                    logger.info(f"Пропущено перемещение: {source} -> {destination}")
                    continue
            
            if self.dry_run:
                logger.info(f"[DRY RUN] Переместили бы: {source_path} -> {dest_path}")
            else:
                # Создаем директорию назначения, если она не существует
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                
                try:
                    # Если директория назначения уже существует, объединяем содержимое
                    if os.path.exists(dest_path):
                        logger.info(f"Объединение директорий: {source_path} -> {dest_path}")
                        self._merge_directories(source_path, dest_path)
                    else:
                        # Просто перемещаем
                        shutil.move(source_path, dest_path)
                        logger.info(f"Перемещено: {source_path} -> {dest_path}")
                except Exception as e:
                    logger.error(f"Ошибка при перемещении {source_path} -> {dest_path}: {str(e)}")
                    continue
            
            moved_dirs.append((source, destination))
        
        return moved_dirs
    
    def _merge_directories(self, source_dir: str, dest_dir: str) -> None:
        """
        Объединяет содержимое двух директорий.
        
        Args:
            source_dir: Исходная директория
            dest_dir: Директория назначения
        """
        for item in os.listdir(source_dir):
            source_item = os.path.join(source_dir, item)
            dest_item = os.path.join(dest_dir, item)
            
            if os.path.isdir(source_item):
                if os.path.exists(dest_item):
                    # Рекурсивно объединяем поддиректории
                    self._merge_directories(source_item, dest_item)
                else:
                    # Если директория назначения не существует, просто перемещаем
                    shutil.move(source_item, dest_item)
            else:
                # Для файлов проверяем, существует ли файл в назначении
                if os.path.exists(dest_item):
                    # Если файл существует, создаем резервную копию перед перезаписью
                    if self.backup:
                        backup_path = os.path.join(self.backup_dir, os.path.relpath(dest_item, self.root_dir))
                        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                        shutil.copy2(dest_item, backup_path)
                
                # Перемещаем файл
                shutil.move(source_item, dest_item)
        
        # Удаляем исходную директорию, если она пуста
        if not os.listdir(source_dir):
            os.rmdir(source_dir)
    
    def _backup_item(self, item_path: str) -> None:
        """
        Создает резервную копию файла или директории.
        
        Args:
            item_path: Путь к файлу или директории
        """
        if not self.backup:
            return
        
        try:
            rel_path = os.path.relpath(item_path, self.root_dir)
            backup_path = os.path.join(self.backup_dir, rel_path)
            
            # Создаем директорию для резервной копии
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            if os.path.isdir(item_path):
                if os.path.exists(backup_path):
                    shutil.rmtree(backup_path)
                shutil.copytree(item_path, backup_path)
            else:
                shutil.copy2(item_path, backup_path)
            
            logger.info(f"Создана резервная копия: {item_path} -> {backup_path}")
        except Exception as e:
            logger.error(f"Ошибка при создании резервной копии {item_path}: {str(e)}")
    
    def cleanup_temp_files(self) -> int:
        """
        Удаляет временные файлы из проекта (*.pyc, __pycache__ и т.д.).
        
        Returns:
            int: Количество удаленных файлов и директорий
        """
        removed_count = 0
        
        for root, dirs, files in os.walk(self.root_dir):
            # Пропускаем исключения
            dirs[:] = [d for d in dirs if d not in EXCLUSIONS]
            
            # Удаляем временные директории
            for dir_name in dirs[:]:
                if any(dir_name == pattern for pattern in TEMP_FILES_PATTERNS):
                    dir_path = os.path.join(root, dir_name)
                    
                    if self.dry_run:
                        logger.info(f"[DRY RUN] Удалили бы временную директорию: {dir_path}")
                    else:
                        try:
                            shutil.rmtree(dir_path)
                            logger.info(f"Удалена временная директория: {dir_path}")
                            dirs.remove(dir_name)  # Удаляем из списка, чтобы не обрабатывать рекурсивно
                            removed_count += 1
                        except Exception as e:
                            logger.error(f"Ошибка при удалении директории {dir_path}: {str(e)}")
            
            # Удаляем временные файлы
            for file_name in files:
                if any(file_name.endswith(pattern.replace('*', '')) for pattern in TEMP_FILES_PATTERNS if '*' in pattern):
                    file_path = os.path.join(root, file_name)
                    
                    if self.dry_run:
                        logger.info(f"[DRY RUN] Удалили бы временный файл: {file_path}")
                    else:
                        try:
                            os.remove(file_path)
                            logger.info(f"Удален временный файл: {file_path}")
                            removed_count += 1
                        except Exception as e:
                            logger.error(f"Ошибка при удалении файла {file_path}: {str(e)}")
        
        return removed_count
    
    def show_structure_mismatch(self) -> Dict[str, Any]:
        """
        Выводит информацию о несоответствиях между текущей и эталонной структурой.
        
        Returns:
            Dict[str, Any]: Словарь с информацией о несоответствиях
        """
        missing_dirs, extra_dirs, move_candidates = self.analyze_structure()
        
        result = {
            "missing_directories": missing_dirs,
            "extra_directories": extra_dirs,
            "move_candidates": [{"source": s, "destination": d} for s, d in move_candidates]
        }
        
        logger.info("Анализ структуры проекта:")
        logger.info(f"Недостающие директории: {len(missing_dirs)}")
        for d in missing_dirs:
            logger.info(f"  - {d}")
        
        logger.info(f"Лишние директории: {len(extra_dirs)}")
        for d in extra_dirs:
            logger.info(f"  - {d}")
        
        logger.info(f"Директории для перемещения: {len(move_candidates)}")
        for s, d in move_candidates:
            logger.info(f"  - {s} -> {d}")
        
        return result


def get_args():
    """Парсинг аргументов командной строки."""
    parser = argparse.ArgumentParser(description='Очистка директорий проекта')
    parser.add_argument('--dry-run', action='store_true', help='Симуляция без реального удаления')
    parser.add_argument('--no-backup', action='store_true', help='Не создавать резервные копии')
    parser.add_argument('--no-interactive', action='store_true', help='Не запрашивать подтверждение')
    parser.add_argument('--cleanup-temp', action='store_true', help='Удалить временные файлы')
    parser.add_argument('--create-missing', action='store_true', help='Создать недостающие директории')
    parser.add_argument('--move-dirs', action='store_true', help='Переместить директории')
    parser.add_argument('--cleanup-extra', action='store_true', help='Удалить лишние директории')
    parser.add_argument('--all', action='store_true', help='Выполнить все операции')
    parser.add_argument('--root-dir', default='.', help='Корневая директория проекта')
    return parser.parse_args()


def main():
    """Основная функция скрипта."""
    args = get_args()
    
    cleaner = DirectoryCleaner(
        root_dir=args.root_dir,
        reference_structure=REFERENCE_STRUCTURE,
        dry_run=args.dry_run,
        backup=not args.no_backup,
        interactive=not args.no_interactive
    )
    
    # Показываем анализ структуры
    cleaner.show_structure_mismatch()
    
    # Определяем операции для выполнения
    operations = []
    if args.all or args.create_missing:
        operations.append(('create_missing', 'Создание недостающих директорий', cleaner.create_missing_directories))
    if args.all or args.move_dirs:
        operations.append(('move_dirs', 'Перемещение директорий', cleaner.move_directories))
    if args.all or args.cleanup_extra:
        operations.append(('cleanup_extra', 'Удаление лишних директорий', cleaner.cleanup_extra_directories))
    if args.all or args.cleanup_temp:
        operations.append(('cleanup_temp', 'Удаление временных файлов', cleaner.cleanup_temp_files))
    
    # Если не указаны операции, просто показываем анализ
    if not operations:
        logger.info("Не указаны операции для выполнения. Используйте --all или конкретные флаги.")
        return
    
    # Выполняем операции
    results = {}
    for op_name, op_desc, op_func in operations:
        logger.info(f"Выполнение операции: {op_desc}")
        result = op_func()
        results[op_name] = result
        if isinstance(result, list):
            logger.info(f"Результат: обработано {len(result)} элементов")
        elif isinstance(result, int):
            logger.info(f"Результат: обработано {result} элементов")
    
    # Выводим итоговую информацию
    logger.info(f"Очистка директорий {'(симуляция)' if args.dry_run else ''} завершена")
    if args.dry_run:
        logger.info("Для реального выполнения операций запустите скрипт без флага --dry-run")


if __name__ == "__main__":
    main()