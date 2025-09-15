"""
Модуль рабочего процесса синхронизации документов.

Обеспечивает надежный рабочий процесс для работы с документами, включая:
1. Проверку соответствия между кешем и файловой системой
2. Архивацию задач и обновление статистики
3. Предотвращение создания дублей
4. Поддержание синхронизации при выполнении операций

Автор: AI Assistant
Дата: 20 мая 2025
"""

import os
import time
import logging
import hashlib
from typing import Dict, Tuple, Any, Optional, List, Union
from pathlib import Path
from datetime import datetime

# Настройка логирования
logger = logging.getLogger("doc_sync_workflow")
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Константы
CACHE_STATE_PATH = ".cache_state.json"
TASK_STATS_PATH = ".task_stats.json"
TODO_PATH = "todo.md"
INCIDENTS_DIR = "[todo · incidents]/ai.incidents"
ARCHIVES_DIR = "archive"

class DocumentSyncWorkflow:
    """
    Класс, реализующий рабочий процесс синхронизации документов.
    Обеспечивает надежную работу с документами, проверку целостности и предотвращение дублей.
    """
    
    def __init__(self):
        """Инициализация рабочего процесса синхронизации."""
        # Проверяем наличие необходимых директорий
        self._ensure_directories_exist()
        
        # Импортируем зависимости динамически для предотвращения циклических импортов
        try:
            from advising_platform.content_deduplication import (
                DocumentRegistry, 
                verify_content_uniqueness,
                generate_content_hash
            )
            from advising_platform.src.core.cache_sync.cache_sync_verifier import CacheSyncVerifier
            
            self.DocumentRegistry = DocumentRegistry
            self.verify_content_uniqueness = verify_content_uniqueness
            self.generate_content_hash = generate_content_hash
            self.CacheSyncVerifier = CacheSyncVerifier
            
            self.has_deduplication = True
            
        except ImportError as e:
            logger.warning(f"Не удалось импортировать модули дедупликации: {str(e)}")
            self.has_deduplication = False
        
        try:
            from advising_platform.sync_verification import verify_file_sync
            self.verify_file_sync = verify_file_sync
            self.has_sync_verification = True
        except ImportError as e:
            logger.warning(f"Не удалось импортировать модуль верификации синхронизации: {str(e)}")
            self.has_sync_verification = False
        
        # Проверяем соответствие кеша и файловой системы при запуске
        self._verify_cache_filesystem_consistency()
    
    def _ensure_directories_exist(self):
        """Проверяет наличие необходимых директорий и создает их при необходимости."""
        os.makedirs(INCIDENTS_DIR, exist_ok=True)
        os.makedirs(ARCHIVES_DIR, exist_ok=True)
        os.makedirs(os.path.join(ARCHIVES_DIR, "tasks"), exist_ok=True)
        os.makedirs(os.path.join(ARCHIVES_DIR, "incidents"), exist_ok=True)
    
    def _verify_cache_filesystem_consistency(self) -> bool:
        """
        Проверяет соответствие между кешем и файловой системой.
        
        Returns:
            bool: True, если кеш и файловая система синхронизированы, иначе False
        """
        if not self.has_sync_verification:
            logger.warning("Модуль верификации синхронизации недоступен, проверка пропущена")
            return False
        
        try:
            # Инициализируем верификатор
            verifier = self.CacheSyncVerifier()
            
            # Получаем список проблемных файлов
            missing_in_cache, missing_in_fs, size_mismatches = verifier.verify_sync()
            
            if not (missing_in_cache or missing_in_fs or size_mismatches):
                logger.info("Кеш и файловая система полностью синхронизированы")
                return True
            
            # Логируем проблемы
            if missing_in_cache:
                logger.warning(f"Найдено {len(missing_in_cache)} файлов, отсутствующих в кеше")
            
            if missing_in_fs:
                logger.warning(f"Найдено {len(missing_in_fs)} записей в кеше для отсутствующих файлов")
            
            if size_mismatches:
                logger.warning(f"Найдено {len(size_mismatches)} файлов с несоответствием размера")
            
            # Пытаемся исправить проблемы
            if verifier.fix_sync_issues():
                logger.info("Проблемы синхронизации успешно исправлены")
                return True
            else:
                logger.error("Не удалось исправить проблемы синхронизации")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка при проверке соответствия кеша и файловой системы: {str(e)}")
            return False
    
    def before_document_operation(self, file_path: str) -> bool:
        """
        Выполняет подготовительные проверки перед операцией с документом.
        
        Args:
            file_path: Путь к документу
            
        Returns:
            bool: True, если предварительные проверки пройдены успешно, иначе False
        """
        # Проверяем существование файла (для операций чтения и обновления)
        if os.path.exists(file_path):
            # Проверяем синхронизацию с кешем
            if self.has_sync_verification:
                success, result = self.verify_file_sync(file_path)
                
                if not success:
                    logger.warning(f"Файл {file_path} не синхронизирован с кешем: {result}")
                    return False
        
        return True
    
    def after_document_operation(self, file_path: str, operation_type: str) -> bool:
        """
        Выполняет проверки после операции с документом.
        
        Args:
            file_path: Путь к документу
            operation_type: Тип операции (create, update, delete)
            
        Returns:
            bool: True, если проверки после операции пройдены успешно, иначе False
        """
        # Проверяем существование файла (для операций создания и обновления)
        if operation_type in ["create", "update"] and not os.path.exists(file_path):
            logger.error(f"Файл {file_path} не существует после операции {operation_type}")
            return False
        
        # Проверяем синхронизацию с кешем
        if self.has_sync_verification and operation_type != "delete":
            start_time = time.time()
            max_wait_time = 5  # Максимальное время ожидания в секундах
            
            while time.time() - start_time < max_wait_time:
                success, result = self.verify_file_sync(file_path)
                
                if success:
                    break
                
                # Ждем немного для процесса синхронизации
                time.sleep(0.5)
            
            if not success:
                logger.warning(f"Файл {file_path} не синхронизирован с кешем после операции {operation_type}: {result}")
                return False
        
        # Для операции удаления проверяем, что файл отсутствует
        if operation_type == "delete" and os.path.exists(file_path):
            logger.error(f"Файл {file_path} все еще существует после операции удаления")
            return False
        
        # Обновляем статистику для задач и инцидентов
        if operation_type in ["create", "update", "archive"] and (
            file_path.endswith(".md") and 
            ("todo" in file_path.lower() or "incident" in file_path.lower())
        ):
            self._update_task_stats()
        
        return True
    
    def check_duplicate_content(self, content: str, document_type: str) -> Tuple[bool, str]:
        """
        Проверяет содержимое на дубликаты.
        
        Args:
            content: Содержимое документа
            document_type: Тип документа (task, incident, standard, etc.)
            
        Returns:
            Tuple[bool, str]: (is_unique, message)
                is_unique - True, если содержимое уникально, иначе False
                message - Сообщение с результатом проверки или путь к дубликату
        """
        if not self.has_deduplication:
            logger.warning("Модуль дедупликации недоступен, проверка на дубликаты пропущена")
            return True, "Проверка на дубликаты недоступна"
        
        try:
            # Проверяем на уникальность
            is_unique, result = self.verify_content_uniqueness(content, document_type)
            
            if not is_unique:
                logger.info(f"Обнаружен дубликат для {document_type}: {result}")
                return False, result
            
            return True, "Содержимое уникально"
            
        except Exception as e:
            logger.error(f"Ошибка при проверке на дубликаты: {str(e)}")
            return True, f"Ошибка проверки: {str(e)}"
    
    def create_document(self, file_path: str, content: str, document_type: str) -> Tuple[bool, str]:
        """
        Создает новый документ с проверкой на дубликаты и синхронизацией.
        
        Args:
            file_path: Путь к файлу
            content: Содержимое документа
            document_type: Тип документа (task, incident, standard, etc.)
            
        Returns:
            Tuple[bool, str]: (success, message)
                success - True, если документ успешно создан, иначе False
                message - Сообщение с результатом операции
        """
        # Проверяем на дубликаты
        is_unique, result = self.check_duplicate_content(content, document_type)
        
        if not is_unique:
            return False, f"Обнаружен дубликат: {result}"
        
        # Создаем директорию, если не существует
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # Проверяем, не существует ли файл уже
        if os.path.exists(file_path):
            return False, f"Файл {file_path} уже существует"
        
        try:
            # Выполняем предварительные проверки
            if not self.before_document_operation(file_path):
                return False, "Предварительные проверки не пройдены"
            
            # Создаем файл
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Выполняем проверки после операции
            if not self.after_document_operation(file_path, "create"):
                return False, "Проверки после создания не пройдены"
            
            # Регистрируем документ в реестре, если доступен модуль дедупликации
            if self.has_deduplication:
                # Извлекаем метаданные из контента в зависимости от типа документа
                try:
                    from advising_platform.content_deduplication import (
                        extract_metadata_from_task,
                        extract_metadata_from_incident,
                        extract_metadata_from_standard
                    )
                    
                    metadata = None
                    if document_type == "task":
                        metadata = extract_metadata_from_task(content)
                    elif document_type == "incident":
                        metadata = extract_metadata_from_incident(content)
                    elif document_type == "standard":
                        metadata = extract_metadata_from_standard(content)
                    
                    if metadata:
                        content_hash = self.generate_content_hash(content)
                        self.DocumentRegistry.register_document(file_path, document_type, metadata, content_hash)
                except Exception as e:
                    logger.warning(f"Не удалось зарегистрировать документ в реестре: {str(e)}")
            
            return True, f"Документ {file_path} успешно создан"
            
        except Exception as e:
            logger.error(f"Ошибка при создании документа {file_path}: {str(e)}")
            return False, str(e)
    
    def update_document(self, file_path: str, content: str, document_type: str) -> Tuple[bool, str]:
        """
        Обновляет существующий документ с проверкой на дубликаты и синхронизацией.
        
        Args:
            file_path: Путь к файлу
            content: Новое содержимое документа
            document_type: Тип документа (task, incident, standard, etc.)
            
        Returns:
            Tuple[bool, str]: (success, message)
                success - True, если документ успешно обновлен, иначе False
                message - Сообщение с результатом операции
        """
        # Проверяем существование файла
        if not os.path.exists(file_path):
            return False, f"Файл {file_path} не существует"
        
        # Проверяем на дубликаты, но только если это не тот же самый файл
        is_unique, result = self.check_duplicate_content(content, document_type)
        
        if not is_unique and result != file_path:
            return False, f"Обнаружен дубликат: {result}"
        
        try:
            # Выполняем предварительные проверки
            if not self.before_document_operation(file_path):
                return False, "Предварительные проверки не пройдены"
            
            # Создаем резервную копию для безопасности
            backup_path = f"{file_path}.bak"
            with open(file_path, 'r', encoding='utf-8') as src, open(backup_path, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
            
            # Обновляем файл
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Выполняем проверки после операции
            if not self.after_document_operation(file_path, "update"):
                # Восстанавливаем из резервной копии в случае ошибки
                if os.path.exists(backup_path):
                    os.replace(backup_path, file_path)
                return False, "Проверки после обновления не пройдены"
            
            # Удаляем резервную копию
            if os.path.exists(backup_path):
                os.remove(backup_path)
            
            # Обновляем запись в реестре, если доступен модуль дедупликации
            if self.has_deduplication:
                try:
                    from advising_platform.content_deduplication import (
                        extract_metadata_from_task,
                        extract_metadata_from_incident,
                        extract_metadata_from_standard
                    )
                    
                    metadata = None
                    if document_type == "task":
                        metadata = extract_metadata_from_task(content)
                    elif document_type == "incident":
                        metadata = extract_metadata_from_incident(content)
                    elif document_type == "standard":
                        metadata = extract_metadata_from_standard(content)
                    
                    if metadata:
                        content_hash = self.generate_content_hash(content)
                        self.DocumentRegistry.update_document(file_path, document_type, metadata, content_hash)
                except Exception as e:
                    logger.warning(f"Не удалось обновить документ в реестре: {str(e)}")
            
            return True, f"Документ {file_path} успешно обновлен"
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении документа {file_path}: {str(e)}")
            # Восстанавливаем из резервной копии в случае исключения
            backup_path = f"{file_path}.bak"
            if os.path.exists(backup_path):
                os.replace(backup_path, file_path)
            return False, str(e)
    
    def archive_document(self, file_path: str, document_type: str) -> Tuple[bool, str]:
        """
        Архивирует документ с проверкой синхронизации.
        
        Args:
            file_path: Путь к файлу
            document_type: Тип документа (task, incident, standard, etc.)
            
        Returns:
            Tuple[bool, str]: (success, message)
                success - True, если документ успешно архивирован, иначе False
                message - Сообщение с результатом операции
        """
        # Проверяем существование файла
        if not os.path.exists(file_path):
            return False, f"Файл {file_path} не существует"
        
        try:
            # Выполняем предварительные проверки
            if not self.before_document_operation(file_path):
                return False, "Предварительные проверки не пройдены"
            
            # Определяем путь в архиве
            archive_subdir = "tasks" if document_type == "task" else "incidents"
            file_name = os.path.basename(file_path)
            archive_path = os.path.join(ARCHIVES_DIR, archive_subdir, file_name)
            
            # Проверяем, не существует ли файл уже в архиве
            if os.path.exists(archive_path):
                # Добавляем временную метку к имени файла
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                name, ext = os.path.splitext(file_name)
                archive_path = os.path.join(ARCHIVES_DIR, archive_subdir, f"{name}_{timestamp}{ext}")
            
            # Перемещаем файл в архив
            os.replace(file_path, archive_path)
            
            # Выполняем проверки после операции
            if not self.after_document_operation(file_path, "archive"):
                return False, "Проверки после архивации не пройдены"
            
            # Обновляем реестр документов, если доступен модуль дедупликации
            if self.has_deduplication:
                try:
                    self.DocumentRegistry.mark_as_archived(file_path, archive_path)
                except Exception as e:
                    logger.warning(f"Не удалось обновить статус документа в реестре: {str(e)}")
            
            return True, f"Документ {file_path} успешно архивирован в {archive_path}"
            
        except Exception as e:
            logger.error(f"Ошибка при архивации документа {file_path}: {str(e)}")
            return False, str(e)
    
    def _update_task_stats(self) -> bool:
        """
        Обновляет статистику задач и инцидентов.
        
        Returns:
            bool: True, если статистика успешно обновлена, иначе False
        """
        try:
            # Проверяем наличие todo.md
            if not os.path.exists(TODO_PATH):
                logger.warning(f"Файл {TODO_PATH} не найден, статистика не обновлена")
                return False
            
            # Подсчитываем задачи
            with open(TODO_PATH, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Подсчитываем задачи по статусам
            total_tasks = content.count("- [ ]")
            completed_tasks = content.count("- [x]")
            
            # Подсчитываем инциденты
            incidents_count = 0
            resolved_incidents = 0
            
            if os.path.exists(INCIDENTS_DIR):
                for file_name in os.listdir(INCIDENTS_DIR):
                    if file_name.endswith(".md"):
                        incidents_count += 1
                        
                        # Проверяем, закрыт ли инцидент
                        incident_path = os.path.join(INCIDENTS_DIR, file_name)
                        with open(incident_path, 'r', encoding='utf-8') as f:
                            incident_content = f.read()
                            if "**Статус**: Закрыт" in incident_content or "**Статус**: Resolved" in incident_content:
                                resolved_incidents += 1
            
            # Подсчитываем архивированные задачи и инциденты
            archived_tasks = 0
            archived_incidents = 0
            
            if os.path.exists(os.path.join(ARCHIVES_DIR, "tasks")):
                archived_tasks = len([f for f in os.listdir(os.path.join(ARCHIVES_DIR, "tasks")) if f.endswith(".md")])
            
            if os.path.exists(os.path.join(ARCHIVES_DIR, "incidents")):
                archived_incidents = len([f for f in os.listdir(os.path.join(ARCHIVES_DIR, "incidents")) if f.endswith(".md")])
            
            # Формируем статистику
            stats = {
                "tasks": {
                    "total": total_tasks,
                    "active": total_tasks - completed_tasks,
                    "completed": completed_tasks,
                    "archived": archived_tasks,
                    "completion_rate": round(completed_tasks / total_tasks * 100, 2) if total_tasks > 0 else 0
                },
                "incidents": {
                    "total": incidents_count,
                    "active": incidents_count - resolved_incidents,
                    "resolved": resolved_incidents,
                    "archived": archived_incidents,
                    "resolution_rate": round(resolved_incidents / incidents_count * 100, 2) if incidents_count > 0 else 0
                },
                "last_updated": datetime.now().isoformat()
            }
            
            # Сохраняем статистику
            import json
            with open(TASK_STATS_PATH, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Статистика задач и инцидентов обновлена: {TASK_STATS_PATH}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении статистики задач и инцидентов: {str(e)}")
            return False


# Создаем экземпляр для использования в других модулях
document_workflow = DocumentSyncWorkflow()