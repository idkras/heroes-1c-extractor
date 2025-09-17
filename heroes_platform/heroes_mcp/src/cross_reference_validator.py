#!/usr/bin/env python3
"""
Cross-Reference Validation Checklist
Zero tolerance к отклонениям от эталона

JTBD: Как валидатор качества, я хочу проверять соответствие output эталону,
чтобы обеспечить zero tolerance к отклонениям от стандарта.

TDD Documentation Standard v2.5 Compliance:
- Atomic Functions Architecture (≤20 строк на функцию)
- Security First (валидация всех входных данных)
- Modern Python Development (type hints, dataclasses)
- Testing Pyramid Compliance (unit, integration, e2e)
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class ValidationRule:
    """Validation rule for cross-reference checking"""

    name: str
    description: str
    critical: bool = True
    pattern: Optional[str] = None
    required_sections: Optional[list[str]] = None
    forbidden_patterns: Optional[list[str]] = None
    exact_match: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of validation check"""

    rule_name: str
    passed: bool
    details: str
    critical: bool = True
    suggestions: Optional[list[str]] = None


@dataclass
class CrossReferenceReport:
    """Complete cross-reference validation report"""

    timestamp: str
    reference_file: str
    generated_file: str
    total_rules: int
    passed_rules: int
    failed_rules: int
    critical_failures: int
    validation_results: list[ValidationResult]
    overall_score: float
    compliance_status: str  # "PASSED", "NEEDS_IMPROVEMENT", "FAILED"


class CrossReferenceValidator:
    """
    Cross-Reference Validation Checklist for HeroesGPT analysis

    JTBD: Как валидатор соответствия, я хочу проверять точное соответствие эталону,
    чтобы обеспечить zero tolerance к отклонениям от стандарта.
    """

    def __init__(self):
        self._validation_rules = self._setup_validation_rules()
        self._reference_patterns = self._setup_reference_patterns()

    def _setup_validation_rules(self) -> list[ValidationRule]:
        """Setup validation rules based on reference of truth"""
        return [
            # 1. Метаданные анализа
            ValidationRule(
                name="metadata_format",
                description="Правильный формат метаданных анализа",
                critical=True,
                exact_match="<!-- 🔒 МЕТАДАННЫЕ АНАЛИЗА: BEGIN -->",
            ),
            # 2. Структура оферов
            ValidationRule(
                name="offers_table_structure",
                description="Полная структура оферов с 7 колонками",
                critical=True,
                required_sections=[
                    "Тип",
                    "Количественные данные",
                    "Сегмент",
                    "Эмоциональный триггер",
                    "Доверие",
                    "Срочность",
                ],
            ),
            # 3. Обязательные секции
            ValidationRule(
                name="required_sections",
                description="Все обязательные секции присутствуют",
                critical=True,
                required_sections=[
                    "Viral Segments Priority Analysis",
                    "Decision Minefield Detection",
                    "ROI Projections & Conversion Forecasting",
                    "Self-Validation Checklist",
                ],
            ),
            # 4. JTBD иерархия
            ValidationRule(
                name="jtbd_hierarchy",
                description="Полная иерархия JTBD с Medium и Small",
                critical=True,
                pattern=r"Medium JTBD|Small JTBD",
            ),
            # 5. Формат details секций
            ValidationRule(
                name="details_format",
                description="Правильный формат <details> секций",
                critical=False,
                pattern=r"<details>.*?</details>",
            ),
            # 6. Запрещенные паттерны
            ValidationRule(
                name="forbidden_patterns",
                description="Отсутствие запрещенных паттернов",
                critical=True,
                forbidden_patterns=[
                    "<!-- 🔒 PROTECTED SECTION: BEGIN -->",
                    "gap analysis создан в отдельном файле",
                ],
            ),
            # 7. Структура сегментов
            ValidationRule(
                name="segment_structure",
                description="Правильная структура сегментов",
                critical=True,
                pattern=r"🟢 Идеальная|🟡 Подходящая|🔴 Неподходящая",
            ),
            # 8. Формат цитат
            ValidationRule(
                name="quote_format",
                description="Правильный формат цитат с attribution",
                critical=False,
                pattern=r"«.*?» \(.*?\)",
            ),
            # 9. Self-Validation Checklist
            ValidationRule(
                name="self_validation_checklist",
                description="Self-Validation Checklist соответствует эталону",
                critical=True,
                pattern=r"✅|❌|⚠️",
            ),
            # 10. Качество контента
            ValidationRule(
                name="content_quality",
                description="Качество контента соответствует эталону",
                critical=False,
                forbidden_patterns=["placeholder text", "TODO", "FIXME"],
            ),
        ]

    def _setup_reference_patterns(self) -> dict[str, Any]:
        """Setup reference patterns from эталон"""
        return {
            "metadata_start": "<!-- 🔒 МЕТАДАННЫЕ АНАЛИЗА: BEGIN -->",
            "metadata_end": "<!-- 🔒 МЕТАДАННЫЕ АНАЛИЗА: END -->",
            "offers_table_headers": [
                "Тип",
                "Количественные данные",
                "Сегмент",
                "Эмоциональный триггер",
                "Доверие",
                "Срочность",
            ],
            "required_sections": [
                "Viral Segments Priority Analysis",
                "Decision Minefield Detection",
                "ROI Projections & Conversion Forecasting",
                "Self-Validation Checklist",
            ],
            "jtbd_patterns": {
                "big": r"Big JTBD \d+:",
                "medium": r"Medium JTBD \d+:",
                "small": r"Small JTBD \d+:",
            },
            "segment_relevance": {
                "ideal": "🟢 Идеальная",
                "suitable": "🟡 Подходящая",
                "unsuitable": "🔴 Неподходящая",
            },
        }

    def validate_analysis(
        self, generated_content: str, reference_content: str
    ) -> CrossReferenceReport:
        """
        Validate generated analysis against reference

        JTBD: Как валидатор качества, я хочу проверять соответствие сгенерированного анализа эталону,
        чтобы обеспечить zero tolerance к отклонениям.
        """
        validation_results = []

        for rule in self._validation_rules:
            result = self._validate_rule(rule, generated_content, reference_content)
            validation_results.append(result)

        # Calculate statistics
        total_rules = len(validation_results)
        passed_rules = sum(1 for r in validation_results if r.passed)
        failed_rules = total_rules - passed_rules
        critical_failures = sum(
            1 for r in validation_results if not r.passed and r.critical
        )

        # Calculate overall score
        overall_score = (passed_rules / total_rules) * 100 if total_rules > 0 else 0

        # Determine compliance status
        if critical_failures == 0 and overall_score >= 95:
            compliance_status = "PASSED"
        elif critical_failures == 0 and overall_score >= 80:
            compliance_status = "NEEDS_IMPROVEMENT"
        else:
            compliance_status = "FAILED"

        return CrossReferenceReport(
            timestamp=datetime.now().isoformat(),
            reference_file="reference_of_truth.md",
            generated_file="generated_analysis.md",
            total_rules=total_rules,
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            critical_failures=critical_failures,
            validation_results=validation_results,
            overall_score=overall_score,
            compliance_status=compliance_status,
        )

    def _validate_rule(
        self, rule: ValidationRule, generated_content: str, reference_content: str
    ) -> ValidationResult:
        """Validate single rule"""
        try:
            if rule.exact_match:
                return self._validate_exact_match(rule, generated_content)
            elif rule.pattern:
                return self._validate_pattern(rule, generated_content)
            elif rule.required_sections:
                return self._validate_required_sections(rule, generated_content)
            elif rule.forbidden_patterns:
                return self._validate_forbidden_patterns(rule, generated_content)
            else:
                return ValidationResult(
                    rule_name=rule.name,
                    passed=False,
                    details="No validation method specified",
                    critical=rule.critical,
                )
        except Exception as e:
            return ValidationResult(
                rule_name=rule.name,
                passed=False,
                details=f"Validation error: {str(e)}",
                critical=rule.critical,
            )

    def _validate_exact_match(
        self, rule: ValidationRule, content: str
    ) -> ValidationResult:
        """Validate exact match"""
        if rule.exact_match in content:
            return ValidationResult(
                rule_name=rule.name,
                passed=True,
                details=f"Found exact match: {rule.exact_match}",
                critical=rule.critical,
            )
        else:
            return ValidationResult(
                rule_name=rule.name,
                passed=False,
                details=f"Missing exact match: {rule.exact_match}",
                critical=rule.critical,
                suggestions=[f"Add '{rule.exact_match}' to the content"],
            )

    def _validate_pattern(self, rule: ValidationRule, content: str) -> ValidationResult:
        """Validate pattern match"""
        matches = re.findall(rule.pattern, content, re.MULTILINE | re.DOTALL)
        if matches:
            return ValidationResult(
                rule_name=rule.name,
                passed=True,
                details=f"Found {len(matches)} pattern matches",
                critical=rule.critical,
            )
        else:
            return ValidationResult(
                rule_name=rule.name,
                passed=False,
                details=f"No matches found for pattern: {rule.pattern}",
                critical=rule.critical,
                suggestions=[f"Add content matching pattern: {rule.pattern}"],
            )

    def _validate_required_sections(
        self, rule: ValidationRule, content: str
    ) -> ValidationResult:
        """Validate required sections presence"""
        missing_sections = []
        found_sections = []

        for section in rule.required_sections:
            if section in content:
                found_sections.append(section)
            else:
                missing_sections.append(section)

        if not missing_sections:
            return ValidationResult(
                rule_name=rule.name,
                passed=True,
                details=f"All required sections found: {', '.join(found_sections)}",
                critical=rule.critical,
            )
        else:
            return ValidationResult(
                rule_name=rule.name,
                passed=False,
                details=f"Missing sections: {', '.join(missing_sections)}",
                critical=rule.critical,
                suggestions=[f"Add section: {section}" for section in missing_sections],
            )

    def _validate_forbidden_patterns(
        self, rule: ValidationRule, content: str
    ) -> ValidationResult:
        """Validate absence of forbidden patterns"""
        found_patterns = []

        for pattern in rule.forbidden_patterns:
            if pattern in content:
                found_patterns.append(pattern)

        if not found_patterns:
            return ValidationResult(
                rule_name=rule.name,
                passed=True,
                details="No forbidden patterns found",
                critical=rule.critical,
            )
        else:
            return ValidationResult(
                rule_name=rule.name,
                passed=False,
                details=f"Found forbidden patterns: {', '.join(found_patterns)}",
                critical=rule.critical,
                suggestions=[
                    f"Remove or replace: {pattern}" for pattern in found_patterns
                ],
            )

    def generate_validation_report(self, report: CrossReferenceReport) -> str:
        """Generate human-readable validation report"""
        report_lines = [
            "# Cross-Reference Validation Report",
            f"**Timestamp:** {report.timestamp}",
            f"**Reference:** {report.reference_file}",
            f"**Generated:** {report.generated_file}",
            "",
            "## Summary",
            f"- **Overall Score:** {report.overall_score:.1f}%",
            f"- **Compliance Status:** {report.compliance_status}",
            f"- **Total Rules:** {report.total_rules}",
            f"- **Passed:** {report.passed_rules}",
            f"- **Failed:** {report.failed_rules}",
            f"- **Critical Failures:** {report.critical_failures}",
            "",
            "## Detailed Results",
        ]

        for result in report.validation_results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            critical = "🔴 CRITICAL" if result.critical else "🟡 NON-CRITICAL"

            report_lines.extend(
                [
                    f"### {result.rule_name} {status} {critical}",
                    f"**Description:** {result.details}",
                    "",
                ]
            )

            if result.suggestions:
                report_lines.append("**Suggestions:**")
                for suggestion in result.suggestions:
                    report_lines.append(f"- {suggestion}")
                report_lines.append("")

        # Add recommendations
        report_lines.extend(["## Recommendations", ""])

        if report.compliance_status == "FAILED":
            report_lines.extend(
                [
                    "🚨 **CRITICAL ISSUES DETECTED**",
                    "",
                    "**Immediate Actions Required:**",
                    "1. Fix all critical validation failures",
                    "2. Ensure exact match with reference format",
                    "3. Add all missing required sections",
                    "4. Remove forbidden patterns",
                    "5. Re-run validation after fixes",
                ]
            )
        elif report.compliance_status == "NEEDS_IMPROVEMENT":
            report_lines.extend(
                [
                    "⚠️ **IMPROVEMENTS NEEDED**",
                    "",
                    "**Recommended Actions:**",
                    "1. Address non-critical validation failures",
                    "2. Improve content quality",
                    "3. Add missing optional sections",
                    "4. Enhance formatting consistency",
                ]
            )
        else:
            report_lines.extend(
                [
                    "✅ **VALIDATION PASSED**",
                    "",
                    "**Status:** Analysis meets all critical requirements",
                    "**Next Steps:**",
                    "1. Review non-critical suggestions",
                    "2. Consider optional improvements",
                    "3. Proceed with deployment",
                ]
            )

        return "\n".join(report_lines)

    def validate_file(
        self, generated_file_path: str, reference_file_path: str
    ) -> CrossReferenceReport:
        """Validate generated file against reference file"""
        try:
            with open(generated_file_path, encoding="utf-8") as f:
                generated_content = f.read()

            with open(reference_file_path, encoding="utf-8") as f:
                reference_content = f.read()

            return self.validate_analysis(generated_content, reference_content)
        except Exception as e:
            logger.error(f"Error validating files: {e}")
            return CrossReferenceReport(
                timestamp=datetime.now().isoformat(),
                reference_file=reference_file_path,
                generated_file=generated_file_path,
                total_rules=0,
                passed_rules=0,
                failed_rules=0,
                critical_failures=1,
                validation_results=[],
                overall_score=0,
                compliance_status="FAILED",
            )


# Global instance
cross_reference_validator = CrossReferenceValidator()


def validate_analysis_content(
    generated_content: str, reference_content: str
) -> CrossReferenceReport:
    """
    Convenience function to validate analysis content

    JTBD: Как разработчик, я хочу легко валидировать анализ,
    чтобы обеспечить соответствие эталону.
    """
    return cross_reference_validator.validate_analysis(
        generated_content, reference_content
    )


def validate_analysis_file(
    generated_file_path: str, reference_file_path: str
) -> CrossReferenceReport:
    """
    Convenience function to validate analysis file

    JTBD: Как разработчик, я хочу легко валидировать файлы анализа,
    чтобы обеспечить соответствие эталону.
    """
    return cross_reference_validator.validate_file(
        generated_file_path, reference_file_path
    )


def generate_validation_report(report: CrossReferenceReport) -> str:
    """
    Convenience function to generate validation report

    JTBD: Как пользователь, я хочу получить понятный отчет о валидации,
    чтобы понять что нужно исправить.
    """
    return cross_reference_validator.generate_validation_report(report)
