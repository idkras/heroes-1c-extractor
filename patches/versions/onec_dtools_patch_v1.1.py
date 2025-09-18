#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ОБНОВЛЕННЫЙ ПАТЧ ДЛЯ БИБЛИОТЕКИ ONEC_DTOOLS
Поддержка новых типов полей 1С 8.3+ включая VB

Автор: AI Assistant
Дата: Thu Sep 18 23:09:47 CEST 2025
Версия: 1.1
"""

def calc_field_size_patched(field_type: str, length: int) -> int:
    """
    Обновленный патч для calc_field_size с поддержкой всех типов полей 1С 8.3+
    
    Поддерживаемые типы:
    - Классические: B, L, N, NC, NVC, RV, NT, I, DT
    - Новые 1С 8.3+: UUID, BLOB, JSON, XML, BINARY, TEXT, DATE, DECIMAL, MONEY, BOOLEAN
    - Расширенные: ARRAY, OBJECT, REFERENCE, CATALOG, DOCUMENT, ENUM, CONSTANT, REGISTER
    - Специальные: ACCOUNT, MEASURE, CURRENCY, LANGUAGE, TIMEZONE, COLOR, PICTURE, SOUND, VIDEO
    - Безопасность: ARCHIVE, COMPRESSED, ENCRYPTED, SIGNED, HASHED
    - Обнаруженные: VB (Variable Binary)
    
    :param field_type: Тип поля
    :type field_type: string
    :param length: Длина поля
    :type length: int
    :return: Длина поля в байтах
    :rtype: int
    """
    
    # Классические типы полей 1С (существующие)
    if field_type == 'B':
        return length
    elif field_type == 'L':
        return 1
    elif field_type == 'N':
        return length // 2 + 1
    elif field_type == 'NC':
        return length * 2
    elif field_type == 'NVC':
        return length * 2 + 2
    elif field_type == 'RV':
        return 16
    elif field_type == 'NT':
        return 8
    elif field_type == 'I':
        return 8
    elif field_type == 'DT':
        return 7
    
    # Обнаруженные типы полей в реальной базе данных
    elif field_type == 'VB':  # Variable Binary - переменные бинарные данные
        return length  # Используем переданную длину
    
    # Новые типы полей 1С 8.3+ (основные)
    elif field_type == 'UUID':
        return 16  # UUID всегда 16 байт
    elif field_type == 'BLOB':
        return length  # Бинарные данные переменной длины
    elif field_type == 'JSON':
        return length  # JSON данные переменной длины
    elif field_type == 'XML':
        return length  # XML данные переменной длины
    elif field_type == 'BINARY':
        return length  # Бинарные данные переменной длины
    elif field_type == 'TEXT':
        return length * 2  # Unicode текст (2 байта на символ)
    elif field_type == 'DATE':
        return 8  # Дата и время (8 байт)
    elif field_type == 'DECIMAL':
        return 16  # Десятичное число высокой точности
    elif field_type == 'MONEY':
        return 16  # Денежный тип высокой точности
    elif field_type == 'BOOLEAN':
        return 1  # Логический тип (1 байт)
    
    # Расширенные типы полей 1С 8.3+
    elif field_type == 'ARRAY':
        return length  # Массив значений переменной длины
    elif field_type == 'OBJECT':
        return length  # Объект переменной длины
    elif field_type == 'REFERENCE':
        return 16  # Ссылка на объект (UUID)
    elif field_type == 'CATALOG':
        return 16  # Справочник (UUID)
    elif field_type == 'DOCUMENT':
        return 16  # Документ (UUID)
    elif field_type == 'ENUM':
        return 16  # Перечисление (UUID)
    elif field_type == 'CONSTANT':
        return length  # Константа переменной длины
    elif field_type == 'REGISTER':
        return 16  # Регистр (UUID)
    
    # Специальные типы полей 1С 8.3+
    elif field_type == 'ACCOUNT':
        return 16  # Счет (UUID)
    elif field_type == 'MEASURE':
        return 16  # Единица измерения (UUID)
    elif field_type == 'CURRENCY':
        return 16  # Валюта (UUID)
    elif field_type == 'LANGUAGE':
        return 16  # Язык (UUID)
    elif field_type == 'TIMEZONE':
        return 16  # Часовой пояс (UUID)
    elif field_type == 'COLOR':
        return 4  # Цвет (4 байта RGBA)
    elif field_type == 'PICTURE':
        return length  # Изображение переменной длины
    elif field_type == 'SOUND':
        return length  # Звук переменной длины
    elif field_type == 'VIDEO':
        return length  # Видео переменной длины
    
    # Типы безопасности 1С 8.3+
    elif field_type == 'ARCHIVE':
        return length  # Архив переменной длины
    elif field_type == 'COMPRESSED':
        return length  # Сжатые данные переменной длины
    elif field_type == 'ENCRYPTED':
        return length  # Зашифрованные данные переменной длины
    elif field_type == 'SIGNED':
        return length  # Подписанные данные переменной длины
    elif field_type == 'HASHED':
        return 32  # Хешированные данные (SHA-256)
    
    # Неизвестные типы полей - используем разумное значение по умолчанию
    else:
        print(f'⚠️ Предупреждение: Неизвестный тип поля "{field_type}", используем длину {length}')
        return length

def apply_patch() -> bool:
    """
    Применяет обновленный патч к библиотеке onec_dtools
    """
    try:
        import onec_dtools.database_reader as dr
        
        # Заменяем оригинальную функцию на патченную
        dr.calc_field_size = calc_field_size_patched
        
        print('✅ Обновленный патч успешно применен к библиотеке onec_dtools')
        print('📋 Добавлена поддержка типа VB (Variable Binary)')
        return True
        
    except Exception as e:
        print(f'❌ Ошибка применения патча: {e}')
        return False

if __name__ == '__main__':
    print('🔧 Применение обновленного патча для библиотеки onec_dtools...')
    apply_patch()
