#!/usr/bin/env python
"""
Командный интерфейс для работы с задачами, инцидентами и стандартами.

Обеспечивает простой и интуитивно понятный способ создания и управления 
рабочими элементами прямо из командной строки.

Автор: AI Assistant
Дата: 20 мая 2025
"""

import os
import sys
import time
import json
import logging
import argparse
from typing import Dict, Any, Optional, List, Tuple, Union

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("task_cli")

# Цвета для вывода в терминал
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Функция для цветного вывода
def color_print(message: str, color: str = Colors.BLUE, bold: bool = False):
    """Выводит цветное сообщение в консоль."""
    if bold:
        print(f"{Colors.BOLD}{color}{message}{Colors.ENDC}")
    else:
        print(f"{color}{message}{Colors.ENDC}")

# Функция для mock report_progress
def mock_report_progress(data: Dict[str, str]) -> None:
    """Имитирует функцию report_progress."""
    color_print("\n🔔 Report Progress:", Colors.GREEN, True)
    color_print(f"  {data['summary']}", Colors.GREEN)
    return None

def use_optimized_verifier():
    """
    Интегрирует оптимизированный верификатор кеша для ускорения работы.
    
    Returns:
        True если успешно интегрирован, иначе False
    """
    try:
        # Проверяем, существует ли оптимизированный верификатор
        from advising_platform.src.core.cache_sync.optimized_verifier import OptimizedVerifier
        
        # Создаем и инициализируем верификатор
        color_print("Инициализация оптимизированного верификатора кеша...", Colors.BLUE)
        
        verifier = OptimizedVerifier(
            cache_path=".cache_state.json",
            base_dir=".",
            whitelist_dirs=[
                "projects",
                "incidents",
                "[todo · incidents]",
                "[standards .md]"
            ]
        )
        
        # Инициализируем кеш если нужно
        if not os.path.exists(".cache_state.json"):
            color_print("Инициализация кеша...", Colors.YELLOW)
            verifier.initialize_cache()
        
        # Проверяем и исправляем несоответствия
        color_print("Проверка состояния кеша...", Colors.BLUE)
        
        missing_in_cache, missing_in_filesystem, metadata_mismatch = verifier.verify_sync()
        
        if missing_in_cache or missing_in_filesystem or metadata_mismatch:
            color_print(
                f"Найдены несоответствия: "
                f"{len(missing_in_cache)} файлов отсутствуют в кеше, "
                f"{len(missing_in_filesystem)} записей отсутствуют в файловой системе, "
                f"{len(metadata_mismatch)} файлов имеют несоответствия метаданных", 
                Colors.YELLOW
            )
            
            color_print("Исправление несоответствий...", Colors.BLUE)
            success = verifier.fix_sync_issues()
            
            if success:
                color_print("Все несоответствия успешно исправлены", Colors.GREEN)
            else:
                color_print("Не удалось исправить все несоответствия", Colors.RED)
        else:
            color_print("Кеш полностью синхронизирован с файловой системой", Colors.GREEN)
        
        # Патчим глобальный CacheSyncVerifier для использования оптимизированной версии
        import advising_platform.src.core.cache_sync.cache_sync_verifier
        advising_platform.src.core.cache_sync.cache_sync_verifier.CacheSyncVerifier = OptimizedVerifier
        
        return True
    
    except ImportError:
        color_print("Оптимизированный верификатор не найден, используется стандартный", Colors.YELLOW)
        return False
    except Exception as e:
        color_print(f"Ошибка при интеграции оптимизированного верификатора: {e}", Colors.RED)
        return False

def create_task(args):
    """Создает новую задачу."""
    try:
        # Все задачи теперь записываются в центральный файл todo.md
        args.file = "[todo · incidents]/todo.md"
        
        # Если описание не указано, запрашиваем у пользователя
        if not args.description:
            print("\nВведите описание задачи (для завершения введите пустую строку):")
            lines = []
            while True:
                line = input()
                if not line:
                    break
                lines.append(line)
            args.description = "\n".join(lines)
        
        # Создаем задачу
        start_time = time.time()
        color_print(f"Создание задачи '{args.title}'...", Colors.BLUE)
        
        result = create_task_trigger(
            title=args.title,
            description=args.description,
            author=args.author,
            assignee=args.assignee,
            file_path=args.file,
            report_progress_func=mock_report_progress
        )
        
        end_time = time.time()
        
        if result and result.success and result.item:
            color_print(f"✅ Задача успешно создана за {end_time - start_time:.2f} секунд", Colors.GREEN, True)
            color_print(f"ID: {result.item.id}", Colors.GREEN)
            color_print(f"Заголовок: {result.item.title}", Colors.GREEN)
            color_print(f"Статус: {result.item.status.value}", Colors.GREEN)
            
            if result.item.file_path and os.path.exists(result.item.file_path):
                color_print(f"Файл: {result.item.file_path}", Colors.GREEN)
            
            return 0
        else:
            color_print("❌ Ошибка при создании задачи", Colors.RED, True)
            if result and result.errors:
                for error in result.errors:
                    color_print(f"  - {error}", Colors.RED)
            return 1
    
    except Exception as e:
        color_print(f"❌ Произошла ошибка: {e}", Colors.RED)
        return 1

def create_incident(args):
    """Создает новый инцидент."""
    try:
        # Все инциденты теперь записываются в центральный файл ai.incidents.md
        args.file = "[todo · incidents]/ai.incidents.md"
        
        # Если описание не указано, запрашиваем у пользователя
        if not args.description:
            print("\nВведите описание инцидента (для завершения введите пустую строку):")
            lines = []
            while True:
                line = input()
                if not line:
                    break
                lines.append(line)
            args.description = "\n".join(lines)
        
        # Создаем инцидент
        start_time = time.time()
        color_print(f"Создание инцидента '{args.title}'...", Colors.BLUE)
        
        result = create_incident_trigger(
            title=args.title,
            description=args.description,
            author=args.author,
            assignee=args.assignee,
            file_path=args.file,
            report_progress_func=mock_report_progress
        )
        
        end_time = time.time()
        
        if result and result.success and result.item:
            color_print(f"✅ Инцидент успешно создан за {end_time - start_time:.2f} секунд", Colors.GREEN, True)
            color_print(f"ID: {result.item.id}", Colors.GREEN)
            color_print(f"Заголовок: {result.item.title}", Colors.GREEN)
            color_print(f"Статус: {result.item.status.value}", Colors.GREEN)
            
            if result.item.file_path and os.path.exists(result.item.file_path):
                color_print(f"Файл: {result.item.file_path}", Colors.GREEN)
            
            return 0
        else:
            color_print("❌ Ошибка при создании инцидента", Colors.RED, True)
            if result and result.errors:
                for error in result.errors:
                    color_print(f"  - {error}", Colors.RED)
            return 1
    
    except Exception as e:
        color_print(f"❌ Произошла ошибка: {e}", Colors.RED)
        return 1

def create_standard(args):
    """Создает новый стандарт."""
    try:
        from advising_platform.src.core.registry.trigger_handler import create_standard as create_standard_trigger
        
        # Если описание не указано, запрашиваем у пользователя
        if not args.description:
            print("\nВведите описание стандарта (для завершения введите пустую строку):")
            lines = []
            while True:
                line = input()
                if not line:
                    break
                lines.append(line)
            args.description = "\n".join(lines)
        
        # Создаем стандарт
        start_time = time.time()
        color_print(f"Создание стандарта '{args.title}'...", Colors.BLUE)
        
        result = create_standard_trigger(
            title=args.title,
            description=args.description,
            author=args.author,
            file_path=args.file,
            standard_type=args.type,
            report_progress_func=mock_report_progress
        )
        
        end_time = time.time()
        
        if result and result.success and result.item:
            color_print(f"✅ Стандарт успешно создан за {end_time - start_time:.2f} секунд", Colors.GREEN, True)
            color_print(f"ID: {result.item.id}", Colors.GREEN)
            color_print(f"Заголовок: {result.item.title}", Colors.GREEN)
            color_print(f"Статус: {result.item.status.value}", Colors.GREEN)
            
            if result.item.file_path and os.path.exists(result.item.file_path):
                color_print(f"Файл: {result.item.file_path}", Colors.GREEN)
            
            return 0
        else:
            color_print("❌ Ошибка при создании стандарта", Colors.RED, True)
            if result and result.errors:
                for error in result.errors:
                    color_print(f"  - {error}", Colors.RED)
            return 1
    
    except Exception as e:
        color_print(f"❌ Произошла ошибка: {e}", Colors.RED)
        return 1

def list_items(args):
    """Выводит список элементов."""
    try:
        from advising_platform.src.core.registry.task_registry import get_registry, WorkItemType, WorkItemStatus
        
        # Получаем реестр
        registry = get_registry()
        
        # Определяем тип элемента для фильтрации
        item_type = None
        if args.type:
            try:
                item_type = WorkItemType(args.type)
            except ValueError:
                color_print(f"❌ Неизвестный тип элемента: {args.type}", Colors.RED)
                return 1
        
        # Определяем статус для фильтрации
        status = None
        if args.status:
            try:
                status = WorkItemStatus(args.status)
            except ValueError:
                color_print(f"❌ Неизвестный статус: {args.status}", Colors.RED)
                return 1
        
        # Ищем элементы
        items = registry.find_items(
            type=item_type,
            status=status,
            author=args.author,
            assignee=args.assignee,
            search_term=args.search
        )
        
        if not items:
            color_print("Элементы не найдены", Colors.YELLOW)
            return 0
        
        # Группируем элементы по типу
        grouped_items = {}
        for item in items:
            if item.type.value not in grouped_items:
                grouped_items[item.type.value] = []
            grouped_items[item.type.value].append(item)
        
        # Выводим элементы
        color_print(f"Найдено {len(items)} элементов:", Colors.BLUE, True)
        
        for type_name, type_items in grouped_items.items():
            color_print(f"\n{type_name.upper()} ({len(type_items)}):", Colors.BOLD + Colors.BLUE)
            
            for item in type_items:
                # Определяем цвет в зависимости от статуса
                status_color = Colors.BLUE
                if item.status.value in ["done", "resolved", "approved", "validated"]:
                    status_color = Colors.GREEN
                elif item.status.value in ["in_progress", "investigating", "testing", "review_pending"]:
                    status_color = Colors.YELLOW
                elif item.status.value in ["blocked", "deprecated", "superseded", "invalidated"]:
                    status_color = Colors.RED
                
                # Выводим информацию об элементе
                color_print(f"  {item.id}: {item.title}", status_color)
                color_print(f"    Статус: {item.status.value}", status_color)
                
                if item.assignee:
                    color_print(f"    Ответственный: {item.assignee}", Colors.BLUE)
                
                if item.file_path:
                    file_exists = os.path.exists(item.file_path)
                    file_status = "существует" if file_exists else "отсутствует"
                    color_print(f"    Файл: {item.file_path} ({file_status})", Colors.BLUE)
                
                # Выводим связи
                if item.relations:
                    color_print(f"    Связи ({len(item.relations)}):", Colors.BLUE)
                    for i, relation in enumerate(item.relations[:3], 1):
                        color_print(f"      {i}. {relation.relation_type.value} -> {relation.target_id}", Colors.BLUE)
                    
                    if len(item.relations) > 3:
                        color_print(f"      ... и еще {len(item.relations) - 3}", Colors.BLUE)
        
        return 0
    
    except Exception as e:
        color_print(f"❌ Произошла ошибка: {e}", Colors.RED)
        return 1

def show_item(args):
    """Показывает детальную информацию об элементе."""
    try:
        from advising_platform.src.core.registry.task_registry import get_registry
        
        # Получаем реестр
        registry = get_registry()
        
        # Получаем элемент
        item = registry.get_item(args.id)
        
        if not item:
            color_print(f"❌ Элемент с ID {args.id} не найден", Colors.RED)
            return 1
        
        # Выводим информацию об элементе
        color_print(f"\nЭлемент {item.id} ({item.type.value}):", Colors.BLUE, True)
        color_print(f"Заголовок: {item.title}", Colors.BLUE)
        color_print(f"Статус: {item.status.value}", Colors.BLUE)
        
        if item.author:
            color_print(f"Автор: {item.author}", Colors.BLUE)
        
        if item.assignee:
            color_print(f"Ответственный: {item.assignee}", Colors.BLUE)
        
        if item.created_at:
            created_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(item.created_at))
            color_print(f"Создан: {created_at}", Colors.BLUE)
        
        if item.updated_at:
            updated_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(item.updated_at))
            color_print(f"Обновлен: {updated_at}", Colors.BLUE)
        
        if item.due_date:
            due_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(item.due_date))
            color_print(f"Срок выполнения: {due_date}", Colors.BLUE)
        
        if item.tags:
            color_print(f"Теги: {', '.join(item.tags)}", Colors.BLUE)
        
        if item.file_path:
            file_exists = os.path.exists(item.file_path)
            file_status = "существует" if file_exists else "отсутствует"
            color_print(f"Файл: {item.file_path} ({file_status})", Colors.BLUE)
            
            # Выводим содержимое файла
            if file_exists and args.content:
                color_print("\nСодержимое файла:", Colors.BLUE, True)
                try:
                    with open(item.file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    print(content)
                except Exception as e:
                    color_print(f"❌ Ошибка при чтении файла: {e}", Colors.RED)
        
        # Выводим связи
        if item.relations:
            color_print(f"\nСвязи ({len(item.relations)}):", Colors.BLUE, True)
            for i, relation in enumerate(item.relations, 1):
                related_item = registry.get_item(relation.target_id)
                related_title = related_item.title if related_item else "???"
                color_print(f"  {i}. {relation.relation_type.value} -> {relation.target_id} ({related_title})", Colors.BLUE)
        
        # Выводим свойства
        if item.properties:
            color_print("\nСвойства:", Colors.BLUE, True)
            for key, value in item.properties.items():
                color_print(f"  {key}: {value}", Colors.BLUE)
        
        return 0
    
    except Exception as e:
        color_print(f"❌ Произошла ошибка: {e}", Colors.RED)
        return 1

def update_item(args):
    """Обновляет существующий элемент."""
    try:
        from advising_platform.src.core.registry.work_item_processor import get_processor
        from advising_platform.src.core.registry.task_registry import WorkItemStatus
        
        # Получаем процессор
        processor = get_processor()
        
        # Проверяем существование элемента
        if not processor.registry.get_item(args.id):
            color_print(f"❌ Элемент с ID {args.id} не найден", Colors.RED)
            return 1
        
        # Преобразуем статус, если указан
        status = None
        if args.status:
            try:
                status = WorkItemStatus(args.status)
            except ValueError:
                color_print(f"❌ Неизвестный статус: {args.status}", Colors.RED)
                return 1
        
        # Собираем обновления
        updates = {}
        
        if args.title:
            updates["title"] = args.title
        
        if args.description:
            updates["description"] = args.description
        
        if status:
            updates["status"] = status
        
        if args.assignee:
            updates["assignee"] = args.assignee
        
        if args.file:
            updates["file_path"] = args.file
        
        if not updates:
            color_print("❌ Не указаны параметры для обновления", Colors.RED)
            return 1
        
        # Обновляем элемент
        start_time = time.time()
        color_print(f"Обновление элемента {args.id}...", Colors.BLUE)
        
        result = processor.update_work_item(
            item_id=args.id,
            **updates
        )
        
        end_time = time.time()
        
        if result and result.success and result.item:
            color_print(f"✅ Элемент успешно обновлен за {end_time - start_time:.2f} секунд", Colors.GREEN, True)
            color_print(f"ID: {result.item.id}", Colors.GREEN)
            color_print(f"Заголовок: {result.item.title}", Colors.GREEN)
            color_print(f"Статус: {result.item.status.value}", Colors.GREEN)
            
            if result.item.file_path and os.path.exists(result.item.file_path):
                color_print(f"Файл: {result.item.file_path}", Colors.GREEN)
            
            return 0
        else:
            color_print("❌ Ошибка при обновлении элемента", Colors.RED, True)
            if result and result.errors:
                for error in result.errors:
                    color_print(f"  - {error}", Colors.RED)
            return 1
    
    except Exception as e:
        color_print(f"❌ Произошла ошибка: {e}", Colors.RED)
        return 1

def add_relation(args):
    """Добавляет связь между элементами."""
    try:
        from advising_platform.src.core.registry.task_registry import get_registry, WorkItemRelationType
        
        # Получаем реестр
        registry = get_registry()
        
        # Проверяем существование элементов
        source_item = registry.get_item(args.source)
        target_item = registry.get_item(args.target)
        
        if not source_item:
            color_print(f"❌ Элемент с ID {args.source} не найден", Colors.RED)
            return 1
        
        if not target_item:
            color_print(f"❌ Элемент с ID {args.target} не найден", Colors.RED)
            return 1
        
        # Преобразуем тип связи
        try:
            relation_type = WorkItemRelationType(args.type)
        except ValueError:
            color_print(f"❌ Неизвестный тип связи: {args.type}", Colors.RED)
            color_print("Доступные типы связей:", Colors.BLUE)
            for relation_type in WorkItemRelationType:
                color_print(f"  - {relation_type.value}: {relation_type.name}", Colors.BLUE)
            return 1
        
        # Добавляем связь
        color_print(f"Добавление связи {args.source} -> {args.target} ({args.type})...", Colors.BLUE)
        
        success = registry.add_relation(
            source_id=args.source,
            target_id=args.target,
            relation_type=relation_type,
            description=args.description
        )
        
        if success:
            color_print("✅ Связь успешно добавлена", Colors.GREEN, True)
            return 0
        else:
            color_print("❌ Ошибка при добавлении связи", Colors.RED, True)
            return 1
    
    except Exception as e:
        color_print(f"❌ Произошла ошибка: {e}", Colors.RED)
        return 1

def remove_relation(args):
    """Удаляет связь между элементами."""
    try:
        from advising_platform.src.core.registry.task_registry import get_registry, WorkItemRelationType
        
        # Получаем реестр
        registry = get_registry()
        
        # Проверяем существование элементов
        source_item = registry.get_item(args.source)
        target_item = registry.get_item(args.target)
        
        if not source_item:
            color_print(f"❌ Элемент с ID {args.source} не найден", Colors.RED)
            return 1
        
        if not target_item:
            color_print(f"❌ Элемент с ID {args.target} не найден", Colors.RED)
            return 1
        
        # Преобразуем тип связи, если указан
        relation_type = None
        if args.type:
            try:
                relation_type = WorkItemRelationType(args.type)
            except ValueError:
                color_print(f"❌ Неизвестный тип связи: {args.type}", Colors.RED)
                return 1
        
        # Удаляем связь
        color_print(f"Удаление связи {args.source} -> {args.target}...", Colors.BLUE)
        
        success = registry.remove_relation(
            source_id=args.source,
            target_id=args.target,
            relation_type=relation_type
        )
        
        if success:
            color_print("✅ Связь успешно удалена", Colors.GREEN, True)
            return 0
        else:
            color_print("❌ Ошибка при удалении связи или связь не существует", Colors.RED, True)
            return 1
    
    except Exception as e:
        color_print(f"❌ Произошла ошибка: {e}", Colors.RED)
        return 1

def check_cache(args):
    """Проверяет и при необходимости исправляет целостность кеша."""
    try:
        # Импортируем верификатор кеша
        try:
            from advising_platform.src.core.cache_sync.cache_sync_verifier import CacheSyncVerifier
            
            color_print("Запуск верификатора кеша...", Colors.BLUE)
            
            # Создаем верификатор с нужными параметрами
            if hasattr(CacheSyncVerifier, '__init__') and 'cache_path' in CacheSyncVerifier.__init__.__code__.co_varnames:
                # Для оптимизированного верификатора
                verifier = CacheSyncVerifier(
                    cache_path=".cache_state.json",
                    base_dir="."
                )
                color_print("Используется оптимизированный верификатор кеша", Colors.GREEN)
            else:
                # Для стандартного верификатора
                verifier = CacheSyncVerifier(
                    cache_paths=[".cache_state.json"],
                    base_dir="."
                )
                color_print("Используется стандартный верификатор кеша", Colors.YELLOW)
                
        except ImportError as e:
            color_print(f"Ошибка при импорте верификатора кеша: {e}", Colors.RED)
            return 1
        
        # Проверяем состояние кеша
        start_time = time.time()
        color_print("Проверка состояния кеша...", Colors.BLUE)
        
        missing_in_cache, missing_in_filesystem, metadata_mismatch = verifier.verify_sync()
        
        mid_time = time.time()
        color_print(f"Проверка завершена за {mid_time - start_time:.2f} секунд", Colors.BLUE)
        
        if missing_in_cache or missing_in_filesystem or metadata_mismatch:
            color_print(
                f"Найдены несоответствия: "
                f"{len(missing_in_cache)} файлов отсутствуют в кеше, "
                f"{len(missing_in_filesystem)} записей отсутствуют в файловой системе, "
                f"{len(metadata_mismatch)} файлов имеют несоответствия метаданных", 
                Colors.YELLOW
            )
            
            if args.fix:
                color_print("Исправление несоответствий...", Colors.BLUE)
                success = verifier.fix_sync_issues()
                
                end_time = time.time()
                color_print(f"Исправление завершено за {end_time - mid_time:.2f} секунд", Colors.BLUE)
                
                if success:
                    color_print("✅ Все несоответствия успешно исправлены", Colors.GREEN, True)
                else:
                    color_print("❌ Не удалось исправить все несоответствия", Colors.RED, True)
            else:
                color_print("Для исправления несоответствий используйте флаг --fix", Colors.BLUE)
        else:
            color_print("✅ Кеш полностью синхронизирован с файловой системой", Colors.GREEN, True)
        
        return 0
    
    except Exception as e:
        color_print(f"❌ Произошла ошибка: {e}", Colors.RED)
        return 1

def main():
    """Основная функция."""
    # Пытаемся использовать оптимизированный верификатор
    use_optimized_verifier()
    
    # Настройка парсера аргументов
    parser = argparse.ArgumentParser(
        description="Командный интерфейс для работы с задачами, инцидентами и стандартами",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  # Создание задачи
  python task_cli.py task create --title "Новая задача" --description "Описание задачи"
  
  # Создание инцидента
  python task_cli.py incident create --title "Новый инцидент" --description "Описание инцидента"
  
  # Вывод списка элементов
  python task_cli.py list
  
  # Просмотр информации об элементе
  python task_cli.py show T0001
  
  # Обновление статуса элемента
  python task_cli.py update T0001 --status "in_progress"
  
  # Добавление связи между элементами
  python task_cli.py relation add --source T0001 --target I0001 --type "relates_to"
        """
    )
    
    # Добавляем команды
    subparsers = parser.add_subparsers(dest="command", help="Команда для выполнения")
    
    # Команда task - работа с задачами
    task_parser = subparsers.add_parser("task", help="Работа с задачами")
    task_subparsers = task_parser.add_subparsers(dest="subcommand", help="Подкоманда для работы с задачами")
    
    # Команда task create - создание задачи
    task_create_parser = task_subparsers.add_parser("create", help="Создание задачи")
    task_create_parser.add_argument("--title", required=True, help="Заголовок задачи")
    task_create_parser.add_argument("--description", help="Описание задачи")
    task_create_parser.add_argument("--author", default="AI Assistant", help="Автор задачи")
    task_create_parser.add_argument("--assignee", help="Ответственный за задачу")
    task_create_parser.add_argument("--file", help="Путь к файлу с описанием задачи")
    task_create_parser.set_defaults(func=create_task)
    
    # Команда incident - работа с инцидентами
    incident_parser = subparsers.add_parser("incident", help="Работа с инцидентами")
    incident_subparsers = incident_parser.add_subparsers(dest="subcommand", help="Подкоманда для работы с инцидентами")
    
    # Команда incident create - создание инцидента
    incident_create_parser = incident_subparsers.add_parser("create", help="Создание инцидента")
    incident_create_parser.add_argument("--title", required=True, help="Заголовок инцидента")
    incident_create_parser.add_argument("--description", help="Описание инцидента")
    incident_create_parser.add_argument("--author", default="AI Assistant", help="Автор инцидента")
    incident_create_parser.add_argument("--assignee", help="Ответственный за инцидент")
    incident_create_parser.add_argument("--file", help="Путь к файлу с описанием инцидента")
    incident_create_parser.set_defaults(func=create_incident)
    
    # Команда standard - работа со стандартами
    standard_parser = subparsers.add_parser("standard", help="Работа со стандартами")
    standard_subparsers = standard_parser.add_subparsers(dest="subcommand", help="Подкоманда для работы со стандартами")
    
    # Команда standard create - создание стандарта
    standard_create_parser = standard_subparsers.add_parser("create", help="Создание стандарта")
    standard_create_parser.add_argument("--title", required=True, help="Заголовок стандарта")
    standard_create_parser.add_argument("--description", help="Описание стандарта")
    standard_create_parser.add_argument("--author", default="AI Assistant", help="Автор стандарта")
    standard_create_parser.add_argument("--file", help="Путь к файлу стандарта")
    standard_create_parser.add_argument("--type", default="basic", choices=["basic", "process", "code", "design"], help="Тип стандарта")
    standard_create_parser.set_defaults(func=create_standard)
    
    # Команда list - вывод списка элементов
    list_parser = subparsers.add_parser("list", help="Вывод списка элементов")
    list_parser.add_argument("--type", help="Тип элемента (task, incident, hypothesis, standard)")
    list_parser.add_argument("--status", help="Статус элемента (backlog, todo, in_progress, done, etc.)")
    list_parser.add_argument("--author", help="Автор элемента")
    list_parser.add_argument("--assignee", help="Ответственный за элемент")
    list_parser.add_argument("--search", help="Поисковый запрос")
    list_parser.set_defaults(func=list_items)
    
    # Команда show - просмотр информации об элементе
    show_parser = subparsers.add_parser("show", help="Просмотр информации об элементе")
    show_parser.add_argument("id", help="Идентификатор элемента")
    show_parser.add_argument("--content", action="store_true", help="Показать содержимое файла")
    show_parser.set_defaults(func=show_item)
    
    # Команда update - обновление элемента
    update_parser = subparsers.add_parser("update", help="Обновление элемента")
    update_parser.add_argument("id", help="Идентификатор элемента")
    update_parser.add_argument("--title", help="Новый заголовок элемента")
    update_parser.add_argument("--description", help="Новое описание элемента")
    update_parser.add_argument("--status", help="Новый статус элемента")
    update_parser.add_argument("--assignee", help="Новый ответственный за элемент")
    update_parser.add_argument("--file", help="Новый путь к файлу элемента")
    update_parser.set_defaults(func=update_item)
    
    # Команда relation - работа со связями
    relation_parser = subparsers.add_parser("relation", help="Работа со связями между элементами")
    relation_subparsers = relation_parser.add_subparsers(dest="subcommand", help="Подкоманда для работы со связями")
    
    # Команда relation add - добавление связи
    relation_add_parser = relation_subparsers.add_parser("add", help="Добавление связи")
    relation_add_parser.add_argument("--source", required=True, help="Идентификатор исходного элемента")
    relation_add_parser.add_argument("--target", required=True, help="Идентификатор целевого элемента")
    relation_add_parser.add_argument("--type", required=True, help="Тип связи (relates_to, blocks, depends_on, etc.)")
    relation_add_parser.add_argument("--description", help="Описание связи")
    relation_add_parser.set_defaults(func=add_relation)
    
    # Команда relation remove - удаление связи
    relation_remove_parser = relation_subparsers.add_parser("remove", help="Удаление связи")
    relation_remove_parser.add_argument("--source", required=True, help="Идентификатор исходного элемента")
    relation_remove_parser.add_argument("--target", required=True, help="Идентификатор целевого элемента")
    relation_remove_parser.add_argument("--type", help="Тип связи (если не указан, удаляются все связи)")
    relation_remove_parser.set_defaults(func=remove_relation)
    
    # Команда cache - проверка кеша
    cache_parser = subparsers.add_parser("cache", help="Проверка и исправление целостности кеша")
    cache_parser.add_argument("--fix", action="store_true", help="Исправить найденные несоответствия")
    cache_parser.set_defaults(func=check_cache)
    
    # Разбор аргументов
    args = parser.parse_args()
    
    if hasattr(args, "func"):
        return args.func(args)
    else:
        if args.command == "task" and not args.subcommand:
            task_parser.print_help()
        elif args.command == "incident" and not args.subcommand:
            incident_parser.print_help()
        elif args.command == "standard" and not args.subcommand:
            standard_parser.print_help()
        elif args.command == "relation" and not args.subcommand:
            relation_parser.print_help()
        else:
            parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())