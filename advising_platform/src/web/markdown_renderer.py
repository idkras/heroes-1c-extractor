"""
Модуль для рендеринга Markdown-документов в HTML с поддержкой комментариев.

Обеспечивает:
1. Преобразование Markdown в HTML
2. Поддержку комментариев к параграфам
3. Синтаксическую подсветку кода
4. Обработку метаданных документа

Автор: AI Assistant
Дата: 20 мая 2025
"""

import re
import os
import json
import time
import logging
import hashlib
import markdown
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Настройка логирования
logger = logging.getLogger("markdown_renderer")
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Константы
COMMENTS_DIR = ".comments"
TASK_STATS_PATH = ".task_stats.json"

class MarkdownRenderer:
    """
    Класс для рендеринга Markdown-документов в HTML с поддержкой комментариев.
    """
    
    def __init__(self):
        """
        Инициализация рендерера.
        """
        # Создаем директорию для комментариев, если она не существует
        os.makedirs(COMMENTS_DIR, exist_ok=True)
        
        # Инициализируем экземпляр Markdown
        self.md = markdown.Markdown(
            extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
                'markdown.extensions.smarty',
                'markdown.extensions.toc'
            ]
        )
        
        # Пытаемся импортировать модуль workflow для синхронизации
        try:
            from advising_platform.src.core.document_sync_workflow import document_workflow
            self.document_workflow = document_workflow
            self.has_workflow = True
        except ImportError as e:
            logger.warning(f"Не удалось импортировать модуль document_workflow: {e}")
            self.has_workflow = False
    
    def render_document(self, document_path: str) -> Dict[str, Any]:
        """
        Рендерит Markdown-документ в HTML и подготавливает данные для шаблона.
        
        Args:
            document_path: Путь к документу
            
        Returns:
            Dict[str, Any]: Данные для шаблона
        """
        # Проверяем существование документа
        if not os.path.exists(document_path):
            logger.error(f"Документ не найден: {document_path}")
            return self._get_error_data(f"Документ не найден: {document_path}")
        
        # Проверяем синхронизацию, если доступен workflow
        sync_status = "unknown"
        sync_message = "Статус синхронизации неизвестен"
        
        if self.has_workflow:
            if self.document_workflow.before_document_operation(document_path):
                sync_status = "success"
                sync_message = "Документ синхронизирован с кешем"
            else:
                sync_status = "error"
                sync_message = "Ошибка синхронизации с кешем"
        
        try:
            # Читаем содержимое документа
            with open(document_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Определяем тип документа и извлекаем метаданные
            document_type, metadata = self._extract_metadata(document_path, content)
            
            # Преобразуем Markdown в HTML
            html_content = self._parse_markdown_to_html(content)
            
            # Добавляем идентификаторы к параграфам для комментариев
            html_content = self._add_paragraph_ids(html_content)
            
            # Получаем комментарии к документу
            comments = self._get_document_comments(document_path)
            
            # Получаем связанные элементы
            related_items = self._get_related_items(document_path, document_type)
            
            # Формируем данные для шаблона
            return {
                "title": metadata.get("title", os.path.basename(document_path)),
                "document_path": document_path,
                "document_type": document_type,
                "content": html_content,
                "comments": comments,
                "created_at": metadata.get("created_at", "Неизвестно"),
                "updated_at": metadata.get("updated_at", "Неизвестно"),
                "author": metadata.get("author", ""),
                "status": metadata.get("status", "Активный"),
                "date": metadata.get("date", datetime.now().strftime("%d %B %Y")),
                "related_items": related_items,
                "sync_status": sync_status,
                "sync_message": sync_message
            }
            
        except Exception as e:
            logger.error(f"Ошибка при рендеринге документа {document_path}: {str(e)}")
            return self._get_error_data(f"Ошибка при рендеринге документа: {str(e)}")
    
    def _extract_metadata(self, document_path: str, content: str) -> Tuple[str, Dict[str, Any]]:
        """
        Извлекает метаданные из документа.
        
        Args:
            document_path: Путь к документу
            content: Содержимое документа
            
        Returns:
            Tuple[str, Dict[str, Any]]: (тип документа, метаданные)
        """
        # Определяем тип документа по пути и имени файла
        document_type = "Документ"
        if "todo" in document_path.lower():
            document_type = "Задача"
        elif "incident" in document_path.lower():
            document_type = "Инцидент"
        elif "[standards" in document_path.lower():
            document_type = "Стандарт"
        elif "hypothesis" in document_path.lower():
            document_type = "Гипотеза"
        
        # Извлекаем заголовок
        title_match = re.search(r'^# (.*?)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else os.path.basename(document_path)
        
        # Базовые метаданные
        metadata = {
            "title": title,
            "created_at": datetime.fromtimestamp(os.path.getctime(document_path)).strftime("%d %B %Y"),
            "updated_at": datetime.fromtimestamp(os.path.getmtime(document_path)).strftime("%d %B %Y"),
            "date": datetime.fromtimestamp(os.path.getmtime(document_path)).strftime("%d %B %Y")
        }
        
        # Для задач ищем статус, автора и срок
        if document_type == "Задача":
            # Ищем строку с метаданными задачи
            task_meta_match = re.search(r'- \[([ x])\] \*\*(.*?)\*\*.*?@(.*?).*?до (.*?)$', content, re.MULTILINE)
            if task_meta_match:
                status = "Выполнено" if task_meta_match.group(1) == "x" else "В работе"
                metadata["status"] = status
                metadata["author"] = task_meta_match.group(3).strip()
                metadata["date"] = task_meta_match.group(4).strip()
        
        # Для инцидентов ищем статус и тип
        elif document_type == "Инцидент":
            # Ищем статус
            status_match = re.search(r'\*\*Статус\*\*: (.*?)$', content, re.MULTILINE)
            if status_match:
                metadata["status"] = status_match.group(1).strip()
            
            # Ищем тип инцидента
            type_match = re.search(r'\*\*Тип инцидента\*\*: (.*?)$', content, re.MULTILINE)
            if type_match:
                metadata["incident_type"] = type_match.group(1).strip()
            
            # Ищем дату
            date_match = re.search(r'^## (.*?) -', content, re.MULTILINE)
            if date_match:
                metadata["date"] = date_match.group(1).strip()
        
        # Для стандартов ищем версию и автора
        elif document_type == "Стандарт":
            # Ищем версию
            version_match = re.search(r'\*\*Версия\*\*: (.*?)$', content, re.MULTILINE)
            if version_match:
                metadata["version"] = version_match.group(1).strip()
            
            # Ищем автора
            author_match = re.search(r'\*\*Автор\*\*: (.*?)$', content, re.MULTILINE)
            if author_match:
                metadata["author"] = author_match.group(1).strip()
        
        return document_type, metadata
    
    def _parse_markdown_to_html(self, content: str) -> str:
        """
        Преобразует Markdown в HTML.
        
        Args:
            content: Markdown-содержимое
            
        Returns:
            str: HTML-содержимое
        """
        # Сбрасываем экземпляр Markdown для повторного использования
        self.md.reset()
        
        # Преобразуем Markdown в HTML
        html = self.md.convert(content)
        
        return html
    
    def _add_paragraph_ids(self, html_content: str) -> str:
        """
        Добавляет идентификаторы к параграфам для комментариев.
        
        Args:
            html_content: HTML-содержимое
            
        Returns:
            str: HTML-содержимое с идентификаторами параграфов
        """
        # Добавляем ID ко всем параграфам, у которых его нет
        paragraph_pattern = r'<p>(.*?)<\/p>'
        
        def add_id_to_paragraph(match):
            content = match.group(1)
            paragraph_hash = hashlib.md5(content.encode('utf-8')).hexdigest()[:8]
            return f'<p id="p-{paragraph_hash}">{content}</p>'
        
        return re.sub(paragraph_pattern, add_id_to_paragraph, html_content, flags=re.DOTALL)
    
    def _get_document_comments(self, document_path: str) -> List[Dict[str, Any]]:
        """
        Получает комментарии к документу.
        
        Args:
            document_path: Путь к документу
            
        Returns:
            List[Dict[str, Any]]: Список комментариев
        """
        # Формируем путь к файлу с комментариями
        comments_file = os.path.join(COMMENTS_DIR, f"{os.path.basename(document_path)}.comments.json")
        
        if not os.path.exists(comments_file):
            return []
        
        try:
            # Читаем комментарии из файла
            with open(comments_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка при чтении комментариев для {document_path}: {str(e)}")
            return []
    
    def _get_related_items(self, document_path: str, document_type: str) -> List[Dict[str, Any]]:
        """
        Получает связанные элементы для документа.
        
        Args:
            document_path: Путь к документу
            document_type: Тип документа
            
        Returns:
            List[Dict[str, Any]]: Список связанных элементов
        """
        # Заглушка для связанных элементов
        # В реальной реализации здесь будет запрос к реестру документов
        related_items = []
        
        # Пример связанных элементов
        if document_type == "Задача":
            related_items = [
                {
                    "type": "Стандарт",
                    "title": "Стандарт 4.5: Customer Injury",
                    "url": "/documents/standards/customer_injury"
                },
                {
                    "type": "Документ",
                    "title": "Анализ блокеров покупки",
                    "url": "/documents/reports/purchase_blockers"
                }
            ]
        elif document_type == "Инцидент":
            related_items = [
                {
                    "type": "Задача",
                    "title": "Исправить ошибку синхронизации кеша",
                    "url": "/documents/tasks/fix_cache_sync"
                },
                {
                    "type": "Стандарт",
                    "title": "Стандарт обработки инцидентов",
                    "url": "/documents/standards/incident_handling"
                }
            ]
        
        return related_items
    
    def add_comment(self, document_path: str, paragraph_id: str, author: str, text: str) -> Tuple[bool, str]:
        """
        Добавляет комментарий к документу.
        
        Args:
            document_path: Путь к документу
            paragraph_id: ID параграфа
            author: Автор комментария
            text: Текст комментария
            
        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        # Проверяем существование документа
        if not os.path.exists(document_path):
            return False, f"Документ не найден: {document_path}"
        
        # Формируем путь к файлу с комментариями
        comments_file = os.path.join(COMMENTS_DIR, f"{os.path.basename(document_path)}.comments.json")
        
        try:
            # Загружаем существующие комментарии или создаем пустой список
            comments = []
            if os.path.exists(comments_file):
                with open(comments_file, 'r', encoding='utf-8') as f:
                    comments = json.load(f)
            
            # Создаем новый комментарий
            new_comment = {
                "id": f"comment-{int(time.time())}",
                "paragraph_id": paragraph_id,
                "author": author,
                "text": text,
                "date": datetime.now().strftime("%d %B %Y"),
                "timestamp": datetime.now().isoformat()
            }
            
            # Добавляем комментарий в список
            comments.append(new_comment)
            
            # Сохраняем комментарии в файл
            with open(comments_file, 'w', encoding='utf-8') as f:
                json.dump(comments, f, indent=2, ensure_ascii=False)
            
            return True, "Комментарий успешно добавлен"
            
        except Exception as e:
            logger.error(f"Ошибка при добавлении комментария для {document_path}: {str(e)}")
            return False, str(e)
    
    def check_document_sync(self, document_path: str) -> Tuple[bool, str]:
        """
        Проверяет синхронизацию документа с кешем.
        
        Args:
            document_path: Путь к документу
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        if not self.has_workflow:
            return False, "Модуль синхронизации недоступен"
        
        if not os.path.exists(document_path):
            return False, f"Документ не найден: {document_path}"
        
        # Проверяем синхронизацию с кешем
        if self.document_workflow.before_document_operation(document_path):
            return True, "Документ синхронизирован с кешем"
        else:
            return False, "Ошибка синхронизации с кешем"
    
    def _get_error_data(self, error_message: str) -> Dict[str, Any]:
        """
        Возвращает данные для шаблона в случае ошибки.
        
        Args:
            error_message: Сообщение об ошибке
            
        Returns:
            Dict[str, Any]: Данные для шаблона
        """
        return {
            "title": "Ошибка",
            "document_path": "",
            "document_type": "Ошибка",
            "content": f"<div class='error-message'><p>{error_message}</p></div>",
            "comments": [],
            "created_at": "",
            "updated_at": "",
            "author": "",
            "status": "Ошибка",
            "date": datetime.now().strftime("%d %B %Y"),
            "related_items": [],
            "sync_status": "error",
            "sync_message": error_message
        }


# Создаем экземпляр для использования в других модулях
markdown_renderer = MarkdownRenderer()