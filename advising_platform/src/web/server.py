import http.server
import socketserver
import mimetypes
import socket
import os
import signal
import sys
import shutil
import logging
import json
import re
from urllib.parse import urlparse, parse_qs, unquote

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("web_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("web_server")

# Добавляем правильные MIME-типы с кодировкой UTF-8
mimetypes.add_type('text/markdown; charset=utf-8', '.md')
mimetypes.add_type('text/html; charset=utf-8', '.html')
mimetypes.add_type('text/css; charset=utf-8', '.css')
mimetypes.add_type('application/javascript; charset=utf-8', '.js')

# Путь к файлу визуализации
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
VISUALIZATION_FILE = os.path.join(ROOT_DIR, 'relation_visualization.html')
STATIC_VISUALIZATION_FILE = os.path.join(STATIC_DIR, 'relation_visualization.html')

# Создаем директории, если не существуют
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, 'css'), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, 'js'), exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# Копируем файл визуализации в статическую директорию
if os.path.exists(VISUALIZATION_FILE):
    try:
        shutil.copy2(VISUALIZATION_FILE, STATIC_VISUALIZATION_FILE)
        logger.info(f"Файл визуализации скопирован в {STATIC_VISUALIZATION_FILE}")
    except Exception as e:
        logger.error(f"Ошибка при копировании файла визуализации: {e}")

# Импортируем обработчики маршрутов для документов
try:
    from advising_platform.src.web.document_routes import DocumentRouteHandler
    HAS_DOCUMENT_ROUTES = True
    logger.info("Модуль обработки документов успешно импортирован")
except ImportError as e:
    logger.warning(f"Не удалось импортировать модуль document_routes: {e}")
    HAS_DOCUMENT_ROUTES = False

# Импортируем шаблонизатор
try:
    from advising_platform.src.web.template_engine import render_template
    HAS_TEMPLATING = True
    logger.info("Шаблонизатор успешно импортирован")
except ImportError:
    logger.warning("Не удалось импортировать шаблонизатор, будет использован базовый режим")
    HAS_TEMPLATING = False

# Импортируем обработчики маршрутов для статистики задач
try:
    from advising_platform.src.tools.task.task_statistics import TaskStatisticsManager
    from datetime import datetime
    HAS_TASK_STATS = True
    task_stats_manager = TaskStatisticsManager()
    logger.info("Модуль статистики задач успешно импортирован")
except ImportError as e:
    logger.warning(f"Не удалось импортировать модуль task_statistics: {e}")
    HAS_TASK_STATS = False

# Простой шаблонизатор для базового режима
def simple_render_template(template_name, context=None):
    """Простой шаблонизатор для базового режима."""
    if context is None:
        context = {}
    
    template_path = os.path.join(TEMPLATES_DIR, template_name)
    if not os.path.exists(template_path):
        return f"Шаблон {template_name} не найден"
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Простая замена переменных
    for key, value in context.items():
        template = template.replace('{{ ' + key + ' }}', str(value))
    
    return template

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def guess_type(self, path):
        """Определяем MIME-тип файла по расширению"""
        if str(path).endswith('.md'):
            return 'text/markdown; charset=utf-8'
        elif str(path).endswith('.html'):
            return 'text/html; charset=utf-8'
        elif str(path).endswith('.css'):
            return 'text/css; charset=utf-8'
        elif str(path).endswith('.js'):
            return 'application/javascript; charset=utf-8'
        return super().guess_type(path)
    
    def handle_task_stats(self):
        """Обрабатывает запрос к странице статистики задач."""
        logger.info("Обработка запроса к странице статистики задач")
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        if not HAS_TASK_STATS or not HAS_TEMPLATING:
            # Если модуль статистики задач недоступен, выводим заглушку
            output = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Статистика задач</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 40px; line-height: 1.6; }
                    h1 { color: #333; }
                    .container { max-width: 800px; margin: 0 auto; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Статистика задач</h1>
                    <p>Модуль статистики задач недоступен.</p>
                    <p><a href="/">На главную</a></p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(output.encode('utf-8'))
            return True
        
        try:
            # Получаем статистику задач
            stats = task_stats_manager.get_statistics_summary()
            
            # Форматируем данные для отображения
            formatted_stats = {
                'total': stats['total_tasks'],
                'completed': stats['completed_tasks'],
                'in_progress': stats['pending_tasks'],
                'completion_rate': round(stats['completion_rate'], 1),
                'categories': {},
                'recently_completed': stats['recently_completed'][:5]  # Только 5 последних
            }
            
            # Форматируем данные категорий
            for category, data in stats['categories'].items():
                formatted_stats['categories'][category] = {
                    'total': data['total'],
                    'completed': data['completed'],
                    'pending': data['pending']
                }
            
            # Получаем список задач из todo.md
            tasks = []
            task_id = 1
            
            with open(task_stats_manager.todo_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
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
            
            # Рендерим шаблон
            output = render_template(
                'task_stats.html',
                {
                    'stats': formatted_stats,
                    'tasks': tasks,
                    'date': datetime.now().strftime("%d.%m.%Y")
                }
            )
            
            self.wfile.write(output.encode('utf-8'))
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при обработке запроса к странице статистики задач: {e}")
            self.send_error_response(500, f"Произошла ошибка при обработке запроса: {e}")
            return False
    
    def send_error_response(self, status_code, message):
        """Отправляет ответ с ошибкой."""
        self.send_response(status_code)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Ошибка {status_code}</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 40px; line-height: 1.6; }}
                h1 {{ color: #c00; }}
                .error-container {{ max-width: 600px; margin: 0 auto; }}
            </style>
        </head>
        <body>
            <div class="error-container">
                <h1>Ошибка {status_code}</h1>
                <p>{message}</p>
                <p><a href="/">На главную</a></p>
            </div>
        </body>
        </html>
        """
        
        self.wfile.write(error_html.encode('utf-8'))
    
    def do_GET(self):
        """Обработка GET-запросов с маршрутизацией"""
        logger.info(f"Обработка запроса: {self.path}")
        
        # Парсим URL для извлечения параметров
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        # Проверяем статические файлы
        if path.startswith('/static/'):
            file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path[1:])
            if os.path.exists(file_path):
                self.path = path
                return http.server.SimpleHTTPRequestHandler.do_GET(self)
        
        # Маршрутизация
        if path == '/':
            self.path = '/index.html'
            logger.info("Отправка главной страницы из advising_platform/src/web/templates/index.html")
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        
        elif path == '/visualization':
            # Перенаправляем на файл визуализации
            self.path = '/static/relation_visualization.html'
            logger.info("Отправка страницы визуализации")
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
            
        elif path == '/tasks/stats':
            # Обработка запроса к странице статистики задач
            return self.handle_task_stats()
        
        # Маршруты для документов
        elif HAS_DOCUMENT_ROUTES:
            # Список документов
            if path == '/documents':
                return DocumentRouteHandler.handle_documents_list(self)
            
            # Просмотр документа
            elif path == '/document':
                document_path = query_params.get('path', [''])[0]
                if document_path:
                    return DocumentRouteHandler.handle_document_view(self, document_path)
                else:
                    return self.send_error_response(400, "Не указан путь к документу")
            
            # Редактирование документа
            elif path == '/edit':
                document_path = query_params.get('path', [''])[0]
                if document_path:
                    return DocumentRouteHandler.handle_document_edit(self, document_path)
                else:
                    return self.send_error_response(400, "Не указан путь к документу")
            
            # Создание документа
            elif path == '/create':
                document_type = query_params.get('type', ['task'])[0]
                return DocumentRouteHandler.handle_document_create(self, document_type)
            
            # API для проверки синхронизации документа
            elif path.startswith('/api/documents/check-sync'):
                document_path = query_params.get('path', [''])[0]
                if document_path:
                    return DocumentRouteHandler.handle_api_document_check_sync(self, document_path)
                else:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {"success": False, "error": "Не указан путь к документу"}
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                    return True
        
        # Если маршрут не найден, проверяем, существует ли файл
        file_path = os.path.join(TEMPLATES_DIR, path.lstrip('/'))
        if os.path.exists(file_path):
            self.path = os.path.join('/templates', path.lstrip('/'))
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        
        # В случае, если ничего не подошло, возвращаем 404
        return self.send_error_response(404, "Страница не найдена")
    
    def do_POST(self):
        """Обработка POST-запросов"""
        logger.info(f"Обработка POST-запроса: {self.path}")
        
        if HAS_DOCUMENT_ROUTES:
            # API для создания документа
            if self.path == '/api/documents/create':
                return DocumentRouteHandler.handle_api_document_create(self)
            
            # API для обновления документа
            elif self.path == '/api/documents/update':
                return DocumentRouteHandler.handle_api_document_update(self)
            
            # API для архивации документа
            elif self.path == '/api/documents/archive':
                return DocumentRouteHandler.handle_api_document_archive(self)
            
            # API для добавления комментария
            elif self.path == '/api/comments/add':
                return DocumentRouteHandler.handle_api_add_comment(self)
        
        # Если маршрут не найден, возвращаем 404
        self.send_error_response(404, "API-метод не найден")

# Запускаем сервер на порту 5000
PORT = 5000
Handler = CustomHTTPRequestHandler

# Создаем простой шаблон для главной страницы, если его нет
index_html_path = os.path.join(TEMPLATES_DIR, 'index.html')
if not os.path.exists(index_html_path):
    os.makedirs(os.path.dirname(index_html_path), exist_ok=True)
    with open(index_html_path, 'w', encoding='utf-8') as f:
        f.write("""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advising Diagnostics</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fira+Sans:wght@400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/static/css/medium-style.css">
</head>
<body>
    <header class="site-header">
        <div class="container header-container">
            <div class="logo-container">
                <a href="/" class="logo">Advising Diagnostics</a>
            </div>
            <nav class="main-nav">
                <a href="/visualization" class="nav-link">Визуализация</a>
                <a href="/documents" class="nav-link">Документы</a>
                <a href="/tasks/stats" class="nav-link">Статистика задач</a>
            </nav>
        </div>
    </header>

    <main class="container">
        <h1>Добро пожаловать в Advising Diagnostics</h1>
        
        <div class="section">
            <h2>Доступные функции</h2>
            
            <div class="actions-grid">
                <a href="/documents" class="action-item">
                    <h3>Документы</h3>
                    <p>Просмотр и редактирование документов проекта</p>
                </a>
                
                <a href="/visualization" class="action-item">
                    <h3>Визуализация</h3>
                    <p>Визуализация связей между рабочими элементами</p>
                </a>
                
                <a href="/tasks/stats" class="action-item">
                    <h3>Статистика задач</h3>
                    <p>Отслеживание прогресса и статистика по задачам</p>
                </a>
                
                <a href="/document?path=lavsit_customer_inquiry_analysis.md" class="action-item">
                    <h3>Анализ запросов клиентов</h3>
                    <p>Результаты анализа запросов клиентов Lavsit</p>
                </a>
            </div>
        </div>
    </main>

    <footer class="site-footer">
        <div class="container">
            <p>&copy; 2025 Advising Diagnostics. Все права защищены.</p>
        </div>
    </footer>
</body>
</html>""")
    logger.info(f"Создан базовый шаблон главной страницы: {index_html_path}")

# Обработка корректного завершения
def signal_handler(sig, frame):
    logger.info('Завершение работы сервера...')
    try:
        if httpd:
            httpd.server_close()
    except:
        pass
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Запускаем сервер
try:
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("0.0.0.0", PORT), Handler)
    logger.info(f"Веб-сервер запущен на порту {PORT} (0.0.0.0), PID: {os.getpid()}")
    print(f"Веб-сервер запущен на порту {PORT} (0.0.0.0), PID: {os.getpid()}")
    httpd.serve_forever()
except OSError as e:
    if e.errno == 98:  # Address already in use
        logger.warning(f"Порт {PORT} уже используется. Пытаемся использовать другой порт.")
        print(f"Port {PORT} is already in use. Attempting to use a different port.")
        # Попробуем найти свободный порт
        for alt_port in range(5001, 5010):
            try:
                httpd = socketserver.TCPServer(("0.0.0.0", alt_port), Handler)
                logger.info(f"Используем альтернативный порт {alt_port}")
                print(f"Using alternative port {alt_port}")
                httpd.serve_forever()
                break
            except OSError:
                continue
        else:
            logger.error("Не удалось найти свободный порт. Пожалуйста, освободите порт 5000 и попробуйте снова.")
            print("Could not find an available port. Please free port 5000 and try again.")
            sys.exit(1)
    else:
        logger.error(f"Ошибка запуска сервера: {e}")
        print(f"Error starting server: {e}")
        sys.exit(1)
