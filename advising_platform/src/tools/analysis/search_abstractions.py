#!/usr/bin/env python3
"""
Инструмент для семантического поиска по документации с поддержкой абстрактных идентификаторов.
Позволяет искать документы и возвращать результаты в форме абстрактных ссылок.
"""

import os
import re
import sys
import json
import argparse
import requests
from typing import Dict, Any, List, Optional, Tuple

# URL API-сервера
API_URL = 'http://localhost:5001/indexer'

def check_server_status() -> bool:
    """Проверяет доступность API-сервера."""
    try:
        response = requests.get(f"{API_URL}/stats", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def make_api_request(endpoint: str, params: Optional[Dict[str, Any]] = None, method: str = 'GET', data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Выполняет запрос к API."""
    url = f"{API_URL}/{endpoint}"
    headers = {'Content-Type': 'application/json'}
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, params=params, timeout=10)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers, timeout=10)
        else:
            print(f"Неподдерживаемый метод: {method}")
            sys.exit(1)
        
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Ошибка при выполнении запроса к API: {e}")
        sys.exit(1)

def search_documents(query: str, doc_type: Optional[str] = None, limit: int = 10, use_abstract: bool = True, format_mode: str = 'abstract') -> None:
    """
    Ищет документы по запросу.
    
    Args:
        query: Поисковый запрос
        doc_type: Тип документа для фильтрации (task, standard, etc.)
        limit: Максимальное количество результатов
        use_abstract: Использовать абстрактные идентификаторы
        format_mode: Формат вывода ссылок (abstract, url, markdown)
    """
    params = {
        'q': query,
        'abstract': 'true' if use_abstract else 'false',
        'limit': limit
    }
    
    if doc_type:
        params['type'] = doc_type
    
    response = make_api_request('search', params=params)
    
    if response and 'results' in response:
        print(f"Результаты поиска для запроса '{response.get('query', query)}':")
        
        if not response['results']:
            print("Документы не найдены.")
            return
        
        for i, result in enumerate(response['results'], 1):
            title = result.get('title', 'Без заголовка')
            doc_type = result.get('doc_type', 'неизвестный')
            path = result.get('path', 'Н/Д')
            relevance = result.get('relevance', 0)
            logical_id = result.get('logical_id')
            
            print(f"{i}. {title} ({doc_type})")
            
            # Форматируем ссылку в зависимости от режима
            if logical_id and use_abstract:
                if format_mode == 'abstract':
                    print(f"   Идентификатор: {logical_id}")
                elif format_mode == 'url':
                    print(f"   Ссылка: abstract://{logical_id}")
                elif format_mode == 'markdown':
                    print(f"   Markdown: [{title}](abstract://{logical_id})")
            else:
                print(f"   Путь: {path}")
            
            print(f"   Релевантность: {relevance:.2f}")
            
            if 'preview' in result:
                preview = result['preview'].replace('\n', ' ').strip()
                print(f"   Предпросмотр: {preview[:100]}...")
            print()
    else:
        print("Ошибка при выполнении поиска.")

def resolve_identifier(identifier: str) -> Optional[str]:
    """Преобразует абстрактный идентификатор в физический путь."""
    try:
        response = make_api_request(f'abstract/document/{identifier}')
        if response and 'path' in response:
            return response['path']
    except Exception:
        pass
    
    return None

def extract_identifiers_from_file(file_path: str) -> List[str]:
    """Извлекает абстрактные идентификаторы из файла."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ищем ссылки формата abstract://тип:идентификатор
        abstract_urls = re.findall(r'abstract://([a-z]+:[a-z0-9_.]+(?:#[a-z0-9_-]+)?)', content)
        
        # Ищем прямые ссылки формата тип:идентификатор
        direct_ids = re.findall(r'\]\(([a-z]+:[a-z0-9_.]+(?:#[a-z0-9_-]+)?)\)', content)
        
        # Объединяем результаты
        return list(set(abstract_urls + direct_ids))
    except Exception as e:
        print(f"Ошибка при чтении файла {file_path}: {e}")
        return []

def analyze_references(file_path: str) -> None:
    """Анализирует ссылки в документе."""
    identifiers = extract_identifiers_from_file(file_path)
    
    if not identifiers:
        print(f"В файле {file_path} не найдено абстрактных ссылок.")
        return
    
    print(f"Анализ абстрактных ссылок в файле {file_path}:")
    print(f"Найдено {len(identifiers)} абстрактных идентификаторов:")
    
    valid_count = 0
    broken_count = 0
    
    for i, identifier in enumerate(identifiers, 1):
        # Отделяем фрагмент, если есть
        base_id = identifier.split('#')[0] if '#' in identifier else identifier
        
        # Проверяем валидность идентификатора
        path = resolve_identifier(base_id)
        
        if path and os.path.exists(path):
            status = "✅ Валидный"
            valid_count += 1
        else:
            status = "❌ Нерабочий"
            broken_count += 1
        
        print(f"{i}. {identifier} -> {status}")
        if path:
            print(f"   Разрешается в: {path}")
        else:
            print(f"   Идентификатор не зарегистрирован")
    
    print(f"\nИтого: {valid_count} валидных, {broken_count} нерабочих ссылок")

def main():
    parser = argparse.ArgumentParser(description='Инструмент для поиска с поддержкой абстрактных идентификаторов.')
    subparsers = parser.add_subparsers(dest='command', help='Команда')
    
    # Команда search
    search_parser = subparsers.add_parser('search', help='Поиск по документам')
    search_parser.add_argument('query', help='Поисковый запрос')
    search_parser.add_argument('--type', help='Фильтр по типу документа (task, standard, etc.)')
    search_parser.add_argument('--limit', type=int, default=10, help='Максимальное количество результатов')
    search_parser.add_argument('--no-abstract', action='store_true', help='Не использовать абстрактные идентификаторы')
    search_parser.add_argument('--format', choices=['abstract', 'url', 'markdown'], default='abstract', 
                             help='Формат вывода ссылок')
    
    # Команда analyze
    analyze_parser = subparsers.add_parser('analyze', help='Анализ ссылок в документе')
    analyze_parser.add_argument('file', help='Путь к документу для анализа')
    
    args = parser.parse_args()
    
    # Проверяем статус сервера
    if not check_server_status():
        print("Ошибка: API-сервер недоступен. Убедитесь, что он запущен на http://localhost:5001")
        return
    
    if args.command == 'search':
        search_documents(args.query, args.type, args.limit, not args.no_abstract, args.format)
    elif args.command == 'analyze':
        analyze_references(args.file)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()