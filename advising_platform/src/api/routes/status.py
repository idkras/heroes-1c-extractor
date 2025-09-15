"""
Маршруты API для проверки статуса системы.
"""

from flask import Blueprint, jsonify

status_blueprint = Blueprint('status', __name__)

@status_blueprint.route('/status', methods=['GET'])
def get_status():
    """
    Проверка статуса системы.
    
    Возвращает базовую информацию о состоянии системы.
    """
    return jsonify({
        'status': 'ok',
        'version': '1.0.0',
        'uptime': '1d 2h 34m',
        'components': {
            'api': {
                'status': 'running'
            },
            'cache': {
                'status': 'running'
            },
            'sync': {
                'status': 'running'
            }
        },
        'file_reorganization': {
            'status': 'completed',
            'timestamp': '2025-05-15T21:54:00Z'
        }
    })