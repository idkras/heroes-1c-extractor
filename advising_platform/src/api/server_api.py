#!/usr/bin/env python3
"""
Сервер API для доступа к стандартам, проектам и инцидентам.
Позволяет получать списки стандартов и проектов, их содержимое, а также управлять инцидентами.
Включает полную поддержку CRUD для системы управления инцидентами с автоматическим анализом
корневых причин и замкнутым циклом обратной связи.
"""

import http.server
import socketserver
import mimetypes
import socket
import os
import signal
import sys
import json
import re
import urllib.parse
import logging
from datetime import datetime
from functools import wraps

# Настройка путей импорта для доступа к модулям проекта
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)
scripts_path = os.path.join(project_root, 'scripts')
sys.path.append(scripts_path)
document_tools_path = os.path.join(scripts_path, 'document_tools')
sys.path.append(document_tools_path)

# Импортируем модуль для API инцидентов
try:
    # Пробуем разные варианты импорта
    try:
        from advising_platform.advising_platform.src.api.incidents_api import register_incidents_api
    except ImportError:
        from api.incidents_api import register_incidents_api
    HAS_INCIDENTS_API = True
except ImportError:
    print("Не удалось импортировать модуль incidents_api, API инцидентов будет недоступно")
    HAS_INCIDENTS_API = False

# Импортируем наш модуль для работы с абстрактными идентификаторами
try:
    from scripts.document_tools.document_abstractions import DocumentRegistry
    HAS_DOCUMENT_REGISTRY = True
except ImportError:
    print("Не удалось импортировать модуль document_abstractions, функции логических идентификаторов будут недоступны")
    HAS_DOCUMENT_REGISTRY = False

# Импортируем наш модуль in-memory индексатора
try:
    from advising_platform.advising_platform.src.core.inmemory_indexer import InMemoryIndexer, indexer as inmemory_indexer
    from advising_platform.advising_platform.src.api.inmemory_api import inmemory_api, register_blueprint
    HAS_INMEMORY_INDEXER = True
    print("Модуль in-memory индексатора успешно загружен")
except ImportError as e:
    print(f"Не удалось импортировать модуль in-memory индексатора: {e}")
    HAS_INMEMORY_INDEXER = False

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('api_server')

# Попытка импорта модуля отслеживания прогресса
try:
    from scripts.progress_tracker import (
        get_system_status, 
        track_standard_action, 
        track_project_action, 
        track_api_action, 
        track_git_action,
        ProgressTracker
    )
    HAS_PROGRESS_TRACKER = True
except ImportError:
    print("Не удалось импортировать модуль отслеживания прогресса, эта функциональность будет недоступна")
    HAS_PROGRESS_TRACKER = False

# Добавляем правильные MIME-типы с кодировкой UTF-8
mimetypes.add_type('text/markdown; charset=utf-8', '.md')
mimetypes.add_type('text/html; charset=utf-8', '.html')
mimetypes.add_type('text/css; charset=utf-8', '.css')
mimetypes.add_type('application/javascript; charset=utf-8', '.js')
mimetypes.add_type('application/json; charset=utf-8', '.json')

# Ключи API для авторизации запросов
API_KEYS = {
    "default": "advising-diagnostics-api-key",
    # Добавьте дополнительные ключи по необходимости
}

# Директории с контентом
STANDARDS_DIR = "advising standards .md"  # Корректный путь с учетом пробелов и точки
PROJECTS_DIR = "projects"

class APIError(Exception):
    """Класс для ошибок API с кодом HTTP-статуса и сообщением."""
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)

def require_api_key(func):
    """Декоратор для проверки API-ключа в запросах."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # Получаем API-ключ из заголовка или query-параметра
        api_key = self.headers.get('X-API-Key')
        
        if not api_key:
            # Проверяем query-параметры
            query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            api_key = query_components.get('api_key', [None])[0]
        
        # Временно отключаем проверку API-ключа для тестирования
        # if api_key not in API_KEYS.values():
        #    self.send_error(401, "Unauthorized - Invalid API Key")
        #    return None
        
        return func(self, *args, **kwargs)
    return wrapper

class APIHandler(http.server.SimpleHTTPRequestHandler):
    """Обработчик HTTP-запросов с поддержкой API."""
    
    # Инициализация реестра документов (если доступен)
    document_registry = None
    if HAS_DOCUMENT_REGISTRY:
        try:
            document_registry = DocumentRegistry()
        except Exception as e:
            print(f"Ошибка при инициализации реестра документов: {e}")
            HAS_DOCUMENT_REGISTRY = False
    
    def guess_type(self, path):
        """Определяем MIME-тип файла по расширению."""
        if str(path).endswith('.md'):
            return 'text/markdown; charset=utf-8'
        elif str(path).endswith('.html'):
            return 'text/html; charset=utf-8'
        elif str(path).endswith('.css'):
            return 'text/css; charset=utf-8'
        elif str(path).endswith('.js'):
            return 'application/javascript; charset=utf-8'
        elif str(path).endswith('.json'):
            return 'application/json; charset=utf-8'
        return super().guess_type(path)
    
    def send_json_response(self, data, status=200):
        """Отправляет JSON-ответ с указанным статусом."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')  # CORS для всех источников
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
    
    def extract_metadata_from_md(self, file_path):
        """Извлекает метаданные из markdown файла."""
        metadata = {
            "path": file_path,
            "filename": os.path.basename(file_path),
            "last_modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
            "title": "",
            "category": "",
            "tags": []
        }
        
        # Определяем категорию на основе директории
        if STANDARDS_DIR in file_path:
            metadata["category"] = "standard"
            # Определяем тип стандарта
            filename = os.path.basename(file_path).lower()
            if "task master" in filename:
                metadata["type"] = "task_master"
            elif "process" in filename:
                metadata["type"] = "process"
            elif "context" in filename:
                metadata["type"] = "client_context"
            elif "hypo" in filename:
                metadata["type"] = "hypothesis"
            elif "diagnostic" in filename:
                metadata["type"] = "diagnostic"
            else:
                metadata["type"] = "other"
        elif PROJECTS_DIR in file_path:
            metadata["category"] = "project"
            # Определяем проект
            parts = file_path.split(os.path.sep)
            if len(parts) > 1:
                metadata["project"] = parts[parts.index(PROJECTS_DIR) + 1]
            
            # Определяем тип проектного документа
            filename = os.path.basename(file_path).lower()
            if "context" in filename:
                metadata["type"] = "context"
            elif "diagnostic" in filename:
                metadata["type"] = "diagnostic"
            elif "hypothis" in filename or "гипотез" in filename:
                metadata["type"] = "hypothesis"
            elif "step" in filename:
                metadata["type"] = "steps"
            else:
                metadata["type"] = "other"
        
        # Извлекаем заголовок из содержимого
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Ищем первый заголовок в формате Markdown
                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                if title_match:
                    metadata["title"] = title_match.group(1).strip()
                
                # Извлекаем теги (если они существуют в формате #тег)
                tag_matches = re.findall(r'#(\w+)', content)
                metadata["tags"] = list(set(tag_matches))  # Убираем дубликаты
        except Exception as e:
            print(f"Ошибка при извлечении метаданных из {file_path}: {e}")
        
        return metadata
    
    def list_markdown_files(self, directory, recursive=True):
        """Возвращает список markdown файлов в указанной директории."""
        markdown_files = []
        
        for root, dirs, files in os.walk(directory):
            if not recursive and root != directory:
                continue
            
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    metadata = self.extract_metadata_from_md(file_path)
                    markdown_files.append(metadata)
        
        return markdown_files
    
    @require_api_key
    def handle_api_standards(self):
        """Обрабатывает запрос на получение списка стандартов."""
        try:
            standards = self.list_markdown_files(STANDARDS_DIR)
            return self.send_json_response({"standards": standards})
        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)
    
    @require_api_key
    def handle_api_projects(self):
        """Обрабатывает запрос на получение списка проектов."""
        try:
            # Получаем список директорий проектов
            projects = []
            for item in os.listdir(PROJECTS_DIR):
                item_path = os.path.join(PROJECTS_DIR, item)
                if os.path.isdir(item_path):
                    project = {
                        "name": item,
                        "path": item_path,
                        "files": self.list_markdown_files(item_path)
                    }
                    projects.append(project)
            
            return self.send_json_response({"projects": projects})
        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)
    
    @require_api_key
    def handle_api_file_content(self, file_path):
        """Обрабатывает запрос на получение содержимого файла."""
        try:
            # Проверяем, существует ли файл
            if not os.path.exists(file_path) or not os.path.isfile(file_path):
                return self.send_json_response({"error": "File not found"}, 404)
            
            # Проверяем, что это markdown файл
            if not file_path.endswith('.md'):
                return self.send_json_response({"error": "Only markdown files are supported"}, 400)
            
            # Получаем метаданные и содержимое
            metadata = self.extract_metadata_from_md(file_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.send_json_response({
                "metadata": metadata,
                "content": content
            })
        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)
    
    @require_api_key
    def handle_api_abstract_doc(self, identifier):
        """Обрабатывает запрос на получение документа по логическому идентификатору."""
        if not HAS_DOCUMENT_REGISTRY or not self.document_registry:
            return self.send_json_response({
                "error": "Document registry functionality is not available"
            }, 500)
        
        try:
            # Получаем документ по логическому идентификатору
            metadata = self.document_registry.get_document(identifier)
            if not metadata:
                return self.send_json_response({
                    "error": f"Document with identifier '{identifier}' not found"
                }, 404)
            
            # Получаем содержимое документа
            with open(metadata.path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Преобразуем метаданные в словарь
            metadata_dict = metadata.to_dict()
            
            return self.send_json_response({
                "identifier": identifier,
                "metadata": metadata_dict,
                "content": content
            })
        except Exception as e:
            return self.send_json_response({
                "error": f"Error retrieving document: {str(e)}"
            }, 500)
    
    @require_api_key
    def handle_api_abstract_list(self, doc_type=None):
        """Обрабатывает запрос на получение списка логических идентификаторов."""
        if not HAS_DOCUMENT_REGISTRY or not self.document_registry:
            return self.send_json_response({
                "error": "Document registry functionality is not available"
            }, 500)
        
        try:
            # Формируем список идентификаторов
            identifiers = []
            
            for identifier, metadata in self.document_registry.id_mapping.items():
                # Фильтруем по типу, если указан
                if doc_type and not identifier.startswith(f"{doc_type}:"):
                    continue
                
                identifiers.append({
                    "identifier": identifier,
                    "title": metadata.title or os.path.basename(metadata.path),
                    "date": metadata.date,
                    "author": metadata.author,
                    "path": metadata.path
                })
            
            return self.send_json_response({
                "identifiers": identifiers
            })
        except Exception as e:
            return self.send_json_response({
                "error": f"Error listing identifiers: {str(e)}"
            }, 500)
    
    @require_api_key
    def handle_api_convert_links(self, file_path, to_abstract=True):
        """Обрабатывает запрос на преобразование ссылок в документе."""
        if not HAS_DOCUMENT_REGISTRY or not self.document_registry:
            return self.send_json_response({
                "error": "Document registry functionality is not available"
            }, 500)
        
        try:
            # Проверяем, существует ли файл
            if not os.path.exists(file_path) or not os.path.isfile(file_path):
                return self.send_json_response({
                    "error": "File not found"
                }, 404)
            
            # Выполняем преобразование
            result = self.document_registry.update_document_links(file_path, to_abstract)
            
            if result:
                return self.send_json_response({
                    "message": f"Successfully converted links in '{file_path}'",
                    "to_abstract": to_abstract
                })
            else:
                return self.send_json_response({
                    "error": "Failed to convert links"
                }, 500)
        except Exception as e:
            return self.send_json_response({
                "error": f"Error converting links: {str(e)}"
            }, 500)
    
    @require_api_key
    def handle_api_search(self, query, filters=None):
        """Обрабатывает запрос на поиск по содержимому файлов с расширенной фильтрацией."""
        try:
            # Получаем параметры запроса
            query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            query = query.lower()
            
            # Параметры фильтрации
            filters = {
                'type': query_components.get('type', [None])[0],  # тип стандарта: task_master, process, client_context и т.д.
                'author': query_components.get('author', [None])[0],  # автор документа
                'after_date': query_components.get('after_date', [None])[0],  # только документы после указанной даты
                'before_date': query_components.get('before_date', [None])[0],  # только документы до указанной даты
                'include_archived': query_components.get('include_archived', ['false'])[0].lower() == 'true',  # включать ли архивные документы
                'exact_match': query_components.get('exact_match', ['false'])[0].lower() == 'true',  # точное совпадение фразы
                'search_content': query_components.get('search_content', ['true'])[0].lower() == 'true'  # искать в содержимом или только в метаданных
            }
            
            # Получаем список файлов
            standards = self.list_markdown_files(STANDARDS_DIR)
            projects_files = self.list_markdown_files(PROJECTS_DIR)
            
            # Объединяем файлы
            all_files = standards + projects_files
            results = []
            
            # Фильтруем архивные документы, если указано
            if not filters['include_archived']:
                all_files = [f for f in all_files if "archive AI never use" not in f["path"]]
            
            # Фильтруем по типу, если указан
            if filters['type']:
                all_files = [f for f in all_files if f.get("type") == filters['type']]
            
            # Фильтруем по автору, если указан 
            if filters['author']:
                author_query = filters['author'].lower()
                all_files = [f for f in all_files if author_query in f.get("filename", "").lower()]
            
            # Фильтруем по датам (в имени файла)
            if filters['after_date']:
                try:
                    after_date = filters['after_date']
                    all_files = [f for f in all_files if after_date in f.get("filename", "") 
                                if datetime.strptime(after_date, "%d %b %Y") <= 
                                datetime.strptime(f.get("filename", "").split("by ")[-2].strip(), "%d %b %Y")]
                except Exception as e:
                    print(f"Ошибка при фильтрации по дате: {e}")
            
            if filters['before_date']:
                try:
                    before_date = filters['before_date']
                    all_files = [f for f in all_files if before_date in f.get("filename", "")
                                if datetime.strptime(before_date, "%d %b %Y") >= 
                                datetime.strptime(f.get("filename", "").split("by ")[-2].strip(), "%d %b %Y")]
                except Exception as e:
                    print(f"Ошибка при фильтрации по дате: {e}")
            
            # Поиск по содержимому
            if not query:
                # Если запрос пустой, возвращаем все отфильтрованные файлы
                results = all_files
            else:
                # Поиск по метаданным и/или содержимому
                for file_info in all_files:
                    file_path = file_info["path"]
                    added = False
                    
                    # Проверяем метаданные
                    if ((filters['exact_match'] and query == file_info["title"].lower()) or
                        (not filters['exact_match'] and query in file_info["title"].lower()) or
                        (filters['exact_match'] and query == file_info["filename"].lower()) or
                        (not filters['exact_match'] and query in file_info["filename"].lower()) or
                        any((filters['exact_match'] and query == tag.lower()) or
                            (not filters['exact_match'] and query in tag.lower()) for tag in file_info["tags"])):
                        file_info["match_type"] = "metadata"
                        results.append(file_info)
                        added = True
                        continue
                    
                    # Проверяем содержимое, если включен соответствующий параметр
                    if filters['search_content'] and not added:
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read().lower()
                                
                                # Поиск с учетом параметра exact_match
                                if (filters['exact_match'] and query in content.split()) or \
                                   (not filters['exact_match'] and query in content):
                                    # Находим все вхождения запроса
                                    all_matches = []
                                    start_pos = 0
                                    while True:
                                        pos = content.find(query, start_pos)
                                        if pos == -1:
                                            break
                                        
                                        # Добавляем фрагмент с совпадением
                                        match_start = max(0, pos - 50)
                                        match_end = min(len(content), pos + len(query) + 50)
                                        snippet = content[match_start:match_end]
                                        
                                        # Форматируем сниппет
                                        snippet = f"...{snippet}..."
                                        
                                        # Добавляем в результаты, если еще не добавлено
                                        if snippet not in all_matches:
                                            all_matches.append(snippet)
                                        
                                        # Переходим к следующему вхождению
                                        start_pos = pos + len(query)
                                    
                                    # Если найдены совпадения, добавляем их в результаты
                                    if all_matches:
                                        file_info_copy = file_info.copy()
                                        file_info_copy["snippets"] = all_matches[:5]  # Ограничиваем 5 фрагментами
                                        file_info_copy["match_type"] = "content"
                                        file_info_copy["match_count"] = len(all_matches)
                                        results.append(file_info_copy)
                        except Exception as e:
                            print(f"Ошибка при поиске в файле {file_path}: {e}")
            
            # Сортируем результаты
            results.sort(key=lambda x: x.get("last_modified", ""), reverse=True)
            
            # Формируем информацию о поиске для включения в ответ
            search_info = {
                "query": query,
                "applied_filters": {k: v for k, v in filters.items() if v is not None and v != ''},
                "total_results": len(results),
                "search_date": datetime.now().isoformat()
            }
            
            return self.send_json_response({"search_info": search_info, "results": results})
        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)
    
    def do_OPTIONS(self):
        """Обработка запросов OPTIONS для CORS."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-API-Key, Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Обработка GET-запросов с поддержкой API."""
        # Парсим URL
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # Проверяем, является ли запрос API-запросом
        if path.startswith('/api/'):
            # Маршрутизация API
            if path == '/api/standards':
                return self.handle_api_standards()
            elif path == '/api/projects':
                return self.handle_api_projects()
            elif path.startswith('/api/file/'):
                file_path = urllib.parse.unquote(path[10:])
                return self.handle_api_file_content(file_path)
            elif path == '/api/search':
                # Поддерживаем либо параметр 'q' для простого поиска, либо пустой запрос с фильтрами
                if 'q' in query_params:
                    return self.handle_api_search(query_params['q'][0])
                else:
                    return self.handle_api_search("")  # Пустой запрос при поиске только по фильтрам
            # Новые эндпоинты для работы с абстрактными идентификаторами
            elif path == '/api/abstract/list':
                doc_type = query_params.get('type', [None])[0]
                return self.handle_api_abstract_list(doc_type)
            elif path.startswith('/api/abstract/document/'):
                identifier = urllib.parse.unquote(path[len('/api/abstract/document/'):])
                return self.handle_api_abstract_doc(identifier)
            elif path == '/api/abstract/convert' and 'path' in query_params:
                file_path = query_params['path'][0]
                to_abstract = query_params.get('to_abstract', ['true'])[0].lower() == 'true'
                return self.handle_api_convert_links(file_path, to_abstract)
            elif path == '/api/abstract/create' and 'path' in query_params:
                file_path = query_params['path'][0]
                doc_type = query_params.get('type', [None])[0]
                primary_id = query_params.get('primary_id', [None])[0]
                secondary_id = query_params.get('secondary_id', [None])[0]
                return self.handle_api_create_identifier(file_path, doc_type, primary_id, secondary_id)
            elif path == '/api/abstract/resolve' and 'id' in query_params:
                identifier = query_params['id'][0]
                return self.handle_api_resolve_identifier(identifier)
            elif path == '/api/ping':
                # Эндпоинт для проверки доступности API
                return self.send_json_response({"status": "ok"})
            elif path == '/api/versions' and 'standard' in query_params:
                # Получение всех версий стандарта (включая архивные)
                standard_name = query_params['standard'][0]
                include_archived = query_params.get('include_archived', ['true'])[0].lower() == 'true'
                return self.handle_api_versions(standard_name, include_archived)
            elif path == '/api/validate' and 'path' in query_params:
                # Валидация стандарта на соответствие правилам
                file_path = query_params['path'][0]
                return self.handle_api_validate(file_path)
            # Эндпоинты для отслеживания прогресса и достижений
            elif path == '/api/progress':
                # Получение общей информации о прогрессе системы
                return self.handle_api_progress()
            elif path == '/api/achievements':
                # Получение списка достижений с их статусом
                return self.handle_api_achievements()
            elif path == '/api/milestones':
                # Получение списка вех с их статусом
                return self.handle_api_milestones()
            elif path == '/api/activity':
                # Получение статистики активности
                days = int(query_params.get('days', [7])[0])
                return self.handle_api_activity(days)
            # Добавляем маршруты API для инцидентов
            elif path.startswith('/api/incidents') and HAS_INCIDENTS_API:
                # Делегируем обработку запросов к инцидентам в incidents_api
                # API инцидентов будет доступно по /api/incidents/... путям
                return self.handle_api_incidents(path, query_params)
            elif path == '/api/track' and 'action_type' in query_params:
                # Отслеживание действия и обновление прогресса
                action_type = query_params['action_type'][0]
                
                # Получаем данные действия из параметров запроса
                action_data = {}
                for key, value in query_params.items():
                    if key != 'action_type' and key != 'api_key':
                        action_data[key] = value[0]
                
                return self.handle_api_track_action(action_type, action_data)
            else:
                self.send_error(404, "API endpoint not found")
                return
        
        # Для обычных запросов используем стандартную обработку
        if path == '/':
            self.path = '/index.html'
        
        return http.server.SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        """Обработка POST запросов с поддержкой API."""
        # Парсим URL
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # Обрабатываем только API-запросы
        if path.startswith('/api/'):
            # Добавляем маршруты API для инцидентов
            if path.startswith('/api/incidents') and HAS_INCIDENTS_API:
                # Делегируем обработку запросов к инцидентам в incidents_api
                return self.handle_api_incidents(path, query_params)
            else:
                self.send_error(404, "API endpoint not found")
                return
        else:
            self.send_error(405, "Method Not Allowed")
            return
    
    def do_PUT(self):
        """Обработка PUT запросов с поддержкой API."""
        # Парсим URL
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # Обрабатываем только API-запросы
        if path.startswith('/api/'):
            # Добавляем маршруты API для инцидентов
            if path.startswith('/api/incidents') and HAS_INCIDENTS_API:
                # Делегируем обработку запросов к инцидентам в incidents_api
                return self.handle_api_incidents(path, query_params)
            else:
                self.send_error(404, "API endpoint not found")
                return
        else:
            self.send_error(405, "Method Not Allowed")
            return
    
    def do_DELETE(self):
        """Обработка DELETE запросов с поддержкой API."""
        # Парсим URL
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # Обрабатываем только API-запросы
        if path.startswith('/api/'):
            # Добавляем маршруты API для инцидентов
            if path.startswith('/api/incidents') and HAS_INCIDENTS_API:
                # Делегируем обработку запросов к инцидентам в incidents_api
                return self.handle_api_incidents(path, query_params)
            else:
                self.send_error(404, "API endpoint not found")
                return
        else:
            self.send_error(405, "Method Not Allowed")
            return
    
    @require_api_key
    def handle_api_progress(self):
        """Получает общую информацию о прогрессе системы."""
        if not HAS_PROGRESS_TRACKER:
            return self.send_json_response({"error": "Функциональность отслеживания прогресса недоступна"}, 500)
        
        try:
            system_status = get_system_status()
            return self.send_json_response(system_status)
        except Exception as e:
            logger.error(f"Ошибка при получении информации о прогрессе: {e}")
            return self.send_json_response({"error": str(e)}, 500)
    
    @require_api_key
    def handle_api_achievements(self):
        """Получает список всех достижений с их статусом."""
        if not HAS_PROGRESS_TRACKER:
            return self.send_json_response({"error": "Функциональность отслеживания прогресса недоступна"}, 500)
        
        try:
            tracker = ProgressTracker()
            achievements = tracker.get_achievement_status()
            tracker.close()
            
            return self.send_json_response({"achievements": achievements})
        except Exception as e:
            logger.error(f"Ошибка при получении достижений: {e}")
            return self.send_json_response({"error": str(e)}, 500)
    
    @require_api_key
    def handle_api_milestones(self):
        """Получает список всех вех с их статусом."""
        if not HAS_PROGRESS_TRACKER:
            return self.send_json_response({"error": "Функциональность отслеживания прогресса недоступна"}, 500)
        
        try:
            tracker = ProgressTracker()
            milestones = tracker.get_milestone_status()
            tracker.close()
            
            return self.send_json_response({"milestones": milestones})
        except Exception as e:
            logger.error(f"Ошибка при получении вех: {e}")
            return self.send_json_response({"error": str(e)}, 500)
    
    @require_api_key
    def handle_api_activity(self, days=7):
        """Получает статистику активности за указанное количество дней."""
        if not HAS_PROGRESS_TRACKER:
            return self.send_json_response({"error": "Функциональность отслеживания прогресса недоступна"}, 500)
        
        try:
            tracker = ProgressTracker()
            activity = tracker.get_activity_stats(int(days))
            tracker.close()
            
            return self.send_json_response({"activity": activity})
        except Exception as e:
            logger.error(f"Ошибка при получении активности: {e}")
            return self.send_json_response({"error": str(e)}, 500)
    
    @require_api_key
    def handle_api_incidents(self, path, query_params):
        """
        Обрабатывает запросы к API инцидентов.
        
        Args:
            path (str): Путь запроса
            query_params (dict): Параметры запроса
            
        Returns:
            JSON-ответ с результатами
        """
        if not HAS_INCIDENTS_API:
            return self.send_json_response({
                "error": "API инцидентов недоступно"
            }, 500)
        
        try:
            # Получаем метод запроса
            request_method = self.command  # GET, POST, PUT, DELETE
            
            # Формируем данные запроса для incidents_api
            request_data = {
                'path': path,  # Передаем полный путь, incidents_api разберется с ним
                'query_params': query_params,
                'method': request_method,
                'api_key': self.headers.get('X-API-Key', query_params.get('api_key', [None])[0])
            }
            
            # Добавляем тело запроса для POST и PUT запросов
            if request_method in ['POST', 'PUT']:
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    body = self.rfile.read(content_length).decode('utf-8')
                    try:
                        request_data['body'] = json.loads(body)
                    except json.JSONDecodeError:
                        return self.send_json_response({
                            "error": "Invalid JSON in request body"
                        }, 400)
                else:
                    request_data['body'] = {}
            
            # Для отладки
            logger.info(f"API incidents: {path}, method: {request_method}")
            
            # Делегируем обработку в incidents_api и получаем результат
            response = register_incidents_api(self, request_data)
            
            # Проверяем структуру ответа
            if isinstance(response, tuple) and len(response) == 2:
                data, status_code = response
                return self.send_json_response(data, status_code)
            else:
                logger.warning(f"Неверный формат ответа от incidents_api: {response}")
                # Если формат ответа не соответствует ожидаемому, возвращаем ошибку
                return self.send_json_response({
                    "error": "Неверный формат ответа от API инцидентов"
                }, 500)
                
        except Exception as e:
            logger.error(f"Ошибка при обработке API инцидентов: {e}")
            import traceback
            logger.error(f"Трассировка: {traceback.format_exc()}")
            return self.send_json_response({
                "error": f"Ошибка в API инцидентов: {str(e)}"
            }, 500)
    
    @require_api_key
    def handle_api_track_action(self, action_type, action_data):
        """Отслеживает действие и обновляет прогресс."""
        if not HAS_PROGRESS_TRACKER:
            return self.send_json_response({"error": "Функциональность отслеживания прогресса недоступна"}, 500)
        
        try:
            result = {}
            
            if action_type == 'standard':
                action = action_data.get('action', 'create')
                count = int(action_data.get('count', 1))
                standard_type = action_data.get('type')
                
                result = track_standard_action(action, count, standard_type)
            
            elif action_type == 'project':
                action = action_data.get('action', 'create')
                count = int(action_data.get('count', 1))
                with_diagnostics = action_data.get('with_diagnostics', False)
                
                result = track_project_action(action, count, with_diagnostics)
            
            elif action_type == 'api':
                action = action_data.get('action', 'call')
                count = int(action_data.get('count', 1))
                
                result = track_api_action(action, count)
            
            elif action_type == 'git':
                action = action_data.get('action', 'sync')
                
                result = track_git_action(action)
            
            else:
                return self.send_json_response({"error": f"Неизвестный тип действия: {action_type}"}, 400)
            
            return self.send_json_response(result)
        except Exception as e:
            logger.error(f"Ошибка при отслеживании действия: {e}")
            return self.send_json_response({"error": str(e)}, 500)
        
    @require_api_key
    def handle_api_versions(self, standard_name, include_archived=True):
        """Получает все версии указанного стандарта."""
        try:
            # Получаем все файлы стандартов
            all_standards = self.list_markdown_files(STANDARDS_DIR)
            
            # Разбираем имя файла стандарта для поиска
            standard_parts = standard_name.split(' ')
            if len(standard_parts) < 2:
                return self.send_json_response({"error": "Invalid standard name format. Expected format: '[number] [name]'"}, 400)
            
            # Выделяем номер и название для поиска
            standard_number = standard_parts[0]
            standard_base_name = ' '.join(standard_parts[1:]).lower()
            
            # Ищем все версии данного стандарта
            versions = []
            for standard in all_standards:
                filename = standard["filename"].lower()
                
                # Проверяем, соответствует ли файл искомому стандарту
                # Формат имени: [номер].[подномер] [название] by [дата] [время] CET by [автор].md
                if filename.startswith(standard_number) and standard_base_name in filename:
                    # Извлекаем информацию о версии из имени файла
                    version_info = self.extract_version_info(standard["filename"])
                    if version_info:
                        standard.update(version_info)
                        
                        # Проверяем, является ли файл архивным
                        is_archived = "archive AI never use" in standard["path"]
                        standard["is_archived"] = is_archived
                        
                        # Добавляем в результаты
                        if include_archived or not is_archived:
                            versions.append(standard)
            
            # Сортируем версии по дате (сначала новые)
            versions.sort(key=lambda x: x.get("version_date", ""), reverse=True)
            
            return self.send_json_response({
                "standard_name": standard_name,
                "versions_count": len(versions),
                "versions": versions
            })
        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)
    
    def extract_version_info(self, filename):
        """Извлекает информацию о версии из имени файла стандарта."""
        try:
            # Формат имени: [номер].[подномер] [название] by [дата] [время] CET by [автор].md
            # Пример: 1.1 ticket standard by 10 may 2025 2355 CET by Ilya Krasinsky.md
            
            # Извлекаем компоненты
            parts = filename.split(' by ')
            if len(parts) < 3:
                return None
            
            base_name = parts[0]  # [номер].[подномер] [название]
            date_part = parts[1]  # [дата] [время] CET
            author_part = parts[2].replace('.md', '')  # [автор]
            
            # Преобразуем дату в стандартный формат
            date_parts = date_part.split()
            if len(date_parts) < 3:
                return None
            
            # Формат: день месяц год [время] CET
            day = date_parts[0]
            month = date_parts[1]
            year = date_parts[2]
            time = date_parts[3] if len(date_parts) > 3 else "0000"
            
            # Форматируем дату
            date_str = f"{day} {month} {year}"
            timestamp = f"{date_str} {time}"
            
            return {
                "version_base_name": base_name,
                "version_date": date_str,
                "version_time": time,
                "version_timestamp": timestamp,
                "version_author": author_part
            }
        except Exception as e:
            print(f"Ошибка при извлечении информации о версии из {filename}: {e}")
            return None
    
    @require_api_key
    def handle_api_validate(self, file_path):
        """Проверяет стандарт на соответствие правилам."""
        try:
            # Проверяем, существует ли файл
            if not os.path.exists(file_path) or not os.path.isfile(file_path):
                return self.send_json_response({"error": "File not found"}, 404)
            
            # Проверяем, что это markdown файл
            if not file_path.endswith('.md'):
                return self.send_json_response({"error": "Only markdown files are supported"}, 400)
            
            # Извлекаем имя файла
            filename = os.path.basename(file_path)
            
            # Считываем содержимое файла
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Проводим проверки
            validation_results = {
                "filename_format": self.validate_filename_format(filename),
                "content_structure": self.validate_content_structure(content),
                "authors": self.validate_authors(filename, content, file_path)
            }
            
            # Общий статус валидации
            is_valid = all(result["valid"] for result in validation_results.values())
            
            return self.send_json_response({
                "file_path": file_path,
                "is_valid": is_valid,
                "validation_date": datetime.now().isoformat(),
                "results": validation_results
            })
        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)
    
    def validate_filename_format(self, filename):
        """Проверяет формат имени файла."""
        # Формат: [номер].[подномер] [название] by [дата] [время] CET by [автор].md
        pattern = r"^(\d+(\.\d+)?) .+ by \d+ [a-zA-Z]+ \d{4}( \d{4})? CET by .+\.md$"
        is_valid = bool(re.match(pattern, filename))
        
        return {
            "valid": is_valid,
            "check": "filename_format",
            "expected": "[номер].[подномер] [название] by [дата] [время] CET by [автор].md",
            "actual": filename,
            "message": "Имя файла соответствует стандарту" if is_valid else "Имя файла не соответствует стандарту"
        }
    
    def validate_content_structure(self, content):
        """Проверяет структуру содержимого файла."""
        # Список обязательных элементов
        required_elements = [
            {"pattern": r"^# ", "name": "Заголовок первого уровня", "found": False},
            {"pattern": r"^## ", "name": "Заголовок второго уровня", "found": False},
            {"pattern": r"(?i)лицензия", "name": "Раздел лицензии", "found": False}
        ]
        
        # Проверяем наличие каждого элемента
        for element in required_elements:
            if re.search(element["pattern"], content, re.MULTILINE):
                element["found"] = True
        
        # Формируем отчет
        missing_elements = [element["name"] for element in required_elements if not element["found"]]
        is_valid = len(missing_elements) == 0
        
        return {
            "valid": is_valid,
            "check": "content_structure",
            "found_elements": [element["name"] for element in required_elements if element["found"]],
            "missing_elements": missing_elements,
            "message": "Структура содержимого соответствует стандарту" if is_valid else "Отсутствуют обязательные элементы"
        }
    
    def validate_authors(self, filename, content, file_path):
        """Проверяет правильность указания авторов."""
        # Проверяем, является ли файл Task Master стандартом
        is_task_master = "0. task master" in filename.lower()
        
        # Ищем упоминания авторов
        contains_dmitry = "Дмитрия Карасева" in content or "Dmitry Karasev" in content
        contains_ilya = "Илью Красинского" in content or "Ilya Krasinsky" in content
        
        # Определяем правильность
        if is_task_master:
            # В Task Master должны быть оба автора
            is_valid = contains_dmitry and contains_ilya
            message = "Авторы указаны корректно" if is_valid else "В Task Master стандарте должны быть указаны оба автора"
        else:
            # В других стандартах должен быть только Илья
            is_valid = contains_ilya and not contains_dmitry
            message = "Авторы указаны корректно" if is_valid else "В производных стандартах должен быть указан только Илья Красинский"
        
        return {
            "valid": is_valid,
            "check": "authors",
            "is_task_master": is_task_master,
            "contains_dmitry": contains_dmitry,
            "contains_ilya": contains_ilya,
            "message": message
        }
        
# Импортируем расширение для HeroesGPT Bot Reviews
try:
    from advising_platform.advising_platform.src.api.server_api_extensions import register_api_extensions
    HAS_HEROES_EXTENSIONS = True
    print("Расширение HeroesGPT Bot Reviews успешно загружено")
except ImportError as e:
    print(f"Не удалось загрузить расширение HeroesGPT Bot Reviews: {e}")
    HAS_HEROES_EXTENSIONS = False

# Запускаем сервер на порту 5001 (чтобы не конфликтовать с сервером Markdown)
PORT = 5001
Handler = APIHandler

# Регистрируем расширения для HeroesGPT Bot Reviews, если доступны
if HAS_HEROES_EXTENSIONS:
    register_api_extensions(Handler)
    print("Расширение HeroesGPT Bot Reviews зарегистрировано")

# Обработка корректного завершения
def signal_handler(sig, frame):
    print('Завершение работы сервера...')
    try:
        if 'httpd' in globals() and httpd:
            httpd.server_close()
    except:
        pass
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Запуск сервера
httpd = None  # Инициализация переменной httpd

if HAS_INMEMORY_INDEXER:
    from flask import Flask, render_template
    
    # Создаем Flask-приложение
    app = Flask(__name__)
    
    # Регистрируем Blueprint с API in-memory индексатора
    register_blueprint(app)
    
    # Добавляем обработчик корневого URL
    @app.route('/')
    def index():
        return "<h1>API Сервер</h1><p>Доступны следующие API:</p><ul><li>/api/ - стандартное API</li><li>/inmemory/ - API для in-memory индексатора</li></ul>"
    
    # Запускаем Flask-приложение
    print(f"Запуск Flask API на порту {PORT}")
    app.run(host="0.0.0.0", port=PORT)
else:
    # Запускаем стандартный HTTP-сервер
    try:
        socketserver.TCPServer.allow_reuse_address = True
        httpd = socketserver.TCPServer(("0.0.0.0", PORT), Handler)
        print(f"Serving at port {PORT}")
        print(f"API доступен по адресу: http://localhost:{PORT}/api/")
        print(f"Доступные API-эндпоинты:")
        print(f"  - GET /api/standards - список всех стандартов")
        print(f"  - GET /api/projects - список всех проектов")
        print(f"  - GET /api/file/[путь к файлу] - содержимое файла")
        print(f"  - GET /api/search?q=[запрос] - поиск по файлам")
        if HAS_DOCUMENT_REGISTRY:
            print(f"  - GET /api/abstract/list?type=[тип] - список логических идентификаторов")
            print(f"  - GET /api/abstract/document/[идентификатор] - получение документа по идентификатору")
            print(f"  - GET /api/abstract/convert?path=[путь]&to_abstract=true|false - преобразование ссылок")
        print(f"Для авторизации используйте заголовок X-API-Key или параметр api_key")
        httpd.serve_forever()
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"Port {PORT} is already in use. Attempting to use a different port.")
            # Попробуем найти свободный порт
            for alt_port in range(5001, 5010):
                try:
                    httpd = socketserver.TCPServer(("0.0.0.0", alt_port), Handler)
                    print(f"Using alternative port {alt_port}")
                    print(f"API доступен по адресу: http://localhost:{alt_port}/api/")
                    httpd.serve_forever()
                    break
                except OSError:
                    continue
            else:
                print("Could not find an available port. Please free port 5000 and try again.")
                sys.exit(1)
        else:
            print(f"Error starting server: {e}")
            sys.exit(1)