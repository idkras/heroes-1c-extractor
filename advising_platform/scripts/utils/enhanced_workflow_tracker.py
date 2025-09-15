"""
Расширенный трекер рабочих процессов для мониторинга кеша и статистики задач.

Этот скрипт дополняет стандартные рабочие процессы следующей функциональностью:
1. Вывод информации о рассинхронизации кеша
2. Предоставление статистики по типам документов в кеше
3. Отображение статистики по статусам задач и инцидентов
4. Публикация ссылки на веб-сервис

Автор: AI Assistant
Дата: 20 мая 2025
"""

import os
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("enhanced_workflow_tracker")

# Константы
CACHE_STATE_FILE = ".cache_state.json"
DETAILED_STATE_FILE = ".cache_detailed_state.json"
REGISTRY_FILE = "registry.json"
TODO_FILE = "[todo · incidents]/todo.md"
INCIDENTS_DIR = "[todo · incidents]/ai.incidents"
WEB_SERVICE_URL = "http://localhost:5000"
API_SERVICE_URL = "http://localhost:5003"

def get_cache_stats() -> Dict[str, Any]:
    """
    Получает статистику кеша.
    
    Returns:
        Dict: Статистика кеша
    """
    stats = {
        "total_files": 0,
        "by_extension": {},
        "by_directory": {},
        "in_sync": True,
        "out_of_sync_files": 0
    }
    
    try:
        if os.path.exists(CACHE_STATE_FILE):
            with open(CACHE_STATE_FILE, 'r', encoding='utf-8') as f:
                cache_state = json.load(f)
                
            files = cache_state.get("files", {})
            stats["total_files"] = len(files)
            
            # Подсчет по расширениям
            for file_path in files:
                ext = os.path.splitext(file_path)[1].lower()
                stats["by_extension"][ext] = stats["by_extension"].get(ext, 0) + 1
                
                # Подсчет по директориям
                dir_path = os.path.dirname(file_path)
                root_dir = dir_path.split('/')[0] if '/' in dir_path else dir_path
                stats["by_directory"][root_dir] = stats["by_directory"].get(root_dir, 0) + 1
            
            # Проверка синхронизации
            # Если есть дополнительная информация о синхронизации
            if "sync_status" in cache_state:
                stats["in_sync"] = cache_state["sync_status"].get("in_sync", True)
                stats["out_of_sync_files"] = cache_state["sync_status"].get("out_of_sync_files", 0)
                
        # Получаем более детальную информацию, если доступна
        if os.path.exists(DETAILED_STATE_FILE):
            with open(DETAILED_STATE_FILE, 'r', encoding='utf-8') as f:
                detailed_state = json.load(f)
                
            if "missing_in_cache" in detailed_state:
                stats["missing_in_cache"] = len(detailed_state["missing_in_cache"])
                stats["in_sync"] = False
                
            if "missing_in_filesystem" in detailed_state:
                stats["missing_in_filesystem"] = len(detailed_state["missing_in_filesystem"])
                stats["in_sync"] = False
                
            if "size_mismatch" in detailed_state:
                stats["size_mismatch"] = len(detailed_state["size_mismatch"])
                stats["in_sync"] = False
                
            stats["out_of_sync_files"] = (
                stats.get("missing_in_cache", 0) + 
                stats.get("missing_in_filesystem", 0) + 
                stats.get("size_mismatch", 0)
            )
            
    except Exception as e:
        logger.error(f"Ошибка при получении статистики кеша: {e}")
        stats["error"] = str(e)
        
    return stats

def get_task_stats() -> Dict[str, Any]:
    """
    Получает статистику задач и инцидентов из файлов todo.md и реестра.
    
    Returns:
        Dict: Статистика задач и инцидентов
    """
    stats = {
        "tasks": {
            "total": 0,
            "by_status": {},
            "by_priority": {},
            "by_assignee": {}
        },
        "incidents": {
            "total": 0,
            "by_status": {},
            "by_severity": {},
            "by_assignee": {}
        }
    }
    
    try:
        # Получаем статистику из реестра
        if os.path.exists(REGISTRY_FILE):
            with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            
            for item_id, item in registry.items():
                item_type = item.get("type", "unknown")
                
                if item_type == "task":
                    stats["tasks"]["total"] += 1
                    
                    # Статус
                    status = item.get("status", "unknown")
                    stats["tasks"]["by_status"][status] = stats["tasks"]["by_status"].get(status, 0) + 1
                    
                    # Приоритет (если есть)
                    if "properties" in item and "priority" in item["properties"]:
                        priority = item["properties"]["priority"]
                        stats["tasks"]["by_priority"][priority] = stats["tasks"]["by_priority"].get(priority, 0) + 1
                    
                    # Ответственный
                    assignee = item.get("assignee", "не назначен")
                    stats["tasks"]["by_assignee"][assignee] = stats["tasks"]["by_assignee"].get(assignee, 0) + 1
                
                elif item_type == "incident":
                    stats["incidents"]["total"] += 1
                    
                    # Статус
                    status = item.get("status", "unknown")
                    stats["incidents"]["by_status"][status] = stats["incidents"]["by_status"].get(status, 0) + 1
                    
                    # Приоритет/серьезность (если есть)
                    if "properties" in item and "severity" in item["properties"]:
                        severity = item["properties"]["severity"]
                        stats["incidents"]["by_severity"][severity] = stats["incidents"]["by_severity"].get(severity, 0) + 1
                    
                    # Ответственный
                    assignee = item.get("assignee", "не назначен")
                    stats["incidents"]["by_assignee"][assignee] = stats["incidents"]["by_assignee"].get(assignee, 0) + 1
        
        # Пробуем извлечь статистику из todo.md (может содержать более актуальную информацию)
        if os.path.exists(TODO_FILE):
            with open(TODO_FILE, 'r', encoding='utf-8') as f:
                todo_content = f.read()
            
            # Пытаемся найти таблицу статистики
            stats_section_start = todo_content.find("## 📊 Статистика задач")
            if stats_section_start != -1:
                stats_section_end = todo_content.find("##", stats_section_start + 1)
                if stats_section_end == -1:
                    stats_section_end = len(todo_content)
                
                stats_section = todo_content[stats_section_start:stats_section_end]
                
                # Извлекаем значения из таблицы
                import re
                
                # Пример: ищем цифры в строке "| Стандартные | 12 | 49 | 23 | 84 | 3.7 дня |"
                standard_tasks_match = re.search(r'\|\s*Стандартные\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)', stats_section)
                if standard_tasks_match:
                    stats["todo_stats"] = {
                        "standard": {
                            "open": int(standard_tasks_match.group(1)),
                            "in_progress": int(standard_tasks_match.group(2)),
                            "done": int(standard_tasks_match.group(3)),
                            "total": int(standard_tasks_match.group(4))
                        }
                    }
                
                # Ищем строку с гипотезами
                hypothesis_match = re.search(r'\|\s*Гипотезы\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)', stats_section)
                if hypothesis_match:
                    stats["todo_stats"]["hypothesis"] = {
                        "open": int(hypothesis_match.group(1)),
                        "in_progress": int(hypothesis_match.group(2)),
                        "done": int(hypothesis_match.group(3)),
                        "total": int(hypothesis_match.group(4))
                    }
                
                # Ищем строку с общими статистиками
                total_match = re.search(r'\|\s*\*\*Всего\*\*\s*\|\s*\*\*(\d+)\*\*\s*\|\s*\*\*(\d+)\*\*\s*\|\s*\*\*(\d+)\*\*\s*\|\s*\*\*(\d+)\*\*', stats_section)
                if total_match:
                    stats["todo_stats"]["total"] = {
                        "open": int(total_match.group(1)),
                        "in_progress": int(total_match.group(2)),
                        "done": int(total_match.group(3)),
                        "total": int(total_match.group(4))
                    }
                
                # Ищем успешные гипотезы
                successful_hypothesis_match = re.search(r'Успешных гипотез: (\d+) из (\d+) \((\d+)%\)', stats_section)
                if successful_hypothesis_match:
                    stats["todo_stats"]["successful_hypothesis"] = {
                        "count": int(successful_hypothesis_match.group(1)),
                        "total": int(successful_hypothesis_match.group(2)),
                        "percentage": int(successful_hypothesis_match.group(3))
                    }
                
                # Ищем неудачные гипотезы
                failed_hypothesis_match = re.search(r'Неудачных гипотез: (\d+) из (\d+) \((\d+)%\)', stats_section)
                if failed_hypothesis_match:
                    stats["todo_stats"]["failed_hypothesis"] = {
                        "count": int(failed_hypothesis_match.group(1)),
                        "total": int(failed_hypothesis_match.group(2)),
                        "percentage": int(failed_hypothesis_match.group(3))
                    }
        
    except Exception as e:
        logger.error(f"Ошибка при получении статистики задач: {e}")
        stats["error"] = str(e)
        
    return stats

def count_files_in_filesystem() -> Dict[str, Any]:
    """
    Подсчитывает количество файлов в файловой системе.
    
    Returns:
        Dict: Статистика файлов в файловой системе
    """
    stats = {
        "total_files": 0,
        "by_extension": {},
        "by_directory": {}
    }
    
    try:
        # Получаем список всех файлов в файловой системе (исключая некоторые директории)
        excluded_dirs = {'.git', '.venv', '__pycache__', 'node_modules', '.replit'}
        
        for root, dirs, files in os.walk('.', topdown=True):
            # Исключаем определенные директории
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
            
            for file in files:
                stats["total_files"] += 1
                
                # Статистика по расширениям
                ext = os.path.splitext(file)[1].lower()
                stats["by_extension"][ext] = stats["by_extension"].get(ext, 0) + 1
                
                # Статистика по директориям первого уровня
                top_dir = root.split(os.sep)[1] if len(root.split(os.sep)) > 1 else root
                top_dir = top_dir if top_dir else '.'
                
                stats["by_directory"][top_dir] = stats["by_directory"].get(top_dir, 0) + 1
    
    except Exception as e:
        logger.error(f"Ошибка при подсчете файлов в файловой системе: {e}")
        stats["error"] = str(e)
    
    return stats

def generate_report() -> Dict[str, Any]:
    """
    Генерирует полный отчет о состоянии системы.
    
    Returns:
        Dict: Полный отчет
    """
    report = {
        "timestamp": datetime.now().isoformat(),
        "web_service_url": WEB_SERVICE_URL,
        "api_service_url": API_SERVICE_URL,
        "cache_stats": get_cache_stats(),
        "task_stats": get_task_stats(),
        "filesystem_stats": count_files_in_filesystem()
    }
    
    # Добавляем вывод в консоль для отображения в чате
    print_report(report)
    
    return report

def print_report(report: Dict[str, Any]) -> None:
    """
    Выводит отчет в консоль.
    
    Args:
        report: Отчет для вывода
    """
    print("\n" + "="*80)
    print(f"📊 ОТЧЕТ О СОСТОЯНИИ СИСТЕМЫ [{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}]")
    print("="*80)
    
    # Ссылки на сервисы
    print(f"\n🌐 Веб-сервис: {report['web_service_url']}")
    print(f"🔌 API-сервис: {report['api_service_url']}")
    
    # Состояние кеша
    cache_stats = report["cache_stats"]
    print("\n📂 СОСТОЯНИЕ КЕША:")
    print(f"  Всего файлов в кеше: {cache_stats.get('total_files', 0)}")
    
    # Статус синхронизации
    if cache_stats.get("in_sync", True):
        print("  ✅ Кеш и файловая система синхронизированы")
    else:
        print("  ⚠️ ОБНАРУЖЕНА РАССИНХРОНИЗАЦИЯ МЕЖДУ КЕШЕМ И ФАЙЛОВОЙ СИСТЕМОЙ:")
        print(f"    - Файлов, отсутствующих в кеше: {cache_stats.get('missing_in_cache', 0)}")
        print(f"    - Файлов, отсутствующих в файловой системе: {cache_stats.get('missing_in_filesystem', 0)}")
        print(f"    - Файлов с несоответствием размера: {cache_stats.get('size_mismatch', 0)}")
        print(f"    - Всего файлов вне синхронизации: {cache_stats.get('out_of_sync_files', 0)}")
    
    # Распределение по типам документов
    print("\n  Распределение по типам документов:")
    for ext, count in sorted(cache_stats.get("by_extension", {}).items(), key=lambda x: x[1], reverse=True)[:5]:
        if ext:
            print(f"    - {ext}: {count}")
    
    # Распределение по директориям
    print("\n  Распределение по директориям:")
    for dir_name, count in sorted(cache_stats.get("by_directory", {}).items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"    - {dir_name}: {count}")
    
    # Статистика задач из todo.md
    task_stats = report["task_stats"]
    if "todo_stats" in task_stats:
        todo_stats = task_stats["todo_stats"]
        print("\n📋 СТАТИСТИКА ЗАДАЧ (из todo.md):")
        
        if "total" in todo_stats:
            total = todo_stats["total"]
            print(f"  Всего задач: {total.get('total', 0)}")
            print(f"  По статусам:")
            print(f"    - Открыто: {total.get('open', 0)}")
            print(f"    - В работе: {total.get('in_progress', 0)}")
            print(f"    - Выполнено: {total.get('done', 0)}")
        
        if "hypothesis" in todo_stats:
            hypothesis = todo_stats["hypothesis"]
            print(f"\n  Гипотезы:")
            print(f"    - Всего: {hypothesis.get('total', 0)}")
            print(f"    - Открыто: {hypothesis.get('open', 0)}")
            print(f"    - В работе: {hypothesis.get('in_progress', 0)}")
            print(f"    - Выполнено: {hypothesis.get('done', 0)}")
        
        if "successful_hypothesis" in todo_stats:
            successful = todo_stats["successful_hypothesis"]
            print(f"    - Успешных: {successful.get('count', 0)} из {successful.get('total', 0)} ({successful.get('percentage', 0)}%)")
        
        if "failed_hypothesis" in todo_stats:
            failed = todo_stats["failed_hypothesis"]
            print(f"    - Неудачных: {failed.get('count', 0)} из {failed.get('total', 0)} ({failed.get('percentage', 0)}%)")
    
    # Статистика задач из реестра
    print("\n📋 СТАТИСТИКА ЗАДАЧ (из реестра):")
    print(f"  Всего задач: {task_stats['tasks']['total']}")
    
    if task_stats['tasks']['by_status']:
        print("  По статусам:")
        for status, count in sorted(task_stats['tasks']['by_status'].items(), key=lambda x: x[1], reverse=True):
            print(f"    - {status}: {count}")
    
    # Статистика инцидентов
    print("\n🚨 СТАТИСТИКА ИНЦИДЕНТОВ:")
    print(f"  Всего инцидентов: {task_stats['incidents']['total']}")
    
    if task_stats['incidents']['by_status']:
        print("  По статусам:")
        for status, count in sorted(task_stats['incidents']['by_status'].items(), key=lambda x: x[1], reverse=True):
            print(f"    - {status}: {count}")
    
    # Статистика файловой системы
    fs_stats = report["filesystem_stats"]
    print("\n💾 СТАТИСТИКА ФАЙЛОВОЙ СИСТЕМЫ:")
    print(f"  Всего файлов: {fs_stats.get('total_files', 0)}")
    
    # Консистентность кеша и файловой системы
    cache_files = cache_stats.get('total_files', 0)
    fs_files = fs_stats.get('total_files', 0)
    print(f"\n🔄 СРАВНЕНИЕ КЕША И ФАЙЛОВОЙ СИСТЕМЫ:")
    print(f"  Файлов в кеше: {cache_files}")
    print(f"  Файлов на диске: {fs_files}")
    
    if cache_files == 0 or fs_files == 0:
        print("  ⚠️ Невозможно сравнить кеш и файловую систему - нет данных о количестве файлов")
    else:
        coverage = (cache_files / fs_files) * 100 if fs_files > 0 else 0
        print(f"  Покрытие файлов кешем: {coverage:.1f}%")
        
        if coverage < 90:
            print("  ⚠️ Покрытие файлов кешем ниже рекомендуемого (90%)")
        else:
            print("  ✅ Покрытие файлов кешем в пределах нормы")
    
    print("\n" + "="*80)

def create_task_for_workflow_enhancement() -> None:
    """
    Создает задачу для улучшения рабочего процесса через механизм создания задач.
    """
    try:
        # Импортируем функции для создания задач
        from advising_platform.src.core.registry.trigger_handler import create_task
        
        # Функция имитации report_progress
        def mock_report_progress(data):
            logger.info(f"Отчет о прогрессе: {data}")
            print(f"\n📋 Отчет о прогрессе: {data}")
        
        # Создаем задачу-гипотезу
        task_title = "Гипотеза расширения рабочего процесса для мониторинга и оповещений"
        task_description = """Расширение рабочего процесса для автоматического вывода в чат:
1. Информации о рассинхронизации кеша
2. Статистики по типам документов в кеше
3. Статистики по статусам задач и инцидентов
4. Ссылок на веб-сервис и API-сервис

Гипотеза: регулярное информирование о текущем состоянии системы повысит осведомленность пользователей и снизит количество проблем, связанных с рассинхронизацией кеша."""

        result = create_task(
            title=task_title,
            description=task_description,
            status="in_progress",
            author="AI Assistant",
            assignee="SysAdmin",
            file_path="projects/tasks/hypothesis_workflow_enhancement.md",
            tags=["hypothesis", "workflow", "monitoring"],
            properties={"priority": "high", "hypothesis_type": "improvement"},
            report_progress_func=mock_report_progress
        )
        
        if hasattr(result, 'success') and result.success:
            logger.info(f"Задача-гипотеза успешно создана: {result.item.id}")
            print(f"\n✅ Создана задача-гипотеза: {task_title} [{result.item.id}]")
        else:
            logger.error(f"Ошибка при создании задачи-гипотезы: {result.errors if hasattr(result, 'errors') else 'Неизвестная ошибка'}")
            print(f"\n❌ Ошибка при создании задачи-гипотезы")
            
    except Exception as e:
        logger.error(f"Исключение при создании задачи-гипотезы: {e}")
        print(f"\n❌ Ошибка при создании задачи-гипотезы: {e}")

def main():
    """Основная функция скрипта."""
    logger.info("=== Запуск расширенного трекера рабочих процессов ===")
    
    try:
        # Генерируем отчет о состоянии системы
        report = generate_report()
        
        # Создаем задачу-гипотезу для улучшения рабочего процесса
        create_task_for_workflow_enhancement()
        
        logger.info("=== Завершение работы расширенного трекера рабочих процессов ===")
        
    except Exception as e:
        logger.error(f"Ошибка при выполнении трекера рабочих процессов: {e}")
        print(f"\n❌ Ошибка при выполнении трекера: {e}")

if __name__ == "__main__":
    main()