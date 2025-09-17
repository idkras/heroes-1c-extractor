"""
Простое тестирование PDF документа Rick.ai без браузера.
Проверяет качество через анализ содержимого и структуры.
"""

import PyPDF2
from pathlib import Path
import re

def comprehensive_pdf_analysis():
    """Комплексный анализ PDF документа."""
    
    pdf_path = "Rick_ai_Security_Documentation_FIXED.pdf"
    
    print("📄 Комплексный анализ PDF документа Rick.ai Security")
    print("=" * 60)
    
    if not Path(pdf_path).exists():
        print("❌ PDF файл не найден")
        return False
    
    # Извлекаем текст
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            full_text = ""
            for page in pdf_reader.pages:
                full_text += page.extract_text() + "\n"
    except Exception as e:
        print(f"❌ Ошибка при чтении PDF: {e}")
        return False
    
    # Базовые метрики
    word_count = len(full_text.split())
    char_count = len(full_text)
    file_size = Path(pdf_path).stat().st_size
    
    print(f"📊 Базовые метрики:")
    print(f"   📝 Слов: {word_count}")
    print(f"   📄 Символов: {char_count}")
    print(f"   💾 Размер файла: {file_size} байт ({file_size/1024:.1f} KB)")
    
    # Проверки качества
    quality_score = 100
    issues = []
    
    # 1. Проверка основных разделов
    print(f"\n🔍 Проверка структуры документа:")
    
    key_content = [
        ("Заголовок документа", "Информация о безопасности Rick.ai"),
        ("Основной принцип", "не хранит и не обрабатывает персональные данные"),
        ("ФЗ-152", "ФЗ-152"),
        ("Идентификаторы", "ym_clientID"),
        ("Хеширование", "SHA-256"),
        ("Архитектура", "Flow"),
        ("Таблицы", "Идентификатор")
    ]
    
    for name, content in key_content:
        if content in full_text:
            print(f"   ✅ {name}: найден")
        else:
            print(f"   ❌ {name}: отсутствует")
            issues.append(f"Отсутствует: {name}")
            quality_score -= 10
    
    # 2. Проверка типографических проблем
    print(f"\n🔤 Проверка типографии:")
    
    typography_checks = [
        ("Символы markdown", "##", "не должны присутствовать"),
        ("Некорректные пробелы", "ФЗ- 152", "должно быть ФЗ-152"),
        ("Читаемость", "персональные данные", "должно присутствовать"),
        ("Структура", "Rick.ai", "должно присутствовать")
    ]
    
    for name, pattern, description in typography_checks:
        if pattern == "##" or pattern == "ФЗ- 152":
            # Эти не должны присутствовать
            if pattern in full_text:
                print(f"   ❌ {name}: найдена проблема ({description})")
                issues.append(f"Типографическая ошибка: {name}")
                quality_score -= 15
            else:
                print(f"   ✅ {name}: без проблем")
        else:
            # Эти должны присутствовать
            if pattern in full_text:
                print(f"   ✅ {name}: корректно")
            else:
                print(f"   ❌ {name}: проблема ({description})")
                issues.append(f"Отсутствует: {name}")
                quality_score -= 10
    
    # 3. Проверка объема и полноты
    print(f"\n📏 Проверка объема:")
    
    if word_count >= 1500:
        print(f"   ✅ Достаточный объем: {word_count} слов")
    elif word_count >= 1000:
        print(f"   ⚠️ Средний объем: {word_count} слов")
        quality_score -= 5
    else:
        print(f"   ❌ Недостаточный объем: {word_count} слов")
        issues.append("Слишком короткий документ")
        quality_score -= 20
    
    # 4. Проверка технических аспектов
    print(f"\n⚙️ Технические аспекты:")
    
    if file_size > 30000:  # Больше 30KB
        print(f"   ✅ Нормальный размер файла")
    else:
        print(f"   ❌ Файл слишком мал")
        issues.append("Подозрительно малый размер файла")
        quality_score -= 15
    
    # Итоговая оценка
    print(f"\n" + "=" * 60)
    print(f"📊 ИТОГОВАЯ ОЦЕНКА: {quality_score}/100")
    
    if quality_score >= 90:
        status = "✅ ОТЛИЧНОЕ КАЧЕСТВО"
        recommendation = "Документ готов к использованию"
    elif quality_score >= 75:
        status = "⚠️ ХОРОШЕЕ КАЧЕСТВО"
        recommendation = "Есть незначительные замечания"
    elif quality_score >= 60:
        status = "❌ СРЕДНЕЕ КАЧЕСТВО"
        recommendation = "Требуются исправления"
    else:
        status = "❌ НИЗКОЕ КАЧЕСТВО"
        recommendation = "Необходима переработка"
    
    print(f"🎯 Статус: {status}")
    print(f"💡 Рекомендация: {recommendation}")
    
    if issues:
        print(f"\n🔧 Обнаруженные проблемы:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
    else:
        print(f"\n🎉 Проблем не обнаружено!")
    
    return quality_score >= 75

def main():
    """Запуск анализа."""
    success = comprehensive_pdf_analysis()
    
    if success:
        print(f"\n✅ PDF прошел проверку качества")
        print(f"📤 Можно отправлять службам безопасности")
    else:
        print(f"\n❌ PDF требует доработки")
        print(f"🔧 Исправьте найденные проблемы")

if __name__ == "__main__":
    main()