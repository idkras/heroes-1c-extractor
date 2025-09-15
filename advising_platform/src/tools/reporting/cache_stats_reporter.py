#!/usr/bin/env python3
"""
Модуль для формирования и отправки отчетов о состоянии кеша в чат-интерфейс.
Предоставляет функциональность для сбора статистики о документах в кеше,
определения рекомендуемых задач и формирования отчетов для пользователя.
"""

import os
import sys
import json
import logging
import traceback
from typing import Dict, List, Any, Optional
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("cache_stats_reporter")

# Путь к текущему файлу
current_dir = os.path.dirname(os.path.abspath(__file__))

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(current_dir, "../../../..")))

# Импортируем функцию отчета из report_interface
from advising_platform.src.tools.reporting.report_interface import report_progress, report_cache_statistics

# Функция для получения статистики о документах в кеше
def get_cache_document_counts() -> Dict[str, Any]:
    """
    Получает статистику о количестве документов разных типов в кеше.
    
    Returns:
        Dict[str, Any]: Словарь со статистикой (общее количество, по типам)
    """
    cache_stats_reporter = CacheStatsReporter()
    return cache_stats_reporter.get_cache_statistics()

class CacheStatsReporter:
    """Класс для сбора и отправки статистики кеша в чат."""
    
    def __init__(self):
        """Инициализация."""
        self.cache_state_file = os.path.abspath(os.path.join(current_dir, "../../../../.cache_state.json"))
        self.cache_detail_file = os.path.abspath(os.path.join(current_dir, "../../../../.cache_detailed_state.pickle"))
        self.last_report_time = None
        self.report_interval = 3600  # Периодичность автоматического отчета в секундах (1 час)
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """
        Получает статистику кеша.
        
        Returns:
            Dict[str, Any]: Статистика кеша
        """
        try:
            # Проверяем наличие файла состояния кеша
            if not os.path.exists(self.cache_state_file):
                logger.warning(f"Файл состояния кеша не найден: {self.cache_state_file}")
                return {
                    "total_documents": 0,
                    "updated": datetime.now().strftime("%d.%m.%Y %H:%M"),
                    "error": "Файл состояния кеша не найден"
                }
            
            # Загружаем состояние кеша
            with open(self.cache_state_file, 'r', encoding='utf-8') as f:
                cache_state = json.load(f)
            
            # В файле .cache_state.json файлы хранятся в виде ключей на верхнем уровне,
            # а не в поле "files" - исправляем это
            # Анализируем содержимое кеша: все ключи словаря кроме служебных полей
            cache_files = {}
            service_fields = ["last_sync", "stats", "version"]
            
            for key, value in cache_state.items():
                if key not in service_fields and isinstance(value, dict):
                    cache_files[key] = value
            
            total_documents = len(cache_files)
            logger.info(f"Найдено {total_documents} документов в кеше")
            
            # Получаем статистику по типам документов
            doc_types = {
                "tasks": 0,
                "incidents": 0,
                "standards": 0,
                "hypotheses": 0,
                "others": 0
            }
            
            for file_path in cache_files:
                if "/todo/" in file_path or file_path.startswith("todo/"):
                    doc_types["tasks"] += 1
                elif "/incidents/" in file_path or file_path.startswith("incidents/"):
                    doc_types["incidents"] += 1
                elif "/standards/" in file_path or file_path.startswith("[standards .md]/"):
                    doc_types["standards"] += 1
                elif "/hypotheses/" in file_path or "/hypothesis/" in file_path:
                    doc_types["hypotheses"] += 1
                else:
                    doc_types["others"] += 1
            
            # Вычисляем процентное соотношение
            percentages = {}
            if total_documents > 0:
                for doc_type, count in doc_types.items():
                    percentages[doc_type] = round((count / total_documents) * 100, 1)
            
            # Формируем объект статистики
            statistics = {
                "total_documents": total_documents,
                "updated": datetime.now().strftime("%d.%m.%Y %H:%M"),
                "document_types": doc_types,
                "percentages": percentages,
                "last_updated_files": self._get_last_updated_files(cache_files, limit=5)
            }
            
            return statistics
        
        except Exception as e:
            logger.error(f"Ошибка при получении статистики кеша: {e}")
            traceback.print_exc()
            return {
                "total_documents": 0,
                "updated": datetime.now().strftime("%d.%m.%Y %H:%M"),
                "error": f"Ошибка при получении статистики кеша: {str(e)}"
            }
    
    def _get_last_updated_files(self, cache_files: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Получает список последних обновленных файлов.
        
        Args:
            cache_files: Словарь файлов из кеша
            limit: Максимальное количество файлов в списке
            
        Returns:
            List[Dict[str, Any]]: Список последних обновленных файлов
        """
        try:
            # Создаем список файлов с временем последнего обновления
            files_with_time = []
            
            for file_path, file_info in cache_files.items():
                # Пропускаем скрытые файлы и директории
                if os.path.basename(file_path).startswith('.'):
                    continue
                
                # Пропускаем служебные папки
                skip_dirs = [".cache", "__pycache__", ".git", "node_modules"]
                should_skip = any(skip_dir in file_path for skip_dir in skip_dirs)
                if should_skip:
                    continue
                
                # Получаем время последнего изменения
                last_modified = file_info.get("last_modified", 0)
                
                # Получаем имя файла без директории
                file_name = os.path.basename(file_path)
                
                # Если это Markdown-файл или текстовый файл, получаем его описание
                if file_path.endswith('.md') or file_path.endswith('.txt'):
                    # Получаем краткое описание файла (первую строку или заголовок)
                    description = self._get_file_description(file_path)
                else:
                    description = f"Файл: {file_name}"
                
                files_with_time.append({
                    "path": file_path,
                    "name": file_name,
                    "description": description,
                    "last_modified": last_modified
                })
            
            # Сортируем файлы по времени последнего изменения (от новых к старым)
            files_with_time.sort(key=lambda x: x["last_modified"], reverse=True)
            
            # Возвращаем ограниченное количество файлов
            return files_with_time[:limit]
        
        except Exception as e:
            logger.error(f"Ошибка при получении последних файлов: {e}")
            traceback.print_exc()
            return []
    
    def _get_file_description(self, file_path: str) -> str:
        """
        Получает краткое описание файла (первую строку или заголовок).
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            str: Краткое описание файла
        """
        try:
            # Проверяем существование файла
            full_path = os.path.abspath(os.path.join(current_dir, "../../../../", file_path))
            if not os.path.exists(full_path):
                return "Нет описания"
            
            # Открываем файл и читаем первые строки
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Ищем заголовок (строку, начинающуюся с #)
            for line in lines:
                line = line.strip()
                if line.startswith('# '):
                    return line[2:]  # Возвращаем текст без символов #
            
            # Если заголовок не найден, возвращаем первую непустую строку
            for line in lines:
                line = line.strip()
                if line:
                    # Ограничиваем длину строки
                    if len(line) > 50:
                        return line[:47] + "..."
                    return line
            
            return "Нет описания"
        
        except Exception as e:
            logger.error(f"Ошибка при получении описания файла: {e}")
            return "Ошибка чтения"
    
    def get_recommended_tasks(self, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Получает список рекомендуемых задач для работы.
        
        Args:
            limit: Максимальное количество задач в списке
            
        Returns:
            List[Dict[str, Any]]: Список рекомендуемых задач
        """
        try:
            # Поиск всех файлов задач
            tasks_dir = os.path.abspath(os.path.join(current_dir, "../../../../todo"))
            if not os.path.exists(tasks_dir) or not os.path.isdir(tasks_dir):
                logger.warning(f"Директория задач не найдена: {tasks_dir}")
                return []
            
            tasks = []
            
            # Получаем список файлов в директории задач
            for file_name in os.listdir(tasks_dir):
                if not file_name.endswith('.md'):
                    continue
                
                file_path = os.path.join(tasks_dir, file_name)
                
                # Анализируем содержимое файла задачи
                task_info = self._parse_task_file(file_path)
                if task_info:
                    tasks.append(task_info)
            
            # Сортируем задачи по приоритету и статусу
            tasks.sort(key=lambda x: (
                0 if x["priority"] == "Высокий" else (1 if x["priority"] == "Средний" else 2),
                0 if x["status"] == "Активна" else 1,
                x["created"]  # Затем по дате создания (более новые выше)
            ))
            
            # Возвращаем только активные задачи
            active_tasks = [task for task in tasks if task["status"] == "Активна"]
            
            # Добавляем объяснение, почему задача рекомендована
            for task in active_tasks:
                if task["priority"] == "Высокий":
                    task["reason"] = "Критическая для улучшения взаимодействия пользователя с системой"
                elif "интеграция" in task["title"].lower() or "api" in task["title"].lower():
                    task["reason"] = "Важная для взаимодействия с внешними системами"
                elif "оптимизация" in task["title"].lower() or "ускорение" in task["title"].lower():
                    task["reason"] = "Текущий процесс недостаточно эффективен при большом объеме данных"
                elif "улучшение" in task["title"].lower() or "расширение" in task["title"].lower():
                    task["reason"] = "Нужны дополнительные функции для повышения удобства использования"
                else:
                    task["reason"] = "Важная задача для развития проекта"
            
            return active_tasks[:limit]
        
        except Exception as e:
            logger.error(f"Ошибка при получении рекомендуемых задач: {e}")
            traceback.print_exc()
            return []
    
    def _parse_task_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Парсит файл задачи и извлекает информацию.
        
        Args:
            file_path: Путь к файлу задачи
            
        Returns:
            Optional[Dict[str, Any]]: Информация о задаче или None, если не удалось распарсить
        """
        try:
            # Открываем файл задачи
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Получаем имя файла без расширения
            file_name = os.path.basename(file_path)
            
            # Инициализируем информацию о задаче
            task_info = {
                "path": file_path,
                "file_name": file_name,
                "title": "Без названия",
                "priority": "Средний",
                "status": "Активна",
                "created": datetime.now().strftime("%d.%m.%Y"),
                "description": ""
            }
            
            # Извлекаем заголовок (название задачи)
            title_match = content.split('\n')[0] if content else ""
            if title_match.startswith('# '):
                task_info["title"] = title_match[2:].strip()
            
            # Извлекаем приоритет
            if "## Приоритет:" in content:
                priority_line = content.split("## Приоритет:")[1].split('\n')[0].strip()
                task_info["priority"] = priority_line
            
            # Извлекаем статус
            if "## Статус:" in content:
                status_line = content.split("## Статус:")[1].split('\n')[0].strip()
                task_info["status"] = status_line
            
            # Извлекаем дату создания
            if "## Дата создания:" in content:
                date_line = content.split("## Дата создания:")[1].split('\n')[0].strip()
                task_info["created"] = date_line
            
            # Извлекаем описание
            if "## Описание" in content:
                description_text = content.split("## Описание")[1].split('##')[0].strip()
                # Ограничиваем длину описания
                if len(description_text) > 200:
                    description_text = description_text[:197] + "..."
                task_info["description"] = description_text
            
            return task_info
        
        except Exception as e:
            logger.error(f"Ошибка при парсинге файла задачи {file_path}: {e}")
            return None
    
    def send_cache_statistics_report(self) -> None:
        """
        Формирует и отправляет отчет о статистике кеша в чат.
        """
        # Получаем статистику кеша
        statistics = self.get_cache_statistics()
        
        # Извлекаем необходимые данные
        total = statistics.get('total_documents', 0)
        doc_types = statistics.get("document_types", {})
        
        # Преобразуем типы документов для использования в отчете
        document_types_dict = {
            "Задачи": doc_types.get("tasks", 0), 
            "Инциденты": doc_types.get("incidents", 0), 
            "Стандарты": doc_types.get("standards", 0), 
            "Гипотезы": doc_types.get("hypotheses", 0), 
            "Другие документы": doc_types.get("others", 0)
        }
        
        # Вычисляем процентное соотношение документов в кеше и на диске
        # Определяем общее количество документов на диске
        disk_files_count = 0
        try:
            # Считаем только файлы с нужными расширениями и исключаем служебные директории
            disk_files_count = sum(1 for _ in self._iterate_disk_files())
            logger.info(f"Найдено {disk_files_count} документов на диске")
        except Exception as e:
            logger.error(f"Ошибка при подсчете файлов на диске: {e}")
            traceback.print_exc()
        
        # Используем функцию из импортированного интерфейса для формирования отчета
        from advising_platform.src.tools.reporting.report_interface import report_cache_statistics as send_report
        
        send_report(
            total=total,
            added=0,
            updated=0,
            deleted=0,
            time_taken=0,
            operation_type="status",
            document_types=document_types_dict
        )
        
        # Если есть расхождение между количеством файлов на диске и в кеше,
        # отправляем дополнительное предупреждение
        if disk_files_count > 0 and total < disk_files_count:
            disk_cache_mismatch = f"⚠️ Внимание: обнаружено расхождение между файлами на диске ({disk_files_count}) и в кеше ({total}).\n"\
                                 f"Необходима синхронизация кеша с файловой системой."
            report_progress({"summary": disk_cache_mismatch}, force_output=True)
    
    def _iterate_disk_files(self):
        """
        Итератор по файлам на диске, исключая служебные директории.
        
        Yields:
            str: Путь к файлу
        """
        base_dir = os.path.abspath(os.path.join(current_dir, "../../../.."))
        
        # Директории, которые стоит исключить из анализа
        exclude_dirs = [
            ".git", "__pycache__", ".cache", "node_modules", 
            "logs/reports", "logs/state", "logs/backups"
        ]
        
        # Расширения файлов для подсчета
        include_extensions = [".md", ".txt", ".py", ".js", ".html", ".json"]
        
        for root, dirs, files in os.walk(base_dir):
            # Исключаем служебные директории
            dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
            
            for file in files:
                # Исключаем скрытые файлы и файлы без нужных расширений
                if not file.startswith('.') and any(file.endswith(ext) for ext in include_extensions):
                    yield os.path.join(root, file)
        
        # Запоминаем время отчета
        self.last_report_time = datetime.now()
    
    def report_cached_documents(self) -> None:
        """
        Формирует и отправляет отчет о последних документах в кеше.
        """
        # Получаем статистику кеша
        statistics = self.get_cache_statistics()
        
        # Получаем список последних обновленных файлов
        last_files = statistics.get("last_updated_files", [])
        
        # Формируем текст отчета
        summary = f"🔍 Последние документы в кеше:\n"
        
        # Добавляем информацию о последних файлах
        if last_files:
            for i, file_info in enumerate(last_files, 1):
                path = file_info.get("path", "")
                description = file_info.get("description", "Нет описания")
                
                summary += f"{i}. \"{description}\" ({path})\n"
        else:
            summary += "Нет данных о последних документах\n"
        
        # Отправляем отчет
        report_progress({"summary": summary})
    
    def report_recommended_tasks(self) -> None:
        """
        Формирует и отправляет отчет о рекомендуемых задачах.
        """
        # Получаем список рекомендуемых задач
        tasks = self.get_recommended_tasks()
        
        # Формируем текст отчета
        summary = f"📋 Рекомендуемые задачи для работы:\n"
        
        # Добавляем информацию о задачах
        if tasks:
            for i, task in enumerate(tasks, 1):
                title = task.get("title", "Без названия")
                priority = task.get("priority", "Средний")
                reason = task.get("reason", "Важная задача для проекта")
                
                summary += f"{i}. ⭐ \"{title}\" (Приоритет: {priority})\n"
                summary += f"   Причина: {reason}\n\n"
        else:
            summary += "Нет активных задач для рекомендации\n"
        
        # Отправляем отчет
        report_progress({"summary": summary})
    
    def report_all(self) -> None:
        """
        Формирует и отправляет полный отчет о кеше и рекомендуемых задачах.
        """
        self.report_cache_statistics()
        self.report_cached_documents()
        self.report_recommended_tasks()
    
    def check_periodic_report(self) -> None:
        """
        Проверяет необходимость отправки периодического отчета.
        """
        now = datetime.now()
        
        # Если отчет ещё не отправлялся или прошло достаточно времени
        if not self.last_report_time or \
           (now - self.last_report_time).total_seconds() > self.report_interval:
            logger.info("Отправка периодического отчета о состоянии кеша")
            self.report_all()
            self.last_report_time = now


# Создаем глобальный экземпляр репортера
cache_stats_reporter = CacheStatsReporter()

def report_cache_statistics():
    """Отправляет отчет о статистике кеша."""
    cache_stats_reporter.report_cache_statistics()

def report_cached_documents():
    """Отправляет отчет о документах в кеше."""
    cache_stats_reporter.report_cached_documents()

def report_recommended_tasks():
    """Отправляет отчет о рекомендуемых задачах."""
    cache_stats_reporter.report_recommended_tasks()

def report_all_cache_info():
    """Отправляет полный отчет о кеше и задачах."""
    cache_stats_reporter.report_all()

def check_periodic_report():
    """Проверяет необходимость отправки периодического отчета."""
    cache_stats_reporter.check_periodic_report()


# Выполняем инициализацию при импорте модуля
def init():
    """Инициализирует модуль."""
    logger.info("Инициализация модуля отчетов о статистике кеша")
    
    # Отправляем первоначальный отчет
    try:
        cache_stats_reporter.report_all()
    except Exception as e:
        logger.error(f"Ошибка при отправке первоначального отчета: {e}")
        traceback.print_exc()
    
    return True


if __name__ == "__main__":
    # При запуске модуля как скрипта отправляем полный отчет
    report_all_cache_info()