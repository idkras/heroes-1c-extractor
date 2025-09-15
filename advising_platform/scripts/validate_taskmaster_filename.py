#!/usr/bin/env python3
"""
Валидатор имен файлов по стандарту TaskMaster.

Проверяет соответствие имен файлов шаблону:
"[версия] [название] by [дата] [время] CET by [автор].md"

Использование:
    python validate_taskmaster_filename.py <путь к файлу или директории>
"""

import os
import re
import sys
import argparse
from datetime import datetime
from typing import List, Dict, Tuple, Optional


class TaskMasterValidator:
    """Класс для валидации файлов по стандарту TaskMaster."""

    # Регулярное выражение для проверки имени файла
    FILENAME_PATTERN = r'^(\d+\.\d+|\d+)\s+(.+)\s+by\s+(\d{1,2}\s+[a-z]{3}\s+\d{4})\s+(\d{3,4})\s+CET\s+by\s+(.+)\.md$'

    def __init__(self, verbose: bool = False):
        """
        Инициализирует валидатор.
        
        Args:
            verbose: Включает подробный вывод результатов проверки
        """
        self.verbose = verbose
        self.filename_regex = re.compile(self.FILENAME_PATTERN, re.IGNORECASE)

    def validate_filename(self, filename: str) -> Tuple[bool, Optional[Dict]]:
        """
        Проверяет имя файла на соответствие стандарту TaskMaster.
        
        Args:
            filename: Имя файла для проверки
            
        Returns:
            Tuple[bool, Dict]: Результат проверки (успех/неудача) и словарь с компонентами имени
                              или None, если проверка не прошла
        """
        match = self.filename_regex.match(os.path.basename(filename))
        
        if not match:
            return False, None
            
        version, title, date, time, author = match.groups()
        
        # Проверка правильности формата даты
        try:
            datetime.strptime(date, "%d %b %Y")
        except ValueError:
            return False, None
            
        # Проверка правильности формата времени
        if len(time) == 3:
            try:
                hour, minute = int(time[0]), int(time[1:3])
                if hour < 0 or hour > 2 or minute < 0 or minute > 59:
                    return False, None
            except ValueError:
                return False, None
        elif len(time) == 4:
            try:
                hour, minute = int(time[0:2]), int(time[2:4])
                if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                    return False, None
            except ValueError:
                return False, None
        else:
            return False, None
            
        components = {
            "version": version,
            "title": title,
            "date": date,
            "time": time,
            "author": author
        }
        
        return True, components

    def validate_file(self, filepath: str) -> Tuple[bool, Optional[Dict]]:
        """
        Проверяет файл на соответствие стандарту TaskMaster.
        
        Args:
            filepath: Путь к файлу для проверки
            
        Returns:
            Tuple[bool, Dict]: Результат проверки (успех/неудача) и словарь с компонентами имени
                              или None, если проверка не прошла
        """
        if not os.path.isfile(filepath) or not filepath.lower().endswith('.md'):
            return False, None
            
        return self.validate_filename(filepath)

    def validate_directory(self, dirpath: str, recursive: bool = True) -> List[Tuple[str, bool, Optional[Dict]]]:
        """
        Проверяет все файлы в директории на соответствие стандарту TaskMaster.
        
        Args:
            dirpath: Путь к директории для проверки
            recursive: Включает рекурсивную проверку поддиректорий
            
        Returns:
            List[Tuple[str, bool, Dict]]: Список из путей к файлам, результатов проверки
                                        и компонентов имени
        """
        results = []
        
        for root, dirs, files in os.walk(dirpath):
            for file in files:
                if file.lower().endswith('.md'):
                    filepath = os.path.join(root, file)
                    is_valid, components = self.validate_filename(file)
                    results.append((filepath, is_valid, components))
                    
            if not recursive:
                break
                
        return results

    def print_validation_result(self, filepath: str, is_valid: bool, components: Optional[Dict]) -> None:
        """
        Выводит результат валидации файла.
        
        Args:
            filepath: Путь к проверенному файлу
            is_valid: Результат проверки
            components: Извлеченные компоненты имени файла
        """
        filename = os.path.basename(filepath)
        
        if is_valid:
            print(f"✅ {filepath}")
            if self.verbose and components:
                print(f"  Версия: {components['version']}")
                print(f"  Название: {components['title']}")
                print(f"  Дата: {components['date']}")
                print(f"  Время: {components['time']}")
                print(f"  Автор: {components['author']}")
        else:
            print(f"❌ {filepath}")
            print(f"  Имя файла не соответствует шаблону: {filename}")
            print(f"  Ожидаемый формат: [версия] [название] by [дата] [время] CET by [автор].md")
            print(f"  Пример: 1.0 design standard by 11 may 2025 1930 CET by Ilya Krasinsky.md")

    def generate_valid_filename(self, title: str, version: str = "1.0", 
                              author: str = "Илья Красинский") -> str:
        """
        Генерирует валидное имя файла по стандарту TaskMaster.
        
        Args:
            title: Название документа
            version: Версия документа
            author: Автор документа
            
        Returns:
            str: Валидное имя файла
        """
        now = datetime.now()
        date_str = now.strftime("%d %b %Y").lower()
        time_str = now.strftime("%H%M")
        
        filename = f"{version} {title} by {date_str} {time_str} CET by {author}.md"
        return filename


def main():
    parser = argparse.ArgumentParser(description='Валидатор имен файлов по стандарту TaskMaster')
    parser.add_argument('path', help='Путь к файлу или директории для проверки')
    parser.add_argument('-r', '--recursive', action='store_true', 
                        help='Рекурсивная проверка директорий')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Подробный вывод результатов')
    parser.add_argument('-g', '--generate', action='store_true',
                        help='Генерировать валидное имя файла для невалидных файлов')
    parser.add_argument('-t', '--title', 
                        help='Название документа (для генерации имени)')
    parser.add_argument('-a', '--author', default="Илья Красинский",
                        help='Автор документа (для генерации имени)')
    parser.add_argument('-V', '--version', default="1.0",
                        help='Версия документа (для генерации имени)')
    
    args = parser.parse_args()
    
    validator = TaskMasterValidator(verbose=args.verbose)
    
    if args.generate and args.title:
        filename = validator.generate_valid_filename(
            args.title, version=args.version, author=args.author)
        print(f"Сгенерированное имя файла: {filename}")
        return
    
    if os.path.isfile(args.path):
        is_valid, components = validator.validate_file(args.path)
        validator.print_validation_result(args.path, is_valid, components)
        
        if not is_valid and args.generate:
            title = os.path.splitext(os.path.basename(args.path))[0]
            filename = validator.generate_valid_filename(
                title, version=args.version, author=args.author)
            print(f"Рекомендуемое имя файла: {filename}")
    
    elif os.path.isdir(args.path):
        results = validator.validate_directory(args.path, recursive=args.recursive)
        
        valid_count = sum(1 for _, is_valid, _ in results if is_valid)
        total_count = len(results)
        
        for filepath, is_valid, components in results:
            validator.print_validation_result(filepath, is_valid, components)
            
            if not is_valid and args.generate:
                title = os.path.splitext(os.path.basename(filepath))[0]
                filename = validator.generate_valid_filename(
                    title, version=args.version, author=args.author)
                print(f"  Рекомендуемое имя файла: {filename}")
        
        print(f"\nИтого: {valid_count}/{total_count} файлов соответствуют стандарту TaskMaster")
        
    else:
        print(f"Ошибка: путь {args.path} не существует")


if __name__ == "__main__":
    main()