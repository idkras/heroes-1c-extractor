"""
Модуль для управления инцидентами в соответствии со стандартом инцидентов.

Реализует централизованное управление инцидентами, обеспечивая их создание,
обновление, архивацию и миграцию согласно актуальному стандарту.
"""

import os
import re
import shutil
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple

from advising_platform.standards.core.traceable import implements_standard

# Настройка логирования
logger = logging.getLogger(__name__)

# Константы
INCIDENTS_DIR = "[todo · incidents]"
MAIN_INCIDENT_FILE = os.path.join(INCIDENTS_DIR, "ai.incidents.md")
ARCHIVE_DIR = os.path.join(INCIDENTS_DIR, "archive")
INDIVIDUAL_INCIDENTS_DIR = os.path.join(INCIDENTS_DIR, "ai.incidents")

# Шаблоны регулярных выражений
RE_INCIDENT_HEADER = r"###\s+(\d{1,2}\s+[A-Za-z]+\s+\d{4})\s+-\s+(.+?)\s*$"
RE_INCIDENT_METADATA = r"\*\*идентификатор\*\*:\s+(.+?)\s*\n\s*\*\*status\*\*:\s+(.+?)\s*\n\s*\*\*severity\*\*:\s+(.+?)\s*\n\s*\*\*category\*\*:\s+(.+?)\s*\n"
RE_FILE_HEADER = r"(#\s+🚨.+?##\s+📅\s+[A-Za-z]+\s+\d{4}\s*\n)"
RE_ARCHIVE_SECTION = r"(---\s*\n\s*##\s+📋\s+Архив\s+инцидентов.*?)$"


@implements_standard("incident", "1.9", "storage")
class IncidentStorage:
    """Хранилище инцидентов в соответствии со стандартом Incident v1.9."""
    
    _instance = None
    
    def __new__(cls):
        """Создает синглтон для управления инцидентами."""
        if cls._instance is None:
            cls._instance = super(IncidentStorage, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Инициализирует менеджер инцидентов."""
        if getattr(self, '_initialized', False):
            return
        
        self._incidents_cache = []
        self._cache_loaded = False
        self._initialized = True
        logger.info("Инициализирован менеджер инцидентов")
    
    def _ensure_main_file_exists(self) -> None:
        """Проверяет существование основного файла инцидентов и создает его при необходимости."""
        if not os.path.exists(MAIN_INCIDENT_FILE):
            # Создаем директорию при необходимости
            if not os.path.exists(INCIDENTS_DIR):
                os.makedirs(INCIDENTS_DIR)
            
            # Создаем основной файл инцидентов с шаблоном
            current_date = datetime.now().strftime("%d %B %Y")
            current_month = datetime.now().strftime("%B %Y")
            
            template = f"""# 🚨 AI Инциденты и анализ корневых причин

updated: {current_date}, {datetime.now().strftime("%H:%M")} CET by AI Assistant  
previous: None  
based on: [AI Incident Standard](abstract://standard:ai_incident), версия 1.9, 15 May 2025  
integrated: [Protocol Challenge](abstract://standard:protocol_challenge), [5 Why Analysis](abstract://standard:5why_analysis)  
status: Active  
description: Единый документ для хранения всех AI инцидентов согласно AI Incident Standard

## 📅 {current_month}


---

## 📋 Архив инцидентов

> Архивные инциденты перемещены в [todo · incidents]/archive/
"""
            with open(MAIN_INCIDENT_FILE, 'w', encoding='utf-8') as f:
                f.write(template)
            
            logger.info(f"Создан основной файл инцидентов: {MAIN_INCIDENT_FILE}")
    
    def _atomic_file_operation(self, file_path: str, operation_func) -> Any:
        """
        Выполняет операцию с файлом атомарно, с созданием резервной копии.
        
        Args:
            file_path: Путь к файлу
            operation_func: Функция, которая будет вызвана с временным файлом
        
        Returns:
            Результат выполнения operation_func
        """
        backup_path = file_path + ".bak"
        temp_path = file_path + ".tmp"
        
        # Обеспечиваем существование файла
        self._ensure_main_file_exists()
        
        # Создаем резервную копию
        shutil.copy2(file_path, backup_path)
        
        try:
            # Выполняем операцию с временным файлом
            result = operation_func(temp_path)
            
            # Атомарно заменяем оригинальный файл
            os.replace(temp_path, file_path)
            return result
        except Exception as e:
            logger.error(f"Ошибка при выполнении атомарной операции с файлом: {e}")
            # В случае ошибки восстанавливаем из резервной копии
            if os.path.exists(temp_path):
                os.remove(temp_path)
            os.replace(backup_path, file_path)
            raise e
        finally:
            # Удаляем резервную копию, если все прошло успешно
            if os.path.exists(backup_path):
                os.remove(backup_path)
    
    def _load_incidents_from_file(self) -> List[Dict[str, Any]]:
        """
        Загружает все инциденты из основного файла.
        
        Returns:
            Список инцидентов с их метаданными
        """
        self._ensure_main_file_exists()
        
        incidents = []
        
        try:
            with open(MAIN_INCIDENT_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Извлекаем все инциденты с метаданными
            matches = re.finditer(RE_INCIDENT_HEADER, content, re.MULTILINE)
            for match in matches:
                date_str = match.group(1)
                title = match.group(2)
                
                # Определяем позицию начала и конца инцидента
                start_pos = match.start()
                
                # Ищем следующий заголовок инцидента или секцию архива
                next_incident = re.search(RE_INCIDENT_HEADER, content[start_pos + 1:])
                archive_section = re.search(RE_ARCHIVE_SECTION, content[start_pos:])
                
                if next_incident:
                    end_pos = start_pos + 1 + next_incident.start()
                elif archive_section:
                    end_pos = start_pos + archive_section.start()
                else:
                    end_pos = len(content)
                
                # Извлекаем полное содержимое инцидента
                incident_content = content[start_pos:end_pos].strip()
                
                # Извлекаем метаданные
                metadata_match = re.search(RE_INCIDENT_METADATA, incident_content)
                if metadata_match:
                    incident_id = metadata_match.group(1).strip()
                    status = metadata_match.group(2).strip()
                    severity = metadata_match.group(3).strip()
                    category = metadata_match.group(4).strip()
                else:
                    incident_id = f"incident_{date_str.replace(' ', '_').lower()}"
                    status = "open"
                    severity = "medium"
                    category = "uncategorized"
                
                # Формируем структуру инцидента
                incident = {
                    "id": incident_id,
                    "date": date_str,
                    "title": title,
                    "status": status,
                    "severity": severity,
                    "category": category,
                    "content": incident_content,
                    "position": start_pos
                }
                
                incidents.append(incident)
            
            logger.info(f"Загружено {len(incidents)} инцидентов из основного файла")
            return incidents
        
        except Exception as e:
            logger.error(f"Ошибка при загрузке инцидентов из файла: {e}")
            return []
    
    @implements_standard("incident", "1.9", "retrieval")
    def get_incidents(self, reload: bool = False) -> List[Dict[str, Any]]:
        """
        Возвращает список всех инцидентов.
        
        Args:
            reload: Принудительно перезагрузить инциденты из файла
        
        Returns:
            Список инцидентов с их метаданными
        """
        if not self._cache_loaded or reload:
            self._incidents_cache = self._load_incidents_from_file()
            self._cache_loaded = True
        
        return self._incidents_cache
    
    @implements_standard("incident", "1.9", "retrieval_by_id")
    def get_incident_by_id(self, incident_id: str, reload: bool = False) -> Optional[Dict[str, Any]]:
        """
        Находит инцидент по его идентификатору.
        
        Args:
            incident_id: Идентификатор инцидента
            reload: Принудительно перезагрузить инциденты из файла
        
        Returns:
            Информация об инциденте или None, если инцидент не найден
        """
        incidents = self.get_incidents(reload)
        
        for incident in incidents:
            if incident["id"] == incident_id:
                return incident
        
        return None
    
    def format_incident(self, incident_data: Dict[str, Any]) -> str:
        """
        Форматирует данные инцидента в текстовое представление для записи в файл.
        
        Args:
            incident_data: Данные инцидента
        
        Returns:
            Отформатированное текстовое представление инцидента
        """
        # Обязательные поля
        date = incident_data.get("date", datetime.now().strftime("%d %b %Y"))
        title = incident_data.get("title", "Инцидент без заголовка")
        incident_id = incident_data.get("id", f"incident_{date.replace(' ', '_').lower()}")
        status = incident_data.get("status", "open")
        severity = incident_data.get("severity", "medium")
        category = incident_data.get("category", "system architecture")
        content = incident_data.get("content", "")
        
        # Если передано только содержимое без метаданных, форматируем стандартный заголовок
        if "metadata_formatted" not in incident_data and not content.startswith("### "):
            formatted = f"""### {date} - {title}

**идентификатор**: {incident_id}  
**status**: {status} · @ai assistant  
**severity**: {severity}  
**category**: {category}

{content}"""
        else:
            formatted = content
        
        return formatted
    
    @implements_standard("incident", "1.9", "creation")
    def add_incident(self, incident_data: Dict[str, Any]) -> str:
        """
        Добавляет новый инцидент в основной файл.
        
        Args:
            incident_data: Данные инцидента
        
        Returns:
            Идентификатор созданного инцидента
        """
        self._ensure_main_file_exists()
        
        # Форматируем инцидент
        formatted_incident = self.format_incident(incident_data)
        
        # Определяем идентификатор инцидента
        incident_id = incident_data.get("id", "")
        if not incident_id:
            # Извлекаем идентификатор из форматированного инцидента
            metadata_match = re.search(RE_INCIDENT_METADATA, formatted_incident)
            if metadata_match:
                incident_id = metadata_match.group(1).strip()
            else:
                # Генерируем идентификатор на основе даты и времени
                now = datetime.now()
                incident_id = f"incident_{now.strftime('%Y%m%d_%H%M')}"
        
        # Определяем операцию для атомарного выполнения
        def _add_incident_operation(temp_path: str) -> str:
            with open(MAIN_INCIDENT_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Находим позицию для вставки (после заголовка и перед первым инцидентом)
            header_match = re.search(RE_FILE_HEADER, content, re.DOTALL)
            if header_match:
                insert_position = header_match.end()
                
                # Собираем новое содержимое
                new_content = (
                    content[:insert_position] +
                    formatted_incident +
                    "\n\n" +
                    content[insert_position:]
                )
                
                # Записываем во временный файл
                with open(temp_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                return incident_id
            else:
                raise ValueError("Не удалось найти заголовок в файле инцидентов")
        
        # Выполняем операцию атомарно
        result = self._atomic_file_operation(MAIN_INCIDENT_FILE, _add_incident_operation)
        
        # Инвалидируем кэш, чтобы при следующем запросе инциденты были перезагружены
        self._cache_loaded = False
        
        logger.info(f"Добавлен новый инцидент: {incident_id}")
        return result
    
    @implements_standard("incident", "1.9", "status_update")
    def update_incident_status(self, incident_id: str, new_status: str, assignee: Optional[str] = None) -> bool:
        """
        Обновляет статус указанного инцидента.
        
        Args:
            incident_id: Идентификатор инцидента
            new_status: Новый статус инцидента
            assignee: Ответственный за инцидент (если нужно изменить)
        
        Returns:
            True, если обновление прошло успешно, иначе False
        """
        # Получаем информацию об инциденте
        incident = self.get_incident_by_id(incident_id, reload=True)
        if not incident:
            logger.warning(f"Инцидент не найден: {incident_id}")
            return False
        
        # Определяем операцию для атомарного выполнения
        def _update_status_operation(temp_path: str) -> bool:
            with open(MAIN_INCIDENT_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Формируем шаблон для замены статуса
            status_pattern = fr'\*\*status\*\*:\s+{re.escape(incident["status"])}'
            
            # Формируем новый статус с возможным ответственным
            if assignee:
                new_status_text = f"**status**: {new_status} · @{assignee}"
            else:
                # Сохраняем существующего ответственного
                assignee_match = re.search(r'\*\*status\*\*:\s+\w+\s+·\s+@(\w+)', incident["content"])
                if assignee_match:
                    existing_assignee = assignee_match.group(1)
                    new_status_text = f"**status**: {new_status} · @{existing_assignee}"
                else:
                    new_status_text = f"**status**: {new_status}"
            
            # Выполняем замену
            new_content = re.sub(status_pattern, new_status_text, content)
            
            # Если содержимое не изменилось, значит шаблон не найден
            if new_content == content:
                logger.warning(f"Не удалось найти шаблон для замены статуса инцидента: {incident_id}")
                return False
            
            # Записываем во временный файл
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
        
        # Выполняем операцию атомарно
        try:
            result = self._atomic_file_operation(MAIN_INCIDENT_FILE, _update_status_operation)
            
            # Инвалидируем кэш, чтобы при следующем запросе инциденты были перезагружены
            self._cache_loaded = False
            
            logger.info(f"Обновлен статус инцидента {incident_id}: {incident['status']} -> {new_status}")
            return result
        except Exception as e:
            logger.error(f"Ошибка при обновлении статуса инцидента {incident_id}: {e}")
            return False
    
    @implements_standard("incident", "1.9", "archiving")
    def archive_incident(self, incident_id: str) -> bool:
        """
        Перемещает инцидент в архив.
        
        Args:
            incident_id: Идентификатор инцидента
        
        Returns:
            True, если архивация прошла успешно, иначе False
        """
        # Получаем информацию об инциденте
        incident = self.get_incident_by_id(incident_id, reload=True)
        if not incident:
            logger.warning(f"Инцидент не найден: {incident_id}")
            return False
        
        # Создаем директорию архива при необходимости
        today = datetime.now().strftime("%Y%m%d")
        archive_date_dir = os.path.join(ARCHIVE_DIR, today)
        if not os.path.exists(archive_date_dir):
            os.makedirs(archive_date_dir, exist_ok=True)
        
        # Имя файла для архивации
        archive_file_name = f"{incident_id}.md"
        archive_file_path = os.path.join(archive_date_dir, archive_file_name)
        
        # Определяем операцию для атомарного выполнения
        def _archive_operation(temp_path: str) -> bool:
            with open(MAIN_INCIDENT_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Записываем инцидент в архивный файл
            with open(archive_file_path, 'w', encoding='utf-8') as f:
                f.write(incident["content"])
            
            # Удаляем инцидент из основного файла
            new_content = content.replace(incident["content"], "").replace("\n\n\n", "\n\n")
            
            # Записываем во временный файл
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
        
        # Выполняем операцию атомарно
        try:
            result = self._atomic_file_operation(MAIN_INCIDENT_FILE, _archive_operation)
            
            # Инвалидируем кэш, чтобы при следующем запросе инциденты были перезагружены
            self._cache_loaded = False
            
            logger.info(f"Инцидент {incident_id} архивирован в {archive_file_path}")
            return result
        except Exception as e:
            logger.error(f"Ошибка при архивации инцидента {incident_id}: {e}")
            return False
    
    @implements_standard("incident", "1.9", "migration")
    def create_incident_from_file(self, file_path: str) -> Optional[str]:
        """
        Создает инцидент в основном файле на основе содержимого отдельного файла.
        
        Args:
            file_path: Путь к файлу инцидента
        
        Returns:
            Идентификатор созданного инцидента или None в случае ошибки
        """
        try:
            # Проверяем существование файла
            if not os.path.exists(file_path):
                logger.warning(f"Файл не найден: {file_path}")
                return None
            
            # Читаем содержимое файла
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Извлекаем заголовок (первую строку)
            title_match = re.match(r'#\s+(.+)', content)
            if title_match:
                title = title_match.group(1)
            else:
                title = "Инцидент без заголовка"
            
            # Извлекаем дату создания
            date_match = re.search(r'\*\*Время обнаружения:\*\*\s+(\d{4}-\d{2}-\d{2})', content)
            if date_match:
                date_str = date_match.group(1)
                try:
                    date = datetime.strptime(date_str, '%Y-%m-%d')
                    formatted_date = date.strftime('%d %b %Y')
                except ValueError:
                    formatted_date = datetime.now().strftime('%d %b %Y')
            else:
                formatted_date = datetime.now().strftime('%d %b %Y')
            
            # Формируем идентификатор на основе имени файла
            file_name = os.path.basename(file_path)
            incident_id = file_name.replace('.md', '').lower()
            
            # Формируем данные инцидента
            incident_data = {
                "id": incident_id,
                "title": title,
                "date": formatted_date,
                "content": content,
                "status": "open",
                "severity": "medium",
                "category": "system architecture"
            }
            
            # Добавляем инцидент в основной файл
            return self.add_incident(incident_data)
        
        except Exception as e:
            logger.error(f"Ошибка при создании инцидента из файла {file_path}: {e}")
            return None
    
    @implements_standard("incident", "1.9", "migration")
    def migrate_individual_incidents(self) -> Tuple[int, int]:
        """
        Мигрирует отдельные файлы инцидентов в основной файл.
        
        Returns:
            Кортеж (успешно_мигрировано, всего_файлов)
        """
        # Создаем архивную директорию при необходимости
        today = datetime.now().strftime("%Y%m%d")
        archive_date_dir = os.path.join(ARCHIVE_DIR, today)
        if not os.path.exists(archive_date_dir):
            os.makedirs(archive_date_dir, exist_ok=True)
        
        # Получаем список файлов в директории индивидуальных инцидентов
        if not os.path.exists(INDIVIDUAL_INCIDENTS_DIR):
            logger.warning(f"Директория индивидуальных инцидентов не найдена: {INDIVIDUAL_INCIDENTS_DIR}")
            return 0, 0
        
        files = [f for f in os.listdir(INDIVIDUAL_INCIDENTS_DIR) if f.endswith('.md')]
        total_files = len(files)
        
        if total_files == 0:
            logger.info("Нет индивидуальных файлов инцидентов для миграции")
            return 0, 0
        
        # Мигрируем каждый файл
        success_count = 0
        for file_name in files:
            file_path = os.path.join(INDIVIDUAL_INCIDENTS_DIR, file_name)
            
            # Создаем инцидент в основном файле
            incident_id = self.create_incident_from_file(file_path)
            
            if incident_id:
                # Перемещаем файл в архив
                archive_path = os.path.join(archive_date_dir, file_name)
                shutil.copy2(file_path, archive_path)
                success_count += 1
                logger.info(f"Успешно мигрирован инцидент: {file_name}")
            else:
                logger.warning(f"Не удалось мигрировать инцидент: {file_name}")
        
        logger.info(f"Миграция завершена: {success_count}/{total_files} файлов успешно мигрировано")
        return success_count, total_files


# Создаем глобальный экземпляр для удобного импорта
incident_storage = IncidentStorage()


# Функции-хелперы для работы с инцидентами
@implements_standard("incident", "1.9", "creation")
def create_incident(title: str, content: str, severity: str = "medium", category: str = "system architecture") -> str:
    """
    Создает новый инцидент в основном файле.
    
    Args:
        title: Заголовок инцидента
        content: Содержимое инцидента
        severity: Серьезность инцидента (critical, high, medium, low)
        category: Категория инцидента
    
    Returns:
        Идентификатор созданного инцидента
    """
    # Генерируем идентификатор на основе заголовка и времени
    now = datetime.now()
    incident_id = f"incident_{re.sub(r'[^a-z0-9]', '_', title.lower())}_{now.strftime('%Y%m%d_%H%M')}"
    
    # Форматируем дату
    date = now.strftime('%d %b %Y')
    
    # Формируем данные инцидента
    incident_data = {
        "id": incident_id,
        "title": title,
        "date": date,
        "content": content,
        "status": "open",
        "severity": severity,
        "category": category
    }
    
    # Добавляем инцидент в основной файл
    return incident_storage.add_incident(incident_data)


@implements_standard("incident", "1.9", "status_update")
def update_incident_status(incident_id: str, new_status: str) -> bool:
    """
    Обновляет статус указанного инцидента.
    
    Args:
        incident_id: Идентификатор инцидента
        new_status: Новый статус инцидента
    
    Returns:
        True, если обновление прошло успешно, иначе False
    """
    return incident_storage.update_incident_status(incident_id, new_status)


@implements_standard("incident", "1.9", "archiving")
def archive_incident(incident_id: str) -> bool:
    """
    Перемещает инцидент в архив.
    
    Args:
        incident_id: Идентификатор инцидента
    
    Returns:
        True, если архивация прошла успешно, иначе False
    """
    return incident_storage.archive_incident(incident_id)


@implements_standard("incident", "1.9", "migration")
def migrate_incidents() -> Tuple[int, int]:
    """
    Мигрирует отдельные файлы инцидентов в основной файл.
    
    Returns:
        Кортеж (успешно_мигрировано, всего_файлов)
    """
    return incident_storage.migrate_individual_incidents()


if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Пример использования
    incidents = incident_storage.get_incidents()
    print(f"Найдено {len(incidents)} инцидентов в основном файле")
    
    # Миграция индивидуальных инцидентов
    success, total = migrate_incidents()
    print(f"Мигрировано {success} из {total} индивидуальных инцидентов")