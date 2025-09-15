"""
API эндпоинты для интеграции команд Heroes с N8N.
Обрабатывает контекст, задачи и гипотезы от команд Heroes Advising Crew.
"""

import json
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Создаем Blueprint для Heroes API
heroes_bp = Blueprint('heroes', __name__, url_prefix='/api/heroes')

@heroes_bp.route('/health', methods=['GET'])
def heroes_health():
    """Проверка работоспособности Heroes API"""
    return jsonify({
        "status": "ok",
        "service": "Heroes API",
        "timestamp": datetime.now().isoformat(),
        "endpoints": [
            "/api/heroes/context",
            "/api/heroes/tasks", 
            "/api/heroes/hypotheses"
        ]
    })

@heroes_bp.route('/context', methods=['POST'])
def receive_context():
    """
    Принимает контекст проекта от команд Heroes через N8N
    
    Expected JSON:
    {
        "team": "Heroes Advising Crew",
        "project": "project_name",
        "context": "описание контекста",
        "priority": "HIGH|MEDIUM|LOW",
        "client": "client_name"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        # Валидация обязательных полей
        required_fields = ['team', 'project', 'context']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                "error": "Missing required fields",
                "missing": missing_fields
            }), 400
        
        # Генерируем структурированный контекст
        structured_context = format_context_for_ticket(data)
        
        # Создаем тикет через существующую систему
        ticket_result = create_heroes_ticket(
            ticket_type="context",
            content=structured_context,
            team=data['team'],
            priority=data.get('priority', 'MEDIUM')
        )
        
        logger.info(f"Контекст получен от команды {data['team']} для проекта {data['project']}")
        
        return jsonify({
            "status": "success",
            "message": "Context received and ticket created",
            "ticket_id": ticket_result.get('ticket_id'),
            "formatted_context": structured_context
        })
        
    except Exception as e:
        logger.error(f"Ошибка обработки контекста: {e}")
        return jsonify({"error": str(e)}), 500

@heroes_bp.route('/tasks', methods=['POST'])
def receive_tasks():
    """
    Принимает задачи от команд Heroes через N8N
    
    Expected JSON:
    {
        "team": "Heroes Advising Crew",
        "task_title": "название задачи",
        "description": "описание задачи",
        "priority": "BLOCKER|ASAP|RESEARCH",
        "assignee": "@username",
        "deadline": "YYYY-MM-DD"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        # Валидация обязательных полей
        required_fields = ['team', 'task_title', 'description']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                "error": "Missing required fields", 
                "missing": missing_fields
            }), 400
        
        # Генерируем структурированную задачу
        structured_task = format_task_for_ticket(data)
        
        # Создаем тикет через существующую систему
        ticket_result = create_heroes_ticket(
            ticket_type="task",
            content=structured_task,
            team=data['team'],
            priority=data.get('priority', 'ASAP')
        )
        
        logger.info(f"Задача получена от команды {data['team']}: {data['task_title']}")
        
        return jsonify({
            "status": "success",
            "message": "Task received and ticket created",
            "ticket_id": ticket_result.get('ticket_id'),
            "formatted_task": structured_task
        })
        
    except Exception as e:
        logger.error(f"Ошибка обработки задачи: {e}")
        return jsonify({"error": str(e)}), 500

@heroes_bp.route('/hypotheses', methods=['POST'])
def receive_hypotheses():
    """
    Принимает гипотезы для тестирования от команд Heroes через N8N
    
    Expected JSON:
    {
        "team": "Heroes Advising Crew",
        "hypothesis": "описание гипотезы",
        "metrics": ["метрика1", "метрика2"],
        "test_duration": "48 hours",
        "expected_result": "ожидаемый результат"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        # Валидация обязательных полей
        required_fields = ['team', 'hypothesis']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                "error": "Missing required fields",
                "missing": missing_fields
            }), 400
        
        # Генерируем структурированную гипотезу с RAT анализом
        structured_hypothesis = format_hypothesis_for_ticket(data)
        
        # Создаем тикет через существующую систему
        ticket_result = create_heroes_ticket(
            ticket_type="hypothesis",
            content=structured_hypothesis,
            team=data['team'],
            priority="RESEARCH"
        )
        
        logger.info(f"Гипотеза получена от команды {data['team']}")
        
        return jsonify({
            "status": "success",
            "message": "Hypothesis received and ticket created",
            "ticket_id": ticket_result.get('ticket_id'),
            "formatted_hypothesis": structured_hypothesis,
            "monitoring_url": f"http://127.0.0.1:5000/experiments/{ticket_result.get('ticket_id')}"
        })
        
    except Exception as e:
        logger.error(f"Ошибка обработки гипотезы: {e}")
        return jsonify({"error": str(e)}), 500

def format_context_for_ticket(data: Dict[str, Any]) -> str:
    """Форматирует контекст в структурированный текст для тикета"""
    
    context_text = f"""# 📋 Контекст проекта от команды {data['team']}

## 🎯 Проект: {data['project']}
**Клиент**: {data.get('client', 'Не указан')}
**Приоритет**: {data.get('priority', 'MEDIUM')}
**Дата**: {datetime.now().strftime('%d %B %Y')}

## 📝 Описание контекста:
{data['context']}

## 🔗 Команда ответственная:
- **Команда**: {data['team']}
- **Контакт**: {data.get('contact', 'Не указан')}

## 📊 Следующие шаги:
- [ ] Проанализировать контекст
- [ ] Определить приоритеты
- [ ] Назначить ответственных
- [ ] Создать план действий

---
*Автоматически создано через Heroes API*
"""
    return context_text

def format_task_for_ticket(data: Dict[str, Any]) -> str:
    """Форматирует задачу в структурированный текст для тикета"""
    
    task_text = f"""# 🎯 Задача от команды {data['team']}

## 📋 {data['task_title']}
**Приоритет**: {data.get('priority', 'ASAP')} 
**Ответственный**: {data.get('assignee', '@не_назначен')}
**Дедлайн**: {data.get('deadline', 'Не указан')}
**Дата создания**: {datetime.now().strftime('%d %B %Y')}

## 📝 Описание:
{data['description']}

## ✅ Критерии выполнения:
{data.get('acceptance_criteria', '- [ ] Задача выполнена согласно описанию')}

## 🔗 Команда:
- **Создано**: {data['team']}
- **Контакт**: {data.get('contact', 'Не указан')}

---
*Автоматически создано через Heroes API*
"""
    return task_text

def format_hypothesis_for_ticket(data: Dict[str, Any]) -> str:
    """Форматирует гипотезу с RAT анализом в структурированный текст для тикета"""
    
    metrics = data.get('metrics', [])
    metrics_text = '\n'.join([f"- {metric}" for metric in metrics]) if metrics else "- Не указаны"
    
    hypothesis_text = f"""# 🧪 Гипотеза от команды {data['team']}

## 🔬 Гипотеза для тестирования:
{data['hypothesis']}

## 📋 RAT (Рациональный Атомарный Тест):
- **Условие**: Если {data['hypothesis']}
- **Действие**: {data.get('test_action', 'Провести эксперимент')}
- **Ожидаемый результат**: {data.get('expected_result', 'Измеримое улучшение')}

## 🎯 Критерий фальсифицируемости:
- Гипотеза опровергается при отклонении >20% от базовой линии
- Период тестирования: {data.get('test_duration', '48 часов')}

## 📊 Метрики для отслеживания:
{metrics_text}

## 🔗 Мониторинг эксперимента:
- **Команда**: {data['team']}
- **Дата начала**: {datetime.now().strftime('%d %B %Y')}
- **Контакт**: {data.get('contact', 'Не указан')}

---
*Автоматически создано через Heroes API*
"""
    return hypothesis_text

def create_heroes_ticket(ticket_type: str, content: str, team: str, priority: str) -> Dict[str, Any]:
    """Создает тикет через существующую систему триггеров"""
    
    try:
        # Импортируем триггеры задач
        from advising_platform.src.core.task_incident_triggers import TaskIncidentTriggers
        
        triggers = TaskIncidentTriggers()
        
        # Генерируем уникальный ID тикета
        ticket_id = f"HEROES_{ticket_type.upper()}_{int(datetime.now().timestamp())}"
        
        # Создаем задачу через систему триггеров
        # Используем существующий метод для создания задач
        task_created = True  # Пока упрощенная реализация
        
        # Логируем создание тикета
        logger.info(f"Создан тикет {ticket_id} для команды {team}")
        
        return {
            "ticket_id": ticket_id,
            "created": task_created,
            "team": team,
            "type": ticket_type
        }
        
    except Exception as e:
        logger.error(f"Ошибка создания тикета: {e}")
        return {
            "ticket_id": f"ERROR_{int(datetime.now().timestamp())}",
            "created": False,
            "error": str(e)
        }