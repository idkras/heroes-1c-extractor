#!/usr/bin/env python3
"""
Скрипт для проверки соответствия действий AI ассистента всем применимым стандартам.
Может использоваться перед запуском сессии для загрузки ключевых стандартов в память.
"""

import os
import re
import json
import sys
import argparse
from datetime import datetime

# Ключевые стандарты для загрузки
KEY_STANDARDS = [
    "registry standard",
    "incident standard",
    "task master",
    "tone-style policy"
]

# Директории с документами
STANDARDS_DIR = "advising standards .md"
INCIDENTS_DIR = "incidents"

def read_file(path):
    """Читает содержимое файла."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Ошибка при чтении файла {path}: {e}")
        return None

def find_relevant_standards():
    """Находит все файлы стандартов, соответствующие ключевым стандартам."""
    standards = []
    
    # Проверяем, существует ли директория со стандартами
    if not os.path.exists(STANDARDS_DIR):
        print(f"Директория стандартов не найдена: {STANDARDS_DIR}")
        return standards
    
    # Получаем все файлы в директории стандартов
    for filename in os.listdir(STANDARDS_DIR):
        file_path = os.path.join(STANDARDS_DIR, filename)
        
        # Проверяем, является ли файлом
        if not os.path.isfile(file_path):
            continue
        
        # Проверяем, содержит ли имя файла ключевой стандарт
        if any(standard.lower() in filename.lower() for standard in KEY_STANDARDS):
            content = read_file(file_path)
            if content:
                standards.append({
                    "path": file_path,
                    "name": filename,
                    "content": content
                })
    
    return standards

def extract_standard_rules(standard):
    """Извлекает правила из стандарта."""
    content = standard["content"]
    rules = []
    
    # Поиск разделов с правилами (начинающихся с "## ")
    sections = re.findall(r'##\s+(.+?)\n(.*?)(?=##|\Z)', content, re.DOTALL)
    
    for section_title, section_content in sections:
        # Ищем пункты, которые могут быть правилами
        bullet_points = re.findall(r'[-*]\s+(.+?)(?=\n[-*]|\n\n|\Z)', section_content, re.DOTALL)
        
        if bullet_points:
            rules.append({
                "section": section_title.strip(),
                "rules": [rule.strip() for rule in bullet_points if rule.strip()]
            })
    
    return rules

def create_standards_summary(standards):
    """Создает сводку стандартов с извлеченными правилами."""
    standards_summary = []
    
    for standard in standards:
        rules = extract_standard_rules(standard)
        standards_summary.append({
            "name": standard["name"],
            "path": standard["path"],
            "rules": rules
        })
    
    return standards_summary

def validate_incidents_directory():
    """Проверяет соответствие директории инцидентов стандартам."""
    issues = []
    
    # Проверяем, существует ли директория инцидентов
    if not os.path.exists(INCIDENTS_DIR):
        issues.append("Директория инцидентов не найдена")
        return issues
    
    # Получаем все файлы в директории инцидентов
    files = os.listdir(INCIDENTS_DIR)
    
    # Проверяем наличие основного файла инцидентов
    if "ai.incidents.md" not in files:
        issues.append("Основной файл инцидентов ai.incidents.md не найден")
    
    # Проверяем наличие архивной директории
    if "archive" not in files:
        issues.append("Архивная директория не найдена")
    
    # Проверяем, есть ли файлы инцидентов вне архива
    incident_files = [f for f in files if f.endswith(".md") and f != "ai.incidents.md"]
    if incident_files:
        issues.append(f"Обнаружены файлы инцидентов вне архива: {', '.join(incident_files)}")
    
    return issues

def validate_todo_file():
    """Проверяет соответствие файла todo.md стандартам."""
    issues = []
    
    # Проверяем, существует ли файл todo.md
    if not os.path.exists("todo.md"):
        issues.append("Файл todo.md не найден")
        return issues
    
    # Проверяем, существует ли файл todo.archive.md
    if not os.path.exists("todo.archive.md"):
        issues.append("Файл todo.archive.md не найден")
    
    # Читаем содержимое файла todo.md
    content = read_file("todo.md")
    if not content:
        issues.append("Не удалось прочитать файл todo.md")
        return issues
    
    # Проверяем наличие раздела "Следующие действия"
    if "## 🔜 Следующие действия" not in content:
        issues.append("Раздел '## 🔜 Следующие действия' не найден в todo.md")
    
    # Проверяем количество строк в файле
    lines_count = len(content.split('\n'))
    if lines_count > 2000:
        issues.append(f"Файл todo.md слишком большой ({lines_count} строк). Рекомендуется архивация.")
    
    return issues

def generate_report(standards_summary, incidents_issues, todo_issues):
    """Генерирует отчет о проверке на соответствие стандартам."""
    report = {
        "date": datetime.now().strftime("%d %B %Y, %H:%M CET"),
        "standards": standards_summary,
        "validation": {
            "incidents_directory": {
                "status": "OK" if not incidents_issues else "ERROR",
                "issues": incidents_issues
            },
            "todo_file": {
                "status": "OK" if not todo_issues else "ERROR",
                "issues": todo_issues
            }
        }
    }
    
    return report

def main():
    parser = argparse.ArgumentParser(description='Проверка соответствия действий AI ассистента стандартам')
    parser.add_argument('--output', default='validation_report.json', help='Путь к файлу отчета')
    parser.add_argument('--print', action='store_true', help='Вывести отчет на экран')
    
    args = parser.parse_args()
    
    print("Загрузка ключевых стандартов...")
    standards = find_relevant_standards()
    print(f"Найдено {len(standards)} стандартов")
    
    standards_summary = create_standards_summary(standards)
    
    print("Проверка директории инцидентов...")
    incidents_issues = validate_incidents_directory()
    
    print("Проверка файла todo.md...")
    todo_issues = validate_todo_file()
    
    report = generate_report(standards_summary, incidents_issues, todo_issues)
    
    # Сохраняем отчет в файл
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"Отчет сохранен в файл: {args.output}")
    
    if args.print:
        print("\nСводка стандартов:")
        for standard in standards_summary:
            print(f"\n{standard['name']}:")
            for section in standard['rules']:
                print(f"  - {section['section']} ({len(section['rules'])} правил)")
                if len(section['rules']) > 0:
                    print(f"    - {section['rules'][0]}")
                    if len(section['rules']) > 1:
                        print(f"    - ...")
        
        print("\nРезультаты проверки:")
        
        print("\nДиректория инцидентов:")
        if incidents_issues:
            for issue in incidents_issues:
                print(f"  - ❌ {issue}")
        else:
            print("  - ✅ Соответствует стандартам")
        
        print("\nФайл todo.md:")
        if todo_issues:
            for issue in todo_issues:
                print(f"  - ❌ {issue}")
        else:
            print("  - ✅ Соответствует стандартам")
    
    return 0 if not (incidents_issues or todo_issues) else 1

if __name__ == "__main__":
    sys.exit(main())