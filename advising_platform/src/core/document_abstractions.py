#!/usr/bin/env python3
"""
Система абстрактных идентификаторов и управления документами для проекта.
Позволяет работать с документами через логические идентификаторы вместо жестких ссылок.
"""

import os
import re
import json
import hashlib
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set, Union

class DocumentIdentifier:
    """JTBD:
Я (разработчик) хочу использовать функциональность класса DocumentIdentifier, чтобы эффективно решать соответствующие задачи в системе.
    
    Класс для работы с абстрактными идентификаторами документов."""
    
    # Типы документов
    DOC_TYPE_STANDARD = "standard"
    DOC_TYPE_PROJECT = "project"
    DOC_TYPE_INCIDENT = "incident"
    DOC_TYPE_GUIDE = "guide"
    DOC_TYPE_TASK = "task"
    DOC_TYPE_OTHER = "other"
    
    # Подтипы проектных документов
    PROJECT_TYPE_ARCHITECTURE = "architecture"
    PROJECT_TYPE_INTEGRATION = "integration"
    PROJECT_TYPE_TECHNICAL = "technical"
    PROJECT_TYPE_GOAL_MAP = "goal_map"
    PROJECT_TYPE_CONTEXT = "context"
    PROJECT_TYPE_DIAGNOSTIC = "diagnostic"
    
    def __init__(self, doc_type: str, primary_id: str, secondary_id: Optional[str] = None):
        """
        Инициализирует идентификатор документа.
        
        Args:
            doc_type: Тип документа (standard, project, incident, etc.)
            primary_id: Первичный идентификатор (имя стандарта, проекта и т.д.)
            secondary_id: Вторичный идентификатор (подтип документа для проектов)
        """
        self.doc_type = doc_type.lower()
        self.primary_id = primary_id.lower()
        self.secondary_id = secondary_id.lower() if secondary_id else None
    
    @classmethod
    def from_string(cls, identifier_str: str) -> 'DocumentIdentifier':
        """
        Создает идентификатор из строкового представления.
        
        Args:
            identifier_str: Строка вида "type:primary_id[:secondary_id]"
        
        Returns:
            Объект DocumentIdentifier
        
        Raises:
            ValueError: Если строка имеет неправильный формат
        """
        parts = identifier_str.split(':')
        if len(parts) < 2:
            raise ValueError(f"Неверный формат идентификатора: {identifier_str}")
        
        doc_type = parts[0]
        primary_id = parts[1]
        secondary_id = parts[2] if len(parts) > 2 else None
        
        return cls(doc_type, primary_id, secondary_id)
    
    def to_string(self) -> str:
        """
        Преобразует идентификатор в строковое представление.
        
        Returns:
            Строка вида "type:primary_id[:secondary_id]"
        """
        if self.secondary_id:
            return f"{self.doc_type}:{self.primary_id}:{self.secondary_id}"
        return f"{self.doc_type}:{self.primary_id}"
    
    def __str__(self) -> str:
        return self.to_string()
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, DocumentIdentifier):
            return False
        return (self.doc_type == other.doc_type and 
                self.primary_id == other.primary_id and 
                self.secondary_id == other.secondary_id)
    
    def __hash__(self) -> int:
        return hash((self.doc_type, self.primary_id, self.secondary_id))


class DocumentMetadata:
    """JTBD:
Я (разработчик) хочу использовать функциональность класса DocumentMetadata, чтобы эффективно решать соответствующие задачи в системе.
    
    Класс для хранения и работы с метаданными документов."""
    
    def __init__(self, path: str, title: str = None, date: str = None, 
                 author: str = None, doc_type: str = None, based_on: str = None,
                 version: str = None, content_hash: str = None):
        """
        Инициализирует метаданные документа.
        
        Args:
            path: Путь к файлу документа
            title: Заголовок документа
            date: Дата создания/обновления
            author: Автор документа
            doc_type: Тип документа
            based_on: Ссылка на базовый документ
            version: Версия документа
            content_hash: Хеш содержимого для идентификации
        """
        self.path = path
        self.title = title
        self.date = date
        self.author = author
        self.doc_type = doc_type
        self.based_on = based_on
        self.version = version
        self.content_hash = content_hash
        self.filename = os.path.basename(path)
        self.directory = os.path.dirname(path)
    
    @classmethod
    def from_file(cls, file_path: str) -> 'DocumentMetadata':
        """
        Создает объект метаданных из файла.
        
        Args:
            file_path: Путь к файлу документа
        
        Returns:
            Объект DocumentMetadata с извлеченными метаданными
        """
        metadata = cls(path=file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Вычисляем хеш содержимого
            metadata.content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            
            # Извлекаем заголовок (первая строка с #)
            title_match = re.search(r'^#\s+(.*?)$', content, re.MULTILINE)
            if title_match:
                metadata.title = title_match.group(1).strip()
            
            # Извлекаем дату в формате "updated: DD month YYYY"
            date_match = re.search(r'updated:\s*(\d+\s+\w+\s+\d{4}(?:,\s*\d{2}:\d{2}\s*\w+)?)', content)
            if date_match:
                metadata.date = date_match.group(1).strip()
            else:
                # Альтернативный формат даты в имени файла
                alt_date_match = re.search(r'(\d+\s+\w+\s+\d{4})', metadata.filename)
                if alt_date_match:
                    metadata.date = alt_date_match.group(1).strip()
            
            # Извлекаем автора
            author_match = re.search(r'by\s+([^,\n]+)', content)
            if author_match:
                metadata.author = author_match.group(1).strip()
            else:
                # Альтернативный поиск автора в имени файла
                alt_author_match = re.search(r'by\s+([^\.]+)', metadata.filename)
                if alt_author_match:
                    metadata.author = alt_author_match.group(1).strip()
            
            # Определяем тип документа
            metadata.doc_type = cls._determine_document_type(file_path, content)
            
            # Ищем based_on
            based_on_match = re.search(r'based\s+on:\s+(.*?)(?:$|\n)', content, re.IGNORECASE)
            if based_on_match:
                metadata.based_on = based_on_match.group(1).strip()
            
            # Ищем версию
            version_match = re.search(r'version[:\s]+(\d+(?:\.\d+)*)', content, re.IGNORECASE)
            if version_match:
                metadata.version = version_match.group(1).strip()
            
        except Exception as e:
            print(f"Ошибка при извлечении метаданных из {file_path}: {e}")
        
        return metadata
    
    @staticmethod
    def _determine_document_type(file_path: str, content: str) -> str:
        """
        Определяет тип документа на основе его расположения и содержимого.
        
        Args:
            file_path: Путь к файлу
            content: Содержимое файла
        
        Returns:
            Тип документа
        """
        file_path_lower = file_path.lower()
        
        if 'advising standards .md' in file_path_lower:
            if 'archive' in file_path_lower:
                return 'archived_standard'
            return DocumentIdentifier.DOC_TYPE_STANDARD
        
        if 'projects/' in file_path_lower:
            # Определяем подтип проектного документа
            if 'architecture' in file_path_lower or 'architecture' in content.lower():
                return f"{DocumentIdentifier.DOC_TYPE_PROJECT}_{DocumentIdentifier.PROJECT_TYPE_ARCHITECTURE}"
            elif 'integration' in file_path_lower or 'integration' in content.lower():
                return f"{DocumentIdentifier.DOC_TYPE_PROJECT}_{DocumentIdentifier.PROJECT_TYPE_INTEGRATION}"
            elif 'technical' in file_path_lower or 'technical' in content.lower():
                return f"{DocumentIdentifier.DOC_TYPE_PROJECT}_{DocumentIdentifier.PROJECT_TYPE_TECHNICAL}"
            elif 'goal_map' in file_path_lower or 'goal map' in content.lower():
                return f"{DocumentIdentifier.DOC_TYPE_PROJECT}_{DocumentIdentifier.PROJECT_TYPE_GOAL_MAP}"
            return DocumentIdentifier.DOC_TYPE_PROJECT
        
        if 'incidents/' in file_path_lower:
            return DocumentIdentifier.DOC_TYPE_INCIDENT
        
        if 'docs/' in file_path_lower:
            return DocumentIdentifier.DOC_TYPE_GUIDE
        
        if 'todo' in file_path_lower:
            return DocumentIdentifier.DOC_TYPE_TASK
        
        # Дополнительное определение типа по содержимому
        if 'JTBD' in content or 'Job to be done' in content:
            return 'jtbd'
        if 'Root Cause' in content or 'Корневая причина' in content:
            return 'root_cause'
            
        return DocumentIdentifier.DOC_TYPE_OTHER
    
    def is_newer_than(self, other: 'DocumentMetadata') -> bool:
        """
        Проверяет, является ли данный документ более новой версией, чем другой.
        
        Args:
            other: Другой объект DocumentMetadata для сравнения
        
        Returns:
            True если текущий документ новее, False в противном случае
        """
        if not self.date or not other.date:
            return False
        
        # Простое сравнение дат
        return self.date > other.date
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует метаданные в словарь.
        
        Returns:
            Словарь с метаданными
        """
        return {
            'path': self.path,
            'filename': self.filename,
            'directory': self.directory,
            'title': self.title,
            'date': self.date,
            'author': self.author,
            'doc_type': self.doc_type,
            'based_on': self.based_on,
            'version': self.version,
            'content_hash': self.content_hash
        }


class DocumentRegistry:
    """JTBD:
Я (разработчик) хочу использовать функциональность класса DocumentRegistry, чтобы эффективно решать соответствующие задачи в системе.
    
    Реестр документов с поддержкой абстрактных идентификаторов."""
    
    def __init__(self, root_dir: str = '.'):
        """
        Инициализирует реестр документов.
        
        Args:
            root_dir: Корневая директория проекта
        """
        self.root_dir = root_dir
        self.documents = {}  # path -> DocumentMetadata
        self.id_mapping = {}  # DocumentIdentifier -> DocumentMetadata
        self.link_mapping = {}  # path -> [path]
        self.indexes = {
            'by_type': defaultdict(list),
            'by_author': defaultdict(list),
            'by_title': defaultdict(list),
            'by_content_hash': defaultdict(list),
            'by_date': defaultdict(list),
        }
        
        # Инициализируем реестр
        self.scan_documents()
        self.build_indexes()
        self.build_id_mapping()
    
    def scan_documents(self) -> None:
        """JTBD:
Я (разработчик) хочу использовать функцию scan_documents, чтобы эффективно выполнить соответствующую операцию.
         
         Сканирует все markdown документы в проекте."""
        # Директории, которые следует пропустить
        skip_dirs = ['.git', 'node_modules', '__pycache__', '.roo', '.cursor', '.cache']
        
        # Список конкретных путей к файлам, которые нам нужно проверить
        specific_paths = [
            './projects/rick.ai/docs_specs/rick_ai_technical_documentation.md',
            './projects/rick.ai/docs_specs/rick_ai_architecture_specification.md',
            './projects/rask.ai/rask_ai_rick_ai_integration_spec.md',
            './projects/rask.ai/rask_ai_rick_ai_integration_goal_map.md',
            './todo.md',
            './docs/advising_instructions.md',
            './docs/project_structure.md'
        ]
        
        # Проверяем и добавляем конкретные файлы
        for path in specific_paths:
            normalized_path = os.path.normpath(path)
            if os.path.exists(normalized_path) and os.path.isfile(normalized_path):
                try:
                    metadata = DocumentMetadata.from_file(normalized_path)
                    self.documents[normalized_path] = metadata
                    print(f"Проиндексирован конкретный файл: {normalized_path}")
                except Exception as e:
                    print(f"Ошибка при обработке конкретного файла {normalized_path}: {e}")
        
        # Обходим все файлы проекта
        for root, dirs, files in os.walk(self.root_dir):
            # Исключаем нежелательные директории
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                if file.endswith('.md'):
                    full_path = os.path.join(root, file)
                    full_path = os.path.normpath(full_path)
                    
                    # Если файл уже обработан в конкретных путях, пропускаем
                    if full_path in self.documents:
                        continue
                        
                    try:
                        metadata = DocumentMetadata.from_file(full_path)
                        self.documents[full_path] = metadata
                    except Exception as e:
                        print(f"Ошибка при обработке файла {full_path}: {e}")
        
        print(f"Проиндексировано {len(self.documents)} документов")
    
    def build_indexes(self) -> None:
        """JTBD:
Я (разработчик) хочу использовать функцию build_indexes, чтобы эффективно выполнить соответствующую операцию.
         
         Строит индексы для быстрого доступа к документам."""
        for path, metadata in self.documents.items():
            # Индексирование по типу
            if metadata.doc_type:
                self.indexes['by_type'][metadata.doc_type].append(path)
            
            # Индексирование по автору
            if metadata.author:
                self.indexes['by_author'][metadata.author].append(path)
            
            # Индексирование по заголовку
            if metadata.title:
                self.indexes['by_title'][metadata.title].append(path)
            
            # Индексирование по хешу содержимого
            if metadata.content_hash:
                self.indexes['by_content_hash'][metadata.content_hash].append(path)
            
            # Индексирование по дате
            if metadata.date:
                self.indexes['by_date'][metadata.date].append(path)
    
    def create_identifier(self, metadata: DocumentMetadata) -> Optional[DocumentIdentifier]:
        """
        Создает логический идентификатор для документа.
        
        Args:
            metadata: Метаданные документа
        
        Returns:
            Объект DocumentIdentifier или None, если не удалось создать идентификатор
        """
        try:
            doc_type = metadata.doc_type
            path = metadata.path
            filename = metadata.filename
            
            # Определяем базовые параметры идентификатора
            identifier_type = None
            primary_id = None
            secondary_id = None
            
            # Стандарты
            if doc_type == DocumentIdentifier.DOC_TYPE_STANDARD or 'standard' in doc_type:
                identifier_type = DocumentIdentifier.DOC_TYPE_STANDARD
                
                # Извлекаем базовое имя стандарта
                # Сначала обработаем особые случаи
                if filename.startswith('0. task master'):
                    base_name = 'task_master'
                else:
                    # Удаляем префикс с номером (e.g., "1.0 ", "2.5 ", etc.)
                    base_name = re.sub(r'^\d+\.?\d*\s+', '', filename)
                    # Удаляем дату и автора (e.g., "11 may 2025 1900 CET by Advising Assistant")
                    base_name = re.sub(r'\d+\s+\w+\s+\d{4}.*', '', base_name)
                    # Удаляем расширение .md
                    base_name = base_name.replace('.md', '')
                    # Преобразуем в snake_case
                    base_name = base_name.lower().replace(' ', '_')
                    # Удаляем лишние символы
                    base_name = re.sub(r'[^\w_]', '', base_name)
                    # Удаляем лишние пробелы и подчеркивания
                    base_name = base_name.strip('_').strip()
                
                primary_id = base_name
            
            # Проектные документы
            elif doc_type.startswith(DocumentIdentifier.DOC_TYPE_PROJECT) or 'project' in path.lower():
                identifier_type = DocumentIdentifier.DOC_TYPE_PROJECT
                
                # Определяем имя проекта
                project_match = re.search(r'projects/([^/]+)', path)
                if project_match:
                    primary_id = project_match.group(1)
                else:
                    primary_id = "unknown_project"
                
                # Определяем подтип документа
                if '_' in doc_type:
                    secondary_id = doc_type.split('_')[1]
                elif 'architecture' in filename.lower() or 'architecture' in path.lower():
                    secondary_id = DocumentIdentifier.PROJECT_TYPE_ARCHITECTURE
                elif 'integration' in filename.lower() or 'integration' in path.lower():
                    secondary_id = DocumentIdentifier.PROJECT_TYPE_INTEGRATION
                elif 'technical' in filename.lower() or 'technical' in path.lower():
                    secondary_id = DocumentIdentifier.PROJECT_TYPE_TECHNICAL
                elif 'goal_map' in filename.lower() or 'goal_map' in path.lower():
                    secondary_id = DocumentIdentifier.PROJECT_TYPE_GOAL_MAP
                else:
                    secondary_id = "general"
            
            # Инциденты
            elif doc_type == DocumentIdentifier.DOC_TYPE_INCIDENT:
                identifier_type = DocumentIdentifier.DOC_TYPE_INCIDENT
                
                # Используем заголовок или имя файла для идентификатора
                if metadata.title:
                    # Преобразуем заголовок в slug
                    primary_id = re.sub(r'[^\w\s]', '', metadata.title.lower())
                    primary_id = primary_id.replace(' ', '_')
                else:
                    # Используем имя файла без расширения
                    primary_id = os.path.splitext(filename)[0]
            
            # Руководства
            elif doc_type == DocumentIdentifier.DOC_TYPE_GUIDE:
                identifier_type = DocumentIdentifier.DOC_TYPE_GUIDE
                
                # Используем имя файла без расширения
                primary_id = os.path.splitext(filename)[0]
            
            # Задачи
            elif doc_type == DocumentIdentifier.DOC_TYPE_TASK:
                identifier_type = DocumentIdentifier.DOC_TYPE_TASK
                
                # Используем имя файла без расширения
                primary_id = os.path.splitext(filename)[0]
            
            # Другие типы документов
            else:
                identifier_type = DocumentIdentifier.DOC_TYPE_OTHER
                
                # Используем хеш содержимого как идентификатор
                primary_id = metadata.content_hash[:8] if metadata.content_hash else os.path.splitext(filename)[0]
            
            return DocumentIdentifier(identifier_type, primary_id, secondary_id)
        
        except Exception as e:
            print(f"Ошибка при создании идентификатора для {metadata.path}: {e}")
            return None
    
    def build_id_mapping(self) -> None:
        """JTBD:
Я (разработчик) хочу использовать функцию build_id_mapping, чтобы эффективно выполнить соответствующую операцию.
         
         Строит отображение логических идентификаторов в документы."""
        for path, metadata in self.documents.items():
            identifier = self.create_identifier(metadata)
            if identifier:
                identifier_str = identifier.to_string()
                
                # Если идентификатор уже существует, выбираем более новый документ
                if identifier_str in self.id_mapping:
                    existing_metadata = self.id_mapping[identifier_str]
                    if metadata.is_newer_than(existing_metadata):
                        self.id_mapping[identifier_str] = metadata
                else:
                    self.id_mapping[identifier_str] = metadata
        
        print(f"Создано {len(self.id_mapping)} логических идентификаторов")
    
    def get_document(self, identifier: str) -> Optional[DocumentMetadata]:
        """
        Получает метаданные документа по логическому идентификатору.
        
        Args:
            identifier: Строка логического идентификатора (например, "standard:task_master")
        
        Returns:
            Объект DocumentMetadata или None, если документ не найден
        """
        return self.id_mapping.get(identifier)
    
    def get_document_content(self, identifier: str) -> Optional[str]:
        """
        Получает содержимое документа по логическому идентификатору.
        
        Args:
            identifier: Строка логического идентификатора
        
        Returns:
            Строка с содержимым документа или None, если документ не найден
        """
        metadata = self.get_document(identifier)
        if not metadata:
            return None
        
        try:
            with open(metadata.path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Ошибка при чтении документа {metadata.path}: {e}")
            return None
    
    def get_standard(self, standard_name: str) -> Optional[DocumentMetadata]:
        """
        Получает метаданные стандарта по имени.
        
        Args:
            standard_name: Имя стандарта
        
        Returns:
            Объект DocumentMetadata или None, если стандарт не найден
        """
        identifier = f"standard:{standard_name}"
        return self.get_document(identifier)
    
    def get_project_document(self, project_name: str, doc_type: str = None) -> List[DocumentMetadata]:
        """
        Получает метаданные документов проекта.
        
        Args:
            project_name: Имя проекта
            doc_type: Тип документа проекта (architecture, integration, etc.)
        
        Returns:
            Список объектов DocumentMetadata
        """
        result = []
        
        if doc_type:
            identifier = f"project:{project_name}:{doc_type}"
            metadata = self.get_document(identifier)
            if metadata:
                result.append(metadata)
        else:
            # Получаем все документы проекта
            for identifier, metadata in self.id_mapping.items():
                if identifier.startswith(f"project:{project_name}:"):
                    result.append(metadata)
        
        return result
    
    def search(self, query: str) -> List[DocumentMetadata]:
        """
        Ищет документы по содержимому и метаданным.
        
        Args:
            query: Поисковый запрос
        
        Returns:
            Список объектов DocumentMetadata
        """
        result = []
        query_lower = query.lower()
        
        # Поиск по заголовкам
        for path_list in self.indexes['by_title'].values():
            for path in path_list:
                metadata = self.documents[path]
                if metadata.title and query_lower in metadata.title.lower():
                    result.append(metadata)
        
        # Поиск по содержимому (если результатов мало)
        if len(result) < 5:
            for path, metadata in self.documents.items():
                if metadata not in result:  # Избегаем дубликатов
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        if query_lower in content.lower():
                            result.append(metadata)
                    except Exception:
                        pass
        
        return result
    
    def find_links_in_content(self, content: str) -> List[Tuple[str, str]]:
        """
        Находит markdown-ссылки в содержимом.
        
        Args:
            content: Содержимое документа
        
        Returns:
            Список кортежей (текст_ссылки, цель_ссылки)
        """
        # Регулярное выражение для поиска markdown-ссылок
        link_pattern = re.compile(r'\[(.*?)\]\((.*?)\)')
        return link_pattern.findall(content)
    
    def convert_to_abstract_links(self, content: str, base_path: str) -> str:
        """
        Преобразует жесткие ссылки в абстрактные.
        
        Args:
            content: Содержимое документа
            base_path: Базовый путь для разрешения относительных ссылок
        
        Returns:
            Содержимое с абстрактными ссылками
        """
        links = self.find_links_in_content(content)
        base_dir = os.path.dirname(base_path)
        
        print(f"Найдено {len(links)} ссылок в документе {base_path}")
        
        for link_text, link_target in links:
            print(f"Обработка ссылки: [{link_text}]({link_target})")
            
            # Пропускаем ссылки, которые уже абстрактные или внешние
            if link_target.startswith('abstract://') or link_target.startswith('http'):
                print(f"  - Пропуск: ссылка уже абстрактная или внешняя")
                continue
            
            # Пропускаем якорные ссылки
            if link_target.startswith('#'):
                print(f"  - Пропуск: якорная ссылка")
                continue
            
            # Проверяем, что ссылка ведет на markdown-файл
            if not link_target.endswith('.md'):
                print(f"  - Пропуск: не markdown-файл")
                continue
            
            # Пытаемся найти целевой файл
            target_path = None
            
            # Абсолютный путь
            if os.path.exists(link_target):
                target_path = link_target
                print(f"  - Найден абсолютный путь: {target_path}")
            
            # Относительный путь
            relative_path = os.path.normpath(os.path.join(base_dir, link_target))
            if os.path.exists(relative_path):
                target_path = relative_path
                print(f"  - Найден относительный путь: {target_path}")
            
            if not target_path:
                print(f"  - Ошибка: целевой файл не найден")
                continue
                
            if target_path not in self.documents:
                print(f"  - Ошибка: целевой файл не проиндексирован")
                continue
                
            # Создаем абстрактный идентификатор
            metadata = self.documents[target_path]
            identifier = self.create_identifier(metadata)
            if not identifier:
                print(f"  - Ошибка: не удалось создать идентификатор")
                continue
                
            # Заменяем ссылку
            abstract_link = f"abstract://{identifier.to_string()}"
            print(f"  - Замена на: [{link_text}]({abstract_link})")
            
            content = content.replace(
                f"[{link_text}]({link_target})",
                f"[{link_text}]({abstract_link})"
            )
        
        return content
    
    def convert_from_abstract_links(self, content: str) -> str:
        """
        Преобразует абстрактные ссылки в физические.
        
        Args:
            content: Содержимое документа
        
        Returns:
            Содержимое с физическими ссылками
        """
        # Регулярное выражение для поиска абстрактных ссылок
        abstract_pattern = re.compile(r'\[(.*?)\]\(abstract://(.*?)\)')
        
        for match in abstract_pattern.finditer(content):
            link_text = match.group(1)
            identifier_str = match.group(2)
            
            # Находим документ по идентификатору
            metadata = self.get_document(identifier_str)
            if metadata:
                # Заменяем абстрактную ссылку на физическую
                physical_path = metadata.path
                content = content.replace(
                    f"[{link_text}](abstract://{identifier_str})",
                    f"[{link_text}]({physical_path})"
                )
        
        return content
    
    def update_document_links(self, path: str, to_abstract: bool = True) -> bool:
        """
        Обновляет ссылки в документе.
        
        Args:
            path: Путь к документу
            to_abstract: True для преобразования в абстрактные ссылки,
                        False для преобразования из абстрактных ссылок
        
        Returns:
            True если документ успешно обновлен, False в случае ошибки
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if to_abstract:
                updated_content = self.convert_to_abstract_links(content, path)
            else:
                updated_content = self.convert_from_abstract_links(content)
            
            if content != updated_content:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                print(f"Документ {path} успешно обновлен")
                return True
            else:
                print(f"Документ {path} не требует обновления")
                return True
        
        except Exception as e:
            print(f"Ошибка при обновлении ссылок в {path}: {e}")
            return False
    
    def export_to_json(self, output_file: str = 'document_registry.json') -> None:
        """
        Экспортирует реестр в JSON-файл.
        
        Args:
            output_file: Имя файла для сохранения
        """
        data = {
            'documents': {},
            'id_mapping': {}
        }
        
        # Экспортируем документы
        for path, metadata in self.documents.items():
            data['documents'][path] = metadata.to_dict()
        
        # Экспортируем отображение идентификаторов
        for identifier, metadata in self.id_mapping.items():
            data['id_mapping'][identifier] = metadata.path
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Реестр документов экспортирован в {output_file}")


if __name__ == "__main__":
    # Пример использования
    registry = DocumentRegistry()
    
    # Поиск стандарта по имени
    task_master = registry.get_standard("task_master")
    if task_master:
        print(f"Найден стандарт Task Master: {task_master.path}")
        print(f"  Заголовок: {task_master.title}")
        print(f"  Дата: {task_master.date}")
        print(f"  Автор: {task_master.author}")
    else:
        print("Стандарт Task Master не найден")
        
        # Поиск похожих стандартов
        print("Поиск похожих стандартов:")
        similar_docs = registry.search("task master")
        for doc in similar_docs:
            print(f"  - {doc.path}")
            print(f"    Заголовок: {doc.title}")
            print(f"    Дата: {doc.date}")
    
    # Поиск документов проекта
    rick_ai_docs = registry.get_project_document("rick.ai")
    print(f"\nНайдено {len(rick_ai_docs)} документов проекта rick.ai:")
    for doc in rick_ai_docs:
        print(f"  - {doc.path}")
        print(f"    Заголовок: {doc.title}")
    
    # Экспортируем реестр
    registry.export_to_json()