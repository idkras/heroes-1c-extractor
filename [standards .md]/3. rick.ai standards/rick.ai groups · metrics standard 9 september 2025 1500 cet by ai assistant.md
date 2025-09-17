# Rick.ai Groups · Metrics Standard

**Версия:** 1.0  
**Дата:** 9 сентября 2025, 15:00 CET  
**Автор:** AI Assistant  
**Статус:** Активный  

## Обзор

Стандарт определяет структуру, классификацию и использование метрик и группировок в платформе Rick.ai. Основан на глоссарии метрик и группировок из Google Sheets и интегрирован с архитектурой Rick.ai.

## JTBD (Jobs To Be Done)

### Основные JTBD
1. **Как аналитик**, я хочу понимать структуру метрик и группировок, чтобы правильно интерпретировать данные
2. **Как разработчик**, я хочу использовать стандартизированные метрики, чтобы обеспечить консистентность API
3. **Как менеджер**, я хочу видеть ключевые показатели эффективности, чтобы принимать решения на основе данных
4. **Как интегратор**, я хочу понимать маппинг метрик, чтобы корректно передавать данные между системами

## Архитектурные принципы

### 1. Классификация метрик
- **Финансовые метрики**: доход, расходы, маржа, ROI
- **Операционные метрики**: заказы, лиды, конверсии
- **Трафиковые метрики**: клики, показы, сессии, пользователи
- **Эффективностные метрики**: CTR, ROAS, CPO, CPL

### 2. Классификация группировок
- **Источники трафика**: source, medium, sourceMedium, channel
- **Рекламные данные**: ads:*, ga:*, deal:*
- **CRM данные**: crm:*, clientID, userID
- **Временные группировки**: day, week, month, hour
- **Географические**: ga:country, ga:city, ga:region
- **Технические**: device, ga:browser, ga:operatingSystem

## Метрики (Metrics)

### Финансовые метрики

#### Доходы и расходы
- **доход / revenue** - Общий доход от продаж
- **расходы с ндс / ad costs incl. VAT** - Расходы на рекламу с НДС
- **расходы с ндс неатр. / ad costs unattributed VAT** - Нераспределенные расходы с НДС
- **маржа / gross profit** - Валовая прибыль
- **ср. маржа / av. margin** - Средняя маржа
- **ср. чек / av. price** - Средний чек

#### Показатели эффективности
- **ROAS с ндс** - Return on Ad Spend с НДС
- **ROI с ндс** - Return on Investment с НДС
- **ROMI с ндс** - Return on Marketing Investment с НДС
- **ДРР с ндс** - Доля рекламных расходов с НДС
- **ARPU** - Average Revenue Per User

### Операционные метрики

#### Заказы и лиды
- **заказы / orders** - Общее количество заказов
- **заказы неатр. / orders unattributed** - Нераспределенные заказы
- **заказы на 1 лида / orders per lead** - Конверсия лид → заказ
- **лиды / leads** - Количество лидов
- **конверсия в лид / conversion to lead** - Процент конверсии в лид

#### Товары и продукты
- **товары / items or products** - Количество проданных товаров

### Трафиковые метрики

#### Пользователи и сессии
- **пользователи / users** - Уникальные пользователи
- **пользователи виртуальные / users virtual** - Виртуальные пользователи
- **пользователи новые / users new** - Новые пользователи
- **сессии / sessions** - Количество сессий
- **событий / hits** - Количество событий

#### Клики и показы
- **клики / clicks** - Количество кликов
- **показы / impressions** - Количество показов
- **CTR** - Click-Through Rate

### Стоимостные метрики

#### Cost Per метрики
- **CPC с ндс** - Cost Per Click с НДС
- **CPL с ндс** - Cost Per Lead с НДС
- **CPO с ндс** - Cost Per Order с НДС
- **CPUser с ндс** - Cost Per User с НДС

### COGS (Cost of Goods Sold)
- **COGS partial refund** - Частичный возврат
- **COGS delivery** - Стоимость доставки
- **COGS tax** - Налоги
- **COGS discounts** - Скидки
- **COGS items costs** - Стоимость товаров

## Группировки (Groupings)

### Источники трафика

#### Основные группировки
- **source** - Источник трафика
- **medium** - Канал/медиум
- **sourceMedium** - Комбинированная группировка источник+медиум
- **sourceMedium real** - Реальная группировка sourceMedium
- **channel** - Канал трафика
- **channel type** - Тип канала
- **channel · campaign** - Канал и кампания

#### Рекламные группировки
- **campaign** - Название кампании
- **campaignType** - Тип кампании
- **ad creative** - Креатив объявления
- **ad group** - Группа объявлений

### Google Analytics группировки

#### GA: Основные
- **ga:sourceMedium** - Источник и медиум GA
- **ga:campaign** - Кампания GA
- **ga:adContent** - Контент объявления GA
- **ga:adGroup** - Группа объявлений GA
- **ga:keyword** - Ключевое слово GA
- **ga:landingPagePath** - Путь посадочной страницы GA

#### GA: Географические
- **ga:country** - Страна
- **ga:region** - Регион
- **ga:city** - Город

#### GA: Технические
- **ga:deviceCategory** - Категория устройства
- **ga:browser** - Браузер
- **ga:browserVersion** - Версия браузера
- **ga:operatingSystem** - Операционная система
- **ga:operatingSystemVersion** - Версия ОС
- **ga:screenResolution** - Разрешение экрана
- **ga:connectionType** - Тип соединения

#### GA: Контент
- **ga:pagePath** - Путь страницы
- **ga:pageTitle** - Заголовок страницы
- **ga:pageReferrer** - Реферер страницы
- **ga:exitPagePath** - Путь страницы выхода
- **ga:fullReferrer** - Полный реферер
- **ga:hostname** - Имя хоста

#### GA: События
- **ga:eventCategory** - Категория события
- **ga:eventAction** - Действие события
- **ga:eventLabel** - Метка события

### Рекламные платформы (ads:*)

#### Google Ads
- **ads:accountId** - ID аккаунта
- **ads:accountName** - Название аккаунта
- **ads:accountStatus** - Статус аккаунта
- **ads:campaignId** - ID кампании
- **ads:campaignName** - Название кампании
- **ads:campaignStatus** - Статус кампании
- **ads:campaignType** - Тип кампании
- **ads:adId** - ID объявления
- **ads:adName** - Название объявления
- **ads:adStatus** - Статус объявления
- **ads:adType** - Тип объявления
- **ads:groupId** - ID группы
- **ads:groupName** - Название группы
- **ads:groupStatus** - Статус группы
- **ads:groupType** - Тип группы

#### UTM параметры
- **ads:utmSourceMedium** - UTM source и medium
- **ads:utmCampaign** - UTM campaign
- **ads:utmAdContent** - UTM ad content
- **ads:utmKeyword** - UTM keyword

#### Дополнительные рекламные данные
- **ads:channel** - Канал рекламы
- **ads:source** - Источник рекламы
- **ads:subtype** - Подтип
- **ads:text** - Текст объявления
- **ads:title** - Заголовок объявления
- **ads:url** - URL объявления
- **ads:previewURL** - URL превью
- **ads:thumbnailURL** - URL миниатюры
- **ads:landingPage** - Посадочная страница
- **ads:erid** - ERID
- **ads:dataImportId** - ID импорта данных

### CRM группировки (crm:*)

#### Основные CRM данные
- **crm:clientID** - ID клиента в CRM
- **crm:userID** - ID пользователя в CRM
- **crm:transactionID** - ID транзакции
- **crm:deal method** - Метод сделки
- **crm:deal method original** - Оригинальный метод сделки
- **crm:pipeline · status** - Воронка и статус
- **crm:manager** - Менеджер
- **crm:coupon** - Купон
- **crm:offline** - Офлайн статус
- **crm:deleted** - Удаленные записи

#### KJ Algorithm данные
- **crm:KJ accuracy** - Точность KJ алгоритма
- **crm:KJ candidate count** - Количество кандидатов KJ
- **crm:KJ class** - Класс KJ
- **crm:KJ distance** - Расстояние KJ
- **crm:KJ errors** - Ошибки KJ
- **crm:KJ extra** - Дополнительные данные KJ
- **crm:KJ matches** - Совпадения KJ
- **crm:KJ offline** - Офлайн KJ
- **crm:KJ transfers** - Передачи KJ
- **crm:KJ weight** - Вес KJ
- **crm:kj weight · crm:kj accuracy · crm:kj class** - Комбинированная группировка KJ

#### Продуктовые данные
- **crm:product SKU** - SKU продукта
- **crm:product category** - Категория продукта
- **crm:product category · name** - Название категории продукта
- **crm:product name** - Название продукта

#### Финансовые данные
- **crm:revenue** - Доход в CRM
- **crm:raw transaction type** - Тип сырой транзакции

#### Временные данные
- **crm:day order created** - День создания заказа
- **crm:hour order created** - Час создания заказа
- **crm:minute order created** - Минута создания заказа
- **crm:month order created** - Месяц создания заказа
- **crm:week order created** - Неделя создания заказа
- **crm:deal created at** - Время создания сделки
- **crm:deal received at** - Время получения сделки

#### Дополнительные CRM данные
- **crm:loss reason** - Причина потери
- **crm:segments by transactions** - Сегменты по транзакциям
- **crm:transactionID · userID · clientID · crm:status** - Комбинированная группировка транзакции

### Временные группировки

#### Основные временные
- **day** - День
- **week** - Неделя
- **month** - Месяц
- **hour event** - Час события
- **day event** - День события
- **week event** - Неделя события
- **month event** - Месяц события
- **minute event** - Минута события

#### Когортные группировки
- **cohorts: new, old cohort** - Новые и старые когорты
- **day cohort user 1st session** - День первой сессии пользователя
- **week cohort user 1st session** - Неделя первой сессии пользователя
- **month cohort user 1st session** - Месяц первой сессии пользователя

#### Рабочие дни
- **day work or weekends** - Рабочие дни или выходные

### Технические группировки

#### Устройства
- **device** - Устройство

#### Идентификаторы
- **clientID** - ID клиента
- **userID** - ID пользователя
- **rickClientID** - ID клиента Rick
- **rick rid** - Rick RID
- **roistatClientID** - ID клиента Roistat
- **roistat** - Roistat данные

#### Хеши
- **email hash** - Хеш email
- **phone hash** - Хеш телефона
- **value hash** - Хеш значения

### Контентные группировки

#### Страницы и события
- **pagePath** - Путь страницы
- **pagePath · pageTitle** - Путь и заголовок страницы
- **page · event** - Страница и событие
- **event** - Событие

#### Посадочные страницы
- **landing initial** - Начальная посадочная страница
- **initial landing short** - Короткая начальная посадочная страница
- **landings only short list** - Короткий список посадочных страниц

### Атрибуционные группировки

#### Правила атрибуции
- **attribution all rules** - Все правила атрибуции
- **attribution applied rules** - Примененные правила атрибуции

#### Click ID
- **clickID** - ID клика
- **clickType** - Тип клика

### Дополнительные группировки

#### Сегментация
- **segments by user** - Сегменты по пользователю
- **segments by transactions** - Сегменты по транзакциям

#### Платежи
- **paymentMethod** - Метод платежа

#### Данные сделок
- **deal adContent** - Контент объявления сделки
- **deal campaign** - Кампания сделки
- **deal ga clientID** - GA clientID сделки
- **deal keyword or term** - Ключевое слово или термин сделки
- **deal method** - Метод сделки
- **deal method original** - Оригинальный метод сделки
- **deal sourceMedium** - SourceMedium сделки
- **deal ym clientID** - YM clientID сделки
- **deal created at** - Время создания сделки
- **deal received at** - Время получения сделки

#### Временные зоны
- **time deal timezone** - Временная зона сделки

#### Правила сессий
- **session rules** - Правила сессий

#### Правила расходов
- **expense rule** - Правило расходов

#### BigQuery
- **bq:stream_id** - ID потока BigQuery

#### Дополнительные GA группировки
- **ga:adMatchedQuery** - Совпавший запрос объявления
- **ga:adwordsAdGroupID** - ID группы AdWords
- **ga:adwordsCampaignID** - ID кампании AdWords
- **ga:adwordsCreativeID** - ID креатива AdWords
- **ga:adwordsCriteriaID** - ID критерия AdWords
- **ga:adwordsCustomerID** - ID клиента AdWords
- **ga:appBuildNumber** - Номер сборки приложения
- **ga:appPackageName** - Имя пакета приложения
- **ga:appVersion** - Версия приложения
- **ga:channelGrouping** - Группировка каналов
- **ga:dataSource** - Источник данных
- **ga:deviceLocale** - Локаль устройства
- **ga:landingPagePath till ? or #** - Путь посадочной страницы до ? или #
- **ga:mobileDeviceInfo** - Информация о мобильном устройстве
- **ga:networkDomain** - Домен сети
- **ga:operatorName** - Имя оператора
- **ga:pageLocation** - Расположение страницы
- **ga:screenName** - Имя экрана

#### Дополнительные рекламные группировки
- **ads:adPlacementDomain** - Домен размещения объявления
- **ads:adPlacementUrl** - URL размещения объявления

#### Интеграционные группировки (i:*)
- **i:ad** - Объявление интеграции
- **i:ad class** - Класс объявления интеграции
- **i:ad group** - Группа объявления интеграции
- **i:ad group class** - Класс группы объявления интеграции
- **i:adContent** - Контент объявления интеграции
- **i:adContent class** - Класс контента объявления интеграции
- **i:campaign** - Кампания интеграции
- **i:campaign class** - Класс кампании интеграции
- **i:keyword** - Ключевое слово интеграции
- **i:keyword class** - Класс ключевого слова интеграции

## Технические требования

### 1. Формат данных
- Все метрики должны быть числовыми (int, float)
- Все группировки должны быть строковыми (string)
- Поддержка NULL значений для отсутствующих данных

### 2. Валидация
- Проверка корректности значений метрик
- Валидация формата группировок
- Проверка обязательных полей

### 3. Производительность
- Индексация по часто используемым группировкам
- Кэширование агрегированных метрик
- Оптимизация запросов

## Интеграция с Rick.ai

### 1. API Endpoints
```
GET /api/v1/metrics - Список доступных метрик
GET /api/v1/groupings - Список доступных группировок
GET /api/v1/data?metrics={metrics}&groupings={groupings} - Получение данных
```

### 2. MCP Commands
- `rick_ai_get_metrics` - Получение списка метрик
- `rick_ai_get_groupings` - Получение списка группировок
- `rick_ai_analyze_metrics` - Анализ метрик
- `rick_ai_validate_grouping` - Валидация группировок

### 3. Widget Integration
- Автоматическое определение доступных метрик и группировок
- Валидация пользовательских запросов
- Предложения по оптимизации запросов

## Примеры использования

### 1. Базовый запрос метрик
```json
{
  "metrics": ["доход / revenue", "расходы с ндс / ad costs incl. VAT", "ROAS с ндс"],
  "groupings": ["sourceMedium", "ga:deviceCategory"],
  "date_range": {
    "from": "2025-01-01",
    "to": "2025-01-31"
  }
}
```

### 2. Анализ эффективности каналов
```json
{
  "metrics": ["CPL с ндс", "конверсия в лид / conversion to lead", "лиды / leads"],
  "groupings": ["channel", "ga:country"],
  "filters": {
    "channel": ["google", "yandex", "facebook"]
  }
}
```

### 3. CRM анализ
```json
{
  "metrics": ["заказы / orders", "ср. чек / av. price", "маржа / gross profit"],
  "groupings": ["crm:deal method", "crm:manager", "crm:KJ accuracy"],
  "date_range": {
    "from": "2025-01-01",
    "to": "2025-01-31"
  }
}
```

## Соответствие стандартам

### Registry Standard
- ✅ Атомарные операции
- ✅ Структурированный output
- ✅ MCP интеграция
- ✅ Валидация данных

### Task Master Standard
- ✅ JTBD сценарии
- ✅ Cross-check валидация
- ✅ Документированные артефакты
- ✅ Протокол челендж

### Rick.ai Methodology Standard
- ✅ Архитектурная совместимость
- ✅ Интеграция с workflow
- ✅ Поддержка KJ алгоритма
- ✅ Атрибуционная логика

## Мониторинг и метрики

### KPI стандарта
- **Покрытие метрик**: 100% метрик из глоссария
- **Покрытие группировок**: 100% группировок из глоссария
- **Время отклика API**: < 2 секунды
- **Точность данных**: 99.9%

### Алерты
- Отсутствие обязательных метрик
- Некорректные значения группировок
- Превышение времени отклика
- Ошибки валидации

## Версионирование

### v1.0 (9 сентября 2025)
- Базовая структура метрик и группировок
- Интеграция с Rick.ai API
- MCP команды
- Валидация данных

### Планы развития
- v1.1: Добавление новых метрик
- v1.2: Расширение группировок
- v2.0: Машинное обучение для оптимизации

## Заключение

Стандарт `rick.ai groups · metrics standard` обеспечивает единообразное понимание и использование метрик и группировок в экосистеме Rick.ai. Интеграция с существующими стандартами и архитектурой гарантирует совместимость и расширяемость системы.

---

**Связанные стандарты:**
- [Registry Standard](0.1%20registry%20standard%2015%20may%202025%201320%20CET%20by%20AI%20Assistant.md)
- [Task Master Standard](0.0%20task%20master%2010%20may%202226%20cet%20by%20ilya%20krasinsky.md)
- [Rick.ai Methodology Standard](rick.ai%20methodology%20standard%209%20september%202025%201400%20cet%20by%20ai%20assistant.md)

**Источники:**
- Google Sheets Glossary: Metrics (gid=297862578)
- Google Sheets Glossary: Groupings (gid=1177501812)
- Rick.ai Knowledge Base
- Rick.ai Architecture Specification
