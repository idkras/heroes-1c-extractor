#!/usr/bin/env python3
"""
Todo Parser Module

Модуль для парсинга *.todo.md файлов согласно TDD принципам.
Отвечает только за извлечение данных из todo файлов.
"""

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TodoCriterion:
    """Критерий из todo файла"""

    text: str
    is_completed: bool
    line_number: int


@dataclass
class TodoRelease:
    """Релиз из todo файла"""

    name: str
    content: str
    criteria: list[TodoCriterion]
    start_line: int
    end_line: int


class TodoParser:
    """Парсер для *.todo.md файлов"""

    def __init__(self):
        self.release_patterns = {
            "default": r"##\s*.*?\*\*([^*]+)\*\*.*?(?=##\s*[🚀🛠️🔧]|\Z)",
            "rocket": r"##\s*🚀\s*\*\*([^*]+)\*\*.*?(?=##\s*[🚀🛠️🔧]|\Z)",
            "tools": r"##\s*[🛠️🔧]\s*\*\*([^*]+)\*\*.*?(?=##\s*[🚀🛠️🔧]|\Z)",
        }
        self.criteria_pattern = r"-\s*\[([ x])\]\s*(.+?)(?=\n|$)"
        self.criteria_section_pattern = (
            r"\*\*✅\s*Критерии успеха.*?(?=\*\*📋|\*\*🤖|\n##|\Z)"
        )

    def parse_file(self, file_path: Path) -> dict[str, TodoRelease]:
        """Парсит todo файл и возвращает словарь релизов"""
        if not file_path.exists():
            raise FileNotFoundError(f"Todo file not found: {file_path}")

        content = file_path.read_text(encoding="utf-8")
        releases = {}

        # Ищем все релизы
        for _pattern_name, pattern in self.release_patterns.items():
            matches = re.finditer(pattern, content, re.DOTALL | re.IGNORECASE)

            for match in matches:
                release_name = match.group(1).strip()
                release_content = match.group(0)

                # Извлекаем критерии
                criteria = self._extract_criteria(release_content)

                releases[release_name] = TodoRelease(
                    name=release_name,
                    content=release_content,
                    criteria=criteria,
                    start_line=content[: match.start()].count("\n") + 1,
                    end_line=content[: match.end()].count("\n") + 1,
                )

        return releases

    def _extract_criteria(self, release_content: str) -> list[TodoCriterion]:
        """Извлекает критерии из содержимого релиза"""
        criteria = []

        # Ищем секцию критериев успеха
        criteria_section_match = re.search(
            self.criteria_section_pattern, release_content, re.DOTALL | re.IGNORECASE
        )

        if criteria_section_match:
            criteria_content = criteria_section_match.group(0)
        else:
            criteria_content = release_content

        # Извлекаем критерии
        matches = re.finditer(self.criteria_pattern, criteria_content)

        for match in matches:
            status = match.group(1)
            criterion_text = match.group(2).strip()
            line_number = criteria_content[: match.start()].count("\n") + 1

            criteria.append(
                TodoCriterion(
                    text=criterion_text,
                    is_completed=status == "x",
                    line_number=line_number,
                )
            )

        return criteria

    def get_release_criteria(
        self, file_path: Path, release_name: str
    ) -> list[TodoCriterion]:
        """Получает критерии для конкретного релиза"""
        releases = self.parse_file(file_path)

        if release_name not in releases:
            raise ValueError(f"Release '{release_name}' not found")

        return releases[release_name].criteria


class TodoValidator:
    """Валидатор для todo файлов"""

    def __init__(self, parser: TodoParser):
        self.parser = parser

    def validate_release(self, file_path: Path, release_name: str) -> dict:
        """Валидирует релиз и возвращает результаты"""
        try:
            criteria = self.parser.get_release_criteria(file_path, release_name)

            validation_results = []
            passed_criteria = 0
            total_criteria = len(criteria)

            for criterion in criteria:
                validation_results.append(
                    {
                        "criterion": criterion.text,
                        "expected": (
                            "Completed" if criterion.is_completed else "Not completed"
                        ),
                        "actual": (
                            "Completed" if criterion.is_completed else "Not completed"
                        ),
                        "status": "passed" if criterion.is_completed else "failed",
                        "evidence": f"Marked as {'completed' if criterion.is_completed else 'not completed'} in todo file",
                    }
                )

                if criterion.is_completed:
                    passed_criteria += 1

            validation_score = (
                (passed_criteria / total_criteria * 100) if total_criteria > 0 else 0
            )

            return {
                "validation_status": "passed" if validation_score >= 80 else "failed",
                "todo_file_parsed": True,
                "success_criteria_found": total_criteria,
                "criteria_validation": validation_results,
                "validation_score": validation_score,
                "release_name": release_name,
            }

        except Exception as e:
            return {
                "validation_status": "failed",
                "error": str(e),
                "todo_file_parsed": False,
                "success_criteria_found": 0,
                "criteria_validation": [],
                "validation_score": 0,
                "release_name": release_name,
            }
