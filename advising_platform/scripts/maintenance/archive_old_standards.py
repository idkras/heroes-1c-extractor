#!/usr/bin/env python3
"""
Скрипт для архивации старых или устаревших стандартов.

Этот скрипт позволяет:
1. Идентифицировать стандарты-кандидаты для архивации
2. Определить дублирующие стандарты на основе их содержимого
3. Архивировать выбранные стандарты
4. Обновить статистику активных стандартов

Автор: AI Assistant
Дата: 20 мая 2025
"""

import os
import re
import sys
import json
import shutil
import logging
import datetime
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Set, Optional

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('archive_standards.log')
    ]
)
logger = logging.getLogger("archive_standards")

# Пути к директориям
STANDARDS_DIR = "[standards .md]"
ARCHIVE_DIR = f"{STANDARDS_DIR}/[archive]"
ARCHIVE_DATE_DIR = f"{ARCHIVE_DIR}/{datetime.datetime.now().strftime('%Y%m%d')}"

# Глобальные переменные
TARGET_ACTIVE_STANDARDS = 40  # Предпочтительное количество активных стандартов

def ensure_directory_exists(directory: str) -> None:
    """
    Проверяет наличие директории и создает ее при необходимости.
    
    Args:
        directory: Путь к директории
    """
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Создана директория: {directory}")

def find_standards() -> List[Dict[str, str]]:
    """
    Находит все активные стандарты.
    
    Returns:
        List[Dict[str, str]]: Список стандартов с метаданными
    """
    standards = []
    
    if not os.path.exists(STANDARDS_DIR):
        logger.error(f"Директория стандартов не найдена: {STANDARDS_DIR}")
        return standards
    
    for root, dirs, files in os.walk(STANDARDS_DIR):
        # Пропускаем архивные директории
        if "[archive]" in root:
            continue
        
        for file in files:
            if not file.endswith(".md"):
                continue
            
            file_path = os.path.join(root, file)
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Извлекаем заголовок
                title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
                title = title_match.group(1).strip() if title_match else file
                
                # Извлекаем дату
                date_match = re.search(r'date:.*?(\d{1,2}[- /.]\d{1,2}[- /.]\d{2,4}|\d{4}[- /.]\d{1,2}[- /.]\d{1,2})', content, re.IGNORECASE)
                date = date_match.group(1).strip() if date_match else None
                
                if not date:
                    # Пытаемся извлечь дату из имени файла
                    date_match = re.search(r'(\d{1,2}[- /.]\d{1,2}[- /.]\d{2,4}|\d{4}[- /.]\d{1,2}[- /.]\d{1,2})', file)
                    date = date_match.group(1).strip() if date_match else None
                
                # Определяем версию
                version_match = re.search(r'version:.*?([0-9.]+)', content, re.IGNORECASE)
                if not version_match:
                    version_match = re.search(r'v([0-9.]+)', file, re.IGNORECASE)
                version = version_match.group(1) if version_match else "1.0"
                
                # Проверяем, является ли это дубликатом или черновиком
                is_draft = "draft" in file.lower() or "черновик" in file.lower() or "draft" in content.lower() or "черновик" in content.lower()
                
                # Размер файла
                file_size = os.path.getsize(file_path)
                
                # Дата последнего изменения
                mtime = os.path.getmtime(file_path)
                last_modified = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
                
                standards.append({
                    "title": title,
                    "path": file_path,
                    "date": date,
                    "version": version,
                    "is_draft": is_draft,
                    "file_size": file_size,
                    "last_modified": last_modified,
                    "content": content
                })
                
                logger.debug(f"Найден стандарт: {title} ({file_path})")
            except Exception as e:
                logger.error(f"Ошибка при обработке файла {file_path}: {e}")
    
    logger.info(f"Найдено {len(standards)} активных стандартов")
    return standards

def identify_duplicates(standards: List[Dict[str, str]]) -> List[Dict[str, List[Dict[str, str]]]]:
    """
    Идентифицирует дублирующие стандарты.
    
    Args:
        standards: Список стандартов с метаданными
        
    Returns:
        List[Dict[str, List[Dict[str, str]]]]: Список групп дубликатов
    """
    duplicates = []
    
    # Группируем стандарты по названию (без учета регистра и версии)
    title_groups = {}
    for standard in standards:
        # Очищаем название от версии и даты
        clean_title = re.sub(r'v\d+(\.\d+)*', '', standard["title"])
        clean_title = re.sub(r'\d{1,2}[- /.]\d{1,2}[- /.]\d{2,4}|\d{4}[- /.]\d{1,2}[- /.]\d{1,2}', '', clean_title)
        clean_title = clean_title.lower().strip()
        
        if clean_title in title_groups:
            title_groups[clean_title].append(standard)
        else:
            title_groups[clean_title] = [standard]
    
    # Находим группы с более чем одним стандартом
    for title, group in title_groups.items():
        if len(group) > 1:
            duplicates.append({
                "title": title,
                "standards": group
            })
    
    # Дополнительно проверяем содержимое для стандартов с разными названиями
    content_similarity = []
    for i, standard1 in enumerate(standards):
        for j, standard2 in enumerate(standards[i+1:], i+1):
            # Сравниваем содержимое (без учета регистра и форматирования)
            content1 = re.sub(r'[^a-zA-Zа-яА-Я0-9]', '', standard1["content"].lower())
            content2 = re.sub(r'[^a-zA-Zа-яА-Я0-9]', '', standard2["content"].lower())
            
            # Если содержимое очень похоже, но названия разные
            if content1 == content2 and standard1["title"].lower() != standard2["title"].lower():
                # Проверяем, не входят ли эти стандарты уже в какую-то группу дубликатов
                is_in_group = False
                for group in duplicates:
                    if standard1 in group["standards"] and standard2 in group["standards"]:
                        is_in_group = True
                        break
                
                if not is_in_group:
                    content_similarity.append({
                        "title": f"Похожие стандарты: {standard1['title']} и {standard2['title']}",
                        "standards": [standard1, standard2]
                    })
    
    # Добавляем группы с похожим содержимым
    duplicates.extend(content_similarity)
    
    logger.info(f"Найдено {len(duplicates)} групп дублирующих стандартов")
    for i, group in enumerate(duplicates, 1):
        logger.info(f"Группа {i}: {group['title']}")
        for standard in group["standards"]:
            logger.info(f"  - {standard['title']} ({standard['path']})")
    
    return duplicates

def identify_candidates_for_archiving(standards: List[Dict[str, str]], duplicates: List[Dict[str, List[Dict[str, str]]]]) -> List[Dict[str, str]]:
    """
    Определяет стандарты-кандидаты для архивации.
    
    Args:
        standards: Список стандартов с метаданными
        duplicates: Список групп дубликатов
        
    Returns:
        List[Dict[str, str]]: Список стандартов-кандидатов для архивации
    """
    candidates = []
    
    # 1. Архивируем черновики
    for standard in standards:
        if standard["is_draft"]:
            candidates.append({
                "standard": standard,
                "reason": "Это черновик"
            })
    
    # 2. Архивируем дубликаты (оставляем только самую последнюю версию)
    for group in duplicates:
        # Сортируем по версии и дате последнего изменения
        sorted_standards = sorted(
            group["standards"],
            key=lambda s: (float(s["version"]), s["last_modified"]),
            reverse=True
        )
        
        # Оставляем только самую последнюю версию
        for standard in sorted_standards[1:]:
            # Проверяем, не добавлен ли стандарт уже в кандидаты
            if not any(c["standard"]["path"] == standard["path"] for c in candidates):
                candidates.append({
                    "standard": standard,
                    "reason": f"Дубликат стандарта {sorted_standards[0]['title']}"
                })
    
    # 3. Если у нас всё ещё слишком много стандартов, архивируем самые старые
    if len(standards) - len(candidates) > TARGET_ACTIVE_STANDARDS:
        # Отбираем стандарты, которые ещё не в списке кандидатов
        remaining = [s for s in standards if not any(c["standard"]["path"] == s["path"] for c in candidates)]
        
        # Сортируем по дате последнего изменения
        sorted_remaining = sorted(
            remaining,
            key=lambda s: s["last_modified"]
        )
        
        # Добавляем столько стандартов, сколько нужно для достижения целевого количества
        num_to_archive = len(remaining) - TARGET_ACTIVE_STANDARDS
        for standard in sorted_remaining[:num_to_archive]:
            candidates.append({
                "standard": standard,
                "reason": "Устаревший стандарт (на основе даты последнего изменения)"
            })
    
    logger.info(f"Идентифицировано {len(candidates)} стандартов-кандидатов для архивации")
    for i, candidate in enumerate(candidates, 1):
        logger.info(f"{i}. {candidate['standard']['title']} ({candidate['standard']['path']})")
        logger.info(f"   Причина: {candidate['reason']}")
    
    return candidates

def archive_standards(candidates: List[Dict[str, str]], dry_run: bool = False) -> int:
    """
    Архивирует стандарты.
    
    Args:
        candidates: Список стандартов-кандидатов для архивации
        dry_run: Режим без внесения изменений (только вывод в лог)
        
    Returns:
        int: Количество архивированных стандартов
    """
    if not candidates:
        logger.info("Нет стандартов для архивации")
        return 0
    
    # Создаем директорию архива
    ensure_directory_exists(ARCHIVE_DIR)
    ensure_directory_exists(ARCHIVE_DATE_DIR)
    
    count = 0
    for candidate in candidates:
        standard = candidate["standard"]
        reason = candidate["reason"]
        
        try:
            # Определяем путь к архивной копии
            filename = os.path.basename(standard["path"])
            archive_path = os.path.join(ARCHIVE_DATE_DIR, filename)
            
            if dry_run:
                logger.info(f"[Режим предпросмотра] Стандарт будет архивирован: {standard['path']} -> {archive_path}")
                logger.info(f"  Причина: {reason}")
                count += 1
                continue
            
            # Архивируем стандарт
            shutil.copy2(standard["path"], archive_path)
            
            # Добавляем информацию об архивации в файл
            with open(archive_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Добавляем отметку об архивации
            archive_note = f"\n\n> [!NOTE]\n> Архивировано: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n> Причина: {reason}\n"
            with open(archive_path, 'w', encoding='utf-8') as f:
                f.write(content + archive_note)
            
            # Удаляем оригинальный файл
            os.remove(standard["path"])
            
            logger.info(f"Стандарт архивирован: {standard['path']} -> {archive_path}")
            logger.info(f"  Причина: {reason}")
            
            count += 1
        except Exception as e:
            logger.error(f"Ошибка при архивации стандарта {standard['path']}: {e}")
    
    logger.info(f"Архивировано {count} стандартов")
    return count

def update_todo_stats(num_archived: int, dry_run: bool = False) -> bool:
    """
    Обновляет статистику в файле todo.md.
    
    Args:
        num_archived: Количество архивированных стандартов
        dry_run: Режим без внесения изменений (только вывод в лог)
        
    Returns:
        bool: True, если обновление успешно, иначе False
    """
    todo_file = "[todo · incidents]/todo.md"
    
    if not os.path.exists(todo_file):
        logger.error(f"Файл todo.md не найден: {todo_file}")
        return False
    
    try:
        # Читаем содержимое todo.md
        with open(todo_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Находим секцию статистики
        stats_section = re.search(r'## 📊 Статистика задач.*?(?=##|$)', content, re.DOTALL)
        if not stats_section:
            logger.warning("Секция статистики не найдена в todo.md")
            return False
        
        stats_content = stats_section.group(0)
        
        # Создаем отметку о выполнении задачи по архивации
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        task_note = f"\n- [x] **Архивация устаревших стандартов** [done] · @ai assistant · завершено {timestamp}\n"
        task_note += f"  **цель**: Уменьшить количество активных стандартов до {TARGET_ACTIVE_STANDARDS}\n"
        task_note += f"  **результат**: Архивировано {num_archived} стандартов, оставлено {TARGET_ACTIVE_STANDARDS} активных стандартов\n"
        
        # Находим подходящее место для вставки задачи
        insert_pos = content.find("## 🔜 Следующие действия")
        if insert_pos == -1:
            insert_pos = content.find("## 📝 Бэклог")
            if insert_pos == -1:
                insert_pos = len(content)
        
        # Создаем обновленное содержимое
        new_content = content[:insert_pos] + task_note + content[insert_pos:]
        
        if not dry_run:
            # Записываем обновленное содержимое
            with open(todo_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logger.info(f"Статистика в todo.md обновлена")
        else:
            logger.info(f"[Режим предпросмотра] Статистика в todo.md будет обновлена")
        
        return True
    except Exception as e:
        logger.error(f"Ошибка при обновлении статистики в todo.md: {e}")
        return False

def update_cache():
    """
    Обновляет кеш после внесения изменений.
    
    Returns:
        bool: True, если обновление успешно, иначе False
    """
    try:
        logger.info("Обновление кеша...")
        
        # Формируем команду для обновления кеша
        cmd = "python sync_verification.py --sync"
        
        # Выполняем команду
        import subprocess
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Кеш успешно обновлен")
            logger.info(result.stdout)
            return True
        else:
            logger.error(f"Ошибка при обновлении кеша: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Исключение при обновлении кеша: {e}")
        return False

def main():
    """Основная функция скрипта."""
    parser = argparse.ArgumentParser(description='Архивация устаревших стандартов')
    
    parser.add_argument('--dry-run', action='store_true',
                        help='Режим без внесения изменений (только вывод в лог)')
    parser.add_argument('--update-cache', action='store_true',
                        help='Обновить кеш после архивации')
    parser.add_argument('--target', type=int, default=TARGET_ACTIVE_STANDARDS,
                        help=f'Целевое количество активных стандартов (по умолчанию {TARGET_ACTIVE_STANDARDS})')
    
    args = parser.parse_args()
    
    # Обновляем целевое количество активных стандартов
    TARGET_ACTIVE_STANDARDS = args.target
    
    logger.info(f"Запуск архивации устаревших стандартов (целевое количество: {TARGET_ACTIVE_STANDARDS})")
    
    # Находим все активные стандарты
    standards = find_standards()
    
    # Если стандартов меньше или равно целевому количеству, ничего не делаем
    if len(standards) <= TARGET_ACTIVE_STANDARDS:
        logger.info(f"Количество активных стандартов ({len(standards)}) уже соответствует целевому ({TARGET_ACTIVE_STANDARDS})")
        return
    
    # Идентифицируем дублирующие стандарты
    duplicates = identify_duplicates(standards)
    
    # Определяем стандарты-кандидаты для архивации
    candidates = identify_candidates_for_archiving(standards, duplicates)
    
    # Если кандидатов слишком много, ограничиваем их количество
    if len(standards) - len(candidates) < TARGET_ACTIVE_STANDARDS:
        num_to_remove = len(candidates) - (len(standards) - TARGET_ACTIVE_STANDARDS)
        candidates = candidates[:-num_to_remove]
    
    # Архивируем стандарты
    num_archived = archive_standards(candidates, args.dry_run)
    
    # Обновляем статистику в todo.md
    update_todo_stats(num_archived, args.dry_run)
    
    # Обновляем кеш
    if args.update_cache and not args.dry_run:
        update_cache()
    
    logger.info("Архивация устаревших стандартов завершена")

if __name__ == "__main__":
    main()