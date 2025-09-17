#!/usr/bin/env python3
"""
Критические тесты PDF - проверка реальных проблем из скриншота.
"""

from pathlib import Path
import re

def test_markdown_processing():
    """Проверка что markdown правильно конвертируется в HTML."""
    
    # Проверяем исходный файл
    source_file = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/when_security_asked_about_user_data RU_fixed.md"
    
    if not Path(source_file).exists():
        print("❌ Исходный файл не найден")
        return False
    
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # Проверяем наличие заголовков markdown
    if '##' not in content:
        issues.append("Отсутствуют заголовки второго уровня ##")
    
    # Проверяем что заголовки правильно оформлены
    h2_headers = re.findall(r'^## (.+)$', content, re.MULTILINE)
    if len(h2_headers) < 3:
        issues.append(f"Недостаточно заголовков H2: найдено {len(h2_headers)}")
    
    if issues:
        print("❌ ПРОБЛЕМЫ MARKDOWN:")
        for issue in issues:
            print(f"   {issue}")
        return False
    else:
        print("✓ Markdown структура правильная")
        return True

def test_html_generation():
    """Проверка что HTML генерируется без ошибок."""
    
    try:
        import markdown
        
        # Тестируем конверсию markdown
        test_md = """
# Заголовок 1
## Заголовок 2
Обычный текст с "кавычками".
        """
        
        html = markdown.markdown(test_md, extensions=['tables', 'fenced_code'])
        
        # Проверяем что заголовки конвертируются
        if '<h1>' not in html or '<h2>' not in html:
            print("❌ Заголовки не конвертируются в HTML")
            return False
        
        print("✓ HTML генерация работает")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка генерации HTML: {e}")
        return False

def test_css_width_settings():
    """Проверка CSS настроек ширины."""
    
    generator_file = "generate_pdf_comprehensive_fix.py"
    
    with open(generator_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # Проверяем max-width
    if 'max-width: 165mm' not in content:
        issues.append("Неправильная ширина полосы набора")
    
    # Проверяем что нет слишком узких настроек
    if 'max-width: 140mm' in content or 'max-width: 120mm' in content:
        issues.append("Слишком узкая ширина колонки")
    
    if issues:
        print("❌ ПРОБЛЕМЫ CSS ШИРИНЫ:")
        for issue in issues:
            print(f"   {issue}")
        return False
    else:
        print("✓ CSS ширина настроена правильно")
        return True

def test_typography_processing():
    """Проверка обработки типографики."""
    
    generator_file = "generate_pdf_comprehensive_fix.py"
    
    with open(generator_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # Проверяем правила кавычек
    if '«\\1»' not in content:
        issues.append("Отсутствует замена кавычек на русские")
    
    # Проверяем правила тире
    if '—' not in content:
        issues.append("Отсутствует замена на длинное тире")
    
    # Проверяем неразрывные пробелы
    if '\\u00A0' not in content:
        issues.append("Отсутствуют неразрывные пробелы")
    
    if issues:
        print("❌ ПРОБЛЕМЫ ТИПОГРАФИКИ:")
        for issue in issues:
            print(f"   {issue}")
        return False
    else:
        print("✓ Типографика обрабатывается")
        return True

def test_structure_preservation():
    """Проверка сохранения структуры документа."""
    
    source_file = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/when_security_asked_about_user_data RU_fixed.md"
    
    if not Path(source_file).exists():
        return False
    
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем структурные элементы
    structure_elements = [
        ('# ', 'заголовок H1'),
        ('## ', 'заголовки H2'),
        ('| ', 'таблицы'),
        ('• ', 'списки'),
        ('**', 'выделения')
    ]
    
    issues = []
    for element, description in structure_elements:
        if element not in content:
            issues.append(f"Отсутствуют {description}")
    
    if issues:
        print("❌ ПРОБЛЕМЫ СТРУКТУРЫ:")
        for issue in issues:
            print(f"   {issue}")
        return False
    else:
        print("✓ Структура документа сохранена")
        return True

def run_critical_tests():
    """Запуск критических тестов."""
    print("Проверка критических проблем PDF...")
    print("=" * 50)
    
    tests = [
        test_markdown_processing,
        test_html_generation,
        test_css_width_settings,
        test_typography_processing,
        test_structure_preservation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Критические тесты: {passed}/{total}")
    
    if passed < total:
        print("🚨 ОБНАРУЖЕНЫ КРИТИЧЕСКИЕ ПРОБЛЕМЫ")
        print("Требуется срочное исправление генератора PDF!")
    else:
        print("✓ Критические тесты пройдены")

if __name__ == "__main__":
    run_critical_tests()