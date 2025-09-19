"""
Анализ содержимого финального PDF без браузера.
Проверяет качество документа через извлечение текста.
"""

from pathlib import Path

import PyPDF2


def extract_pdf_text(pdf_path):
    """Извлекает текст из PDF для анализа."""
    try:
        with open(pdf_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        print(f"Ошибка при извлечении текста из PDF: {e}")
        return ""


def analyze_final_pdf_quality(pdf_text):
    """Анализирует качество финального PDF."""

    issues = []
    quality_score = 100

    # Проверка 1: Отсутствие символов markdown
    if "##" in pdf_text:
        issues.append("❌ Найдены нераспознанные символы markdown (##)")
        quality_score -= 25
    else:
        print("✅ Символы markdown корректно обработаны")

    # Проверка 2: Правильное отображение ФЗ-152
    if "ФЗ- 152" in pdf_text:
        issues.append("❌ Найден некорректный пробел в 'ФЗ- 152'")
        quality_score -= 15
    elif "ФЗ-152" in pdf_text:
        print("✅ ФЗ-152 отображается корректно")

    # Проверка 3: Структура заголовков
    if "Информация о безопасности Rick.ai" in pdf_text:
        print("✅ Главный заголовок присутствует")
    else:
        issues.append("❌ Главный заголовок не найден")
        quality_score -= 20

    # Проверка 4: Ключевые разделы
    required_sections = [
        "Ключевые принципы работы:",
        "Примеры используемых обезличенных идентификаторов",
        "Принципы чтения, обработки, передачи и хранения данных",
        "Архитектура безопасности данных",
    ]

    for section in required_sections:
        if section in pdf_text:
            print(f"✅ Раздел найден: {section}")
        else:
            issues.append(f"❌ Отсутствует раздел: {section}")
            quality_score -= 10

    # Проверка 5: Таблицы
    if "ym_clientID" in pdf_text and "ga_clientID" in pdf_text:
        print("✅ Таблица идентификаторов присутствует")
    else:
        issues.append("❌ Таблица идентификаторов повреждена")
        quality_score -= 15

    # Проверка 6: Длина контента
    word_count = len(pdf_text.split())
    if word_count > 800:
        print(f"✅ Достаточный объем контента: {word_count} слов")
    else:
        issues.append(f"❌ Недостаточный объем контента: {word_count} слов")
        quality_score -= 20

    # Проверка 7: Кодировка и читаемость
    if "Rick.ai" in pdf_text and "персональные данные" in pdf_text:
        print("✅ Кодировка и читаемость текста корректны")
    else:
        issues.append("❌ Проблемы с кодировкой или извлечением текста")
        quality_score -= 25

    return issues, quality_score


def main():
    """Основная функция анализа PDF."""

    pdf_path = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_FINAL.pdf"

    print("📄 Анализ финального PDF документа Rick.ai")
    print("=" * 50)

    if not Path(pdf_path).exists():
        print(f"❌ PDF файл не найден: {pdf_path}")
        return

    # Извлекаем текст
    print("🔍 Извлечение текста из PDF...")
    pdf_text = extract_pdf_text(pdf_path)

    if not pdf_text:
        print("❌ Не удалось извлечь текст из PDF")
        return

    # Анализируем качество
    print("\n📋 Проверка качества документа:")
    issues, quality_score = analyze_final_pdf_quality(pdf_text)

    # Итоговый отчет
    print("\n" + "=" * 50)
    print("📊 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print(f"🎯 Оценка качества: {quality_score}/100")

    if quality_score >= 90:
        print("✅ ОТЛИЧНОЕ КАЧЕСТВО - документ готов к использованию")
        print("📤 Можно отправлять службам безопасности клиентов")
    elif quality_score >= 75:
        print("⚠️ ХОРОШЕЕ КАЧЕСТВО - есть незначительные замечания")
        print("🔧 Рекомендуется устранить мелкие недочеты")
    elif quality_score >= 50:
        print("❌ СРЕДНЕЕ КАЧЕСТВО - требуются исправления")
        print("🛠️ Необходима доработка перед использованием")
    else:
        print("❌ НИЗКОЕ КАЧЕСТВО - серьезные проблемы")
        print("🚨 Требуется полная переработка документа")

    if issues:
        print("\n🔧 Обнаруженные проблемы:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n🎉 Проблем не обнаружено!")

    print(f"\n📝 Размер документа: {len(pdf_text.split())} слов")
    print(f"📄 Количество символов: {len(pdf_text)}")


if __name__ == "__main__":
    main()
