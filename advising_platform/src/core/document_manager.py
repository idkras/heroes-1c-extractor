#!/usr/bin/env python3
"""
Унифицированный интерфейс для работы с Markdown-документами и другими файлами.
Объединяет и расширяет функциональность из различных модулей обработки документов.

Основные компоненты:
1. MarkdownDocument - класс для работы с Markdown-документами
2. DocumentManager - менеджер документов с поддержкой кэширования
3. DocumentIdentifier - система логических идентификаторов документов
"""

import os
import re
import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from pathlib import Path

# Импортируем функции безопасной работы с файлами
try:
    from advising_platform.safe_file_operations import SafeFileOperations
except ImportError:
    try:
        from safe_file_operations import SafeFileOperations
    except ImportError:
        logging.error("Не удалось импортировать SafeFileOperations")
        raise ImportError("Не удалось импортировать SafeFileOperations")

# Настройка логирования
logger = logging.getLogger("document_manager")

class MarkdownDocument:
    """
    Класс для работы с Markdown-документами.
    Обеспечивает чтение, запись, валидацию и обработку Markdown-файлов.
    """
    
    def __init__(self, path: str, content: Optional[str] = None):
        """
        Инициализирует объект Markdown-документа.
        
        Args:
            path: Путь к файлу документа
            content: Содержимое документа (опционально)
        """
        self.path = path
        self._content = content
        self._metadata = {}
        self._loaded = content is not None
        self._modified = False
        
    @property
    def content(self) -> str:
        """
        Получает содержимое документа. Загружает его при необходимости.
        
        Returns:
            Содержимое документа
        """
        if not self._loaded:
            self._load()
        # Гарантируем, что всегда возвращаем строку даже если _content может быть None
        return self._content if self._content is not None else ""
    
    @content.setter
    def content(self, value: str) -> None:
        """
        Устанавливает содержимое документа.
        
        Args:
            value: Новое содержимое документа
        """
        self._content = value
        self._loaded = True
        self._modified = True
        self._parse_metadata()
    
    def _load(self) -> bool:
        """
        Загружает содержимое документа с диска.
        
        Returns:
            True если загрузка успешна, False в противном случае
        """
        try:
            success, content = SafeFileOperations.read_file(self.path)
            if success:
                self._content = content
                self._loaded = True
                self._modified = False
                self._parse_metadata()
                return True
            else:
                logger.error(f"Ошибка загрузки документа {self.path}")
                return False
        except Exception as e:
            logger.error(f"Исключение при загрузке документа {self.path}: {e}")
            return False
    
    def save(self) -> bool:
        """
        Сохраняет документ на диск.
        
        Returns:
            True если сохранение успешно, False в противном случае
        """
        if not self._loaded:
            logger.warning(f"Попытка сохранить незагруженный документ {self.path}")
            return False
        
        try:
            success = SafeFileOperations.write_file(self.path, self._content)
            if success:
                self._modified = False
                return True
            else:
                logger.error(f"Ошибка сохранения документа {self.path}")
                return False
        except Exception as e:
            logger.error(f"Исключение при сохранении документа {self.path}: {e}")
            return False
    
    def _parse_metadata(self) -> None:
        """
        Извлекает метаданные из содержимого документа.
        """
        if not self._loaded or self._content is None:
            return
        
        metadata = {}
        content = self._content  # Гарантируем, что _content не None
        
        # Извлекаем заголовок (первая строка с #)
        title_match = re.search(r'^#\s+(.*?)$', content, re.MULTILINE)
        if title_match:
            metadata['title'] = title_match.group(1).strip()
        
        # Извлекаем дату в формате "updated: DD month YYYY"
        date_match = re.search(r'updated:\s*(\d+\s+\w+\s+\d{4}(?:,\s*\d{2}:\d{2}\s*\w+)?)', content)
        if date_match:
            metadata['date'] = date_match.group(1).strip()
        
        # Извлекаем автора
        author_match = re.search(r'by\s+([^,\n]+)', content)
        if author_match:
            metadata['author'] = author_match.group(1).strip()
        
        # Ищем based_on
        based_on_match = re.search(r'based\s+on:\s+(.*?)(?:$|\n)', content, re.IGNORECASE)
        if based_on_match:
            metadata['based_on'] = based_on_match.group(1).strip()
        
        # Ищем версию
        version_match = re.search(r'version[:\s]+(\d+(?:\.\d+)*)', content, re.IGNORECASE)
        if version_match:
            metadata['version'] = version_match.group(1).strip()
        
        # Сохраняем метаданные
        self._metadata = metadata
    
    @property
    def metadata(self) -> Dict[str, str]:
        """
        Получает метаданные документа.
        
        Returns:
            Словарь с метаданными документа
        """
        if not self._loaded:
            self._load()
        return self._metadata
    
    @property
    def title(self) -> Optional[str]:
        """
        Получает заголовок документа.
        
        Returns:
            Заголовок документа или None, если заголовок не найден
        """
        return self.metadata.get('title')
    
    @title.setter
    def title(self, value: str) -> None:
        """
        Устанавливает заголовок документа.
        
        Args:
            value: Новый заголовок документа
        """
        # Обновляем содержимое
        if not self._loaded:
            self._load()
        
        # Убеждаемся, что content не None
        doc_content = self._content if self._content is not None else ""
        
        # Если есть существующий заголовок, заменяем его
        if title_match := re.search(r'^(#\s+).*?$', doc_content, re.MULTILINE):
            self._content = re.sub(r'^#\s+.*?$', f'# {value}', doc_content, 1, re.MULTILINE)
        else:
            # Иначе добавляем заголовок в начало документа
            self._content = f'# {value}\n\n{doc_content}'
        
        # Обновляем метаданные
        self._metadata['title'] = value
        self._modified = True
    
    @property
    def content_hash(self) -> str:
        """
        Вычисляет и возвращает хеш-сумму содержимого документа.
        
        Returns:
            MD5-хеш содержимого документа
        """
        if not self._loaded:
            self._load()
        content = self._content if self._content is not None else ""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def extract_sections(self) -> Dict[str, str]:
        """
        Извлекает разделы документа.
        
        Returns:
            Словарь, где ключи - заголовки разделов, значения - содержимое разделов
        """
        if not self._loaded:
            self._load()
        
        sections = {}
        current_section = None
        current_content = []
        
        # Проверяем что content не None и разбиваем его на строки
        content = self._content if self._content is not None else ""
        
        for line in content.split('\n'):
            # Проверяем, является ли строка заголовком
            if re.match(r'^#{2,}\s+', line):
                # Если был предыдущий раздел, сохраняем его
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                    current_content = []
                
                # Запоминаем новый раздел
                current_section = line.strip('#').strip()
                
            # Если у нас есть текущий раздел, добавляем строку к его содержимому
            elif current_section:
                current_content.append(line)
        
        # Сохраняем последний раздел
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def get_section(self, section_title: str) -> Optional[str]:
        """
        Получает содержимое конкретного раздела документа.
        
        Args:
            section_title: Заголовок раздела (без символов #)
        
        Returns:
            Содержимое раздела или None, если раздел не найден
        """
        sections = self.extract_sections()
        return sections.get(section_title)
    
    def update_section(self, section_title: str, content: str) -> bool:
        """
        Обновляет содержимое раздела документа.
        
        Args:
            section_title: Заголовок раздела (без символов #)
            content: Новое содержимое раздела
        
        Returns:
            True, если раздел обновлен, False в противном случае
        """
        if not self._loaded:
            self._load()
        
        # Убеждаемся, что content не None
        doc_content = self._content if self._content is not None else ""
        
        # Определяем уровень заголовка (количество #)
        existing_sections = self.extract_sections()
        if section_title in existing_sections:
            # Если раздел существует, определяем его уровень
            # Ищем полное совпадение заголовка с учетом уровня
            pattern = re.compile(r'^(#+)\s+' + re.escape(section_title) + r'\s*$', re.MULTILINE)
            if match := pattern.search(doc_content):
                heading_level = len(match.group(1))
                
                # Формируем новый раздел
                heading = '#' * heading_level + ' ' + section_title
                section_content = heading + '\n\n' + content
                
                # Заменяем старый раздел новым
                current_pattern = pattern.pattern + r'[\s\S]+?(?=^#+\s+|\Z)'
                self._content = re.sub(current_pattern, section_content + '\n\n', doc_content, 1, re.MULTILINE)
                self._modified = True
                return True
        
        # Если раздел не найден, добавляем его в конец
        heading = '## ' + section_title  # По умолчанию уровень 2
        section_content = '\n\n' + heading + '\n\n' + content
        self._content = (doc_content + section_content)
        self._modified = True
        return True
    
    def is_modified(self) -> bool:
        """
        Проверяет, был ли документ изменен.
        
        Returns:
            True, если документ был изменен, False в противном случае
        """
        return self._modified


class DocumentManager:
    """
    Менеджер документов с поддержкой кэширования.
    Обеспечивает единый интерфейс для работы с документами.
    """
    
    def __init__(self, base_dir: str = '.'):
        """
        Инициализирует менеджер документов.
        
        Args:
            base_dir: Базовая директория проекта
        """
        self.base_dir = base_dir
        self._documents = {}  # Кэш документов: path -> MarkdownDocument
        self._registry = {}   # Реестр документов: path -> metadata
    
    def get_document(self, path: str) -> Optional[MarkdownDocument]:
        """
        Получает документ по пути. Использует кэш при возможности.
        
        Args:
            path: Путь к документу
        
        Returns:
            Объект MarkdownDocument или None, если документ не найден
        """
        # Нормализуем путь
        normalized_path = os.path.normpath(os.path.join(self.base_dir, path))
        
        # Проверяем, есть ли документ в кэше
        if normalized_path in self._documents:
            return self._documents[normalized_path]
        
        # Проверяем, существует ли файл
        if not os.path.exists(normalized_path):
            logger.warning(f"Документ не найден: {normalized_path}")
            return None
        
        # Создаем новый объект документа
        document = MarkdownDocument(normalized_path)
        
        # Добавляем документ в кэш
        self._documents[normalized_path] = document
        
        return document
    
    def create_document(self, path: str, content: str = "") -> Optional[MarkdownDocument]:
        """
        Создает новый документ.
        
        Args:
            path: Путь к новому документу
            content: Начальное содержимое документа
        
        Returns:
            Объект MarkdownDocument или None, если документ не удалось создать
        """
        # Нормализуем путь
        normalized_path = os.path.normpath(os.path.join(self.base_dir, path))
        
        # Проверяем, не существует ли уже файл
        if os.path.exists(normalized_path):
            logger.warning(f"Документ уже существует: {normalized_path}")
            return None
        
        # Создаем директории при необходимости
        os.makedirs(os.path.dirname(normalized_path), exist_ok=True)
        
        # Создаем документ
        document = MarkdownDocument(normalized_path, content)
        
        # Сохраняем документ
        if not document.save():
            logger.error(f"Не удалось сохранить документ: {normalized_path}")
            return None
        
        # Добавляем документ в кэш
        self._documents[normalized_path] = document
        
        return document
    
    def save_all_modified(self) -> Tuple[int, int]:
        """
        Сохраняет все измененные документы.
        
        Returns:
            Кортеж (количество успешно сохраненных документов, общее количество измененных документов)
        """
        modified_count = 0
        success_count = 0
        
        for path, document in self._documents.items():
            if document.is_modified():
                modified_count += 1
                if document.save():
                    success_count += 1
        
        return success_count, modified_count
    
    def search_documents(self, query: str, include_content: bool = False) -> List[Dict[str, Any]]:
        """
        Выполняет поиск документов по содержимому или метаданным.
        
        Args:
            query: Поисковый запрос
            include_content: Включать ли содержимое документов в результаты
        
        Returns:
            Список словарей с результатами поиска
        """
        results = []
        
        # Формируем паттерн поиска
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        
        # Проходим по всем документам в базовой директории
        for root, _, files in os.walk(self.base_dir):
            for file in files:
                if file.endswith('.md'):
                    path = os.path.join(root, file)
                    document = self.get_document(path)
                    
                    if document:
                        # Проверяем метаданные
                        metadata_match = any(
                            pattern.search(str(value)) 
                            for value in document.metadata.values() 
                            if value
                        )
                        
                        # Проверяем содержимое если нет совпадения в метаданных
                        content_match = False
                        if not metadata_match:
                            content_match = bool(pattern.search(document.content))
                        
                        # Если есть совпадение, добавляем в результаты
                        if metadata_match or content_match:
                            result = {
                                'path': path,
                                'title': document.title or os.path.basename(path),
                                'metadata': document.metadata,
                                'match_type': 'metadata' if metadata_match else 'content'
                            }
                            
                            if include_content:
                                result['content'] = document.content
                            
                            results.append(result)
        
        return results
    
    def find_similar_documents(self, document_path: str, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Находит документы, похожие на указанный.
        
        Args:
            document_path: Путь к документу
            threshold: Порог похожести (от 0 до 1)
        
        Returns:
            Список словарей с результатами поиска
        """
        # Получаем указанный документ
        document = self.get_document(document_path)
        if not document:
            return []
        
        # Получаем множество слов из документа
        doc_words = set(re.findall(r'\b\w+\b', document.content.lower()))
        
        results = []
        
        # Проходим по всем документам
        for root, _, files in os.walk(self.base_dir):
            for file in files:
                if file.endswith('.md'):
                    path = os.path.join(root, file)
                    
                    # Пропускаем сам документ
                    if os.path.normpath(path) == os.path.normpath(document_path):
                        continue
                    
                    other_doc = self.get_document(path)
                    if other_doc:
                        # Получаем множество слов из другого документа
                        other_words = set(re.findall(r'\b\w+\b', other_doc.content.lower()))
                        
                        # Вычисляем коэффициент похожести (коэффициент Жаккара)
                        if not doc_words or not other_words:
                            continue
                            
                        intersection = len(doc_words.intersection(other_words))
                        union = len(doc_words.union(other_words))
                        similarity = intersection / union
                        
                        # Если похожесть выше порога, добавляем в результаты
                        if similarity >= threshold:
                            results.append({
                                'path': path,
                                'title': other_doc.title or os.path.basename(path),
                                'similarity': similarity,
                                'metadata': other_doc.metadata
                            })
        
        # Сортируем результаты по убыванию похожести
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        return results


class DocumentIdentifier:
    """
    Система логических идентификаторов документов.
    Позволяет ссылаться на документы с помощью абстрактных идентификаторов
    вместо конкретных путей.
    """
    
    # Типы документов
    DOC_TYPE_STANDARD = "standard"
    DOC_TYPE_PROJECT = "project"
    DOC_TYPE_INCIDENT = "incident"
    DOC_TYPE_GUIDE = "guide"
    DOC_TYPE_TASK = "task"
    DOC_TYPE_OTHER = "other"
    
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


# Функция для простого создания документов
def create_markdown_document(path: str, title: str, content: str = "", **metadata) -> Optional[MarkdownDocument]:
    """
    Удобная функция для создания Markdown-документов с заданными метаданными.
    
    Args:
        path: Путь к документу
        title: Заголовок документа
        content: Основное содержимое документа
        **metadata: Дополнительные метаданные (author, date, version, etc.)
    
    Returns:
        Созданный документ или None, если не удалось создать
    """
    # Формируем заголовок документа
    header = f"# {title}\n\n"
    
    # Добавляем метаданные
    for key, value in metadata.items():
        if key == 'author':
            header += f"by {value}\n"
        elif key == 'date':
            header += f"updated: {value}\n"
        elif key == 'version':
            header += f"version: {value}\n"
        elif key != 'content':
            header += f"{key}: {value}\n"
    
    # Объединяем заголовок и содержимое
    full_content = header + "\n" + content
    
    # Создаем и возвращаем документ
    manager = DocumentManager()
    return manager.create_document(path, full_content)


# Создаем глобальный экземпляр менеджера документов
_document_manager = None

def get_document_manager() -> DocumentManager:
    """
    Получает глобальный экземпляр менеджера документов.
    
    Returns:
        Глобальный экземпляр DocumentManager
    """
    global _document_manager
    if not _document_manager:
        _document_manager = DocumentManager()
    return _document_manager