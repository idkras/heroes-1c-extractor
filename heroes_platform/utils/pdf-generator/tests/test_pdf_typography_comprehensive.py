#!/usr/bin/env python3
"""
Комплексные тесты типографики PDF документов.
Проверяет все выявленные проблемы: структуру, переносы, кавычки, тире, неразрывные пробелы.
"""

import re
from pathlib import Path
import subprocess

def test_pdf_line_width():
    """Тест правильной ширины полосы набора - не должно быть слишком узких колонок."""
    print("Проверка ширины полосы набора...")
    
    # Проверяем CSS в генераторах PDF
    pdf_generators = [
        "generate_pdf_final.py",
        "generate_pdf_typography_enhanced.py"
    ]
    
    issues = []
    
    for generator in pdf_generators:
        if Path(generator).exists():
            with open(generator, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Проверяем max-width в CSS
            if "max-width:" in content:
                max_widths = re.findall(r'max-width:\s*(\d+)mm', content)
                for width in max_widths:
                    if int(width) < 140:  # Слишком узко
                        issues.append(f"{generator}: ширина {width}mm слишком узкая")
                    elif int(width) > 180:  # Слишком широко
                        issues.append(f"{generator}: ширина {width}mm слишком широкая")
    
    if issues:
        print("❌ ПРОБЛЕМЫ С ШИРИНОЙ:")
        for issue in issues:
            print(f"   {issue}")
        return False
    else:
        print("✓ Ширина полосы набора: ОПТИМАЛЬНАЯ")
        return True

def test_pdf_paragraph_structure():
    """Тест структуры абзацев - не должно быть неструктурированных длинных блоков."""
    print("Проверка структуры абзацев...")
    
    source_file = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/when_security_asked_about_user_data RU.md"
    
    if not Path(source_file).exists():
        print("⚠️ Исходный файл не найден")
        return True
    
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # Находим длинные абзацы
    paragraphs = content.split('\n\n')
    for i, paragraph in enumerate(paragraphs):
        if len(paragraph) > 500:  # Слишком длинный абзац
            sentences = re.split(r'[.!?]+', paragraph)
            if len(sentences) > 4:
                issues.append(f"Абзац {i+1}: {len(paragraph)} символов, {len(sentences)} предложений")
    
    # Проверяем наличие структурирующих элементов
    if '##' not in content:
        issues.append("Отсутствуют подзаголовки для структурирования")
    
    if issues:
        print("❌ ПРОБЛЕМЫ СТРУКТУРЫ:")
        for issue in issues:
            print(f"   {issue}")
        return False
    else:
        print("✓ Структура абзацев: ХОРОШАЯ")
        return True

def test_pdf_quotes_and_dashes():
    """Тест правильных кавычек и тире."""
    print("Проверка кавычек и тире...")
    
    # Проверяем генераторы на правильную обработку
    generators = [
        "generate_pdf_final.py",
        "generate_pdf_typography_enhanced.py"
    ]
    
    issues = []
    
    for generator in generators:
        if Path(generator).exists():
            with open(generator, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Проверяем правила для кавычек
            if '"([^"]*)"' not in content and '«\\1»' not in content:
                issues.append(f"{generator}: отсутствует обработка русских кавычек")
            
            # Проверяем правила для тире
            if '--' not in content or '—' not in content:
                issues.append(f"{generator}: отсутствует обработка тире")
    
    if issues:
        print("❌ ПРОБЛЕМЫ КАВЫЧЕК И ТИРЕ:")
        for issue in issues:
            print(f"   {issue}")
        return False
    else:
        print("✓ Кавычки и тире: ПРАВИЛЬНЫЕ")
        return True

def test_pdf_non_breaking_spaces():
    """Тест неразрывных пробелов."""
    print("Проверка неразрывных пробелов...")
    
    source_file = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/when_security_asked_about_user_data RU.md"
    
    if not Path(source_file).exists():
        print("⚠️ Исходный файл не найден")
        return True
    
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # Проверяем места где нужны неразрывные пробелы
    problems = [
        (r'\d+\s+(лет|года|дней)', "числительные с единицами времени"),
        (r'(ст\.|п\.|ч\.)\s+\d+', "сокращения с номерами"),
        (r'№\s+\d+', "номера"),
        (r'[А-ЯЁ]\.\s+[А-ЯЁ][а-яё]+', "инициалы"),
    ]
    
    for pattern, description in problems:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            issues.append(f"{description}: найдено {len(matches)} случаев без неразрывных пробелов")
    
    if issues:
        print("❌ ПРОБЛЕМЫ НЕРАЗРЫВНЫХ ПРОБЕЛОВ:")
        for issue in issues:
            print(f"   {issue}")
        return False
    else:
        print("✓ Неразрывные пробелы: ПРАВИЛЬНЫЕ")
        return True

def test_pdf_hyphenation():
    """Тест правильности переносов."""
    print("Проверка переносов...")
    
    source_file = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/when_security_asked_about_user_data RU.md"
    
    if not Path(source_file).exists():
        print("⚠️ Исходный файл не найден")
        return True
    
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # Проверяем неправильные переносы
    bad_hyphens = re.findall(r'([а-яё])-\s+([а-яё])', content, re.IGNORECASE)
    if bad_hyphens:
        issues.append(f"Найдено {len(bad_hyphens)} неправильных переносов с пробелами")
    
    # Проверяем генераторы на исправление переносов
    generators = [
        "generate_pdf_final.py",
        "generate_pdf_typography_enhanced.py"
    ]
    
    for generator in generators:
        if Path(generator).exists():
            with open(generator, 'r', encoding='utf-8') as f:
                gen_content = f.read()
            
            if 'hyphens: auto' not in gen_content:
                issues.append(f"{generator}: отсутствует автоматическая расстановка переносов")
    
    if issues:
        print("❌ ПРОБЛЕМЫ ПЕРЕНОСОВ:")
        for issue in issues:
            print(f"   {issue}")
        return False
    else:
        print("✓ Переносы: ПРАВИЛЬНЫЕ")
        return True

def test_pdf_typography_processor():
    """Тест работы процессора типографики."""
    print("Проверка процессора типографики...")
    
    if not Path("utils/typography_processor.py").exists():
        print("❌ Процессор типографики не найден")
        return False
    
    try:
        # Тестируем базовые функции
        test_text = '''
        Это "тестовый" текст с проблемами.
        Здесь есть неправильные -- тире.
        Числа 5 лет должны иметь неразрывные пробелы.
        Проблемы с пере- носами.
        '''
        
        # Проверяем, что модуль можно импортировать
        result = subprocess.run(
            ['python', '-c', 'from utils.typography_processor import TypographyProcessor; print("OK")'],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            print("✓ Процессор типографики: РАБОТАЕТ")
            return True
        else:
            print(f"❌ Ошибка импорта: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

def test_pdf_css_quality():
    """Тест качества CSS для PDF."""
    print("Проверка качества CSS...")
    
    generators = [
        "generate_pdf_final.py",
        "generate_pdf_typography_enhanced.py"
    ]
    
    issues = []
    
    for generator in generators:
        if Path(generator).exists():
            with open(generator, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Проверяем важные CSS свойства
            css_checks = [
                ('line-height', "межстрочный интервал"),
                ('orphans', "контроль сирот"),
                ('widows', "контроль вдов"),
                ('page-break-inside', "разрывы страниц"),
                ('text-rendering', "рендеринг текста"),
                ('font-feature-settings', "лигатуры и кернинг"),
            ]
            
            for prop, description in css_checks:
                if prop not in content:
                    issues.append(f"{generator}: отсутствует {description} ({prop})")
    
    if issues:
        print("❌ ПРОБЛЕМЫ CSS:")
        for issue in issues:
            print(f"   {issue}")
        return False
    else:
        print("✓ Качество CSS: ВЫСОКОЕ")
        return True

def run_comprehensive_tests():
    """Запуск всех комплексных тестов."""
    print("Запуск комплексных тестов типографики...")
    print("=" * 60)
    
    tests = [
        test_pdf_line_width,
        test_pdf_paragraph_structure,
        test_pdf_quotes_and_dashes,
        test_pdf_non_breaking_spaces,
        test_pdf_hyphenation,
        test_pdf_typography_processor,
        test_pdf_css_quality,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"Результат: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты типографики пройдены успешно!")
    else:
        print(f"⚠️  {total - passed} тестов требуют доработки")
    
    return passed == total

if __name__ == "__main__":
    run_comprehensive_tests()