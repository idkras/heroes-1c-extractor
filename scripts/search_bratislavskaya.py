#!/usr/bin/env python3

import json
from datetime import datetime

from onec_dtools.database_reader import DatabaseReader


def safe_get_blob_content(value):
    """
    Безопасное извлечение содержимого BLOB поля
    """
    try:
        if hasattr(value, "value"):
            content = value.value
            if content and len(str(content)) > 0:
                return str(content)
        elif hasattr(value, "__iter__"):
            try:
                iterator = iter(value)
                content = next(iterator)
                if content and len(content) > 0:
                    return str(content)
            except StopIteration:
                pass
        elif hasattr(value, "__bytes__"):
            try:
                content = bytes(value)
                if content and len(content) > 0:
                    return str(content)
            except:
                pass
    except Exception as e:
        return f"Ошибка чтения BLOB: {e}"

    return None


def search_bratislavskaya_documents():
    """
    Поиск документов по Братиславской
    """
    print("🔍 Поиск документов по Братиславской")
    print("🎯 ЦЕЛЬ: Найти все документы, связанные с Братиславской")
    print("=" * 60)

    try:
        with open("data/raw/1Cv8.1CD", "rb") as f:
            db = DatabaseReader(f)

            print("✅ База данных открыта успешно!")
            print(f"📊 Количество таблиц: {len(db.tables)}")

            results = {
                "bratislavskaya_documents": [],
                "metadata": {
                    "extraction_date": datetime.now().isoformat(),
                    "total_tables": len(db.tables),
                    "source_file": "data/raw/1Cv8.1CD",
                },
            }

            # Ключевые слова для поиска
            search_keywords = [
                "братиславская",
                "братиславская",
                "братиславская",
                "братиславская",
                "братиславская",
            ]

            print("\n🔍 Поиск по ключевым словам")
            print("-" * 40)

            # Анализируем основные таблицы документов
            document_tables = [
                "_DOCUMENT163",  # Акты выполненных работ
                "_DOCUMENT184",  # Счета-фактуры
                "_DOCUMENT154",  # Накладные
                "_DOCUMENT137",  # Дополнительные документы
                "_DOCUMENT12259",  # Служебные документы
            ]

            for table_name in document_tables:
                if table_name in db.tables:
                    print(f"\n📊 Анализ таблицы: {table_name}")
                    table = db.tables[table_name]
                    print(f"   📈 Всего записей: {len(table):,}")

                    # Анализируем первые 100 записей
                    found_documents = []
                    for i in range(min(100, len(table))):
                        try:
                            row = table[i]
                            if not row.is_empty:
                                # Получаем данные записи
                                row_data = row.as_dict()

                                # Ищем ключевые слова в полях
                                found_keywords = []
                                for field_name, value in row_data.items():
                                    if value is not None:
                                        value_str = str(value).lower()
                                        for keyword in search_keywords:
                                            if keyword.lower() in value_str:
                                                found_keywords.append(keyword)

                                # Ищем в BLOB полях
                                blob_content = ""
                                for field_name, value in row_data.items():
                                    if hasattr(value, "__class__") and "Blob" in str(
                                        value.__class__,
                                    ):
                                        content = safe_get_blob_content(value)
                                        if content:
                                            blob_content += content.lower()

                                for keyword in search_keywords:
                                    if keyword.lower() in blob_content:
                                        found_keywords.append(f"{keyword} (в BLOB)")

                                if found_keywords:
                                    document = {
                                        "table_name": table_name,
                                        "row_index": i,
                                        "fields": row_data,
                                        "found_keywords": found_keywords,
                                        "blob_content": blob_content[:500]
                                        if blob_content
                                        else "",
                                    }
                                    found_documents.append(document)
                                    print(
                                        f"   ✅ Найден документ {i}: {found_keywords}",
                                    )

                        except Exception as e:
                            print(f"   ⚠️ Ошибка при анализе записи {i}: {e}")
                            continue

                    if found_documents:
                        results["bratislavskaya_documents"].extend(found_documents)
                        print(f"   📋 Найдено документов: {len(found_documents)}")

            # Сохраняем результаты
            with open(
                "data/results/bratislavskaya_search.json",
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

            print(
                "\n📄 Результаты сохранены в: data/results/bratislavskaya_search.json",
            )
            print(
                f"📊 Всего найдено документов: {len(results['bratislavskaya_documents'])}",
            )

            return results

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback

        print("🔍 Детали ошибки:")
        traceback.print_exc()
        return None


if __name__ == "__main__":
    search_bratislavskaya_documents()
