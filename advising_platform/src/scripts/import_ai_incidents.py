#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт для импорта инцидентов из файла 'AI incidents.md' в базу данных.
"""

import os
import sys
import re
import json
import requests
from datetime import datetime

# Добавляем src к путям, чтобы импортировать модули из проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Получаем API URL из переменной окружения или используем значение по умолчанию
API_URL = os.environ.get('API_URL', 'http://localhost:5001/api')


def parse_incident(incident_text):
    """
    Разбирает текст инцидента для извлечения всей необходимой информации.
    
    Args:
        incident_text (str): Текст инцидента из файла
    
    Returns:
        dict: Словарь с данными инцидента
    """
    # Извлекаем заголовок (первая строка после ###)
    title_match = re.search(r'###\s+(.*?\d{2}:\d{2})?\s*-\s*(.+)', incident_text)
    if not title_match:
        return None
    
    # Если есть дата в заголовке, извлекаем её и заголовок отдельно
    if title_match.group(1):
        incident_date = title_match.group(1)
        title = title_match.group(2).strip()
    else:
        incident_date = datetime.now().strftime('%Y-%m-%d %H:%M')
        title = title_match.group(2).strip()
    
    # Ищем описание (обычно между заголовком и "5 почему разбор")
    description = ""
    desc_match = re.search(r'###.*?\n(.*?)(?:\*\*5 почему разбор\*\*|\*\*Корневая причина\*\*)', 
                          incident_text, re.DOTALL)
    if desc_match:
        description = desc_match.group(1).strip()
    
    # Если описание не найдено, используем первый пункт из "5 почему разбор"
    if not description:
        why_match = re.search(r'\*\*5 почему разбор\*\*:.*?\n1\. .*? - (.*?)\n', incident_text, re.DOTALL)
        if why_match:
            description = why_match.group(1).strip()
    
    # Ищем корневую причину
    root_cause = ""
    root_cause_match = re.search(r'\*\*Корневая причина\*\*:\s*(.*?)(?:\n\n|\*\*)', incident_text, re.DOTALL)
    if root_cause_match:
        root_cause = root_cause_match.group(1).strip()
    
    # Ищем анализ причин "5 почему"
    rca = ""
    rca_match = re.search(r'\*\*5 почему разбор\*\*:(.*?)(?:\*\*Корневая причина\*\*)', incident_text, re.DOTALL)
    if rca_match:
        rca = rca_match.group(1).strip()
    
    # Ищем предлагаемые решения
    proposed_solutions = {"immediate": [], "short_term": [], "long_term": []}
    
    # Ищем Дизайн изменения, который содержит решения
    design_changes_match = re.search(r'\*\*Дизайн изменения\*\*:(.*?)(?:\*\*Статус\*\*|\Z)', 
                                    incident_text, re.DOTALL)
    if design_changes_match:
        solutions_text = design_changes_match.group(1).strip()
        # Разбиваем на отдельные решения
        solutions = re.findall(r'\d+\)\s*(.*?)(?:\n|$)', solutions_text)
        
        # Распределяем решения по категориям
        for idx, solution in enumerate(solutions):
            if idx < 2:  # Первые 2 - срочные
                proposed_solutions["immediate"].append(solution.strip())
            elif idx < 4:  # Следующие 2 - краткосрочные
                proposed_solutions["short_term"].append(solution.strip())
            else:  # Остальные - долгосрочные
                proposed_solutions["long_term"].append(solution.strip())
    
    # Ищем статус
    status_match = re.search(r'\*\*Статус\*\*:\s*(.*?)(?:\n|$)', incident_text)
    status = status_match.group(1).strip() if status_match else "Зафиксирован"
    
    # Очищаем статус от дополнительной информации (в скобках)
    status = re.sub(r'\s*\(.*?\)\s*', '', status).strip()
    
    # Преобразуем статусы в формат API
    status_mapping = {
        "Recorded": "Зафиксирован",
        "In Progress": "В работе", 
        "Hypothesis Testing": "Проверка гипотезы",
        "Hypothesis Confirmed": "Гипотеза подтверждена",
        "Hypothesis Rejected": "Гипотеза не подтверждена",
        "Archived": "Архивирован",
        "Fixed": "Гипотеза подтверждена"  # Часто "Fixed" используется как синоним "Hypothesis Confirmed"
    }
    
    # Если статус на английском, переводим его
    if status in status_mapping:
        status = status_mapping[status]
    
    # Проверяем, что статус соответствует допустимым значениям
    valid_statuses = ["Зафиксирован", "В работе", "Проверка гипотезы", 
                       "Гипотеза подтверждена", "Гипотеза не подтверждена", "Архивирован"]
    
    if status not in valid_statuses:
        # По умолчанию используем "Зафиксирован"
        status = "Зафиксирован"
    
    # Ищем автора
    author_match = re.search(r'\*\*Ответственный\*\*:\s*(.*?)(?:\n|$)', incident_text)
    author = author_match.group(1).strip() if author_match else "AI Assistant"
    
    # Определяем приоритет на основе ключевых слов в тексте
    priority = "HIGH"  # По умолчанию используем "HIGH" (безопаснее, чем "MEDIUM")
    
    # Маппинг приоритетов (русских вариантов в константы API)
    priority_mapping = {
        "Критический": "CRITICAL",
        "Высокий": "HIGH",
        "Средний": "MEDIUM",
        "Низкий": "LOW",
        # Английские варианты тоже преобразуем
        "Critical": "CRITICAL",
        "High": "HIGH",
        "Medium": "MEDIUM", 
        "Low": "LOW"
    }
    
    # Проверяем наличие явного указания приоритета
    priority_match = re.search(r'\*\*Приоритет\*\*:\s*(.*?)(?:\n|$)', incident_text)
    if priority_match:
        matched_priority = priority_match.group(1).strip()
        # Проверяем маппинг
        if matched_priority in priority_mapping:
            priority = priority_mapping[matched_priority]
    
    # Дополнительная проверка по ключевым словам, если приоритет не найден явно
    else:
        if "критич" in incident_text.lower() or "блокир" in incident_text.lower():
            priority = "CRITICAL"
        elif "высок" in incident_text.lower() or "серьезн" in incident_text.lower():
            priority = "HIGH"
        elif "средн" in incident_text.lower():
            priority = "MEDIUM"
        elif "низк" in incident_text.lower() or "незначител" in incident_text.lower():
            priority = "LOW"
    
    # Проверяем, что приоритет соответствует допустимым значениям
    valid_priorities = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    
    if priority not in valid_priorities:
        # По умолчанию используем "HIGH"
        priority = "HIGH"
    
    # Определяем тип инцидента
    incident_type = "SYSTEM"  # По умолчанию
    
    # Маппинг типов инцидентов (русских вариантов в константы API)
    type_mapping = {
        "Системный": "SYSTEM",
        "Функциональный": "FUNCTIONAL", 
        "Безопасность": "SECURITY",
        "Производительность": "PERFORMANCE",
        # Английские варианты тоже преобразуем
        "System": "SYSTEM",
        "Functional": "FUNCTIONAL", 
        "Security": "SECURITY",
        "Performance": "PERFORMANCE"
    }
    
    # Проверяем наличие явного указания типа
    type_match = re.search(r'\*\*Тип инцидента\*\*:\s*(.*?)(?:\n|$)', incident_text)
    if type_match:
        matched_type = type_match.group(1).strip()
        # Проверяем маппинг
        if matched_type in type_mapping:
            incident_type = type_mapping[matched_type]
    
    # Дополнительная проверка по ключевым словам, если тип не найден явно
    else:
        if "функционал" in incident_text.lower() or "функция" in incident_text.lower():
            incident_type = "FUNCTIONAL"
        elif "безопас" in incident_text.lower() or "уязвим" in incident_text.lower():
            incident_type = "SECURITY"
        elif "производит" in incident_text.lower() or "скорост" in incident_text.lower():
            incident_type = "PERFORMANCE"
    
    # Проверяем, что тип соответствует допустимым значениям
    valid_types = ["SYSTEM", "FUNCTIONAL", "SECURITY", "PERFORMANCE"]
    
    if incident_type not in valid_types:
        # По умолчанию используем "SYSTEM"
        incident_type = "SYSTEM"
    
    # Ищем связанные стандарты
    standards = []
    design_injection_match = re.search(r'\*\*Дизайн-инъекция\*\*:\s*(.*?)(?:\n|$)', incident_text)
    if design_injection_match:
        injection_text = design_injection_match.group(1).lower()
        
        # Маппинг названий стандартов на их коды
        standard_mapping = {
            "task master": "standard:task_master",
            "registry standard": "standard:registry", 
            "ai incident": "standard:incident",
            "ai qa": "standard:ai_qa",
            "clir": "standard:clir",
            "root cause": "standard:root_cause",
            "design": "standard:design"
        }
        
        # Проверяем, упоминается ли стандарт
        for name, code in standard_mapping.items():
            if name in injection_text:
                standards.append(code)
        
        # Всегда добавляем task_master как базовый стандарт
        if "standard:task_master" not in standards:
            standards.append("standard:task_master")
    else:
        # Если не найдено, добавляем хотя бы базовый стандарт
        standards.append("standard:task_master")
    
    # Собираем данные инцидента
    incident_data = {
        "title": title,
        "description": description,
        "status": status,
        "priority": priority,
        "incident_type": incident_type,
        "author": author,
        "standards": standards
    }
    
    # Добавляем опциональные поля, если они есть
    if root_cause:
        incident_data["root_cause"] = root_cause
    
    if rca:
        incident_data["root_cause_analysis"] = rca
    
    if any(proposed_solutions.values()):
        incident_data["proposed_solutions"] = proposed_solutions
    
    return incident_data


def extract_incidents(file_path):
    """
    Извлекает все инциденты из файла markdown.
    
    Args:
        file_path (str): Путь к файлу инцидентов
    
    Returns:
        list: Список словарей с данными инцидентов
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ищем все блоки инцидентов, начинающиеся с ### и продолжающиеся до следующего ### или конца файла
        incidents_blocks = re.split(r'(?=###\s+\d+\s+[A-Za-zА-Яа-я]+\s+\d{4}\s+\d{2}:\d{2}\s+-\s+)', content)
        
        # Первый блок обычно содержит заголовок и вводную информацию, пропускаем его
        incidents_blocks = [block for block in incidents_blocks if block.strip().startswith('###')]
        
        # Разбираем каждый блок инцидента
        incidents = []
        for block in incidents_blocks:
            incident_data = parse_incident(block)
            if incident_data:
                incidents.append(incident_data)
        
        return incidents
    
    except Exception as e:
        print(f"Ошибка при извлечении инцидентов: {e}")
        return []


def import_incidents(incidents):
    """
    Импортирует инциденты в базу данных через API.
    
    Args:
        incidents (list): Список словарей с данными инцидентов
    
    Returns:
        tuple: (Количество успешно импортированных инцидентов, количество ошибок)
    """
    success_count = 0
    error_count = 0
    
    for incident in incidents:
        try:
            # Пропускаем инциденты без заголовка
            if not incident.get('title'):
                print(f"Пропущен инцидент без заголовка")
                error_count += 1
                continue
            
            # Проверяем, есть ли инцидент с таким же заголовком в API
            response = requests.get(f"{API_URL}/incidents", 
                                    params={"search": incident['title']})
            
            if response.status_code == 200:
                existing_incidents = response.json().get('incidents', [])
                
                # Пропускаем инцидент, если он уже существует
                if any(inc['title'] == incident['title'] for inc in existing_incidents):
                    print(f"Инцидент уже существует: {incident['title']}")
                    continue
            
            # Создаем инцидент
            response = requests.post(f"{API_URL}/incidents", 
                                     json=incident,
                                     headers={"Content-Type": "application/json"})
            
            if response.status_code == 201:
                print(f"Успешно импортирован инцидент: {incident['title']}")
                success_count += 1
            else:
                error_data = response.json()
                print(f"Ошибка при импорте инцидента {incident['title']}: {error_data.get('error', 'Неизвестная ошибка')}")
                print(f"Данные инцидента: {json.dumps(incident, ensure_ascii=False, indent=2)}")
                error_count += 1
        
        except Exception as e:
            print(f"Ошибка при импорте инцидента {incident.get('title', 'без названия')}: {str(e)}")
            error_count += 1
    
    return success_count, error_count


def main():
    file_path = 'incidents/AI incidents.md'
    
    print(f"Импорт инцидентов из файла: {file_path}")
    
    # Извлекаем инциденты из файла
    incidents = extract_incidents(file_path)
    
    if not incidents:
        print("Не удалось извлечь инциденты из файла")
        return
    
    print(f"Найдено {len(incidents)} инцидентов")
    
    # Импортируем инциденты в базу данных
    success_count, error_count = import_incidents(incidents)
    
    print(f"\nРезультаты импорта:")
    print(f"- Успешно импортировано: {success_count}")
    print(f"- Ошибок импорта: {error_count}")
    print(f"- Всего обработано: {len(incidents)}")


if __name__ == "__main__":
    main()