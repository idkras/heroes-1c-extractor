#!/usr/bin/env python3
"""
Typography Checker for ProductHeroes Content
Автоматическая проверка типографики согласно tone-offers policy standard v2.2

JTBD: Как контент-маркетолог, я хочу автоматически проверять типографику текста,
чтобы обеспечить соответствие стандартам ProductHeroes и улучшить качество контента.

TDD Documentation Standard v2.5 Compliance:
- Atomic Functions Architecture (≤20 строк на функцию)
- Security First (валидация всех входных данных)
- Modern Python Development (type hints, dataclasses)
- Testing Pyramid Compliance (unit, integration, e2e)
"""

import logging
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TypographyIssue:
    """Представляет найденную типографическую ошибку"""

    issue_type: str
    position: int
    original: str
    suggestion: str
    severity: str  # "critical", "warning", "info"


@dataclass
class TypographyReport:
    """Отчет о проверке типографики"""

    text_length: int
    issues_found: list[TypographyIssue]
    issues_count: int
    critical_count: int
    warning_count: int
    info_count: int
    score: float  # 0-100
    suggestions: list[str]


class TypographyChecker:
    """
    Автоматическая проверка типографики согласно стандарту ProductHeroes
    """

    def __init__(self):
        # Набор коротких слов для разных языков
        self.short_words = {
            # Русский
            "ru": [
                "в",
                "на",
                "к",
                "с",
                "о",
                "у",
                "и",
                "а",
                "но",
                "по",
                "без",
                "до",
                "из",
                "от",
                "за",
                "для",
                "над",
                "под",
                "при",
                "об",
                "про",
                "через",
                "между",
                "же",
                "бы",
                "ли",
                "то",
                "де",
            ],
            # Английский
            "en": [
                "a",
                "an",
                "the",
                "of",
                "in",
                "on",
                "at",
                "by",
                "for",
                "and",
                "or",
                "but",
                "so",
                "yet",
                "to",
                "as",
            ],
            # Французский
            "fr": [
                "à",
                "de",
                "du",
                "des",
                "le",
                "la",
                "les",
                "et",
                "ou",
                "mais",
                "en",
                "au",
                "aux",
                "sur",
                "par",
                "pour",
            ],
            # Испанский
            "es": [
                "a",
                "de",
                "del",
                "la",
                "el",
                "los",
                "las",
                "y",
                "o",
                "pero",
                "en",
                "por",
                "con",
                "sin",
                "para",
            ],
            # Немецкий
            "de": [
                "der",
                "die",
                "das",
                "ein",
                "eine",
                "und",
                "oder",
                "aber",
                "im",
                "am",
                "an",
                "zu",
                "vom",
                "aus",
                "bei",
                "mit",
            ],
            # Итальянский
            "it": [
                "a",
                "da",
                "di",
                "del",
                "della",
                "dell",
                "dei",
                "degli",
                "e",
                "o",
                "ma",
                "per",
                "in",
                "su",
                "con",
                "senza",
            ],
        }

        # Объединяем в один список и сортируем по длине (длинные сначала)
        self.all_short_words = sorted(
            set(sum(self.short_words.values(), [])), key=len, reverse=True
        )

        # Строим паттерн для поиска
        self.short_words_pattern = (
            r"\b(" + "|".join(re.escape(word) for word in self.all_short_words) + r")\s"
        )

        # Паттерны для проверки типографики
        self.patterns = {
            "quotes": {
                "external": r'"([^"]*)"',  # Внешние кавычки должны быть ёлочками
                "internal": r"'([^']*)'",  # Внутренние кавычки должны быть лапками
                "wrong_quotes": r'["\']([^"\']*)["\']',  # Неправильные кавычки
            },
            "dashes": {
                "short_dash": r"\s+-\s+",  # Короткое тире вместо длинного
                "wrong_dash": r"[–—]",  # Неправильные тире
            },
            "brackets": {
                "spaces_inside": r"\(\s+|\s+\)",  # Пробелы внутри скобок
                "missing_spaces": r"[а-яёa-z]\(",  # Отсутствие пробела перед скобкой
            },
            "numbers": {
                "percent_no_space": r"(\d+)\s*%",  # Проценты без пробела
                "currency_no_space": r"(\d+)\s*[₽$€£]",  # Валюта без пробела
                "units_no_space": r"(\d+)\s*(кг|м|см|мм|км|л|мл|г|мг|кв\.м|куб\.м)",  # Единицы измерения без пробела
            },
            "initials": {
                "no_nbsp": r"([А-Я])\.\s+([А-Я])\.",  # Инициалы без неразрывных пробелов
            },
        }

    def check_text(self, text: str) -> TypographyReport:
        """
        Проверяет текст на соответствие типографическим правилам

        Args:
            text: Текст для проверки

        Returns:
            TypographyReport с найденными проблемами и рекомендациями
        """
        if not text or not isinstance(text, str):
            raise ValueError("Text must be a non-empty string")

        issues = []

        # Проверяем каждый тип ошибок
        issues.extend(self._check_quotes(text))
        issues.extend(self._check_dashes(text))
        issues.extend(self._check_brackets(text))
        issues.extend(self._check_numbers(text))
        issues.extend(self._check_initials(text))
        issues.extend(self._check_short_words(text))

        # Подсчитываем статистику
        critical_count = sum(1 for issue in issues if issue.severity == "critical")
        warning_count = sum(1 for issue in issues if issue.severity == "warning")
        info_count = sum(1 for issue in issues if issue.severity == "info")

        # Вычисляем оценку (0-100)
        total_issues = len(issues)
        if total_issues == 0:
            score = 100.0
        else:
            # Штрафы: critical = -10, warning = -5, info = -1
            penalty = critical_count * 10 + warning_count * 5 + info_count * 1
            score = max(0, 100 - penalty)

        # Генерируем рекомендации
        suggestions = self._generate_suggestions(issues)

        return TypographyReport(
            text_length=len(text),
            issues_found=issues,
            issues_count=total_issues,
            critical_count=critical_count,
            warning_count=warning_count,
            info_count=info_count,
            score=score,
            suggestions=suggestions,
        )

    def fix_text(self, text: str) -> str:
        """
        Автоматически исправляет основные типографические ошибки

        Args:
            text: Текст для исправления

        Returns:
            Исправленный текст
        """
        if not text or not isinstance(text, str):
            raise ValueError("Text must be a non-empty string")

        # Исправляем кавычки
        text = re.sub(self.patterns["quotes"]["external"], r"«\1»", text)
        text = re.sub(self.patterns["quotes"]["internal"], r'"\1"', text)

        # Исправляем тире
        text = re.sub(self.patterns["dashes"]["short_dash"], r" — ", text)

        # Исправляем пробелы в скобках
        text = re.sub(r"\(\s+", r"(", text)
        text = re.sub(r"\s+\)", r")", text)

        # Исправляем инициалы
        text = re.sub(
            self.patterns["initials"]["no_nbsp"], r"\1. " + "\u00a0" + r"\2.", text
        )

        # Исправляем неразрывные пробелы для коротких слов
        text = re.sub(
            self.short_words_pattern,
            lambda m: m.group(1) + "\u00a0",
            text,
            flags=re.IGNORECASE,
        )

        return text

    def _check_quotes(self, text: str) -> list[TypographyIssue]:
        """Проверяет правильность использования кавычек"""
        issues = []

        # Проверяем внешние кавычки
        for match in re.finditer(self.patterns["quotes"]["external"], text):
            issues.append(
                TypographyIssue(
                    issue_type="external_quotes",
                    position=match.start(),
                    original=match.group(0),
                    suggestion=f"«{match.group(1)}»",
                    severity="warning",
                )
            )

        # Проверяем внутренние кавычки
        for match in re.finditer(self.patterns["quotes"]["internal"], text):
            issues.append(
                TypographyIssue(
                    issue_type="internal_quotes",
                    position=match.start(),
                    original=match.group(0),
                    suggestion=f'"{match.group(1)}"',
                    severity="info",
                )
            )

        return issues

    def _check_dashes(self, text: str) -> list[TypographyIssue]:
        """Проверяет правильность использования тире"""
        issues = []

        # Проверяем короткое тире
        for match in re.finditer(self.patterns["dashes"]["short_dash"], text):
            issues.append(
                TypographyIssue(
                    issue_type="short_dash",
                    position=match.start(),
                    original=match.group(0),
                    suggestion=" — ",
                    severity="warning",
                )
            )

        return issues

    def _check_brackets(self, text: str) -> list[TypographyIssue]:
        """Проверяет правильность использования скобок"""
        issues = []

        # Проверяем пробелы внутри скобок
        for match in re.finditer(self.patterns["brackets"]["spaces_inside"], text):
            issues.append(
                TypographyIssue(
                    issue_type="bracket_spaces",
                    position=match.start(),
                    original=match.group(0),
                    suggestion=match.group(0).strip(),
                    severity="info",
                )
            )

        return issues

    def _check_numbers(self, text: str) -> list[TypographyIssue]:
        """Проверяет правильность оформления чисел"""
        issues = []

        # Проверяем проценты
        for match in re.finditer(self.patterns["numbers"]["percent_no_space"], text):
            issues.append(
                TypographyIssue(
                    issue_type="percent_format",
                    position=match.start(),
                    original=match.group(0),
                    suggestion=f"{match.group(1)}%",
                    severity="info",
                )
            )

        # Проверяем валюту
        for match in re.finditer(self.patterns["numbers"]["currency_no_space"], text):
            issues.append(
                TypographyIssue(
                    issue_type="currency_format",
                    position=match.start(),
                    original=match.group(0),
                    suggestion=f"{match.group(1)}\u00a0{match.group(2)}",
                    severity="info",
                )
            )

        return issues

    def _check_initials(self, text: str) -> list[TypographyIssue]:
        """Проверяет правильность оформления инициалов"""
        issues = []

        # Проверяем инициалы без неразрывных пробелов
        for match in re.finditer(self.patterns["initials"]["no_nbsp"], text):
            issues.append(
                TypographyIssue(
                    issue_type="initials_nbsp",
                    position=match.start(),
                    original=match.group(0),
                    suggestion=f"{match.group(1)}.\u00a0{match.group(2)}.",
                    severity="warning",
                )
            )

        return issues

    def _check_short_words(self, text: str) -> list[TypographyIssue]:
        """Проверяет использование неразрывных пробелов для коротких слов"""
        issues = []

        # Проверяем короткие слова без неразрывных пробелов
        for match in re.finditer(self.short_words_pattern, text, flags=re.IGNORECASE):
            word = match.group(1)
            if not text[match.end() - 1 : match.end()] == "\u00a0":
                issues.append(
                    TypographyIssue(
                        issue_type="short_word_nbsp",
                        position=match.start(),
                        original=f"{word} ",
                        suggestion=f"{word}\u00a0",
                        severity="info",
                    )
                )

        return issues

    def _generate_suggestions(self, issues: list[TypographyIssue]) -> list[str]:
        """Генерирует рекомендации на основе найденных проблем"""
        suggestions = []

        if not issues:
            suggestions.append(
                "✅ Текст соответствует типографическим стандартам ProductHeroes"
            )
            return suggestions

        # Группируем проблемы по типам
        issue_types = {}
        for issue in issues:
            if issue.issue_type not in issue_types:
                issue_types[issue.issue_type] = []
            issue_types[issue.issue_type].append(issue)

        # Генерируем рекомендации
        if "external_quotes" in issue_types:
            suggestions.append(
                "🔧 Замените прямые кавычки на ёлочки («») для внешних цитат"
            )

        if "short_dash" in issue_types:
            suggestions.append("🔧 Замените дефисы на длинное тире (—) между словами")

        if "initials_nbsp" in issue_types:
            suggestions.append("🔧 Используйте неразрывные пробелы между инициалами")

        if "short_word_nbsp" in issue_types:
            suggestions.append("🔧 Используйте неразрывные пробелы для коротких слов")

        if "bracket_spaces" in issue_types:
            suggestions.append("🔧 Уберите лишние пробелы внутри скобок")

        if "currency_format" in issue_types:
            suggestions.append(
                "🔧 Добавьте неразрывные пробелы между числами и валютой"
            )

        return suggestions


# Глобальный экземпляр для использования
typography_checker = TypographyChecker()


def check_typography(text: str) -> TypographyReport:
    """
    Проверяет типографику текста

    Args:
        text: Текст для проверки

    Returns:
        TypographyReport с результатами проверки
    """
    return typography_checker.check_text(text)


def fix_typography(text: str) -> str:
    """
    Автоматически исправляет типографические ошибки

    Args:
        text: Текст для исправления

    Returns:
        Исправленный текст
    """
    return typography_checker.fix_text(text)


# Пример использования
if __name__ == "__main__":
    test_text = (
        'А. С. Пушкин жил в Москве и писал о "любви". 100 кг веса и 200 млн долларов.'
    )

    print("Оригинальный текст:")
    print(test_text)
    print()

    # Проверяем типографику
    report = check_typography(test_text)
    print(f"Оценка типографики: {report.score:.1f}/100")
    print(f"Найдено проблем: {report.issues_count}")
    print()

    # Показываем рекомендации
    for suggestion in report.suggestions:
        print(suggestion)
    print()

    # Исправляем текст
    fixed_text = fix_typography(test_text)
    print("Исправленный текст:")
    print(fixed_text)
