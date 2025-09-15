#!/usr/bin/env python3
"""
Скрипт для проверки обратной хронологии в API для context.md и next_actions.md.

Проверяет:
1. Сортировку записей в обратном хронологическом порядке в context.md
2. Сортировку daily_digests в next_actions.md
3. Соответствие API требованиям Client Context Standard v2.2

Использование:
    python verify_chronology.py --project "rick.ai"
"""

import os
import sys
import json
import argparse
import requests
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('verify_chronology')

# Конфигурация
API_BASE_URL = "http://localhost:5003/api/v1/external"

def check_context_chronology(project_id, api_base_url=API_BASE_URL):
    """
    Проверяет обратную хронологию в context.md.
    
    Args:
        project_id: Идентификатор проекта
        api_base_url: URL API
    
    Returns:
        bool: True, если хронология соблюдена, иначе False
    """
    api_url = f"{api_base_url}/context/{project_id}"
    
    try:
        response = requests.get(api_url)
        
        if response.status_code == 200:
            result = response.json()
            context_data = result.get("context", {})
            history_entries = context_data.get("history", [])
            
            # Проверяем обратную хронологию
            if history_entries:
                is_chronological = True
                prev_date = None
                
                logger.info(f"Проверка хронологии для {len(history_entries)} записей в context.md")
                
                for i, entry in enumerate(history_entries):
                    current_date = entry.get("date", "")
                    logger.debug(f"Запись {i+1}: {current_date}")
                    
                    # Если первая запись, сохраняем дату
                    if prev_date is None:
                        prev_date = current_date
                        continue
                    
                    # Проверяем, что текущая дата не позже предыдущей
                    # (это обеспечивает обратную хронологию - новые записи вверху)
                    if current_date > prev_date:
                        logger.error(f"Нарушение обратной хронологии в context.md: {prev_date} перед {current_date}")
                        is_chronological = False
                    
                    prev_date = current_date
                
                if is_chronological:
                    logger.info("✅ Context.md: Обратная хронология соблюдена (новые записи вверху)")
                else:
                    logger.warning("❌ Context.md: Обнаружено нарушение обратной хронологии!")
                
                return is_chronological
            else:
                logger.warning("⚠️ Context.md: Не найдены записи для проверки хронологии")
                return True
        else:
            logger.error(f"Ошибка при получении данных context.md: {response.status_code}")
            logger.error(f"Ответ: {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"Ошибка при проверке context.md: {e}")
        return False

def check_next_actions_chronology(api_base_url=API_BASE_URL, days_back=30):
    """
    Проверяет обратную хронологию в next_actions.md.
    
    Args:
        api_base_url: URL API
        days_back: Количество дней для проверки
    
    Returns:
        bool: True, если хронология соблюдена, иначе False
    """
    api_url = f"{api_base_url}/next_actions?days_back={days_back}"
    
    try:
        response = requests.get(api_url)
        
        if response.status_code == 200:
            result = response.json()
            actions_data = result.get("actions_data", {})
            daily_digests = actions_data.get("daily_digests", [])
            
            # Проверяем обратную хронологию
            if daily_digests:
                is_chronological = True
                prev_date = None
                
                logger.info(f"Проверка хронологии для {len(daily_digests)} дневных дайджестов в next_actions.md")
                
                for i, digest in enumerate(daily_digests):
                    current_date = digest.get("date", "")
                    logger.debug(f"Дайджест {i+1}: {current_date}")
                    
                    # Если первый дайджест, сохраняем дату
                    if prev_date is None:
                        prev_date = current_date
                        continue
                    
                    # Проверяем, что текущая дата не позже предыдущей
                    if current_date > prev_date:
                        logger.error(f"Нарушение обратной хронологии в next_actions.md: {prev_date} перед {current_date}")
                        is_chronological = False
                    
                    prev_date = current_date
                
                if is_chronological:
                    logger.info("✅ Next_actions.md: Обратная хронология соблюдена (новые записи вверху)")
                else:
                    logger.warning("❌ Next_actions.md: Обнаружено нарушение обратной хронологии!")
                
                return is_chronological
            else:
                logger.warning("⚠️ Next_actions.md: Не найдены дневные дайджесты для проверки хронологии")
                return True
        else:
            logger.error(f"Ошибка при получении данных next_actions.md: {response.status_code}")
            logger.error(f"Ответ: {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"Ошибка при проверке next_actions.md: {e}")
        return False

def verify_api_implementation(api_base_url=API_BASE_URL):
    """
    Проверяет реализацию API на соответствие требованиям Client Context Standard v2.2.
    
    Args:
        api_base_url: URL API
    
    Returns:
        bool: True, если API соответствует требованиям, иначе False
    """
    try:
        # Проверяем доступность API
        response = requests.get(f"{api_base_url}/healthcheck")
        if response.status_code != 200:
            logger.error(f"API недоступен: {response.status_code}")
            return False
        
        logger.info("✅ API доступен и отвечает на запросы")
        
        # Проверяем поддержку обратной хронологии в next_actions.md
        next_actions_chronology = check_next_actions_chronology(api_base_url)
        
        return next_actions_chronology
    
    except Exception as e:
        logger.error(f"Ошибка при проверке API: {e}")
        return False

def main():
    """Основная функция скрипта."""
    parser = argparse.ArgumentParser(description='Проверка обратной хронологии в API')
    parser.add_argument('--project', help='Идентификатор проекта для проверки context.md')
    parser.add_argument('--api-url', default=API_BASE_URL, help='URL API')
    parser.add_argument('--days-back', type=int, default=30, help='Количество дней для проверки next_actions.md')
    parser.add_argument('--verbose', '-v', action='store_true', help='Подробный вывод')
    
    args = parser.parse_args()
    
    # Настраиваем подробный вывод
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    logger.info("Начинаем проверку обратной хронологии в API...")
    
    # Проверяем общую реализацию API
    api_result = verify_api_implementation(args.api_url)
    
    # Если указан проект, проверяем хронологию в context.md
    if args.project:
        context_result = check_context_chronology(args.project, args.api_url)
    else:
        context_result = None
        logger.info("Проект не указан, пропускаем проверку context.md")
    
    # Выводим общий результат
    logger.info("==== Результаты проверки обратной хронологии ====")
    if api_result:
        logger.info("✅ API поддерживает обратную хронологию для next_actions.md")
    else:
        logger.error("❌ API НЕ соответствует требованиям обратной хронологии для next_actions.md")
    
    if context_result is not None:
        if context_result:
            logger.info(f"✅ Context.md проекта {args.project} соответствует обратной хронологии")
        else:
            logger.error(f"❌ Context.md проекта {args.project} НЕ соответствует обратной хронологии")
    
    # Общий вывод для обновления статуса гипотезы
    if api_result and (context_result is None or context_result):
        logger.info("==== ГИПОТЕЗА ПОДТВЕРЖДЕНА ====")
        logger.info("API реализует обратную хронологию в соответствии с Client Context Standard v2.2")
        return 0
    else:
        logger.error("==== ГИПОТЕЗА НЕ ПОДТВЕРЖДЕНА ====")
        logger.error("Обнаружены проблемы с обратной хронологией")
        return 1

if __name__ == "__main__":
    sys.exit(main())