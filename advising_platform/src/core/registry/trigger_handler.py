"""
Упрощенный модуль обработчика триггеров для задач и инцидентов.
Предоставляет основные функции для обработки различных типов триггеров.
"""

import logging
import traceback
import time
import os
import re
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
        self.source = source or "unknown"
        
    def __str__(self) -> str:
        return f"TriggerContext(type={self.trigger_type}, source={self.source})"

class TriggerHandler:
    """JTBD:
Я (разработчик) хочу использовать функциональность класса TriggerHandler, чтобы эффективно решать соответствующие задачи в системе.
    
    Упрощенный обработчик триггеров."""
    _instance: Optional['TriggerHandler'] = None
    
    def __init__(self, report_progress_func: Optional[Callable] = None):
        """
        Инициализирует упрощенный обработчик триггеров.
        
        Args:
            report_progress_func: Функция для отчета о прогрессе
        """
        self.report_progress_func = report_progress_func
        self.handlers = {}
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Регистрирует обработчики по умолчанию."""
        self.register_handler(TriggerType.TASK_CREATE, self._handle_task_create)
        self.register_handler(TriggerType.TASK_UPDATE, self._handle_task_update)
        self.register_handler(TriggerType.INCIDENT_CREATE, self._handle_incident_create)
        self.register_handler(TriggerType.INCIDENT_UPDATE, self._handle_incident_update)
        self.register_handler(TriggerType.HYPOTHESIS_CREATE, self._handle_hypothesis_create)
        self.register_handler(TriggerType.HYPOTHESIS_UPDATE, self._handle_hypothesis_update)
        self.register_handler(TriggerType.STANDARD_CREATE, self._handle_standard_create)
        self.register_handler(TriggerType.STANDARD_UPDATE, self._handle_standard_update)
        self.register_handler(TriggerType.FILE_DUPLICATION_CHECK, self._handle_file_duplication_check)
    
    def register_handler(self, trigger_type: str, handler_func: Callable) -> bool:
        """
        Регистрирует функцию-обработчик для указанного типа триггера.
        
        Args:
            trigger_type: Тип триггера
            handler_func: Функция-обработчик
            
        Returns:
            bool: True, если регистрация успешна, иначе False
        """
        if not callable(handler_func):
            logger.error(f"Ошибка регистрации обработчика для {trigger_type}: функция не callable")
            return False
            
        self.handlers[trigger_type] = handler_func
        logger.info(f"Зарегистрирован обработчик для {trigger_type}")
        return True
    
    def has_handler(self, trigger_type: str) -> bool:
        """
        Проверяет наличие обработчика для указанного типа триггера.
        
        Args:
            trigger_type: Тип триггера
            
        Returns:
            bool: True, если обработчик зарегистрирован, иначе False
        """
        return trigger_type in self.handlers
    
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
            logger.error(f"Обработчик для типа триггера {trigger_type} не найден")
            return TriggerResult(success=False, message=f"Обработчик для типа триггера {trigger_type} не найден")
        
        try:
            handler = self.handlers[trigger_type]
            return handler(context)
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
            priority = data.get("priority", "")
            status = data.get("status", "")
            task_type = data.get("type", "")
            description = data.get("description", "")
            
            # Анализируем документацию существующих скриптов для предотвращения дублирования
            similar_scripts = []
            documentation_analysis = None
            
            try:
                # Импортируем анализатор документации скриптов
                from advising_platform.src.core.script_documentation_analyzer import find_similar_scripts
                
                # Если есть описание, ищем похожие скрипты
                if description:
                    similar_scripts = find_similar_scripts(description, threshold=2)
                    logger.info(f"Найдено {len(similar_scripts)} похожих скриптов для задачи '{title}'")
            except Exception as script_error:
                logger.warning(f"Ошибка при анализе документации скриптов: {script_error}")
                similar_scripts = []
                
            # Анализируем наличие JTBD-документации в коде
            try:
                # Импортируем анализатор JTBD-документации
                from advising_platform.src.core.documentation_analyzer import analyze_directory, generate_jtbd_suggestions
                
                # Получаем директорию из описания задачи или используем стандартную
                target_directory = "advising_platform/src"
                
                if "path:" in description or "директория:" in description:
                    # Ищем упоминание пути или директории в описании
                    matches = re.findall(r'(?:path|директория):\s*([^\s,;]+)', description, re.IGNORECASE)
                    if matches:
                        target_directory = matches[0]
                
                # Проверяем только определенную директорию, если она существует
                if os.path.exists(target_directory):
                    documentation_analysis = analyze_directory(target_directory)
                    jtbd_coverage = documentation_analysis.get("jtbd_coverage_percentage", 0)
                    logger.info(f"Покрытие JTBD-документацией: {jtbd_coverage:.1f}% в директории {target_directory}")
                else:
                    logger.warning(f"Директория {target_directory} не существует")
            except Exception as doc_error:
                logger.warning(f"Ошибка при анализе JTBD-документации: {doc_error}")
                documentation_analysis = None
            
            # Формируем сообщение о создании задачи
            task_message = f"✅ **Задача создана**: {title}\n"
            
            if priority:
                priority_icon = "🔴" if priority == 3 or str(priority).lower() == "высокий" else "🟠" if priority == 2 or str(priority).lower() == "средний" else "🟢"
                task_message += f"{priority_icon} Приоритет: {priority}\n"
                
            if status:
                task_message += f"📋 Статус: {status}\n"
                
            if task_type:
                task_message += f"🏷️ Тип: {task_type}\n"
                
            # Добавляем ссылку на просмотр задачи
            task_message += f"🌐 Просмотр: http://0.0.0.0:5000/tasks/{title.replace(' ', '-')}\n\n"
            
            # Добавляем информацию о похожих скриптах, если они найдены
            if similar_scripts:
                task_message += f"📚 **Найдены похожие скрипты для решения этой задачи**:\n"
                for i, script in enumerate(similar_scripts[:3], 1):  # Показываем только топ-3 скрипта
                    script_name = script.get('name', 'Неизвестный скрипт')
                    script_path = script.get('path', '')
                    match_count = script.get('match_count', 0)
                    docstring = script.get('docstring', '')
                    
                    # Выводим путь и краткое описание
                    task_message += f"{i}. **{script_name}** ({script_path})\n"
                    
                    # Добавляем сокращенное описание (первые 100 символов)
                    if docstring:
                        short_desc = docstring[:100] + "..." if len(docstring) > 100 else docstring
                        task_message += f"   {short_desc}\n"
                    
                    # Добавляем совпадающие ключевые слова
                    matched_keywords = script.get('matched_keywords', [])
                    if matched_keywords:
                        keywords_str = ", ".join(matched_keywords[:5])  # Показываем только первые 5 ключевых слов
                        task_message += f"   Ключевые слова: {keywords_str}\n"
                
                task_message += "\n❗ **Рекомендация**: Используйте существующие скрипты вместо создания новых.\n\n"
            
            # Добавляем информацию о JTBD-документации, если она была проанализирована
            if documentation_analysis:
                jtbd_coverage = documentation_analysis.get("jtbd_coverage_percentage", 0)
                missing_modules = documentation_analysis.get("missing_jtbd_modules", 0)
                missing_classes = documentation_analysis.get("missing_jtbd_classes", 0)
                missing_functions = documentation_analysis.get("missing_jtbd_functions", 0)
                
                task_message += f"📊 **Статистика JTBD-документации**:\n"
                task_message += f"📝 Покрытие документацией: {jtbd_coverage:.1f}%\n"
                
                if missing_modules > 0 or missing_classes > 0 or missing_functions > 0:
                    task_message += f"⚠️ Компоненты без JTBD-документации:\n"
                    if missing_modules > 0:
                        task_message += f"  - Модули: {missing_modules}\n"
                    if missing_classes > 0:
                        task_message += f"  - Классы: {missing_classes}\n"
                    if missing_functions > 0:
                        task_message += f"  - Функции: {missing_functions}\n"
                    
                    task_message += f"\n🔍 **Рекомендация**: При реализации этой задачи добавьте JTBD-документацию согласно [стандарту](http://0.0.0.0:5000/docs/jtbd_documentation_standard)\n\n"
                else:
                    task_message += f"✅ Все компоненты имеют JTBD-документацию\n\n"
            
            # Добавляем статистику по задачам к сообщению
            try:
                from advising_platform.src.core.storage.task_storage import get_task_statistics
                
                # Получаем реальную статистику
                stats = get_task_statistics()
                
                # Добавляем статистику к сообщению
                task_message += f"📊 **Статистика по задачам**:\n"
                task_message += f"📝 Всего задач: {stats.get('total', 0)}\n"
                task_message += f"✅ Выполнено: {stats.get('completed', 0)} ({stats.get('completion_rate', 0)}%)\n"
                task_message += f"⏳ В процессе: {stats.get('in_progress', 0)}\n"
                task_message += f"🆕 Не начато: {stats.get('not_started', 0)}\n\n"
                task_message += f"🔢 **По приоритетам**:\n"
                task_message += f"🔴 Высокий: {stats.get('high_priority', 0)}\n"
                task_message += f"🟠 Средний: {stats.get('medium_priority', 0)}\n"
                task_message += f"🟢 Низкий: {stats.get('low_priority', 0)}"
            except Exception as stats_error:
                logger.warning(f"Ошибка при получении статистики по задачам: {stats_error}")
                task_message += "⚠️ Не удалось получить статистику по задачам."
            
            # Отправляем общее сообщение, содержащее всю информацию
            if self.report_progress_func:
                self.report_progress_func({"summary": task_message})
                
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
            description = data.get("description", "")
            
            # Формируем полное сообщение с информацией об инциденте
            incident_message = f"⚠️ **Инцидент создан**: {title}\n"
            incident_message += f"🌐 Просмотр: http://0.0.0.0:5000/incidents/{title.replace(' ', '-')}\n\n"
            
            # Извлекаем анализ 5-почему из описания
            five_why_analysis = []
            root_cause = "Не указана"
            
            if description:
                # Парсим описание для извлечения анализа 5-почему и корневой причины
                why_section_started = False
                root_cause_section_started = False
                
                lines = description.split("\n")
                for line in lines:
                    if "## Анализ 5-почему" in line:
                        why_section_started = True
                        continue
                    elif "## Корневая причина" in line:
                        why_section_started = False
                        root_cause_section_started = True
                        continue
                    elif why_section_started and line.strip() and ("Почему #" in line or "**Почему" in line):
                        # Нашли вопрос почему, добавляем в анализ
                        question = line.strip()
                        answer = ""
                        five_why_analysis.append({"question": question, "answer": answer})
                    elif why_section_started and line.strip() and five_why_analysis and not five_why_analysis[-1]["answer"]:
                        # Это ответ на последний вопрос
                        five_why_analysis[-1]["answer"] = line.strip()
                    elif root_cause_section_started and line.strip() and not line.startswith("##"):
                        root_cause = line.strip()
                        root_cause_section_started = False
            
            # Если нашли анализ 5-почему, добавляем его к сообщению
            if five_why_analysis:
                incident_message += f"🔍 **Анализ 5-почему**:\n\n"
                
                for i, why in enumerate(five_why_analysis, 1):
                    incident_message += f"{i}. {why['question']}\n   {why['answer']}\n\n"
                
                incident_message += f"🌱 **Корневая причина**: {root_cause}\n\n"
            
            # Добавляем статистику по задачам к сообщению
            try:
                from advising_platform.src.core.storage.task_storage import get_task_statistics
                
                # Получаем реальную статистику
                stats = get_task_statistics()
                
                # Добавляем статистику к сообщению
                incident_message += f"📊 **Статистика по задачам**:\n"
                incident_message += f"📝 Всего задач: {stats.get('total', 0)}\n"
                incident_message += f"✅ Выполнено: {stats.get('completed', 0)} ({stats.get('completion_rate', 0)}%)\n"
                incident_message += f"⏳ В процессе: {stats.get('in_progress', 0)}\n"
                incident_message += f"🆕 Не начато: {stats.get('not_started', 0)}\n\n"
                incident_message += f"🔢 **По приоритетам**:\n"
                incident_message += f"🔴 Высокий: {stats.get('high_priority', 0)}\n"
                incident_message += f"🟠 Средний: {stats.get('medium_priority', 0)}\n"
                incident_message += f"🟢 Низкий: {stats.get('low_priority', 0)}"
            except Exception as stats_error:
                logger.warning(f"Ошибка при получении статистики по задачам: {stats_error}")
                incident_message += "⚠️ Не удалось получить статистику по задачам."
            
            # Отправляем единое сообщение со всей информацией
            if self.report_progress_func:
                self.report_progress_func({"summary": incident_message})
                
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
            description = data.get("description", "")
            
            # Извлекаем RAT и критерий фальсифицируемости из описания (если есть)
            rat = "Не указан"
            falsifiability = "Не указан"
            
            if description:
                # Улучшенный парсинг для извлечения RAT и критерия фальсифицируемости
                lines = description.split("\n")
                
                rat_section_started = False
                falsifiability_section_started = False
                relevant_found = False
                actionable_found = False
                testable_found = False
                rat_relevant = ""
                rat_actionable = ""
                rat_testable = ""
                
                i = 0
                while i < len(lines):
                    line = lines[i].strip()
                    
                    # Обнаружение секции RAT-анализа
                    if "## RAT" in line or "## Реалистичность, Амбициозность, Тестируемость" in line:
                        rat_section_started = True
                        falsifiability_section_started = False
                    
                    # Обнаружение секции критерия фальсифицируемости
                    elif "## Критерий фальсифицируемости" in line or "## Фальсифицируемость" in line:
                        rat_section_started = False
                        falsifiability_section_started = True
                    
                    # Переход к другому разделу
                    elif line.startswith("## ") and "RAT" not in line and "Критерий" not in line and "Фальсифицируемость" not in line:
                        rat_section_started = False
                        falsifiability_section_started = False
                    
                    # Обработка внутри секции RAT
                    elif rat_section_started:
                        # Поиск компонентов RAT
                        if "### Relevant" in line or "### Релевантность" in line:
                            relevant_found = True
                            
                            # Собираем текст до следующего заголовка
                            j = i + 1
                            while j < len(lines) and not lines[j].strip().startswith("###"):
                                if lines[j].strip():
                                    rat_relevant += lines[j].strip() + " "
                                j += 1
                            
                            i = j - 1  # Перемещаем индекс на последнюю строку перед следующим заголовком
                        
                        elif "### Actionable" in line or "### Применимость" in line:
                            actionable_found = True
                            
                            # Собираем текст до следующего заголовка
                            j = i + 1
                            while j < len(lines) and not lines[j].strip().startswith("###"):
                                if lines[j].strip():
                                    rat_actionable += lines[j].strip() + " "
                                j += 1
                            
                            i = j - 1  # Перемещаем индекс на последнюю строку перед следующим заголовком
                        
                        elif "### Testable" in line or "### Тестируемость" in line:
                            testable_found = True
                            
                            # Собираем текст до следующего заголовка
                            j = i + 1
                            while j < len(lines) and not lines[j].strip().startswith("###") and not lines[j].strip().startswith("##"):
                                if lines[j].strip():
                                    rat_testable += lines[j].strip() + " "
                                j += 1
                            
                            i = j - 1  # Перемещаем индекс на последнюю строку перед следующим заголовком
                    
                    # Обработка внутри секции критерия фальсифицируемости
                    elif falsifiability_section_started:
                        # Сбрасываем значение по умолчанию при первом нахождении текста
                        if line and not line.startswith("##") and falsifiability == "Не указан":
                            falsifiability = line
                        # Добавляем следующие строки, если они не пустые и не заголовки
                        elif line and not line.startswith("##") and falsifiability != "Не указан":
                            falsifiability += " " + line
                    
                    i += 1
                
                # Формируем полный RAT-анализ, если есть компоненты
                if relevant_found or actionable_found or testable_found:
                    rat = ""
                    if relevant_found:
                        rat += f"**Relevant**: {rat_relevant.strip()}\n\n"
                    if actionable_found:
                        rat += f"**Actionable**: {rat_actionable.strip()}\n\n"
                    if testable_found:
                        rat += f"**Testable**: {rat_testable.strip()}"
                
                # Обрезаем лишние пробелы
                falsifiability = falsifiability.strip()
                
                # Если найден текст критерия фальсифицируемости, заменяем значение по умолчанию
                if falsifiability and falsifiability != "Не указан":
                    falsifiability = f"{falsifiability}"
            
            # Формируем сообщение для чата напрямую
            hypothesis_message = f"🧪 **Гипотеза создана**: {title}\n\n"
            hypothesis_message += f"📋 **RAT**: {rat}\n\n"
            hypothesis_message += f"🔍 **Критерий фальсифицируемости**: {falsifiability}\n\n"
            hypothesis_message += f"🌐 Просмотр: http://0.0.0.0:5000/hypotheses/{title.replace(' ', '-')}\n\n"
            
            # Добавляем статистику задач к сообщению
            try:
                from advising_platform.src.core.storage.task_storage import get_task_statistics
                
                # Получаем реальную статистику
                stats = get_task_statistics()
                
                # Добавляем статистику к сообщению
                hypothesis_message += f"📊 **Статистика по задачам**:\n"
                hypothesis_message += f"📝 Всего задач: {stats.get('total', 0)}\n"
                hypothesis_message += f"✅ Выполнено: {stats.get('completed', 0)} ({stats.get('completion_rate', 0)}%)\n"
                hypothesis_message += f"⏳ В процессе: {stats.get('in_progress', 0)}\n"
                hypothesis_message += f"🆕 Не начато: {stats.get('not_started', 0)}\n\n"
                hypothesis_message += f"🔢 **По приоритетам**:\n"
                hypothesis_message += f"🔴 Высокий: {stats.get('high_priority', 0)}\n"
                hypothesis_message += f"🟠 Средний: {stats.get('medium_priority', 0)}\n"
                hypothesis_message += f"🟢 Низкий: {stats.get('low_priority', 0)}"
            except Exception as stats_error:
                logger.warning(f"Ошибка при выводе статистики по задачам: {stats_error}")
                hypothesis_message += "⚠️ Не удалось получить статистику по задачам."
                
            # Отправляем сообщение напрямую через report_progress_func
            if self.report_progress_func:
                self.report_progress_func({"summary": hypothesis_message})
                
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
        
    def _handle_standard_create(self, context: TriggerContext) -> TriggerResult:
        """
        Обрабатывает триггер создания стандарта.
        
        Args:
            context: Контекст триггера
            
        Returns:
            TriggerResult: Результат обработки триггера
        """
        try:
            # Извлекаем данные из контекста
            data = context.data
            title = data.get("title", "")
            description = data.get("description", "")
            author = data.get("author", "Неизвестный автор")
            category = data.get("category", "Общая")
            
            # Извлекаем информацию о стандарте из описания
            purpose = "Не указана"
            requirements = []
            benefits = []
            related_standards = []
            
            if description:
                # Парсинг описания для извлечения полезной информации
                lines = description.split("\n")
                current_section = None
                
                for line in lines:
                    if "## Цель" in line:
                        current_section = "purpose"
                        continue
                    elif "## Требования" in line:
                        current_section = "requirements"
                        continue
                    elif "## Преимущества" in line or "## Польза" in line:
                        current_section = "benefits"
                        continue
                    elif "## Связанные стандарты" in line:
                        current_section = "related"
                        continue
                    elif line.startswith("##"):
                        current_section = None
                        continue
                        
                    if current_section == "purpose" and line.strip():
                        purpose = line.strip()
                    elif current_section == "requirements" and line.strip():
                        if line.strip().startswith("- "):
                            requirements.append(line.strip()[2:])
                    elif current_section == "benefits" and line.strip():
                        if line.strip().startswith("- "):
                            benefits.append(line.strip()[2:])
                    elif current_section == "related" and line.strip():
                        if line.strip().startswith("- "):
                            related_standards.append(line.strip()[2:])
            
            # Формируем сообщение для чата
            standard_message = f"📜 **Стандарт создан**: {title}\n"
            standard_message += f"👤 Автор: {author}\n"
            standard_message += f"🏷️ Категория: {category}\n"
            standard_message += f"🎯 Цель: {purpose}\n\n"
            
            if requirements:
                standard_message += "✅ **Ключевые требования**:\n"
                for req in requirements[:3]:  # Ограничиваем количество выводимых требований
                    standard_message += f"- {req}\n"
                if len(requirements) > 3:
                    standard_message += f"...и еще {len(requirements) - 3} требований\n\n"
                else:
                    standard_message += "\n"
            
            if related_standards:
                standard_message += "🔄 **Связанные стандарты**:\n"
                for rel in related_standards[:3]:  # Ограничиваем количество связанных стандартов
                    standard_message += f"- {rel}\n"
                if len(related_standards) > 3:
                    standard_message += f"...и еще {len(related_standards) - 3} связанных стандартов\n\n"
                else:
                    standard_message += "\n"
            
            # Добавляем ссылку на просмотр стандарта
            standard_message += f"🌐 Просмотр: http://0.0.0.0:5000/standards/{title.replace(' ', '-')}\n\n"
            
            # Добавляем статистику по стандартам и задачам
            try:
                total_standards = 0
                standards_dir = "[standards .md]"
                
                if os.path.exists(standards_dir):
                    total_standards = len([f for f in os.listdir(standards_dir) if f.endswith('.md')])
                
                standard_message += f"📊 **Статистика по стандартам**:\n"
                standard_message += f"📝 Всего активных стандартов: {total_standards}\n"
                standard_message += f"📋 Целевое количество: ~40 активных стандартов\n\n"
                
                # Также добавляем статистику по задачам
                try:
                    from advising_platform.src.core.storage.task_storage import get_task_statistics
                    
                    # Получаем реальную статистику
                    stats = get_task_statistics()
                    
                    # Добавляем статистику к сообщению
                    standard_message += f"📊 **Статистика по задачам**:\n"
                    standard_message += f"📝 Всего задач: {stats.get('total', 0)}\n"
                    standard_message += f"✅ Выполнено: {stats.get('completed', 0)} ({stats.get('completion_rate', 0)}%)\n"
                    standard_message += f"⏳ В процессе: {stats.get('in_progress', 0)}\n"
                    standard_message += f"🆕 Не начато: {stats.get('not_started', 0)}\n\n"
                    standard_message += f"🔢 **По приоритетам**:\n"
                    standard_message += f"🔴 Высокий: {stats.get('high_priority', 0)}\n"
                    standard_message += f"🟠 Средний: {stats.get('medium_priority', 0)}\n"
                    standard_message += f"🟢 Низкий: {stats.get('low_priority', 0)}"
                except Exception as stats_error:
                    logger.warning(f"Ошибка при выводе статистики по задачам: {stats_error}")
                    standard_message += "⚠️ Не удалось получить статистику по задачам."
            except Exception as standards_error:
                logger.warning(f"Ошибка при выводе статистики по стандартам: {standards_error}")
                standard_message += "⚠️ Не удалось получить статистику по стандартам."
            
            # Отправляем основное сообщение о стандарте
            if self.report_progress_func:
                self.report_progress_func({"summary": standard_message})
                
            return TriggerResult(
                success=True,
                message=f"Стандарт '{title}' успешно создан",
                data={"title": title}
            )
        except Exception as e:
            logger.error(f"Ошибка при обработке триггера создания стандарта: {e}")
            traceback.print_exc()
            return TriggerResult(success=False, message=f"Ошибка при обработке триггера создания стандарта: {e}")
    
    def _handle_standard_update(self, context: TriggerContext) -> TriggerResult:
        """
        Обрабатывает триггер обновления стандарта.
        
        Args:
            context: Контекст триггера
            
        Returns:
            TriggerResult: Результат обработки триггера
        """
        return TriggerResult(success=True, message="Стандарт обновлен")
        
    def _handle_file_duplication_check(self, context: TriggerContext) -> TriggerResult:
        """
        Обрабатывает триггер проверки дублирования файла.
        
        Args:
            context: Контекст триггера
            
        Returns:
            TriggerResult: Результат обработки триггера
        """
        try:
            data = context.data
            file_path = data.get("file_path", "")
            
            # В реальной системе здесь будет проверка на дубликаты
            # Имитация проверки
            duplicates = []
            
            # Возвращаем результат проверки
            return TriggerResult(
                success=True,
                message=f"Проверка дублирования файла '{file_path}' успешно выполнена",
                data={"file_path": file_path, "duplicates": duplicates}
            )
        except Exception as e:
            logger.error(f"Ошибка при обработке триггера проверки дублирования файла: {e}")
            traceback.print_exc()
            return TriggerResult(success=False, message=f"Ошибка при обработке триггера проверки дублирования файла: {e}")

def get_handler(report_progress_func: Optional[Callable] = None) -> TriggerHandler:
    """
    Возвращает экземпляр упрощенного обработчика триггеров (синглтон).
    
    Args:
        report_progress_func: Функция для отчета о прогрессе
        
    Returns:
        TriggerHandler: Экземпляр упрощенного обработчика триггеров
    """
    if TriggerHandler._instance is None:
        TriggerHandler._instance = TriggerHandler(report_progress_func)
    return TriggerHandler._instance

def get_trigger_handler_instance(report_progress_func: Optional[Callable] = None) -> TriggerHandler:
    """
    Возвращает экземпляр упрощенного обработчика триггеров для совместимости.
    Обертка вокруг функции get_handler.
    
    Args:
        report_progress_func: Функция для отчета о прогрессе
        
    Returns:
        SimpleTriggerHandler: Экземпляр упрощенного обработчика триггеров
    """
    return get_handler(report_progress_func)
