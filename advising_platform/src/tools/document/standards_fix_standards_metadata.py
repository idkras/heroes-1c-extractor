#!/usr/bin/env python3
"""
Скрипт для автоматического исправления проблем в стандартах.

Выполняет:
1. Добавление защищенных разделов с метаданными в файлы, у которых их нет
2. Добавление обязательных полей в защищенные разделы
3. Проверку и добавление обязательных разделов в стандарты
4. Создание резервных копий перед модификацией файлов

Использование:
    python fix_standards_metadata.py [директория] [--apply] [--verbose]

Аргументы:
    директория - путь к директории со стандартами (по умолчанию: текущая директория)
    --apply    - применить исправления (без этого флага только показывает проблемы)
    --verbose  - подробный вывод о всех операциях

Примеры:
    python fix_standards_metadata.py --verbose
    python fix_standards_metadata.py "[standards .md]" --apply
"""

import os
import re
import sys
import glob
import shutil
import argparse
import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Any

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

# Обязательные разделы стандартов
REQUIRED_SECTIONS = [
    "## 🎯 Цель документа",
]

def extract_standard_id_from_filename(filename):
    """Извлекает номер стандарта из имени файла."""
    match = re.match(r'^(\d+\.\d+)', os.path.basename(filename))
    if match:
        return match.group(1)
    return None

def extract_title_from_content(content):
    """Извлекает заголовок стандарта из содержимого."""
    lines = content.split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    return None

def get_standard_directory_number(file_path):
    """Получает номер категории стандарта на основе его расположения в директории."""
    parts = Path(file_path).parts
    for part in parts:
        match = re.match(r'^(\d+)\.\s+', part)
        if match:
            return match.group(1)
    return None

def create_backup(file_path):
    """Создает резервную копию файла перед изменением."""
    backup_path = f"{file_path}.bak"
    shutil.copy2(file_path, backup_path)
    return backup_path

def add_protected_section(file_path, apply=False, verbose=False):
    """Добавляет защищенный раздел с метаданными в файл, если его нет."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем наличие защищенного раздела
        has_protected_begin = re.search(PROTECTED_SECTION_BEGIN, content, re.MULTILINE) is not None
        has_protected_end = re.search(PROTECTED_SECTION_END, content, re.MULTILINE) is not None
        
        if has_protected_begin and has_protected_end:
            if verbose:
                print(f"{GREEN}Файл уже имеет защищенный раздел: {file_path}{ENDC}")
            return False, "Файл уже имеет защищенный раздел"
        
        # Извлекаем информацию для метаданных
        title = extract_title_from_content(content)
        standard_id = extract_standard_id_from_filename(file_path)
        directory_number = get_standard_directory_number(file_path)
        
        if not standard_id and directory_number:
            standard_id = f"{directory_number}.0"  # Примерный номер на основе директории
        
        logical_id = "standard:" + (title.lower().replace(' ', '_') if title else os.path.basename(file_path).replace('.md', ''))
        current_date = datetime.datetime.now().strftime("%d %b %Y, %H:%M CET")
        
        # Создаем шаблон защищенного раздела
        protected_template = f"""<!-- 🔒 PROTECTED SECTION: BEGIN -->
standard_id: {standard_id or "N/A (требуется указать)"}
logical_id: {logical_id}
updated: {current_date} by AI Assistant  
previous version: N/A (первая версия с метаданными)  
based on: [Task Master Standard](abstract://standard:task_master_standard), версия 1.4  
version: 1.0  
status: Active
<!-- 🔒 PROTECTED SECTION: END -->

---"""
        
        # Вставляем шаблон после заголовка
        if title and content.startswith(f"# {title}"):
            new_content = content.replace(f"# {title}", f"# {title}\n\n{protected_template}", 1)
        else:
            new_content = f"{content}\n\n{protected_template}"
        
        if apply:
            # Создаем резервную копию
            backup_path = create_backup(file_path)
            
            # Записываем изменения
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"{GREEN}Добавлен защищенный раздел в: {file_path}{ENDC}")
            print(f"{BLUE}Создана резервная копия: {backup_path}{ENDC}")
            return True, "Добавлен защищенный раздел и создана резервная копия"
        else:
            print(f"{YELLOW}Необходимо добавить защищенный раздел в: {file_path}{ENDC}")
            return True, "Необходимо добавить защищенный раздел"
            
    except Exception as e:
        print(f"{RED}Ошибка при обработке файла {file_path}: {str(e)}{ENDC}")
        return False, f"Ошибка: {str(e)}"

def add_required_fields(file_path, apply=False, verbose=False):
    """Добавляет обязательные поля в защищенный раздел, если их нет."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Извлекаем защищенный раздел
        protected_match = re.search(f"{PROTECTED_SECTION_BEGIN}(.*?){PROTECTED_SECTION_END}", content, re.DOTALL)
        if not protected_match:
            return False, "Отсутствует защищенный раздел"
        
        protected_content = protected_match.group(1)
        
        # Проверяем наличие обязательных полей
        has_updated = re.search(r'updated:', protected_content, re.MULTILINE) is not None
        has_version = re.search(r'version:', protected_content, re.MULTILINE) is not None
        has_status = re.search(r'status:', protected_content, re.MULTILINE) is not None
        
        if has_updated and has_version and has_status:
            if verbose:
                print(f"{GREEN}Все обязательные поля присутствуют в: {file_path}{ENDC}")
            return False, "Все обязательные поля присутствуют"
        
        # Добавляем отсутствующие поля
        new_protected_content = protected_content
        current_date = datetime.datetime.now().strftime("%d %b %Y, %H:%M CET")
        
        if not has_updated:
            new_protected_content += f"\nupdated: {current_date} by AI Assistant  "
        
        if not has_version:
            new_protected_content += f"\nversion: 1.0  "
        
        if not has_status:
            new_protected_content += f"\nstatus: Active  "
        
        # Заменяем защищенный раздел
        new_content = content.replace(
            protected_match.group(0),
            f"{PROTECTED_SECTION_BEGIN}{new_protected_content}{PROTECTED_SECTION_END}"
        )
        
        if apply:
            # Создаем резервную копию
            backup_path = create_backup(file_path)
            
            # Записываем изменения
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"{GREEN}Добавлены обязательные поля в: {file_path}{ENDC}")
            print(f"{BLUE}Создана резервная копия: {backup_path}{ENDC}")
            return True, "Добавлены обязательные поля и создана резервная копия"
        else:
            fields = []
            if not has_updated: fields.append("updated")
            if not has_version: fields.append("version")
            if not has_status: fields.append("status")
            print(f"{YELLOW}Необходимо добавить поля {', '.join(fields)} в: {file_path}{ENDC}")
            return True, f"Необходимо добавить поля: {', '.join(fields)}"
            
    except Exception as e:
        print(f"{RED}Ошибка при обработке полей в файле {file_path}: {str(e)}{ENDC}")
        return False, f"Ошибка: {str(e)}"

def add_required_sections(file_path, apply=False, verbose=False):
    """Добавляет обязательные разделы в стандарт, если их нет."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        missing_sections = []
        for section in REQUIRED_SECTIONS:
            if not re.search(re.escape(section), content, re.MULTILINE):
                missing_sections.append(section)
        
        if not missing_sections:
            if verbose:
                print(f"{GREEN}Все обязательные разделы присутствуют в: {file_path}{ENDC}")
            return False, "Все обязательные разделы присутствуют"
        
        # Находим метку --- после защищенного раздела или конец файла
        delimiter_match = re.search(r'<!-- 🔒 PROTECTED SECTION: END -->\s*\n\s*---', content)
        insertion_point = delimiter_match.end() if delimiter_match else len(content)
        
        # Добавляем отсутствующие разделы
        section_content = "\n\n"
        for section in missing_sections:
            section_content += f"{section}\n\nЭтот раздел был автоматически добавлен и требует заполнения.\n\n"
        
        new_content = content[:insertion_point] + section_content + content[insertion_point:]
        
        if apply:
            # Создаем резервную копию
            backup_path = create_backup(file_path)
            
            # Записываем изменения
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"{GREEN}Добавлены разделы {', '.join(missing_sections)} в: {file_path}{ENDC}")
            print(f"{BLUE}Создана резервная копия: {backup_path}{ENDC}")
            return True, f"Добавлены разделы и создана резервная копия"
        else:
            print(f"{YELLOW}Необходимо добавить разделы {', '.join(missing_sections)} в: {file_path}{ENDC}")
            return True, f"Необходимо добавить разделы: {', '.join(missing_sections)}"
            
    except Exception as e:
        print(f"{RED}Ошибка при обработке разделов в файле {file_path}: {str(e)}{ENDC}")
        return False, f"Ошибка: {str(e)}"

def process_standards(base_dir=".", apply=False, verbose=False):
    """Обрабатывает все стандарты в указанной директории."""
    # Получаем список всех markdown-файлов
    if os.path.isdir(base_dir):
        md_files = glob.glob(os.path.join(base_dir, "**/*.md"), recursive=True)
    else:
        md_files = [base_dir] if base_dir.endswith('.md') else []
    
    if not md_files:
        print(f"{YELLOW}Не найдено .md файлов в директории: {base_dir}{ENDC}")
        return
    
    print(f"{BLUE}Начинаю обработку {len(md_files)} файлов в директории: {base_dir}{ENDC}")
    
    stats = {
        "total": len(md_files),
        "protected_section_added": 0,
        "fields_added": 0,
        "sections_added": 0,
        "errors": 0,
        "skipped": 0
    }
    
    for file_path in md_files:
        if "archive" in file_path.lower():
            if verbose:
                print(f"{BLUE}Пропущен архивный файл: {file_path}{ENDC}")
            stats["skipped"] += 1
            continue
        
        print(f"\nОбработка файла: {file_path}")
        
        # 1. Добавляем защищенный раздел, если его нет
        changed, message = add_protected_section(file_path, apply, verbose)
        if changed and apply:
            stats["protected_section_added"] += 1
        
        # 2. Добавляем обязательные поля, если их нет
        changed, message = add_required_fields(file_path, apply, verbose)
        if changed and apply:
            stats["fields_added"] += 1
        
        # 3. Добавляем обязательные разделы, если их нет
        changed, message = add_required_sections(file_path, apply, verbose)
        if changed and apply:
            stats["sections_added"] += 1
    
    print(f"\n{BOLD}Статистика обработки:{ENDC}")
    print(f"Всего файлов: {stats['total']}")
    print(f"Пропущено архивных файлов: {stats['skipped']}")
    if apply:
        print(f"Добавлено защищенных разделов: {stats['protected_section_added']}")
        print(f"Добавлено обязательных полей: {stats['fields_added']}")
        print(f"Добавлено обязательных разделов: {stats['sections_added']}")
    else:
        print(f"{YELLOW}Запуск в режиме проверки. Используйте --apply для применения изменений.{ENDC}")

def main():
    """Основная функция скрипта."""
    parser = argparse.ArgumentParser(description='Исправляет проблемы в стандартах.')
    parser.add_argument('directory', nargs='?', default='.', 
                        help='Директория со стандартами (по умолчанию: текущая директория)')
    parser.add_argument('--apply', action='store_true', 
                        help='Применить исправления (по умолчанию: только показать проблемы)')
    parser.add_argument('--verbose', action='store_true', 
                        help='Подробный вывод о всех операциях')
    
    args = parser.parse_args()
    process_standards(args.directory, args.apply, args.verbose)

if __name__ == "__main__":
    main()