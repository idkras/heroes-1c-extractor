#!/usr/bin/env python3
"""
Простой тест для проверки исправленного flat_table_extractor.py
"""

import sys
import os
import json
from datetime import datetime

# Добавляем путь к проекту
sys.path.append("src")

from extractors.flat_table_extractor import FlatTableExtractor


def test_fixed_flat_table():
    """
    Тестирует исправленный FlatTableExtractor
    """
    print("🧪 ТЕСТ ИСПРАВЛЕННОГО FLAT TABLE EXTRACTOR")
    print("=" * 60)

    # Путь к базе данных 1С
    db_path = "data/raw/1Cv8.1CD"

    if not os.path.exists(db_path):
        print(f"❌ Файл базы данных не найден: {db_path}")
        return False

    try:
        # Создаем экземпляр извлекателя
        extractor = FlatTableExtractor(db_path)
        print("✅ FlatTableExtractor создан успешно")

        # Тестируем извлечение плоской таблицы
        print("\n🔍 Тестирование извлечения плоской таблицы...")
        result = extractor.extract_flat_table()

        if result and "flat_data" in result:
            flat_data = result["flat_data"]
            print(f"✅ Извлечено сущностей: {len(flat_data)}")

            # Анализируем результаты
            if flat_data:
                print("\n📊 АНАЛИЗ РЕЗУЛЬТАТОВ:")

                # Анализируем типы сущностей
                entity_types = {}
                for entity in flat_data:
                    entity_type = entity.get("entity_type", "unknown")
                    entity_types[entity_type] = entity_types.get(entity_type, 0) + 1

                print("📈 Типы сущностей:")
                for entity_type, count in entity_types.items():
                    print(f"  - {entity_type}: {count}")

                # Анализируем N/A значения
                na_count = 0
                total_fields = 0
                for entity in flat_data:
                    for key, value in entity.items():
                        total_fields += 1
                        if value is None or value == "N/A" or str(value).strip() == "":
                            na_count += 1

                na_percentage = (
                    (na_count / total_fields * 100) if total_fields > 0 else 0
                )
                print(
                    f"\n📊 N/A значения: {na_count}/{total_fields} ({na_percentage:.1f}%)"
                )

                # Показываем превью плоской таблицы
                extractor.print_flat_table_preview(limit=5)

                # Сохраняем результаты
                output_path = "data/results/fixed_flat_table_test.json"
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                # Обработка datetime объектов для JSON
                def json_serializer(obj):
                    if isinstance(obj, datetime):
                        return obj.isoformat()
                    raise TypeError(
                        f"Object of type {type(obj)} is not JSON serializable"
                    )

                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(
                        result, f, ensure_ascii=False, indent=2, default=json_serializer
                    )

                print(f"\n💾 Результаты сохранены: {output_path}")

                return True
            else:
                print("❌ Не удалось извлечь данные")
                return False
        else:
            print("❌ Ошибка при извлечении данных")
            return False

    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_fixed_flat_table()
    if success:
        print("\n✅ ТЕСТ ПРОЙДЕН УСПЕШНО")
    else:
        print("\n❌ ТЕСТ НЕ ПРОЙДЕН")
