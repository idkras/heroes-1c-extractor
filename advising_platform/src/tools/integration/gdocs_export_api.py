#!/usr/bin/env python3
"""
API для экспорта документов в Google Docs.

Этот сервис предоставляет API для экспорта документов в Google Docs.
Запускается на порту 5005.
"""

import os
import sys
import json
import logging
import time
from pathlib import Path
from flask import Flask, request, jsonify
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('gdocs_export_api')

# Инициализация Flask приложения
app = Flask(__name__)

# Определение корневой директории проекта
ROOT_DIR = Path(__file__).parent.parent.parent.parent.parent

# Путь к основному скрипту экспорта
EXPORT_SCRIPT = ROOT_DIR / "export_to_gdocs.py"

@app.route('/api/export/gdocs', methods=['POST'])
def export_to_gdocs():
    """
    Экспортирует документ в Google Docs.
    
    Ожидает JSON с параметрами:
    {
        "path": "путь/к/документу.md",
        "doc_id": "идентификатор_google_docs" (опционально)
    }
    
    Возвращает:
    {
        "success": true/false,
        "message": "сообщение",
        "doc_url": "URL документа в Google Docs" (если успешно)
    }
    """
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "message": "Отсутствуют данные запроса"}), 400
        
        path = data.get('path')
        doc_id = data.get('doc_id', '')
        
        if not path:
            return jsonify({"success": False, "message": "Не указан путь к документу"}), 400
        
        # Здесь будет вызов скрипта экспорта
        logger.info(f"Запрос на экспорт документа {path} в Google Docs")
        
        # Заглушка для демонстрации
        time.sleep(1)  # Имитация задержки при экспорте
        
        # В реальном сценарии здесь будет вызов функции экспорта
        # from export_to_gdocs import export_document
        # result = export_document(path, doc_id)
        
        # Демонстрационный результат
        result = {
            "success": True,
            "message": f"Документ {path} успешно экспортирован",
            "doc_url": f"https://docs.google.com/document/d/{doc_id or 'new_doc_id'}"
        }
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Ошибка при экспорте документа: {str(e)}")
        return jsonify({"success": False, "message": f"Ошибка: {str(e)}"}), 500

@app.route('/api/export/status', methods=['GET'])
def get_status():
    """Возвращает статус сервиса."""
    return jsonify({
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('GDOCS_EXPORT_PORT', 5005))
    logger.info(f"Запуск сервера экспорта в Google Docs на порту {port}")
    app.run(host='0.0.0.0', port=port)