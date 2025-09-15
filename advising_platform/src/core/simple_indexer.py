#!/usr/bin/env python3
"""
Упрощенная реализация in-memory индексатора для демонстрации концепции.
"""

import os
import re
import time
import json
import hashlib
from typing import Dict, List, Tuple, Set, Optional, Any
from dataclasses import dataclass, field

# Глобальный экземпляр индексатора для использования во всем приложении
indexer = None

@dataclass
class DocumentMetadata:
    """JTBD:
Я (разработчик) хочу использовать функциональность класса DocumentMetadata, чтобы эффективно решать соответствующие задачи в системе.
    
    Метаданные документа."""
    path: str
    doc_type: Optional[str] = None
    title: Optional[str] = None
    date: Optional[str] = None
    author: Optional[str] = None
    last_modified: float = field(default_factory=time.time)

@dataclass
class DocumentContent:
    """JTBD:
Я (разработчик) хочу использовать функциональность класса DocumentContent, чтобы эффективно решать соответствующие задачи в системе.
    
    Содержимое документа."""
    raw_content: str
    sections: Dict[str, str] = field(default_factory=dict)
    tasks: List[Dict[str, Any]] = field(default_factory=list)
    links: List[str] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)

class InMemoryIndexer:
    """
    Упрощенный индексатор документов в памяти.
    """
    def __init__(self):
        self.documents = {}  # Словарь с документами (путь -> (метаданные, содержимое))
        self.index_by_word = {}  # Обратный индекс слов (слово -> список (путь, вес))
        self.abstractions = {}  # Словарь логических идентификаторов (id -> путь)
        self.last_indexed = 0
        self.registry_file = "document_registry.json"
        
        # Загружаем реестр абстрактных идентификаторов, если он существует
        self._load_registry()

    def index_document(self, path: str, force_reindex: bool = False) -> bool:
        """JTBD:
Я (разработчик) хочу использовать функцию index_document, чтобы эффективно выполнить соответствующую операцию.
         
         Индексирует документ по указанному пути."""
        if not os.path.isfile(path):
            return False
        
        # Проверяем изменился ли документ
        if not force_reindex and path in self.documents:
            last_modified = os.path.getmtime(path)
            if last_modified <= self.documents[path][0].last_modified:
                return False
        
        # Читаем содержимое документа
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Ошибка при чтении файла {path}: {e}")
            return False
        
        # Вычисляем хеш содержимого
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        
        # Создаем метаданные документа
        metadata = DocumentMetadata(
            path=path,
            doc_type=self._determine_doc_type(path),
            last_modified=os.path.getmtime(path)
        )
        
        # Извлекаем заголовок
        title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        if title_match:
            metadata.title = title_match.group(1).strip()
        
        # Создаем структуру содержимого
        doc_content = DocumentContent(raw_content=content)
        
        # Индексируем слова
        self._index_words(path, content)
        
        # Добавляем документ в индекс
        self.documents[path] = (metadata, doc_content)
        
        return True
    
    def _determine_doc_type(self, path: str) -> str:
        """Определяет тип документа на основе пути и содержимого."""
        # Проверка на архивные и временные файлы
        if '/archive/' in path or '/[archive]/' in path or '.bak' in path or 'backup' in path.lower():
            return "archived_document"
            
        # Получаем содержимое для более точного определения типа
        content = None
        if path in self.documents:
            content = self.documents[path][1].raw_content
        else:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                # Если не удалось прочитать файл, используем только путь
                pass
        
        # Проверка на стандарты по названию файла или пути
        is_in_standards_dir = "/standards" in path or "[standards" in path
        is_standard_name = "standard" in path.lower() and path.endswith('.md')
        
        # Определение типа на основе пути и содержимого
        if is_in_standards_dir or is_standard_name:
            if content:
                # Проверяем на статус архивного документа
                if 'status: Archived' in content or 'status: Draft' in content:
                    return "archived_standard"
                
                # Проверяем наличие обязательных секций стандарта
                has_standard_sections = any(section in content for section in [
                    '## 🎯 Цель', '## Цель документа', '## 🎯 Цель стандарта', 
                    '## Версии', '## Versions', '## Глоссарий', '## Общие положения',
                    '### 1. Общие положения'
                ])
                
                if has_standard_sections:
                    return "standard"
                
                # Технические файлы в директории стандартов
                if '.gitignore' in path or 'README' in path or '.md.bak' in path:
                    return "standard_related"
            
            # Если не удалось точно определить, но файл находится в директории стандартов
            # или имеет "standard" в названии, считаем стандартом
            return "standard"
        elif "/todo" in path or "[todo" in path:
            # Проверка на архивные задачи
            if content and ('todo.archive' in path or 'archive' in path.lower()):
                return "archived_task"
            # Проверка на задачи по содержимому
            if content and ('## Следующие действия' in content or '## ToDo' in content or '# 📋 ToDo' in content):
                return "task"
            # По умолчанию, если в пути есть 'todo', считаем задачей
            return "task"
        elif "/projects" in path or "[projects" in path:
            # Проверка на стандарты в проектах
            if is_standard_name and content:
                has_standard_sections = any(section in content for section in [
                    '## 🎯 Цель', '## Цель документа', '## Цель стандарта', 
                    '## Версии', '## Versions', '## Глоссарий', '## Общие положения'
                ])
                if has_standard_sections or is_standard_name:
                    return "standard"
            return "project"
        elif "/incidents" in path or "incidents" in path or "ai.incidents" in path:
            # Проверяем наличие маркеров инцидента в содержимом
            is_incident = False
            if content:
                incident_markers = [
                    '## 🔍 Описание инцидента', 
                    '## 🚨 Описание инцидента',
                    '# 🚨 Инцидент:',
                    '## Описание инцидента'
                ]
                is_incident = any(marker in content for marker in incident_markers)
            
            # Проверяем на архивный инцидент
            if is_incident and 'archive' in path.lower():
                return "archived_incident"
            elif is_incident:
                return "incident"
            
            # Файлы, связанные с инцидентами, но не содержащие описания инцидента
            return "incident_related"
        else:
            # Проверка на стандарты вне стандартных директорий
            if is_standard_name and content:
                has_standard_sections = any(section in content for section in [
                    '## 🎯 Цель', '## Цель документа', '## Цель стандарта', 
                    '## Версии', '## Versions', '## Глоссарий', '## Общие положения'
                ])
                if has_standard_sections:
                    return "standard"
            return "document"
    
    def _index_words(self, path: str, content: str):
        """Индексирует слова в документе."""
        # Удаляем слова документа из индекса
        for word, entries in list(self.index_by_word.items()):
            self.index_by_word[word] = [entry for entry in entries if entry[0] != path]
            if not self.index_by_word[word]:
                del self.index_by_word[word]
        
        # Выполняем токенизацию слов
        words = re.findall(r'\b\w+\b', content.lower())
        
        # Считаем частоту слов в документе
        word_counts = {}
        for word in words:
            if len(word) > 2:  # Пропускаем короткие слова
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # Добавляем слова в индекс
        for word, count in word_counts.items():
            if word not in self.index_by_word:
                self.index_by_word[word] = []
            self.index_by_word[word].append((path, count))
    
    def index_directory(self, directory: str, extensions: Optional[List[str]] = None, recursive: bool = True) -> int:
        """JTBD:
Я (разработчик) хочу использовать функцию index_directory, чтобы эффективно выполнить соответствующую операцию.
         
         Индексирует все файлы в указанной директории."""
        if extensions is None:
            extensions = ['.md']
        
        indexed_count = 0
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    path = os.path.join(root, file)
                    if self.index_document(path):
                        indexed_count += 1
            
            if not recursive:
                break
        
        self.last_indexed = time.time()
        return indexed_count
    
    def search(self, query: str, doc_type: Optional[str] = None, limit: int = 10) -> List[Tuple[str, float]]:
        """JTBD:
Я (разработчик) хочу использовать функцию search, чтобы эффективно выполнить соответствующую операцию.
         
         Выполняет поиск по проиндексированным документам."""
        results = {}
        
        # Простой поиск по словам
        words = re.findall(r'\b\w+\b', query.lower())
        for word in words:
            if word in self.index_by_word:
                for path, weight in self.index_by_word[word]:
                    # Если указан тип документа, фильтруем по нему
                    if doc_type and path in self.documents:
                        if self.documents[path][0].doc_type != doc_type:
                            continue
                    
                    results[path] = results.get(path, 0) + weight
        
        # Сортируем результаты по релевантности
        sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
        return sorted_results[:limit]
    
    def get_document(self, path: str) -> Optional[Tuple[DocumentMetadata, DocumentContent]]:
        """JTBD:
Я (разработчик) хочу получить document, чтобы использовать эти данные в дальнейших операциях.
         
         Возвращает документ по указанному пути."""
        return self.documents.get(path)
    
    def get_document_by_id(self, identifier: str) -> Optional[Tuple[DocumentMetadata, DocumentContent]]:
        """JTBD:
Я (разработчик) хочу получить document_by_id, чтобы использовать эти данные в дальнейших операциях.
         
         Возвращает документ по логическому идентификатору."""
        path = self.abstractions.get(identifier)
        if path:
            return self.get_document(path)
        return None
    
    def register_logical_id(self, path: str, identifier: str) -> bool:
        """JTBD:
Я (разработчик) хочу использовать функцию register_logical_id, чтобы эффективно выполнить соответствующую операцию.
         
         Регистрирует логический идентификатор для документа."""
        if not os.path.exists(path):
            return False
        
        self.abstractions[identifier] = path
        return True
    
    def get_tasks(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """JTBD:
Я (разработчик) хочу получить tasks, чтобы использовать эти данные в дальнейших операциях.
         
         Возвращает список задач с применением фильтров."""
        if filters is None:
            filters = {}
        
        tasks = []
        for path, (metadata, content) in self.documents.items():
            if metadata.doc_type == "task":
                task_info = {
                    "path": path,
                    "title": metadata.title,
                    "last_modified": metadata.last_modified
                }
                # Проверка фильтров
                include = True
                for key, value in filters.items():
                    if key in task_info and task_info[key] != value:
                        include = False
                        break
                
                if include:
                    tasks.append(task_info)
        
        return tasks
    
    def get_incidents(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """JTBD:
Я (разработчик) хочу получить incidents, чтобы использовать эти данные в дальнейших операциях.
         
         Возвращает список инцидентов с применением фильтров."""
        if filters is None:
            filters = {}
        
        incidents = []
        for path, (metadata, content) in self.documents.items():
            if metadata.doc_type == "incident":
                incident_info = {
                    "path": path,
                    "title": metadata.title,
                    "last_modified": metadata.last_modified
                }
                # Проверка фильтров
                include = True
                for key, value in filters.items():
                    if key in incident_info and incident_info[key] != value:
                        include = False
                        break
                
                if include:
                    incidents.append(incident_info)
        
        return incidents
    
    def get_path_by_id(self, identifier: str) -> Optional[str]:
        """JTBD:
Я (разработчик) хочу получить path_by_id, чтобы использовать эти данные в дальнейших операциях.
         
         Возвращает путь документа по логическому идентификатору."""
        return self.abstractions.get(identifier)
    
    def get_id_by_path(self, path: str) -> Optional[str]:
        """JTBD:
Я (разработчик) хочу получить id_by_path, чтобы использовать эти данные в дальнейших операциях.
         
         Возвращает логический идентификатор документа по пути."""
        for identifier, doc_path in self.abstractions.items():
            if doc_path == path:
                return identifier
        return None
    
    def _load_registry(self) -> None:
        """JTBD:
Я (разработчик) хочу использовать функцию register_logical_id, чтобы эффективно выполнить соответствующую операцию.
         
         Загружает реестр абстрактных идентификаторов из файла."""
        try:
            if os.path.exists(self.registry_file):
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'abstractions' in data and isinstance(data['abstractions'], dict):
                        self.abstractions = data['abstractions']
                        print(f"Загружено {len(self.abstractions)} логических идентификаторов")
        except Exception as e:
            print(f"Ошибка при загрузке реестра: {e}")
    
    def _save_registry(self) -> None:
        """JTBD:
Я (разработчик) хочу использовать функцию search, чтобы эффективно выполнить соответствующую операцию.
         
         Сохраняет реестр абстрактных идентификаторов в файл."""
        try:
            data = {
                'abstractions': self.abstractions,
                'last_updated': time.time()
            }
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка при сохранении реестра: {e}")
    
    def register_logical_id(self, path: str, identifier: str) -> bool:
        """JTBD:
Я (разработчик) хочу использовать функцию register_logical_id, чтобы эффективно выполнить соответствующую операцию.
         
         Регистрирует логический идентификатор для документа."""
        if not os.path.exists(path):
            return False
        
        self.abstractions[identifier] = path
        self._save_registry()  # Сохраняем изменения
        return True
        
    def get_statistics(self) -> Dict[str, Any]:
        """JTBD:
Я (разработчик) хочу получить statistics, чтобы использовать эти данные в дальнейших операциях.
         
         Возвращает статистику по индексу."""
        # Статистика по типам документов
        doc_types = {}
        active_standards = []
        active_tasks = []
        active_incidents = []
        
        for path, (metadata, content) in self.documents.items():
            doc_type = metadata.doc_type or "unknown"
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            
            # Собираем статистику по стандартам
            if doc_type == "standard":
                title = metadata.title or os.path.basename(path)
                active_standards.append({
                    "path": path,
                    "title": title,
                    "category": self._get_standard_category(path)
                })
            
            # Собираем статистику по задачам
            elif doc_type == "task":
                title = metadata.title or os.path.basename(path)
                active_tasks.append({
                    "path": path,
                    "title": title
                })
            
            # Собираем статистику по инцидентам
            elif doc_type == "incident":
                title = metadata.title or os.path.basename(path)
                active_incidents.append({
                    "path": path,
                    "title": title
                })
        
        # Группируем стандарты по категориям
        standards_by_category = {}
        for standard in active_standards:
            category = standard["category"]
            if category not in standards_by_category:
                standards_by_category[category] = []
            standards_by_category[category].append(standard["title"])
        
        return {
            "total_documents": len(self.documents),
            "document_types": doc_types,
            "total_tasks": len(active_tasks),
            "total_incidents": len(active_incidents),
            "total_archived_tasks": doc_types.get("archived_task", 0),
            "total_archived_incidents": doc_types.get("archived_incident", 0),
            "logical_ids": len(self.abstractions),
            "indexed_words": len(self.index_by_word),
            "last_indexed": self.last_indexed,
            "active_standards_count": len(active_standards),
            "standards_by_category": standards_by_category,
            "active_tasks": active_tasks,
            "active_incidents": active_incidents
        }
        
    def _get_standard_category(self, path: str) -> str:
        """JTBD:
Я (разработчик) хочу получить document, чтобы использовать эти данные в дальнейших операциях.
         
         Определяет категорию стандарта на основе пути."""
        if "0. core standards" in path:
            return "core"
        elif "1. process" in path:
            return "process"
        elif "2. projects" in path:
            return "projects"
        elif "3. scenarium" in path:
            return "scenarium"
        elif "6. advising" in path:
            return "advising"
        elif "8. auto" in path:
            return "auto"
        elif "9. development" in path:
            return "development"
        else:
            return "other"

class SimpleIndexer:
    """
    Класс-обертка для InMemoryIndexer с дополнительной функциональностью для индексации инцидентов и стандартов.
    
    Этот класс предоставляет высокоуровневые методы для индексации всех типов документов,
    аудита индексации и переиндексации документов.
    """
    def __init__(self):
        """Инициализирует индексатор и выполняет первичную загрузку документов."""
        self._indexer = InMemoryIndexer()
        self._initialized = False
    
    def is_initialized(self) -> bool:
        """JTBD:
Я (разработчик) хочу использовать функцию is_initialized, чтобы эффективно выполнить соответствующую операцию.
         
         Проверяет, был ли индексатор уже инициализирован."""
        return self._initialized
    
    def reindex_all(self, directories: List[str] = None) -> int:
        """
        Переиндексирует все документы в указанных директориях.
        
        Args:
            directories: Список директорий для индексации
                         По умолчанию [standards .md] и [todo · incidents]
        
        Returns:
            Общее количество проиндексированных документов
        """
        if directories is None or not directories:
            directories = ['[standards .md]', '[todo · incidents]']
        
        total_indexed = 0
        for directory in directories:
            if os.path.exists(directory):
                indexed = self._indexer.index_directory(directory, extensions=['.md'], recursive=True)
                total_indexed += indexed
                print(f"Проиндексировано {indexed} документов в директории {directory}")
            else:
                print(f"Директория {directory} не существует")
        
        self._initialized = True
        return total_indexed
    
    def search(self, query: str, doc_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Выполняет поиск по проиндексированным документам.
        
        Args:
            query: Поисковый запрос
            doc_type: Тип документа для фильтрации (standard, task, incident и т.д.)
            limit: Максимальное количество результатов
        
        Returns:
            Список словарей с результатами поиска
        """
        raw_results = self._indexer.search(query, doc_type, limit)
        results = []
        
        for path, relevance in raw_results:
            doc = self._indexer.get_document(path)
            if doc:
                metadata, content = doc
                results.append({
                    "path": path,
                    "title": metadata.title or os.path.basename(path),
                    "type": metadata.doc_type or "unknown",
                    "relevance": relevance,
                    "last_modified": metadata.last_modified
                })
        
        return results
    
    def get_documents(self, doc_type: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[DocumentMetadata]:
        """
        Возвращает список метаданных документов с возможностью фильтрации по типу.
        
        Args:
            doc_type: Тип документа для фильтрации
            limit: Максимальное количество результатов
            offset: Смещение для пагинации
        
        Returns:
            Список метаданных документов
        """
        documents = []
        
        for path, (metadata, _) in self._indexer.documents.items():
            if doc_type is None or metadata.doc_type == doc_type:
                documents.append(metadata)
        
        # Сортируем по времени изменения
        documents.sort(key=lambda x: x.last_modified, reverse=True)
        
        # Применяем пагинацию
        return documents[offset:offset + limit]
    
    def get_document(self, path: str) -> Optional[Tuple[DocumentMetadata, DocumentContent]]:
        """JTBD:
Я (разработчик) хочу получить document, чтобы использовать эти данные в дальнейших операциях.
         
         Возвращает документ по указанному пути."""
        return self._indexer.get_document(path)
    
    def get_document_by_id(self, identifier: str) -> Optional[Tuple[DocumentMetadata, DocumentContent]]:
        """JTBD:
Я (разработчик) хочу получить document_by_id, чтобы использовать эти данные в дальнейших операциях.
         
         Возвращает документ по логическому идентификатору."""
        return self._indexer.get_document_by_id(identifier)
    
    def register_logical_id(self, path: str, identifier: str) -> bool:
        """JTBD:
Я (разработчик) хочу использовать функцию register_logical_id, чтобы эффективно выполнить соответствующую операцию.
         
         Регистрирует логический идентификатор для документа."""
        return self._indexer.register_logical_id(path, identifier)
    
    def get_tasks(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """JTBD:
Я (разработчик) хочу получить tasks, чтобы использовать эти данные в дальнейших операциях.
         
         Возвращает список задач с применением фильтров."""
        return self._indexer.get_tasks(filters)
    
    def get_incidents(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """JTBD:
Я (разработчик) хочу получить incidents, чтобы использовать эти данные в дальнейших операциях.
         
         Возвращает список инцидентов с применением фильтров."""
        return self._indexer.get_incidents(filters)
    
    def get_statistics(self) -> Dict[str, Any]:
        """JTBD:
Я (разработчик) хочу получить statistics, чтобы использовать эти данные в дальнейших операциях.
         
         Возвращает статистику по индексу."""
        return self._indexer.get_statistics()

# Создаем глобальный экземпляр индексатора
indexer = SimpleIndexer()