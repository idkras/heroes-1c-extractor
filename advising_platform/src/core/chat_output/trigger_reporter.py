#!/usr/bin/env python3
"""
Модуль для вывода информации в чат при создании документов через систему триггеров.

Этот модуль обеспечивает автоматический вывод информации в чат при:
1. Создании новых задач (с выводом статистики)
2. Создании инцидентов (с выводом 5-почему анализа)
3. Создании гипотез (с выводом RAT и критерия фальсифицируемости)
4. Создании стандартов
5. Для всех типов документов выводятся ссылки на веб-превью

Автор: AI Assistant
Дата: 22 мая 2025
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("chat_reporter.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("chat_reporter")


class TaskStatisticsProvider:
    """JTBD:
Я (разработчик) хочу использовать функциональность класса TaskStatisticsProvider, чтобы эффективно решать соответствующие задачи в системе.
    
    Класс для получения статистики по задачам."""
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """
        Получает статистику по задачам из системы.
        
        Returns:
            Dict[str, Any]: Словарь с метриками по задачам
        """
        try:
            # Импортируем модуль получения статистики задач из системы
            from advising_platform.src.core.storage.task_storage import get_task_statistics
            
            # Получаем статистику задач из хранилища
            stats = get_task_statistics()
            
            # Преобразуем ключи из хранилища в ожидаемые ключи для вывода в чат
            return {
                'total_tasks': stats.get('total', 0),
                'open_tasks': stats.get('not_started', 0),
                'in_progress_tasks': stats.get('in_progress', 0),
                'completed_tasks': stats.get('completed', 0),
                'average_lead_time': 0,  # Это значение пока не доступно из хранилища
                'high_priority': stats.get('high_priority', 0),
                'medium_priority': stats.get('medium_priority', 0),
                'low_priority': stats.get('low_priority', 0),
                'completion_rate': stats.get('completion_rate', 0)
            }
        except Exception as e:
            logger.error(f"Ошибка при получении статистики задач: {str(e)}")
            # Возвращаем базовую структуру в случае ошибки
            return {
                'total_tasks': 0,
                'open_tasks': 0,
                'in_progress_tasks': 0,
                'completed_tasks': 0,
                'average_lead_time': 0,
                'high_priority': 0,
                'medium_priority': 0,
                'low_priority': 0,
                'completion_rate': 0
            }


class ChatReporter(ABC):
    """JTBD:
Я (разработчик) хочу использовать функциональность класса ChatReporter, чтобы эффективно решать соответствующие задачи в системе.
    
    Базовый абстрактный класс для репортеров, выводящих информацию в чат."""
    
    @abstractmethod
    def report_creation(self, document_data: Dict[str, Any]) -> None:
        """
        Выводит информацию о создании документа в чат.
        
        Args:
            document_data (Dict[str, Any]): Данные о созданном документе
        """
        pass
    
    def _send_to_chat(self, message: str) -> None:
        """
        Отправляет сообщение в чат через встроенный инструмент report_progress Replit.
        
        Args:
            message (str): Сообщение для отправки в чат
        """
        try:
            # Логируем сообщение для отладки
            logger.info("Подготовка сообщения для отправки в чат")
            
            # Для отладки в консоли (не отображается пользователю)
            print(f"\n[DEBUG] Сообщение для отправки в чат:\n{message}")
            
            # Конвертируем многострочное сообщение в формат, подходящий для summary
            # в report_progress
            formatted_summary = self._format_for_report_progress(message)
            
            # Отправляем сообщение напрямую через встроенную функцию report_progress
            # Это самый надежный способ, так как функция доступна глобально в среде Replit
            try:
                # В среде Replit функция report_progress доступна глобально
                # Мы используем встроенную глобальную функцию
                print("\n[CHAT] Отправка сообщения через report_progress")
                
                # Используем глобальную функцию без импорта
                report_progress(summary=formatted_summary)
                logger.info("Сообщение успешно отправлено в чат через глобальную report_progress")
            except NameError:
                # Если функция недоступна глобально, выводим сообщение для отладки
                print("\n[CHAT] Глобальная функция report_progress недоступна, отправляем через консоль")
                print(f"\n[CHAT OUTPUT] {formatted_summary}\n")
            
            logger.info("Сообщение успешно подготовлено для отправки")
                
        except Exception as e:
            # В случае ошибки, выводим сообщение в консоль для отладки
            print(f"\n[ERROR] Ошибка при отправке в чат: {str(e)}")
            logger.error(f"Ошибка при отправке сообщения в чат: {str(e)}")
            
    def _format_for_report_progress(self, message: str) -> str:
        """
        Форматирует сообщение для использования в функции report_progress.
        Преобразует многострочное сообщение в формат, подходящий для вывода в чат.
        
        Args:
            message (str): Исходное сообщение
            
        Returns:
            str: Отформатированное сообщение для report_progress
        """
        lines = [line for line in message.split('\n') if line.strip()]
        if not lines:
            return "Пустое сообщение"
            
        # Находим основной заголовок (обычно первая содержательная строка)
        title = lines[0].strip()
        
        # Добавляем остальные строки с правильным форматированием
        result = title + "\n"
        
        for line in lines[1:]:
            if line.startswith('='):
                continue  # Пропускаем разделительные линии
            result += line + "\n"
            
        return result


class TaskChatReporter(ChatReporter):
    """JTBD:
Я (разработчик) хочу использовать функциональность класса TaskChatReporter, чтобы эффективно решать соответствующие задачи в системе.
    
    Класс для вывода информации о задачах в чат."""
    
    def __init__(self, stats_provider: Optional[TaskStatisticsProvider] = None):
        """
        Инициализирует репортер для задач.
        
        Args:
            stats_provider (TaskStatisticsProvider, optional): Провайдер статистики задач
        """
        self.stats_provider = stats_provider or TaskStatisticsProvider()
    
    def report_creation(self, document_data: Dict[str, Any]) -> None:
        """
        Выводит информацию о создании задачи в чат.
        
        Args:
            document_data (Dict[str, Any]): Данные о созданной задаче
        """
        try:
            logger.info(f"Вывод информации о создании задачи: {document_data['title']}")
            
            message = "\n" + "="*80 + "\n"
            message += f"🚀 СОЗДАНА НОВАЯ ЗАДАЧА: {document_data['title']}\n"
            message += f"Приоритет: {document_data.get('priority', 'Не указан')}\n"
            message += f"Статус: {document_data.get('status', 'Не указан')}\n"
            message += f"Создана: {document_data.get('created_at', 'Не указано')}\n"
            
            # Вывод ссылки на веб-превью
            if document_data.get('url'):
                message += f"\n🔍 Ссылка для просмотра: {document_data['url']}\n"
            
            # Выводим в консоль для отладки
            print(message)
            
            # Вывод статистики задач
            stats_message = self.report_statistics()
            message += stats_message
            
            message += "="*80 + "\n"
            
            # Отправляем сообщение в чат через API или специальную функцию
            self._send_to_chat(message)
        except Exception as e:
            logger.error(f"Ошибка при выводе информации о создании задачи: {str(e)}")
    
    def report_statistics(self) -> str:
        """JTBD:
Я (разработчик) хочу использовать функцию report_statistics, чтобы эффективно выполнить соответствующую операцию.
         
        Формирует сообщение со статистикой задач для вывода в чат.
        
        Returns:
            str: Сообщение со статистикой задач
        """
        try:
            logger.info("Формирование статистики задач для чата")
            
            stats = self.stats_provider.get_task_statistics()
            
            message = "\n📊 Статистика задач:\n"
            message += f"Всего задач: {stats['total_tasks']}\n"
            message += f"Открытых задач: {stats['open_tasks']}\n"
            message += f"Задач в работе: {stats['in_progress_tasks']}\n"
            message += f"Выполненных задач: {stats['completed_tasks']}\n"
            
            # Добавляем информацию о приоритетах задач
            message += f"\n🔥 Распределение по приоритетам:\n"
            message += f"Высокий приоритет: {stats.get('high_priority', 0)}\n"
            message += f"Средний приоритет: {stats.get('medium_priority', 0)}\n"
            message += f"Низкий приоритет: {stats.get('low_priority', 0)}\n"
            
            # Добавляем процент выполнения
            if stats.get('completion_rate', 0) > 0:
                message += f"\n✅ Прогресс выполнения: {stats.get('completion_rate', 0)}%\n"
            
            if stats.get('average_lead_time', 0) > 0:
                message += f"Среднее время выполнения: {stats['average_lead_time']} дней\n"
            
            return message
        except Exception as e:
            logger.error(f"Ошибка при формировании статистики задач: {str(e)}")
            return "\n📊 Статистика задач недоступна\n"


class IncidentChatReporter(ChatReporter):
    """JTBD:
Я (разработчик) хочу использовать функциональность класса IncidentChatReporter, чтобы эффективно решать соответствующие задачи в системе.
    
    Класс для вывода информации об инцидентах в чат."""
    
    def report_creation(self, document_data: Dict[str, Any]) -> None:
        """
        Выводит информацию о создании инцидента в чат.
        
        Args:
            document_data (Dict[str, Any]): Данные о созданном инциденте
        """
        try:
            logger.info(f"Вывод информации о создании инцидента: {document_data['title']}")
            
            message = "\n" + "="*80 + "\n"
            message += f"⚠️ СОЗДАН НОВЫЙ ИНЦИДЕНТ: {document_data['title']}\n"
            message += f"Важность: {document_data.get('severity', 'Не указана')}\n"
            message += f"Создан: {document_data.get('created_at', 'Не указано')}\n"
            
            # Вывод ссылки на веб-превью
            if document_data.get('url'):
                message += f"\n🔍 Ссылка для просмотра: {document_data['url']}\n"
            
            # Выводим в консоль для отладки
            print(message)
            
            # Вывод 5-почему анализа, если он есть
            if document_data.get('five_why_analysis'):
                analysis_message = self.report_five_why_analysis(document_data)
                message += analysis_message
            
            message += "="*80 + "\n"
            
            # Отправляем сообщение в чат через API или специальную функцию
            self._send_to_chat(message)
        except Exception as e:
            logger.error(f"Ошибка при выводе информации о создании инцидента: {str(e)}")
    
    def report_five_why_analysis(self, document_data: Dict[str, Any]) -> str:
        """
        Формирует сообщение с 5-почему анализом инцидента для вывода в чат.
        
        Args:
            document_data (Dict[str, Any]): Данные об инциденте
            
        Returns:
            str: Сообщение с 5-почему анализом
        """
        try:
            logger.info(f"Формирование 5-почему анализа для инцидента: {document_data['title']}")
            
            five_why = document_data.get('five_why_analysis', {})
            
            message = "\n🔎 5-почему анализ:\n"
            
            # Вывод проблемы
            if five_why.get('problem'):
                message += f"Проблема: {five_why['problem']}\n"
            
            # Вывод цепочки "почему"
            if five_why.get('whys') and isinstance(five_why['whys'], list):
                message += "\nЦепочка причин:\n"
                for i, why in enumerate(five_why['whys'], 1):
                    message += f"{i}. {why}\n"
            
            # Вывод корневой причины
            if five_why.get('root_cause'):
                message += f"\nКорневая причина: {five_why['root_cause']}\n"
            
            # Вывод решения
            if five_why.get('solution'):
                message += f"\nРешение: {five_why['solution']}\n"
            
            return message
        except Exception as e:
            logger.error(f"Ошибка при формировании 5-почему анализа: {str(e)}")
            return "\n🔎 5-почему анализ недоступен\n"


class HypothesisChatReporter(ChatReporter):
    """JTBD:
Я (разработчик) хочу использовать функциональность класса HypothesisChatReporter, чтобы эффективно решать соответствующие задачи в системе.
    
    Класс для вывода информации о гипотезах в чат."""
    
    def report_creation(self, document_data: Dict[str, Any]) -> None:
        """
        Выводит информацию о создании гипотезы в чат.
        
        Args:
            document_data (Dict[str, Any]): Данные о созданной гипотезе
        """
        try:
            logger.info(f"Вывод информации о создании гипотезы: {document_data['title']}")
            
            message = "\n" + "="*80 + "\n"
            message += f"❓ СОЗДАНА НОВАЯ ГИПОТЕЗА: {document_data['title']}\n"
            message += f"Создана: {document_data.get('created_at', 'Не указано')}\n"
            
            # Вывод ссылки на веб-превью
            if document_data.get('url'):
                message += f"\n🔍 Ссылка для просмотра: {document_data['url']}\n"
            
            # Выводим в консоль для отладки
            print(message)
            
            # Вывод RAT и критерия фальсифицируемости
            rat_message = self.report_rat_and_falsifiability(document_data)
            message += rat_message
            
            message += "="*80 + "\n"
            
            # Отправляем сообщение в чат через API или специальную функцию
            self._send_to_chat(message)
        except Exception as e:
            logger.error(f"Ошибка при выводе информации о создании гипотезы: {str(e)}")
    
    def report_rat_and_falsifiability(self, document_data: Dict[str, Any]) -> str:
        """
        Формирует сообщение с RAT и критерием фальсифицируемости гипотезы для вывода в чат.
        
        Args:
            document_data (Dict[str, Any]): Данные о гипотезе
            
        Returns:
            str: Сообщение с RAT и критерием фальсифицируемости
        """
        try:
            logger.info(f"Формирование RAT и критерия фальсифицируемости для гипотезы: {document_data['title']}")
            
            rat = document_data.get('rat', {})
            
            message = "\n📋 RAT-анализ:\n"
            
            # Вывод реалистичности
            if rat.get('realistic'):
                message += f"R - {rat['realistic']}\n"
            
            # Вывод амбициозности
            if rat.get('ambitious'):
                message += f"A - {rat['ambitious']}\n"
            
            # Вывод тестируемости
            if rat.get('testable'):
                message += f"T - {rat['testable']}\n"
            
            # Вывод критерия фальсифицируемости
            if document_data.get('falsifiability'):
                message += f"\n🔬 Критерий фальсифицируемости:\n"
                message += f"{document_data['falsifiability']}\n"
            
            return message
        except Exception as e:
            logger.error(f"Ошибка при формировании RAT и критерия фальсифицируемости: {str(e)}")
            return "\n📋 RAT-анализ и критерий фальсифицируемости недоступны\n"


class StandardChatReporter(ChatReporter):
    """JTBD:
Я (разработчик) хочу использовать функциональность класса StandardChatReporter, чтобы эффективно решать соответствующие задачи в системе.
    
    Класс для вывода информации о стандартах в чат."""
    
    def report_creation(self, document_data: Dict[str, Any]) -> None:
        """
        Выводит информацию о создании стандарта в чат.
        
        Args:
            document_data (Dict[str, Any]): Данные о созданном стандарте
        """
        try:
            logger.info(f"Вывод информации о создании стандарта: {document_data['title']}")
            
            message = "\n" + "="*80 + "\n"
            message += f"📋 СОЗДАН НОВЫЙ СТАНДАРТ: {document_data['title']}\n"
            message += f"Создан: {document_data.get('created_at', 'Не указано')}\n"
            
            # Вывод ссылки на веб-превью
            if document_data.get('url'):
                message += f"\n🔍 Ссылка для просмотра: {document_data['url']}\n"
            
            message += "="*80 + "\n"
            
            # Выводим в консоль для отладки
            print(message)
            
            # Отправляем сообщение в чат через API или специальную функцию
            self._send_to_chat(message)
        except Exception as e:
            logger.error(f"Ошибка при выводе информации о создании стандарта: {str(e)}")


class ChatReporterFactory:
    """JTBD:
Я (разработчик) хочу использовать функциональность класса ChatReporterFactory, чтобы эффективно решать соответствующие задачи в системе.
    
    Фабрика для создания репортеров различных типов документов."""
    
    def create_reporter(self, document_type: str) -> ChatReporter:
        """
        Создает репортер для указанного типа документа.
        
        Args:
            document_type (str): Тип документа ('task', 'incident', 'hypothesis', 'standard')
        
        Returns:
            ChatReporter: Репортер для указанного типа документа
        
        Raises:
            ValueError: Если указан неизвестный тип документа
        """
        if document_type == 'task':
            return TaskChatReporter()
        elif document_type == 'incident':
            return IncidentChatReporter()
        elif document_type == 'hypothesis':
            return HypothesisChatReporter()
        elif document_type == 'standard':
            return StandardChatReporter()
        else:
            raise ValueError(f"Неизвестный тип документа: {document_type}")


# Функция для интеграции с триггерами
def process_document_creation_trigger(document_type: str, document_data: Dict[str, Any]) -> None:
    """
    Обрабатывает триггер создания документа и выводит информацию в чат.
    
    Args:
        document_type (str): Тип созданного документа
        document_data (Dict[str, Any]): Данные о созданном документе
    """
    try:
        logger.info(f"Обработка триггера создания документа типа {document_type}")
        
        factory = ChatReporterFactory()
        reporter = factory.create_reporter(document_type)
        reporter.report_creation(document_data)
    except Exception as e:
        logger.error(f"Ошибка при обработке триггера создания документа: {str(e)}")