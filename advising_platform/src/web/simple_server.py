import http.server
import socketserver
import mimetypes
import os
import signal
import sys
import traceback
import logging
import time
import json
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='web_server.log'
)
logger = logging.getLogger(__name__)

# Консольный обработчик для логов
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# Настройка типов MIME
mimetypes.init()
mimetypes.add_type('text/css', '.css')
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('image/svg+xml', '.svg')

# Порт для веб-сервера
PORT = 5000

class ImprovedHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Улучшенный обработчик HTTP-запросов с расширенной обработкой ошибок и MIME-типов."""
    
    # Увеличенный размер буфера для чтения запросов
    rbufsize = 1024000  # 1MB
    
    def log_message(self, format, *args):
        """Улучшенное логирование запросов"""
        logger.info("%s - - [%s] %s" % (self.client_address[0], self.log_date_time_string(), format % args))
    
    def log_error(self, format, *args):
        """Улучшенное логирование ошибок"""
        logger.error("%s - - [%s] %s" % (self.client_address[0], self.log_date_time_string(), format % args))
    
    def guess_type(self, path):
        """Определяем MIME-тип файла по расширению с улучшенной поддержкой статических файлов"""
        path_str = str(path)
        if path_str.endswith('.css'):
            return 'text/css'
        elif path_str.endswith('.js'):
            return 'application/javascript'
        elif path_str.endswith('.svg'):
            return 'image/svg+xml'
        return super().guess_type(path)
    
    def do_GET(self):
        """Улучшенная обработка GET-запросов с расширенной обработкой ошибок"""
        try:
            # Обработка запроса к корневому пути (главная страница)
            if self.path == '/' or self.path == '/index.html':
                logger.info(f"Обработка запроса к главной странице: {self.path}")
                
                try:
                    # Путь к файлу index.html в директории templates
                    current_dir = Path(__file__).parent
                    index_file = current_dir / 'templates' / 'index.html'
                    
                    if os.path.exists(index_file):
                        with open(index_file, 'rb') as f:
                            content = f.read()
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html; charset=utf-8')
                        self.send_header('Content-Length', str(len(content)))
                        self.end_headers()
                        self.wfile.write(content)
                        logger.info(f"Отправлена главная страница из {index_file}")
                        return
                    else:
                        logger.warning(f"Файл главной страницы не найден: {index_file}")
                        # Если index.html не найден, продолжаем стандартную обработку
                except Exception as e:
                    logger.error(f"Ошибка при отправке главной страницы: {str(e)}")
                    logger.error(traceback.format_exc())
                    self.send_error(500, f"Internal server error: {str(e)}")
                    return
            
            # Обработка запросов к директории static
            if self.path.startswith('/static/'):
                logger.info(f"Обработка запроса к статическому ресурсу: {self.path}")
                # Проверяем, существует ли файл
                file_path = self.translate_path(self.path)
                if not os.path.exists(file_path):
                    logger.warning(f"Файл не найден: {file_path}")
                    self.send_error(404, f"File not found: {self.path}")
                    return
                
                # Если это HTML-файл в static, отправляем его напрямую
                if file_path.endswith('.html') or file_path.endswith('.htm'):
                    try:
                        with open(file_path, 'rb') as f:
                            content = f.read()
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html; charset=utf-8')
                        self.send_header('Content-Length', str(len(content)))
                        self.end_headers()
                        self.wfile.write(content)
                        return
                    except Exception as e:
                        logger.error(f"Ошибка при отправке HTML-файла: {str(e)}")
                        self.send_error(500, f"Internal server error: {str(e)}")
                        return
            
            # Обработка запросов к документам (задачи, инциденты, гипотезы, стандарты)
            if self.path.startswith('/tasks/') or self.path.startswith('/incidents/') or self.path.startswith('/hypotheses/') or self.path.startswith('/standards/'):
                logger.info(f"Обработка запроса к документу: {self.path}")
                
                try:
                    # Разбираем URL для определения типа документа и его названия
                    parts = self.path.split('/')
                    if len(parts) >= 3:
                        doc_type = parts[1]  # tasks, incidents, hypotheses, standards
                        doc_title = parts[2]  # название документа
                        
                        # Заменяем дефисы на пробелы для поиска документа
                        doc_title = doc_title.replace('-', ' ')
                        
                        # В зависимости от типа документа, обращаемся к соответствующему файлу
                        if doc_type == 'tasks':
                            content = self.generate_task_view(doc_title)
                        elif doc_type == 'incidents':
                            content = self.generate_incident_view(doc_title)
                        elif doc_type == 'hypotheses':
                            content = self.generate_hypothesis_view(doc_title)
                        elif doc_type == 'standards':
                            content = self.generate_standard_view(doc_title)
                        else:
                            content = "<h1>Неподдерживаемый тип документа</h1>"
                            self.send_response(400)
                            self.send_header('Content-type', 'text/html; charset=utf-8')
                            self.send_header('Content-Length', str(len(content.encode('utf-8'))))
                            self.end_headers()
                            self.wfile.write(content.encode('utf-8'))
                            return
                        
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html; charset=utf-8')
                        self.send_header('Content-Length', str(len(content.encode('utf-8'))))
                        self.end_headers()
                        self.wfile.write(content.encode('utf-8'))
                        return
                    else:
                        content = "<h1>Некорректный URL</h1><p>URL должен содержать тип документа и его название.</p>"
                        self.send_response(400)
                        self.send_header('Content-type', 'text/html; charset=utf-8')
                        self.send_header('Content-Length', str(len(content.encode('utf-8'))))
                        self.end_headers()
                        self.wfile.write(content.encode('utf-8'))
                        return
                except Exception as e:
                    logger.error(f"Ошибка при обработке запроса к документу: {str(e)}")
                    logger.error(traceback.format_exc())
                    self.send_error(500, f"Internal server error: {str(e)}")
                    return
            
            # Обработка запросов к отчетам
            if self.path.startswith('/lavsit_report'):
                logger.info(f"Обработка запроса к отчету: {self.path}")
                
                try:
                    # Проверяем существование файла отчета
                    report_file = Path('lavsit_blockers_report.html')
                    
                    if report_file.exists():
                        with open(report_file, 'rb') as f:
                            content = f.read()
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html; charset=utf-8')
                        self.send_header('Content-Length', str(len(content)))
                        self.end_headers()
                        self.wfile.write(content)
                        return
                    else:
                        # Если отчет не найден, проверяем JSON-файл
                        json_file = Path('lavsit_blockers_report.json')
                        
                        if json_file.exists():
                            # Генерируем HTML на лету
                            try:
                                with open(json_file, 'r', encoding='utf-8') as f:
                                    report_data = json.load(f)
                                
                                # Генерируем простой HTML-отчет
                                html_content = self.generate_report_html(report_data)
                                
                                self.send_response(200)
                                self.send_header('Content-type', 'text/html; charset=utf-8')
                                self.send_header('Content-Length', str(len(html_content.encode('utf-8'))))
                                self.end_headers()
                                self.wfile.write(html_content.encode('utf-8'))
                                return
                            except Exception as e:
                                logger.error(f"Ошибка при генерации HTML-отчета: {str(e)}")
                                self.send_error(500, f"Internal server error: {str(e)}")
                                return
                        else:
                            # Если нет ни HTML, ни JSON, возвращаем сообщение об ошибке
                            content = "<h1>Отчет не найден</h1><p>Отчет по блокерам покупки Lavsit.ru еще не создан.</p>"
                            self.send_response(404)
                            self.send_header('Content-type', 'text/html; charset=utf-8')
                            self.send_header('Content-Length', str(len(content.encode('utf-8'))))
                            self.end_headers()
                            self.wfile.write(content.encode('utf-8'))
                            return
                except Exception as e:
                    logger.error(f"Ошибка при обработке запроса к отчету: {str(e)}")
                    self.send_error(500, f"Internal server error: {str(e)}")
                    return
            
            # Стандартная обработка для других запросов
            return super().do_GET()
        except Exception as e:
            # Расширенное логирование ошибок
            logger.error(f"Необработанная ошибка в do_GET: {str(e)}")
            logger.error(traceback.format_exc())
            self.send_error(500, f"Internal server error: {str(e)}")
            return
    
    def generate_task_view(self, task_title):
        """Генерирует HTML-страницу для просмотра задачи"""
        try:
            # Путь к файлу задач
            tasks_file = 'todo/tasks.md'
            
            if not os.path.exists(tasks_file):
                return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Задача не найдена</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2 {{ color: #333; }}
        .error {{ color: #e74c3c; }}
        .back-link {{ margin-top: 20px; }}
    </style>
</head>
<body>
    <h1 class="error">Задача не найдена</h1>
    <p>Файл задач не существует: {tasks_file}</p>
    <div class="back-link">
        <a href="/">← Вернуться на главную</a>
    </div>
</body>
</html>"""
            
            # Ищем задачу в файле
            task_content = ""
            found_task = False
            
            with open(tasks_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                i = 0
                while i < len(lines):
                    if lines[i].strip().startswith('## ') and task_title.lower() in lines[i].lower():
                        found_task = True
                        # Извлекаем содержимое задачи до следующего заголовка ## или до конца файла
                        task_content += lines[i]
                        i += 1
                        while i < len(lines) and not lines[i].strip().startswith('## '):
                            task_content += lines[i]
                            i += 1
                        break
                    i += 1
            
            if not found_task:
                return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Задача не найдена</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2 {{ color: #333; }}
        .error {{ color: #e74c3c; }}
        .back-link {{ margin-top: 20px; }}
    </style>
</head>
<body>
    <h1 class="error">Задача не найдена</h1>
    <p>Задача с названием "{task_title}" не найдена в файле {tasks_file}</p>
    <div class="back-link">
        <a href="/">← Вернуться на главную</a>
    </div>
</body>
</html>"""
            
            # Преобразуем Markdown в HTML
            import markdown
            html_content = markdown.markdown(task_content)
            
            return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Задача: {task_title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2 {{ color: #333; }}
        .task-content {{ margin-top: 20px; padding: 15px; border-left: 4px solid #3498db; background-color: #f8f9fa; }}
        .back-link {{ margin-top: 20px; }}
    </style>
</head>
<body>
    <h1>Задача: {task_title}</h1>
    <div class="task-content">
        {html_content}
    </div>
    <div class="back-link">
        <a href="/">← Вернуться на главную</a>
    </div>
</body>
</html>"""
        except Exception as e:
            logger.error(f"Ошибка при генерации страницы задачи: {str(e)}")
            logger.error(traceback.format_exc())
            return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Ошибка</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #e74c3c; }}
        .error-details {{ margin-top: 20px; padding: 15px; border-left: 4px solid #e74c3c; background-color: #f8f9fa; }}
        .back-link {{ margin-top: 20px; }}
    </style>
</head>
<body>
    <h1>Ошибка при загрузке задачи</h1>
    <div class="error-details">
        <p>Произошла ошибка при попытке загрузить задачу "{task_title}":</p>
        <code>{str(e)}</code>
    </div>
    <div class="back-link">
        <a href="/">← Вернуться на главную</a>
    </div>
</body>
</html>"""
    
    def generate_incident_view(self, incident_title):
        """Генерирует HTML-страницу для просмотра инцидента"""
        try:
            # Путь к файлу инцидентов
            incidents_file = 'incidents/incidents.md'
            
            if not os.path.exists(incidents_file):
                return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Инцидент не найден</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2 {{ color: #333; }}
        .error {{ color: #e74c3c; }}
        .back-link {{ margin-top: 20px; }}
    </style>
</head>
<body>
    <h1 class="error">Инцидент не найден</h1>
    <p>Файл инцидентов не существует: {incidents_file}</p>
    <div class="back-link">
        <a href="/">← Вернуться на главную</a>
    </div>
</body>
</html>"""
            
            # Ищем инцидент в файле
            incident_content = ""
            found_incident = False
            
            with open(incidents_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                i = 0
                while i < len(lines):
                    if lines[i].strip().startswith('## ') and incident_title.lower() in lines[i].lower():
                        found_incident = True
                        # Извлекаем содержимое инцидента до следующего заголовка ## или до конца файла
                        incident_content += lines[i]
                        i += 1
                        while i < len(lines) and not lines[i].strip().startswith('## '):
                            incident_content += lines[i]
                            i += 1
                        break
                    i += 1
            
            if not found_incident:
                return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Инцидент не найден</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2 {{ color: #333; }}
        .error {{ color: #e74c3c; }}
        .back-link {{ margin-top: 20px; }}
    </style>
</head>
<body>
    <h1 class="error">Инцидент не найден</h1>
    <p>Инцидент с названием "{incident_title}" не найден в файле {incidents_file}</p>
    <div class="back-link">
        <a href="/">← Вернуться на главную</a>
    </div>
</body>
</html>"""
            
            # Преобразуем Markdown в HTML
            import markdown
            html_content = markdown.markdown(incident_content)
            
            return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Инцидент: {incident_title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2 {{ color: #333; }}
        .incident-content {{ margin-top: 20px; padding: 15px; border-left: 4px solid #e74c3c; background-color: #f8f9fa; }}
        .back-link {{ margin-top: 20px; }}
    </style>
</head>
<body>
    <h1>Инцидент: {incident_title}</h1>
    <div class="incident-content">
        {html_content}
    </div>
    <div class="back-link">
        <a href="/">← Вернуться на главную</a>
    </div>
</body>
</html>"""
        except Exception as e:
            logger.error(f"Ошибка при генерации страницы инцидента: {str(e)}")
            logger.error(traceback.format_exc())
            return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Ошибка</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #e74c3c; }}
        .error-details {{ margin-top: 20px; padding: 15px; border-left: 4px solid #e74c3c; background-color: #f8f9fa; }}
        .back-link {{ margin-top: 20px; }}
    </style>
</head>
<body>
    <h1>Ошибка при загрузке инцидента</h1>
    <div class="error-details">
        <p>Произошла ошибка при попытке загрузить инцидент "{incident_title}":</p>
        <code>{str(e)}</code>
    </div>
    <div class="back-link">
        <a href="/">← Вернуться на главную</a>
    </div>
</body>
</html>"""
    
    def generate_hypothesis_view(self, hypothesis_title):
        """Генерирует HTML-страницу для просмотра гипотезы"""
        try:
            # Путь к файлу гипотез
            hypotheses_file = 'hypotheses/hypotheses.md'
            
            if not os.path.exists(hypotheses_file):
                return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Гипотеза не найдена</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2 {{ color: #333; }}
        .error {{ color: #e74c3c; }}
        .back-link {{ margin-top: 20px; }}
    </style>
</head>
<body>
    <h1 class="error">Гипотеза не найдена</h1>
    <p>Файл гипотез не существует: {hypotheses_file}</p>
    <div class="back-link">
        <a href="/">← Вернуться на главную</a>
    </div>
</body>
</html>"""
            
            # Ищем гипотезу в файле
            hypothesis_content = ""
            found_hypothesis = False
            
            with open(hypotheses_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                i = 0
                while i < len(lines):
                    if lines[i].strip().startswith('## ') and hypothesis_title.lower() in lines[i].lower():
                        found_hypothesis = True
                        # Извлекаем содержимое гипотезы до следующего заголовка ## или до конца файла
                        hypothesis_content += lines[i]
                        i += 1
                        while i < len(lines) and not lines[i].strip().startswith('## '):
                            hypothesis_content += lines[i]
                            i += 1
                        break
                    i += 1
            
            if not found_hypothesis:
                return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Гипотеза не найдена</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2 {{ color: #333; }}
        .error {{ color: #e74c3c; }}
        .back-link {{ margin-top: 20px; }}
    </style>
</head>
<body>
    <h1 class="error">Гипотеза не найдена</h1>
    <p>Гипотеза с названием "{hypothesis_title}" не найдена в файле {hypotheses_file}</p>
    <div class="back-link">
        <a href="/">← Вернуться на главную</a>
    </div>
</body>
</html>"""
            
            # Преобразуем Markdown в HTML
            import markdown
            html_content = markdown.markdown(hypothesis_content)
            
            return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Гипотеза: {hypothesis_title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2 {{ color: #333; }}
        .hypothesis-content {{ margin-top: 20px; padding: 15px; border-left: 4px solid #f39c12; background-color: #f8f9fa; }}
        .back-link {{ margin-top: 20px; }}
    </style>
</head>
<body>
    <h1>Гипотеза: {hypothesis_title}</h1>
    <div class="hypothesis-content">
        {html_content}
    </div>
    <div class="back-link">
        <a href="/">← Вернуться на главную</a>
    </div>
</body>
</html>"""
        except Exception as e:
            logger.error(f"Ошибка при генерации страницы гипотезы: {str(e)}")
            logger.error(traceback.format_exc())
            return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Ошибка</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #e74c3c; }}
        .error-details {{ margin-top: 20px; padding: 15px; border-left: 4px solid #e74c3c; background-color: #f8f9fa; }}
        .back-link {{ margin-top: 20px; }}
    </style>
</head>
<body>
    <h1>Ошибка при загрузке гипотезы</h1>
    <div class="error-details">
        <p>Произошла ошибка при попытке загрузить гипотезу "{hypothesis_title}":</p>
        <code>{str(e)}</code>
    </div>
    <div class="back-link">
        <a href="/">← Вернуться на главную</a>
    </div>
</body>
</html>"""
    
    def generate_standard_view(self, standard_title):
        """Генерирует HTML-страницу для просмотра стандарта"""
        try:
            # Путь к файлу стандартов
            standards_file = 'standards/standards.md'
            
            if not os.path.exists(standards_file):
                return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Стандарт не найден</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2 {{ color: #333; }}
        .error {{ color: #e74c3c; }}
        .back-link {{ margin-top: 20px; }}
    </style>
</head>
<body>
    <h1 class="error">Стандарт не найден</h1>
    <p>Файл стандартов не существует: {standards_file}</p>
    <div class="back-link">
        <a href="/">← Вернуться на главную</a>
    </div>
</body>
</html>"""
            
            # Ищем стандарт в файле
            standard_content = ""
            found_standard = False
            
            with open(standards_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                i = 0
                while i < len(lines):
                    if lines[i].strip().startswith('## ') and standard_title.lower() in lines[i].lower():
                        found_standard = True
                        # Извлекаем содержимое стандарта до следующего заголовка ## или до конца файла
                        standard_content += lines[i]
                        i += 1
                        while i < len(lines) and not lines[i].strip().startswith('## '):
                            standard_content += lines[i]
                            i += 1
                        break
                    i += 1
            
            if not found_standard:
                return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Стандарт не найден</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2 {{ color: #333; }}
        .error {{ color: #e74c3c; }}
        .back-link {{ margin-top: 20px; }}
    </style>
</head>
<body>
    <h1 class="error">Стандарт не найден</h1>
    <p>Стандарт с названием "{standard_title}" не найден в файле {standards_file}</p>
    <div class="back-link">
        <a href="/">← Вернуться на главную</a>
    </div>
</body>
</html>"""
            
            # Преобразуем Markdown в HTML
            import markdown
            html_content = markdown.markdown(standard_content)
            
            return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Стандарт: {standard_title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2 {{ color: #333; }}
        .standard-content {{ margin-top: 20px; padding: 15px; border-left: 4px solid #27ae60; background-color: #f8f9fa; }}
        .back-link {{ margin-top: 20px; }}
    </style>
</head>
<body>
    <h1>Стандарт: {standard_title}</h1>
    <div class="standard-content">
        {html_content}
    </div>
    <div class="back-link">
        <a href="/">← Вернуться на главную</a>
    </div>
</body>
</html>"""
        except Exception as e:
            logger.error(f"Ошибка при генерации страницы стандарта: {str(e)}")
            logger.error(traceback.format_exc())
            return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Ошибка</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #e74c3c; }}
        .error-details {{ margin-top: 20px; padding: 15px; border-left: 4px solid #e74c3c; background-color: #f8f9fa; }}
        .back-link {{ margin-top: 20px; }}
    </style>
</head>
<body>
    <h1>Ошибка при загрузке стандарта</h1>
    <div class="error-details">
        <p>Произошла ошибка при попытке загрузить стандарт "{standard_title}":</p>
        <code>{str(e)}</code>
    </div>
    <div class="back-link">
        <a href="/">← Вернуться на главную</a>
    </div>
</body>
</html>"""
    
    def generate_report_html(self, report_data):
        """Генерирует HTML-отчет на основе данных из JSON"""
        # Сортируем блокеры по количеству сообщений
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
        
        return html_content

def signal_handler(sig, frame):
    """Обработчик сигналов для корректного завершения работы"""
    logger.info("Получен сигнал завершения, останавливаем сервер...")
    sys.exit(0)

def clear_server_cache():
    """Очищает кэш сервера для обеспечения актуальности файлов"""
    # Сбрасываем внутренний кэш SimpleHTTPRequestHandler
    if hasattr(http.server.SimpleHTTPRequestHandler, '_cacheable_paths'):
        http.server.SimpleHTTPRequestHandler._cacheable_paths.clear()
    logger.info("Кэш сервера очищен")

class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Многопоточный HTTP-сервер с расширенной обработкой ошибок"""
    
    # Позволяет быстро перезапускать сервер на том же порту
    allow_reuse_address = True
    
    # Таймаут для обработки запросов
    timeout = 60
    
    # Размер очереди запросов
    request_queue_size = 20

def start_server(port=PORT):
    """Запускает веб-сервер на указанном порту с расширенной обработкой ошибок"""
    try:
        # Регистрируем обработчик сигналов
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Создаем экземпляр сервера
        server = ThreadedHTTPServer(("0.0.0.0", port), ImprovedHTTPRequestHandler)
        
        # Выводим информацию о запуске
        print(f"Веб-сервер запущен на порту {port} (0.0.0.0), PID: {os.getpid()}")
        logger.info(f"Веб-сервер запущен на порту {port} (0.0.0.0), PID: {os.getpid()}")
        
        # Запускаем сервер
        server.serve_forever()
    except OSError as e:
        if e.errno == 98:  # Address already in use
            logger.error(f"Порт {port} уже используется другим процессом")
            print(f"Порт {port} уже используется другим процессом")
            # Пробуем запустить на другом порту
            alternative_port = port + 1
            logger.info(f"Пробуем запустить на порту {alternative_port}...")
            print(f"Пробуем запустить на порту {alternative_port}...")
            time.sleep(1)
            start_server(alternative_port)
        else:
            logger.error(f"Ошибка запуска сервера: {str(e)}")
            print(f"Ошибка запуска сервера: {str(e)}")
    except Exception as e:
        logger.error(f"Необработанная ошибка: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"Необработанная ошибка: {str(e)}")

if __name__ == "__main__":
    print("Запуск веб-сервера...")
    start_server()