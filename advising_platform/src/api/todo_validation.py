#!/usr/bin/env python3
"""
Модуль для валидации Todo документов.

Предоставляет функции для проверки корректности Todo документов
и их интеграции с системой архивации.
"""

import os
import re
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("todo_validation")

# Константы
TODO_DIR = "[todo · incidents]"
ARCHIVE_DIR = "[todo · incidents]/[archive]"
VALIDATION_SCRIPT = "scripts/validate_cache_system.py"

def validate_todo_structure(content: str) -> Tuple[bool, List[str]]:
    """
    Проверяет структуру Todo документа.
    
    Args:
        content: Содержимое документа
        
    Returns:
        Кортеж (валидно, список_ошибок)
    """
    errors = []
    
    # Проверяем наличие заголовка
    if not content.startswith("# "):
        errors.append("Документ должен начинаться с заголовка первого уровня (# )")
    
    # Проверяем наличие обязательных полей
    required_fields = ["date", "version", "author", "type", "category", "status", "priority"]
    
    # Извлекаем метаданные
    metadata_section = re.search(r"date:.*?(?=\n\n|\n##|\n\Z)", content, re.DOTALL)
    
    if not metadata_section:
        errors.append("Отсутствует секция метаданных")
    else:
        metadata_text = metadata_section.group(0)
        found_fields = []
        
        for field in required_fields:
            if re.search(rf"{field}:\s*.+", metadata_text):
                found_fields.append(field)
        
        missing_fields = [field for field in required_fields if field not in found_fields]
        if missing_fields:
            errors.append(f"Отсутствуют обязательные поля: {', '.join(missing_fields)}")
        
        # Проверяем правильность значения поля priority
        priority_match = re.search(r"priority:\s*(.+)", metadata_text)
        if priority_match:
            priority = priority_match.group(1).strip()
            valid_priorities = ["ALARM", "ASAP", "RESEARCH", "BLOCKER", "SMALL TASK", "EXCITER"]
            if priority not in valid_priorities:
                errors.append(f"Неверное значение поля priority: {priority}. Допустимые значения: {', '.join(valid_priorities)}")
    
    # Проверяем наличие раздела "Описание"
    if not re.search(r"##\s+Описание", content):
        errors.append("Отсутствует раздел 'Описание'")
    
    return len(errors) == 0, errors

def validate_cache_integration() -> Dict[str, Any]:
    """
    Проверяет интеграцию системы кэширования с архивацией.
    
    Returns:
        Словарь с результатами валидации
    """
    logger.info("Запуск валидации интеграции кэша с архивацией")
    
    # Запускаем скрипт валидации
    try:
        result = subprocess.run(
            ["python", VALIDATION_SCRIPT, "--api-url", "http://localhost:5003"],
            capture_output=True,
            text=True,
            check=False  # Не выбрасывать исключение при ненулевом коде возврата
        )
        
        # Читаем отчет валидации
        report_path = Path("cache_validation_report.json")
        if report_path.exists():
            with open(report_path, "r") as f:
                report = json.load(f)
        else:
            report = {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": result.returncode,
                "test_details": []
            }
        
        success = result.returncode == 0
        
        validation_result = {
            "success": success,
            "report": report,
            "archive_test_passed": any(
                test.get("name") == "Интеграция с системой архивации" and test.get("passed", False)
                for test in report.get("test_details", [])
            ),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "timestamp": datetime.now().isoformat()
        }
        
        return validation_result
    except Exception as e:
        logger.error(f"Ошибка при выполнении валидации: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def ensure_archive_directory_exists() -> bool:
    """
    Проверяет и создает директорию архива, если она не существует.
    
    Returns:
        True, если директория создана или уже существует
    """
    try:
        archive_path = Path(ARCHIVE_DIR)
        if not archive_path.exists():
            archive_path.mkdir(exist_ok=True)
            logger.info(f"Создана директория архива: {ARCHIVE_DIR}")
        return True
    except Exception as e:
        logger.error(f"Не удалось создать директорию архива: {e}")
        return False

def validate_todo_document(file_path: str) -> Dict[str, Any]:
    """
    Комплексная валидация Todo документа.
    
    Args:
        file_path: Путь к документу
        
    Returns:
        Словарь с результатами валидации
    """
    result = {
        "file_path": file_path,
        "timestamp": datetime.now().isoformat(),
        "structure_valid": False,
        "structure_errors": [],
        "cache_integration_valid": False,
        "cache_integration_details": {},
        "archive_directory_exists": False
    }
    
    try:
        # Проверяем существование файла
        path = Path(file_path)
        if not path.exists():
            result["structure_errors"].append(f"Файл не найден: {file_path}")
            return result
        
        # Читаем содержимое файла
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Валидируем структуру документа
        structure_valid, structure_errors = validate_todo_structure(content)
        result["structure_valid"] = structure_valid
        result["structure_errors"] = structure_errors
        
        # Проверяем наличие директории архива
        result["archive_directory_exists"] = ensure_archive_directory_exists()
        
        # Проверяем интеграцию с кэшем
        cache_validation = validate_cache_integration()
        result["cache_integration_valid"] = cache_validation.get("success", False)
        result["cache_integration_details"] = cache_validation
        
        return result
    except Exception as e:
        logger.error(f"Ошибка при валидации документа {file_path}: {e}")
        result["structure_errors"].append(f"Ошибка валидации: {str(e)}")
        return result

def handle_todo_created(file_path: str) -> Dict[str, Any]:
    """
    Обрабатывает событие создания Todo документа.
    
    Args:
        file_path: Путь к созданному документу
        
    Returns:
        Результат валидации
    """
    logger.info(f"Обработка создания Todo документа: {file_path}")
    
    # Валидируем документ
    validation_result = validate_todo_document(file_path)
    
    # Записываем результаты валидации в лог
    log_entry = {
        "event": "todo_created",
        "file_path": file_path,
        "validation_result": validation_result,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        # Добавляем запись в лог валидации
        log_path = Path("todo_validation.log")
        with open(log_path, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        logger.error(f"Не удалось записать результаты валидации: {e}")
    
    return validation_result

if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Валидация Todo документов")
    parser.add_argument("--validate", help="Проверить указанный Todo документ")
    parser.add_argument("--check-cache", action="store_true", help="Проверить интеграцию с кэшем")
    
    args = parser.parse_args()
    
    if args.validate:
        result = validate_todo_document(args.validate)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["structure_valid"] and result["cache_integration_valid"] else 1)
    
    if args.check_cache:
        result = validate_cache_integration()
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["success"] else 1)
    
    parser.print_help()