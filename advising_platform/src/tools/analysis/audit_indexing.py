#!/usr/bin/env python3
"""
Инструмент для аудита качества и полноты индексации документов.

Позволяет выявить несоответствия между фактическими документами в файловой системе
и их представлением в индексе, а также обнаружить проблемы с классификацией документов.
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("audit_indexing")

# Добавляем путь к корневой директории проекта
ROOT_DIR = Path(__file__).parent.parent.parent.parent.parent
sys.path.append(str(ROOT_DIR))

# Импортируем индексатор
try:
    from advising_platform.src.core.simple_indexer import indexer
    logger.info("Индексатор успешно импортирован")
except ImportError as e:
    logger.error(f"Ошибка при импорте индексатора: {e}")
    indexer = None

def count_files_by_extension(directory: str, extensions: Optional[List[str]] = None) -> Dict[str, int]:
    """
    Подсчитывает количество файлов в директории по расширениям.
    
    Args:
        directory: Путь к директории
        extensions: Список расширений для подсчета
                    По умолчанию ['.md']
    
    Returns:
        Словарь с количеством файлов по расширениям
    """
    if extensions is None or not extensions:
        extensions = ['.md']
    
    result = {ext: 0 for ext in extensions}
    
    for root, _, files in os.walk(directory):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in result:
                result[ext] += 1
    
    return result

def find_unindexed_files(directory: str, extension: str = '.md') -> List[str]:
    """
    Находит файлы, которые не проиндексированы.
    
    Args:
        directory: Путь к директории
        extension: Расширение файлов для проверки
    
    Returns:
        Список путей к непроиндексированным файлам
    """
    if indexer is None:
        logger.error("Индексатор не доступен")
        return []
    
    unindexed_files = []
    indexed_paths = set(indexer._indexer.documents.keys())
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                path = os.path.join(root, file)
                if path not in indexed_paths:
                    unindexed_files.append(path)
    
    return unindexed_files

def check_document_types(directory: str, extension: str = '.md') -> Dict[str, List[str]]:
    """
    Проверяет корректность определения типов документов.
    
    Args:
        directory: Путь к директории
        extension: Расширение файлов для проверки
    
    Returns:
        Словарь с потенциально некорректно классифицированными документами
    """
    if indexer is None:
        logger.error("Индексатор не доступен")
        return {}
    
    suspected_misclassifications = {
        "incident_files_not_as_incidents": [],
        "task_files_not_as_tasks": [],
        "standard_files_not_as_standards": []
    }
    
    for path, (metadata, _) in indexer._indexer.documents.items():
        if not path.startswith(directory) or not path.endswith(extension):
            continue
        
        # Проверка на инциденты
        if "/incidents" in path or "ai.incidents" in path:
            if metadata.doc_type != "incident" and metadata.doc_type != "archived_incident":
                suspected_misclassifications["incident_files_not_as_incidents"].append(path)
        
        # Проверка на задачи
        if "/todo" in path or "[todo" in path:
            if metadata.doc_type != "task" and metadata.doc_type != "archived_task":
                suspected_misclassifications["task_files_not_as_tasks"].append(path)
        
        # Проверка на стандарты
        if "/standards" in path or "[standards" in path:
            if metadata.doc_type != "standard" and metadata.doc_type != "archived_standard":
                suspected_misclassifications["standard_files_not_as_standards"].append(path)
    
    return suspected_misclassifications

def generate_audit_report() -> Dict[str, Any]:
    """
    Генерирует полный отчет аудита индексации.
    
    Returns:
        Словарь с результатами аудита
    """
    if indexer is None:
        logger.error("Индексатор не доступен")
        return {"status": "error", "message": "Индексатор не доступен"}
    
    # Получаем статистику индексатора
    indexer_stats = indexer.get_statistics()
    
    # Подсчитываем файлы в директориях
    standards_dir = '[standards .md]'
    incidents_dir = '[todo · incidents]'
    
    standards_files = count_files_by_extension(standards_dir)['.md']
    incidents_files = count_files_by_extension(incidents_dir)['.md']
    
    # Находим непроиндексированные файлы
    unindexed_standards = find_unindexed_files(standards_dir)
    unindexed_incidents = find_unindexed_files(incidents_dir)
    
    # Проверяем классификацию документов
    misclassifications_standards = check_document_types(standards_dir)
    misclassifications_incidents = check_document_types(incidents_dir)
    
    # Формируем отчет
    report = {
        "timestamp": datetime.now().isoformat(),
        "indexer_stats": indexer_stats,
        "filesystem_stats": {
            "standards_files": standards_files,
            "incidents_files": incidents_files
        },
        "discrepancies": {
            "unindexed_standards_count": len(unindexed_standards),
            "unindexed_incidents_count": len(unindexed_incidents),
            "unindexed_standards": unindexed_standards[:10],  # Первые 10 для краткости
            "unindexed_incidents": unindexed_incidents[:10]   # Первые 10 для краткости
        },
        "misclassifications": {
            "standards": misclassifications_standards,
            "incidents": misclassifications_incidents
        },
        "recommendations": []
    }
    
    # Добавляем рекомендации
    if len(unindexed_standards) > 0:
        report["recommendations"].append(
            f"Найдено {len(unindexed_standards)} непроиндексированных стандартов. Рекомендуется переиндексировать директорию {standards_dir}"
        )
    
    if len(unindexed_incidents) > 0:
        report["recommendations"].append(
            f"Найдено {len(unindexed_incidents)} непроиндексированных инцидентов. Рекомендуется переиндексировать директорию {incidents_dir}"
        )
    
    if len(misclassifications_standards["standard_files_not_as_standards"]) > 0:
        report["recommendations"].append(
            f"Найдено {len(misclassifications_standards['standard_files_not_as_standards'])} потенциально неправильно классифицированных стандартов"
        )
    
    if len(misclassifications_incidents["incident_files_not_as_incidents"]) > 0:
        report["recommendations"].append(
            f"Найдено {len(misclassifications_incidents['incident_files_not_as_incidents'])} потенциально неправильно классифицированных инцидентов"
        )
    
    return report

def save_audit_report_to_file(report: Dict[str, Any]) -> str:
    """
    Сохраняет отчет аудита в Markdown-файл.
    
    Args:
        report: Словарь с результатами аудита
    
    Returns:
        Путь к созданному файлу отчета
    """
    # Создаем имя файла с датой
    report_date = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = ROOT_DIR / f"indexing_audit_report_{report_date}.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"# Отчет по аудиту индексации\n\n")
        f.write(f"Дата проведения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Статистика индексатора\n\n")
        f.write(f"* Всего документов: {report['indexer_stats'].get('total_documents', 0)}\n")
        f.write(f"* Всего задач: {report['indexer_stats'].get('total_tasks', 0)}\n")
        f.write(f"* Всего инцидентов: {report['indexer_stats'].get('total_incidents', 0)}\n")
        f.write(f"* Логических ID: {report['indexer_stats'].get('logical_ids', 0)}\n")
        f.write(f"* Проиндексированных слов: {report['indexer_stats'].get('indexed_words', 0)}\n\n")
        
        f.write("### Типы документов\n\n")
        doc_types = report['indexer_stats'].get('document_types', {})
        for doc_type, count in sorted(doc_types.items()):
            f.write(f"* {doc_type}: {count}\n")
        
        f.write("\n## Статистика файловой системы\n\n")
        f.write(f"* Файлов .md в директории стандартов: {report['filesystem_stats']['standards_files']}\n")
        f.write(f"* Файлов .md в директории инцидентов: {report['filesystem_stats']['incidents_files']}\n\n")
        
        f.write("## Несоответствия\n\n")
        f.write(f"* Непроиндексированных стандартов: {report['discrepancies']['unindexed_standards_count']}\n")
        f.write(f"* Непроиндексированных инцидентов: {report['discrepancies']['unindexed_incidents_count']}\n\n")
        
        if report['discrepancies']['unindexed_standards_count'] > 0:
            f.write("### Примеры непроиндексированных стандартов:\n\n")
            for path in report['discrepancies']['unindexed_standards']:
                f.write(f"* `{path}`\n")
            f.write("\n")
        
        if report['discrepancies']['unindexed_incidents_count'] > 0:
            f.write("### Примеры непроиндексированных инцидентов:\n\n")
            for path in report['discrepancies']['unindexed_incidents']:
                f.write(f"* `{path}`\n")
            f.write("\n")
        
        f.write("## Потенциальные ошибки классификации\n\n")
        
        standards_misclassified = report['misclassifications']['standards']['standard_files_not_as_standards']
        incidents_misclassified = report['misclassifications']['incidents']['incident_files_not_as_incidents']
        
        if len(standards_misclassified) > 0:
            f.write("### Файлы в директории стандартов, не классифицированные как стандарты:\n\n")
            for path in standards_misclassified[:10]:  # Первые 10 для краткости
                f.write(f"* `{path}`\n")
            f.write("\n")
        
        if len(incidents_misclassified) > 0:
            f.write("### Файлы в директории инцидентов, не классифицированные как инциденты:\n\n")
            for path in incidents_misclassified[:10]:  # Первые 10 для краткости
                f.write(f"* `{path}`\n")
            f.write("\n")
        
        f.write("## Рекомендации\n\n")
        for recommendation in report['recommendations']:
            f.write(f"* {recommendation}\n")
    
    logger.info(f"Отчет сохранен в файл: {report_file}")
    return str(report_file)

def main():
    """Основная функция для запуска аудита из командной строки."""
    if indexer is None:
        logger.error("Индексатор не доступен. Убедитесь, что модуль индексатора корректно установлен.")
        return
    
    logger.info("Запуск аудита индексации...")
    
    # Генерируем отчет
    report = generate_audit_report()
    
    # Сохраняем отчет в файл
    report_file = save_audit_report_to_file(report)
    
    logger.info(f"Аудит завершен. Отчет сохранен в {report_file}")
    
    # Выводим рекомендации
    if report['recommendations']:
        logger.info("Рекомендации:")
        for i, recommendation in enumerate(report['recommendations'], 1):
            logger.info(f"{i}. {recommendation}")

if __name__ == "__main__":
    main()