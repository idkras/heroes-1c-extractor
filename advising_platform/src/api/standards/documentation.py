"""
API для работы с документацией.

Предоставляет маршруты для:
1. Получения документации по стандартам
2. Обработки абстрактных ссылок
3. Поиска и индексации документов
"""

import re
import logging
from typing import Dict, List, Any, Optional
from flask import Blueprint, jsonify, request, Response

from advising_platform.standards.document.abstract_links import (
    create_abstract_link,
    resolve_abstract_link,
    extract_abstract_links,
    replace_abstract_links
)

# Настройка логирования
logger = logging.getLogger(__name__)

# Создаем Blueprint для API документации
documentation_api = Blueprint('documentation_api', __name__)


@documentation_api.route('/abstract-links/types', methods=['GET'])
def get_abstract_link_types() -> Response:
    """
    Возвращает список поддерживаемых типов абстрактных ссылок.
    
    Returns:
        JSON-ответ со списком типов абстрактных ссылок
    """
    try:
        from advising_platform.standards.document.abstract_links import abstract_link_registry
        
        # Получаем список типов ссылок
        link_types = abstract_link_registry.get_known_types()
        
        return jsonify({
            "status": "success",
            "data": {
                "link_types": link_types
            }
        })
    
    except Exception as e:
        logger.error(f"Ошибка при получении типов абстрактных ссылок: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        })


@documentation_api.route('/abstract-links/create', methods=['POST'])
def create_abstract_link_endpoint() -> Response:
    """
    Создает абстрактную ссылку.
    
    Request Body:
        {
            "link_type": "standard",
            "link_id": "ai_incident",
            "subpath": null
        }
    
    Returns:
        JSON-ответ с созданной абстрактной ссылкой
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "Не предоставлены данные для создания ссылки"
            })
        
        link_type = data.get("link_type")
        link_id = data.get("link_id")
        subpath = data.get("subpath")
        
        if not all([link_type, link_id]):
            return jsonify({
                "status": "error",
                "message": "Необходимо указать link_type и link_id"
            })
        
        # Создаем абстрактную ссылку
        link = create_abstract_link(link_type, link_id, subpath)
        
        return jsonify({
            "status": "success",
            "data": {
                "link": link
            }
        })
    
    except Exception as e:
        logger.error(f"Ошибка при создании абстрактной ссылки: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        })


@documentation_api.route('/abstract-links/resolve', methods=['POST'])
def resolve_abstract_link_endpoint() -> Response:
    """
    Разрешает абстрактную ссылку в физический путь.
    
    Request Body:
        {
            "link": "abstract://standard:ai_incident"
        }
    
    или:
    
        {
            "link_type": "standard",
            "link_id": "ai_incident",
            "subpath": null
        }
    
    Returns:
        JSON-ответ с разрешенной ссылкой
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "Не предоставлены данные для разрешения ссылки"
            })
        
        # Определяем формат входных данных
        if "link" in data:
            # Входные данные в формате полной ссылки
            link = data.get("link")
            
            # Извлекаем компоненты ссылки
            matches = extract_abstract_links(link)
            
            if not matches:
                return jsonify({
                    "status": "error",
                    "message": f"Некорректный формат абстрактной ссылки: {link}"
                })
            
            full_link, link_type, link_id, subpath = matches[0]
        else:
            # Входные данные в формате отдельных компонентов
            link_type = data.get("link_type")
            link_id = data.get("link_id")
            subpath = data.get("subpath")
            
            if not all([link_type, link_id]):
                return jsonify({
                    "status": "error",
                    "message": "Необходимо указать link_type и link_id"
                })
            
            # Формируем полную ссылку для вывода в результате
            full_link = create_abstract_link(link_type, link_id, subpath)
        
        # Разрешаем ссылку
        physical_path = resolve_abstract_link(link_type, link_id, subpath)
        
        if not physical_path:
            return jsonify({
                "status": "warning",
                "message": f"Не удалось разрешить ссылку: {full_link}",
                "data": {
                    "link": full_link,
                    "physical_path": None
                }
            })
        
        return jsonify({
            "status": "success",
            "data": {
                "link": full_link,
                "physical_path": physical_path
            }
        })
    
    except Exception as e:
        logger.error(f"Ошибка при разрешении абстрактной ссылки: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        })


@documentation_api.route('/abstract-links/extract', methods=['POST'])
def extract_abstract_links_endpoint() -> Response:
    """
    Извлекает абстрактные ссылки из текста.
    
    Request Body:
        {
            "content": "Текст с [абстрактными ссылками](abstract://standard:ai_incident)"
        }
    
    Returns:
        JSON-ответ со списком извлеченных ссылок
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "Не предоставлены данные для извлечения ссылок"
            })
        
        content = data.get("content")
        
        if not content:
            return jsonify({
                "status": "error",
                "message": "Необходимо указать content"
            })
        
        # Извлекаем ссылки
        links = extract_abstract_links(content)
        
        # Преобразуем результат в более удобный формат
        formatted_links = []
        
        for full_link, link_type, link_id, subpath in links:
            # Разрешаем ссылку
            physical_path = resolve_abstract_link(link_type, link_id, subpath)
            
            formatted_links.append({
                "link": full_link,
                "type": link_type,
                "id": link_id,
                "subpath": subpath,
                "resolved_path": physical_path
            })
        
        return jsonify({
            "status": "success",
            "data": {
                "links": formatted_links,
                "count": len(formatted_links)
            }
        })
    
    except Exception as e:
        logger.error(f"Ошибка при извлечении абстрактных ссылок: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        })


@documentation_api.route('/abstract-links/replace', methods=['POST'])
def replace_abstract_links_endpoint() -> Response:
    """
    Заменяет абстрактные ссылки в тексте на их физические пути.
    
    Request Body:
        {
            "content": "Текст с [абстрактными ссылками](abstract://standard:ai_incident)",
            "format": "markdown"
        }
    
    Returns:
        JSON-ответ с текстом, в котором ссылки заменены на физические пути
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "Не предоставлены данные для замены ссылок"
            })
        
        content = data.get("content")
        format_type = data.get("format", "plain")
        
        if not content:
            return jsonify({
                "status": "error",
                "message": "Необходимо указать content"
            })
        
        # Определяем функцию замены в зависимости от формата
        if format_type == "markdown":
            def markdown_replacement(link_type, link_id, subpath, full_link):
                physical_path = resolve_abstract_link(link_type, link_id, subpath)
                if physical_path:
                    # Текст ссылки (извлекаем из полной ссылки, если это markdown)
                    link_text = None
                    md_link_match = re.search(r'\[([^\]]+)\]\(' + re.escape(full_link) + r'\)', content)
                    if md_link_match:
                        link_text = md_link_match.group(1)
                    else:
                        link_text = link_id
                    
                    return f'[{link_text}]({physical_path} "{link_type}:{link_id}")'
                else:
                    return full_link
            
            replacement_func = markdown_replacement
        elif format_type == "html":
            def html_replacement(link_type, link_id, subpath, full_link):
                physical_path = resolve_abstract_link(link_type, link_id, subpath)
                if physical_path:
                    return f'<a href="{physical_path}" data-link-type="{link_type}" data-link-id="{link_id}">{link_id}</a>'
                else:
                    return f'<span class="unresolved-link" data-link-type="{link_type}" data-link-id="{link_id}">{link_id}</span>'
            
            replacement_func = html_replacement
        else:  # plain
            replacement_func = None  # Используем стандартную функцию замены
        
        # Заменяем ссылки
        replaced_content = replace_abstract_links(content, replacement_func)
        
        # Извлекаем ссылки для включения в ответ
        links = extract_abstract_links(content)
        formatted_links = []
        
        for full_link, link_type, link_id, subpath in links:
            physical_path = resolve_abstract_link(link_type, link_id, subpath)
            formatted_links.append({
                "link": full_link,
                "type": link_type,
                "id": link_id,
                "subpath": subpath,
                "resolved_path": physical_path
            })
        
        return jsonify({
            "status": "success",
            "data": {
                "original_content": content,
                "replaced_content": replaced_content,
                "format": format_type,
                "links": formatted_links,
                "count": len(formatted_links)
            }
        })
    
    except Exception as e:
        logger.error(f"Ошибка при замене абстрактных ссылок: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        })


def register_documentation_api(app):
    """
    Регистрирует API документации в приложении Flask.
    
    Args:
        app: Приложение Flask
    """
    app.register_blueprint(documentation_api, url_prefix='/api/v1/documentation')
    logger.info("Documentation API зарегистрировано")