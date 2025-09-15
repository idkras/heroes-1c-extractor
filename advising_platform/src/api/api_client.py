#!/usr/bin/env python3
"""
Клиент для работы с API системы абстрактных идентификаторов.
Позволяет получать документы и ссылаться на них через логические идентификаторы.
"""

import argparse
import json
import os
import requests
import sys
from typing import Dict, List, Any, Optional

API_BASE_URL = "http://localhost:5001/api"
API_KEY = "advising-diagnostics-api-key"

def make_api_request(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Выполняет API-запрос."""
    url = f"{API_BASE_URL}/{endpoint}"
    
    # Добавляем API-ключ
    if params is None:
        params = {}
    params["api_key"] = API_KEY
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Ответ сервера: {e.response.text}")
        sys.exit(1)

def list_identifiers(doc_type: Optional[str] = None) -> None:
    """Выводит список логических идентификаторов."""
    params = {}
    if doc_type:
        params["type"] = doc_type
    
    data = make_api_request("abstract/list", params)
    identifiers = data.get("identifiers", [])
    
    print(f"Найдено {len(identifiers)} идентификаторов:")
    
    # Группируем по типу
    identifiers_by_type = {}
    for item in identifiers:
        identifier = item["identifier"]
        doc_type = identifier.split(":")[0]
        
        if doc_type not in identifiers_by_type:
            identifiers_by_type[doc_type] = []
        
        identifiers_by_type[doc_type].append(item)
    
    # Выводим группы
    for doc_type, items in identifiers_by_type.items():
        print(f"\n=== {doc_type.upper()} ({len(items)}) ===")
        for item in sorted(items, key=lambda x: x["identifier"]):
            print(f"{item['identifier']}")
            print(f"   Заголовок: {item['title'] or 'Без заголовка'}")
            if item['date']:
                print(f"   Дата: {item['date']}")
            if item['author']:
                print(f"   Автор: {item['author']}")
            print()

def get_document(identifier: str, show_content: bool = False) -> None:
    """Получает и выводит информацию о документе."""
    data = make_api_request(f"abstract/document/{identifier}")
    
    print(f"Документ: {identifier}")
    print(f"Путь: {data['metadata']['path']}")
    print(f"Заголовок: {data['metadata']['title'] or 'Без заголовка'}")
    
    if data['metadata']['date']:
        print(f"Дата: {data['metadata']['date']}")
    
    if data['metadata']['author']:
        print(f"Автор: {data['metadata']['author']}")
    
    if data['metadata']['doc_type']:
        print(f"Тип: {data['metadata']['doc_type']}")
    
    if show_content:
        print("\nСодержимое:")
        print("=" * 80)
        content = data.get("content", "")
        print(content[:2000] + "..." if len(content) > 2000 else content)
        print("=" * 80)

def convert_links(file_path: str, to_abstract: bool = True) -> None:
    """Преобразует ссылки в документе."""
    params = {
        "path": file_path,
        "to_abstract": str(to_abstract).lower()
    }
    
    data = make_api_request("abstract/convert", params)
    print(data.get("message", "Ошибка при преобразовании ссылок"))

def search_documents(query: str) -> None:
    """Ищет документы по запросу."""
    params = {
        "q": query
    }
    
    data = make_api_request("search", params)
    results = data.get("results", [])
    
    print(f"Найдено {len(results)} документов:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['path']}")
        if result.get('title'):
            print(f"   Заголовок: {result['title']}")
        if result.get('match_type'):
            print(f"   Тип совпадения: {result['match_type']}")
        if result.get('snippets'):
            print(f"   Фрагменты:")
            for snippet in result['snippets'][:2]:  # Показываем только первые 2 фрагмента
                print(f"   - {snippet}")
        print()

def main():
    parser = argparse.ArgumentParser(description='Клиент для работы с API системы абстрактных идентификаторов')
    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')
    
    # Команда list - список идентификаторов
    list_parser = subparsers.add_parser('list', help='Список логических идентификаторов')
    list_parser.add_argument('--type', help='Тип документа для фильтрации (standard, project, incident)')
    
    # Команда get - получение документа
    get_parser = subparsers.add_parser('get', help='Получение документа')
    get_parser.add_argument('identifier', help='Логический идентификатор документа')
    get_parser.add_argument('--content', action='store_true', help='Показать содержимое документа')
    
    # Команда convert - преобразование ссылок
    convert_parser = subparsers.add_parser('convert', help='Преобразование ссылок')
    convert_parser.add_argument('path', help='Путь к документу')
    convert_group = convert_parser.add_mutually_exclusive_group(required=True)
    convert_group.add_argument('--to-abstract', action='store_true', help='Преобразовать в абстрактные ссылки')
    convert_group.add_argument('--to-physical', action='store_true', help='Преобразовать в физические ссылки')
    
    # Команда search - поиск документов
    search_parser = subparsers.add_parser('search', help='Поиск документов')
    search_parser.add_argument('query', help='Поисковый запрос')
    
    args = parser.parse_args()
    
    # Обрабатываем команду
    if args.command == 'list':
        list_identifiers(args.type)
    elif args.command == 'get':
        get_document(args.identifier, args.content)
    elif args.command == 'convert':
        convert_links(args.path, args.to_abstract)
    elif args.command == 'search':
        search_documents(args.query)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()