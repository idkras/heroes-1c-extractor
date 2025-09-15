"""
API для работы со стандартами и их реализациями.

Предоставляет маршруты для:
1. Получения списка доступных стандартов
2. Получения информации о реализациях стандартов
3. Валидации соответствия реализаций стандартам
"""

import logging
from typing import Dict, List, Any, Optional
from flask import Blueprint, jsonify, request, Response

from advising_platform.standards.core.registry import (
    list_implementations,
    get_implementation_status
)
from advising_platform.standards.core.validation import validate_implementation
from advising_platform.standards import get_implementation

# Настройка логирования
logger = logging.getLogger(__name__)

# Создаем Blueprint для API стандартов
standards_api = Blueprint('standards_api', __name__)


@standards_api.route('/standards', methods=['GET'])
def get_standards() -> Response:
    """
    Возвращает список доступных стандартов и их реализаций.
    
    Returns:
        JSON-ответ со списком стандартов
    """
    try:
        implementations = list_implementations()
        
        # Группируем реализации по стандартам и версиям
        standards_dict = {}
        
        for impl in implementations:
            standard_id = impl.standard_id
            version = impl.version
            component = impl.component
            
            if standard_id not in standards_dict:
                standards_dict[standard_id] = {}
            
            if version not in standards_dict[standard_id]:
                standards_dict[standard_id][version] = []
            
            standards_dict[standard_id][version].append({
                "component": component,
                "obj_type": impl.obj_type,
                "obj_name": impl.obj_name,
                "module": impl.module,
                "description": impl.description
            })
        
        # Формируем результат
        result = []
        
        for standard_id, versions in standards_dict.items():
            standard_info = {
                "id": standard_id,
                "versions": []
            }
            
            for version, components in versions.items():
                version_info = {
                    "version": version,
                    "components": components
                }
                standard_info["versions"].append(version_info)
            
            result.append(standard_info)
        
        return jsonify({
            "status": "success",
            "data": {
                "standards": result
            }
        })
    
    except Exception as e:
        logger.error(f"Ошибка при получении списка стандартов: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@standards_api.route('/standards/<standard_id>/status', methods=['GET'])
def get_standard_status(standard_id: str) -> Response:
    """
    Возвращает статус реализации стандарта.
    
    Args:
        standard_id: Идентификатор стандарта
    
    Returns:
        JSON-ответ со статусом реализации стандарта
    """
    try:
        # Получаем все реализации стандарта
        implementations = list_implementations(standard_id)
        
        if not implementations:
            return jsonify({
                "status": "error",
                "message": f"Стандарт не найден: {standard_id}"
            }), 404
        
        # Группируем реализации по компонентам
        components = {}
        
        for impl in implementations:
            component = impl.component
            
            if component not in components:
                components[component] = []
            
            components[component].append({
                "version": impl.version,
                "obj_type": impl.obj_type,
                "obj_name": impl.obj_name,
                "module": impl.module
            })
        
        # Получаем статус для каждого компонента
        components_status = {}
        
        for component in components:
            status = get_implementation_status(standard_id, component)
            components_status[component] = status.to_dict()
        
        return jsonify({
            "status": "success",
            "data": {
                "standard_id": standard_id,
                "components": components,
                "components_status": components_status
            }
        })
    
    except Exception as e:
        logger.error(f"Ошибка при получении статуса стандарта {standard_id}: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@standards_api.route('/standards/<standard_id>/<version>/<component>', methods=['GET'])
def get_implementation_info(standard_id: str, version: str, component: str) -> Response:
    """
    Возвращает информацию о реализации компонента стандарта.
    
    Args:
        standard_id: Идентификатор стандарта
        version: Версия стандарта
        component: Компонент стандарта
    
    Returns:
        JSON-ответ с информацией о реализации компонента стандарта
    """
    try:
        # Получаем реализацию
        implementation = get_implementation(standard_id, version, component)
        
        if not implementation:
            return jsonify({
                "status": "error",
                "message": f"Реализация не найдена: {standard_id}:{version}:{component}"
            }), 404
        
        # Получаем информацию об объекте
        obj_info = {
            "standard_id": standard_id,
            "version": version,
            "component": component,
            "obj_type": type(implementation).__name__,
            "obj_name": getattr(implementation, "__name__", str(implementation)),
            "module": getattr(implementation, "__module__", ""),
            "doc": implementation.__doc__ or ""
        }
        
        return jsonify({
            "status": "success",
            "data": obj_info
        })
    
    except Exception as e:
        logger.error(f"Ошибка при получении информации о реализации {standard_id}:{version}:{component}: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@standards_api.route('/standards/validate', methods=['POST'])
def validate_implementation_endpoint() -> Response:
    """
    Валидирует соответствие реализации стандарту.
    
    Request Body:
        {
            "standard_id": "incident",
            "version": "1.9",
            "component": "creation"
        }
    
    Returns:
        JSON-ответ с результатами валидации
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "Не предоставлены данные для валидации"
            }), 400
        
        standard_id = data.get("standard_id")
        version = data.get("version")
        component = data.get("component")
        
        if not all([standard_id, version, component]):
            return jsonify({
                "status": "error",
                "message": "Необходимо указать standard_id, version и component"
            }), 400
        
        # Получаем реализацию
        implementation = get_implementation(standard_id, version, component)
        
        if not implementation:
            return jsonify({
                "status": "error",
                "message": f"Реализация не найдена: {standard_id}:{version}:{component}"
            }), 404
        
        # Валидируем реализацию
        validation_results = validate_implementation(implementation)
        
        # Преобразуем результаты валидации в JSON
        results = []
        
        for result in validation_results:
            results.append({
                "standard_info": result.standard_info.to_dict(),
                "is_valid": result.is_valid,
                "issues": [issue.to_dict() for issue in result.issues]
            })
        
        return jsonify({
            "status": "success",
            "data": {
                "validation_results": results
            }
        })
    
    except Exception as e:
        logger.error(f"Ошибка при валидации реализации: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@standards_api.route('/incidents', methods=['GET'])
def get_incidents() -> Response:
    """
    Возвращает список инцидентов.
    
    Query Parameters:
        status (str, optional): Фильтр по статусу инцидента
        severity (str, optional): Фильтр по серьезности инцидента
    
    Returns:
        JSON-ответ со списком инцидентов
    """
    try:
        from advising_platform.standards.incidents import incident_storage
        
        # Получаем параметры запроса
        status = request.args.get('status')
        severity = request.args.get('severity')
        
        # Получаем все инциденты
        incidents = incident_storage.get_incidents(reload=True)
        
        # Применяем фильтры
        if status:
            incidents = [inc for inc in incidents if inc.get('status') == status]
        
        if severity:
            incidents = [inc for inc in incidents if inc.get('severity') == severity]
        
        return jsonify({
            "status": "success",
            "data": {
                "incidents": incidents
            }
        })
    
    except Exception as e:
        logger.error(f"Ошибка при получении списка инцидентов: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@standards_api.route('/incidents/<incident_id>', methods=['GET'])
def get_incident(incident_id: str) -> Response:
    """
    Возвращает информацию об инциденте.
    
    Args:
        incident_id: Идентификатор инцидента
    
    Returns:
        JSON-ответ с информацией об инциденте
    """
    try:
        from advising_platform.standards.incidents import incident_storage
        
        # Получаем инцидент
        incident = incident_storage.get_incident_by_id(incident_id, reload=True)
        
        if not incident:
            return jsonify({
                "status": "error",
                "message": f"Инцидент не найден: {incident_id}"
            }), 404
        
        return jsonify({
            "status": "success",
            "data": {
                "incident": incident
            }
        })
    
    except Exception as e:
        logger.error(f"Ошибка при получении информации об инциденте {incident_id}: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@standards_api.route('/incidents', methods=['POST'])
def create_incident() -> Response:
    """
    Создает новый инцидент.
    
    Request Body:
        {
            "title": "Заголовок инцидента",
            "content": "Содержимое инцидента",
            "severity": "medium",
            "category": "system architecture"
        }
    
    Returns:
        JSON-ответ с идентификатором созданного инцидента
    """
    try:
        from advising_platform.standards.incidents import create_incident as create_incident_func
        
        data = request.json
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "Не предоставлены данные для создания инцидента"
            }), 400
        
        title = data.get("title")
        content = data.get("content")
        severity = data.get("severity", "medium")
        category = data.get("category", "system architecture")
        
        if not all([title, content]):
            return jsonify({
                "status": "error",
                "message": "Необходимо указать title и content"
            }), 400
        
        # Создаем инцидент
        incident_id = create_incident_func(title, content, severity, category)
        
        return jsonify({
            "status": "success",
            "data": {
                "incident_id": incident_id
            }
        })
    
    except Exception as e:
        logger.error(f"Ошибка при создании инцидента: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@standards_api.route('/incidents/<incident_id>/status', methods=['PUT'])
def update_incident_status(incident_id: str) -> Response:
    """
    Обновляет статус инцидента.
    
    Args:
        incident_id: Идентификатор инцидента
    
    Request Body:
        {
            "status": "resolved"
        }
    
    Returns:
        JSON-ответ с результатом обновления
    """
    try:
        from advising_platform.standards.incidents import update_incident_status as update_status_func
        
        data = request.json
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "Не предоставлены данные для обновления статуса"
            }), 400
        
        new_status = data.get("status")
        
        if not new_status:
            return jsonify({
                "status": "error",
                "message": "Необходимо указать status"
            }), 400
        
        # Обновляем статус инцидента
        result = update_status_func(incident_id, new_status)
        
        if not result:
            return jsonify({
                "status": "error",
                "message": f"Не удалось обновить статус инцидента {incident_id}"
            }), 400
        
        return jsonify({
            "status": "success",
            "data": {
                "incident_id": incident_id,
                "new_status": new_status
            }
        })
    
    except Exception as e:
        logger.error(f"Ошибка при обновлении статуса инцидента {incident_id}: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@standards_api.route('/todos', methods=['GET'])
def get_todos() -> Response:
    """
    Возвращает список задач.
    
    Query Parameters:
        status (str, optional): Фильтр по статусу задачи
        priority (str, optional): Фильтр по приоритету задачи
    
    Returns:
        JSON-ответ со списком задач
    """
    try:
        from advising_platform.standards.task import todo_storage, get_todos_by_status, get_todos_by_priority
        
        # Получаем параметры запроса
        status = request.args.get('status')
        priority = request.args.get('priority')
        
        # Получаем задачи в зависимости от параметров
        if status:
            todos = get_todos_by_status(status)
        elif priority:
            todos = get_todos_by_priority(priority)
        else:
            todos = todo_storage.get_todos(reload=True)
        
        return jsonify({
            "status": "success",
            "data": {
                "todos": todos
            }
        })
    
    except Exception as e:
        logger.error(f"Ошибка при получении списка задач: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@standards_api.route('/todos/<todo_id>', methods=['GET'])
def get_todo(todo_id: str) -> Response:
    """
    Возвращает информацию о задаче.
    
    Args:
        todo_id: Идентификатор задачи
    
    Returns:
        JSON-ответ с информацией о задаче
    """
    try:
        from advising_platform.standards.task import todo_storage
        
        # Получаем задачу
        todo = todo_storage.get_todo_by_id(todo_id, reload=True)
        
        if not todo:
            return jsonify({
                "status": "error",
                "message": f"Задача не найдена: {todo_id}"
            }), 404
        
        return jsonify({
            "status": "success",
            "data": {
                "todo": todo
            }
        })
    
    except Exception as e:
        logger.error(f"Ошибка при получении информации о задаче {todo_id}: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@standards_api.route('/todos', methods=['POST'])
def create_todo() -> Response:
    """
    Создает новую задачу.
    
    Request Body:
        {
            "title": "Заголовок задачи",
            "description": "Описание задачи",
            "priority": "NORMAL",
            "plan": "План решения",
            "success_criteria": "Критерии успеха",
            "dependencies": "Зависимости",
            "notes": "Примечания"
        }
    
    Returns:
        JSON-ответ с идентификатором созданной задачи
    """
    try:
        from advising_platform.standards.task import create_todo as create_todo_func
        
        data = request.json
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "Не предоставлены данные для создания задачи"
            }), 400
        
        title = data.get("title")
        description = data.get("description")
        priority = data.get("priority", "NORMAL")
        plan = data.get("plan", "")
        success_criteria = data.get("success_criteria", "")
        dependencies = data.get("dependencies", "")
        notes = data.get("notes", "")
        
        if not all([title, description]):
            return jsonify({
                "status": "error",
                "message": "Необходимо указать title и description"
            }), 400
        
        # Создаем задачу
        todo_id = create_todo_func(
            title, description, priority, plan,
            success_criteria, dependencies, notes
        )
        
        return jsonify({
            "status": "success",
            "data": {
                "todo_id": todo_id
            }
        })
    
    except Exception as e:
        logger.error(f"Ошибка при создании задачи: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@standards_api.route('/todos/<todo_id>/status', methods=['PUT'])
def update_todo_status(todo_id: str) -> Response:
    """
    Обновляет статус задачи.
    
    Args:
        todo_id: Идентификатор задачи
    
    Request Body:
        {
            "status": "IN_PROGRESS"
        }
    
    Returns:
        JSON-ответ с результатом обновления
    """
    try:
        from advising_platform.standards.task import update_todo_status as update_status_func
        
        data = request.json
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "Не предоставлены данные для обновления статуса"
            }), 400
        
        new_status = data.get("status")
        
        if not new_status:
            return jsonify({
                "status": "error",
                "message": "Необходимо указать status"
            }), 400
        
        # Обновляем статус задачи
        result = update_status_func(todo_id, new_status)
        
        if not result:
            return jsonify({
                "status": "error",
                "message": f"Не удалось обновить статус задачи {todo_id}"
            }), 400
        
        return jsonify({
            "status": "success",
            "data": {
                "todo_id": todo_id,
                "new_status": new_status
            }
        })
    
    except Exception as e:
        logger.error(f"Ошибка при обновлении статуса задачи {todo_id}: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@standards_api.route('/hypotheses', methods=['GET'])
def get_hypotheses() -> Response:
    """
    Возвращает список гипотез.
    
    Query Parameters:
        status (str, optional): Фильтр по статусу гипотезы
        tag (str, optional): Фильтр по тегу гипотезы
        incident_id (str, optional): Фильтр по связанному инциденту
    
    Returns:
        JSON-ответ со списком гипотез
    """
    try:
        from advising_platform.standards.task import hypothesis_storage
        
        # Получаем параметры запроса
        status = request.args.get('status')
        tag = request.args.get('tag')
        incident_id = request.args.get('incident_id')
        
        # Получаем все гипотезы
        if status:
            hypotheses = hypothesis_storage.find_hypotheses_by_status(status)
        elif tag:
            hypotheses = hypothesis_storage.find_hypotheses_by_tag(tag)
        elif incident_id:
            hypotheses = hypothesis_storage.find_hypotheses_by_incident(incident_id)
        else:
            hypotheses = hypothesis_storage.get_all_hypotheses()
        
        # Преобразуем гипотезы в словари
        hypotheses_dict = [h.to_dict() for h in hypotheses]
        
        return jsonify({
            "status": "success",
            "data": {
                "hypotheses": hypotheses_dict
            }
        })
    
    except Exception as e:
        logger.error(f"Ошибка при получении списка гипотез: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@standards_api.route('/hypotheses/<hypothesis_id>', methods=['GET'])
def get_hypothesis(hypothesis_id: str) -> Response:
    """
    Возвращает информацию о гипотезе.
    
    Args:
        hypothesis_id: Идентификатор гипотезы
    
    Returns:
        JSON-ответ с информацией о гипотезе
    """
    try:
        from advising_platform.standards.task import hypothesis_storage
        
        # Получаем гипотезу
        hypothesis = hypothesis_storage.get_hypothesis(hypothesis_id)
        
        if not hypothesis:
            return jsonify({
                "status": "error",
                "message": f"Гипотеза не найдена: {hypothesis_id}"
            }), 404
        
        return jsonify({
            "status": "success",
            "data": {
                "hypothesis": hypothesis.to_dict(),
                "markdown": hypothesis.to_markdown()
            }
        })
    
    except Exception as e:
        logger.error(f"Ошибка при получении информации о гипотезе {hypothesis_id}: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@standards_api.route('/hypotheses', methods=['POST'])
def create_hypothesis() -> Response:
    """
    Создает новую гипотезу.
    
    Request Body:
        {
            "statement": "Формулировка гипотезы",
            "context": "Контекст гипотезы",
            "verification_method": "Метод проверки",
            "experiment_design": "Дизайн эксперимента",
            "expected_results": "Ожидаемые результаты",
            "tags": ["tag1", "tag2"],
            "related_incidents": ["incident_id1", "incident_id2"]
        }
    
    Returns:
        JSON-ответ с идентификатором созданной гипотезы
    """
    try:
        from advising_platform.standards.task import create_hypothesis as create_hypothesis_func
        
        data = request.json
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "Не предоставлены данные для создания гипотезы"
            }), 400
        
        statement = data.get("statement")
        context = data.get("context", "")
        verification_method = data.get("verification_method", "")
        experiment_design = data.get("experiment_design", "")
        expected_results = data.get("expected_results", "")
        tags = data.get("tags", [])
        related_incidents = data.get("related_incidents", [])
        
        if not statement:
            return jsonify({
                "status": "error",
                "message": "Необходимо указать statement"
            }), 400
        
        # Создаем гипотезу
        hypothesis_id = create_hypothesis_func(
            statement, context, verification_method,
            experiment_design, expected_results, tags, related_incidents
        )
        
        return jsonify({
            "status": "success",
            "data": {
                "hypothesis_id": hypothesis_id
            }
        })
    
    except Exception as e:
        logger.error(f"Ошибка при создании гипотезы: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@standards_api.route('/hypotheses/<hypothesis_id>/verify', methods=['PUT'])
def verify_hypothesis(hypothesis_id: str) -> Response:
    """
    Верифицирует гипотезу.
    
    Args:
        hypothesis_id: Идентификатор гипотезы
    
    Request Body:
        {
            "actual_results": "Фактические результаты",
            "conclusion": "Заключение",
            "status": "CONFIRMED"
        }
    
    Returns:
        JSON-ответ с результатом верификации
    """
    try:
        from advising_platform.standards.task import verify_hypothesis as verify_hypothesis_func
        
        data = request.json
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "Не предоставлены данные для верификации гипотезы"
            }), 400
        
        actual_results = data.get("actual_results")
        conclusion = data.get("conclusion")
        status = data.get("status")
        
        if not all([actual_results, conclusion, status]):
            return jsonify({
                "status": "error",
                "message": "Необходимо указать actual_results, conclusion и status"
            }), 400
        
        # Верифицируем гипотезу
        result = verify_hypothesis_func(hypothesis_id, actual_results, conclusion, status)
        
        if not result:
            return jsonify({
                "status": "error",
                "message": f"Не удалось верифицировать гипотезу {hypothesis_id}"
            }), 400
        
        return jsonify({
            "status": "success",
            "data": {
                "hypothesis_id": hypothesis_id,
                "new_status": status
            }
        })
    
    except Exception as e:
        logger.error(f"Ошибка при верификации гипотезы {hypothesis_id}: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@standards_api.route('/five-whys', methods=['POST'])
def analyze_five_whys() -> Response:
    """
    Выполняет анализ "5 почему" для указанной проблемы.
    
    Request Body:
        {
            "problem_statement": "Проблема для анализа",
            "whys": [
                {"question": "вопрос 1", "answer": "ответ 1"},
                {"question": "вопрос 2", "answer": "ответ 2"},
                ...
            ]
        }
    
    Returns:
        JSON-ответ с результатами анализа
    """
    try:
        from advising_platform.standards.incidents.fivewhys import perform_five_whys_analysis
        
        data = request.json
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "Не предоставлены данные для анализа"
            }), 400
        
        problem_statement = data.get("problem_statement")
        whys = data.get("whys", [])
        
        if not problem_statement:
            return jsonify({
                "status": "error",
                "message": "Необходимо указать problem_statement"
            }), 400
        
        # Выполняем анализ
        analysis = perform_five_whys_analysis(problem_statement, whys)
        
        return jsonify({
            "status": "success",
            "data": {
                "analysis": {
                    "problem_statement": analysis["problem_statement"],
                    "whys": analysis["whys"],
                    "validation": analysis["validation"],
                    "text": analysis["text"]
                }
            }
        })
    
    except Exception as e:
        logger.error(f"Ошибка при выполнении анализа 5 почему: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


def register_standards_api(app):
    """
    Регистрирует API стандартов в приложении Flask.
    
    Args:
        app: Приложение Flask
    """
    app.register_blueprint(standards_api, url_prefix='/api/v1')
    logger.info("Standards API зарегистрировано")