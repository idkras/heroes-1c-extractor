#!/usr/bin/env python3
"""
Модуль для обработки инцидентов с улучшенной интеграцией вывода отчетов в чат.

Решает проблему отсутствия вывода анализа 5-почему в чат-интерфейс
и добавляет проверку дублирования при создании инцидентов.

Автор: AI Assistant
Дата: 20 мая 2025
"""

import os
import re
import json
import logging
import traceback
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("incident_processor")

# Импортируем улучшенную систему отчетов
try:
    from advising_platform.src.tools.reporting.report_interface import (
        report_progress, force_report, report_five_why_analysis
    )
    REPORT_INTERFACE_AVAILABLE = True
    logger.info("Улучшенный интерфейс отчетов доступен")
except ImportError as e:
    REPORT_INTERFACE_AVAILABLE = False
    logger.warning(f"Не удалось импортировать улучшенный интерфейс отчетов: {e}")
    traceback.print_exc()

# Константы
INCIDENTS_FILE = "[todo · incidents]/ai.incidents.md"

class IncidentProcessor:
    """Класс для обработки инцидентов с улучшенной отчетностью."""
    
    def __init__(self):
        self.incidents_file = INCIDENTS_FILE
    
    def extract_five_why_from_incident(self, incident_text: str) -> Tuple[str, List[Dict[str, str]], str]:
        """
        Извлекает название инцидента, анализ 5-почему и корневую причину из текста инцидента.
        
        Args:
            incident_text: Текст инцидента
            
        Returns:
            Tuple: (название инцидента, анализ 5-почему, корневая причина)
        """
        # Извлекаем название инцидента
        title_match = re.search(r'#\s+(.*?)\n', incident_text)
        title = title_match.group(1) if title_match else "Без названия"
        
        # Извлекаем анализ 5-почему
        five_why_list = []
        why_matches = re.finditer(r'###\s+Почему\s+#(\d+):\s*(.*?)\n\s*\*\*Ответ\*\*:\s*(.*?)(?=\n###|\n##|\n\*\*|$)', 
                                  incident_text, re.DOTALL)
        
        for match in why_matches:
            number = match.group(1)
            question = match.group(2).strip()
            answer = match.group(3).strip()
            
            five_why_list.append({
                "number": number,
                "question": question,
                "answer": answer
            })
        
        # Извлекаем корневую причину
        root_cause_match = re.search(r'##\s+🌟\s+Корневая\s+причина\s*\n(.*?)(?=\n##|$)', incident_text, re.DOTALL)
        root_cause = root_cause_match.group(1).strip() if root_cause_match else "Не определена"
        
        return title, five_why_list, root_cause
    
    def process_incident_file(self, file_path: str, force_output: bool = False) -> bool:
        """
        Обрабатывает файл инцидента и отправляет 5-почему анализ в чат.
        
        Args:
            file_path: Путь к файлу инцидента
            force_output: Принудительный вывод в чат без проверки на дублирование
            
        Returns:
            bool: True, если обработка прошла успешно, иначе False
        """
        try:
            # Проверяем существование файла
            if not os.path.exists(file_path):
                logger.warning(f"Файл инцидента не найден: {file_path}")
                return False
            
            # Читаем содержимое файла
            with open(file_path, 'r', encoding='utf-8') as f:
                incident_text = f.read()
            
            # Извлекаем данные инцидента
            title, five_why_list, root_cause = self.extract_five_why_from_incident(incident_text)
            
            # Проверяем, есть ли анализ 5-почему
            if not five_why_list:
                logger.warning(f"В инциденте '{title}' не найден анализ 5-почему")
                return False
            
            # Выводим информацию об инциденте в чат
            logger.info(f"Обработка инцидента: {title}")
            logger.info(f"Анализ 5-почему: {len(five_why_list)} вопросов")
            logger.info(f"Корневая причина: {root_cause}")
            
            # Отправляем отчет в чат
            if REPORT_INTERFACE_AVAILABLE:
                report_five_why_analysis(title, five_why_list, root_cause)
                logger.info(f"Анализ 5-почему для инцидента '{title}' отправлен в чат")
            else:
                # Если улучшенный интерфейс недоступен, используем стандартный механизм
                self._legacy_report_five_why(title, five_why_list, root_cause)
            
            return True
        except Exception as e:
            logger.error(f"Ошибка при обработке файла инцидента {file_path}: {e}")
            traceback.print_exc()
            return False
    
    def _legacy_report_five_why(self, title: str, five_why_list: List[Dict[str, str]], root_cause: str) -> None:
        """
        Запасной вариант отчета о 5-почему анализе, если улучшенный интерфейс недоступен.
        
        Args:
            title: Название инцидента
            five_why_list: Список вопросов и ответов
            root_cause: Корневая причина
        """
        try:
            # Формируем отчет
            report = {
                "incident": {
                    "title": title,
                    "five_why": five_why_list,
                    "root_cause": root_cause
                }
            }
            
            # Пробуем использовать стандартную функцию report_progress
            if 'report_progress' in globals():
                report_progress(report)
                logger.info(f"Анализ 5-почему для инцидента '{title}' отправлен через стандартный механизм")
            else:
                # Если и стандартный механизм недоступен, просто выводим в консоль
                print(f"\n{'=' * 80}")
                print(f"🔍 Анализ 5-почему для инцидента: {title}")
                for why in five_why_list:
                    print(f"Почему #{why.get('number', '?')}: {why.get('question', '')}")
                    print(f"Ответ: {why.get('answer', '')}")
                print(f"🌱 Корневая причина: {root_cause}")
                print(f"{'=' * 80}\n")
                
        except Exception as e:
            logger.error(f"Ошибка при создании запасного отчета: {e}")
            traceback.print_exc()
    
    def check_duplicates(self, incident_title: str, incident_text: str) -> List[Dict[str, Any]]:
        """
        Проверяет наличие дубликатов для нового инцидента.
        
        Args:
            incident_title: Название инцидента
            incident_text: Содержимое инцидента
            
        Returns:
            List[Dict[str, Any]]: Список потенциальных дубликатов
        """
        duplicates = []
        
        try:
            # Проверяем существование файла инцидентов
            if not os.path.exists(self.incidents_file):
                logger.warning(f"Файл инцидентов не найден: {self.incidents_file}")
                return duplicates
            
            # Читаем содержимое файла инцидентов
            with open(self.incidents_file, 'r', encoding='utf-8') as f:
                incidents_content = f.read()
            
            # Разделяем файл на отдельные инциденты
            incidents = re.split(r'(?=# )', incidents_content)
            
            # Импортируем библиотеку для определения схожести текста
            try:
                from difflib import SequenceMatcher
                
                # Для каждого инцидента проверяем схожесть с новым инцидентом
                for incident in incidents:
                    if not incident.strip():
                        continue
                    
                    # Извлекаем заголовок инцидента
                    title_match = re.search(r'#\s+(.*?)\n', incident)
                    if not title_match:
                        continue
                        
                    existing_title = title_match.group(1)
                    
                    # Вычисляем схожесть заголовков
                    title_similarity = SequenceMatcher(None, incident_title, existing_title).ratio()
                    
                    # Вычисляем схожесть содержимого
                    content_similarity = SequenceMatcher(None, incident_text, incident).ratio()
                    
                    # Если схожесть выше порога, добавляем в список дубликатов
                    if title_similarity > 0.7 or content_similarity > 0.5:
                        duplicates.append({
                            "title": existing_title,
                            "title_similarity": title_similarity,
                            "content_similarity": content_similarity
                        })
            except ImportError:
                logger.warning("Не удалось импортировать библиотеку difflib для определения схожести текста")
                
        except Exception as e:
            logger.error(f"Ошибка при проверке дубликатов: {e}")
            traceback.print_exc()
        
        return duplicates
    
    def scan_all_incidents(self) -> int:
        """
        Сканирует все инциденты в директории инцидентов.
        
        Returns:
            int: Количество обработанных инцидентов
        """
        processed_count = 0
        incident_dir = os.path.dirname(self.incidents_file)
        
        try:
            # Проверяем существование директории
            if not os.path.exists(incident_dir):
                logger.warning(f"Директория инцидентов не найдена: {incident_dir}")
                return 0
            
            # Сканируем директорию инцидентов
            for root, dirs, files in os.walk(incident_dir):
                for file in files:
                    if file.endswith('.md') and 'incident' in file.lower():
                        file_path = os.path.join(root, file)
                        
                        # Обрабатываем файл инцидента
                        if self.process_incident_file(file_path):
                            processed_count += 1
            
            logger.info(f"Обработано инцидентов: {processed_count}")
            
        except Exception as e:
            logger.error(f"Ошибка при сканировании инцидентов: {e}")
            traceback.print_exc()
        
        return processed_count

# Создаем экземпляр процессора инцидентов для использования в других модулях
incident_processor = IncidentProcessor()

# Функция для обработки инцидента из внешних модулей
def process_incident(file_path: str, force_output: bool = False) -> bool:
    """
    Обрабатывает файл инцидента и отправляет 5-почему анализ в чат.
    
    Args:
        file_path: Путь к файлу инцидента
        force_output: Принудительный вывод в чат без проверки на дублирование
        
    Returns:
        bool: True, если обработка прошла успешно, иначе False
    """
    return incident_processor.process_incident_file(file_path, force_output)

# Функция для проверки дубликатов инцидента
def check_incident_duplicates(incident_title: str, incident_text: str) -> List[Dict[str, Any]]:
    """
    Проверяет наличие дубликатов для нового инцидента.
    
    Args:
        incident_title: Название инцидента
        incident_text: Содержимое инцидента
        
    Returns:
        List[Dict[str, Any]]: Список потенциальных дубликатов
    """
    return incident_processor.check_duplicates(incident_title, incident_text)

# Функция для сканирования всех инцидентов
def scan_all_incidents() -> int:
    """
    Сканирует все инциденты в директории инцидентов.
    
    Returns:
        int: Количество обработанных инцидентов
    """
    return incident_processor.scan_all_incidents()

# Если скрипт запущен напрямую, выполняем сканирование всех инцидентов
if __name__ == "__main__":
    logger.info("Запуск сканирования инцидентов")
    count = scan_all_incidents()
    logger.info(f"Завершено сканирование инцидентов, обработано: {count}")