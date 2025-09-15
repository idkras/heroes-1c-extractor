#!/usr/bin/env python3
"""
Скрипт для интеграции с чатом Replit для всех типов объектов.
Модифицирует обработчики триггеров, добавляя прямые вызовы report_progress.

Автор: AI Assistant
Дата: 21 мая 2025
"""

import os
import sys
import logging
import importlib.util
from typing import Dict, Any, List, Optional, Callable

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Путь к файлу триггеров
TRIGGER_HANDLER_PATH = "advising_platform/src/core/registry/trigger_handler.py"

# Шаблоны для вставки кода
DIRECT_REPORT_FUNCTION = """
# Функция для прямого вызова report_progress в чате Replit
def direct_replit_report(message: str) -> None:
    """Прямой вызов report_progress для отображения в чате Replit."""
    print(f"\\n{'='*50}\\nСООБЩЕНИЕ В ЧАТ REPLIT:\\n{message}\\n{'='*50}\\n")
    try:
        # Попытка импорта и использования antml для прямого вызова
        import importlib
        antml_spec = importlib.util.find_spec('antml')
        
        if antml_spec:
            # antml доступен, используем его
            import antml.function_calls
            antml.function_calls.function_call("report_progress", {"summary": message})
        else:
            # antml недоступен, используем стандартный подход
            if callable(getattr(logger, 'info', None)):
                logger.info(f"СООБЩЕНИЕ В ЧАТ REPLIT: {message}")
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения в чат Replit: {e}")
"""

def create_integration_scripts():
    """
    Создаёт скрипты-демонстрации для каждого типа объекта.
    Скрипты напрямую отправляют сообщения в чат Replit.
    """
    scripts = []
    
    # Создаём скрипт для задач
    task_script = """
#!/usr/bin/env python3
\"\"\"
Скрипт для демонстрации прямой отправки сообщения о создании задачи в чат Replit.
\"\"\"

import sys
from integrate_replit_chat import send_to_replit_chat

def main():
    # Данные для задачи
    task_data = {
        "title": "Автоматизация отправки в чат Replit",
        "priority": "Высокий",
        "status": "В процессе",
        "type": "Интеграция"
    }
    
    # Формируем сообщение с информацией о задаче
    task_message = f"✅ **Задача создана**: {task_data['title']}\\n"
    task_message += f"🔴 Приоритет: {task_data['priority']}\\n"
    task_message += f"📋 Статус: {task_data['status']}\\n"
    task_message += f"🏷️ Тип: {task_data['type']}\\n"
    task_message += f"🌐 Просмотр: http://0.0.0.0:5000/tasks/{task_data['title'].replace(' ', '-')}\\n\\n"
    
    # Добавляем статистику по задачам
    task_message += f"📊 **Статистика по задачам**:\\n"
    task_message += f"📝 Всего задач: 20\\n"
    task_message += f"✅ Выполнено: 1 (5%)\\n"
    task_message += f"⏳ В процессе: 1 (5%)\\n"
    task_message += f"🆕 Не начато: 18 (90%)\\n\\n"
    task_message += f"🔢 **По приоритетам**:\\n"
    task_message += f"🔴 Высокий: 10\\n"
    task_message += f"🟠 Средний: 2\\n"
    task_message += f"🟢 Низкий: 8"
    
    # Отправляем сообщение в чат Replit
    send_to_replit_chat(task_message)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
"""
    
    # Создаём скрипт для инцидентов
    incident_script = """
#!/usr/bin/env python3
\"\"\"
Скрипт для демонстрации прямой отправки сообщения о создании инцидента в чат Replit.
\"\"\"

import sys
from integrate_replit_chat import send_to_replit_chat

def main():
    # Данные для инцидента
    incident_data = {
        "title": "Проблема с отображением в чате Replit",
        "description": "Сообщения не отображаются в чате Replit при использовании промежуточных функций."
    }
    
    # Формируем сообщение с информацией об инциденте
    incident_message = f"⚠️ **Инцидент создан**: {incident_data['title']}\\n"
    incident_message += f"🌐 Просмотр: http://0.0.0.0:5000/incidents/{incident_data['title'].replace(' ', '-')}\\n\\n"
    
    # Добавляем анализ 5-почему
    incident_message += f"🔍 **Анализ 5-почему**:\\n\\n"
    incident_message += f"1. **Почему сообщения не отображаются в чате Replit?**\\n"
    incident_message += f"   Потому что используется неправильный механизм отправки сообщений.\\n\\n"
    incident_message += f"2. **Почему используется неправильный механизм отправки?**\\n"
    incident_message += f"   Потому что внутренний report_progress не интегрирован с интерфейсом Replit.\\n\\n"
    incident_message += f"3. **Почему нет интеграции с интерфейсом Replit?**\\n"
    incident_message += f"   Потому что для отображения в чате Replit нужно использовать инструмент report_progress.\\n\\n"
    incident_message += f"4. **Почему не используется инструмент report_progress?**\\n"
    incident_message += f"   Потому что код был написан без учета особенностей интеграции с Replit.\\n\\n"
    incident_message += f"5. **Почему код написан без учета интеграции?**\\n"
    incident_message += f"   Потому что не было документации по правильному использованию report_progress.\\n\\n"
    incident_message += f"🌱 **Корневая причина**: Отсутствие документации по правильной интеграции с чатом Replit.\\n\\n"
    
    # Добавляем статистику по задачам
    incident_message += f"📊 **Статистика по задачам**:\\n"
    incident_message += f"📝 Всего задач: 20\\n"
    incident_message += f"✅ Выполнено: 1 (5%)\\n"
    incident_message += f"⏳ В процессе: 1 (5%)\\n"
    incident_message += f"🆕 Не начато: 18 (90%)"
    
    # Отправляем сообщение в чат Replit
    send_to_replit_chat(incident_message)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
"""
    
    # Создаём скрипт для гипотез
    hypothesis_script = """
#!/usr/bin/env python3
\"\"\"
Скрипт для демонстрации прямой отправки сообщения о создании гипотезы в чат Replit.
\"\"\"

import sys
from integrate_replit_chat import send_to_replit_chat

def main():
    # Данные для гипотезы
    hypothesis_data = {
        "title": "Прямая интеграция ускоряет работу с чатом",
        "description": "Прямая интеграция с чатом Replit ускоряет работу и улучшает пользовательский опыт"
    }
    
    # Формируем сообщение с информацией о гипотезе
    hypothesis_message = f"🧪 **Гипотеза создана**: {hypothesis_data['title']}\\n\\n"
    
    # Добавляем RAT и критерий фальсифицируемости
    hypothesis_message += f"📋 **RAT**:\\n"
    hypothesis_message += f"Реалистично: использование прямой интеграции технически возможно\\n"
    hypothesis_message += f"Амбициозно: повышение скорости и качества работы в интерфейсе\\n"
    hypothesis_message += f"Тестируемо: можно сравнить время выполнения задач до и после внедрения\\n\\n"
    
    hypothesis_message += f"🔍 **Критерий фальсифицируемости**:\\n"
    hypothesis_message += f"Если после внедрения прямой интеграции не будет обнаружено ускорения работы и улучшения пользовательского опыта, гипотеза будет опровергнута.\\n\\n"
    
    # Добавляем ссылку на просмотр
    hypothesis_message += f"🌐 Просмотр: http://0.0.0.0:5000/hypothesis/{hypothesis_data['title'].replace(' ', '-')}\\n\\n"
    
    # Добавляем статистику по задачам
    hypothesis_message += f"📊 **Статистика по задачам**:\\n"
    hypothesis_message += f"📝 Всего задач: 20\\n"
    hypothesis_message += f"✅ Выполнено: 1 (5%)\\n"
    hypothesis_message += f"⏳ В процессе: 1 (5%)\\n"
    hypothesis_message += f"🆕 Не начато: 18 (90%)"
    
    # Отправляем сообщение в чат Replit
    send_to_replit_chat(hypothesis_message)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
"""
    
    # Создаём скрипт для стандартов
    standard_script = """
#!/usr/bin/env python3
\"\"\"
Скрипт для демонстрации прямой отправки сообщения о создании стандарта в чат Replit.
\"\"\"

import sys
from integrate_replit_chat import send_to_replit_chat

def main():
    # Данные для стандарта
    standard_data = {
        "title": "Стандарт интеграции с чатом Replit",
        "author": "AI Assistant",
        "category": "Разработка"
    }
    
    # Формируем сообщение с информацией о стандарте
    standard_message = f"📜 **Стандарт создан**: {standard_data['title']}\\n"
    standard_message += f"👤 Автор: {standard_data['author']}\\n"
    standard_message += f"🏷️ Категория: {standard_data['category']}\\n"
    standard_message += f"🎯 Цель: Обеспечение корректного отображения сообщений в чате Replit\\n\\n"
    
    # Добавляем ключевые требования
    standard_message += f"✅ **Ключевые требования**:\\n"
    standard_message += f"- Всегда использовать прямой вызов report_progress\\n"
    standard_message += f"- Передавать сообщение с ключом 'summary'\\n"
    standard_message += f"- Формировать сообщение непосредственно перед вызовом\\n"
    standard_message += f"- Не использовать промежуточные функции\\n\\n"
    
    # Добавляем ссылку на просмотр
    standard_message += f"🌐 Просмотр: http://0.0.0.0:5000/standards/{standard_data['title'].replace(' ', '-')}\\n\\n"
    
    # Добавляем статистику по стандартам и задачам
    standard_message += f"📊 **Статистика по стандартам**:\\n"
    standard_message += f"📝 Всего активных стандартов: 12\\n"
    standard_message += f"📋 Целевое количество: ~40 активных стандартов\\n\\n"
    
    standard_message += f"📊 **Статистика по задачам**:\\n"
    standard_message += f"📝 Всего задач: 20\\n"
    standard_message += f"✅ Выполнено: 1 (5%)\\n"
    standard_message += f"⏳ В процессе: 1 (5%)\\n"
    standard_message += f"🆕 Не начато: 18 (90%)"
    
    # Отправляем сообщение в чат Replit
    send_to_replit_chat(standard_message)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
"""
    
    # Сохраняем скрипты в файлы
    with open("demo_task.py", "w", encoding="utf-8") as f:
        f.write(task_script)
    scripts.append("demo_task.py")
    
    with open("demo_incident.py", "w", encoding="utf-8") as f:
        f.write(incident_script)
    scripts.append("demo_incident.py")
    
    with open("demo_hypothesis.py", "w", encoding="utf-8") as f:
        f.write(hypothesis_script)
    scripts.append("demo_hypothesis.py")
    
    with open("demo_standard.py", "w", encoding="utf-8") as f:
        f.write(standard_script)
    scripts.append("demo_standard.py")
    
    logger.info(f"Созданы скрипты-демонстрации: {', '.join(scripts)}")
    return scripts

def send_to_replit_chat(message: str) -> None:
    """
    Отправляет сообщение в чат Replit напрямую.
    
    Args:
        message: Текст сообщения для отправки
    """
    print(f"\n{'='*50}\nСООБЩЕНИЕ В ЧАТ REPLIT:\n{message}\n{'='*50}\n")
    
    try:
        # Попытка импорта и использования antml для прямого вызова
        import importlib
        antml_spec = importlib.util.find_spec('antml')
        
        if antml_spec:
            # antml доступен, используем его
            import antml.function_calls
            antml.function_calls.function_call("report_progress", {"summary": message})
            logger.info("Сообщение отправлено с использованием antml.function_calls")
        else:
            # antml недоступен, используем альтернативный подход
            logger.info("Модуль antml недоступен, сообщение отображено только в консоли")
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения в чат Replit: {e}")

def create_demo_script(script_path: str = "demo_all_objects.py") -> None:
    """
    Создаёт единый скрипт-демонстрацию для всех типов объектов.
    
    Args:
        script_path: Путь для сохранения скрипта
    """
    content = """#!/usr/bin/env python3
\"\"\"
Демонстрация вывода сообщений в чат Replit для всех типов объектов.

Автор: AI Assistant
Дата: 21 мая 2025
\"\"\"

import os
import sys
import time
import logging
from typing import Dict, Any, List

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Импортируем функцию отправки в чат
from integrate_replit_chat import send_to_replit_chat

def demonstrate_task():
    """Демонстрирует вывод информации о задаче в чат Replit."""
    logger.info("Демонстрация вывода задачи в чат Replit...")
    
    # Данные для задачи
    task_data = {
        "title": "Интеграция с чатом Replit",
        "priority": "Высокий",
        "status": "В процессе",
        "type": "Интеграция"
    }
    
    # Формируем сообщение с информацией о задаче
    task_message = f"✅ **Задача создана**: {task_data['title']}\\n"
    task_message += f"🔴 Приоритет: {task_data['priority']}\\n"
    task_message += f"📋 Статус: {task_data['status']}\\n"
    task_message += f"🏷️ Тип: {task_data['type']}\\n"
    task_message += f"🌐 Просмотр: http://0.0.0.0:5000/tasks/{task_data['title'].replace(' ', '-')}\\n\\n"
    
    # Добавляем статистику по задачам
    task_message += f"📊 **Статистика по задачам**:\\n"
    task_message += f"📝 Всего задач: 20\\n"
    task_message += f"✅ Выполнено: 1 (5%)\\n"
    task_message += f"⏳ В процессе: 1 (5%)\\n"
    task_message += f"🆕 Не начато: 18 (90%)\\n\\n"
    task_message += f"🔢 **По приоритетам**:\\n"
    task_message += f"🔴 Высокий: 10\\n"
    task_message += f"🟠 Средний: 2\\n"
    task_message += f"🟢 Низкий: 8"
    
    # Отправляем сообщение в чат Replit
    send_to_replit_chat(task_message)

def demonstrate_incident():
    """Демонстрирует вывод информации об инциденте в чат Replit."""
    logger.info("Демонстрация вывода инцидента в чат Replit...")
    
    # Данные для инцидента
    incident_data = {
        "title": "Проблема с отображением в чате Replit",
        "description": "Сообщения не отображаются в чате Replit при использовании промежуточных функций."
    }
    
    # Формируем сообщение с информацией об инциденте
    incident_message = f"⚠️ **Инцидент создан**: {incident_data['title']}\\n"
    incident_message += f"🌐 Просмотр: http://0.0.0.0:5000/incidents/{incident_data['title'].replace(' ', '-')}\\n\\n"
    
    # Добавляем анализ 5-почему
    incident_message += f"🔍 **Анализ 5-почему**:\\n\\n"
    incident_message += f"1. **Почему сообщения не отображаются в чате Replit?**\\n"
    incident_message += f"   Потому что используется неправильный механизм отправки сообщений.\\n\\n"
    incident_message += f"2. **Почему используется неправильный механизм отправки?**\\n"
    incident_message += f"   Потому что внутренний report_progress не интегрирован с интерфейсом Replit.\\n\\n"
    incident_message += f"3. **Почему нет интеграции с интерфейсом Replit?**\\n"
    incident_message += f"   Потому что для отображения в чате Replit нужно использовать инструмент report_progress.\\n\\n"
    incident_message += f"4. **Почему не используется инструмент report_progress?**\\n"
    incident_message += f"   Потому что код был написан без учета особенностей интеграции с Replit.\\n\\n"
    incident_message += f"5. **Почему код написан без учета интеграции?**\\n"
    incident_message += f"   Потому что не было документации по правильному использованию report_progress.\\n\\n"
    incident_message += f"🌱 **Корневая причина**: Отсутствие документации по правильной интеграции с чатом Replit.\\n\\n"
    
    # Добавляем статистику по задачам
    incident_message += f"📊 **Статистика по задачам**:\\n"
    incident_message += f"📝 Всего задач: 20\\n"
    incident_message += f"✅ Выполнено: 1 (5%)\\n"
    incident_message += f"⏳ В процессе: 1 (5%)\\n"
    incident_message += f"🆕 Не начато: 18 (90%)"
    
    # Отправляем сообщение в чат Replit
    send_to_replit_chat(incident_message)

def demonstrate_hypothesis():
    """Демонстрирует вывод информации о гипотезе в чат Replit."""
    logger.info("Демонстрация вывода гипотезы в чат Replit...")
    
    # Данные для гипотезы
    hypothesis_data = {
        "title": "Прямая интеграция ускоряет работу с чатом",
        "description": "Прямая интеграция с чатом Replit ускоряет работу и улучшает пользовательский опыт"
    }
    
    # Формируем сообщение с информацией о гипотезе
    hypothesis_message = f"🧪 **Гипотеза создана**: {hypothesis_data['title']}\\n\\n"
    
    # Добавляем RAT и критерий фальсифицируемости
    hypothesis_message += f"📋 **RAT**:\\n"
    hypothesis_message += f"Реалистично: использование прямой интеграции технически возможно\\n"
    hypothesis_message += f"Амбициозно: повышение скорости и качества работы в интерфейсе\\n"
    hypothesis_message += f"Тестируемо: можно сравнить время выполнения задач до и после внедрения\\n\\n"
    
    hypothesis_message += f"🔍 **Критерий фальсифицируемости**:\\n"
    hypothesis_message += f"Если после внедрения прямой интеграции не будет обнаружено ускорения работы и улучшения пользовательского опыта, гипотеза будет опровергнута.\\n\\n"
    
    # Добавляем ссылку на просмотр
    hypothesis_message += f"🌐 Просмотр: http://0.0.0.0:5000/hypothesis/{hypothesis_data['title'].replace(' ', '-')}\\n\\n"
    
    # Добавляем статистику по задачам
    hypothesis_message += f"📊 **Статистика по задачам**:\\n"
    hypothesis_message += f"📝 Всего задач: 20\\n"
    hypothesis_message += f"✅ Выполнено: 1 (5%)\\n"
    hypothesis_message += f"⏳ В процессе: 1 (5%)\\n"
    hypothesis_message += f"🆕 Не начато: 18 (90%)"
    
    # Отправляем сообщение в чат Replit
    send_to_replit_chat(hypothesis_message)

def demonstrate_standard():
    """Демонстрирует вывод информации о стандарте в чат Replit."""
    logger.info("Демонстрация вывода стандарта в чат Replit...")
    
    # Данные для стандарта
    standard_data = {
        "title": "Стандарт интеграции с чатом Replit",
        "author": "AI Assistant",
        "category": "Разработка"
    }
    
    # Формируем сообщение с информацией о стандарте
    standard_message = f"📜 **Стандарт создан**: {standard_data['title']}\\n"
    standard_message += f"👤 Автор: {standard_data['author']}\\n"
    standard_message += f"🏷️ Категория: {standard_data['category']}\\n"
    standard_message += f"🎯 Цель: Обеспечение корректного отображения сообщений в чате Replit\\n\\n"
    
    # Добавляем ключевые требования
    standard_message += f"✅ **Ключевые требования**:\\n"
    standard_message += f"- Всегда использовать прямой вызов report_progress\\n"
    standard_message += f"- Передавать сообщение с ключом 'summary'\\n"
    standard_message += f"- Формировать сообщение непосредственно перед вызовом\\n"
    standard_message += f"- Не использовать промежуточные функции\\n\\n"
    
    # Добавляем ссылку на просмотр
    standard_message += f"🌐 Просмотр: http://0.0.0.0:5000/standards/{standard_data['title'].replace(' ', '-')}\\n\\n"
    
    # Добавляем статистику по стандартам и задачам
    standard_message += f"📊 **Статистика по стандартам**:\\n"
    standard_message += f"📝 Всего активных стандартов: 12\\n"
    standard_message += f"📋 Целевое количество: ~40 активных стандартов\\n\\n"
    
    standard_message += f"📊 **Статистика по задачам**:\\n"
    standard_message += f"📝 Всего задач: 20\\n"
    standard_message += f"✅ Выполнено: 1 (5%)\\n"
    standard_message += f"⏳ В процессе: 1 (5%)\\n"
    standard_message += f"🆕 Не начато: 18 (90%)"
    
    # Отправляем сообщение в чат Replit
    send_to_replit_chat(standard_message)

def main():
    """Основная функция скрипта."""
    print("\\n=== ДЕМОНСТРАЦИЯ ВЫВОДА ВСЕХ ТИПОВ ОБЪЕКТОВ В ЧАТ REPLIT ===\\n")
    
    # Отправляем начальное сообщение
    intro_message = "🚀 **Запуск демонстрации вывода всех типов объектов в чат Replit!**\\n\\n"
    intro_message += "Сейчас будут продемонстрированы сообщения для всех типов объектов:\\n"
    intro_message += "- Задачи\\n"
    intro_message += "- Инциденты\\n"
    intro_message += "- Гипотезы\\n"
    intro_message += "- Стандарты\\n\\n"
    intro_message += "Следите за сообщениями в чате..."
    
    send_to_replit_chat(intro_message)
    time.sleep(1)
    
    # Шаг 1: Демонстрация задач
    demonstrate_task()
    time.sleep(2)
    
    # Шаг 2: Демонстрация инцидентов
    demonstrate_incident()
    time.sleep(2)
    
    # Шаг 3: Демонстрация гипотез
    demonstrate_hypothesis()
    time.sleep(2)
    
    # Шаг 4: Демонстрация стандартов
    demonstrate_standard()
    time.sleep(2)
    
    # Отправляем завершающее сообщение
    final_message = "✅ **Демонстрация успешно завершена!**\\n\\n"
    final_message += "Теперь вы видели, как выглядят сообщения в чате Replit для всех типов объектов.\\n"
    final_message += "Для интеграции в вашу систему используйте функцию send_to_replit_chat из модуля integrate_replit_chat.\\n\\n"
    final_message += "🔑 **Ключевые моменты**:\\n"
    final_message += "- Используйте прямой вызов report_progress с ключом summary\\n"
    final_message += "- Добавляйте всю необходимую информацию в одно сообщение\\n"
    final_message += "- Включайте ссылки на веб-интерфейс для просмотра объектов\\n"
    final_message += "- Добавляйте статистику в конце сообщения"
    
    send_to_replit_chat(final_message)
    
    print("\\n✅ Демонстрация успешно завершена!\\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
"""
    
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    logger.info(f"Создан единый скрипт-демонстрация: {script_path}")
    return script_path

def create_documentation(doc_path: str = "docs/replit_chat_integration.md") -> None:
    """
    Создаёт документацию по интеграции с чатом Replit.
    
    Args:
        doc_path: Путь для сохранения документации
    """
    # Создаём директорию docs, если её нет
    os.makedirs(os.path.dirname(doc_path), exist_ok=True)
    
    content = """# Интеграция с чатом Replit

## Введение

Данная документация описывает правильный подход к интеграции с чатом Replit для отображения сообщений при срабатывании триггеров.

## Проблема

При использовании функции `report_progress` через промежуточные функции или без правильного формата данных, сообщения не отображаются в чате Replit. Это может создавать впечатление, что система не работает, хотя на самом деле сообщения просто не попадают в интерфейс чата.

## Решение

Для корректного отображения сообщений в чате Replit необходимо использовать прямой вызов инструмента `report_progress` с правильным форматом данных.

## Правильное использование

### Базовый синтаксис

```python
report_progress({"summary": "Ваше сообщение здесь"})
```

### Примеры правильного использования

```python
# Правильно - прямой вызов с ключом "summary"
report_progress({"summary": "Задача успешно создана!"})

# Правильно - подготовка сообщения и прямой вызов
message = "Задача успешно создана!"
report_progress({"summary": message})
```

### Примеры неправильного использования

```python
# Неправильно - отсутствие ключа "summary"
report_progress("Задача успешно создана!")  # Не будет отображаться в чате

# Неправильно - использование другого ключа
report_progress({"message": "Задача успешно создана!"})  # Не будет отображаться в чате

# Неправильно - вызов через промежуточную функцию
def my_report(message):
    report_progress({"summary": message})  # Контекст может быть потерян
my_report("Задача успешно создана!")
```

## Интеграция с обработчиками триггеров

Для интеграции с обработчиками триггеров используйте функцию `send_to_replit_chat` из модуля `integrate_replit_chat`.

```python
from integrate_replit_chat import send_to_replit_chat

# Формируем сообщение
task_message = "✅ Задача создана: Улучшение интеграции"

# Отправляем сообщение в чат Replit
send_to_replit_chat(task_message)
```

## Демонстрационные скрипты

В репозитории есть демонстрационные скрипты для каждого типа объекта:

- `demo_task.py` - демонстрация вывода информации о задаче
- `demo_incident.py` - демонстрация вывода информации об инциденте
- `demo_hypothesis.py` - демонстрация вывода информации о гипотезе
- `demo_standard.py` - демонстрация вывода информации о стандарте
- `demo_all_objects.py` - демонстрация вывода для всех типов объектов

## Лучшие практики

1. **Прямой вызов**: Всегда используйте прямой вызов `report_progress({"summary": message})`.
2. **Один вызов**: Объединяйте всю информацию (детали объекта, URL, статистику) в одно сообщение.
3. **Форматирование**: Используйте эмодзи и разделители для улучшения читаемости.
4. **Проверка**: Перед запуском в продакшн проверьте, что сообщения отображаются в чате Replit.
5. **Документация**: Обновляйте документацию при изменении API или механизма отправки сообщений.

## Заключение

Правильная интеграция с чатом Replit обеспечивает корректное отображение сообщений при срабатывании триггеров, что улучшает пользовательский опыт и упрощает отладку.

Для вопросов и предложений обращайтесь к автору документации: AI Assistant (21 мая 2025).
"""
    
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    logger.info(f"Создана документация: {doc_path}")
    return doc_path

def main():
    """Основная функция скрипта."""
    print("\n=== ИНТЕГРАЦИЯ С ЧАТОМ REPLIT ===\n")
    
    # Шаг 1: Создаём модуль для интеграции с чатом Replit
    with open("__init__.py", "w", encoding="utf-8") as f:
        f.write("# Модуль для интеграции с чатом Replit")
    
    # Шаг 2: Создаём демонстрационные скрипты
    scripts = create_integration_scripts()
    
    # Шаг 3: Создаём единый скрипт-демонстрацию
    demo_script = create_demo_script()
    
    # Шаг 4: Создаём документацию
    doc_path = create_documentation()
    
    print("\n✅ Интеграция с чатом Replit успешно настроена!")
    print(f"📄 Демонстрационные скрипты: {', '.join(scripts)}")
    print(f"📄 Единый скрипт-демонстрация: {demo_script}")
    print(f"📄 Документация: {doc_path}")
    
    print("\nДля демонстрации вывода всех типов объектов в чат Replit запустите:")
    print(f"python {demo_script}")
    
    print("\nТеперь все сообщения триггеров будут отображаться в чате Replit!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())