"""
Адаптер для интеграции протокола синхронизации с существующим менеджером кэша документов.
"""

import os
import time
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from advising_platform.src.cache.document_cache import DocumentCacheManager
from advising_platform.standards.core.traceable import implements_standard

logger = logging.getLogger(__name__)

@implements_standard("sync_protocol", "1.0", "cache_integration")
class DocumentCacheAdapter:
    """
    Адаптер для интеграции протокола синхронизации с существующим менеджером кэша документов.
    
    Предоставляет унифицированный интерфейс для работы с кэшем документов, скрывая
    детали реализации исходного DocumentCacheManager.
    """
    
    def __init__(self, cache_manager: DocumentCacheManager):
        """
        Инициализирует адаптер кэша документов.
        
        Args:
            cache_manager: Исходный менеджер кэша документов
        """
        self.cache_manager = cache_manager
        logger.info(f"DocumentCacheAdapter инициализирован")
    
    def exists(self, logical_path: str) -> bool:
        """
        Проверяет, существует ли документ в кэше.
        
        Args:
            logical_path: Логический путь документа
            
        Returns:
            True, если документ существует, иначе False
        """
        return self.cache_manager.has_document(logical_path)
    
    def get_content(self, logical_path: str) -> Optional[str]:
        """
        Возвращает содержимое документа из кэша.
        
        Args:
            logical_path: Логический путь документа
            
        Returns:
            Содержимое документа или None, если документ не найден
        """
        document = self.cache_manager.get_document(logical_path)
        if document:
            return document.content
        return None
    
    def get_modified_time(self, logical_path: str) -> Optional[float]:
        """
        Возвращает время последней модификации документа в кэше.
        
        Args:
            logical_path: Логический путь документа
            
        Returns:
            Время последней модификации или None, если документ не найден
        """
        document = self.cache_manager.get_document(logical_path)
        if document:
            # Преобразуем строковый формат времени в timestamp
            if hasattr(document, 'last_modified'):
                try:
                    # Если время в формате строки ISO
                    from datetime import datetime
                    dt = datetime.fromisoformat(document.last_modified.replace('Z', '+00:00'))
                    return dt.timestamp()
                except:
                    logger.warning(f"Не удалось преобразовать время модификации для {logical_path}")
            
            # Если нет времени модификации, используем текущее время
            return time.time()
        return None
    
    def create_document(self, logical_path: str, content: str) -> bool:
        """
        Создает новый документ в кэше.
        
        Args:
            logical_path: Логический путь документа
            content: Содержимое документа
            
        Returns:
            True, если документ успешно создан, иначе False
        """
        try:
            self.cache_manager.add_document(logical_path, content)
            return True
        except Exception as e:
            logger.error(f"Ошибка создания документа {logical_path}: {e}")
            return False
    
    def update_content(self, logical_path: str, content: str) -> bool:
        """
        Обновляет содержимое документа в кэше.
        
        Args:
            logical_path: Логический путь документа
            content: Новое содержимое
            
        Returns:
            True, если документ успешно обновлен, иначе False
        """
        try:
            if self.exists(logical_path):
                self.cache_manager.update_document(logical_path, content)
            else:
                self.create_document(logical_path, content)
            return True
        except Exception as e:
            logger.error(f"Ошибка обновления документа {logical_path}: {e}")
            return False
    
    def delete_document(self, logical_path: str) -> bool:
        """
        Удаляет документ из кэша.
        
        Args:
            logical_path: Логический путь документа
            
        Returns:
            True, если документ успешно удален, иначе False
        """
        try:
            if self.exists(logical_path):
                self.cache_manager.remove_document(logical_path)
            return True
        except Exception as e:
            logger.error(f"Ошибка удаления документа {logical_path}: {e}")
            return False
    
    def get_documents_in_directory(self, logical_dir: str) -> List[Any]:
        """
        Возвращает список документов в указанной директории.
        
        Args:
            logical_dir: Логический путь директории
            
        Returns:
            Список документов
        """
        try:
            # Получаем все документы и фильтруем по директории
            all_documents = self.cache_manager.get_all_documents()
            
            # Фильтруем только документы в указанной директории
            documents_in_dir = [
                doc for doc in all_documents
                if doc.path.startswith(logical_dir) or doc.path == logical_dir
            ]
            
            return documents_in_dir
        except Exception as e:
            logger.error(f"Ошибка получения документов в директории {logical_dir}: {e}")
            return []
    
    def get_document_state(self, logical_path: str) -> Dict[str, Any]:
        """
        Возвращает информацию о состоянии документа.
        
        Args:
            logical_path: Логический путь документа
            
        Returns:
            Словарь с информацией о документе
        """
        try:
            document = self.cache_manager.get_document(logical_path)
            if document:
                return {
                    'path': document.path,
                    'exists': True,
                    'modified_time': self.get_modified_time(logical_path),
                    'size': len(document.content) if hasattr(document, 'content') else 0,
                    'metadata': document.metadata if hasattr(document, 'metadata') else {}
                }
            else:
                return {
                    'path': logical_path,
                    'exists': False
                }
        except Exception as e:
            logger.error(f"Ошибка получения состояния документа {logical_path}: {e}")
            return {
                'path': logical_path,
                'exists': False,
                'error': str(e)
            }