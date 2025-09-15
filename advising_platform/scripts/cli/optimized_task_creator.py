"""
Оптимизированный скрипт для работы с задачами, инцидентами и стандартами.

Использует механизм белого списка директорий для ускорения синхронизации.

Автор: AI Assistant
Дата: 20 мая 2025
"""

import os
import sys
import time
import logging
from typing import Dict, Any, Optional, List

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("optimized_task_creator")

# Функция для фиктивного report_progress
def mock_report_progress(data: Dict[str, str]) -> None:
    """Имитирует функцию report_progress."""
    print("\n🔔 Report Progress вызван с данными:")
    print(f"  {data['summary']}")
    return None

def init_registry_with_whitelist():
    """
    Инициализирует реестр с белым списком директорий для ускорения синхронизации.
    
    Это значительно ускоряет проверку синхронизации, ограничивая ее только 
    важными директориями вместо всей файловой системы.
    """
    try:
        from advising_platform.src.core.registry.task_registry import get_registry
        from advising_platform.src.core.cache_sync.cache_sync_verifier import CacheSyncVerifier
        
        # Определяем белый список директорий
        whitelist_dirs = [
            "projects",
            "incidents",
            "[todo · incidents]",
            "[standards .md]"
        ]
        
        # Создаем строку с шаблонами для фильтрации
        include_patterns = [f"{dir}/**" for dir in whitelist_dirs]
        
        # Создаем верификатор кеша с фильтрами
        verifier = CacheSyncVerifier(
            cache_paths=[".cache_state.json"],
            base_dir=".",
            include_patterns=include_patterns,
            exclude_patterns=["**/.git/**", "**/__pycache__/**", "**/.cache/**"]
        )
        
        # Проверяем и исправляем синхронизацию
        start_time = time.time()
        logger.info("Начало оптимизированной синхронизации кеша (только важные директории)")
        
        missing_in_cache, missing_in_filesystem, metadata_mismatch = verifier.verify_sync()
        
        if missing_in_cache or missing_in_filesystem or metadata_mismatch:
            logger.info(
                f"Найдены несоответствия: "
                f"{len(missing_in_cache)} отсутствуют в кеше, "
                f"{len(missing_in_filesystem)} отсутствуют в файловой системе, "
                f"{len(metadata_mismatch)} имеют несоответствия метаданных"
            )
            
            success = verifier.fix_sync_issues()
            if success:
                logger.info("Все несоответствия успешно исправлены")
            else:
                logger.warning("Не все несоответствия удалось исправить")
        else:
            logger.info("Кеш полностью синхронизирован")
        
        end_time = time.time()
        logger.info(f"Синхронизация завершена за {end_time - start_time:.2f} секунд")
        
        # Получаем реестр (он уже создан и инициализирован)
        return get_registry()
    
    except Exception as e:
        logger.error(f"Ошибка при инициализации реестра: {e}")
        return None

def create_task(title: str, description: str, author: str = "AI Assistant", assignee: Optional[str] = None, file_path: Optional[str] = None):
    """
    Создает новую задачу в реестре.
    
    Args:
        title: Заголовок задачи
        description: Описание задачи
        author: Автор задачи
        assignee: Ответственный за задачу
        file_path: Путь к файлу задачи
    
    Returns:
        ID созданной задачи или None при ошибке
    """
    try:
        from advising_platform.src.core.registry.trigger_handler import create_task as create_task_trigger
        
        # Все задачи записываются в центральный файл todo.md
        file_path = "[todo · incidents]/todo.md"
        
        # Создаем задачу
        result = create_task_trigger(
            title=title,
            description=description,
            author=author,
            assignee=assignee,
            file_path=file_path,
            report_progress_func=mock_report_progress
        )
        
        if result and result.success and result.item:
            return result.item.id
        else:
            if result and result.errors:
                for error in result.errors:
                    logger.error(f"Ошибка при создании задачи: {error}")
            return None
    
    except Exception as e:
        logger.error(f"Ошибка при создании задачи: {e}")
        return None

def create_incident(title: str, description: str, author: str = "AI Assistant", assignee: Optional[str] = None, file_path: Optional[str] = None):
    """
    Создает новый инцидент в реестре.
    
    Args:
        title: Заголовок инцидента
        description: Описание инцидента
        author: Автор инцидента
        assignee: Ответственный за инцидент
        file_path: Путь к файлу инцидента
    
    Returns:
        ID созданного инцидента или None при ошибке
    """
    try:
        from advising_platform.src.core.registry.trigger_handler import create_incident as create_incident_trigger
        
        # Если путь не указан, генерируем стандартный
        if not file_path:
            incident_dir = "incidents"
            os.makedirs(incident_dir, exist_ok=True)
            
            # Создаем безопасное имя файла из заголовка
            safe_title = "".join(c if c.isalnum() else "_" for c in title.lower())
            file_path = f"{incident_dir}/{safe_title}.md"
        else:
            # Создаем директорию, если не существует
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # Создаем инцидент
        result = create_incident_trigger(
            title=title,
            description=description,
            author=author,
            assignee=assignee,
            file_path=file_path,
            report_progress_func=mock_report_progress
        )
        
        if result and result.success and result.item:
            return result.item.id
        else:
            if result and result.errors:
                for error in result.errors:
                    logger.error(f"Ошибка при создании инцидента: {error}")
            return None
    
    except Exception as e:
        logger.error(f"Ошибка при создании инцидента: {e}")
        return None

def create_standard(title: str, description: Optional[str] = None, author: str = "AI Assistant", file_path: Optional[str] = None, standard_type: str = "basic"):
    """
    Создает новый стандарт в реестре.
    
    Args:
        title: Заголовок стандарта
        description: Описание стандарта
        author: Автор стандарта
        file_path: Путь к файлу стандарта
        standard_type: Тип стандарта (basic, process, code, design)
    
    Returns:
        ID созданного стандарта или None при ошибке
    """
    try:
        from advising_platform.src.core.registry.trigger_handler import create_standard as create_standard_trigger
        
        # Создаем стандарт
        result = create_standard_trigger(
            title=title,
            description=description or f"Стандарт: {title}",
            author=author,
            file_path=file_path,
            standard_type=standard_type,
            report_progress_func=mock_report_progress
        )
        
        if result and result.success and result.item:
            return result.item.id
        else:
            if result and result.errors:
                for error in result.errors:
                    logger.error(f"Ошибка при создании стандарта: {error}")
            return None
    
    except Exception as e:
        logger.error(f"Ошибка при создании стандарта: {e}")
        return None

def establish_relation(source_id: str, target_id: str, relation_type: str = "relates_to", description: Optional[str] = None):
    """
    Устанавливает связь между двумя элементами.
    
    Args:
        source_id: ID исходного элемента
        target_id: ID целевого элемента
        relation_type: Тип связи
        description: Описание связи
    
    Returns:
        True если связь установлена, иначе False
    """
    try:
        from advising_platform.src.core.registry.task_registry import get_registry, WorkItemRelationType
        
        # Получаем реестр
        registry = get_registry()
        
        # Преобразуем тип связи в перечисление
        relation_type_enum = getattr(WorkItemRelationType, relation_type.upper(), WorkItemRelationType.RELATES_TO)
        
        # Устанавливаем связь
        success = registry.add_relation(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type_enum,
            description=description
        )
        
        if success:
            logger.info(f"Установлена связь {source_id} -> {target_id} ({relation_type})")
        else:
            logger.warning(f"Не удалось установить связь {source_id} -> {target_id}")
        
        return success
    
    except Exception as e:
        logger.error(f"Ошибка при установке связи: {e}")
        return False

def demo_create_elements():
    """Демонстрирует создание элементов и связей между ними."""
    print("🚀 Запуск демонстрации системы управления задачами и инцидентами...")
    
    # Инициализируем реестр с оптимизированной синхронизацией
    registry = init_registry_with_whitelist()
    if not registry:
        print("❌ Не удалось инициализировать реестр")
        return
    
    # Создаем задачу
    print("\n📋 Создание задачи...")
    task_id = create_task(
        title="Оптимизировать проверку целостности кеша",
        description="Разработать механизм для оптимизации проверки целостности кеша "
                   "путем использования белого списка директорий и исключения ненужных файлов."
    )
    
    if task_id:
        print(f"✅ Задача успешно создана: {task_id}")
    else:
        print("❌ Не удалось создать задачу")
    
    # Создаем инцидент
    print("\n🚨 Создание инцидента...")
    incident_id = create_incident(
        title="Длительная синхронизация кеша",
        description="При запуске скриптов наблюдается длительная синхронизация кеша, "
                    "которая может занимать несколько минут из-за проверки всех файлов "
                    "в системе, включая большие бинарные файлы и файлы в кеше."
    )
    
    if incident_id:
        print(f"✅ Инцидент успешно создан: {incident_id}")
    else:
        print("❌ Не удалось создать инцидент")
    
    # Создаем стандарт
    print("\n📚 Создание стандарта...")
    standard_id = create_standard(
        title="Стандарт оптимизации синхронизации кеша",
        description="Определяет правила и методы для оптимизации синхронизации "
                    "кеша, включая использование белых списков директорий и "
                    "механизмов исключения ненужных файлов.",
        standard_type="process"
    )
    
    if standard_id:
        print(f"✅ Стандарт успешно создан: {standard_id}")
    else:
        print("❌ Не удалось создать стандарт")
    
    # Устанавливаем связи между элементами
    if task_id and incident_id:
        print("\n🔗 Установка связей между элементами...")
        
        # Связываем задачу с инцидентом
        if establish_relation(task_id, incident_id, "relates_to", "Задача по решению инцидента"):
            print(f"✅ Установлена связь между задачей и инцидентом")
        
        # Связываем задачу со стандартом
        if standard_id and establish_relation(task_id, standard_id, "implements", "Задача реализует стандарт"):
            print(f"✅ Установлена связь между задачей и стандартом")
        
        # Связываем инцидент со стандартом
        if standard_id and establish_relation(incident_id, standard_id, "derives", "Инцидент привел к созданию стандарта"):
            print(f"✅ Установлена связь между инцидентом и стандартом")
    
    print("\n✅ Демонстрация завершена")
    return {
        "task_id": task_id,
        "incident_id": incident_id,
        "standard_id": standard_id
    }

if __name__ == "__main__":
    demo_create_elements()