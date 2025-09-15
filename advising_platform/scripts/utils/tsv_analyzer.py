#!/usr/bin/env python3
"""
Анализатор данных TSV-файла Wazzup24 с ручной обработкой строк.
"""

import re
import json
from datetime import datetime
from collections import Counter, defaultdict

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
    """
    Определяет блокеры в тексте сообщения.
    
    Args:
        text: Текст сообщения
        blockers: Список блокеров для проверки
    
    Returns:
        Список найденных блокеров
    """
    if not isinstance(text, str) or not text:
        return []
    
    text = text.lower()
    found_blockers = []
    
    for blocker in blockers:
        for keyword in blocker['keywords']:
            if keyword.lower() in text:
                found_blockers.append(blocker['category'])
                break
    
    return found_blockers

def parse_tsv_line(line, headers=None):
    """
    Разбирает строку TSV-файла на поля.
    
    Args:
        line: Строка TSV-файла
        headers: Заголовки столбцов (если None, возвращается список полей)
    
    Returns:
        Словарь {'имя_поля': 'значение'} или список полей, если headers=None
    """
    if not line:
        return {}
    
    # Разбиваем строку по табуляции, обрабатывая кавычки
    fields = []
    field = ""
    in_quotes = False
    
    for char in line:
        if char == '"':
            in_quotes = not in_quotes
            field += char
        elif char == '\t' and not in_quotes:
            fields.append(field)
            field = ""
        else:
            field += char
    
    # Добавляем последнее поле
    fields.append(field)
    
    if not headers:
        return fields
    
    # Создаем словарь {имя_поля: значение}
    result = {}
    for i, header in enumerate(headers):
        if i < len(fields):
            result[header] = fields[i]
        else:
            result[header] = ""
    
    return result

def main():
    # Пути к файлам
    file_paths = [
        'attached_assets/2025-04-30 when user or operator send message in wazzup  - lavsit wazzup24.tsv',
        'attached_assets/2024.05.19_when user or operator send message in wazzup  - lavsit wazzup24.tsv'
    ]
    
    # Попытка загрузки данных из каждого файла
    messages = []
    headers = None
    
    for file_path in file_paths:
        try:
            print(f"Попытка загрузки данных из файла: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                if not lines:
                    print(f"Файл {file_path} пуст")
                    continue
                
                # Первая строка - заголовки
                headers = parse_tsv_line(lines[0])
                print(f"Найдено {len(headers)} заголовков")
                
                # Обрабатываем сообщения
                for i, line in enumerate(lines[1:], 1):
                    try:
                        message = parse_tsv_line(line, headers)
                        if message:
                            messages.append(message)
                    except Exception as e:
                        print(f"Ошибка при обработке строки {i}: {str(e)}")
                
                print(f"Загружено {len(messages)} сообщений из {file_path}")
                
                # Если удалось загрузить сообщения, прекращаем попытки
                if messages:
                    break
        except Exception as e:
            print(f"Ошибка при загрузке файла {file_path}: {str(e)}")
    
    if not messages:
        print("Не удалось загрузить данные.")
        return
    
    # Фильтруем сообщения от клиентов (не от операторов)
    client_messages = []
    for message in messages:
        # Проверяем, является ли сообщение эхом (от оператора)
        is_echo = message.get('isEcho', '').upper() in ['TRUE', '1', 'YES', 'Y']
        
        # Проверяем имя контакта
        contact_name = message.get('contact.name', '')
        is_operator = any(name in contact_name for name in ['Admin', 'Оператор', 'Менеджер', 'Марина', 'Казьмина'])
        
        # Проверяем имя автора
        author_name = message.get('authorName', '')
        is_author_operator = any(name in author_name for name in ['Admin', 'Оператор', 'Менеджер', 'Марина', 'Казьмина'])
        
        if not is_echo and not is_operator and not is_author_operator:
            client_messages.append(message)
    
    print(f"Найдено {len(client_messages)} сообщений от клиентов")
    
    # Анализ блокеров
    blocker_counts = {blocker['category']: 0 for blocker in BLOCKERS}
    blocker_examples = {blocker['category']: [] for blocker in BLOCKERS}
    
    for message in client_messages:
        text = message.get('text', '')
        date = message.get('dateTime', '').split('T')[0] if 'dateTime' in message else 'Не указана'
        
        blockers_found = identify_blockers(text)
        
        for blocker in blockers_found:
            blocker_counts[blocker] += 1
            
            # Сохраняем примеры (не более 3 для каждого блокера)
            if len(blocker_examples[blocker]) < 3:
                blocker_examples[blocker].append({
                    'text': text,
                    'name': message.get('contact.name', 'Клиент'),
                    'date': date
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
    
    # Создаем отчет
    report = {
        'analysis_date': datetime.now().strftime('%Y-%m-%d'),
        'total_messages': len(client_messages),
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
    try:
        with open('lavsit_blockers_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print("Отчет сохранен в lavsit_blockers_report.json")
    except Exception as e:
        print(f"Ошибка при сохранении отчета: {str(e)}")
    
    # Создаем HTML-отчет
    try:
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
    <p>Всего сообщений клиентов: """ + str(len(client_messages)) + """</p>
    
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
        <p>Для повышения конверсии на сайте Lavsit.ru рекомендуется провести следующие эксперименты:</p>
        <ol>
            <li><strong>Калькулятор сроков доставки</strong> - добавить на страницы товаров интерактивный калькулятор с актуальными сроками доставки и производства</li>
            <li><strong>Подробные характеристики дивана</strong> - добавить больше технических деталей и визуализаций размеров с возможностью сравнения с обычными предметами</li>
            <li><strong>Объяснение цены</strong> - добавить блок "Из чего складывается цена" с разбивкой стоимости по компонентам</li>
            <li><strong>Улучшенное описание гарантии</strong> - сделать раздел о гарантии и послепродажном обслуживании более заметным</li>
            <li><strong>Обновленная система уведомлений</strong> - реализовать автоматические уведомления о статусе производства и доставки</li>
        </ol>
    </div>
</body>
</html>""")
            print("HTML-отчет сохранен в lavsit_blockers_report.html")
    except Exception as e:
        print(f"Ошибка при сохранении HTML-отчета: {str(e)}")

if __name__ == "__main__":
    main()