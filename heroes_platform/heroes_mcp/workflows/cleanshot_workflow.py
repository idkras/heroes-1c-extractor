"""
JTBD: Как CleanShot workflow, я хочу читать изображения из CleanShot по URL,
чтобы предоставить guidance для анализа скриншотов лендингов.

AI QA PRE-CHECK:
✅ Анализ реальных данных: Изучил структуру функции read_cleanshot из mcp_server.py
✅ Предотвращение галлюцинаций: Использую только проверенные форматы и логику
✅ Валидация сценария: Сценарий основан на реальной функциональности
❌ Запрещено: Предполагать структуру данных без анализа
"""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class CleanShotWorkflow:
    """
    JTBD: Как CleanShot workflow, я хочу управлять чтением изображений из CleanShot,
    чтобы обеспечить анализ скриншотов лендингов с guidance.
    """

    def read_cleanshot(self, url: str, task_name: str = "feedback") -> str:
        """
        JTBD: Как CleanShot reader, я хочу читать изображение из CleanShot по URL,
        чтобы предоставить структурированный анализ с guidance для UI/UX аналитика.

        Args:
            url: URL CleanShot ссылки
            task_name: Название задачи для именования файла

        Returns:
            str: JSON строка с результатами анализа изображения и guidance
        """
        try:
            self._validate_url(url)
            response = self._fetch_html_page(url)
            image_url = self._extract_og_image(response)
            img_response, temp_path = self._download_and_save_image(
                image_url, task_name
            )
            result = self._create_analysis_result(image_url, temp_path, img_response)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return self._handle_error(e, url)

    def _validate_url(self, url: str) -> None:
        """
        JTBD: Как валидатор, я хочу проверить корректность URL,
        чтобы предотвратить ошибки обработки.

        Args:
            url: URL для валидации

        Raises:
            ValueError: Если URL пустой
        """
        if not url:
            raise ValueError("URL is required")

    def _fetch_html_page(self, url: str):
        """
        JTBD: Как HTTP клиент, я хочу получить HTML страницу,
        чтобы извлечь метаданные изображения.

        Args:
            url: URL страницы

        Returns:
            requests.Response: HTTP ответ с HTML
        """
        import requests

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response

    def _extract_og_image(self, response) -> str:
        """
        JTBD: Как парсер HTML, я хочу извлечь og:image URL,
        чтобы получить ссылку на изображение.

        Args:
            response: HTTP ответ с HTML

        Returns:
            str: URL изображения

        Raises:
            ValueError: Если og:image не найден
        """
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(response.text, "html.parser")
        og_image = soup.find("meta", property="og:image")

        if not og_image:
            raise ValueError("og:image не найден в HTML")

        return og_image.get("content")  # type: ignore

    def _download_and_save_image(self, image_url: str, task_name: str = "feedback"):
        """
        JTBD: Как загрузчик изображений, я хочу скачать и сохранить изображение,
        чтобы обеспечить локальный доступ к файлу с структурированным именованием.

        Args:
            image_url: URL изображения
            task_name: Название задачи для именования файла

        Returns:
            tuple: (HTTP ответ, путь к файлу)
        """
        import os
        from datetime import datetime

        import requests

        img_response = requests.get(image_url, timeout=30)
        img_response.raise_for_status()

        # Создаем структурированное имя файла
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{task_name}_{timestamp}.jpg"

        # Создаем папку по дате
        date_folder = datetime.now().strftime("%Y-%m-%d")
        screenshots_dir = os.path.join(
            os.getcwd(), "screenshots", "feedback", date_folder
        )
        os.makedirs(screenshots_dir, exist_ok=True)

        # Сохраняем файл в структурированную папку
        temp_path = os.path.join(screenshots_dir, filename)
        with open(temp_path, "wb") as f:
            f.write(img_response.content)

        return img_response, temp_path

    def _handle_error(self, error: Exception, url: str) -> str:
        """
        JTBD: Как обработчик ошибок, я хочу обработать исключения,
        чтобы предоставить понятную информацию об ошибке.

        Args:
            error: Исключение
            url: URL, который вызвал ошибку

        Returns:
            str: JSON строка с информацией об ошибке
        """
        logger.error(f"Error in read_cleanshot: {error}")
        return json.dumps(
            {"success": False, "error": str(error), "url": url}, ensure_ascii=False
        )

    def _create_analysis_result(
        self, image_url: str, temp_path: str, img_response
    ) -> dict[str, Any]:
        """
        JTBD: Как результат анализа, я хочу создать структурированный ответ,
        чтобы предоставить полную информацию для анализа изображения.

        Args:
            image_url: URL изображения
            temp_path: Путь к временному файлу
            img_response: HTTP ответ с изображением

        Returns:
            Dict[str, Any]: Структурированный результат анализа
        """
        # Создание JTBD сценария (≤5 строк)
        jtbd_scenario = {
            "when": "Разработчик получает скриншот лендинга для анализа",
            "role": "UI/UX аналитик",
            "wants": "быстро выявить визуальные и функциональные проблемы",
            "so_that": "исправить их и улучшить пользовательский опыт",
            "sees": "структурированный анализ с конкретными проблемами и решениями",
            "injection_point": "момент получения скриншота - сразу начать анализ по чеклисту",
        }

        # Создание тест-кейсов (≤5 строк)
        test_cases = self._create_test_cases()

        # Создание чеклиста дефектов (≤5 строк)
        defect_checklist = self._create_defect_checklist()

        # Создание критериев качества (≤5 строк)
        quality_criteria = self._create_quality_criteria()

        # Создание AI QA задач (≤5 строк)
        ai_qa_tasks = self._create_ai_qa_tasks()

        return {
            "success": True,
            "image_url": image_url,
            "temp_path": temp_path,
            "file_size": len(img_response.content),
            "content_type": img_response.headers.get("content-type"),
            "analysis": "Изображение успешно получено и сохранено",
            "jtbd_scenario": jtbd_scenario,
            "test_cases": test_cases,
            "defect_checklist": defect_checklist,
            "quality_criteria": quality_criteria,
            "ai_qa_tasks": ai_qa_tasks,
        }

    def _create_test_cases(self) -> dict[str, Any]:
        """
        JTBD: Как тестировщик, я хочу создать тест-кейсы для анализа,
        чтобы обеспечить систематическую проверку качества.

        Returns:
            Dict[str, Any]: Структурированные тест-кейсы
        """
        return {
            "visual_quality": [
                {
                    "id": "test_1",
                    "name": "Отсутствие градиентов",
                    "input": "Проверить все секции на градиенты",
                    "expected": "0 градиентов на details/summary секциях",
                    "actual": "[заполнить после анализа]",
                    "status": "pending",
                },
                {
                    "id": "test_2",
                    "name": "Правильные отступы",
                    "input": "Проверить отступы слева и справа",
                    "expected": "Контент занимает ≥90% ширины экрана",
                    "actual": "[заполнить после анализа]",
                    "status": "pending",
                },
                {
                    "id": "test_3",
                    "name": "Читаемость кода",
                    "input": "Проверить шрифт и размер кода",
                    "expected": "Моноширинный шрифт 14-16px, легко читается",
                    "actual": "[заполнить после анализа]",
                    "status": "pending",
                },
            ],
            "functional_quality": [
                {
                    "id": "test_4",
                    "name": "Навигация",
                    "input": "Попытаться найти конкретную информацию",
                    "expected": "Найти нужную секцию за ≤30 секунд",
                    "actual": "[заполнить после анализа]",
                    "status": "pending",
                },
                {
                    "id": "test_5",
                    "name": "Копирование кода",
                    "input": "Попытаться скопировать код блок",
                    "expected": "Код копируется без проблем",
                    "actual": "[заполнить после анализа]",
                    "status": "pending",
                },
            ],
        }

    def _create_defect_checklist(self) -> dict[str, Any]:
        """
        JTBD: Как QA инженер, я хочу создать чеклист дефектов,
        чтобы систематически выявлять проблемы качества.

        Returns:
            Dict[str, Any]: Структурированный чеклист дефектов
        """
        return {
            "critical_defects": [
                "Градиенты на секциях (критично - отвлекает внимание)",
                "Неправильные отступы (критично - плохое использование пространства)",
                "Нечитаемый код (критично - основная цель документации)",
                "Медленная загрузка >3 секунд (критично - плохой UX)",
            ],
            "major_defects": [
                "Плохая контрастность текста",
                "Не работает навигация",
                "Код не копируется",
                "Ссылки не работают",
            ],
            "minor_defects": [
                "Неоптимальные шрифты",
                "Мелкие проблемы с layout",
                "Незначительные проблемы с accessibility",
            ],
        }

    def _create_quality_criteria(self) -> dict[str, str]:
        """
        JTBD: Как QA менеджер, я хочу создать критерии качества,
        чтобы обеспечить объективную оценку результатов.

        Returns:
            Dict[str, str]: Критерии качества
        """
        return {
            "visual_hierarchy": "Пользователь сразу понимает структуру страницы",
            "code_readability": "Разработчик может легко прочитать и скопировать код",
            "navigation_efficiency": "Найти нужную информацию за ≤30 секунд",
            "visual_cleanliness": "Нет отвлекающих элементов (градиенты, лишние отступы)",
            "information_absorption": "Информация усваивается быстро и без усилий",
        }

    def _create_ai_qa_tasks(self) -> list:
        """
        JTBD: Как AI QA система, я хочу создать список задач для анализа,
        чтобы обеспечить систематический подход к проверке качества.

        Returns:
            list: Список AI QA задач
        """
        return [
            "1. АНАЛИЗ ИЗОБРАЖЕНИЯ: Открой скриншот и проанализируй визуальные элементы",
            "2. ПРОВЕРЬ ГРАДИЕНТЫ: Найди все секции с градиентами на details/summary",
            "3. ПРОВЕРЬ ОТСТУПЫ: Измерь ширину контента, проверь использование пространства",
            "4. ПРОВЕРЬ КОД: Оцени читаемость кода, размер шрифта, контрастность",
            "5. ЗАПОЛНИ TEST CASES: Внеси реальные результаты в actual поля",
            "6. ВЫЯВИ ДЕФЕКТЫ: Проверь defect_checklist и найди конкретные проблемы",
            "7. ОЦЕНИ КАЧЕСТВО: Поставь оценки по quality_criteria",
            "8. ПРЕДЛОЖИ РЕШЕНИЯ: Для каждой найденной проблемы предложи конкретное исправление",
        ]
