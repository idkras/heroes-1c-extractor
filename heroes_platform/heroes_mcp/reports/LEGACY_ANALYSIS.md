# 🔍 Анализ Legacy HeroesGPT системы

## 📋 Обзор Legacy системы

**Путь:** `/Users/ilyakrasinsky/workspace/vscode.projects/heroes.advising.project/advising_platform/src/mcp/`

**Дата анализа:** 15 Aug 2025  
**Аналитик:** AI Assistant  
**Цель:** Планирование переноса HeroesGPT команд в новый MCP сервер

---

## 🏗️ Архитектура Legacy системы

### Основные компоненты:

1. **`mcp_cursor_server.py`** (8.0KB, 240 строк)
   - Основной MCP сервер для Cursor
   - Обработка JSON-RPC запросов
   - Интеграция с MCPOrchestrator

2. **`mcp_orchestrator.py`** (153KB, 3910 строк)
   - Центральный оркестратор всех MCP команд
   - Управление workflow и процессами
   - Интеграция с различными модулями

3. **`heroes_workflow_orchestrator.py`** (49KB, 1093 строки)
   - Специализированный оркестратор для HeroesGPT
   - Анализ лендингов и генерация отчетов
   - Управление JTBD сценариями

### Дополнительные компоненты:

4. **`challenge_protocol_engine.py`** (37KB, 952 строки)
   - Протокол вызовов и валидации
   - Обработка edge cases

5. **`gap_coverage_analyzer.py`** (38KB, 1041 строка)
   - Анализ пробелов в покрытии
   - Выявление missing functionality

6. **`offers_enforcement_engine.py`** (15KB, 420 строк)
   - Анализ и валидация офферов
   - Проверка compliance

---

## 🔧 Ключевые команды для переноса

### Core команды (Приоритет 1):

1. **`heroes_gpt_workflow`**
   - **Функция:** Основной анализатор лендингов
   - **Вход:** URL лендинга или контент
   - **Выход:** Структурированный анализ по стандарту HeroesGPT
   - **Источник:** `heroes_workflow_orchestrator.py`

2. **`standards_management`**
   - **Функция:** Управление стандартами проекта
   - **Вход:** Команда (list, get, search), путь, запрос
   - **Выход:** Результаты поиска/управления стандартами
   - **Источник:** `mcp_orchestrator.py`

3. **`performance_monitor`**
   - **Функция:** Мониторинг производительности системы
   - **Вход:** Метрика (status, memory, cpu)
   - **Выход:** Данные о производительности
   - **Источник:** `mcp_orchestrator.py`

4. **`server_info`**
   - **Функция:** Информация о сервере
   - **Вход:** Dummy параметр
   - **Выход:** Информация о сервере и доступных командах
   - **Источник:** `mcp_cursor_server.py`

### Расширенные команды (Приоритет 2):

5. **`challenge_protocol_engine`**
   - **Функция:** Протокол вызовов и валидации
   - **Вход:** Параметры вызова
   - **Выход:** Результаты валидации
   - **Источник:** `challenge_protocol_engine.py`

6. **`gap_coverage_analyzer`**
   - **Функция:** Анализ пробелов в покрытии
   - **Вход:** Данные для анализа
   - **Выход:** Отчет о пробелах
   - **Источник:** `gap_coverage_analyzer.py`

7. **`offers_enforcement_engine`**
   - **Функция:** Анализ и валидация офферов
   - **Вход:** Офферы для анализа
   - **Выход:** Результаты валидации
   - **Источник:** `offers_enforcement_engine.py`

---

## 📊 Структура данных HeroesGPT

### Основные dataclass'ы:

```python
@dataclass
class OfferAnalysis:
    offer_text: str
    offer_type: str  # обещание/выгода/гарантия/соц_доказательство
    quantitative_data: str
    target_segment: str
    emotional_trigger: str
    value_tax_rating: str  # Выгода/Налог

@dataclass
class JTBDScenario:
    big_jtbd: str
    when_trigger: str
    medium_jtbd: str
    small_jtbd: str
    implementing_files: str
    status: str

@dataclass
class LandingAnalysis:
    url: str
    business_type: str
    main_value_prop: str
    target_segments: list[str]
    analysis_time: float
    content_length: int

@dataclass
class HeroesGPTReport:
    id: str
    timestamp: str
    landing_analysis: LandingAnalysis
    offers_table: list[OfferAnalysis]
    jtbd_scenarios: list[JTBDScenario]
    segments: dict[str, Any]
    rating: int  # 1-5
    recommendations: list[str]
    reflections: list[ReflectionCheckpoint]
    narrative_coherence_score: int  # 1-10
    self_compliance_passed: bool
```

---

## 🔄 Workflow процессы

### Основной workflow анализа лендинга:

1. **Инициализация анализа**
   - Валидация входных данных
   - Создание уникального ID анализа
   - Настройка логирования

2. **Извлечение контента**
   - Парсинг URL лендинга
   - Извлечение текстового контента
   - Анализ метаданных

3. **Анализ офферов**
   - Выявление всех офферов и сообщений
   - Классификация по типам
   - Анализ количественных данных

4. **Сегментация аудитории**
   - Определение целевых сегментов
   - Анализ JTBD сценариев
   - Оценка релевантности

5. **Генерация отчета**
   - Создание структурированного отчета
   - Расчет рейтингов и метрик
   - Формирование рекомендаций

---

## 🎯 Эталонный анализ zipsale.co.uk

### Ключевые компоненты эталонного отчета:

1. **Метаданные анализа:**
   - type: heroes_gpt_analysis
   - analysis_id: HGA004
   - created: 11 Jun 2025, 13:20 CET
   - analyzed_url: zipsale.co.uk
   - standard_version: HeroesGPT Landing Analysis Standard v1.4.1

2. **Общий обзор:**
   - Тип бизнеса: B2B SaaS / Автоматизация e-commerce
   - Основная цель: Привлечение ресселлеров для SaaS подписки
   - Ценовая категория: Mid-tier B2B SaaS решение

3. **Анализ офферов:**
   - Таблица с 9 офферами
   - Классификация по типам (позиционирование, описание продукта, функция)
   - Анализ количественных данных и эмоциональных триггеров

4. **Сегментация аудитории:**
   - Винтажные магазины (специализированные)
   - Профессиональные ресселлеры (мульти-канальные)
   - Начинающие ресселлеры
   - Крупные ресселлеры (business-scale)

---

## 🔧 Технические зависимости

### Внешние зависимости:
- `mcp` - MCP SDK
- `fastmcp` - FastMCP framework
- `requests` - HTTP запросы
- `beautifulsoup4` - Парсинг HTML
- `dataclasses` - Структуры данных

### Внутренние зависимости:
- `mcp_orchestrator` - Центральный оркестратор
- `standards_system` - Система стандартов
- `monitoring` - Система мониторинга

---

## 📋 План переноса

### Этап 1: Core команды (Релиз 2)
1. Перенести `heroes_gpt_workflow`
2. Перенести `standards_management`
3. Перенести `performance_monitor`
4. Перенести `server_info`

### Этап 2: Расширенные команды (Релиз 3)
1. Перенести `challenge_protocol_engine`
2. Перенести `gap_coverage_analyzer`
3. Перенести `offers_enforcement_engine`
4. Интегрировать с `workflow_orchestrator`

### Этап 3: Валидация (Релиз 4)
1. Тестирование на zipsale.co.uk
2. Сравнение с эталонным отчетом
3. Оптимизация производительности
4. Создание документации

---

## ⚠️ Риски и ограничения

### Технические риски:
- Сложность интеграции с legacy компонентами
- Зависимости от внешних систем
- Производительность при больших объемах данных

### Функциональные риски:
- Потеря функциональности при переносе
- Несовместимость с новым MCP сервером
- Изменения в API внешних сервисов

### Митигация рисков:
- Поэтапный перенос с тестированием
- Сохранение обратной совместимости
- Создание fallback механизмов

---

## ✅ Критерии успеха переноса

1. **Функциональность:**
   - Все core команды работают
   - Анализ zipsale.co.uk соответствует эталону
   - Производительность не хуже legacy

2. **Качество:**
   - TDD стандарт соблюден
   - Покрытие тестами ≥90%
   - Линтеры не выдают ошибок

3. **Интеграция:**
   - Cursor видит и может использовать команды
   - MCP протокол соблюден
   - Обратная совместимость сохранена

4. **Документация:**
   - API документация создана
   - Примеры использования готовы
   - Troubleshooting guide доступен
