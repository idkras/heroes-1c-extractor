#!/usr/bin/env python3
"""
Скрипт для анализа доли B2B-сегмента, связанного с грузовыми автомобилями в звонках avtoall.ru
"""

import pandas as pd
import re

# Путь к файлу с данными
DATA_FILE = "[projects]/avtoall.ru/sales blockers/[heroes] transcribations autoall.ru - avtoall_ru all recordings.tsv"

# Определение ключевых слов, связанных с грузовыми автомобилями
TRUCK_KEYWORDS = [
    'грузов', 'камаз', 'камазы', 'камазов', 'камазу', 'уаз', 'газ', 'газель', 'газели', 'маз',
    'фургон', 'грузовик', 'еврофура', 'фура', 'тягач', 'полуприцеп', 'прицеп',
    'груз', 'грузов', 'автопарк', 'howo', 'man', 'ман', 'daf', 'scania', 'скания',
    'volvo', 'вольво', 'mercedes', 'мерседес', 'iveco', 'ивеко', 'reno', 'рено',
    'зил', 'миксер', 'самосвал', 'шакман', 'shaanxi', 'шаанкси', 'shacman', 'ису', 'isuzu',
    'hino', 'хино', 'mitsu fuso', 'фусо'
]

def is_truck_related(text):
    """Проверяет, связан ли текст с грузовыми автомобилями"""
    if not isinstance(text, str):
        return False
    
    # Преобразуем в нижний регистр для единообразного сравнения
    text_lower = text.lower()
    
    # Проверяем наличие ключевых слов
    for keyword in TRUCK_KEYWORDS:
        # Используем границы слов для более точного соответствия
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        if re.search(pattern, text_lower):
            return True
    
    return False

def main():
    """Основная функция анализа"""
    print("Загрузка данных из файла...")
    try:
        # Загружаем данные
        df = pd.read_csv(DATA_FILE, sep='\t', encoding='utf-8')
        print(f"Загружено записей: {len(df)}")
        
        # Анализируем колонки
        print("\nКолонки в датасете:")
        for col in df.columns:
            print(f"- {col}")
        
        # Проверяем наличие колонки с типом клиента (B2B/B2C)
        client_type_col = None
        for col in df.columns:
            if 'b2b' in col.lower() and 'b2c' in col.lower():
                client_type_col = col
                break
        
        if client_type_col:
            print(f"\nИспользуем колонку для определения типа клиента: {client_type_col}")
        else:
            print("\nВНИМАНИЕ: Колонка для определения типа клиента (B2B/B2C) не найдена.")
            client_type_col = "b2c и b2b"  # Предполагаемое название колонки
        
        # Находим колонку с текстом разговора
        text_col = None
        for col in df.columns:
            if col.lower() in ['разговор', 'conversation', 'text', 'текст']:
                text_col = col
                break
        
        if text_col:
            print(f"Используем колонку для анализа текста разговора: {text_col}")
        else:
            print("ВНИМАНИЕ: Колонка с текстом разговора не найдена.")
            text_col = "разговор"  # Предполагаемое название колонки
        
        # Анализ B2B и связанных с грузовиками звонков
        total_calls = len(df)
        
        # Определяем B2B звонки (если такая колонка есть)
        b2b_calls = 0
        if client_type_col in df.columns:
            b2b_values = df[client_type_col].fillna('').astype(str)
            b2b_calls = sum(1 for val in b2b_values if 'b2b' in val.lower())
            print(f"\nВсего B2B звонков: {b2b_calls} ({b2b_calls/total_calls*100:.1f}% от общего числа)")
        else:
            print("\nНевозможно определить количество B2B звонков - колонка не найдена")
        
        # Определяем звонки, связанные с грузовыми автомобилями
        truck_related_calls = 0
        b2b_truck_calls = 0
        
        # Создаем массив для хранения примеров звонков, связанных с грузовиками
        truck_examples = []
        
        if text_col in df.columns:
            for idx, row in df.iterrows():
                text = str(row[text_col]) if not pd.isna(row[text_col]) else ""
                is_b2b = False
                
                if client_type_col in df.columns:
                    client_type = str(row[client_type_col]) if not pd.isna(row[client_type_col]) else ""
                    is_b2b = 'b2b' in client_type.lower()
                
                if is_truck_related(text):
                    truck_related_calls += 1
                    if is_b2b:
                        b2b_truck_calls += 1
                    
                    # Сохраняем пример для отчета (первые 100 символов текста)
                    truck_examples.append({
                        'id': idx,
                        'is_b2b': is_b2b,
                        'text_snippet': text[:200] + "..." if len(text) > 200 else text
                    })
            
            print(f"\nВсего звонков, связанных с грузовыми автомобилями: {truck_related_calls} ({truck_related_calls/total_calls*100:.1f}% от общего числа)")
            
            if b2b_calls > 0:
                print(f"B2B звонков, связанных с грузовыми автомобилями: {b2b_truck_calls} ({b2b_truck_calls/b2b_calls*100:.1f}% от B2B, {b2b_truck_calls/total_calls*100:.1f}% от общего числа)")
            
            # Вывод примеров звонков, связанных с грузовиками
            print("\nПримеры звонков, связанных с грузовыми автомобилями:")
            for i, example in enumerate(truck_examples[:5], 1):  # Показываем первые 5 примеров
                print(f"\nПример {i} (ID: {example['id']}, B2B: {'Да' if example['is_b2b'] else 'Нет'}):")
                print(example['text_snippet'])
            
            # Анализ наиболее частых марок грузовиков
            truck_brands = {}
            for keyword in TRUCK_KEYWORDS:
                count = 0
                for idx, row in df.iterrows():
                    text = str(row[text_col]) if not pd.isna(row[text_col]) else ""
                    pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                    if re.search(pattern, text.lower()):
                        count += 1
                
                if count > 0:
                    truck_brands[keyword] = count
            
            # Сортируем марки по частоте упоминания
            sorted_brands = sorted(truck_brands.items(), key=lambda x: x[1], reverse=True)
            
            print("\nЧастота упоминания различных марок/типов грузовых автомобилей:")
            for brand, count in sorted_brands[:10]:  # Показываем топ-10
                print(f"- {brand}: {count} упоминаний ({count/total_calls*100:.1f}% звонков)")
            
        else:
            print("Невозможно проанализировать связь с грузовыми автомобилями - колонка с текстом не найдена")
    
    except Exception as e:
        print(f"Ошибка при анализе данных: {e}")

if __name__ == "__main__":
    main()