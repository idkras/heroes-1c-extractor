#!/usr/bin/env python3
"""
Скрипт для автоматизации работы с context.md и next_actions.md через API.

Этот скрипт позволяет:
1. Добавлять новые записи в context.md проектов
2. Добавлять задачи в next_actions.md
3. Проверять соответствие структуры документов стандартам
4. Работать с проектами через их идентификаторы

Для использования:
- context_tools.py add-context PROJECT_ID "Содержание контекста" --author "Автор" --date "2025-05-16"
- context_tools.py add-action PROJECT_ID "Задача" --assignee "@username" --deadline "до 2025-05-25"
- context_tools.py validate PROJECT_ID --standard "client_context"
"""

import os
import sys
import json
import argparse
import requests
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('context_tools')

# Конфигурация
API_BASE_URL = "http://localhost:5003/api/v1/external"
CONFIG_FILE = os.path.expanduser("~/.context_tools_config.json")

def load_config():
    """Загружает конфигурацию из файла."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка при загрузке конфигурации: {e}")
    
    # Возвращаем конфигурацию по умолчанию
    return {
        "api_url": API_BASE_URL,
        "api_token": None,
        "default_author": "Context Tools Script"
    }

def save_config(config):
    """Сохраняет конфигурацию в файл."""
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Ошибка при сохранении конфигурации: {e}")
        return False

def format_date(date_str=None):
    """Форматирует дату в соответствии со стандартом."""
    if not date_str:
        now = datetime.now()
        return now.strftime("%Y-%m-%d")
    return date_str

def add_context_entry(project_id, content, author=None, date=None, config=None):
    """
    Добавляет запись в context.md проекта.
    
    Args:
        project_id: Идентификатор проекта
        content: Содержание записи
        author: Автор записи
        date: Дата записи
        config: Конфигурация
    
    Returns:
        bool: True, если добавление успешно, иначе False
    """
    if config is None:
        config = load_config()
    
    api_url = f"{config['api_url']}/context/{project_id}"
    
    # Форматирование даты
    formatted_date = format_date(date)
    
    # Автор записи
    if not author:
        author = config.get("default_author", "Context Tools Script")
    
    # Подготавливаем данные для запроса
    data = {
        "action": "add_entry",
        "content": content,
        "author": author,
        "date": formatted_date
    }
    
    # Добавляем токен API, если он есть
    headers = {}
    if config.get("api_token"):
        headers["Authorization"] = f"Bearer {config['api_token']}"
    
    try:
        response = requests.post(api_url, json=data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Запись успешно добавлена в контекст проекта {project_id}")
            logger.info(f"URL: {result.get('context_url', 'Недоступно')}")
            return True
        else:
            logger.error(f"Ошибка при добавлении записи: {response.status_code}")
            logger.error(f"Ответ: {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"Ошибка при отправке запроса: {e}")
        return False

def add_next_action(project_id, task, assignee=None, deadline=None, config=None):
    """
    Добавляет задачу в next_actions.md.
    
    Args:
        project_id: Идентификатор проекта
        task: Описание задачи
        assignee: Ответственный за задачу
        deadline: Срок выполнения
        config: Конфигурация
    
    Returns:
        bool: True, если добавление успешно, иначе False
    """
    if config is None:
        config = load_config()
    
    api_url = f"{config['api_url']}/next_actions"
    
    # Подготавливаем данные для запроса
    data = {
        "action": "add_task",
        "project_id": project_id,
        "task": task
    }
    
    if assignee:
        data["assignee"] = assignee
    
    if deadline:
        data["deadline"] = deadline
    
    # Добавляем токен API, если он есть
    headers = {}
    if config.get("api_token"):
        headers["Authorization"] = f"Bearer {config['api_token']}"
    
    try:
        response = requests.post(api_url, json=data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Задача успешно добавлена в next_actions.md")
            logger.info(f"URL: {result.get('actions_url', 'Недоступно')}")
            return True
        else:
            logger.error(f"Ошибка при добавлении задачи: {response.status_code}")
            logger.error(f"Ответ: {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"Ошибка при отправке запроса: {e}")
        return False

def validate_document_structure(project_id, standard_type, config=None):
    """
    Проверяет соответствие структуры документа стандартам.
    
    Args:
        project_id: Идентификатор проекта
        standard_type: Тип стандарта (client_context, next_actions)
        config: Конфигурация
    
    Returns:
        dict: Результаты проверки
    """
    if config is None:
        config = load_config()
    
    api_url = f"{config['api_url']}/validate"
    
    # Подготавливаем данные для запроса
    data = {
        "project_id": project_id,
        "standard_type": standard_type
    }
    
    # Добавляем токен API, если он есть
    headers = {}
    if config.get("api_token"):
        headers["Authorization"] = f"Bearer {config['api_token']}"
    
    try:
        response = requests.post(api_url, json=data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("valid", False):
                logger.info(f"Документ соответствует стандарту {standard_type}")
            else:
                logger.warning(f"Документ НЕ соответствует стандарту {standard_type}")
                for issue in result.get("issues", []):
                    logger.warning(f"- {issue}")
            
            return result
        else:
            logger.error(f"Ошибка при проверке документа: {response.status_code}")
            logger.error(f"Ответ: {response.text}")
            return {"valid": False, "error": response.text}
    
    except Exception as e:
        logger.error(f"Ошибка при отправке запроса: {e}")
        return {"valid": False, "error": str(e)}

def configure(args):
    """Настраивает конфигурацию скрипта."""
    config = load_config()
    
    if args.api_url:
        config["api_url"] = args.api_url
    
    if args.api_token:
        config["api_token"] = args.api_token
    
    if args.default_author:
        config["default_author"] = args.default_author
    
    if save_config(config):
        logger.info("Конфигурация сохранена успешно")
        logger.info(f"API URL: {config['api_url']}")
        logger.info(f"Default Author: {config['default_author']}")
        logger.info(f"API Token: {'Установлен' if config.get('api_token') else 'Не установлен'}")
    else:
        logger.error("Ошибка при сохранении конфигурации")

def main():
    """Основная функция скрипта."""
    parser = argparse.ArgumentParser(description='Инструменты для работы с context.md и next_actions.md')
    subparsers = parser.add_subparsers(dest='command', help='Команды')
    
    # Команда add-context
    add_context_parser = subparsers.add_parser('add-context', help='Добавить запись в context.md')
    add_context_parser.add_argument('project_id', help='Идентификатор проекта')
    add_context_parser.add_argument('content', help='Содержание записи')
    add_context_parser.add_argument('--author', help='Автор записи')
    add_context_parser.add_argument('--date', help='Дата записи (YYYY-MM-DD)')
    
    # Команда add-action
    add_action_parser = subparsers.add_parser('add-action', help='Добавить задачу в next_actions.md')
    add_action_parser.add_argument('project_id', help='Идентификатор проекта')
    add_action_parser.add_argument('task', help='Описание задачи')
    add_action_parser.add_argument('--assignee', help='Ответственный за задачу')
    add_action_parser.add_argument('--deadline', help='Срок выполнения')
    
    # Команда validate
    validate_parser = subparsers.add_parser('validate', help='Проверить соответствие документа стандартам')
    validate_parser.add_argument('project_id', help='Идентификатор проекта')
    validate_parser.add_argument('--standard', required=True, choices=['client_context', 'next_actions'], 
                                help='Тип стандарта для проверки')
    
    # Команда config
    config_parser = subparsers.add_parser('config', help='Настроить параметры скрипта')
    config_parser.add_argument('--api-url', help='URL API')
    config_parser.add_argument('--api-token', help='Токен API')
    config_parser.add_argument('--default-author', help='Автор по умолчанию')
    
    # Парсим аргументы
    args = parser.parse_args()
    
    # Загружаем конфигурацию
    config = load_config()
    
    # Выполняем команду
    if args.command == 'add-context':
        success = add_context_entry(args.project_id, args.content, args.author, args.date, config)
        sys.exit(0 if success else 1)
    
    elif args.command == 'add-action':
        success = add_next_action(args.project_id, args.task, args.assignee, args.deadline, config)
        sys.exit(0 if success else 1)
    
    elif args.command == 'validate':
        result = validate_document_structure(args.project_id, args.standard, config)
        sys.exit(0 if result.get("valid", False) else 1)
    
    elif args.command == 'config':
        configure(args)
        sys.exit(0)
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()