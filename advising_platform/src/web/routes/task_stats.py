"""
Маршрут для отображения статистики по задачам.

Этот модуль предоставляет маршруты для отображения статистики по задачам,
включая общие метрики, прогресс по категориям и недавно выполненные задачи.

Автор: AI Assistant
Дата: 20 мая 2025
"""

import os
import logging
from flask import Blueprint, render_template, jsonify, request
from datetime import datetime

# Настраиваем логирование
logger = logging.getLogger("task_stats_routes")
logger.setLevel(logging.INFO)

# Импортируем менеджер статистики задач
try:
    from advising_platform.src.tools.task.task_statistics import TaskStatisticsManager
    task_stats_manager = TaskStatisticsManager()
    has_task_stats = True
except ImportError:
    logger.warning("Не удалось импортировать TaskStatisticsManager, будет использован режим с заглушками")
    has_task_stats = False

# Создаем Blueprint для маршрутов статистики задач
task_stats_bp = Blueprint('task_stats', __name__)

@task_stats_bp.route('/tasks/stats')
def show_task_stats():
    """
    Отображает страницу со статистикой задач.
    
    Returns:
        Отрендеренный HTML-шаблон с данными о статистике задач
    """
    logger.info("Запрос страницы статистики задач")
    
    # Получаем статистику задач
    if has_task_stats:
        stats = task_stats_manager.get_statistics_summary()
        
        # Форматируем данные для отображения
        formatted_stats = {
            'total': stats['total_tasks'],
            'completed': stats['completed_tasks'],
            'in_progress': stats['pending_tasks'],
            'completion_rate': round(stats['completion_rate'], 1),
            'categories': {},
            'recently_completed': stats['recently_completed']
        }
        
        # Форматируем данные категорий
        for category, data in stats['categories'].items():
            formatted_stats['categories'][category] = {
                'total': data['total'],
                'completed': data['completed'],
                'pending': data['pending']
            }
        
        # Получаем исторические данные для графика
        history_data = _prepare_history_data(stats['history'] if 'history' in stats else [])
        
        # Получаем список задач
        tasks = _get_tasks_list()
        
        return render_template(
            'task_stats.html',
            stats=formatted_stats,
            history=history_data,
            tasks=tasks,
            date=datetime.now().strftime("%d.%m.%Y")
        )
    else:
        # Заглушка для статистики в случае отсутствия TaskStatisticsManager
        dummy_stats = {
            'total': 15,
            'completed': 8,
            'in_progress': 7,
            'completion_rate': 53.3,
            'categories': {
                'Общая': {'total': 5, 'completed': 3, 'pending': 2},
                'Ошибка': {'total': 3, 'completed': 1, 'pending': 2},
                'Функциональность': {'total': 4, 'completed': 2, 'pending': 2},
                'Интерфейс': {'total': 2, 'completed': 1, 'pending': 1},
                'Оптимизация': {'total': 1, 'completed': 1, 'pending': 0}
            },
            'recently_completed': [
                {'task': 'Оптимизация верификатора кеша', 'completed_at': datetime.now().isoformat()},
                {'task': 'Создание интерфейса командной строки', 'completed_at': datetime.now().isoformat()},
                {'task': 'Разработка визуализатора связей', 'completed_at': datetime.now().isoformat()},
                {'task': 'Обеспечение обратной совместимости', 'completed_at': datetime.now().isoformat()},
                {'task': 'Доработка механизма синхронизации кеша', 'completed_at': datetime.now().isoformat()}
            ]
        }
        
        # Заглушка для истории в случае отсутствия TaskStatisticsManager
        dummy_history = {
            'labels': ['15.05', '16.05', '17.05', '18.05', '19.05', '20.05'],
            'completion_rate': [30, 35, 40, 45, 50, 53.3],
            'completed': [3, 4, 5, 6, 7, 8],
            'total': [10, 12, 12, 13, 14, 15]
        }
        
        # Заглушка для списка задач
        dummy_tasks = _get_dummy_tasks()
        
        return render_template(
            'task_stats.html',
            stats=dummy_stats,
            history=dummy_history,
            tasks=dummy_tasks,
            date=datetime.now().strftime("%d.%m.%Y")
        )

@task_stats_bp.route('/api/tasks/stats')
def get_task_stats_api():
    """
    API для получения статистики задач в формате JSON.
    
    Returns:
        JSON с данными о статистике задач
    """
    logger.info("API-запрос статистики задач")
    
    if has_task_stats:
        stats = task_stats_manager.get_statistics_summary()
        return jsonify(stats)
    else:
        # Заглушка для API в случае отсутствия TaskStatisticsManager
        dummy_stats = {
            'total_tasks': 15,
            'completed_tasks': 8,
            'pending_tasks': 7,
            'completion_rate': 53.3,
            'categories': {
                'Общая': {'total': 5, 'completed': 3, 'pending': 2},
                'Ошибка': {'total': 3, 'completed': 1, 'pending': 2},
                'Функциональность': {'total': 4, 'completed': 2, 'pending': 2},
                'Интерфейс': {'total': 2, 'completed': 1, 'pending': 1},
                'Оптимизация': {'total': 1, 'completed': 1, 'pending': 0}
            }
        }
        return jsonify(dummy_stats)

@task_stats_bp.route('/api/tasks/update-status', methods=['POST'])
def update_task_status():
    """
    API для обновления статуса задачи.
    
    Returns:
        JSON с результатом операции
    """
    logger.info("API-запрос на обновление статуса задачи")
    data = request.json
    
    if not data or 'task_description' not in data:
        return jsonify({
            'success': False,
            'error': 'Требуется указать описание задачи'
        }), 400
    
    task_description = data['task_description']
    completed = data.get('completed', True)
    
    if has_task_stats:
        success = task_stats_manager.update_task_status_in_todo(task_description, completed)
        if success:
            # Обновляем статистику
            task_stats_manager.update_statistics()
            return jsonify({
                'success': True,
                'message': f'Статус задачи "{task_description}" успешно обновлен'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Не удалось обновить статус задачи "{task_description}"'
            }), 500
    else:
        # Заглушка в случае отсутствия TaskStatisticsManager
        return jsonify({
            'success': True,
            'message': f'Статус задачи "{task_description}" успешно обновлен (режим заглушки)'
        })

def _prepare_history_data(history):
    """
    Подготавливает исторические данные для отображения на графиках.
    
    Args:
        history: Список записей истории
        
    Returns:
        Словарь с отформатированными данными для графиков
    """
    if not history:
        return {
            'labels': [],
            'completion_rate': [],
            'completed': [],
            'total': []
        }
    
    # Сортируем записи по дате
    history.sort(key=lambda x: x['timestamp'])
    
    # Форматируем данные для графиков
    labels = []
    completion_rate = []
    completed = []
    total = []
    
    for entry in history:
        date = datetime.fromisoformat(entry['timestamp']).strftime("%d.%m")
        labels.append(date)
        completion_rate.append(entry['completion_rate'])
        completed.append(entry['completed_tasks'])
        total.append(entry['total_tasks'])
    
    return {
        'labels': labels,
        'completion_rate': completion_rate,
        'completed': completed,
        'total': total
    }

def _get_tasks_list():
    """
    Получает список задач из todo.md.
    
    Returns:
        Список словарей с информацией о задачах
    """
    if not has_task_stats:
        return _get_dummy_tasks()
    
    tasks = []
    try:
        todo_file = task_stats_manager.todo_file
        
        with open(todo_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Парсим задачи
        task_id = 1
        for line in content.split('\n'):
            if line.strip().startswith('- ['):
                completed = '[x]' in line
                description = line.split(']', 2)[-1].strip()
                
                if description:
                    tasks.append({
                        'id': task_id,
                        'title': description,
                        'description': '',
                        'completed': completed
                    })
                    task_id += 1
        
        return tasks
    except Exception as e:
        logger.error(f"Ошибка при получении списка задач: {e}")
        return _get_dummy_tasks()

def _get_dummy_tasks():
    """
    Генерирует заглушку для списка задач.
    
    Returns:
        Список словарей с информацией о задачах
    """
    return [
        {
            'id': 1,
            'title': 'Оптимизация верификатора кеша для ускорения работы системы',
            'description': 'Повышение производительности верификатора кеша для быстрой обработки больших объемов данных.',
            'completed': True
        },
        {
            'id': 2,
            'title': 'Создание интерфейса командной строки для управления задачами',
            'description': 'Разработка CLI для упрощения работы с задачами и инцидентами через командную строку.',
            'completed': True
        },
        {
            'id': 3,
            'title': 'Разработка визуализатора связей между элементами',
            'description': 'Создание инструмента для визуального отображения взаимосвязей между задачами, инцидентами и другими элементами системы.',
            'completed': True
        },
        {
            'id': 4,
            'title': 'Обеспечение обратной совместимости для плавного перехода',
            'description': 'Реализация механизмов поддержки старых форматов и API для обеспечения плавного перехода на новую версию системы.',
            'completed': True
        },
        {
            'id': 5,
            'title': 'Доработка механизма синхронизации кеша и системы триггеров',
            'description': 'Улучшение механизма синхронизации кеша и системы триггеров для повышения надежности и производительности.',
            'completed': True
        },
        {
            'id': 6,
            'title': 'Проверка кеша, файлов на диске и рефакторинг кодовой базы',
            'description': 'Анализ состояния кеша и файлов на диске, рефакторинг кодовой базы для улучшения качества и поддерживаемости.',
            'completed': False
        },
        {
            'id': 7,
            'title': 'Интеграция с внешними системами трекинга задач',
            'description': 'Создание интеграций с Jira, GitHub Issues и другими системами трекинга задач для обеспечения синхронизации данных.',
            'completed': False
        }
    ]

def register_routes(app):
    """
    Регистрирует все маршруты в приложении Flask.
    
    Args:
        app: Приложение Flask
    """
    app.register_blueprint(task_stats_bp)
    logger.info("Маршруты статистики задач зарегистрированы")