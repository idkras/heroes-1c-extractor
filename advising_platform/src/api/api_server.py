"""
API-сервер для интеграции с внешними системами.
Обеспечивает эндпоинты для работы с отчетами Lavsit и управления задачами и инцидентами.
"""

import os
import logging
import json
from flask import Flask, request, jsonify
from pathlib import Path

# Пытаемся импортировать API управления задачами
try:
    from advising_platform.src.api.task_manager_api import register_task_api
    HAS_TASK_API = True
except ImportError as e:
    print(f"Не удалось импортировать модуль управления задачами: {e}")
    HAS_TASK_API = False

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='external_api.log'
)
logger = logging.getLogger(__name__)

# Консольный обработчик для логов
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# Создаем Flask-приложение
app = Flask(__name__)

# Регистрируем Heroes API Blueprint
try:
    from advising_platform.src.api.heroes_api import heroes_bp
    app.register_blueprint(heroes_bp)
    logger.info("Heroes API успешно зарегистрирован")
except ImportError as e:
    logger.warning(f"Не удалось загрузить Heroes API: {e}")

# Порт для API-сервера
API_PORT = 5003

@app.route('/api/health', methods=['GET'])
def health_check():
    """Простая проверка работоспособности API"""
    return jsonify({"status": "ok", "message": "API server is running"})

@app.route('/api/lavsit/report', methods=['GET'])
def get_lavsit_report():
    """Возвращает данные отчета по Lavsit в формате JSON"""
    json_file = Path('lavsit_blockers_report.json')
    
    if json_file.exists():
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            return jsonify(report_data)
        except Exception as e:
            logger.error(f"Ошибка при чтении файла отчета: {str(e)}")
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Отчет не найден"}), 404

@app.route('/api/lavsit/blockers', methods=['GET'])
def get_lavsit_blockers():
    """Возвращает только блокеры из отчета по Lavsit"""
    json_file = Path('lavsit_blockers_report.json')
    
    if json_file.exists():
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            
            blockers = report_data.get('blockers', [])
            sorted_blockers = sorted(blockers, key=lambda x: x['count'], reverse=True)
            
            return jsonify({
                "blockers": sorted_blockers,
                "analysis_date": report_data.get('analysis_date', ''),
                "total_messages": report_data.get('total_messages', 0)
            })
        except Exception as e:
            logger.error(f"Ошибка при чтении файла отчета: {str(e)}")
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Отчет не найден"}), 404

@app.route('/api/analyze', methods=['POST'])
def analyze_data():
    """
    Запускает анализ данных из предоставленного файла.
    
    Ожидает JSON в формате:
    {
        "file_path": "путь/к/файлу.tsv",
        "analysis_type": "lavsit_wazzup"
    }
    """
    data = request.json
    
    if not data:
        return jsonify({"error": "Отсутствуют данные в запросе"}), 400
    
    file_path = data.get('file_path')
    analysis_type = data.get('analysis_type')
    
    if not file_path:
        return jsonify({"error": "Не указан путь к файлу"}), 400
    
    if not analysis_type:
        return jsonify({"error": "Не указан тип анализа"}), 400
    
    if not os.path.exists(file_path):
        return jsonify({"error": f"Файл не найден: {file_path}"}), 404
    
    # Запускаем анализ в зависимости от типа
    try:
        if analysis_type == "lavsit_wazzup":
            # Импортируем здесь, чтобы не было циклических зависимостей
            import subprocess
            
            # Запускаем анализ как отдельный процесс
            process = subprocess.Popen(
                ["python", "analyze_lavsit_wazzup.py", file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Ошибка при запуске анализа: {stderr.decode('utf-8')}")
                return jsonify({"error": f"Ошибка при запуске анализа: {stderr.decode('utf-8')}"}), 500
            
            # Проверяем, создан ли файл отчета
            json_file = Path('lavsit_blockers_report.json')
            if not json_file.exists():
                return jsonify({"error": "Файл отчета не был создан после анализа"}), 500
            
            return jsonify({"status": "success", "message": "Анализ успешно завершен"}), 200
        else:
            return jsonify({"error": f"Неизвестный тип анализа: {analysis_type}"}), 400
    except Exception as e:
        logger.error(f"Ошибка при запуске анализа: {str(e)}")
        return jsonify({"error": str(e)}), 500

def start_api_server(port=API_PORT):
    """Запускает API-сервер на указанном порту"""
    try:
        # Регистрируем API управления задачами, если оно доступно
        if HAS_TASK_API:
            register_task_api(app)
            logger.info("API управления задачами успешно зарегистрировано")
        else:
            logger.warning("API управления задачами недоступно")
        
        # Выводим информацию о запуске
        print(f"API-сервер запущен на порту {port} (0.0.0.0), PID: {os.getpid()}")
        logger.info(f"API-сервер запущен на порту {port} (0.0.0.0), PID: {os.getpid()}")
        
        # Запускаем сервер
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        logger.error(f"Ошибка запуска API-сервера: {str(e)}")
        print(f"Ошибка запуска API-сервера: {str(e)}")

if __name__ == "__main__":
    start_api_server()