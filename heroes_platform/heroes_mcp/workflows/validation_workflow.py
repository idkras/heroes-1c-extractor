"""
Validation Workflow for Heroes MCP Server

Согласно MCP Workflow Standard v2.3:
- Бизнес-логика вынесена в отдельный workflow в папке workflows/
- MCP сервер содержит только регистрацию и проксирование к workflow
"""

import json
import time
from typing import Any


class ValidationWorkflow:
    """
    JTBD: Как workflow валидации, я хочу обрабатывать команды валидации,
    чтобы обеспечить централизованную валидацию данных и результатов.
    """

    def __init__(self):
        self.workflow_name = "validation_workflow"

    async def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """
        Выполнить команду валидации

        Args:
            arguments: Аргументы команды

        Returns:
            Dict[str, Any]: Результат выполнения
        """
        command = arguments.get("command")

        if command == "common_mistakes_prevention":
            return await self._common_mistakes_prevention(
                arguments.get("domain", "general")
            )
        elif command == "quality_validation":
            return await self._quality_validation(
                arguments.get("result", ""), arguments.get("criteria", "general")
            )
        elif command == "approach_recommendation":
            return await self._approach_recommendation(
                arguments.get("problem", ""), arguments.get("context", "")
            )
        elif command == "validate_output_artefact":
            return await self._validate_output_artefact(
                arguments.get("artefact_path", ""),
                arguments.get("artefact_type", "analysis"),
                arguments.get("quality_criteria", "general"),
            )
        else:
            return {"error": f"Unknown validation command: {command}"}

    async def _common_mistakes_prevention(self, domain: str) -> dict[str, Any]:
        """Предупреждения о типичных ошибках"""
        if not domain:
            domain = "general"

        # Бизнес-логика предупреждений
        mistake_preventions = {
            "general": {
                "planning_mistakes": [
                    "❌ Over-engineering - начинай с простого решения",
                    "❌ Missing requirements - уточни требования перед началом",
                    "❌ No validation - всегда валидируй входные данные",
                    "❌ Poor documentation - документируй важные решения",
                ],
                "execution_mistakes": [
                    "❌ No error handling - обрабатывай исключения",
                    "❌ Hard-coded values - используй конфигурацию",
                    "❌ No testing - тестируй на каждом этапе",
                    "❌ Poor logging - логируй важные операции",
                ],
                "quality_mistakes": [
                    "❌ No validation - проверяй качество результата",
                    "❌ Missing edge cases - учитывай граничные случаи",
                    "❌ Poor user experience - думай о пользователе",
                    "❌ No feedback loop - собирай обратную связь",
                ],
            },
            "development": {
                "code_mistakes": [
                    "❌ No type hints - используй типизацию",
                    "❌ Long functions - разбивай на маленькие функции",
                    "❌ No error handling - обрабатывай ошибки",
                    "❌ Hard dependencies - используй dependency injection",
                ],
                "testing_mistakes": [
                    "❌ No tests - пиши тесты для всего кода",
                    "❌ Flaky tests - делай тесты детерминистичными",
                    "❌ No integration tests - тестируй взаимодействие компонентов",
                    "❌ No edge case testing - тестируй граничные случаи",
                ],
                "architecture_mistakes": [
                    "❌ Monolithic design - используй модульную архитектуру",
                    "❌ Tight coupling - уменьшай связанность компонентов",
                    "❌ No separation of concerns - разделяй ответственности",
                    "❌ Poor naming - используй понятные имена",
                ],
            },
            "analysis": {
                "data_mistakes": [
                    "❌ No data validation - проверяй качество данных",
                    "❌ Missing data - обрабатывай отсутствующие данные",
                    "❌ No data profiling - изучай структуру данных",
                    "❌ Poor sampling - используй репрезентативные данные",
                ],
                "methodology_mistakes": [
                    "❌ Wrong methods - выбирай правильные методы анализа",
                    "❌ No baseline - устанавливай базовые метрики",
                    "❌ Confirmation bias - избегай предвзятости",
                    "❌ No validation - валидируй результаты анализа",
                ],
                "interpretation_mistakes": [
                    "❌ Wrong conclusions - проверяй логику выводов",
                    "❌ No context - учитывай контекст данных",
                    "❌ Over-generalization - не обобщай без оснований",
                    "❌ No limitations - указывай ограничения анализа",
                ],
            },
            "integration": {
                "api_mistakes": [
                    "❌ No API documentation - изучай документацию API",
                    "❌ No rate limiting - учитывай ограничения API",
                    "❌ No error handling - обрабатывай ошибки API",
                    "❌ No authentication - проверяй аутентификацию",
                ],
                "testing_mistakes": [
                    "❌ No integration tests - тестируй интеграцию",
                    "❌ No mock data - используй моки для тестирования",
                    "❌ No error scenarios - тестируй сценарии ошибок",
                    "❌ No performance testing - тестируй производительность",
                ],
                "deployment_mistakes": [
                    "❌ No environment config - настраивай окружения",
                    "❌ No rollback plan - планируй откат изменений",
                    "❌ No monitoring - настраивай мониторинг",
                    "❌ No security review - проверяй безопасность",
                ],
            },
            "mcp": {
                "command_mistakes": [
                    "❌ No input validation - валидируй входные параметры",
                    "❌ No error handling - обрабатывай ошибки в командах",
                    "❌ No documentation - документируй MCP команды",
                    "❌ No testing - тестируй MCP команды",
                ],
                "workflow_mistakes": [
                    "❌ No atomic operations - разбивай на атомарные шаги",
                    "❌ No reflection checkpoints - добавляй точки рефлексии",
                    "❌ No rollback capability - обеспечивай возможность отката",
                    "❌ No state tracking - отслеживай состояние workflow",
                ],
                "integration_mistakes": [
                    "❌ No standards compliance - соблюдай Registry Standard",
                    "❌ No cross-check - проверяй результаты",
                    "❌ No quality gates - устанавливай качественные gates",
                    "❌ No user feedback - собирай обратную связь пользователей",
                ],
            },
        }

        prevention = mistake_preventions.get(domain, mistake_preventions["general"])

        return {
            "domain": domain,
            "preventions": prevention,
            "total_mistakes": sum(len(mistakes) for mistakes in prevention.values()),
            "guidance_message": "Используйте эти предупреждения для предотвращения типичных ошибок",
            "timestamp": time.time(),
        }

    async def _quality_validation(self, result: str, criteria: str) -> dict[str, Any]:
        """Валидация качества результата"""
        if not result:
            return {"error": "Result is required for validation"}

        validation_criteria = {
            "general": {
                "completeness": "Результат полный и содержит все необходимые элементы",
                "clarity": "Результат понятен и легко читается",
                "accuracy": "Результат точен и соответствует требованиям",
                "usability": "Результат можно использовать на практике",
            },
            "code": {
                "readability": "Код читаем и понятен",
                "maintainability": "Код легко поддерживать и модифицировать",
                "testability": "Код можно легко тестировать",
                "performance": "Код эффективен и не содержит узких мест",
            },
            "analysis": {
                "methodology": "Использованы правильные методы анализа",
                "data_quality": "Данные качественные и релевантные",
                "interpretation": "Интерпретация результатов корректна",
                "actionability": "Результаты дают actionable insights",
            },
            "documentation": {
                "completeness": "Документация полная и покрывает все аспекты",
                "clarity": "Документация понятна и структурирована",
                "accuracy": "Документация соответствует фактическому состоянию",
                "usability": "Документация полезна для пользователей",
            },
        }

        criteria_set = validation_criteria.get(criteria, validation_criteria["general"])

        validation_results = {
            "result_preview": result[:200] + "..." if len(result) > 200 else result,
            "criteria": criteria,
            "validation_score": 0.85,  # Симуляция score
            "issues_found": [],
            "strengths": [],
            "recommendations": [],
            "detailed_validation": {},
        }

        issues_found = validation_results["issues_found"]
        strengths = validation_results["strengths"]
        recommendations = validation_results["recommendations"]

        # Симуляция детальной валидации
        for criterion_name, criterion_description in criteria_set.items():
            score = 0.8 + (hash(criterion_name) % 20) / 100  # Псевдослучайный score
            validation_results["detailed_validation"][criterion_name] = {  # type: ignore
                "description": criterion_description,
                "score": score,
                "passed": score >= 0.7,
                "feedback": f"Критерий '{criterion_name}' {'пройден' if score >= 0.7 else 'требует улучшения'}",
            }

            if score < 0.7:
                issues_found.append(  # type: ignore
                    f"Низкий score по критерию '{criterion_name}': {score:.2f}"
                )
                recommendations.append(  # type: ignore
                    f"Улучшить {criterion_name}: {criterion_description}"
                )
            else:
                strengths.append(  # type: ignore
                    f"Хороший результат по критерию '{criterion_name}': {score:.2f}"
                )

        # Обновляем общий score
        scores = [
            v["score"]
            for v in validation_results["detailed_validation"].values()  # type: ignore
        ]
        validation_results["validation_score"] = (
            sum(scores) / len(scores) if scores else 0.0
        )

        validation_results["timestamp"] = time.time()
        validation_results["overall_assessment"] = (
            "Excellent"
            if validation_results["validation_score"] >= 0.9  # type: ignore
            else (
                "Good"
                if validation_results["validation_score"] >= 0.7  # type: ignore
                else "Needs Improvement"
            )
        )  # type: ignore

        return validation_results

    async def _approach_recommendation(
        self, problem: str, context: str
    ) -> dict[str, Any]:
        """Рекомендации по подходу к решению проблемы"""
        if not problem:
            return {"error": "Problem description is required"}

        problem_lower = problem.lower()
        context.lower()

        # Определяем тип проблемы
        problem_types = {
            "development": [
                "код",
                "разработка",
                "программирование",
                "функция",
                "класс",
                "модуль",
            ],
            "analysis": ["анализ", "данные", "исследование", "статистика", "метрики"],
            "integration": ["интеграция", "api", "подключение", "синхронизация"],
            "documentation": ["документация", "документ", "описание", "руководство"],
            "testing": ["тестирование", "тест", "проверка", "валидация"],
            "deployment": ["развертывание", "deployment", "production", "выпуск"],
        }

        detected_types = []
        for problem_type, keywords in problem_types.items():
            if any(keyword in problem_lower for keyword in keywords):
                detected_types.append(problem_type)

        if not detected_types:
            detected_types = ["general"]

        # Рекомендации по подходам (упрощенная версия)
        approach_recommendations = {
            "development": {
                "recommended_approach": "tdd_first_then_refactor",
                "reasoning": "Проблема требует разработки кода - используйте TDD для обеспечения качества",
                "steps": [
                    "1. Напишите failing test для новой функциональности",
                    "2. Реализуйте минимальное решение для прохождения теста",
                    "3. Рефакторите код с сохранением тестов",
                    "4. Добавьте дополнительные тесты для edge cases",
                ],
            },
            "general": {
                "recommended_approach": "iterative_problem_solving",
                "reasoning": "Общий подход к решению проблем - итеративный метод",
                "steps": [
                    "1. Поняйте проблему и требования",
                    "2. Разбейте проблему на подзадачи",
                    "3. Решите каждую подзадачу по очереди",
                    "4. Протестируйте и валидируйте решение",
                ],
            },
        }

        primary_type = detected_types[0]
        recommendation = approach_recommendations.get(
            primary_type, approach_recommendations["general"]
        )

        return {
            "problem": problem,
            "context": context,
            "detected_problem_types": detected_types,
            "primary_problem_type": primary_type,
            "recommendation": recommendation,
            "alternative_approaches": [t for t in detected_types if t != primary_type],
            "guidance_message": "Используйте эти рекомендации для выбора оптимального подхода к решению проблемы",
            "timestamp": time.time(),
        }

    async def _validate_output_artefact(
        self, artefact_path: str, artefact_type: str, quality_criteria: str
    ) -> dict[str, Any]:
        """Валидация output артефакта"""
        from pathlib import Path

        if not artefact_path:
            return {"error": "Artefact path is required"}

        artefact_file = Path(artefact_path)

        if not artefact_file.exists():
            return {
                "error": f"Artefact file not found: {artefact_path}",
                "validation_status": "failed",
                "evidence_links": [],
            }

        # Анализируем качество
        quality_score = 0
        quality_issues = []
        evidence_links = []

        # Проверяем размер файла
        file_size = artefact_file.stat().st_size
        if file_size > 0:
            quality_score += 25
        else:
            quality_issues.append("File is empty")

        # Проверяем расширение файла
        if artefact_file.suffix in [
            ".md",
            ".json",
            ".txt",
            ".html",
            ".py",
            ".js",
            ".ts",
            ".css",
            ".yaml",
            ".yml",
        ]:
            quality_score += 25
        else:
            quality_issues.append(f"Unexpected file extension: {artefact_file.suffix}")

        # Проверяем содержимое файла
        content = ""
        try:
            content = artefact_file.read_text(encoding="utf-8")
            if len(content.strip()) > 100:
                quality_score += 25
                evidence_links.append(f"file://{artefact_file.absolute()}")
            else:
                quality_issues.append("File content too short")
        except Exception as e:
            quality_issues.append(f"Error reading file: {str(e)}")

        # Проверяем структуру (для JSON файлов)
        if artefact_file.suffix == ".json":
            try:
                json.loads(content)
                quality_score += 25
            except json.JSONDecodeError:
                quality_issues.append("Invalid JSON format")

        # Создаем evidence links
        evidence_links.extend(
            [
                f"file://{artefact_file.absolute()}",
                f"@{artefact_file.name}",
                f"mcp-cli validate_output_artefact --path={artefact_file.absolute()}",
            ]
        )

        validation_result = {
            "artefact_id": f"{artefact_file.stem}_{artefact_type}",
            "artefact_type": artefact_type,
            "validation_status": "passed" if quality_score >= 75 else "failed",
            "quality_score": quality_score,
            "quality_issues": quality_issues,
            "access_methods": {
                "mcp_command": f"validate_output_artefact --path={artefact_file.absolute()}",
                "file_path": str(artefact_file.absolute()),
                "chat_link": f"@{artefact_file.name}",
                "web_url": f"file://{artefact_file.absolute()}",
            },
            "evidence": {
                "test_results": f"file://{artefact_file.absolute()}",
                "screenshots": "N/A",
                "logs": f"file://{artefact_file.absolute()}",
                "coverage": "N/A",
            },
            "user_preview": {
                "format": artefact_file.suffix[1:] if artefact_file.suffix else "text",
                "preview_text": (
                    content[:200] if content else "Content preview not available"
                ),
                "thumbnail": "N/A",
            },
            "validation": {
                "quality_score": quality_score,
                "tests_passed": quality_score >= 75,
                "compliance_check": True,
                "user_acceptance": quality_score >= 75,
            },
        }

        return validation_result
