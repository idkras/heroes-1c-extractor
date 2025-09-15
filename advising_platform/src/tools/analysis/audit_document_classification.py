#!/usr/bin/env python3
"""
Инструмент для аудита классификации документов.

Выполняет сравнение между автоматической классификацией и ручной проверкой,
позволяя выявить несоответствия и проблемы в алгоритме классификации.
"""

import os
import re
import sys
import json
import csv
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

# Определение корневой директории проекта
ROOT_DIR = Path(__file__).parent.parent.parent.parent.parent

# Пути к директориям с документами
STANDARDS_DIR = ROOT_DIR / "[standards .md]"
TASKS_DIR = ROOT_DIR / "[todo · incidents]"

# Критерии для определения типов документов
# Более формализованные критерии на основе TaskMaster
DOCUMENT_CRITERIA = {
    "standard": {
        "required_sections": ["Описание", "Цели", "Процедура"],
        "required_metadata": ["Идентификатор", "Версия", "Статус", "Дата обновления"],
        "title_patterns": [r"Стандарт", r"Standard"],
        "content_patterns": [
            r"status:\s*(Active|Активен|Действующий)",
            r"version:\s*\d+\.\d+",
            r"updated:\s*\d{1,2}\s+\w+\s+\d{4}",
            r"based on:\s*.*?Standard"
        ],
        "path_patterns": [r"standards\.md", r"standard[s]?/", r"standard[s]?\."]
    },
    "task": {
        "required_sections": ["Следующие действия", "Архив задач"],
        "required_metadata": [],
        "title_patterns": [r"ToDo", r"Todo", r"Задач[аи]"],
        "content_patterns": [
            r"^\s*#{1,3}\s+(?:🔜|📋)\s+.*(?:ToDo|Todo|Следующие действия|Задачи)",
            r"\[(?:alarm|asap|blocker|research|small task|exciter)\]"
        ],
        "path_patterns": [r"todo", r"task[s]?/", r"task[s]?\."]
    },
    "incident": {
        "required_sections": ["Описание инцидента", "Последствия", "Решение"],
        "required_metadata": [],
        "title_patterns": [r"Инцидент", r"Incident"],
        "content_patterns": [
            r"^\s*#{1,3}\s+(?:🚨|🔍)\s+.*(?:Инцидент|Incident)",
            r"^\s*#{1,3}\s+(?:❌|🧑‍🔧)\s+.*(?:Последствия|Корневые причины)"
        ],
        "path_patterns": [r"incident[s]?/", r"incident[s]?\."]
    }
}

# Критерии для определения архивного статуса
ARCHIVE_CRITERIA = {
    "path_patterns": [r"archive", r"архив"],
    "content_patterns": [
        r"(?:status|статус):\s*(?:Archived|Архивирован|Неактивен)",
        r"Архивировано",
        r"^\s*#{1,3}\s+.*?(?:Архив)"
    ]
}

def extract_document_metadata(content):
    """
    Извлекает метаданные из документа.
    
    Args:
        content (str): Содержимое документа
        
    Returns:
        dict: Словарь с метаданными
    """
    metadata = {}
    
    # Извлечение заголовка
    title_match = re.search(r"^\s*#\s+(.*?)$", content, re.MULTILINE)
    if title_match:
        metadata["title"] = title_match.group(1).strip()
    
    # Извлечение метаданных в формате key: value
    metadata_pattern = r"^\s*(?:\*\*)?([A-Za-zА-Яа-я][A-Za-zА-Яа-я\s]+?)(?:\*\*)?\s*:\s*(.+?)$"
    for match in re.finditer(metadata_pattern, content, re.MULTILINE):
        key = match.group(1).strip().lower()
        value = match.group(2).strip()
        metadata[key] = value
    
    # Извлечение разделов (заголовков второго уровня)
    sections = []
    section_pattern = r"^\s*##\s+(.*?)$"
    for match in re.finditer(section_pattern, content, re.MULTILINE):
        sections.append(match.group(1).strip())
    
    if sections:
        metadata["sections"] = sections
    
    return metadata

def check_criteria_match(content, file_path, criteria):
    """
    Проверяет, соответствует ли документ заданным критериям.
    
    Args:
        content (str): Содержимое документа
        file_path (Path): Путь к файлу
        criteria (dict): Критерии для проверки
        
    Returns:
        bool: True, если документ соответствует критериям, иначе False
    """
    str_path = str(file_path)
    
    # Проверка по пути
    for pattern in criteria.get("path_patterns", []):
        if re.search(pattern, str_path, re.IGNORECASE):
            return True
    
    metadata = extract_document_metadata(content)
    
    # Проверка заголовка
    if "title" in metadata:
        for pattern in criteria.get("title_patterns", []):
            if re.search(pattern, metadata["title"], re.IGNORECASE):
                return True
    
    # Проверка обязательных разделов
    if "sections" in metadata:
        required_sections = criteria.get("required_sections", [])
        if required_sections:
            section_matches = sum(1 for section in required_sections if any(
                re.search(f"{re.escape(section)}", s, re.IGNORECASE) for s in metadata["sections"]
            ))
            # Если найдено более половины требуемых разделов, считаем критерий выполненным
            if section_matches >= len(required_sections) / 2:
                return True
    
    # Проверка по содержимому
    for pattern in criteria.get("content_patterns", []):
        if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
            return True
    
    return False

def is_archived(content, file_path):
    """
    Проверяет, является ли документ архивным.
    
    Args:
        content (str): Содержимое документа
        file_path (Path): Путь к файлу
        
    Returns:
        bool: True, если документ архивный, иначе False
    """
    str_path = str(file_path)
    
    # Проверка по пути
    for pattern in ARCHIVE_CRITERIA.get("path_patterns", []):
        if re.search(pattern, str_path, re.IGNORECASE):
            return True
    
    # Проверка по содержимому
    for pattern in ARCHIVE_CRITERIA.get("content_patterns", []):
        if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
            return True
    
    return False

def determine_document_type(content, file_path):
    """
    Определяет тип документа на основе содержимого и пути.
    
    Args:
        content (str): Содержимое документа
        file_path (Path): Путь к файлу
        
    Returns:
        str: Тип документа (standard, task, incident, unknown) с префиксом archived_ для архивных документов
    """
    # Проверяем, является ли документ архивным
    archived = is_archived(content, file_path)
    prefix = "archived_" if archived else ""
    
    # Проверяем каждый тип документа
    for doc_type, criteria in DOCUMENT_CRITERIA.items():
        if check_criteria_match(content, file_path, criteria):
            return f"{prefix}{doc_type}"
    
    # Если документ архивный, но тип не определен, считаем его архивным документом
    if archived:
        return "archived_document"
    
    # Если тип не определен и документ не архивный, считаем его неизвестным
    return "unknown"

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
            try:
                with open(item, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                doc_type = determine_document_type(content, item)
                results[doc_type]["files"].append(item)
                results[doc_type]["count"] += 1
                
                print(f"  {item.name}: {doc_type}")
                
            except Exception as e:
                print(f"Ошибка при анализе файла {item}: {e}")
                results["error"]["files"].append(item)
                results["error"]["count"] += 1

def compare_with_indexer(results):
    """
    Сравнивает результаты аудита с данными индексатора.
    
    Args:
        results (dict): Результаты сканирования
        
    Returns:
        dict: Результаты сравнения
    """
    # Получаем статистику от индексатора через API
    try:
        import requests
        response = requests.get("http://localhost:5001/api/indexer/statistics")
        if response.status_code != 200:
            print(f"Ошибка при получении статистики индексатора: {response.status_code}")
            return None
        
        indexer_stats = response.json()
        
        # Сравниваем количество документов
        audit_total = sum(data["count"] for data in results.values())
        indexer_total = indexer_stats.get("total_documents", 0)
        
        # Сравниваем количество по типам
        comparison = {
            "total": {
                "audit": audit_total,
                "indexer": indexer_total,
                "difference": audit_total - indexer_total
            },
            "types": {}
        }
        
        # Преобразуем результаты аудита в формат для сравнения
        audit_by_type = {}
        for doc_type, data in results.items():
            audit_by_type[doc_type] = data["count"]
        
        # Получаем типы документов из индексатора
        indexer_by_type = indexer_stats.get("document_types", {})
        
        # Создаем объединенный список типов документов
        all_types = set(audit_by_type.keys()) | set(indexer_by_type.keys())
        
        # Сравниваем каждый тип
        for doc_type in all_types:
            audit_count = audit_by_type.get(doc_type, 0)
            indexer_count = indexer_by_type.get(doc_type, 0)
            
            comparison["types"][doc_type] = {
                "audit": audit_count,
                "indexer": indexer_count,
                "difference": audit_count - indexer_count
            }
        
        return comparison
    
    except Exception as e:
        print(f"Ошибка при сравнении с индексатором: {e}")
        return None

def generate_report(results, comparison=None):
    """
    Генерирует отчет по результатам аудита.
    
    Args:
        results (dict): Результаты сканирования
        comparison (dict, optional): Результаты сравнения с индексатором
        
    Returns:
        str: Путь к файлу отчета
    """
    report_date = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = ROOT_DIR / f"classification_audit_report_{report_date}.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"# Отчет по аудиту классификации документов\n\n")
        f.write(f"Дата проведения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Общая статистика
        total_docs = sum(data["count"] for data in results.values())
        f.write(f"## Общая статистика\n\n")
        f.write(f"Всего проанализировано документов: {total_docs}\n\n")
        
        # Статистика по типам
        f.write("## Распределение по типам\n\n")
        f.write("| Тип документа | Количество | Процент |\n")
        f.write("|---------------|------------|--------|\n")
        
        for doc_type, data in sorted(results.items(), key=lambda x: x[1]["count"], reverse=True):
            count = data["count"]
            percent = (count / total_docs) * 100 if total_docs > 0 else 0
            f.write(f"| {doc_type} | {count} | {percent:.2f}% |\n")
        
        # Сравнение с индексатором
        if comparison:
            f.write("\n## Сравнение с индексатором\n\n")
            
            # Общее количество
            total_diff = comparison["total"]["difference"]
            diff_symbol = "✓" if total_diff == 0 else ("+" if total_diff > 0 else "-")
            
            f.write("### Общее количество документов\n\n")
            f.write(f"* Аудит: {comparison['total']['audit']}\n")
            f.write(f"* Индексатор: {comparison['total']['indexer']}\n")
            f.write(f"* Разница: {diff_symbol} {abs(total_diff)}\n\n")
            
            # По типам
            f.write("### По типам документов\n\n")
            f.write("| Тип документа | Аудит | Индексатор | Разница |\n")
            f.write("|---------------|-------|------------|--------|\n")
            
            for doc_type, data in sorted(comparison["types"].items(), key=lambda x: abs(x[1]["difference"]), reverse=True):
                diff = data["difference"]
                diff_symbol = "✓" if diff == 0 else ("+" if diff > 0 else "-")
                f.write(f"| {doc_type} | {data['audit']} | {data['indexer']} | {diff_symbol} {abs(diff)} |\n")
            
            # Рекомендации
            f.write("\n## Рекомендации\n\n")
            
            if total_diff == 0 and all(d["difference"] == 0 for d in comparison["types"].values()):
                f.write("Классификация документов соответствует данным индексатора. Корректировка не требуется.\n")
            else:
                f.write("Обнаружены расхождения между результатами аудита и данными индексатора:\n\n")
                
                for doc_type, data in comparison["types"].items():
                    if data["difference"] != 0:
                        if data["difference"] > 0:
                            f.write(f"* **{doc_type}**: Аудит обнаружил на {data['difference']} документов больше. ")
                            f.write("Возможно, индексатор не обнаруживает некоторые документы этого типа.\n")
                        else:
                            f.write(f"* **{doc_type}**: Индексатор учитывает на {abs(data['difference'])} документов больше. ")
                            f.write("Возможно, критерии аудита недостаточно точны для этого типа.\n")
                
                f.write("\nРекомендуемые действия:\n\n")
                f.write("1. Обновить критерии классификации в индексаторе\n")
                f.write("2. Привести все документы к единому формату\n")
                f.write("3. Добавить метаданные в документы для более точной классификации\n")
        
        # Детали по каждому типу
        f.write("\n## Детали по типам документов\n\n")
        
        for doc_type, data in sorted(results.items(), key=lambda x: x[1]["count"], reverse=True):
            if data["count"] > 0:
                f.write(f"### {doc_type} ({data['count']})\n\n")
                
                for file_path in sorted(data["files"]):
                    rel_path = file_path.relative_to(ROOT_DIR)
                    f.write(f"* `{rel_path}`\n")
                
                f.write("\n")
    
    print(f"\nОтчет сохранен в файл: {report_file}")
    return str(report_file)

def generate_csv_report(results, comparison=None):
    """
    Генерирует CSV-отчет для дальнейшего анализа.
    
    Args:
        results (dict): Результаты сканирования
        comparison (dict, optional): Результаты сравнения с индексатором
        
    Returns:
        str: Путь к файлу отчета
    """
    report_date = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = ROOT_DIR / f"classification_audit_report_{report_date}.csv"
    
    with open(report_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Заголовок
        writer.writerow(["File Path", "Document Type", "Relative Path"])
        
        # Данные по каждому файлу
        for doc_type, data in results.items():
            for file_path in sorted(data["files"]):
                rel_path = str(file_path.relative_to(ROOT_DIR))
                writer.writerow([str(file_path), doc_type, rel_path])
    
    print(f"\nCSV-отчет сохранен в файл: {report_file}")
    return str(report_file)

def save_statistics(results, comparison=None):
    """
    Сохраняет статистику в JSON-файл.
    
    Args:
        results (dict): Результаты сканирования
        comparison (dict, optional): Результаты сравнения с индексатором
        
    Returns:
        str: Путь к файлу статистики
    """
    # Преобразуем данные в формат для JSON
    stats = {
        "timestamp": datetime.now().isoformat(),
        "total_documents": sum(data["count"] for data in results.values()),
        "document_types": {doc_type: data["count"] for doc_type, data in results.items()},
        "comparison": comparison
    }
    
    # Добавляем более подробную информацию
    stats["documents_by_type"] = {}
    for doc_type, data in results.items():
        stats["documents_by_type"][doc_type] = [str(file_path.relative_to(ROOT_DIR)) for file_path in data["files"]]
    
    # Сохраняем статистику
    stats_file = ROOT_DIR / "classification_statistics.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print(f"\nСтатистика сохранена в файл: {stats_file}")
    return str(stats_file)

def main():
    """Основная функция скрипта."""
    print("Запуск аудита классификации документов")
    
    # Инициализация словаря для результатов
    results = defaultdict(lambda: {"files": [], "count": 0})
    
    # Сканирование директорий
    scan_documents(STANDARDS_DIR, results)
    scan_documents(TASKS_DIR, results)
    
    # Сравнение с индексатором
    comparison = compare_with_indexer(results)
    
    # Генерация отчетов
    generate_report(results, comparison)
    generate_csv_report(results)
    
    # Сохранение статистики
    save_statistics(results, comparison)
    
    print("\nАудит классификации документов завершен успешно")

if __name__ == "__main__":
    main()