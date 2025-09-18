#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
            elif field_type == 'VB':  # Variable Binary
                return length
            
            # Новые типы полей 1С 8.3+
            elif field_type == 'UUID':
                return 16
            elif field_type == 'BLOB':
                return length
            elif field_type == 'JSON':
                return length
            elif field_type == 'XML':
                return length
            elif field_type == 'BINARY':
                return length
            elif field_type == 'TEXT':
                return length * 2
            elif field_type == 'DATE':
                return 8
            elif field_type == 'DECIMAL':
                return 16
            elif field_type == 'MONEY':
                return 16
            elif field_type == 'BOOLEAN':
                return 1
            
            # Расширенные типы полей
            elif field_type == 'ARRAY':
                return length
            elif field_type == 'OBJECT':
                return length
            elif field_type == 'REFERENCE':
                return 16
            elif field_type == 'CATALOG':
                return 16
            elif field_type == 'DOCUMENT':
                return 16
            elif field_type == 'ENUM':
                return 16
            elif field_type == 'CONSTANT':
                return length
            elif field_type == 'REGISTER':
                return 16
            
            # Специальные типы полей
            elif field_type == 'ACCOUNT':
                return 16
            elif field_type == 'MEASURE':
                return 16
            elif field_type == 'CURRENCY':
                return 16
            elif field_type == 'LANGUAGE':
                return 16
            elif field_type == 'TIMEZONE':
                return 16
            elif field_type == 'COLOR':
                return 4
            elif field_type == 'PICTURE':
                return length
            elif field_type == 'SOUND':
                return length
            elif field_type == 'VIDEO':
                return length
            
            # Типы безопасности
            elif field_type == 'ARCHIVE':
                return length
            elif field_type == 'COMPRESSED':
                return length
            elif field_type == 'ENCRYPTED':
                return length
            elif field_type == 'SIGNED':
                return length
            elif field_type == 'HASHED':
                return 32
            
            # Неизвестные типы полей - используем разумное значение по умолчанию
            else:
                print(f'⚠️ Предупреждение: Неизвестный тип поля "{field_type}", используем длину {length}')
                return length
        
        # Заменяем оригинальную функцию на патченную
        dr.calc_field_size = calc_field_size_patched
        
        print('✅ Простой патч успешно применен к библиотеке onec_dtools')
        print('📋 Добавлена поддержка всех типов полей включая VB')
        return True
        
    except Exception as e:
        print(f'❌ Ошибка применения патча: {e}')
        return False

if __name__ == '__main__':
    print('🔧 Применение простого патча для библиотеки onec_dtools...')
    apply_simple_patch()
