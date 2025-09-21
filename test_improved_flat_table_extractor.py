#!/usr/bin/env python3
"""
Тест улучшенного FlatTableExtractor с интеграцией маппинга полей
"""

import logging
import os
import sys
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
sys.path.append(os.path.join(os.path.dirname(__file__), "src", "extractors"))
sys.path.append(os.path.join(os.path.dirname(__file__), "src", "processors"))

from extractors.flat_table_extractor import FlatTableExtractor

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def test_improved_flat_table_extractor():
    """
    Тестирует улучшенный FlatTableExtractor с интеграцией маппинга полей
    """
    print("🧪 ТЕСТ УЛУЧШЕННОГО FLAT TABLE EXTRACTOR")
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
                    f"\n📊 N/A значения: {na_count}/{total_fields} ({na_percentage:.1f}%)",
                )

                # Анализируем форматы дат
                date_fields = ["created_at", "updated_at"]
                for field in date_fields:
                    if flat_data and field in flat_data[0]:
                        sample_date = flat_data[0][field]
                        print(f"📅 Формат {field}: {sample_date}")
                        if sample_date and sample_date.endswith("Z"):
                            print("  ✅ Формат даты корректен (с Z суффиксом)")
                        else:
                            print("  ❌ Формат даты некорректен (без Z суффикса)")

                # Анализируем BLOB данные
                blob_fields = ["description"]
                for field in blob_fields:
                    if flat_data and field in flat_data[0]:
                        sample_blob = flat_data[0][field]
                        if sample_blob and len(str(sample_blob).strip()) > 0:
                            print(
                                f"🔍 BLOB данные {field}: {len(str(sample_blob))} символов",
                            )
                            print("  ✅ BLOB данные извлечены")
                        else:
                            print("  ❌ BLOB данные пусты")

                # Показываем превью плоской таблицы
                extractor.print_flat_table_preview(limit=10)

                # Показываем детальную информацию
                extractor.print_flat_table_detailed(limit=3)

                # Сохраняем результаты
                output_path = "data/results/improved_flat_table_extraction.json"
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                import json

                # Обработка datetime объектов для JSON
                def json_serializer(obj):
                    if isinstance(obj, datetime):
                        return obj.isoformat()
                    raise TypeError(
                        f"Object of type {type(obj)} is not JSON serializable",
                    )

                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(
                        result,
                        f,
                        ensure_ascii=False,
                        indent=2,
                        default=json_serializer,
                    )

                print(f"\n💾 Результаты сохранены: {output_path}")

                # Создаем Parquet файл
                try:
                    import pandas as pd

                    # ИСПРАВЛЕНИЕ: Конвертируем datetime объекты и проблемные типы для Parquet
                    def convert_for_parquet(obj):
                        if isinstance(obj, datetime):
                            return obj.isoformat()
                        if isinstance(obj, bool):
                            # Конвертируем boolean в None для числовых полей
                            return None
                        if obj is None:
                            return None
                        if isinstance(obj, (int, float)):
                            return obj
                        if isinstance(obj, str):
                            # Проверяем, является ли строка числом
                            if obj and (
                                obj != "N/A"
                                and obj != "None"
                                and obj != "!!!!"
                                and obj != "False"
                                and obj != "True"
                            ):
                                # Проверяем, не является ли это датой
                                if "T" in obj and ("-" in obj or ":" in obj):
                                    # Это похоже на дату, оставляем как строку
                                    return obj
                                # Попытка конвертировать в число
                                try:
                                    return float(obj)
                                except (ValueError, UnicodeDecodeError):
                                    # Если не число или corrupted string, заменяем на None
                                    return None
                            else:
                                # Если это N/A, None, False, True, заменяем на None
                                return None
                        else:
                            # Конвертируем все остальные типы в строки
                            return str(obj)

                    # Обрабатываем все данные для конвертации
                    processed_data = []
                    for item in flat_data:
                        processed_item = {}
                        for key, value in item.items():
                            processed_item[key] = convert_for_parquet(value)
                        processed_data.append(processed_item)

                    df = pd.DataFrame(processed_data)
                    parquet_path = "data/results/improved_flat_table.parquet"
                    df.to_parquet(parquet_path, index=False)
                    print(f"💾 Parquet файл создан: {parquet_path}")

                    # Анализируем Parquet файл
                    print("\n📊 АНАЛИЗ PARQUET ФАЙЛА:")
                    print(f"  - Размер: {os.path.getsize(parquet_path) / 1024:.2f} KB")
                    print(f"  - Строк: {len(df)}")
                    print(f"  - Колонок: {len(df.columns)}")

                    # Анализируем N/A значения в Parquet
                    na_percentage = (
                        df.isna().sum().sum() / (len(df) * len(df.columns)) * 100
                    )
                    print(f"  - N/A значения: {na_percentage:.1f}%")

                except Exception as e:
                    print(f"⚠️ Ошибка при создании Parquet файла: {e}")

                return True
            print("❌ Не удалось извлечь данные")
            return False
        print("❌ Ошибка при извлечении данных")
        return False

    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_improved_flat_table_extractor()
    if success:
        print("\n✅ ТЕСТ ПРОЙДЕН УСПЕШНО")
    else:
        print("\n❌ ТЕСТ НЕ ПРОЙДЕН")
