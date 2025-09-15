#!/usr/bin/env python3
"""
Упрощенный анализатор данных Wazzup24 для клиентов Lavsit.ru.
"""

import pandas as pd
import json
import os
from collections import Counter
from datetime import datetime
import matplotlib.pyplot as plt
from pathlib import Path

# Определение основных блокеров
BLOCKERS = [
    # Неопределенность с доставкой
    {
        "category": "delivery_uncertainty",
        "name": "Неопределенность с доставкой",
        "keywords": [
            "когда доставят", "срок доставки", "доставка задерживается", 
            "перенести доставку", "отложить доставку", "доставка откладывается",
            "не привезли", "задержка доставки", "изменить дату доставки",
            "дату доставки", "перенести выезд"
        ],
        "score": 14.8,
    },
    # Неопределенность характеристик мебели
    {
        "category": "furniture_characteristics_uncertainty",
        "name": "Неопределенность характеристик мебели",
        "keywords": [
            "размер дивана", "высота дивана", "ширина дивана", "длина дивана",
            "габариты", "материал обивки", "ткань", "цвет дивана", "мебельная ткань",
            "характеристики", "параметры", "замена ткани", "каталоги тканей",
            "фактура", "плотность", "мягкость", "жесткость", "механизм",
            "расцветки", "фото дивана", "фотографии дивана", "раскладывается"
        ],
        "score": 13.4,
    },
    # Завышенные ожидания цены
    {
        "category": "price_expectations",
        "name": "Завышенные ожидания цены",
        "keywords": [
            "дорого", "снизить цену", "скидка", "дорогая доставка", "дешевле",
            "акция", "распродажа", "дорогая мебель", "высокая цена", "цена высокая",
            "слишком дорого", "выгодное предложение", "стоимость", "дешевый аналог",
            "сумма заказа", "оплата", "какая цена", "сколько стоит", "не готов платить",
            "дорогостоящая", "первый взнос", "предоплата", "платное хранение", "рассрочка"
        ],
        "score": 12.9,
    },
    # Неопределенность послепродажного обслуживания
    {
        "category": "post_sale_service",
        "name": "Неопределенность послепродажного обслуживания",
        "keywords": [
            "гарантия", "обслуживание", "ремонт", "замена", "возврат", "сервис",
            "гарантийный срок", "обмен", "претензия", "рекламация", "не работает",
            "сломался", "неисправность", "дефект", "поломка", "скрипит", "шатается",
            "пятно", "бракованный", "повреждение", "запах", "царапина", "потертость"
        ],
        "score": 11.7,
    },
    # Долгие сроки изготовления
    {
        "category": "production_timeframes",
        "name": "Долгие сроки изготовления",
        "keywords": [
            "срок изготовления", "долго делают", "долго ждать", "когда будет готово",
            "срок производства", "изготовление затягивается", "задержка производства",
            "когда сделают", "долгий срок", "изготовление мебели", "сроки затягиваются",
            "производство задерживается", "когда изготовят"
        ],
        "score": 10.5,
    }
]

def identify_blockers(text, blockers=BLOCKERS):
    """Определяет блокеры в тексте сообщения."""
    if not isinstance(text, str):
        return []
    
    text = text.lower()
    found_blockers = []
    
    for blocker in blockers:
        for keyword in blocker['keywords']:
            if keyword.lower() in text:
                found_blockers.append(blocker['category'])
                break
    
    return found_blockers

def main():
    # Путь к файлу с данными
    file_path = 'attached_assets/2025-04-30 when user or operator send message in wazzup  - lavsit wazzup24.tsv'
    old_file_path = 'attached_assets/2024.05.19_when user or operator send message in wazzup  - lavsit wazzup24.tsv'
    
    # Загрузка данных с параметром low_memory=False для смешанных типов данных
    try:
        print(f"Попытка загрузки данных из файла: {file_path}")
        data = pd.read_csv(file_path, sep='\t', encoding='utf-8', low_memory=False)
        print(f"Загружено сообщений: {len(data)}")
    except Exception as e:
        print(f"Ошибка при загрузке данных из {file_path}: {str(e)}")
        data = None
    
    if data is None or len(data) == 0:
        try:
            print(f"Попытка загрузки из альтернативного файла: {old_file_path}")
            data = pd.read_csv(old_file_path, sep='\t', encoding='utf-8', low_memory=False)
            print(f"Загружено сообщений: {len(data)}")
        except Exception as e:
            print(f"Ошибка при загрузке данных из {old_file_path}: {str(e)}")
            data = None
    
    if data is None or len(data) == 0:
        print("Не удалось загрузить данные.")
        return
    
    # Предобработка данных
    try:
        # Преобразуем isEcho в логический тип
        data['isEcho_bool'] = data['isEcho'].astype(str).str.upper().isin(['TRUE', '1', 'YES', 'Y'])
        
        # Фильтруем только сообщения от клиентов (не от операторов)
        client_data = data[
            (~data['isEcho_bool']) & 
            (~data['contact.name'].astype(str).str.contains('Admin|Оператор|Менеджер|Марина|Казьмина', 
                                                          na=False, case=False, regex=True))
        ].copy()
        
        print(f"Найдено сообщений от клиентов: {len(client_data)}")
        
        # Анализ блокеров в сообщениях
        blocker_counts = {blocker['category']: 0 for blocker in BLOCKERS}
        blocker_examples = {blocker['category']: [] for blocker in BLOCKERS}
        
        # Обрабатываем каждое сообщение
        for idx, row in client_data.iterrows():
            if 'text' in row and isinstance(row['text'], str):
                blockers_found = identify_blockers(row['text'])
                
                # Увеличиваем счетчики блокеров
                for blocker in blockers_found:
                    blocker_counts[blocker] += 1
                    
                    # Сохраняем примеры (не более 3 для каждого блокера)
                    if len(blocker_examples[blocker]) < 3:
                        blocker_examples[blocker].append({
                            'text': row['text'],
                            'name': row['contact.name'] if 'contact.name' in row else 'Клиент',
                            'date': row['dateTime'].split('T')[0] if 'dateTime' in row else 'Не указана'
                        })
        
        # Выводим результаты
        print("\n=== Статистика блокеров покупки ===")
        for blocker in BLOCKERS:
            category = blocker['category']
            count = blocker_counts[category]
            print(f"{blocker['name']}: {count} сообщений (влияние: {blocker['score']})")
            
            print("  Примеры сообщений:")
            for example in blocker_examples[category]:
                print(f"    - \"{example['text']}\" ({example['name']}, {example['date']})")
            print()
        
        # Создаем простой JSON-отчет
        report = {
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'total_messages': len(client_data),
            'blockers': []
        }
        
        for blocker in BLOCKERS:
            category = blocker['category']
            report['blockers'].append({
                'category': category,
                'name': blocker['name'],
                'count': blocker_counts[category],
                'score': blocker['score'],
                'examples': blocker_examples[category]
            })
        
        # Сохраняем отчет в JSON
        with open('lavsit_blockers_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print("Отчет сохранен в lavsit_blockers_report.json")
        
        # Создаем простой HTML-отчет
        with open('lavsit_blockers_report.html', 'w', encoding='utf-8') as f:
            f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Отчет по блокерам покупки Lavsit.ru</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1, h2 { color: #333; }
        .blocker { margin-bottom: 20px; padding: 15px; border-left: 4px solid #3498db; background-color: #f8f9fa; }
        .example { margin: 10px 0; padding: 10px; background-color: #f0f0f0; border-left: 2px solid #7f8c8d; }
        .meta { color: #7f8c8d; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>Отчет по блокерам покупки Lavsit.ru</h1>
    <p>Дата анализа: """ + datetime.now().strftime('%Y-%m-%d') + """</p>
    <p>Всего сообщений клиентов: """ + str(len(client_data)) + """</p>
    
    <h2>Блокеры покупки (по частоте упоминания)</h2>
""")
            
            # Сортируем блокеры по количеству сообщений
            sorted_blockers = sorted(BLOCKERS, key=lambda x: blocker_counts[x['category']], reverse=True)
            
            for blocker in sorted_blockers:
                category = blocker['category']
                f.write(f"""
    <div class="blocker">
        <h3>{blocker['name']} ({blocker_counts[category]} сообщений)</h3>
        <p>Оценка влияния: {blocker['score']}</p>
        <h4>Примеры сообщений:</h4>
""")
                
                for example in blocker_examples[category]:
                    f.write(f"""
        <div class="example">
            <p>"{example['text']}"</p>
            <p class="meta">Клиент: {example['name']}, Дата: {example['date']}</p>
        </div>
""")
                
                f.write("""
    </div>
""")
            
            f.write("""
    <div style="margin-top: 30px; padding: 15px; background-color: #e7f5fe; border-radius: 5px;">
        <h2>Выводы и рекомендации</h2>
        <ol>
            <li>Улучшить коммуникацию по срокам доставки и производства</li>
            <li>Добавить более подробные характеристики мебели на сайт</li>
            <li>Пересмотреть ценовую политику или более четко объяснять формирование цены</li>
            <li>Усилить информацию о гарантийном обслуживании</li>
            <li>Оптимизировать процесс производства или коммуникацию о сроках</li>
        </ol>
    </div>
</body>
</html>""")

        print("HTML-отчет сохранен в lavsit_blockers_report.html")
        
    except Exception as e:
        print(f"Ошибка при анализе данных: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()