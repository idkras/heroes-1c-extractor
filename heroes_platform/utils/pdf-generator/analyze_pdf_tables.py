#!/usr/bin/env python3
"""
Анализ таблиц в PDF файлах
Проверяет качество отображения таблиц в разных генераторах
"""

import PyPDF2
import re
from pathlib import Path

def extract_text_from_pdf(pdf_path):
    """Извлекает текст из PDF"""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text() + '\n'
            return text
    except Exception as e:
        return f'Ошибка: {e}'

def analyze_tables_in_text(text):
    """Анализирует таблицы в тексте"""
    
    # Ищем паттерны таблиц
    table_patterns = [
        r'№.*AppMetrica.*Adjust',  # Заголовки таблицы
        r'\|.*\|.*\|',  # Строки с разделителями
        r'-------',  # Разделители столбцов
        r'1\s+received adjust attribution',  # Первая строка данных
        r'2\s+system adjust_id',  # Вторая строка данных
    ]
    
    found_tables = []
    
    for pattern in table_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        if matches:
            found_tables.extend(matches)
    
    # Ищем структурированные данные
    structured_data = []
    
    # Ищем строки с номерами и описаниями
    lines = text.split('\n')
    for line in lines:
        if re.match(r'^\d+\.?\s+', line.strip()):
            structured_data.append(line.strip())
    
    return {
        'table_patterns_found': len(found_tables),
        'structured_data_lines': len(structured_data),
        'sample_structured_data': structured_data[:5],
        'table_patterns': found_tables[:3]
    }

def compare_pdf_tables():
    """Сравнивает качество таблиц в разных PDF"""
    
    print("🔍 АНАЛИЗ ТАБЛИЦ В PDF ФАЙЛАХ")
    print("=" * 60)
    
    pdf_files = [
        'vipavenue-adjust-appmetrica_MODERN.pdf',
        'vipavenue-adjust-appmetrica_NODEJS.pdf',
        'vipavenue-adjust-appmetrica_NODEJS_ADVANCED.pdf'
    ]
    
    results = {}
    
    for pdf_file in pdf_files:
        if not Path(pdf_file).exists():
            print(f"❌ Файл {pdf_file} не найден")
            continue
            
        print(f"\n📄 Анализ таблиц в: {pdf_file}")
        
        # Извлекаем текст
        text = extract_text_from_pdf(pdf_file)
        
        if text.startswith('Ошибка:'):
            print(f"   ❌ {text}")
            continue
        
        # Анализируем таблицы
        table_analysis = analyze_tables_in_text(text)
        
        print(f"   📊 Найдено паттернов таблиц: {table_analysis['table_patterns_found']}")
        print(f"   📋 Строк структурированных данных: {table_analysis['structured_data_lines']}")
        
        # Показываем примеры
        if table_analysis['sample_structured_data']:
            print(f"   📝 Примеры структурированных данных:")
            for i, data in enumerate(table_analysis['sample_structured_data'][:3]):
                print(f"      {i+1}. {data[:80]}...")
        
        # Оценка качества таблиц
        quality_score = 0
        if table_analysis['table_patterns_found'] > 0:
            quality_score += 3
        if table_analysis['structured_data_lines'] > 10:
            quality_score += 4
        if table_analysis['structured_data_lines'] > 20:
            quality_score += 3
        
        quality_text = "❌ Плохо" if quality_score < 3 else "⚠️ Средне" if quality_score < 6 else "✅ Хорошо" if quality_score < 8 else "🌟 Отлично"
        
        print(f"   🎯 Качество таблиц: {quality_text} ({quality_score}/10)")
        
        results[pdf_file] = {
            'text_length': len(text),
            'table_analysis': table_analysis,
            'quality_score': quality_score
        }
    
    return results

def analyze_details_blocks(text):
    """Анализирует details блоки в тексте"""
    
    # Ищем паттерны details блоков
    details_patterns = [
        r'QUICK START.*5 минут',  # Заголовок details
        r'Flutter.*main\.dart',  # Flutter секция
        r'iOS.*AppDelegate\.swift',  # iOS секция
        r'Android.*MainActivity\.kt',  # Android секция
    ]
    
    found_details = []
    
    for pattern in details_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        if matches:
            found_details.extend(matches)
    
    return {
        'details_patterns_found': len(found_details),
        'details_content': found_details[:3]
    }

def analyze_code_blocks(text):
    """Анализирует блоки кода в тексте"""
    
    # Ищем паттерны кода
    code_patterns = [
        r'```dart',  # Dart код
        r'```swift',  # Swift код
        r'```kotlin',  # Kotlin код
        r'```java',  # Java код
        r'```xml',  # XML код
    ]
    
    found_code = []
    
    for pattern in code_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        if matches:
            found_code.extend(matches)
    
    return {
        'code_blocks_found': len(found_code),
        'code_types': list(set(found_code))
    }

def comprehensive_analysis():
    """Комплексный анализ всех аспектов"""
    
    print("\n🔍 КОМПЛЕКСНЫЙ АНАЛИЗ PDF КАЧЕСТВА")
    print("=" * 60)
    
    pdf_files = [
        'vipavenue-adjust-appmetrica_MODERN.pdf',
        'vipavenue-adjust-appmetrica_NODEJS.pdf',
        'vipavenue-adjust-appmetrica_NODEJS_ADVANCED.pdf'
    ]
    
    comprehensive_results = {}
    
    for pdf_file in pdf_files:
        if not Path(pdf_file).exists():
            continue
            
        print(f"\n📄 Комплексный анализ: {pdf_file}")
        
        # Извлекаем текст
        text = extract_text_from_pdf(pdf_file)
        
        if text.startswith('Ошибка:'):
            continue
        
        # Анализируем все аспекты
        table_analysis = analyze_tables_in_text(text)
        details_analysis = analyze_details_blocks(text)
        code_analysis = analyze_code_blocks(text)
        
        # Общая оценка
        total_score = 0
        
        # Оценка таблиц (0-10)
        table_score = min(10, table_analysis['table_patterns_found'] * 2 + table_analysis['structured_data_lines'])
        total_score += table_score
        
        # Оценка details блоков (0-5)
        details_score = min(5, details_analysis['details_patterns_found'] * 2)
        total_score += details_score
        
        # Оценка блоков кода (0-5)
        code_score = min(5, code_analysis['code_blocks_found'] * 2)
        total_score += code_score
        
        print(f"   📊 Таблицы: {table_score}/10")
        print(f"   📋 Details блоки: {details_score}/5")
        print(f"   💻 Блоки кода: {code_score}/5")
        print(f"   🎯 Общая оценка: {total_score}/20")
        
        comprehensive_results[pdf_file] = {
            'table_score': table_score,
            'details_score': details_score,
            'code_score': code_score,
            'total_score': total_score,
            'text_length': len(text)
        }
    
    return comprehensive_results

def main():
    """Главная функция"""
    
    print("🚀 АНАЛИЗ КАЧЕСТВА ТАБЛИЦ И СТРУКТУРЫ В PDF")
    print("=" * 60)
    
    # Анализ таблиц
    table_results = compare_pdf_tables()
    
    # Комплексный анализ
    comprehensive_results = comprehensive_analysis()
    
    # Итоговый отчет
    print(f"\n📋 ИТОГОВЫЙ ОТЧЕТ ПО КАЧЕСТВУ")
    print("=" * 60)
    
    if comprehensive_results:
        best_file = max(comprehensive_results.items(), key=lambda x: x[1]['total_score'])
        print(f"🏆 Лучший результат:")
        print(f"   📄 Файл: {best_file[0]}")
        print(f"   🎯 Общая оценка: {best_file[1]['total_score']}/20")
        print(f"   📊 Таблицы: {best_file[1]['table_score']}/10")
        print(f"   📋 Details: {best_file[1]['details_score']}/5")
        print(f"   💻 Код: {best_file[1]['code_score']}/5")
    
    print(f"\n💡 РЕКОМЕНДАЦИИ:")
    print("   - Проверьте PDF файлы вручную для финальной оценки")
    print("   - Обратите внимание на качество таблиц и details блоков")
    print("   - Сравните читаемость кода в разных генераторах")

if __name__ == "__main__":
    main()
