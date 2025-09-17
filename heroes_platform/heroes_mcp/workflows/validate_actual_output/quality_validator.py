#!/usr/bin/env python3
"""
Quality Validator Module
MCP Workflow Standard v2.3 Compliance

JTBD: Когда мне нужно проверить качество страницы и сгенерировать тест-кейсы,
я хочу использовать QualityValidator,
чтобы автоматически анализировать качество и выявлять дефекты.

COMPLIANCE: MCP Workflow Standard v2.3, TDD Documentation Standard v2.5
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class QualityValidator:
    """Quality Validator - MCP Workflow Standard v2.3"""

    def __init__(self):
        self.quality_criteria = {
            "visual_hierarchy": "Пользователь сразу понимает структуру страницы",
            "code_readability": "Разработчик может легко прочитать и скопировать код",
            "navigation_efficiency": "Найти нужную информацию за ≤30 секунд",
            "visual_cleanliness": "Нет отвлекающих элементов (градиенты, лишние отступы)",
            "information_absorption": "Информация усваивается быстро и без усилий",
            "performance_quality": "Страница загружается быстро и работает плавно",
        }

    async def generate_quality_test_cases(
        self, url: str, analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Генерация тест-кейсов качества (≤20 строк)"""
        try:
            test_cases = {
                "visual_hierarchy": self._create_visual_hierarchy_tests(analysis),
                "code_readability": self._create_code_readability_tests(analysis),
                "navigation_efficiency": self._create_navigation_tests(analysis),
                "visual_cleanliness": self._create_cleanliness_tests(analysis),
                "information_absorption": self._create_absorption_tests(analysis),
                "performance_quality": self._create_performance_tests(analysis),
            }

            return {
                "test_cases": test_cases,
                "total_tests": sum(len(tests) for tests in test_cases.values()),
                "quality_criteria": self.quality_criteria,
            }

        except Exception as e:
            logger.error(f"Quality test cases generation failed: {e}")
            return {"error": str(e)}

    async def detect_defects(
        self, analysis: dict[str, Any], test_cases: dict[str, Any]
    ) -> dict[str, Any]:
        """Выявление дефектов (≤20 строк)"""
        try:
            defects = {
                "critical": self._detect_critical_defects(analysis),
                "major": self._detect_major_defects(analysis),
                "minor": self._detect_minor_defects(analysis),
                "suggestions": self._generate_suggestions(analysis),
            }

            return {
                "defects": defects,
                "total_defects": sum(
                    len(defect_list) for defect_list in defects.values()
                ),
                "severity_distribution": {k: len(v) for k, v in defects.items()},
            }

        except Exception as e:
            logger.error(f"Defect detection failed: {e}")
            return {"error": str(e)}

    def _create_visual_hierarchy_tests(self, analysis: dict[str, Any]) -> list[str]:
        """Создание тестов визуальной иерархии (≤20 строк)"""
        tests = [
            "Проверить наличие четкого заголовка страницы",
            "Проверить структуру навигации",
            "Проверить контрастность текста",
            "Проверить размеры шрифтов",
        ]

        if analysis.get("content_checks", {}).get("has_navigation"):
            tests.append("Проверить работу навигационного меню")

        return tests

    def _create_code_readability_tests(self, analysis: dict[str, Any]) -> list[str]:
        """Создание тестов читаемости кода (≤20 строк)"""
        tests = [
            "Проверить подсветку синтаксиса в code blocks",
            "Проверить копирование кода",
            "Проверить отступы в коде",
        ]

        if analysis.get("content_checks", {}).get("has_code_blocks"):
            tests.extend(["Проверить нумерацию строк", "Проверить комментарии в коде"])

        return tests

    def _create_navigation_tests(self, analysis: dict[str, Any]) -> list[str]:
        """Создание тестов навигации (≤20 строк)"""
        return [
            "Проверить скорость загрузки страницы",
            "Проверить работу внутренних ссылок",
            "Проверить breadcrumbs",
            "Проверить поиск по странице",
        ]

    def _create_cleanliness_tests(self, analysis: dict[str, Any]) -> list[str]:
        """Создание тестов чистоты дизайна (≤20 строк)"""
        return [
            "Проверить отсутствие лишних элементов",
            "Проверить цветовую схему",
            "Проверить отступы и выравнивание",
            "Проверить типографику",
        ]

    def _create_absorption_tests(self, analysis: dict[str, Any]) -> list[str]:
        """Создание тестов усвоения информации (≤20 строк)"""
        return [
            "Проверить структуру контента",
            "Проверить наличие примеров",
            "Проверить иллюстрации",
            "Проверить краткость изложения",
        ]

    def _create_performance_tests(self, analysis: dict[str, Any]) -> list[str]:
        """Создание тестов производительности (≤20 строк)"""
        return [
            "Проверить время загрузки",
            "Проверить размер страницы",
            "Проверить количество запросов",
            "Проверить кэширование",
        ]

    def _detect_critical_defects(self, analysis: dict[str, Any]) -> list[str]:
        """Выявление критических дефектов (≤20 строк)"""
        defects = []

        if not analysis.get("content_checks", {}).get("has_main_content"):
            defects.append("Отсутствует основной контент")

        if analysis.get("status_code", 0) != 200:
            defects.append(f"Ошибка HTTP: {analysis.get('status_code')}")

        return defects

    def _detect_major_defects(self, analysis: dict[str, Any]) -> list[str]:
        """Выявление серьезных дефектов (≤20 строк)"""
        defects = []

        if not analysis.get("content_checks", {}).get("has_navigation"):
            defects.append("Отсутствует навигация")

        if analysis.get("content_length", 0) < 1000:
            defects.append("Слишком мало контента")

        return defects

    def _detect_minor_defects(self, analysis: dict[str, Any]) -> list[str]:
        """Выявление мелких дефектов (≤20 строк)"""
        defects = []

        if not analysis.get("content_checks", {}).get("has_images"):
            defects.append("Отсутствуют изображения")

        if not analysis.get("content_checks", {}).get("has_tables"):
            defects.append("Отсутствуют таблицы")

        return defects

    def _generate_suggestions(self, analysis: dict[str, Any]) -> list[str]:
        """Генерация предложений (≤20 строк)"""
        suggestions = [
            "Добавить мета-описание для SEO",
            "Оптимизировать изображения",
            "Добавить интерактивные элементы",
        ]

        if not analysis.get("meta_tags"):
            suggestions.append("Добавить мета-теги")

        return suggestions
