"""
Модуль маршрутов для отображения отчетов и аналитики.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from flask import Blueprint, render_template, send_file, jsonify, request, abort, Response

# Создаем Blueprint для маршрутов отчетов
reports_blueprint = Blueprint('reports', __name__)

# Директория для хранения отчетов
REPORTS_DIR = Path('.') / 'reports'
if not REPORTS_DIR.exists():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

@reports_blueprint.route('/lavsit_report')
def lavsit_report():
    """
    Отображает аналитический отчет по блокерам покупки Lavsit.ru.
    
    Returns:
        HTML-страница с отчетом
    """
    # Проверяем существование файла отчета
    report_file = Path('lavsit_blockers_report.html')
    
    if report_file.exists():
        with open(report_file, 'r', encoding='utf-8') as f:
            report_content = f.read()
            
        return Response(report_content, mimetype='text/html')
    else:
        # Если отчет не найден, проверяем JSON-файл
        json_file = Path('lavsit_blockers_report.json')
        
        if json_file.exists():
            # Читаем JSON-данные
            with open(json_file, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
                
            # Генерируем HTML на основе JSON-данных
            sorted_blockers = sorted(report_data['blockers'], key=lambda x: x['count'], reverse=True)
            
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Отчет по блокерам покупки Lavsit.ru</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2 {{ color: #333; }}
        .blocker {{ margin-bottom: 20px; padding: 15px; border-left: 4px solid #3498db; background-color: #f8f9fa; }}
        .example {{ margin: 10px 0; padding: 10px; background-color: #f0f0f0; border-left: 2px solid #7f8c8d; }}
        .meta {{ color: #7f8c8d; font-size: 0.9em; }}
    </style>
</head>
<body>
    <h1>Отчет по блокерам покупки Lavsit.ru</h1>
    <p>Дата анализа: {report_data['analysis_date']}</p>
    <p>Всего сообщений клиентов: {report_data['total_messages']}</p>
    
    <h2>Блокеры покупки (по частоте упоминания)</h2>
"""
            
            for blocker in sorted_blockers:
                html_content += f"""
    <div class="blocker">
        <h3>{blocker['name']} ({blocker['count']} сообщений)</h3>
        <p>Оценка влияния: {blocker['score']}</p>
        <h4>Примеры сообщений:</h4>
"""
                
                for example in blocker['examples']:
                    html_content += f"""
        <div class="example">
            <p>"{example['text']}"</p>
            <p class="meta">Клиент: {example['name']}, Дата: {example['date']}</p>
        </div>
"""
                
                html_content += """
    </div>
"""
            
            html_content += """
    <div style="margin-top: 30px; padding: 15px; background-color: #e7f5fe; border-radius: 5px;">
        <h2>Выводы и рекомендации</h2>
        <ol>
            <li>Улучшить коммуникацию по срокам доставки и производства</li>
            <li>Добавить более подробные характеристики мебели на сайт</li>
            <li>Пересмотреть ценовую политику или более четко объяснять формирование цены</li>
            <li>Усилить информацию о гарантийном обслуживании</li>
            <li>Оптимизировать процесс производства или коммуникацию о сроках</li>
        </ol>
        <p>Для повышения конверсии на сайте Lavsit.ru рекомендуется провести следующие эксперименты:</p>
        <ol>
            <li><strong>Калькулятор сроков доставки</strong> - добавить на страницы товаров интерактивный калькулятор с актуальными сроками доставки и производства</li>
            <li><strong>Подробные характеристики дивана</strong> - добавить больше технических деталей и визуализаций размеров с возможностью сравнения с обычными предметами</li>
            <li><strong>Объяснение цены</strong> - добавить блок "Из чего складывается цена" с разбивкой стоимости по компонентам</li>
            <li><strong>Улучшенное описание гарантии</strong> - сделать раздел о гарантии и послепродажном обслуживании более заметным</li>
            <li><strong>Обновленная система уведомлений</strong> - реализовать автоматические уведомления о статусе производства и доставки</li>
        </ol>
    </div>
</body>
</html>"""
            
            return Response(html_content, mimetype='text/html')
        else:
            # Если нет ни HTML, ни JSON, возвращаем сообщение об ошибке
            return "<h1>Отчет не найден</h1><p>Отчет по блокерам покупки Lavsit.ru еще не создан. Запустите скрипт анализа для генерации отчета.</p>"

@reports_blueprint.route('/lavsit_report/data')
def lavsit_report_data():
    """
    Предоставляет данные отчета в формате JSON.
    
    Returns:
        JSON с данными отчета
    """
    json_file = Path('lavsit_blockers_report.json')
    
    if json_file.exists():
        with open(json_file, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
        return jsonify(report_data)
    else:
        return jsonify({"error": "Отчет не найден"}), 404

@reports_blueprint.route('/reports')
def list_reports():
    """
    Отображает список доступных отчетов.
    
    Returns:
        HTML-страница со списком отчетов
    """
    reports = []
    
    # Отчет по блокерам Lavsit
    if Path('lavsit_blockers_report.html').exists() or Path('lavsit_blockers_report.json').exists():
        last_modified = datetime.fromtimestamp(
            max(
                Path('lavsit_blockers_report.html').stat().st_mtime if Path('lavsit_blockers_report.html').exists() else 0,
                Path('lavsit_blockers_report.json').stat().st_mtime if Path('lavsit_blockers_report.json').exists() else 0
            )
        ).strftime('%Y-%m-%d %H:%M:%S')
        
        reports.append({
            'title': 'Анализ блокеров покупки Lavsit.ru',
            'description': 'Отчет по анализу блокеров покупки мебели Lavsit на основе данных Wazzup24',
            'url': '/reports/lavsit_report',
            'last_modified': last_modified
        })
    
    return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Аналитические отчеты</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1, h2 { color: #333; }
        .report-card {
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 15px;
            background-color: #f9f9f9;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .report-title {
            font-size: 1.2em;
            margin-bottom: 5px;
        }
        .report-meta {
            color: #777;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        .report-desc {
            margin-bottom: 10px;
        }
        .btn {
            display: inline-block;
            padding: 8px 16px;
            background-color: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 4px;
        }
        .btn:hover {
            background-color: #2980b9;
        }
    </style>
</head>
<body>
    <h1>Аналитические отчеты</h1>
    
    <div class="report-card">
        <div class="report-title">Анализ блокеров покупки Lavsit.ru</div>
        <div class="report-meta">Последнее обновление: 2025-05-19</div>
        <div class="report-desc">Отчет по анализу блокеров покупки мебели Lavsit на основе данных Wazzup24</div>
        <a href="/lavsit_report" class="btn">Просмотреть отчет</a>
    </div>
    
</body>
</html>
"""