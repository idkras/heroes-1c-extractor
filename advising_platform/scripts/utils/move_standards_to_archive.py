#!/usr/bin/env python3
"""
Скрипт для перемещения избыточных стандартов в архив.

Автор: AI Assistant
Дата: 20 мая 2025
"""

import os
import shutil
import logging
import datetime
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("archive_standards")

# Пути к директориям
STANDARDS_DIR = "[standards .md]"
ARCHIVE_DIR = os.path.join(STANDARDS_DIR, "[archive]")
TODAY_DATE = datetime.datetime.now().strftime('%Y%m%d')
ARCHIVE_DATE_DIR = os.path.join(ARCHIVE_DIR, TODAY_DATE)

# Целевое количество активных стандартов
TARGET_ACTIVE_STANDARDS = 40

def ensure_directory_exists(directory):
    """Создает директорию, если она не существует"""
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Создана директория: {directory}")

def find_duplicates():
    """Находит дублирующиеся стандарты"""
    duplicates = []
    standards_by_name = {}
    
    # Сначала собираем все стандарты
    for root, _, files in os.walk(STANDARDS_DIR):
        # Пропускаем архивные директории
        if "[archive]" in root:
            continue
            
        for file in files:
            if file.endswith(".md"):
                full_path = os.path.join(root, file)
                base_name = file.lower()
                
                # Очищаем имя от даты и версии для поиска дубликатов
                clean_name = base_name
                for date_format in ["_20250", "_202505", "202505", "2025"]:
                    clean_name = clean_name.replace(date_format, "")
                
                for version in ["v1.0", "v1", "v2.0", "v2"]:
                    clean_name = clean_name.replace(version, "")
                
                # Добавляем в словарь для поиска дубликатов
                if clean_name in standards_by_name:
                    standards_by_name[clean_name].append(full_path)
                else:
                    standards_by_name[clean_name] = [full_path]
    
    # Выбираем те, где больше одного файла с похожим именем
    for clean_name, paths in standards_by_name.items():
        if len(paths) > 1:
            duplicates.extend(paths[1:])  # Добавляем все кроме первого
            logger.info(f"Найдены дубликаты для {clean_name}: {paths}")
    
    return duplicates

def find_drafts_and_old_standards():
    """Находит черновики и устаревшие стандарты"""
    drafts = []
    
    for root, _, files in os.walk(STANDARDS_DIR):
        # Пропускаем архивные директории
        if "[archive]" in root:
            continue
            
        for file in files:
            if file.endswith(".md"):
                full_path = os.path.join(root, file)
                
                # Проверяем, является ли файл черновиком
                if "draft" in file.lower() or "черновик" in file.lower():
                    drafts.append(full_path)
                    logger.info(f"Найден черновик: {full_path}")
    
    return drafts

def main():
    """Основная функция скрипта"""
    logger.info("Начало архивации избыточных стандартов")
    
    # Создаем директории архива
    ensure_directory_exists(ARCHIVE_DIR)
    ensure_directory_exists(ARCHIVE_DATE_DIR)
    
    # Получаем список файлов для архивации
    duplicates = find_duplicates()
    drafts = find_drafts_and_old_standards()
    
    # Объединяем списки
    to_archive = duplicates + drafts
    
    # Подсчитываем количество активных стандартов
    total_standards = 0
    for root, _, files in os.walk(STANDARDS_DIR):
        if "[archive]" in root:
            continue
        total_standards += sum(1 for f in files if f.endswith(".md"))
    
    # Определяем, сколько ещё нужно архивировать
    remaining_to_archive = max(0, total_standards - TARGET_ACTIVE_STANDARDS - len(to_archive))
    
    if remaining_to_archive > 0:
        logger.info(f"Нужно архивировать ещё {remaining_to_archive} стандартов")
        
        # Собираем список всех стандартов с датами изменения
        all_standards = []
        for root, _, files in os.walk(STANDARDS_DIR):
            if "[archive]" in root or any(p in to_archive for p in [os.path.join(root, f) for f in files if f.endswith(".md")]):
                continue
            
            for file in files:
                if file.endswith(".md"):
                    full_path = os.path.join(root, file)
                    mtime = os.path.getmtime(full_path)
                    all_standards.append((full_path, mtime))
        
        # Сортируем по дате изменения (старые в начале)
        all_standards.sort(key=lambda x: x[1])
        
        # Добавляем самые старые стандарты в список архивации
        additional_to_archive = [path for path, _ in all_standards[:remaining_to_archive]]
        to_archive.extend(additional_to_archive)
        
        for path in additional_to_archive:
            logger.info(f"Добавлен к архивации устаревший стандарт: {path}")
    
    # Архивируем файлы
    archived_count = 0
    for source_path in to_archive:
        try:
            if os.path.exists(source_path):
                filename = os.path.basename(source_path)
                dest_path = os.path.join(ARCHIVE_DATE_DIR, filename)
                
                # Копируем файл в архив
                shutil.copy2(source_path, dest_path)
                
                # Добавляем отметку об архивации
                with open(dest_path, 'a', encoding='utf-8') as f:
                    f.write(f"\n\n> [!NOTE]\n> Архивировано: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} для достижения целевого количества активных стандартов\n")
                
                # Удаляем оригинальный файл
                os.remove(source_path)
                
                logger.info(f"Архивирован стандарт: {source_path} -> {dest_path}")
                archived_count += 1
            else:
                logger.warning(f"Файл не существует: {source_path}")
        except Exception as e:
            logger.error(f"Ошибка при архивации {source_path}: {e}")
    
    logger.info(f"Архивация завершена. Архивировано {archived_count} стандартов.")
    
    # Обновляем статистику в todo.md
    try:
        todo_path = "[todo · incidents]/todo.md"
        if os.path.exists(todo_path):
            with open(todo_path, 'r', encoding='utf-8') as f:
                todo_content = f.read()
            
            # Добавляем запись о выполненной задаче
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            task_note = f"\n- [x] **Архивация устаревших стандартов** [done] · @ai assistant · завершено {timestamp}\n"
            task_note += f"  **цель**: Уменьшить количество активных стандартов до {TARGET_ACTIVE_STANDARDS}\n"
            task_note += f"  **результат**: Архивировано {archived_count} стандартов\n"
            
            # Находим подходящее место для вставки
            insert_pos = todo_content.find("## 🔜 Следующие действия")
            if insert_pos == -1:
                insert_pos = todo_content.find("## 📝 Бэклог")
            if insert_pos == -1:
                insert_pos = len(todo_content)
            
            # Обновляем содержимое
            updated_content = todo_content[:insert_pos] + task_note + todo_content[insert_pos:]
            
            with open(todo_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
                
            logger.info(f"Обновлена запись в todo.md")
    except Exception as e:
        logger.error(f"Ошибка при обновлении todo.md: {e}")

if __name__ == "__main__":
    main()