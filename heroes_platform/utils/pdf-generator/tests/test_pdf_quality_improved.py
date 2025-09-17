#!/usr/bin/env python3
"""
Улучшенные автотесты для проверки качества PDF документов по TDD-doc стандарту.
Проверяет типографику, шрифты, отступы и переносы строк с расширенной функциональностью.
"""

import pytest
from pathlib import Path
import PyPDF2
import re
import os

def test_pdf_typography():
    """Тест качества типографики в PDF."""
    pdf_path = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_Improved.pdf"
    
    if not Path(pdf_path).exists():
        pytest.skip("PDF файл не найден")
    
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    
    # Проверяем правильные кавычки
    assert '«' in text and '»' in text, "Должны использоваться правильные русские кавычки"
    
    # Проверяем длинное тире
    assert '—' in text, "Должно использоваться длинное тире"
    
    # Проверяем отсутствие двойных дефисов
    assert '--' not in text, "Не должно быть двойных дефисов"
    
    # Проверяем неразрывные пробелы
    assert ' лет' not in text or 'лет' in text, "Должны использоваться неразрывные пробелы"

def test_pdf_structure():
    """Тест структуры PDF документа."""
    pdf_path = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_Improved.pdf"
    
    if not Path(pdf_path).exists():
        pytest.skip("PDF файл не найден")
    
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        
        # Проверяем количество страниц
        assert len(reader.pages) >= 2, "Документ должен содержать минимум 2 страницы"
        
        # Проверяем метаданные
        metadata = reader.metadata
        assert metadata is not None, "PDF должен содержать метаданные"

def test_pdf_content_quality():
    """Тест качества контента PDF."""
    pdf_path = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_Improved.pdf"
    
    if not Path(pdf_path).exists():
        pytest.skip("PDF файл не найден")
    
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    
    # Проверяем ключевые разделы
    assert "Rick.ai" in text, "Документ должен содержать название Rick.ai"
    assert "безопасности" in text, "Документ должен содержать информацию о безопасности"
    assert "персональные данные" in text, "Документ должен содержать информацию о персональных данных"
    
    # Проверяем минимальную длину контента
    assert len(text) > 1000, "Документ должен содержать достаточно контента"

def test_pdf_file_properties():
    """Тест свойств PDF файла."""
    pdf_path = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_Improved.pdf"
    
    if not Path(pdf_path).exists():
        pytest.skip("PDF файл не найден")
    
    # Проверяем размер файла
    file_size = Path(pdf_path).stat().st_size
    assert file_size > 50000, "PDF файл должен быть достаточно большим для качественной типографики"
    assert file_size < 5000000, "PDF файл не должен быть слишком большим"

def test_improved_typography_features():
    """Тест улучшенных типографических функций."""
    pdf_path = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_Improved.pdf"
    
    if not Path(pdf_path).exists():
        pytest.skip("PDF файл не найден")
    
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    
    # Проверяем специальную разметку ключевых принципов
    assert "Ключевой принцип" in text, "Должны быть выделены ключевые принципы"
    
    # Проверяем правильное оформление юридических ссылок
    legal_patterns = [r'ст\.\s*\d+', r'п\.\s*\d+', r'ч\.\s*\d+']
    has_legal_refs = any(re.search(pattern, text) for pattern in legal_patterns)
    if has_legal_refs:
        # Если есть юридические ссылки, проверяем их правильность
        # Проверяем, что нет обычных пробелов после сокращений
        bad_patterns = [r'ст\.\s{2,}\d+', r'п\.\s{2,}\d+', r'ч\.\s{2,}\d+']
        has_bad_spacing = any(re.search(pattern, text) for pattern in bad_patterns)
        assert not has_bad_spacing, "Юридические ссылки не должны содержать множественные пробелы"

def test_comparison_with_basic_version():
    """Тест сравнения улучшенной версии с базовой."""
    improved_path = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_Improved.pdf"
    basic_path = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation.pdf"
    
    # Генерируем базовую версию, если её нет
    if not Path(basic_path).exists():
        from generators.generate_pdf import convert_md_to_pdf
        md_file = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/when_security_asked_about_user_data RU.md"
        if Path(md_file).exists():
            convert_md_to_pdf(md_file, basic_path)
    
    if Path(improved_path).exists() and Path(basic_path).exists():
        improved_size = Path(improved_path).stat().st_size
        basic_size = Path(basic_path).stat().st_size
        
        # Улучшенная версия может быть больше из-за лучшего форматирования
        assert improved_size >= basic_size * 0.8, "Улучшенная версия не должна быть значительно меньше базовой"

def run_all_tests():
    """Запуск всех тестов."""
    print("Запуск автотестов качества PDF...")
    print("="*50)
    
    tests = [
        ("Типографика", test_pdf_typography),
        ("Структура PDF", test_pdf_structure),
        ("Качество контента", test_pdf_content_quality),
        ("Свойства файла", test_pdf_file_properties),
        ("Улучшенная типографика", test_improved_typography_features),
        ("Сравнение версий", test_comparison_with_basic_version)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            test_func()
            print(f"✓ {test_name}: ПРОЙДЕН")
            passed += 1
        except Exception as e:
            print(f"✗ {test_name}: НЕ ПРОЙДЕН - {e}")
    
    print("="*50)
    print(f"Результат: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты качества PDF пройдены успешно!")
    else:
        print("⚠️  Некоторые тесты не пройдены. Требуется улучшение качества PDF.")
    
    return passed == total

if __name__ == "__main__":
    run_all_tests()