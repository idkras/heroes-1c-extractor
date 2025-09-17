# Яндекс.Директ OAuth 2.0 Интеграция для MCP Сервера

## Описание

Интеграция с Яндекс.Директ API через OAuth 2.0 для получения данных рекламных кампаний и групп объявлений через MCP команды.

## Структура проекта

```
mcp_server/
├── src/
│   ├── raw/                           # Продакшн код из внешнего источника
│   │   ├── yandex_direct_report_code.py  # Основной код для работы с отчетами
│   │   ├── consts.py                     # Константы API
│   │   ├── lib.py                        # Исключения
│   │   └── README.md                     # Документация raw модуля
│   ├── yandex_direct_integration.py      # Основной модуль интеграции
│   ├── credentials_manager.py            # Менеджер credentials (обновлен)
│   └── mcp_server.py                     # MCP сервер (обновлен)
├── scripts/
│   └── get_yandex_oauth_tokens.py        # Скрипт получения токенов
└── requirements.txt                      # Зависимости (обновлен)
```

## Настройка OAuth 2.0

### 1. Создание приложения в Яндекс.OAuth

1. Перейдите на [Yandex OAuth](https://oauth.yandex.ru/client/new)
2. Создайте новое приложение
3. В настройках укажите:
   - **Redirect URI**: `http://localhost:8080`
   - **Права доступа**: `direct:read`
4. Сохраните **Client ID** и **Client Secret**

### 2. Получение токенов

Запустите скрипт для получения токенов:

```bash
cd heroes-platform
python scripts/get_yandex_oauth_tokens.py
```

Следуйте инструкциям в скрипте для получения:
- Client ID
- Client Secret  
- Access Token
- Refresh Token

### 3. Проверка настройки

Токены автоматически сохраняются в macOS Keychain и доступны для MCP сервера.

## Использование MCP команд

### Получение списка кампаний

```python
# Получить все кампании
result = await yandex_direct_get_campaigns()
```

### Получение данных кампаний

```python
# Получить данные за период
result = await yandex_direct_get_data(
    date_from="2025-01-01",
    date_to="2025-01-31"
)

# Получить данные конкретных кампаний
result = await yandex_direct_get_data(
    date_from="2025-01-01", 
    date_to="2025-01-31",
    campaign_ids="12345,67890"
)
```

### Получение статистики баннеров по ключевым словам

```python
# Получить статистику баннеров за период
result = await yandex_direct_get_banners_stat(
    date_from="2025-01-01",
    date_to="2025-01-31"
)

# Получить статистику баннеров конкретных кампаний
result = await yandex_direct_get_banners_stat(
    date_from="2025-01-01", 
    date_to="2025-01-31",
    campaign_ids="12345,67890"
)
```

## Структура ответа

### yandex_direct_get_campaigns()

```json
{
  "status": "success",
  "operation": "yandex_direct_get_campaigns",
  "data": [
    {
      "Id": 12345,
      "Name": "Кампания 1",
      "Type": "TEXT_CAMPAIGN",
      "Status": "ACCEPTED",
      "StartDate": "2025-01-01",
      "DailyBudget": 1000,
      "Currency": "RUB"
    }
  ],
  "timestamp": "2025-01-15T10:30:00"
}
```

### yandex_direct_get_data()

```json
{
  "status": "success",
  "operation": "yandex_direct_get_data",
  "data": {
    "campaigns": [...],
    "ad_groups": [...],
    "ads": [...],
    "campaign_report": [...],
    "adgroup_report": [...],
    "summary": {
      "total_campaigns": 5,
      "total_ad_groups": 25,
      "total_ads": 100,
      "campaign_report_records": 5,
      "adgroup_report_records": 25,
      "date_from": "2025-01-01",
      "date_to": "2025-01-31"
    }
  },
  "timestamp": "2025-01-15T10:30:00"
}
```

### yandex_direct_get_banners_stat()

```json
{
  "status": "success",
  "operation": "yandex_direct_get_banners_stat",
  "data": [
    {
      "ad_id": "12345",
      "ad_group_id": "67890",
      "clicks": 150,
      "impressions": 5000,
      "price": 1250.50,
      "campaign_id": "11111",
      "campaign_name": "Кампания 1",
      "campaign_url": "/campaign1",
      "date": "2025-01-15",
      "phrase": "купить товар",
      "phrase_id": "search",
      "criteria": "купить товар",
      "show_type": "KEYWORD",
      "placement": "https://search",
      "matched_keyword": "купить товар дешево",
      "ad_network_type": "search"
    }
  ],
  "summary": {
    "total_records": 100,
    "date_from": "2025-01-01",
    "date_to": "2025-01-31",
    "campaigns_analyzed": 5
  },
  "timestamp": "2025-01-15T10:30:00"
}
```

## Обработка ошибок

### Ошибки авторизации

- **401 Unauthorized**: Проверьте access token
- **403 Forbidden**: Проверьте права доступа к аккаунту

### Ошибки API

- **53**: Статистика недоступна
- **54**: Нет данных за указанный период  
- **55**: Превышен лимит запросов

## Обновление токенов

Access token автоматически обновляется через refresh token при необходимости.

## Ограничения API

- Лимит запросов: 10,000 записей на страницу
- Максимальное время выполнения отчета: 30 минут
- Семафор для ограничения одновременных запросов: 20

## Примеры использования

### Анализ эффективности кампаний

```python
# Получить данные за последний месяц
from datetime import datetime, timedelta

end_date = datetime.now().strftime("%Y-%m-%d")
start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

data = await yandex_direct_get_data(start_date, end_date)

# Анализ данных
for campaign in data['campaign_report']:
    ctr = float(campaign.get('Ctr', 0))
    cost = float(campaign.get('Cost', 0))
    clicks = int(campaign.get('Clicks', 0))
    
    print(f"Кампания: {campaign['CampaignName']}")
    print(f"CTR: {ctr:.2f}%")
    print(f"Стоимость: {cost:.2f} руб")
    print(f"Клики: {clicks}")
    print("---")
```

### Мониторинг бюджета

```python
# Проверить остатки бюджета
campaigns = await yandex_direct_get_campaigns()

for campaign in campaigns:
    daily_budget = float(campaign.get('DailyBudget', 0))
    funds_balance = float(campaign.get('FundsBalance', 0))
    
    if funds_balance < daily_budget * 2:
        print(f"⚠️ Низкий баланс в кампании {campaign['Name']}: {funds_balance:.2f} руб")
```

## Тестирование

### Проверка регистрации инструментов

```bash
cd heroes-platform/mcp_server
python test_main_tools.py
```

### Проверка MCP сервера

```bash
cd heroes-platform/mcp_server
python src/mcp_server.py --test
```

## Зависимости

Добавлены в `requirements.txt`:

```
# Yandex Direct integration dependencies
arrow>=1.2.0
ujson>=5.7.0
```

## Поддержка

При возникновении проблем:

1. Проверьте логи MCP сервера
2. Убедитесь что токены не истекли
3. Проверьте права доступа к аккаунту Яндекс.Директ
4. Обратитесь к документации [Yandex Direct API](https://yandex.ru/dev/direct/doc/dg/concepts/about-docpage/)

## Безопасность

- Все credentials хранятся в macOS Keychain
- OAuth 2.0 токены автоматически обновляются
- Нет хардкода секретов в коде
- Поддержка fallback источников для credentials

## Разработка

### Добавление новых полей

Для добавления новых полей в отчеты отредактируйте файл `src/raw/consts.py`:

```python
# Добавить новые поля
CAMPAIGN_FIELDS.extend([
    "NewField1",
    "NewField2"
])
```

### Расширение функциональности

Для добавления новых методов API создайте их в `src/yandex_direct_integration.py`:

```python
async def get_new_data(self, param1: str, param2: str) -> List[Dict]:
    """Новый метод для получения данных"""
    # Реализация
    pass
```

### Создание новых MCP команд

Добавьте новые команды в `src/mcp_server.py`:

```python
@mcp.tool()
async def yandex_direct_new_command(param: str) -> str:
    """Новая MCP команда"""
    # Реализация
    pass
```
