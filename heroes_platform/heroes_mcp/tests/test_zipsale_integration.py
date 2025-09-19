#!/usr/bin/env python3
"""
Интеграционный тест для HeroesGPT Offers Extractor на zipsale.co.uk
HeroesGPT Landing Analysis Standard v1.8 Compliance Testing

JTBD: Когда нужно проверить работу команды извлечения оферов,
я хочу протестировать её на реальном сайте zipsale.co.uk,
чтобы убедиться что команда работает корректно и соответствует эталону.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

import pytest

# Добавляем путь к src для импорта
sys.path.append("src")
from heroes_gpt_offers_extractor import OffersExtractor


class TestZipsaleIntegration:
    """Интеграционные тесты на zipsale.co.uk"""

    @pytest.fixture
    async def extractor(self):
        """Фикстура для создания экстрактора"""
        async with OffersExtractor() as extractor:
            yield extractor

    @pytest.mark.asyncio
    async def test_extract_offers_from_zipsale_co_uk(self, extractor):
        """
        Тест извлечения оферов с zipsale.co.uk

        Согласно HeroesGPT Standard v1.8:
        - Минимум 60+ оферов
        - Все 7 типов оферов представлены
        - Количественные данные извлечены
        - Эмоциональные триггеры идентифицированы
        """
        print("🔍 Начинаем тест извлечения оферов с zipsale.co.uk")

        # STEP 1: Извлечение оферов
        result = await extractor.extract_offers_from_url("https://zipsale.co.uk")

        # STEP 2: Проверка успешности
        assert result["status"] == "success", (
            f"Ошибка извлечения: {result.get('error', 'Unknown error')}"
        )

        # STEP 3: Проверка соответствия стандарту v1.8
        validation = result["validation"]

        print("📊 Результаты анализа zipsale.co.uk:")
        print(f"   - Всего оферов: {result['offers_count']}")
        print(f"   - Минимум 60+: {validation['meets_minimum']}")
        print(f"   - Compliance score: {validation['compliance_score']:.2%}")
        print(f"   - Типы оферов: {list(validation['offer_types'].keys())}")

        # Проверяем требования стандарта
        assert result["offers_count"] >= 60, (
            f"Недостаточно оферов: {result['offers_count']} < 60"
        )
        assert validation["meets_minimum"] == True, (
            "Не соответствует требованию минимум 60+ оферов"
        )
        assert validation["compliance_score"] >= 0.8, (
            f"Низкий compliance score: {validation['compliance_score']}"
        )

        # STEP 4: Анализ типов оферов
        offer_types = validation["offer_types"]
        print(
            f"   - Количественные обещания: {offer_types.get('quantitative_promises', 0)}"
        )
        print(f"   - Качественные выгоды: {offer_types.get('qualitative_benefits', 0)}")
        print(f"   - Социальные доказательства: {offer_types.get('social_proof', 0)}")
        print(f"   - Снижение рисков: {offer_types.get('risk_reducers', 0)}")
        print(f"   - Срочность/дефицит: {offer_types.get('urgency_scarcity', 0)}")
        print(f"   - Ясность процесса: {offer_types.get('process_clarity', 0)}")
        print(f"   - Сигналы авторитета: {offer_types.get('authority_signals', 0)}")

        # Проверяем разнообразие типов оферов
        assert len(offer_types) >= 5, (
            f"Недостаточно типов оферов: {len(offer_types)} < 5"
        )

        # STEP 5: Проверка количественных данных
        assert validation["quantitative_data_present"] == True, (
            "Отсутствуют количественные данные"
        )

        # STEP 6: Проверка эмоциональных триггеров
        assert validation["emotional_triggers_present"] == True, (
            "Отсутствуют эмоциональные триггеры"
        )

        # STEP 7: Сохранение результатов для сравнения с эталоном
        test_results = {
            "test_name": "zipsale_co_uk_integration_test",
            "timestamp": datetime.now().isoformat(),
            "url": "https://zipsale.co.uk",
            "standard_version": "v1.8",
            "results": result,
            "validation_passed": True,
        }

        # Сохраняем результаты
        results_file = Path("test_results_zipsale.json")
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)

        print("✅ Тест zipsale.co.uk пройден успешно!")
        print(f"📁 Результаты сохранены в: {results_file}")

        return result

    @pytest.mark.asyncio
    async def test_zipsale_offers_quality_analysis(self, extractor):
        """
        Детальный анализ качества оферов zipsale.co.uk

        Проверяем соответствие эталонному анализу:
        - Crosslisting software focus
        - Multi-platform management
        - Professional resellers target
        """
        print("🔍 Начинаем детальный анализ качества оферов zipsale.co.uk")

        result = await extractor.extract_offers_from_url("https://zipsale.co.uk")
        assert result["status"] == "success"

        offers = result["offers"]

        # Анализируем ключевые темы
        crosslisting_offers = []
        multi_platform_offers = []
        professional_offers = []

        for offer in offers:
            text_lower = offer["text"].lower()

            if any(
                word in text_lower
                for word in ["crosslisting", "cross-listing", "cross listing"]
            ):
                crosslisting_offers.append(offer)

            if any(
                word in text_lower
                for word in [
                    "multi-platform",
                    "multi platform",
                    "platforms",
                    "marketplace",
                ]
            ):
                multi_platform_offers.append(offer)

            if any(
                word in text_lower
                for word in ["professional", "reseller", "seller", "business"]
            ):
                professional_offers.append(offer)

        print("📊 Анализ тематики оферов:")
        print(f"   - Crosslisting оферы: {len(crosslisting_offers)}")
        print(f"   - Multi-platform оферы: {len(multi_platform_offers)}")
        print(f"   - Professional оферы: {len(professional_offers)}")

        # Проверяем что найдены ключевые оферы
        assert len(crosslisting_offers) > 0, "Не найдены оферы по crosslisting"
        assert len(multi_platform_offers) > 0, "Не найдены оферы по multi-platform"
        assert len(professional_offers) > 0, "Не найдены оферы для профессионалов"

        # Анализируем количественные данные
        quantitative_offers = [o for o in offers if o["quantitative_data"]]
        print(f"   - Оферы с количественными данными: {len(quantitative_offers)}")

        # Показываем примеры количественных данных
        for i, offer in enumerate(quantitative_offers[:5]):
            print(
                f"     {i + 1}. {offer['text'][:100]}... - {offer['quantitative_data']}"
            )

        assert len(quantitative_offers) > 0, (
            "Не найдены оферы с количественными данными"
        )

        print("✅ Детальный анализ качества пройден успешно!")

    @pytest.mark.asyncio
    async def test_zipsale_compliance_with_standard_v1_8(self, extractor):
        """
        Проверка соответствия HeroesGPT Standard v1.8

        Согласно стандарту:
        - Минимум 60+ оферов
        - 7 типов оферов
        - Количественные данные
        - Эмоциональные триггеры
        - Сегментация аудитории
        """
        print("🔍 Проверка соответствия HeroesGPT Standard v1.8")

        result = await extractor.extract_offers_from_url("https://zipsale.co.uk")
        assert result["status"] == "success"

        validation = result["validation"]

        # Проверяем все требования стандарта
        compliance_checks = {
            "Минимум 60+ оферов": validation["meets_minimum"],
            "Количественные данные": validation["quantitative_data_present"],
            "Эмоциональные триггеры": validation["emotional_triggers_present"],
            "Compliance score >= 0.8": validation["compliance_score"] >= 0.8,
            "Разнообразие типов оферов": len(validation["offer_types"]) >= 5,
        }

        print("📋 Результаты проверки соответствия стандарту:")
        for check, passed in compliance_checks.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check}")

        # Проверяем что все требования выполнены
        failed_checks = [
            check for check, passed in compliance_checks.items() if not passed
        ]
        assert len(failed_checks) == 0, f"Не выполнены требования: {failed_checks}"

        print("✅ Соответствие HeroesGPT Standard v1.8 подтверждено!")

    @pytest.mark.asyncio
    async def test_zipsale_performance_benchmark(self, extractor):
        """
        Тест производительности на zipsale.co.uk

        Проверяем:
        - Время выполнения
        - Качество извлечения
        - Стабильность работы
        """
        print("🔍 Тест производительности на zipsale.co.uk")

        import time

        start_time = time.time()
        result = await extractor.extract_offers_from_url("https://zipsale.co.uk")
        end_time = time.time()

        execution_time = end_time - start_time

        print("📊 Результаты производительности:")
        print(f"   - Время выполнения: {execution_time:.2f} секунд")
        print(f"   - Оферов в секунду: {result['offers_count'] / execution_time:.1f}")
        print(f"   - Статус: {result['status']}")

        # Проверяем производительность
        assert execution_time < 30.0, f"Слишком медленно: {execution_time:.2f}s > 30s"
        assert result["status"] == "success", "Ошибка выполнения"
        assert result["offers_count"] > 0, "Не извлечено ни одного офера"

        print("✅ Тест производительности пройден успешно!")


async def run_zipsale_integration_test():
    """
    Запуск полного интеграционного теста на zipsale.co.uk

    JTBD: Когда нужно проверить работу команды извлечения оферов,
    я хочу запустить полный тест на zipsale.co.uk,
    чтобы убедиться что команда готова к использованию.
    """
    print("🚀 Запуск интеграционного теста на zipsale.co.uk")
    print("=" * 60)

    async with OffersExtractor() as extractor:
        # Тест 1: Базовое извлечение оферов
        print("\n1️⃣ Тест базового извлечения оферов")
        result = await extractor.extract_offers_from_url("https://zipsale.co.uk")

        if result["status"] == "success":
            print(f"✅ Успешно извлечено {result['offers_count']} оферов")
            print(
                f"📊 Compliance score: {result['validation']['compliance_score']:.2%}"
            )
        else:
            print(f"❌ Ошибка: {result.get('error', 'Unknown error')}")
            return False

        # Тест 2: Анализ качества
        print("\n2️⃣ Анализ качества оферов")
        offers = result["offers"]

        # Подсчитываем типы оферов
        offer_types = {}
        for offer in offers:
            offer_type = offer["type"]
            offer_types[offer_type] = offer_types.get(offer_type, 0) + 1

        print("📋 Распределение типов оферов:")
        for offer_type, count in offer_types.items():
            print(f"   - {offer_type}: {count}")

        # Тест 3: Проверка ключевых тем
        print("\n3️⃣ Проверка ключевых тем")
        crosslisting_count = sum(
            1 for o in offers if "crosslisting" in o["text"].lower()
        )
        multi_platform_count = sum(1 for o in offers if "platform" in o["text"].lower())

        print(f"   - Crosslisting оферы: {crosslisting_count}")
        print(f"   - Multi-platform оферы: {multi_platform_count}")

        # Тест 4: Сохранение результатов
        print("\n4️⃣ Сохранение результатов")
        test_results = {
            "test_name": "zipsale_co_uk_full_integration_test",
            "timestamp": datetime.now().isoformat(),
            "url": "https://zipsale.co.uk",
            "standard_version": "v1.8",
            "results": result,
            "summary": {
                "total_offers": result["offers_count"],
                "offer_types": offer_types,
                "crosslisting_offers": crosslisting_count,
                "multi_platform_offers": multi_platform_count,
                "compliance_score": result["validation"]["compliance_score"],
            },
        }

        results_file = Path("zipsale_integration_test_results.json")
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)

        print(f"📁 Результаты сохранены в: {results_file}")

        # Финальная проверка
        print("\n5️⃣ Финальная проверка")
        success = (
            result["status"] == "success"
            and result["offers_count"] >= 60
            and result["validation"]["compliance_score"] >= 0.8
        )

        if success:
            print("✅ Интеграционный тест zipsale.co.uk пройден успешно!")
            print("🎯 Команда готова к использованию")
        else:
            print("❌ Интеграционный тест не пройден")
            print("🔧 Требуется доработка")

        return success


if __name__ == "__main__":
    # Запуск интеграционного теста
    success = asyncio.run(run_zipsale_integration_test())

    if success:
        print("\n🎉 Команда извлечения оферов успешно протестирована на zipsale.co.uk!")
        print("📋 Соответствует HeroesGPT Standard v1.8")
        print("🚀 Готова к интеграции в MCP workflow")
    else:
        print("\n⚠️ Требуется доработка команды")
        exit(1)
