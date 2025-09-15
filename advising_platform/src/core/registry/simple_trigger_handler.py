"""
Упрощенный модуль обработчика триггеров для задач и инцидентов.
Предоставляет основные функции для обработки различных типов триггеров.
"""

import logging
import traceback
import time
from typing import Any, Dict, List, Optional, Callable

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TriggerType:
    """JTBD:
Я (разработчик) хочу использовать функциональность класса TriggerType, чтобы эффективно решать соответствующие задачи в системе.
    
    Типы триггеров."""
    TASK_CREATE = "task_create"  
    TASK_UPDATE = "task_update"  
    INCIDENT_CREATE = "incident_create"  
    INCIDENT_UPDATE = "incident_update"  
    HYPOTHESIS_CREATE = "hypothesis_create"  
    HYPOTHESIS_UPDATE = "hypothesis_update"  
    STANDARD_CREATE = "standard_create"  
    STANDARD_UPDATE = "standard_update"  
    CACHE_SYNC = "cache_sync"  
    PERIODIC_CHECK = "periodic_check"
    FILE_DUPLICATION_CHECK = "file_duplication_check"

class TriggerResult:
    """JTBD:
Я (разработчик) хочу использовать функциональность класса TriggerResult, чтобы эффективно решать соответствующие задачи в системе.
    
    Результат обработки триггера."""
    def __init__(self, success: bool = False, message: str = "", data: Optional[Dict[str, Any]] = None):
        self.success = success
        self.message = message
        self.data = data or {}
        
    def __str__(self) -> str:
        return f"TriggerResult(success={self.success}, message={self.message}, data={self.data})"

class TriggerContext:
    """JTBD:
Я (разработчик) хочу использовать функциональность класса TriggerContext, чтобы эффективно решать соответствующие задачи в системе.
    
    Контекст триггера."""
    def __init__(self, trigger_type: str, data: Dict[str, Any], timestamp: Optional[float] = None, source: Optional[str] = None):
        self.trigger_type = trigger_type
        self.data = data
        self.timestamp = timestamp or time.time()
        self.source = source
        
    def __str__(self) -> str:
        return f"TriggerContext(type={self.trigger_type}, source={self.source}, timestamp={self.timestamp})"

class SimpleTriggerHandler:
    """JTBD:
Я (разработчик) хочу использовать функциональность класса SimpleTriggerHandler, чтобы эффективно решать соответствующие задачи в системе.
    
    Упрощенный обработчик триггеров."""
    
    _instance = None
    
    def __init__(self, report_progress_func: Optional[Callable] = None):
        """
        Инициализирует упрощенный обработчик триггеров.
        
        Args:
            report_progress_func: Функция для отчета о прогрессе
        """
        self.handlers = {}
        self.report_progress_func = report_progress_func
        self.archived_tasks_count = 0
        self.task_statistics = {}
        
        # Регистрируем обработчики по умолчанию
        self._register_default_handlers()
        
    def _register_default_handlers(self):
        """Регистрирует обработчики по умолчанию."""
        self.register_handler(TriggerType.TASK_CREATE, self._handle_task_create)
        self.register_handler(TriggerType.TASK_UPDATE, self._handle_task_update)
        self.register_handler(TriggerType.INCIDENT_CREATE, self._handle_incident_create)
        self.register_handler(TriggerType.INCIDENT_UPDATE, self._handle_incident_update)
        self.register_handler(TriggerType.HYPOTHESIS_CREATE, self._handle_hypothesis_create)
        self.register_handler(TriggerType.HYPOTHESIS_UPDATE, self._handle_hypothesis_update)
        
    def register_handler(self, trigger_type: str, handler_func: Callable) -> bool:
        """
        Регистрирует функцию-обработчик для указанного типа триггера.
        
        Args:
            trigger_type: Тип триггера
            handler_func: Функция-обработчик
            
        Returns:
            bool: True, если регистрация успешна, иначе False
        """
        if trigger_type in self.handlers:
            logger.warning(f"Обработчик для триггера {trigger_type} уже зарегистрирован, он будет перезаписан")
            
        self.handlers[trigger_type] = handler_func
        return True
        
    def trigger(self, context: TriggerContext) -> bool:
        """
        Запускает обработку триггера.
        
        Args:
            context: Контекст триггера
            
        Returns:
            bool: True, если обработка прошла успешно, иначе False
        """
        result = self.handle_trigger(context)
        return result.success
        
    def handle_trigger(self, context: TriggerContext) -> TriggerResult:
        """
        Обрабатывает триггер.
        
        Args:
            context: Контекст триггера
            
        Returns:
            TriggerResult: Результат обработки триггера
        """
        trigger_type = context.trigger_type
        
        if trigger_type not in self.handlers:
            logger.error(f"Неизвестный тип триггера: {trigger_type}")
            return TriggerResult(success=False, message=f"Неизвестный тип триггера: {trigger_type}")
            
        try:
            handler = self.handlers[trigger_type]
            result = handler(context)
            
            # Если обработчик вернул не TriggerResult, а что-то другое, оборачиваем в TriggerResult
            if not isinstance(result, TriggerResult):
                result = TriggerResult(success=True, message="Триггер обработан", data={"result": result})
                
            return result
        except Exception as e:
            logger.error(f"Ошибка при обработке триггера {trigger_type}: {e}")
            traceback.print_exc()
            return TriggerResult(success=False, message=f"Ошибка при обработке триггера: {e}")
    
    def _handle_task_create(self, context: TriggerContext) -> TriggerResult:
        """
        Обрабатывает триггер создания задачи.
        
        Args:
            context: Контекст триггера
            
        Returns:
            TriggerResult: Результат обработки триггера
        """
        try:
            # Извлекаем данные из контекста
            data = context.data
            title = data.get("title", "")
            
            # Имитация обработки
            if self.report_progress_func:
                self.report_progress_func({
                    "event": "task_created",
                    "title": title,
                    "message": f"Задача '{title}' создана"
                })
                
            return TriggerResult(
                success=True,
                message=f"Задача '{title}' успешно создана",
                data={"title": title}
            )
        except Exception as e:
            logger.error(f"Ошибка при обработке триггера создания задачи: {e}")
            traceback.print_exc()
            return TriggerResult(success=False, message=f"Ошибка при обработке триггера создания задачи: {e}")
    
    def _handle_task_update(self, context: TriggerContext) -> TriggerResult:
        """
        Обрабатывает триггер обновления задачи.
        
        Args:
            context: Контекст триггера
            
        Returns:
            TriggerResult: Результат обработки триггера
        """
        return TriggerResult(success=True, message="Задача обновлена")
    
    def _handle_incident_create(self, context: TriggerContext) -> TriggerResult:
        """
        Обрабатывает триггер создания инцидента.
        
        Args:
            context: Контекст триггера
            
        Returns:
            TriggerResult: Результат обработки триггера
        """
        try:
            # Извлекаем данные из контекста
            data = context.data
            title = data.get("title", "")
            
            # Имитация обработки
            if self.report_progress_func:
                self.report_progress_func({
                    "event": "incident_created",
                    "title": title,
                    "message": f"Инцидент '{title}' создан"
                })
                
            return TriggerResult(
                success=True,
                message=f"Инцидент '{title}' успешно создан",
                data={"title": title}
            )
        except Exception as e:
            logger.error(f"Ошибка при обработке триггера создания инцидента: {e}")
            traceback.print_exc()
            return TriggerResult(success=False, message=f"Ошибка при обработке триггера создания инцидента: {e}")
    
    def _handle_incident_update(self, context: TriggerContext) -> TriggerResult:
        """
        Обрабатывает триггер обновления инцидента.
        
        Args:
            context: Контекст триггера
            
        Returns:
            TriggerResult: Результат обработки триггера
        """
        return TriggerResult(success=True, message="Инцидент обновлен")
    
    def _handle_hypothesis_create(self, context: TriggerContext) -> TriggerResult:
        """
        Обрабатывает триггер создания гипотезы.
        
        Args:
            context: Контекст триггера
            
        Returns:
            TriggerResult: Результат обработки триггера
        """
        try:
            # Извлекаем данные из контекста
            data = context.data
            title = data.get("title", "")
            
            # Имитация обработки
            if self.report_progress_func:
                self.report_progress_func({
                    "event": "hypothesis_created",
                    "title": title,
                    "message": f"Гипотеза '{title}' создана"
                })
                
            return TriggerResult(
                success=True,
                message=f"Гипотеза '{title}' успешно создана",
                data={"title": title}
            )
        except Exception as e:
            logger.error(f"Ошибка при обработке триггера создания гипотезы: {e}")
            traceback.print_exc()
            return TriggerResult(success=False, message=f"Ошибка при обработке триггера создания гипотезы: {e}")
    
    def _handle_hypothesis_update(self, context: TriggerContext) -> TriggerResult:
        """
        Обрабатывает триггер обновления гипотезы.
        
        Args:
            context: Контекст триггера
            
        Returns:
            TriggerResult: Результат обработки триггера
        """
        return TriggerResult(success=True, message="Гипотеза обновлена")


# Функция для получения экземпляра обработчика триггеров (синглтон)
def get_handler(report_progress_func: Optional[Callable] = None) -> SimpleTriggerHandler:
    """
    Возвращает экземпляр упрощенного обработчика триггеров (синглтон).
    
    Args:
        report_progress_func: Функция для отчета о прогрессе
        
    Returns:
        SimpleTriggerHandler: Экземпляр упрощенного обработчика триггеров
    """
    if SimpleTriggerHandler._instance is None:
        SimpleTriggerHandler._instance = SimpleTriggerHandler(report_progress_func)
    return SimpleTriggerHandler._instance

# Для совместимости с предыдущими версиями
def get_trigger_handler_instance(report_progress_func: Optional[Callable] = None) -> SimpleTriggerHandler:
    """
    Возвращает экземпляр упрощенного обработчика триггеров для совместимости.
    Обертка вокруг функции get_handler.
    
    Args:
        report_progress_func: Функция для отчета о прогрессе
        
    Returns:
        SimpleTriggerHandler: Экземпляр упрощенного обработчика триггеров
    """
    return get_handler(report_progress_func)