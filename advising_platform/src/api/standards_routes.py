#!/usr/bin/env python3
"""
API-маршруты для работы со стандартами и проверки соответствия документов стандартам.
"""

import os
import json
from flask import Blueprint, request, jsonify
from pathlib import Path

from ..tools.standards_validator import StandardsValidator

# Создаем экземпляр валидатора стандартов
validator = StandardsValidator()

# Создаем Blueprint для маршрутов API
standards_routes = Blueprint('standards_routes', __name__)

@standards_routes.route('/standards/access/log', methods=['POST'])
def log_standard_access():
    """
    Регистрирует факт доступа к стандарту.
    
    Ожидаемый формат запроса:
    {
        "standard_path": "путь/к/стандарту.md"
    }
    
    Returns:
        JSON-ответ с результатом операции.
    """
    data = request.json
    
    if not data or 'standard_path' not in data:
        return jsonify({"error": "Missing required field: standard_path"}), 400
    
    standard_path = data['standard_path']
    
    # Проверяем существование файла
    if not os.path.exists(standard_path):
        return jsonify({"error": f"Standard not found: {standard_path}"}), 404
    
    if validator.log_standard_access(standard_path):
        return jsonify({"success": True, "message": f"Access to {standard_path} logged successfully"}), 200
    else:
        return jsonify({"success": False, "message": "Failed to log access"}), 500

@standards_routes.route('/standards/compliance/check', methods=['POST'])
def check_standards_compliance():
    """
    Проверяет соответствие документа стандартам.
    
    Ожидаемый формат запроса:
    {
        "document_path": "путь/к/документу.md"
    }
    
    Returns:
        JSON-ответ с результатом проверки.
    """
    data = request.json
    
    if not data or 'document_path' not in data:
        return jsonify({"error": "Missing required field: document_path"}), 400
    
    document_path = data['document_path']
    
    compliance, missing_standards = validator.check_standards_compliance(document_path)
    
    if compliance:
        checklist = validator.get_checklist_by_document_type(document_path)
        template_path = validator.get_template_by_document_type(document_path)
        
        response = {
            "compliance": True,
            "document_path": document_path,
            "checklist": checklist
        }
        
        if template_path:
            response["template_path"] = template_path
        
        return jsonify(response), 200
    else:
        return jsonify({
            "compliance": False,
            "document_path": document_path,
            "missing_standards": missing_standards
        }), 200

@standards_routes.route('/standards/required', methods=['GET'])
def get_required_standards():
    """
    Возвращает список обязательных стандартов.
    
    Returns:
        JSON-ответ со списком обязательных стандартов.
    """
    return jsonify({
        "required_standards": validator.required_standards
    }), 200

@standards_routes.route('/standards/templates/<doc_type>', methods=['GET'])
def get_template(doc_type):
    """
    Возвращает шаблон для указанного типа документа.
    
    Args:
        doc_type (str): Тип документа (incident, task, etc.).
    
    Returns:
        JSON-ответ с путем к шаблону или содержимым шаблона.
    """
    template_path = None
    
    if doc_type == 'incident':
        template_path = "templates/incident_template.md"
    elif doc_type == 'task':
        template_path = "templates/task_template.md"
    
    if not template_path or not os.path.exists(template_path):
        return jsonify({"error": f"Template not found for document type: {doc_type}"}), 404
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    return jsonify({
        "template_path": template_path,
        "template_content": template_content
    }), 200

def register_routes(app):
    """
    Регистрирует маршруты API в приложении Flask.
    
    Args:
        app: Приложение Flask.
    """
    app.register_blueprint(standards_routes, url_prefix='/api/standards')