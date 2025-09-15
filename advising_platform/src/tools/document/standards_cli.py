#!/usr/bin/env python3
"""
Интерфейс командной строки для работы со стандартами.

Этот скрипт предоставляет командный интерфейс для:
1. Проверки стандартов на соответствие требованиям
2. Исправления метаданных в стандартах
3. Переименования файлов стандартов
4. Анализа пересечений между стандартами

Использование:
    python standards_cli.py validate [директория]
    python standards_cli.py fix [директория] [--no-backup]
    python standards_cli.py rename [директория] [--no-backup]
    python standards_cli.py analyze [директория] [--threshold THRESHOLD]
    python standards_cli.py clean [директория] - удаляет дубликаты стандартов

Автор: AI Assistant
Дата: 19 May 2025
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('standards_management.log')
    ]
)

logger = logging.getLogger('standards_cli')

# Импортируем функции из модуля standards_manager
from .standards_manager import (
    validate_standards,
    fix_standards_metadata,
    rename_standards,
    analyze_standards_overlap,
    STANDARDS_DIR
)


def setup_parser():
    """Настраивает парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description='Инструменты для работы со стандартами документации.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Создаем подпарсеры для разных команд
    subparsers = parser.add_subparsers(dest='command', help='Команда для выполнения')
    
    # Парсер для команды validate
    validate_parser = subparsers.add_parser('validate', help='Проверить стандарты на соответствие требованиям')
    validate_parser.add_argument('directory', nargs='?', default=None, help='Директория со стандартами')
    
    # Парсер для команды fix
    fix_parser = subparsers.add_parser('fix', help='Исправить метаданные в стандартах')
    fix_parser.add_argument('directory', nargs='?', default=None, help='Директория со стандартами')
    fix_parser.add_argument('--no-backup', action='store_true', help='Не создавать резервные копии')
    
    # Парсер для команды rename
    rename_parser = subparsers.add_parser('rename', help='Переименовать файлы стандартов')
    rename_parser.add_argument('directory', nargs='?', default=None, help='Директория со стандартами')
    rename_parser.add_argument('--no-backup', action='store_true', help='Не создавать резервные копии')
    
    # Парсер для команды analyze
    analyze_parser = subparsers.add_parser('analyze', help='Анализировать пересечения между стандартами')
    analyze_parser.add_argument('directory', nargs='?', default=None, help='Директория со стандартами')
    analyze_parser.add_argument('--threshold', type=float, default=0.3, help='Порог сходства (от 0 до 1)')
    
    return parser


def main():
    """Основная функция скрипта."""
    parser = setup_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        # Определяем директорию стандартов
        base_dir = args.directory if hasattr(args, 'directory') and args.directory else STANDARDS_DIR
        
        # Выводим информацию о выполняемой команде
        logger.info(f"Выполняется команда: {args.command}")
        logger.info(f"Директория стандартов: {base_dir}")
        
        # Выполняем нужную команду
        if args.command == 'validate':
            issues_count = validate_standards(base_dir)
            return 1 if issues_count > 0 else 0
            
        elif args.command == 'fix':
            create_backups = not args.no_backup
            files_fixed = fix_standards_metadata(base_dir, create_backups)
            logger.info(f"Исправлено файлов: {files_fixed}")
            return 0
            
        elif args.command == 'rename':
            create_backups = not args.no_backup
            files_renamed = rename_standards(base_dir, create_backups)
            logger.info(f"Переименовано файлов: {files_renamed}")
            return 0
            
        elif args.command == 'analyze':
            threshold = args.threshold
            similar_pairs = analyze_standards_overlap(base_dir, threshold)
            
            # Выводим результаты
            if similar_pairs:
                logger.info(f"Найдены пересечения между стандартами (порог: {threshold}):")
                for i, pair in enumerate(similar_pairs[:10], 1):
                    logger.info(f"{i}. {pair['standard1']} <-> {pair['standard2']}: {pair['similarity']:.2f}")
            else:
                logger.info(f"Не найдено пересечений между стандартами с порогом сходства >= {threshold}")
                
            return 0
        
    except Exception as e:
        logger.error(f"Ошибка выполнения команды: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())