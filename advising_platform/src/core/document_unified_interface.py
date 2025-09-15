#!/usr/bin/env python3
"""
Унифицированный интерфейс для работы с документами системы.
Обеспечивает единый способ создания, чтения, обновления и удаления документов,
соблюдая паттерны registry и task master.

Автор: AI Assistant
Дата: 21 мая 2025
"""

import os
import re
import sys
import json
import logging
from datetime import datetime
import uuid
from typing import Dict, List, Any, Optional, Union, Tuple

# Импортируем необходимые компоненты для триггеров и чат-интеграции
try:
    from advising_platform.src.core.registry.trigger_handler import (
        TriggerHandler, TriggerType, TriggerContext, get_handler
    )
    from advising_platform.src.tools.reporting.report_interface import report_progress
    
    TRIGGER_SYSTEM_AVAILABLE = True
except ImportError as e:
    TRIGGER_SYSTEM_AVAILABLE = False
    logger = logging.getLogger("document_interface")
    logger.warning(f"Система триггеров недоступна: {e}")
    
    # Создаем заглушки для необходимых компонентов
    class TriggerType:
        TASK_CREATE = "task_create"
        INCIDENT_CREATE = "incident_create"
        HYPOTHESIS_CREATE = "hypothesis_create"
        STANDARD_CREATE = "standard_create"
    
    class TriggerContext:
        def __init__(self, trigger_type, data, timestamp, source):
            self.trigger_type = trigger_type
            self.data = data
            self.timestamp = timestamp
            self.source = source
    
    class TriggerResult:
        def __init__(self, success, message, data=None):
            self.success = success
            self.message = message
            self.data = data or {}
    
    def get_handler(report_func=None):
        class MockHandler:
            def handle_trigger(self, context):
                return TriggerResult(
                    success=True, 
                    message=f"Mock trigger handled: {context.trigger_type}", 
                    data=context.data
                )
        return MockHandler()
    
    def report_progress(data):
        logger.info(f"Mock report_progress: {data}")
        return True

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("document_interface.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("document_interface")

class DocumentInterface:
    """JTBD:
Я (разработчик) хочу использовать функциональность класса DocumentInterface, чтобы эффективно решать соответствующие задачи в системе.
    
    Базовый класс для унифицированного интерфейса документов."""
    
    def __init__(self, base_dir: str = '.'):
        """
        Инициализирует интерфейс документов.
        
        Args:
            base_dir: Базовая директория проекта
        """
        self.base_dir = os.path.abspath(base_dir)
        self.document_type = "generic"
        self.consolidated_file = "documents.md"
        self.section_marker = "##"
        self.item_marker = "###"
    
    def create(self, **kwargs) -> str:
        """
        Создает новый документ в консолидированном файле.
        
        Args:
            **kwargs: Атрибуты документа (title, description и т.д.)
            
        Returns:
            str: Идентификатор созданного документа
        """
        logger.info(f"Создание нового документа типа {self.document_type}")
        
        # Генерируем уникальный идентификатор
        doc_id = str(uuid.uuid4()).split('-')[0]
        
        # Получаем путь к консолидированному файлу
        consolidated_path = self.get_consolidated_path()
        
        # Проверяем, существует ли файл
        if not os.path.exists(consolidated_path):
            # Создаем базовый файл с заголовком
            with open(consolidated_path, 'w', encoding='utf-8') as f:
                f.write(f"# Список {self.document_type}ов\n\n")
                f.write(f"{self.section_marker} Новые {self.document_type}ы\n\n")
        
        # Форматируем документ для добавления
        doc_content = self._format_document_for_consolidated(doc_id, **kwargs)
        
        # Добавляем документ в консолидированный файл
        with open(consolidated_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Находим нужную секцию для добавления
        section_match = re.search(f"{self.section_marker} Новые {self.document_type}ы", content)
        if section_match:
            # Вставляем документ после заголовка секции
            insert_pos = section_match.end() + 2  # +2 для перехода на новую строку после заголовка
            new_content = content[:insert_pos] + doc_content + "\n" + content[insert_pos:]
        else:
            # Добавляем секцию и документ в конец файла
            new_content = content + f"\n{self.section_marker} Новые {self.document_type}ы\n\n" + doc_content + "\n"
        
        # Записываем обновленное содержимое
        with open(consolidated_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        logger.info(f"Документ {self.document_type} с ID {doc_id} успешно создан")
        
        # Активируем триггер для созданного документа
        self._trigger_document_creation(doc_id, **kwargs)
        
        return doc_id
    
    def read(self, doc_id: str) -> Dict[str, Any]:
        """
        Читает документ из консолидированного файла.
        
        Args:
            doc_id: Идентификатор документа
            
        Returns:
            Dict[str, Any]: Данные документа
        """
        logger.info(f"Чтение документа {self.document_type} с ID {doc_id}")
        
        # Получаем путь к консолидированному файлу
        consolidated_path = self.get_consolidated_path()
        
        # Проверяем, существует ли файл
        if not os.path.exists(consolidated_path):
            logger.error(f"Консолидированный файл {consolidated_path} не найден")
            return {}
        
        # Читаем файл
        with open(consolidated_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ищем документ по ID
        doc_pattern = re.compile(
            f"{self.item_marker} .*{self.document_type.title()}: (.*) #{doc_id}.*?(?={self.item_marker}|$)",
            re.DOTALL
        )
        doc_match = doc_pattern.search(content)
        
        if not doc_match:
            logger.error(f"Документ {self.document_type} с ID {doc_id} не найден")
            return {}
        
        # Извлекаем данные документа
        doc_content = doc_match.group(0)
        
        # Парсим данные
        doc_data = self._parse_document_from_consolidated(doc_content)
        doc_data['id'] = doc_id
        
        return doc_data
    
    def update(self, doc_id: str, data: Dict[str, Any]) -> bool:
        """
        Обновляет документ в консолидированном файле.
        
        Args:
            doc_id: Идентификатор документа
            data: Новые данные документа
            
        Returns:
            bool: True, если обновление успешно, иначе False
        """
        logger.info(f"Обновление документа {self.document_type} с ID {doc_id}")
        
        # Получаем путь к консолидированному файлу
        consolidated_path = self.get_consolidated_path()
        
        # Проверяем, существует ли файл
        if not os.path.exists(consolidated_path):
            logger.error(f"Консолидированный файл {consolidated_path} не найден")
            return False
        
        # Читаем файл
        with open(consolidated_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ищем документ по ID
        doc_pattern = re.compile(
            f"{self.item_marker} .*{self.document_type.title()}: (.*) #{doc_id}.*?(?={self.item_marker}|$)",
            re.DOTALL
        )
        doc_match = doc_pattern.search(content)
        
        if not doc_match:
            logger.error(f"Документ {self.document_type} с ID {doc_id} не найден")
            return False
        
        # Получаем старое содержимое документа
        old_doc_content = doc_match.group(0)
        
        # Читаем текущие данные документа
        current_data = self._parse_document_from_consolidated(old_doc_content)
        
        # Объединяем текущие данные с новыми
        merged_data = {**current_data, **data}
        
        # Форматируем новое содержимое документа
        new_doc_content = self._format_document_for_consolidated(doc_id, **merged_data)
        
        # Заменяем старое содержимое новым
        new_content = content.replace(old_doc_content, new_doc_content)
        
        # Записываем обновленное содержимое
        with open(consolidated_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        logger.info(f"Документ {self.document_type} с ID {doc_id} успешно обновлен")
        return True
    
    def delete(self, doc_id: str) -> bool:
        """
        Удаляет документ из консолидированного файла.
        
        Args:
            doc_id: Идентификатор документа
            
        Returns:
            bool: True, если удаление успешно, иначе False
        """
        logger.info(f"Удаление документа {self.document_type} с ID {doc_id}")
        
        # Получаем путь к консолидированному файлу
        consolidated_path = self.get_consolidated_path()
        
        # Проверяем, существует ли файл
        if not os.path.exists(consolidated_path):
            logger.error(f"Консолидированный файл {consolidated_path} не найден")
            return False
        
        # Читаем файл
        with open(consolidated_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ищем документ по ID
        doc_pattern = re.compile(
            f"{self.item_marker} .*{self.document_type.title()}: (.*) #{doc_id}.*?(?={self.item_marker}|$)",
            re.DOTALL
        )
        doc_match = doc_pattern.search(content)
        
        if not doc_match:
            logger.error(f"Документ {self.document_type} с ID {doc_id} не найден")
            return False
        
        # Получаем содержимое документа
        doc_content = doc_match.group(0)
        
        # Удаляем документ из содержимого
        new_content = content.replace(doc_content, "")
        
        # Записываем обновленное содержимое
        with open(consolidated_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        logger.info(f"Документ {self.document_type} с ID {doc_id} успешно удален")
        return True
    
    def get_consolidated_path(self) -> str:
        """
        Возвращает путь к консолидированному файлу.
        
        Returns:
            str: Путь к консолидированному файлу
        """
        return os.path.join(self.base_dir, self.consolidated_file)
        
    def _trigger_document_creation(self, doc_id: str, **kwargs) -> None:
        """
        Активирует триггер для созданного документа, чтобы вывести информацию в чат.
        
        Args:
            doc_id: Идентификатор созданного документа
            **kwargs: Атрибуты документа
        """
        # Получаем логгер
        logger = logging.getLogger("document_interface")
        
        # Проверяем доступность системы триггеров
        if not TRIGGER_SYSTEM_AVAILABLE:
            logger.warning("Система триггеров недоступна. Невозможно активировать триггер.")
            return
        
        try:
            # Импортируем заново, чтобы избежать проблем с неопределенными переменными
            from advising_platform.src.core.registry.trigger_handler import (
                TriggerType, TriggerContext, get_handler
            )
            from advising_platform.src.tools.reporting.report_interface import report_progress
            
            # Получаем тип триггера в зависимости от типа документа
            trigger_type = None
            if self.document_type == 'задача':
                trigger_type = TriggerType.TASK_CREATE
            elif self.document_type == 'инцидент':
                trigger_type = TriggerType.INCIDENT_CREATE
            elif self.document_type == 'гипотеза':
                trigger_type = TriggerType.HYPOTHESIS_CREATE
            elif self.document_type == 'стандарт':
                trigger_type = TriggerType.STANDARD_CREATE
            else:
                logger.warning(f"Неизвестный тип документа: {self.document_type}. Невозможно активировать триггер.")
                return
            
            # Формируем ссылку для просмотра документа
            title = kwargs.get('title', f"Документ-{doc_id}")
            # Формируем корректный URL-путь в зависимости от типа документа
            if self.document_type == 'задача':
                url_path = 'tasks'
            elif self.document_type == 'инцидент':
                url_path = 'incidents'
            elif self.document_type == 'гипотеза':
                url_path = 'hypotheses'
            elif self.document_type == 'стандарт':
                url_path = 'standards'
            else:
                url_path = f"{self.document_type}s"
            
            web_url = f"http://0.0.0.0:5000/{url_path}/{title.replace(' ', '-')}"
            
            # Подготавливаем данные для триггера
            trigger_data = {
                'id': doc_id,
                'title': title,
                'description': kwargs.get('description', ''),
                'file_path': self.get_consolidated_path(),
                'web_url': web_url
            }
            
            # Добавляем специфичные данные в зависимости от типа документа
            if self.document_type == 'задача':
                trigger_data['priority'] = kwargs.get('priority', 'Средний')
                trigger_data['status'] = kwargs.get('status', 'Не начато')
                trigger_data['type'] = kwargs.get('type', 'Общая')
            elif self.document_type == 'инцидент':
                # Для инцидентов извлекаем анализ 5-почему и корневую причину
                description = kwargs.get('description', '')
                five_why_analysis = []
                root_cause = "Не указана"
                
                if description:
                    # Парсим описание для извлечения анализа 5-почему
                    lines = description.split("\n")
                    in_five_why_section = False
                    in_root_cause_section = False
                    
                    for line in lines:
                        if "## Анализ 5-почему" in line:
                            in_five_why_section = True
                            in_root_cause_section = False
                            continue
                        elif "## Корневая причина" in line:
                            in_five_why_section = False
                            in_root_cause_section = True
                            continue
                        elif line.startswith("## "):
                            in_five_why_section = False
                            in_root_cause_section = False
                            continue
                        
                        if in_five_why_section and line.strip():
                            if line.strip().startswith("Почему"):
                                five_why_analysis.append({"question": line.strip(), "answer": ""})
                            elif five_why_analysis and not five_why_analysis[-1]["answer"]:
                                five_why_analysis[-1]["answer"] = line.strip()
                        
                        if in_root_cause_section and line.strip():
                            root_cause = line.strip()
                            in_root_cause_section = False
                
                trigger_data['five_why_analysis'] = five_why_analysis
                trigger_data['root_cause'] = root_cause
            elif self.document_type == 'гипотеза':
                # Для гипотез извлекаем RAT и критерий фальсифицируемости
                description = kwargs.get('description', '')
                rat = "Не указан"
                falsifiability = "Не указан"
                
                if description:
                    lines = description.split("\n")
                    for i, line in enumerate(lines):
                        if "RAT:" in line or "Реалистичность, Амбициозность, Тестируемость:" in line:
                            if i+1 < len(lines) and lines[i+1].strip():
                                rat = lines[i+1].strip()
                        if "Критерий фальсифицируемости:" in line or "Фальсифицируемость:" in line:
                            if i+1 < len(lines) and lines[i+1].strip():
                                falsifiability = lines[i+1].strip()
                
                trigger_data['rat'] = kwargs.get('rat', rat)
                trigger_data['falsifiability'] = kwargs.get('falsifiability', falsifiability)
            
            # Создаем контекст триггера
            context = TriggerContext(
                trigger_type=trigger_type,
                data=trigger_data,
                timestamp=datetime.now().timestamp(),
                source="document_unified_interface.py"
            )
            
            # Получаем обработчик триггеров и активируем триггер
            handler = get_handler(report_progress)
            result = handler.handle_trigger(context)
            
            if result.success:
                logger.info(f"Триггер {trigger_type} успешно активирован: {result.message}")
            else:
                logger.warning(f"Ошибка при активации триггера {trigger_type}: {result.message}")
        
        except Exception as e:
            logger.error(f"Ошибка при активации триггера для документа {self.document_type} с ID {doc_id}: {e}")
            import traceback
            traceback.print_exc()
    
    def _format_document_for_consolidated(self, doc_id: str, **kwargs) -> str:
        """
        Форматирует документ для добавления в консолидированный файл.
        
        Args:
            doc_id: Идентификатор документа
            **kwargs: Атрибуты документа
            
        Returns:
            str: Отформатированное содержимое документа
        """
        title = kwargs.get('title', f"Новый {self.document_type}")
        doc_content = f"{self.item_marker} {self.document_type.title()}: {title} #{doc_id}\n\n"
        
        # Добавляем атрибуты документа
        for key, value in kwargs.items():
            if key != 'title':
                doc_content += f"**{key.title()}**: {value}\n"
        
        return doc_content
    
    def _parse_document_from_consolidated(self, doc_content: str) -> Dict[str, Any]:
        """
        Парсит данные документа из консолидированного файла.
        
        Args:
            doc_content: Содержимое документа
            
        Returns:
            Dict[str, Any]: Данные документа
        """
        data = {}
        
        # Извлекаем заголовок
        title_pattern = re.compile(f"{self.item_marker} {self.document_type.title()}: (.*) #")
        title_match = title_pattern.search(doc_content)
        if title_match:
            data['title'] = title_match.group(1).strip()
        
        # Извлекаем атрибуты
        attr_pattern = re.compile(r"\*\*(.*?)\*\*: (.*?)(?:\n|$)")
        for match in attr_pattern.finditer(doc_content):
            key = match.group(1).lower()
            value = match.group(2).strip()
            data[key] = value
        
        # Добавляем описание, если его нет, но оно может понадобиться
        if 'description' not in data and 'описание' in data:
            data['description'] = data['описание']
        elif 'description' not in data:
            data['description'] = ""
            
        # Добавляем другие часто используемые поля, если их нет
        if 'priority' not in data and 'приоритет' in data:
            data['priority'] = data['приоритет']
        elif 'priority' not in data:
            data['priority'] = ""
            
        if 'status' not in data and 'статус' in data:
            data['status'] = data['статус']
        elif 'status' not in data:
            data['status'] = ""
        
        return data
    
    def migrate_separate_file(self, file_path: str) -> bool:
        """
        Мигрирует отдельный файл в консолидированный документ.
        
        Args:
            file_path: Путь к отдельному файлу
            
        Returns:
            bool: True, если миграция успешна, иначе False
        """
        logger.info(f"Миграция отдельного файла {file_path}")
        
        # Проверяем, существует ли файл
        full_path = os.path.join(self.base_dir, file_path)
        if not os.path.exists(full_path):
            logger.error(f"Файл {full_path} не найден")
            return False
        
        # Читаем файл
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Парсим данные из файла
        data = self._parse_separate_file(content)
        
        # Создаем новый документ в консолидированном файле
        doc_id = self.create(**data)
        
        if not doc_id:
            logger.error(f"Не удалось создать документ из файла {file_path}")
            return False
        
        # Архивируем или удаляем исходный файл
        archive_dir = os.path.join(self.base_dir, 'archive', os.path.dirname(file_path))
        os.makedirs(archive_dir, exist_ok=True)
        
        archive_path = os.path.join(archive_dir, os.path.basename(file_path))
        try:
            # Перемещаем файл в архив
            os.rename(full_path, archive_path)
            logger.info(f"Файл {file_path} перемещен в архив {archive_path}")
        except Exception as e:
            logger.error(f"Ошибка при архивации файла {file_path}: {e}")
            # Если не удалось переместить, удаляем
            try:
                os.remove(full_path)
                logger.info(f"Файл {file_path} удален")
            except Exception as e2:
                logger.error(f"Ошибка при удалении файла {file_path}: {e2}")
                return False
        
        logger.info(f"Миграция файла {file_path} успешно завершена")
        return True
    
    def _parse_separate_file(self, content: str) -> Dict[str, Any]:
        """
        Парсит данные из отдельного файла.
        
        Args:
            content: Содержимое файла
            
        Returns:
            Dict[str, Any]: Данные документа
        """
        data = {}
        
        # Извлекаем заголовок
        title_patterns = [
            re.compile(r"# (?:.*): (.*?)(?:\n|$)"),  # формат "# Задача: Название задачи"
            re.compile(r"# (.*?)(?:\n|$)")           # простой формат "# Название"
        ]
        
        for pattern in title_patterns:
            title_match = pattern.search(content)
            if title_match:
                data['title'] = title_match.group(1).strip()
                break
        
        # Если заголовок не найден, используем default
        if 'title' not in data:
            data['title'] = f"Мигрированный документ {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Извлекаем описание - все, что между заголовком и первым атрибутом
        description_match = re.search(r"#.*?\n(.*?)(?:\n\*\*|\Z)", content, re.DOTALL)
        if description_match:
            description = description_match.group(1).strip()
            if description:
                data['description'] = description
        
        # Извлекаем атрибуты
        attr_pattern = re.compile(r"\*\*(.*?)\*\*: (.*?)(?:\n|$)")
        for match in attr_pattern.finditer(content):
            key = match.group(1).lower()
            value = match.group(2).strip()
            data[key] = value
        
        # Добавляем стандартные атрибуты, если их нет
        if 'priority' not in data and 'приоритет' not in data:
            data['priority'] = 'Средний'
            
        if 'status' not in data and 'статус' not in data:
            data['status'] = 'Не начато'
            
        if 'created_at' not in data and 'дата создания' not in data:
            data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
            
        if 'author' not in data and 'автор' not in data:
            data['author'] = 'System Migration'
        
        return data
    
    def bulk_migrate_separate_files(self) -> Dict[str, int]:
        """
        Выполняет массовую миграцию отдельных файлов в консолидированные документы.
        
        Returns:
            Dict[str, int]: Результаты миграции {total: int, success: int, failed: int}
        """
        logger.info(f"Запуск массовой миграции отдельных файлов")
        
        # Результаты миграции
        results = {
            'total': 0,
            'success': 0,
            'failed': 0
        }
        
        # Определяем директории в зависимости от типа документов
        dirs_to_check = {
            'задача': ['todo'],
            'инцидент': ['incidents'],
            'стандарт': ['standards'],
            'гипотеза': ['hypotheses']
        }
        
        # Если у нас базовый класс, проверяем все директории
        if self.document_type == 'generic':
            directories = sum(dirs_to_check.values(), [])
        else:
            directories = dirs_to_check.get(self.document_type, [])
        
        # Обрабатываем файлы в каждой директории
        separate_files = []
        
        for directory in directories:
            separate_dir = os.path.join(self.base_dir, directory)
            
            if not os.path.exists(separate_dir) or not os.path.isdir(separate_dir):
                logger.warning(f"Директория {separate_dir} не найдена или не является директорией")
                continue
            
            # Определяем паттерн в зависимости от директории
            if directory == 'todo':
                file_pattern = r"task_.*\.md"
            elif directory == 'incidents':
                file_pattern = r"incident_.*\.md"
            elif directory == 'standards':
                file_pattern = r"standard_.*\.md"
            elif directory == 'hypotheses':
                file_pattern = r"hypothesis_.*\.md"
            else:
                file_pattern = r".*_.*\.md"
            
            # Получаем список файлов для миграции
            for root, dirs, files in os.walk(separate_dir):
                for file in files:
                    if re.match(file_pattern, file):
                        rel_path = os.path.relpath(os.path.join(root, file), self.base_dir)
                        separate_files.append(rel_path)
        
        results['total'] = len(separate_files)
        
        # Мигрируем каждый файл
        for file_path in separate_files:
            try:
                # Определяем класс документа для миграции на основе пути файла
                if file_path.startswith('todo/'):
                    doc_interface = TaskDocument(self.base_dir)
                elif file_path.startswith('incidents/'):
                    doc_interface = IncidentDocument(self.base_dir)
                elif file_path.startswith('standards/'):
                    doc_interface = StandardDocument(self.base_dir)
                elif file_path.startswith('hypotheses/'):
                    doc_interface = HypothesisDocument(self.base_dir)
                else:
                    # Используем текущий интерфейс, если не удалось определить тип
                    doc_interface = self
                
                success = doc_interface.migrate_separate_file(file_path)
                if success:
                    results['success'] += 1
                else:
                    results['failed'] += 1
            except Exception as e:
                logger.error(f"Ошибка при миграции файла {file_path}: {e}")
                results['failed'] += 1
        
        logger.info(f"Массовая миграция завершена. Результаты: {results}")
        return results


class TaskDocument(DocumentInterface):
    """JTBD:
Я (разработчик) хочу использовать функциональность класса TaskDocument, чтобы эффективно решать соответствующие задачи в системе.
    
    Класс для работы с задачами."""
    
    def __init__(self, base_dir: str = '.'):
        """
        Инициализирует интерфейс задач.
        
        Args:
            base_dir: Базовая директория проекта
        """
        super().__init__(base_dir)
        self.document_type = "задача"
        self.consolidated_file = "todo.md"
        self.section_marker = "##"
        self.item_marker = "###"


class IncidentDocument(DocumentInterface):
    """JTBD:
Я (разработчик) хочу использовать функциональность класса IncidentDocument, чтобы эффективно решать соответствующие задачи в системе.
    
    Класс для работы с инцидентами."""
    
    def __init__(self, base_dir: str = '.'):
        """
        Инициализирует интерфейс инцидентов.
        
        Args:
            base_dir: Базовая директория проекта
        """
        super().__init__(base_dir)
        self.document_type = "инцидент"
        self.consolidated_file = "incidents.md"
        self.section_marker = "##"
        self.item_marker = "###"


class StandardDocument(DocumentInterface):
    """JTBD:
Я (разработчик) хочу использовать функциональность класса StandardDocument, чтобы эффективно решать соответствующие задачи в системе.
    
    Класс для работы со стандартами."""
    
    def __init__(self, base_dir: str = '.'):
        """
        Инициализирует интерфейс стандартов.
        
        Args:
            base_dir: Базовая директория проекта
        """
        super().__init__(base_dir)
        self.document_type = "стандарт"
        self.consolidated_file = "standards.md"
        self.section_marker = "##"
        self.item_marker = "###"


class HypothesisDocument(DocumentInterface):
    """JTBD:
Я (разработчик) хочу использовать функциональность класса HypothesisDocument, чтобы эффективно решать соответствующие задачи в системе.
    
    Класс для работы с гипотезами."""
    
    def __init__(self, base_dir: str = '.'):
        """
        Инициализирует интерфейс гипотез.
        
        Args:
            base_dir: Базовая директория проекта
        """
        super().__init__(base_dir)
        self.document_type = "гипотеза"
        self.consolidated_file = "hypotheses.md"
        self.section_marker = "##"
        self.item_marker = "###"


def main():
    """
    Основная функция для демонстрации и тестирования интерфейса документов.
    """
    # Инициализируем интерфейсы для разных типов документов
    task_doc = TaskDocument()
    incident_doc = IncidentDocument()
    standard_doc = StandardDocument()
    hypothesis_doc = HypothesisDocument()
    
    # Демонстрируем создание документов
    print("Создание тестовой задачи...")
    task_id = task_doc.create(
        title="Тестовая задача",
        description="Описание тестовой задачи",
        priority="Высокий",
        status="Не начато"
    )
    print(f"Создана задача с ID: {task_id}")
    
    print("\nСоздание тестового инцидента...")
    incident_id = incident_doc.create(
        title="Тестовый инцидент",
        description="Описание тестового инцидента",
        priority="Критический",
        status="Открыт"
    )
    print(f"Создан инцидент с ID: {incident_id}")
    
    # Демонстрируем чтение документов
    print("\nЧтение созданной задачи...")
    task = task_doc.read(task_id)
    print(f"Задача: {task}")
    
    # Демонстрируем обновление документов
    print("\nОбновление задачи...")
    task_doc.update(task_id, {
        'status': 'В процессе',
        'priority': 'Средний'
    })
    print("Задача обновлена")
    
    # Проверяем обновленную задачу
    task = task_doc.read(task_id)
    print(f"Обновленная задача: {task}")
    
    print("\nГотово!")


if __name__ == "__main__":
    main()