#!/usr/bin/env python3
"""
Скрипт для миграции оставшихся файлов из корневой директории в соответствующие директории в advising_platform.

Категории файлов для перемещения:
1. Log файлы (.log) - перемещаются в advising_platform/data/logs/
2. JSON файлы - перемещаются в advising_platform/data/json/
3. Python скрипты - создаются переадресации, а сами скрипты перемещаются в соответствующие директории
"""

import os
import shutil
import logging
from datetime import datetime
import json

# Настройка логирования
log_dir = os.path.join('advising_platform', 'data', 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'root_files_migration.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('root_files_migrator')

# Создаем директории для хранения файлов
json_dir = os.path.join('advising_platform', 'data', 'json')
os.makedirs(json_dir, exist_ok=True)


def create_redirector(original_path, new_path):
    """Создает файл-переадресацию в оригинальном местоположении файла."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    redirector_content = f"""# Файл перемещен
# {timestamp}

Этот файл был перемещен в новое расположение в рамках реорганизации проекта.

Новый путь: {new_path}

Для доступа к актуальным данным используйте новый путь.
"""
    with open(original_path, 'w') as f:
        f.write(redirector_content)
    
    logger.info(f"Создан файл-переадресация: {original_path} -> {new_path}")


def migrate_log_files():
    """Перемещает файлы логов из корневой директории в advising_platform/data/logs/"""
    log_files = [f for f in os.listdir('.') if f.endswith('.log') and os.path.isfile(f)]
    
    for log_file in log_files:
        source_path = log_file
        target_path = os.path.join(log_dir, log_file)
        
        # Если файл уже существует в целевой директории, добавляем timestamp к имени
        if os.path.exists(target_path):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_name, file_ext = os.path.splitext(log_file)
            target_path = os.path.join(log_dir, f"{file_name}_{timestamp}{file_ext}")
        
        # Копируем файл
        shutil.copy2(source_path, target_path)
        logger.info(f"Скопирован лог-файл: {source_path} -> {target_path}")
        
        # Создаем файл-переадресацию
        create_redirector(source_path, target_path)


def migrate_json_files():
    """Перемещает JSON файлы из корневой директории в advising_platform/data/json/"""
    json_files = [f for f in os.listdir('.') if f.endswith('.json') and os.path.isfile(f) and not f.startswith('.')]
    
    for json_file in json_files:
        source_path = json_file
        target_path = os.path.join(json_dir, json_file)
        
        # Если файл уже существует в целевой директории, добавляем timestamp к имени
        if os.path.exists(target_path):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_name, file_ext = os.path.splitext(json_file)
            target_path = os.path.join(json_dir, f"{file_name}_{timestamp}{file_ext}")
        
        # Копируем файл
        shutil.copy2(source_path, target_path)
        logger.info(f"Скопирован JSON-файл: {source_path} -> {target_path}")
        
        # Создаем файл-переадресацию
        create_redirector(source_path, target_path)


def migrate_python_scripts():
    """
    Перемещает Python скрипты из корневой директории в соответствующие директории
    и создает файлы-переадресации.
    """
    script_mappings = {
        'process_incidents.py': os.path.join('advising_platform', 'scripts', 'incidents', 'process_incidents.py'),
        'test_bidirectional_sync.py': os.path.join('advising_platform', 'scripts', 'tests', 'test_bidirectional_sync.py')
    }
    
    for source_script, target_script in script_mappings.items():
        if not os.path.isfile(source_script):
            logger.warning(f"Исходный скрипт не найден: {source_script}")
            continue
        
        # Создаем директорию для целевого скрипта, если она не существует
        target_dir = os.path.dirname(target_script)
        os.makedirs(target_dir, exist_ok=True)
        
        # Копируем скрипт
        shutil.copy2(source_script, target_script)
        logger.info(f"Скопирован Python-скрипт: {source_script} -> {target_script}")
        
        # Создаем файл-переадресацию
        redirect_content = f"""#!/usr/bin/env python3
\"\"\"
Файл-переадресация для совместимости с существующими скриптами.
Основная реализация перемещена в {target_script}
\"\"\"

import os
import sys
import importlib.util

try:
    # Добавляем корневую директорию в sys.path, если её нет
    root_dir = os.path.dirname(os.path.abspath(__file__))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)

    # Импортируем модуль из нового местоположения
    target_path = "{target_script}"
    module_name = os.path.basename(target_path).replace('.py', '')
    
    spec = importlib.util.spec_from_file_location(module_name, target_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Перенаправляем выполнение на импортированный модуль
    if hasattr(module, 'main') and callable(module.main):
        module.main()
    
except Exception as e:
    print(f"Ошибка при перенаправлении на {target_script}: {{e}}")
    print(f"Используйте напрямую: python {target_script}")
    sys.exit(1)
"""
        
        with open(source_script, 'w') as f:
            f.write(redirect_content)
        
        # Делаем скрипт исполняемым
        os.chmod(source_script, 0o755)
        
        logger.info(f"Создан файл-переадресация для скрипта: {source_script}")


def main():
    """Основная функция для запуска миграции файлов."""
    logger.info("Начинаем миграцию файлов из корневой директории...")
    
    # Создаем необходимые директории
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(json_dir, exist_ok=True)
    
    # Миграция файлов
    migrate_log_files()
    migrate_json_files()
    migrate_python_scripts()
    
    logger.info("Миграция файлов успешно завершена!")


if __name__ == "__main__":
    main()