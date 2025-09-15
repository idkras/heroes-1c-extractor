#!/usr/bin/env python3
"""
Маршруты API для работы с индексатором документов.

API предоставляет доступ к функциям индексации документов,
поиска и статистики по индексированным документам.
"""

import os
import re
import time
import json
import logging
from typing import Dict, List, Any, Optional
from flask import Blueprint, jsonify, request

# Настройка логирования
logger = logging.getLogger("indexer_api")

# Попытка импорта модуля индексатора
try:
    from advising_platform.src.core.simple_indexer import SimpleIndexer, indexer
    logger.info("Модуль индексатора успешно импортирован")
except ImportError as e:
    logger.error(f"Ошибка при импорте модуля индексатора: {e}")
    indexer = None

def register_routes(app):
    """
    Регистрирует маршруты API для работы с индексатором.
    
    Args:
        app: Экземпляр Flask приложения
    """
    if indexer is None:
        logger.warning("Индексатор не доступен, маршруты не будут зарегистрированы")
        return
    
    # Создаем Blueprint
    indexer_api = Blueprint('indexer', __name__)
    
    @indexer_api.route('/api/indexer/status', methods=['GET'])
    def get_indexer_status():
        """
        Возвращает текущий статус индексатора.
        
        Returns:
            JSON с информацией о статусе индексатора
        """
        if indexer is None:
            return jsonify({
                "status": "error",
                "message": "Индексатор не инициализирован"
            }), 500
        
        # Получаем статистику индексатора
        stats = indexer.get_statistics()
        
        return jsonify({
            "status": "ok",
            "initialized": indexer.is_initialized(),
            "statistics": stats
        })
    
    @indexer_api.route('/api/indexer/reindex', methods=['POST'])
    def reindex_documents():
        """
        Переиндексирует все документы.
        
        Returns:
            JSON с результатом операции
        """
        if indexer is None:
            return jsonify({
                "status": "error",
                "message": "Индексатор не инициализирован"
            }), 500
        
        try:
            # По умолчанию используем стандартные директории
            directories = ['[standards .md]', '[todo · incidents]']
            
            # Пробуем получить параметры из запроса, если они есть
            if request.is_json:
                data = request.get_json()
                if data and 'directories' in data:
                    directories = data['directories']
            
            # Запускаем индексацию
            start_time = time.time()
            total_docs = indexer.reindex_all(directories)
            elapsed_time = time.time() - start_time
            
            return jsonify({
                "status": "ok",
                "indexed_documents": total_docs,
                "elapsed_time": elapsed_time,
                "directories": directories
            })
        except Exception as e:
            logger.error(f"Ошибка при переиндексации: {e}")
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500
    
    @indexer_api.route('/api/indexer/documents', methods=['GET'])
    def get_indexed_documents():
        """
        Возвращает список индексированных документов с возможностью фильтрации.
        
        Returns:
            JSON со списком документов
        """
        if indexer is None:
            return jsonify({
                "status": "error",
                "message": "Индексатор не инициализирован"
            }), 500
        
        try:
            # Получаем параметры фильтрации
            doc_type = request.args.get('type')
            limit = int(request.args.get('limit', 100))
            offset = int(request.args.get('offset', 0))
            
            # Получаем документы с фильтрацией
            documents = indexer.get_documents(doc_type=doc_type, limit=limit, offset=offset)
            
            # Преобразуем метаданные в словари для JSON
            result = [doc.__dict__ for doc in documents]
            
            return jsonify({
                "status": "ok",
                "total": len(result),
                "offset": offset,
                "limit": limit,
                "documents": result
            })
        except Exception as e:
            logger.error(f"Ошибка при получении списка документов: {e}")
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500
    
    @indexer_api.route('/api/indexer/search', methods=['GET'])
    def search_documents():
        """
        Выполняет поиск по индексированным документам.
        
        Returns:
            JSON с результатами поиска
        """
        if indexer is None:
            return jsonify({
                "status": "error",
                "message": "Индексатор не инициализирован"
            }), 500
        
        try:
            # Получаем параметры поиска
            query = request.args.get('q', '')
            doc_type = request.args.get('type')
            limit = int(request.args.get('limit', 20))
            
            if not query:
                return jsonify({
                    "status": "error",
                    "message": "Отсутствует поисковый запрос"
                }), 400
            
            # Выполняем поиск
            start_time = time.time()
            results = indexer.search(query, doc_type=doc_type, limit=limit)
            elapsed_time = time.time() - start_time
            
            return jsonify({
                "status": "ok",
                "query": query,
                "type": doc_type,
                "elapsed_time": elapsed_time,
                "total_results": len(results),
                "results": results
            })
        except Exception as e:
            logger.error(f"Ошибка при выполнении поиска: {e}")
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500
    
    @indexer_api.route('/api/indexer/audit', methods=['GET'])
    def audit_indexing():
        """
        Выполняет аудит индексации и возвращает отчет.
        
        Returns:
            JSON с отчетом аудита
        """
        if indexer is None:
            return jsonify({
                "status": "error",
                "message": "Индексатор не инициализирован"
            }), 500
        
        try:
            # Импортируем модуль аудита
            from advising_platform.src.tools.analysis.audit_indexing import generate_audit_report
            
            # Генерируем отчет
            start_time = time.time()
            audit_report = generate_audit_report()
            elapsed_time = time.time() - start_time
            
            return jsonify({
                "status": "ok",
                "elapsed_time": elapsed_time,
                "audit_report": audit_report
            })
        except ImportError as e:
            logger.error(f"Ошибка при импорте модуля аудита: {e}")
            return jsonify({
                "status": "error",
                "message": f"Модуль аудита индексации не доступен: {e}"
            }), 500
        except Exception as e:
            logger.error(f"Ошибка при выполнении аудита: {e}")
            return jsonify({
                "status": "error",
                "message": f"Ошибка при выполнении аудита: {str(e)}"
            }), 500
    
    # Вспомогательная функция для подсчета файлов
    def _count_files_in_directory(directory: str, extension: str) -> int:
        """
        Подсчитывает количество файлов с указанным расширением в директории.
        
        Args:
            directory: Путь к директории
            extension: Расширение файлов
        
        Returns:
            Количество файлов
        """
        count = 0
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(extension):
                    count += 1
        return count
    
    # Регистрируем Blueprint
    app.register_blueprint(indexer_api)
    logger.info("Маршруты индексатора успешно зарегистрированы")