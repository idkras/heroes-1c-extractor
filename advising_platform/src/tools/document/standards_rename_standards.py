#!/usr/bin/env python3
"""
Скрипт для автоматического переименования файлов стандартов в соответствии с требованиями.

Переименовывает файлы стандартов в формат:
[номер].[подномер] [название] [дата] [время] cet by [автор].md

Использование:
    python rename_standards.py [директория]

Аргументы:
    директория - путь к директории со стандартами (по умолчанию: текущая директория)
"""

import os
import re
import sys
import datetime
from pathlib import Path

# Цветные обозначения для вывода
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
ENDC = '\033[0m'
BOLD = '\033[1m'

# Регулярные выражения для извлечения информации
PROTECTED_SECTION_BEGIN = r'<!--\s*🔒\s*PROTECTED SECTION:\s*BEGIN\s*-->'
PROTECTED_SECTION_END = r'<!--\s*🔒\s*PROTECTED SECTION:\s*END\s*-->'
UPDATED_REGEX = r'updated:\s*(\d{1,2}\s+[A-Za-z]+\s+\d{4}),\s*(\d{1,2}:\d{2})\s+CET\s+by\s+(.+)'
VERSION_REGEX = r'version:\s*(\d+\.\d+)'

# Категории по директориям
DIRECTORY_CATEGORIES = {
    "0. core standards": "0.",
    "1. process · goalmap · task · incidents · tickets · qa": "1.",
    "2. projects · context · next actions": "2.",
    "3. scenarium · jtbd · hipothises · offering · tone": "3.",
    "3. communication": "3.",
    "6. advising · review · supervising": "6.",
    "8. auto · n8n": "8.",
    "9. development · documentation": "9.",
}

def get_standard_info_from_content(content):
    """Извлекает информацию о стандарте из содержимого файла."""
    info = {
        'date': None,
        'time': None,
        'author': None,
        'version': None
    }
    
    # Поиск защищенного раздела
    begin_match = re.search(PROTECTED_SECTION_BEGIN, content)
    end_match = re.search(PROTECTED_SECTION_END, content)
    
    if begin_match and end_match:
        protected_section = content[begin_match.end():end_match.start()]
        
        # Извлечение даты, времени и автора
        updated_match = re.search(UPDATED_REGEX, protected_section)
        if updated_match:
            info['date'] = updated_match.group(1).lower()
            info['time'] = updated_match.group(2)
            info['author'] = updated_match.group(3).lower()
        
        # Извлечение версии
        version_match = re.search(VERSION_REGEX, protected_section)
        if version_match:
            info['version'] = version_match.group(1)
    
    return info

def get_standard_title(content):
    """Извлекает заголовок стандарта из содержимого файла."""
    lines = content.split("\n")
    for line in lines:
        if line.startswith("# "):
            return line[2:].lower()
    return None

def get_expected_category(directory_path):
    """Определяет ожидаемую категорию для директории."""
    for dir_name, category in DIRECTORY_CATEGORIES.items():
        if dir_name in directory_path:
            return category
    return None

def suggest_new_filename(file_path, content):
    """Предлагает новое имя файла на основе содержимого."""
    directory = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    
    # Определяем ожидаемую категорию
    category = get_expected_category(directory)
    if not category:
        print(f"{YELLOW}Предупреждение: Не удалось определить категорию для {directory}{ENDC}")
        category = "0."
    
    # Получаем информацию из содержимого файла
    info = get_standard_info_from_content(content)
    
    # Если нет информации в защищенном разделе, попробуем извлечь из имени файла
    if not info['date'] or not info['time'] or not info['author']:
        date_match = re.search(r'(\d{1,2}\s+[a-zA-Z]+\s+\d{4})', file_name)
        if date_match:
            info['date'] = date_match.group(1).lower()
        
        time_match = re.search(r'(\d{2}:\d{2}|\d{4})', file_name)
        if time_match and ':' in time_match.group(1):
            info['time'] = time_match.group(1)
        elif time_match:
            # Преобразование 1345 в 13:45
            time_str = time_match.group(1)
            if len(time_str) == 4:
                info['time'] = f"{time_str[:2]}:{time_str[2:]}"
        
        author_match = re.search(r'by\s+([A-Za-z\s]+)', file_name)
        if author_match:
            info['author'] = author_match.group(1).lower()
    
    # Извлекаем существующий номер стандарта или предлагаем новый
    number_match = re.match(r'(\d+)\.(\d+)', file_name)
    subcategory = "1"
    
    if number_match:
        subcategory = number_match.group(2)
    
    # Получаем заголовок стандарта
    title = get_standard_title(content)
    if not title:
        # Извлекаем название из текущего имени файла
        title_match = re.search(r'\d+\.\d+\s+(.*?)(?:\d{1,2}\s+[a-zA-Z]+|\d{4}|\s+v\d+)', file_name)
        if title_match:
            title = title_match.group(1).strip().lower()
        else:
            title = file_name.replace('.md', '').lower()
    
    # Формируем новое имя файла
    new_filename = ""
    
    # Добавляем номер категории и подкатегории
    new_filename += f"{category.strip('.')}.{subcategory} "
    
    # Добавляем название стандарта (если есть)
    if title:
        # Убираем лишние пробелы и приводим к нижнему регистру
        title = " ".join(title.split())
        # Убираем версии из названия, если они есть
        title = re.sub(r'\s+v\d+(\.\d+)?', '', title)
        new_filename += f"{title} "
    
    # Добавляем дату
    if info['date']:
        new_filename += f"{info['date']} "
    else:
        # Используем текущую дату
        current_date = datetime.datetime.now().strftime("%d %b %Y").lower()
        new_filename += f"{current_date} "
    
    # Добавляем время
    if info['time']:
        new_filename += f"{info['time']} cet "
    else:
        # Используем текущее время
        current_time = datetime.datetime.now().strftime("%H:%M")
        new_filename += f"{current_time} cet "
    
    # Добавляем автора
    if info['author']:
        new_filename += f"by {info['author']}"
    else:
        new_filename += "by ai assistant"
    
    # Добавляем расширение
    new_filename += ".md"
    
    # Очищаем от лишних пробелов и символов
    new_filename = new_filename.replace("  ", " ")
    
    return new_filename

def rename_standards(base_dir="."):
    """Переименовывает файлы стандартов в указанной директории."""
    print(f"{BLUE}{BOLD}Начинаю сканирование стандартов в директории: {base_dir}{ENDC}")
    
    # Получаем все файлы .md рекурсивно
    standard_files = []
    for root, dirs, files in os.walk(base_dir):
        # Пропускаем директории [archive]
        if '[archive]' in root or '/archive/' in root:
            continue
                
        for file in files:
            if file.endswith('.md'):
                full_path = os.path.join(root, file)
                standard_files.append(full_path)
    
    renamed_count = 0
    skipped_count = 0
    failed_count = 0
    
    # Список предлагаемых переименований
    rename_suggestions = []
    
    for file_path in standard_files:
        try:
            # Пропускаем README.md и другие специальные файлы
            if os.path.basename(file_path) in ["README.md", "todo.md", "ai.incidents.md"]:
                continue
            
            # Читаем содержимое файла
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Предлагаем новое имя файла
            new_filename = suggest_new_filename(file_path, content)
            
            # Добавляем предложение в список
            rename_suggestions.append((file_path, os.path.join(os.path.dirname(file_path), new_filename)))
            
        except Exception as e:
            print(f"{RED}Ошибка при обработке файла {file_path}: {str(e)}{ENDC}")
            failed_count += 1
    
    # Выводим список предлагаемых переименований
    print(f"\n{BLUE}{BOLD}Предлагаемые переименования:{ENDC}")
    
    for i, (old_path, new_path) in enumerate(rename_suggestions, 1):
        old_name = os.path.basename(old_path)
        new_name = os.path.basename(new_path)
        
        if old_name != new_name:
            print(f"{i}. {YELLOW}{old_name}{ENDC} → {GREEN}{new_name}{ENDC}")
        else:
            print(f"{i}. {GREEN}{old_name} (без изменений){ENDC}")
    
    # Спрашиваем пользователя, хочет ли он применить изменения
    print(f"\n{BLUE}{BOLD}Всего файлов: {len(rename_suggestions)}{ENDC}")
    print(f"Применить изменения? (y/n): ", end="")
    answer = input().strip().lower()
    
    if answer == 'y':
        # Применяем переименования
        for old_path, new_path in rename_suggestions:
            if old_path != new_path and os.path.basename(old_path) != os.path.basename(new_path):
                try:
                    if not os.path.exists(new_path):
                        os.rename(old_path, new_path)
                        print(f"{GREEN}Переименован: {os.path.basename(old_path)} → {os.path.basename(new_path)}{ENDC}")
                        renamed_count += 1
                    else:
                        print(f"{YELLOW}Пропущен (файл уже существует): {os.path.basename(old_path)}{ENDC}")
                        skipped_count += 1
                except Exception as e:
                    print(f"{RED}Ошибка при переименовании {old_path}: {str(e)}{ENDC}")
                    failed_count += 1
            else:
                # Файл уже имеет правильное имя
                skipped_count += 1
        
        print(f"\n{BLUE}{BOLD}Переименование завершено.{ENDC}")
        print(f"{GREEN}Переименовано: {renamed_count}{ENDC}")
        print(f"{YELLOW}Пропущено: {skipped_count}{ENDC}")
        print(f"{RED}Ошибок: {failed_count}{ENDC}")
    else:
        print(f"\n{YELLOW}Переименование отменено.{ENDC}")

def main():
    # Получаем путь к директории из аргументов или используем текущую директорию
    base_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    
    # Переименовываем стандарты
    rename_standards(base_dir)

if __name__ == "__main__":
    main()