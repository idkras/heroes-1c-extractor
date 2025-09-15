#!/usr/bin/env python3
"""
Скрипт для создания тестовых файлов с дублирующимся кодом и запуска проверки.
"""

import os
import sys
import logging
import traceback
from datetime import datetime

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Импортируем необходимые модули
try:
    from advising_platform.src.core.registry.trigger_handler import (
        TriggerHandler, TriggerType, TriggerContext, get_handler
    )
    from advising_platform.src.tools.reporting.report_interface import report_progress
    
    logger.info("Модули триггеров успешно импортированы")
except ImportError as e:
    logger.error(f"Не удалось импортировать модули триггеров: {e}")
    sys.exit(1)

def create_test_code_files():
    """
    Создает тестовые файлы с дублирующимся кодом и активирует триггер проверки.
    """
    # Создаем временную директорию для тестовых файлов
    test_code_dir = "test_code"
    os.makedirs(test_code_dir, exist_ok=True)
    
    # Создаем несколько файлов с дублирующимся кодом
    file_paths = []
    
    # Файл 1
    file1_path = os.path.join(test_code_dir, "test_code1.py")
    file1_content = """#!/usr/bin/env python3
\"\"\"
Тестовый файл 1 для проверки обнаружения дублирования кода.
\"\"\"
import re
import logging

logger = logging.getLogger(__name__)

def parse_document(file_path: str) -> dict:
    \"\"\"
    Парсит документ и извлекает его содержимое.
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        dict: Словарь с содержимым документа
    \"\"\"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Извлекаем заголовок
        title = ""
        title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        if title_match:
            title = title_match.group(1)
            
        # Извлекаем описание
        description = ""
        desc_match = re.search(r'^## Описание\\s+(.+?)(?=\\s*^##|\\s*$)', content, re.MULTILINE | re.DOTALL)
        if desc_match:
            description = desc_match.group(1).strip()
            
        # Извлекаем статус
        status = ""
        status_match = re.search(r'^## Статус: (.+)$', content, re.MULTILINE)
        if status_match:
            status = status_match.group(1)
            
        # Формируем результат
        result = {
            "title": title,
            "description": description,
            "status": status,
            "file_path": file_path
        }
        
        return result
    except Exception as e:
        logger.error(f"Ошибка при парсинге документа {file_path}: {e}")
        return None

def process_document(file_path: str) -> bool:
    \"\"\"
    Обрабатывает документ.
    
    Args:
        file_path: Путь к документу
        
    Returns:
        bool: True, если обработка успешна, иначе False
    \"\"\"
    try:
        document = parse_document(file_path)
        if not document:
            return False
            
        # Обработка документа
        print(f"Обработка документа {document['title']}")
        
        return True
    except Exception as e:
        print(f"Ошибка при обработке документа {file_path}: {e}")
        return False
"""
    
    with open(file1_path, 'w', encoding='utf-8') as f:
        f.write(file1_content)
    
    file_paths.append(file1_path)
    
    # Файл 2
    file2_path = os.path.join(test_code_dir, "test_code2.py")
    file2_content = """#!/usr/bin/env python3
\"\"\"
Тестовый файл 2 для проверки обнаружения дублирования кода.
\"\"\"
import re
import logging

logger = logging.getLogger(__name__)

def extract_document_data(file_path: str) -> dict:
    \"\"\"
    Извлекает данные из документа.
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        dict: Словарь с данными документа
    \"\"\"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Извлекаем заголовок
        title = ""
        title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        if title_match:
            title = title_match.group(1)
            
        # Извлекаем описание
        description = ""
        desc_match = re.search(r'^## Описание\\s+(.+?)(?=\\s*^##|\\s*$)', content, re.MULTILINE | re.DOTALL)
        if desc_match:
            description = desc_match.group(1).strip()
            
        # Извлекаем статус
        status = ""
        status_match = re.search(r'^## Статус: (.+)$', content, re.MULTILINE)
        if status_match:
            status = status_match.group(1)
            
        # Формируем результат
        result = {
            "title": title,
            "description": description,
            "status": status,
            "file_path": file_path
        }
        
        return result
    except Exception as e:
        logger.error(f"Ошибка при извлечении данных из документа {file_path}: {e}")
        return None

def analyze_document(file_path: str) -> dict:
    \"\"\"
    Анализирует документ.
    
    Args:
        file_path: Путь к документу
        
    Returns:
        dict: Результаты анализа
    \"\"\"
    try:
        document = extract_document_data(file_path)
        if not document:
            return {}
            
        # Анализируем документ
        print(f"Анализ документа {document['title']}")
        
        return {
            "title": document["title"],
            "status": document["status"],
            "analyzed": True
        }
    except Exception as e:
        print(f"Ошибка при анализе документа {file_path}: {e}")
        return {}
"""
    
    with open(file2_path, 'w', encoding='utf-8') as f:
        f.write(file2_content)
    
    file_paths.append(file2_path)
    
    logger.info(f"Созданы тестовые файлы с дублирующимся кодом: {file_paths}")
    
    # Вызываем обработчик триггеров для проверки кода
    handler = get_handler(report_progress_func=report_progress)
    
    # Создаем контекст триггера для проверки кода
    context = TriggerContext(
        trigger_type=TriggerType.PERIODIC_CHECK,
        data={
            "check_type": "code_duplication",
            "file_paths": file_paths
        },
        source="test_script"
    )
    
    # Запускаем триггер
    try:
        result = handler.handle_trigger(context)
        
        if result.success:
            # Получаем информацию о дублированиях из результата
            duplications = result.data.get('duplications', [])
            logger.info(f"Проверка кода успешно выполнена: {len(duplications)} дубликатов найдено")
            return True, file_paths, duplications
        else:
            logger.warning(f"Проверка кода не была успешно выполнена: {result.message}")
            return False, file_paths, []
    except Exception as e:
        logger.error(f"Ошибка при проверке кода: {e}")
        traceback.print_exc()
        return False, file_paths, []

def cleanup_files(file_paths):
    """
    Удаляет созданные тестовые файлы.
    
    Args:
        file_paths: Список путей к файлам
    """
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Удален тестовый файл: {file_path}")
        except Exception as e:
            logger.error(f"Ошибка при удалении файла {file_path}: {e}")
    
    # Удаляем тестовую директорию, если она пуста
    test_code_dir = "test_code"
    try:
        if os.path.exists(test_code_dir) and not os.listdir(test_code_dir):
            os.rmdir(test_code_dir)
            logger.info(f"Удалена тестовая директория: {test_code_dir}")
    except Exception as e:
        logger.error(f"Ошибка при удалении директории {test_code_dir}: {e}")

if __name__ == "__main__":
    success, file_paths, duplications = create_test_code_files()
    
    if success:
        print(f"✅ Проверка дублирования кода успешно выполнена: {len(duplications)} дубликатов найдено")
        for i, duplication in enumerate(duplications):
            print(f"\nДубликат #{i+1}:")
            print(f"Файл 1: {duplication.get('file1', '')}")
            print(f"Файл 2: {duplication.get('file2', '')}")
            print(f"Похожесть: {duplication.get('similarity', 0):.2f}%")
            print(f"Строки 1: {duplication.get('start_line1', 0)}-{duplication.get('end_line1', 0)}")
            print(f"Строки 2: {duplication.get('start_line2', 0)}-{duplication.get('end_line2', 0)}")
    else:
        print("❌ Ошибка при проверке дублирования кода")
    
    # Спрашиваем, нужно ли удалить тестовые файлы
    answer = input("\nУдалить тестовые файлы? (y/n): ")
    if answer.lower() == 'y':
        cleanup_files(file_paths)
        print("Тестовые файлы удалены")
    else:
        print(f"Тестовые файлы сохранены в директории: {os.path.dirname(file_paths[0])}")