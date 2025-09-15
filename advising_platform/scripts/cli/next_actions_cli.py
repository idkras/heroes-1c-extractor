#!/usr/bin/env python3
"""
Утилита командной строки для работы с next_actions.md.

Позволяет добавлять, редактировать и управлять задачами в next_actions.md
с соблюдением принципа обратной хронологии, согласно обновленному
Client Context Standard v2.2.

Использование:
    next_actions_cli.py add-daily-digest --date "YYYY-MM-DD" [--project "project_id"]
    next_actions_cli.py add-task "Описание задачи" --assignee "@username" --deadline "до YYYY-MM-DD" [--project "project_id"]
    next_actions_cli.py check-chronology [--project "project_id"]
"""

import os
import sys
import re
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
logger = logging.getLogger('next_actions_cli')

# Конфигурация
API_BASE_URL = "http://localhost:5003/api/v1/external"
CONFIG_FILE = os.path.expanduser("~/.next_actions_cli_config.json")
DEFAULT_PROJECT = "main"  # Используется для main next_actions.md в корне projects/

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
        "default_author": "Next Actions CLI"
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

def add_daily_digest(date=None, project_id=None, config=None):
    """
    Добавляет дневной дайджест в next_actions.md.
    
    Args:
        date: Дата дайджеста
        project_id: Идентификатор проекта
        config: Конфигурация
    
    Returns:
        bool: True, если добавление успешно, иначе False
    """
    if config is None:
        config = load_config()
    
    if project_id is None:
        project_id = DEFAULT_PROJECT
    
    api_url = f"{config['api_url']}/next_actions"
    
    # Форматирование даты
    formatted_date = format_date(date)
    
    # Подготавливаем данные для запроса
    data = {
        "action": "add_daily_digest",
        "project_id": project_id,
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
            logger.info(f"Дневной дайджест на {formatted_date} успешно добавлен в next_actions.md")
            logger.info(f"URL: {result.get('actions_url', 'Недоступно')}")
            return True
        else:
            logger.error(f"Ошибка при добавлении дневного дайджеста: {response.status_code}")
            logger.error(f"Ответ: {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"Ошибка при отправке запроса: {e}")
        return False

def add_task(task, assignee=None, deadline=None, project_id=None, config=None):
    """
    Добавляет задачу в next_actions.md.
    
    Args:
        task: Описание задачи
        assignee: Ответственный за задачу
        deadline: Срок выполнения
        project_id: Идентификатор проекта
        config: Конфигурация
    
    Returns:
        bool: True, если добавление успешно, иначе False
    """
    if config is None:
        config = load_config()
    
    if project_id is None:
        project_id = DEFAULT_PROJECT
    
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

def check_chronology(project_id=None, config=None):
    """
    Проверяет соблюдение обратной хронологии в next_actions.md.
    
    Args:
        project_id: Идентификатор проекта
        config: Конфигурация
    
    Returns:
        bool: True, если хронология соблюдена, иначе False
    """
    if config is None:
        config = load_config()
    
    if project_id is None:
        project_id = DEFAULT_PROJECT
    
    api_url = f"{config['api_url']}/next_actions"
    if project_id != DEFAULT_PROJECT:
        api_url += f"?project_id={project_id}"
    
    # Добавляем токен API, если он есть
    headers = {}
    if config.get("api_token"):
        headers["Authorization"] = f"Bearer {config['api_token']}"
    
    try:
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            daily_digests = result.get("actions_data", {}).get("daily_digests", [])
            
            # Проверяем обратную хронологию
            if daily_digests:
                is_chronological = True
                prev_date = None
                
                for digest in daily_digests:
                    current_date = digest.get("date", "")
                    
                    if prev_date is not None and current_date > prev_date:
                        logger.error(f"Нарушение обратной хронологии: {prev_date} перед {current_date}")
                        is_chronological = False
                    
                    prev_date = current_date
                
                if is_chronological:
                    logger.info("Обратная хронология соблюдена (новые записи вверху)")
                else:
                    logger.warning("Обнаружено нарушение обратной хронологии!")
                
                return is_chronological
            else:
                logger.warning("Не найдены дневные дайджесты для проверки хронологии")
                return True
        else:
            logger.error(f"Ошибка при получении данных next_actions.md: {response.status_code}")
            logger.error(f"Ответ: {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"Ошибка при отправке запроса: {e}")
        return False

def configure(args):
    """Настраивает конфигурацию скрипта."""
    config = load_config()
    
    if args.api_url:
        config["api_url"] = args.api_url
    
    if args.api_token:
        config["api_token"] = args.api_token
    
    if args.default_project:
        config["default_project"] = args.default_project
    
    if save_config(config):
        logger.info("Конфигурация сохранена успешно")
        logger.info(f"API URL: {config['api_url']}")
        logger.info(f"Default Project: {config.get('default_project', DEFAULT_PROJECT)}")
        logger.info(f"API Token: {'Установлен' if config.get('api_token') else 'Не установлен'}")
    else:
        logger.error("Ошибка при сохранении конфигурации")

def main():
    """Основная функция скрипта."""
    parser = argparse.ArgumentParser(description='Утилита для работы с next_actions.md')
    subparsers = parser.add_subparsers(dest='command', help='Команды')
    
    # Команда add-daily-digest
    add_digest_parser = subparsers.add_parser('add-daily-digest', help='Добавить дневной дайджест')
    add_digest_parser.add_argument('--date', help='Дата дайджеста (YYYY-MM-DD)')
    add_digest_parser.add_argument('--project', help='Идентификатор проекта')
    
    # Команда add-task
    add_task_parser = subparsers.add_parser('add-task', help='Добавить задачу')
    add_task_parser.add_argument('task', help='Описание задачи')
    add_task_parser.add_argument('--assignee', help='Ответственный за задачу')
    add_task_parser.add_argument('--deadline', help='Срок выполнения')
    add_task_parser.add_argument('--project', help='Идентификатор проекта')
    
    # Команда check-chronology
    check_parser = subparsers.add_parser('check-chronology', help='Проверить обратную хронологию')
    check_parser.add_argument('--project', help='Идентификатор проекта')
    
    # Команда config
    config_parser = subparsers.add_parser('config', help='Настроить параметры скрипта')
    config_parser.add_argument('--api-url', help='URL API')
    config_parser.add_argument('--api-token', help='Токен API')
    config_parser.add_argument('--default-project', help='Проект по умолчанию')
    
    # Парсим аргументы
    args = parser.parse_args()
    
    # Загружаем конфигурацию
    config = load_config()
    
    # Выполняем команду
    if args.command == 'add-daily-digest':
        success = add_daily_digest(args.date, args.project, config)
        sys.exit(0 if success else 1)
    
    elif args.command == 'add-task':
        success = add_task(args.task, args.assignee, args.deadline, args.project, config)
        sys.exit(0 if success else 1)
    
    elif args.command == 'check-chronology':
        success = check_chronology(args.project, config)
        sys.exit(0 if success else 1)
    
    elif args.command == 'config':
        configure(args)
        sys.exit(0)
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()