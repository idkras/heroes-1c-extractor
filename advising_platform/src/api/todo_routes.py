#!/usr/bin/env python3
"""
Маршруты API для работы с Todo документами.

Предоставляет API для валидации и управления Todo документами.
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from flask import Blueprint, jsonify, request
from advising_platform.src.api.todo_validation import (
    validate_todo_document,
    validate_cache_integration,
    handle_todo_created,
    ensure_archive_directory_exists
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("todo_api")

# Создаем Blueprint
todo_api = Blueprint('todo_api', __name__)

@todo_api.route('/api/todo/validate', methods=['POST'])
def validate_todo():
    """
    Валидирует Todo документ.
    
    Ожидает JSON с полем "file_path" - путь к документу.
    
    Returns:
        JSON с результатами валидации
    """
    try:
        data = request.json
        if not data or 'file_path' not in data:
            return jsonify({
                "success": False,
                "error": "Не указан путь к документу (file_path)"
            }), 400
        
        file_path = data['file_path']
        result = validate_todo_document(file_path)
        
        return jsonify({
            "success": True,
            "result": result
        })
    except Exception as e:
        logger.error(f"Ошибка при валидации документа: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@todo_api.route('/api/todo/validate_cache', methods=['GET'])
def check_cache_integration():
    """
    Проверяет интеграцию с системой кэширования.
    
    Returns:
        JSON с результатами проверки
    """
    try:
        result = validate_cache_integration()
        
        return jsonify({
            "success": True,
            "result": result
        })
    except Exception as e:
        logger.error(f"Ошибка при проверке интеграции с кэшем: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@todo_api.route('/api/todo/create_notification', methods=['POST'])
def todo_created():
    """
    Обрабатывает уведомление о создании Todo документа.
    
    Ожидает JSON с полем "file_path" - путь к созданному документу.
    
    Returns:
        JSON с результатами обработки
    """
    try:
        data = request.json
        if not data or 'file_path' not in data:
            return jsonify({
                "success": False,
                "error": "Не указан путь к документу (file_path)"
            }), 400
        
        file_path = data['file_path']
        result = handle_todo_created(file_path)
        
        return jsonify({
            "success": True,
            "result": result
        })
    except Exception as e:
        logger.error(f"Ошибка при обработке создания документа: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@todo_api.route('/api/todo/ensure_archive', methods=['GET'])
def check_archive_directory():
    """
    Проверяет и создает директорию архива, если она не существует.
    
    Returns:
        JSON с результатом проверки
    """
    try:
        result = ensure_archive_directory_exists()
        
        return jsonify({
            "success": result,
            "message": "Директория архива проверена и создана при необходимости" if result else "Не удалось создать директорию архива"
        })
    except Exception as e:
        logger.error(f"Ошибка при проверке директории архива: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def register_routes(app):
    """
    Регистрирует маршруты для работы с Todo документами.
    
    Args:
        app: Экземпляр приложения Flask
    """
    app.register_blueprint(todo_api)