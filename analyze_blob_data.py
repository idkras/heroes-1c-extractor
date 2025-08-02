#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from onec_dtools.database_reader import DatabaseReader
import sys
import os

def analyze_blob_data():
    """
    Анализ BLOB данных для поиска изображений
    """
    print("🔍 Анализ BLOB данных для поиска изображений")
    print("=" * 60)
    
    try:
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            
            # Анализируем таблицу CONFIG с BLOB данными
            if 'CONFIG' in db.tables:
                table = db.tables['CONFIG']
                print(f"\n📊 Анализ таблицы CONFIG:")
                print(f"   📈 Всего записей: {len(table):,}")
                
                # Находим записи с BLOB данными
                blob_records = []
                for i in range(min(10, len(table))):
                    row = table[i]
                    if not row.is_empty:
                        try:
                            blob_data = row['BINARYDATA']
                            if blob_data and hasattr(blob_data, 'value'):
                                blob_records.append((i, row, blob_data))
                        except:
                            pass
                
                print(f"   ✅ Найдено {len(blob_records)} записей с BLOB данными")
                
                # Анализируем BLOB данные
                for idx, (row_num, row, blob) in enumerate(blob_records[:5]):
                    print(f"\n   📄 BLOB запись #{row_num}:")
                    print(f"      FILENAME: {row['FILENAME']}")
                    print(f"      DATASIZE: {row['DATASIZE']}")
                    
                    try:
                        # Получаем BLOB данные
                        blob_value = blob.value
                        print(f"      BLOB размер: {len(blob_value)} байт")
                        print(f"      BLOB начало: {blob_value[:50].hex()}")
                        
                        # Ищем сигнатуры изображений
                        if blob_value.startswith(b'\xff\xd8\xff'):  # JPEG
                            print(f"      ✅ Обнаружен JPEG файл!")
                        elif blob_value.startswith(b'\x89PNG\r\n\x1a\n'):  # PNG
                            print(f"      ✅ Обнаружен PNG файл!")
                        elif blob_value.startswith(b'GIF87a') or blob_value.startswith(b'GIF89a'):  # GIF
                            print(f"      ✅ Обнаружен GIF файл!")
                        else:
                            # Ищем текстовые данные
                            try:
                                text_data = blob_value.decode('utf-8', errors='ignore')
                                if len(text_data) > 10:
                                    print(f"      📝 Текстовые данные: {text_data[:200]}...")
                                    
                                    # Ищем ключевые слова
                                    keywords = ['цвет', 'rose', 'tulip', 'flower', 'товар', 'номенклатура', 'наименование', 'описание']
                                    for keyword in keywords:
                                        if keyword.lower() in text_data.lower():
                                            print(f"      🔍 Найдено ключевое слово: '{keyword}'")
                            except:
                                print(f"      ❓ Бинарные данные (не текст)")
                        
                    except Exception as e:
                        print(f"      ❌ Ошибка при анализе BLOB: {e}")
                    
                    if idx >= 2:  # Показываем только первые 3 BLOB записи
                        break
                        
    except Exception as e:
        print(f"❌ Ошибка при работе с базой данных: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_blob_data()
    print("\n✅ Анализ завершен") 