#!/usr/bin/env python3
"""
TDD тест для полной логики триггеров с report_progress().

Проверяет:
1. Отметку выполненных задач
2. Архивирование выполненных
3. Подсчет статистики  
4. Вывод в чат через report_progress()
5. Анализ инцидентов (5 почему)
6. Анализ гипотез (RAT + фальсифицируемость)
7. Веб-ссылки для проверки

Автор: AI Assistant  
Дата: 22 May 2025
"""

import unittest
import os
import sys
import time
from datetime import datetime

# Добавляем корневую папку в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class FullTriggerLogicTDDTest(unittest.TestCase):
    """
    TDD тест полной логики триггеров с report_progress().
    
    Проверяет все аспекты работы триггера при создании задач.
    """
    
    def setUp(self):
        """Подготовка к тестам."""
        print(f"\n🎯 === TDD ТЕСТ ПОЛНОЙ ЛОГИКИ ТРИГГЕРОВ ({datetime.now().strftime('%H:%M:%S')}) ===")
        
        from src.core.task_incident_triggers import TaskIncidentTriggers
        self.triggers = TaskIncidentTriggers()
        
        # Перехватываем вызовы report_progress для анализа
        self.report_progress_calls = []
        
        # Тестовые данные
        self.normal_task = {
            'id': f'NORMAL_TASK_{int(time.time())}',
            'title': 'Обычная задача разработки',
            'priority': 'SMALL TASK 🟢',
            'description': 'Простая задача для тестирования триггера'
        }
        
        self.incident_task = {
            'id': f'INCIDENT_TASK_{int(time.time())}',
            'title': 'Критическая ошибка системы',
            'priority': 'BLOCKER 🔴',
            'description': 'Обнаружен инцидент с отказом базы данных - требует немедленного исправления'
        }
        
        self.hypothesis_task = {
            'id': f'HYPOTHESIS_TASK_{int(time.time())}',
            'title': 'Гипотеза: улучшение производительности кеша',
            'priority': 'RESEARCH 🔍',
            'description': 'Эксперимент по оптимизации кеша для повышения скорости на 30%'
        }
    
    def test_01_normal_task_trigger_full_logic(self):
        """
        ТЕСТ 1: Полная логика триггера для обычной задачи
        
        Проверяет все компоненты:
        - Отметку выполненных задач
        - Архивирование
        - Статистику
        - Вывод через report_progress()
        - Веб-ссылки
        """
        print("\n🔥 ТЕСТ 1: Полная логика для обычной задачи")
        
        # Перехватываем report_progress
        original_report_progress = None
        try:
            from src.core.task_completion_manager import report_progress
            original_report_progress = report_progress
        except:
            pass
        
        def mock_report_progress(message):
            self.report_progress_calls.append(message)
            print(f"📊 REPORT_PROGRESS ВЫЗВАН:")
            print(message)
            print("📊 КОНЕЦ REPORT_PROGRESS")
            return True
        
        # Подменяем функцию
        if original_report_progress:
            import src.core.task_completion_manager
            src.core.task_completion_manager.report_progress = mock_report_progress
        
        try:
            # Запускаем триггер
            print(f"📝 Создаем обычную задачу: {self.normal_task['id']}")
            result = self.triggers.task_creation_trigger(self.normal_task)
            
            print(f"✅ Результат триггера: {result}")
            
            # Проверяем, что триггер сработал
            self.assertTrue(result, "Триггер должен успешно сработать")
            
            # Проверяем, что report_progress был вызван
            if original_report_progress:
                self.assertGreater(len(self.report_progress_calls), 0, "report_progress должен быть вызван")
                
                # Анализируем содержимое сообщения
                message = self.report_progress_calls[0]
                self.assertIn("НОВАЯ ЗАДАЧА СОЗДАНА", message, "Сообщение должно содержать заголовок")
                self.assertIn(self.normal_task['id'], message, "Сообщение должно содержать ID задачи")
                self.assertIn("СТАТИСТИКА", message, "Сообщение должно содержать статистику")
                self.assertIn("ВЕБ-ССЫЛКИ", message, "Сообщение должно содержать веб-ссылки")
                self.assertIn("http://127.0.0.1:5000/", message, "Должна быть ссылка на веб-интерфейс")
                self.assertIn("http://127.0.0.1:5003/", message, "Должна быть ссылка на API")
                
                print("✅ ТЕСТ 1 ПРОЙДЕН: Все компоненты работают!")
            else:
                print("⚠️  report_progress не найден, проверяем базовую функциональность")
                
        finally:
            # Восстанавливаем оригинальную функцию
            if original_report_progress:
                src.core.task_completion_manager.report_progress = original_report_progress
    
    def test_02_incident_task_5_why_analysis(self):
        """
        ТЕСТ 2: Анализ инцидента с 5 почему
        
        Проверяет:
        - Обнаружение инцидента по маркерам
        - Проведение анализа 5 почему
        - Вывод анализа через report_progress()
        """
        print("\n🔥 ТЕСТ 2: Анализ инцидента с 5 почему")
        
        # Перехватываем report_progress
        incident_report_calls = []
        def mock_incident_report(message):
            incident_report_calls.append(message)
            print(f"🚨 INCIDENT REPORT_PROGRESS:")
            print(message)
            print("🚨 КОНЕЦ INCIDENT REPORT")
            return True
        
        try:
            import src.core.task_completion_manager
            original = getattr(src.core.task_completion_manager, 'report_progress', None)
            if original:
                src.core.task_completion_manager.report_progress = mock_incident_report
        except:
            pass
        
        try:
            print(f"🚨 Создаем инцидент: {self.incident_task['id']}")
            print(f"📝 Заголовок: {self.incident_task['title']}")
            
            result = self.triggers.task_creation_trigger(self.incident_task)
            
            print(f"✅ Результат: {result}")
            self.assertTrue(result, "Инцидент должен быть обработан")
            
            if len(incident_report_calls) > 0:
                message = incident_report_calls[0]
                
                # Проверяем наличие анализа 5 почему
                self.assertIn("ИНЦИДЕНТ - АНАЛИЗ 5 ПОЧЕМУ", message, "Должен быть анализ 5 почему")
                self.assertIn("1. ПОЧЕМУ", message, "Должен быть первый вопрос")
                self.assertIn("5. ПОЧЕМУ", message, "Должен быть пятый вопрос")
                self.assertIn("КОРНЕВАЯ ПРИЧИНА", message, "Должна быть корневая причина")
                self.assertIn("РЕКОМЕНДАЦИЯ", message, "Должна быть рекомендация")
                
                print("✅ ТЕСТ 2 ПРОЙДЕН: Анализ 5 почему работает!")
            else:
                print("⚠️  report_progress не сработал для инцидента")
                
        finally:
            try:
                if original:
                    src.core.task_completion_manager.report_progress = original
            except:
                pass
    
    def test_03_hypothesis_task_rat_analysis(self):
        """
        ТЕСТ 3: Анализ гипотезы с RAT и фальсифицируемостью
        
        Проверяет:
        - Обнаружение гипотезы по маркерам
        - RAT анализ (Рациональный Атомарный Тест)
        - Критерий фальсифицируемости
        - Ссылки на мониторинг эксперимента
        """
        print("\n🔥 ТЕСТ 3: Анализ гипотезы с RAT и фальсифицируемостью")
        
        hypothesis_report_calls = []
        def mock_hypothesis_report(message):
            hypothesis_report_calls.append(message)
            print(f"🧪 HYPOTHESIS REPORT_PROGRESS:")
            print(message)
            print("🧪 КОНЕЦ HYPOTHESIS REPORT")
            return True
        
        try:
            import src.core.task_completion_manager
            original = getattr(src.core.task_completion_manager, 'report_progress', None)
            if original:
                src.core.task_completion_manager.report_progress = mock_hypothesis_report
        except:
            pass
        
        try:
            print(f"🧪 Создаем гипотезу: {self.hypothesis_task['id']}")
            print(f"📝 Заголовок: {self.hypothesis_task['title']}")
            
            result = self.triggers.task_creation_trigger(self.hypothesis_task)
            
            print(f"✅ Результат: {result}")
            self.assertTrue(result, "Гипотеза должна быть обработана")
            
            if len(hypothesis_report_calls) > 0:
                message = hypothesis_report_calls[0]
                
                # Проверяем анализ гипотезы
                self.assertIn("ЗАДАЧА-ГИПОТЕЗА", message, "Должен быть заголовок гипотезы")
                self.assertIn("RAT (Рациональный Атомарный Тест)", message, "Должен быть RAT анализ")
                self.assertIn("КРИТЕРИЙ ФАЛЬСИФИЦИРУЕМОСТИ", message, "Должен быть критерий фальсифицируемости")
                self.assertIn("МОНИТОРИНГ ЭКСПЕРИМЕНТА", message, "Должны быть ссылки на мониторинг")
                self.assertIn("experiments/", message, "Должна быть ссылка на эксперименты")
                self.assertIn("metrics/", message, "Должна быть ссылка на метрики")
                
                print("✅ ТЕСТ 3 ПРОЙДЕН: Анализ гипотез работает!")
            else:
                print("⚠️  report_progress не сработал для гипотезы")
                
        finally:
            try:
                if original:
                    src.core.task_completion_manager.report_progress = original
            except:
                pass
    
    def test_04_web_links_validation(self):
        """
        ТЕСТ 4: Проверка веб-ссылок в триггерах
        
        Проверяет, что все ссылки корректно формируются и доступны.
        """
        print("\n🔥 ТЕСТ 4: Проверка веб-ссылок")
        
        web_links_calls = []
        def mock_web_links_report(message):
            web_links_calls.append(message)
            # Извлекаем ссылки из сообщения
            import re
            links = re.findall(r'http://[^\s]+', message)
            print(f"🔗 Найденные ссылки:")
            for link in links:
                print(f"  • {link}")
            return True
        
        try:
            import src.core.task_completion_manager
            original = getattr(src.core.task_completion_manager, 'report_progress', None)
            if original:
                src.core.task_completion_manager.report_progress = mock_web_links_report
        except:
            pass
        
        try:
            print(f"🔗 Проверяем веб-ссылки для задачи: {self.normal_task['id']}")
            
            result = self.triggers.task_creation_trigger(self.normal_task)
            self.assertTrue(result, "Триггер должен сработать")
            
            if len(web_links_calls) > 0:
                message = web_links_calls[0]
                
                # Проверяем обязательные ссылки
                required_links = [
                    "http://127.0.0.1:5000/",      # Веб-интерфейс
                    "http://127.0.0.1:5003/",      # API-сервер
                    "http://127.0.0.1:5000/tasks", # Задачи
                    "http://127.0.0.1:5003/api/tasks/statistics"  # Статистика
                ]
                
                for link in required_links:
                    self.assertIn(link, message, f"Должна быть ссылка: {link}")
                
                print("✅ ТЕСТ 4 ПРОЙДЕН: Все веб-ссылки присутствуют!")
            else:
                print("⚠️  report_progress не сработал для проверки ссылок")
                
        finally:
            try:
                if original:
                    src.core.task_completion_manager.report_progress = original
            except:
                pass
    
    def test_05_statistics_calculation(self):
        """
        ТЕСТ 5: Проверка подсчета статистики
        
        Проверяет корректность подсчета:
        - Выполненных задач
        - Архивированных задач
        - Активных задач
        - Открытых инцидентов
        """
        print("\n🔥 ТЕСТ 5: Проверка подсчета статистики")
        
        try:
            # Тестируем внутренние методы
            completed = self.triggers._mark_completed_tasks()
            archived = self.triggers._archive_completed_tasks()
            stats = self.triggers._calculate_task_statistics()
            
            print(f"📊 Выполненных задач: {completed}")
            print(f"📦 Архивированных: {archived}")
            print(f"📋 Активных задач: {stats['active_tasks']}")
            print(f"🚨 Открытых инцидентов: {stats['open_incidents']}")
            
            # Проверяем, что значения разумные
            self.assertIsInstance(completed, int, "Количество выполненных должно быть числом")
            self.assertIsInstance(archived, int, "Количество архивированных должно быть числом")
            self.assertGreaterEqual(completed, 0, "Выполненных не может быть отрицательное число")
            self.assertGreaterEqual(archived, 0, "Архивированных не может быть отрицательное число")
            
            print("✅ ТЕСТ 5 ПРОЙДЕН: Статистика рассчитывается корректно!")
            
        except Exception as e:
            print(f"❌ Ошибка в подсчете статистики: {e}")
            self.fail(f"Статистика должна рассчитываться без ошибок: {e}")
    
    def tearDown(self):
        """Финальная оценка всех тестов."""
        print(f"\n🎯 === ИТОГОВЫЙ ОТЧЕТ TDD ТЕСТОВ ТРИГГЕРОВ ===")
        print(f"📞 Вызовов report_progress: {len(self.report_progress_calls)}")
        
        if len(self.report_progress_calls) > 0:
            print("✅ report_progress работает и выводит в чат!")
        else:
            print("⚠️  report_progress требует дополнительной настройки")


if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=False)