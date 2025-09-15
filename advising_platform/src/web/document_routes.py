"""
Маршруты для документов.

Модуль содержит обработчики для маршрутов, связанных с документами,
включая отображение, создание, редактирование и архивацию документов.

Автор: AI Assistant
Дата: 20 мая 2025
"""

import os
import json
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import unquote
import http.server
from http.server import BaseHTTPRequestHandler
import re
import cgi
import logging
from datetime import datetime

# Настройка логирования
logger = logging.getLogger("document_routes")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Импортируем шаблонизатор
try:
    from advising_platform.src.web.template_engine import render_template
    has_templating = True
except ImportError:
    logger.warning("Не удалось импортировать шаблонизатор, будет использован базовый режим")
    has_templating = False

# Импортируем рендерер Markdown
try:
    from advising_platform.src.web.markdown_renderer import markdown_renderer
    has_markdown_renderer = True
except ImportError:
    logger.warning("Не удалось импортировать рендерер Markdown, будет использован базовый режим")
    has_markdown_renderer = False

# Импортируем модуль рабочего процесса синхронизации документов
try:
    from advising_platform.src.core.document_sync_workflow import document_workflow
    has_workflow = True
except ImportError:
    logger.warning("Не удалось импортировать модуль document_workflow, операции синхронизации будут недоступны")
    has_workflow = False

# Пути к основным директориям
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
REPORT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO_PATH = os.path.join(REPORT_DIR, "todo.md")
INCIDENTS_DIR = os.path.join(REPORT_DIR, "[todo · incidents]/ai.incidents")
STANDARDS_DIR = os.path.join(REPORT_DIR, "[standards .md]")

class DocumentRouteHandler:
    """
    Обработчик маршрутов для документов. Используется для отображения,
    создания, редактирования и архивации документов.
    """
    
    @staticmethod
    def handle_documents_list(handler: BaseHTTPRequestHandler) -> bool:
        """
        Обработчик для страницы списка документов.
        
        Args:
            handler: Обработчик HTTP-запросов
            
        Returns:
            bool: True, если запрос обработан успешно, иначе False
        """
        logger.info("Обработка запроса к списку документов")
        
        # Пока просто выводим список документов
        handler.send_response(200)
        handler.send_header("Content-type", "text/html; charset=utf-8")
        handler.end_headers()
        
        if has_templating:
            # Получаем список документов
            documents = DocumentRouteHandler._get_documents_list()
            
            # Рендерим шаблон
            output = render_template(
                "documents_list.html",
                {
                    "title": "Список документов",
                    "documents": documents,
                    "date": datetime.now().strftime("%d %B %Y")
                }
            )
            handler.wfile.write(output.encode("utf-8"))
            return True
        else:
            # Базовый режим без шаблонизатора
            output = "<html><head><title>Список документов</title></head><body>"
            output += "<h1>Список документов</h1>"
            output += "<p>Шаблонизатор недоступен, используется базовый режим</p>"
            output += "</body></html>"
            handler.wfile.write(output.encode("utf-8"))
            return True
    
    @staticmethod
    def handle_document_view(handler: BaseHTTPRequestHandler, path: str) -> bool:
        """
        Обработчик для просмотра документа.
        
        Args:
            handler: Обработчик HTTP-запросов
            path: Путь к документу
            
        Returns:
            bool: True, если запрос обработан успешно, иначе False
        """
        logger.info(f"Обработка запроса к документу: {path}")
        
        # Декодируем URL-параметры
        path = unquote(path)
        
        # Проверяем существование файла
        if not os.path.exists(path):
            logger.warning(f"Файл не найден: {path}")
            handler.send_response(404)
            handler.send_header("Content-type", "text/html; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(b"<html><body><h1>404 Not Found</h1><p>Документ не найден</p></body></html>")
            return False
        
        handler.send_response(200)
        handler.send_header("Content-type", "text/html; charset=utf-8")
        handler.end_headers()
        
        if has_templating and has_markdown_renderer:
            # Получаем данные документа
            document_data = markdown_renderer.render_document(path)
            
            # Рендерим шаблон
            output = render_template("medium_style/markdown_viewer.html", document_data)
            handler.wfile.write(output.encode("utf-8"))
            return True
        else:
            # Базовый режим без шаблонизатора и рендерера
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            output = "<html><head><title>Просмотр документа</title></head><body>"
            output += f"<h1>{os.path.basename(path)}</h1>"
            output += f"<pre>{content}</pre>"
            output += "</body></html>"
            handler.wfile.write(output.encode("utf-8"))
            return True
    
    @staticmethod
    def handle_document_edit(handler: BaseHTTPRequestHandler, path: str) -> bool:
        """
        Обработчик для редактирования документа.
        
        Args:
            handler: Обработчик HTTP-запросов
            path: Путь к документу
            
        Returns:
            bool: True, если запрос обработан успешно, иначе False
        """
        logger.info(f"Обработка запроса на редактирование документа: {path}")
        
        # Декодируем URL-параметры
        path = unquote(path)
        
        # Проверяем существование файла
        if not os.path.exists(path):
            logger.warning(f"Файл не найден: {path}")
            handler.send_response(404)
            handler.send_header("Content-type", "text/html; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(b"<html><body><h1>404 Not Found</h1><p>Документ не найден</p></body></html>")
            return False
        
        handler.send_response(200)
        handler.send_header("Content-type", "text/html; charset=utf-8")
        handler.end_headers()
        
        if has_templating:
            # Читаем содержимое документа
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Рендерим шаблон
            output = render_template(
                "document_edit.html",
                {
                    "title": f"Редактирование: {os.path.basename(path)}",
                    "document_path": path,
                    "content": content,
                    "date": datetime.now().strftime("%d %B %Y")
                }
            )
            handler.wfile.write(output.encode("utf-8"))
            return True
        else:
            # Базовый режим без шаблонизатора
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            output = "<html><head><title>Редактирование документа</title></head><body>"
            output += f"<h1>Редактирование: {os.path.basename(path)}</h1>"
            output += f"<form method='post' action='/api/documents/update'>"
            output += f"<input type='hidden' name='document_path' value='{path}'>"
            output += f"<textarea name='content' rows='20' cols='80'>{content}</textarea>"
            output += f"<br><input type='submit' value='Сохранить'>"
            output += f"</form>"
            output += "</body></html>"
            handler.wfile.write(output.encode("utf-8"))
            return True
    
    @staticmethod
    def handle_document_create(handler: BaseHTTPRequestHandler, document_type: str) -> bool:
        """
        Обработчик для создания нового документа.
        
        Args:
            handler: Обработчик HTTP-запросов
            document_type: Тип документа (task, incident, standard, etc.)
            
        Returns:
            bool: True, если запрос обработан успешно, иначе False
        """
        logger.info(f"Обработка запроса на создание документа типа: {document_type}")
        
        handler.send_response(200)
        handler.send_header("Content-type", "text/html; charset=utf-8")
        handler.end_headers()
        
        if has_templating:
            # Получаем шаблон для нового документа
            template_content = DocumentRouteHandler._get_document_template(document_type)
            
            # Рендерим шаблон
            output = render_template(
                "document_create.html",
                {
                    "title": f"Создание: {document_type}",
                    "document_type": document_type,
                    "template_content": template_content,
                    "date": datetime.now().strftime("%d %B %Y")
                }
            )
            handler.wfile.write(output.encode("utf-8"))
            return True
        else:
            # Базовый режим без шаблонизатора
            template_content = DocumentRouteHandler._get_document_template(document_type)
            
            output = "<html><head><title>Создание документа</title></head><body>"
            output += f"<h1>Создание: {document_type}</h1>"
            output += f"<form method='post' action='/api/documents/create'>"
            output += f"<input type='hidden' name='document_type' value='{document_type}'>"
            output += f"<textarea name='content' rows='20' cols='80'>{template_content}</textarea>"
            output += f"<br><input type='submit' value='Создать'>"
            output += f"</form>"
            output += "</body></html>"
            handler.wfile.write(output.encode("utf-8"))
            return True
    
    @staticmethod
    def handle_api_document_create(handler: BaseHTTPRequestHandler) -> bool:
        """
        Обработчик API для создания документа.
        
        Args:
            handler: Обработчик HTTP-запросов
            
        Returns:
            bool: True, если запрос обработан успешно, иначе False
        """
        logger.info("Обработка API-запроса на создание документа")
        
        # Проверяем наличие модуля рабочего процесса
        if not has_workflow:
            handler.send_response(500)
            handler.send_header("Content-type", "application/json")
            handler.end_headers()
            response = {"success": False, "error": "Модуль рабочего процесса недоступен"}
            handler.wfile.write(json.dumps(response).encode("utf-8"))
            return False
        
        # Получаем данные из запроса
        content_length = int(handler.headers['Content-Length'])
        post_data = handler.rfile.read(content_length).decode('utf-8')
        form_data = DocumentRouteHandler._parse_form_data(post_data)
        
        document_type = form_data.get("document_type", "")
        content = form_data.get("content", "")
        
        if not document_type or not content:
            handler.send_response(400)
            handler.send_header("Content-type", "application/json")
            handler.end_headers()
            response = {"success": False, "error": "Не указан тип документа или содержимое"}
            handler.wfile.write(json.dumps(response).encode("utf-8"))
            return False
        
        # Определяем путь к файлу
        file_path = DocumentRouteHandler._get_new_document_path(document_type)
        
        # Создаем документ с проверкой на дубликаты и синхронизацией
        success, message = document_workflow.create_document(file_path, content, document_type)
        
        handler.send_response(200)
        handler.send_header("Content-type", "application/json")
        handler.end_headers()
        
        response = {
            "success": success,
            "message": message,
            "document_path": file_path if success else None
        }
        
        handler.wfile.write(json.dumps(response).encode("utf-8"))
        return True
    
    @staticmethod
    def handle_api_document_update(handler: BaseHTTPRequestHandler) -> bool:
        """
        Обработчик API для обновления документа.
        
        Args:
            handler: Обработчик HTTP-запросов
            
        Returns:
            bool: True, если запрос обработан успешно, иначе False
        """
        logger.info("Обработка API-запроса на обновление документа")
        
        # Проверяем наличие модуля рабочего процесса
        if not has_workflow:
            handler.send_response(500)
            handler.send_header("Content-type", "application/json")
            handler.end_headers()
            response = {"success": False, "error": "Модуль рабочего процесса недоступен"}
            handler.wfile.write(json.dumps(response).encode("utf-8"))
            return False
        
        # Получаем данные из запроса
        content_length = int(handler.headers['Content-Length'])
        post_data = handler.rfile.read(content_length).decode('utf-8')
        form_data = DocumentRouteHandler._parse_form_data(post_data)
        
        document_path = form_data.get("document_path", "")
        content = form_data.get("content", "")
        
        if not document_path or not content:
            handler.send_response(400)
            handler.send_header("Content-type", "application/json")
            handler.end_headers()
            response = {"success": False, "error": "Не указан путь к документу или содержимое"}
            handler.wfile.write(json.dumps(response).encode("utf-8"))
            return False
        
        # Определяем тип документа
        document_type = DocumentRouteHandler._get_document_type(document_path)
        
        # Обновляем документ с проверкой на дубликаты и синхронизацией
        success, message = document_workflow.update_document(document_path, content, document_type)
        
        handler.send_response(200)
        handler.send_header("Content-type", "application/json")
        handler.end_headers()
        
        response = {
            "success": success,
            "message": message
        }
        
        handler.wfile.write(json.dumps(response).encode("utf-8"))
        return True
    
    @staticmethod
    def handle_api_document_archive(handler: BaseHTTPRequestHandler) -> bool:
        """
        Обработчик API для архивации документа.
        
        Args:
            handler: Обработчик HTTP-запросов
            
        Returns:
            bool: True, если запрос обработан успешно, иначе False
        """
        logger.info("Обработка API-запроса на архивацию документа")
        
        # Проверяем наличие модуля рабочего процесса
        if not has_workflow:
            handler.send_response(500)
            handler.send_header("Content-type", "application/json")
            handler.end_headers()
            response = {"success": False, "error": "Модуль рабочего процесса недоступен"}
            handler.wfile.write(json.dumps(response).encode("utf-8"))
            return False
        
        # Получаем данные из запроса
        content_length = int(handler.headers['Content-Length'])
        post_data = handler.rfile.read(content_length).decode('utf-8')
        json_data = json.loads(post_data)
        
        document_path = json_data.get("document_path", "")
        
        if not document_path:
            handler.send_response(400)
            handler.send_header("Content-type", "application/json")
            handler.end_headers()
            response = {"success": False, "error": "Не указан путь к документу"}
            handler.wfile.write(json.dumps(response).encode("utf-8"))
            return False
        
        # Определяем тип документа
        document_type = DocumentRouteHandler._get_document_type(document_path)
        
        # Архивируем документ с проверкой синхронизации
        success, message = document_workflow.archive_document(document_path, document_type)
        
        handler.send_response(200)
        handler.send_header("Content-type", "application/json")
        handler.end_headers()
        
        response = {
            "success": success,
            "message": message
        }
        
        handler.wfile.write(json.dumps(response).encode("utf-8"))
        return True
    
    @staticmethod
    def handle_api_document_check_sync(handler: BaseHTTPRequestHandler, path: str) -> bool:
        """
        Обработчик API для проверки синхронизации документа.
        
        Args:
            handler: Обработчик HTTP-запросов
            path: Путь к документу
            
        Returns:
            bool: True, если запрос обработан успешно, иначе False
        """
        logger.info(f"Обработка API-запроса на проверку синхронизации документа: {path}")
        
        # Декодируем URL-параметры
        path = unquote(path)
        
        # Проверяем наличие модуля рабочего процесса
        if not has_workflow:
            handler.send_response(500)
            handler.send_header("Content-type", "application/json")
            handler.end_headers()
            response = {"success": False, "error": "Модуль рабочего процесса недоступен"}
            handler.wfile.write(json.dumps(response).encode("utf-8"))
            return False
        
        # Проверяем существование файла
        if not os.path.exists(path):
            handler.send_response(404)
            handler.send_header("Content-type", "application/json")
            handler.end_headers()
            response = {"success": False, "error": f"Документ не найден: {path}"}
            handler.wfile.write(json.dumps(response).encode("utf-8"))
            return False
        
        # Проверяем синхронизацию с кешем
        success = document_workflow.before_document_operation(path)
        
        handler.send_response(200)
        handler.send_header("Content-type", "application/json")
        handler.end_headers()
        
        response = {
            "success": success,
            "message": "Документ синхронизирован с кешем" if success else "Ошибка синхронизации с кешем"
        }
        
        handler.wfile.write(json.dumps(response).encode("utf-8"))
        return True
    
    @staticmethod
    def handle_api_add_comment(handler: BaseHTTPRequestHandler) -> bool:
        """
        Обработчик API для добавления комментария к документу.
        
        Args:
            handler: Обработчик HTTP-запросов
            
        Returns:
            bool: True, если запрос обработан успешно, иначе False
        """
        logger.info("Обработка API-запроса на добавление комментария")
        
        # Проверяем наличие рендерера Markdown
        if not has_markdown_renderer:
            handler.send_response(500)
            handler.send_header("Content-type", "application/json")
            handler.end_headers()
            response = {"success": False, "error": "Рендерер Markdown недоступен"}
            handler.wfile.write(json.dumps(response).encode("utf-8"))
            return False
        
        # Получаем данные из запроса
        content_length = int(handler.headers['Content-Length'])
        post_data = handler.rfile.read(content_length).decode('utf-8')
        json_data = json.loads(post_data)
        
        document_path = json_data.get("document_path", "")
        paragraph_id = json_data.get("paragraph_id", "")
        author = json_data.get("author", "")
        text = json_data.get("text", "")
        
        if not document_path or not paragraph_id or not author or not text:
            handler.send_response(400)
            handler.send_header("Content-type", "application/json")
            handler.end_headers()
            response = {"success": False, "error": "Не указаны необходимые параметры"}
            handler.wfile.write(json.dumps(response).encode("utf-8"))
            return False
        
        # Добавляем комментарий
        success, message = markdown_renderer.add_comment(document_path, paragraph_id, author, text)
        
        handler.send_response(200)
        handler.send_header("Content-type", "application/json")
        handler.end_headers()
        
        response = {
            "success": success,
            "message": message
        }
        
        handler.wfile.write(json.dumps(response).encode("utf-8"))
        return True
    
    @staticmethod
    def _get_documents_list() -> List[Dict[str, Any]]:
        """
        Возвращает список документов.
        
        Returns:
            List[Dict[str, Any]]: Список документов
        """
        documents = []
        
        # Добавляем задачи
        if os.path.exists(TODO_PATH):
            documents.append({
                "type": "Основной файл",
                "title": "Список задач",
                "path": TODO_PATH,
                "updated_at": datetime.fromtimestamp(os.path.getmtime(TODO_PATH)).strftime("%d %B %Y")
            })
        
        # Добавляем инциденты
        if os.path.exists(INCIDENTS_DIR):
            for file_name in os.listdir(INCIDENTS_DIR):
                if file_name.endswith(".md"):
                    file_path = os.path.join(INCIDENTS_DIR, file_name)
                    documents.append({
                        "type": "Инцидент",
                        "title": file_name.replace(".md", "").replace("incident-", "").replace("-", " ").title(),
                        "path": file_path,
                        "updated_at": datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%d %B %Y")
                    })
        
        # Добавляем стандарты
        if os.path.exists(STANDARDS_DIR):
            for root, dirs, files in os.walk(STANDARDS_DIR):
                for file_name in files:
                    if file_name.endswith(".md"):
                        file_path = os.path.join(root, file_name)
                        documents.append({
                            "type": "Стандарт",
                            "title": file_name.replace(".md", "").replace("-", " ").title(),
                            "path": file_path,
                            "updated_at": datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%d %B %Y")
                        })
        
        return documents
    
    @staticmethod
    def _get_document_template(document_type: str) -> str:
        """
        Возвращает шаблон для нового документа заданного типа.
        
        Args:
            document_type: Тип документа (task, incident, standard, etc.)
            
        Returns:
            str: Шаблон документа
        """
        if document_type == "task":
            return """# Новая задача

- [ ] **Название задачи** [standard] · @ai assistant · до 31 мая 2025
**цель**: Описание цели задачи
**dod · result**: Критерии выполнения задачи
**подзадачи**:
- [ ] Подзадача 1
- [ ] Подзадача 2
- [ ] Подзадача 3

## Описание задачи

Подробное описание задачи...

## Связанные документы

- [Ссылка на связанный документ](путь/к/документу)
"""
        elif document_type == "incident":
            return """# Новый инцидент

## 20 мая 2025 - Название инцидента

**Тип инцидента**: Системная ошибка  
**Приоритет**: Средний  
**Статус**: Зафиксирован  
**Влияние**: Требует анализа  

**Описание**: 
Подробное описание инцидента...

## Анализ причин (5 Why)

1. **Почему возникла проблема?**
   Ответ на первый вопрос...

2. **Почему это произошло?**
   Ответ на второй вопрос...

3. **Почему это стало возможным?**
   Ответ на третий вопрос...

4. **Почему это не было предотвращено?**
   Ответ на четвертый вопрос...

5. **Почему отсутствовали меры защиты?**
   Ответ на пятый вопрос...

## Решение

Описание решения проблемы...

## Превентивные меры

Описание мер для предотвращения подобных инцидентов в будущем...
"""
        elif document_type == "standard":
            return """# Название стандарта

## Мини-манифест

**Для чего нужен этот стандарт?**
Описание назначения стандарта...

**Когда он применяется?**
Описание условий применения стандарта...

**Как его применять?**
Подробное описание применения стандарта...

**Как проверить, что он применен правильно?**
Критерии проверки правильности применения стандарта...

## Версионирование

**Версия**: 1.0  
**Дата создания**: 20 мая 2025  
**Автор**: AI Assistant  
**Статус**: Проект  

## Дополнительная информация

Дополнительная информация о стандарте...

## Связанные стандарты

- [Ссылка на связанный стандарт](путь/к/стандарту)
"""
        else:
            return f"""# Новый документ типа {document_type}

Содержимое документа...
"""
    
    @staticmethod
    def _get_new_document_path(document_type: str) -> str:
        """
        Возвращает путь для нового документа заданного типа.
        
        Args:
            document_type: Тип документа (task, incident, standard, etc.)
            
        Returns:
            str: Путь для нового документа
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        if document_type == "task":
            return os.path.join(REPORT_DIR, f"todo-new-task-{timestamp}.md")
        elif document_type == "incident":
            return os.path.join(INCIDENTS_DIR, f"incident-new-incident-{timestamp}.md")
        elif document_type == "standard":
            return os.path.join(STANDARDS_DIR, f"new-standard-{timestamp}.md")
        else:
            return os.path.join(REPORT_DIR, f"document-{document_type}-{timestamp}.md")
    
    @staticmethod
    def _get_document_type(document_path: str) -> str:
        """
        Определяет тип документа по пути.
        
        Args:
            document_path: Путь к документу
            
        Returns:
            str: Тип документа (task, incident, standard, etc.)
        """
        if "todo" in document_path.lower():
            return "task"
        elif "incident" in document_path.lower():
            return "incident"
        elif "[standards" in document_path.lower():
            return "standard"
        elif "hypothesis" in document_path.lower():
            return "hypothesis"
        else:
            return "document"
    
    @staticmethod
    def _parse_form_data(post_data: str) -> Dict[str, str]:
        """
        Парсит данные формы.
        
        Args:
            post_data: Данные POST-запроса
            
        Returns:
            Dict[str, str]: Словарь с данными формы
        """
        result = {}
        for item in post_data.split('&'):
            if '=' not in item:
                continue
            key, value = item.split('=', 1)
            result[unquote(key)] = unquote(value.replace('+', ' '))
        return result