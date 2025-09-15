#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Утилита для автоматизированной миграции устаревших стандартов в архив.
Анализирует стандарты по дате создания и наличию более новых версий.
"""

import os
import re
import sys
import shutil
import logging
import argparse
from datetime import datetime, timedelta
from collections import defaultdict

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scripts/archive_standards.log')
    ]
)

logger = logging.getLogger('archive_standards')

# Константы
STANDARDS_DIR = "[standards .md]"
ARCHIVE_DIR = os.path.join(STANDARDS_DIR, "[archive]")

def extract_date_from_filename(filename):
    """Извлекает дату и время из имени файла стандарта."""
    # Формат: [номер].[подномер] [название] by [дата] [время] CET by [автор].md
    pattern = r"by (\d+) ([a-zA-Z]+) (\d{4}) ?(\d{4})? CET by"
    match = re.search(pattern, filename)
    
    if not match:
        return None
    
    day = int(match.group(1))
    month_name = match.group(2).lower()
    year = int(match.group(3))
    time_str = match.group(4) or "0000"
    
    # Преобразуем название месяца в номер
    month_map = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
        "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
        "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12
    }
    
    month = month_map.get(month_name.lower(), 1)
    
    # Парсим время
    hour = int(time_str[:2]) if len(time_str) >= 2 else 0
    minute = int(time_str[2:]) if len(time_str) >= 4 else 0
    
    # Создаем объект datetime
    try:
        date = datetime(year, month, day, hour, minute)
        return date
    except ValueError:
        return None

def get_standard_base_name(filename):
    """Извлекает базовое имя стандарта без даты и времени."""
    parts = filename.split(" by ")
    if len(parts) > 0:
        return parts[0]
    return None

def find_outdated_standards(standards_dir, age_threshold=None, keep_latest=True, simulate=True):
    """
    Находит устаревшие стандарты для архивирования.
    
    Args:
        standards_dir: Путь к директории со стандартами
        age_threshold: Пороговое значение возраста в днях для архивации
        keep_latest: Оставлять ли последнюю версию каждого стандарта
        simulate: Только показать, что будет сделано, без реального перемещения
    
    Returns:
        Список файлов для архивации
    """
    if not os.path.exists(standards_dir):
        logger.error(f"Директория стандартов не найдена: {standards_dir}")
        return []
    
    # Проверяем/создаем архивную директорию
    if not os.path.exists(ARCHIVE_DIR):
        if not simulate:
            os.makedirs(ARCHIVE_DIR)
        logger.info(f"Создана архивная директория: {ARCHIVE_DIR}")
    
    # Считываем все файлы стандартов (исключая архивные)
    all_standards = []
    
    for root, _, files in os.walk(standards_dir):
        # Пропускаем архивную директорию
        if "archive AI never use" in root:
            continue
        
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                date = extract_date_from_filename(file)
                base_name = get_standard_base_name(file)
                
                if date and base_name:
                    all_standards.append({
                        'path': file_path,
                        'filename': file,
                        'date': date,
                        'base_name': base_name
                    })
    
    # Группируем стандарты по базовому имени
    standards_by_base = defaultdict(list)
    
    for standard in all_standards:
        standards_by_base[standard['base_name']].append(standard)
    
    # Определяем, какие стандарты архивировать
    to_archive = []
    
    for base_name, standards in standards_by_base.items():
        # Сортируем версии по дате (сначала новые)
        standards.sort(key=lambda x: x['date'], reverse=True)
        
        # Если нужно сохранить последнюю версию, пропускаем её
        offset = 1 if keep_latest and len(standards) > 1 else 0
        
        for i in range(offset, len(standards)):
            standard = standards[i]
            
            # Проверяем возраст, если указан порог
            if age_threshold:
                age_days = (datetime.now() - standard['date']).days
                
                if age_days < age_threshold:
                    continue
            
            to_archive.append(standard)
    
    return to_archive

def archive_standards(standards_to_archive, simulate=True):
    """
    Перемещает стандарты в архив.
    
    Args:
        standards_to_archive: Список стандартов для архивации
        simulate: Только показать, что будет сделано, без реального перемещения
    
    Returns:
        Количество архивированных стандартов
    """
    archived_count = 0
    
    for standard in standards_to_archive:
        src_path = standard['path']
        
        # Формируем путь в архиве, сохраняя структуру каталогов
        rel_path = os.path.relpath(src_path, STANDARDS_DIR)
        dst_path = os.path.join(ARCHIVE_DIR, rel_path)
        
        # Создаем промежуточные директории, если нужно
        dst_dir = os.path.dirname(dst_path)
        
        if not simulate:
            os.makedirs(dst_dir, exist_ok=True)
            
            # Перемещаем файл
            try:
                shutil.move(src_path, dst_path)
                archived_count += 1
                logger.info(f"Архивирован: {rel_path}")
            except Exception as e:
                logger.error(f"Ошибка при архивации {rel_path}: {e}")
        else:
            logger.info(f"[СИМУЛЯЦИЯ] Будет архивирован: {rel_path}")
            archived_count += 1
    
    return archived_count

def main():
    """Основная функция программы."""
    parser = argparse.ArgumentParser(description='Автоматическая архивация устаревших стандартов')
    parser.add_argument('--age', type=int, default=None, 
                        help='Архивировать стандарты старше указанного количества дней')
    parser.add_argument('--all-versions', action='store_true', 
                        help='Архивировать все версии, включая последнюю')
    parser.add_argument('--force', action='store_true', 
                        help='Выполнить архивацию без подтверждения')
    parser.add_argument('--simulate', action='store_true', 
                        help='Показать, что будет сделано, без реального перемещения файлов')
    
    args = parser.parse_args()
    
    # Находим стандарты для архивации
    standards_to_archive = find_outdated_standards(
        STANDARDS_DIR,
        age_threshold=args.age,
        keep_latest=not args.all_versions,
        simulate=args.simulate or not args.force
    )
    
    if not standards_to_archive:
        logger.info("Не найдены стандарты для архивации.")
        return
    
    # Выводим информацию о найденных стандартах
    logger.info(f"Найдено {len(standards_to_archive)} стандартов для архивации:")
    
    for i, standard in enumerate(standards_to_archive, 1):
        logger.info(f"{i}. {standard['filename']} (от {standard['date'].strftime('%d.%m.%Y %H:%M')})")
    
    # Запрашиваем подтверждение, если не указан флаг --force
    if not args.force and not args.simulate:
        confirm = input("\nАрхивировать найденные стандарты? (y/n): ").lower().strip()
        
        if confirm != 'y':
            logger.info("Архивация отменена.")
            return
    
    # Выполняем архивацию
    archived_count = archive_standards(standards_to_archive, simulate=args.simulate)
    
    if args.simulate:
        logger.info(f"[СИМУЛЯЦИЯ] Была бы выполнена архивация {archived_count} стандартов.")
    else:
        logger.info(f"Успешно архивировано {archived_count} стандартов.")

if __name__ == "__main__":
    main()