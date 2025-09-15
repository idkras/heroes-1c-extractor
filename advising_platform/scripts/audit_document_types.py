#!/usr/bin/env python3
"""
Инструмент аудита для проверки точности классификации документов.
Позволяет выявить несоответствия между фактическим типом документов и
их классификацией в системе in-memory индексирования.
"""

import os
import sys
import re
import json
from collections import Counter
from typing import Dict, List, Tuple, Set, Optional, Any

# Добавляем путь к корневой директории проекта
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Импортируем упрощенный индексатор
from advising_platform.src.core.simple_indexer import indexer

def audit_standards_directory(standards_dir: str = "[standards .md]") -> Dict[str, List[str]]:
    """
    Проверяет директорию стандартов и классифицирует файлы.
    
    Returns:
        Dict с типами документов и списками относящихся к ним файлов.
    """
    results = {
        "standards": [],              # Активные стандарты
        "archived_standards": [],     # Архивированные стандарты
        "drafts": [],                 # Черновики стандартов
        "backups": [],                # Резервные копии
        "technical_files": [],        # Технические файлы (.gitignore и т.д.)
        "unknown": []                 # Неклассифицированные файлы
    }
    
    # Критерии для определения типов файлов
    backup_patterns = ['.bak', 'backup', 'copy', 'old']
    technical_patterns = ['.gitignore', 'README', '.DS_Store', 'Thumbs.db']
    
    for root, dirs, files in os.walk(standards_dir):
        for file in files:
            path = os.path.join(root, file)
            full_path = os.path.abspath(path)
            
            # Проверяем технические файлы по имени
            if any(pattern in file for pattern in technical_patterns):
                results["technical_files"].append(path)
                continue
                
            # Проверяем бэкапы по имени
            if any(pattern in file for pattern in backup_patterns):
                results["backups"].append(path)
                continue
                
            # Проверяем архивные файлы по пути
            if '/archive/' in path:
                results["archived_standards"].append(path)
                continue
                
            # Для остальных файлов читаем содержимое
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Проверка на статус документа
                    if 'status: Archived' in content:
                        results["archived_standards"].append(path)
                    elif 'status: Draft' in content:
                        results["drafts"].append(path)
                    # Проверка наличия обязательных секций стандарта
                    elif any(marker in content for marker in ['## 🎯 Цель', '## Цель документа', '## 🎯 Цель стандарта']):
                        results["standards"].append(path)
                    else:
                        results["unknown"].append(path)
            except Exception as e:
                print(f"Ошибка при чтении файла {path}: {e}")
                results["unknown"].append(path)
                
    return results

def check_indexer_classification(audit_results: Dict[str, List[str]]) -> Dict[str, Any]:
    """
    Сравнивает результаты аудита с классификацией в индексаторе.
    
    Returns:
        Dict с результатами проверки.
    """
    results = {
        "total_files": sum(len(files) for files in audit_results.values()),
        "correctly_classified": 0,
        "misclassified": [],
        "errors": [],
        "type_stats": {}
    }
    
    # Ожидаемые типы документов для каждой категории аудита
    expected_types = {
        "standards": "standard",
        "archived_standards": "archived_standard",
        "drafts": "archived_standard",  # Черновики считаем как архивные
        "backups": "archived_document",
        "technical_files": "standard_related",
        "unknown": None  # Для неизвестных не задаем ожидаемый тип
    }
    
    # Счетчик для статистики
    type_counter = Counter()
    
    # Проверяем каждый файл
    for category, files in audit_results.items():
        expected_type = expected_types[category]
        
        for path in files:
            # Получаем тип документа из индексатора
            doc_type = None
            doc = indexer.get_document(path)
            
            if doc:
                doc_type = doc[0].doc_type
                type_counter[doc_type] += 1
                
                # Проверяем соответствие типов
                if expected_type and doc_type != expected_type:
                    results["misclassified"].append({
                        "path": path,
                        "expected_type": expected_type,
                        "actual_type": doc_type,
                        "category": category
                    })
                elif expected_type:
                    results["correctly_classified"] += 1
            else:
                results["errors"].append({
                    "path": path,
                    "error": "Документ не найден в индексе"
                })
    
    # Статистика по типам
    results["type_stats"] = dict(type_counter)
    
    return results

def generate_report(audit_results: Dict[str, List[str]], classification_results: Dict[str, Any]) -> str:
    """
    Генерирует отчет в формате Markdown на основе результатов аудита.
    
    Returns:
        Строка с отчетом в формате Markdown.
    """
    report = []
    report.append("# 📊 Отчет о проверке классификации документов")
    report.append("")
    report.append(f"Дата проверки: {import_time.strftime('%d %B %Y, %H:%M')}")
    report.append("")
    
    report.append("## 📑 Статистика файлов")
    report.append("")
    report.append("| Категория | Количество файлов |")
    report.append("|-----------|-------------------|")
    
    for category, files in audit_results.items():
        report.append(f"| {category} | {len(files)} |")
    
    report.append("")
    report.append(f"**Всего файлов**: {classification_results['total_files']}")
    report.append(f"**Корректно классифицировано**: {classification_results['correctly_classified']}")
    report.append(f"**Ошибки классификации**: {len(classification_results['misclassified'])}")
    report.append(f"**Документы не найдены в индексе**: {len(classification_results['errors'])}")
    report.append("")
    
    report.append("## 🔍 Типы документов в индексе")
    report.append("")
    report.append("| Тип документа | Количество |")
    report.append("|---------------|------------|")
    
    for doc_type, count in classification_results['type_stats'].items():
        report.append(f"| {doc_type} | {count} |")
    
    report.append("")
    
    if classification_results['misclassified']:
        report.append("## ⚠️ Ошибки классификации")
        report.append("")
        report.append("| Путь к файлу | Ожидаемый тип | Фактический тип | Категория |")
        report.append("|--------------|---------------|-----------------|-----------|")
        
        for item in classification_results['misclassified']:
            report.append(f"| {item['path']} | {item['expected_type']} | {item['actual_type']} | {item['category']} |")
        
        report.append("")
    
    return "\n".join(report)

def main():
    """Основная функция."""
    print("Запуск аудита классификации документов...")
    
    # Проверка директории стандартов
    standards_dir = "[standards .md]"
    if not os.path.exists(standards_dir):
        print(f"Директория стандартов не найдена: {standards_dir}")
        return
    
    # Аудит директории стандартов
    print(f"Анализ директории {standards_dir}...")
    audit_results = audit_standards_directory(standards_dir)
    
    # Проверка классификации в индексаторе
    print("Проверка классификации в индексаторе...")
    classification_results = check_indexer_classification(audit_results)
    
    # Генерация отчета
    print("Создание отчета...")
    report = generate_report(audit_results, classification_results)
    
    # Сохранение отчета
    report_path = "document_classification_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Отчет сохранен в файл: {report_path}")
    
    # Вывод краткой статистики
    total = classification_results['total_files']
    correct = classification_results['correctly_classified']
    incorrect = len(classification_results['misclassified'])
    errors = len(classification_results['errors'])
    
    print("\nРезультаты аудита:")
    print(f"- Всего файлов: {total}")
    print(f"- Корректно классифицировано: {correct} ({correct/total*100:.1f}%)")
    print(f"- Ошибки классификации: {incorrect} ({incorrect/total*100:.1f}%)")
    print(f"- Документы не найдены в индексе: {errors} ({errors/total*100:.1f}%)")
    
    # Вывод рекомендаций
    if incorrect > 0:
        print("\nРекомендации:")
        print("1. Обновите метод _determine_doc_type в src/core/simple_indexer.py")
        print("2. Добавьте дополнительные проверки для различных типов документов")
        print("3. Учитывайте статус документа при определении его типа")
        print("4. Разместите архивные стандарты в директории /archive/")

if __name__ == "__main__":
    import time as import_time
    main()