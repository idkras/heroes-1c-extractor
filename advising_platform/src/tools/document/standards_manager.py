"""
Модуль для управления стандартами документации.

Этот модуль объединяет инструменты для работы со стандартами документации:
1. Валидация стандартов на соответствие требованиям
2. Исправление метаданных в стандартах
3. Переименование файлов стандартов
4. Анализ пересечений между стандартами

Автор: AI Assistant
Дата: 19 May 2025
"""

import os
import re
import sys
import glob
import logging
import datetime
import difflib
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any

# Настройка логирования
logger = logging.getLogger(__name__)

# Корневая директория проекта
from . import STANDARDS_DIR

# Регулярные выражения для работы со стандартами
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
    """
    Класс для проверки стандартов на соответствие требованиям.
    """
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or STANDARDS_DIR
        self.issues = []
        self.warnings = []
        self.standards_checked = 0
        self.standards_with_issues = 0
        self.standards_ok = 0
    
    def validate_all(self):
        """Проверяет все стандарты в указанной директории."""
        logger.info(f"Начинаю проверку стандартов в директории: {self.base_dir}")
        
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
        logger.info(f"Проверка завершена.")
        logger.info(f"Проверено стандартов: {self.standards_checked}")
        logger.info(f"Стандартов без проблем: {self.standards_ok}")
        logger.info(f"Стандартов с проблемами: {self.standards_with_issues}")
        logger.info(f"Обнаружено проблем: {len(self.issues)}")
        logger.info(f"Обнаружено предупреждений: {len(self.warnings)}")
        
        # Возвращаем количество найденных проблем
        return len(self.issues)
    
    def validate_standard(self, file_path):
        """Проверяет один стандарт на соответствие требованиям."""
        self.standards_checked += 1
        
        # Получаем относительный путь и имя файла
        rel_path = os.path.relpath(file_path, self.base_dir)
        file_name = os.path.basename(file_path)
        
        logger.info(f"Проверка стандарта: {rel_path}")
        
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
            logger.info(f"  ✓ Стандарт соответствует требованиям")
        else:
            self.standards_with_issues += 1
            logger.info(f"  ✗ Обнаружены проблемы")
    
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


class StandardFixer:
    """
    Класс для исправления проблем в стандартах.
    """
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or STANDARDS_DIR
        self.files_fixed = 0
        self.issues_fixed = 0
    
    def fix_all(self, create_backups=True):
        """Исправляет все стандарты в указанной директории."""
        logger.info(f"Начинаю исправление стандартов в директории: {self.base_dir}")
        
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
        
        # Исправляем каждый файл
        for standard_file in standard_files:
            self.fix_standard(standard_file, create_backups)
            
        # Выводим статистику
        logger.info(f"Исправление завершено.")
        logger.info(f"Исправлено файлов: {self.files_fixed}")
        logger.info(f"Исправлено проблем: {self.issues_fixed}")
        
        # Возвращаем количество исправленных файлов
        return self.files_fixed
    
    def fix_standard(self, file_path, create_backup=True):
        """Исправляет один стандарт."""
        # Получаем относительный путь и имя файла
        rel_path = os.path.relpath(file_path, self.base_dir)
        file_name = os.path.basename(file_path)
        
        logger.info(f"Исправление стандарта: {rel_path}")
        
        # Читаем содержимое файла
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Ошибка чтения файла {rel_path}: {str(e)}")
            return
        
        # Сохраняем оригинальное содержимое для сравнения
        original_content = content
        
        # Исправляем защищенный раздел
        content = self._fix_protected_section(content, file_path)
        
        # Исправляем имя файла, если необходимо
        new_file_path = self._fix_filename(file_path)
        
        # Если содержимое изменилось, создаем бэкап и сохраняем изменения
        if content != original_content:
            if create_backup:
                backup_path = file_path + ".bak"
                try:
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.write(original_content)
                    logger.info(f"  Создана резервная копия: {os.path.basename(backup_path)}")
                except Exception as e:
                    logger.error(f"  Ошибка создания резервной копии {os.path.basename(backup_path)}: {str(e)}")
            
            # Сохраняем изменения
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"  ✓ Файл успешно обновлен")
                self.files_fixed += 1
                self.issues_fixed += 1
            except Exception as e:
                logger.error(f"  Ошибка сохранения файла {rel_path}: {str(e)}")
        
        # Если путь к файлу изменился, перемещаем файл
        if new_file_path and new_file_path != file_path:
            try:
                # Создаем резервную копию, если необходимо
                if create_backup:
                    backup_dir = os.path.join(os.path.dirname(file_path), "[archive]", "rename_backups")
                    os.makedirs(backup_dir, exist_ok=True)
                    backup_path = os.path.join(backup_dir, os.path.basename(file_path))
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    logger.info(f"  Создана резервная копия перед переименованием: {os.path.basename(backup_path)}")
                
                # Перемещаем файл
                os.rename(file_path, new_file_path)
                logger.info(f"  ✓ Файл успешно переименован в: {os.path.basename(new_file_path)}")
                self.files_fixed += 1
                self.issues_fixed += 1
            except Exception as e:
                logger.error(f"  Ошибка переименования файла {rel_path}: {str(e)}")
    
    def _fix_protected_section(self, content, file_path):
        """Исправляет защищенный раздел в стандарте."""
        # Проверяем наличие начала и конца защищенного раздела
        begin_match = re.search(PROTECTED_SECTION_BEGIN, content)
        end_match = re.search(PROTECTED_SECTION_END, content)
        
        # Если защищенный раздел отсутствует, добавляем его
        if not begin_match or not end_match:
            # Формируем защищенный раздел
            now = datetime.datetime.now()
            date_str = now.strftime("%-d %B %Y")
            time_str = now.strftime("%-H:%M")
            author = "AI Assistant"
            
            protected_section = f"""<!-- 🔒 PROTECTED SECTION: BEGIN -->
type: standard
version: 1.0
status: Active
updated: {date_str}, {time_str} CET by {author}
tags: standard, documentation
<!-- 🔒 PROTECTED SECTION: END -->

"""
            
            # Добавляем раздел в начало файла
            content = protected_section + content
            logger.info(f"  Добавлен защищенный раздел")
            return content
        
        # Если защищенный раздел есть, проверяем и дополняем его
        protected_section = content[begin_match.end():end_match.start()]
        modified_section = protected_section
        
        # Проверяем наличие обязательных полей
        if not re.search(r'type:\s*standard', protected_section, re.IGNORECASE):
            modified_section = "type: standard\n" + modified_section
        
        if not re.search(VERSION_REGEX, protected_section):
            modified_section = modified_section + "version: 1.0\n"
        
        if not re.search(STATUS_REGEX, protected_section):
            modified_section = modified_section + "status: Active\n"
        
        if not re.search(UPDATED_REGEX, protected_section):
            now = datetime.datetime.now()
            date_str = now.strftime("%-d %B %Y")
            time_str = now.strftime("%-H:%M")
            author = "AI Assistant"
            modified_section = modified_section + f"updated: {date_str}, {time_str} CET by {author}\n"
        
        if not re.search(r'tags:', protected_section, re.IGNORECASE):
            modified_section = modified_section + "tags: standard, documentation\n"
        
        # Если раздел был изменен, обновляем его
        if modified_section != protected_section:
            content = content[:begin_match.end()] + modified_section + content[end_match.start():]
            logger.info(f"  Исправлен защищенный раздел")
        
        return content
    
    def _fix_filename(self, file_path):
        """Исправляет имя файла стандарта."""
        file_name = os.path.basename(file_path)
        
        # Пропускаем README и другие специальные файлы
        if file_name.startswith("README") or '.' not in file_name:
            return None
        
        # Проверяем, нужно ли исправлять имя файла
        is_valid = True
        
        # Проверяем наличие номера стандарта
        number_match = re.match(r'^\d+\.\d+', file_name)
        if not number_match:
            is_valid = False
        
        # Проверяем формат даты
        date_match = re.search(r'(\d{1,2})\s+([a-zA-Z]+)\s+(\d{4})', file_name)
        if not date_match:
            is_valid = False
        
        # Проверяем наличие автора
        if "by" not in file_name.lower():
            is_valid = False
        
        # Если имя файла уже корректно, пропускаем
        if is_valid:
            return None
        
        # Читаем содержимое файла для извлечения метаданных
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"  Ошибка чтения файла для исправления имени: {str(e)}")
            return None
        
        # Извлекаем номер стандарта
        standard_number = "1.0"  # По умолчанию
        number_match = re.search(r'^\d+\.\d+', file_name)
        if number_match:
            standard_number = number_match.group(0)
        else:
            # Пытаемся найти номер в первой строке содержимого
            first_line = content.split('\n')[0]
            number_match = re.search(r'^\d+\.\d+', first_line)
            if number_match:
                standard_number = number_match.group(0)
        
        # Извлекаем название стандарта
        title = file_name.replace('.md', '')
        title_match = re.search(r'^\d+\.\d+\s+(.*?)(?:\s+\d{1,2}\s+[a-zA-Z]+\s+\d{4}|$)', file_name)
        if title_match:
            title = title_match.group(1).strip()
        else:
            # Пытаемся найти название в первой строке содержимого
            first_line = content.split('\n')[0]
            title_match = re.search(r'^\s*#\s+(.+)$', first_line)
            if title_match:
                title = title_match.group(1).strip()
                # Удаляем номер стандарта из названия, если он есть
                title = re.sub(r'^\d+\.\d+\s+', '', title)
        
        # Извлекаем дату и автора
        now = datetime.datetime.now()
        date_str = now.strftime("%-d %B %Y").lower()
        time_str = now.strftime("%H%M")
        author = "ai assistant"
        
        # Ищем дату обновления в защищенном разделе
        begin_match = re.search(PROTECTED_SECTION_BEGIN, content)
        end_match = re.search(PROTECTED_SECTION_END, content)
        if begin_match and end_match:
            protected_section = content[begin_match.end():end_match.start()]
            updated_match = re.search(UPDATED_REGEX, protected_section)
            if updated_match:
                date_str = updated_match.group(1).lower()
                time_parts = updated_match.group(2).split(':')
                time_str = time_parts[0] + time_parts[1]
                author = updated_match.group(3).lower()
        
        # Формируем новое имя файла
        new_file_name = f"{standard_number} {title} {date_str} {time_str} cet by {author}.md"
        
        # Заменяем "|" на "·" в имени файла
        new_file_name = new_file_name.replace("|", "·")
        
        # Формируем новый путь
        new_file_path = os.path.join(os.path.dirname(file_path), new_file_name)
        
        # Если старое и новое имя совпадают, пропускаем
        if file_path == new_file_path:
            return None
        
        return new_file_path


class StandardAnalyzer:
    """
    Класс для анализа пересечений содержимого между стандартами.
    """
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or STANDARDS_DIR
        self.standards = {}  # id -> (path, content)
        self.similarity_matrix = {}  # (id1, id2) -> similarity
    
    def analyze_all(self, threshold=0.3):
        """Анализирует пересечения между всеми стандартами в директории."""
        logger.info(f"Начинаю анализ пересечений между стандартами в директории: {self.base_dir}")
        
        # Загружаем все стандарты
        self._load_standards()
        
        # Если найдено менее 2 стандартов, пропускаем анализ
        if len(self.standards) < 2:
            logger.warning(f"Найдено менее 2 стандартов, анализ пересечений невозможен.")
            return {}
        
        # Вычисляем матрицу сходства
        self._compute_similarity_matrix()
        
        # Находим пары с наибольшим сходством
        similar_pairs = []
        for (id1, id2), similarity in self.similarity_matrix.items():
            if similarity >= threshold:
                path1, _ = self.standards[id1]
                path2, _ = self.standards[id2]
                rel_path1 = os.path.relpath(path1, self.base_dir)
                rel_path2 = os.path.relpath(path2, self.base_dir)
                similar_pairs.append({
                    'standard1': rel_path1,
                    'standard2': rel_path2,
                    'similarity': similarity
                })
        
        # Сортируем по убыванию сходства
        similar_pairs.sort(key=lambda pair: pair['similarity'], reverse=True)
        
        # Выводим результаты
        logger.info(f"Анализ завершен. Найдено {len(similar_pairs)} пар стандартов с сходством >= {threshold}.")
        for i, pair in enumerate(similar_pairs[:10], 1):
            logger.info(f"{i}. {pair['standard1']} <-> {pair['standard2']}: {pair['similarity']:.2f}")
        
        return similar_pairs
    
    def _load_standards(self):
        """Загружает все стандарты из директории."""
        self.standards = {}
        
        # Получаем все файлы .md рекурсивно
        for root, dirs, files in os.walk(self.base_dir):
            # Пропускаем директории [archive]
            if '[archive]' in root or '/archive/' in root:
                continue
                
            for file in files:
                if file.endswith('.md'):
                    full_path = os.path.join(root, file)
                    
                    # Читаем содержимое файла
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                            # Очищаем содержимое от защищенных разделов
                            content = self._clean_content(content)
                            
                            # Добавляем в словарь стандартов
                            standard_id = os.path.relpath(full_path, self.base_dir)
                            self.standards[standard_id] = (full_path, content)
                    except Exception as e:
                        logger.error(f"Ошибка чтения файла {full_path}: {str(e)}")
        
        logger.info(f"Загружено {len(self.standards)} стандартов.")
    
    def _clean_content(self, content):
        """Очищает содержимое от защищенных разделов и метаданных."""
        # Удаляем защищенные разделы
        content = re.sub(f"{PROTECTED_SECTION_BEGIN}.*?{PROTECTED_SECTION_END}", "", content, flags=re.DOTALL)
        
        # Удаляем пустые строки
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        return content
    
    def _compute_similarity_matrix(self):
        """Вычисляет матрицу сходства между стандартами."""
        self.similarity_matrix = {}
        
        # Получаем список идентификаторов стандартов
        standard_ids = list(self.standards.keys())
        
        # Вычисляем сходство для каждой пары стандартов
        total_pairs = len(standard_ids) * (len(standard_ids) - 1) // 2
        processed_pairs = 0
        
        for i, id1 in enumerate(standard_ids):
            for id2 in standard_ids[i+1:]:
                # Вычисляем сходство
                _, content1 = self.standards[id1]
                _, content2 = self.standards[id2]
                
                similarity = self._compute_similarity(content1, content2)
                
                # Сохраняем результат
                self.similarity_matrix[(id1, id2)] = similarity
                
                # Обновляем счетчик
                processed_pairs += 1
                if processed_pairs % 100 == 0:
                    logger.info(f"Обработано {processed_pairs}/{total_pairs} пар стандартов.")
        
        logger.info(f"Вычислена матрица сходства для {len(standard_ids)} стандартов.")
    
    def _compute_similarity(self, content1, content2):
        """Вычисляет сходство между двумя текстами."""
        # Разбиваем тексты на строки
        lines1 = content1.split('\n')
        lines2 = content2.split('\n')
        
        # Используем difflib для вычисления сходства
        matcher = difflib.SequenceMatcher(None, lines1, lines2)
        return matcher.ratio()


# Публичные функции для использования в других модулях

def validate_standards(base_dir=None):
    """
    Проверяет стандарты на соответствие требованиям.
    
    Args:
        base_dir (str, optional): Директория со стандартами
        
    Returns:
        int: Количество найденных проблем
    """
    validator = StandardValidator(base_dir)
    return validator.validate_all()


def fix_standards_metadata(base_dir=None, create_backups=True):
    """
    Исправляет метаданные в стандартах.
    
    Args:
        base_dir (str, optional): Директория со стандартами
        create_backups (bool): Создавать ли резервные копии
        
    Returns:
        int: Количество исправленных файлов
    """
    fixer = StandardFixer(base_dir)
    return fixer.fix_all(create_backups)


def rename_standards(base_dir=None, create_backups=True):
    """
    Переименовывает файлы стандартов в соответствии с требованиями.
    
    Args:
        base_dir (str, optional): Директория со стандартами
        create_backups (bool): Создавать ли резервные копии
        
    Returns:
        int: Количество переименованных файлов
    """
    fixer = StandardFixer(base_dir)
    return fixer.fix_all(create_backups)


def analyze_standards_overlap(base_dir=None, threshold=0.3):
    """
    Анализирует пересечения содержимого между стандартами.
    
    Args:
        base_dir (str, optional): Директория со стандартами
        threshold (float): Порог сходства
        
    Returns:
        List[Dict]: Список пар стандартов с сходством >= threshold
    """
    analyzer = StandardAnalyzer(base_dir)
    return analyzer.analyze_all(threshold)