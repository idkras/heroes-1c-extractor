#!/usr/bin/env python3
"""
Пример клиента для веб-хуков Advising Diagnostics API.
Демонстрирует получение стандартов и проектов через API и их обработку.
"""

import requests
import json
import os
import sys
import argparse
from datetime import datetime

# Настройки API
API_BASE_URL = "http://localhost:5001/api"
API_KEY = "advising-diagnostics-api-key"

def make_api_request(endpoint, params=None):
    """Выполняет запрос к API и возвращает результат."""
    url = f"{API_BASE_URL}/{endpoint}"
    headers = {"X-API-Key": API_KEY}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Проверка на HTTP-ошибки
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return None

def get_standards():
    """Получает список стандартов из API."""
    return make_api_request("standards")

def get_projects():
    """Получает список проектов из API."""
    return make_api_request("projects")

def get_file_content(file_path):
    """Получает содержимое файла из API."""
    endpoint = f"file/{file_path}"
    return make_api_request(endpoint)

def search_files(query):
    """Выполняет поиск по файлам."""
    return make_api_request("search", {"q": query})

def save_to_json(data, filename):
    """Сохраняет данные в JSON-файл."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, ensure_ascii=False, indent=2, fp=f)
        print(f"Файл {filename} успешно сохранен")
    except Exception as e:
        print(f"Ошибка при сохранении файла {filename}: {e}")

def download_all_standards():
    """Загружает все стандарты и сохраняет их локально."""
    standards_data = get_standards()
    if not standards_data or "standards" not in standards_data:
        print("Не удалось получить список стандартов")
        return
    
    # Создаем директорию для сохранения стандартов
    output_dir = "downloaded_standards"
    os.makedirs(output_dir, exist_ok=True)
    
    # Сохраняем список стандартов
    save_to_json(standards_data, os.path.join(output_dir, "standards_index.json"))
    
    # Загружаем и сохраняем каждый стандарт
    for standard in standards_data["standards"]:
        file_path = standard["path"]
        content_data = get_file_content(file_path)
        
        if content_data and "content" in content_data:
            # Создаем имя файла на основе пути
            file_name = os.path.basename(file_path)
            output_path = os.path.join(output_dir, file_name)
            
            # Сохраняем содержимое в markdown-файл
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content_data["content"])
                print(f"Сохранен стандарт: {file_name}")
            except Exception as e:
                print(f"Ошибка при сохранении стандарта {file_name}: {e}")
    
    print(f"Все стандарты загружены в директорию {output_dir}")

def download_all_projects():
    """Загружает все проекты и сохраняет их локально."""
    projects_data = get_projects()
    if not projects_data or "projects" not in projects_data:
        print("Не удалось получить список проектов")
        return
    
    # Создаем директорию для сохранения проектов
    output_dir = "downloaded_projects"
    os.makedirs(output_dir, exist_ok=True)
    
    # Сохраняем список проектов
    save_to_json(projects_data, os.path.join(output_dir, "projects_index.json"))
    
    # Загружаем и сохраняем каждый проект
    for project in projects_data["projects"]:
        project_name = project["name"]
        project_dir = os.path.join(output_dir, project_name)
        os.makedirs(project_dir, exist_ok=True)
        
        # Загружаем каждый файл проекта
        for file_info in project["files"]:
            file_path = file_info["path"]
            content_data = get_file_content(file_path)
            
            if content_data and "content" in content_data:
                # Создаем имя файла на основе пути
                file_name = os.path.basename(file_path)
                output_path = os.path.join(project_dir, file_name)
                
                # Сохраняем содержимое в markdown-файл
                try:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(content_data["content"])
                    print(f"Сохранен файл проекта: {project_name}/{file_name}")
                except Exception as e:
                    print(f"Ошибка при сохранении файла {project_name}/{file_name}: {e}")
    
    print(f"Все проекты загружены в директорию {output_dir}")

def generate_report():
    """Генерирует отчет о стандартах и проектах."""
    # Получаем данные о стандартах и проектах
    standards_data = get_standards()
    projects_data = get_projects()
    
    if not standards_data or not projects_data:
        print("Не удалось получить данные для отчета")
        return
    
    # Создаем отчет в формате markdown
    report = f"""# Отчет о стандартах и проектах Advising Diagnostics

*Сгенерировано: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*

## Обзор стандартов

Всего стандартов: {len(standards_data.get("standards", []))}

| Название файла | Категория | Тип | Заголовок |
|---------------|-----------|-----|-----------|
"""
    
    # Добавляем информацию о стандартах
    for standard in standards_data.get("standards", []):
        report += f"| {standard.get('filename', 'Н/Д')} | {standard.get('category', 'Н/Д')} | {standard.get('type', 'Н/Д')} | {standard.get('title', 'Н/Д')} |\n"
    
    report += f"""
## Обзор проектов

Всего проектов: {len(projects_data.get("projects", []))}

"""
    
    # Добавляем информацию о проектах
    for project in projects_data.get("projects", []):
        project_name = project.get("name", "Н/Д")
        project_files = project.get("files", [])
        
        report += f"### Проект: {project_name}\n\n"
        report += f"Количество файлов: {len(project_files)}\n\n"
        
        if project_files:
            report += "| Файл | Тип | Заголовок |\n"
            report += "|------|-----|----------|\n"
            
            for file_info in project_files:
                report += f"| {file_info.get('filename', 'Н/Д')} | {file_info.get('type', 'Н/Д')} | {file_info.get('title', 'Н/Д')} |\n"
            
            report += "\n"
    
    # Сохраняем отчет
    report_file = "advising_diagnostics_report.md"
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Отчет сохранен в файл {report_file}")
    except Exception as e:
        print(f"Ошибка при сохранении отчета: {e}")

def main():
    """Основная функция программы."""
    parser = argparse.ArgumentParser(description="Клиент для Advising Diagnostics API")
    parser.add_argument("action", choices=["standards", "projects", "file", "search", 
                                          "download-standards", "download-projects", "report"],
                       help="Действие для выполнения")
    parser.add_argument("--query", "-q", help="Поисковый запрос для действия 'search'")
    parser.add_argument("--file", "-f", help="Путь к файлу для действия 'file'")
    parser.add_argument("--output", "-o", help="Путь для сохранения результатов")
    
    args = parser.parse_args()
    
    # Выполняем выбранное действие
    if args.action == "standards":
        data = get_standards()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        
    elif args.action == "projects":
        data = get_projects()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        
    elif args.action == "file":
        if not args.file:
            print("Необходимо указать путь к файлу с помощью --file")
            return
        data = get_file_content(args.file)
        print(json.dumps(data, ensure_ascii=False, indent=2))
        
    elif args.action == "search":
        if not args.query:
            print("Необходимо указать поисковый запрос с помощью --query")
            return
        data = search_files(args.query)
        print(json.dumps(data, ensure_ascii=False, indent=2))
        
    elif args.action == "download-standards":
        download_all_standards()
        
    elif args.action == "download-projects":
        download_all_projects()
        
    elif args.action == "report":
        generate_report()

if __name__ == "__main__":
    main()