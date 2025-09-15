#!/usr/bin/env python3
"""
Инструмент для валидации имен файлов на соответствие стандарту TaskMaster.
Проверяет корректность имен файлов и соответствие метаданных в файлах стандартам.

Использование:
  python validate_filename.py [путь к файлу или директории]
"""

import os
import re
import sys
import argparse
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class TaskMasterValidator:
    """Класс для валидации имен файлов и метаданных на соответствие стандарту TaskMaster."""

    # Регулярное выражение для валидации имен файлов стандартов
    STANDARD_FILENAME_PATTERN = r'^(\d+\.\d+|\d+\.|\d+)\s+([a-zA-Zа-яА-Я_\s]+)\s+(\d+\s+[a-z]+\s+\d{4})\s+(\d+:\d+)\s+CET\s+by\s+(.+)\.md$'
    
    # Регулярное выражение для строки updated
    UPDATED_PATTERN = r'updated:\s*(\d+\s+[a-z]+\s+\d{4},\s*\d+:\d+\s+CET)\s+by\s+(.+)'
    
    # Регулярное выражение для строки based on
    BASED_ON_PATTERN = r'based on:\s*([^,]+),\s*версия\s+(\d+\s+[a-z]+\s+\d{4},\s*\d+:\d+\s+CET)'
    
    # Обязательные поля метаданных в начале файла
    REQUIRED_METADATA_FIELDS = ['updated', 'based on']
    
    def __init__(self):
        """Инициализация валидатора."""
        self.validation_results = {
            'valid_files': [],
            'invalid_files': [],
            'errors': []
        }

    def validate_filename(self, filename: str) -> Tuple[bool, Optional[str]]:
        """
        Проверяет соответствие имени файла стандарту TaskMaster.
        
        Args:
            filename: Имя файла для проверки
            
        Returns:
            Tuple[bool, Optional[str]]: (Результат валидации, Сообщение об ошибке)
        """
        if not filename.endswith('.md'):
            return False, "Файл должен иметь расширение .md"
            
        # Проверка на соответствие шаблону имени файла стандарта
        match = re.match(self.STANDARD_FILENAME_PATTERN, os.path.basename(filename))
        if not match:
            return False, "Имя файла не соответствует шаблону '[версия] [название] [дата] [время] CET by [автор].md'"
            
        version, name, date, time, author = match.groups()
        
        # Дополнительные проверки компонентов имени файла
        try:
            # Проверка формата даты
            date_parts = date.split()
            if len(date_parts) != 3:
                return False, "Неверный формат даты в имени файла"
            
            day, month, year = date_parts
            int(day)  # Проверка, что день - число
            int(year)  # Проверка, что год - число
            
            # Проверка формата времени
            time_parts = time.split(':')
            if len(time_parts) != 2:
                return False, "Неверный формат времени в имени файла"
            
            hour, minute = time_parts
            int(hour)  # Проверка, что час - число
            int(minute)  # Проверка, что минута - число
            
        except (ValueError, IndexError):
            return False, "Неверный формат даты или времени в имени файла"
            
        return True, None

    def validate_file_content(self, file_path: str) -> Tuple[bool, List[str]]:
        """
        Проверяет содержимое файла на соответствие стандарту TaskMaster.
        
        Args:
            file_path: Путь к файлу для проверки
            
        Returns:
            Tuple[bool, List[str]]: (Результат валидации, Список ошибок)
        """
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                lines = content.split('\n')
                
                # Проверка наличия заголовка
                if not lines or not lines[0].startswith('# '):
                    errors.append("Отсутствует заголовок (строка, начинающаяся с '# ')")
                
                # Проверка наличия строки updated
                updated_match = re.search(self.UPDATED_PATTERN, content)
                if not updated_match:
                    errors.append("Отсутствует или неверный формат строки 'updated:'")
                    
                # Проверка наличия строки based on для стандартов, основанных на TaskMaster
                if "Task Master" not in os.path.basename(file_path):
                    based_on_match = re.search(self.BASED_ON_PATTERN, content)
                    if not based_on_match:
                        errors.append("Отсутствует или неверный формат строки 'based on:' для стандарта, основанного на TaskMaster")
                
                # Проверка наличия секции лицензии и условий использования для TaskMaster
                if "Task Master" in os.path.basename(file_path) and "## 🛡️ Лицензия и условия использования" not in content:
                    errors.append("Отсутствует секция '## 🛡️ Лицензия и условия использования' в TaskMaster")
                
        except Exception as e:
            errors.append(f"Ошибка при анализе файла: {str(e)}")
            
        return len(errors) == 0, errors

    def validate_file(self, file_path: str) -> Tuple[bool, List[str]]:
        """
        Проверяет файл на соответствие стандарту TaskMaster.
        
        Args:
            file_path: Путь к файлу для проверки
            
        Returns:
            Tuple[bool, List[str]]: (Результат валидации, Список ошибок)
        """
        errors = []
        
        # Проверка имени файла
        filename_valid, filename_error = self.validate_filename(file_path)
        if not filename_valid:
            errors.append(f"Ошибка в имени файла: {filename_error}")
            
        # Проверка содержимого файла
        content_valid, content_errors = self.validate_file_content(file_path)
        if not content_valid:
            errors.extend(content_errors)
            
        return len(errors) == 0, errors

    def validate_directory(self, directory_path: str, recursive: bool = False) -> Dict:
        """
        Проверяет все md-файлы в директории на соответствие стандарту TaskMaster.
        
        Args:
            directory_path: Путь к директории для проверки
            recursive: Рекурсивная проверка поддиректорий
            
        Returns:
            Dict: Результаты валидации
        """
        if not os.path.isdir(directory_path):
            self.validation_results['errors'].append(f"Указанный путь не является директорией: {directory_path}")
            return self.validation_results
            
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            
            if os.path.isfile(item_path) and item.endswith('.md'):
                valid, errors = self.validate_file(item_path)
                if valid:
                    self.validation_results['valid_files'].append(item_path)
                else:
                    self.validation_results['invalid_files'].append({
                        'file': item_path,
                        'errors': errors
                    })
            elif os.path.isdir(item_path) and recursive:
                self.validate_directory(item_path, recursive)
                
        return self.validation_results

    def print_validation_results(self):
        """Выводит результаты валидации в консоль."""
        print("\n====== Результаты валидации ======")
        print(f"Проверено файлов: {len(self.validation_results['valid_files']) + len(self.validation_results['invalid_files'])}")
        print(f"Файлов, соответствующих стандарту: {len(self.validation_results['valid_files'])}")
        print(f"Файлов с ошибками: {len(self.validation_results['invalid_files'])}")
        
        if self.validation_results['errors']:
            print("\n----- Общие ошибки -----")
            for error in self.validation_results['errors']:
                print(f"- {error}")
                
        if self.validation_results['invalid_files']:
            print("\n----- Ошибки в файлах -----")
            for file_info in self.validation_results['invalid_files']:
                print(f"\nФайл: {file_info['file']}")
                for error in file_info['errors']:
                    print(f"  - {error}")
        
        print("\n====== Конец отчета ======")


def main():
    """Основная функция программы."""
    parser = argparse.ArgumentParser(description='Валидатор имен файлов и содержимого для стандарта TaskMaster')
    parser.add_argument('path', help='Путь к файлу или директории для проверки')
    parser.add_argument('-r', '--recursive', action='store_true', help='Рекурсивная проверка поддиректорий')
    
    args = parser.parse_args()
    
    validator = TaskMasterValidator()
    
    if os.path.isfile(args.path):
        valid, errors = validator.validate_file(args.path)
        if valid:
            print(f"✅ Файл {args.path} соответствует стандарту TaskMaster")
        else:
            print(f"❌ Файл {args.path} не соответствует стандарту TaskMaster:")
            for error in errors:
                print(f"  - {error}")
    elif os.path.isdir(args.path):
        results = validator.validate_directory(args.path, args.recursive)
        validator.print_validation_results()
    else:
        print(f"Ошибка: Указанный путь не существует: {args.path}")
        return 1
        
    return 0


if __name__ == "__main__":
    sys.exit(main())