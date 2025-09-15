#!/usr/bin/env python3
"""
Модуль для интеграции системы кеширования и системы триггеров.
Обеспечивает эффективное взаимодействие этих двух ключевых подсистем.

Автор: AI Assistant
Дата: 21 мая 2025
"""

import os
import sys
import logging
from typing import Dict, List, Set, Tuple, Optional, Any, Union, Callable

# Настройка логирования
logger = logging.getLogger("cache_trigger_connector")

# Импортируем необходимые модули
try:
    from advising_platform.src.cache.critical_instructions_cache import CriticalInstructionsCache
    from advising_platform.src.cache.optimized_cache_manager import OptimizedCacheManager
    from advising_platform.src.core.registry.trigger_handler import TriggerHandler, TriggerType, TriggerContext, TriggerResult
    from advising_platform.src.core.document_scanner import scan_file_for_triggers, extract_task_data, extract_incident_data
    from advising_platform.src.cache.task_incident_triggers import (
        process_task_create_trigger,
        process_incident_create_trigger,
        process_hypothesis_create_trigger,
        process_file_duplication_check
    )
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    logger.error(f"Ошибка импорта модулей: {e}")
    IMPORTS_SUCCESSFUL = False


class CacheTriggerConnector:
    """
    Класс для интеграции системы кеширования и системы триггеров.
    Обеспечивает эффективное взаимодействие этих двух ключевых подсистем.
    """

    def __init__(self):
        """Инициализирует коннектор для интеграции системы кеширования и системы триггеров."""
        # Проверяем, что необходимые модули успешно импортированы
        if not IMPORTS_SUCCESSFUL:
            logger.error("Не удалось импортировать необходимые модули")
            raise ImportError("Не удалось импортировать необходимые модули")

        # Инициализируем необходимые компоненты
        self.cache = CriticalInstructionsCache()
        self.cache_manager = OptimizedCacheManager()
        self.trigger_handler = TriggerHandler()

        # Регистрируем обработчики триггеров
        self._register_trigger_handlers()

        # Флаг для отслеживания состояния подписки на события кеша
        self._subscribed_to_cache_events = False

        logger.info("Коннектор для интеграции системы кеширования и системы триггеров инициализирован")

    def _register_trigger_handlers(self) -> None:
        """Регистрирует обработчики триггеров."""
        # Регистрируем обработчики для различных типов триггеров
        self.trigger_handler.register_handler(TriggerType.TASK_CREATE, process_task_create_trigger)
        self.trigger_handler.register_handler(TriggerType.INCIDENT_CREATE, process_incident_create_trigger)
        self.trigger_handler.register_handler(TriggerType.HYPOTHESIS_CREATE, process_hypothesis_create_trigger)
        self.trigger_handler.register_handler(TriggerType.FILE_DUPLICATION_CHECK, process_file_duplication_check)

        logger.info("Обработчики триггеров успешно зарегистрированы")

    def subscribe_to_cache_events(self) -> bool:
        """
        Подписывается на события кеша для активации триггеров.
        
        Returns:
            bool: True, если подписка успешна, иначе False
        """
        # Проверяем, подписаны ли мы уже на события кеша
        if self._subscribed_to_cache_events:
            logger.warning("Коннектор уже подписан на события кеша")
            return True

        # Подписываемся на события кеша
        try:
            if hasattr(self.cache_manager, "subscribe_to_update_events"):
                self.cache_manager.subscribe_to_update_events(self._on_file_updated)
                logger.info("Подписка на события обновления кеша успешно установлена")
            else:
                # Если такого метода нет, пытаемся использовать другие механизмы
                logger.warning("Метод subscribe_to_update_events отсутствует в cache_manager")
                
                # Проверяем наличие других методов для подписки
                if hasattr(self.cache_manager, "set_update_callback"):
                    self.cache_manager.set_update_callback(self._on_file_updated)
                    logger.info("Подписка на события обновления кеша установлена через set_update_callback")
                else:
                    logger.error("Не найдены методы для подписки на события кеша")
                    return False

            self._subscribed_to_cache_events = True
            return True

        except Exception as e:
            logger.error(f"Ошибка при подписке на события кеша: {e}")
            return False

    def unsubscribe_from_cache_events(self) -> bool:
        """
        Отписывается от событий кеша.
        
        Returns:
            bool: True, если отписка успешна, иначе False
        """
        # Проверяем, подписаны ли мы на события кеша
        if not self._subscribed_to_cache_events:
            logger.warning("Коннектор не подписан на события кеша")
            return True

        # Отписываемся от событий кеша
        try:
            if hasattr(self.cache_manager, "unsubscribe_from_update_events"):
                self.cache_manager.unsubscribe_from_update_events(self._on_file_updated)
                logger.info("Отписка от событий обновления кеша успешно выполнена")
            else:
                # Если такого метода нет, пытаемся использовать другие механизмы
                logger.warning("Метод unsubscribe_from_update_events отсутствует в cache_manager")
                
                # Проверяем наличие других методов для отписки
                if hasattr(self.cache_manager, "clear_update_callback"):
                    self.cache_manager.clear_update_callback()
                    logger.info("Отписка от событий обновления кеша выполнена через clear_update_callback")
                else:
                    logger.error("Не найдены методы для отписки от событий кеша")
                    return False

            self._subscribed_to_cache_events = False
            return True

        except Exception as e:
            logger.error(f"Ошибка при отписке от событий кеша: {e}")
            return False

    def _on_file_updated(self, file_path: str, content: Optional[str] = None) -> None:
        """
        Обработчик события обновления файла в кеше.
        
        Args:
            file_path: Путь к обновленному файлу
            content: Содержимое файла (опционально)
        """
        logger.debug(f"Получено событие обновления файла в кеше: {file_path}")

        # Получаем содержимое файла, если оно не передано
        if content is None:
            try:
                # Пытаемся получить содержимое файла из кеша
                if hasattr(self.cache_manager, "get_file_content"):
                    content = self.cache_manager.get_file_content(file_path)
                # Если не удалось получить из кеша, пробуем прочитать из файловой системы
                if content is None and os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
            except Exception as e:
                logger.error(f"Ошибка при получении содержимого файла {file_path}: {e}")
                return

        # Если содержимое файла не удалось получить, выходим
        if content is None:
            logger.warning(f"Не удалось получить содержимое файла {file_path}, пропускаем обработку триггеров")
            return

        # Сканируем файл на наличие триггеров
        try:
            # Определяем тип файла по расширению и содержимому
            file_type = self._determine_file_type(file_path, content)
            
            # Обрабатываем файл в зависимости от его типа
            if file_type == "task":
                self._process_task_file(file_path, content)
            elif file_type == "incident":
                self._process_incident_file(file_path, content)
            elif file_type == "hypothesis":
                self._process_hypothesis_file(file_path, content)
            else:
                # Для неизвестного типа файла просто сканируем на наличие триггеров
                self._scan_file_for_triggers(file_path, content)
        
        except Exception as e:
            logger.error(f"Ошибка при обработке триггеров для файла {file_path}: {e}")

    def _determine_file_type(self, file_path: str, content: str) -> str:
        """
        Определяет тип файла по его содержимому и пути.
        
        Args:
            file_path: Путь к файлу
            content: Содержимое файла
            
        Returns:
            str: Тип файла ("task", "incident", "hypothesis" или "unknown")
        """
        # Проверяем по расширению
        if file_path.endswith(".md"):
            # Проверяем содержимое файла
            if "#" in content[:100]:
                first_heading = content.split("#")[1].strip() if len(content.split("#")) > 1 else ""
                
                if "задача" in first_heading.lower() or "task" in first_heading.lower():
                    return "task"
                elif "инцидент" in first_heading.lower() or "incident" in first_heading.lower():
                    return "incident"
                elif "гипотеза" in first_heading.lower() or "hypothesis" in first_heading.lower():
                    return "hypothesis"
        
        # Проверяем путь к файлу
        if "/tasks/" in file_path or "\\tasks\\" in file_path:
            return "task"
        elif "/incidents/" in file_path or "\\incidents\\" in file_path:
            return "incident"
        elif "/hypotheses/" in file_path or "\\hypotheses\\" in file_path:
            return "hypothesis"
        
        # Если не удалось определить тип, возвращаем unknown
        return "unknown"

    def _process_task_file(self, file_path: str, content: str) -> None:
        """
        Обрабатывает файл задачи.
        
        Args:
            file_path: Путь к файлу
            content: Содержимое файла
        """
        logger.debug(f"Обработка файла задачи: {file_path}")
        
        # Извлекаем данные о задаче
        task_data = extract_task_data(file_path, content)
        
        # Если данные не удалось извлечь, выходим
        if not task_data:
            logger.warning(f"Не удалось извлечь данные о задаче из файла {file_path}")
            return
        
        # Добавляем путь к файлу в данные
        task_data["file_path"] = file_path
        
        # Создаем контекст триггера
        trigger_context = TriggerContext(
            type=TriggerType.TASK_CREATE,
            data=task_data
        )
        
        # Обрабатываем триггер
        result = self.trigger_handler.handle_trigger(trigger_context)
        
        # Логируем результат
        if result and result.success:
            logger.info(f"Триггер задачи успешно обработан: {result.message}")
        else:
            logger.warning(f"Ошибка при обработке триггера задачи: {result.message if result else 'Неизвестная ошибка'}")

    def _process_incident_file(self, file_path: str, content: str) -> None:
        """
        Обрабатывает файл инцидента.
        
        Args:
            file_path: Путь к файлу
            content: Содержимое файла
        """
        logger.debug(f"Обработка файла инцидента: {file_path}")
        
        # Извлекаем данные об инциденте
        incident_data = extract_incident_data(file_path, content)
        
        # Если данные не удалось извлечь, выходим
        if not incident_data:
            logger.warning(f"Не удалось извлечь данные об инциденте из файла {file_path}")
            return
        
        # Добавляем путь к файлу в данные
        incident_data["file_path"] = file_path
        
        # Создаем контекст триггера
        trigger_context = TriggerContext(
            type=TriggerType.INCIDENT_CREATE,
            data=incident_data
        )
        
        # Обрабатываем триггер
        result = self.trigger_handler.handle_trigger(trigger_context)
        
        # Логируем результат
        if result and result.success:
            logger.info(f"Триггер инцидента успешно обработан: {result.message}")
        else:
            logger.warning(f"Ошибка при обработке триггера инцидента: {result.message if result else 'Неизвестная ошибка'}")

    def _process_hypothesis_file(self, file_path: str, content: str) -> None:
        """
        Обрабатывает файл гипотезы.
        
        Args:
            file_path: Путь к файлу
            content: Содержимое файла
        """
        logger.debug(f"Обработка файла гипотезы: {file_path}")
        
        # Извлекаем данные о гипотезе (используем тот же метод, что и для задач)
        hypothesis_data = extract_task_data(file_path, content)
        
        # Если данные не удалось извлечь, выходим
        if not hypothesis_data:
            logger.warning(f"Не удалось извлечь данные о гипотезе из файла {file_path}")
            return
        
        # Добавляем путь к файлу в данные
        hypothesis_data["file_path"] = file_path
        
        # Создаем контекст триггера
        trigger_context = TriggerContext(
            type=TriggerType.HYPOTHESIS_CREATE,
            data=hypothesis_data
        )
        
        # Обрабатываем триггер
        result = self.trigger_handler.handle_trigger(trigger_context)
        
        # Логируем результат
        if result and result.success:
            logger.info(f"Триггер гипотезы успешно обработан: {result.message}")
        else:
            logger.warning(f"Ошибка при обработке триггера гипотезы: {result.message if result else 'Неизвестная ошибка'}")

    def _scan_file_for_triggers(self, file_path: str, content: str) -> None:
        """
        Сканирует файл на наличие триггеров.
        
        Args:
            file_path: Путь к файлу
            content: Содержимое файла
        """
        logger.debug(f"Сканирование файла на наличие триггеров: {file_path}")
        
        # Получаем все триггеры задач и инцидентов из кеша
        task_triggers = self.cache.get_task_triggers()
        incident_triggers = self.cache.get_incident_triggers()
        
        # Проверяем наличие триггеров в содержимом файла
        for trigger in task_triggers:
            if trigger.keyword in content:
                logger.info(f"Найден триггер задачи '{trigger.keyword}' в файле {file_path}")
                # Здесь можно добавить логику для создания задачи
        
        for trigger in incident_triggers:
            if trigger.keyword in content:
                logger.info(f"Найден триггер инцидента '{trigger.keyword}' в файле {file_path}")
                # Здесь можно добавить логику для создания инцидента

    def scan_all_cached_files(self) -> Dict[str, Any]:
        """
        Сканирует все файлы в кеше на наличие триггеров.
        
        Returns:
            Dict[str, Any]: Результаты сканирования
        """
        logger.info("Сканирование всех файлов в кеше на наличие триггеров")
        
        # Получаем список всех файлов в кеше
        cached_files = []
        if hasattr(self.cache_manager, "get_all_cached_files"):
            cached_files = self.cache_manager.get_all_cached_files()
        elif hasattr(self.cache_manager, "get_cache_state"):
            cache_state = self.cache_manager.get_cache_state()
            if isinstance(cache_state, dict) and "files" in cache_state:
                cached_files = list(cache_state["files"].keys())
        
        # Если не удалось получить список файлов, выходим
        if not cached_files:
            logger.warning("Не удалось получить список файлов в кеше")
            return {"success": False, "error": "Не удалось получить список файлов в кеше"}
        
        # Статистика сканирования
        stats = {
            "total_files": len(cached_files),
            "processed_files": 0,
            "triggered_files": 0,
            "task_triggers": 0,
            "incident_triggers": 0,
            "hypothesis_triggers": 0,
            "errors": 0
        }
        
        # Сканируем каждый файл
        for file_path in cached_files:
            try:
                # Получаем содержимое файла из кеша
                content = None
                if hasattr(self.cache_manager, "get_file_content"):
                    content = self.cache_manager.get_file_content(file_path)
                
                # Если не удалось получить содержимое, пропускаем файл
                if content is None:
                    logger.warning(f"Не удалось получить содержимое файла {file_path} из кеша, пропускаем")
                    continue
                
                # Обрабатываем файл как событие обновления
                self._on_file_updated(file_path, content)
                
                # Увеличиваем счетчик обработанных файлов
                stats["processed_files"] += 1
                
            except Exception as e:
                logger.error(f"Ошибка при сканировании файла {file_path}: {e}")
                stats["errors"] += 1
        
        logger.info(f"Сканирование завершено. Обработано {stats['processed_files']} из {stats['total_files']} файлов")
        return {"success": True, "stats": stats}

    def verify_integration(self) -> Dict[str, Any]:
        """
        Проверяет корректность интеграции системы кеширования и системы триггеров.
        
        Returns:
            Dict[str, Any]: Результаты проверки
        """
        logger.info("Проверка корректности интеграции системы кеширования и системы триггеров")
        
        results = {
            "cache_available": False,
            "trigger_handler_available": False,
            "handlers_registered": False,
            "task_triggers_loaded": False,
            "incident_triggers_loaded": False,
            "success": False
        }
        
        # Проверяем доступность кеша
        try:
            # Проверяем методы кеша
            if hasattr(self.cache, "get_task_triggers") and hasattr(self.cache, "get_incident_triggers"):
                # Получаем триггеры задач и инцидентов из кеша
                task_triggers = self.cache.get_task_triggers()
                incident_triggers = self.cache.get_incident_triggers()
                
                # Проверяем, что триггеры загружены
                results["task_triggers_loaded"] = task_triggers is not None and len(task_triggers) > 0
                results["incident_triggers_loaded"] = incident_triggers is not None and len(incident_triggers) > 0
                
                # Если триггеры загружены, считаем кеш доступным
                results["cache_available"] = True
        except Exception as e:
            logger.error(f"Ошибка при проверке доступности кеша: {e}")
        
        # Проверяем доступность обработчика триггеров
        try:
            # Проверяем методы обработчика триггеров
            if hasattr(self.trigger_handler, "register_handler") and hasattr(self.trigger_handler, "handle_trigger"):
                results["trigger_handler_available"] = True
                
                # Проверяем регистрацию обработчиков
                if hasattr(self.trigger_handler, "_handlers"):
                    handlers = getattr(self.trigger_handler, "_handlers")
                    results["handlers_registered"] = isinstance(handlers, dict) and len(handlers) > 0
        except Exception as e:
            logger.error(f"Ошибка при проверке доступности обработчика триггеров: {e}")
        
        # Определяем успешность интеграции
        results["success"] = (
            results["cache_available"] and
            results["trigger_handler_available"] and
            results["handlers_registered"] and
            results["task_triggers_loaded"] and
            results["incident_triggers_loaded"]
        )
        
        # Добавляем дополнительную информацию
        if results["success"]:
            logger.info("Интеграция системы кеширования и системы триггеров работает корректно")
        else:
            logger.warning("Проблемы с интеграцией системы кеширования и системы триггеров")
        
        return results


# Глобальный экземпляр коннектора
_connector = None


def get_connector() -> CacheTriggerConnector:
    """
    Возвращает глобальный экземпляр коннектора.
    
    Returns:
        CacheTriggerConnector: Экземпляр коннектора
    """
    global _connector
    
    # Создаем коннектор, если он не существует
    if _connector is None:
        _connector = CacheTriggerConnector()
    
    return _connector