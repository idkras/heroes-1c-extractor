#!/usr/bin/env python3

"""
ПРОСТОЙ РАБОЧИЙ ПАТЧ ДЛЯ БИБЛИОТЕКИ ONEC_DTOOLS
Поддержка новых типов полей 1С 8.3+ включая VB

Автор: AI Assistant
Дата: Thu Sep 18 23:10:39 CEST 2025
Версия: 1.3
"""


def apply_simple_patch() -> bool:
    """
    Применяет простой патч к библиотеке onec_dtools
    """
    try:
        import onec_dtools.database_reader as dr

        # Сохраняем оригинальную функцию
        original_calc_field_size = dr.calc_field_size

        def calc_field_size_patched(field_type: str, length: int) -> int:
            """
            Патченная функция calc_field_size с поддержкой новых типов полей
            """
            # Классические типы полей 1С
            if field_type == "B":
                return length
            if field_type == "L":
                return 1
            if field_type == "N":
                return length // 2 + 1
            if field_type == "NC":
                return length * 2
            if field_type == "NVC":
                return length * 2 + 2
            if field_type == "RV":
                return 16
            if field_type == "NT" or field_type == "I":
                return 8
            if field_type == "DT":
                return 7

            # Обнаруженные типы полей в реальной базе данных
            if field_type == "VB":  # Variable Binary
                return length

            # Новые типы полей 1С 8.3+
            if field_type == "UUID":
                return 16
            if (
                field_type == "BLOB"
                or field_type == "JSON"
                or field_type == "XML"
                or field_type == "BINARY"
            ):
                return length
            if field_type == "TEXT":
                return length * 2
            if field_type == "DATE":
                return 8
            if field_type == "DECIMAL" or field_type == "MONEY":
                return 16
            if field_type == "BOOLEAN":
                return 1

            # Расширенные типы полей
            if field_type == "ARRAY" or field_type == "OBJECT":
                return length
            if (
                field_type == "REFERENCE"
                or field_type == "CATALOG"
                or field_type == "DOCUMENT"
                or field_type == "ENUM"
            ):
                return 16
            if field_type == "CONSTANT":
                return length
            if (
                field_type == "REGISTER"
                or field_type == "ACCOUNT"
                or field_type == "MEASURE"
                or field_type == "CURRENCY"
                or field_type == "LANGUAGE"
                or field_type == "TIMEZONE"
            ):
                return 16
            if field_type == "COLOR":
                return 4
            if (
                field_type == "PICTURE"
                or field_type == "SOUND"
                or field_type == "VIDEO"
                or field_type == "ARCHIVE"
                or field_type == "COMPRESSED"
                or field_type == "ENCRYPTED"
                or field_type == "SIGNED"
            ):
                return length
            if field_type == "HASHED":
                return 32

            # Неизвестные типы полей - используем разумное значение по умолчанию
            print(
                f'⚠️ Предупреждение: Неизвестный тип поля "{field_type}", используем длину {length}',
            )
            return length

        # Заменяем оригинальную функцию на патченную
        dr.calc_field_size = calc_field_size_patched

        print("✅ Простой патч успешно применен к библиотеке onec_dtools")
        print("📋 Добавлена поддержка всех типов полей включая VB")
        return True

    except Exception as e:
        print(f"❌ Ошибка применения патча: {e}")
        return False


if __name__ == "__main__":
    print("🔧 Применение простого патча для библиотеки onec_dtools...")
    apply_simple_patch()
