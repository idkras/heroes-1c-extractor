#!/usr/bin/env python3
"""
Утилита для нормализации путей и синхронизации кеша с файловой системой.

Данная утилита решает проблему рассинхронизации кеша с файловой системой
при создании новых файлов задач и инцидентов.

Автор: AI Assistant
Дата: 20 мая 2025
"""

import os
import sys
import json
import logging
from pathlib import Path
import time

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('path_normalizer.log')
    ]
)
logger = logging.getLogger("path_normalizer")

# Путь к файлу кеша
CACHE_STATE_FILE = ".cache_state.json"
DETAILED_CACHE_STATE_FILE = ".cache_detailed_state.pickle"
CONTEXT_CACHE_STATE_FILE = ".context_cache_state.json"

class PathNormalizer:
    """Класс для нормализации путей и обновления кеша."""

    @staticmethod
    def normalize_path(path):
        """
        Нормализует путь к файлу для использования в операциях с кешем.

        Args:
            path: Путь к файлу (абсолютный или относительный)

        Returns:
            str: Нормализованный путь относительно корня проекта
        """
        # Преобразуем путь в объект Path
        file_path = Path(path)

        # Получаем корень проекта (текущая директория)
        root_dir = Path(".")

        # Если путь абсолютный, делаем его относительным
        if file_path.is_absolute():
            try:
                file_path = file_path.relative_to(root_dir.absolute())
            except ValueError:
                # Если не удалось сделать относительно корня, берем только имя файла
                file_path = Path(file_path.name)

        # Преобразуем Path обратно в строку
        normalized_path = str(file_path)

        # Замена обратных слешей на прямые (для Windows)
        normalized_path = normalized_path.replace("\\", "/")

        # Удаляем начальные './' если есть
        if normalized_path.startswith("./"):
            normalized_path = normalized_path[2:]

        # Удаляем лишние слеши
        while "//" in normalized_path:
            normalized_path = normalized_path.replace("//", "/")

        return normalized_path

    @staticmethod
    def get_cache_state():
        """
        Загружает состояние кеша из файла.

        Returns:
            dict: Словарь с состоянием кеша
        """
        if not os.path.exists(CACHE_STATE_FILE):
            logger.warning(f"Файл кеша {CACHE_STATE_FILE} не найден")
            return {}
        
        try:
            with open(CACHE_STATE_FILE, 'r', encoding='utf-8') as f:
                cache_state = json.load(f)
            
            logger.info(f"Загружено состояние кеша из {CACHE_STATE_FILE}")
            return cache_state
        except Exception as e:
            logger.error(f"Ошибка при загрузке состояния кеша: {e}")
            return {}

    @staticmethod
    def save_cache_state(cache_state):
        """
        Сохраняет состояние кеша в файл.

        Args:
            cache_state: Словарь с состоянием кеша

        Returns:
            bool: True, если сохранение успешно, иначе False
        """
        try:
            with open(CACHE_STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache_state, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Сохранено состояние кеша в {CACHE_STATE_FILE}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении состояния кеша: {e}")
            return False

    @staticmethod
    def update_cache_for_file(file_path):
        """
        Обновляет кеш для указанного файла.

        Args:
            file_path: Путь к файлу (будет нормализован)

        Returns:
            bool: True, если обновление успешно, иначе False
        """
        # Нормализуем путь
        normalized_path = PathNormalizer.normalize_path(file_path)
        
        # Проверяем существование файла
        if not os.path.exists(normalized_path):
            logger.error(f"Файл не существует: {normalized_path}")
            return False
        
        # Получаем состояние кеша
        cache_state = PathNormalizer.get_cache_state()
        
        # Обновляем кеш
        try:
            # Получаем метаданные файла
            mtime = os.path.getmtime(normalized_path)
            size = os.path.getsize(normalized_path)
            
            # Читаем содержимое файла
            with open(normalized_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Обновляем запись в кеше
            if "documents" not in cache_state:
                cache_state["documents"] = {}
            
            cache_state["documents"][normalized_path] = {
                "path": normalized_path,
                "last_modified": mtime,
                "size": size,
                "content": content
            }
            
            # Сохраняем обновленное состояние кеша
            PathNormalizer.save_cache_state(cache_state)
            
            logger.info(f"Кеш обновлен для файла: {normalized_path}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при обновлении кеша для файла {normalized_path}: {e}")
            return False

    @staticmethod
    def verify_file_in_cache(file_path):
        """
        Проверяет, находится ли файл в кеше.

        Args:
            file_path: Путь к файлу (будет нормализован)

        Returns:
            bool: True, если файл в кеше, иначе False
        """
        # Нормализуем путь
        normalized_path = PathNormalizer.normalize_path(file_path)
        
        # Получаем состояние кеша
        cache_state = PathNormalizer.get_cache_state()
        
        # Проверяем наличие файла в кеше
        return "documents" in cache_state and normalized_path in cache_state["documents"]

    @staticmethod
    def force_resync_cache():
        """
        Принудительно синхронизирует кеш с файловой системой.

        Returns:
            Tuple[int, int, int]: Кортеж (количество добавленных, обновленных и удаленных файлов)
        """
        logger.info("Начало принудительной синхронизации кеша")
        
        # Получаем состояние кеша
        cache_state = PathNormalizer.get_cache_state()
        
        # Если в кеше нет документов, создаем пустой словарь
        if "documents" not in cache_state:
            cache_state["documents"] = {}
        
        # Получаем список всех файлов в файловой системе
        all_files = []
        for root, _, files in os.walk("."):
            # Исключаем скрытые директории
            if any(part.startswith(".") for part in Path(root).parts):
                continue
            
            for file in files:
                # Исключаем скрытые и бинарные файлы
                if file.startswith(".") or file.endswith((".pyc", ".pyo", ".so", ".dll", ".exe", ".zip", ".tar", ".gz")):
                    continue
                
                file_path = os.path.join(root, file)
                normalized_path = PathNormalizer.normalize_path(file_path)
                all_files.append(normalized_path)
        
        # Счетчики для статистики
        added_count = 0
        updated_count = 0
        deleted_count = 0
        
        # Добавляем и обновляем файлы в кеше
        for file_path in all_files:
            try:
                # Проверяем, что это текстовый файл
                # Пропускаем бинарные файлы и файлы без расширения
                text_extensions = ['.md', '.txt', '.py', '.js', '.html', '.css', '.json', '.yml', '.yaml', '.ini', '.cfg', '.conf', '.xml']
                is_text_file = any(file_path.endswith(ext) for ext in text_extensions)
                
                if not is_text_file:
                    continue
                
                # Проверяем, есть ли файл в кеше
                file_in_cache = file_path in cache_state["documents"]
                
                # Получаем метаданные файла
                mtime = os.path.getmtime(file_path)
                size = os.path.getsize(file_path)
                
                # Если файла нет в кеше или метаданные изменились
                if not file_in_cache or cache_state["documents"][file_path]["last_modified"] != mtime or cache_state["documents"][file_path]["size"] != size:
                    # Читаем содержимое файла
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Обновляем запись в кеше
                        cache_state["documents"][file_path] = {
                            "path": file_path,
                            "last_modified": mtime,
                            "size": size,
                            "content": content
                        }
                        
                        if file_in_cache:
                            updated_count += 1
                        else:
                            added_count += 1
                    except UnicodeDecodeError:
                        # Пропускаем файлы, которые не являются текстовыми
                        logger.debug(f"Пропускаем бинарный файл: {file_path}")
                        continue
            except Exception as e:
                logger.warning(f"Ошибка при обработке файла {file_path}: {e}")
        
        # Удаляем файлы из кеша, которых нет в файловой системе
        files_in_cache = list(cache_state["documents"].keys())
        for file_path in files_in_cache:
            if file_path not in all_files:
                del cache_state["documents"][file_path]
                deleted_count += 1
        
        # Сохраняем обновленное состояние кеша
        PathNormalizer.save_cache_state(cache_state)
        
        logger.info(f"Принудительная синхронизация завершена. Добавлено: {added_count}, обновлено: {updated_count}, удалено: {deleted_count}")
        return added_count, updated_count, deleted_count

def main():
    """
    Основная функция скрипта.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Утилита для нормализации путей и синхронизации кеша')
    
    parser.add_argument('--normalize', type=str, help='Нормализовать указанный путь')
    parser.add_argument('--update-cache', type=str, help='Обновить кеш для указанного файла')
    parser.add_argument('--verify', type=str, help='Проверить, находится ли файл в кеше')
    parser.add_argument('--resync', action='store_true', help='Принудительно синхронизировать кеш с файловой системой')
    
    args = parser.parse_args()
    
    if args.normalize:
        normalized_path = PathNormalizer.normalize_path(args.normalize)
        print(f"Нормализованный путь: {normalized_path}")
    
    if args.update_cache:
        success = PathNormalizer.update_cache_for_file(args.update_cache)
        if success:
            print(f"Кеш успешно обновлен для файла: {args.update_cache}")
        else:
            print(f"Ошибка при обновлении кеша для файла: {args.update_cache}")
    
    if args.verify:
        is_in_cache = PathNormalizer.verify_file_in_cache(args.verify)
        if is_in_cache:
            print(f"Файл находится в кеше: {args.verify}")
        else:
            print(f"Файл отсутствует в кеше: {args.verify}")
    
    if args.resync:
        added, updated, deleted = PathNormalizer.force_resync_cache()
        print(f"Принудительная синхронизация завершена. Добавлено: {added}, обновлено: {updated}, удалено: {deleted}")

if __name__ == "__main__":
    main()