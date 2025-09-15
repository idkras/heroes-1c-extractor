#!/usr/bin/env python3
"""
Модуль для внешнего API, позволяющего взаимодействовать с Advising Platform из Slack и Telegram.
Обеспечивает передачу клиентского контекста по стандартам для обновления информации
по проектам и задачам.
"""

import os
import sys
import json
import time
import logging
import hmac
import hashlib
import base64
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Union

from flask import Blueprint, request, jsonify, abort, current_app
from werkzeug.exceptions import BadRequest, Unauthorized, NotFound

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("external_api")

# Создаем Blueprint для маршрутов внешнего API
external_api = Blueprint('external_api', __name__, url_prefix='/api/v1/external')

# Конфигурация безопасности
API_TOKENS = {}  # Будет заполнено при инициализации из окружения
ALLOWED_SOURCES = ['slack', 'telegram']  # Разрешенные источники запросов
SLACK_SIGNING_SECRET = os.environ.get('SLACK_SIGNING_SECRET', '')
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')

# Список доступных действий
ALLOWED_ACTIONS = [
    'update_context',        # Обновить контекст проекта
    'create_task',           # Создать новую задачу
    'update_task',           # Обновить существующую задачу
    'create_incident',       # Создать новый инцидент
    'update_incident',       # Обновить существующий инцидент
    'get_task_status',       # Получить статус задачи
    'get_incident_status',   # Получить статус инцидента
    'get_project_summary',   # Получить краткую информацию о проекте
    'search',                # Поиск по документам
    'get_context',           # Получить context.md для конкретного проекта
    'get_next_actions',      # Получить next.action.md для всех проектов
    'execute_task',          # Выполнить задачу на основе контекста
    'generate_tasks',        # Сгенерировать задачи на основе контекста
]

def initialize_api_tokens():
    """Инициализирует токены доступа из переменных окружения."""
    global API_TOKENS
    
    # Получаем токены для разных источников
    slack_token = os.environ.get('ADVISING_API_SLACK_TOKEN', '')
    telegram_token = os.environ.get('ADVISING_API_TELEGRAM_TOKEN', '')
    
    if slack_token:
        API_TOKENS['slack'] = slack_token
    if telegram_token:
        API_TOKENS['telegram'] = telegram_token
    
    logger.info(f"Инициализировано {len(API_TOKENS)} токенов API")


def verify_slack_signature(request_data, timestamp, signature):
    """
    Проверяет подпись запроса от Slack.
    
    Args:
        request_data: Данные запроса
        timestamp: Временная метка запроса
        signature: Подпись запроса
    
    Returns:
        bool: True, если подпись верна, иначе False
    """
    if not SLACK_SIGNING_SECRET:
        logger.warning("SLACK_SIGNING_SECRET не настроен")
        return False
    
    # Формируем строку для подписи
    sig_basestring = f"v0:{timestamp}:{request_data}"
    
    # Создаем подпись с использованием HMAC-SHA256
    my_signature = 'v0=' + hmac.new(
        SLACK_SIGNING_SECRET.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Сравниваем подписи
    return hmac.compare_digest(my_signature, signature)


def verify_telegram_signature(request_data, signature):
    """
    Проверяет подпись запроса от Telegram.
    
    Args:
        request_data: Данные запроса
        signature: Подпись запроса
    
    Returns:
        bool: True, если подпись верна, иначе False
    """
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN не настроен")
        return False
    
    # Создаем подпись с использованием HMAC-SHA256
    secret_key = hashlib.sha256(TELEGRAM_BOT_TOKEN.encode()).digest()
    my_signature = hmac.new(
        secret_key,
        request_data.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Сравниваем подписи
    return hmac.compare_digest(my_signature, signature)


def verify_request(request, source):
    """
    Проверяет аутентификацию и авторизацию запроса.
    
    Args:
        request: Объект запроса Flask
        source: Источник запроса (slack, telegram)
    
    Returns:
        bool: True, если запрос верифицирован, иначе False
    
    Raises:
        Unauthorized: Если запрос не прошел проверку аутентификации
    """
    if source not in ALLOWED_SOURCES:
        logger.warning(f"Неподдерживаемый источник запроса: {source}")
        raise Unauthorized("Неподдерживаемый источник запроса")
    
    # Проверяем токен для источника
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        logger.warning("Отсутствует токен в заголовке Authorization")
        raise Unauthorized("Отсутствует токен в заголовке Authorization")
    
    token = auth_header.split(' ')[1]
    if source not in API_TOKENS or token != API_TOKENS[source]:
        logger.warning(f"Неверный токен для источника {source}")
        raise Unauthorized("Неверный токен")
    
    # Дополнительные проверки для разных источников
    if source == 'slack':
        timestamp = request.headers.get('X-Slack-Request-Timestamp', '')
        signature = request.headers.get('X-Slack-Signature', '')
        
        # Проверяем актуальность временной метки (не старше 5 минут)
        current_timestamp = int(time.time())
        if abs(current_timestamp - int(timestamp)) > 300:
            logger.warning("Устаревший запрос от Slack")
            raise Unauthorized("Устаревший запрос")
        
        # Проверяем подпись
        if not verify_slack_signature(request.get_data(as_text=True), timestamp, signature):
            logger.warning("Неверная подпись запроса от Slack")
            raise Unauthorized("Неверная подпись запроса")
    
    elif source == 'telegram':
        signature = request.headers.get('X-Telegram-Bot-Api-Secret-Token', '')
        
        # Проверяем подпись
        if not verify_telegram_signature(request.get_data(as_text=True), signature):
            logger.warning("Неверная подпись запроса от Telegram")
            raise Unauthorized("Неверная подпись запроса")
    
    return True


def validate_context_format(context):
    """
    Проверяет формат контекста на соответствие стандарту.
    
    Args:
        context: Словарь с контекстом
    
    Returns:
        bool: True, если формат верен, иначе False
    """
    # Проверяем наличие обязательных полей
    required_fields = ['project', 'namespace', 'version', 'data']
    if not all(field in context for field in required_fields):
        return False
    
    # Проверяем версию формата
    if not isinstance(context['version'], str):
        return False
    
    # Проверяем наличие данных
    if not isinstance(context['data'], dict):
        return False
    
    return True


def process_context_update(context_data, source):
    """
    Обрабатывает обновление контекста проекта.
    
    Args:
        context_data: Данные контекста
        source: Источник запроса (slack, telegram)
    
    Returns:
        Tuple[bool, str]: Результат обработки и сообщение
    """
    try:
        # Проверяем формат контекста
        if not validate_context_format(context_data):
            return False, "Неверный формат контекста"
        
        # Получаем данные проекта
        project = context_data['project']
        namespace = context_data['namespace']
        version = context_data['version']
        data = context_data['data']
        
        # Импортируем необходимые модули для работы с контекстом
        from advising_platform.src.context.context_manager import ContextManager
        
        # Получаем экземпляр менеджера контекста
        context_manager = ContextManager.get_instance()
        
        # Обновляем контекст
        result = context_manager.update_context(project, namespace, data, source=source, version=version)
        
        if result:
            return True, f"Контекст успешно обновлен для проекта {project}"
        else:
            return False, f"Ошибка при обновлении контекста для проекта {project}"
    
    except Exception as e:
        logger.error(f"Ошибка при обработке обновления контекста: {e}")
        return False, f"Внутренняя ошибка: {str(e)}"


def process_task_creation(task_data, source):
    """
    Обрабатывает создание новой задачи.
    
    Args:
        task_data: Данные задачи
        source: Источник запроса (slack, telegram)
    
    Returns:
        Tuple[bool, str, dict]: Результат обработки, сообщение и данные созданной задачи
    """
    try:
        # Проверяем наличие обязательных полей
        required_fields = ['title', 'project', 'priority']
        if not all(field in task_data for field in required_fields):
            return False, "Отсутствуют обязательные поля", {}
        
        # Импортируем необходимые модули
        from advising_platform.src.tasks.task_manager import TaskManager
        
        # Получаем экземпляр менеджера задач
        task_manager = TaskManager.get_instance()
        
        # Создаем задачу
        task_id, created = task_manager.create_task(
            title=task_data['title'],
            project=task_data['project'],
            priority=task_data['priority'],
            description=task_data.get('description', ''),
            due_date=task_data.get('due_date', ''),
            assignee=task_data.get('assignee', ''),
            tags=task_data.get('tags', []),
            source=source
        )
        
        if created:
            # Получаем данные созданной задачи
            task = task_manager.get_task(task_id)
            return True, f"Задача создана с ID: {task_id}", task
        else:
            return False, f"Ошибка при создании задачи", {}
    
    except Exception as e:
        logger.error(f"Ошибка при создании задачи: {e}")
        return False, f"Внутренняя ошибка: {str(e)}", {}


def process_incident_creation(incident_data, source):
    """
    Обрабатывает создание нового инцидента.
    
    Args:
        incident_data: Данные инцидента
        source: Источник запроса (slack, telegram)
    
    Returns:
        Tuple[bool, str, dict]: Результат обработки, сообщение и данные созданного инцидента
    """
    try:
        # Проверяем наличие обязательных полей
        required_fields = ['title', 'description', 'severity']
        if not all(field in incident_data for field in required_fields):
            return False, "Отсутствуют обязательные поля", {}
        
        # Импортируем необходимые модули
        from advising_platform.src.incidents.incident_manager import IncidentManager
        
        # Получаем экземпляр менеджера инцидентов
        incident_manager = IncidentManager.get_instance()
        
        # Создаем инцидент
        incident_id, created = incident_manager.create_incident(
            title=incident_data['title'],
            description=incident_data['description'],
            severity=incident_data['severity'],
            category=incident_data.get('category', 'process'),
            project=incident_data.get('project', ''),
            assignee=incident_data.get('assignee', ''),
            tags=incident_data.get('tags', []),
            source=source
        )
        
        if created:
            # Получаем данные созданного инцидента
            incident = incident_manager.get_incident(incident_id)
            return True, f"Инцидент создан с ID: {incident_id}", incident
        else:
            return False, f"Ошибка при создании инцидента", {}
    
    except Exception as e:
        logger.error(f"Ошибка при создании инцидента: {e}")
        return False, f"Внутренняя ошибка: {str(e)}", {}


def get_project_summary(project_id):
    """
    Получает краткую информацию о проекте.
    
    Args:
        project_id: Идентификатор проекта
    
    Returns:
        dict: Данные по проекту
    """
    try:
        # Импортируем необходимые модули
        from advising_platform.src.projects.project_manager import ProjectManager
        
        # Получаем экземпляр менеджера проектов
        project_manager = ProjectManager.get_instance()
        
        # Получаем данные проекта
        project_data = project_manager.get_project_summary(project_id)
        
        if project_data:
            return project_data
        else:
            return {"error": f"Проект не найден: {project_id}"}
    
    except Exception as e:
        logger.error(f"Ошибка при получении информации о проекте: {e}")
        return {"error": f"Внутренняя ошибка: {str(e)}"}


def search_documents(query, project=None, document_type=None, limit=10):
    """
    Выполняет поиск по документам.
    
    Args:
        query: Поисковый запрос
        project: Проект для фильтрации
        document_type: Тип документа для фильтрации
        limit: Максимальное количество результатов
    
    Returns:
        List[dict]: Список найденных документов
    """
    try:
        # Импортируем необходимые модули
        from advising_platform.src.search.search_engine import SearchEngine
        
        # Получаем экземпляр поискового движка
        search_engine = SearchEngine.get_instance()
        
        # Выполняем поиск
        results = search_engine.search(
            query=query,
            project=project,
            document_type=document_type,
            limit=limit
        )
        
        return results
    
    except Exception as e:
        logger.error(f"Ошибка при поиске документов: {e}")
        return []


def get_project_context(project_id):
    """
    Получает context.md для конкретного проекта.
    
    Args:
        project_id: Идентификатор проекта (например, 'rick.ai')
    
    Returns:
        dict: Данные контекста проекта
    """
    try:
        import os
        import re
        from datetime import datetime
        
        # Импортируем необходимые модули для работы с кешем документов
        from advising_platform.src.cache.document_cache import DocumentCacheManager
        
        # Получаем экземпляр менеджера кеша
        cache_manager = DocumentCacheManager.get_instance()
        
        # Путь к файлу context.md для проекта
        context_path = f"[projects]/{project_id}/context.md"
        
        # Проверяем существование файла
        file_exists = os.path.exists(context_path)
        
        # Если основной файл не найден, ищем альтернативные пути
        if not file_exists:
            projects_dir = "[projects]"
            alt_paths = [
                f"[projects]/{project_id}/context.md",
                f"[projects]/{project_id}/{project_id}.context.md",
                f"[projects]/{project_id.lower()}/context.md",
                f"[projects]/{project_id.replace('.', ' ')}/context.md",
                f"[projects]/{project_id.replace(' ', '_')}/context.md"
            ]
            
            # Проверяем каждый альтернативный путь
            for alt_path in alt_paths:
                if os.path.exists(alt_path):
                    context_path = alt_path
                    file_exists = True
                    break
            
            # Если все еще не найден, ищем по всем подкаталогам в [projects]
            if not file_exists:
                try:
                    for dir_name in os.listdir(projects_dir):
                        dir_path = os.path.join(projects_dir, dir_name)
                        if os.path.isdir(dir_path) and (dir_name.lower() == project_id.lower() or 
                                                      project_id.lower() in dir_name.lower()):
                            potential_path = os.path.join(dir_path, "context.md")
                            if os.path.exists(potential_path):
                                context_path = potential_path
                                file_exists = True
                                break
                except Exception as e:
                    logger.error(f"Ошибка при поиске альтернативных путей: {e}")
        
        # Получаем содержимое файла
        context_content = None
        if file_exists:
            try:
                # Используем корректный метод для получения документа из кеша
                context_content = cache_manager.get_document(context_path)
            except Exception as cache_error:
                logger.error(f"Ошибка при получении документа из кеша: {cache_error}")
                # Пробуем прочитать напрямую
                try:
                    with open(context_path, 'r', encoding='utf-8') as f:
                        context_content = f.read()
                except Exception as file_error:
                    logger.error(f"Ошибка при чтении файла {context_path}: {file_error}")
        
        if context_content:
            # Парсим содержимое для более информативной структуры
            title = project_id
            updated_date = None
            
            # Извлекаем название проекта и дату обновления
            title_match = re.search(r"^#\s+(.+)$", context_content, re.MULTILINE)
            if title_match:
                title = title_match.group(1)
            
            updated_match = re.search(r"updated:\s+(.+)$", context_content, re.MULTILINE)
            if updated_match:
                updated_date = updated_match.group(1)
            
            # Извлекаем события из истории проекта (в обратной хронологии)
            history_entries = []
            
            # Ищем заголовки с датами
            date_patterns = [
                r"##\s+(\d{4}-\d{2}-\d{2})",  # YYYY-MM-DD
                r"##\s+(\d{1,2}\s+(?:января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+\d{4})"  # DD Month YYYY
            ]
            
            date_sections = []
            for pattern in date_patterns:
                for match in re.finditer(pattern, context_content, re.MULTILINE):
                    date_str = match.group(1)
                    position = match.start()
                    date_sections.append((date_str, position))
            
            # Сортируем секции по позиции в документе
            date_sections.sort(key=lambda x: x[1])
            
            # Извлекаем содержимое каждой секции с датой
            for i, (date_str, position) in enumerate(date_sections):
                section_start = context_content.find('\n', position) + 1
                section_end = len(context_content)
                
                # Если есть следующая секция, используем её начало как конец текущей секции
                if i < len(date_sections) - 1:
                    section_end = date_sections[i+1][1]
                
                section_content = context_content[section_start:section_end].strip()
                
                # Добавляем запись в историю, даже если не удалось разбить на категории
                entry = {
                    "date": date_str,
                    "content": section_content
                }
                
                history_entries.append(entry)
            
            # Сортируем историю в обратном хронологическом порядке для соответствия требованию
            history_entries.reverse()
            
            return {
                "project": project_id,
                "title": title,
                "updated": updated_date,
                "path": context_path,
                "content": context_content,
                "history": history_entries,
                "exists": True
            }
        else:
            logger.warning(f"Файл контекста не найден или пуст: {context_path}")
            return {
                "project": project_id,
                "error": "Context file not found or empty",
                "path": context_path,
                "exists": False
            }
    
    except Exception as e:
        logger.error(f"Ошибка при получении контекста проекта {project_id}: {e}")
        return {
            "project": project_id,
            "error": f"Internal error: {str(e)}",
            "exists": False
        }


def get_next_actions(days_back=None):
    """
    Получает список next_actions.md для всех проектов, учитывая обратную хронологию.
    
    Args:
        days_back: Количество дней, за которые нужно получить дайджест задач. 
                  Если None, возвращает все задачи.
    
    Returns:
        dict: Данные next_actions.md со списком задач по всем проектам
    """
    try:
        # Импортируем необходимые модули
        from advising_platform.src.cache.document_cache import DocumentCacheManager
        import os
        import re
        from datetime import datetime, timedelta
        
        # Получаем экземпляр менеджера кеша
        cache_manager = DocumentCacheManager.get_instance()
        
        # Главный файл next_actions.md в корне [projects]
        main_next_actions_path = "[projects]/next_actions.md"
        
        # Ищем другие файлы next_actions.md в подкаталогах
        actions_files = []
        projects_dir = "[projects]"
        
        # Если указан days_back, вычисляем дату начала периода
        start_date = None
        if days_back is not None:
            start_date = datetime.now() - timedelta(days=days_back)
        
        # Добавляем главный файл next_actions.md, если он существует
        if os.path.exists(main_next_actions_path):
            actions_files.append(("main", main_next_actions_path))
        
        # Рекурсивная функция для поиска файлов next_actions.md
        def find_next_actions_files(directory):
            found_files = []
            try:
                items = os.listdir(directory)
                for item in items:
                    full_path = os.path.join(directory, item)
                    if os.path.isdir(full_path):
                        # Рекурсивно ищем в подкаталогах
                        found_files.extend(find_next_actions_files(full_path))
                    elif item == "next_actions.md" and full_path != main_next_actions_path:
                        # Извлекаем имя каталога для идентификации проекта/team
                        dir_name = os.path.basename(directory)
                        found_files.append((dir_name, full_path))
            except Exception as e:
                logger.error(f"Ошибка при сканировании директории {directory}: {e}")
            return found_files
        
        # Добавляем все найденные файлы next_actions.md
        actions_files.extend(find_next_actions_files(projects_dir))
        
        # Собираем результаты
        results = {
            "updated": datetime.now().strftime("%Y-%m-%d, %H:%M CET"),
            "projects": [],
            "total_actions": 0,
            "daily_digests": []
        }
        
        # Шаблон для поиска дат в формате "## YYYY-MM-DD" или "## DD Month YYYY"
        date_patterns = [
            r"##\s+(\d{4}-\d{2}-\d{2})",  # YYYY-MM-DD
            r"##\s+(\d{1,2}\s+(?:января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+\d{4})",  # DD Month YYYY
            r"##\s+(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})",  # DD Month YYYY (английский)
            r"##\s+(?:План на|Итоги|Расписание).*?(\d{1,2}\s+(?:января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+\d{4})"  # Названия разделов с датами
        ]
        
        # Извлечение блоков next actions из содержимого в формате "— [что делать] → @[кто делает] → до [какого времени]"
        next_action_pattern = r"—\s+(.+?)\s+→\s+@([^\s]+)\s+→\s+до\s+(.+?)$"
        
        for project, file_path in actions_files:
            try:
                # Получаем содержимое файла
                content = None
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except:
                    # Если не удалось прочитать напрямую, пробуем через кеш
                    try:
                        # Используем экземпляр cache_manager, который уже получили выше
                        content = cache_manager.get_document(file_path)
                    except Exception as e:
                        logger.error(f"Ошибка при получении документа из кэша: {e}")
                        # Пробуем прочитать напрямую еще раз
                        if os.path.exists(file_path):
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                            except Exception as e2:
                                logger.error(f"Повторная ошибка при чтении файла {file_path}: {e2}")
                                content = None
                
                if content:
                    # Обрабатываем содержимое, чтобы извлечь название проекта и метаданные
                    title = "Неизвестный проект"
                    updated_date = None
                    
                    # Ищем заголовок и дату обновления
                    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
                    if title_match:
                        title = title_match.group(1)
                    
                    updated_match = re.search(r"updated:\s+(.+)$", content, re.MULTILINE)
                    if updated_match:
                        updated_date = updated_match.group(1)
                    
                    # Извлекаем задачи по проектам
                    project_actions = []
                    project_sections = re.finditer(r"###\s+([^@\n]+)(?:\s+@([^\n]+))?", content)
                    
                    for section_match in project_sections:
                        project_name = section_match.group(1).strip()
                        responsible = section_match.group(2).strip() if section_match.group(2) else None
                        
                        # Находим конец секции (следующий заголовок ###, ## или #)
                        section_start = section_match.end()
                        section_end = content.find("###", section_start)
                        if section_end == -1:
                            section_end = content.find("##", section_start)
                        if section_end == -1:
                            section_end = content.find("#", section_start)
                        if section_end == -1:
                            section_end = len(content)
                        
                        section_content = content[section_start:section_end]
                        
                        # Ищем next actions в секции
                        actions = []
                        next_action_matches = re.finditer(next_action_pattern, section_content, re.MULTILINE)
                        
                        for action_match in next_action_matches:
                            task = action_match.group(1).strip()
                            assignee = action_match.group(2).strip()
                            deadline = action_match.group(3).strip()
                            
                            actions.append({
                                "task": task,
                                "assignee": assignee,
                                "deadline": deadline
                            })
                        
                        if actions:
                            project_actions.append({
                                "project_name": project_name,
                                "responsible": responsible,
                                "actions": actions,
                                "count": len(actions)
                            })
                    
                    # Извлекаем дневные дайджесты в обратной хронологии
                    daily_digests = []
                    
                    # Ищем все заголовки с датами
                    date_sections = []
                    for pattern in date_patterns:
                        for match in re.finditer(pattern, content, re.MULTILINE):
                            date_str = match.group(1)
                            position = match.start()
                            date_sections.append((date_str, position))
                    
                    # Сортируем секции по позиции в документе
                    date_sections.sort(key=lambda x: x[1])
                    
                    # Извлекаем содержимое каждой секции с датой
                    for i, (date_str, position) in enumerate(date_sections):
                        section_start = content.find('\n', position) + 1
                        section_end = len(content)
                        
                        # Если есть следующая секция, используем её начало как конец текущей секции
                        if i < len(date_sections) - 1:
                            section_end = date_sections[i+1][1]
                        
                        section_content = content[section_start:section_end].strip()
                        
                        # Пропускаем пустые секции
                        if not section_content:
                            continue
                        
                        # Проверяем, подходит ли дата под фильтр days_back
                        include_section = True
                        if start_date is not None:
                            # Пытаемся распарсить дату
                            try:
                                # Проверяем разные форматы
                                parsed_date = None
                                for fmt in ["%Y-%m-%d", "%d %B %Y", "%d %b %Y"]:
                                    try:
                                        parsed_date = datetime.strptime(date_str, fmt)
                                        break
                                    except:
                                        pass
                                
                                if parsed_date and parsed_date < start_date:
                                    include_section = False
                            except:
                                # Если не удалось распарсить дату, включаем секцию
                                pass
                        
                        if include_section:
                            daily_digests.append({
                                "date": date_str,
                                "content": section_content
                            })
                    
                    # Добавляем информацию о проекте в результаты
                    project_info = {
                        "name": project,
                        "title": title,
                        "path": file_path,
                        "updated": updated_date,
                        "project_actions": project_actions,
                        "total_actions": sum(p["count"] for p in project_actions)
                    }
                    
                    results["projects"].append(project_info)
                    results["total_actions"] += project_info["total_actions"]
                    
                    # Добавляем дневные дайджесты, если они есть
                    if daily_digests:
                        # Группируем дайджесты по дате
                        for digest in daily_digests:
                            results["daily_digests"].append({
                                "source": project,
                                "date": digest["date"],
                                "content": digest["content"]
                            })
            except Exception as e:
                logger.error(f"Ошибка при обработке файла {file_path}: {e}")
        
        # Сортируем дневные дайджесты в обратном хронологическом порядке
        # Это обеспечивает соответствие принципу обратной хронологии
        results["daily_digests"].sort(key=lambda x: x["date"], reverse=True)
        
        return results
    
    except Exception as e:
        logger.error(f"Ошибка при получении списка next_actions.md: {e}")
        return {
            "error": f"Internal error: {str(e)}",
            "projects": [],
            "total_actions": 0,
            "daily_digests": []
        }


def execute_task(task_data, source):
    """
    Выполняет задачу на основе контекста.
    
    Args:
        task_data: Данные задачи для выполнения
        source: Источник запроса (slack, telegram)
    
    Returns:
        Tuple[bool, str, dict]: Результат выполнения, сообщение и результаты
    """
    try:
        # Проверяем наличие обязательных полей
        required_fields = ['project', 'task_description']
        if not all(field in task_data for field in required_fields):
            return False, "Отсутствуют обязательные поля", {}
        
        project_id = task_data['project']
        task_description = task_data['task_description']
        context = task_data.get('context', '')
        
        # Получаем контекст проекта, если он не предоставлен
        if not context:
            project_context = get_project_context(project_id)
            if project_context.get('exists', False):
                context = project_context.get('content', '')
        
        # Здесь должна быть логика выполнения задачи
        # Например, вызов AI-модели для обработки задачи на основе контекста
        
        # Заглушка для демонстрации
        result = {
            "project": project_id,
            "task": task_description,
            "status": "processing",
            "message": "Задача принята в обработку"
        }
        
        return True, "Задача принята в обработку", result
    
    except Exception as e:
        logger.error(f"Ошибка при выполнении задачи: {e}")
        return False, f"Внутренняя ошибка: {str(e)}", {}


def generate_tasks(context_data, source):
    """
    Генерирует задачи на основе контекста проекта.
    
    Args:
        context_data: Данные контекста
        source: Источник запроса (slack, telegram)
    
    Returns:
        Tuple[bool, str, List[dict]]: Результат генерации, сообщение и список задач
    """
    try:
        # Проверяем наличие обязательных полей
        required_fields = ['project']
        if not all(field in context_data for field in required_fields):
            return False, "Отсутствует идентификатор проекта", []
        
        project_id = context_data['project']
        context_content = context_data.get('context', '')
        
        # Получаем контекст проекта, если он не предоставлен
        if not context_content:
            project_context = get_project_context(project_id)
            if project_context.get('exists', False):
                context_content = project_context.get('content', '')
        
        # Если контекст все еще пустой, возвращаем ошибку
        if not context_content:
            return False, f"Контекст для проекта {project_id} не найден", []
        
        # Здесь должна быть логика генерации задач на основе контекста
        # Например, вызов AI-модели для анализа контекста и создания задач
        
        # Заглушка для демонстрации
        tasks = [
            {
                "title": "Проанализировать требования проекта",
                "priority": "high",
                "project": project_id
            },
            {
                "title": "Составить план работ",
                "priority": "medium",
                "project": project_id
            },
            {
                "title": "Обновить документацию",
                "priority": "low",
                "project": project_id
            }
        ]
        
        return True, f"Сгенерировано {len(tasks)} задач для проекта {project_id}", tasks
    
    except Exception as e:
        logger.error(f"Ошибка при генерации задач: {e}")
        return False, f"Внутренняя ошибка: {str(e)}", []


# Создаем Blueprint для внешнего API
from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest, Unauthorized, NotFound
import logging
import time
from datetime import datetime

# Создаем Blueprint
external_api = Blueprint('external_api', __name__, url_prefix='/api/external')

# Настраиваем логирование
logger = logging.getLogger('external_api')

# Маршруты API

@external_api.before_request
def before_request():
    """Выполняется перед обработкой запроса."""
    # Инициализируем токены, если это еще не сделано
    if not API_TOKENS:
        initialize_api_tokens()


@external_api.route('/healthcheck', methods=['GET'])
def healthcheck():
    """Проверка работоспособности API."""
    return jsonify({
        "status": "ok",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })


@external_api.route('/context/<project_id>', methods=['GET'])
def api_get_project_context(project_id):
    """
    API-метод для получения context.md проекта.
    
    Args:
        project_id: Идентификатор проекта
    
    Returns:
        JSON с данными контекста проекта
    """
    try:
        context_data = get_project_context(project_id)
        status_code = 200 if context_data.get("exists", False) else 404
        
        return jsonify({
            "success": context_data.get("exists", False),
            "context": context_data,
            "timestamp": datetime.now().isoformat()
        }), status_code
    
    except Exception as e:
        logger.error(f"Ошибка при получении контекста проекта {project_id}: {e}")
        return jsonify({
            "success": False,
            "error": "internal_error",
            "message": "Внутренняя ошибка сервера при получении контекста проекта",
            "timestamp": datetime.now().isoformat()
        }), 500


@external_api.route('/next_actions', methods=['GET'])
def api_get_next_actions():
    """
    API-метод для получения next_actions.md со списком задач.
    
    Query Parameters:
        days_back (int, optional): Количество дней, за которые нужно получить дайджест задач
    
    Returns:
        JSON с данными next_actions.md
    """
    try:
        # Получаем параметр days_back из запроса
        days_back = request.args.get('days_back', default=None, type=int)
        
        # Получаем данные задач
        actions_data = get_next_actions(days_back)
        
        return jsonify({
            "success": True,
            "actions_data": actions_data,
            "timestamp": datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Ошибка при получении списка задач: {e}")
        return jsonify({
            "success": False,
            "error": "internal_error",
            "message": "Внутренняя ошибка сервера при получении списка задач",
            "timestamp": datetime.now().isoformat()
        }), 500


@external_api.route('/<source>/action', methods=['POST'])
def perform_action(source):
    """
    Обрабатывает запрос на выполнение действия.
    
    Args:
        source: Источник запроса (slack, telegram)
    
    Returns:
        Flask response: Результат обработки запроса
    """
    try:
        # Проверяем запрос
        verify_request(request, source)
        
        # Получаем данные запроса
        try:
            data = request.get_json()
            if not data:
                raise BadRequest("Неверный формат JSON")
        except:
            raise BadRequest("Неверный формат JSON")
        
        # Проверяем наличие действия
        action = data.get('action')
        if not action or action not in ALLOWED_ACTIONS:
            raise BadRequest(f"Неподдерживаемое действие: {action}")
        
        # Обрабатываем разные действия
        if action == 'update_context':
            # Проверяем наличие данных контекста
            context_data = data.get('context')
            if not context_data:
                raise BadRequest("Отсутствуют данные контекста")
            
            # Обрабатываем обновление контекста
            success, message = process_context_update(context_data, source)
            
            return jsonify({
                "success": success,
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
        
        elif action == 'create_task':
            # Проверяем наличие данных задачи
            task_data = data.get('task')
            if not task_data:
                raise BadRequest("Отсутствуют данные задачи")
            
            # Обрабатываем создание задачи
            success, message, task = process_task_creation(task_data, source)
            
            return jsonify({
                "success": success,
                "message": message,
                "task": task,
                "timestamp": datetime.now().isoformat()
            })
        
        elif action == 'create_incident':
            # Проверяем наличие данных инцидента
            incident_data = data.get('incident')
            if not incident_data:
                raise BadRequest("Отсутствуют данные инцидента")
            
            # Обрабатываем создание инцидента
            success, message, incident = process_incident_creation(incident_data, source)
            
            return jsonify({
                "success": success,
                "message": message,
                "incident": incident,
                "timestamp": datetime.now().isoformat()
            })
        
        elif action == 'get_project_summary':
            # Проверяем наличие идентификатора проекта
            project_id = data.get('project_id')
            if not project_id:
                raise BadRequest("Отсутствует идентификатор проекта")
            
            # Получаем данные проекта
            project_data = get_project_summary(project_id)
            
            return jsonify({
                "success": "error" not in project_data,
                "project": project_data,
                "timestamp": datetime.now().isoformat()
            })
        
        elif action == 'search':
            # Проверяем наличие поискового запроса
            query = data.get('query')
            if not query:
                raise BadRequest("Отсутствует поисковый запрос")
            
            # Получаем параметры поиска
            project = data.get('project')
            document_type = data.get('document_type')
            limit = data.get('limit', 10)
            
            # Выполняем поиск
            results = search_documents(query, project, document_type, limit)
            
            return jsonify({
                "success": True,
                "results": results,
                "count": len(results),
                "timestamp": datetime.now().isoformat()
            })
        
        # Обработка остальных действий будет добавлена по мере необходимости
        
        # Если действие не обработано (что странно, т.к. мы проверяем ALLOWED_ACTIONS)
        return jsonify({
            "success": False,
            "message": f"Действие {action} не реализовано",
            "timestamp": datetime.now().isoformat()
        })
    
    except BadRequest as e:
        logger.warning(f"Ошибка в запросе: {str(e)}")
        return jsonify({
            "success": False,
            "error": "bad_request",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 400
    
    except Unauthorized as e:
        logger.warning(f"Ошибка авторизации: {str(e)}")
        return jsonify({
            "success": False,
            "error": "unauthorized",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 401
    
    except NotFound as e:
        logger.warning(f"Ресурс не найден: {str(e)}")
        return jsonify({
            "success": False,
            "error": "not_found",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 404
    
    except Exception as e:
        logger.error(f"Внутренняя ошибка: {str(e)}")
        return jsonify({
            "success": False,
            "error": "internal_error",
            "message": "Внутренняя ошибка сервера",
            "timestamp": datetime.now().isoformat()
        }), 500


# Регистрация Blueprint в приложении
def register_external_api(app):
    """
    Регистрирует Blueprint внешнего API в приложении Flask.
    
    Args:
        app: Приложение Flask
    """
    app.register_blueprint(external_api)
    logger.info("Внешнее API зарегистрировано")


# Инициализация модуля
initialize_api_tokens()