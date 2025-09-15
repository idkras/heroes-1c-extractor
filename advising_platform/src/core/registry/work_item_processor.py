"""
Модуль для обработки рабочих элементов (задач, инцидентов, гипотез, стандартов).

Обеспечивает стандартизированный процесс создания, обновления и управления
рабочими элементами, гарантируя целостность данных, проверку зависимостей и 
соблюдение стандартов.

Автор: AI Assistant
Дата: 20 мая 2025
"""

import os
import logging
import traceback
from typing import Dict, List, Optional, Tuple, Any, Union, Set, Callable
from enum import Enum

# Настройка логирования
logger = logging.getLogger("work_item_processor")
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Импорт необходимых модулей
try:
    import sys
    from pathlib import Path
    
    # Добавляем корневую директорию в путь
    current_dir = Path(__file__).parent
    root_dir = current_dir.parent.parent.parent
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))
    
    from src.core.registry.task_registry import (
        TaskRegistry, WorkItem, WorkItemType, WorkItemStatus, WorkItemRelationType,
        get_registry
    )
    from src.core.cache_sync.cache_sync_verifier import CacheSyncVerifier
    from src.core.cache_sync.transaction_manager import AtomicFileOperations
    from src.core.standards.standard_manifest import (
        StandardManifest, ManifestSectionType, StandardTemplate
    )
    from src.core.notifications import (
        NotificationType, NotificationPriority, NotificationChannel,
        send_notification
    )
except ImportError as e:
    logger.error(f"Ошибка импорта модулей: {e}")
    traceback.print_exc()
    raise


class ProcessStage(Enum):
    """JTBD:
Я (разработчик) хочу использовать функциональность класса ProcessStage, чтобы эффективно решать соответствующие задачи в системе.
    
    Стадии процесса обработки рабочего элемента."""
    PRE_CHECK = "pre_check"           # Предварительные проверки
    VALIDATION = "validation"         # Валидация данных
    CREATION = "creation"             # Создание нового элемента
    UPDATE = "update"                 # Обновление существующего элемента
    FILE_OPERATIONS = "file_operations"  # Операции с файлами
    RELATION_PROCESSING = "relation_processing"  # Обработка связей
    CACHE_SYNC = "cache_sync"         # Синхронизация кеша
    NOTIFICATIONS = "notifications"   # Отправка уведомлений
    POST_PROCESSING = "post_processing"  # Завершающие операции
    REPORT = "report"                 # Формирование отчета
    COMPLETE = "complete"             # Завершение процесса


class ProcessResult:
    """JTBD:
Я (разработчик) хочу использовать функциональность класса ProcessResult, чтобы эффективно решать соответствующие задачи в системе.
    
    Результат выполнения процесса обработки рабочего элемента."""
    
    def __init__(self):
        """Инициализация результата процесса."""
        self.success = False
        self.stage = ProcessStage.PRE_CHECK
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
        self.item: Optional[WorkItem] = None
        self.related_items: List[WorkItem] = []
        self.file_paths: List[str] = []
        self.similar_items: List[Tuple[WorkItem, float]] = []
        self.process_log: List[Dict[str, Any]] = []
    
    def add_error(self, message: str, stage: Optional[ProcessStage] = None):
        """
        Добавляет сообщение об ошибке.
        
        Args:
            message: Текст сообщения
            stage: Стадия процесса (если None, используется текущая стадия)
        """
        if stage:
            self.stage = stage
        
        self.errors.append(message)
        logger.error(f"[{self.stage.value}] {message}")
        
        # Добавляем в лог процесса
        self.process_log.append({
            "stage": self.stage.value,
            "type": "error",
            "message": message
        })
    
    def add_warning(self, message: str, stage: Optional[ProcessStage] = None):
        """
        Добавляет предупреждение.
        
        Args:
            message: Текст сообщения
            stage: Стадия процесса (если None, используется текущая стадия)
        """
        if stage:
            self.stage = stage
        
        self.warnings.append(message)
        logger.warning(f"[{self.stage.value}] {message}")
        
        # Добавляем в лог процесса
        self.process_log.append({
            "stage": self.stage.value,
            "type": "warning",
            "message": message
        })
    
    def add_info(self, message: str, stage: Optional[ProcessStage] = None):
        """
        Добавляет информационное сообщение.
        
        Args:
            message: Текст сообщения
            stage: Стадия процесса (если None, используется текущая стадия)
        """
        if stage:
            self.stage = stage
        
        self.info.append(message)
        logger.info(f"[{self.stage.value}] {message}")
        
        # Добавляем в лог процесса
        self.process_log.append({
            "stage": self.stage.value,
            "type": "info",
            "message": message
        })
    
    def set_stage(self, stage: ProcessStage):
        """
        Устанавливает текущую стадию процесса.
        
        Args:
            stage: Стадия процесса
        """
        self.stage = stage
        
        # Добавляем в лог процесса
        self.process_log.append({
            "stage": stage.value,
            "type": "stage_change",
            "message": f"Переход к стадии {stage.value}"
        })
    
    def is_successful(self) -> bool:
        """
        Проверяет успешность выполнения процесса.
        
        Returns:
            True, если процесс выполнен успешно, иначе False
        """
        return self.success and not self.errors
    
    def get_item_id(self) -> Optional[str]:
        """
        Получает идентификатор обработанного элемента.
        
        Returns:
            Идентификатор элемента или None, если элемент не создан
        """
        return self.item.id if self.item else None
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Получает краткую сводку по результатам процесса.
        
        Returns:
            Словарь с результатами
        """
        return {
            "success": self.success,
            "errors_count": len(self.errors),
            "warnings_count": len(self.warnings),
            "info_count": len(self.info),
            "last_stage": self.stage.value,
            "item_id": self.get_item_id(),
            "item_type": self.item.type.value if self.item else None,
            "item_title": self.item.title if self.item else None,
            "related_items_count": len(self.related_items),
            "similar_items_count": len(self.similar_items)
        }
    
    def get_full_report(self) -> Dict[str, Any]:
        """
        Получает полный отчет о выполнении процесса.
        
        Returns:
            Словарь с полным отчетом
        """
        return {
            "success": self.success,
            "stage": self.stage.value,
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "item": self.item.to_dict() if self.item else None,
            "related_items": [item.to_dict() for item in self.related_items],
            "similar_items": [
                {"item": item.to_dict(), "similarity": similarity}
                for item, similarity in self.similar_items
            ],
            "file_paths": self.file_paths,
            "process_log": self.process_log
        }


class WorkItemProcessor:
    """
    Процессор для обработки рабочих элементов.
    
    Обеспечивает стандартизированный процесс создания, обновления и управления
    рабочими элементами, гарантируя целостность данных, проверку зависимостей и
    соблюдение стандартов.
    """
    
    def __init__(
        self,
        registry: Optional[TaskRegistry] = None,
        cache_path: str = ".cache_state.json",
        similarity_threshold: float = 0.7,
        enable_notifications: bool = True
    ):
        """
        Инициализация процессора.
        
        Args:
            registry: Реестр задач (если None, используется глобальный реестр)
            cache_path: Путь к файлу кеша
            similarity_threshold: Порог сходства для поиска похожих элементов
            enable_notifications: Включить отправку уведомлений
        """
        self.registry = registry or get_registry()
        self.cache_path = cache_path
        self.similarity_threshold = similarity_threshold
        self.enable_notifications = enable_notifications
        
        # Создаем валидатор кеша
        self.cache_verifier = CacheSyncVerifier(
            cache_paths=[self.cache_path],
            base_dir="."
        )
    
    def check_cache_consistency(self) -> bool:
        """
        Проверяет целостность кеша.
        
        Returns:
            True, если кеш в согласованном состоянии, иначе False
        """
        try:
            # Проверяем целостность кеша
            missing_in_cache, missing_in_filesystem, metadata_mismatch = \
                self.cache_verifier.verify_sync()
            
            # Если есть проблемы, исправляем их
            if missing_in_cache or missing_in_filesystem or metadata_mismatch:
                logger.warning(
                    f"Обнаружены проблемы синхронизации: "
                    f"{len(missing_in_cache)} отсутствуют в кеше, "
                    f"{len(missing_in_filesystem)} отсутствуют в файловой системе, "
                    f"{len(metadata_mismatch)} имеют несоответствия метаданных"
                )
                
                return self.cache_verifier.fix_sync_issues()
            
            return True
        except Exception as e:
            logger.error(f"Ошибка при проверке целостности кеша: {e}")
            return False
    
    def send_item_notification(
        self,
        result: ProcessResult,
        notification_type: NotificationType,
        operation_desc: str = "создания"
    ) -> bool:
        """
        Отправляет уведомление о создании или обновлении элемента.
        
        Args:
            result: Результат операции
            notification_type: Тип уведомления
            operation_desc: Описание операции (для логирования)
            
        Returns:
            True, если уведомление отправлено успешно, иначе False
        """
        if not self.enable_notifications or not result.item:
            return False
            
        try:
            result.set_stage(ProcessStage.NOTIFICATIONS)
            result.add_info(f"Подготовка уведомления о {operation_desc} элемента")
            
            item_type_str = {
                WorkItemType.TASK: "задача",
                WorkItemType.INCIDENT: "инцидент",
                WorkItemType.HYPOTHESIS: "гипотеза",
                WorkItemType.STANDARD: "стандарт",
                WorkItemType.EXPERIMENT: "эксперимент"
            }.get(result.item.type, "элемент")
            
            # Формируем заголовок и сообщение в зависимости от типа уведомления
            if notification_type == NotificationType.ITEM_CREATED:
                notification_title = f"Создан новый {item_type_str}: {result.item.id}"
            elif notification_type == NotificationType.ITEM_UPDATED:
                notification_title = f"Обновлен {item_type_str}: {result.item.id}"
            else:
                notification_title = f"Операция с элементом {result.item.id} ({item_type_str})"
                
            notification_message = result.item.title
            
            # Формируем данные для уведомления
            notification_data = {
                "item_id": result.item.id,
                "item_type": result.item.type.value,
                "item_title": result.item.title,
                "created_by": getattr(result.item, "author", "система"),
                "file_path": getattr(result.item, "file_path", ""),
                "process_log": [log for log in result.process_log if log["type"] != "stage_change"]
            }
            
            # Отправляем уведомление
            success = send_notification(
                notification_type=notification_type,
                title=notification_title,
                message=notification_message,
                data=notification_data,
                priority=NotificationPriority.NORMAL
            )
            
            if success:
                result.add_info(f"Отправлено уведомление о {operation_desc} {item_type_str} {result.item.id}")
            else:
                result.add_warning(f"Проблема при отправке уведомления о {operation_desc} {item_type_str} {result.item.id}")
                
            return success
        except Exception as e:
            result.add_warning(f"Не удалось отправить уведомление о {operation_desc} элемента: {e}")
            return False
    
    def find_similar_items(
        self,
        title: str,
        type: Optional[WorkItemType] = None
    ) -> List[Tuple[WorkItem, float]]:
        """
        Ищет похожие элементы по заголовку.
        
        Args:
            title: Заголовок элемента
            type: Тип элемента (если None, ищет среди всех типов)
            
        Returns:
            Список кортежей (элемент, степень сходства)
        """
        # Собственная реализация для исключения зависимости от registry.find_similar_items
        if not title:
            return []
        
        title_lower = title.lower()
        similar_items = []
        
        for item in self.registry.items.values():
            # Фильтруем по типу, если указан
            if type and item.type != type:
                continue
            
            # Простая проверка на частичное совпадение
            item_title_lower = item.title.lower()
            
            if title_lower in item_title_lower or item_title_lower in title_lower:
                # Базовое сходство на основе длины совпадающей части
                overlap = len(set(title_lower.split()) & set(item_title_lower.split()))
                total = len(set(title_lower.split()) | set(item_title_lower.split()))
                similarity = overlap / total if total > 0 else 0
                
                if similarity >= self.similarity_threshold:
                    similar_items.append((item, similarity))
        
        # Сортируем по убыванию степени сходства
        similar_items.sort(key=lambda x: x[1], reverse=True)
        
        # Ограничиваем количество результатов
        return similar_items[:5]
    
    def validate_mandatory_fields(
        self,
        type: WorkItemType,
        title: str,
        description: Optional[str] = None,
        file_path: Optional[str] = None
    ) -> List[str]:
        """
        Валидирует обязательные поля элемента.
        
        Args:
            type: Тип элемента
            title: Заголовок
            description: Описание
            file_path: Путь к файлу
            
        Returns:
            Список сообщений об ошибках (пустой список, если ошибок нет)
        """
        errors = []
        
        # Проверка заголовка
        if not title:
            errors.append("Не указан заголовок элемента")
        elif len(title) < 3:
            errors.append("Заголовок элемента слишком короткий (минимум 3 символа)")
        elif len(title) > 200:
            errors.append("Заголовок элемента слишком длинный (максимум 200 символов)")
        
        # Проверка описания в зависимости от типа
        if type in [WorkItemType.TASK, WorkItemType.INCIDENT, WorkItemType.HYPOTHESIS]:
            if not description:
                errors.append(f"Для элемента типа {type.value} необходимо указать описание")
        
        # Проверка файла
        if file_path:
            if os.path.exists(file_path) and os.path.isdir(file_path):
                errors.append(f"Путь {file_path} указывает на директорию, а не на файл")
        
        # Дополнительные проверки для стандартов
        if type == WorkItemType.STANDARD and file_path:
            # Проверяем соответствие файла требованиям мини-манифеста
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    manifest = StandardManifest.from_markdown(content, file_path)
                    if not manifest.is_complete:
                        errors.append(
                            f"Файл стандарта {file_path} не соответствует требованиям мини-манифеста. "
                            f"Отсутствуют разделы: {', '.join(manifest.missing_sections)}"
                        )
                except Exception as e:
                    errors.append(f"Ошибка при проверке манифеста в файле {file_path}: {e}")
        
        return errors
    
    def create_task(
        self,
        title: str,
        description: str,
        status: Optional[WorkItemStatus] = None,
        author: Optional[str] = None,
        assignee: Optional[str] = None,
        file_path: Optional[str] = None,
        due_date: Optional[float] = None,
        tags: Optional[List[str]] = None,
        properties: Optional[Dict[str, Any]] = None,
        related_items: Optional[List[Tuple[str, WorkItemRelationType]]] = None
    ) -> ProcessResult:
        """
        Создает новую задачу.
        
        Args:
            title: Заголовок задачи
            description: Описание задачи
            status: Статус задачи
            author: Автор задачи
            assignee: Ответственный за задачу
            file_path: Путь к файлу с описанием задачи
            due_date: Срок выполнения задачи
            tags: Теги задачи
            properties: Дополнительные свойства задачи
            related_items: Список связанных элементов (идентификатор, тип связи)
            
        Returns:
            Результат создания задачи
        """
        return self.create_work_item(
            type=WorkItemType.TASK,
            title=title,
            description=description,
            status=status,
            author=author,
            assignee=assignee,
            file_path=file_path,
            due_date=due_date,
            tags=tags,
            properties=properties,
            related_items=related_items
        )
    
    def create_incident(
        self,
        title: str,
        description: str,
        status: Optional[WorkItemStatus] = None,
        author: Optional[str] = None,
        assignee: Optional[str] = None,
        file_path: Optional[str] = None,
        tags: Optional[List[str]] = None,
        properties: Optional[Dict[str, Any]] = None,
        related_items: Optional[List[Tuple[str, WorkItemRelationType]]] = None
    ) -> ProcessResult:
        """
        Создает новый инцидент.
        
        Args:
            title: Заголовок инцидента
            description: Описание инцидента
            status: Статус инцидента
            author: Автор инцидента
            assignee: Ответственный за инцидент
            file_path: Путь к файлу с описанием инцидента
            tags: Теги инцидента
            properties: Дополнительные свойства инцидента
            related_items: Список связанных элементов (идентификатор, тип связи)
            
        Returns:
            Результат создания инцидента
        """
        return self.create_work_item(
            type=WorkItemType.INCIDENT,
            title=title,
            description=description,
            status=status,
            author=author,
            assignee=assignee,
            file_path=file_path,
            tags=tags,
            properties=properties,
            related_items=related_items
        )
    
    def create_hypothesis(
        self,
        title: str,
        description: str,
        status: Optional[WorkItemStatus] = None,
        author: Optional[str] = None,
        file_path: Optional[str] = None,
        tags: Optional[List[str]] = None,
        properties: Optional[Dict[str, Any]] = None,
        related_items: Optional[List[Tuple[str, WorkItemRelationType]]] = None
    ) -> ProcessResult:
        """
        Создает новую гипотезу.
        
        Args:
            title: Заголовок гипотезы
            description: Описание гипотезы
            status: Статус гипотезы
            author: Автор гипотезы
            file_path: Путь к файлу с описанием гипотезы
            tags: Теги гипотезы
            properties: Дополнительные свойства гипотезы
            related_items: Список связанных элементов (идентификатор, тип связи)
            
        Returns:
            Результат создания гипотезы
        """
        return self.create_work_item(
            type=WorkItemType.HYPOTHESIS,
            title=title,
            description=description,
            status=status,
            author=author,
            file_path=file_path,
            tags=tags,
            properties=properties,
            related_items=related_items
        )
    
    def create_standard(
        self,
        title: str,
        description: Optional[str] = None,
        status: Optional[WorkItemStatus] = None,
        author: Optional[str] = None,
        file_path: Optional[str] = None,
        tags: Optional[List[str]] = None,
        properties: Optional[Dict[str, Any]] = None,
        related_items: Optional[List[Tuple[str, WorkItemRelationType]]] = None,
        standard_type: str = "basic"
    ) -> ProcessResult:
        """
        Создает новый стандарт.
        
        Args:
            title: Заголовок стандарта
            description: Описание стандарта
            status: Статус стандарта
            author: Автор стандарта
            file_path: Путь к файлу стандарта
            tags: Теги стандарта
            properties: Дополнительные свойства стандарта
            related_items: Список связанных элементов (идентификатор, тип связи)
            standard_type: Тип стандарта (basic, process, code, design)
            
        Returns:
            Результат создания стандарта
        """
        result = ProcessResult()
        result.set_stage(ProcessStage.PRE_CHECK)
        
        # Если файл не указан, генерируем стандартный путь
        if not file_path:
            base_dir = "[standards .md]/0. core standards"
            if not os.path.exists(base_dir):
                os.makedirs(base_dir, exist_ok=True)
            
            # Генерируем имя файла из заголовка
            safe_title = title.lower().replace(" ", "-").replace("/", "-")
            file_path = os.path.join(base_dir, f"{safe_title}.md")
            
            result.add_info(f"Автоматически сгенерирован путь к файлу стандарта: {file_path}")
        
        # Проверяем, существует ли файл
        if not os.path.exists(file_path):
            # Создаем директорию, если её нет
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # Создаем файл стандарта по шаблону
            try:
                if standard_type == "basic":
                    content = StandardTemplate.get_basic_template(title)
                elif standard_type == "process":
                    content = StandardTemplate.get_process_template(title)
                elif standard_type == "code":
                    content = StandardTemplate.get_code_template(title)
                elif standard_type == "design":
                    content = StandardTemplate.get_design_template(title)
                else:
                    result.add_warning(f"Неизвестный тип стандарта: {standard_type}, используем базовый шаблон")
                    content = StandardTemplate.get_basic_template(title)
                
                # Записываем контент в файл
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                
                result.add_info(f"Создан файл стандарта {file_path} с использованием шаблона {standard_type}")
                
                # НОВОЕ: Проверка соответствия Registry Standard согласно T005
                try:
                    from advising_platform.src.standards.registry_compliance_checker import check_registry_compliance_on_trigger
                    
                    is_compliant = check_registry_compliance_on_trigger(file_path, operation="create")
                    
                    if is_compliant:
                        result.add_info(f"✅ Стандарт соответствует Registry Standard")
                    else:
                        result.add_warning(f"⚠️ Стандарт не соответствует Registry Standard - проверьте размещение в правильной папке")
                        
                except ImportError:
                    result.add_warning("Registry compliance checker недоступен")
                except Exception as e:
                    result.add_warning(f"Ошибка при проверке Registry compliance: {e}")
                    
            except Exception as e:
                result.add_error(f"Ошибка при создании файла стандарта {file_path}: {e}")
                return result
        
        # Создаем стандарт как рабочий элемент
        return self.create_work_item(
            type=WorkItemType.STANDARD,
            title=title,
            description=description,
            status=status,
            author=author,
            file_path=file_path,
            tags=tags,
            properties=properties,
            related_items=related_items
        )
    
    def create_work_item(
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
        properties: Optional[Dict[str, Any]] = None,
        related_items: Optional[List[Tuple[str, WorkItemRelationType]]] = None
    ) -> ProcessResult:
        """
        Создает новый рабочий элемент.
        
        Args:
            type: Тип элемента
            title: Заголовок
            description: Описание
            status: Статус
            author: Автор
            assignee: Ответственный
            file_path: Путь к файлу
            due_date: Срок выполнения
            tags: Теги
            properties: Дополнительные свойства
            related_items: Список связанных элементов (идентификатор, тип связи)
            
        Returns:
            Результат создания элемента
        """
        result = ProcessResult()
        
        try:
            # 1. Предварительные проверки
            result.set_stage(ProcessStage.PRE_CHECK)
            result.add_info("Начало предварительных проверок (pre_check)")
            
            # 1.1. Проверка целостности кеша
            result.add_info("Проверка целостности кеша...")
            cache_consistency = self.check_cache_consistency()
            if not cache_consistency:
                result.add_warning("Обнаружены проблемы с целостностью кеша")
            else:
                result.add_info("Проверка целостности кеша успешно завершена")
            
            # 1.2. Проверка существования директорий
            dir_path = os.path.dirname(file_path) if file_path else None
            if dir_path:
                result.add_info(f"Проверка существования директории: {dir_path}")
                if not os.path.exists(dir_path):
                    result.add_info(f"Директория не существует: {dir_path}. Будет создана автоматически.")
                else:
                    result.add_info(f"Директория существует: {dir_path}")
            
            # 1.3. Поиск похожих элементов
            result.add_info(f"Поиск элементов, похожих на '{title}'...")
            similar_items = self.find_similar_items(title, type)
            result.similar_items = similar_items
            
            if similar_items:
                result.add_warning(
                    f"Найдено {len(similar_items)} похожих элементов. "
                    f"Рекомендуется проверить их перед созданием нового."
                )
                
                # Логируем информацию о похожих элементах
                for i, (item, similarity) in enumerate(similar_items[:3], 1):
                    result.add_info(
                        f"Похожий элемент #{i}: {item.id} '{item.title}' "
                        f"(сходство: {similarity:.2f})"
                    )
            else:
                result.add_info("Похожих элементов не найдено")
            
            result.add_info("Предварительные проверки (pre_check) завершены")
            
            # 2. Валидация данных
            result.set_stage(ProcessStage.VALIDATION)
            result.add_info("Начало валидации данных")
            
            # 2.1. Проверка обязательных полей
            result.add_info("Проверка обязательных полей...")
            validation_errors = self.validate_mandatory_fields(
                type=type,
                title=title,
                description=description,
                file_path=file_path
            )
            
            if validation_errors:
                for error in validation_errors:
                    result.add_error(error)
                result.add_info("Обнаружены ошибки валидации, прерывание процесса создания")
                return result
            else:
                result.add_info("Все обязательные поля заполнены корректно")
            
            # 2.2. Проверка названия (дополнительная валидация)
            if any(char in title for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']):
                error_msg = "Название содержит недопустимые символы (/, \\, :, *, ?, \", <, >, |)"
                result.add_error(error_msg)
                return result
            else:
                result.add_info("Проверка названия на недопустимые символы пройдена")
            
            # 2.3. Проверка связанных элементов
            if related_items:
                result.add_info(f"Проверка {len(related_items)} связанных элементов...")
                for item_id, relation_type in related_items:
                    result.add_info(f"Проверка связанного элемента {item_id}...")
                    related_item = self.registry.get_item(item_id)
                    if not related_item:
                        result.add_error(f"Связанный элемент {item_id} не найден в реестре")
                        return result
                    
                    result.related_items.append(related_item)
                    result.add_info(f"Связанный элемент {item_id} существует ({related_item.type.value}: {related_item.title})")
            else:
                result.add_info("Связанные элементы не указаны")
                
            result.add_info("Валидация данных успешно завершена")
            
            # 3. Создание элемента
            result.set_stage(ProcessStage.CREATION)
            
            # 3.1. Создаем элемент в реестре
            item = self.registry.create_item(
                type=type,
                title=title,
                description=description,
                status=status,
                author=author,
                assignee=assignee,
                file_path=file_path,
                due_date=due_date,
                tags=tags,
                properties=properties
            )
            
            if not item:
                result.add_error("Не удалось создать элемент в реестре")
                return result
            
            result.item = item
            result.add_info(f"Создан элемент {item.id} ({type.value}): {title}")
            
            # 4. Обработка связей
            result.set_stage(ProcessStage.RELATION_PROCESSING)
            
            # 4.1. Добавляем связи с другими элементами
            if related_items:
                for item_id, relation_type in related_items:
                    success = self.registry.add_relation(
                        source_id=item.id,
                        target_id=item_id,
                        relation_type=relation_type
                    )
                    
                    if success:
                        result.add_info(f"Добавлена связь {item.id} -> {item_id} ({relation_type.value})")
                    else:
                        result.add_warning(f"Не удалось добавить связь {item.id} -> {item_id}")
            
            # 5. Операции с файлами
            result.set_stage(ProcessStage.FILE_OPERATIONS)
            
            # 5.1. Если указан путь к файлу, но файл не существует, создаем его
            if file_path and not os.path.exists(file_path):
                try:
                    # Создаем директорию, если её нет
                    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
                    
                    # Создаем базовый контент в зависимости от типа
                    content = f"# {title}\n\n"
                    
                    if type == WorkItemType.TASK:
                        content += f"## Описание задачи\n\n{description or ''}\n\n"
                        content += "## Критерии выполнения\n\n- [ ] Критерий 1\n\n"
                    elif type == WorkItemType.INCIDENT:
                        content += f"## Описание инцидента\n\n{description or ''}\n\n"
                        content += "## Шаги воспроизведения\n\n1. Шаг 1\n\n"
                        content += "## Анализ причин (5 почему)\n\n1. Почему произошел инцидент?\n\n"
                    elif type == WorkItemType.HYPOTHESIS:
                        content += f"## Гипотеза\n\n{description or ''}\n\n"
                        content += "## Метод проверки\n\n...\n\n"
                        content += "## Результаты\n\n...\n\n"
                    
                    # Записываем контент в файл
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    
                    result.add_info(f"Создан файл {file_path}")
                    result.file_paths.append(file_path)
                except Exception as e:
                    result.add_error(f"Ошибка при создании файла {file_path}: {e}")
            elif file_path:
                result.file_paths.append(file_path)
            
            # 6. Синхронизация кеша
            result.set_stage(ProcessStage.CACHE_SYNC)
            
            # 6.1. Проверяем и обновляем кеш
            if result.file_paths:
                missing_in_cache, _, _ = self.cache_verifier.verify_sync()
                
                for path in result.file_paths:
                    if path in missing_in_cache:
                        result.add_info(f"Файл {path} добавлен в кеш")
            
            # 7. Завершение процесса
            result.set_stage(ProcessStage.COMPLETE)
            result.success = True
            
            return result
        
        except Exception as e:
            # Логируем ошибку и возвращаем результат
            logger.error(f"Ошибка при создании элемента: {e}")
            traceback.print_exc()
            
            result.add_error(f"Неожиданная ошибка: {e}")
            return result
    
    def update_work_item(
        self,
        item_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[WorkItemStatus] = None,
        assignee: Optional[str] = None,
        file_path: Optional[str] = None,
        due_date: Optional[float] = None,
        tags: Optional[List[str]] = None,
        properties: Optional[Dict[str, Any]] = None,
        add_relations: Optional[List[Tuple[str, WorkItemRelationType]]] = None,
        remove_relations: Optional[List[str]] = None
    ) -> ProcessResult:
        """
        Обновляет существующий рабочий элемент.
        
        Args:
            item_id: Идентификатор элемента
            title: Новый заголовок
            description: Новое описание
            status: Новый статус
            assignee: Новый ответственный
            file_path: Новый путь к файлу
            due_date: Новый срок выполнения
            tags: Новые теги
            properties: Новые или обновленные свойства
            add_relations: Список связей для добавления (идентификатор, тип связи)
            remove_relations: Список идентификаторов элементов, связи с которыми нужно удалить
            
        Returns:
            Результат обновления элемента
        """
        result = ProcessResult()
        
        try:
            # 1. Предварительные проверки
            result.set_stage(ProcessStage.PRE_CHECK)
            
            # 1.1. Проверка целостности кеша
            if not self.check_cache_consistency():
                result.add_warning("Обнаружены проблемы с целостностью кеша")
            
            # 1.2. Получаем элемент
            item = self.registry.get_item(item_id)
            if not item:
                result.add_error(f"Элемент {item_id} не найден в реестре")
                return result
            
            result.item = item
            result.add_info(f"Получен элемент {item_id} ({item.type.value}): {item.title}")
            
            # 2. Валидация данных
            result.set_stage(ProcessStage.VALIDATION)
            
            # 2.1. Если меняется заголовок, проверяем на похожие элементы
            if title and title != item.title:
                similar_items = self.find_similar_items(title, item.type)
                result.similar_items = similar_items
                
                if similar_items:
                    result.add_warning(
                        f"Найдено {len(similar_items)} похожих элементов на новый заголовок. "
                        f"Рекомендуется проверить их перед обновлением."
                    )
            
            # 2.2. Проверка связанных элементов
            if add_relations:
                for related_id, relation_type in add_relations:
                    related_item = self.registry.get_item(related_id)
                    if not related_item:
                        result.add_error(f"Связанный элемент {related_id} не найден в реестре")
                        return result
                    
                    result.related_items.append(related_item)
            
            # 3. Обновление элемента
            result.set_stage(ProcessStage.UPDATE)
            
            # Создаем словарь с обновлениями
            updates = {}
            
            if title:
                updates["title"] = title
            
            if description is not None:
                updates["description"] = description
            
            if status:
                updates["status"] = status
            
            if assignee is not None:
                updates["assignee"] = assignee
            
            if file_path is not None:
                updates["file_path"] = file_path
            
            if due_date is not None:
                updates["due_date"] = due_date
            
            if tags is not None:
                updates["tags"] = tags
            
            if properties:
                updates["properties"] = properties
            
            # 3.1. Обновляем элемент, если есть изменения
            if updates:
                updated_item = self.registry.update_item(item_id, **updates)
                if not updated_item:
                    result.add_error(f"Не удалось обновить элемент {item_id}")
                    return result
                
                result.item = updated_item
                result.add_info(f"Обновлен элемент {item_id}: {', '.join(updates.keys())}")
            
            # 4. Обработка связей
            result.set_stage(ProcessStage.RELATION_PROCESSING)
            
            # 4.1. Добавляем новые связи
            if add_relations:
                for related_id, relation_type in add_relations:
                    success = self.registry.add_relation(
                        source_id=item_id,
                        target_id=related_id,
                        relation_type=relation_type
                    )
                    
                    if success:
                        result.add_info(f"Добавлена связь {item_id} -> {related_id} ({relation_type.value})")
                    else:
                        result.add_warning(f"Не удалось добавить связь {item_id} -> {related_id}")
            
            # 4.2. Удаляем указанные связи
            if remove_relations:
                for related_id in remove_relations:
                    success = self.registry.remove_relation(
                        source_id=item_id,
                        target_id=related_id
                    )
                    
                    if success:
                        result.add_info(f"Удалена связь {item_id} -> {related_id}")
                    else:
                        result.add_warning(f"Не удалось удалить связь {item_id} -> {related_id}")
            
            # 5. Операции с файлами
            result.set_stage(ProcessStage.FILE_OPERATIONS)
            
            # 5.1. Если файл изменился и указан новый путь, обрабатываем его
            if "file_path" in updates and file_path:
                # Если файл не существует, создаем его
                if not os.path.exists(file_path):
                    try:
                        # Создаем директорию, если её нет
                        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
                        
                        # Создаем базовый контент
                        content = f"# {item.title}\n\n"
                        
                        # Записываем контент в файл
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(content)
                        
                        result.add_info(f"Создан новый файл {file_path}")
                        result.file_paths.append(file_path)
                    except Exception as e:
                        result.add_error(f"Ошибка при создании файла {file_path}: {e}")
                else:
                    result.add_info(f"Файл {file_path} уже существует")
                    result.file_paths.append(file_path)
            
            # 6. Синхронизация кеша
            result.set_stage(ProcessStage.CACHE_SYNC)
            
            # 6.1. Проверяем и обновляем кеш
            if result.file_paths:
                missing_in_cache, _, _ = self.cache_verifier.verify_sync()
                
                for path in result.file_paths:
                    if path in missing_in_cache:
                        result.add_info(f"Файл {path} добавлен в кеш")
            
            # 7. Завершение процесса
            result.set_stage(ProcessStage.COMPLETE)
            result.success = True
            
            return result
        
        except Exception as e:
            # Логируем ошибку и возвращаем результат
            logger.error(f"Ошибка при обновлении элемента: {e}")
            traceback.print_exc()
            
            result.add_error(f"Неожиданная ошибка: {e}")
            return result
    
    def generate_progress_report(self, result: ProcessResult) -> Dict[str, Any]:
        """
        Генерирует отчет о прогрессе для функции report_progress.
        
        Args:
            result: Результат процесса
            
        Returns:
            Словарь с данными для отчета
        """
        # Форматируем сообщения для отчета
        messages = []
        
        # Добавляем информацию об элементе
        if result.item:
            item_type_str = {
                WorkItemType.TASK: "задача",
                WorkItemType.INCIDENT: "инцидент",
                WorkItemType.HYPOTHESIS: "гипотеза",
                WorkItemType.STANDARD: "стандарт"
            }.get(result.item.type, "элемент")
            
            status_str = {
                WorkItemStatus.BACKLOG: "в бэклоге",
                WorkItemStatus.TODO: "в планах",
                WorkItemStatus.IN_PROGRESS: "в работе",
                WorkItemStatus.DONE: "выполнено",
                WorkItemStatus.REVIEW: "на проверке",
                WorkItemStatus.BLOCKED: "заблокировано",
                WorkItemStatus.ARCHIVED: "в архиве"
            }.get(result.item.status, "")
            
            # Сообщение о создании или обновлении
            if result.process_log[0]["message"].startswith("Получен элемент"):
                messages.append(f"✓ Обновлен {item_type_str} {result.item.id}: {result.item.title}")
            else:
                messages.append(f"✓ Создан {item_type_str} {result.item.id}: {result.item.title} ({status_str})")
        
        # Добавляем информацию о файлах
        if result.file_paths:
            messages.append(f"✓ Обработаны файлы: {len(result.file_paths)}")
        
        # Добавляем информацию о связях
        if result.related_items:
            messages.append(f"✓ Установлены связи с другими элементами: {len(result.related_items)}")
        
        # Добавляем предупреждения
        if result.warnings:
            messages.append(f"→ Обратите внимание: {len(result.warnings)} предупреждений")
        
        # Добавляем ошибки
        if result.errors:
            messages.append(f"⚠ Ошибки: {len(result.errors)}")
            for error in result.errors[:2]:  # Показываем только первые 2 ошибки
                messages.append(f"  - {error}")
        
        # Добавляем информацию о похожих элементах
        if result.similar_items:
            messages.append(f"→ Найдены похожие элементы: {len(result.similar_items)}")
        
        return {
            "summary": "\n".join(messages)
        }


# Глобальный экземпляр процессора
_PROCESSOR = None

def get_processor() -> WorkItemProcessor:
    """
    Получает глобальный экземпляр процессора.
    
    Returns:
        Экземпляр WorkItemProcessor
    """
    global _PROCESSOR
    
    if _PROCESSOR is None:
        _PROCESSOR = WorkItemProcessor()
    
    return _PROCESSOR


# Функции интерфейса командной строки

def create_task_cli():
    """JTBD:
Я (разработчик) хочу создать task_cli, чтобы добавить новый объект в систему и использовать его функциональность.
     
     Создает задачу через интерфейс командной строки."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Создание новой задачи")
    parser.add_argument("--title", required=True, help="Заголовок задачи")
    parser.add_argument("--description", required=True, help="Описание задачи")
    parser.add_argument("--author", help="Автор задачи")
    parser.add_argument("--assignee", help="Ответственный за задачу")
    parser.add_argument("--file", help="Путь к файлу с описанием задачи")
    
    args = parser.parse_args()
    
    processor = get_processor()
    result = processor.create_task(
        title=args.title,
        description=args.description,
        author=args.author,
        assignee=args.assignee,
        file_path=args.file
    )
    
    if result.success:
        print(f"Задача {result.item.id} успешно создана: {result.item.title}")
    else:
        print("Ошибка при создании задачи:")
        for error in result.errors:
            print(f"- {error}")


def create_incident_cli():
    """JTBD:
Я (разработчик) хочу создать incident_cli, чтобы добавить новый объект в систему и использовать его функциональность.
     
     Создает инцидент через интерфейс командной строки."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Создание нового инцидента")
    parser.add_argument("--title", required=True, help="Заголовок инцидента")
    parser.add_argument("--description", required=True, help="Описание инцидента")
    parser.add_argument("--author", help="Автор инцидента")
    parser.add_argument("--assignee", help="Ответственный за инцидент")
    parser.add_argument("--file", help="Путь к файлу с описанием инцидента")
    
    args = parser.parse_args()
    
    processor = get_processor()
    result = processor.create_incident(
        title=args.title,
        description=args.description,
        author=args.author,
        assignee=args.assignee,
        file_path=args.file
    )
    
    if result.success:
        print(f"Инцидент {result.item.id} успешно создан: {result.item.title}")
    else:
        print("Ошибка при создании инцидента:")
        for error in result.errors:
            print(f"- {error}")


def create_standard_cli():
    """JTBD:
Я (разработчик) хочу создать standard_cli, чтобы добавить новый объект в систему и использовать его функциональность.
     
     Создает стандарт через интерфейс командной строки."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Создание нового стандарта")
    parser.add_argument("--title", required=True, help="Заголовок стандарта")
    parser.add_argument("--description", help="Описание стандарта")
    parser.add_argument("--author", help="Автор стандарта")
    parser.add_argument("--file", help="Путь к файлу стандарта")
    parser.add_argument("--type", choices=["basic", "process", "code", "design"], 
                       default="basic", help="Тип стандарта")
    
    args = parser.parse_args()
    
    processor = get_processor()
    result = processor.create_standard(
        title=args.title,
        description=args.description,
        author=args.author,
        file_path=args.file,
        standard_type=args.type
    )
    
    if result.success:
        print(f"Стандарт {result.item.id} успешно создан: {result.item.title}")
    else:
        print("Ошибка при создании стандарта:")
        for error in result.errors:
            print(f"- {error}")


def update_work_item_cli():
    """JTBD:
Я (разработчик) хочу обновить work_item_cli, чтобы отразить изменения в состоянии системы и поддерживать актуальность данных.
     
     Обновляет рабочий элемент через интерфейс командной строки."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Обновление рабочего элемента")
    parser.add_argument("--id", required=True, help="Идентификатор элемента")
    parser.add_argument("--title", help="Новый заголовок")
    parser.add_argument("--description", help="Новое описание")
    parser.add_argument("--status", choices=[s.value for s in WorkItemStatus], help="Новый статус")
    parser.add_argument("--assignee", help="Новый ответственный")
    parser.add_argument("--file", help="Новый путь к файлу")
    
    args = parser.parse_args()
    
    processor = get_processor()
    result = processor.update_work_item(
        item_id=args.id,
        title=args.title,
        description=args.description,
        status=WorkItemStatus(args.status) if args.status else None,
        assignee=args.assignee,
        file_path=args.file
    )
    
    if result.success:
        print(f"Элемент {result.item.id} успешно обновлен")
    else:
        print("Ошибка при обновлении элемента:")
        for error in result.errors:
            print(f"- {error}")


def main():
    """JTBD:
Я (разработчик) хочу использовать функцию main, чтобы эффективно выполнить соответствующую операцию.
     
     Основная функция модуля."""
    import sys
    
    if len(sys.argv) < 2:
        print("Использование: python work_item_processor.py <команда>")
        print("Команды:")
        print("  create_task - создать задачу")
        print("  create_incident - создать инцидент")
        print("  create_standard - создать стандарт")
        print("  update - обновить элемент")
        return
    
    command = sys.argv[1]
    sys.argv = [sys.argv[0]] + sys.argv[2:]
    
    if command == "create_task":
        create_task_cli()
    elif command == "create_incident":
        create_incident_cli()
    elif command == "create_standard":
        create_standard_cli()
    elif command == "update":
        update_work_item_cli()
    else:
        print(f"Неизвестная команда: {command}")


if __name__ == "__main__":
    main()