"""
Расширенный модуль реестра документов для централизованного управления метаданными.

Обеспечивает:
1. Централизованное управление метаданными всех документов в системе
2. Отслеживание истории изменений документов
3. Продвинутое обнаружение дубликатов с различными стратегиями сравнения
4. Поддержку логических идентификаторов для документов
5. Управление связями между документами
"""

import os
import re
import json
import hashlib
import logging
import difflib
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Set, Tuple, Union, Any

# Настраиваем логирование
logger = logging.getLogger("document_registry")

# Константы
REGISTRY_FILE = "document_registry.json"
REGISTRY_BACKUP_DIR = ".registry_backups"
MAX_BACKUPS = 5

# Типы документов
DOCUMENT_TYPES = {
    "task": {"dir": "[todo · incidents]/ai.todo", "prefix": "todo-"},
    "incident": {"dir": "[todo · incidents]/ai.incidents", "prefix": "incident-"},
    "standard": {"dir": "[standards .md]", "prefix": ""},
    "project": {"dir": "projects", "prefix": ""},
    "report": {"dir": "reports", "prefix": "report-"},
}


@dataclass
class DocumentMetadata:
    """JTBD:
Я (разработчик) хочу использовать функциональность класса DocumentMetadata, чтобы эффективно решать соответствующие задачи в системе.
    
    Класс для хранения метаданных документа."""
    path: str
    document_type: str
    title: str
    content_hash: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "active"
    tags: List[str] = field(default_factory=list)
    related_documents: List[str] = field(default_factory=list)
    version: int = 1
    history: List[Dict[str, Any]] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    logical_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """JTBD:
Я (разработчик) хочу использовать функцию to_dict, чтобы эффективно выполнить соответствующую операцию.
         
         Преобразует метаданные в словарь."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentMetadata':
        """JTBD:
Я (разработчик) хочу использовать функцию from_dict, чтобы эффективно выполнить соответствующую операцию.
         
         Создает объект метаданных из словаря."""
        return cls(**data)


class DocumentRegistry:
    """
    Расширенный класс для управления реестром документов с поддержкой 
    истории изменений, связей и продвинутого обнаружения дубликатов.
    """
    
    def __init__(self, registry_file: str = REGISTRY_FILE):
        """Инициализирует реестр документов."""
        self.registry_file = registry_file
        self.documents: Dict[str, DocumentMetadata] = {}
        self.id_mapping: Dict[str, str] = {}  # mapping from logical_id to path
        self._load_registry()
    
    def _load_registry(self) -> None:
        """Загружает реестр документов из файла."""
        try:
            if os.path.exists(self.registry_file):
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                
                # Преобразуем данные в объекты DocumentMetadata
                self.documents = {}
                for path, metadata in raw_data.get("documents", {}).items():
                    self.documents[path] = DocumentMetadata.from_dict(metadata)
                
                # Загружаем словарь маппинга идентификаторов
                self.id_mapping = raw_data.get("id_mapping", {})
                
                logger.info(f"Загружено {len(self.documents)} документов из реестра")
            else:
                logger.info("Реестр документов не найден, создаем новый")
                self.documents = {}
                self.id_mapping = {}
        except Exception as e:
            logger.error(f"Ошибка при загрузке реестра: {str(e)}")
            self.documents = {}
            self.id_mapping = {}
    
    def _save_registry(self) -> bool:
        """Сохраняет реестр документов в файл с резервным копированием."""
        try:
            # Создаем директорию для резервных копий, если её нет
            if not os.path.exists(REGISTRY_BACKUP_DIR):
                os.makedirs(REGISTRY_BACKUP_DIR, exist_ok=True)
            
            # Создаем резервную копию текущего реестра, если он существует
            if os.path.exists(self.registry_file):
                backup_name = f"{os.path.basename(self.registry_file)}.{datetime.now().strftime('%Y%m%d%H%M%S')}"
                backup_path = os.path.join(REGISTRY_BACKUP_DIR, backup_name)
                with open(self.registry_file, 'r', encoding='utf-8') as src, open(backup_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
                
                # Удаляем старые резервные копии, если их слишком много
                backup_files = sorted([
                    os.path.join(REGISTRY_BACKUP_DIR, f)
                    for f in os.listdir(REGISTRY_BACKUP_DIR)
                    if f.startswith(os.path.basename(self.registry_file))
                ])
                if len(backup_files) > MAX_BACKUPS:
                    for old_backup in backup_files[:-MAX_BACKUPS]:
                        os.remove(old_backup)
            
            # Преобразуем объекты DocumentMetadata в словари
            documents_dict = {path: metadata.to_dict() for path, metadata in self.documents.items()}
            
            # Сохраняем реестр
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "documents": documents_dict,
                    "id_mapping": self.id_mapping,
                    "last_updated": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Реестр успешно сохранен, {len(self.documents)} документов")
            return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении реестра: {str(e)}")
            return False

    def register_document(self, path: str, document_type: str, 
                         title: str, content: str, 
                         tags: List[str] = None, 
                         related_documents: List[str] = None,
                         attributes: Dict[str, Any] = None,
                         logical_id: str = None) -> Tuple[bool, Optional[str]]:
        """
        Регистрирует документ в реестре с проверкой на дубликаты.
        
        Args:
            path: Путь к файлу
            document_type: Тип документа (task, incident, standard, project)
            title: Заголовок документа
            content: Содержимое документа
            tags: Список тегов
            related_documents: Список связанных документов
            attributes: Дополнительные атрибуты
            logical_id: Логический идентификатор документа
            
        Returns:
            Tuple[bool, Optional[str]]: (успех, путь к дубликату или None)
        """
        # Генерируем хеш содержимого
        content_hash = self.generate_content_hash(content)
        
        # Проверяем наличие дубликатов
        is_duplicate, duplicate_path = self.check_for_duplicates(content, document_type)
        if is_duplicate:
            logger.warning(f"Обнаружен дубликат документа: {duplicate_path}")
            return False, duplicate_path
        
        # Создаем метаданные
        metadata = DocumentMetadata(
            path=path,
            document_type=document_type,
            title=title,
            content_hash=content_hash,
            tags=tags or [],
            related_documents=related_documents or [],
            attributes=attributes or {},
            logical_id=logical_id
        )
        
        # Регистрируем логический идентификатор, если он указан
        if logical_id and logical_id not in self.id_mapping:
            self.id_mapping[logical_id] = path
        
        # Добавляем документ в реестр
        self.documents[path] = metadata
        
        # Сохраняем реестр
        self._save_registry()
        
        logger.info(f"Документ успешно зарегистрирован: {path}")
        return True, None
    
    def update_document(self, path: str, content: str, 
                       title: Optional[str] = None,
                       tags: Optional[List[str]] = None,
                       related_documents: Optional[List[str]] = None,
                       attributes: Optional[Dict[str, Any]] = None) -> bool:
        """
        Обновляет метаданные документа в реестре.
        
        Args:
            path: Путь к документу
            content: Новое содержимое
            title: Новый заголовок (None, если не изменился)
            tags: Новые теги (None, если не изменились)
            related_documents: Новые связанные документы (None, если не изменились)
            attributes: Новые атрибуты (None, если не изменились)
            
        Returns:
            bool: True, если обновление успешно, иначе False
        """
        if path not in self.documents:
            logger.warning(f"Документ не найден в реестре: {path}")
            return False
        
        # Получаем текущие метаданные
        metadata = self.documents[path]
        
        # Сохраняем историю
        history_entry = {
            "content_hash": metadata.content_hash,
            "updated_at": metadata.updated_at,
            "version": metadata.version,
            "title": metadata.title
        }
        
        if not metadata.history:
            metadata.history = []
        
        metadata.history.append(history_entry)
        
        # Обновляем метаданные
        metadata.content_hash = self.generate_content_hash(content)
        metadata.updated_at = datetime.now().isoformat()
        metadata.version += 1
        
        if title is not None:
            metadata.title = title
        
        if tags is not None:
            metadata.tags = tags
        
        if related_documents is not None:
            metadata.related_documents = related_documents
        
        if attributes is not None:
            metadata.attributes.update(attributes)
        
        # Сохраняем реестр
        self._save_registry()
        
        logger.info(f"Документ успешно обновлен: {path}")
        return True
    
    def archive_document(self, path: str, archive_path: str, 
                        reason: str = "archived") -> bool:
        """
        Архивирует документ и обновляет реестр.
        
        Args:
            path: Путь к документу
            archive_path: Путь в архиве
            reason: Причина архивации
            
        Returns:
            bool: True, если архивация успешна, иначе False
        """
        if path not in self.documents:
            logger.warning(f"Документ не найден в реестре: {path}")
            return False
        
        # Получаем метаданные
        metadata = self.documents[path]
        
        # Обновляем метаданные
        metadata.path = archive_path
        metadata.status = "archived"
        metadata.attributes["archive_reason"] = reason
        metadata.attributes["archived_at"] = datetime.now().isoformat()
        metadata.attributes["original_path"] = path
        
        # Удаляем старую запись и добавляем новую
        del self.documents[path]
        self.documents[archive_path] = metadata
        
        # Обновляем логический идентификатор, если он есть
        if metadata.logical_id and metadata.logical_id in self.id_mapping:
            self.id_mapping[metadata.logical_id] = archive_path
        
        # Сохраняем реестр
        self._save_registry()
        
        logger.info(f"Документ успешно архивирован: {path} -> {archive_path}")
        return True
    
    def add_relation(self, source_path: str, target_path: str) -> bool:
        """
        Добавляет связь между документами.
        
        Args:
            source_path: Путь к исходному документу
            target_path: Путь к целевому документу
            
        Returns:
            bool: True, если связь добавлена успешно, иначе False
        """
        if source_path not in self.documents:
            logger.warning(f"Исходный документ не найден: {source_path}")
            return False
        
        if target_path not in self.documents:
            logger.warning(f"Целевой документ не найден: {target_path}")
            return False
        
        # Добавляем связь в исходный документ
        source_metadata = self.documents[source_path]
        if target_path not in source_metadata.related_documents:
            source_metadata.related_documents.append(target_path)
        
        # Сохраняем реестр
        self._save_registry()
        
        logger.info(f"Связь успешно добавлена: {source_path} -> {target_path}")
        return True
    
    def remove_relation(self, source_path: str, target_path: str) -> bool:
        """
        Удаляет связь между документами.
        
        Args:
            source_path: Путь к исходному документу
            target_path: Путь к целевому документу
            
        Returns:
            bool: True, если связь удалена успешно, иначе False
        """
        if source_path not in self.documents:
            logger.warning(f"Исходный документ не найден: {source_path}")
            return False
        
        # Удаляем связь из исходного документа
        source_metadata = self.documents[source_path]
        if target_path in source_metadata.related_documents:
            source_metadata.related_documents.remove(target_path)
        
        # Сохраняем реестр
        self._save_registry()
        
        logger.info(f"Связь успешно удалена: {source_path} -> {target_path}")
        return True
    
    def get_related_documents(self, path: str) -> List[str]:
        """
        Возвращает список связанных документов.
        
        Args:
            path: Путь к документу
            
        Returns:
            List[str]: Список путей к связанным документам
        """
        if path not in self.documents:
            logger.warning(f"Документ не найден: {path}")
            return []
        
        return self.documents[path].related_documents
    
    def set_logical_id(self, path: str, logical_id: str) -> bool:
        """
        Устанавливает логический идентификатор для документа.
        
        Args:
            path: Путь к документу
            logical_id: Логический идентификатор
            
        Returns:
            bool: True, если идентификатор установлен успешно, иначе False
        """
        if path not in self.documents:
            logger.warning(f"Документ не найден: {path}")
            return False
        
        # Удаляем старый идентификатор, если он есть
        old_id = self.documents[path].logical_id
        if old_id and old_id in self.id_mapping:
            del self.id_mapping[old_id]
        
        # Устанавливаем новый идентификатор
        self.documents[path].logical_id = logical_id
        self.id_mapping[logical_id] = path
        
        # Сохраняем реестр
        self._save_registry()
        
        logger.info(f"Логический идентификатор успешно установлен: {path} -> {logical_id}")
        return True
    
    def get_document_by_id(self, logical_id: str) -> Optional[DocumentMetadata]:
        """
        Возвращает документ по логическому идентификатору.
        
        Args:
            logical_id: Логический идентификатор
            
        Returns:
            Optional[DocumentMetadata]: Метаданные документа или None
        """
        if logical_id not in self.id_mapping:
            logger.warning(f"Документ с идентификатором не найден: {logical_id}")
            return None
        
        path = self.id_mapping[logical_id]
        if path not in self.documents:
            logger.warning(f"Несоответствие идентификатора и пути: {logical_id} -> {path}")
            return None
        
        return self.documents[path]
    
    def get_documents_by_type(self, document_type: str) -> List[DocumentMetadata]:
        """
        Возвращает список документов указанного типа.
        
        Args:
            document_type: Тип документа
            
        Returns:
            List[DocumentMetadata]: Список метаданных документов
        """
        return [
            metadata for metadata in self.documents.values()
            if metadata.document_type == document_type and metadata.status != "archived"
        ]
    
    def get_documents_by_tag(self, tag: str) -> List[DocumentMetadata]:
        """
        Возвращает список документов с указанным тегом.
        
        Args:
            tag: Тег
            
        Returns:
            List[DocumentMetadata]: Список метаданных документов
        """
        return [
            metadata for metadata in self.documents.values()
            if tag in metadata.tags and metadata.status != "archived"
        ]
    
    def get_documents_by_status(self, status: str) -> List[DocumentMetadata]:
        """
        Возвращает список документов с указанным статусом.
        
        Args:
            status: Статус
            
        Returns:
            List[DocumentMetadata]: Список метаданных документов
        """
        return [
            metadata for metadata in self.documents.values()
            if metadata.status == status
        ]
    
    def export_to_json(self, file_path: str) -> bool:
        """
        Экспортирует реестр в JSON-файл.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            bool: True, если экспорт успешен, иначе False
        """
        try:
            # Преобразуем объекты DocumentMetadata в словари
            documents_dict = {path: metadata.to_dict() for path, metadata in self.documents.items()}
            
            # Сохраняем в файл
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "documents": documents_dict,
                    "id_mapping": self.id_mapping,
                    "exported_at": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Реестр успешно экспортирован в {file_path}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при экспорте реестра: {str(e)}")
            return False
    
    def import_from_json(self, file_path: str, merge: bool = False) -> bool:
        """
        Импортирует реестр из JSON-файла.
        
        Args:
            file_path: Путь к файлу
            merge: Объединять с текущим реестром (True) или заменить (False)
            
        Returns:
            bool: True, если импорт успешен, иначе False
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not merge:
                # Заменяем текущий реестр
                self.documents = {}
                self.id_mapping = {}
            
            # Импортируем документы
            for path, metadata_dict in data.get("documents", {}).items():
                self.documents[path] = DocumentMetadata.from_dict(metadata_dict)
            
            # Импортируем маппинг идентификаторов
            for logical_id, path in data.get("id_mapping", {}).items():
                self.id_mapping[logical_id] = path
            
            # Сохраняем реестр
            self._save_registry()
            
            logger.info(f"Реестр успешно импортирован из {file_path}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при импорте реестра: {str(e)}")
            return False
    
    def generate_content_hash(self, content: str) -> str:
        """
        Генерирует хеш содержимого, игнорируя несущественные различия.
        
        Args:
            content: Содержимое документа
        
        Returns:
            str: Хеш содержимого
        """
        # Очистка содержимого
        lines = content.strip().splitlines()
        cleaned_lines = []
        for line in lines:
            # Пропускаем строки с датами, пустые строки и метаданные
            if (re.search(r'updated:|date:|created:|время:|updated at|created at', line, re.IGNORECASE) or 
                not line.strip() or
                re.match(r'^---', line) or
                re.match(r'^tags:', line, re.IGNORECASE)):
                continue
            # Добавляем остальные строки, удаляя лишние пробелы
            cleaned_lines.append(line.strip())
        
        # Создаем хеш из очищенного содержимого
        cleaned_content = "\n".join(cleaned_lines)
        return hashlib.md5(cleaned_content.encode('utf-8')).hexdigest()
    
    def check_for_duplicates(self, content: str, document_type: str = None, 
                            similarity_threshold: float = 0.9) -> Tuple[bool, Optional[str]]:
        """
        Проверяет наличие дубликатов содержимого с учетом нечеткого сравнения.
        
        Args:
            content: Содержимое для проверки
            document_type: Тип документа (для ограничения поиска)
            similarity_threshold: Порог схожести для нечеткого сравнения
            
        Returns:
            Tuple[bool, Optional[str]]: (есть_дубликат, путь_к_дубликату)
        """
        content_hash = self.generate_content_hash(content)
        
        # Точное совпадение по хешу
        for path, metadata in self.documents.items():
            if metadata.content_hash == content_hash:
                return True, path
        
        # Если не найдено точное совпадение, используем нечеткое сравнение
        cleaned_content = self._clean_content_for_comparison(content)
        
        for path, metadata in self.documents.items():
            # Если указан тип документа, проверяем только документы этого типа
            if document_type and metadata.document_type != document_type:
                continue
            
            # Получаем содержимое документа для сравнения
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    doc_content = f.read()
                
                # Очищаем содержимое для сравнения
                doc_cleaned = self._clean_content_for_comparison(doc_content)
                
                # Вычисляем степень схожести
                similarity = difflib.SequenceMatcher(None, cleaned_content, doc_cleaned).ratio()
                
                if similarity >= similarity_threshold:
                    logger.info(f"Найден дубликат с коэффициентом схожести {similarity:.2f}: {path}")
                    return True, path
                
            except Exception as e:
                logger.warning(f"Ошибка при чтении файла {path}: {str(e)}")
        
        return False, None
    
    def _clean_content_for_comparison(self, content: str) -> str:
        """
        Очищает содержимое для нечеткого сравнения.
        
        Args:
            content: Исходное содержимое
            
        Returns:
            str: Очищенное содержимое
        """
        # Удаляем несущественные символы и приводим к нижнему регистру
        cleaned = re.sub(r'[\s\n\r\t]+', ' ', content).lower()
        
        # Удаляем пунктуацию
        cleaned = re.sub(r'[^\w\s]', '', cleaned)
        
        # Удаляем общие слова (артикли, предлоги)
        common_words = {'a', 'an', 'the', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'и', 'в', 'на', 'с', 'к', 'по', 'от', 'для'}
        words = cleaned.split()
        cleaned = ' '.join(word for word in words if word not in common_words)
        
        return cleaned
    
    def get_document_history(self, path: str) -> List[Dict[str, Any]]:
        """
        Возвращает историю изменений документа.
        
        Args:
            path: Путь к документу
            
        Returns:
            List[Dict[str, Any]]: История изменений
        """
        if path not in self.documents:
            logger.warning(f"Документ не найден: {path}")
            return []
        
        return self.documents[path].history
    
    def verify_registry_integrity(self) -> Dict[str, Any]:
        """
        Проверяет целостность реестра.
        
        Returns:
            Dict[str, Any]: Результаты проверки
        """
        results = {
            "missing_files": [],
            "orphaned_entries": [],
            "invalid_relationships": [],
            "broken_id_mappings": []
        }
        
        # Проверяем существующие файлы
        for path in list(self.documents.keys()):
            if not os.path.exists(path):
                results["missing_files"].append(path)
        
        # Проверяем связи между документами
        for path, metadata in self.documents.items():
            for related_path in metadata.related_documents:
                if related_path not in self.documents:
                    results["invalid_relationships"].append((path, related_path))
        
        # Проверяем маппинг идентификаторов
        for logical_id, path in list(self.id_mapping.items()):
            if path not in self.documents:
                results["broken_id_mappings"].append((logical_id, path))
        
        return results
    
    def clean_registry(self) -> Dict[str, int]:
        """
        Очищает реестр от некорректных записей.
        
        Returns:
            Dict[str, int]: Количество удаленных записей по категориям
        """
        counts = {
            "missing_files": 0,
            "invalid_relationships": 0,
            "broken_id_mappings": 0
        }
        
        # Удаляем записи о несуществующих файлах
        for path in list(self.documents.keys()):
            if not os.path.exists(path):
                del self.documents[path]
                counts["missing_files"] += 1
        
        # Удаляем некорректные связи
        for metadata in self.documents.values():
            original_count = len(metadata.related_documents)
            metadata.related_documents = [
                path for path in metadata.related_documents
                if path in self.documents
            ]
            counts["invalid_relationships"] += original_count - len(metadata.related_documents)
        
        # Удаляем некорректные маппинги идентификаторов
        for logical_id in list(self.id_mapping.keys()):
            path = self.id_mapping[logical_id]
            if path not in self.documents:
                del self.id_mapping[logical_id]
                counts["broken_id_mappings"] += 1
        
        # Сохраняем очищенный реестр
        self._save_registry()
        
        return counts
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Возвращает статистику реестра.
        
        Returns:
            Dict[str, Any]: Статистика реестра
        """
        stats = {
            "total_documents": len(self.documents),
            "by_type": {},
            "by_status": {},
            "relationships": 0,
            "logical_ids": len(self.id_mapping),
            "average_version": 0,
            "documents_with_history": 0
        }
        
        # Подсчитываем по типам и статусам
        for metadata in self.documents.values():
            # По типу
            if metadata.document_type not in stats["by_type"]:
                stats["by_type"][metadata.document_type] = 0
            stats["by_type"][metadata.document_type] += 1
            
            # По статусу
            if metadata.status not in stats["by_status"]:
                stats["by_status"][metadata.status] = 0
            stats["by_status"][metadata.status] += 1
            
            # Связи
            stats["relationships"] += len(metadata.related_documents)
            
            # Версии и история
            stats["average_version"] += metadata.version
            if metadata.history:
                stats["documents_with_history"] += 1
        
        # Вычисляем среднюю версию
        if stats["total_documents"] > 0:
            stats["average_version"] /= stats["total_documents"]
        
        return stats


def create_singleton_registry():
    """
    Создает и возвращает единственный экземпляр реестра документов.
    
    Returns:
        DocumentRegistry: Экземпляр реестра документов
    """
    if not hasattr(create_singleton_registry, 'instance'):
        create_singleton_registry.instance = DocumentRegistry()
    return create_singleton_registry.instance