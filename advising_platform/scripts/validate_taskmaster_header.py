#!/usr/bin/env python3
"""
Валидатор заголовков документов по стандарту TaskMaster.

Проверяет соответствие метаданных заголовка стандарту TaskMaster,
включая наличие обязательных полей "updated", "based on", "integrated".

Использование:
    python validate_taskmaster_header.py <путь к файлу или директории>
"""

import os
import re
import sys
import argparse
from typing import List, Dict, Tuple, Optional, Set


class TaskMasterHeaderValidator:
    """Класс для валидации заголовков документов по стандарту TaskMaster."""

    # Обязательные поля метаданных
    REQUIRED_FIELDS = {"updated", "based on"}
    
    # Рекомендуемые поля метаданных
    RECOMMENDED_FIELDS = {"integrated", "status"}
    
    # Регулярные выражения для проверки полей
    FIELD_PATTERNS = {
        "updated": r"^updated: \d{1,2} [a-z]{3} \d{4}, \d{2}:\d{2} CET by .+$",
        "based on": r"^based on: .+, version \d{1,2} [a-z]{3} \d{4}, \d{2}:\d{2} CET$",
        "integrated": r"^integrated: .+$",
        "status": r"^status: (In Progress|Draft|Review|Approved|Completed|Archived)$"
    }

    def __init__(self, verbose: bool = False):
        """
        Инициализирует валидатор.
        
        Args:
            verbose: Включает подробный вывод результатов проверки
        """
        self.verbose = verbose
        self.compiled_patterns = {
            field: re.compile(pattern, re.IGNORECASE) 
            for field, pattern in self.FIELD_PATTERNS.items()
        }

    def extract_metadata_from_content(self, content: str) -> Dict[str, str]:
        """
        Извлекает метаданные из содержимого документа.
        
        Args:
            content: Содержимое документа
            
        Returns:
            Dict[str, str]: Словарь с извлеченными метаданными
        """
        metadata = {}
        
        # Проверяем наличие заголовка с эмодзи
        title_match = re.search(r'^#\s+[^\n]*', content)
        if title_match:
            metadata["title"] = title_match.group(0).strip()
            
            # Проверяем наличие эмодзи в заголовке
            emoji_match = re.search(r'#\s+([^\w\s])', metadata["title"])
            if emoji_match:
                metadata["has_emoji"] = True
            else:
                metadata["has_emoji"] = False
        
        # Извлекаем метаданные из верхней части документа
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if i == 0 or not line.strip():
                continue
                
            # Ищем разделитель --- который должен быть после метаданных
            if line.strip() == "---":
                metadata["has_separator"] = True
                break
                
            # Ищем пары ключ-значение в формате "ключ: значение"
            parts = line.split(":", 1)
            if len(parts) == 2:
                key = parts[0].strip().lower()
                value = parts[1].strip()
                metadata[key] = value
        
        # Если мы не нашли разделитель, отмечаем это
        if "has_separator" not in metadata:
            metadata["has_separator"] = False
            
        return metadata

    def validate_metadata(self, metadata: Dict[str, str]) -> Tuple[bool, Dict[str, bool], Set[str]]:
        """
        Проверяет метаданные на соответствие стандарту.
        
        Args:
            metadata: Словарь с метаданными
            
        Returns:
            Tuple[bool, Dict[str, bool], Set[str]]: 
                - Общий результат проверки
                - Результаты проверок по полям
                - Набор отсутствующих обязательных полей
        """
        field_results = {}
        missing_required = set()
        
        # Проверяем наличие и формат обязательных полей
        for field in self.REQUIRED_FIELDS:
            if field not in metadata:
                field_results[field] = False
                missing_required.add(field)
            else:
                pattern = self.compiled_patterns.get(field)
                if pattern and not pattern.match(metadata[field]):
                    field_results[field] = False
                    # Поле есть, но формат неправильный
                else:
                    field_results[field] = True
        
        # Проверяем формат рекомендуемых полей, если они есть
        for field in self.RECOMMENDED_FIELDS:
            if field in metadata:
                pattern = self.compiled_patterns.get(field)
                if pattern and not pattern.match(metadata[field]):
                    field_results[field] = False
                else:
                    field_results[field] = True
        
        # Проверяем наличие эмодзи в заголовке
        if "has_emoji" in metadata:
            field_results["emoji_in_title"] = metadata["has_emoji"]
        
        # Проверяем наличие разделителя после метаданных
        if "has_separator" in metadata:
            field_results["separator"] = metadata["has_separator"]
        
        # Документ валиден, если все обязательные поля есть и они валидны
        is_valid = len(missing_required) == 0 and all(
            field_results.get(field, False) for field in self.REQUIRED_FIELDS
        )
        
        return is_valid, field_results, missing_required

    def validate_document(self, filepath: str) -> Tuple[bool, Dict[str, bool], Dict[str, str], Set[str]]:
        """
        Проверяет документ на соответствие стандарту TaskMaster.
        
        Args:
            filepath: Путь к документу
            
        Returns:
            Tuple[bool, Dict[str, bool], Dict[str, str], Set[str]]:
                - Общий результат проверки
                - Результаты проверок по полям
                - Извлеченные метаданные
                - Набор отсутствующих обязательных полей
        """
        if not os.path.isfile(filepath) or not filepath.lower().endswith('.md'):
            return False, {}, {}, set()
            
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
        except Exception as e:
            print(f"Ошибка при чтении файла {filepath}: {e}")
            return False, {}, {}, set()
            
        metadata = self.extract_metadata_from_content(content)
        is_valid, field_results, missing_required = self.validate_metadata(metadata)
        
        return is_valid, field_results, metadata, missing_required

    def validate_directory(self, dirpath: str, recursive: bool = True) -> List[Tuple[str, bool, Dict[str, bool], Dict[str, str], Set[str]]]:
        """
        Проверяет все документы в директории на соответствие стандарту TaskMaster.
        
        Args:
            dirpath: Путь к директории
            recursive: Включает рекурсивную проверку поддиректорий
            
        Returns:
            List[Tuple[str, bool, Dict[str, bool], Dict[str, str], Set[str]]]: 
                Список результатов проверки для каждого документа
        """
        results = []
        
        for root, dirs, files in os.walk(dirpath):
            for file in files:
                if file.lower().endswith('.md'):
                    filepath = os.path.join(root, file)
                    is_valid, field_results, metadata, missing_required = self.validate_document(filepath)
                    results.append((filepath, is_valid, field_results, metadata, missing_required))
                    
            if not recursive:
                break
                
        return results

    def print_validation_result(self, filepath: str, is_valid: bool, 
                              field_results: Dict[str, bool], 
                              metadata: Dict[str, str],
                              missing_required: Set[str]) -> None:
        """
        Выводит результат валидации документа.
        
        Args:
            filepath: Путь к документу
            is_valid: Общий результат проверки
            field_results: Результаты проверок по полям
            metadata: Извлеченные метаданные
            missing_required: Набор отсутствующих обязательных полей
        """
        filename = os.path.basename(filepath)
        
        if is_valid:
            print(f"✅ {filepath}")
            if self.verbose:
                print("  Метаданные:")
                for field, value in metadata.items():
                    if field not in ("has_emoji", "has_separator"):
                        print(f"    {field}: {value}")
                
                print("  Проверки:")
                for field, result in field_results.items():
                    status = "✅" if result else "❌"
                    print(f"    {status} {field}")
        else:
            print(f"❌ {filepath}")
            if missing_required:
                print(f"  Отсутствуют обязательные поля: {', '.join(missing_required)}")
            
            print("  Проверки:")
            for field, result in field_results.items():
                status = "✅" if result else "❌"
                print(f"    {status} {field}")
            
            if self.verbose:
                print("  Найденные метаданные:")
                for field, value in metadata.items():
                    if field not in ("has_emoji", "has_separator") and field in metadata:
                        print(f"    {field}: {value}")

    def generate_header_template(self, title: str = "Заголовок документа", 
                               emoji: str = "📝", 
                               based_on: str = "Master Task Standard, version 10 may 2025, 17:00 CET",
                               author: str = "Илья Красинский",
                               integrated: str = "None",
                               status: str = "Draft") -> str:
        """
        Генерирует шаблон заголовка по стандарту TaskMaster.
        
        Args:
            title: Заголовок документа
            emoji: Эмодзи для заголовка
            based_on: Базовый стандарт
            author: Автор документа
            integrated: Интегрированные стандарты
            status: Статус документа
            
        Returns:
            str: Шаблон заголовка
        """
        from datetime import datetime
        
        now = datetime.now()
        date_str = now.strftime("%d %b %Y").lower()
        time_str = now.strftime("%H:%M")
        
        header = f"# {emoji} {title}\n\n"
        header += f"updated: {date_str}, {time_str} CET by {author}  \n"
        header += f"based on: {based_on}  \n"
        
        if integrated and integrated.lower() != "none":
            header += f"integrated: {integrated}  \n"
            
        header += f"status: {status}\n\n"
        header += "---\n\n"
        
        return header


def main():
    parser = argparse.ArgumentParser(description='Валидатор заголовков по стандарту TaskMaster')
    parser.add_argument('path', help='Путь к файлу или директории для проверки')
    parser.add_argument('-r', '--recursive', action='store_true', 
                        help='Рекурсивная проверка директорий')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Подробный вывод результатов')
    parser.add_argument('-g', '--generate', action='store_true',
                        help='Генерировать шаблон заголовка')
    parser.add_argument('-t', '--title', default="Заголовок документа",
                        help='Заголовок документа (для генерации шаблона)')
    parser.add_argument('-e', '--emoji', default="📝",
                        help='Эмодзи для заголовка (для генерации шаблона)')
    parser.add_argument('-a', '--author', default="Илья Красинский",
                        help='Автор документа (для генерации шаблона)')
    parser.add_argument('-b', '--based-on', 
                        default="Master Task Standard, version 10 may 2025, 17:00 CET",
                        help='Базовый стандарт (для генерации шаблона)')
    parser.add_argument('-i', '--integrated', default="None",
                        help='Интегрированные стандарты (для генерации шаблона)')
    parser.add_argument('-s', '--status', default="Draft",
                        help='Статус документа (для генерации шаблона)')
    
    args = parser.parse_args()
    
    validator = TaskMasterHeaderValidator(verbose=args.verbose)
    
    if args.generate:
        header = validator.generate_header_template(
            title=args.title, 
            emoji=args.emoji,
            based_on=args.based_on,
            author=args.author,
            integrated=args.integrated,
            status=args.status
        )
        print("Шаблон заголовка:")
        print("-" * 40)
        print(header)
        print("-" * 40)
        return
    
    if os.path.isfile(args.path):
        is_valid, field_results, metadata, missing_required = validator.validate_document(args.path)
        validator.print_validation_result(args.path, is_valid, field_results, metadata, missing_required)
    
    elif os.path.isdir(args.path):
        results = validator.validate_directory(args.path, recursive=args.recursive)
        
        valid_count = sum(1 for _, is_valid, _, _, _ in results if is_valid)
        total_count = len(results)
        
        for filepath, is_valid, field_results, metadata, missing_required in results:
            validator.print_validation_result(filepath, is_valid, field_results, metadata, missing_required)
        
        print(f"\nИтого: {valid_count}/{total_count} документов соответствуют стандарту TaskMaster")
        
    else:
        print(f"Ошибка: путь {args.path} не существует")


if __name__ == "__main__":
    main()