#!/usr/bin/env python3
"""
Скрипт для проверки соответствия имен файлов стандарту TaskMaster.
Стандарт имен файлов:
[номер раздела].[номер подраздела] [тип документа] [дата] [время] [часовой пояс] by [автор].md

Примеры правильных имен:
0.0 task master 14 may 2025 0500 cet by ai assistant.md
1.1 ai incident standard 14 may 2025 0505 cet by ai assistant.md
2.3 ux checklist 15 may 2025 1430 cet by design team.md
"""

import os
import sys
import re
import argparse
from colorama import init, Fore, Style

# Инициализация colorama для поддержки цветов в Windows
init()

# Регулярное выражение для проверки соответствия имени файла стандарту
FILENAME_PATTERN = r'^(\d+)\.(\d+)\s+([a-z\s-_]+)\s+(\d{1,2}\s+[a-z]+\s+\d{4})\s+(\d{4})\s+([a-z]{2,4})\s+by\s+([a-z\s]+)\.md$'

def validate_filename(filename):
    """Проверяет, соответствует ли имя файла стандарту TaskMaster."""
    match = re.match(FILENAME_PATTERN, filename, re.IGNORECASE)
    if not match:
        return False, "Имя файла не соответствует шаблону"
    
    # Проверяем регистр символов
    if not filename.islower():
        return False, "Имя файла содержит заглавные буквы"
    
    return True, "OK"

def scan_directory(directory, recursive=False):
    """
    Сканирует указанную директорию на наличие markdown файлов.
    Проверяет каждый файл на соответствие стандарту.
    """
    results = {"valid": [], "invalid": []}
    
    for root, dirs, files in os.walk(directory):
        # Если не рекурсивный поиск, пропускаем вложенные директории
        if not recursive and root != directory:
            continue
        
        # Находим все markdown файлы
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                is_valid, reason = validate_filename(file)
                
                if is_valid:
                    results["valid"].append((file_path, reason))
                else:
                    results["invalid"].append((file_path, reason))
    
    return results

def print_results(results):
    """Выводит результаты проверки в удобном формате."""
    print(f"\n{Fore.CYAN}=== Результаты проверки имен файлов ==={Style.RESET_ALL}\n")
    
    if results["valid"]:
        print(f"{Fore.GREEN}Допустимые имена файлов ({len(results['valid'])}):${Style.RESET_ALL}")
        for file_path, reason in results["valid"]:
            print(f"  {Fore.GREEN}✓ {os.path.basename(file_path)}{Style.RESET_ALL}")
        print()
    
    if results["invalid"]:
        print(f"{Fore.RED}Недопустимые имена файлов ({len(results['invalid'])}):${Style.RESET_ALL}")
        for file_path, reason in results["invalid"]:
            print(f"  {Fore.RED}✗ {os.path.basename(file_path)}: {reason}{Style.RESET_ALL}")
            # Предлагаем корректное имя
            suggest_correct_name(file_path)
        print()
    
    print(f"{Fore.CYAN}Всего файлов: {len(results['valid']) + len(results['invalid'])}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Валидных: {len(results['valid'])}{Style.RESET_ALL}")
    print(f"{Fore.RED}Невалидных: {len(results['invalid'])}{Style.RESET_ALL}")

def suggest_correct_name(file_path):
    """Предлагает корректное имя файла на основе текущего имени."""
    filename = os.path.basename(file_path)
    
    # Попытка извлечь основные компоненты из имени для корректировки
    # Этот код очень упрощенный и требует доработки для реальных случаев
    
    # Пример: преобразование "1.5 Ticket Standard 14 May 2025.md" в корректный формат
    # 1.5 ticket standard 14 may 2025 1200 cet by ai assistant.md
    
    parts = filename.lower().split()
    if len(parts) >= 3 and re.match(r'^\d+\.\d+$', parts[0]):
        # Предположим, что у нас есть номер раздела, тип документа и возможно дата
        section = parts[0]
        doc_type = ' '.join(parts[1:-3] if len(parts) > 4 else parts[1:])
        
        # Значения по умолчанию
        date = "DD month YYYY"
        time = "HHMM"
        timezone = "cet"
        author = "author"
        
        # Ищем дату, если она есть
        date_match = re.search(r'(\d{1,2}\s+[a-z]+\s+\d{4})', filename.lower())
        if date_match:
            date = date_match.group(1)
        
        suggested_name = f"{section} {doc_type} {date} {time} {timezone} by {author}.md"
        
        print(f"  {Fore.YELLOW}  Предлагаемое имя: {suggested_name}{Style.RESET_ALL}")

def main():
    parser = argparse.ArgumentParser(description="Проверка имен файлов на соответствие стандарту TaskMaster")
    parser.add_argument("directory", help="Директория для сканирования")
    parser.add_argument("-r", "--recursive", action="store_true", help="Рекурсивно сканировать вложенные директории")
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.directory):
        print(f"{Fore.RED}Ошибка: {args.directory} не является директорией{Style.RESET_ALL}")
        sys.exit(1)
    
    print(f"{Fore.CYAN}Сканирование директории: {args.directory} {'(рекурсивно)' if args.recursive else ''}{Style.RESET_ALL}")
    results = scan_directory(args.directory, args.recursive)
    print_results(results)
    
    # Вернем код ошибки, если есть недопустимые файлы
    return 1 if results["invalid"] else 0

if __name__ == "__main__":
    sys.exit(main())