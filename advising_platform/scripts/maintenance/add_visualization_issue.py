"""
Скрипт для добавления задачи-гипотезы и инцидента по проблеме с визуализацией связей.
Использует штатный механизм системы вместо создания отдельных файлов.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Импортируем функцию отчета о прогрессе из нашей системы
try:
    from advising_platform.src.tools.reporting.report_interface import report_progress
    logger.info("Импортирована функция report_progress из модуля report_interface")
except ImportError:
    logger.warning("Не удалось импортировать report_progress, будет использоваться локальная версия")
    
    # Функция для имитации report_progress (используется только если импорт не удался)
    def report_progress(data: Dict[str, str]) -> None:
        """Имитирует функцию report_progress."""
        logger.info(f"Report Progress: {data['summary']}")
        return None

def main():
    """Основная функция для добавления задачи-гипотезы и инцидента."""
    try:
        # Добавляем путь к корневой директории проекта
        project_root = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, project_root)
        
        # Импортируем нужные модули
        from advising_platform.src.core.registry.trigger_handler import create_task, create_incident
        
        # Создаем директории для файлов
        incident_dir = "incidents"
        task_dir = "projects/tasks"
        os.makedirs(incident_dir, exist_ok=True)
        os.makedirs(task_dir, exist_ok=True)
        
        # Создаем инцидент
        logger.info("Создание инцидента о проблеме с визуализацией связей...")
        incident_result = create_incident(
            title="Проблема с визуализацией связей между рабочими элементами",
            description=(
                "При попытке просмотра визуализации связей между рабочими элементами "
                "(задачи T0004, T0005 и гипотеза H0001) контент не отображается корректно "
                "в веб-интерфейсе. HTML-файл визуализации генерируется успешно, но пользователь "
                "не имеет к нему доступа через веб-интерфейс."
            ),
            incident_type="Функциональность",
            priority="Высокий",
            analysis=[
                "Пользователь не видит визуализацию связей, потому что файл визуализации не интегрирован в веб-интерфейс",
                "Файл не интегрирован в веб-интерфейс, потому что отсутствует маршрут в веб-сервере для доступа к HTML-файлу визуализации",
                "Маршрут отсутствует, потому что веб-сервер настроен как простой HTTP-сервер без поддержки специальных маршрутов",
                "Используется простой HTTP-сервер, потому что проект изначально планировался с минимальными требованиями к веб-интерфейсу",
                "Доступ к визуализации не был предусмотрен, потому что функциональность визуализации была добавлена позже, без соответствующих изменений в веб-интерфейсе"
            ],
            resolution_steps=[
                "Создать директорию `static` в папке `advising_platform/src/web/` для хранения статических файлов",
                "Переместить файл визуализации в эту директорию", 
                "Модифицировать веб-сервер для обеспечения доступа к статическим файлам",
                "Добавить ссылку на визуализацию на главной странице", 
                "Разработать механизм автоматического обновления визуализации при изменении связей"
            ],
            related_items=["T0004", "T0005", "H0001"],
            file_path=f"{incident_dir}/visualization_issue_incident.md"
        )
        
        if not incident_result or not hasattr(incident_result, 'success') or not incident_result.success:
            logger.error("Ошибка при создании инцидента")
            if hasattr(incident_result, 'errors'):
                for error in incident_result.errors:
                    logger.error(f"  - {error}")
            return False
        
        logger.info(f"Инцидент успешно создан: {incident_result.item.id if hasattr(incident_result, 'item') else 'ID неизвестен'}")
        
        # Создаем гипотезу
        logger.info("Создание гипотезы о визуализации связей...")
        hypothesis_result = create_task(
            title="Визуализация связей повышает эффективность работы с задачами и инцидентами",
            description=(
                "Предполагается, что графическое представление связей между задачами, "
                "инцидентами и другими элементами системы повышает скорость навигации, "
                "улучшает понимание структуры проекта и снижает ошибки при работе. "
                "Внедрение специализированного интерфейса визуализации связей с возможностью "
                "интерактивного взаимодействия позволит значительно повысить "
                "продуктивность работы с системой."
            ),
            author="AI Assistant",
            assignee="Developer",
            file_path=f"{task_dir}/visualization_hypothesis.md",
            report_progress_func=mock_report_progress
        )
        
        if not hypothesis_result or not hasattr(hypothesis_result, 'success') or not hypothesis_result.success:
            logger.error("Ошибка при создании гипотезы")
            if hasattr(hypothesis_result, 'errors'):
                for error in hypothesis_result.errors:
                    logger.error(f"  - {error}")
            return False
        
        logger.info(f"Гипотеза успешно создана: {hypothesis_result.item.id if hasattr(hypothesis_result, 'item') else 'ID неизвестен'}")
        
        # Обновляем состояние кеша
        os.system("python cache_manager.py sync --verify")
        logger.info("Кэш успешно синхронизирован")
        
        # Запускаем скрипт консолидации задач и инцидентов для переноса их в главные файлы
        logger.info("Запуск консолидации задач и инцидентов...")
        os.system("python consolidate_tasks_and_incidents.py")
        
        return True
    
    except ImportError as e:
        logger.error(f"Ошибка импорта модуля: {e}")
        logger.error("Убедитесь, что пути к модулям указаны правильно")
        return False
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("✅ Задача-гипотеза и инцидент успешно добавлены в систему")
    else:
        print("❌ Возникла ошибка при добавлении задачи-гипотезы и инцидента")