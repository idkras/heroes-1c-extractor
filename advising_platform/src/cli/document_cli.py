#!/usr/bin/env python3
"""
Командный интерфейс для системы управления документами.
Позволяет выполнять операции с документами через абстрактные идентификаторы.
"""

import os
import sys
import argparse
import json

# Добавляем пути для импорта
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from advising_platform.advising_platform.src.core.document_abstractions import DocumentRegistry
except ImportError:
    print("Не удалось импортировать модуль document_abstractions.")
    sys.exit(1)

def handle_get(args, registry):
    """Обрабатывает команду get."""
    if args.standard:
        # Получение стандарта по имени
        standard_name = args.standard.lower().replace(' ', '_')
        metadata = registry.get_standard(standard_name)
        if metadata:
            print(f"Стандарт: {metadata.path}")
            if metadata.title:
                print(f"Заголовок: {metadata.title}")
            if metadata.date:
                print(f"Дата: {metadata.date}")
            if metadata.author:
                print(f"Автор: {metadata.author}")
            
            if args.content:
                print("\nСодержимое:")
                print("=" * 80)
                try:
                    with open(metadata.path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        print(content[:1000] + "..." if len(content) > 1000 else content)
                except Exception as e:
                    print(f"Ошибка при чтении файла: {e}")
                print("=" * 80)
        else:
            print(f"Стандарт '{args.standard}' не найден")
            
            # Показываем список доступных стандартов
            standards = []
            for identifier, metadata in registry.id_mapping.items():
                if identifier.startswith('standard:'):
                    standard_name = identifier.split(':')[1]
                    standards.append((standard_name, metadata.title or "Без названия"))
            
            if standards:
                print("\nДоступные стандарты:")
                for name, title in sorted(standards):
                    print(f"- {name} ({title})")
    
    elif args.project:
        # Получение документов проекта
        project_name = args.project.lower()
        doc_type = args.type.lower() if args.type else None
        
        docs = registry.get_project_document(project_name, doc_type)
        if docs:
            print(f"Документы проекта '{args.project}':")
            for i, doc in enumerate(docs, 1):
                print(f"{i}. {doc.path}")
                if doc.title:
                    print(f"   Заголовок: {doc.title}")
                if doc.date:
                    print(f"   Дата: {doc.date}")
        else:
            print(f"Документы проекта '{args.project}' не найдены")
            
            # Показываем список доступных проектов
            projects = set()
            for identifier in registry.id_mapping:
                if identifier.startswith('project:'):
                    project_name = identifier.split(':')[1]
                    projects.add(project_name)
            
            if projects:
                print("\nДоступные проекты:")
                for name in sorted(projects):
                    print(f"- {name}")
    
    elif args.id:
        # Получение документа по логическому идентификатору
        metadata = registry.get_document(args.id)
        if metadata:
            print(f"Документ: {metadata.path}")
            if metadata.title:
                print(f"Заголовок: {metadata.title}")
            if metadata.date:
                print(f"Дата: {metadata.date}")
            if metadata.author:
                print(f"Автор: {metadata.author}")
            
            if args.content:
                print("\nСодержимое:")
                print("=" * 80)
                try:
                    with open(metadata.path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        print(content[:1000] + "..." if len(content) > 1000 else content)
                except Exception as e:
                    print(f"Ошибка при чтении файла: {e}")
                print("=" * 80)
        else:
            print(f"Документ с идентификатором '{args.id}' не найден")

def handle_search(args, registry):
    """Обрабатывает команду search."""
    results = registry.search(args.query)
    print(f"Результаты поиска '{args.query}' ({len(results)} результатов):")
    
    # Ограничиваем количество результатов
    limit = args.limit if args.limit else 10
    for i, metadata in enumerate(results[:limit], 1):
        print(f"{i}. {metadata.path}")
        if metadata.title:
            print(f"   Заголовок: {metadata.title}")
        if metadata.date:
            print(f"   Дата: {metadata.date}")
        print()
    
    if len(results) > limit:
        print(f"...и еще {len(results) - limit} результатов")

def handle_convert(args, registry):
    """Обрабатывает команду convert."""
    if not os.path.exists(args.path):
        print(f"Файл {args.path} не существует")
        return
    
    to_abstract = args.to_abstract
    to_physical = args.to_physical
    
    if not to_abstract and not to_physical:
        print("Укажите тип преобразования: --to-abstract или --to-physical")
        return
    
    if to_abstract:
        result = registry.update_document_links(args.path, to_abstract=True)
        if result:
            print(f"Документ {args.path} успешно обновлен с абстрактными ссылками")
    elif to_physical:
        result = registry.update_document_links(args.path, to_abstract=False)
        if result:
            print(f"Документ {args.path} успешно обновлен с физическими ссылками")

def handle_list(args, registry):
    """Обрабатывает команду list."""
    if args.standards:
        # Список стандартов
        standards = []
        for identifier, metadata in registry.id_mapping.items():
            if identifier.startswith('standard:'):
                standard_name = identifier.split(':')[1]
                standards.append((standard_name, metadata.title or "Без названия", metadata.date or "Без даты"))
        
        print(f"Список стандартов ({len(standards)}):")
        for name, title, date in sorted(standards):
            print(f"- {name}: {title} ({date})")
    
    elif args.projects:
        # Список проектов
        projects = set()
        for identifier in registry.id_mapping:
            if identifier.startswith('project:'):
                project_name = identifier.split(':')[1]
                projects.add(project_name)
        
        print(f"Список проектов ({len(projects)}):")
        for name in sorted(projects):
            print(f"- {name}")
            
            # Показываем документы проекта
            if args.details:
                docs = registry.get_project_document(name)
                for doc in docs:
                    print(f"  - {os.path.basename(doc.path)}")
                    if doc.title:
                        print(f"    {doc.title}")
    
    elif args.identifiers:
        # Список всех идентификаторов
        print(f"Список логических идентификаторов ({len(registry.id_mapping)}):")
        for identifier, metadata in sorted(registry.id_mapping.items()):
            print(f"- {identifier}: {metadata.path}")

def handle_export(args, registry):
    """Обрабатывает команду export."""
    registry.export_to_json(args.output)

def handle_info(args, registry):
    """Обрабатывает команду info."""
    print("Информация о системе управления документами:")
    print(f"Всего документов: {len(registry.documents)}")
    print(f"Логических идентификаторов: {len(registry.id_mapping)}")
    
    # Статистика по типам документов
    doc_types = {}
    for metadata in registry.documents.values():
        doc_type = metadata.doc_type
        if doc_type:
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
    
    print("\nРаспределение по типам документов:")
    for doc_type, count in sorted(doc_types.items(), key=lambda x: x[1], reverse=True):
        print(f"- {doc_type}: {count}")
    
    # Статистика по авторам
    authors = {}
    for metadata in registry.documents.values():
        author = metadata.author
        if author:
            authors[author] = authors.get(author, 0) + 1
    
    print("\nРаспределение по авторам:")
    for author, count in sorted(authors.items(), key=lambda x: x[1], reverse=True):
        print(f"- {author}: {count}")

def main():
    parser = argparse.ArgumentParser(description='Управление документами через абстрактные идентификаторы')
    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')
    
    # Команда get - получение документов
    get_parser = subparsers.add_parser('get', help='Получение документа')
    get_group = get_parser.add_mutually_exclusive_group(required=True)
    get_group.add_argument('--standard', help='Имя стандарта')
    get_group.add_argument('--project', help='Имя проекта')
    get_group.add_argument('--id', help='Логический идентификатор')
    get_parser.add_argument('--type', help='Тип документа проекта (для --project)')
    get_parser.add_argument('--content', action='store_true', help='Показать содержимое документа')
    
    # Команда search - поиск документов
    search_parser = subparsers.add_parser('search', help='Поиск документов')
    search_parser.add_argument('query', help='Поисковый запрос')
    search_parser.add_argument('--limit', type=int, help='Ограничение количества результатов')
    
    # Команда convert - преобразование ссылок
    convert_parser = subparsers.add_parser('convert', help='Преобразование ссылок')
    convert_parser.add_argument('path', help='Путь к документу')
    convert_group = convert_parser.add_mutually_exclusive_group(required=True)
    convert_group.add_argument('--to-abstract', action='store_true', help='Преобразовать в абстрактные ссылки')
    convert_group.add_argument('--to-physical', action='store_true', help='Преобразовать в физические ссылки')
    
    # Команда list - список документов
    list_parser = subparsers.add_parser('list', help='Список документов')
    list_group = list_parser.add_mutually_exclusive_group(required=True)
    list_group.add_argument('--standards', action='store_true', help='Список стандартов')
    list_group.add_argument('--projects', action='store_true', help='Список проектов')
    list_group.add_argument('--identifiers', action='store_true', help='Список логических идентификаторов')
    list_parser.add_argument('--details', action='store_true', help='Показать подробную информацию')
    
    # Команда export - экспорт реестра
    export_parser = subparsers.add_parser('export', help='Экспорт реестра')
    export_parser.add_argument('--output', default='document_registry.json', help='Имя выходного файла')
    
    # Команда info - информация о системе
    info_parser = subparsers.add_parser('info', help='Информация о системе')
    
    args = parser.parse_args()
    
    # Создаем реестр документов
    registry = DocumentRegistry()
    
    # Обрабатываем команду
    if args.command == 'get':
        handle_get(args, registry)
    elif args.command == 'search':
        handle_search(args, registry)
    elif args.command == 'convert':
        handle_convert(args, registry)
    elif args.command == 'list':
        handle_list(args, registry)
    elif args.command == 'export':
        handle_export(args, registry)
    elif args.command == 'info':
        handle_info(args, registry)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()