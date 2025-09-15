#!/usr/bin/env python3
"""
API адаптер для In-Memory индексатора.
Предоставляет API для работы с документами через in-memory индексирование.
"""

import os
import sys
import json
import time
from flask import Blueprint, jsonify, request, current_app

# Добавляем путь к корневой директории проекта
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

# Импортируем in-memory индексатор
from advising_platform.advising_platform.src.core.inmemory_indexer import InMemoryIndexer, indexer

# Создаем Blueprint
inmemory_api = Blueprint('inmemory_api', __name__)

# Инициализируем индексатор сразу
print("Инициализация In-Memory индексатора...")

# Директории для индексации
directories = [
    ".",
    "[standards .md]",
    "[todo · incidents]",
]

# Индексируем документы
total_docs = 0
for directory in directories:
    if not os.path.exists(directory):
        print(f"Директория не существует: {directory}")
        continue
    
    print(f"Индексация директории: {directory}")
    docs_count = indexer.index_directory(directory)
    total_docs += docs_count
    print(f"  - Проиндексировано {docs_count} документов")

print(f"Всего проиндексировано: {total_docs} документов")

# Выводим статистику индексатора
stats = indexer.get_statistics()
print("\nСтатистика индексатора:")
print(f"  - Всего документов: {stats['total_documents']}")
print(f"  - Типы документов: {stats['document_types']}")
print(f"  - Всего задач: {stats['total_tasks']}")
print(f"  - Всего инцидентов: {stats['total_incidents']}")
print(f"  - Логических ID: {stats['logical_ids']}")
print(f"  - Проиндексированных слов: {stats['indexed_words']}")

@inmemory_api.route('/inmemory/stats', methods=['GET'])
def get_stats():
    """Возвращает статистику индексатора."""
    stats = indexer.get_statistics()
    return jsonify(stats)

@inmemory_api.route('/inmemory/search', methods=['GET'])
def search():
    """Выполняет поиск по индексированным документам."""
    query = request.args.get('q', '')
    doc_type = request.args.get('type', '')
    limit = int(request.args.get('limit', 10))
    
    if not query:
        return jsonify({'error': 'Query parameter q is required'}), 400
    
    # Передаем None вместо пустой строки для doc_type
    doc_type_param = doc_type if doc_type else None
    results = indexer.search(query, doc_type_param, limit)
    
    formatted_results = []
    for path, relevance in results:
        doc = indexer.get_document(path)
        if doc:
            metadata, _ = doc
            formatted_results.append({
                'path': path,
                'title': metadata.title if metadata.title else '',
                'author': metadata.author if metadata.author else '',
                'date': metadata.date if metadata.date else '',
                'doc_type': metadata.doc_type if metadata.doc_type else '',
                'relevance': relevance
            })
    
    return jsonify({
        'query': query,
        'doc_type': doc_type if doc_type else 'all',
        'results': formatted_results
    })

@inmemory_api.route('/inmemory/document/<path:path>', methods=['GET'])
def get_document(path):
    """Возвращает содержимое документа."""
    doc = indexer.get_document(path)
    
    if not doc:
        return jsonify({'error': f'Document not found: {path}'}), 404
    
    metadata, content = doc
    
    return jsonify({
        'path': path,
        'metadata': {
            'title': metadata.title,
            'author': metadata.author,
            'date': metadata.date,
            'doc_type': metadata.doc_type,
            'based_on': metadata.based_on,
            'version': metadata.version,
            'content_hash': metadata.content_hash
        },
        'content': content.raw_content
    })

@inmemory_api.route('/inmemory/document/abstract/<identifier>', methods=['GET'])
def get_document_by_id(identifier):
    """Возвращает содержимое документа по логическому идентификатору."""
    doc = indexer.get_document_by_id(identifier)
    
    if not doc:
        return jsonify({'error': f'Document not found: {identifier}'}), 404
    
    metadata, content = doc
    
    return jsonify({
        'identifier': identifier,
        'path': metadata.path,
        'metadata': {
            'title': metadata.title,
            'author': metadata.author,
            'date': metadata.date,
            'doc_type': metadata.doc_type,
            'based_on': metadata.based_on,
            'version': metadata.version,
            'content_hash': metadata.content_hash
        },
        'content': content.raw_content
    })

@inmemory_api.route('/inmemory/tasks', methods=['GET'])
def get_tasks():
    """Возвращает список задач с применением фильтров."""
    filters = {}
    
    if 'completed' in request.args and request.args.get('completed'):
        completed_val = request.args.get('completed')
        filters['completed'] = completed_val.lower() == 'true' if completed_val else False
    
    if 'priority' in request.args and request.args.get('priority'):
        filters['priority'] = request.args.get('priority')
    
    if 'responsible' in request.args and request.args.get('responsible'):
        filters['responsible'] = request.args.get('responsible')
    
    if 'deadline' in request.args:
        filters['deadline'] = request.args.get('deadline')
    
    tasks = indexer.get_tasks(filters)
    
    return jsonify({
        'count': len(tasks),
        'tasks': tasks
    })

@inmemory_api.route('/inmemory/incidents', methods=['GET'])
def get_incidents():
    """Возвращает список инцидентов с применением фильтров."""
    filters = {}
    
    if 'id' in request.args:
        filters['id'] = request.args.get('id')
    
    if 'status' in request.args:
        filters['status'] = request.args.get('status')
    
    if 'date' in request.args:
        filters['date'] = request.args.get('date')
    
    incidents = indexer.get_incidents(filters)
    
    return jsonify({
        'count': len(incidents),
        'incidents': incidents
    })

@inmemory_api.route('/inmemory/reindex', methods=['POST'])
def reindex():
    """Переиндексирует документы."""
    # Получаем JSON-данные из запроса или используем пустой словарь, если их нет
    data = request.json if request.is_json else {}
    
    # Устанавливаем значения по умолчанию, если они не указаны
    default_dirs = ['.', '[standards .md]', '[todo · incidents]']
    directories = data.get('directories', default_dirs) if data else default_dirs
    force_reindex = data.get('force', False) if data else False
    
    total_docs = 0
    for directory in directories:
        if not os.path.exists(directory):
            continue
        
        docs_count = indexer.index_directory(directory)
        total_docs += docs_count
    
    stats = indexer.get_statistics()
    
    return jsonify({
        'reindexed': total_docs,
        'stats': stats
    })

def register_blueprint(app):
    """Регистрирует Blueprint в приложении Flask."""
    app.register_blueprint(inmemory_api)
    print("In-Memory API зарегистрировано")