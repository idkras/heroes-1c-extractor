#!/usr/bin/env python3
"""
Скрипт для проверки вывода сообщений в чат при создании различных типов объектов.
"""

import os
import time
import json
import datetime
import requests
import logging
from typing import Dict, Any, Optional, List, Union

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("check_chat_reporting")

# API URL
API_BASE_URL = "http://localhost:5003/api/v1"
WEB_BASE_URL = "http://localhost:5000"

def generate_web_url(object_type: str, object_path: str) -> str:
    """
    Генерирует веб-URL для просмотра объекта.
    
    Args:
        object_type: Тип объекта (task, incident, hypothesis, standard)
        object_path: Путь к файлу объекта
        
    Returns:
        str: URL для просмотра объекта
    """
    # Получаем имя файла
    file_name = os.path.basename(object_path)
    
    # Генерируем URL в зависимости от типа объекта
    if object_type == "task":
        return f"{WEB_BASE_URL}/tasks/view?file={file_name}"
    elif object_type == "incident":
        return f"{WEB_BASE_URL}/incidents/view?file={file_name}"
    elif object_type == "hypothesis":
        return f"{WEB_BASE_URL}/hypotheses/view?file={file_name}"
    elif object_type == "standard":
        return f"{WEB_BASE_URL}/standards/view?file={file_name}"
    else:
        return f"{WEB_BASE_URL}/view?path={object_path}"

def create_task() -> Dict[str, Any]:
    """
    Создает тестовую задачу и выводит информацию в чат.
    
    Returns:
        Dict[str, Any]: Ответ API
    """
    endpoint = f"{API_BASE_URL}/tasks/create"
    data = {
        "title": f"Тестовая задача от {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "description": "Эта задача создана для проверки вывода сообщений в чат.",
        "priority": "Высокий",
        "task_type": "Проверка"
    }
    
    try:
        logger.info(f"Отправка запроса на создание задачи: {endpoint}")
        response = requests.post(endpoint, json=data)
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Задача успешно создана: {result.get('message', '')}")
            
            # Генерируем URL для просмотра задачи
            task_id = result.get('task_id', '')
            if task_id:
                web_url = generate_web_url("task", task_id)
                logger.info(f"URL для просмотра задачи: {web_url}")
                
                # Добавляем прямой вывод в консоль для надежности
                print(f"\n{'=' * 80}")
                print(f"ЗАДАЧА СОЗДАНА: {result.get('message', '')}")
                print(f"URL для просмотра: {web_url}")
                print(f"{'=' * 80}\n")
                
                try:
                    # Используем отчет о прогрессе для вывода в чат
                    from advising_platform.src.tools.reporting.report_interface import report_progress
                    
                    # Создаем отчет о создании задачи
                    report_data = {
                        "summary": f"✅ Задача создана: {data['title']}\n"\
                                  f"🔗 URL для просмотра: {web_url}"
                    }
                    
                    # Отправляем отчет
                    report_progress(report_data, force_output=True)
                except Exception as e:
                    logger.error(f"Ошибка при отправке отчета о создании задачи: {e}")
            
            return result
        else:
            logger.error(f"Ошибка при создании задачи: {response.status_code} - {response.text}")
            return {"success": False, "error": f"Ошибка при создании задачи: {response.status_code}"}
    except Exception as e:
        logger.error(f"Исключение при создании задачи: {e}")
        return {"success": False, "error": str(e)}

def create_incident() -> Dict[str, Any]:
    """
    Создает тестовый инцидент и выводит информацию в чат.
    
    Returns:
        Dict[str, Any]: Ответ API
    """
    endpoint = f"{API_BASE_URL}/incidents/create"
    data = {
        "title": f"Тестовый инцидент от {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "description": """# Проблема
        
При выводе отчетов в чат возникают ошибки и сообщения не отображаются.

## 5 Почему

1. **Почему не отображаются сообщения в чате?**
   Потому что не работает интеграция с API Replit.

2. **Почему не работает интеграция с API?**
   Потому что изменился интерфейс API.

3. **Почему мы не заметили изменение интерфейса API?**
   Потому что не было настроено тестирование интеграции.

4. **Почему не было настроено тестирование?**
   Потому что не было выделено время на написание тестов.

5. **Почему не было выделено время?**
   Потому что тестирование не было включено в план разработки.

## Корневая причина

Отсутствие включения тестирования внешних интеграций в план разработки.
        """,
        "severity": 4,
        "incident_type": "Интеграция"
    }
    
    try:
        logger.info(f"Отправка запроса на создание инцидента: {endpoint}")
        response = requests.post(endpoint, json=data)
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Инцидент успешно создан: {result.get('message', '')}")
            
            # Генерируем URL для просмотра инцидента
            incident_id = result.get('incident_id', '')
            if incident_id:
                web_url = generate_web_url("incident", incident_id)
                logger.info(f"URL для просмотра инцидента: {web_url}")
                
                # Добавляем прямой вывод в консоль для надежности
                print(f"\n{'=' * 80}")
                print(f"ИНЦИДЕНТ СОЗДАН: {result.get('message', '')}")
                print(f"URL для просмотра: {web_url}")
                print(f"{'=' * 80}\n")
                
                try:
                    # Используем отчет о прогрессе для вывода в чат
                    from advising_platform.src.tools.reporting.report_interface import report_progress
                    
                    # Создаем отчет о создании инцидента с анализом 5-почему
                    report_data = {
                        "incident": {
                            "title": data['title'],
                            "five_why": [
                                {"question": "Почему не отображаются сообщения в чате?", 
                                 "answer": "Потому что не работает интеграция с API Replit."},
                                {"question": "Почему не работает интеграция с API?", 
                                 "answer": "Потому что изменился интерфейс API."},
                                {"question": "Почему мы не заметили изменение интерфейса API?", 
                                 "answer": "Потому что не было настроено тестирование интеграции."},
                                {"question": "Почему не было настроено тестирование?", 
                                 "answer": "Потому что не было выделено время на написание тестов."},
                                {"question": "Почему не было выделено время?", 
                                 "answer": "Потому что тестирование не было включено в план разработки."}
                            ],
                            "root_cause": "Отсутствие включения тестирования внешних интеграций в план разработки."
                        }
                    }
                    
                    # Отправляем отчет
                    report_progress(report_data, force_output=True)
                    
                    # Добавляем URL для просмотра отдельным сообщением
                    url_data = {
                        "summary": f"🔗 URL для просмотра инцидента: {web_url}"
                    }
                    report_progress(url_data, force_output=True)
                except Exception as e:
                    logger.error(f"Ошибка при отправке отчета о создании инцидента: {e}")
            
            return result
        else:
            logger.error(f"Ошибка при создании инцидента: {response.status_code} - {response.text}")
            return {"success": False, "error": f"Ошибка при создании инцидента: {response.status_code}"}
    except Exception as e:
        logger.error(f"Исключение при создании инцидента: {e}")
        return {"success": False, "error": str(e)}

def create_hypothesis() -> Dict[str, Any]:
    """
    Создает тестовую гипотезу и выводит информацию в чат.
    
    Returns:
        Dict[str, Any]: Ответ API
    """
    endpoint = f"{API_BASE_URL}/hypotheses/create"
    data = {
        "title": f"Гипотеза о выводе в чат от {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "description": """# Гипотеза

При использовании прямого вызова функции report_progress из API Replit сообщения будут корректно отображаться в чате.

# Критерии RAT

- Релевантность: Гипотеза напрямую связана с проблемой отображения сообщений в чате.
- Проверяемость: Можно легко проверить, отображаются ли сообщения в чате после изменений.
- Выполнимость: Интеграция с API Replit может быть реализована в разумные сроки.

# Фальсифицируемость

Гипотеза будет опровергнута, если после внедрения прямого вызова API Replit сообщения все равно не будут отображаться в чате.
        """,
        "category": "Интеграция",
        "status": "pending"
    }
    
    try:
        logger.info(f"Отправка запроса на создание гипотезы: {endpoint}")
        response = requests.post(endpoint, json=data)
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Гипотеза успешно создана: {result.get('message', '')}")
            
            # Генерируем URL для просмотра гипотезы
            hypothesis_id = result.get('hypothesis_id', '')
            if hypothesis_id:
                web_url = generate_web_url("hypothesis", hypothesis_id)
                logger.info(f"URL для просмотра гипотезы: {web_url}")
                
                # Добавляем прямой вывод в консоль для надежности
                print(f"\n{'=' * 80}")
                print(f"ГИПОТЕЗА СОЗДАНА: {result.get('message', '')}")
                print(f"URL для просмотра: {web_url}")
                print(f"{'=' * 80}\n")
                
                try:
                    # Используем отчет о прогрессе для вывода в чат
                    from advising_platform.src.tools.reporting.report_interface import report_progress
                    
                    # Создаем отчет о создании гипотезы
                    report_data = {
                        "hypothesis": {
                            "title": data['title'],
                            "rat": """- Релевантность: Гипотеза напрямую связана с проблемой отображения сообщений в чате.
- Проверяемость: Можно легко проверить, отображаются ли сообщения в чате после изменений.
- Выполнимость: Интеграция с API Replit может быть реализована в разумные сроки.""",
                            "falsifiability": "Гипотеза будет опровергнута, если после внедрения прямого вызова API Replit сообщения все равно не будут отображаться в чате."
                        }
                    }
                    
                    # Отправляем отчет
                    report_progress(report_data, force_output=True)
                    
                    # Добавляем URL для просмотра отдельным сообщением
                    url_data = {
                        "summary": f"🔗 URL для просмотра гипотезы: {web_url}"
                    }
                    report_progress(url_data, force_output=True)
                except Exception as e:
                    logger.error(f"Ошибка при отправке отчета о создании гипотезы: {e}")
            
            return result
        else:
            logger.error(f"Ошибка при создании гипотезы: {response.status_code} - {response.text}")
            return {"success": False, "error": f"Ошибка при создании гипотезы: {response.status_code}"}
    except Exception as e:
        logger.error(f"Исключение при создании гипотезы: {e}")
        return {"success": False, "error": str(e)}

def test_direct_report() -> bool:
    """
    Тестирует прямой вывод сообщений в чат с использованием Replit API.
    
    Returns:
        bool: True, если сообщение успешно отправлено, иначе False
    """
    try:
        # Импортируем функцию для отчета о прогрессе
        from antml.function_calls import report_progress
        
        # Отправляем тестовое сообщение
        message = f"✅ Тестовое сообщение от check_chat_reporting.py ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
        report_progress({"summary": message})
        
        logger.info(f"Тестовое сообщение отправлено: {message}")
        print(f"\n{'=' * 80}\nТЕСТОВОЕ СООБЩЕНИЕ ОТПРАВЛЕНО: {message}\n{'=' * 80}\n")
        
        return True
    except Exception as e:
        logger.error(f"Ошибка при прямом тестировании отчета: {e}")
        return False

def check_web_urls() -> None:
    """
    Проверяет доступность веб-URL для просмотра объектов.
    """
    # Проверяем главную страницу
    try:
        logger.info(f"Проверка доступности главной страницы: {WEB_BASE_URL}")
        response = requests.get(WEB_BASE_URL)
        
        if response.status_code == 200:
            logger.info(f"Главная страница доступна: {WEB_BASE_URL}")
            
            # Проверяем API
            api_health_url = f"{API_BASE_URL}/health"
            logger.info(f"Проверка доступности API: {api_health_url}")
            
            try:
                api_response = requests.get(api_health_url)
                
                if api_response.status_code == 200:
                    logger.info(f"API доступен: {api_health_url}")
                else:
                    logger.error(f"API недоступен: {api_health_url} - Код ответа: {api_response.status_code}")
            except Exception as api_error:
                logger.error(f"Ошибка при проверке API: {api_error}")
        else:
            logger.error(f"Главная страница недоступна: {WEB_BASE_URL} - Код ответа: {response.status_code}")
    except Exception as e:
        logger.error(f"Ошибка при проверке веб-URL: {e}")

def test_all() -> None:
    """
    Тестирует все функции для проверки вывода в чат.
    """
    logger.info("Начало тестирования функций вывода в чат")
    
    # Проверяем веб-URL
    check_web_urls()
    
    # Тестируем прямой вывод сообщений
    if test_direct_report():
        logger.info("Прямой вывод сообщений в чат успешно протестирован")
    else:
        logger.warning("Прямой вывод сообщений в чат не работает")
    
    # Создаем задачу
    task_result = create_task()
    if task_result.get("success", False):
        logger.info("Задача успешно создана и выведена в чат")
    else:
        logger.warning(f"Проблема при создании задачи: {task_result.get('error', 'Неизвестная ошибка')}")
    
    # Небольшая пауза между запросами
    time.sleep(1)
    
    # Создаем инцидент
    incident_result = create_incident()
    if incident_result.get("success", False):
        logger.info("Инцидент успешно создан и выведен в чат")
    else:
        logger.warning(f"Проблема при создании инцидента: {incident_result.get('error', 'Неизвестная ошибка')}")
    
    # Небольшая пауза между запросами
    time.sleep(1)
    
    # Создаем гипотезу
    hypothesis_result = create_hypothesis()
    if hypothesis_result.get("success", False):
        logger.info("Гипотеза успешно создана и выведена в чат")
    else:
        logger.warning(f"Проблема при создании гипотезы: {hypothesis_result.get('error', 'Неизвестная ошибка')}")
    
    logger.info("Завершено тестирование функций вывода в чат")

def main():
    """
    Основная функция для проверки вывода сообщений в чат.
    """
    print(f"\n{'=' * 80}")
    print(f"ПРОВЕРКА ВЫВОДА СООБЩЕНИЙ В ЧАТ")
    print(f"{'=' * 80}\n")
    
    # Тестируем все функции
    test_all()
    
    print(f"\n{'=' * 80}")
    print(f"ЗАВЕРШЕНИЕ ПРОВЕРКИ ВЫВОДА СООБЩЕНИЙ В ЧАТ")
    print(f"{'=' * 80}\n")

if __name__ == "__main__":
    main()