#!/usr/bin/env python3
"""
API маршруты для работы с инициализатором контекста.
"""

from flask import Blueprint, request, jsonify
from advising_platform.src.cache.context_initializer import context_initializer

# Создаем Blueprint для маршрутов контекста
context_routes = Blueprint('context_routes', __name__)

@context_routes.route('/initialize', methods=['POST'])
def initialize_context():
    """Инициализирует контекст с загрузкой ключевых документов."""
    try:
        data = request.get_json() or {}
        force = data.get('force', False)
        
        success = context_initializer.initialize(force=force)
        return jsonify({'success': success}), 200 if success else 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@context_routes.route('/status', methods=['GET'])
def get_context_status():
    """Возвращает статус инициализации контекста."""
    try:
        stats = context_initializer.check_context_health()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def register_routes(app):
    """
    Регистрирует маршруты API в приложении Flask.
    
    Args:
        app: Приложение Flask.
    """
    # Инициализируем контекст при запуске
    context_initializer.initialize()
    
    # Регистрируем маршруты
    app.register_blueprint(context_routes, url_prefix='/api/context')