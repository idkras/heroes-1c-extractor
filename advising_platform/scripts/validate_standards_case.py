#!/usr/bin/env python3
"""
Скрипт для валидации соответствия стандартов TaskMaster требованиям к регистру букв.
Проверяет заголовки и метаданные на соответствие стандарту (нижний регистр).

Использование:
    python validate_standards_case.py [путь к директории]

Пример:
    python validate_standards_case.py "../advising standards .md/"
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

STANDARDS_DIR = "../advising standards .md/" if len(sys.argv) < 2 else sys.argv[1]
EXCLUDE_DIRS = ["archive", "backups", "backups_20250514"]

class StandardValidator:
    """Класс для валидации стандартов."""
    
    def __init__(self, standards_dir: str):
        """Инициализация валидатора.
        
        Args:
            standards_dir: Путь к директории со стандартами
        """
        self.standards_dir = standards_dir
        self.issues = []
    
    def validate_all(self) -> List[Dict]:
        """Валидирует все стандарты в директории.
        
        Returns:
            Список проблем, обнаруженных в стандартах
        """
        all_md_files = self._find_all_markdown_files()
        print(f"Найдено {len(all_md_files)} markdown-файлов для проверки.")
        
        for file_path in all_md_files:
            self._validate_file(file_path)
            
        return self.issues
    
    def _find_all_markdown_files(self) -> List[str]:
        """Находит все markdown-файлы в директории стандартов.
        
        Returns:
            Список путей к markdown-файлам
        """
        markdown_files = []
        
        for root, dirs, files in os.walk(self.standards_dir):
            # Исключаем директории архивов и бэкапов
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                if file.endswith(".md"):
                    full_path = os.path.join(root, file)
                    markdown_files.append(full_path)
        
        return markdown_files
    
    def _validate_file(self, file_path: str) -> None:
        """Валидирует отдельный файл стандарта.
        
        Args:
            file_path: Путь к файлу стандарта
        """
        print(f"Проверка файла: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Проверяем заголовок
            title_issues = self._validate_title(content, file_path)
            if title_issues:
                self.issues.extend(title_issues)
            
            # Проверяем метаданные
            metadata_issues = self._validate_metadata(content, file_path)
            if metadata_issues:
                self.issues.extend(metadata_issues)
                
        except Exception as e:
            self.issues.append({
                "file": file_path,
                "type": "error",
                "description": f"Ошибка при обработке файла: {str(e)}"
            })
    
    def _validate_title(self, content: str, file_path: str) -> List[Dict]:
        """Валидирует заголовок стандарта.
        
        Args:
            content: Содержимое файла
            file_path: Путь к файлу
            
        Returns:
            Список проблем, связанных с заголовком
        """
        issues = []
        
        # Ищем заголовок первого уровня
        title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        if not title_match:
            issues.append({
                "file": file_path,
                "type": "title_missing",
                "description": "Заголовок первого уровня не найден"
            })
            return issues
            
        title = title_match.group(1)
        
        # Проверяем наличие слов с верхним регистром (исключая эмодзи)
        uppercase_words = re.findall(r'[A-Z][a-zA-Z]*', title)
        if uppercase_words:
            issues.append({
                "file": file_path,
                "type": "title_case",
                "description": f"Заголовок содержит слова с верхним регистром: {', '.join(uppercase_words)}",
                "position": title_match.start(),
                "original": title,
                "suggestion": title.lower()
            })
            
        return issues
    
    def _validate_metadata(self, content: str, file_path: str) -> List[Dict]:
        """Валидирует метаданные стандарта.
        
        Args:
            content: Содержимое файла
            file_path: Путь к файлу
            
        Returns:
            Список проблем, связанных с метаданными
        """
        issues = []
        
        # Ищем защищенный раздел с метаданными
        metadata_match = re.search(r'<!-- 🔒 PROTECTED SECTION: BEGIN -->(.*?)<!-- 🔒 PROTECTED SECTION: END -->', 
                                  content, re.DOTALL)
        
        if not metadata_match:
            # Проверяем старый формат метаданных
            metadata_lines = re.findall(r'^(updated|based on|previous version|integrated|version|status):(.+?)$', 
                                      content, re.MULTILINE)
            
            if not metadata_lines:
                issues.append({
                    "file": file_path,
                    "type": "metadata_missing",
                    "description": "Метаданные не найдены"
                })
                return issues
        else:
            metadata_text = metadata_match.group(1)
            
            # Проверяем строки метаданных на наличие слов с верхним регистром
            for line in metadata_text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                # Пропускаем имена пользователей и даты
                if "by " in line:
                    name_part = line.split("by ")[-1]
                    line_without_name = line.replace(name_part, "")
                    
                    uppercase_words = re.findall(r'[A-Z][a-zA-Z]+', line_without_name)
                    if uppercase_words:
                        issues.append({
                            "file": file_path,
                            "type": "metadata_case",
                            "description": f"Метаданные содержат слова с верхним регистром: {', '.join(uppercase_words)}",
                            "original": line,
                            "suggestion": line.lower()
                        })
                else:
                    uppercase_words = re.findall(r'[A-Z][a-zA-Z]+', line)
                    if uppercase_words:
                        issues.append({
                            "file": file_path,
                            "type": "metadata_case",
                            "description": f"Метаданные содержат слова с верхним регистром: {', '.join(uppercase_words)}",
                            "original": line,
                            "suggestion": line.lower()
                        })
            
        return issues
    
    def print_report(self) -> None:
        """Выводит отчет о найденных проблемах."""
        if not self.issues:
            print("\n✅ Проблем не обнаружено. Все стандарты соответствуют требованиям к регистру букв.")
            return
            
        print(f"\n❌ Обнаружено {len(self.issues)} проблем:")
        
        by_file = {}
        for issue in self.issues:
            file_path = issue["file"]
            if file_path not in by_file:
                by_file[file_path] = []
            by_file[file_path].append(issue)
            
        for file_path, file_issues in by_file.items():
            print(f"\n📄 {os.path.basename(file_path)}:")
            for issue in file_issues:
                print(f"  • {issue['description']}")
                if "suggestion" in issue:
                    print(f"    Текущее: {issue['original']}")
                    print(f"    Рекомендуемое: {issue['suggestion']}")
                    
        print("\nⓘ Для исправления проблем обновите заголовки и метаданные, используя нижний регистр.")

def main():
    validator = StandardValidator(STANDARDS_DIR)
    validator.validate_all()
    validator.print_report()

if __name__ == "__main__":
    main()