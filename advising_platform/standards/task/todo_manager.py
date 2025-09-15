"""
Модуль для управления задачами в соответствии со стандартом задач.

Реализует централизованное управление задачами, обеспечивая их создание,
обновление и отслеживание согласно актуальному стандарту.
"""

import os
import re
import logging
import datetime
from typing import Dict, List, Optional, Any, Union, Tuple

from advising_platform.standards.core.traceable import implements_standard

# Настройка логирования
logger = logging.getLogger(__name__)

# Константы
TODO_DIR = "[todo · incidents]"
MAIN_TODO_FILE = os.path.join(TODO_DIR, "todo.md")
TODO_INDIVIDUAL_DIR = os.path.join(TODO_DIR, "ai.todo")

# Статусы задач
TODO_STATUSES = [
    "TODO",          # Задача в очереди
    "IN_PROGRESS",   # Задача в работе
    "COMPLETED",     # Задача завершена
    "BLOCKED",       # Задача заблокирована
    "CANCELLED"      # Задача отменена
]

# Приоритеты задач
TODO_PRIORITIES = [
    "CRITICAL",      # Критический приоритет
    "IMPORTANT",     # Важный приоритет
    "NORMAL",        # Нормальный приоритет
    "LOW"            # Низкий приоритет
]

# Шаблоны регулярных выражений
RE_TODO_HEADER = r"#\s+(📋|:clipboard:)\s+(.+?)\s*$"
RE_TODO_METADATA = r"\s*##\s+Метаданные\s*\n([\s\S]*?)(?:\n\s*##|$)"
RE_TODO_METADATA_FIELD = r"\s*-\s+\*\*([^:]+):\*\*\s+(.*?)\s*$"


@implements_standard("todo", "1.5", "storage")
class TodoStorage:
    """Хранилище задач в соответствии со стандартом Todo v1.5."""
    
    _instance = None
    
    def __new__(cls):
        """Создает синглтон для управления задачами."""
        if cls._instance is None:
            cls._instance = super(TodoStorage, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Инициализирует менеджер задач."""
        if getattr(self, '_initialized', False):
            return
        
        self._todos_cache = []
        self._cache_loaded = False
        self._initialized = True
        logger.info("Инициализирован менеджер задач")
    
    def _ensure_dirs_exist(self) -> None:
        """Проверяет существование необходимых директорий и создает их при необходимости."""
        if not os.path.exists(TODO_DIR):
            os.makedirs(TODO_DIR, exist_ok=True)
            logger.info(f"Создана директория для задач: {TODO_DIR}")
        
        if not os.path.exists(TODO_INDIVIDUAL_DIR):
            os.makedirs(TODO_INDIVIDUAL_DIR, exist_ok=True)
            logger.info(f"Создана директория для индивидуальных задач: {TODO_INDIVIDUAL_DIR}")
    
    @implements_standard("todo", "1.5", "parsing")
    def _parse_todo_metadata(self, metadata_section: str) -> Dict[str, str]:
        """
        Извлекает метаданные задачи из секции метаданных.
        
        Args:
            metadata_section: Секция метаданных задачи
        
        Returns:
            Словарь с метаданными задачи
        """
        metadata = {}
        
        # Ищем все поля метаданных
        for line in metadata_section.split('\n'):
            match = re.match(RE_TODO_METADATA_FIELD, line)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                metadata[key] = value
        
        return metadata
    
    @implements_standard("todo", "1.5", "retrieval")
    def load_individual_todo(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Загружает задачу из отдельного файла.
        
        Args:
            file_path: Путь к файлу задачи
        
        Returns:
            Информация о задаче или None, если файл не найден или неверного формата
        """
        try:
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Извлекаем заголовок задачи
            header_match = re.search(RE_TODO_HEADER, content)
            if not header_match:
                logger.warning(f"Не удалось найти заголовок задачи в файле: {file_path}")
                return None
            
            title = header_match.group(2)
            todo_id = os.path.splitext(os.path.basename(file_path))[0]
            
            # Извлекаем метаданные
            metadata_match = re.search(RE_TODO_METADATA, content)
            metadata = {}
            
            if metadata_match:
                metadata_section = metadata_match.group(1)
                metadata = self._parse_todo_metadata(metadata_section)
            
            # Формируем структуру задачи
            todo = {
                "id": todo_id,
                "title": title,
                "content": content,
                "file_path": file_path,
                "metadata": metadata,
                "status": metadata.get("Статус", "TODO"),
                "priority": metadata.get("Приоритет", "NORMAL"),
                "created": metadata.get("Дата создания", datetime.datetime.now().strftime("%Y-%m-%d")),
                "deadline": metadata.get("Крайний срок", "")
            }
            
            return todo
        
        except Exception as e:
            logger.error(f"Ошибка при загрузке задачи из файла {file_path}: {e}")
            return None
    
    @implements_standard("todo", "1.5", "retrieval")
    def get_todos(self, reload: bool = False) -> List[Dict[str, Any]]:
        """
        Возвращает список всех задач.
        
        Args:
            reload: Принудительно перезагрузить задачи из файлов
        
        Returns:
            Список задач с их метаданными
        """
        if not self._cache_loaded or reload:
            self._ensure_dirs_exist()
            
            # Загружаем задачи из индивидуальных файлов
            todos = []
            
            if os.path.exists(TODO_INDIVIDUAL_DIR):
                file_paths = [
                    os.path.join(TODO_INDIVIDUAL_DIR, f) 
                    for f in os.listdir(TODO_INDIVIDUAL_DIR) 
                    if f.endswith('.md')
                ]
                
                for file_path in file_paths:
                    todo = self.load_individual_todo(file_path)
                    if todo:
                        todos.append(todo)
            
            # Сортируем задачи по приоритету и дате создания
            todos.sort(
                key=lambda x: (
                    TODO_PRIORITIES.index(x["priority"]) if x["priority"] in TODO_PRIORITIES else 999,
                    x.get("created", "")
                )
            )
            
            self._todos_cache = todos
            self._cache_loaded = True
            
            logger.info(f"Загружено {len(todos)} задач")
        
        return self._todos_cache
    
    @implements_standard("todo", "1.5", "retrieval_by_id")
    def get_todo_by_id(self, todo_id: str, reload: bool = False) -> Optional[Dict[str, Any]]:
        """
        Находит задачу по её идентификатору.
        
        Args:
            todo_id: Идентификатор задачи
            reload: Принудительно перезагрузить задачи из файлов
        
        Returns:
            Информация о задаче или None, если задача не найдена
        """
        todos = self.get_todos(reload)
        
        for todo in todos:
            if todo["id"] == todo_id:
                return todo
        
        # Если не нашли в кэше, пробуем загрузить из отдельного файла
        file_path = os.path.join(TODO_INDIVIDUAL_DIR, f"{todo_id}.md")
        return self.load_individual_todo(file_path)
    
    @implements_standard("todo", "1.5", "formatting")
    def format_todo_metadata(self, metadata: Dict[str, str]) -> str:
        """
        Форматирует метаданные задачи для записи в файл.
        
        Args:
            metadata: Метаданные задачи
        
        Returns:
            Отформатированные метаданные задачи
        """
        lines = []
        
        # Добавляем обязательные поля в определенном порядке
        for key in ["Дата создания", "Приоритет", "Статус", "Автор", "Крайний срок"]:
            if key in metadata:
                lines.append(f"- **{key}:** {metadata[key]}")
        
        # Добавляем остальные поля
        for key, value in metadata.items():
            if key not in ["Дата создания", "Приоритет", "Статус", "Автор", "Крайний срок"]:
                lines.append(f"- **{key}:** {value}")
        
        return "\n".join(lines)
    
    @implements_standard("todo", "1.5", "formatting")
    def format_todo(self, todo_data: Dict[str, Any]) -> str:
        """
        Форматирует данные задачи в текстовое представление для записи в файл.
        
        Args:
            todo_data: Данные задачи
        
        Returns:
            Отформатированное текстовое представление задачи
        """
        title = todo_data.get("title", "Задача без заголовка")
        metadata = todo_data.get("metadata", {})
        content = todo_data.get("content", "")
        
        # Если передано полное содержимое, возвращаем его
        if content and "# 📋" in content:
            return content
        
        # Форматируем метаданные
        metadata_formatted = self.format_todo_metadata(metadata)
        
        # Формируем содержимое задачи
        formatted = f"""# 📋 {title}

## Метаданные
{metadata_formatted}

## Описание задачи

{todo_data.get("description", "")}

## План решения

{todo_data.get("plan", "")}

## Критерии успеха

{todo_data.get("success_criteria", "")}

## Зависимости
{todo_data.get("dependencies", "")}

## Примечания
{todo_data.get("notes", "")}"""
        
        return formatted
    
    @implements_standard("todo", "1.5", "creation")
    def create_todo(self, todo_data: Dict[str, Any]) -> str:
        """
        Создает новую задачу в отдельном файле.
        
        Args:
            todo_data: Данные задачи
        
        Returns:
            Идентификатор созданной задачи
        """
        self._ensure_dirs_exist()
        
        # Генерируем идентификатор, если не предоставлен
        todo_id = todo_data.get("id", "")
        if not todo_id:
            title_slug = re.sub(r'[^a-z0-9]', '-', todo_data.get("title", "").lower())
            date_str = datetime.datetime.now().strftime("%Y%m%d")
            todo_id = f"todo-{title_slug}-{date_str}"
        
        # Формируем путь к файлу
        file_path = os.path.join(TODO_INDIVIDUAL_DIR, f"{todo_id}.md")
        
        # Получаем метаданные
        metadata = todo_data.get("metadata", {})
        
        # Добавляем обязательные метаданные, если отсутствуют
        if "Дата создания" not in metadata:
            metadata["Дата создания"] = datetime.datetime.now().strftime("%Y-%m-%d")
        
        if "Статус" not in metadata:
            metadata["Статус"] = "TODO"
        
        if "Приоритет" not in metadata:
            metadata["Приоритет"] = "NORMAL"
        
        if "Автор" not in metadata:
            metadata["Автор"] = "AI Assistant"
        
        # Обновляем данные задачи
        todo_data["metadata"] = metadata
        todo_data["id"] = todo_id
        
        # Форматируем содержимое файла
        content = self.format_todo(todo_data)
        
        # Записываем в файл
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Создана новая задача: {todo_id}")
            
            # Инвалидируем кэш
            self._cache_loaded = False
            
            return todo_id
        
        except Exception as e:
            logger.error(f"Ошибка при создании задачи: {e}")
            raise
    
    @implements_standard("todo", "1.5", "update")
    def update_todo(self, todo_id: str, updated_data: Dict[str, Any]) -> bool:
        """
        Обновляет существующую задачу.
        
        Args:
            todo_id: Идентификатор задачи
            updated_data: Обновленные данные задачи
        
        Returns:
            True, если обновление прошло успешно, иначе False
        """
        # Получаем текущие данные задачи
        todo = self.get_todo_by_id(todo_id, reload=True)
        if not todo:
            logger.warning(f"Задача не найдена: {todo_id}")
            return False
        
        # Обновляем данные
        for key, value in updated_data.items():
            if key == "metadata":
                # Обновляем метаданные
                todo["metadata"].update(value)
            else:
                todo[key] = value
        
        # Получаем путь к файлу
        file_path = todo.get("file_path", os.path.join(TODO_INDIVIDUAL_DIR, f"{todo_id}.md"))
        
        # Форматируем содержимое файла
        content = self.format_todo(todo)
        
        # Записываем в файл
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Обновлена задача: {todo_id}")
            
            # Инвалидируем кэш
            self._cache_loaded = False
            
            return True
        
        except Exception as e:
            logger.error(f"Ошибка при обновлении задачи {todo_id}: {e}")
            return False
    
    @implements_standard("todo", "1.5", "status_update")
    def update_todo_status(self, todo_id: str, new_status: str) -> bool:
        """
        Обновляет статус задачи.
        
        Args:
            todo_id: Идентификатор задачи
            new_status: Новый статус задачи
        
        Returns:
            True, если обновление прошло успешно, иначе False
        """
        # Проверяем корректность статуса
        if new_status not in TODO_STATUSES:
            logger.warning(f"Некорректный статус задачи: {new_status}")
            return False
        
        # Обновляем задачу
        return self.update_todo(todo_id, {"metadata": {"Статус": new_status}})
    
    @implements_standard("todo", "1.5", "priority_update")
    def update_todo_priority(self, todo_id: str, new_priority: str) -> bool:
        """
        Обновляет приоритет задачи.
        
        Args:
            todo_id: Идентификатор задачи
            new_priority: Новый приоритет задачи
        
        Returns:
            True, если обновление прошло успешно, иначе False
        """
        # Проверяем корректность приоритета
        if new_priority not in TODO_PRIORITIES:
            logger.warning(f"Некорректный приоритет задачи: {new_priority}")
            return False
        
        # Обновляем задачу
        return self.update_todo(todo_id, {"metadata": {"Приоритет": new_priority}})


# Создаем глобальный экземпляр для удобного импорта
todo_storage = TodoStorage()


# Функции-хелперы для работы с задачами
@implements_standard("todo", "1.5", "creation")
def create_todo(
    title: str,
    description: str,
    priority: str = "NORMAL",
    plan: str = "",
    success_criteria: str = "",
    dependencies: str = "",
    notes: str = ""
) -> str:
    """
    Создает новую задачу.
    
    Args:
        title: Заголовок задачи
        description: Описание задачи
        priority: Приоритет задачи
        plan: План решения задачи
        success_criteria: Критерии успеха задачи
        dependencies: Зависимости задачи
        notes: Примечания к задаче
    
    Returns:
        Идентификатор созданной задачи
    """
    # Генерируем идентификатор на основе заголовка и времени
    title_slug = re.sub(r'[^a-z0-9]', '-', title.lower())
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    todo_id = f"todo-{title_slug}-{date_str}"
    
    # Формируем данные задачи
    todo_data = {
        "id": todo_id,
        "title": title,
        "description": description,
        "plan": plan,
        "success_criteria": success_criteria,
        "dependencies": dependencies,
        "notes": notes,
        "metadata": {
            "Дата создания": datetime.datetime.now().strftime("%Y-%m-%d"),
            "Приоритет": priority,
            "Статус": "TODO",
            "Автор": "AI Assistant"
        }
    }
    
    # Создаем задачу
    return todo_storage.create_todo(todo_data)


@implements_standard("todo", "1.5", "status_update")
def update_todo_status(todo_id: str, new_status: str) -> bool:
    """
    Обновляет статус задачи.
    
    Args:
        todo_id: Идентификатор задачи
        new_status: Новый статус задачи
    
    Returns:
        True, если обновление прошло успешно, иначе False
    """
    return todo_storage.update_todo_status(todo_id, new_status)


@implements_standard("todo", "1.5", "retrieval")
def get_todos_by_status(status: str) -> List[Dict[str, Any]]:
    """
    Возвращает список задач с указанным статусом.
    
    Args:
        status: Статус задач
    
    Returns:
        Список задач с указанным статусом
    """
    todos = todo_storage.get_todos()
    return [todo for todo in todos if todo.get("status") == status]


@implements_standard("todo", "1.5", "retrieval")
def get_todos_by_priority(priority: str) -> List[Dict[str, Any]]:
    """
    Возвращает список задач с указанным приоритетом.
    
    Args:
        priority: Приоритет задач
    
    Returns:
        Список задач с указанным приоритетом
    """
    todos = todo_storage.get_todos()
    return [todo for todo in todos if todo.get("priority") == priority]


if __name__ == "__main__":
    # Пример использования
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Создаем тестовую задачу
    todo_id = create_todo(
        title="Тестовая задача",
        description="Описание тестовой задачи",
        priority="IMPORTANT",
        plan="1. Шаг 1\n2. Шаг 2\n3. Шаг 3",
        success_criteria="Задача считается выполненной, если ...",
        dependencies="- Зависимость 1\n- Зависимость 2",
        notes="Примечание к задаче"
    )
    
    print(f"Создана задача: {todo_id}")
    
    # Получаем все задачи
    todos = todo_storage.get_todos()
    print(f"Всего задач: {len(todos)}")
    
    # Обновляем статус задачи
    if todo_id:
        print(f"Обновляем статус задачи {todo_id}")
        update_todo_status(todo_id, "IN_PROGRESS")
        
        # Получаем задачу по идентификатору
        todo = todo_storage.get_todo_by_id(todo_id, reload=True)
        if todo:
            print(f"Задача {todo_id}: {todo['title']} - {todo['status']}")