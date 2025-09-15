#!/usr/bin/env python3
"""
Анализатор данных Wazzup24 для клиентов Lavsit.ru.

Обрабатывает данные чатов из Wazzup24 и выявляет основные блокеры покупки.
"""

import pandas as pd
import re
import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timedelta
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

def load_data(file_path):
    """
    Загружает данные из TSV-файла Wazzup24.
    
    Args:
        file_path: Путь к файлу данных
        
    Returns:
        DataFrame с данными
    """
    try:
        # Проверяем формат файла
        if file_path.endswith('.tsv'):
            df = pd.read_csv(file_path, sep='\t', encoding='utf-8')
        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_path, encoding='utf-8')
        else:
            raise ValueError(f"Неподдерживаемый формат файла: {file_path}")
        
        print(f"Загружено сообщений: {len(df)}")
        return df
    except Exception as e:
        print(f"Ошибка при загрузке данных: {str(e)}")
        return None

def preprocess_data(df):
    """
    Предобработка данных перед анализом.
    
    Args:
        df: DataFrame с данными
        
    Returns:
        Предобработанный DataFrame
    """
    if df is None or len(df) == 0:
        return None
    
    # Преобразование даты и времени с обработкой ошибок
    try:
        # Сначала очистим поля dateTime от потенциальных проблем
        df['dateTime_clean'] = df['dateTime'].astype(str).str.replace(r'[^\d\-T:\.Z]', '', regex=True)
        
        # Попробуем преобразовать очищенную дату
        df['dateTime'] = pd.to_datetime(df['dateTime_clean'], errors='coerce')
        
        # Если есть NaT значения, заменим их на текущую дату
        if df['dateTime'].isna().any():
            current_date = pd.Timestamp.now()
            df.loc[df['dateTime'].isna(), 'dateTime'] = current_date
            print(f"Внимание: {df['dateTime'].isna().sum()} записей с неправильным форматом даты заменены на текущую дату")
        
        # Извлекаем дату
        df['date'] = df['dateTime'].dt.date
        
        # Удаляем вспомогательный столбец
        df = df.drop(columns=['dateTime_clean'])
    except Exception as e:
        print(f"Ошибка при обработке даты: {str(e)}")
        # Если не удалось обработать дату, создаем поле date как строку
        if 'dateTime' in df.columns:
            df['date'] = df['dateTime'].astype(str).str.split('T').str[0]
    
    # Оставляем только входящие сообщения от клиентов
    try:
        # Конвертируем колонку isEcho в булев тип с обработкой различных форматов
        df['isEcho_bool'] = df['isEcho'].astype(str).str.upper().isin(['TRUE', '1', 'YES', 'Y'])
        
        client_messages = df[
            (~df['isEcho_bool']) & 
            (~df['contact.name'].astype(str).str.contains('Admin|Оператор|Менеджер|Марина|Казьмина', 
                                                        na=False, case=False, regex=True)) &
            (~df['authorName'].astype(str).str.contains('Admin|Оператор|Менеджер|Марина|Казьмина', 
                                                      na=False, case=False, regex=True))
        ].copy()
        
        # Удаляем вспомогательный столбец
        client_messages = client_messages.drop(columns=['isEcho_bool'])
        
        print(f"Входящих сообщений от клиентов: {len(client_messages)}")
        return client_messages
    except Exception as e:
        print(f"Ошибка при предобработке данных: {str(e)}")
        return df

def identify_blockers(text, blockers=BLOCKERS):
    """
    Определяет блокеры в тексте сообщения.
    
    Args:
        text: Текст сообщения
        blockers: Список блокеров для проверки
        
    Returns:
        Список найденных блокеров
    """
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

def analyze_blockers_over_time(df, blockers=BLOCKERS):
    """
    Анализирует частоту появления блокеров по времени.
    
    Args:
        df: DataFrame с данными
        blockers: Список блокеров для анализа
        
    Returns:
        DataFrame с частотой блокеров по дням
    """
    if df is None or len(df) == 0:
        return None
    
    # Создаем столбцы для каждого блокера
    for blocker in blockers:
        category = blocker['category']
        df[category] = df['text'].apply(
            lambda x: 1 if category in identify_blockers(x, blockers) else 0
        )
    
    # Группируем по дате и считаем количество блокеров
    blockers_by_date = df.groupby('date')[
        [blocker['category'] for blocker in blockers]
    ].sum().reset_index()
    
    # Добавляем общее количество сообщений в день
    messages_per_day = df.groupby('date').size().reset_index(name='total_messages')
    blockers_by_date = blockers_by_date.merge(messages_per_day, on='date')
    
    return blockers_by_date

def extract_blocker_examples(df, blockers=BLOCKERS, max_examples=3):
    """
    Извлекает примеры сообщений для каждого блокера.
    
    Args:
        df: DataFrame с данными
        blockers: Список блокеров для анализа
        max_examples: Максимальное количество примеров для каждого блокера
        
    Returns:
        Словарь с примерами сообщений для каждого блокера
    """
    if df is None or len(df) == 0:
        return {}
    
    examples = {}
    
    for blocker in blockers:
        category = blocker['category']
        examples[category] = []
        
        # Применяем функцию идентификации блокеров к каждому сообщению
        df['contains_blocker'] = df['text'].apply(
            lambda x: category in identify_blockers(x, blockers)
        )
        
        # Фильтруем сообщения, содержащие данный блокер
        blocker_messages = df[df['contains_blocker'] == True]
        
        # Выбираем примеры сообщений
        if len(blocker_messages) > 0:
            # Сортируем по длине текста, чтобы выбрать наиболее информативные примеры
            blocker_messages = blocker_messages.sort_values(
                by='text', key=lambda x: x.str.len(), ascending=False
            )
            
            for _, row in blocker_messages.head(max_examples).iterrows():
                examples[category].append({
                    'text': row['text'],
                    'date': row['date'].strftime('%Y-%m-%d') if hasattr(row['date'], 'strftime') else str(row['date']),
                    'name': row['contact.name'] if 'contact.name' in row else 'Клиент'
                })
    
    return examples

def generate_weekly_data(blockers_by_date):
    """
    Генерирует данные по неделям для построения графика.
    
    Args:
        blockers_by_date: DataFrame с данными по дням
        
    Returns:
        DataFrame с данными по неделям
    """
    if blockers_by_date is None or len(blockers_by_date) == 0:
        return None
    
    # Преобразуем дату в формат datetime, если она еще не в этом формате
    if not pd.api.types.is_datetime64_any_dtype(blockers_by_date['date']):
        blockers_by_date['date'] = pd.to_datetime(blockers_by_date['date'])
    
    # Добавляем номер недели
    blockers_by_date['week'] = blockers_by_date['date'].dt.isocalendar().week
    blockers_by_date['year'] = blockers_by_date['date'].dt.isocalendar().year
    
    # Создаем уникальный идентификатор для недели (год + неделя)
    blockers_by_date['year_week'] = blockers_by_date['year'].astype(str) + '-' + blockers_by_date['week'].astype(str)
    
    # Группируем по неделе
    blockers_by_week = blockers_by_date.groupby('year_week')[
        [col for col in blockers_by_date.columns if col not in ['date', 'week', 'year', 'year_week']]
    ].sum().reset_index()
    
    # Сортируем по году и неделе
    blockers_by_week['year'] = blockers_by_week['year_week'].str.split('-').str[0].astype(int)
    blockers_by_week['week'] = blockers_by_week['year_week'].str.split('-').str[1].astype(int)
    blockers_by_week = blockers_by_week.sort_values(by=['year', 'week'])
    
    return blockers_by_week

def generate_report(data, blockers_by_time, examples, output_file='lavsit_wazzup_report.json'):
    """
    Генерирует отчет по результатам анализа.
    
    Args:
        data: DataFrame с исходными данными
        blockers_by_time: DataFrame с данными по времени
        examples: Словарь с примерами сообщений для каждого блокера
        output_file: Путь к выходному файлу
        
    Returns:
        Словарь с данными отчета
    """
    if data is None or len(data) == 0:
        return None
    
    # Генерируем недельные данные
    weekly_data = generate_weekly_data(blockers_by_time)
    
    # Создаем отчет
    report = {
        'analysis_date': datetime.now().strftime('%Y-%m-%d'),
        'total_messages': len(data),
        'date_range': {
            'start': data['date'].min().strftime('%Y-%m-%d') if hasattr(data['date'].min(), 'strftime') else str(data['date'].min()),
            'end': data['date'].max().strftime('%Y-%m-%d') if hasattr(data['date'].max(), 'strftime') else str(data['date'].max())
        },
        'blockers': [],
        'weekly_data': []
    }
    
    # Добавляем информацию о блокерах
    for blocker in BLOCKERS:
        category = blocker['category']
        
        # Подсчитываем общее количество сообщений с этим блокером
        if category in blockers_by_time.columns:
            blocker_count = blockers_by_time[category].sum()
        else:
            blocker_count = 0
        
        report['blockers'].append({
            'category': category,
            'name': blocker['name'],
            'count': int(blocker_count),
            'score': blocker['score'],
            'examples': examples.get(category, [])
        })
    
    # Сортируем блокеры по количеству сообщений
    report['blockers'] = sorted(report['blockers'], key=lambda x: x['count'], reverse=True)
    
    # Добавляем недельные данные
    if weekly_data is not None:
        for _, row in weekly_data.iterrows():
            week_data = {
                'week': f"{row['year']}-W{row['week']}",
                'blockers': {}
            }
            
            for blocker in BLOCKERS:
                category = blocker['category']
                if category in row:
                    week_data['blockers'][category] = int(row[category])
            
            week_data['total_messages'] = int(row['total_messages'])
            report['weekly_data'].append(week_data)
    
    # Сохраняем отчет в JSON-файл
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"Отчет сохранен в {output_file}")
    except Exception as e:
        print(f"Ошибка при сохранении отчета: {str(e)}")
    
    return report

def plot_blockers_by_week(weekly_data, blockers=BLOCKERS, output_file='lavsit_blockers_by_week.png'):
    """
    Строит график блокеров по неделям.
    
    Args:
        weekly_data: DataFrame с данными по неделям
        blockers: Список блокеров для анализа
        output_file: Путь к выходному файлу
        
    Returns:
        None
    """
    if weekly_data is None or len(weekly_data) == 0:
        return
    
    plt.figure(figsize=(12, 8))
    
    # Создаем график для каждого блокера
    for blocker in blockers:
        category = blocker['category']
        if category in weekly_data.columns:
            plt.plot(
                weekly_data['year_week'], 
                weekly_data[category], 
                label=blocker['name'],
                marker='o'
            )
    
    plt.title('Динамика блокеров по неделям')
    plt.xlabel('Неделя')
    plt.ylabel('Количество сообщений')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    # Сохраняем график
    try:
        plt.savefig(output_file)
        print(f"График сохранен в {output_file}")
    except Exception as e:
        print(f"Ошибка при сохранении графика: {str(e)}")
    
    plt.close()

def generate_html_report(report_data, output_file='lavsit-wazzup-report.html'):
    """
    Генерирует HTML-отчет по результатам анализа.
    
    Args:
        report_data: Словарь с данными отчета
        output_file: Путь к выходному файлу
        
    Returns:
        None
    """
    if report_data is None:
        return
    
    # Подготовка данных для HTML-отчета
    blockers_html = ""
    for blocker in report_data['blockers']:
        examples_html = ""
        for example in blocker['examples']:
            examples_html += f"""
            <div class="example-item">
                <p>"{example['text']}"</p>
                <p class="example-meta">Клиент: {example['name']}, Дата: {example['date']}</p>
            </div>
            """
        
        blockers_html += f"""
        <div class="blocker-card">
            <h3>{blocker['name']} <span class="badge">{blocker['count']}</span></h3>
            <p>Оценка влияния: {blocker['score']}</p>
            <div class="examples">
                <h4>Примеры сообщений:</h4>
                {examples_html if examples_html else "<p>Нет примеров</p>"}
            </div>
        </div>
        """
    
    # Подготовка данных для графиков
    weeks = [week_data['week'] for week_data in report_data['weekly_data']]
    blocker_categories = [blocker['category'] for blocker in report_data['blockers']]
    blocker_names = [blocker['name'] for blocker in report_data['blockers']]
    
    blocker_data = {category: [] for category in blocker_categories}
    blocker_data['total_messages'] = []
    
    for week_data in report_data['weekly_data']:
        for category in blocker_categories:
            blocker_data[category].append(week_data['blockers'].get(category, 0))
        blocker_data['total_messages'].append(week_data['total_messages'])
    
    weeks_json = json.dumps(weeks)
    blocker_categories_json = json.dumps(blocker_categories)
    blocker_names_json = json.dumps(blocker_names)
    blocker_data_json = json.dumps(blocker_data)
    
    # HTML-шаблон как строка, а не как многострочный литерал
    html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Отчет по блокерам покупки Lavsit.ru</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        h1 {{
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        .summary-box {{
            background-color: #ecf0f1;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
        }}
        .blocker-card {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            padding: 20px;
            position: relative;
            overflow: hidden;
        }}
        .blocker-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 6px;
            height: 100%;
            background-color: #3498db;
        }}
        .examples {{
            margin-top: 15px;
            background-color: #f8f9fa;
            border-radius: 4px;
            padding: 10px;
        }}
        .example-item {{
            border-left: 2px solid #7f8c8d;
            padding-left: 15px;
            margin-bottom: 10px;
        }}
        .example-meta {{
            color: #7f8c8d;
            font-size: 0.85em;
            margin-top: 5px;
        }}
        .chart-container {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 20px;
            margin-top: 30px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            background-color: #3498db;
            color: white;
            font-size: 0.85em;
        }}
        .chart-tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
        }}
        .chart-tab {{
            padding: 8px 15px;
            background-color: #eee;
            border-radius: 4px;
            cursor: pointer;
            font-weight: 500;
        }}
        .chart-tab.active {{
            background-color: #3498db;
            color: white;
        }}
        .chart {{
            width: 100%;
            height: 400px;
        }}
        .conclusion {{
            margin-top: 30px;
            padding: 20px;
            background-color: #e8f4fd;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h1>Отчет по блокерам покупки Lavsit.ru</h1>
    
    <div class="summary-box">
        <p><strong>Дата анализа:</strong> {report_data['analysis_date']}</p>
        <p><strong>Период:</strong> {report_data['date_range']['start']} - {report_data['date_range']['end']}</p>
        <p><strong>Всего сообщений:</strong> {report_data['total_messages']}</p>
    </div>
    
    <h2>Рейтинг блокеров покупки</h2>
    
    {blockers_html}
    
    <div class="chart-container">
        <h2>Динамика блокеров по неделям</h2>
        <div class="chart-tabs">
            <div class="chart-tab active" onclick="showChart('absolute')">Абсолютные значения</div>
            <div class="chart-tab" onclick="showChart('percentage')">Проценты</div>
        </div>
        <canvas id="blockersChart" class="chart"></canvas>
    </div>
    
    <div class="chart-container">
        <h2>Распределение блокеров</h2>
        <canvas id="pieChart" class="chart" style="height: 300px;"></canvas>
    </div>
    
    <div class="conclusion">
        <h3>Выводы и рекомендации</h3>
        <p>На основе анализа сообщений клиентов в чатах Wazzup24, выделено 5 основных блокеров, препятствующих покупке мебели в Lavsit.ru. Для повышения конверсии рекомендуется:</p>
        <ol>
            <li>Улучшить коммуникацию по срокам доставки и производства</li>
            <li>Добавить более подробные характеристики мебели на сайт</li>
            <li>Пересмотреть ценовую политику или более четко объяснять формирование цены</li>
            <li>Усилить информацию о гарантийном обслуживании</li>
            <li>Оптимизировать процесс производства или коммуникацию о сроках</li>
        </ol>
    </div>
    
    <script>
        // Данные для графиков
        const weeks = {weeks_json};
        const blockerCategories = {blocker_categories_json};
        const blockerNames = {blocker_names_json};
        const blockerData = {blocker_data_json};
        const blockerColors = [
            'rgba(52, 152, 219, 0.7)',
            'rgba(231, 76, 60, 0.7)',
            'rgba(241, 196, 15, 0.7)',
            'rgba(46, 204, 113, 0.7)',
            'rgba(155, 89, 182, 0.7)'
        ];
        
        // График по неделям
        const ctx = document.getElementById('blockersChart').getContext('2d');
        let blockersChart;
        
        function showChart(type) {{
            // Активируем выбранный таб
            document.querySelectorAll('.chart-tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            document.querySelector(`.chart-tab[onclick*="${{type}}"]`).classList.add('active');
            
            // Подготавливаем данные
            const datasets = [];
            
            blockerCategories.forEach((category, i) => {{
                const data = type === 'absolute' 
                    ? blockerData[category] 
                    : blockerData[category].map((value, j) => {{
                        return blockerData.total_messages[j] > 0 
                            ? (value / blockerData.total_messages[j] * 100).toFixed(1)
                            : 0;
                    }});
                
                datasets.push({{
                    label: blockerNames[i],
                    data: data,
                    borderColor: blockerColors[i],
                    backgroundColor: blockerColors[i].replace('0.7', '0.2'),
                    borderWidth: 2,
                    pointRadius: 4,
                    tension: 0.1
                }});
            }});
            
            // Уничтожаем предыдущий график, если он существует
            if (blockersChart) {{
                blockersChart.destroy();
            }}
            
            // Создаем новый график
            blockersChart = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: weeks,
                    datasets: datasets
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            title: {{
                                display: true,
                                text: type === 'absolute' ? 'Количество сообщений' : 'Процент от всех сообщений'
                            }}
                        }},
                        x: {{
                            title: {{
                                display: true,
                                text: 'Неделя'
                            }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            position: 'top',
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    let label = context.dataset.label || '';
                                    if (label) {{
                                        label += ': ';
                                    }}
                                    label += context.parsed.y;
                                    if (type === 'percentage') {{
                                        label += '%';
                                    }}
                                    return label;
                                }}
                            }}
                        }}
                    }}
                }}
            }});
        }}
        
        // Круговая диаграмма
        const ctxPie = document.getElementById('pieChart').getContext('2d');
        const totalBlockers = blockerCategories.reduce((sum, category) => {{
            return sum + blockerData[category].reduce((a, b) => a + b, 0);
        }}, 0);
        
        const pieData = blockerCategories.map((category, i) => {{
            return blockerData[category].reduce((a, b) => a + b, 0);
        }});
        
        new Chart(ctxPie, {{
            type: 'pie',
            data: {{
                labels: blockerNames,
                datasets: [{{
                    data: pieData,
                    backgroundColor: blockerColors,
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'right',
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                const value = context.parsed;
                                const percentage = Math.round(value / totalBlockers * 100);
                                return `${{context.label}}: ${{value}} (${{percentage}}%)`;
                            }}
                        }}
                    }}
                }}
            }}
        }});
        
        // Инициализация графика при загрузке
        window.onload = function() {{
            showChart('absolute');
        }};
    </script>
</body>
</html>
    """
    
    # Сохранение HTML-отчета
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML-отчет сохранен в {output_file}")
    except Exception as e:
        print(f"Ошибка при сохранении HTML-отчета: {str(e)}")
    <body>
        <h1>Отчет по блокерам покупки Lavsit.ru</h1>
        
        <div class="summary-box">
            <p><strong>Дата анализа:</strong> {analysis_date}</p>
            <p><strong>Период:</strong> {date_start} - {date_end}</p>
            <p><strong>Всего сообщений:</strong> {total_messages}</p>
        </div>
        
        <h2>Рейтинг блокеров покупки</h2>
        
        {blockers_html}
        
        <div class="chart-container">
            <h2>Динамика блокеров по неделям</h2>
            <div class="chart-tabs">
                <div class="chart-tab active" onclick="showChart('absolute')">Абсолютные значения</div>
                <div class="chart-tab" onclick="showChart('percentage')">Проценты</div>
            </div>
            <canvas id="blockersChart" class="chart"></canvas>
        </div>
        
        <div class="chart-container">
            <h2>Распределение блокеров</h2>
            <canvas id="pieChart" class="chart" style="height: 300px;"></canvas>
        </div>
        
        <div class="conclusion">
            <h3>Выводы и рекомендации</h3>
            <p>На основе анализа сообщений клиентов в чатах Wazzup24, выделено 5 основных блокеров, препятствующих покупке мебели в Lavsit.ru. Для повышения конверсии рекомендуется:</p>
            <ol>
                <li>Улучшить коммуникацию по срокам доставки и производства</li>
                <li>Добавить более подробные характеристики мебели на сайт</li>
                <li>Пересмотреть ценовую политику или более четко объяснять формирование цены</li>
                <li>Усилить информацию о гарантийном обслуживании</li>
                <li>Оптимизировать процесс производства или коммуникацию о сроках</li>
            </ol>
        </div>
        
        <script>
            // Данные для графиков
            const weeks = {weeks_json};
            const blockerCategories = {blocker_categories_json};
            const blockerNames = {blocker_names_json};
            const blockerData = {blocker_data_json};
            const blockerColors = [
                'rgba(52, 152, 219, 0.7)',
                'rgba(231, 76, 60, 0.7)',
                'rgba(241, 196, 15, 0.7)',
                'rgba(46, 204, 113, 0.7)',
                'rgba(155, 89, 182, 0.7)'
            ];
            
            // График по неделям
            const ctx = document.getElementById('blockersChart').getContext('2d');
            let blockersChart;
            
            function showChart(type) {
                // Активируем выбранный таб
                document.querySelectorAll('.chart-tab').forEach(tab => {
                    tab.classList.remove('active');
                });
                document.querySelector(`.chart-tab[onclick*="${type}"]`).classList.add('active');
                
                // Подготавливаем данные
                const datasets = [];
                
                blockerCategories.forEach((category, i) => {
                    const data = type === 'absolute' 
                        ? blockerData[category] 
                        : blockerData[category].map((value, j) => {
                            return blockerData.total_messages[j] > 0 
                                ? (value / blockerData.total_messages[j] * 100).toFixed(1)
                                : 0;
                        });
                    
                    datasets.push({
                        label: blockerNames[i],
                        data: data,
                        borderColor: blockerColors[i],
                        backgroundColor: blockerColors[i].replace('0.7', '0.2'),
                        borderWidth: 2,
                        pointRadius: 4,
                        tension: 0.1
                    });
                });
                
                // Уничтожаем предыдущий график, если он существует
                if (blockersChart) {
                    blockersChart.destroy();
                }
                
                // Создаем новый график
                blockersChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: weeks,
                        datasets: datasets
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: type === 'absolute' ? 'Количество сообщений' : 'Процент от всех сообщений'
                                }
                            },
                            x: {
                                title: {
                                    display: true,
                                    text: 'Неделя'
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                position: 'top',
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        let label = context.dataset.label || '';
                                        if (label) {
                                            label += ': ';
                                        }
                                        label += context.parsed.y;
                                        if (type === 'percentage') {
                                            label += '%';
                                        }
                                        return label;
                                    }
                                }
                            }
                        }
                    }
                });
            }
            
            // Круговая диаграмма
            const ctxPie = document.getElementById('pieChart').getContext('2d');
            const totalBlockers = blockerCategories.reduce((sum, category) => {
                return sum + blockerData[category].reduce((a, b) => a + b, 0);
            }, 0);
            
            const pieData = blockerCategories.map((category, i) => {
                return blockerData[category].reduce((a, b) => a + b, 0);
            });
            
            new Chart(ctxPie, {
                type: 'pie',
                data: {
                    labels: blockerNames,
                    datasets: [{
                        data: pieData,
                        backgroundColor: blockerColors,
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'right',
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const value = context.parsed;
                                    const percentage = Math.round(value / totalBlockers * 100);
                                    return `${context.label}: ${value} (${percentage}%)`;
                                }
                            }
                        }
                    }
                }
            });
            
            // Инициализация графика при загрузке
            window.onload = function() {
                showChart('absolute');
            };
        </script>
    </body>
    </html>
    """
    
    # Подготовка данных для HTML-отчета
    blockers_html = ""
    for blocker in report_data['blockers']:
        examples_html = ""
        for example in blocker['examples']:
            examples_html += f"""
            <div class="example-item">
                <p>"{example['text']}"</p>
                <p class="example-meta">Клиент: {example['name']}, Дата: {example['date']}</p>
            </div>
            """
        
        blockers_html += f"""
        <div class="blocker-card">
            <h3>{blocker['name']} <span class="badge">{blocker['count']}</span></h3>
            <p>Оценка влияния: {blocker['score']}</p>
            <div class="examples">
                <h4>Примеры сообщений:</h4>
                {examples_html if examples_html else "<p>Нет примеров</p>"}
            </div>
        </div>
        """
    
    # Подготовка данных для графиков
    weeks = [week_data['week'] for week_data in report_data['weekly_data']]
    blocker_categories = [blocker['category'] for blocker in report_data['blockers']]
    blocker_names = [blocker['name'] for blocker in report_data['blockers']]
    
    blocker_data = {category: [] for category in blocker_categories}
    blocker_data['total_messages'] = []
    
    for week_data in report_data['weekly_data']:
        for category in blocker_categories:
            blocker_data[category].append(week_data['blockers'].get(category, 0))
        blocker_data['total_messages'].append(week_data['total_messages'])
    
    # Форматирование данных для JavaScript
    html_content = html_template.format(
        analysis_date=report_data['analysis_date'],
        date_start=report_data['date_range']['start'],
        date_end=report_data['date_range']['end'],
        total_messages=report_data['total_messages'],
        blockers_html=blockers_html,
        weeks_json=json.dumps(weeks),
        blocker_categories_json=json.dumps(blocker_categories),
        blocker_names_json=json.dumps(blocker_names),
        blocker_data_json=json.dumps(blocker_data)
    )
    
    # Сохранение HTML-отчета
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML-отчет сохранен в {output_file}")
    except Exception as e:
        print(f"Ошибка при сохранении HTML-отчета: {str(e)}")

def create_simple_html_report(data, output_file='lavsit-wazzup-simple-report.html'):
    """
    Создает упрощенный HTML-отчет без сложных графиков и JavaScript.
    
    Args:
        data: DataFrame с данными
        output_file: Путь к выходному файлу
    """
    if data is None or len(data) == 0:
        print("Нет данных для создания отчета")
        return
    
    # Создаем простой HTML с таблицей данных
    html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Простой отчет по данным Lavsit.ru Wazzup24</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 20px;
        }}
        h1, h2 {{
            color: #333;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 20px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .info-box {{
            background-color: #e7f3fe;
            border-left: 6px solid #2196F3;
            padding: 10px;
            margin-bottom: 15px;
        }}
        .blocker-box {{
            background-color: #fff3cd;
            border-left: 6px solid #ffc107;
            padding: 10px;
            margin-bottom: 15px;
        }}
    </style>
</head>
<body>
    <h1>Отчет по данным Lavsit.ru Wazzup24</h1>
    
    <div class="info-box">
        <h2>Общая информация</h2>
        <p>Всего сообщений: {len(data)}</p>
        <p>Период: с {data['date'].min()} по {data['date'].max()}</p>
    </div>
    
    <h2>Статистика по блокерам</h2>
"""
    
    # Добавляем статистику по блокерам
    for blocker in BLOCKERS:
        category = blocker['category']
        data[category] = data['text'].apply(
            lambda x: 1 if category in identify_blockers(x, BLOCKERS) else 0
        )
        count = data[category].sum()
        
        # Получаем 3 примера сообщений с этим блокером
        examples = data[data[category] == 1].sort_values(
            by='text', key=lambda x: x.str.len(), ascending=False
        ).head(3)
        
        examples_html = ""
        for _, example in examples.iterrows():
            examples_html += f"""
            <div style="margin-bottom: 10px; border-left: 3px solid #ddd; padding-left: 10px;">
                <p>"{example['text']}"</p>
                <p style="color: #666; font-size: 0.9em;">
                    Клиент: {example['contact.name'] if 'contact.name' in example and not pd.isna(example['contact.name']) else 'Не указан'}, 
                    Дата: {example['date']}
                </p>
            </div>
            """
        
        html_content += f"""
    <div class="blocker-box">
        <h3>{blocker['name']} ({count} сообщений)</h3>
        <p>Оценка влияния: {blocker['score']}</p>
        <h4>Примеры сообщений:</h4>
        {examples_html if examples_html else "<p>Нет примеров</p>"}
    </div>
"""
    
    # Добавляем таблицу последних 20 сообщений
    html_content += """
    <h2>Последние 20 сообщений</h2>
    <table>
        <tr>
            <th>Дата</th>
            <th>Клиент</th>
            <th>Сообщение</th>
            <th>Блокеры</th>
        </tr>
"""
    
    # Сортируем по дате и берем 20 последних
    last_messages = data.sort_values(by='dateTime', ascending=False).head(20)
    
    for _, msg in last_messages.iterrows():
        blockers_found = identify_blockers(msg['text'], BLOCKERS)
        blockers_names = [next(b['name'] for b in BLOCKERS if b['category'] == blocker) for blocker in blockers_found]
        blockers_text = ", ".join(blockers_names) if blockers_names else "Нет"
        
        client_name = msg['contact.name'] if 'contact.name' in msg and not pd.isna(msg['contact.name']) else 'Не указан'
        
        html_content += f"""
        <tr>
            <td>{msg['date']}</td>
            <td>{client_name}</td>
            <td>{msg['text']}</td>
            <td>{blockers_text}</td>
        </tr>
"""
    
    html_content += """
    </table>
</body>
</html>
"""
    
    # Сохраняем HTML-отчет
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Простой HTML-отчет сохранен в {output_file}")
    except Exception as e:
        print(f"Ошибка при сохранении простого HTML-отчета: {str(e)}")

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
    
    # Попробуем загрузить старые данные, если новые не загрузились
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
    processed_data = preprocess_data(data)
    
    if processed_data is None or len(processed_data) == 0:
        print("Не удалось обработать данные.")
        return
    
    try:
        # Анализ блокеров по времени
        blockers_by_time = analyze_blockers_over_time(processed_data)
        
        # Извлечение примеров сообщений для каждого блокера
        examples = extract_blocker_examples(processed_data)
        
        # Генерация полного отчета
        report_data = generate_report(processed_data, blockers_by_time, examples)
        
        # Создаем полный HTML-отчет
        try:
            generate_html_report(report_data)
        except Exception as e:
            print(f"Ошибка при создании полного HTML-отчета: {str(e)}")
        
        # Построение графика блокеров по неделям
        try:
            weekly_data = generate_weekly_data(blockers_by_time)
            plot_blockers_by_week(weekly_data)
        except Exception as e:
            print(f"Ошибка при создании графика: {str(e)}")
    except Exception as e:
        print(f"Ошибка при анализе данных: {str(e)}")
    
    # Создаем упрощенный HTML-отчет как запасной вариант
    try:
        create_simple_html_report(processed_data)
    except Exception as e:
        print(f"Ошибка при создании упрощенного отчета: {str(e)}")
    
    print("Анализ завершен.")

if __name__ == "__main__":
    main()