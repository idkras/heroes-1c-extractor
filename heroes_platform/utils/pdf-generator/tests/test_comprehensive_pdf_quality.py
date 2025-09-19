#!/usr/bin/env python3
"""
Проверка качества PDF документа Rick_ai_Security_Documentation_Comprehensive.pdf
через стандарты дизайна и типографики.
"""

import os
import re
from pathlib import Path


def test_pdf_exists():
    """Проверка существования PDF файла."""
    pdf_path = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_Final_Fixed.pdf"

    if Path(pdf_path).exists():
        size = os.path.getsize(pdf_path)
        print(f"✓ PDF файл найден: {size} bytes")
        return True
    else:
        print("❌ PDF файл не найден")
        return False


def test_generator_compliance():
    """Проверка соответствия генератора стандартам типографики."""
    generator_path = "generate_pdf_comprehensive_fix.py"

    if not Path(generator_path).exists():
        print("❌ Генератор не найден")
        return False

    with open(generator_path, encoding="utf-8") as f:
        content = f.read()

    issues = []
    checks = [
        ("max-width: 165mm", "оптимальная ширина полосы набора"),
        ("line-height: 1.5", "межстрочный интервал"),
        ("hyphens: auto", "автоматические переносы"),
        ("orphans: 2", "контроль сирот"),
        ("widows: 3", "контроль вдов"),
        ("text-rendering: optimizeLegibility", "качество рендеринга"),
        ("font-feature-settings", "кернинг и лигатуры"),
        ("«\\1»", "русские кавычки"),
        ("—", "правильные тире"),
        ("\\u00A0", "неразрывные пробелы"),
    ]

    for check, description in checks:
        if check not in content:
            issues.append(f"Отсутствует {description}")

    if issues:
        print("❌ ПРОБЛЕМЫ ГЕНЕРАТОРА:")
        for issue in issues:
            print(f"   {issue}")
        return False
    else:
        print("✓ Генератор соответствует стандартам")
        return True


def test_source_text_quality():
    """Проверка качества исходного текста."""
    source_path = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/when_security_asked_about_user_data RU_fixed.md"

    if not Path(source_path).exists():
        print("❌ Исходный файл не найден")
        return False

    with open(source_path, encoding="utf-8") as f:
        content = f.read()

    issues = []

    # Проверка структуры
    if content.count("##") < 3:
        issues.append("Недостаточно подзаголовков для структурирования")

    # Проверка длинных абзацев
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    long_paragraphs = [p for p in paragraphs if len(p) > 500]

    if long_paragraphs:
        issues.append(f"Найдено {len(long_paragraphs)} слишком длинных абзацев")

    # Проверка типографических проблем
    typography_issues = []

    if '"' in content and "«" not in content:
        typography_issues.append("неправильные кавычки")

    if re.search(r"\d+\s+(лет|года|дней)", content):
        typography_issues.append("отсутствуют неразрывные пробелы")

    if re.search(r"([а-яё])-\s+([а-яё])", content, re.IGNORECASE):
        typography_issues.append("неправильные переносы")

    if typography_issues:
        issues.append(f"Типографические проблемы: {', '.join(typography_issues)}")

    if issues:
        print("⚠️  ПРОБЛЕМЫ ИСХОДНОГО ТЕКСТА:")
        for issue in issues:
            print(f"   {issue}")
        return False
    else:
        print("✓ Качество исходного текста хорошее")
        return True


def test_comprehensive_standard_compliance():
    """Проверка соответствия комплексному стандарту типографики."""
    standard_path = "[standards .md]/9. development · documentation/2.6 comprehensive typography standard 31 may 2025 1022 cet by ai assistant.md"

    if not Path(standard_path).exists():
        print("❌ Стандарт типографики не найден")
        return False

    with open(standard_path, encoding="utf-8") as f:
        standard_content = f.read()

    # Проверяем, что стандарт содержит все необходимые разделы
    required_sections = [
        "Проблемы ширины полосы набора",
        "Неструктурированные абзацы",
        "Ошибки в кавычках",
        "Проблемы с тире и дефисами",
        "Отсутствие неразрывных пробелов",
        "Неправильные переносы",
        "Обязательные CSS свойства",
        "Контроль качества",
    ]

    missing_sections = [
        section for section in required_sections if section not in standard_content
    ]

    if missing_sections:
        print("❌ НЕПОЛНЫЙ СТАНДАРТ:")
        for section in missing_sections:
            print(f"   Отсутствует раздел: {section}")
        return False
    else:
        print("✓ Стандарт типографики полный")
        return True


def test_css_quality():
    """Проверка качества CSS в генераторе."""
    generator_path = "generate_pdf_comprehensive_fix.py"

    with open(generator_path, encoding="utf-8") as f:
        content = f.read()

    # Извлекаем CSS блок
    css_match = re.search(r'css_styles = """(.*?)"""', content, re.DOTALL)
    if not css_match:
        print("❌ CSS блок не найден")
        return False

    css_content = css_match.group(1)

    issues = []

    # Проверяем критические CSS свойства
    critical_props = [
        "max-width",
        "line-height",
        "hyphens",
        "orphans",
        "widows",
        "page-break-inside",
        "text-rendering",
        "font-feature-settings",
    ]

    for prop in critical_props:
        if prop not in css_content:
            issues.append(f"Отсутствует свойство {prop}")

    # Проверяем значения
    if "max-width: 165mm" not in css_content:
        issues.append("Неоптимальная ширина полосы набора")

    if "line-height: 1.5" not in css_content:
        issues.append("Неоптимальный межстрочный интервал")

    if issues:
        print("❌ ПРОБЛЕМЫ CSS:")
        for issue in issues:
            print(f"   {issue}")
        return False
    else:
        print("✓ Качество CSS высокое")
        return True


def analyze_pdf_size_and_quality():
    """Анализ размера и качества PDF."""
    pdf_path = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_Final_Fixed.pdf"

    if not Path(pdf_path).exists():
        return False

    size = os.path.getsize(pdf_path)

    # Анализ размера файла
    if size < 30000:
        print(f"⚠️  PDF слишком мал: {size} bytes - возможны проблемы с контентом")
        return False
    elif size > 100000:
        print(f"⚠️  PDF слишком велик: {size} bytes - возможны проблемы с оптимизацией")
        return False
    else:
        print(f"✓ Размер PDF оптимальный: {size} bytes")
        return True


def manual_review_checklist():
    """Чеклист для ручной проверки PDF."""
    print("\n📋 ЧЕКЛИСТ ДЛЯ РУЧНОЙ ПРОВЕРКИ:")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    checklist = [
        "Ширина текста удобна для чтения (не слишком узкая)",
        "Абзацы структурированы, нет огромных блоков текста",
        'Используются русские кавычки «» вместо ""',
        "Тире — правильные, не дефисы -",
        'Нет переносов типа "5 лет", "ст. 152" на разные строки',
        'Нет странных переносов "пере- носов" в середине слов',
        "Заголовки без зеленого оформления",
        "Таблицы читаемы и правильно оформлены",
        "Нет пустых страниц",
        "Шрифт читаемый и профессиональный",
        "Отступы и поля документа правильные",
        "Нумерация страниц присутствует",
        "Документ выглядит профессионально для корпоративной проверки",
    ]

    for i, item in enumerate(checklist, 1):
        print(f"{i:2d}. ☐ {item}")

    print("\n💡 Откройте PDF файл и проверьте каждый пункт визуально")


def run_comprehensive_quality_check():
    """Запуск полной проверки качества PDF."""
    print("Комплексная проверка качества PDF документа")
    print("=" * 60)

    tests = [
        test_pdf_exists,
        test_generator_compliance,
        test_source_text_quality,
        test_comprehensive_standard_compliance,
        test_css_quality,
        analyze_pdf_size_and_quality,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 60)
    print(f"Автоматические тесты: {passed}/{total} пройдено")

    if passed == total:
        print("🎉 Все автоматические тесты пройдены!")
    else:
        print(f"⚠️  {total - passed} тестов требуют внимания")

    manual_review_checklist()

    return passed == total


if __name__ == "__main__":
    run_comprehensive_quality_check()
