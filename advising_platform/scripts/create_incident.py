#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для создания и обновления инцидентов.

Автоматически генерирует файлы инцидентов по стандарту 1.1 ai incident standard.
Помогает с анализом "5 почему", отслеживанием статусов и управлением инцидентами.
"""

import os
import sys
import re
import argparse
import datetime
import json
from typing import Dict, List, Optional, Tuple

# Конфигурация - все инциденты теперь в центральном файле
INCIDENTS_DIR = "[todo · incidents]"
CENTRAL_INCIDENTS_FILE = "[todo · incidents]/ai.incidents.md"
ARCHIVE_FILE = f"{INCIDENTS_DIR}/ai.incident.archive.md"
REGISTRY_FILE = f"{INCIDENTS_DIR}/registry.md"
STANDARD_FILE = "advising standards .md/1.1 ai incident standard 14 may 2025 0505 cet by ai assistant.md"

# Статусы инцидентов
STATUSES = [
    "Recorded",         # Зафиксирован
    "In Progress",      # В работе
    "Hypothesis Testing", # На проверке гипотезы
    "Hypothesis Confirmed", # Гипотеза сработала
    "Hypothesis Failed",  # Гипотеза не сработала
    "Archived"          # Архивирован
]

def get_current_date() -> Tuple[str, str]:
    """
    Получает текущую дату в формате YYYYMMDD и DD MMM YYYY.
    
    Returns:
        Кортеж из двух строк: дата в формате YYYYMMDD и дата в формате DD MMM YYYY
    """
    now = datetime.datetime.now()
    yyyymmdd = now.strftime("%Y%m%d")
    readable_date = now.strftime("%d %b %Y")
    return yyyymmdd, readable_date

def get_next_incident_number(date_prefix: str) -> str:
    """
    Определяет следующий порядковый номер инцидента для указанной даты.
    
    Args:
        date_prefix: Дата в формате YYYYMMDD
    
    Returns:
        Следующий номер инцидента в формате NN (01, 02, ...)
    """
    existing_numbers = []
    pattern = re.compile(f"{date_prefix}-([0-9]{{2}})")
    
    # Проверяем существующие файлы инцидентов
    if os.path.exists(INCIDENTS_DIR):
        for filename in os.listdir(INCIDENTS_DIR):
            match = pattern.match(filename)
            if match:
                existing_numbers.append(int(match.group(1)))
    
    # Определяем следующий номер
    next_number = 1
    if existing_numbers:
        next_number = max(existing_numbers) + 1
    
    return f"{next_number:02d}"

def generate_incident_filename(date_prefix: str, number: str, description: str) -> str:
    """
    Генерирует имя файла инцидента.
    
    Args:
        date_prefix: Дата в формате YYYYMMDD
        number: Номер инцидента
        description: Краткое описание инцидента
    
    Returns:
        Имя файла в формате YYYYMMDD-NN-short-description.md
    """
    # Преобразуем описание в slug (нижний регистр, дефисы вместо пробелов)
    slug = description.lower()
    slug = re.sub(r'[^a-zA-Zа-яА-Я0-9\s-]', '', slug)  # Удаляем спецсимволы
    slug = re.sub(r'\s+', '-', slug.strip())           # Заменяем пробелы на дефисы
    
    return f"{date_prefix}-{number}-{slug}.md"

def create_incident_template(description: str, readable_date: str) -> str:
    """
    Создает шаблон инцидента.
    
    Args:
        description: Краткое описание инцидента
        readable_date: Дата в формате DD MMM YYYY
    
    Returns:
        Строка с шаблоном инцидента
    """
    template = f"""# Инцидент: {description}

## Метаданные
- **Дата создания**: {readable_date}
- **Автор**: AI Assistant
- **Тип инцидента**: (выберите: Системный/Функциональный/Безопасность/Производительность)
- **Статус**: Recorded
- **Приоритет**: (выберите: Критический/Высокий/Средний/Низкий)
- **Связанные стандарты**: 
  - `standard:task_master` (0.0 task master)
  - (добавьте другие связанные стандарты)

## Описание проблемы
(Подробное описание проблемы, включая контекст и последствия)

## Анализ "5 почему"

### Проблема 1: (Сформулируйте первый аспект проблемы)
**Почему?** (Первый уровень - непосредственная причина)
**Почему?** (Второй уровень - причина предыдущей причины)
**Почему?** (Третий уровень)
**Почему?** (Четвертый уровень)
**Почему?** (Пятый уровень - корневая причина)

### Проблема 2: (При необходимости сформулируйте другой аспект проблемы)
**Почему?** (Первый уровень)
**Почему?** (Второй уровень)
**Почему?** (Третий уровень)
**Почему?** (Четвертый уровень)
**Почему?** (Пятый уровень - корневая причина)

## Корневая причина
(Краткая формулировка системной проблемы, которая привела к инциденту)

## Предлагаемые решения

### Немедленные действия:
1. (Укажите конкретное действие)
2. (Укажите конкретное действие)
3. (Укажите конкретное действие)

### Краткосрочные действия:
1. (Укажите конкретное действие)
2. (Укажите конкретное действие)
3. (Укажите конкретное действие)

### Долгосрочные действия:
1. (Укажите конкретное действие)
2. (Укажите конкретное действие)
3. (Укажите конкретное действие)

## Обновления

### {readable_date}
Инцидент создан и добавлен в реестр."""
    
    return template

def update_incident_registry(filename: str, description: str, status: str = "Recorded") -> None:
    """
    Обновляет реестр инцидентов.
    
    Args:
        filename: Имя файла инцидента
        description: Краткое описание инцидента
        status: Статус инцидента
    """
    # Создаем реестр, если он не существует
    if not os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
            f.write("# Реестр инцидентов\n\n")
            f.write("| Файл | Описание | Статус | Дата последнего обновления |\n")
            f.write("|------|----------|--------|---------------------------|\n")
    
    today = datetime.datetime.now().strftime("%d %b %Y")
    
    # Проверяем, есть ли уже запись для этого инцидента
    with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
        registry_content = f.read()
    
    # Если записи нет, добавляем новую
    if filename not in registry_content:
        with open(REGISTRY_FILE, 'a', encoding='utf-8') as f:
            f.write(f"| [{filename}]({filename}) | {description} | {status} | {today} |\n")
    else:
        # Если запись есть, обновляем статус и дату
        lines = registry_content.split('\n')
        for i, line in enumerate(lines):
            if filename in line:
                # Разбиваем строку на колонки
                columns = line.split('|')
                if len(columns) >= 5:
                    # Обновляем статус и дату
                    columns[3] = f" {status} "
                    columns[4] = f" {today} "
                    lines[i] = '|'.join(columns)
                break
        
        # Записываем обновленный реестр
        with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

def create_incident(description: str) -> str:
    """
    Создает новый инцидент в центральном файле ai.incidents.md.
    
    Args:
        description: Краткое описание инцидента
    
    Returns:
        Путь к файлу инцидента (всегда CENTRAL_INCIDENTS_FILE)
    """
    # Получаем текущую дату и следующий номер инцидента
    date_prefix, readable_date = get_current_date()
    incident_number = get_next_incident_number(date_prefix)
    
    # Создаем шаблон инцидента
    template = create_incident_template(description, readable_date)
    
    # Записываем инцидент в центральный файл ai.incidents.md
    try:
        # Читаем существующий файл
        if os.path.exists(CENTRAL_INCIDENTS_FILE):
            with open(CENTRAL_INCIDENTS_FILE, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        else:
            existing_content = "# AI Incidents Log\n\n"
        
        # Добавляем новый инцидент в начало (после заголовка)
        lines = existing_content.split('\n')
        header = lines[0] + '\n\n'
        new_content = header + template + '\n\n---\n\n' + '\n'.join(lines[2:])
        
        # Записываем обновленное содержимое
        with open(CENTRAL_INCIDENTS_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        # Обновляем реестр инцидентов
        update_incident_registry(f"{date_prefix}_{incident_number}", description)
        
        return CENTRAL_INCIDENTS_FILE
        
    except Exception as e:
        print(f"Ошибка при записи инцидента: {e}")
        return CENTRAL_INCIDENTS_FILE

def update_incident_status(filename: str, new_status: str, update_note: str) -> None:
    """
    Обновляет статус инцидента.
    
    Args:
        filename: Имя файла инцидента
        new_status: Новый статус инцидента
        update_note: Примечание к обновлению
    """
    if new_status not in STATUSES:
        print(f"Ошибка: Недопустимый статус '{new_status}'. Разрешенные статусы: {', '.join(STATUSES)}")
        return
    
    filepath = os.path.join(INCIDENTS_DIR, filename)
    
    if not os.path.exists(filepath):
        print(f"Ошибка: Файл инцидента '{filepath}' не найден.")
        return
    
    # Считываем содержимое файла
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Обновляем статус в метаданных
    content = re.sub(r'- \*\*Статус\*\*: [^\n]+', f'- **Статус**: {new_status}', content)
    
    # Добавляем запись об обновлении
    today = datetime.datetime.now().strftime("%d %b %Y")
    
    if "## Обновления" in content:
        # Добавляем новую запись в раздел обновлений
        update_section = f"\n\n### {today}\nСтатус изменен на '{new_status}'. {update_note}"
        content = re.sub(r'(## Обновления\n\n)', f'\\1### {today}\nСтатус изменен на \'{new_status}\'. {update_note}\n', content)
    else:
        # Создаем раздел обновлений
        update_section = f"\n\n## Обновления\n\n### {today}\nСтатус изменен на '{new_status}'. {update_note}"
        content += update_section
    
    # Записываем обновленное содержимое
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Если статус "Archived", перемещаем в архив
    if new_status == "Archived":
        archive_incident(filename, content)
    
    # Обновляем реестр инцидентов
    update_incident_registry(filename, "", new_status)
    
    print(f"Статус инцидента '{filename}' обновлен на '{new_status}'.")

def archive_incident(filename: str, content: str) -> None:
    """
    Архивирует инцидент.
    
    Args:
        filename: Имя файла инцидента
        content: Содержимое файла инцидента
    """
    filepath = os.path.join(INCIDENTS_DIR, filename)
    
    # Проверяем существование архивного файла
    if not os.path.exists(ARCHIVE_FILE):
        with open(ARCHIVE_FILE, 'w', encoding='utf-8') as f:
            f.write("# Архив инцидентов\n\n")
    
    # Добавляем инцидент в архив
    with open(ARCHIVE_FILE, 'a', encoding='utf-8') as f:
        f.write(f"\n\n## Архивировано: {filename}\n\n")
        f.write(content)
    
    # Удаляем оригинальный файл
    os.remove(filepath)
    
    print(f"Инцидент '{filename}' архивирован.")

def list_incidents(status_filter: Optional[str] = None) -> None:
    """
    Выводит список инцидентов.
    
    Args:
        status_filter: Фильтр по статусу
    """
    if not os.path.exists(INCIDENTS_DIR):
        print("Каталог инцидентов не найден.")
        return
    
    incidents = []
    
    # Собираем информацию о файлах инцидентов
    for filename in os.listdir(INCIDENTS_DIR):
        if filename.endswith(".md") and not filename in ["registry.md", "ai.incident.archive.md"]:
            filepath = os.path.join(INCIDENTS_DIR, filename)
            
            # Извлекаем информацию из файла
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Получаем заголовок
            title_match = re.search(r'# [^:]+: (.+)', content)
            title = title_match.group(1) if title_match else "Неизвестный инцидент"
            
            # Получаем статус
            status_match = re.search(r'- \*\*Статус\*\*: ([^\n]+)', content)
            status = status_match.group(1) if status_match else "Неизвестно"
            
            # Получаем приоритет
            priority_match = re.search(r'- \*\*Приоритет\*\*: ([^\n]+)', content)
            priority = priority_match.group(1) if priority_match else "Неизвестно"
            
            # Получаем дату создания
            date_match = re.search(r'- \*\*Дата создания\*\*: ([^\n]+)', content)
            date = date_match.group(1) if date_match else "Неизвестно"
            
            # Применяем фильтр по статусу
            if status_filter and status != status_filter:
                continue
            
            incidents.append({
                "filename": filename,
                "title": title,
                "status": status,
                "priority": priority,
                "date": date
            })
    
    # Сортируем по дате и статусу
    incidents.sort(key=lambda x: (x["date"], x["status"]))
    
    # Выводим информацию
    print(f"\n=== Список инцидентов ===")
    if status_filter:
        print(f"Фильтр: Статус = {status_filter}")
    print(f"Всего найдено: {len(incidents)}\n")
    
    if not incidents:
        print("Инциденты не найдены.")
        return
    
    # Форматируем вывод в виде таблицы
    print(f"{'Файл':<30} | {'Заголовок':<40} | {'Статус':<20} | {'Приоритет':<15} | {'Дата':<12}")
    print("-" * 120)
    
    for incident in incidents:
        print(f"{incident['filename']:<30} | {incident['title'][:40]:<40} | {incident['status']:<20} | {incident['priority']:<15} | {incident['date'][:12]:<12}")

def generate_statistics() -> None:
    """
    Генерирует статистику по инцидентам.
    """
    if not os.path.exists(INCIDENTS_DIR):
        print("Каталог инцидентов не найден.")
        return
    
    # Статистика по статусам
    status_counts = {status: 0 for status in STATUSES}
    priority_counts = {"Критический": 0, "Высокий": 0, "Средний": 0, "Низкий": 0, "Неизвестно": 0}
    
    # Статистика по времени
    dates = []
    
    # Собираем данные
    for filename in os.listdir(INCIDENTS_DIR):
        if filename.endswith(".md") and not filename in ["registry.md", "ai.incident.archive.md"]:
            filepath = os.path.join(INCIDENTS_DIR, filename)
            
            # Извлекаем информацию из файла
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Получаем статус
            status_match = re.search(r'- \*\*Статус\*\*: ([^\n]+)', content)
            status = status_match.group(1) if status_match else "Неизвестно"
            
            # Получаем приоритет
            priority_match = re.search(r'- \*\*Приоритет\*\*: ([^\n]+)', content)
            priority = priority_match.group(1) if priority_match else "Неизвестно"
            
            # Получаем дату создания
            date_match = re.search(r'- \*\*Дата создания\*\*: ([^\n]+)', content)
            if date_match:
                try:
                    date = datetime.datetime.strptime(date_match.group(1), "%d %b %Y")
                    dates.append(date)
                except ValueError:
                    pass
            
            # Обновляем счетчики
            if status in status_counts:
                status_counts[status] += 1
            
            if priority in priority_counts:
                priority_counts[priority] += 1
            else:
                priority_counts["Неизвестно"] += 1
    
    # Выводим статистику
    print("\n=== Статистика инцидентов ===")
    
    # Статистика по статусам
    print("\nРаспределение по статусам:")
    for status, count in status_counts.items():
        print(f"  {status}: {count}")
    
    # Статистика по приоритетам
    print("\nРаспределение по приоритетам:")
    for priority, count in priority_counts.items():
        print(f"  {priority}: {count}")
    
    # Статистика по времени
    if dates:
        print("\nВременная статистика:")
        dates.sort()
        first_date = dates[0]
        last_date = dates[-1]
        duration = (last_date - first_date).days
        
        print(f"  Первый инцидент: {first_date.strftime('%d %b %Y')}")
        print(f"  Последний инцидент: {last_date.strftime('%d %b %Y')}")
        print(f"  Период: {duration} дней")
        
        if duration > 0:
            print(f"  Среднее количество инцидентов в день: {len(dates) / duration:.2f}")
    
    # Общая статистика
    print("\nОбщая статистика:")
    active_incidents = sum(count for status, count in status_counts.items() if status != "Archived")
    print(f"  Всего инцидентов: {sum(status_counts.values())}")
    print(f"  Активных инцидентов: {active_incidents}")
    print(f"  Архивированных инцидентов: {status_counts.get('Archived', 0)}")

def main():
    """Основная функция."""
    parser = argparse.ArgumentParser(description="Управление инцидентами")
    subparsers = parser.add_subparsers(dest="command", help="Команда")
    
    # Команда для создания инцидента
    create_parser = subparsers.add_parser("create", help="Создать новый инцидент")
    create_parser.add_argument("description", help="Краткое описание инцидента")
    
    # Команда для обновления статуса инцидента
    update_parser = subparsers.add_parser("update", help="Обновить статус инцидента")
    update_parser.add_argument("filename", help="Имя файла инцидента")
    update_parser.add_argument("status", choices=STATUSES, help="Новый статус инцидента")
    update_parser.add_argument("note", help="Примечание к обновлению")
    
    # Команда для вывода списка инцидентов
    list_parser = subparsers.add_parser("list", help="Вывести список инцидентов")
    list_parser.add_argument("--status", choices=STATUSES, help="Фильтр по статусу")
    
    # Команда для генерации статистики
    stats_parser = subparsers.add_parser("stats", help="Вывести статистику по инцидентам")
    
    args = parser.parse_args()
    
    # Обработка команд
    if args.command == "create":
        filepath = create_incident(args.description)
        print(f"Инцидент создан: {filepath}")
    
    elif args.command == "update":
        update_incident_status(args.filename, args.status, args.note)
    
    elif args.command == "list":
        list_incidents(args.status)
    
    elif args.command == "stats":
        generate_statistics()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()