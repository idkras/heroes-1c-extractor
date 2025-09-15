"""
API для управления задачами и инцидентами.

Предоставляет эндпоинты для:
1. Отметки задач как выполненных
2. Архивации выполненных задач
3. Получения статистики по задачам
4. Создания новых задач и инцидентов
"""

import os
import json
import logging
import time
from datetime import datetime
from flask import Blueprint, request, jsonify

# Импортируем необходимые модули для работы с задачами
try:
    from advising_platform.src.tools.task.task_statistics import TaskStatisticsManager
    from advising_platform.src.cache.task_incident_triggers import (
        register_default_triggers,
        register_custom_task_trigger,
        register_custom_incident_trigger,
        create_task,
        create_incident,
        process_hypothesis_trigger
    )
    modules_available = True
except ImportError:
    # Если модули не доступны, используем заглушки
    modules_available = False
    from advising_platform.src.core.task_completion_manager import TaskCompletionManager
    from advising_platform.src.core.task_incident_triggers import TaskIncidentTriggers

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("advising_platform.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("task_manager_api")

# Создаем экземпляры необходимых классов
if modules_available:
    task_manager = TaskStatisticsManager()
    # Для работы с триггерами используем функции напрямую из модуля
    # Создаем API клиент для работы с триггерами
    register_default_triggers()
    logger.info("Используются новые модули для работы с задачами")
else:
    # Используем старые классы в качестве заглушек
    task_manager = TaskCompletionManager()
    trigger_manager = TaskIncidentTriggers()
    logger.warning("Используются устаревшие модули для работы с задачами")

# Создаем Blueprint для API управления задачами
task_api = Blueprint('task_api', __name__)

@task_api.route('/tasks/complete', methods=['POST'])
def complete_task():
    """Эндпоинт для отметки задачи как выполненной."""
    data = request.json
    
    if not data or 'task_description' not in data:
        return jsonify({
            'success': False,
            'error': 'Необходимо указать описание задачи'
        }), 400
    
    task_description = data['task_description']
    category = data.get('category', None)
    
    result = task_manager.mark_task_completed(task_description, category)
    
    if result:
        return jsonify({
            'success': True,
            'message': f'Задача "{task_description}" успешно отмечена как выполненная'
        })
    else:
        return jsonify({
            'success': False,
            'error': f'Не удалось отметить задачу "{task_description}" как выполненную'
        }), 500

@task_api.route('/tasks/archive', methods=['POST'])
def archive_tasks():
    """Эндпоинт для архивации выполненных задач."""
    success, count = task_manager.archive_completed_tasks()
    
    if success:
        return jsonify({
            'success': True,
            'message': f'Успешно архивировано {count} задач',
            'archived_count': count
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Не удалось архивировать выполненные задачи'
        }), 500

@task_api.route('/tasks/stats', methods=['GET'])
def get_task_stats():
    """Эндпоинт для получения статистики по задачам."""
    stats = task_manager.get_statistics_summary()
    
    return jsonify({
        'success': True,
        'stats': stats
    })

@task_api.route('/tasks/create', methods=['POST'])
def create_task_endpoint():
    """Эндпоинт для создания новой задачи."""
    data = request.json
    
    if not data or 'title' not in data:
        return jsonify({
            'success': False,
            'error': 'Необходимо указать название задачи'
        }), 400
    
    task_type = data.get('task_type', 'Задача')
    title = data['title']
    description = data.get('description', '')
    priority = data.get('priority', 'Средний')
    
    try:
        # Используем импортированную функцию create_task для создания задачи
        if modules_available:
            properties = {
                'type': task_type,
                'priority': priority,
                'status': 'Новая'
            }
            
            # Создаем задачу с использованием новой системы триггеров
            task_id = create_task(title, description, properties)
            
            return jsonify({
                'success': True,
                'message': f'Создана новая задача "{title}"',
                'task_id': task_id
            })
        else:
            # Используем старую систему для обратной совместимости
            task_template = trigger_manager.generate_task_template(
                task_type=task_type,
                title=title,
                description=description,
                priority=priority
            )
            
            return jsonify({
                'success': True,
                'message': f'Создана новая задача "{title}"',
                'task_template': task_template
            })
    except Exception as e:
        logger.error(f"Ошибка при создании задачи: {e}")
        return jsonify({
            'success': False,
            'error': f'Не удалось создать задачу: {str(e)}'
        }), 500

@task_api.route('/incidents/create', methods=['POST'])
def create_incident_endpoint():
    """Эндпоинт для создания нового инцидента."""
    data = request.json
    
    if not data or 'title' not in data or 'description' not in data:
        return jsonify({
            'success': False,
            'error': 'Необходимо указать название и описание инцидента'
        }), 400
    
    incident_type = data.get('incident_type', 'Инцидент')
    title = data['title']
    description = data['description']
    severity = data.get('severity', 5)
    
    try:
        # Используем импортированную функцию create_incident для создания инцидента
        if modules_available:
            properties = {
                'type': incident_type,
                'severity': severity,
                'status': 'Новый'
            }
            
            # Создаем инцидент с использованием новой системы триггеров
            incident_id = create_incident(title, description, properties)
            
            return jsonify({
                'success': True,
                'message': f'Создан новый инцидент "{title}"',
                'incident_id': incident_id
            })
        else:
            # Используем старую систему для обратной совместимости
            incident_template = trigger_manager.generate_incident_template(
                incident_type=incident_type,
                title=title,
                description=description,
                severity=severity
            )
            
            return jsonify({
                'success': True,
                'message': f'Создан новый инцидент "{title}"',
                'incident_template': incident_template
            })
    except Exception as e:
        logger.error(f"Ошибка при создании инцидента: {e}")
        return jsonify({
            'success': False,
            'error': f'Не удалось создать инцидент: {str(e)}'
        }), 500

@task_api.route('/hypotheses/create', methods=['POST'])
def create_hypothesis_endpoint():
    """Эндпоинт для создания новой гипотезы."""
    data = request.json
    
    if not data or 'title' not in data or 'description' not in data:
        return jsonify({
            'success': False,
            'error': 'Необходимо указать название и описание гипотезы'
        }), 400
    
    title = data['title']
    description = data['description']
    category = data.get('category', 'Общая')
    status = data.get('status', 'pending')
    
    try:
        # Используем импортированную функцию process_hypothesis_trigger для создания гипотезы
        if modules_available:
            properties = {
                'category': category,
                'status': status,
                'tags': data.get('tags', [])
            }
            
            # Создаем директорию гипотез, если она не существует
            if not os.path.exists("hypotheses"):
                os.makedirs("hypotheses")
            
            # Создаем файл гипотезы
            timestamp = int(time.time())
            file_name = f"{timestamp}_{title.replace(' ', '_')}.md"
            file_path = os.path.join("hypotheses", file_name)
            
            # Форматируем описание гипотезы
            formatted_description = f"""# {title}

{description}

## Метаданные

- **Дата создания:** {datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')}
- **Категория:** {category}
- **Статус:** {status}
- **Теги:** {', '.join(properties.get('tags', []))}
"""
            
            # Записываем гипотезу в файл
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(formatted_description)
            
            # Запускаем триггер для создания гипотезы
            properties_for_trigger = {
                'category': category,
                'status': status,
                'tags': properties.get('tags', [])
            }
            success = process_hypothesis_trigger(title, description, file_path, "ai_assistant", properties_for_trigger)
            
            if success:
                logger.info(f"Гипотеза '{title}' успешно создана и обработана триггером")
                return jsonify({
                    'success': True,
                    'message': f'Создана новая гипотеза "{title}"',
                    'hypothesis_id': file_path
                })
            else:
                logger.warning(f"Гипотеза '{title}' создана, но не обработана триггером")
                return jsonify({
                    'success': True,
                    'message': f'Создана новая гипотеза "{title}", но не обработана триггером',
                    'hypothesis_id': file_path,
                    'warning': 'Триггер не был обработан'
                })
        else:
            # Используем старую систему для обратной совместимости
            hypothesis_template = {
                "title": title,
                "description": description,
                "category": category,
                "status": status,
                "tags": data.get('tags', [])
            }
            
            return jsonify({
                'success': True,
                'message': f'Создана новая гипотеза "{title}"',
                'hypothesis_template': hypothesis_template
            })
    except Exception as e:
        logger.error(f"Ошибка при создании гипотезы: {e}")
        return jsonify({
            'success': False,
            'error': f'Не удалось создать гипотезу: {str(e)}'
        }), 500

@task_api.route('/incidents/check', methods=['POST'])
def check_incident_quality():
    """Эндпоинт для проверки качества инцидента."""
    data = request.json
    
    if not data or 'file_path' not in data:
        return jsonify({
            'success': False,
            'error': 'Необходимо указать путь к файлу инцидента'
        }), 400
    
    file_path = data['file_path']
    
    result = trigger_manager.check_incident_quality(file_path)
    
    return jsonify({
        'success': True,
        'result': result
    })

@task_api.route('/tasks/verify', methods=['POST'])
def verify_task_against_standard():
    """Эндпоинт для проверки соответствия задачи стандарту."""
    data = request.json
    
    if not data or 'task_description' not in data or 'standard_name' not in data:
        return jsonify({
            'success': False,
            'error': 'Необходимо указать описание задачи и название стандарта'
        }), 400
    
    task_description = data['task_description']
    standard_name = data['standard_name']
    
    result = task_manager.verify_task_against_standard(task_description, standard_name)
    
    return jsonify({
        'success': True,
        'result': result
    })

# Функция для регистрации Blueprint в приложении
def register_task_api(app):
    """Регистрирует API управления задачами в приложении Flask."""
    app.register_blueprint(task_api, url_prefix='/api/v1')
    logger.info("API управления задачами зарегистрировано")