"""
Центральный реестр для управления задачами, инцидентами, гипотезами и стандартами.

Обеспечивает единую систему учета, создания и управления всеми рабочими элементами,
включая проверку связей и целостности данных между кешем и файловой системой.

Автор: AI Assistant
Дата: 20 мая 2025
"""

import os
import sys
import json
import time
import logging
import datetime
import threading
from enum import Enum
from typing import Dict, List, Set, Any, Optional, Tuple, Union

# Настройка логирования
logger = logging.getLogger("task_registry")
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Импортируем необходимые модули
try:
    from advising_platform.src.core.cache_sync.transaction_manager import (
        AtomicFileOperations,
        Transaction,
        GlobalLockManager
    )
    from advising_platform.src.core.cache_sync.cache_sync_verifier import CacheSyncVerifier
except ImportError:
    logger.warning("Не удалось импортировать модули. Используем заглушки для тестирования.")
    
    # Заглушки для тестирования
    class AtomicFileOperations:
        @classmethod
        def read_json(cls, file_path: str) -> Tuple[bool, Optional[Any]]:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return True, json.load(f)
            except Exception:
                return False, None
        
        @classmethod
        def write_json(cls, file_path: str, data: Any, **kwargs) -> bool:
            try:
                os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                return True
            except Exception:
                return False
    
    class Transaction:
        def __init__(self, **kwargs):
            pass
        
        def __enter__(self):
            return self
        
        def __exit__(self, *args):
            pass
        
        def add_file_operation(self, *args):
            pass
        
        def add_cache_operation(self, *args):
            pass
        
        def execute(self):
            return True
    
    class GlobalLockManager:
        @classmethod
        def get_file_lock(cls, *args):
            class DummyLock:
                def __enter__(self):
                    return self
                
                def __exit__(self, *args):
                    pass
            
            return DummyLock()
    
    class CacheSyncVerifier:
        def __init__(self, **kwargs):
            pass
        
        def verify_sync(self):
            return [], [], []
        
        def fix_sync_issues(self):
            return True


class WorkItemType(Enum):
    """JTBD:
Я (разработчик) хочу использовать функциональность класса WorkItemType, чтобы эффективно решать соответствующие задачи в системе.
    
    Типы рабочих элементов."""
    TASK = "task"
    INCIDENT = "incident"
    HYPOTHESIS = "hypothesis"
    STANDARD = "standard"
    UNKNOWN = "unknown"


class WorkItemStatus(Enum):
    """JTBD:
Я (разработчик) хочу использовать функциональность класса WorkItemStatus, чтобы эффективно решать соответствующие задачи в системе.
    
    Статусы рабочих элементов."""
    # Общие статусы
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    ARCHIVED = "archived"
    
    # Специфичные для задач
    REVIEW = "review"
    BLOCKED = "blocked"
    
    # Специфичные для инцидентов
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    
    # Специфичные для гипотез
    PROPOSED = "proposed"
    TESTING = "testing"
    VALIDATED = "validated"
    INVALIDATED = "invalidated"
    
    # Специфичные для стандартов
    DRAFT = "draft"
    REVIEW_PENDING = "review_pending"
    APPROVED = "approved"
    DEPRECATED = "deprecated"
    SUPERSEDED = "superseded"


class WorkItemRelationType(Enum):
    """JTBD:
Я (разработчик) хочу использовать функциональность класса WorkItemRelationType, чтобы эффективно решать соответствующие задачи в системе.
    
    Типы связей между рабочими элементами."""
    BLOCKS = "blocks"  # A блокирует B
    BLOCKED_BY = "blocked_by"  # A блокируется B
    DEPENDS_ON = "depends_on"  # A зависит от B
    RELATES_TO = "relates_to"  # A связан с B
    DUPLICATES = "duplicates"  # A дублирует B
    DUPLICATED_BY = "duplicated_by"  # A дублируется B
    PART_OF = "part_of"  # A является частью B
    PARENT_OF = "parent_of"  # A родитель B
    CHILD_OF = "child_of"  # A потомок B
    DERIVED_FROM = "derived_from"  # A получен из B
    SUPERSEDES = "supersedes"  # A заменяет B
    SUPERSEDED_BY = "superseded_by"  # A заменен B
    PRECEDES = "precedes"  # A предшествует B
    FOLLOWS = "follows"  # A следует за B


class WorkItemRelation:
    """JTBD:
Я (разработчик) хочу использовать функциональность класса WorkItemRelation, чтобы эффективно решать соответствующие задачи в системе.
    
    Связь между рабочими элементами."""
    
    def __init__(
        self,
        source_id: str,
        target_id: str,
        relation_type: WorkItemRelationType,
        created_at: Optional[float] = None,
        description: Optional[str] = None
    ):
        """
        Инициализация связи.
        
        Args:
            source_id: Идентификатор исходного элемента
            target_id: Идентификатор целевого элемента
            relation_type: Тип связи
            created_at: Время создания связи
            description: Описание связи
        """
        self.source_id = source_id
        self.target_id = target_id
        self.relation_type = relation_type
        self.created_at = created_at or time.time()
        self.description = description
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует связь в словарь.
        
        Returns:
            Словарь с данными связи
        """
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type.value,
            "created_at": self.created_at,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkItemRelation':
        """
        Создает связь из словаря.
        
        Args:
            data: Словарь с данными связи
            
        Returns:
            Экземпляр связи
        """
        return cls(
            source_id=data["source_id"],
            target_id=data["target_id"],
            relation_type=WorkItemRelationType(data["relation_type"]),
            created_at=data.get("created_at"),
            description=data.get("description")
        )
    
    def get_inverse_relation(self) -> 'WorkItemRelation':
        """
        Создает обратную связь.
        
        Returns:
            Обратная связь
        """
        # Определяем обратный тип связи
        inverse_type_map = {
            WorkItemRelationType.BLOCKS: WorkItemRelationType.BLOCKED_BY,
            WorkItemRelationType.BLOCKED_BY: WorkItemRelationType.BLOCKS,
            WorkItemRelationType.DEPENDS_ON: WorkItemRelationType.PARENT_OF,
            WorkItemRelationType.PARENT_OF: WorkItemRelationType.DEPENDS_ON,
            WorkItemRelationType.CHILD_OF: WorkItemRelationType.PARENT_OF,
            WorkItemRelationType.PARENT_OF: WorkItemRelationType.CHILD_OF,
            WorkItemRelationType.DERIVED_FROM: WorkItemRelationType.PARENT_OF,
            WorkItemRelationType.SUPERSEDES: WorkItemRelationType.SUPERSEDED_BY,
            WorkItemRelationType.SUPERSEDED_BY: WorkItemRelationType.SUPERSEDES,
            # Для симметричных связей тип остается тем же
            WorkItemRelationType.RELATES_TO: WorkItemRelationType.RELATES_TO,
            WorkItemRelationType.DUPLICATES: WorkItemRelationType.DUPLICATES
        }
        
        inverse_type = inverse_type_map.get(
            self.relation_type, 
            WorkItemRelationType.RELATES_TO
        )
        
        return WorkItemRelation(
            source_id=self.target_id,
            target_id=self.source_id,
            relation_type=inverse_type,
            created_at=self.created_at,
            description=self.description
        )


class WorkItem:
    """JTBD:
Я (разработчик) хочу использовать функциональность класса WorkItem, чтобы эффективно решать соответствующие задачи в системе.
    
    Рабочий элемент (задача, инцидент, гипотеза или стандарт)."""
    
    def __init__(
        self,
        id: str,
        type: WorkItemType,
        title: str,
        status: WorkItemStatus = WorkItemStatus.BACKLOG,
        description: Optional[str] = None,
        created_at: Optional[float] = None,
        updated_at: Optional[float] = None,
        author: Optional[str] = None,
        assignee: Optional[str] = None,
        file_path: Optional[str] = None,
        due_date: Optional[float] = None,
        tags: Optional[List[str]] = None,
        properties: Optional[Dict[str, Any]] = None
    ):
        """
        Инициализация рабочего элемента.
        
        Args:
            id: Уникальный идентификатор
            type: Тип элемента
            title: Название
            status: Статус
            description: Описание
            created_at: Время создания
            updated_at: Время обновления
            author: Автор
            assignee: Ответственный
            file_path: Путь к файлу
            due_date: Срок выполнения
            tags: Теги
            properties: Дополнительные свойства
        """
        self.id = id
        self.type = type
        self.title = title
        self.status = status
        self.description = description or ""
        self.created_at = created_at or time.time()
        self.updated_at = updated_at or time.time()
        self.author = author
        self.assignee = assignee
        self.file_path = file_path
        self.due_date = due_date
        self.tags = tags or []
        self.properties = properties or {}
        self.relations: List[WorkItemRelation] = []
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует рабочий элемент в словарь.
        
        Returns:
            Словарь с данными элемента
        """
        return {
            "id": self.id,
            "type": self.type.value,
            "title": self.title,
            "status": self.status.value,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "author": self.author,
            "assignee": self.assignee,
            "file_path": self.file_path,
            "due_date": self.due_date,
            "tags": self.tags,
            "properties": self.properties,
            "relations": [relation.to_dict() for relation in self.relations]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkItem':
        """
        Создает рабочий элемент из словаря.
        
        Args:
            data: Словарь с данными элемента
            
        Returns:
            Экземпляр рабочего элемента
        """
        item = cls(
            id=data["id"],
            type=WorkItemType(data["type"]),
            title=data["title"],
            status=WorkItemStatus(data["status"]),
            description=data.get("description", ""),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            author=data.get("author"),
            assignee=data.get("assignee"),
            file_path=data.get("file_path"),
            due_date=data.get("due_date"),
            tags=data.get("tags", []),
            properties=data.get("properties", {})
        )
        
        # Добавляем связи
        if "relations" in data:
            for relation_data in data["relations"]:
                item.relations.append(WorkItemRelation.from_dict(relation_data))
        
        return item
    
    def add_relation(self, target_id: str, relation_type: WorkItemRelationType, description: Optional[str] = None) -> bool:
        """
        Добавляет связь с другим элементом.
        
        Args:
            target_id: Идентификатор целевого элемента
            relation_type: Тип связи
            description: Описание связи
            
        Returns:
            True, если связь добавлена, иначе False
        """
        # Проверяем, нет ли уже такой связи
        for relation in self.relations:
            if relation.target_id == target_id and relation.relation_type == relation_type:
                return False
        
        # Создаем и добавляем связь
        relation = WorkItemRelation(
            source_id=self.id,
            target_id=target_id,
            relation_type=relation_type,
            description=description
        )
        
        self.relations.append(relation)
        self.updated_at = time.time()
        
        return True
    
    def remove_relation(self, target_id: str, relation_type: Optional[WorkItemRelationType] = None) -> bool:
        """
        Удаляет связь с другим элементом.
        
        Args:
            target_id: Идентификатор целевого элемента
            relation_type: Тип связи (если None, удаляются все связи с target_id)
            
        Returns:
            True, если связь удалена, иначе False
        """
        before_count = len(self.relations)
        
        if relation_type:
            # Удаляем конкретную связь
            self.relations = [
                relation for relation in self.relations
                if not (relation.target_id == target_id and relation.relation_type == relation_type)
            ]
        else:
            # Удаляем все связи с целевым элементом
            self.relations = [
                relation for relation in self.relations
                if relation.target_id != target_id
            ]
        
        after_count = len(self.relations)
        
        if after_count < before_count:
            self.updated_at = time.time()
            return True
        
        return False
    
    def get_related_items(self, relation_type: Optional[WorkItemRelationType] = None) -> List[str]:
        """
        Получает идентификаторы связанных элементов.
        
        Args:
            relation_type: Тип связи (если None, возвращаются все связанные элементы)
            
        Returns:
            Список идентификаторов связанных элементов
        """
        if relation_type:
            return [
                relation.target_id for relation in self.relations
                if relation.relation_type == relation_type
            ]
        else:
            return [relation.target_id for relation in self.relations]
    
    def update_status(self, new_status: WorkItemStatus) -> bool:
        """
        Обновляет статус элемента.
        
        Args:
            new_status: Новый статус
            
        Returns:
            True, если статус обновлен, иначе False
        """
        if self.status == new_status:
            return False
        
        self.status = new_status
        self.updated_at = time.time()
        
        return True
    
    def update_properties(self, properties_updates: Dict[str, Any]) -> bool:
        """
        Обновляет свойства элемента.
        
        Args:
            properties_updates: Обновления свойств
            
        Returns:
            True, если свойства обновлены, иначе False
        """
        if not properties_updates:
            return False
        
        self.properties.update(properties_updates)
        self.updated_at = time.time()
        
        return True


class TaskRegistry:
    """
    Центральный реестр для управления задачами, инцидентами, гипотезами и стандартами.
    
    Обеспечивает единую систему учета, создания и управления всеми рабочими элементами,
    включая проверку связей и целостности данных между кешем и файловой системой.
    """
    
    def __init__(
        self,
        registry_file: str = "registry.json",
        cache_path: str = ".cache_state.json",
        consistency_check_interval: int = 3600  # 1 час
    ):
        """
        Инициализация реестра.
        
        Args:
            registry_file: Путь к файлу реестра
            cache_path: Путь к файлу кеша
            consistency_check_interval: Интервал проверки целостности данных (в секундах)
        """
        self.registry_file = registry_file
        self.cache_path = cache_path
        self.consistency_check_interval = consistency_check_interval
        
        # Блокировка для многопоточного доступа
        self.lock = threading.RLock()
        
        # Загружаем реестр
        self.items: Dict[str, WorkItem] = {}
        self._load_registry()
        
        # Запускаем фоновую проверку целостности данных
        self._start_consistency_checker()
    
    def _load_registry(self) -> bool:
        """
        Загружает реестр из файла.
        
        Returns:
            True, если загрузка успешна, иначе False
        """
        with self.lock:
            # Проверяем существование файла
            if not os.path.exists(self.registry_file):
                logger.info(f"Файл реестра {self.registry_file} не существует. Создаем новый реестр.")
                self.items = {}
                return self._save_registry()
            
            # Загружаем данные из файла
            success, data = AtomicFileOperations.read_json(self.registry_file)
            
            if not success or not isinstance(data, dict):
                logger.error(f"Ошибка при загрузке реестра из файла {self.registry_file}")
                self.items = {}
                return False
            
            # Преобразуем данные в объекты WorkItem
            self.items = {}
            try:
                for item_id, item_data in data.items():
                    self.items[item_id] = WorkItem.from_dict(item_data)
                
                logger.info(f"Загружено {len(self.items)} элементов из реестра")
                return True
            except Exception as e:
                logger.error(f"Ошибка при преобразовании данных реестра: {e}")
                self.items = {}
                return False
    
    def _save_registry(self) -> bool:
        """
        Сохраняет реестр в файл.
        
        Returns:
            True, если сохранение успешно, иначе False
        """
        with self.lock:
            # Преобразуем объекты WorkItem в словари
            data = {item_id: item.to_dict() for item_id, item in self.items.items()}
            
            # Сохраняем данные в файл
            return AtomicFileOperations.write_json(self.registry_file, data)
    
    def _start_consistency_checker(self):
        """Запускает фоновую проверку целостности данных."""
        def consistency_checker():
            """JTBD:
Я (разработчик) хочу использовать функцию consistency_checker, чтобы эффективно выполнить соответствующую операцию.
             
             Фоновый процесс проверки целостности данных."""
            while True:
                try:
                    time.sleep(self.consistency_check_interval)
                    self.check_consistency()
                except Exception as e:
                    logger.error(f"Ошибка при проверке целостности данных: {e}")
        
        # Запускаем в фоновом потоке
        thread = threading.Thread(target=consistency_checker, daemon=True)
        thread.start()
    
    def get_outgoing_relations(self, item_id: str) -> List[WorkItemRelation]:
        """
        Получает список исходящих связей для указанного элемента.
        
        Args:
            item_id: Идентификатор элемента
            
        Returns:
            Список связей, исходящих от указанного элемента
        """
        with self.lock:
            if item_id in self.items:
                return self.items[item_id].relations
            else:
                logger.warning(f"Элемент с идентификатором {item_id} не найден")
                return []
    
    def get_incoming_relations(self, item_id: str) -> List[WorkItemRelation]:
        """
        Получает список входящих связей для указанного элемента.
        
        Args:
            item_id: Идентификатор элемента
            
        Returns:
            Список связей, направленных на указанный элемент
        """
        incoming_relations = []
        
        with self.lock:
            for source_id, source_item in self.items.items():
                for relation in source_item.relations:
                    if relation.target_id == item_id:
                        incoming_relations.append(relation)
        
        return incoming_relations

    def check_consistency(self) -> bool:
        """
        Проверяет целостность данных между кешем, реестром и файловой системой.
        
        Returns:
            True, если целостность данных обеспечена, иначе False
        """
        logger.info("Начало проверки целостности данных")
        
        # Проверяем целостность кеша
        verifier = CacheSyncVerifier(
            cache_paths=[self.cache_path],
            base_dir="."
        )
        
        missing_in_cache, missing_in_filesystem, metadata_mismatch = verifier.verify_sync()
        
        # Если есть проблемы, исправляем их
        if missing_in_cache or missing_in_filesystem or metadata_mismatch:
            logger.warning(
                f"Обнаружены проблемы синхронизации: "
                f"{len(missing_in_cache)} отсутствуют в кеше, "
                f"{len(missing_in_filesystem)} отсутствуют в файловой системе, "
                f"{len(metadata_mismatch)} имеют несоответствия метаданных"
            )
            
            # Исправляем проблемы
            if verifier.fix_sync_issues():
                logger.info("Проблемы синхронизации успешно исправлены")
            else:
                logger.error("Не удалось исправить все проблемы синхронизации")
                return False
        
        # Проверяем наличие файлов для элементов реестра
        with self.lock:
            missing_files = []
            for item_id, item in self.items.items():
                if item.file_path and not os.path.exists(item.file_path):
                    missing_files.append((item_id, item.file_path))
            
            if missing_files:
                logger.warning(f"Обнаружено {len(missing_files)} элементов с отсутствующими файлами")
                for item_id, file_path in missing_files:
                    logger.warning(f"Элемент {item_id}: файл {file_path} не существует")
        
        logger.info("Проверка целостности данных завершена")
        return True
    
    def generate_id(self, type: WorkItemType) -> str:
        """
        Генерирует уникальный идентификатор для нового элемента.
        
        Args:
            type: Тип элемента
            
        Returns:
            Уникальный идентификатор
        """
        with self.lock:
            # Получаем префикс в зависимости от типа
            prefix_map = {
                WorkItemType.TASK: "T",
                WorkItemType.INCIDENT: "I",
                WorkItemType.HYPOTHESIS: "H",
                WorkItemType.STANDARD: "S"
            }
            
            prefix = prefix_map.get(type, "X")
            
            # Ищем максимальный номер для данного типа
            max_num = 0
            for item_id in self.items.keys():
                if item_id.startswith(prefix):
                    try:
                        num = int(item_id[1:])
                        max_num = max(max_num, num)
                    except ValueError:
                        pass
            
            # Генерируем новый идентификатор
            return f"{prefix}{max_num + 1:04d}"
    
    def create_item(
        self,
        type: WorkItemType,
        title: str,
        description: Optional[str] = None,
        status: Optional[WorkItemStatus] = None,
        author: Optional[str] = None,
        assignee: Optional[str] = None,
        file_path: Optional[str] = None,
        due_date: Optional[float] = None,
        tags: Optional[List[str]] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> Optional[WorkItem]:
        """
        Создает новый рабочий элемент в реестре.
        
        Args:
            type: Тип элемента
            title: Название
            description: Описание
            status: Статус
            author: Автор
            assignee: Ответственный
            file_path: Путь к файлу
            due_date: Срок выполнения
            tags: Теги
            properties: Дополнительные свойства
            
        Returns:
            Созданный элемент или None в случае ошибки
        """
        with self.lock:
            # Генерируем идентификатор
            item_id = self.generate_id(type)
            
            # Определяем статус по умолчанию в зависимости от типа
            if status is None:
                default_status_map = {
                    WorkItemType.TASK: WorkItemStatus.BACKLOG,
                    WorkItemType.INCIDENT: WorkItemStatus.BACKLOG,
                    WorkItemType.HYPOTHESIS: WorkItemStatus.PROPOSED,
                    WorkItemType.STANDARD: WorkItemStatus.DRAFT
                }
                status = default_status_map.get(type, WorkItemStatus.BACKLOG)
            
            # Создаем элемент
            item = WorkItem(
                id=item_id,
                type=type,
                title=title,
                status=status,
                description=description,
                author=author,
                assignee=assignee,
                file_path=file_path,
                due_date=due_date,
                tags=tags,
                properties=properties
            )
            
            # Добавляем в реестр
            self.items[item_id] = item
            
            # Сохраняем реестр
            if not self._save_registry():
                logger.error(f"Не удалось сохранить реестр после создания элемента {item_id}")
                return None
            
            logger.info(f"Создан новый элемент {item_id} ({type.value}): {title}")
            return item
    
    def get_item(self, item_id: str) -> Optional[WorkItem]:
        """
        Получает элемент из реестра.
        
        Args:
            item_id: Идентификатор элемента
            
        Returns:
            Элемент или None, если элемент не найден
        """
        with self.lock:
            return self.items.get(item_id)
    
    def update_item(self, item_id: str, **updates) -> Optional[WorkItem]:
        """
        Обновляет элемент в реестре.
        
        Args:
            item_id: Идентификатор элемента
            **updates: Обновления атрибутов
            
        Returns:
            Обновленный элемент или None в случае ошибки
        """
        with self.lock:
            # Получаем элемент
            item = self.items.get(item_id)
            if not item:
                logger.error(f"Элемент {item_id} не найден в реестре")
                return None
            
            # Обновляем атрибуты
            if "title" in updates:
                item.title = updates["title"]
            
            if "description" in updates:
                item.description = updates["description"]
            
            if "status" in updates and isinstance(updates["status"], WorkItemStatus):
                item.status = updates["status"]
            
            if "assignee" in updates:
                item.assignee = updates["assignee"]
            
            if "file_path" in updates:
                item.file_path = updates["file_path"]
            
            if "due_date" in updates:
                item.due_date = updates["due_date"]
            
            if "tags" in updates:
                item.tags = updates["tags"]
            
            if "properties" in updates:
                item.properties.update(updates["properties"])
            
            # Обновляем время изменения
            item.updated_at = time.time()
            
            # Сохраняем реестр
            if not self._save_registry():
                logger.error(f"Не удалось сохранить реестр после обновления элемента {item_id}")
                return None
            
            logger.info(f"Обновлен элемент {item_id}: {', '.join(updates.keys())}")
            return item
    
    def delete_item(self, item_id: str) -> bool:
        """
        Удаляет элемент из реестра.
        
        Args:
            item_id: Идентификатор элемента
            
        Returns:
            True, если элемент удален, иначе False
        """
        with self.lock:
            # Проверяем наличие элемента
            if item_id not in self.items:
                logger.error(f"Элемент {item_id} не найден в реестре")
                return False
            
            # Получаем информацию об элементе для логирования
            item = self.items[item_id]
            item_type = item.type.value
            item_title = item.title
            
            # Удаляем элемент
            del self.items[item_id]
            
            # Удаляем связи с этим элементом из других элементов
            for other_item in self.items.values():
                other_item.remove_relation(item_id)
            
            # Сохраняем реестр
            if not self._save_registry():
                logger.error(f"Не удалось сохранить реестр после удаления элемента {item_id}")
                return False
            
            logger.info(f"Удален элемент {item_id} ({item_type}): {item_title}")
            return True
    
    def add_relation(
        self,
        source_id: str,
        target_id: str,
        relation_type: WorkItemRelationType,
        bidirectional: bool = True,
        description: Optional[str] = None
    ) -> bool:
        """
        Добавляет связь между элементами.
        
        Args:
            source_id: Идентификатор исходного элемента
            target_id: Идентификатор целевого элемента
            relation_type: Тип связи
            bidirectional: Создавать ли обратную связь
            description: Описание связи
            
        Returns:
            True, если связь добавлена, иначе False
        """
        with self.lock:
            # Проверяем наличие элементов
            source_item = self.items.get(source_id)
            target_item = self.items.get(target_id)
            
            if not source_item:
                logger.error(f"Исходный элемент {source_id} не найден в реестре")
                return False
            
            if not target_item:
                logger.error(f"Целевой элемент {target_id} не найден в реестре")
                return False
            
            # Добавляем связь
            source_updated = source_item.add_relation(target_id, relation_type, description)
            
            # Добавляем обратную связь, если нужно
            target_updated = False
            if bidirectional:
                # Создаем обратную связь
                inverse_relation = WorkItemRelation(
                    source_id=source_id,
                    target_id=target_id,
                    relation_type=relation_type,
                    description=description
                ).get_inverse_relation()
                
                target_updated = target_item.add_relation(
                    source_id,
                    inverse_relation.relation_type,
                    description
                )
            
            # Если что-то изменилось, сохраняем реестр
            if source_updated or target_updated:
                if not self._save_registry():
                    logger.error(f"Не удалось сохранить реестр после добавления связи {source_id} -> {target_id}")
                    return False
                
                logger.info(f"Добавлена связь {source_id} -> {target_id} ({relation_type.value})")
                return True
            
            return False
    
    def remove_relation(
        self,
        source_id: str,
        target_id: str,
        relation_type: Optional[WorkItemRelationType] = None,
        bidirectional: bool = True
    ) -> bool:
        """
        Удаляет связь между элементами.
        
        Args:
            source_id: Идентификатор исходного элемента
            target_id: Идентификатор целевого элемента
            relation_type: Тип связи (если None, удаляются все связи)
            bidirectional: Удалять ли обратную связь
            
        Returns:
            True, если связь удалена, иначе False
        """
        with self.lock:
            # Проверяем наличие элементов
            source_item = self.items.get(source_id)
            target_item = self.items.get(target_id)
            
            if not source_item:
                logger.error(f"Исходный элемент {source_id} не найден в реестре")
                return False
            
            if not target_item:
                logger.error(f"Целевой элемент {target_id} не найден в реестре")
                return False
            
            # Удаляем связь
            source_updated = source_item.remove_relation(target_id, relation_type)
            
            # Удаляем обратную связь, если нужно
            target_updated = False
            if bidirectional:
                target_updated = target_item.remove_relation(source_id, None)
            
            # Если что-то изменилось, сохраняем реестр
            if source_updated or target_updated:
                if not self._save_registry():
                    logger.error(f"Не удалось сохранить реестр после удаления связи {source_id} -> {target_id}")
                    return False
                
                logger.info(f"Удалена связь {source_id} -> {target_id}")
                return True
            
            return False
    
    def get_related_items(
        self,
        item_id: str,
        relation_type: Optional[WorkItemRelationType] = None
    ) -> List[WorkItem]:
        """
        Получает список связанных элементов.
        
        Args:
            item_id: Идентификатор элемента
            relation_type: Тип связи (если None, возвращаются все связанные элементы)
            
        Returns:
            Список связанных элементов
        """
        with self.lock:
            # Получаем элемент
            item = self.items.get(item_id)
            if not item:
                logger.error(f"Элемент {item_id} не найден в реестре")
                return []
            
            # Получаем идентификаторы связанных элементов
            related_ids = item.get_related_items(relation_type)
            
            # Получаем элементы по идентификаторам
            return [self.items.get(related_id) for related_id in related_ids if related_id in self.items]
    
    def find_items(
        self,
        type: Optional[WorkItemType] = None,
        status: Optional[WorkItemStatus] = None,
        author: Optional[str] = None,
        assignee: Optional[str] = None,
        tags: Optional[List[str]] = None,
        created_after: Optional[float] = None,
        created_before: Optional[float] = None,
        updated_after: Optional[float] = None,
        updated_before: Optional[float] = None,
        due_after: Optional[float] = None,
        due_before: Optional[float] = None,
        search_term: Optional[str] = None
    ) -> List[WorkItem]:
        """
        Поиск элементов по различным критериям.
        
        Args:
            type: Тип элемента
            status: Статус элемента
            author: Автор
            assignee: Ответственный
            tags: Теги (должны присутствовать все указанные теги)
            created_after: Создан после указанного времени
            created_before: Создан до указанного времени
            updated_after: Обновлен после указанного времени
            updated_before: Обновлен до указанного времени
            due_after: Срок выполнения после указанного времени
            due_before: Срок выполнения до указанного времени
            search_term: Поисковый запрос (ищется в заголовке и описании)
            
        Returns:
            Список найденных элементов
        """
        with self.lock:
            # Применяем фильтры
            results = []
            for item in self.items.values():
                # Фильтр по типу
                if type is not None and item.type != type:
                    continue
                
                # Фильтр по статусу
                if status is not None and item.status != status:
                    continue
                
                # Фильтр по автору
                if author is not None and item.author != author:
                    continue
                
                # Фильтр по ответственному
                if assignee is not None and item.assignee != assignee:
                    continue
                
                # Фильтр по тегам
                if tags is not None:
                    if not all(tag in item.tags for tag in tags):
                        continue
                
                # Фильтр по времени создания
                if created_after is not None and item.created_at < created_after:
                    continue
                
                if created_before is not None and item.created_at > created_before:
                    continue
                
                # Фильтр по времени обновления
                if updated_after is not None and item.updated_at < updated_after:
                    continue
                
                if updated_before is not None and item.updated_at > updated_before:
                    continue
                
                # Фильтр по сроку выполнения
                if due_after is not None:
                    if item.due_date is None or item.due_date < due_after:
                        continue
                
                if due_before is not None:
                    if item.due_date is None or item.due_date > due_before:
                        continue
                
                # Фильтр по поисковому запросу
                if search_term is not None:
                    search_term_lower = search_term.lower()
                    title_match = search_term_lower in item.title.lower()
                    desc_match = search_term_lower in item.description.lower()
                    
                    if not (title_match or desc_match):
                        continue
                
                # Если прошел все фильтры, добавляем в результаты
                results.append(item)
            
            return results


# Создаем глобальный экземпляр реестра
_REGISTRY = None

def get_registry() -> TaskRegistry:
    """
    Получает глобальный экземпляр реестра.
    
    Returns:
        Экземпляр TaskRegistry
    """
    global _REGISTRY
    
    if _REGISTRY is None:
        _REGISTRY = TaskRegistry()
    
    return _REGISTRY


def main():
    """JTBD:
Я (разработчик) хочу использовать функцию main, чтобы эффективно выполнить соответствующую операцию.
     
     Основная функция модуля."""
    if len(sys.argv) > 1 and sys.argv[1] == "check_consistency":
        # Проверяем целостность данных
        registry = get_registry()
        if registry.check_consistency():
            print("Проверка целостности данных успешно завершена")
            return 0
        else:
            print("Обнаружены проблемы с целостностью данных")
            return 1
    
    # Просто инициализируем реестр, если нет аргументов
    registry = get_registry()
    print(f"Реестр инициализирован, загружено {len(registry.items)} элементов")
    return 0


if __name__ == "__main__":
    sys.exit(main())