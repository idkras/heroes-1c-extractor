#!/usr/bin/env python3
"""
Скрипт для проверки стандартов на соответствие требованиям Registry Standard и Task Master.

Проверяет:
1. Наличие защищенных разделов с метаданными
2. Правильное именование файлов (lowercase, формат даты и т.д.)
3. Соответствие номеров стандартов их расположению в директориях
4. Наличие обязательных разделов в стандартах

Использование:
    python validate_standards.py [директория]

Аргументы:
    директория - путь к директории со стандартами (по умолчанию: текущая директория)

Примеры:
    python validate_standards.py
    python validate_standards.py "[standards .md]"
"""

import os
import re
import sys
import glob
import datetime
from pathlib import Path

# Цветные обозначения для вывода
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
ENDC = '\033[0m'
BOLD = '\033[1m'

# Регулярные выражения для проверки
PROTECTED_SECTION_BEGIN = r'<!--\s*🔒\s*PROTECTED SECTION:\s*BEGIN\s*-->'
PROTECTED_SECTION_END = r'<!--\s*🔒\s*PROTECTED SECTION:\s*END\s*-->'
UPDATED_REGEX = r'updated:\s*(\d{1,2}\s+[A-Za-z]+\s+\d{4}),\s*(\d{1,2}:\d{2})\s+CET\s+by\s+(.+)'
PREVIOUS_VERSION_REGEX = r'previous\s+version:\s*(\d{1,2}\s+[A-Za-z]+\s+\d{4})'
VERSION_REGEX = r'version:\s*(\d+\.\d+)'
STATUS_REGEX = r'status:\s*(Active|Draft|Archived|Deprecated)'
FILENAME_REGEX = r'^(\d+\.\d+)\s+(.+)\s+(\d{1,2}\s+[a-z]+\s+\d{4})\s+(\d{2}:\d{2})\s+CET\s+by\s+(.+)\.md$'

# Обязательные разделы стандартов
REQUIRED_SECTIONS = [
    "## 🎯 Цель документа",
]

# Категории по директориям
DIRECTORY_CATEGORIES = {
    "0. core standards": "0.",
    "1. process · goalmap · task · incidents · tickets · qa": "1.",
    "2. projects · context · next actions": "2.",
    "3. scenarium · jtbd · hipothises · offering · tone": "3.",
    "6. advising · review · supervising": "6.",
    "8. auto · n8n": "8.",
    "9. development · documentation": "9.",
}

class StandardValidator:
    def __init__(self, base_dir="."):
        self.base_dir = base_dir
        self.issues = []
        self.warnings = []
        self.standards_checked = 0
        self.standards_with_issues = 0
        self.standards_ok = 0
    
    def validate_all(self):
        """Проверяет все стандарты в указанной директории."""
        print(f"{BLUE}{BOLD}Начинаю проверку стандартов в директории: {self.base_dir}{ENDC}")
        
        # Получаем все файлы .md рекурсивно
        standard_files = []
        for root, dirs, files in os.walk(self.base_dir):
            # Пропускаем директории [archive]
            if '[archive]' in root or '/archive/' in root:
                continue
                
            for file in files:
                if file.endswith('.md'):
                    full_path = os.path.join(root, file)
                    standard_files.append(full_path)
        
        # Проверяем каждый файл
        for standard_file in standard_files:
            self.validate_standard(standard_file)
            
        # Выводим статистику
        print(f"\n{BLUE}{BOLD}Проверка завершена.{ENDC}")
        print(f"Проверено стандартов: {self.standards_checked}")
        print(f"{GREEN}Стандартов без проблем: {self.standards_ok}{ENDC}")
        print(f"{RED}Стандартов с проблемами: {self.standards_with_issues}{ENDC}")
        print(f"Обнаружено проблем: {len(self.issues)}")
        print(f"Обнаружено предупреждений: {len(self.warnings)}")
        
        # Выводим все проблемы
        if self.issues:
            print(f"\n{RED}{BOLD}Обнаруженные проблемы:{ENDC}")
            for i, issue in enumerate(self.issues, 1):
                print(f"{RED}{i}. {issue}{ENDC}")
        
        # Выводим все предупреждения
        if self.warnings:
            print(f"\n{YELLOW}{BOLD}Предупреждения:{ENDC}")
            for i, warning in enumerate(self.warnings, 1):
                print(f"{YELLOW}{i}. {warning}{ENDC}")
                
        # Возвращаем количество найденных проблем
        return len(self.issues)
    
    def validate_standard(self, file_path):
        """Проверяет один стандарт на соответствие требованиям."""
        self.standards_checked += 1
        
        # Получаем относительный путь и имя файла
        rel_path = os.path.relpath(file_path, self.base_dir)
        file_name = os.path.basename(file_path)
        
        print(f"\nПроверка стандарта: {rel_path}")
        
        issues_before = len(self.issues)
        
        # Читаем содержимое файла
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.issues.append(f"Ошибка чтения файла {rel_path}: {str(e)}")
            self.standards_with_issues += 1
            return
        
        # Проверяем наличие защищенного раздела
        self._check_protected_section(content, file_path)
        
        # Проверяем правильность имени файла
        self._check_filename(file_name, file_path)
        
        # Проверяем соответствие номера стандарта и директории
        self._check_standard_number_and_directory(file_name, file_path)
        
        # Проверяем наличие обязательных разделов
        self._check_required_sections(content, file_path)
        
        # Если не добавилось новых проблем, стандарт в порядке
        if len(self.issues) == issues_before:
            self.standards_ok += 1
            print(f"  {GREEN}✓ Стандарт соответствует требованиям{ENDC}")
        else:
            self.standards_with_issues += 1
            print(f"  {RED}✗ Обнаружены проблемы{ENDC}")
    
    def _check_protected_section(self, content, file_path):
        """Проверяет наличие и корректность защищенного раздела."""
        rel_path = os.path.relpath(file_path, self.base_dir)
        
        # Проверяем наличие начала и конца защищенного раздела
        begin_match = re.search(PROTECTED_SECTION_BEGIN, content)
        end_match = re.search(PROTECTED_SECTION_END, content)
        
        if not begin_match:
            self.issues.append(f"Отсутствует начало защищенного раздела '<!-- 🔒 PROTECTED SECTION: BEGIN -->' в {rel_path}")
        
        if not end_match:
            self.issues.append(f"Отсутствует конец защищенного раздела '<!-- 🔒 PROTECTED SECTION: END -->' в {rel_path}")
        
        if begin_match and end_match:
            protected_section = content[begin_match.end():end_match.start()]
            
            # Проверяем наличие обязательных метаданных
            if not re.search(UPDATED_REGEX, protected_section):
                self.issues.append(f"Отсутствует поле 'updated' в защищенном разделе файла {rel_path}")
            
            if not re.search(VERSION_REGEX, protected_section):
                self.issues.append(f"Отсутствует поле 'version' в защищенном разделе файла {rel_path}")
            
            if not re.search(STATUS_REGEX, protected_section):
                self.issues.append(f"Отсутствует поле 'status' в защищенном разделе файла {rel_path}")
            
            # Проверяем наличие поля previous version (предупреждение, не ошибка)
            if not re.search(PREVIOUS_VERSION_REGEX, protected_section):
                self.warnings.append(f"Отсутствует поле 'previous version' в защищенном разделе файла {rel_path}")
    
    def _check_filename(self, file_name, file_path):
        """Проверяет правильность имени файла."""
        rel_path = os.path.relpath(file_path, self.base_dir)
        
        # Проверяем, содержит ли имя файла заглавные буквы (кроме имен собственных)
        english_words = re.findall(r'\b[A-Z][a-z]+\b', file_name)
        for word in english_words:
            if word not in ["CET", "AI", "JTBD"] and not any(month in word for month in ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]):
                self.issues.append(f"Имя файла содержит заглавные буквы: '{word}' в {rel_path}. Необходимо использовать lowercase.")
        
        # Проверяем наличие номера стандарта в имени файла
        if not re.match(r'^\d+\.\d+', file_name) and not file_name.startswith("README"):
            self.issues.append(f"Отсутствует номер стандарта в имени файла {rel_path}")
        
        # Проверяем формат даты в имени файла
        date_match = re.search(r'(\d{1,2})\s+([a-zA-Z]+)\s+(\d{4})', file_name)
        if not date_match and not file_name.startswith("README"):
            self.issues.append(f"Отсутствует или неправильный формат даты в имени файла {rel_path}")
        
        # Проверяем наличие "by author" в имени файла
        if "by" not in file_name.lower() and not file_name.startswith("README"):
            self.issues.append(f"Отсутствует указание автора ('by author') в имени файла {rel_path}")
        
        # Проверяем использование символа "|" вместо "·"
        if "|" in file_name:
            self.issues.append(f"Имя файла использует символ '|' вместо '·' (middle dot) в {rel_path}")
    
    def _check_standard_number_and_directory(self, file_name, file_path):
        """Проверяет соответствие номера стандарта его расположению в директориях."""
        rel_path = os.path.relpath(file_path, self.base_dir)
        
        # Извлекаем номер стандарта из имени файла
        number_match = re.match(r'(\d+)\.(\d+)', file_name)
        if not number_match:
            return  # Эта проблема уже зафиксирована в _check_filename
        
        category_number = number_match.group(1)
        
        # Определяем ожидаемую категорию для директории
        directory = os.path.dirname(file_path)
        expected_category = None
        
        for dir_name, category in DIRECTORY_CATEGORIES.items():
            if dir_name in directory:
                expected_category = category.rstrip('.')
                break
        
        # Если мы не смогли определить ожидаемую категорию, пропускаем проверку
        if expected_category is None:
            return
        
        # Проверяем соответствие номера стандарта категории директории
        if category_number != expected_category:
            self.issues.append(f"Номер стандарта ({category_number}) не соответствует категории директории ({expected_category}) для {rel_path}")
    
    def _check_required_sections(self, content, file_path):
        """Проверяет наличие обязательных разделов в стандарте."""
        rel_path = os.path.relpath(file_path, self.base_dir)
        
        for section in REQUIRED_SECTIONS:
            if section not in content:
                self.issues.append(f"Отсутствует обязательный раздел '{section}' в {rel_path}")


def main():
    # Получаем путь к директории из аргументов или используем текущую директорию
    base_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    
    # Создаем валидатор
    validator = StandardValidator(base_dir)
    
    # Проверяем все стандарты
    issues_count = validator.validate_all()
    
    # Устанавливаем код возврата в зависимости от наличия проблем
    sys.exit(1 if issues_count > 0 else 0)


if __name__ == "__main__":
    main()