#!/usr/bin/env python3
"""
Инкрементальный in-memory индексатор для markdown документов.
Обеспечивает высокую скорость индексации и поиска по документам.
"""

import os
import re
import time
import hashlib
from typing import Dict, List, Tuple, Set, Optional, Any, cast
from dataclasses import dataclass, field

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
    content_hash: Optional[str] = None
    based_on: Optional[str] = None
    version: Optional[str] = None
    last_modified: float = field(default_factory=time.time)

@dataclass
class DocumentContent:
    """JTBD:
Я (разработчик) хочу использовать функциональность класса DocumentContent, чтобы эффективно решать соответствующие задачи в системе.
    
    Содержимое документа с разбивкой на секции."""
    raw_content: str
    sections: Dict[str, str] = field(default_factory=dict)
    tasks: List[Dict[str, Any]] = field(default_factory=list)
    incidents: List[Dict[str, Any]] = field(default_factory=list)
    links: List[str] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)

class InMemoryIndexer:
    """
    Инкрементальный индексатор документов, хранящий все данные в памяти.
    Обеспечивает быстрый доступ к документам и их частям.
    """

    def __init__(self):
        self.documents: Dict[str, Tuple[DocumentMetadata, DocumentContent]] = {}
        self.path_to_id: Dict[str, str] = {}  # Маппинг путей к логическим идентификаторам
        self.id_to_path: Dict[str, str] = {}  # Маппинг логических идентификаторов к путям
        self.index_by_title: Dict[str, List[str]] = {}  # Индекс по заголовкам
        self.index_by_author: Dict[str, List[str]] = {}  # Индекс по авторам
        self.index_by_tag: Dict[str, List[str]] = {}  # Индекс по тегам
        self.index_by_word: Dict[str, List[Tuple[str, int]]] = {}  # Индекс по словам с весами
        self.last_indexed: float = 0  # Время последнего полного индексирования

    def index_document(self, path: str, force_reindex: bool = False) -> bool:
        """
        Индексирует документ по указанному пути.
        
        Args:
            path: Путь к документу
            force_reindex: Принудительное переиндексирование даже если документ не изменился
            
        Returns:
            True, если документ был переиндексирован, False в противном случае
        """
        if not os.path.exists(path) or not os.path.isfile(path):
            if path in self.documents:
                # Документ удален, удаляем его из индекса
                self._remove_from_index(path)
            return False

        # Проверяем, изменился ли документ с момента последней индексации
        mtime = os.path.getmtime(path)
        if path in self.documents and not force_reindex:
            metadata, _ = self.documents[path]
            if mtime <= metadata.last_modified:
                # Документ не изменился, пропускаем
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

        # Если документ уже проиндексирован и хеш не изменился, пропускаем
        if path in self.documents and not force_reindex:
            metadata, _ = self.documents[path]
            if metadata.content_hash == content_hash:
                # Обновляем только время последней модификации
                metadata.last_modified = mtime
                return False

        # Парсим метаданные документа
        metadata = self._parse_metadata(path, content, content_hash)
        metadata.last_modified = mtime

        # Парсим содержимое документа
        doc_content = self._parse_content(content)

        # Обновляем индексы
        self._add_to_index(path, metadata, doc_content)

        return True

    def _parse_metadata(self, path: str, content: str, content_hash: str) -> DocumentMetadata:
        """
        Извлекает метаданные из содержимого документа.
        
        Args:
            path: Путь к документу
            content: Содержимое документа
            content_hash: Хеш содержимого
            
        Returns:
            Метаданные документа
        """
        metadata = DocumentMetadata(path=path, content_hash=content_hash)
        
        # Извлекаем имя файла и директорию
        metadata.doc_type = self._determine_doc_type(path)
        
        # Извлекаем заголовок (первый заголовок первого уровня)
        title_match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
        if title_match:
            metadata.title = title_match.group(1).strip()
        
        # Извлекаем дату и автора из метаданных
        date_match = re.search(r'(?:updated|date):\s*(.+?)(?:,|\n)', content, re.IGNORECASE)
        if date_match:
            metadata.date = date_match.group(1).strip()
        
        author_match = re.search(r'(?:author|by):\s*(.+?)(?:,|\n)', content, re.IGNORECASE)
        if author_match:
            metadata.author = author_match.group(1).strip()
        
        # Извлекаем based_on и version
        based_on_match = re.search(r'based\s+on:\s*(.+?)(?:,|\n)', content, re.IGNORECASE)
        if based_on_match:
            metadata.based_on = based_on_match.group(1).strip()
        
        version_match = re.search(r'version:\s*(.+?)(?:,|\n)', content, re.IGNORECASE)
        if version_match:
            metadata.version = version_match.group(1).strip()
        
        return metadata

    def _determine_doc_type(self, path: str) -> str:
        """Определяет тип документа на основе пути."""
        if 'standards' in path.lower():
            return 'standard'
        elif 'incidents' in path.lower() or 'ai.incidents.md' in path.lower():
            return 'incident'
        elif 'todo.md' in path.lower():
            return 'task'
        elif 'todo.archive.md' in path.lower():
            return 'task'
        elif 'projects' in path.lower():
            return 'project'
        else:
            return 'document'

    def _parse_content(self, content: str) -> DocumentContent:
        """
        Разбирает содержимое документа на секции, задачи, инциденты и т.д.
        
        Args:
            content: Содержимое документа
            
        Returns:
            Структурированное содержимое документа
        """
        doc_content = DocumentContent(raw_content=content)
        
        # Разбиваем документ на секции по заголовкам
        sections = {}
        current_section = 'header'
        current_content = []
        
        for line in content.split('\n'):
            if re.match(r'^#{1,6}\s+', line):
                # Новый заголовок - сохраняем предыдущую секцию
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                    current_content = []
                
                # Используем заголовок как имя секции
                current_section = line.strip()
            
            current_content.append(line)
        
        # Добавляем последнюю секцию
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        doc_content.sections = sections
        
        # Извлекаем задачи
        doc_content.tasks = self._extract_tasks(content)
        
        # Извлекаем инциденты
        doc_content.incidents = self._extract_incidents(content)
        
        # Извлекаем ссылки
        doc_content.links = self._extract_links(content)
        
        # Извлекаем теги
        doc_content.tags = self._extract_tags(content)
        
        return doc_content

    def _extract_tasks(self, content: str) -> List[Dict[str, Any]]:
        """Извлекает задачи из содержимого документа."""
        tasks = []
        
        # Используем регулярные выражения для поиска задач в формате Task Master
        task_pattern = r'- \[([ x])\] \*\*(.+?)\*\*(?:\s\[(.*?)\])?\s·\s@(.*?)\s·\sдо\s(.*?)$\n(?:\*\*цель\*\*:.*?(?:\n(?:\*\*.*?\*\*:(?:(?:\n- .*?)*)+))*)'
        task_matches = re.finditer(task_pattern, content, re.MULTILINE)
        
        for match in task_matches:
            completed = match.group(1) == 'x'
            title = match.group(2).strip()
            priority = match.group(3) or ''
            responsible = match.group(4).strip()
            deadline = match.group(5).strip()
            full_text = match.group(0)
            
            # Извлекаем цель задачи
            goal_match = re.search(r'\*\*цель\*\*:\s*(.*?)(?:\n\*\*|\Z)', full_text, re.DOTALL)
            goal = goal_match.group(1).strip() if goal_match else ''
            
            # Извлекаем подзадачи
            subtasks = []
            subtasks_match = re.search(r'\*\*подзадачи\*\*:((?:\n- .*?)*)', full_text)
            if subtasks_match:
                subtasks_text = subtasks_match.group(1)
                for line in subtasks_text.strip().split('\n'):
                    if line.strip().startswith('- '):
                        subtask = {
                            'text': line.strip()[2:].strip(),
                            'completed': line.strip().startswith('- [x]')
                        }
                        subtasks.append(subtask)
            
            task = {
                'title': title,
                'completed': completed,
                'priority': priority,
                'responsible': responsible,
                'deadline': deadline,
                'goal': goal,
                'subtasks': subtasks,
                'full_text': full_text
            }
            
            tasks.append(task)
        
        return tasks

    def _extract_incidents(self, content: str) -> List[Dict[str, Any]]:
        """Извлекает инциденты из содержимого документа."""
        incidents = []
        
        # Регулярное выражение для поиска инцидентов
        incident_pattern = r'## (AI Incident|Инцидент).*?ID:\s*(\d+).*?\n.*?(?:до|next update):.*?(\d{1,2}[^\d]{1,3}\d{4})'
        incident_matches = re.finditer(incident_pattern, content, re.MULTILINE | re.DOTALL)
        
        for match in incident_matches:
            incident_type = match.group(1)
            incident_id = match.group(2)
            incident_date = match.group(3)
            
            # Находим границы инцидента
            start_pos = match.start()
            next_incident = re.search(r'## (AI Incident|Инцидент)', content[start_pos + 1:], re.MULTILINE)
            end_pos = next_incident.start() + start_pos + 1 if next_incident else len(content)
            
            incident_text = content[start_pos:end_pos]
            
            # Извлекаем статус инцидента
            status_match = re.search(r'status:\s*(.+?)\n', incident_text, re.IGNORECASE)
            status = status_match.group(1).strip() if status_match else 'Unknown'
            
            # Извлекаем описание инцидента
            description_match = re.search(r'### Описание.*?\n(.*?)(?:###|\Z)', incident_text, re.DOTALL)
            description = description_match.group(1).strip() if description_match else ''
            
            incident = {
                'id': incident_id,
                'type': incident_type,
                'date': incident_date,
                'status': status,
                'description': description,
                'full_text': incident_text
            }
            
            incidents.append(incident)
        
        return incidents

    def _extract_links(self, content: str) -> List[str]:
        """Извлекает ссылки из содержимого документа."""
        links = []
        
        # Ищем Markdown-ссылки [текст](URL)
        md_links = re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', content)
        for match in md_links:
            links.append(match.group(2))
        
        # Ищем абстрактные ссылки abstract://type:id
        abstract_links = re.finditer(r'abstract://([^)\s]+)', content)
        for match in abstract_links:
            links.append(f"abstract://{match.group(1)}")
        
        return links

    def _extract_tags(self, content: str) -> Set[str]:
        """Извлекает теги из содержимого документа."""
        tags = set()
        
        # Ищем теги в формате #тег
        tag_matches = re.finditer(r'(?:^|\s)#(\w+)', content)
        for match in tag_matches:
            tags.add(match.group(1).lower())
        
        # Ищем приоритеты в формате [alarm], [asap], и т.д.
        priority_matches = re.finditer(r'\[(alarm|asap|research|blocker|small task|exciter)\]', content, re.IGNORECASE)
        for match in priority_matches:
            tags.add(match.group(1).lower())
        
        return tags

    def _add_to_index(self, path: str, metadata: DocumentMetadata, content: DocumentContent):
        """Добавляет документ в индекс."""
        # Сохраняем документ в основной индекс
        self.documents[path] = (metadata, content)
        
        # Обновляем индекс по заголовкам
        if metadata.title:
            title_key = metadata.title.lower()
            if title_key not in self.index_by_title:
                self.index_by_title[title_key] = []
            if path not in self.index_by_title[title_key]:
                self.index_by_title[title_key].append(path)
        
        # Обновляем индекс по авторам
        if metadata.author:
            author_key = metadata.author.lower()
            if author_key not in self.index_by_author:
                self.index_by_author[author_key] = []
            if path not in self.index_by_author[author_key]:
                self.index_by_author[author_key].append(path)
        
        # Обновляем индекс по тегам
        for tag in content.tags:
            tag_key = tag.lower()
            if tag_key not in self.index_by_tag:
                self.index_by_tag[tag_key] = []
            if path not in self.index_by_tag[tag_key]:
                self.index_by_tag[tag_key].append(path)
        
        # Обновляем индекс по словам
        self._index_words(path, content.raw_content)

    def _index_words(self, path: str, content: str):
        """Индексирует слова в документе."""
        # Удаляем старые записи для этого документа
        for word, entries in list(self.index_by_word.items()):
            self.index_by_word[word] = [entry for entry in entries if entry[0] != path]
            if not self.index_by_word[word]:
                del self.index_by_word[word]
        
        # Разбиваем текст на слова и подсчитываем частоту
        words = re.findall(r'\b\w{3,}\b', content.lower())
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # Добавляем слова в индекс
        for word, count in word_counts.items():
            if word not in self.index_by_word:
                self.index_by_word[word] = []
            self.index_by_word[word].append((path, count))

    def _remove_from_index(self, path: str):
        """Удаляет документ из индекса."""
        if path not in self.documents:
            return
        
        # Удаляем из основного индекса
        metadata, content = self.documents[path]
        del self.documents[path]
        
        # Удаляем из индекса по заголовкам
        if metadata.title:
            title_key = metadata.title.lower()
            if title_key in self.index_by_title:
                self.index_by_title[title_key] = [p for p in self.index_by_title[title_key] if p != path]
                if not self.index_by_title[title_key]:
                    del self.index_by_title[title_key]
        
        # Удаляем из индекса по авторам
        if metadata.author:
            author_key = metadata.author.lower()
            if author_key in self.index_by_author:
                self.index_by_author[author_key] = [p for p in self.index_by_author[author_key] if p != path]
                if not self.index_by_author[author_key]:
                    del self.index_by_author[author_key]
        
        # Удаляем из индекса по тегам
        for tag in content.tags:
            tag_key = tag.lower()
            if tag_key in self.index_by_tag:
                self.index_by_tag[tag_key] = [p for p in self.index_by_tag[tag_key] if p != path]
                if not self.index_by_tag[tag_key]:
                    del self.index_by_tag[tag_key]
        
        # Удаляем из индекса по словам
        for word, entries in list(self.index_by_word.items()):
            self.index_by_word[word] = [entry for entry in entries if entry[0] != path]
            if not self.index_by_word[word]:
                del self.index_by_word[word]

    def index_directory(self, directory: str, extensions: Optional[List[str]] = None, recursive: bool = True) -> int:
        """
        Индексирует все файлы в указанной директории.
        
        Args:
            directory: Путь к директории
            extensions: Список расширений файлов для индексации (по умолчанию ['.md'])
            recursive: Рекурсивный обход поддиректорий
            
        Returns:
            Количество проиндексированных документов
        """
        if extensions is None:
            extensions = ['.md']
        
        indexed_count = 0
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                # Проверяем расширение файла
                if not any(file.endswith(ext) for ext in extensions):
                    continue
                
                file_path = os.path.join(root, file)
                if self.index_document(file_path):
                    indexed_count += 1
            
            if not recursive:
                break
        
        self.last_indexed = time.time()
        return indexed_count

    def search(self, query: str, doc_type: Optional[str] = None, limit: int = 10) -> List[Tuple[str, float]]:
        """
        Выполняет поиск по проиндексированным документам.
        
        Args:
            query: Поисковый запрос
            doc_type: Тип документов для поиска (None - все типы)
            limit: Максимальное количество результатов
            
        Returns:
            Список путей к документам с релевантностью
        """
        # Разбиваем запрос на слова и операторы
        query = query.lower()
        terms = []
        
        # Обрабатываем операторы AND и OR
        if ' and ' in query:
            subqueries = query.split(' and ')
            results = None
            for subquery in subqueries:
                subresults = set(path for path, _ in self._search_simple(subquery, doc_type))
                if results is None:
                    results = subresults
                else:
                    results = results.intersection(subresults)
            
            if not results:
                return []
            
            # Ранжируем результаты
            return self._rank_results(list(results), query, doc_type)[:limit]
        
        elif ' or ' in query:
            subqueries = query.split(' or ')
            results = set()
            for subquery in subqueries:
                subresults = set(path for path, _ in self._search_simple(subquery, doc_type))
                results = results.union(subresults)
            
            if not results:
                return []
            
            # Ранжируем результаты
            return self._rank_results(list(results), query, doc_type)[:limit]
        
        else:
            # Простой поиск
            return self._search_simple(query, doc_type)[:limit]

    def _search_simple(self, query: str, doc_type: Optional[str] = None) -> List[Tuple[str, float]]:
        """Выполняет простой поиск без сложных операторов."""
        results = {}
        query = query.lower().strip()
        
        # Проверяем наличие тегов
        tag_match = re.search(r'#(\w+)', query)
        if tag_match:
            tag = tag_match.group(1).lower()
            if tag in self.index_by_tag:
                for path in self.index_by_tag[tag]:
                    # Проверяем тип документа
                    if doc_type and self.documents[path][0].doc_type != doc_type:
                        continue
                    results[path] = results.get(path, 0) + 5.0  # Высокий вес для тегов
        
        # Проверяем наличие автора
        author_match = re.search(r'@(\w+)', query)
        if author_match:
            author = author_match.group(1).lower()
            for author_key, paths in self.index_by_author.items():
                if author in author_key:
                    for path in paths:
                        # Проверяем тип документа
                        if doc_type and self.documents[path][0].doc_type != doc_type:
                            continue
                        results[path] = results.get(path, 0) + 3.0  # Средний вес для авторов
        
        # Проверяем наличие приоритета
        priority_match = re.search(r'\[(alarm|asap|research|blocker|small task|exciter)\]', query, re.IGNORECASE)
        if priority_match:
            priority = priority_match.group(1).lower()
            for tag_key, paths in self.index_by_tag.items():
                if priority == tag_key:
                    for path in paths:
                        # Проверяем тип документа
                        if doc_type and self.documents[path][0].doc_type != doc_type:
                            continue
                        results[path] = results.get(path, 0) + 4.0  # Высокий вес для приоритетов
        
        # Выполняем поиск по словам
        words = re.findall(r'\b\w{3,}\b', query)
        for word in words:
            if word in self.index_by_word:
                for path, count in self.index_by_word[word]:
                    # Проверяем тип документа
                    if doc_type and self.documents[path][0].doc_type != doc_type:
                        continue
                    results[path] = results.get(path, 0) + 0.1 * count  # Вес зависит от частоты слова
        
        # Проверяем наличие точного совпадения в заголовке
        for title_key, paths in self.index_by_title.items():
            if query in title_key:
                for path in paths:
                    # Проверяем тип документа
                    if doc_type and self.documents[path][0].doc_type != doc_type:
                        continue
                    results[path] = results.get(path, 0) + 10.0  # Очень высокий вес для заголовков
        
        # Сортируем результаты по релевантности
        sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
        return sorted_results

    def _rank_results(self, paths: List[str], query: str, doc_type: Optional[str] = None) -> List[Tuple[str, float]]:
        """Ранжирует результаты поиска по релевантности."""
        results = {}
        
        for path in paths:
            # Проверяем тип документа
            if doc_type and self.documents[path][0].doc_type != doc_type:
                continue
            
            metadata, content = self.documents[path]
            relevance = 0.0
            
            # Релевантность по заголовку
            if metadata.title and query.lower() in metadata.title.lower():
                relevance += 10.0
            
            # Релевантность по содержимому
            word_count = 0
            words = re.findall(r'\b\w{3,}\b', query.lower())
            for word in words:
                if word in self.index_by_word:
                    for doc_path, count in self.index_by_word[word]:
                        if doc_path == path:
                            word_count += count
            
            relevance += 0.1 * word_count
            
            # Релевантность по тегам
            tag_match = re.search(r'#(\w+)', query)
            if tag_match:
                tag = tag_match.group(1).lower()
                if tag in content.tags:
                    relevance += 5.0
            
            # Релевантность по автору
            author_match = re.search(r'@(\w+)', query)
            if author_match and metadata.author:
                author = author_match.group(1).lower()
                if author in metadata.author.lower():
                    relevance += 3.0
            
            # Релевантность по приоритету
            priority_match = re.search(r'\[(alarm|asap|research|blocker|small task|exciter)\]', query, re.IGNORECASE)
            if priority_match:
                priority = priority_match.group(1).lower()
                if priority in content.tags:
                    relevance += 4.0
            
            results[path] = relevance
        
        # Сортируем результаты по релевантности
        sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
        return sorted_results

    def get_tasks(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        # Инициализация пустого словаря фильтров, если они не предоставлены
        if filters is None:
            filters = {}
        """
        Возвращает список задач с применением фильтров.
        
        Args:
            filters: Словарь фильтров (completed, priority, responsible, deadline)
            
        Returns:
            Список задач, соответствующих фильтрам
        """
        if filters is None:
            filters = {}
        
        tasks = []
        
        for path, (metadata, content) in self.documents.items():
            # Пропускаем документы, не содержащие задачи
            if not content.tasks:
                continue
            
            for task in content.tasks:
                # Применяем фильтры
                if 'completed' in filters and task['completed'] != filters['completed']:
                    continue
                
                if 'priority' in filters and filters['priority'].lower() not in task['priority'].lower():
                    continue
                
                if 'responsible' in filters and filters['responsible'].lower() not in task['responsible'].lower():
                    continue
                
                if 'deadline' in filters and filters['deadline'] not in task['deadline']:
                    continue
                
                # Добавляем информацию о документе
                task_info = task.copy()
                task_info['document_path'] = path
                task_info['document_title'] = metadata.title
                
                tasks.append(task_info)
        
        return tasks

    def get_incidents(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        # Инициализация пустого словаря фильтров, если они не предоставлены
        if filters is None:
            filters = {}
        """
        Возвращает список инцидентов с применением фильтров.
        
        Args:
            filters: Словарь фильтров (id, status, date)
            
        Returns:
            Список инцидентов, соответствующих фильтрам
        """
        if filters is None:
            filters = {}
        
        incidents = []
        
        for path, (metadata, content) in self.documents.items():
            # Пропускаем документы, не содержащие инциденты
            if not content.incidents:
                continue
            
            for incident in content.incidents:
                # Применяем фильтры
                if 'id' in filters and incident['id'] != filters['id']:
                    continue
                
                if 'status' in filters and filters['status'].lower() not in incident['status'].lower():
                    continue
                
                if 'date' in filters and filters['date'] not in incident['date']:
                    continue
                
                # Добавляем информацию о документе
                incident_info = incident.copy()
                incident_info['document_path'] = path
                incident_info['document_title'] = metadata.title
                
                incidents.append(incident_info)
        
        return incidents

    def get_document(self, path: str) -> Optional[Tuple[DocumentMetadata, DocumentContent]]:
        """
        Возвращает документ по указанному пути.
        
        Args:
            path: Путь к документу
            
        Returns:
            Кортеж (метаданные, содержимое) или None, если документ не найден
        """
        return self.documents.get(path)

    def get_document_by_id(self, identifier: str) -> Optional[Tuple[DocumentMetadata, DocumentContent]]:
        """
        Возвращает документ по логическому идентификатору.
        
        Args:
            identifier: Логический идентификатор документа
            
        Returns:
            Кортеж (метаданные, содержимое) или None, если документ не найден
        """
        if identifier in self.id_to_path:
            path = self.id_to_path[identifier]
            return self.documents.get(path)
        return None

    def register_logical_id(self, path: str, identifier: str) -> bool:
        """
        Регистрирует логический идентификатор для документа.
        
        Args:
            path: Путь к документу
            identifier: Логический идентификатор
            
        Returns:
            True, если идентификатор успешно зарегистрирован, False в противном случае
        """
        if path not in self.documents:
            return False
        
        self.path_to_id[path] = identifier
        self.id_to_path[identifier] = path
        return True

    def get_statistics(self) -> Dict[str, Any]:
        """
        Возвращает статистику по индексу.
        
        Returns:
            Словарь со статистикой
        """
        doc_types = {}
        for path, (metadata, _) in self.documents.items():
            doc_type = metadata.doc_type or 'unknown'
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        total_tasks = sum(len(content.tasks) for _, content in self.documents.values())
        total_incidents = sum(len(content.incidents) for _, content in self.documents.values())
        
        return {
            'total_documents': len(self.documents),
            'document_types': doc_types,
            'total_tasks': total_tasks,
            'total_incidents': total_incidents,
            'logical_ids': len(self.id_to_path),
            'indexed_words': len(self.index_by_word),
            'last_indexed': self.last_indexed
        }


# Создаем глобальный экземпляр индексатора
indexer = InMemoryIndexer()