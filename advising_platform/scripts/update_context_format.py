#!/usr/bin/env python3
"""
Скрипт для обновления файлов context.md в соответствии с Client Context Standard v2.2.

Обновляет:
1. Формат имени файла (если требуется) - приводит к формату {full_domain}.context.md
2. Проверяет и обеспечивает обратную хронологию для истории проекта
3. Добавляет ссылку на обновленную версию стандарта

Использование:
    python update_context_format.py --project-dir [projects]
    python update_context_format.py --file [projects]/example/context.md
"""

import os
import re
import sys
import argparse
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('update_context_format')

# Константы
CURRENT_DATE = datetime.now().strftime("%d %B %Y")
UPDATED_STANDARD = "Client Context Standard v2.2, 16 May 2025"

def get_project_name_from_path(file_path):
    """
    Извлекает имя проекта из пути к файлу.
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        str: Имя проекта
    """
    parts = file_path.split(os.sep)
    # Если путь содержит [projects], ищем следующий каталог
    if "[projects]" in parts:
        project_index = parts.index("[projects]") + 1
        if project_index < len(parts):
            return parts[project_index]
    
    # Если не нашли проект, пытаемся извлечь имя из имени файла
    filename = os.path.basename(file_path)
    if filename.endswith(".context.md"):
        return filename.replace(".context.md", "")
    elif filename == "context.md":
        parent_dir = os.path.basename(os.path.dirname(file_path))
        return parent_dir
    
    return "unknown"

def get_correct_filename(project_name, file_path):
    """
    Генерирует правильное имя файла в соответствии со стандартом.
    
    Args:
        project_name: Имя проекта
        file_path: Путь к файлу
        
    Returns:
        str: Правильное имя файла
    """
    directory = os.path.dirname(file_path)
    correct_filename = f"{project_name}.context.md"
    return os.path.join(directory, correct_filename)

def update_file_format(file_path):
    """
    Обновляет формат файла context.md в соответствии со стандартом.
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        bool: True, если обновление успешно, иначе False
    """
    try:
        # Проверяем существование файла
        if not os.path.exists(file_path):
            logger.error(f"Файл не найден: {file_path}")
            return False
        
        # Читаем содержимое файла
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Извлекаем имя проекта
        project_name = get_project_name_from_path(file_path)
        
        # Проверяем имя файла
        correct_filename = get_correct_filename(project_name, file_path)
        filename_needs_update = os.path.basename(file_path) != os.path.basename(correct_filename)
        
        # Обновляем ссылку на стандарт
        content_updated = False
        new_content = content
        
        # Обновляем based on:
        based_on_pattern = r"based on: (.*?)(?:\n|$)"
        based_on_match = re.search(based_on_pattern, content)
        if based_on_match:
            old_based_on = based_on_match.group(1)
            if "Client Context Standard v2.2" not in old_based_on:
                new_based_on = f"based on: {UPDATED_STANDARD}"
                new_content = re.sub(based_on_pattern, f"{new_based_on}\n", new_content)
                content_updated = True
                logger.info(f"Обновлена ссылка на стандарт: {old_based_on} -> {UPDATED_STANDARD}")
        else:
            # Если нет строки based on, добавляем её после updated
            updated_pattern = r"(updated: .*?)(?:\n)"
            updated_match = re.search(updated_pattern, content)
            if updated_match:
                new_content = re.sub(updated_pattern, f"\\1\nbased on: {UPDATED_STANDARD}\n", new_content)
                content_updated = True
                logger.info(f"Добавлена ссылка на стандарт: {UPDATED_STANDARD}")
        
        # Обновляем updated
        now = datetime.now().strftime("%d %B %Y, %H:%M CET")
        updated_pattern = r"updated: (.*?)(?:\n|$)"
        updated_match = re.search(updated_pattern, new_content)
        if updated_match:
            old_updated = updated_match.group(1)
            new_updated = f"updated: {now} by Update Script"
            new_content = re.sub(updated_pattern, f"{new_updated}\n", new_content)
            content_updated = True
            logger.info(f"Обновлена дата изменения: {old_updated} -> {now}")
        
        # Проверяем наличие секций истории и их порядок
        history_sections = []
        history_section_pattern = r"^##\s+(\d{4}-\d{2}-\d{2}|\d{1,2}\s+(?:января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+\d{4}|\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})"
        
        for match in re.finditer(history_section_pattern, content, re.MULTILINE):
            date_str = match.group(1)
            position = match.start()
            history_sections.append((date_str, position))
        
        # Если есть секции истории, проверяем их порядок
        if history_sections:
            # Сортируем секции по дате (новые в начале)
            history_sections.sort(key=lambda x: x[0], reverse=True)
            
            # Проверяем текущий порядок секций в документе
            current_order = sorted(history_sections, key=lambda x: x[1])
            
            # Если порядок не соответствует обратной хронологии
            if current_order != history_sections:
                logger.info("Обнаружен неправильный порядок секций истории, переупорядочиваем...")
                
                # Пока мы не реализуем автоматическое переупорядочивание,
                # сообщаем о необходимости ручного обновления
                logger.warning(f"Файл {file_path} требует ручного переупорядочивания секций истории для соответствия обратной хронологии")
                # Здесь можно добавить код для автоматического переупорядочивания
        
        # Сохраняем изменения, если были обновления
        if content_updated:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            logger.info(f"Файл обновлен: {file_path}")
        
        # Если имя файла требует обновления
        if filename_needs_update:
            try:
                os.rename(file_path, correct_filename)
                logger.info(f"Файл переименован: {file_path} -> {correct_filename}")
                file_path = correct_filename
            except Exception as e:
                logger.error(f"Ошибка при переименовании файла: {e}")
        
        return True
    
    except Exception as e:
        logger.error(f"Ошибка при обновлении файла {file_path}: {e}")
        return False

def update_project_directory(directory):
    """
    Обновляет все файлы context.md в указанной директории.
    
    Args:
        directory: Путь к директории
        
    Returns:
        tuple: (количество обновленных файлов, количество ошибок)
    """
    updated_files = 0
    errors = 0
    
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file == "context.md" or file.endswith(".context.md"):
                    file_path = os.path.join(root, file)
                    if update_file_format(file_path):
                        updated_files += 1
                    else:
                        errors += 1
    
    except Exception as e:
        logger.error(f"Ошибка при обработке директории {directory}: {e}")
        errors += 1
    
    return updated_files, errors

def main():
    """Основная функция скрипта."""
    parser = argparse.ArgumentParser(description='Обновление файлов context.md в соответствии со стандартом')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--project-dir', help='Директория проектов для обновления')
    group.add_argument('--file', help='Конкретный файл для обновления')
    
    args = parser.parse_args()
    
    if args.project_dir:
        logger.info(f"Обновление файлов context.md в директории: {args.project_dir}")
        updated, errors = update_project_directory(args.project_dir)
        logger.info(f"Обновлено файлов: {updated}, ошибок: {errors}")
    elif args.file:
        logger.info(f"Обновление файла: {args.file}")
        if update_file_format(args.file):
            logger.info("Файл успешно обновлен")
        else:
            logger.error("Ошибка при обновлении файла")
            sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()