#!/usr/bin/env python3
"""
Скрипт для анализа и рефакторинга кодовой базы.

Выполняет следующие задачи:
1. Анализ структуры кода и поиск возможностей для улучшения
2. Выявление дублирующейся функциональности
3. Проверку стилей кодирования и форматирования
4. Улучшение документации и комментариев

Автор: AI Assistant
Дата: 20 мая 2025
"""

import os
import re
import sys
import ast
import logging
import argparse
from pathlib import Path
from collections import defaultdict, Counter

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger('codebase_refactor')

# Паттерны для поиска проблем
DEAD_CODE_PATTERNS = [
    r'if\s+False:',
    r'if\s+0:',
    r'if\s+\[\]:',
    r'if\s+"":',
    r'if\s+None:',
    r'while\s+False:',
    r'while\s+0:',
    r'#\s*TODO',
    r'#\s*FIXME',
]

# Игнорируемые директории
IGNORED_DIRS = [
    '.git',
    '__pycache__',
    '.venv',
    'venv',
    'node_modules',
    '.checkpoint_backup',
]

class CodeAnalyzer:
    """Анализатор кодовой базы."""
    
    def __init__(self, base_dir='.', ignored_dirs=None, python_only=True):
        """
        Инициализация анализатора.
        
        Args:
            base_dir: Базовая директория для анализа
            ignored_dirs: Список игнорируемых директорий
            python_only: Анализ только Python-файлов
        """
        self.base_dir = Path(base_dir)
        self.ignored_dirs = ignored_dirs or IGNORED_DIRS
        self.python_only = python_only
        self.python_files = []
        self.all_files = []
        self.issues = defaultdict(list)
        self.statistics = {
            'total_files': 0,
            'python_files': 0,
            'lines_of_code': 0,
            'functions': 0,
            'classes': 0,
            'modules': 0,
            'imports': Counter(),
            'issues': Counter(),
        }
    
    def scan_files(self):
        """
        Сканирует файлы в указанной директории.
        
        Returns:
            Количество найденных файлов
        """
        logger.info(f"Сканирование файлов в {self.base_dir}...")
        
        for path in self.base_dir.rglob('*'):
            # Пропускаем игнорируемые директории
            if any(ignored in str(path) for ignored in self.ignored_dirs):
                continue
            
            if path.is_file():
                self.all_files.append(path)
                
                if path.suffix == '.py':
                    self.python_files.append(path)
        
        self.statistics['total_files'] = len(self.all_files)
        self.statistics['python_files'] = len(self.python_files)
        
        logger.info(f"Найдено {self.statistics['total_files']} файлов, из них {self.statistics['python_files']} Python-файлов")
        return len(self.all_files)
    
    def analyze_python_files(self):
        """
        Анализирует Python-файлы.
        
        Returns:
            Словарь с результатами анализа
        """
        logger.info("Анализ Python-файлов...")
        
        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Подсчет строк кода
                lines = content.splitlines()
                self.statistics['lines_of_code'] += len(lines)
                
                # Анализ структуры кода с помощью ast
                try:
                    tree = ast.parse(content)
                    self._analyze_ast(tree, file_path)
                except SyntaxError as e:
                    self.issues['syntax_errors'].append((file_path, f"Синтаксическая ошибка: {e}"))
                    self.statistics['issues']['syntax_errors'] += 1
                
                # Поиск проблемных паттернов
                self._find_code_issues(content, file_path)
                
            except Exception as e:
                logger.error(f"Ошибка при анализе файла {file_path}: {e}")
                self.issues['parsing_errors'].append((file_path, str(e)))
                self.statistics['issues']['parsing_errors'] += 1
        
        return self.statistics
    
    def _analyze_ast(self, tree, file_path):
        """
        Анализирует AST Python-кода.
        
        Args:
            tree: AST-дерево кода
            file_path: Путь к анализируемому файлу
        """
        # Анализ импортов
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append(name.name)
                    self.statistics['imports'][name.name] += 1
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_name = node.module
                    for name in node.names:
                        full_name = f"{module_name}.{name.name}"
                        imports.append(full_name)
                        self.statistics['imports'][full_name] += 1
        
        # Анализ функций и классов
        functions = []
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
                self.statistics['functions'] += 1
                
                # Проверка документации
                if not ast.get_docstring(node):
                    self.issues['missing_docstrings'].append((file_path, f"Функция {node.name} без документации"))
                    self.statistics['issues']['missing_docstrings'] += 1
            
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
                self.statistics['classes'] += 1
                
                # Проверка документации
                if not ast.get_docstring(node):
                    self.issues['missing_docstrings'].append((file_path, f"Класс {node.name} без документации"))
                    self.statistics['issues']['missing_docstrings'] += 1
        
        self.statistics['modules'] += 1
    
    def _find_code_issues(self, content, file_path):
        """
        Ищет проблемы в коде.
        
        Args:
            content: Содержимое файла
            file_path: Путь к файлу
        """
        # Поиск мертвого кода
        for pattern in DEAD_CODE_PATTERNS:
            for match in re.finditer(pattern, content):
                line_number = content[:match.start()].count('\n') + 1
                issue = f"Строка {line_number}: {match.group()}"
                self.issues['dead_code'].append((file_path, issue))
                self.statistics['issues']['dead_code'] += 1
        
        # Поиск длинных строк
        for i, line in enumerate(content.splitlines(), 1):
            if len(line) > 100:
                self.issues['long_lines'].append((file_path, f"Строка {i}: длина {len(line)} символов"))
                self.statistics['issues']['long_lines'] += 1
    
    def find_duplicate_code(self, min_lines=3, threshold=0.8):
        """
        Находит дублирующийся код.
        
        Args:
            min_lines: Минимальное количество строк для поиска дубликатов
            threshold: Порог схожести
            
        Returns:
            Список найденных дубликатов
        """
        from difflib import SequenceMatcher
        
        logger.info("Поиск дублирующегося кода...")
        
        duplicates = []
        file_contents = {}
        
        # Загружаем содержимое файлов
        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                file_contents[file_path] = content.splitlines()
            except Exception as e:
                logger.error(f"Ошибка при чтении файла {file_path}: {e}")
        
        # Сравниваем файлы попарно
        processed_pairs = set()
        for file1 in self.python_files:
            for file2 in self.python_files:
                if file1 == file2 or (file1, file2) in processed_pairs or (file2, file1) in processed_pairs:
                    continue
                
                processed_pairs.add((file1, file2))
                
                lines1 = file_contents.get(file1, [])
                lines2 = file_contents.get(file2, [])
                
                # Пропускаем пустые файлы
                if not lines1 or not lines2:
                    continue
                
                # Сравниваем блоки строк
                for i in range(len(lines1) - min_lines + 1):
                    block1 = '\n'.join(lines1[i:i+min_lines])
                    
                    for j in range(len(lines2) - min_lines + 1):
                        block2 = '\n'.join(lines2[j:j+min_lines])
                        
                        similarity = SequenceMatcher(None, block1, block2).ratio()
                        
                        if similarity >= threshold:
                            duplicates.append({
                                'file1': file1,
                                'file2': file2,
                                'line1': i + 1,
                                'line2': j + 1,
                                'lines': min_lines,
                                'similarity': similarity,
                            })
        
        self.statistics['duplicates'] = len(duplicates)
        logger.info(f"Найдено {len(duplicates)} потенциальных дубликатов кода")
        
        return duplicates
    
    def generate_report(self, output_file=None):
        """
        Генерирует отчет о результатах анализа.
        
        Args:
            output_file: Путь к файлу для сохранения отчета
            
        Returns:
            Текст отчета
        """
        logger.info("Генерация отчета...")
        
        report = []
        report.append("=" * 80)
        report.append("ОТЧЕТ ОБ АНАЛИЗЕ КОДОВОЙ БАЗЫ")
        report.append("=" * 80)
        report.append("")
        
        report.append("ОБЩАЯ СТАТИСТИКА:")
        report.append(f"Всего файлов: {self.statistics['total_files']}")
        report.append(f"Python-файлов: {self.statistics['python_files']}")
        report.append(f"Строк кода: {self.statistics['lines_of_code']}")
        report.append(f"Функций: {self.statistics['functions']}")
        report.append(f"Классов: {self.statistics['classes']}")
        report.append(f"Модулей: {self.statistics['modules']}")
        report.append("")
        
        report.append("ПОПУЛЯРНЫЕ ИМПОРТЫ:")
        for module, count in self.statistics['imports'].most_common(10):
            report.append(f"  {module}: {count}")
        report.append("")
        
        report.append("ПРОБЛЕМЫ В КОДЕ:")
        for issue_type, count in self.statistics['issues'].items():
            report.append(f"  {issue_type}: {count}")
        report.append("")
        
        if 'duplicates' in self.statistics:
            report.append(f"ДУБЛИРУЮЩИЙСЯ КОД: {self.statistics['duplicates']} потенциальных дубликатов")
            report.append("")
        
        report.append("ДЕТАЛИ ПРОБЛЕМ:")
        for issue_type, issues in self.issues.items():
            report.append(f"\n{issue_type.upper()} ({len(issues)}):")
            for file_path, issue in issues[:10]:  # Ограничиваем количество выводимых проблем
                report.append(f"  {file_path}: {issue}")
            if len(issues) > 10:
                report.append(f"  ... и еще {len(issues) - 10} проблем")
        
        report_text = '\n'.join(report)
        
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report_text)
                logger.info(f"Отчет сохранен в {output_file}")
            except Exception as e:
                logger.error(f"Ошибка при сохранении отчета: {e}")
        
        return report_text
    
    def suggest_refactoring(self, output_file=None):
        """
        Формирует рекомендации по рефакторингу.
        
        Args:
            output_file: Путь к файлу для сохранения рекомендаций
            
        Returns:
            Текст рекомендаций
        """
        logger.info("Формирование рекомендаций по рефакторингу...")
        
        recommendations = []
        recommendations.append("=" * 80)
        recommendations.append("РЕКОМЕНДАЦИИ ПО РЕФАКТОРИНГУ")
        recommendations.append("=" * 80)
        recommendations.append("")
        
        # Документация
        if 'missing_docstrings' in self.issues:
            recommendations.append("1. УЛУЧШЕНИЕ ДОКУМЕНТАЦИИ:")
            recommendations.append("   - Добавить документацию к классам и функциям")
            for file_path, issue in self.issues['missing_docstrings'][:5]:
                recommendations.append(f"   - {file_path}: {issue}")
            if len(self.issues['missing_docstrings']) > 5:
                recommendations.append(f"   - ... и еще {len(self.issues['missing_docstrings']) - 5} элементов без документации")
            recommendations.append("")
        
        # Дублирующийся код
        if 'duplicates' in self.statistics and self.statistics['duplicates'] > 0:
            recommendations.append("2. УСТРАНЕНИЕ ДУБЛИРОВАНИЯ:")
            recommendations.append("   - Выделить повторяющуюся функциональность в общие методы/классы/модули")
            recommendations.append("   - Создать вспомогательные утилиты для часто используемых операций")
            recommendations.append("")
        
        # Стиль кода
        if 'long_lines' in self.issues:
            recommendations.append("3. УЛУЧШЕНИЕ СТИЛЯ КОДА:")
            recommendations.append("   - Сократить длинные строки для улучшения читаемости")
            recommendations.append("   - Убедиться, что код соответствует PEP 8")
            recommendations.append("")
        
        # Мертвый код
        if 'dead_code' in self.issues:
            recommendations.append("4. ОЧИСТКА КОДА:")
            recommendations.append("   - Удалить мертвый код и неиспользуемые элементы")
            recommendations.append("   - Решить задачи, отмеченные TODO/FIXME")
            for file_path, issue in self.issues['dead_code'][:5]:
                recommendations.append(f"   - {file_path}: {issue}")
            if len(self.issues['dead_code']) > 5:
                recommendations.append(f"   - ... и еще {len(self.issues['dead_code']) - 5} проблем с мертвым кодом")
            recommendations.append("")
        
        # Структура проекта
        recommendations.append("5. УЛУЧШЕНИЕ СТРУКТУРЫ ПРОЕКТА:")
        recommendations.append("   - Организовать логически связанные функции в модули")
        recommendations.append("   - Улучшить именование для более ясного описания назначения")
        recommendations.append("   - Применить паттерны проектирования в подходящих местах")
        recommendations.append("")
        
        # Конкретные рекомендации для часто используемых модулей
        common_imports = self.statistics['imports'].most_common(5)
        if common_imports:
            recommendations.append("6. ОПТИМИЗАЦИЯ ИМПОРТОВ:")
            for module, count in common_imports:
                recommendations.append(f"   - {module}: используется в {count} местах, рассмотреть создание обертки/утилиты")
            recommendations.append("")
        
        recommendations_text = '\n'.join(recommendations)
        
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(recommendations_text)
                logger.info(f"Рекомендации сохранены в {output_file}")
            except Exception as e:
                logger.error(f"Ошибка при сохранении рекомендаций: {e}")
        
        return recommendations_text

def main():
    """Основная функция скрипта."""
    parser = argparse.ArgumentParser(description='Анализ и рефакторинг кодовой базы')
    parser.add_argument('--dir', '-d', default='.', help='Директория для анализа')
    parser.add_argument('--report', '-r', help='Путь для сохранения отчета')
    parser.add_argument('--recommendations', '-rec', help='Путь для сохранения рекомендаций')
    parser.add_argument('--python-only', '-p', action='store_true', help='Анализировать только Python-файлы')
    parser.add_argument('--find-duplicates', '-dup', action='store_true', help='Искать дублирующийся код')
    parser.add_argument('--min-lines', '-m', type=int, default=3, help='Минимальное количество строк для поиска дубликатов')
    parser.add_argument('--threshold', '-t', type=float, default=0.8, help='Порог схожести для поиска дубликатов')
    
    args = parser.parse_args()
    
    # Создаем анализатор
    analyzer = CodeAnalyzer(base_dir=args.dir, python_only=args.python_only)
    
    # Сканируем файлы
    analyzer.scan_files()
    
    # Анализируем Python-файлы
    analyzer.analyze_python_files()
    
    # Ищем дублирующийся код при необходимости
    if args.find_duplicates:
        analyzer.find_duplicate_code(min_lines=args.min_lines, threshold=args.threshold)
    
    # Генерируем отчет
    report = analyzer.generate_report(output_file=args.report)
    print(report)
    
    # Формируем рекомендации
    recommendations = analyzer.suggest_refactoring(output_file=args.recommendations)
    print(recommendations)

if __name__ == "__main__":
    main()