#!/usr/bin/env python3
"""
Скрипт для аудита типов документов в системе.

Выполняет проверку правильности типизации документов в системе индексации:
1. Сканирует директории с документами
2. Проверяет, что документы правильно классифицированы
3. Выводит статистику и предложения по исправлению
"""

import os
import re
import sys
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Определение корневой директории проекта
ROOT_DIR = Path(__file__).parent.parent.parent.parent.parent

# Пути к директориям с документами
STANDARDS_DIR = ROOT_DIR / "[standards .md]"
TASKS_DIR = ROOT_DIR / "[todo · incidents]"

# Шаблоны для определения типов документов
PATTERNS = {
    "standard": [
        r"^#\s+.*?Стандарт",
        r"status:\s*(Active|Активен|Действующий)",
        r"version:\s*\d+\.\d+",
        r"updated:\s*\d{1,2}\s+\w+\s+\d{4}",
        r"based on:\s*.*?Standard"
    ],
    "task": [
        r"^#\s+📋\s+ToDo",
        r"^##\s+🔜\s+Следующие действия",
        r"^##\s+ToDo",
        r"^##\s+Задачи"
    ],
    "incident": [
        r"^#\s+🚨\s+Инцидент",
        r"^##\s+🔍\s+Описание инцидента",
        r"^##\s+Описание инцидента",
        r"^##\s+❌\s+Последствия"
    ],
    "archived": [
        r"archive",
        r"архив",
        r"Архивировано"
    ]
}

def detect_document_type(file_path):
    """
    Определяет тип документа на основе содержимого и пути.
    
    Args:
        file_path (Path): Путь к файлу
        
    Returns:
        str: Тип документа (standard, task, incident, archived_standard, archived_task, archived_incident, unknown)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверка на стандарт
        is_standard = any(re.search(pattern, content, re.MULTILINE) for pattern in PATTERNS["standard"])
        
        # Проверка на задачу
        is_task = any(re.search(pattern, content, re.MULTILINE) for pattern in PATTERNS["task"])
        
        # Проверка на инцидент
        is_incident = any(re.search(pattern, content, re.MULTILINE) for pattern in PATTERNS["incident"])
        
        # Проверка на архивный документ
        is_archived = any(re.search(pattern, file_path.name.lower()) for pattern in PATTERNS["archived"]) or \
                     any(re.search(pattern, content, re.MULTILINE) for pattern in PATTERNS["archived"])
        
        # Определение типа на основе результатов проверок
        if is_standard:
            return "archived_standard" if is_archived else "standard"
        elif is_task:
            return "archived_task" if is_archived else "task"
        elif is_incident:
            return "archived_incident" if is_archived else "incident"
        else:
            return "archived_document" if is_archived else "unknown"
    
    except Exception as e:
        print(f"Ошибка при анализе файла {file_path}: {e}")
        return "error"

def scan_documents(directory, results):
    """
    Рекурсивно сканирует директорию и определяет типы документов.
    
    Args:
        directory (Path): Директория для сканирования
        results (dict): Словарь для хранения результатов
    """
    if not directory.exists():
        print(f"Директория {directory} не существует")
        return
    
    print(f"Сканирование директории: {directory}")
    
    for item in directory.iterdir():
        if item.is_dir():
            scan_documents(item, results)
        elif item.is_file() and item.suffix.lower() in ['.md', '.markdown']:
            doc_type = detect_document_type(item)
            results[doc_type].append(item)
            print(f"  {item.name}: {doc_type}")

def analyze_results(results):
    """
    Анализирует результаты сканирования и выводит статистику.
    
    Args:
        results (dict): Словарь с результатами сканирования
        
    Returns:
        dict: Статистика по типам документов
    """
    statistics = {
        "total": sum(len(docs) for docs in results.values()),
        "types": {doc_type: len(docs) for doc_type, docs in results.items()},
        "timestamp": datetime.now().isoformat()
    }
    
    # Выводим статистику
    print("\nСтатистика сканирования:")
    print(f"  Всего документов: {statistics['total']}")
    print("  Типы документов:")
    for doc_type, count in statistics["types"].items():
        print(f"    {doc_type}: {count}")
    
    return statistics

def generate_report(results, statistics):
    """
    Генерирует подробный отчет по результатам аудита.
    
    Args:
        results (dict): Словарь с результатами сканирования
        statistics (dict): Статистика по типам документов
        
    Returns:
        str: Путь к файлу отчета
    """
    report_date = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = ROOT_DIR / f"audit_report_{report_date}.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"# Отчет по аудиту типов документов\n\n")
        f.write(f"Дата проведения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Статистика\n\n")
        f.write(f"Всего документов: {statistics['total']}\n\n")
        f.write("Распределение по типам:\n\n")
        
        for doc_type, count in statistics["types"].items():
            f.write(f"- {doc_type}: {count}\n")
        
        f.write("\n## Список документов по типам\n\n")
        
        for doc_type, docs in results.items():
            if docs:
                f.write(f"### {doc_type}\n\n")
                for doc in docs:
                    rel_path = doc.relative_to(ROOT_DIR)
                    f.write(f"- `{rel_path}`\n")
                f.write("\n")
    
    print(f"\nОтчет сохранен в файл: {report_file}")
    return str(report_file)

def save_statistics(statistics):
    """
    Сохраняет статистику в JSON-файл.
    
    Args:
        statistics (dict): Статистика по типам документов
        
    Returns:
        str: Путь к файлу статистики
    """
    stats_file = ROOT_DIR / "document_type_statistics.json"
    
    # Читаем историю статистики, если файл существует
    history = []
    if stats_file.exists():
        try:
            with open(stats_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
                if not isinstance(history, list):
                    history = [history]
        except:
            history = []
    
    # Добавляем новую статистику
    history.append(statistics)
    
    # Сохраняем обновленную историю
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    
    print(f"\nСтатистика сохранена в файл: {stats_file}")
    return str(stats_file)

def main():
    """Основная функция скрипта."""
    print("Запуск аудита типов документов")
    
    # Инициализация словаря для результатов
    results = defaultdict(list)
    
    # Сканирование директорий
    scan_documents(STANDARDS_DIR, results)
    scan_documents(TASKS_DIR, results)
    
    # Анализ результатов
    statistics = analyze_results(results)
    
    # Генерация отчета
    generate_report(results, statistics)
    
    # Сохранение статистики
    save_statistics(statistics)
    
    print("\nАудит завершен успешно")

if __name__ == "__main__":
    main()