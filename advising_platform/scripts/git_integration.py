#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль для интеграции с GitHub/GitLab.
Предоставляет функции для синхронизации стандартов с удаленным репозиторием.
"""

import os
import sys
import json
import subprocess
import shutil
import argparse
import logging
import configparser
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scripts/git_sync.log')
    ]
)

logger = logging.getLogger('git_integration')

# Чтение конфигурации
DEFAULT_CONFIG = {
    'git': {
        'repository': 'https://github.com/idkras/heroes-advising-project.git',
        'branch': 'main',
        'username': '',
        'token': '',
        'commit_message_template': 'Sync standards: {date} by {user}',
        'local_repo_path': 'git_repo'
    },
    'standards': {
        'standards_dir': 'advising standards.md',
        'backup_dir': 'backups/standards_{date}'
    }
}

def load_config(config_path='scripts/git_config.ini'):
    """Загружает конфигурацию из файла или создает файл с настройками по умолчанию."""
    config = configparser.ConfigParser()
    
    if not os.path.exists(config_path):
        # Создаем директорию, если она не существует
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # Создаем конфигурацию по умолчанию
        for section, options in DEFAULT_CONFIG.items():
            config[section] = options
        
        # Записываем в файл
        with open(config_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        
        logger.info(f"Создан файл конфигурации по умолчанию: {config_path}")
    else:
        # Загружаем существующую конфигурацию
        config.read(config_path, encoding='utf-8')
    
    return config

def git_command(cmd, cwd=None, check=True):
    """Выполняет git-команду и возвращает результат."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=check,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка выполнения git-команды: {e}")
        logger.error(f"STDERR: {e.stderr}")
        if check:
            raise
        return None

def setup_git_repo(config):
    """Настраивает локальный Git-репозиторий."""
    repo_url = config['git']['repository']
    branch = config['git']['branch']
    repo_path = config['git']['local_repo_path']
    username = config['git']['username']
    token = config['git']['token']
    
    # Формируем URL с учетом авторизации
    if username and token and 'github.com' in repo_url:
        auth_repo_url = repo_url.replace('https://', f'https://{username}:{token}@')
    else:
        auth_repo_url = repo_url
    
    if os.path.exists(repo_path):
        # Репозиторий уже существует, обновляем его
        logger.info(f"Обновление существующего репозитория: {repo_path}")
        git_command(['git', 'fetch', 'origin'], cwd=repo_path)
        git_command(['git', 'checkout', branch], cwd=repo_path)
        git_command(['git', 'pull', 'origin', branch], cwd=repo_path)
    else:
        # Клонируем репозиторий
        logger.info(f"Клонирование репозитория: {repo_url} в {repo_path}")
        git_command(['git', 'clone', '-b', branch, auth_repo_url, repo_path])
    
    return repo_path

def backup_standards(config):
    """Создает резервную копию текущих стандартов."""
    standards_dir = config['standards']['standards_dir']
    backup_dir_template = config['standards']['backup_dir']
    backup_dir = backup_dir_template.format(date=datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    
    if not os.path.exists(standards_dir):
        logger.warning(f"Директория стандартов не найдена: {standards_dir}")
        return None
    
    os.makedirs(backup_dir, exist_ok=True)
    
    logger.info(f"Создание резервной копии стандартов: {backup_dir}")
    
    # Копируем файлы
    for root, dirs, files in os.walk(standards_dir):
        # Создаем соответствующую структуру в backup_dir
        relative_path = os.path.relpath(root, standards_dir)
        backup_path = os.path.join(backup_dir, relative_path) if relative_path != '.' else backup_dir
        os.makedirs(backup_path, exist_ok=True)
        
        # Копируем все файлы
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(backup_path, file)
            shutil.copy2(src_file, dst_file)
    
    logger.info(f"Резервная копия создана: {backup_dir}")
    return backup_dir

def sync_to_git(config):
    """Синхронизирует текущие стандарты с Git-репозиторием."""
    repo_path = setup_git_repo(config)
    standards_dir = config['standards']['standards_dir']
    commit_message_template = config['git']['commit_message_template']
    username = config['git'].get('username', 'unknown')
    commit_message = commit_message_template.format(
        date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        user=username
    )
    
    # Создаем резервную копию перед синхронизацией
    backup_dir = backup_standards(config)
    if not backup_dir:
        logger.error("Не удалось создать резервную копию, отмена синхронизации")
        return False
    
    # Копируем текущие стандарты в репозиторий
    repo_standards_dir = os.path.join(repo_path, standards_dir)
    
    # Удаляем предыдущие файлы стандартов в репозитории
    if os.path.exists(repo_standards_dir):
        shutil.rmtree(repo_standards_dir)
    
    # Копируем текущие стандарты
    logger.info(f"Копирование стандартов в Git-репозиторий: {repo_standards_dir}")
    shutil.copytree(standards_dir, repo_standards_dir)
    
    # Фиксируем изменения
    logger.info("Фиксация изменений в Git")
    git_command(['git', 'add', standards_dir], cwd=repo_path)
    git_command(['git', 'commit', '-m', commit_message], cwd=repo_path, check=False)
    
    # Отправляем изменения
    logger.info("Отправка изменений в удаленный репозиторий")
    git_command(['git', 'push', 'origin', config['git']['branch']], cwd=repo_path)
    
    logger.info("Синхронизация с Git успешно выполнена")
    return True

def sync_from_git(config):
    """Получает последние стандарты из Git-репозитория."""
    repo_path = setup_git_repo(config)
    standards_dir = config['standards']['standards_dir']
    repo_standards_dir = os.path.join(repo_path, standards_dir)
    
    if not os.path.exists(repo_standards_dir):
        logger.error(f"Директория стандартов не найдена в репозитории: {repo_standards_dir}")
        return False
    
    # Создаем резервную копию перед синхронизацией
    backup_dir = backup_standards(config)
    if not backup_dir:
        logger.error("Не удалось создать резервную копию, отмена синхронизации")
        return False
    
    # Удаляем текущие стандарты
    if os.path.exists(standards_dir):
        shutil.rmtree(standards_dir)
    
    # Копируем стандарты из репозитория
    logger.info(f"Копирование стандартов из Git-репозитория: {repo_standards_dir}")
    shutil.copytree(repo_standards_dir, standards_dir)
    
    logger.info("Синхронизация из Git успешно выполнена")
    return True

def get_version_history(config, standard_name):
    """Получает историю изменений конкретного стандарта из Git."""
    repo_path = setup_git_repo(config)
    standards_dir = config['standards']['standards_dir']
    
    # Ищем все файлы, соответствующие указанному стандарту
    # (имя может меняться из-за даты и времени)
    standard_prefix = standard_name.split(' by ')[0]
    
    # Путь к директории стандартов в репозитории
    repo_standards_dir = os.path.join(repo_path, standards_dir)
    
    # Получаем список коммитов, затрагивающих этот стандарт
    git_log_cmd = [
        'git', 'log', '--pretty=format:%H|%an|%ad|%s', '--date=iso',
        '--', f'{standards_dir}/*{standard_prefix}*'
    ]
    
    log_output = git_command(git_log_cmd, cwd=repo_path, check=False)
    if not log_output:
        logger.warning(f"История изменений не найдена для стандарта: {standard_name}")
        return []
    
    # Парсим вывод git log
    history = []
    for line in log_output.split('\n'):
        if not line.strip():
            continue
        
        commit_hash, author, date, message = line.split('|', 3)
        
        # Получаем список файлов, затронутых в этом коммите
        files_cmd = ['git', 'show', '--name-only', '--pretty=format:', commit_hash]
        files_output = git_command(files_cmd, cwd=repo_path)
        
        # Фильтруем только файлы стандартов, соответствующие искомому
        standard_files = []
        for file_path in files_output.split('\n'):
            if file_path.strip() and standard_prefix in file_path:
                standard_files.append(file_path)
        
        if standard_files:
            history.append({
                'commit': commit_hash,
                'author': author,
                'date': date,
                'message': message,
                'files': standard_files
            })
    
    return history

def main():
    """Основная функция для запуска из командной строки."""
    parser = argparse.ArgumentParser(description='Интеграция стандартов с Git')
    parser.add_argument('action', choices=['push', 'pull', 'history'], 
                      help='Действие: push - отправка в Git, pull - получение из Git, history - история версий')
    parser.add_argument('--standard', help='Имя стандарта для получения истории (только для action=history)')
    parser.add_argument('--config', default='scripts/git_config.ini', help='Путь к файлу конфигурации')
    
    args = parser.parse_args()
    config = load_config(args.config)
    
    try:
        if args.action == 'push':
            success = sync_to_git(config)
            sys.exit(0 if success else 1)
        elif args.action == 'pull':
            success = sync_from_git(config)
            sys.exit(0 if success else 1)
        elif args.action == 'history':
            if not args.standard:
                logger.error("Необходимо указать имя стандарта с помощью параметра --standard")
                sys.exit(1)
            
            history = get_version_history(config, args.standard)
            print(json.dumps(history, indent=2, ensure_ascii=False))
            sys.exit(0)
    except Exception as e:
        logger.error(f"Ошибка выполнения: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()