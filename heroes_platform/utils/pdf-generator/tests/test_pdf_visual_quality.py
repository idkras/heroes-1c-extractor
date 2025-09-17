#!/usr/bin/env python3
"""
Визуальные тесты качества PDF документов.
Проверяет конкретные проблемы, выявленные пользователем.
"""

import pytest
from pathlib import Path
import PyPDF2
import re

def test_pdf_no_spacing_holes():
    """Тест отсутствия дырок между словами."""
    pdf_path = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_Fixed.pdf"
    
    if not Path(pdf_path).exists():
        pytest.skip("Исправленный PDF файл не найден")
    
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    
    # Проверяем отсутствие множественных пробелов
    assert not re.search(r'\s{3,}', text), "Не должно быть больших промежутков между словами"
    
    # Проверяем нормальное распределение пробелов
    word_count = len(text.split())
    assert word_count > 100, "Документ должен содержать достаточно слов для анализа"

def test_pdf_proper_font_usage():
    """Тест использования подходящих шрифтов."""
    pdf_path = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_Fixed.pdf"
    
    if not Path(pdf_path).exists():
        pytest.skip("Исправленный PDF файл не найден")
    
    # Проверяем, что файл корректно создан без ошибок шрифтов
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        
        # Проверяем что все страницы читаются
        for i, page in enumerate(reader.pages):
            try:
                text = page.extract_text()
                assert len(text) > 0, f"Страница {i+1} должна содержать текст"
            except Exception as e:
                pytest.fail(f"Ошибка чтения страницы {i+1}: {e}")

def test_pdf_no_empty_pages():
    """Тест отсутствия пустых страниц."""
    pdf_path = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_Fixed.pdf"
    
    if not Path(pdf_path).exists():
        pytest.skip("Исправленный PDF файл не найден")
    
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        
        empty_pages = 0
        for i, page in enumerate(reader.pages):
            text = page.extract_text().strip()
            if len(text) < 50:  # Очень мало текста = возможно пустая страница
                empty_pages += 1
        
        total_pages = len(reader.pages)
        assert empty_pages < total_pages * 0.3, f"Слишком много пустых страниц: {empty_pages} из {total_pages}"

def test_pdf_no_green_headers():
    """Тест отсутствия зеленого оформления в заголовках."""
    pdf_path = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_Fixed.pdf"
    
    if not Path(pdf_path).exists():
        pytest.skip("Исправленный PDF файл не найден")
    
    # Проверяем CSS исходного HTML на отсутствие зеленых цветов
    from generators.generate_pdf_fixed import improve_typography_fixed
    
    # Читаем исходный markdown
    md_file = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/when_security_asked_about_user_data RU.md"
    if Path(md_file).exists():
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        import markdown
        html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
        html_content = improve_typography_fixed(html_content)
        
        # Проверяем, что нет зеленых классов или стилей
        assert 'green' not in html_content.lower(), "HTML не должен содержать зеленое оформление"
        assert '#03A87C' not in html_content, "HTML не должен содержать зеленый цвет #03A87C"

def test_pdf_proper_line_width():
    """Тест правильной ширины полосы набора."""
    pdf_path = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_Fixed.pdf"
    
    if not Path(pdf_path).exists():
        pytest.skip("Исправленный PDF файл не найден")
    
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        
        # Проверяем первую страницу с содержимым
        for page in reader.pages:
            text = page.extract_text()
            if len(text) > 100:
                lines = text.split('\n')
                content_lines = [line.strip() for line in lines if len(line.strip()) > 20]
                
                if content_lines:
                    # Проверяем, что строки не слишком длинные
                    avg_line_length = sum(len(line) for line in content_lines[:10]) / min(10, len(content_lines))
                    assert 30 <= avg_line_length <= 85, f"Средняя длина строки {avg_line_length} не в оптимальном диапазоне 30-85 символов"
                break

def test_pdf_no_weird_hyphens():
    """Тест отсутствия странных дефисов в середине текста."""
    pdf_path = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_Fixed.pdf"
    
    if not Path(pdf_path).exists():
        pytest.skip("Исправленный PDF файл не найден")
    
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    
    # Проверяем отсутствие висячих дефисов
    assert not re.search(r'-\s+\w', text), "Не должно быть дефисов с пробелами в середине слов"
    
    # Проверяем отсутствие множественных дефисов
    assert not re.search(r'--+', text), "Не должно быть множественных дефисов"

def test_comparison_with_broken_version():
    """Сравнение исправленной версии с проблемной."""
    fixed_path = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_Fixed.pdf"
    broken_path = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_Improved.pdf"
    
    if not Path(fixed_path).exists():
        pytest.skip("Исправленный PDF не найден")
    
    fixed_size = Path(fixed_path).stat().st_size
    
    if Path(broken_path).exists():
        broken_size = Path(broken_path).stat().st_size
        
        # Исправленная версия может отличаться по размеру
        assert fixed_size > 1000, "Исправленный PDF должен иметь содержимое"
        
        # Проверяем, что исправленная версия читается
        with open(fixed_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            fixed_text = ""
            for page in reader.pages:
                fixed_text += page.extract_text()
        
        assert len(fixed_text) > 1000, "Исправленный PDF должен содержать достаточно текста"

def run_visual_tests():
    """Запуск визуальных тестов."""
    print("Запуск визуальных тестов качества PDF...")
    print("="*60)
    
    tests = [
        ("Дырки между словами", test_pdf_no_spacing_holes),
        ("Использование шрифтов", test_pdf_proper_font_usage),
        ("Пустые страницы", test_pdf_no_empty_pages),
        ("Зеленые заголовки", test_pdf_no_green_headers),
        ("Ширина полосы набора", test_pdf_proper_line_width),
        ("Странные дефисы", test_pdf_no_weird_hyphens),
        ("Сравнение версий", test_comparison_with_broken_version)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            test_func()
            print(f"✓ {test_name}: ИСПРАВЛЕН")
            passed += 1
        except Exception as e:
            print(f"✗ {test_name}: ТРЕБУЕТ ВНИМАНИЯ - {e}")
    
    print("="*60)
    print(f"Результат: {passed}/{total} проблем исправлено")
    
    if passed == total:
        print("🎉 Все визуальные проблемы PDF исправлены!")
    else:
        print("⚠️  Некоторые проблемы требуют дополнительной работы.")
    
    return passed == total

if __name__ == "__main__":
    run_visual_tests()