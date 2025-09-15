#!/usr/bin/env python3
"""
JTBD:
Я (разработчик) хочу автоматически добавлять JTBD-документацию к файлам при их изменении,
чтобы поддерживать высокое качество документации и единый стандарт без ручного вмешательства.

Скрипт для автоматического добавления и обновления JTBD-документации в файлах.
Интегрируется с системой триггеров для отслеживания изменений файлов.

Автор: AI Assistant
Дата: 21 мая 2025
"""

import os
import sys
import re
import ast
import time
import logging
import threading

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("auto_documentation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Импортируем анализатор документации
try:
    from src.core.documentation_analyzer import (
        analyze_file, 
        generate_jtbd_suggestions,
        JTBDDocumentationAnalyzer
    )
except ImportError as e:
    logger.error(f"Ошибка импорта анализатора документации: {e}")
    logger.info("Trying alternative import path...")
    try:
        import sys
        sys.path.append('/home/runner/workspace/advising_platform')
        from src.core.documentation_analyzer import (
            analyze_file, 
            generate_jtbd_suggestions,
            JTBDDocumentationAnalyzer
        )
    except ImportError as e2:
        logger.error(f"Alternative import also failed: {e2}")
        sys.exit(1)

class JTBDDocumentationUpdater:
    """
    JTBD:
    Я (разработчик) хочу автоматически обновлять JTBD-документацию в файлах, чтобы
    поддерживать единый стандарт документирования с минимальными усилиями.
    
    Класс для автоматического обновления JTBD-документации в файлах Python.
    """
    
    def __init__(self, target_directories: List[str], exclude_dirs: Optional[List[str]] = None):
        """
        Инициализирует обновлятор JTBD-документации.
        
        Args:
            target_directories: Список директорий для отслеживания изменений
            exclude_dirs: Список директорий для исключения
        """
        self.target_directories = target_directories
        self.exclude_dirs = exclude_dirs or ['__pycache__', 'venv', '.git', '.vscode']
        self.analyzer = JTBDDocumentationAnalyzer()
        self.lock = threading.RLock()
        self.observers = []
        
        logger.info(f"JTBDDocumentationUpdater инициализирован для директорий: {target_directories}")
    
    def start(self):
        """
        JTBD:
        Я (разработчик) хочу запустить автоматическое отслеживание изменений файлов,
        чтобы обновлять документацию без моего вмешательства.
        
        Запускает отслеживание файловой системы.
        """
        for directory in self.target_directories:
            if not os.path.exists(directory):
                logger.warning(f"Директория '{directory}' не существует")
                continue
            
            observer = Observer()
            event_handler = JTBDDocumentationEventHandler(self)
            observer.schedule(event_handler, directory, recursive=True)
            observer.start()
            self.observers.append(observer)
            
            logger.info(f"Отслеживание запущено для директории: {directory}")
        
        logger.info("Автоматическое обновление JTBD-документации запущено")
    
    def stop(self):
        """
        JTBD:
        Я (разработчик) хочу правильно завершить работу модуля отслеживания файлов,
        чтобы освободить системные ресурсы.
        
        Останавливает отслеживание файловой системы.
        """
        for observer in self.observers:
            observer.stop()
        
        for observer in self.observers:
            observer.join()
        
        self.observers = []
        logger.info("Автоматическое обновление JTBD-документации остановлено")
    
    def update_file_documentation(self, file_path: str):
        """
        JTBD:
        Я (разработчик) хочу обновить документацию в конкретном файле, чтобы привести ее в
        соответствие со стандартом JTBD.
        
        Обновляет JTBD-документацию в файле.
        
        Args:
            file_path: Путь к файлу для обновления
        
        Returns:
            bool: True, если документация была обновлена, иначе False
        """
        if not file_path.endswith('.py'):
            return False
        
        for exclude_dir in self.exclude_dirs:
            if exclude_dir in file_path:
                logger.debug(f"Файл '{file_path}' в исключенной директории, пропускаем")
                return False
        
        with self.lock:
            try:
                # Анализируем файл
                analysis_result = analyze_file(file_path)
                
                if analysis_result.get("status") != "success":
                    logger.warning(f"Ошибка при анализе файла '{file_path}': {analysis_result.get('message')}")
                    return False
                
                # Проверяем, нужно ли обновлять документацию
                if not analysis_result.get("missing_jtbd"):
                    logger.debug(f"Файл '{file_path}' уже имеет всю необходимую JTBD-документацию")
                    return False
                
                # Генерируем предложения для документации
                suggestions = generate_jtbd_suggestions(analysis_result)
                
                # Обновляем файл
                updated = self._update_file_with_suggestions(file_path, suggestions, analysis_result)
                
                if updated:
                    logger.info(f"Документация обновлена для файла: {file_path}")
                    return True
                else:
                    logger.debug(f"Не удалось обновить документацию для файла: {file_path}")
                    return False
                
            except Exception as e:
                logger.error(f"Ошибка при обновлении документации файла '{file_path}': {e}")
                return False
    
    def _update_file_with_suggestions(self, file_path: str, suggestions: Dict[str, str], 
                                     analysis_result: Dict[str, Any]) -> bool:
        """
        Обновляет файл с предложениями по документации.
        
        Args:
            file_path: Путь к файлу
            suggestions: Предложения по документации
            analysis_result: Результаты анализа файла
        
        Returns:
            bool: True, если файл был обновлен, иначе False
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Парсим файл
            tree = ast.parse(content)
            
            # Обновляем содержимое файла
            updated_content = content
            
            # Обновляем документацию модуля
            if "module" in suggestions and not analysis_result.get("has_module_jtbd"):
                updated_content = self._update_module_docstring(updated_content, suggestions["module"])
            
            # Обновляем документацию классов
            for class_info in analysis_result.get("has_class_jtbd", []):
                if not class_info.get("has_jtbd"):
                    class_name = class_info.get("name")
                    key = f"class_{class_name}"
                    if key in suggestions:
                        updated_content = self._update_class_docstring(
                            updated_content, class_name, suggestions[key]
                        )
            
            # Обновляем документацию функций
            for function_info in analysis_result.get("has_function_jtbd", []):
                if not function_info.get("has_jtbd"):
                    function_name = function_info.get("name")
                    key = f"function_{function_name}"
                    if key in suggestions:
                        updated_content = self._update_function_docstring(
                            updated_content, function_name, suggestions[key]
                        )
            
            # Записываем обновленное содержимое, если есть изменения
            if updated_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении файла '{file_path}' с предложениями: {e}")
            return False
    
    def _update_module_docstring(self, content: str, jtbd_doc: str) -> str:
        """
        Обновляет документацию модуля.
        
        Args:
            content: Содержимое файла
            jtbd_doc: JTBD-документация
        
        Returns:
            str: Обновленное содержимое файла
        """
        # Проверяем, есть ли уже документация модуля
        module_docstring_pattern = r'("""|\'\'\')\s*(?!\s*JTBD:)(.*?)\1'
        
        match = re.search(module_docstring_pattern, content, re.DOTALL)
        if match:
            # Добавляем JTBD в существующую документацию
            current_docstring = match.group(0)
            doc_delimiter = match.group(1)
            
            # Формируем новую документацию
            jtbd_part = f"{jtbd_doc}\n\n"
            new_docstring = current_docstring.replace(
                f"{doc_delimiter}{match.group(2)}", 
                f"{doc_delimiter}{jtbd_part}{match.group(2)}"
            )
            
            # Заменяем в содержимом файла
            return content.replace(current_docstring, new_docstring)
        else:
            # Если документации нет, добавляем новую после шебанга или в начало файла
            shebang_pattern = r'^#!.*?$'
            match = re.search(shebang_pattern, content)
            
            if match:
                # Добавляем после шебанга
                new_content = re.sub(
                    shebang_pattern,
                    f"{match.group(0)}\n\"\"\"\n{jtbd_doc}\n\"\"\"",
                    content,
                    count=1
                )
                return new_content
            else:
                # Добавляем в начало файла
                return f"\"\"\"\n{jtbd_doc}\n\"\"\"\n\n{content}"
    
    def _update_class_docstring(self, content: str, class_name: str, jtbd_doc: str) -> str:
        """
        Обновляет документацию класса.
        
        Args:
            content: Содержимое файла
            class_name: Имя класса
            jtbd_doc: JTBD-документация
        
        Returns:
            str: Обновленное содержимое файла
        """
        # Ищем определение класса и его документацию
        class_pattern = rf'class\s+{re.escape(class_name)}\s*(?:\([^)]*\))?\s*:'
        match = re.search(class_pattern, content)
        
        if not match:
            return content
        
        class_pos = match.end()
        
        # Проверяем, есть ли уже документация
        docstring_pattern = r'\s+("""|\'\'\')\s*(?!\s*JTBD:)(.*?)\1'
        rest_content = content[class_pos:]
        doc_match = re.search(docstring_pattern, rest_content, re.DOTALL)
        
        if doc_match:
            # Добавляем JTBD в существующую документацию
            current_docstring = doc_match.group(0)
            doc_delimiter = doc_match.group(1)
            
            # Формируем новую документацию
            jtbd_part = f"{jtbd_doc}\n    \n    "
            new_docstring = current_docstring.replace(
                f"{doc_delimiter}{doc_match.group(2)}", 
                f"{doc_delimiter}{jtbd_part}{doc_match.group(2)}"
            )
            
            # Заменяем в содержимом файла
            return content[:class_pos] + rest_content.replace(current_docstring, new_docstring)
        else:
            # Если документации нет, добавляем новую
            new_content = f"{content[:class_pos]}\n    \"\"\"\n    {jtbd_doc}\n    \"\"\"{content[class_pos:]}"
            return new_content
    
    def _update_function_docstring(self, content: str, function_name: str, jtbd_doc: str) -> str:
        """
        Обновляет документацию функции.
        
        Args:
            content: Содержимое файла
            function_name: Имя функции
            jtbd_doc: JTBD-документация
        
        Returns:
            str: Обновленное содержимое файла
        """
        # Ищем определение функции и ее документацию
        function_pattern = rf'def\s+{re.escape(function_name)}\s*\([^)]*\)\s*(?:->[^:]+)?\s*:'
        match = re.search(function_pattern, content)
        
        if not match:
            return content
        
        function_pos = match.end()
        
        # Проверяем, есть ли уже документация
        docstring_pattern = r'\s+("""|\'\'\')\s*(?!\s*JTBD:)(.*?)\1'
        rest_content = content[function_pos:]
        doc_match = re.search(docstring_pattern, rest_content, re.DOTALL)
        
        if doc_match:
            # Добавляем JTBD в существующую документацию
            current_docstring = doc_match.group(0)
            doc_delimiter = doc_match.group(1)
            
            # Формируем новую документацию (в зависимости от уровня отступа)
            indent = ' ' * (len(current_docstring) - len(current_docstring.lstrip()))
            jtbd_part = f"{jtbd_doc}\n{indent}\n{indent}"
            new_docstring = current_docstring.replace(
                f"{doc_delimiter}{doc_match.group(2)}", 
                f"{doc_delimiter}{jtbd_part}{doc_match.group(2)}"
            )
            
            # Заменяем в содержимом файла
            return content[:function_pos] + rest_content.replace(current_docstring, new_docstring)
        else:
            # Если документации нет, добавляем новую
            # Определяем отступ из окружающего кода
            next_line = rest_content.split('\n', 1)[0] if '\n' in rest_content else ''
            indent = ' ' * (len(next_line) - len(next_line.lstrip()))
            new_content = f"{content[:function_pos]}\n{indent}\"\"\"\n{indent}{jtbd_doc}\n{indent}\"\"\"{content[function_pos:]}"
            return new_content


class JTBDDocumentationEventHandler(FileSystemEventHandler):
    """
    JTBD:
    Я (разработчик) хочу автоматически реагировать на изменения файлов,
    чтобы обновлять документацию сразу после создания или изменения файлов.
    
    Обработчик событий файловой системы для обновления JTBD-документации.
    """
    
    def __init__(self, updater: JTBDDocumentationUpdater):
        """
        Инициализирует обработчик событий.
        
        Args:
            updater: Объект обновлятеля документации
        """
        self.updater = updater
        self.last_processed = {}  # Словарь с временем последней обработки файлов
    
    def on_modified(self, event):
        """
        Обрабатывает событие изменения файла.
        
        Args:
            event: Событие изменения файла
        """
        if not isinstance(event, FileModifiedEvent):
            return
        
        if not event.src_path.endswith('.py'):
            return
        
        file_path = event.src_path
        
        # Проверяем, не обрабатывали ли мы этот файл недавно
        current_time = time.time()
        last_time = self.last_processed.get(file_path, 0)
        
        if current_time - last_time > 5:  # Минимальный интервал между обработками - 5 секунд
            logger.debug(f"Обнаружено изменение файла: {file_path}")
            self.updater.update_file_documentation(file_path)
            self.last_processed[file_path] = current_time
    
    def on_created(self, event):
        """
        Обрабатывает событие создания файла.
        
        Args:
            event: Событие создания файла
        """
        if not isinstance(event, FileCreatedEvent):
            return
        
        if not event.src_path.endswith('.py'):
            return
        
        file_path = event.src_path
        logger.debug(f"Обнаружен новый файл: {file_path}")
        
        # Даем небольшую задержку, чтобы файл был полностью записан
        time.sleep(1)
        
        self.updater.update_file_documentation(file_path)
        self.last_processed[file_path] = time.time()


def register_with_trigger_system(target_directories: List[str]):
    """
    JTBD:
    Я (разработчик) хочу интегрировать автоматическое документирование с системой триггеров,
    чтобы обеспечить согласованную работу всех компонентов системы.
    
    Регистрирует обработчики в системе триггеров.
    
    Args:
        target_directories: Список директорий для отслеживания
    """
    try:
        # Импортируем систему триггеров
        from advising_platform.src.core.registry.trigger_handler import (
            get_handler, TriggerType, TriggerContext
        )
        
        # Получаем обработчик триггеров
        trigger_handler = get_handler()
        
        # Создаем функцию-обработчик для триггера обновления файла
        def on_file_update_trigger(context: TriggerContext):
            data = context.data
            file_path = data.get("file_path")
            
            if file_path and file_path.endswith('.py'):
                updater = JTBDDocumentationUpdater([os.path.dirname(file_path)])
                return updater.update_file_documentation(file_path)
            
            return False
        
        # Регистрируем обработчик триггера
        # В нашей системе нет типа триггера FILE_MODIFIED, используем PERIODIC_CHECK
        trigger_handler.register_handler(TriggerType.PERIODIC_CHECK, on_file_update_trigger)
        logger.info("Обработчик JTBD-документации зарегистрирован в системе триггеров")
        
    except ImportError as e:
        logger.warning(f"Не удалось интегрироваться с системой триггеров: {e}")
        logger.info("Будет использоваться только отслеживание файловой системы")


def main():
    """
    JTBD:
    Я (разработчик) хочу запустить автоматическое обновление документации,
    чтобы поддерживать актуальность и полноту JTBD-документации в проекте.
    
    Основная функция для запуска автоматического обновления документации.
    """
    logger.info("Запуск автоматического обновления JTBD-документации...")
    
    # Директории для отслеживания
    target_dirs = [
        "advising_platform/src/cache",
        "advising_platform/src/core"
    ]
    
    # Регистрируем в системе триггеров
    register_with_trigger_system(target_dirs)
    
    # Создаем и запускаем обновлятель документации
    updater = JTBDDocumentationUpdater(target_dirs)
    
    try:
        updater.start()
        
        # Также выполняем начальное обновление всех файлов
        for directory in target_dirs:
            if os.path.exists(directory):
                for root, _, files in os.walk(directory):
                    for file in files:
                        if file.endswith('.py'):
                            file_path = os.path.join(root, file)
                            updater.update_file_documentation(file_path)
        
        logger.info("Начальное обновление файлов завершено")
        
        # Работаем до прерывания
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Получен сигнал завершения работы")
        
    finally:
        updater.stop()
        logger.info("Автоматическое обновление JTBD-документации остановлено")


if __name__ == "__main__":
    main()