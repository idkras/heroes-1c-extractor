"""
Модуль командного интерфейса для управления связями между элементами.

Предоставляет инструменты командной строки для создания, обновления и удаления
связей между задачами, инцидентами, гипотезами и стандартами.

Автор: AI Assistant
Дата: 20 мая 2025
"""

import argparse
import logging
import sys
import textwrap
from typing import List, Dict, Optional, Any, Tuple

# Настройка логирования
logger = logging.getLogger("relation_cli")
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Импорт необходимых модулей
try:
    from advising_platform.src.core.registry.task_registry import (
        WorkItemRelationType, get_registry, WorkItem
    )
    from advising_platform.src.core.registry.work_item_processor import (
        WorkItemProcessor, ProcessResult
    )
    from advising_platform.src.core.notifications import (
        NotificationType, NotificationPriority, send_notification
    )
except ImportError as e:
    logger.error(f"Ошибка импорта модулей: {e}")
    raise


# Цвета для вывода в консоль
class Colors:
    """Цвета для вывода в консоль."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def color_print(text: str, color: str = Colors.END, bold: bool = False):
    """
    Выводит цветной текст в консоль.
    
    Args:
        text: Текст для вывода
        color: Цвет текста
        bold: Делать ли текст жирным
    """
    bold_str = Colors.BOLD if bold else ""
    print(f"{bold_str}{color}{text}{Colors.END}")


def get_relation_type_from_string(relation_type_str: str) -> Optional[WorkItemRelationType]:
    """
    Преобразует строковое представление типа связи в перечисление.
    
    Args:
        relation_type_str: Строковое представление типа связи
        
    Returns:
        Тип связи или None, если не найден
    """
    relation_type_str = relation_type_str.upper()
    
    # Создаем словарь соответствия строк типам связей
    relation_types = {
        "BLOCKS": WorkItemRelationType.BLOCKS,
        "BLOCKED_BY": WorkItemRelationType.BLOCKED_BY,
        "DUPLICATES": WorkItemRelationType.DUPLICATES,
        "DUPLICATED_BY": WorkItemRelationType.DUPLICATED_BY,
        "RELATES_TO": WorkItemRelationType.RELATES_TO,
        "PART_OF": WorkItemRelationType.PART_OF,
        "PARENT_OF": WorkItemRelationType.PARENT_OF,
        "PRECEDES": WorkItemRelationType.PRECEDES,
        "FOLLOWS": WorkItemRelationType.FOLLOWS
    }
    
    return relation_types.get(relation_type_str)


def list_available_relation_types():
    """
    Выводит список доступных типов связей.
    """
    color_print("\nДоступные типы связей:", Colors.HEADER, True)
    
    relation_descriptions = {
        "BLOCKS": "Блокирует выполнение целевого элемента",
        "BLOCKED_BY": "Блокируется целевым элементом",
        "DUPLICATES": "Дублирует целевой элемент",
        "DUPLICATED_BY": "Дублируется целевым элементом",
        "RELATES_TO": "Связан с целевым элементом",
        "PART_OF": "Является частью целевого элемента",
        "PARENT_OF": "Является родителем для целевого элемента",
        "PRECEDES": "Предшествует целевому элементу",
        "FOLLOWS": "Следует за целевым элементом"
    }
    
    for relation_type, description in relation_descriptions.items():
        print(f"  {Colors.BOLD}{Colors.GREEN}{relation_type}{Colors.END}: {description}")


def format_item_info(item: WorkItem) -> str:
    """
    Форматирует информацию об элементе для вывода.
    
    Args:
        item: Элемент
        
    Returns:
        Отформатированная строка с информацией об элементе
    """
    item_type_str = {
        "TASK": "Задача",
        "INCIDENT": "Инцидент",
        "HYPOTHESIS": "Гипотеза",
        "STANDARD": "Стандарт",
        "EXPERIMENT": "Эксперимент"
    }.get(item.type.value, "Элемент")
    
    status_str = {
        "BACKLOG": "В бэклоге",
        "TODO": "В планах",
        "IN_PROGRESS": "В работе",
        "DONE": "Выполнено",
        "REVIEW": "На проверке",
        "BLOCKED": "Заблокировано",
        "ARCHIVED": "В архиве"
    }.get(item.status.value, "Неизвестно")
    
    return f"{item_type_str} {item.id} (Статус: {status_str}): {item.title}"


def list_relations(item_id: str):
    """
    Выводит список связей для указанного элемента.
    
    Args:
        item_id: Идентификатор элемента
    """
    registry = get_registry()
    item = registry.get_item(item_id)
    
    if not item:
        color_print(f"Ошибка: элемент {item_id} не найден", Colors.RED)
        return
    
    outgoing_relations = registry.get_outgoing_relations(item_id)
    incoming_relations = registry.get_incoming_relations(item_id)
    
    color_print(f"\nСвязи для элемента {item_id}: {item.title}", Colors.HEADER, True)
    
    if not outgoing_relations and not incoming_relations:
        color_print("У этого элемента нет связей", Colors.YELLOW)
        return
    
    if outgoing_relations:
        color_print("\nИсходящие связи:", Colors.BLUE, True)
        for relation in outgoing_relations:
            target_item = registry.get_item(relation.target_id)
            if target_item:
                target_info = format_item_info(target_item)
                print(f"  {Colors.GREEN}{relation.relation_type.value}{Colors.END} -> {target_info}")
                if relation.description:
                    print(f"    {Colors.YELLOW}Описание:{Colors.END} {relation.description}")
    
    if incoming_relations:
        color_print("\nВходящие связи:", Colors.BLUE, True)
        for relation in incoming_relations:
            source_item = registry.get_item(relation.source_id)
            if source_item:
                source_info = format_item_info(source_item)
                print(f"  {source_info} {Colors.GREEN}{relation.relation_type.value}{Colors.END} -> {item_id}")
                if relation.description:
                    print(f"    {Colors.YELLOW}Описание:{Colors.END} {relation.description}")


def search_items(query: str, limit: int = 10) -> List[WorkItem]:
    """
    Ищет элементы по запросу.
    
    Args:
        query: Строка запроса
        limit: Максимальное количество результатов
        
    Returns:
        Список найденных элементов
    """
    registry = get_registry()
    results = []
    
    # Поиск по идентификатору
    if query.startswith("T") or query.startswith("I") or query.startswith("H") or query.startswith("S"):
        item = registry.get_item(query)
        if item:
            return [item]
    
    # Поиск по названию
    query_lower = query.lower()
    for item in registry.items.values():
        if query_lower in item.title.lower():
            results.append(item)
            if len(results) >= limit:
                break
    
    return results


def add_relation(source_id: str, target_id: str, relation_type_str: str, description: Optional[str] = None):
    """
    Добавляет связь между элементами.
    
    Args:
        source_id: Идентификатор исходного элемента
        target_id: Идентификатор целевого элемента
        relation_type_str: Тип связи (строковое представление)
        description: Описание связи
    """
    registry = get_registry()
    processor = WorkItemProcessor()
    
    # Проверяем существование элементов
    source_item = registry.get_item(source_id)
    if not source_item:
        color_print(f"Ошибка: исходный элемент {source_id} не найден", Colors.RED)
        return
    
    target_item = registry.get_item(target_id)
    if not target_item:
        color_print(f"Ошибка: целевой элемент {target_id} не найден", Colors.RED)
        return
    
    # Преобразуем строковый тип связи в перечисление
    relation_type = get_relation_type_from_string(relation_type_str)
    if not relation_type:
        color_print(f"Ошибка: неизвестный тип связи: {relation_type_str}", Colors.RED)
        list_available_relation_types()
        return
    
    # Добавляем связь
    success = registry.add_relation(
        source_id=source_id,
        target_id=target_id,
        relation_type=relation_type,
        description=description
    )
    
    if success:
        color_print(
            f"Связь успешно добавлена: {source_id} {relation_type.value} -> {target_id}",
            Colors.GREEN
        )
        
        # Отправляем уведомление о добавлении связи
        try:
            notification_title = f"Добавлена связь между элементами"
            notification_message = f"{source_id} {relation_type.value} -> {target_id}"
            
            notification_data = {
                "source_id": source_id,
                "source_title": source_item.title,
                "source_type": source_item.type.value,
                "target_id": target_id,
                "target_title": target_item.title,
                "target_type": target_item.type.value,
                "relation_type": relation_type.value,
                "description": description or ""
            }
            
            send_notification(
                notification_type=NotificationType.RELATION_ADDED,
                title=notification_title,
                message=notification_message,
                data=notification_data,
                priority=NotificationPriority.NORMAL
            )
        except Exception as e:
            color_print(f"Ошибка при отправке уведомления: {e}", Colors.RED)
    else:
        color_print(
            f"Ошибка при добавлении связи: {source_id} {relation_type.value} -> {target_id}",
            Colors.RED
        )


def remove_relation(source_id: str, target_id: str):
    """
    Удаляет связь между элементами.
    
    Args:
        source_id: Идентификатор исходного элемента
        target_id: Идентификатор целевого элемента
    """
    registry = get_registry()
    processor = WorkItemProcessor()
    
    # Проверяем существование элементов
    source_item = registry.get_item(source_id)
    if not source_item:
        color_print(f"Ошибка: исходный элемент {source_id} не найден", Colors.RED)
        return
    
    target_item = registry.get_item(target_id)
    if not target_item:
        color_print(f"Ошибка: целевой элемент {target_id} не найден", Colors.RED)
        return
    
    # Получаем информацию о связи перед удалением
    relation_info = None
    outgoing_relations = registry.get_outgoing_relations(source_id)
    for rel_target_id, relation_type, description in outgoing_relations:
        if rel_target_id == target_id:
            relation_info = (relation_type, description)
            break
    
    # Удаляем связь
    success = registry.remove_relation(
        source_id=source_id,
        target_id=target_id
    )
    
    if success:
        color_print(
            f"Связь успешно удалена: {source_id} -> {target_id}",
            Colors.GREEN
        )
        
        # Отправляем уведомление об удалении связи
        if relation_info:
            try:
                relation_type, description = relation_info
                notification_title = f"Удалена связь между элементами"
                notification_message = f"{source_id} {relation_type.value} -> {target_id}"
                
                notification_data = {
                    "source_id": source_id,
                    "source_title": source_item.title,
                    "source_type": source_item.type.value,
                    "target_id": target_id,
                    "target_title": target_item.title,
                    "target_type": target_item.type.value,
                    "relation_type": relation_type.value,
                    "description": description or ""
                }
                
                send_notification(
                    notification_type=NotificationType.RELATION_REMOVED,
                    title=notification_title,
                    message=notification_message,
                    data=notification_data,
                    priority=NotificationPriority.NORMAL
                )
            except Exception as e:
                color_print(f"Ошибка при отправке уведомления: {e}", Colors.RED)
    else:
        color_print(
            f"Ошибка при удалении связи: связь {source_id} -> {target_id} не найдена",
            Colors.RED
        )


def search_command(args):
    """
    Обрабатывает команду поиска.
    
    Args:
        args: Аргументы командной строки
    """
    query = args.query
    limit = args.limit
    
    items = search_items(query, limit)
    
    if not items:
        color_print(f"По запросу '{query}' ничего не найдено", Colors.YELLOW)
        return
    
    color_print(f"\nРезультаты поиска по запросу '{query}':", Colors.HEADER, True)
    
    for item in items:
        item_info = format_item_info(item)
        print(f"  {item_info}")


def list_command(args):
    """
    Обрабатывает команду вывода списка связей.
    
    Args:
        args: Аргументы командной строки
    """
    item_id = args.item_id
    list_relations(item_id)


def add_command(args):
    """
    Обрабатывает команду добавления связи.
    
    Args:
        args: Аргументы командной строки
    """
    source_id = args.source_id
    target_id = args.target_id
    relation_type = args.relation_type
    description = args.description
    
    add_relation(source_id, target_id, relation_type, description)


def remove_command(args):
    """
    Обрабатывает команду удаления связи.
    
    Args:
        args: Аргументы командной строки
    """
    source_id = args.source_id
    target_id = args.target_id
    
    remove_relation(source_id, target_id)


def types_command(args):
    """
    Обрабатывает команду вывода списка типов связей.
    
    Args:
        args: Аргументы командной строки
    """
    list_available_relation_types()


def main():
    """
    Основная функция, точка входа в программу.
    """
    # Создаем парсер аргументов командной строки
    parser = argparse.ArgumentParser(
        description="Инструмент для управления связями между элементами (задачами, инцидентами, гипотезами, стандартами).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            Примеры использования:
              relation_cli.py list T0001                        # Вывести список связей для задачи T0001
              relation_cli.py add T0001 I0002 RELATES_TO        # Добавить связь: T0001 связан с I0002
              relation_cli.py add T0001 T0002 BLOCKS "Блокирует задачу по техническим причинам"
                                                               # Добавить связь с описанием
              relation_cli.py remove T0001 I0002               # Удалить связь между T0001 и I0002
              relation_cli.py search "улучшение производительности"
                                                               # Найти элементы по запросу
              relation_cli.py types                            # Вывести список доступных типов связей
        """)
    )
    
    # Создаем подпарсеры для разных команд
    subparsers = parser.add_subparsers(dest="command", help="Команда")
    
    # Парсер для команды list
    list_parser = subparsers.add_parser("list", help="Вывести список связей для элемента")
    list_parser.add_argument("item_id", help="Идентификатор элемента")
    list_parser.set_defaults(func=list_command)
    
    # Парсер для команды add
    add_parser = subparsers.add_parser("add", help="Добавить связь между элементами")
    add_parser.add_argument("source_id", help="Идентификатор исходного элемента")
    add_parser.add_argument("target_id", help="Идентификатор целевого элемента")
    add_parser.add_argument("relation_type", help="Тип связи (например, RELATES_TO, BLOCKS)")
    add_parser.add_argument("description", nargs="?", help="Описание связи")
    add_parser.set_defaults(func=add_command)
    
    # Парсер для команды remove
    remove_parser = subparsers.add_parser("remove", help="Удалить связь между элементами")
    remove_parser.add_argument("source_id", help="Идентификатор исходного элемента")
    remove_parser.add_argument("target_id", help="Идентификатор целевого элемента")
    remove_parser.set_defaults(func=remove_command)
    
    # Парсер для команды search
    search_parser = subparsers.add_parser("search", help="Найти элементы по запросу")
    search_parser.add_argument("query", help="Строка запроса")
    search_parser.add_argument("--limit", type=int, default=10, help="Максимальное количество результатов")
    search_parser.set_defaults(func=search_command)
    
    # Парсер для команды types
    types_parser = subparsers.add_parser("types", help="Вывести список доступных типов связей")
    types_parser.set_defaults(func=types_command)
    
    # Парсим аргументы командной строки
    args = parser.parse_args()
    
    # Если команда не указана, выводим справку
    if not args.command:
        parser.print_help()
        return
    
    # Выполняем соответствующую функцию
    args.func(args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        color_print("\nПрерывание пользователем", Colors.YELLOW)
        sys.exit(0)
    except Exception as e:
        color_print(f"Ошибка: {e}", Colors.RED)
        sys.exit(1)