#!/usr/bin/env python3
"""
Скрипт для консолидации задач и инцидентов.

Этот скрипт позволяет:
1. Находить и объединять дубликаты задач и инцидентов
2. Перемещать завершенные задачи в архив
3. Переносить закрытые инциденты в архив
4. Проверять и исправлять несоответствия между файлами и реестром документов
"""

import os
import re
import sys
import json
import shutil
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set, Any

# Добавляем корневую директорию в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем наш улучшенный модуль предотвращения дубликатов
from advising_platform.content_deduplication import (
    DocumentRegistry, generate_content_hash, ARCHIVE_DATE_DIR, TODO_DIR, INCIDENTS_DIR,
    extract_metadata_from_task, extract_metadata_from_incident
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('consolidation.log')
    ]
)
logger = logging.getLogger("consolidate")


def find_duplicates(registry=None, similarity_threshold=0.85):
    """
    Находит дубликаты документов.
    
    Args:
        registry: Экземпляр реестра документов (None - создать новый)
        similarity_threshold: Порог схожести для обнаружения дубликатов
        
    Returns:
        Dict[str, List[str]]: Словарь {оригинал: [дубликаты]}
    """
    if registry is None:
        registry = DocumentRegistry.get_instance()
    
    logger.info("Поиск дубликатов документов...")
    duplicates = registry.consolidate_duplicates(similarity_threshold)
    
    logger.info(f"Найдено {len(duplicates)} групп дубликатов")
    for original, dupes in duplicates.items():
        logger.info(f"Оригинал: {original}")
        for dupe in dupes:
            logger.info(f"  - Дубликат: {dupe}")
    
    return duplicates


def consolidate_duplicates(duplicates, merge_content=False, archive_duplicates=True):
    """
    Консолидирует найденные дубликаты.
    
    Args:
        duplicates: Словарь {оригинал: [дубликаты]}
        merge_content: Объединять содержимое дубликатов
        archive_duplicates: Архивировать дубликаты после консолидации
        
    Returns:
        int: Количество обработанных групп дубликатов
    """
    if not duplicates:
        logger.info("Нет дубликатов для консолидации")
        return 0
    
    # Получаем экземпляр реестра
    registry = DocumentRegistry.get_instance()
    
    # Создаем директорию архива, если её нет
    if archive_duplicates and not os.path.exists(ARCHIVE_DATE_DIR):
        os.makedirs(ARCHIVE_DATE_DIR, exist_ok=True)
    
    count = 0
    for original, dupes in duplicates.items():
        if not os.path.exists(original):
            logger.warning(f"Оригинальный файл не существует: {original}")
            continue
        
        # Получаем содержимое оригинального файла
        with open(original, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Объединяем содержимое, если требуется
        if merge_content:
            merged_content = original_content
            
            for dupe in dupes:
                if os.path.exists(dupe):
                    with open(dupe, 'r', encoding='utf-8') as f:
                        dupe_content = f.read()
                    
                    # Добавляем уникальные части содержимого
                    dupe_lines = set(dupe_content.strip().splitlines())
                    original_lines = set(original_content.strip().splitlines())
                    unique_lines = dupe_lines - original_lines
                    
                    if unique_lines:
                        merged_content += "\n\n# Дополнительное содержимое\n\n"
                        merged_content += "\n".join(unique_lines)
            
            # Записываем объединенное содержимое
            with open(original, 'w', encoding='utf-8') as f:
                f.write(merged_content)
            
            logger.info(f"Содержимое объединено в файле: {original}")
        
        # Обновляем метаданные оригинального документа
        original_type = "task" if "todo" in original.lower() else "incident"
        if original_type == "task":
            metadata = extract_metadata_from_task(original_content)
        else:
            metadata = extract_metadata_from_incident(original_content)
        
        # Архивируем дубликаты
        if archive_duplicates:
            for dupe in dupes:
                if os.path.exists(dupe):
                    # Генерируем путь в архиве
                    filename = os.path.basename(dupe)
                    archive_path = os.path.join(ARCHIVE_DATE_DIR, filename)
                    
                    # Архивируем файл
                    try:
                        # Перемещаем файл в архив через реестр
                        success, new_path = registry.archive_document(dupe, archive_path, reason="duplicate")
                        if success:
                            logger.info(f"Дубликат архивирован: {dupe} -> {new_path}")
                        else:
                            logger.warning(f"Не удалось архивировать дубликат: {dupe}")
                    except Exception as e:
                        logger.error(f"Ошибка при архивации дубликата {dupe}: {str(e)}")
        
        count += 1
    
    logger.info(f"Консолидировано {count} групп дубликатов")
    return count


def archive_completed_tasks(registry=None):
    """
    Архивирует завершенные задачи.
    
    Args:
        registry: Экземпляр реестра документов (None - создать новый)
        
    Returns:
        int: Количество архивированных задач
    """
    if registry is None:
        registry = DocumentRegistry.get_instance()
    
    # Получаем список путей к файлам задач
    task_files = []
    if os.path.exists(TODO_DIR):
        task_files = [os.path.join(TODO_DIR, f) for f in os.listdir(TODO_DIR) if f.endswith('.md')]
    
    # Проверяем директорию [todo · incidents] на наличие задач
    if os.path.exists("[todo · incidents]"):
        for f in os.listdir("[todo · incidents]"):
            if f.endswith('.md') and f.startswith('todo-'):
                task_files.append(os.path.join("[todo · incidents]", f))
    
    # Создаем директорию архива, если её нет
    if not os.path.exists(ARCHIVE_DATE_DIR):
        os.makedirs(ARCHIVE_DATE_DIR, exist_ok=True)
    
    count = 0
    for task_file in task_files:
        try:
            # Проверяем, завершена ли задача
            with open(task_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Проверяем статус задачи
            completed = False
            
            # Проверка по чекбоксу
            if re.search(r'- \[x\]', content):
                completed = True
            
            # Проверка по статусу
            if re.search(r'статус:.*выполнено|status:.*completed|статус:.*завершено', content, re.IGNORECASE):
                completed = True
            
            if completed:
                # Генерируем путь в архиве
                filename = os.path.basename(task_file)
                archive_path = os.path.join(ARCHIVE_DATE_DIR, filename)
                
                # Архивируем задачу
                success, new_path = registry.archive_document(task_file, archive_path, reason="completed")
                if success:
                    logger.info(f"Завершенная задача архивирована: {task_file} -> {new_path}")
                    count += 1
                else:
                    logger.warning(f"Не удалось архивировать завершенную задачу: {task_file}")
        except Exception as e:
            logger.error(f"Ошибка при обработке задачи {task_file}: {str(e)}")
    
    logger.info(f"Архивировано {count} завершенных задач")
    return count


def archive_closed_incidents(registry=None):
    """
    Архивирует закрытые инциденты.
    
    Args:
        registry: Экземпляр реестра документов (None - создать новый)
        
    Returns:
        int: Количество архивированных инцидентов
    """
    if registry is None:
        registry = DocumentRegistry.get_instance()
    
    # Получаем список путей к файлам инцидентов
    incident_files = []
    if os.path.exists(INCIDENTS_DIR):
        incident_files = [os.path.join(INCIDENTS_DIR, f) for f in os.listdir(INCIDENTS_DIR) if f.endswith('.md')]
    
    # Проверяем директорию [todo · incidents] на наличие инцидентов
    if os.path.exists("[todo · incidents]"):
        for f in os.listdir("[todo · incidents]"):
            if f.endswith('.md') and f.startswith('incident-'):
                incident_files.append(os.path.join("[todo · incidents]", f))
    
    # Создаем директорию архива, если её нет
    if not os.path.exists(ARCHIVE_DATE_DIR):
        os.makedirs(ARCHIVE_DATE_DIR, exist_ok=True)
    
    count = 0
    for incident_file in incident_files:
        try:
            # Проверяем, закрыт ли инцидент
            with open(incident_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Проверяем статус инцидента
            closed = False
            
            # Проверка по статусу
            if re.search(r'статус:.*закрыт|status:.*closed|статус:.*решен|статус:.*готово', content, re.IGNORECASE):
                closed = True
            
            if closed:
                # Генерируем путь в архиве
                filename = os.path.basename(incident_file)
                archive_path = os.path.join(ARCHIVE_DATE_DIR, filename)
                
                # Архивируем инцидент
                success, new_path = registry.archive_document(incident_file, archive_path, reason="closed")
                if success:
                    logger.info(f"Закрытый инцидент архивирован: {incident_file} -> {new_path}")
                    count += 1
                else:
                    logger.warning(f"Не удалось архивировать закрытый инцидент: {incident_file}")
        except Exception as e:
            logger.error(f"Ошибка при обработке инцидента {incident_file}: {str(e)}")
    
    logger.info(f"Архивировано {count} закрытых инцидентов")
    return count


def verify_registry_integrity(registry=None, fix_issues=True):
    """
    Проверяет целостность реестра документов.
    
    Args:
        registry: Экземпляр реестра документов (None - создать новый)
        fix_issues: Исправлять обнаруженные проблемы
        
    Returns:
        Dict[str, int]: Статистика проверки
    """
    if registry is None:
        registry = DocumentRegistry.get_instance()
    
    logger.info("Проверка целостности реестра документов...")
    
    # Проверяем целостность реестра
    issues = registry.verify_registry_integrity()
    
    stats = {
        "missing_files": len(issues["missing_files"]),
        "invalid_relationships": len(issues["invalid_relationships"]),
        "broken_id_mappings": len(issues["broken_id_mappings"])
    }
    
    # Выводим информацию о проблемах
    if stats["missing_files"] > 0:
        logger.warning(f"Найдено {stats['missing_files']} отсутствующих файлов:")
        for path in issues["missing_files"]:
            logger.warning(f"  - {path}")
    
    if stats["invalid_relationships"] > 0:
        logger.warning(f"Найдено {stats['invalid_relationships']} некорректных связей:")
        for source, target in issues["invalid_relationships"]:
            logger.warning(f"  - {source} -> {target}")
    
    if stats["broken_id_mappings"] > 0:
        logger.warning(f"Найдено {stats['broken_id_mappings']} поврежденных идентификаторов:")
        for logical_id, path in issues["broken_id_mappings"]:
            logger.warning(f"  - {logical_id} -> {path}")
    
    # Исправляем проблемы, если требуется
    if fix_issues:
        logger.info("Исправление проблем с целостностью реестра...")
        fixed = registry.clean_registry()
        
        logger.info(f"Исправлено проблем:")
        logger.info(f"  - Отсутствующие файлы: {fixed['missing_files']}")
        logger.info(f"  - Некорректные связи: {fixed['invalid_relationships']}")
        logger.info(f"  - Поврежденные идентификаторы: {fixed['broken_id_mappings']}")
    
    return stats


def register_missing_documents(registry=None):
    """
    Регистрирует документы, отсутствующие в реестре.
    
    Args:
        registry: Экземпляр реестра документов (None - создать новый)
        
    Returns:
        int: Количество зарегистрированных документов
    """
    if registry is None:
        registry = DocumentRegistry.get_instance()
    
    logger.info("Поиск незарегистрированных документов...")
    
    # Проверяем директории
    directories = [TODO_DIR, INCIDENTS_DIR]
    if os.path.exists("[todo · incidents]"):
        directories.append("[todo · incidents]")
    
    count = 0
    for directory in directories:
        if not os.path.exists(directory):
            continue
        
        for filename in os.listdir(directory):
            if not filename.endswith('.md'):
                continue
            
            file_path = os.path.join(directory, filename)
            
            # Проверяем, зарегистрирован ли документ
            if file_path not in registry.documents:
                try:
                    # Определяем тип документа
                    if "todo" in filename.lower():
                        document_type = "task"
                    elif "incident" in filename.lower():
                        document_type = "incident"
                    else:
                        continue
                    
                    # Читаем содержимое
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Регистрируем документ
                    registry.register_document(file_path, document_type, content)
                    logger.info(f"Зарегистрирован документ: {file_path}")
                    count += 1
                except Exception as e:
                    logger.error(f"Ошибка при регистрации документа {file_path}: {str(e)}")
    
    logger.info(f"Зарегистрировано {count} новых документов")
    return count


def update_registry_statistics(registry=None):
    """
    Обновляет и выводит статистику реестра документов.
    
    Args:
        registry: Экземпляр реестра документов (None - создать новый)
        
    Returns:
        Dict[str, Any]: Статистика реестра
    """
    if registry is None:
        registry = DocumentRegistry.get_instance()
    
    stats = registry.get_statistics()
    
    logger.info("Статистика реестра документов:")
    logger.info(f"Всего документов: {stats['total_documents']}")
    
    logger.info("По типам:")
    for doc_type, count in stats.get("by_type", {}).items():
        logger.info(f"  - {doc_type}: {count}")
    
    logger.info("По статусам:")
    for status, count in stats.get("by_status", {}).items():
        logger.info(f"  - {status}: {count}")
    
    logger.info(f"Количество связей: {stats.get('relationships', 0)}")
    logger.info(f"Логических идентификаторов: {stats.get('logical_ids', 0)}")
    logger.info(f"Средняя версия: {stats.get('average_version', 1):.2f}")
    logger.info(f"Документов с историей: {stats.get('documents_with_history', 0)}")
    
    return stats


def main():
    """Основная функция скрипта."""
    parser = argparse.ArgumentParser(description='Консолидация задач и инцидентов')
    
    parser.add_argument('--find-duplicates', action='store_true',
                        help='Найти дубликаты документов')
    parser.add_argument('--consolidate', action='store_true',
                        help='Консолидировать найденные дубликаты')
    parser.add_argument('--merge-content', action='store_true',
                        help='Объединять содержимое дубликатов при консолидации')
    parser.add_argument('--archive-duplicates', action='store_true',
                        help='Архивировать дубликаты после консолидации')
    parser.add_argument('--archive-completed', action='store_true',
                        help='Архивировать завершенные задачи')
    parser.add_argument('--archive-closed', action='store_true',
                        help='Архивировать закрытые инциденты')
    parser.add_argument('--verify-registry', action='store_true',
                        help='Проверить целостность реестра документов')
    parser.add_argument('--fix-registry', action='store_true',
                        help='Исправить проблемы с целостностью реестра')
    parser.add_argument('--register-missing', action='store_true',
                        help='Зарегистрировать отсутствующие в реестре документы')
    parser.add_argument('--show-stats', action='store_true',
                        help='Показать статистику реестра документов')
    parser.add_argument('--all', action='store_true',
                        help='Выполнить все операции')
    parser.add_argument('--similarity-threshold', type=float, default=0.85,
                        help='Порог схожести для обнаружения дубликатов (0.0-1.0)')
    
    args = parser.parse_args()
    
    # Если не указаны опции, выполняем все операции
    if not any([
        args.find_duplicates, args.consolidate, args.archive_completed, 
        args.archive_closed, args.verify_registry, args.fix_registry,
        args.register_missing, args.show_stats, args.all
    ]):
        args.all = True
    
    # Получаем экземпляр реестра
    registry = DocumentRegistry.get_instance()
    
    # Регистрируем отсутствующие документы, если требуется
    if args.register_missing or args.all:
        register_missing_documents(registry)
    
    # Проверяем целостность реестра, если требуется
    if args.verify_registry or args.fix_registry or args.all:
        verify_registry_integrity(registry, fix_issues=args.fix_registry or args.all)
    
    # Находим дубликаты, если требуется
    duplicates = None
    if args.find_duplicates or args.consolidate or args.all:
        duplicates = find_duplicates(registry, args.similarity_threshold)
    
    # Консолидируем дубликаты, если требуется
    if (args.consolidate or args.all) and duplicates:
        consolidate_duplicates(duplicates, args.merge_content, args.archive_duplicates or args.all)
    
    # Архивируем завершенные задачи, если требуется
    if args.archive_completed or args.all:
        archive_completed_tasks(registry)
    
    # Архивируем закрытые инциденты, если требуется
    if args.archive_closed or args.all:
        archive_closed_incidents(registry)
    
    # Выводим статистику реестра, если требуется
    if args.show_stats or args.all:
        update_registry_statistics(registry)
    
    logger.info("Консолидация завершена")


if __name__ == "__main__":
    main()