"""
Модуль для работы с абстрактными ссылками.

Абстрактные ссылки - это механизм, позволяющий ссылаться на документы, стандарты
и другие элементы системы через логические идентификаторы, а не физические пути.
Это обеспечивает независимость от конкретной структуры файловой системы и
устойчивость к изменениям физического расположения файлов.
"""

import re
import os
import logging
from typing import Dict, List, Optional, Any, Union, Tuple, Callable

from advising_platform.standards.core.traceable import implements_standard

# Настройка логирования
logger = logging.getLogger(__name__)

# Шаблон абстрактной ссылки
ABSTRACT_LINK_PATTERN = r'abstract://([a-zA-Z0-9_]+):([a-zA-Z0-9_\-\.]+)(?:/([a-zA-Z0-9_\-\.\/]+))?'


class AbstractLinkRegistry:
    """Реестр отображений абстрактных ссылок на физические пути."""
    
    _instance = None
    
    def __new__(cls):
        """Создает синглтон для управления абстрактными ссылками."""
        if cls._instance is None:
            cls._instance = super(AbstractLinkRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Инициализирует реестр абстрактных ссылок."""
        if getattr(self, '_initialized', False):
            return
        
        # Маппинг типов логических идентификаторов к функциям разрешения
        self._resolvers = {}
        
        # Известные типы абстрактных ссылок
        self._known_types = set()
        
        # Кэш разрешенных ссылок
        self._resolution_cache = {}
        
        # Инициализированы реестр
        self._initialized = True
        
        # Регистрируем стандартные обработчики
        self._register_standard_handlers()
        
        logger.info("Инициализирован реестр абстрактных ссылок")
    
    def _register_standard_handlers(self) -> None:
        """Регистрирует стандартные обработчики абстрактных ссылок."""
        # Регистрируем обработчик для стандартов
        self.register_resolver("standard", self._resolve_standard)
        
        # Регистрируем обработчик для инцидентов
        self.register_resolver("incident", self._resolve_incident)
        
        # Регистрируем обработчик для задач
        self.register_resolver("todo", self._resolve_todo)
        
        # Регистрируем обработчик для гипотез
        self.register_resolver("hypothesis", self._resolve_hypothesis)
    
    @implements_standard("abstract_link", "1.0", "resolver_registration")
    def register_resolver(self, link_type: str, resolver_func: Callable[[str, Optional[str]], Optional[str]]) -> None:
        """
        Регистрирует функцию разрешения для указанного типа абстрактной ссылки.
        
        Args:
            link_type: Тип абстрактной ссылки
            resolver_func: Функция разрешения ссылки
        """
        self._resolvers[link_type] = resolver_func
        self._known_types.add(link_type)
        
        # Очищаем кэш разрешенных ссылок для этого типа
        self._clear_cache_for_type(link_type)
        
        logger.info(f"Зарегистрирован обработчик для абстрактных ссылок типа '{link_type}'")
    
    def _clear_cache_for_type(self, link_type: str) -> None:
        """
        Очищает кэш разрешенных ссылок для указанного типа.
        
        Args:
            link_type: Тип абстрактной ссылки
        """
        keys_to_remove = []
        
        for key in self._resolution_cache:
            if key.startswith(f"{link_type}:"):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self._resolution_cache[key]
    
    @implements_standard("abstract_link", "1.0", "resolution")
    def resolve_link(self, link_type: str, link_id: str, subpath: Optional[str] = None) -> Optional[str]:
        """
        Разрешает абстрактную ссылку в физический путь.
        
        Args:
            link_type: Тип абстрактной ссылки
            link_id: Идентификатор ссылки
            subpath: Дополнительный путь внутри ресурса (опционально)
        
        Returns:
            Физический путь к ресурсу или None, если ссылка не может быть разрешена
        """
        # Формируем ключ для кэша
        cache_key = f"{link_type}:{link_id}"
        if subpath:
            cache_key += f"/{subpath}"
        
        # Проверяем наличие в кэше
        if cache_key in self._resolution_cache:
            return self._resolution_cache[cache_key]
        
        # Проверяем наличие обработчика для типа ссылки
        if link_type not in self._resolvers:
            logger.warning(f"Неизвестный тип абстрактной ссылки: {link_type}")
            return None
        
        # Получаем физический путь с помощью обработчика
        resolver = self._resolvers[link_type]
        physical_path = resolver(link_id, subpath)
        
        # Кэшируем результат
        if physical_path:
            self._resolution_cache[cache_key] = physical_path
        
        return physical_path
    
    @implements_standard("abstract_link", "1.0", "extraction")
    def extract_links(self, content: str) -> List[Tuple[str, str, str, Optional[str]]]:
        """
        Извлекает абстрактные ссылки из текста.
        
        Args:
            content: Текст для поиска ссылок
        
        Returns:
            Список кортежей (полная_ссылка, тип, идентификатор, подпуть)
        """
        links = []
        
        # Находим все вхождения абстрактных ссылок
        matches = re.finditer(ABSTRACT_LINK_PATTERN, content)
        
        for match in matches:
            full_link = match.group(0)
            link_type = match.group(1)
            link_id = match.group(2)
            subpath = match.group(3) if match.group(3) else None
            
            links.append((full_link, link_type, link_id, subpath))
        
        return links
    
    @implements_standard("abstract_link", "1.0", "replacement")
    def replace_links(self, content: str, replacement_func: Optional[Callable[[str, str, str, Optional[str]], str]] = None) -> str:
        """
        Заменяет абстрактные ссылки в тексте на их физические пути или результат работы функции замены.
        
        Args:
            content: Текст с абстрактными ссылками
            replacement_func: Функция замены ссылок (опционально)
        
        Returns:
            Текст с замененными ссылками
        """
        if not replacement_func:
            # Используем стандартную функцию замены
            replacement_func = self._default_replacement
        
        # Извлекаем ссылки
        links = self.extract_links(content)
        
        # Заменяем ссылки
        result = content
        for full_link, link_type, link_id, subpath in links:
            replacement = replacement_func(link_type, link_id, subpath, full_link)
            result = result.replace(full_link, replacement)
        
        return result
    
    def _default_replacement(self, link_type: str, link_id: str, subpath: Optional[str], full_link: str) -> str:
        """
        Стандартная функция замены абстрактных ссылок на их физические пути.
        
        Args:
            link_type: Тип абстрактной ссылки
            link_id: Идентификатор ссылки
            subpath: Дополнительный путь внутри ресурса
            full_link: Полная абстрактная ссылка
        
        Returns:
            Физический путь или исходная ссылка, если путь не может быть разрешен
        """
        physical_path = self.resolve_link(link_type, link_id, subpath)
        return physical_path if physical_path else full_link
    
    @implements_standard("abstract_link", "1.0", "standard_resolver")
    def _resolve_standard(self, standard_id: str, subpath: Optional[str] = None) -> Optional[str]:
        """
        Обработчик для абстрактных ссылок на стандарты.
        
        Args:
            standard_id: Идентификатор стандарта
            subpath: Дополнительный путь внутри ресурса
        
        Returns:
            Физический путь к стандарту или None, если стандарт не найден
        """
        # Базовый путь к директории стандартов
        base_path = "[standards .md]"
        
        # Примеры стандартных идентификаторов:
        # - ai_incident: Стандарт инцидентов
        # - todo: Стандарт задач
        # - hypothesis: Стандарт гипотез
        # - protocol_challenge: Стандарт протокола вызова
        # - 5why_analysis: Стандарт анализа 5 почему
        
        # Маппинг идентификаторов стандартов к физическим путям
        standard_paths = {
            "ai_incident": os.path.join(base_path, "1. process · goalmap · task · incidents · tickets · qa", "1.1 ai incident standard 14 may 2025 0505 cet by ai assistant.md"),
            "todo": os.path.join(base_path, "1. process · goalmap · task · incidents · tickets · qa", "1.2 todo standard 14 may 2025 1825 cet by ai assistant.md"),
            "hypothesis": os.path.join(base_path, "1. process · goalmap · task · incidents · tickets · qa", "1.3 hypothesis standard 14 may 2025 2000 cet by ai assistant.md"),
            "protocol_challenge": os.path.join(base_path, "0. core standards", "0.2 protocol challenge standard 13 may 2025 1200 cet by krasinsky.md"),
            "5why_analysis": os.path.join(base_path, "0. core standards", "0.3 5why analysis standard 13 may 2025 1500 cet by krasinsky.md"),
            "standa": os.path.join(base_path, "9. development · documentation", "9.8 standards implementation system standa 15 may 2025 2245 cet by ai assistant.md"),
            "ai_personality": os.path.join(base_path, "9. development · documentation", "9.7 ai personality standard 15 may 2025 2150 cet by ai assistant.md")
        }
        
        # Получаем путь к стандарту
        if standard_id not in standard_paths:
            logger.warning(f"Неизвестный стандарт: {standard_id}")
            return None
        
        path = standard_paths[standard_id]
        
        # Добавляем подпуть, если указан
        if subpath:
            path = os.path.join(os.path.dirname(path), subpath)
        
        return path
    
    @implements_standard("abstract_link", "1.0", "incident_resolver")
    def _resolve_incident(self, incident_id: str, subpath: Optional[str] = None) -> Optional[str]:
        """
        Обработчик для абстрактных ссылок на инциденты.
        
        Args:
            incident_id: Идентификатор инцидента
            subpath: Дополнительный путь внутри ресурса
        
        Returns:
            Физический путь к инциденту или None, если инцидент не найден
        """
        # Базовый путь к директории инцидентов
        base_path = "[todo · incidents]"
        
        # Основной файл инцидентов
        main_file = os.path.join(base_path, "ai.incidents.md")
        
        # Директория с индивидуальными инцидентами
        incidents_dir = os.path.join(base_path, "ai.incidents")
        
        # Проверяем наличие индивидуального файла инцидента
        individual_file = os.path.join(incidents_dir, f"{incident_id}.md")
        if os.path.exists(individual_file):
            return individual_file
        
        # Если не найден индивидуальный файл, возвращаем основной файл
        # (предполагается, что инцидент находится в нем)
        return main_file
    
    @implements_standard("abstract_link", "1.0", "todo_resolver")
    def _resolve_todo(self, todo_id: str, subpath: Optional[str] = None) -> Optional[str]:
        """
        Обработчик для абстрактных ссылок на задачи.
        
        Args:
            todo_id: Идентификатор задачи
            subpath: Дополнительный путь внутри ресурса
        
        Returns:
            Физический путь к задаче или None, если задача не найдена
        """
        # Базовый путь к директории задач
        base_path = "[todo · incidents]"
        
        # Основной файл задач
        main_file = os.path.join(base_path, "todo.md")
        
        # Директория с индивидуальными задачами
        todos_dir = os.path.join(base_path, "ai.todo")
        
        # Проверяем наличие индивидуального файла задачи
        individual_file = os.path.join(todos_dir, f"{todo_id}.md")
        if os.path.exists(individual_file):
            return individual_file
        
        # Если не найден индивидуальный файл, возвращаем основной файл
        # (предполагается, что задача находится в нем)
        return main_file
    
    @implements_standard("abstract_link", "1.0", "hypothesis_resolver")
    def _resolve_hypothesis(self, hypothesis_id: str, subpath: Optional[str] = None) -> Optional[str]:
        """
        Обработчик для абстрактных ссылок на гипотезы.
        
        Args:
            hypothesis_id: Идентификатор гипотезы
            subpath: Дополнительный путь внутри ресурса
        
        Returns:
            Физический путь к гипотезе или None, если гипотеза не найдена
        """
        # В текущей реализации гипотезы хранятся только в памяти
        # и не имеют физического представления в файловой системе
        return None
    
    @implements_standard("abstract_link", "1.0", "get_types")
    def get_known_types(self) -> List[str]:
        """
        Возвращает список известных типов абстрактных ссылок.
        
        Returns:
            Список типов абстрактных ссылок
        """
        return list(self._known_types)


# Создаем глобальный экземпляр для удобного импорта
abstract_link_registry = AbstractLinkRegistry()


@implements_standard("abstract_link", "1.0", "create_link")
def create_abstract_link(link_type: str, link_id: str, subpath: Optional[str] = None) -> str:
    """
    Создает абстрактную ссылку.
    
    Args:
        link_type: Тип абстрактной ссылки
        link_id: Идентификатор ссылки
        subpath: Дополнительный путь внутри ресурса (опционально)
    
    Returns:
        Строка с абстрактной ссылкой
    """
    # Проверяем корректность типа ссылки
    if link_type not in abstract_link_registry.get_known_types():
        logger.warning(f"Неизвестный тип абстрактной ссылки: {link_type}")
    
    # Формируем ссылку
    link = f"abstract://{link_type}:{link_id}"
    if subpath:
        link += f"/{subpath}"
    
    return link


@implements_standard("abstract_link", "1.0", "resolve_link")
def resolve_abstract_link(link_type: str, link_id: str, subpath: Optional[str] = None) -> Optional[str]:
    """
    Разрешает абстрактную ссылку в физический путь.
    
    Args:
        link_type: Тип абстрактной ссылки
        link_id: Идентификатор ссылки
        subpath: Дополнительный путь внутри ресурса (опционально)
    
    Returns:
        Физический путь к ресурсу или None, если ссылка не может быть разрешена
    """
    return abstract_link_registry.resolve_link(link_type, link_id, subpath)


@implements_standard("abstract_link", "1.0", "extract_links")
def extract_abstract_links(content: str) -> List[Tuple[str, str, str, Optional[str]]]:
    """
    Извлекает абстрактные ссылки из текста.
    
    Args:
        content: Текст для поиска ссылок
    
    Returns:
        Список кортежей (полная_ссылка, тип, идентификатор, подпуть)
    """
    return abstract_link_registry.extract_links(content)


@implements_standard("abstract_link", "1.0", "replace_links")
def replace_abstract_links(content: str, replacement_func: Optional[Callable[[str, str, str, Optional[str]], str]] = None) -> str:
    """
    Заменяет абстрактные ссылки в тексте на их физические пути или результат работы функции замены.
    
    Args:
        content: Текст с абстрактными ссылками
        replacement_func: Функция замены ссылок (опционально)
    
    Returns:
        Текст с замененными ссылками
    """
    return abstract_link_registry.replace_links(content, replacement_func)


@implements_standard("abstract_link", "1.0", "register_resolver")
def register_abstract_link_resolver(link_type: str, resolver_func: Callable[[str, Optional[str]], Optional[str]]) -> None:
    """
    Регистрирует функцию разрешения для указанного типа абстрактной ссылки.
    
    Args:
        link_type: Тип абстрактной ссылки
        resolver_func: Функция разрешения ссылки
    """
    abstract_link_registry.register_resolver(link_type, resolver_func)


if __name__ == "__main__":
    # Пример использования
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Создаем абстрактную ссылку на стандарт
    standard_link = create_abstract_link("standard", "ai_incident")
    print(f"Абстрактная ссылка на стандарт: {standard_link}")
    
    # Разрешаем ссылку в физический путь
    physical_path = resolve_abstract_link("standard", "ai_incident")
    print(f"Физический путь: {physical_path}")
    
    # Текст с абстрактными ссылками
    text = """
    Информация о стандартах:
    - [Стандарт инцидентов](abstract://standard:ai_incident)
    - [Стандарт задач](abstract://standard:todo)
    - [Стандарт гипотез](abstract://standard:hypothesis)
    
    Инциденты:
    - [Инцидент 1](abstract://incident:incident_20250510_001)
    - [Инцидент 2](abstract://incident:incident_20250511_002)
    """
    
    # Извлекаем ссылки
    links = extract_abstract_links(text)
    print("\nНайденные ссылки:")
    for link in links:
        full_link, link_type, link_id, subpath = link
        print(f"- {full_link} (тип: {link_type}, id: {link_id}, подпуть: {subpath})")
    
    # Заменяем ссылки на физические пути
    replaced_text = replace_abstract_links(text)
    print("\nТекст с замененными ссылками:")
    print(replaced_text)
    
    # Примеры различных функций замены
    def html_replacement(link_type: str, link_id: str, subpath: Optional[str], full_link: str) -> str:
        """Заменяет абстрактную ссылку на HTML-ссылку."""
        physical_path = resolve_abstract_link(link_type, link_id, subpath)
        if physical_path:
            return f'<a href="{physical_path}" data-link-type="{link_type}" data-link-id="{link_id}">{link_id}</a>'
        else:
            return f'<span class="unresolved-link" data-link-type="{link_type}" data-link-id="{link_id}">{link_id}</span>'
    
    # Заменяем ссылки на HTML-ссылки
    html_text = replace_abstract_links(text, html_replacement)
    print("\nТекст с HTML-ссылками:")
    print(html_text)