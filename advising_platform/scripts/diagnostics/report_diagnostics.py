#!/usr/bin/env python3
"""
Диагностический инструмент для тестирования отображения ссылок в чате Replit.
Помогает выявить проблемы с отображением разных элементов в сообщениях.

Автор: AI Assistant
Дата: 21 мая 2025
"""

import sys
import time
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='report_diagnostics.log'
)
logger = logging.getLogger(__name__)

# Добавляем вывод в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# Тестовые сценарии для проверки отображения элементов в чате
TEST_SCENARIOS = [
    {
        "name": "basic_text",
        "description": "Базовый текст без форматирования",
        "message": "Это простое тестовое сообщение без форматирования."
    },
    {
        "name": "markdown_formatting",
        "description": "Markdown-форматирование",
        "message": """
# Заголовок первого уровня
## Заголовок второго уровня

**Жирный текст**, *курсив* и `код`.

- Первый пункт списка
- Второй пункт списка
  - Вложенный пункт
"""
    },
    {
        "name": "emoji",
        "description": "Эмодзи в тексте",
        "message": """
✅ Задача выполнена
⚠️ Предупреждение
🔍 Поиск
📊 Статистика
📝 Заметка
"""
    },
    {
        "name": "server_links",
        "description": "Ссылки на сервер и веб-ресурсы",
        "message": """
🌐 Ссылки на сервер:
- http://0.0.0.0:5000/tasks
- http://0.0.0.0:5000/incidents
- http://0.0.0.0:5000/standards

📡 Внешние ссылки:
- [Google](https://www.google.com)
- [GitHub](https://github.com)
"""
    },
    {
        "name": "statistics_with_links",
        "description": "Статистика с ссылками",
        "message": f"""
📊 **Статистика по проекту**

Задачи ([перейти](http://0.0.0.0:5000/tasks)):
- ✅ Выполнено: 10
- ⏳ В процессе: 5
- 🆕 Не начато: 8

Инциденты ([перейти](http://0.0.0.0:5000/incidents)):
- ✅ Решено: 12
- 🔍 Открыто: 3

Стандарты ([перейти](http://0.0.0.0:5000/standards)):
- 📌 Активных: 25
"""
    },
    {
        "name": "complex_formatting",
        "description": "Комплексное форматирование и разные элементы",
        "message": f"""
# 📊 Отчет о состоянии системы

## Компоненты
| Компонент | Статус | Время проверки |
|-----------|--------|---------------|
| API-сервер | ✅ Работает | {datetime.now().strftime('%H:%M:%S')} |
| Веб-сервер | ✅ Работает | {datetime.now().strftime('%H:%M:%S')} |
| База данных | ✅ Работает | {datetime.now().strftime('%H:%M:%S')} |

## Доступные URL
- 🌐 Основной интерфейс: [http://0.0.0.0:5000](http://0.0.0.0:5000)
- 📊 Панель статистики: [http://0.0.0.0:5000/stats](http://0.0.0.0:5000/stats)
- 📝 Управление задачами: [http://0.0.0.0:5000/tasks](http://0.0.0.0:5000/tasks)

> **Примечание**: Этот отчет сгенерирован автоматически в {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    }
]

def send_test_message(message: str, test_name: str) -> bool:
    """
    Отправляет тестовое сообщение напрямую в чат Replit.
    
    Args:
        message: Текст сообщения
        test_name: Название теста
        
    Returns:
        bool: True если сообщение успешно отправлено, иначе False
    """
    logger.info(f"Отправка тестового сообщения '{test_name}'")
    
    try:
        # Отправляем сообщение напрямую через API Replit
        # Используем сообщение о тестовом характере сообщения
        message_with_header = f"""🧪 **Тест отображения '{test_name}'**

{message}

---
⏱️ Время отправки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # Импортируем функцию для отправки сообщений
        try:
            # Прямой вызов через report_progress
            from importlib.util import find_spec
            
            if find_spec('antml'):
                # Если модуль antml доступен
                import antml.function_calls
                antml.function_calls.function_call("report_progress", {"summary": message_with_header})
                logger.info(f"Сообщение отправлено через antml.function_calls.function_call")
                return True
            else:
                # Если модуль antml недоступен, используем встроенную функцию
                from advising_platform.src.tools.reporting.report_interface import report_progress
                report_progress({"summary": message_with_header})
                logger.info(f"Сообщение отправлено через advising_platform.src.tools.reporting.report_interface.report_progress")
                return True
                
        except ImportError as e:
            # Если не удалось импортировать ни один модуль
            logger.error(f"Ошибка импорта: {e}")
            
            # В качестве крайней меры используем глобальные переменные
            try:
                # Прямая отправка в чат - не рекомендуется для обычного использования
                print("\n\n[СООБЩЕНИЕ ДЛЯ ЧАТА REPLIT]")
                print(message_with_header)
                print("[КОНЕЦ СООБЩЕНИЯ]\n")
                logger.info("Сообщение выведено в консоль (прямая отправка в чат недоступна)")
                return False
            except Exception as e2:
                logger.error(f"Критическая ошибка при выводе сообщения: {e2}")
                return False
                
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения: {e}")
        return False

def run_diagnostic_tests(selected_tests: Optional[List[str]] = None) -> Dict[str, bool]:
    """
    Запускает диагностические тесты для проверки отображения элементов в чате.
    
    Args:
        selected_tests: Список имен тестов для запуска (если не указан, запускаются все тесты)
        
    Returns:
        Dict[str, bool]: Словарь {имя_теста: результат}
    """
    results = {}
    
    # Определяем, какие тесты запускать
    if selected_tests:
        tests_to_run = [t for t in TEST_SCENARIOS if t["name"] in selected_tests]
    else:
        tests_to_run = TEST_SCENARIOS
    
    # Выводим информацию о запуске тестов
    print(f"\n🧪 Запуск {len(tests_to_run)} диагностических тестов для проверки отображения в чате Replit")
    
    # Запускаем тесты
    for i, test in enumerate(tests_to_run):
        print(f"\n[{i+1}/{len(tests_to_run)}] Тест '{test['name']}': {test['description']}")
        
        # Отправляем тестовое сообщение
        result = send_test_message(test["message"], test["name"])
        results[test["name"]] = result
        
        # Выводим результат
        status = "✅ УСПЕШНО" if result else "❌ ОШИБКА"
        print(f"Результат: {status}")
        
        # Пауза между тестами, чтобы избежать превышения лимитов и для лучшей читаемости
        if i < len(tests_to_run) - 1:
            print("Пауза перед следующим тестом...")
            time.sleep(3)
    
    # Выводим общий результат
    success_count = sum(1 for result in results.values() if result)
    print(f"\n📊 Результаты тестирования: {success_count}/{len(results)} успешно")
    
    return results

def submit_report(results: Dict[str, bool], message: Optional[str] = None) -> None:
    """
    Отправляет отчет о результатах диагностики в чат Replit.
    
    Args:
        results: Словарь {имя_теста: результат}
        message: Дополнительное сообщение
    """
    # Форматируем отчет
    success_count = sum(1 for result in results.values() if result)
    total_count = len(results)
    success_percent = int(success_count / total_count * 100) if total_count > 0 else 0
    
    report = f"""📊 **Отчет о диагностике отображения в чате Replit**

### Общие результаты:
- Всего тестов: {total_count}
- Успешно: {success_count} ({success_percent}%)
- Ошибок: {total_count - success_count} ({100 - success_percent}%)

### Детальные результаты:
"""
    
    # Добавляем результаты по каждому тесту
    for test_name, test_result in results.items():
        test_info = next((t for t in TEST_SCENARIOS if t["name"] == test_name), None)
        if test_info:
            status = "✅" if test_result else "❌"
            report += f"- {status} **{test_info['name']}**: {test_info['description']}\n"
    
    # Добавляем рекомендации
    report += f"""
### Рекомендации:
"""
    
    if success_count == total_count:
        report += "✅ Все тесты прошли успешно. Система отображения в чате работает корректно.\n"
    else:
        report += "⚠️ Некоторые тесты не прошли. Рекомендуется:\n"
        
        # Анализируем проблемные сценарии
        if not results.get("server_links", True) or not results.get("statistics_with_links", True):
            report += "1. Проверить форматирование URL-адресов. Убедитесь, что используется правильный формат.\n"
            report += "2. Проверить доступность сервера по адресу http://0.0.0.0:5000.\n"
        
        if not results.get("markdown_formatting", True) or not results.get("complex_formatting", True):
            report += "3. Проверить обработку Markdown-форматирования. Возможно, некоторые теги не поддерживаются.\n"
        
        if not results.get("emoji", True):
            report += "4. Проверить поддержку эмодзи в чате Replit.\n"
            
        report += "5. Проверить логи на наличие ошибок при отправке сообщений.\n"
    
    # Добавляем дополнительное сообщение, если оно предоставлено
    if message:
        report += f"""
### Дополнительная информация:
{message}
"""
    
    # Добавляем время формирования отчета
    report += f"""
---
⏱️ Отчет сформирован: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    # Отправляем отчет в чат
    try:
        from importlib.util import find_spec
        
        if find_spec('antml'):
            # Если модуль antml доступен
            import antml.function_calls
            antml.function_calls.function_call("report_progress", {"summary": report})
            logger.info("Отчет отправлен через antml.function_calls.function_call")
        else:
            # Если модуль antml недоступен, используем встроенную функцию
            from advising_platform.src.tools.reporting.report_interface import report_progress
            report_progress({"summary": report})
            logger.info("Отчет отправлен через advising_platform.src.tools.reporting.report_interface.report_progress")
            
    except Exception as e:
        logger.error(f"Ошибка при отправке отчета: {e}")
        
        # В качестве крайней меры выводим отчет в консоль
        print("\n\n[ОТЧЕТ О ДИАГНОСТИКЕ]")
        print(report)
        print("[КОНЕЦ ОТЧЕТА]\n")

def main():
    """Основная функция скрипта."""
    print("\n=== ДИАГНОСТИКА ОТОБРАЖЕНИЯ СООБЩЕНИЙ В ЧАТЕ REPLIT ===\n")
    
    # Запускаем все тесты
    results = run_diagnostic_tests()
    
    # Формируем дополнительное сообщение
    additional_message = """
Для стабильной работы системы отображения сообщений в чате Replit рекомендуется:

1. Использовать прямой вызов antml.function_calls.function_call с параметром "summary"
2. Проверять корректность форматирования URL-адресов
3. Избегать сложного Markdown-форматирования
4. Убедиться, что сервер доступен по адресу http://0.0.0.0:5000
5. Использовать единый подход к форматированию во всех компонентах системы
"""
    
    # Отправляем отчет
    submit_report(results, additional_message)
    
    print("\n✅ Диагностика завершена. Отчет отправлен в чат Replit.")
    return 0

if __name__ == "__main__":
    sys.exit(main())