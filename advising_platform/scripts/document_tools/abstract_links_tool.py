#!/usr/bin/env python3
"""
Инструмент для работы с абстрактными ссылками в документах.
Позволяет преобразовывать ссылки между физическими и абстрактными форматами,
получать содержимое документов по абстрактным идентификаторам
и создавать новые абстрактные идентификаторы.
"""

import argparse
import os
import sys
import json
import requests
from urllib.parse import quote

# API-ключ для доступа к API
API_KEY = "advising-diagnostics-api-key"
API_BASE_URL = "http://localhost:5001/api"

def check_server_status():
    """Проверяет доступность API-сервера."""
    try:
        response = requests.get(f"{API_BASE_URL}/ping")
        if response.status_code == 200:
            return True
    except requests.exceptions.RequestException:
        pass
    return False

def make_api_request(endpoint, params=None, headers=None):
    """Выполняет запрос к API."""
    if not headers:
        headers = {}
    headers["X-API-Key"] = API_KEY
    
    if params:
        # Добавляем API-ключ в параметры
        params["api_key"] = API_KEY
    else:
        params = {"api_key": API_KEY}
    
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}", params=params, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Ошибка API: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return None

def convert_links(file_path, to_abstract=True):
    """Преобразует ссылки в документе."""
    # Проверяем существование файла
    if not os.path.exists(file_path):
        print(f"Ошибка: файл {file_path} не существует")
        return False
    
    # Формируем параметры запроса
    params = {
        "path": file_path,
        "to_abstract": "true" if to_abstract else "false"
    }
    
    # Выполняем запрос
    result = make_api_request("abstract/convert", params)
    
    if result:
        print(f"Успешно преобразованы ссылки в файле {file_path}")
        return True
    else:
        print(f"Не удалось преобразовать ссылки в файле {file_path}")
        return False

def list_identifiers(doc_type=None):
    """Выводит список логических идентификаторов."""
    # Формируем параметры запроса
    params = {}
    if doc_type:
        params["type"] = doc_type
    
    # Выполняем запрос
    result = make_api_request("abstract/list", params)
    
    if result and "identifiers" in result:
        identifiers = result["identifiers"]
        print(f"Найдено {len(identifiers)} логических идентификаторов:")
        
        # Группируем идентификаторы по типу
        grouped = {}
        for item in identifiers:
            identifier = item["identifier"]
            parts = identifier.split(":")
            doc_type = parts[0]
            
            if doc_type not in grouped:
                grouped[doc_type] = []
            
            grouped[doc_type].append(item)
        
        # Выводим идентификаторы по группам
        for dtype, items in grouped.items():
            print(f"\n== {dtype.upper()} ({len(items)}) ==")
            for item in items:
                identifier = item["identifier"]
                title = item["title"] or "Без заголовка"
                path = item["path"]
                print(f"  {identifier}")
                print(f"    Заголовок: {title}")
                print(f"    Путь: {path}")
        
        return True
    else:
        print("Не удалось получить список идентификаторов")
        return False

def get_document(identifier, show_content=False):
    """Получает и выводит информацию о документе по логическому идентификатору."""
    # Кодируем идентификатор для URL
    encoded_identifier = quote(identifier)
    
    # Выполняем запрос
    result = make_api_request(f"abstract/document/{encoded_identifier}")
    
    if result and "metadata" in result:
        metadata = result["metadata"]
        content = result.get("content", "")
        
        print(f"== Документ: {identifier} ==")
        print(f"Заголовок: {metadata.get('title', 'Не указан')}")
        print(f"Автор: {metadata.get('author', 'Не указан')}")
        print(f"Дата: {metadata.get('date', 'Не указана')}")
        print(f"Тип: {metadata.get('doc_type', 'Не указан')}")
        print(f"Путь: {metadata.get('path', 'Не указан')}")
        
        if show_content:
            print("\n== Содержимое документа ==\n")
            print(content)
        
        return True
    else:
        print(f"Не удалось получить информацию о документе {identifier}")
        return False

def search_documents(query):
    """Ищет документы по запросу."""
    # Формируем параметры запроса
    params = {"q": query}
    
    # Выполняем запрос
    result = make_api_request("search", params)
    
    if result and "results" in result:
        results = result["results"]
        print(f"Найдено {len(results)} документов по запросу '{query}':")
        
        for item in results:
            path = item.get("path", "")
            title = item.get("title", "Без заголовка")
            print(f"  {title}")
            print(f"    Путь: {path}")
        
        return True
    else:
        print(f"Не удалось выполнить поиск по запросу '{query}'")
        return False

def main():
    parser = argparse.ArgumentParser(description="Инструмент для работы с абстрактными ссылками")
    subparsers = parser.add_subparsers(dest="command", help="Команда")
    
    # Команда convert
    convert_parser = subparsers.add_parser("convert", help="Преобразует ссылки в документе")
    convert_parser.add_argument("file_path", help="Путь к файлу")
    convert_parser.add_argument("--to-physical", action="store_true", 
                              help="Преобразовать абстрактные ссылки в физические (по умолчанию - наоборот)")
    
    # Команда list
    list_parser = subparsers.add_parser("list", help="Выводит список логических идентификаторов")
    list_parser.add_argument("--type", help="Тип документа для фильтрации")
    
    # Команда get
    get_parser = subparsers.add_parser("get", help="Получает информацию о документе по идентификатору")
    get_parser.add_argument("identifier", help="Логический идентификатор документа")
    get_parser.add_argument("--show-content", action="store_true", help="Вывести содержимое документа")
    
    # Команда search
    search_parser = subparsers.add_parser("search", help="Ищет документы по запросу")
    search_parser.add_argument("query", help="Поисковый запрос")
    
    args = parser.parse_args()
    
    # Проверяем статус сервера
    if not check_server_status():
        print("Ошибка: API-сервер недоступен. Убедитесь, что он запущен.")
        return 1
    
    # Выполняем соответствующую команду
    if args.command == "convert":
        convert_links(args.file_path, not args.to_physical)
    elif args.command == "list":
        list_identifiers(args.type)
    elif args.command == "get":
        get_document(args.identifier, args.show_content)
    elif args.command == "search":
        search_documents(args.query)
    else:
        parser.print_help()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())