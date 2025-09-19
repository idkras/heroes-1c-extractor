#!/usr/bin/env python3
"""
Тестирование современного PDF генератора
Создает PDF из vipavenue-adjust-appmetrica.md для проверки качества
"""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к генераторам
sys.path.insert(0, str(Path(__file__).parent / "generators"))


def test_modern_generator():
    """Тестирует современный генератор на реальном файле"""

    # Путь к исходному markdown файлу
    md_file = Path(
        "../../heroes-template/[rick.ai]/clients/vipavenue.ru/vipavenue-adjust-appmetrica.md"
    )

    if not md_file.exists():
        print(f"❌ Файл не найден: {md_file}")
        print("Убедитесь, что вы находитесь в корневой папке проекта")
        return False

    # Путь для выходного PDF
    output_pdf = Path("vipavenue-adjust-appmetrica_MODERN.pdf")

    print(f"📖 Читаю файл: {md_file}")
    print(f"📄 Создаю PDF: {output_pdf}")

    try:
        # Импортируем современный генератор
        from generators.pdf_generator_modern import convert_md_to_pdf_modern_sync

        # Создаем PDF
        print("🔄 Генерирую PDF с современной типографикой...")
        result = convert_md_to_pdf_modern_sync(str(md_file), str(output_pdf))

        if result["success"]:
            print(f"✅ PDF успешно создан: {output_pdf}")
            print(f"📊 Размер файла: {output_pdf.stat().st_size / 1024:.1f} KB")
            print(f"💬 Сообщение: {result['message']}")

            # Проверяем качество
            check_pdf_quality(output_pdf)

            return True
        else:
            print(f"❌ Ошибка создания PDF: {result['error']}")
            return False

    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Установите зависимости: pip install -r requirements_modern.txt")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False


def check_pdf_quality(pdf_path: Path):
    """Проверяет качество созданного PDF"""

    print("\n🔍 Проверка качества PDF:")

    # Проверяем размер файла
    size_kb = pdf_path.stat().st_size / 1024
    if size_kb > 100:
        print(f"✅ Размер файла: {size_kb:.1f} KB (нормально)")
    else:
        print(f"⚠️ Размер файла: {size_kb:.1f} KB (возможно слишком маленький)")

    # Проверяем, что файл не пустой
    if size_kb > 1:
        print("✅ Файл не пустой")
    else:
        print("❌ Файл слишком маленький")

    # Проверяем расширение
    if pdf_path.suffix.lower() == ".pdf":
        print("✅ Правильное расширение .pdf")
    else:
        print("❌ Неправильное расширение файла")

    print("\n📋 Рекомендации:")
    print("- Откройте PDF в браузере для проверки отображения")
    print("- Проверьте качество таблиц и details блоков")
    print("- Убедитесь, что русский текст читаем")


async def test_async_generator():
    """Тестирует асинхронную версию генератора"""

    md_file = Path(
        "../../heroes-template/[rick.ai]/clients/vipavenue.ru/vipavenue-adjust-appmetrica.md"
    )
    output_pdf = Path("vipavenue-adjust-appmetrica_MODERN_ASYNC.pdf")

    if not md_file.exists():
        print(f"❌ Файл не найден: {md_file}")
        return False

    try:
        from generators.pdf_generator_modern import convert_md_to_pdf_modern

        print("🔄 Тестирую асинхронный генератор...")
        result = await convert_md_to_pdf_modern(str(md_file), str(output_pdf))

        if result["success"]:
            print(f"✅ Асинхронный PDF создан: {output_pdf}")
            return True
        else:
            print(f"❌ Ошибка асинхронного генератора: {result['error']}")
            return False

    except Exception as e:
        print(f"❌ Ошибка асинхронного генератора: {e}")
        return False


def main():
    """Главная функция"""

    print("🚀 Тестирование современного PDF генератора")
    print("=" * 50)

    # Тестируем синхронную версию
    print("\n📋 Тест 1: Синхронный генератор")
    sync_success = test_modern_generator()

    # Тестируем асинхронную версию
    print("\n📋 Тест 2: Асинхронный генератор")
    try:
        async_success = asyncio.run(test_async_generator())
    except Exception as e:
        print(f"❌ Асинхронный тест не прошел: {e}")
        async_success = False

    # Итоговый результат
    print("\n" + "=" * 50)
    print("📊 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print(f"Синхронный генератор: {'✅' if sync_success else '❌'}")
    print(f"Асинхронный генератор: {'✅' if async_success else '❌'}")

    if sync_success or async_success:
        print("\n🎉 Тестирование завершено успешно!")
        print("📁 Проверьте созданные PDF файлы:")

        pdf_files = list(Path(".").glob("vipavenue-adjust-appmetrica_MODERN*.pdf"))
        for pdf_file in pdf_files:
            if pdf_file.exists():
                size_kb = pdf_file.stat().st_size / 1024
                print(f"   - {pdf_file.name} ({size_kb:.1f} KB)")
    else:
        print("\n❌ Все тесты провалились")
        print("🔧 Проверьте установку зависимостей и настройки")


if __name__ == "__main__":
    main()
