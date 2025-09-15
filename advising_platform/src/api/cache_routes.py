#!/usr/bin/env python3
"""
API маршруты для работы с кэшем документов.
"""

import os
from flask import Blueprint, request, jsonify
from advising_platform.src.cache.document_cache import DocumentCacheManager

# Создаем Blueprint для маршрутов кэша
cache_routes = Blueprint('cache_routes', __name__)

# Получаем экземпляр менеджера кэша
cache_manager = DocumentCacheManager.get_instance()

@cache_routes.route('/stats', methods=['GET'])
def get_cache_stats():
    """Возвращает статистику использования кэша."""
    try:
        stats = cache_manager.get_statistics()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
@cache_routes.route('/stats/key_categories', methods=['GET'])
def get_key_categories_stats():
    """Возвращает детальную статистику по ключевым категориям документов."""
    try:
        stats = cache_manager.get_statistics()
        # Извлекаем только данные о ключевых категориях для более компактного ответа
        if 'key_categories_stats' in stats:
            return jsonify({
                'key_categories_stats': stats['key_categories_stats'],
                'total_documents': stats['cache_size'],
                'hit_rate': stats['hit_rate']
            }), 200
        else:
            return jsonify({'error': 'Статистика по ключевым категориям недоступна'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cache_routes.route('/get', methods=['GET'])
def get_cached_document():
    """Получает документ из кэша."""
    path = request.args.get('path')
    if not path:
        return jsonify({'error': 'Параметр path обязателен'}), 400
        
    try:
        content = cache_manager.get_document(path)
        return jsonify({'path': path, 'content': content}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cache_routes.route('/invalidate', methods=['POST'])
def invalidate_cached_document():
    """Инвалидирует кэш для указанного документа."""
    data = request.get_json()
    if not data or 'path' not in data:
        return jsonify({'error': 'Параметр path обязателен'}), 400
        
    path = data['path']
    try:
        result = cache_manager.invalidate(path)
        return jsonify({'success': result, 'path': path}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cache_routes.route('/preload', methods=['POST'])
def preload_directory():
    """Предзагружает документы из указанной директории в кэш."""
    data = request.get_json()
    if not data or 'directory' not in data:
        return jsonify({'error': 'Параметр directory обязателен'}), 400
        
    directory = data['directory']
    recursive = data.get('recursive', True)
    
    if not os.path.isdir(directory):
        return jsonify({'error': f'Директория не существует: {directory}'}), 400
        
    try:
        count = cache_manager.document_cache.preload_documents(directory, recursive=recursive)
        return jsonify({'success': True, 'directory': directory, 'count': count}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cache_routes.route('/clear', methods=['POST'])
def clear_cache():
    """Очищает кэш документов."""
    try:
        count = cache_manager.document_cache.clear()
        return jsonify({'success': True, 'count': count}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def register_routes(app):
    """
    Регистрирует маршруты API в приложении Flask.
    
    Args:
        app: Приложение Flask.
    """
    # Инициализируем кэш при регистрации маршрутов
    if not cache_manager.is_initialized:
        cache_manager.initialize([
            '[standards .md]',
            '[todo · incidents]'
        ])
        
    app.register_blueprint(cache_routes, url_prefix='/api/cache')