#!/usr/bin/env python3
"""
Скрипт для извлечения конкретных примеров звонков для каждого из 5 ключевых блокеров B2B-сегмента
из базы звонков avtoall.ru
"""

import pandas as pd
import re
import json

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

# Блокеры и ключевые слова для их идентификации
BLOCKERS = {
    "tech_info": {
        "name": "Недостаток технической информации",
        "keywords": [
            'совместимость', 'подходит', 'характеристик', 'технические данные', 'спецификаци', 
            'детали', 'номер детали', 'каталог', 'не знаю', 'информаци', 'не могу сказать', 
            'уточнить', 'проверить', 'посмотреть'
        ],
    },
    "availability": {
        "name": "Проблемы с наличием",
        "keywords": [
            'наличие', 'под заказ', 'нет в наличии', 'отсутствует', 'закончил', 'нет на складе',
            'придется подождать', 'не осталось', 'в пути', 'временно нет', 'поставка',
            'не привозят', 'нет такого'
        ],
    },
    "logistics": {
        "name": "Логистические барьеры",
        "keywords": [
            'доставка', 'заберу', 'привезти', 'курьер', 'самовывоз', 'транспорт', 'логистика',
            'перевозка', 'срочно', 'быстро', 'срок доставки', 'завтра', 'сегодня', 'пункт выдачи',
            'магазин', 'склад', 'территориально', 'адрес'
        ],
    },
    "b2b_process": {
        "name": "Отсутствие B2B-процессов",
        "keywords": [
            'юридическое лицо', 'юрлицо', 'компания', 'фирма', 'предприятие', 'организация',
            'безнал', 'безналичный', 'счет', 'документы', 'накладная', 'отчетность', 'договор',
            'оптом', 'скидка', 'постоянный клиент', 'корпоратив', 'партнер', 'сотрудничество'
        ],
    },
    "operator_knowledge": {
        "name": "Неподготовленность операторов",
        "keywords": [
            'не могу сказать', 'не знаю', 'затрудняюсь', 'сложно сказать', 'надо уточнить',
            'спрошу у', 'узнаю', 'переспрошу', 'не уверен', 'нет информации', 'не компетентен',
            'не в курсе', 'впервые слышу', 'не подскажу', 'не разбираюсь', 'впервые сталкиваюсь'
        ],
    }
}

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

def contains_blocker_keywords(text, blocker_keywords):
    """Проверяет, содержит ли текст ключевые слова блокера"""
    if not isinstance(text, str):
        return False
    
    text_lower = text.lower()
    
    for keyword in blocker_keywords:
        if keyword.lower() in text_lower:
            return True
    
    return False

def main():
    """Основная функция анализа"""
    print("Загрузка данных из файла...")
    try:
        # Загружаем данные
        df = pd.read_csv(DATA_FILE, sep='\t', encoding='utf-8')
        print(f"Загружено записей: {len(df)}")
        
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
        
        # Собираем примеры для каждого блокера
        examples = {}
        
        for blocker_key, blocker_info in BLOCKERS.items():
            examples[blocker_key] = []
            blocker_name = blocker_info["name"]
            blocker_keywords = blocker_info["keywords"]
            
            print(f"\nИщем примеры для блокера: {blocker_name}")
            
            for idx, row in df.iterrows():
                text = str(row[text_col]) if not pd.isna(row[text_col]) else ""
                
                # Проверяем, что звонок связан с грузовыми автомобилями
                if is_truck_related(text) and contains_blocker_keywords(text, blocker_keywords):
                    # Добавляем пример
                    examples[blocker_key].append({
                        'id': int(idx),
                        'text': text[:800] + "..." if len(text) > 800 else text,  # Ограничиваем длину для читаемости
                        'blocker': blocker_name
                    })
            
            print(f"Найдено примеров: {len(examples[blocker_key])}")
        
        # Выводим примеры для каждого блокера
        print("\n\n===== ПРИМЕРЫ ДЛЯ КАЖДОГО БЛОКЕРА =====\n")
        
        for blocker_key, blocker_examples in examples.items():
            blocker_name = BLOCKERS[blocker_key]["name"]
            print(f"\n## {blocker_name}\n")
            
            # Сортируем примеры по длине текста (предпочитаем более короткие и понятные примеры)
            sorted_examples = sorted(blocker_examples, key=lambda x: len(x['text']))
            
            # Выводим до 4 примеров
            for i, example in enumerate(sorted_examples[:4], 1):
                print(f"### Пример {i} (ID звонка: {example['id']})")
                print(f"{example['text']}\n")
        
        # Сохраняем результаты в JSON для дальнейшего использования
        with open('b2b_truck_examples.json', 'w', encoding='utf-8') as f:
            json.dump(examples, f, ensure_ascii=False, indent=2)
        
        print("Примеры сохранены в файл b2b_truck_examples.json")
                
    except Exception as e:
        print(f"Ошибка при анализе данных: {e}")

if __name__ == "__main__":
    main()