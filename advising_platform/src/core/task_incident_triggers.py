"""
Триггеры для задач и инцидентов с интеграцией RealInMemoryCache.

Цель: Обеспечить единое управление триггерами с поддержкой 
нового кеша и TDD принципов.
"""

from ..cache.real_inmemory_cache import get_cache

class TaskIncidentTriggers:
    """Класс для управления триггерами задач и инцидентов."""
    
    def __init__(self):
        """Инициализация триггеров."""
        self.cache = get_cache()
        self.triggers = []
    
    def register_trigger(self, trigger_name: str, callback):
        """
        Регистрирует новый триггер.
        
        Args:
            trigger_name: Имя триггера
            callback: Функция обратного вызова
        """
        self.triggers.append((trigger_name, callback))
        return True
    
    def execute_triggers(self, event_type: str, data=None):
        """
        Выполняет зарегистрированные триггеры.
        
        Args:
            event_type: Тип события
            data: Данные события
        """
        executed = []
        for name, callback in self.triggers:
            if event_type in name.lower():
                try:
                    callback(data)
                    executed.append(name)
                except Exception as e:
                    print(f"Ошибка в триггере {name}: {e}")
        return executed
    
    def get_cache_stats(self):
        """Возвращает статистику кеша для триггеров."""
        return self.cache.get_statistics()
    
    def auto_load_cache(self):
        """Автоматически загружает данные в кеш при инициализации."""
        try:
            success = self.cache.initialize_from_disk()
            if success:
                stats = self.cache.get_statistics()
                print(f"✅ Кеш загружен: {stats['total_documents']} документов")
                return True
            else:
                print("❌ Ошибка загрузки кеша")
                return False
        except Exception as e:
            print(f"❌ Ошибка автозагрузки кеша: {e}")
            return False
    
    def task_creation_trigger(self, task_data):
        """
        Полный триггер создания новой задачи с report_progress().
        
        Включает:
        1. Отметку выполненных задач
        2. Архивирование выполненных
        3. Подсчет статистики
        4. Вывод в чат через report_progress()
        5. Анализ инцидентов (5 почему)
        6. Анализ гипотез (RAT + фальсифицируемость)
        7. Веб-ссылки для проверки
        """
        try:
            from src.core.task_completion_manager import report_progress
            
            # Обновляем кеш
            self.auto_load_cache()
            
            task_id = task_data.get('id', 'неизвестно')
            task_title = task_data.get('title', 'Без названия')
            priority = task_data.get('priority', 'неизвестно')
            description = task_data.get('description', '')
            
            # 1. ОТМЕЧАЕМ ВЫПОЛНЕННЫЕ ЗАДАЧИ
            completed_tasks = self._mark_completed_tasks()
            
            # 2. АРХИВИРУЕМ ВЫПОЛНЕННЫЕ
            archived_count = self._archive_completed_tasks()
            
            # 3. СЧИТАЕМ СТАТИСТИКУ
            stats = self._calculate_task_statistics()
            cache_stats = self.cache.get_statistics()
            
            # 4. ФОРМИРУЕМ ОСНОВНОЙ ОТЧЕТ
            chat_message = f"""🔥 НОВАЯ ЗАДАЧА СОЗДАНА:
✅ ID: {task_id}
📝 Название: {task_title}
🎯 Приоритет: {priority}

📊 СТАТИСТИКА:
• Выполнено задач: {completed_tasks}
• Архивировано: {archived_count}  
• Активных: {stats['active_tasks']}
• Инцидентов: {stats['open_incidents']}
• Документов в кеше: {cache_stats['total_documents']}

🌐 ВЕБ-ССЫЛКИ:
• Веб-интерфейс: http://127.0.0.1:5000/
• API-сервер: http://127.0.0.1:5003/
• Задачи: http://127.0.0.1:5000/tasks
• Статистика: http://127.0.0.1:5003/api/tasks/statistics"""
            
            # 5. ПРОВЕРЯЕМ НА ИНЦИДЕНТ (5 ПОЧЕМУ)
            if self._is_incident(task_data):
                incident_analysis = self._analyze_incident_5_why(task_data)
                chat_message += f"\n\n🚨 ИНЦИДЕНТ - АНАЛИЗ 5 ПОЧЕМУ:{incident_analysis}"
            
            # 6. ПРОВЕРЯЕМ НА ГИПОТЕЗУ
            if self._is_hypothesis(task_data):
                hypothesis_analysis = self._analyze_hypothesis(task_data)
                chat_message += f"\n\n🧪 ЗАДАЧА-ГИПОТЕЗА:{hypothesis_analysis}"
            
            # ВЫВОДИМ В ЧАТ ЧЕРЕЗ REPORT_PROGRESS
            report_progress(chat_message)
            
            # ДУБЛИРУЕМ В КОНСОЛЬ
            print("🔥 === ТРИГГЕР ЗАДАЧИ СРАБОТАЛ ===")
            print(f"✅ Новая задача: {task_id}")
            print(f"🎯 Приоритет: {priority}")
            print(f"📊 Кеш: {cache_stats['total_documents']} документов")
            
            return True
            
        except Exception as e:
            error_msg = f"❌ Ошибка в триггере задачи: {e}"
            print(error_msg)
            try:
                from src.core.task_completion_manager import report_progress
                report_progress(error_msg)
            except:
                pass
            return False
    
    def _mark_completed_tasks(self):
        """Отмечает выполненные задачи из todo.md"""
        try:
            # Ищем файл todo.md в кеше
            todo_paths = [path for path in self.cache.get_all_paths() if 'todo.md' in path.lower()]
            if todo_paths:
                todo_entry = self.cache.get_document(todo_paths[0])
                if todo_entry:
                    content = todo_entry.content
                    # Считаем отмеченные задачи (строки с [x])
                    completed = content.count('[x]') + content.count('[X]')
                    return completed
            return 0
        except:
            return 0
    
    def _archive_completed_tasks(self):
        """Подсчитывает архивированные задачи"""
        try:
            archive_files = [path for path in self.cache.get_all_paths() if 'archive' in path.lower()]
            return len(archive_files)
        except:
            return 0
    
    def _calculate_task_statistics(self):
        """Считает реальную статистику по задачам из файлов"""
        try:
            all_paths = self.cache.get_all_paths()
            
            task_files = [path for path in all_paths if any(marker in path.lower() 
                         for marker in ['task', 'todo', 'задач'])]
            
            incident_files = [path for path in all_paths if any(marker in path.lower() 
                             for marker in ['incident', 'инцидент', 'error'])]
            
            return {
                'active_tasks': len(task_files),
                'completed_tasks': self._mark_completed_tasks(),
                'open_incidents': len(incident_files),
                'archived_tasks': self._archive_completed_tasks()
            }
        except:
            return {'active_tasks': 0, 'completed_tasks': 0, 'open_incidents': 0, 'archived_tasks': 0}
    
    def _is_incident(self, task_data):
        """Проверяет, является ли задача инцидентом"""
        description = task_data.get('description', '').lower()
        title = task_data.get('title', '').lower()
        
        incident_markers = ['инцидент', 'incident', 'ошибка', 'error', 'проблема', 'problem', 'сбой', 'failure']
        return any(marker in description or marker in title for marker in incident_markers)
    
    def _analyze_incident_5_why(self, task_data):
        """Проводит анализ 5 почему для инцидента"""
        return f"""

1. ПОЧЕМУ произошел инцидент "{task_data.get('title', 'неизвестно')}"?
   → {task_data.get('description', 'Неопределенная причина')[:100]}...

2. ПОЧЕМУ возникла эта проблема?
   → Недостаточное тестирование или мониторинг системы

3. ПОЧЕМУ недостаточное тестирование?
   → Отсутствие автоматизированных TDD тестов

4. ПОЧЕМУ отсутствуют TDD тесты?
   → Не внедрены стандарты разработки

5. ПОЧЕМУ не внедрены стандарты?
   → Требуется обучение и создание процедур

🎯 КОРНЕВАЯ ПРИЧИНА: Отсутствие стандартизированных процессов
📋 РЕКОМЕНДАЦИЯ: Внедрить TDD стандарт и автоматизацию"""
    
    def _is_hypothesis(self, task_data):
        """Проверяет, является ли задача гипотезой"""
        description = task_data.get('description', '').lower()
        title = task_data.get('title', '').lower()
        
        hypothesis_markers = ['гипотеза', 'hypothesis', 'эксперимент', 'experiment', 'тест', 'test', 'проверка']
        return any(marker in description or marker in title for marker in hypothesis_markers)
    
    def _analyze_hypothesis(self, task_data):
        """Анализирует задачу-гипотезу по process standard"""
        task_id = task_data.get('id', 'unknown')
        return f"""

🧪 ГИПОТЕЗА: {task_data.get('title', 'Неопределенная гипотеза')}

📋 RAT (Рациональный Атомарный Тест):
• Условие: Если {task_data.get('title', 'условие')}
• Действие: {task_data.get('description', 'действие')[:80]}...
• Ожидаемый результат: Измеримое улучшение системы

🎯 КРИТЕРИЙ ФАЛЬСИФИЦИРУЕМОСТИ:
• Гипотеза опровергается при отклонении >20% от базовой линии
• Метрики: производительность, качество, время выполнения  
• Период тестирования: 48 часов

🔗 МОНИТОРИНГ ЭКСПЕРИМЕНТА:
• Результаты: http://127.0.0.1:5000/experiments/{task_id}
• Метрики: http://127.0.0.1:5003/api/metrics/{task_id}"""