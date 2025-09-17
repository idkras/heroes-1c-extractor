#!/usr/bin/env python3
"""
Анализ содержимого PDF без браузера - проверка как документ выглядит для пользователя.
Использует текстовое извлечение для проверки реальных проблем верстки.
"""

import subprocess
from pathlib import Path
import re
import json

def extract_pdf_text(pdf_path):
    """Извлекает текст из PDF для анализа."""
    try:
        # Используем pdftotext если доступен
        result = subprocess.run(
            ['pdftotext', '-layout', pdf_path, '-'],
            capture_output=True, text=True, encoding='utf-8'
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"pdftotext недоступен, используем альтернативный метод")
            return None
            
    except FileNotFoundError:
        print("pdftotext не установлен")
        return None

def analyze_pdf_visual_issues(pdf_text):
    """Анализирует реальные визуальные проблемы в PDF тексте."""
    
    issues = []
    passed_checks = []
    
    if not pdf_text:
        return {"error": "Не удалось извлечь текст из PDF"}
    
    # Проверка 1: Символы markdown остались в тексте
    if '##' in pdf_text:
        issues.append("КРИТИЧЕСКАЯ ПРОБЛЕМА: Символы ## найдены в тексте вместо заголовков")
    else:
        passed_checks.append("Markdown символы правильно конвертированы")
    
    # Проверка 2: Кавычки
    straight_quotes = pdf_text.count('"')
    russian_quotes = pdf_text.count('«') + pdf_text.count('»')
    
    if straight_quotes > 5:  # Допускаем несколько для кода
        issues.append(f"Найдено {straight_quotes} прямых кавычек, должны быть русские")
    else:
        passed_checks.append("Кавычки правильные")
    
    # Проверка 3: Проблемные переносы
    problematic_patterns = [
        (r'ФЗ-\s+152', 'ФЗ-152 разорван переносом'),
        (r'\d+\s+лет\b', 'числа с "лет" могут разрываться'),
        (r'\d+\s+года\b', 'числа с "года" могут разрываться'),
        (r'ст\.\s+\d+', 'сокращения "ст." разрываются с номерами')
    ]
    
    for pattern, description in problematic_patterns:
        if re.search(pattern, pdf_text):
            issues.append(f"Проблема переносов: {description}")
    
    if not any(re.search(pattern, pdf_text) for pattern, _ in problematic_patterns):
        passed_checks.append("Переносы в порядке")
    
    # Проверка 4: Структура документа
    lines = [line.strip() for line in pdf_text.split('\n') if line.strip()]
    
    if len(lines) < 20:
        issues.append("КРИТИЧЕСКАЯ ПРОБЛЕМА: Слишком мало строк - документ может быть слит")
    else:
        passed_checks.append("Документ имеет нормальную структуру")
    
    # Проверка 5: Наличие заголовков
    has_title = any('Rick.ai' in line and 'безопасности' in line for line in lines[:5])
    if not has_title:
        issues.append("Заголовок документа не найден в начале")
    else:
        passed_checks.append("Заголовок документа присутствует")
    
    # Проверка 6: Тире вместо дефисов
    dash_count = pdf_text.count('—')
    text_dashes = len(re.findall(r'\s-\s', pdf_text))
    
    if text_dashes > dash_count / 3:
        issues.append(f"Много дефисов ({text_dashes}) вместо тире ({dash_count})")
    else:
        passed_checks.append("Тире используются правильно")
    
    return {
        "issues": issues,
        "passed_checks": passed_checks,
        "total_lines": len(lines),
        "text_sample": pdf_text[:500] + "..." if len(pdf_text) > 500 else pdf_text
    }

def test_pdf_visual_content(pdf_path):
    """Основная функция тестирования PDF контента."""
    
    print(f"Анализ PDF документа: {pdf_path}")
    print("=" * 60)
    
    if not Path(pdf_path).exists():
        print(f"❌ PDF файл не найден: {pdf_path}")
        return False
    
    # Размер файла
    file_size = Path(pdf_path).stat().st_size
    print(f"📄 Размер файла: {file_size:,} bytes")
    
    # Извлекаем текст
    pdf_text = extract_pdf_text(pdf_path)
    
    if pdf_text:
        # Анализируем проблемы
        results = analyze_pdf_visual_issues(pdf_text)
        
        print("\n✅ ПРОЙДЕННЫЕ ПРОВЕРКИ:")
        for check in results["passed_checks"]:
            print(f"   {check}")
        
        if results["issues"]:
            print(f"\n❌ ОБНАРУЖЕННЫЕ ПРОБЛЕМЫ ({len(results['issues'])}):")
            for issue in results["issues"]:
                print(f"   {issue}")
        
        print(f"\n📊 СТАТИСТИКА:")
        print(f"   Строк в документе: {results['total_lines']}")
        print(f"   Длина текста: {len(pdf_text):,} символов")
        
        # Сохраняем отчет
        report_file = pdf_path.replace('.pdf', '_content_analysis.json')
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "pdf_file": pdf_path,
                "file_size": file_size,
                "analysis": results,
                "text_length": len(pdf_text)
            }, f, ensure_ascii=False, indent=2)
        
        print(f"📁 Отчет сохранен: {report_file}")
        
        return len(results["issues"]) == 0
    else:
        print("❌ Не удалось извлечь текст из PDF для анализа")
        return False

def main():
    """Запуск анализа."""
    pdf_path = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_Emergency_Fix.pdf"
    test_pdf_visual_content(pdf_path)

if __name__ == "__main__":
    main()