#!/usr/bin/env python3
"""
Инструмент командной строки для работы с абстрактными ссылками в документах.
Позволяет преобразовывать ссылки между физическими и абстрактными форматами,
получать содержимое документов по абстрактным идентификаторам
и создавать новые абстрактные идентификаторы.
"""

import os
import re
import sys
import json
import argparse
import requests
from typing import Dict, Any, Optional, List, Tuple

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

def list_identifiers(doc_type: Optional[str] = None) -> None:
    """Выводит список логических идентификаторов."""
    response = make_api_request('abstract/list')
    
    if response:
        print(f"Всего логических идентификаторов: {response.get('count', 0)}")
        
        if response.get('identifiers'):
            print("\nСписок идентификаторов:")
            for item in response['identifiers']:
                print(f"{item['identifier']} -> {item['path']}")
        else:
            print("Нет зарегистрированных логических идентификаторов.")

def register_identifier(path: str, identifier: str) -> None:
    """Регистрирует логический идентификатор для документа."""
    data = {
        'path': path,
        'identifier': identifier
    }
    
    response = make_api_request('abstract/register', method='POST', data=data)
    
    if response.get('success'):
        print(f"Успешно зарегистрирован идентификатор {identifier} для {path}")
    else:
        print(f"Ошибка при регистрации идентификатора: {response.get('error', 'Неизвестная ошибка')}")

def get_document(identifier: str, show_content: bool = False) -> None:
    """Получает и выводит информацию о документе по логическому идентификатору."""
    response = make_api_request(f'abstract/document/{identifier}')
    
    if response:
        print(f"Идентификатор: {identifier}")
        print(f"Путь: {response.get('path', 'Н/Д')}")
        print(f"Заголовок: {response.get('metadata', {}).get('title', 'Без заголовка')}")
        print(f"Тип: {response.get('metadata', {}).get('doc_type', 'Неизвестный')}")
        
        if show_content and 'content' in response:
            print("\nСодержимое:")
            print("=" * 80)
            print(response['content'])
            print("=" * 80)
    else:
        print(f"Документ не найден по идентификатору {identifier}")

def extract_markdown_links(content: str) -> List[Tuple[str, str]]:
    """Извлекает все Markdown-ссылки из текста."""
    # Регулярное выражение для поиска Markdown-ссылок:
    # - [текст ссылки](URL)
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    return re.findall(link_pattern, content)

def is_abstract_id(link: str) -> bool:
    """Проверяет, является ли ссылка абстрактным идентификатором."""
    # Абстрактные идентификаторы имеют формат: тип:идентификатор[#fragment]
    return bool(re.match(r'^[a-z]+:[a-z0-9_.]+(?:#[a-z0-9_-]+)?$', link))

def is_abstract_url(link: str) -> bool:
    """Проверяет, является ли ссылка URL с префиксом abstract://"""
    return link.startswith('abstract://')

def extract_fragment(link: str) -> Tuple[str, Optional[str]]:
    """
    Извлекает основную часть ссылки и фрагмент.
    Возвращает кортеж (основная_ссылка, фрагмент).
    Пример: 
        "abstract://standard:ticket#format" -> ("abstract://standard:ticket", "format")
        "standard:ticket#format" -> ("standard:ticket", "format")
        "[путь/к/файлу.md]" -> ("[путь/к/файлу.md]", None)
    """
    fragment_match = re.search(r'^(.+?)(?:#([a-z0-9_-]+))?$', link)
    if fragment_match:
        base_link = fragment_match.group(1)
        fragment = fragment_match.group(2)
        return base_link, fragment
    return link, None

def convert_links(file_path: str, to_abstract: bool = True) -> None:
    """Преобразует ссылки в документе."""
    if not os.path.isfile(file_path):
        print(f"Файл не найден: {file_path}")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return
    
    # Получаем все ссылки в документе
    links = extract_markdown_links(content)
    if not links:
        print("В документе не найдено ссылок для преобразования.")
        return
    
    # Словари для маппинга путей к идентификаторам и наоборот
    path_to_id = {}
    id_to_path = {}
    
    # Получаем список всех зарегистрированных идентификаторов
    response = make_api_request('abstract/list')
    if 'identifiers' in response:
        for item in response['identifiers']:
            id_to_path[item['identifier']] = item['path']
            path_to_id[item['path']] = item['identifier']
    
    # Преобразуем ссылки
    modified_content = content
    replaced_count = 0
    
    for text, link in links:
        base_link, fragment = extract_fragment(link)
        fragment_suffix = f"#{fragment}" if fragment else ""
        
        if to_abstract:
            # Преобразование физических путей в абстрактные идентификаторы в формате abstract://
            if base_link in path_to_id and not is_abstract_id(base_link) and not is_abstract_url(base_link):
                new_link = f"abstract://{path_to_id[base_link]}{fragment_suffix}"
                modified_content = modified_content.replace(f'[{text}]({link})', f'[{text}]({new_link})')
                replaced_count += 1
            # Преобразование идентификаторов типа:id в формат abstract://
            elif is_abstract_id(base_link) and not is_abstract_url(base_link):
                new_link = f"abstract://{base_link}{fragment_suffix}"
                modified_content = modified_content.replace(f'[{text}]({link})', f'[{text}]({new_link})')
                replaced_count += 1
        else:
            # Преобразование абстрактных идентификаторов (типа:id) в физические пути
            if is_abstract_id(base_link) and base_link in id_to_path:
                new_link = f"{id_to_path[base_link]}{fragment_suffix}"
                modified_content = modified_content.replace(f'[{text}]({link})', f'[{text}]({new_link})')
                replaced_count += 1
            # Преобразование abstract:// URL в физические пути
            elif is_abstract_url(base_link):
                abstract_id = base_link.replace('abstract://', '')
                if abstract_id in id_to_path:
                    new_link = f"{id_to_path[abstract_id]}{fragment_suffix}"
                    modified_content = modified_content.replace(f'[{text}]({link})', f'[{text}]({new_link})')
                    replaced_count += 1
    
    if replaced_count > 0:
        # Сохраняем измененный документ
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            print(f"Преобразовано {replaced_count} ссылок в документе.")
        except Exception as e:
            print(f"Ошибка при сохранении файла: {e}")
    else:
        print("Не найдено ссылок для преобразования.")

def search_documents(query: str) -> None:
    """Ищет документы по запросу."""
    params = {'q': query, 'abstract': 'true'}
    
    response = make_api_request('search', params=params)
    
    if response and 'results' in response:
        print(f"Результаты поиска для запроса '{response.get('query', query)}':")
        
        if not response['results']:
            print("Документы не найдены.")
            return
        
        for i, result in enumerate(response['results'], 1):
            print(f"{i}. {result.get('title', 'Без заголовка')} ({result.get('doc_type', 'неизвестный')})")
            print(f"   Путь: {result.get('path', 'Н/Д')}")
            
            if 'logical_id' in result:
                print(f"   Идентификатор: {result.get('logical_id')}")
            
            print(f"   Релевантность: {result.get('relevance', 0):.2f}")
            if 'preview' in result:
                preview = result['preview'].replace('\n', ' ').strip()
                print(f"   Предпросмотр: {preview[:100]}...")
            print()
    else:
        print("Ошибка при выполнении поиска.")

def main():
    parser = argparse.ArgumentParser(description='Инструмент для работы с абстрактными ссылками.')
    subparsers = parser.add_subparsers(dest='command', help='Команда')
    
    # Команда list
    list_parser = subparsers.add_parser('list', help='Вывести список логических идентификаторов')
    list_parser.add_argument('--type', help='Фильтр по типу документа')
    
    # Команда register
    register_parser = subparsers.add_parser('register', help='Зарегистрировать логический идентификатор')
    register_parser.add_argument('path', help='Путь к документу')
    register_parser.add_argument('identifier', help='Логический идентификатор (например, standard:api)')
    
    # Команда get
    get_parser = subparsers.add_parser('get', help='Получить документ по логическому идентификатору')
    get_parser.add_argument('identifier', help='Логический идентификатор')
    get_parser.add_argument('--content', action='store_true', help='Показать содержимое документа')
    
    # Команда convert
    convert_parser = subparsers.add_parser('convert', help='Преобразовать ссылки в документе')
    convert_parser.add_argument('file', help='Путь к документу для преобразования')
    convert_parser.add_argument('--to-physical', action='store_true', 
                               help='Преобразовать из абстрактных в физические (по умолчанию: физические -> абстрактные)')
    
    # Команда search
    search_parser = subparsers.add_parser('search', help='Поиск по индексированным документам')
    search_parser.add_argument('query', help='Поисковый запрос')
    
    args = parser.parse_args()
    
    # Проверяем статус сервера
    if not check_server_status():
        print("Ошибка: API-сервер недоступен. Убедитесь, что он запущен на http://localhost:5001")
        return
    
    if args.command == 'list':
        list_identifiers(args.type)
    elif args.command == 'register':
        register_identifier(args.path, args.identifier)
    elif args.command == 'get':
        get_document(args.identifier, args.content)
    elif args.command == 'convert':
        convert_links(args.file, not args.to_physical)
    elif args.command == 'search':
        search_documents(args.query)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()