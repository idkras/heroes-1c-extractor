#!/usr/bin/env python3
"""
API для упрощенного in-memory индексатора.
"""

import os
import re
import sys
import json
from flask import Blueprint, jsonify, request

# Добавляем путь к корневой директории проекта
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

# Импортируем упрощенный индексатор
from advising_platform.src.core.simple_indexer import indexer

# Импортируем анализатор связей документов и константы
from advising_platform.src.tools.document_relation_analyzer import DocumentRelationAnalyzer, RELATION_TYPES

# Инициализируем анализатор связей и загружаем данные из индексатора
document_analyzer = DocumentRelationAnalyzer()
document_analyzer.load_abstract_ids(from_indexer=indexer)

# Создаем Blueprint
indexer_api = Blueprint('indexer_api', __name__)

# Инициализируем индексатор при старте
print("Инициализация упрощенного индексатора...")
directories = [
    "[standards .md]", 
    "[todo · incidents]"
]

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

# Статистика индексатора
stats = indexer.get_statistics()
print("\nСтатистика индексатора:")
print(f"  - Всего документов: {stats['total_documents']}")
print(f"  - Типы документов: {stats['document_types']}")
print(f"  - Всего задач: {stats['total_tasks']}")
print(f"  - Всего инцидентов: {stats['total_incidents']}")
print(f"  - Логических ID: {stats['logical_ids']}")
print(f"  - Проиндексированных слов: {stats['indexed_words']}")

@indexer_api.route('/stats', methods=['GET'])
def get_stats():
    """Возвращает статистику индексатора."""
    stats = indexer.get_statistics()
    return jsonify(stats)

@indexer_api.route('/search', methods=['GET'])
def search():
    """Выполняет поиск по индексированным документам."""
    query = request.args.get('q', '')
    doc_type = request.args.get('type', '')
    limit = int(request.args.get('limit', 10))
    use_abstract = request.args.get('abstract', '').lower() in ('true', '1', 'yes')
    
    if not query:
        return jsonify({'error': 'Query parameter q is required'}), 400
    
    # Используем None если тип документа не указан
    doc_type_param = doc_type if doc_type else None
    results = indexer.search(query, doc_type_param, limit)
    
    formatted_results = []
    for path, relevance in results:
        doc = indexer.get_document(path)
        if doc:
            metadata, content = doc
            
            # Проверяем, есть ли логический идентификатор для этого документа
            logical_id = None
            if use_abstract:
                for identifier, p in indexer.abstractions.items():
                    if p == path:
                        logical_id = identifier
                        break
            
            result = {
                'path': path,
                'title': metadata.title if metadata.title else os.path.basename(path),
                'doc_type': metadata.doc_type if metadata.doc_type else 'unknown',
                'relevance': relevance,
                'preview': content.raw_content[:200] + '...' if len(content.raw_content) > 200 else content.raw_content
            }
            
            # Добавляем логический идентификатор, если найден
            if logical_id:
                result['logical_id'] = logical_id
            
            formatted_results.append(result)
    
    return jsonify({
        'query': query,
        'doc_type': doc_type if doc_type else 'all',
        'use_abstract': use_abstract,
        'results': formatted_results
    })

@indexer_api.route('/document/<path:path>', methods=['GET'])
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
            'doc_type': metadata.doc_type,
            'last_modified': metadata.last_modified
        },
        'content': content.raw_content
    })

@indexer_api.route('/abstract/document/<identifier>', methods=['GET'])
def get_document_by_id(identifier):
    """Возвращает документ по логическому идентификатору."""
    doc = indexer.get_document_by_id(identifier)
    
    if not doc:
        return jsonify({'error': f'Document not found by identifier: {identifier}'}), 404
    
    metadata, content = doc
    
    return jsonify({
        'identifier': identifier,
        'path': metadata.path,
        'metadata': {
            'title': metadata.title,
            'doc_type': metadata.doc_type,
            'last_modified': metadata.last_modified
        },
        'content': content.raw_content
    })

@indexer_api.route('/abstract/register', methods=['POST'])
def register_logical_id():
    """Регистрирует логический идентификатор для документа."""
    data = request.json
    
    if not data or 'path' not in data or 'identifier' not in data:
        return jsonify({'error': 'Both path and identifier are required'}), 400
    
    path = data['path']
    identifier = data['identifier']
    
    success = indexer.register_logical_id(path, identifier)
    
    if success:
        return jsonify({'success': True, 'message': f'Registered identifier {identifier} for {path}'})
    else:
        return jsonify({'error': f'Failed to register identifier {identifier} for {path}'}), 400

@indexer_api.route('/abstract/list', methods=['GET'])
def list_logical_ids():
    """Возвращает список зарегистрированных логических идентификаторов."""
    stats = indexer.get_statistics()
    abstractions = getattr(indexer, 'abstractions', {})
    
    return jsonify({
        'count': len(abstractions),
        'identifiers': [
            {'identifier': identifier, 'path': path}
            for identifier, path in abstractions.items()
        ]
    })

@indexer_api.route('/abstract/convert', methods=['POST'])
def convert_abstract_links():
    """Преобразует ссылки в документе между физическими и абстрактными форматами."""
    data = request.json
    
    if not data or 'path' not in data:
        return jsonify({'error': 'Path parameter is required'}), 400
    
    path = data['path']
    to_abstract = data.get('to_abstract', True)
    
    if not os.path.exists(path):
        return jsonify({'error': f'File not found: {path}'}), 404
    
    try:
        # Читаем содержимое файла
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Паттерн для поиска Markdown-ссылок
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = re.findall(link_pattern, content)
        
        if not links:
            return jsonify({'message': 'No links found in document', 'changed': 0})
        
        # Преобразуем ссылки
        modified_content = content
        changed_count = 0
        
        for link_text, link_url in links:
            if to_abstract:
                # Преобразование физического пути в абстрактный идентификатор
                for identifier, doc_path in indexer.abstractions.items():
                    if doc_path == link_url:
                        new_link = f"[{link_text}]({identifier})"
                        old_link = f"[{link_text}]({link_url})"
                        modified_content = modified_content.replace(old_link, new_link)
                        changed_count += 1
                        break
            else:
                # Преобразование абстрактного идентификатора в физический путь
                # Проверяем, является ли ссылка абстрактным идентификатором
                if re.match(r'^[a-z]+:[a-z0-9_.]+(?:#[a-z0-9_-]+)?$', link_url):
                    if link_url in indexer.abstractions:
                        physical_path = indexer.abstractions[link_url]
                        new_link = f"[{link_text}]({physical_path})"
                        old_link = f"[{link_text}]({link_url})"
                        modified_content = modified_content.replace(old_link, new_link)
                        changed_count += 1
        
        if changed_count > 0:
            # Сохраняем изменения в файл
            with open(path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            return jsonify({
                'message': f'Successfully converted {changed_count} links',
                'changed': changed_count
            })
        else:
            return jsonify({'message': 'No links were converted', 'changed': 0})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@indexer_api.route('/tasks', methods=['GET'])
def get_tasks():
    """Возвращает список задач."""
    tasks = indexer.get_tasks()
    return jsonify({
        'count': len(tasks),
        'tasks': tasks
    })

@indexer_api.route('/incidents', methods=['GET'])
def get_incidents():
    """Возвращает список инцидентов."""
    incidents = indexer.get_incidents()
    return jsonify({
        'count': len(incidents),
        'incidents': incidents
    })

@indexer_api.route('/reindex', methods=['POST'])
def reindex():
    """Переиндексирует документы."""
    data = request.json if request.is_json else {}
    
    default_dirs = ['.', '[standards .md]', '[todo · incidents]']
    directories = data.get('directories', default_dirs) if data else default_dirs
    
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

@indexer_api.route('/document/relations', methods=['GET'])
def get_document_relations():
    """Возвращает список всех найденных связей между документами."""
    return jsonify({
        'count': len(document_analyzer.relations),
        'relations': [relation.to_dict() for relation in document_analyzer.relations]
    })

@indexer_api.route('/document/analyze/<path:path>', methods=['POST'])
def analyze_document(path):
    """Анализирует документ на наличие связей с другими документами."""
    try:
        # Проверяем существование файла
        if not os.path.exists(path):
            return jsonify({'error': f'File not found: {path}'}), 404
        
        # Анализируем документ
        relations = document_analyzer.analyze_document(path)
        
        return jsonify({
            'path': path,
            'relations_count': len(relations),
            'relations': [relation.to_dict() for relation in relations]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@indexer_api.route('/document/analyze/all', methods=['POST'])
def analyze_all_documents():
    """Анализирует все документы в стандартных директориях."""
    try:
        dirs_to_analyze = [
            "[standards .md]",
            "[todo · incidents]",
            "[todo · incidents]/ai.incidents"
        ]
        
        total_docs = 0
        total_relations = 0
        analyzed_docs = []
        
        for directory in dirs_to_analyze:
            if os.path.exists(directory):
                for root, _, files in os.walk(directory):
                    for file in files:
                        if file.endswith('.md'):
                            file_path = os.path.join(root, file)
                            relations = document_analyzer.analyze_document(file_path)
                            total_docs += 1
                            total_relations += len(relations)
                            analyzed_docs.append({
                                'path': file_path,
                                'relations_count': len(relations)
                            })
        
        return jsonify({
            'analyzed_documents': total_docs,
            'total_relations': total_relations,
            'documents': analyzed_docs
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@indexer_api.route('/document/relations/visualize', methods=['GET'])
def visualize_relations():
    """Создает визуализацию связей в формате DOT для Graphviz."""
    try:
        # Создаем временный файл для визуализации
        import tempfile
        temp_dir = tempfile.gettempdir()
        dot_file = os.path.join(temp_dir, 'document_relations.dot')
        
        with open(dot_file, 'w', encoding='utf-8') as f:
            f.write("digraph document_relations {\n")
            f.write("  rankdir=LR;\n")
            f.write("  node [shape=box, style=filled, fillcolor=lightblue];\n")
            
            # Группируем узлы по типам документов
            document_types = {}
            for relation in document_analyzer.relations:
                source_type = relation.source_id.split(':')[0] if ':' in relation.source_id else 'unknown'
                target_type = relation.target_id.split(':')[0] if ':' in relation.target_id else 'unknown'
                
                if source_type not in document_types:
                    document_types[source_type] = set()
                if target_type not in document_types:
                    document_types[target_type] = set()
                
                document_types[source_type].add(relation.source_id)
                document_types[target_type].add(relation.target_id)
            
            # Определяем цвета для разных типов документов
            type_colors = {
                'task': 'lightblue',
                'incident': 'salmon',
                'standard': 'lightgreen',
                'unknown': 'lightgray'
            }
            
            # Создаем подграфы для каждого типа документов
            for doc_type, docs in document_types.items():
                color = type_colors.get(doc_type, 'lightgray')
                f.write(f'  subgraph cluster_{doc_type} {{\n')
                f.write(f'    label="{doc_type}";\n')
                f.write(f'    node [fillcolor={color}];\n')
                for doc_id in docs:
                    label = doc_id.split(':')[1] if ':' in doc_id else doc_id
                    f.write(f'    "{doc_id}" [label="{label}"];\n')
                f.write('  }\n')
            
            # Добавляем ребра
            for relation in document_analyzer.relations:
                relation_type = RELATION_TYPES.get(relation.relation_type, relation.relation_type)
                f.write(f'  "{relation.source_id}" -> "{relation.target_id}" [label="{relation_type}"];\n')
            
            f.write("}\n")
        
        # Отдаем файл
        with open(dot_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return content, 200, {'Content-Type': 'text/plain'}
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@indexer_api.route('/document/relations/stats', methods=['GET'])
def get_relations_stats():
    """Возвращает статистику связей между документами."""
    try:
        # Собираем данные о документах
        documents = set()
        documents_by_type = {}
        relation_types_count = {}
        
        for relation in document_analyzer.relations:
            documents.add(relation.source_id)
            documents.add(relation.target_id)
            
            # Подсчитываем количество документов по типам
            source_type = relation.source_id.split(':')[0] if ':' in relation.source_id else 'unknown'
            target_type = relation.target_id.split(':')[0] if ':' in relation.target_id else 'unknown'
            
            documents_by_type[source_type] = documents_by_type.get(source_type, 0) + 1
            documents_by_type[target_type] = documents_by_type.get(target_type, 0) + 1
            
            # Подсчитываем количество связей по типам
            relation_type = relation.relation_type
            relation_types_count[relation_type] = relation_types_count.get(relation_type, 0) + 1
        
        # Формируем статистику
        stats = {
            'total_documents': len(documents),
            'total_relations': len(document_analyzer.relations),
            'documents_by_type': documents_by_type,
            'relation_types': relation_types_count
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@indexer_api.route('/document/relations/export', methods=['GET'])
def export_relations():
    """Экспортирует связи в указанном формате."""
    format_type = request.args.get('format', 'json')
    
    if format_type not in ['json', 'csv', 'markdown']:
        return jsonify({'error': f'Unsupported format: {format_type}'}), 400
    
    try:
        # Создаем временный файл для экспорта
        import tempfile
        temp_dir = tempfile.gettempdir()
        output_file = os.path.join(temp_dir, f'document_relations.{format_type}')
        
        # Экспортируем связи
        document_analyzer.export_relations(format_type, output_file)
        
        # Отдаем файл
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if format_type == 'json':
            return jsonify(json.loads(content))
        elif format_type == 'csv':
            return content, 200, {'Content-Type': 'text/csv'}
        else:  # markdown
            return content, 200, {'Content-Type': 'text/markdown'}
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def register_blueprint(app):
    """Регистрирует Blueprint в приложении Flask."""
    app.register_blueprint(indexer_api, url_prefix='/indexer')
    print("Indexer API зарегистрировано")