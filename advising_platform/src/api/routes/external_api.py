"""
Маршруты API для управления внешними API и секретами.
"""

from flask import Blueprint, jsonify, request, current_app
import logging
from typing import Dict, Any
from ..external_api_manager import secret_manager, request_manager, initialize_apis

# Настройка логирования
logger = logging.getLogger("external_api")

# Создание Blueprint для маршрутов внешнего API
external_api_blueprint = Blueprint('external_api_manager', __name__)

# Инициализация доступных API
initialized_apis = {}

def init_external_api():
    """Инициализирует внешние API."""
    global initialized_apis
    initialized_apis = initialize_apis()
    logger.info(f"Инициализировано {len([api for api, status in initialized_apis.items() if status])} токенов API")

# Маршрут для получения статуса внешних API
@external_api_blueprint.route('/external/status', methods=['GET'])
def get_external_api_status():
    """
    Возвращает статус доступных внешних API.
    
    Returns:
        JSON с информацией о статусе внешних API
    """
    return jsonify({
        'status': 'success',
        'initialized_apis': initialized_apis,
        'apis_list': secret_manager.list_apis()
    })

# Маршрут для проверки наличия секрета для конкретного API
@external_api_blueprint.route('/external/check/<api_name>', methods=['GET'])
def check_api_secret(api_name: str):
    """
    Проверяет наличие секрета для указанного API.
    
    Args:
        api_name: Имя API
    
    Returns:
        JSON с информацией о наличии секрета
    """
    has_secret = secret_manager.has_secret(api_name)
    return jsonify({
        'status': 'success',
        'api_name': api_name,
        'has_secret': has_secret
    })

# Маршрут для установки секрета для конкретного API
@external_api_blueprint.route('/external/setup', methods=['POST'])
def setup_api_secret():
    """
    Устанавливает секрет для указанного API.
    
    Returns:
        JSON с результатом операции
    """
    data = request.json
    
    if not data or 'api_name' not in data or 'api_key' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Отсутствуют обязательные поля: api_name, api_key'
        }), 400
    
    api_name = data['api_name']
    api_key = data['api_key']
    key_name = data.get('key_name', 'api_key')
    
    success = secret_manager.set_secret(api_name, key_name, api_key)
    
    if success:
        # Обновляем статус инициализации
        global initialized_apis
        initialized_apis[api_name] = True
        
        # Настраиваем ограничение скорости запросов для API, если оно не настроено
        if api_name not in request_manager.rate_limits:
            request_manager.set_rate_limit(api_name, 60, 60)  # По умолчанию 60 запросов в минуту
        
        return jsonify({
            'status': 'success',
            'message': f'Секрет для {api_name} успешно установлен'
        })
    else:
        return jsonify({
            'status': 'error',
            'message': f'Не удалось установить секрет для {api_name}'
        }), 500

# Маршрут для удаления секрета для конкретного API
@external_api_blueprint.route('/external/remove/<api_name>', methods=['DELETE'])
def remove_api_secret(api_name: str):
    """
    Удаляет секрет для указанного API.
    
    Args:
        api_name: Имя API
    
    Returns:
        JSON с результатом операции
    """
    key_name = request.args.get('key_name', default=None)
    
    # Передаем None или строку, метод delete_secret обрабатывает оба варианта
    success = secret_manager.delete_secret(api_name, key_name)
    
    if success:
        # Обновляем статус инициализации
        global initialized_apis
        if api_name in initialized_apis:
            initialized_apis[api_name] = False
        
        return jsonify({
            'status': 'success',
            'message': f'Секрет для {api_name} успешно удален'
        })
    else:
        return jsonify({
            'status': 'error',
            'message': f'Не удалось удалить секрет для {api_name}'
        }), 404

# Маршрут для получения списка доступных API
@external_api_blueprint.route('/external/list', methods=['GET'])
def list_apis():
    """
    Возвращает список имен API, для которых есть секреты.
    
    Returns:
        JSON со списком имен API
    """
    apis = secret_manager.list_apis()
    return jsonify({
        'status': 'success',
        'apis': apis
    })

# Маршрут для получения списка секретов для конкретного API
@external_api_blueprint.route('/external/list/<api_name>', methods=['GET'])
def list_api_secrets(api_name: str):
    """
    Возвращает список имен секретов для указанного API.
    
    Args:
        api_name: Имя API
    
    Returns:
        JSON со списком имен секретов
    """
    secrets = secret_manager.list_secrets(api_name)
    return jsonify({
        'status': 'success',
        'api_name': api_name,
        'secrets': secrets
    })

# Инициализация при импорте
init_external_api()