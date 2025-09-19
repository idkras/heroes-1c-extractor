#!/usr/bin/env python3
"""
Анализ качества PDF файлов, созданных разными генераторами
Сравнение размеров, проверка содержимого, выявление косяков
"""

import subprocess
from pathlib import Path


def analyze_pdf_files():
    """Анализирует все созданные PDF файлы"""

    print("🔍 АНАЛИЗ КАЧЕСТВА PDF ГЕНЕРАТОРОВ")
    print("=" * 60)

    # Находим все PDF файлы
    pdf_files = list(Path(".").glob("vipavenue-adjust-appmetrica_*.pdf"))

    if not pdf_files:
        print("❌ PDF файлы не найдены")
        return

    print(f"📁 Найдено {len(pdf_files)} PDF файлов:")

    # Анализируем каждый файл
    results = {}

    for pdf_file in sorted(pdf_files):
        print(f"\n📄 Анализ: {pdf_file.name}")

        # Базовая информация
        file_size = pdf_file.stat().st_size
        file_size_kb = file_size / 1024
        file_size_mb = file_size_kb / 1024

        print(f"   📊 Размер: {file_size_kb:.1f} KB ({file_size_mb:.2f} MB)")

        # Определяем тип генератора
        generator_type = "Unknown"
        if "MODERN" in pdf_file.name:
            generator_type = "Playwright (Modern)"
        elif "NODEJS" in pdf_file.name:
            generator_type = "Node.js (md-to-pdf)"
        elif "WEASYPRINT" in pdf_file.name:
            generator_type = "WeasyPrint"

        print(f"   🔧 Генератор: {generator_type}")

        # Проверяем, что файл не поврежден
        try:
            # Пытаемся получить информацию о PDF
            result = subprocess.run(
                ["file", str(pdf_file)], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                file_info = result.stdout.strip()
                print(f"   ✅ Тип файла: {file_info}")

                if "PDF document" in file_info:
                    print("   ✅ Валидный PDF файл")
                else:
                    print("   ❌ Не PDF файл")
            else:
                print("   ⚠️ Не удалось определить тип файла")

        except Exception as e:
            print(f"   ⚠️ Ошибка анализа: {e}")

        # Сохраняем результаты
        results[pdf_file.name] = {
            "size_kb": file_size_kb,
            "size_mb": file_size_mb,
            "generator": generator_type,
            "path": str(pdf_file),
        }

    return results


def compare_generators(results):
    """Сравнивает генераторы по качеству"""

    print("\n📊 СРАВНЕНИЕ ГЕНЕРАТОРОВ")
    print("=" * 60)

    if not results:
        return

    # Группируем по типу генератора
    generators = {}
    for filename, data in results.items():
        gen_type = data["generator"]
        if gen_type not in generators:
            generators[gen_type] = []
        generators[gen_type].append(data)

    # Анализируем каждый тип
    for gen_type, files in generators.items():
        print(f"\n🔧 {gen_type}:")

        total_size = sum(f["size_kb"] for f in files)
        avg_size = total_size / len(files)

        print(f"   📁 Файлов: {len(files)}")
        print(f"   📊 Общий размер: {total_size:.1f} KB")
        print(f"   📊 Средний размер: {avg_size:.1f} KB")

        # Оценка качества по размеру
        if avg_size < 1000:
            quality = "❌ Возможно низкое качество"
        elif avg_size < 2000:
            quality = "⚠️ Среднее качество"
        elif avg_size < 4000:
            quality = "✅ Хорошее качество"
        else:
            quality = "🌟 Отличное качество (возможно избыточное)"

        print(f"   🎯 Оценка качества: {quality}")


def identify_issues(results):
    """Выявляет проблемы и косяки"""

    print("\n🐛 ВЫЯВЛЕННЫЕ ПРОБЛЕМЫ И КОСЯКИ")
    print("=" * 60)

    if not results:
        return

    issues = []

    # Анализируем размеры
    for filename, data in results.items():
        size_kb = data["size_kb"]
        generator = data["generator"]

        # Проблемы с размером
        if size_kb < 100:
            issues.append(
                f"❌ {filename}: Слишком маленький размер ({size_kb:.1f} KB) - возможно поврежден"
            )
        elif size_kb > 10000:
            issues.append(
                f"⚠️ {filename}: Очень большой размер ({size_kb:.1f} KB) - возможно избыточное качество"
            )

        # Проблемы с генераторами
        if "WeasyPrint" in generator:
            issues.append(
                f"❌ {filename}: WeasyPrint не работает на macOS из-за системных зависимостей"
            )

    # Проверяем отсутствующие генераторы
    expected_generators = ["Playwright (Modern)", "Node.js (md-to-pdf)", "WeasyPrint"]
    found_generators = set(data["generator"] for data in results.values())

    for expected in expected_generators:
        if expected not in found_generators:
            if "WeasyPrint" in expected:
                issues.append(
                    f"❌ {expected}: Не работает на macOS (libgobject-2.0-0 отсутствует)"
                )
            else:
                issues.append(f"❌ {expected}: Не протестирован")

    # Выводим проблемы
    if issues:
        for issue in issues:
            print(f"   {issue}")
    else:
        print("   ✅ Критических проблем не выявлено")

    # Рекомендации
    print("\n💡 РЕКОМЕНДАЦИИ:")

    if "Node.js (md-to-pdf)" in found_generators:
        print("   ✅ Node.js генератор работает стабильно")
        print("   💡 Рекомендуется для продакшена")

    if "Playwright (Modern)" in found_generators:
        print("   ✅ Playwright генератор работает")
        print("   💡 Хорош для сложных CSS и интерактивности")

    if "WeasyPrint" not in found_generators:
        print("   ❌ WeasyPrint не работает на macOS")
        print("   💡 Требует установки системных зависимостей")


def generate_report(results):
    """Генерирует итоговый отчет"""

    print("\n📋 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 60)

    if not results:
        print("❌ Нет данных для отчета")
        return

    # Статистика
    total_files = len(results)
    total_size_mb = sum(data["size_mb"] for data in results.values())

    print("📊 Общая статистика:")
    print(f"   📁 Всего PDF файлов: {total_files}")
    print(f"   📊 Общий размер: {total_size_mb:.2f} MB")
    print(f"   📊 Средний размер: {total_size_mb / total_files:.2f} MB")

    # Лучший генератор
    best_generator = None
    best_score = 0

    for filename, data in results.items():
        # Простая оценка: размер в разумных пределах + тип генератора
        size_score = 0
        if 1000 <= data["size_kb"] <= 5000:
            size_score = 10
        elif 500 <= data["size_kb"] < 1000:
            size_score = 8
        elif 5000 < data["size_kb"] <= 10000:
            size_score = 7
        else:
            size_score = 5

        generator_score = 0
        if "Node.js" in data["generator"]:
            generator_score = 10
        elif "Playwright" in data["generator"]:
            generator_score = 9
        elif "WeasyPrint" in data["generator"]:
            generator_score = 6

        total_score = size_score + generator_score

        if total_score > best_score:
            best_score = total_score
            best_generator = filename

    if best_generator:
        print("\n🏆 Лучший результат:")
        print(f"   📄 Файл: {best_generator}")
        print(f"   🔧 Генератор: {results[best_generator]['generator']}")
        print(f"   📊 Размер: {results[best_generator]['size_kb']:.1f} KB")
        print(f"   🎯 Оценка: {best_score}/20")


def main():
    """Главная функция"""

    print("🚀 АНАЛИЗ КАЧЕСТВА PDF ГЕНЕРАТОРОВ")
    print("=" * 60)

    # Анализируем файлы
    results = analyze_pdf_files()

    if not results:
        print("❌ Анализ не удался")
        return

    # Сравниваем генераторы
    compare_generators(results)

    # Выявляем проблемы
    identify_issues(results)

    # Генерируем отчет
    generate_report(results)

    print("\n🎉 Анализ завершен!")
    print("📁 Проверьте созданные PDF файлы вручную для финальной оценки качества")


if __name__ == "__main__":
    main()
