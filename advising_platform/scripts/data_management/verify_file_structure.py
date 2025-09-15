#!/usr/bin/env python3
"""
Скрипт для проверки структуры файлов и директорий проекта.

Скрипт сравнивает текущую структуру файлов с ожидаемой согласно стандарту
и выдает отчет о несоответствиях.
"""

import os
import sys
import argparse
import json
from pathlib import Path
import logging
from datetime import datetime
from typing import Dict, List, Set, Tuple, Any, Optional

# Настройка логирования
# Создаем директории для логов, если они не существуют
log_dir = os.path.join('data', 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(log_dir, 'file_structure_verification.log'))
    ]
)
logger = logging.getLogger(__name__)

# Определение ожидаемой структуры файлов
# Структура: {директория: {поддиректория: [список обязательных файлов/папок]}}
EXPECTED_STRUCTURE = {
    'advising_platform': {
        'config': [],
        'data': {
            'logs': [],
            'json': [],
            'test_results': []
        },
        'docs': [],
        'scripts': {
            'data_management': [],
            'incidents': [],
            'tests': []
        },
        'src': {
            'api': [],
            'sync': [],
            'web': [],
            'utils': [],
            'core': [],
            'tools': [],
            'cli': []
        },
        'tests': []
    }
}

# Директории, которые могут оставаться в корне проекта
ALLOWED_ROOT_DIRS = [
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
    'advising_platform'
]

# Файлы, которые могут оставаться в корне проекта
ALLOWED_ROOT_FILES = [
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

# Директории, которые должны быть перемещены из корня в advising_platform
DIRS_TO_MOVE = [
    'data',
    'doc_changes',
    'docs',
    'examples',
    'git_logs',
    'hooks',
    'scripts',
    'server',
    'templates',
    'tests'
]

# Файлы, которые должны быть перемещены или иметь редиректы
FILES_TO_MOVE = [
    'process_incidents.py',
    'test_bidirectional_sync.py'
]


def scan_directory(directory: str) -> Dict[str, List[str]]:
    """
    Сканирует директорию и возвращает словарь с поддиректориями и файлами.
    
    Args:
        directory: Путь к директории для сканирования
        
    Returns:
        Словарь, где ключи - поддиректории, значения - списки файлов
    """
    structure = {}
    
    try:
        for item in os.listdir(directory):
            if item.startswith('.') and item != '.git':
                continue
                
            item_path = os.path.join(directory, item)
            
            if os.path.isdir(item_path):
                structure[item] = scan_directory(item_path)
            else:
                if '_files' not in structure:
                    structure['_files'] = []
                structure['_files'].append(item)
    except FileNotFoundError:
        logger.warning(f"Директория {directory} не найдена")
    except PermissionError:
        logger.warning(f"Нет доступа к директории {directory}")
    
    return structure


def compare_with_expected(
    actual: Dict[str, Any], 
    expected: Dict[str, Any], 
    path: str = ""
) -> List[Dict[str, str]]:
    """
    Сравнивает фактическую структуру с ожидаемой и возвращает список несоответствий.
    
    Args:
        actual: Фактическая структура
        expected: Ожидаемая структура
        path: Текущий путь для формирования полного пути к файлам/директориям
        
    Returns:
        Список несоответствий с указанием пути и типа несоответствия
    """
    issues = []
    
    # Проверяем наличие ожидаемых директорий
    for directory, contents in expected.items():
        if directory != '_files':
            current_path = os.path.join(path, directory)
            
            if directory not in actual:
                issues.append({
                    'path': current_path,
                    'type': 'missing_directory',
                    'message': f"Отсутствует ожидаемая директория: {current_path}"
                })
            elif isinstance(contents, dict):
                # Рекурсивная проверка поддиректорий
                issues.extend(compare_with_expected(
                    actual.get(directory, {}),
                    contents,
                    current_path
                ))
    
    return issues


def check_root_directory() -> List[Dict[str, str]]:
    """
    Проверяет корневую директорию на наличие файлов и директорий,
    которые должны быть перемещены.
    
    Returns:
        Список файлов и директорий, которые нужно переместить
    """
    issues = []
    
    for item in os.listdir('.'):
        if os.path.isdir(item):
            if item in DIRS_TO_MOVE and item not in ALLOWED_ROOT_DIRS:
                issues.append({
                    'path': item,
                    'type': 'directory_to_move',
                    'message': f"Директория {item} должна быть перемещена в advising_platform/"
                })
        else:
            if item in FILES_TO_MOVE and item not in ALLOWED_ROOT_FILES:
                issues.append({
                    'path': item,
                    'type': 'file_to_move',
                    'message': f"Файл {item} должен быть перемещен или иметь редирект"
                })
    
    return issues


def generate_report(issues: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Генерирует отчет о проверке структуры файлов.
    
    Args:
        issues: Список обнаруженных проблем
        
    Returns:
        Словарь с отчетом
    """
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_issues': len(issues),
        'missing_directories': [],
        'directories_to_move': [],
        'files_to_move': [],
        'other_issues': []
    }
    
    for issue in issues:
        if issue['type'] == 'missing_directory':
            report['missing_directories'].append(issue)
        elif issue['type'] == 'directory_to_move':
            report['directories_to_move'].append(issue)
        elif issue['type'] == 'file_to_move':
            report['files_to_move'].append(issue)
        else:
            report['other_issues'].append(issue)
    
    return report


def save_report(report: Dict[str, Any], output_file: str) -> None:
    """
    Сохраняет отчет в JSON-файл.
    
    Args:
        report: Отчет для сохранения
        output_file: Путь к файлу для сохранения отчета
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        logger.info(f"Отчет сохранен в {output_file}")
    except Exception as e:
        logger.error(f"Ошибка при сохранении отчета: {e}")


def print_report_summary(report: Dict[str, Any]) -> None:
    """
    Выводит краткую сводку отчета в консоль.
    
    Args:
        report: Отчет для вывода
    """
    print("\n" + "="*50)
    print("ОТЧЕТ О ПРОВЕРКЕ СТРУКТУРЫ ФАЙЛОВ")
    print("="*50)
    print(f"Всего проблем: {report['total_issues']}")
    
    if report['missing_directories']:
        print("\nОтсутствующие директории:")
        for issue in report['missing_directories']:
            print(f"  - {issue['path']}")
    
    if report['directories_to_move']:
        print("\nДиректории для перемещения:")
        for issue in report['directories_to_move']:
            print(f"  - {issue['path']}")
    
    if report['files_to_move']:
        print("\nФайлы для перемещения:")
        for issue in report['files_to_move']:
            print(f"  - {issue['path']}")
    
    print("="*50)


def suggest_fixes(report: Dict[str, Any]) -> None:
    """
    Предлагает команды для исправления проблем.
    
    Args:
        report: Отчет с проблемами
    """
    if not any([
        report['missing_directories'],
        report['directories_to_move'],
        report['files_to_move']
    ]):
        print("\nНе обнаружено проблем, требующих исправления.")
        return
    
    print("\n" + "="*50)
    print("ПРЕДЛАГАЕМЫЕ ИСПРАВЛЕНИЯ")
    print("="*50)
    
    # Создание отсутствующих директорий
    if report['missing_directories']:
        print("\n# Создание отсутствующих директорий:")
        for issue in report['missing_directories']:
            print(f"mkdir -p {issue['path']}")
    
    # Перемещение директорий
    if report['directories_to_move']:
        print("\n# Перемещение директорий:")
        for issue in report['directories_to_move']:
            dest_path = os.path.join('advising_platform', issue['path'])
            print(f"# Перемещение {issue['path']} в advising_platform/")
            print(f"mkdir -p $(dirname {dest_path})")
            print(f"mv {issue['path']} {dest_path}")
    
    # Перемещение файлов
    if report['files_to_move']:
        print("\n# Перемещение файлов:")
        for issue in report['files_to_move']:
            dest_dir = None
            
            # Определяем, в какую директорию перемещать файл
            if issue['path'] == 'process_incidents.py':
                dest_dir = 'advising_platform/scripts/incidents'
            elif issue['path'] == 'test_bidirectional_sync.py':
                dest_dir = 'advising_platform/scripts/tests'
            else:
                dest_dir = 'advising_platform'
            
            print(f"# Перемещение {issue['path']} в {dest_dir}/")
            print(f"mkdir -p {dest_dir}")
            print(f"mv {issue['path']} {dest_dir}/")
            
            # Создание файла-редиректа
            print(f"# Создание файла-редиректа для обратной совместимости")
            print(f"echo 'import sys\\nimport os\\n\\nprint(\"Перенаправление на {dest_dir}/{issue['path']}...\")\\n\\n"
                  f"# Добавляем путь к директории проекта в sys.path\\nsys.path.insert(0, os.path.abspath(\".\"))\\n\\n"
                  f"# Импортируем и запускаем модуль\\nfrom {dest_dir.replace('/', '.')} import {issue['path'].replace('.py', '')}\\n\\n"
                  f"if __name__ == \"__main__\":\\n    {issue['path'].replace('.py', '')}.main()' > {issue['path']}")
    
    print("="*50)


def main():
    """Основная функция скрипта."""
    parser = argparse.ArgumentParser(description='Проверка структуры файлов проекта')
    parser.add_argument('--output', '-o', default='data/json/file_structure_report.json',
                      help='Путь для сохранения отчета (по умолчанию: data/json/file_structure_report.json)')
    parser.add_argument('--fix', action='store_true',
                      help='Предложить команды для исправления проблем')
    parser.add_argument('--verbose', '-v', action='store_true',
                      help='Вывести подробный отчет')
    
    args = parser.parse_args()
    
    # Создаем директорию для отчета, если она не существует
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    logger.info("Начинаем проверку структуры файлов...")
    
    # Сканируем фактическую структуру
    logger.info("Сканирование фактической структуры...")
    actual_structure = {'advising_platform': scan_directory('advising_platform')}
    
    # Сравниваем с ожидаемой структурой
    logger.info("Сравнение с ожидаемой структурой...")
    issues = compare_with_expected(actual_structure, {'advising_platform': EXPECTED_STRUCTURE['advising_platform']})
    
    # Проверяем файлы и директории в корне проекта
    logger.info("Проверка файлов и директорий в корне проекта...")
    issues.extend(check_root_directory())
    
    # Генерируем отчет
    logger.info("Генерация отчета...")
    report = generate_report(issues)
    
    # Сохраняем отчет
    save_report(report, args.output)
    
    # Выводим краткую сводку
    print_report_summary(report)
    
    # Предлагаем исправления, если запрошено
    if args.fix:
        suggest_fixes(report)
    
    logger.info("Проверка завершена.")
    
    # Возвращаем количество проблем как код возврата
    return len(issues)


if __name__ == "__main__":
    sys.exit(main())