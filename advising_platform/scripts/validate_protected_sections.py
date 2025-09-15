#!/usr/bin/env python3
"""
Инструмент для проверки защищенных разделов в документах стандартов.
Проверяет наличие, целостность и правильное форматирование защищенных разделов.

Защищенные разделы обозначаются маркерами:
<!-- 🔒 PROTECTED SECTION: BEGIN -->
[защищенный контент]
<!-- 🔒 PROTECTED SECTION: END -->

Использование:
  python validate_protected_sections.py [путь к файлу или директории]
"""

import os
import sys
import re
import argparse
from colorama import init, Fore, Style
from typing import Dict, List, Tuple, Optional, Union, cast

# Инициализация colorama для поддержки цветов в Windows
init()

# Регулярное выражение для поиска защищенных разделов
PROTECTED_BEGIN = r'<!--\s*🔒\s*PROTECTED\s*SECTION:\s*BEGIN\s*-->'
PROTECTED_END = r'<!--\s*🔒\s*PROTECTED\s*SECTION:\s*END\s*-->'

# Обязательные метаданные, которые должны быть в защищенном разделе
REQUIRED_METADATA = [
    'updated',
    'version',
    'status'
]

# Дополнительные метаданные, которые могут быть в защищенном разделе
OPTIONAL_METADATA = [
    'based on',
    'previous version',
    'integrated',
    'author'
]

class ProtectedSectionValidator:
    """Класс для проверки защищенных разделов в документах."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def reset(self):
        """Сбрасывает ошибки и предупреждения."""
        self.errors = []
        self.warnings = []
    
    def validate_file(self, file_path: str) -> Tuple[bool, List[str], List[str]]:
        """
        Проверяет защищенные разделы в файле.
        
        Args:
            file_path: Путь к файлу для проверки
            
        Returns:
            Tuple[bool, List[str], List[str]]: (успех, ошибки, предупреждения)
        """
        self.reset()
        
        # Проверка существования файла
        if not os.path.exists(file_path):
            self.errors.append(f"Файл {file_path} не существует")
            return False, self.errors, self.warnings
        
        # Проверка markdown файла
        if not file_path.endswith('.md'):
            self.warnings.append(f"Файл {file_path} не является markdown файлом")
            return True, self.errors, self.warnings
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Поиск начала и конца защищенных разделов
            begin_matches = list(re.finditer(PROTECTED_BEGIN, content, re.IGNORECASE))
            end_matches = list(re.finditer(PROTECTED_END, content, re.IGNORECASE))
            
            # Проверка наличия защищенных разделов
            if not begin_matches:
                self.errors.append(f"В файле {file_path} не найдено начало защищенного раздела")
                return False, self.errors, self.warnings
                
            if not end_matches:
                self.errors.append(f"В файле {file_path} не найдено окончание защищенного раздела")
                return False, self.errors, self.warnings
                
            # Проверка соответствия количества маркеров начала и конца
            if len(begin_matches) != len(end_matches):
                self.errors.append(f"В файле {file_path} количество маркеров начала ({len(begin_matches)}) не соответствует количеству маркеров конца ({len(end_matches)})")
                return False, self.errors, self.warnings
            
            # Проверка правильного порядка маркеров (начало должно быть перед концом)
            for i in range(len(begin_matches)):
                begin_pos = begin_matches[i].start()
                end_pos = end_matches[i].start()
                
                if begin_pos >= end_pos:
                    self.errors.append(f"В файле {file_path} маркер начала защищенного раздела находится после маркера конца")
                    return False, self.errors, self.warnings
            
            # Проверка содержимого первого защищенного раздела (метаданные)
            if len(begin_matches) > 0:
                protected_content = content[begin_matches[0].end():end_matches[0].start()].strip()
                # Проверка обязательных метаданных
                for metadata in REQUIRED_METADATA:
                    if not re.search(rf'{metadata}:', protected_content, re.IGNORECASE):
                        self.errors.append(f"В файле {file_path} отсутствует обязательное поле '{metadata}' в защищенном разделе")
                
                # Проверка регистра полей метаданных (должны быть в нижнем регистре)
                metadata_lines = protected_content.split('\n')
                for line in metadata_lines:
                    if ':' in line:
                        field = line.split(':', 1)[0].strip()
                        if not field.islower():
                            self.errors.append(f"В файле {file_path} поле '{field}' должно быть в нижнем регистре")
            
            # Проверка лицензии (должна быть в защищенном разделе)
            license_begin = None
            license_end = None
            
            if len(begin_matches) >= 2:
                # Проверяем последний защищенный раздел на наличие лицензии
                last_protected_content = content[begin_matches[-1].end():end_matches[-1].start()].strip()
                if "лицензия" in last_protected_content.lower() or "license" in last_protected_content.lower():
                    license_begin = begin_matches[-1]
                    license_end = end_matches[-1]
            
            if not license_begin:
                self.warnings.append(f"В файле {file_path} не найден защищенный раздел с лицензией")
            
            return len(self.errors) == 0, self.errors, self.warnings
            
        except Exception as e:
            self.errors.append(f"Ошибка при проверке файла {file_path}: {str(e)}")
            return False, self.errors, self.warnings
    
    def scan_directory(self, directory: str, recursive: bool = False) -> Dict[str, Union[List[str], Dict[str, Dict[str, List[str]]]]]:
        """
        Сканирует директорию на наличие markdown файлов и проверяет в них защищенные разделы.
        
        Args:
            directory: Путь к директории для сканирования
            recursive: Рекурсивный поиск во вложенных директориях
            
        Returns:
            Dict содержащий списки валидных и невалидных файлов с ошибками
        """
        results: Dict[str, Union[List[str], Dict[str, Dict[str, List[str]]]]] = {
            "valid": [], 
            "invalid": {}
        }
        
        for root, dirs, files in os.walk(directory):
            # Если не рекурсивный поиск, пропускаем вложенные директории
            if not recursive and root != directory:
                continue
            
            # Находим все markdown файлы
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    
                    is_valid, errors, warnings = self.validate_file(file_path)
                    
                    if is_valid:
                        results["valid"].append(file_path)  # type: ignore
                    else:
                        if "invalid" in results:
                            invalid_dict = results["invalid"]  # type: ignore
                            if isinstance(invalid_dict, dict):
                                invalid_dict[file_path] = {
                                    "errors": errors,
                                    "warnings": warnings
                                }
        
        return results

def print_results(results: Dict[str, Union[List[str], Dict[str, Dict[str, List[str]]]]]) -> None:
    """
    Выводит результаты проверки в удобном для чтения формате.
    
    Args:
        results: Результаты проверки
    """
    print(f"\n{Fore.CYAN}=== Результаты проверки защищенных разделов ==={Style.RESET_ALL}\n")
    
    # Вывод валидных файлов
    print(f"{Fore.GREEN}Валидные файлы ({len(results['valid'])}):${Style.RESET_ALL}")
    for file_path in results['valid']:
        print(f"  {Fore.GREEN}✓ {os.path.basename(file_path)}{Style.RESET_ALL}")
    print()
    
    # Вывод невалидных файлов
    invalid_count = len(results['invalid'])
    if invalid_count > 0:
        print(f"{Fore.RED}Невалидные файлы ({invalid_count}):${Style.RESET_ALL}")
        for file_path, issues in results['invalid'].items():
            print(f"  {Fore.RED}✗ {os.path.basename(file_path)}{Style.RESET_ALL}")
            
            if 'errors' in issues:
                for error in issues['errors']:
                    print(f"    {Fore.RED}• {error}{Style.RESET_ALL}")
            
            if 'warnings' in issues:
                for warning in issues['warnings']:
                    print(f"    {Fore.YELLOW}• {warning}{Style.RESET_ALL}")
        print()
    
    # Итоговая статистика
    total_files = len(results['valid']) + invalid_count
    print(f"{Fore.CYAN}Всего проверено файлов: {total_files}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Валидных файлов: {len(results['valid'])} ({len(results['valid'])/total_files*100:.1f}%){Style.RESET_ALL}")
    print(f"{Fore.RED}Невалидных файлов: {invalid_count} ({invalid_count/total_files*100:.1f}%){Style.RESET_ALL}")
    
def main():
    parser = argparse.ArgumentParser(description="Проверка защищенных разделов в документах стандартов")
    parser.add_argument("path", help="Путь к файлу или директории для проверки")
    parser.add_argument("-r", "--recursive", action="store_true", help="Рекурсивный поиск во вложенных директориях")
    
    args = parser.parse_args()
    path = args.path
    
    validator = ProtectedSectionValidator()
    
    # Проверка пути
    if not os.path.exists(path):
        print(f"{Fore.RED}Ошибка: {path} не существует{Style.RESET_ALL}")
        return 1
    
    # Проверка файла или директории
    if os.path.isfile(path):
        is_valid, errors, warnings = validator.validate_file(path)
        
        if is_valid:
            print(f"{Fore.GREEN}Файл {path} валиден{Style.RESET_ALL}")
            for warning in warnings:
                print(f"{Fore.YELLOW}• {warning}{Style.RESET_ALL}")
            return 0
        else:
            print(f"{Fore.RED}Файл {path} невалиден:{Style.RESET_ALL}")
            for error in errors:
                print(f"{Fore.RED}• {error}{Style.RESET_ALL}")
            for warning in warnings:
                print(f"{Fore.YELLOW}• {warning}{Style.RESET_ALL}")
            return 1
    else:
        print(f"{Fore.CYAN}Сканирование директории: {path} {'(рекурсивно)' if args.recursive else ''}{Style.RESET_ALL}")
        results = validator.scan_directory(path, args.recursive)
        print_results(results)
        
        # Возвращаем статус ошибки, если есть невалидные файлы
        return 1 if results['invalid'] else 0

if __name__ == "__main__":
    sys.exit(main())