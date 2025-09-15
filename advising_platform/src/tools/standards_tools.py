#!/usr/bin/env python3
"""
Клиентский скрипт для работы со стандартами.

Предоставляет простой интерфейс для управления стандартами документации:
1. Проверка стандартов на соответствие требованиям
2. Исправление метаданных в стандартах
3. Переименование файлов стандартов
4. Анализ пересечений между стандартами

Использование:
    python standards_tools.py validate [директория]
    python standards_tools.py fix [директория] [--no-backup]
    python standards_tools.py rename [директория] [--no-backup]
    python standards_tools.py analyze [директория] [--threshold THRESHOLD]

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

logger = logging.getLogger('standards_tools')

# Добавляем директорию проекта в путь импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем функции для работы со стандартами
from advising_platform.src.tools.document.standards_manager import (
    validate_standards,
    fix_standards_metadata,
    rename_standards,
    analyze_standards_overlap
)

# Путь к директории стандартов
STANDARDS_DIR = Path(__file__).parent / "[standards .md]"


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
        logger.info(f"Директория стандартов: {base_dir}")
        
        # Выполняем нужную команду
        if args.command == 'validate':
            logger.info("Проверка стандартов на соответствие требованиям...")
            issues_count = validate_standards(base_dir)
            if issues_count == 0:
                logger.info("Проверка успешно завершена. Все стандарты соответствуют требованиям.")
            else:
                logger.warning(f"Проверка завершена. Найдено {issues_count} проблем.")
            return 1 if issues_count > 0 else 0
            
        elif args.command == 'fix':
            logger.info("Исправление метаданных в стандартах...")
            create_backups = not args.no_backup
            files_fixed = fix_standards_metadata(base_dir, create_backups)
            logger.info(f"Исправление завершено. Исправлено файлов: {files_fixed}")
            return 0
            
        elif args.command == 'rename':
            logger.info("Переименование файлов стандартов...")
            create_backups = not args.no_backup
            files_renamed = rename_standards(base_dir, create_backups)
            logger.info(f"Переименование завершено. Переименовано файлов: {files_renamed}")
            return 0
            
        elif args.command == 'analyze':
            threshold = args.threshold
            logger.info(f"Анализ пересечений между стандартами (порог: {threshold})...")
            similar_pairs = analyze_standards_overlap(base_dir, threshold)
            
            # Выводим результаты
            if similar_pairs:
                logger.info(f"Анализ завершен. Найдено {len(similar_pairs)} пар стандартов с сходством >= {threshold}:")
                for i, pair in enumerate(similar_pairs[:10], 1):
                    logger.info(f"{i}. {pair['standard1']} <-> {pair['standard2']}: {pair['similarity']:.2f}")
            else:
                logger.info(f"Анализ завершен. Не найдено пересечений между стандартами с порогом сходства >= {threshold}")
                
            return 0
        
    except Exception as e:
        logger.error(f"Ошибка выполнения команды: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())