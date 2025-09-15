#!/usr/bin/env python3
"""
Скрипт для удаления дублирующихся файлов из корневой директории.
Файлы удаляются только если они имеют копии в структуре проекта advising_platform.

Скрипт соответствует стандарту организации кодовой базы и
критериям порядка в процессах разработки.
"""

import os
import sys
import shutil
import argparse
import filecmp
from pathlib import Path

# Определение пути к корневой директории проекта
ROOT_DIR = Path(__file__).parent.parent.parent
PROJECT_DIR = Path(__file__).parent.parent

def find_duplicate_files():
    """
    Находит дублирующиеся файлы между корневой директорией и структурой проекта.
    
    Returns:
        list: Список кортежей (путь_к_файлу_в_корне, путь_к_файлу_в_проекте)
    """
    print("Поиск дублирующихся файлов...")
    
    duplicates = []
    
    # Рекурсивно ищем файлы в структуре проекта
    for root, dirs, files in os.walk(PROJECT_DIR):
        root_path = Path(root)
        
        for file in files:
            # Путь к файлу в структуре проекта
            file_path = root_path / file
            
            # Путь к потенциальному дубликату в корне
            root_file_path = ROOT_DIR / file
            
            # Проверяем, существует ли файл в корне
            if root_file_path.exists() and root_file_path.is_file():
                try:
                    # Проверяем, что содержимое файлов идентично
                    if filecmp.cmp(file_path, root_file_path, shallow=False):
                        duplicates.append((root_file_path, file_path))
                except Exception as e:
                    print(f"Ошибка при сравнении {file_path} и {root_file_path}: {e}")
    
    return duplicates

def remove_duplicates(duplicates, dry_run=True):
    """
    Удаляет дублирующиеся файлы из корневой директории.
    
    Args:
        duplicates (list): Список кортежей (путь_к_файлу_в_корне, путь_к_файлу_в_проекте)
        dry_run (bool): Если True, только показывает, что будет удалено, без фактического удаления
    
    Returns:
        int: Количество удаленных файлов
    """
    if dry_run:
        print("\nСПИСОК ФАЙЛОВ ДЛЯ УДАЛЕНИЯ (dry run):")
    else:
        print("\nУДАЛЕНИЕ ФАЙЛОВ:")
    
    removed_count = 0
    
    for root_file, project_file in duplicates:
        if dry_run:
            print(f"  БУДЕТ УДАЛЕН: {root_file}")
        else:
            try:
                os.remove(root_file)
                print(f"  УДАЛЕН: {root_file}")
                removed_count += 1
            except Exception as e:
                print(f"  ОШИБКА при удалении {root_file}: {e}")
    
    return removed_count

def verify_removal(duplicates):
    """
    Проверяет, что файлы действительно были удалены.
    
    Args:
        duplicates (list): Список кортежей (путь_к_файлу_в_корне, путь_к_файлу_в_проекте)
    
    Returns:
        bool: True, если все файлы были успешно удалены
    """
    print("\nПРОВЕРКА УДАЛЕНИЯ:")
    
    all_removed = True
    
    for root_file, _ in duplicates:
        if root_file.exists():
            print(f"  НЕ УДАЛЕН: {root_file}")
            all_removed = False
        else:
            print(f"  ПОДТВЕРЖДЕНО: {root_file}")
    
    return all_removed

def check_remaining_files():
    """
    Проверяет, остались ли еще файлы в корневой директории.
    
    Returns:
        list: Список оставшихся файлов в корневой директории
    """
    print("\nОСТАВШИЕСЯ ФАЙЛЫ В КОРНЕВОЙ ДИРЕКТОРИИ:")
    
    remaining_files = []
    
    for item in ROOT_DIR.iterdir():
        if item.is_file() and not item.name.startswith('.'):
            remaining_files.append(item)
            print(f"  {item}")
    
    dirs = []
    for item in ROOT_DIR.iterdir():
        if item.is_dir() and not item.name.startswith('.') and not str(item).startswith(str(PROJECT_DIR)):
            dirs.append(item)
    
    if dirs:
        print("\nОСТАВШИЕСЯ ДИРЕКТОРИИ В КОРНЕ:")
        for dir_path in dirs:
            print(f"  {dir_path}")
    
    return remaining_files

def parse_arguments():
    """
    Обрабатывает аргументы командной строки.
    
    Returns:
        argparse.Namespace: Объект с аргументами командной строки
    """
    parser = argparse.ArgumentParser(
        description='Скрипт для удаления дублирующихся файлов',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Только показать, что будет удалено, без фактического удаления'
    )
    
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Проверить после удаления, что файлы были успешно удалены'
    )
    
    parser.add_argument(
        '--check-remaining',
        action='store_true',
        help='Показать оставшиеся файлы в корневой директории после удаления'
    )
    
    return parser.parse_args()

def main():
    """
    Основная функция скрипта.
    
    Returns:
        int: Код завершения (0 - успех, 1 - ошибка)
    """
    args = parse_arguments()
    
    # Проверка существования директорий
    if not ROOT_DIR.exists():
        print(f"Ошибка: корневая директория {ROOT_DIR} не найдена")
        return 1
    
    if not PROJECT_DIR.exists():
        print(f"Ошибка: директория проекта {PROJECT_DIR} не найдена")
        return 1
    
    # Поиск дублирующихся файлов
    duplicates = find_duplicate_files()
    
    if not duplicates:
        print("Дублирующиеся файлы не найдены")
        return 0
    
    print(f"\nНайдено {len(duplicates)} дублирующихся файлов")
    
    # Удаление дублирующихся файлов
    removed_count = remove_duplicates(duplicates, dry_run=args.dry_run)
    
    if args.dry_run:
        print(f"\nВ режиме dry run: было бы удалено {len(duplicates)} файлов")
        print("Для фактического удаления запустите скрипт без флага --dry-run")
    else:
        print(f"\nУдалено {removed_count} из {len(duplicates)} файлов")
    
    # Проверка удаления
    if args.verify and not args.dry_run:
        all_removed = verify_removal(duplicates)
        if not all_removed:
            print("\nВНИМАНИЕ: Некоторые файлы не были удалены!")
    
    # Проверка оставшихся файлов
    if args.check_remaining:
        remaining_files = check_remaining_files()
        print(f"\nВсего осталось {len(remaining_files)} файлов в корневой директории")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())