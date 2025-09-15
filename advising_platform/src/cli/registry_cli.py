#!/usr/bin/env python3
"""
Инструмент командной строки для управления реестром документов.

Предоставляет интерфейс для:
1. Поиска и регистрации документов
2. Проверки и обнаружения дубликатов
3. Управления связями между документами
4. Визуализации структуры реестра
5. Экспорта и импорта данных
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set, Any

# Добавляем корневую директорию в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем улучшенный модуль реестра документов
from advising_platform.content_deduplication import (
    DocumentRegistry, generate_content_hash, extract_metadata_from_task,
    extract_metadata_from_incident, DOCUMENT_TYPES
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('registry.log')
    ]
)
logger = logging.getLogger("registry_cli")


def handle_list(args):
    """
    Обрабатывает команду 'list' для отображения списка документов.
    
    Args:
        args: Аргументы командной строки
    """
    registry = DocumentRegistry.get_instance()
    
    # Применяем фильтры
    filtered_docs = {}
    for path, metadata in registry.documents.items():
        # Фильтр по типу
        if args.type and metadata.document_type != args.type:
            continue
        
        # Фильтр по статусу
        if args.status and metadata.status != args.status:
            continue
        
        # Фильтр по тегу
        if args.tag and args.tag not in metadata.tags:
            continue
        
        # Фильтр по поисковому запросу
        if args.query:
            query = args.query.lower()
            if (query not in metadata.title.lower() and 
                query not in path.lower() and
                not any(query in tag.lower() for tag in metadata.tags)):
                continue
        
        filtered_docs[path] = metadata
    
    # Сортировка результатов
    if args.sort == 'title':
        sorted_items = sorted(filtered_docs.items(), key=lambda x: x[1].title)
    elif args.sort == 'updated':
        sorted_items = sorted(filtered_docs.items(), key=lambda x: x[1].updated_at, reverse=True)
    elif args.sort == 'type':
        sorted_items = sorted(filtered_docs.items(), key=lambda x: x[1].document_type)
    elif args.sort == 'status':
        sorted_items = sorted(filtered_docs.items(), key=lambda x: x[1].status)
    else:  # path
        sorted_items = sorted(filtered_docs.items())
    
    # Вывод результатов
    if not filtered_docs:
        print("Документы не найдены")
        return
    
    print(f"Найдено {len(filtered_docs)} документов:")
    for path, metadata in sorted_items:
        tags_str = ", ".join(metadata.tags) if metadata.tags else ""
        related_count = len(metadata.related_documents)
        
        # Базовый вывод
        print(f"[{metadata.document_type}] {metadata.title} ({path})")
        
        # Подробный вывод
        if args.verbose:
            print(f"  Статус: {metadata.status}")
            print(f"  Создан: {metadata.created_at}")
            print(f"  Обновлен: {metadata.updated_at}")
            print(f"  Версия: {metadata.version}")
            print(f"  Теги: {tags_str}")
            print(f"  Связи: {related_count}")
            if metadata.logical_id:
                print(f"  ID: {metadata.logical_id}")
            print()


def handle_search(args):
    """
    Обрабатывает команду 'search' для поиска документов по содержимому.
    
    Args:
        args: Аргументы командной строки
    """
    registry = DocumentRegistry.get_instance()
    
    if not args.query:
        print("Необходимо указать поисковый запрос")
        return
    
    query = args.query.lower()
    results = []
    
    # Поиск по содержимому
    for path, metadata in registry.documents.items():
        # Применяем базовые фильтры
        if args.type and metadata.document_type != args.type:
            continue
        
        if args.status and metadata.status != args.status:
            continue
        
        # Пропускаем файлы, которых нет на диске
        if not os.path.exists(path):
            continue
        
        # Читаем содержимое
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
            
            if query in content:
                # Находим контекст вокруг совпадения
                context = ""
                lines = content.splitlines()
                for i, line in enumerate(lines):
                    if query in line:
                        # Получаем контекст (до 2 строк до и после)
                        start = max(0, i - 2)
                        end = min(len(lines), i + 3)
                        context = "\n".join(lines[start:end])
                        break
                
                results.append((path, metadata, context))
        except Exception as e:
            logger.warning(f"Ошибка при чтении файла {path}: {str(e)}")
    
    # Сортировка результатов
    if args.sort == 'title':
        results.sort(key=lambda x: x[1].title)
    elif args.sort == 'updated':
        results.sort(key=lambda x: x[1].updated_at, reverse=True)
    elif args.sort == 'type':
        results.sort(key=lambda x: x[1].document_type)
    else:  # path
        results.sort(key=lambda x: x[0])
    
    # Вывод результатов
    if not results:
        print("Совпадения не найдены")
        return
    
    print(f"Найдено {len(results)} совпадений:")
    for path, metadata, context in results:
        print(f"[{metadata.document_type}] {metadata.title} ({path})")
        
        # Выводим контекст
        if args.verbose:
            print("Контекст:")
            print("---")
            print(context)
            print("---")
            print()


def handle_register(args):
    """
    Обрабатывает команду 'register' для регистрации документов в реестре.
    
    Args:
        args: Аргументы командной строки
    """
    registry = DocumentRegistry.get_instance()
    
    # Проверяем аргументы
    if not args.path:
        print("Необходимо указать путь к документу")
        return
    
    # Получаем абсолютный путь
    path = os.path.abspath(args.path)
    
    # Проверяем существование файла
    if not os.path.exists(path):
        print(f"Файл не найден: {path}")
        return
    
    # Определяем тип документа
    doc_type = args.type
    if not doc_type:
        # Пытаемся определить тип по имени файла
        filename = os.path.basename(path).lower()
        if "todo" in filename or "task" in filename:
            doc_type = "task"
        elif "incident" in filename:
            doc_type = "incident"
        elif "standard" in filename:
            doc_type = "standard"
        elif "project" in filename:
            doc_type = "project"
        elif "report" in filename:
            doc_type = "report"
        else:
            print("Не удалось определить тип документа, укажите его явно с помощью --type")
            return
    
    # Проверяем корректность типа
    if doc_type not in DOCUMENT_TYPES:
        print(f"Некорректный тип документа: {doc_type}")
        print(f"Доступные типы: {', '.join(DOCUMENT_TYPES.keys())}")
        return
    
    # Читаем содержимое
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Ошибка при чтении файла: {str(e)}")
        return
    
    # Парсим теги
    tags = []
    if args.tags:
        tags = [tag.strip() for tag in args.tags.split(',')]
    
    # Парсим связи
    related = []
    if args.related:
        related = [os.path.abspath(rel.strip()) for rel in args.related.split(',')]
    
    # Регистрируем документ
    try:
        registry.register_document(
            file_path=path,
            document_type=doc_type,
            content=content,
            title=args.title,
            tags=tags,
            related_documents=related,
            logical_id=args.logical_id
        )
        print(f"Документ успешно зарегистрирован: {path}")
    except Exception as e:
        print(f"Ошибка при регистрации документа: {str(e)}")


def handle_check_duplicates(args):
    """
    Обрабатывает команду 'check-duplicates' для проверки документа на дубликаты.
    
    Args:
        args: Аргументы командной строки
    """
    registry = DocumentRegistry.get_instance()
    
    # Проверяем аргументы
    if not args.path:
        print("Необходимо указать путь к документу")
        return
    
    # Получаем абсолютный путь
    path = os.path.abspath(args.path)
    
    # Проверяем существование файла
    if not os.path.exists(path):
        print(f"Файл не найден: {path}")
        return
    
    # Определяем тип документа
    doc_type = args.type
    if not doc_type:
        # Пытаемся определить тип по имени файла
        filename = os.path.basename(path).lower()
        if "todo" in filename or "task" in filename:
            doc_type = "task"
        elif "incident" in filename:
            doc_type = "incident"
        else:
            doc_type = None  # Проверяем среди всех типов
    
    # Читаем содержимое
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Ошибка при чтении файла: {str(e)}")
        return
    
    # Проверяем на дубликаты
    try:
        is_duplicate, duplicate_path, similarity = registry.check_for_duplicates(
            content=content,
            document_type=doc_type,
            similarity_threshold=args.threshold
        )
        
        if is_duplicate:
            print(f"Найден дубликат: {duplicate_path}")
            print(f"Коэффициент схожести: {similarity:.2%}")
            
            # Дополнительная информация о дубликате
            if duplicate_path in registry.documents:
                metadata = registry.documents[duplicate_path]
                print(f"Тип документа: {metadata.document_type}")
                print(f"Заголовок: {metadata.title}")
                print(f"Статус: {metadata.status}")
                print(f"Последнее обновление: {metadata.updated_at}")
        else:
            print("Дубликаты не найдены")
            
            # Если задан флаг verbose, выводим наиболее похожие документы
            if args.verbose:
                print("\nНаиболее похожие документы:")
                # Получаем топ-3 наиболее похожих документа
                similar_docs = []
                for doc_path, metadata in registry.documents.items():
                    # Пропускаем файлы, которых нет на диске
                    if not os.path.exists(doc_path):
                        continue
                    
                    # Пропускаем, если задан тип документа и он не совпадает
                    if doc_type and metadata.document_type != doc_type:
                        continue
                    
                    try:
                        with open(doc_path, 'r', encoding='utf-8') as f:
                            doc_content = f.read()
                        
                        # Очищаем содержимое для сравнения
                        cleaned_content = registry._clean_content_for_comparison(content)
                        doc_cleaned = registry._clean_content_for_comparison(doc_content)
                        
                        # Вычисляем степень схожести
                        import difflib
                        similarity = difflib.SequenceMatcher(None, cleaned_content, doc_cleaned).ratio()
                        
                        similar_docs.append((doc_path, metadata, similarity))
                    except Exception as e:
                        logger.warning(f"Ошибка при чтении файла {doc_path}: {str(e)}")
                
                # Сортируем по убыванию схожести и выбираем топ-3
                similar_docs.sort(key=lambda x: x[2], reverse=True)
                for doc_path, metadata, sim in similar_docs[:3]:
                    print(f"- {metadata.title} ({doc_path}): {sim:.2%}")
    except Exception as e:
        print(f"Ошибка при проверке на дубликаты: {str(e)}")


def handle_update(args):
    """
    Обрабатывает команду 'update' для обновления метаданных документа.
    
    Args:
        args: Аргументы командной строки
    """
    registry = DocumentRegistry.get_instance()
    
    # Проверяем аргументы
    if not args.path:
        print("Необходимо указать путь к документу")
        return
    
    # Получаем абсолютный путь
    path = os.path.abspath(args.path)
    
    # Проверяем существование файла
    if not os.path.exists(path):
        print(f"Файл не найден: {path}")
        return
    
    # Проверяем наличие в реестре
    if path not in registry.documents:
        print(f"Документ не найден в реестре: {path}")
        print("Сначала зарегистрируйте его с помощью команды 'register'")
        return
    
    # Читаем содержимое
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Ошибка при чтении файла: {str(e)}")
        return
    
    # Парсим теги
    tags = None
    if args.tags:
        tags = [tag.strip() for tag in args.tags.split(',')]
    
    # Парсим связи
    related = None
    if args.related:
        related = [os.path.abspath(rel.strip()) for rel in args.related.split(',')]
    
    # Обновляем метаданные
    try:
        registry.update_document(
            file_path=path,
            content=content,
            title=args.title,
            tags=tags,
            related_documents=related,
            status=args.status,
            logical_id=args.logical_id
        )
        print(f"Документ успешно обновлен: {path}")
    except Exception as e:
        print(f"Ошибка при обновлении документа: {str(e)}")


def handle_archive(args):
    """
    Обрабатывает команду 'archive' для архивации документа.
    
    Args:
        args: Аргументы командной строки
    """
    registry = DocumentRegistry.get_instance()
    
    # Проверяем аргументы
    if not args.path:
        print("Необходимо указать путь к документу")
        return
    
    # Получаем абсолютный путь
    path = os.path.abspath(args.path)
    
    # Проверяем существование файла
    if not os.path.exists(path):
        print(f"Файл не найден: {path}")
        return
    
    # Проверяем наличие в реестре
    if path not in registry.documents:
        print(f"Документ не найден в реестре: {path}")
        print("Сначала зарегистрируйте его с помощью команды 'register'")
        return
    
    # Архивируем документ
    try:
        success, archive_path = registry.archive_document(path, reason=args.reason)
        if success:
            print(f"Документ успешно архивирован: {path} -> {archive_path}")
        else:
            print(f"Не удалось архивировать документ: {path}")
    except Exception as e:
        print(f"Ошибка при архивации документа: {str(e)}")


def handle_relation(args):
    """
    Обрабатывает команду 'relation' для управления связями между документами.
    
    Args:
        args: Аргументы командной строки
    """
    registry = DocumentRegistry.get_instance()
    
    # Проверяем аргументы
    if not args.source:
        print("Необходимо указать путь к исходному документу")
        return
    
    # Получаем абсолютные пути
    source_path = os.path.abspath(args.source)
    
    # Для команды 'show' не нужен целевой документ
    if args.action == 'show':
        # Проверяем наличие в реестре
        if source_path not in registry.documents:
            print(f"Документ не найден в реестре: {source_path}")
            return
        
        # Получаем связанные документы
        metadata = registry.documents[source_path]
        related = metadata.related_documents
        
        if not related:
            print(f"Документ не имеет связей: {source_path}")
            return
        
        print(f"Связи документа {metadata.title} ({source_path}):")
        for rel_path in related:
            # Проверяем наличие связанного документа в реестре
            if rel_path in registry.documents:
                rel_metadata = registry.documents[rel_path]
                print(f"- {rel_metadata.title} ({rel_path})")
            else:
                print(f"- {rel_path} (не найден в реестре)")
        
        return
    
    # Для остальных команд нужен целевой документ
    if not args.target:
        print("Необходимо указать путь к целевому документу")
        return
    
    target_path = os.path.abspath(args.target)
    
    # Проверяем наличие в реестре
    if source_path not in registry.documents:
        print(f"Исходный документ не найден в реестре: {source_path}")
        return
    
    if target_path not in registry.documents:
        print(f"Целевой документ не найден в реестре: {target_path}")
        return
    
    # Выполняем нужное действие
    if args.action == 'add':
        try:
            success = registry.add_relation(source_path, target_path, args.bidirectional)
            if success:
                print(f"Связь успешно добавлена: {source_path} -> {target_path}")
                if args.bidirectional:
                    print(f"Обратная связь также добавлена: {target_path} -> {source_path}")
            else:
                print(f"Не удалось добавить связь: {source_path} -> {target_path}")
        except Exception as e:
            print(f"Ошибка при добавлении связи: {str(e)}")
    
    elif args.action == 'remove':
        try:
            success = registry.remove_relation(source_path, target_path, args.bidirectional)
            if success:
                print(f"Связь успешно удалена: {source_path} -> {target_path}")
                if args.bidirectional:
                    print(f"Обратная связь также удалена: {target_path} -> {source_path}")
            else:
                print(f"Не удалось удалить связь: {source_path} -> {target_path}")
        except Exception as e:
            print(f"Ошибка при удалении связи: {str(e)}")


def handle_verify(args):
    """
    Обрабатывает команду 'verify' для проверки целостности реестра.
    
    Args:
        args: Аргументы командной строки
    """
    registry = DocumentRegistry.get_instance()
    
    print("Проверка целостности реестра документов...")
    
    # Проверяем целостность реестра
    issues = registry.verify_registry_integrity()
    
    stats = {
        "missing_files": len(issues["missing_files"]),
        "invalid_relationships": len(issues["invalid_relationships"]),
        "broken_id_mappings": len(issues["broken_id_mappings"])
    }
    
    # Выводим информацию о проблемах
    if sum(stats.values()) == 0:
        print("Реестр в порядке, проблем не обнаружено.")
        return
    
    if stats["missing_files"] > 0:
        print(f"\nОтсутствующие файлы ({stats['missing_files']}):")
        for path in issues["missing_files"]:
            print(f"  - {path}")
    
    if stats["invalid_relationships"] > 0:
        print(f"\nНекорректные связи ({stats['invalid_relationships']}):")
        for source, target in issues["invalid_relationships"]:
            print(f"  - {source} -> {target}")
    
    if stats["broken_id_mappings"] > 0:
        print(f"\nПоврежденные идентификаторы ({stats['broken_id_mappings']}):")
        for logical_id, path in issues["broken_id_mappings"]:
            print(f"  - {logical_id} -> {path}")
    
    # Исправляем проблемы, если требуется
    if args.fix:
        print("\nИсправление проблем с целостностью реестра...")
        fixed = registry.clean_registry()
        
        print("Исправлено проблем:")
        print(f"  - Отсутствующие файлы: {fixed['missing_files']}")
        print(f"  - Некорректные связи: {fixed['invalid_relationships']}")
        print(f"  - Поврежденные идентификаторы: {fixed['broken_id_mappings']}")


def handle_stats(args):
    """
    Обрабатывает команду 'stats' для отображения статистики реестра.
    
    Args:
        args: Аргументы командной строки
    """
    registry = DocumentRegistry.get_instance()
    
    stats = registry.get_statistics()
    
    print("Статистика реестра документов:")
    print(f"Всего документов: {stats['total_documents']}")
    
    print("\nПо типам:")
    for doc_type, count in stats.get("by_type", {}).items():
        print(f"  - {doc_type}: {count}")
    
    print("\nПо статусам:")
    for status, count in stats.get("by_status", {}).items():
        print(f"  - {status}: {count}")
    
    print(f"\nКоличество связей: {stats.get('relationships', 0)}")
    print(f"Логических идентификаторов: {stats.get('logical_ids', 0)}")
    print(f"Средняя версия: {stats.get('average_version', 1):.2f}")
    print(f"Документов с историей: {stats.get('documents_with_history', 0)}")
    
    # Дополнительная статистика
    if args.verbose:
        # Статистика по тегам
        tags = {}
        for metadata in registry.documents.values():
            for tag in metadata.tags:
                if tag in tags:
                    tags[tag] += 1
                else:
                    tags[tag] = 1
        
        if tags:
            print("\nПопулярные теги:")
            for tag, count in sorted(tags.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  - {tag}: {count}")
        
        # Статистика по времени изменения
        today = 0
        week = 0
        month = 0
        
        now = datetime.now()
        for metadata in registry.documents.values():
            try:
                updated = datetime.fromisoformat(metadata.updated_at)
                
                # Сегодня
                if (now - updated).days < 1:
                    today += 1
                
                # Неделя
                if (now - updated).days < 7:
                    week += 1
                
                # Месяц
                if (now - updated).days < 30:
                    month += 1
            except Exception:
                pass
        
        print("\nАктивность:")
        print(f"  - Обновлено сегодня: {today}")
        print(f"  - Обновлено за неделю: {week}")
        print(f"  - Обновлено за месяц: {month}")


def handle_export(args):
    """
    Обрабатывает команду 'export' для экспорта реестра в JSON-файл.
    
    Args:
        args: Аргументы командной строки
    """
    registry = DocumentRegistry.get_instance()
    
    if not args.output:
        print("Необходимо указать путь для экспорта")
        return
    
    # Экспортируем реестр
    try:
        success = registry.export_to_json(args.output)
        if success:
            print(f"Реестр успешно экспортирован в {args.output}")
        else:
            print(f"Не удалось экспортировать реестр в {args.output}")
    except Exception as e:
        print(f"Ошибка при экспорте реестра: {str(e)}")


def handle_import(args):
    """
    Обрабатывает команду 'import' для импорта реестра из JSON-файла.
    
    Args:
        args: Аргументы командной строки
    """
    registry = DocumentRegistry.get_instance()
    
    if not args.input:
        print("Необходимо указать путь для импорта")
        return
    
    # Проверяем существование файла
    if not os.path.exists(args.input):
        print(f"Файл не найден: {args.input}")
        return
    
    # Импортируем реестр
    try:
        success = registry.import_from_json(args.input, args.merge)
        if success:
            print(f"Реестр успешно импортирован из {args.input}")
            if args.merge:
                print("Данные объединены с текущим реестром")
            else:
                print("Данные заменили текущий реестр")
        else:
            print(f"Не удалось импортировать реестр из {args.input}")
    except Exception as e:
        print(f"Ошибка при импорте реестра: {str(e)}")


def main():
    """Основная функция скрипта."""
    parser = argparse.ArgumentParser(description='Инструмент для управления реестром документов')
    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')
    
    # Команда 'list'
    list_parser = subparsers.add_parser('list', help='Показать список документов')
    list_parser.add_argument('--type', help='Фильтр по типу документа')
    list_parser.add_argument('--status', help='Фильтр по статусу документа')
    list_parser.add_argument('--tag', help='Фильтр по тегу')
    list_parser.add_argument('--query', help='Поисковый запрос')
    list_parser.add_argument('--sort', default='path', choices=['path', 'title', 'updated', 'type', 'status'],
                            help='Сортировка результатов')
    list_parser.add_argument('-v', '--verbose', action='store_true', help='Подробный вывод')
    list_parser.set_defaults(func=handle_list)
    
    # Команда 'search'
    search_parser = subparsers.add_parser('search', help='Поиск документов по содержимому')
    search_parser.add_argument('query', help='Поисковый запрос')
    search_parser.add_argument('--type', help='Фильтр по типу документа')
    search_parser.add_argument('--status', help='Фильтр по статусу документа')
    search_parser.add_argument('--sort', default='path', choices=['path', 'title', 'updated', 'type'],
                              help='Сортировка результатов')
    search_parser.add_argument('-v', '--verbose', action='store_true', help='Подробный вывод')
    search_parser.set_defaults(func=handle_search)
    
    # Команда 'register'
    register_parser = subparsers.add_parser('register', help='Регистрация документа в реестре')
    register_parser.add_argument('path', help='Путь к документу')
    register_parser.add_argument('--type', help='Тип документа')
    register_parser.add_argument('--title', help='Заголовок документа')
    register_parser.add_argument('--tags', help='Теги документа (через запятую)')
    register_parser.add_argument('--related', help='Связанные документы (через запятую)')
    register_parser.add_argument('--logical-id', help='Логический идентификатор документа')
    register_parser.set_defaults(func=handle_register)
    
    # Команда 'check-duplicates'
    check_parser = subparsers.add_parser('check-duplicates', help='Проверка документа на дубликаты')
    check_parser.add_argument('path', help='Путь к документу')
    check_parser.add_argument('--type', help='Тип документа для сравнения')
    check_parser.add_argument('--threshold', type=float, default=0.85,
                             help='Порог схожести для обнаружения дубликатов (0.0-1.0)')
    check_parser.add_argument('-v', '--verbose', action='store_true', help='Подробный вывод')
    check_parser.set_defaults(func=handle_check_duplicates)
    
    # Команда 'update'
    update_parser = subparsers.add_parser('update', help='Обновление метаданных документа')
    update_parser.add_argument('path', help='Путь к документу')
    update_parser.add_argument('--title', help='Новый заголовок документа')
    update_parser.add_argument('--tags', help='Новые теги документа (через запятую)')
    update_parser.add_argument('--related', help='Новые связанные документы (через запятую)')
    update_parser.add_argument('--status', help='Новый статус документа')
    update_parser.add_argument('--logical-id', help='Новый логический идентификатор документа')
    update_parser.set_defaults(func=handle_update)
    
    # Команда 'archive'
    archive_parser = subparsers.add_parser('archive', help='Архивация документа')
    archive_parser.add_argument('path', help='Путь к документу')
    archive_parser.add_argument('--reason', default='archived', help='Причина архивации')
    archive_parser.set_defaults(func=handle_archive)
    
    # Команда 'relation'
    relation_parser = subparsers.add_parser('relation', help='Управление связями между документами')
    relation_parser.add_argument('action', choices=['add', 'remove', 'show'], help='Действие')
    relation_parser.add_argument('--source', required=True, help='Путь к исходному документу')
    relation_parser.add_argument('--target', help='Путь к целевому документу')
    relation_parser.add_argument('--bidirectional', action='store_true',
                                help='Двунаправленная связь')
    relation_parser.set_defaults(func=handle_relation)
    
    # Команда 'verify'
    verify_parser = subparsers.add_parser('verify', help='Проверка целостности реестра')
    verify_parser.add_argument('--fix', action='store_true', help='Исправлять найденные проблемы')
    verify_parser.set_defaults(func=handle_verify)
    
    # Команда 'stats'
    stats_parser = subparsers.add_parser('stats', help='Статистика реестра')
    stats_parser.add_argument('-v', '--verbose', action='store_true', help='Подробный вывод')
    stats_parser.set_defaults(func=handle_stats)
    
    # Команда 'export'
    export_parser = subparsers.add_parser('export', help='Экспорт реестра в JSON-файл')
    export_parser.add_argument('--output', required=True, help='Путь для экспорта')
    export_parser.set_defaults(func=handle_export)
    
    # Команда 'import'
    import_parser = subparsers.add_parser('import', help='Импорт реестра из JSON-файла')
    import_parser.add_argument('--input', required=True, help='Путь для импорта')
    import_parser.add_argument('--merge', action='store_true',
                              help='Объединить с текущим реестром')
    import_parser.set_defaults(func=handle_import)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    # Выполняем соответствующую команду
    args.func(args)


if __name__ == "__main__":
    main()