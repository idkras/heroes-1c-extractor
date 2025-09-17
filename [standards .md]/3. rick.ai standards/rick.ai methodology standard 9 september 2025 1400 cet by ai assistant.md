# 📊 Rick.ai Methodology Standard

<!-- 🔒 PROTECTED SECTION: BEGIN -->type: standard

updated: 9 September 2025, 20:30 CET by AI Assistant
previous version: 9 September 2025, 19:00 CET by AI Assistant
based on: [Registry Standard](abstract://standard:registry_standard), версия 6.4, 9 September 2025, 14:05 CET
integrated: [Task Master Standard](abstract://standard:task_master_standard), [Protocol Challenge](abstract://standard:protocol_challenge), [From-The-End Standard](abstract://standard:from_the_end_standard), [MCP Workflow Standard](abstract://standard:mcp_workflow_standard), [Rick.ai Knowledge Base](abstract://rick_ai_knowledge_base), [Rick.ai Chat Messages](abstract://rick_ai_chat_messages), [Rick.ai Technical Issues](abstract://rick_ai_technical_issues)
version: 1.6
status: Active
tags: standard, methodology, rick.ai, analytics
<!-- 🔒 PROTECTED SECTION: END -->

---

## 🛡️ Лицензия и условия использования

**Все права защищены.** Данный документ является интеллектуальной собственностью Ильи Красинского и не может быть скопирован, использован или адаптирован в любых целях без предварительного письменного согласия автора. Авторские права защищены законодательством США.

**Magic Rick Inc.**, зарегистрированная в штате Делавэр (США), действует от имени автора в целях защиты его интеллектуальной собственности и будет преследовать любые нарушения в соответствии с законодательством США.

---

## 🎯 Цель документа

Создать единую методологию работы с аналитической платформой Rick.ai, обеспечивающую стандартизированные процессы сбора данных, анализа атрибуции, интеграции с внешними системами и построения сквозной аналитики. Методология основана на принципах Registry Standard и Task Master Standard для обеспечения атомарности операций, reflection checkpoints и качества результатов.

---

## 🧠 Архитектурные принципы Rick.ai

### 0. Архитектура доменов Rick.ai

**КРИТИЧЕСКИ ВАЖНО**: Rick.ai использует разделение доменов:

- **rick.ai** - основной домен с API для получения данных клиентов, виджетов, аналитики
- **flow.rick.ai** - n8n автоматизация на поддомене для workflow процессов

**Для MCP команд Rick.ai**: Всегда обращаться к **rick.ai**, НЕ к flow.rick.ai

### 1. Принцип атомарности операций

Все операции в Rick.ai должны выполняться как атомарные транзакции с обязательными reflection checkpoints:

#### ✅ **Обязательные Reflection Points:**
- **Input validation**: "Работаю ли я с валидными данными?"
- **Process validation**: "Следую ли я правильной процедуре?"
- **Output validation**: "Соответствует ли результат стандартам качества?"
- **Standard compliance**: "Соблюдаю ли я все применимые стандарты?"

#### 🔄 **Пример атомарного workflow для Rick.ai:**
```
1. validate_rick_data → [reflection]
2. analyze_source_medium → [reflection]
3. apply_kj_algorithm → [reflection]
4. generate_attribution_report → [reflection]
5. validate_standard_compliance → [reflection]
```

### 2. Принцип 71-поля sourceMedium

Rick.ai использует расширенную модель атрибуции с 71 полем для определения sourceMedium:

#### 📊 **Категории полей атрибуции:**

**Click IDs (Приоритет 1):**
- `gclid`, `yclid`, `fbclid`, `ysclid`, `msclid`, `ttclid`
- `wbraid`, `gbraid`, `dclid`, `sclid`

**UTM параметры и URL данные (Приоритет 2):**
- `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content`
- `utm_id`, `utm_source_platform`, `utm_creative_format`
- `page_location` - URL страницы с параметрами
- Параметры из URL (gclid, yclid, fbclid, ysclid в URL)

**Yandex Metrica параметры (Приоритет 3):**
- `ym:sourceMedium`, `ym:source`, `ym:medium`
- `raw_source_medium` - синоним ym:sourceMedium (восстановление Метрики)
- `last_traffic_source`, `last_search_engine_root`

**Traffic Source данные (Приоритет 4):**
- `traffic_source.source`, `traffic_source.medium`
- `traffic_source.name`, `traffic_source.term`

**Referrer данные (Приоритет 5):**
- `page_referrer`, `referrer`
- `document_referrer`, `navigation_type`

#### 🎯 **Правильный алгоритм приоритизации sourceMedium:**

**ПРИОРИТЕТ 1: Click ID (наивысший)**
- `yclid:` → `yandex / cpc` (channel: yandex direct)
- `gclid:` → `google / cpc` (channel: google ads)
- `fbclid:` → `facebook / cpc` (channel: facebook ads)
- `ysclid:` → `yandex / cpc` (channel: yandex direct)

**ПРИОРИТЕТ 2: UTM параметры и URL данные**
- `utm_source` + `utm_medium` из `page_location` → `{utm_source} / {utm_medium}`
- Параметры из URL (gclid, yclid, fbclid, ysclid в URL)

**ПРИОРИТЕТ 3: Traffic Source данные**
- `event_param_last_traffic_source` = "organic" → `organic / organic`
- `event_param_last_traffic_source` = "referral" → `referral / referral`

**ПРИОРИТЕТ 4: Referrer данные (анализ домена)**
- `event_param_page_referrer` содержит домен → `{domain} / organic` (НЕ referral!)
- **ВАЖНО**: Домен из referrer МОЖЕТ быть источником (например, google.com → google / organic)
- **Примеры правильной атрибуции по referrer:**
  - `https://google.com/search` → `google / organic`
  - `https://yandex.ru/search` → `yandex / organic`
  - `https://facebook.com` → `facebook / social`
  - `https://vk.com` → `vk / social`

**ПРИОРИТЕТ 5: Fallback**
- Все поля пустые или internal → `direct / none`

#### 🚨 **Критические проблемы текущего алгоритма:**
1. **previous_* правила** игнорируют Click ID и используют данные с предыдущих страниц
2. **Неправильная приоритизация** - Click ID не используется как приоритет 1
3. **raw_source_medium = ym:sourceMedium** - синонимы, но восстанавливаются неправильно
4. **Неправильная атрибуция referrer** - домены из referrer должны быть источниками (google.com → google / organic)
5. **Отсутствие сессионного анализа** - нужно анализировать все события clientID, а не одно

#### 📋 **Определение терминов:**
- **sourceMedium** - точная группировка Рика на основе правил атрибуции
- **raw_source_medium** - синоним ym:sourceMedium, восстановление того, что Яндекс.Метрика восстанавливает по событиям и параметрам событий
- **ym:sourceMedium** - восстановление Метрики из event_param_source/event_param_medium

#### 🔧 **Примеры правильных Channel Rules:**

**Правило 1: Click ID (yclid)**
```
когда
clientID равно "* любое не пустое"
и event_param_rick_ad_channel_identifiers содержит yclid:
то
channel = yandex direct
sourceMedium = yandex / cpc || {параметр где определен sourceMedium}
raw_source_medium = yandex / cpc || {параметр где определен sourceMedium}
```

#### 📊 **Формат анализа sourceMedium данных:**

**Структура группировки полей для анализа (с мягкими переносами между группами) и абзацными отступами! их нужно сохранить!:**

```
day: 2025-09-03
event_param_date_hour_minute: 2025-09-03 05:03

client_id: 16748222471051939108
event_param_rick_rid: SyxThnYotY

channel_group: yandex direct
source_medium: yandex_sm / cpc
raw_source_medium: yandex_sm / cpc
applied_rules: previous_landing

click_id:

event_param_source:
event_param_medium:
event_param_last_search_engine:
event_param_last_search_engine_root:
event_param_last_adv_engine:
event_param_last_traffic_source: internal
event_param_last_social_network:
event_param_last_social_network_profile:

device_category: mobile
all_landing_page_path: /matrasy/sleep-expert-master.htm
page_location: https://www.askona.ru/matrasy/sleep-expert-master.htm?selected_hash_size=80x200-99f4666067a778dd908a8d67652aeb74&utm_source=yandex_sm&utm_medium=cpc&utm_campaign=sm_yd_askona_other_person_perform_god_rk485876gr3785_context_shopping_feed_rus|119710113&utm_content=cid|119710113|gid|5568399787|ad|17180150848_17180150848|ph_id|205568399787|rtg_id|205568399787|src|none_search|geo|_967&utm_term=---autotargeting&yclid=86520401018748927
event_param_page_referrer: https://askona.ru/matrasy/sleep-expert-master.htm?SELECTED_HASH_SIZE=80x200-99f4666067a778dd908a8d67652aeb74

event_param_rick_user_agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36
event_param_rick_url: yclid:86520401018748927;ym_client_id:16748222471051939108;hostname:www.askona.ru;pagepath:/matrasy/sleep-expert-master.htm

campaign_id:
event_param_campaign:
custom_group_campaign_grouping: sm_yd_askona_other_person_perform_god_rk485876gr3785_context_shopping_feed_rus|119710113
campaign: sm_yd_askona_other_person_perform_god_rk485876gr3785_context_shopping_feed_rus|119710113

ad_group_combined:
ad_group:
keyword: ---autotargeting
ad_content: cid|119710113|gid|5568399787|ad|17180150848_17180150848|ph_id|205568399787|rtg_id|205568399787|src|none_search|geo|_967
ad_utm_source_medium:
campaign_name:
campaign_status:
ad_utm_keyword:
ad_combined:
ad_group_name:
ad_group_status:
ad_campaign_type:
ad_group_type:
ad_name:
ad_status:
ad_placement_domain:
ad_placement_url:
ad_utm_campaign:
ad_subtype:
ad_utm_content:
ad_title:
ad_text:
ad_url:
ad_thumbnail_url:
ad_preview_url:
ad_source:
ga_data_import_id: 0
ad_group_id:
ad_type:
ad_landing_page:
ad_id:
ad_erid:

event_param_ad_source:
event_param_content:
event_param_term:
event_param_rick_ad_channel_identifiers: gclid:;fbclid:;yclid:86520401018748927;ysclid:
event_param_rick_additional_campaign_data: etext:;campaign_id:
event_param_rick_ad_identifiers: ad_id:;group_id:
event_param_rick_campaign_attribution: utm_source:;utm_medium:;utm_campaign:;utm_content:
event_param_rick_fb_client_id:
```

**Ключевые принципы форматирования:**
- **Мягкие переносы** (пустые строки) между логическими группами полей
- **БЕЗ заголовков** группировки (никаких "Основные данные:", "Атрибуция:" и т.д.)
- **Плоский список** всех 71 поля с визуальным разделением группами
- **Порядок полей** согласно логической группировке Rick.ai

**Формат sourceMedium result:**
- Если все правильно: `✔️`
- Если есть ошибки: `ошибка: в page_location найден yclid=86520401018748927, но не применен`
- Если Click ID найден, но не применен: `ошибка: yclid найден, но previous_landing правило перезаписывает`

**Формат sourceMedium rules:**
```
**Правило: clickId: yclid**
когда clientID равно "* любое не пустое" и
event_param_rick_ad_channel_identifiers содержит yclid:

то
channel = yandex direct
sourceMedium = yandex / cpc || {параметр где определен sourceMedium}
raw_source_medium = yandex / cpc || {параметр где определен sourceMedium}
```

**Правило 2: UTM параметры**
```
когда
clientID равно "* любое не пустое"
и page_location содержит utm_source=google и utm_medium=cpc
то
channel = utm campaign
sourceMedium = google / cpc
raw_source_medium = google / cpc
```

**Правило 3: Traffic Source**
```
когда
clientID равно "* любое не пустое"
и event_param_last_traffic_source содержит organic
то
channel = organic
sourceMedium = organic / organic
raw_source_medium = organic / organic
```

**Правило 4: Referrer (анализ домена)**
```
когда
clientID равно "* любое не пустое"
и event_param_page_referrer содержит google.com
то
channel = organic
sourceMedium = google / organic
raw_source_medium = google / organic

ПРИМЕРЫ:
- https://google.com/search → google / organic
- https://yandex.ru/search → yandex / organic  
- https://facebook.com → facebook / social
- https://vk.com → vk / social
```

**Правило 5: Fallback**
```
когда
clientID равно "* любое не пустое"
и все остальные поля пустые или internal
то
channel = direct
sourceMedium = direct / none
raw_source_medium = direct / none
```

### 3. Принцип KJ (Критерий Женни) алгоритма

Алгоритм KJ используется для связывания анонимных пользователей с контактами в CRM:

#### 🔍 **Принцип работы:**
1. **Анализ временных совпадений** между активностью на сайте и событиями в CRM
2. **Учет дополнительных факторов** (IP-адрес, устройство, местоположение)
3. **Байесовская вероятностная модель** для определения точности совпадения
4. **Механизм самообучения** на основе подтвержденных связей

#### ⚙️ **Настройки алгоритма:**
- **Временное окно**: 15 минут (по умолчанию)
- **Минимальный порог вероятности**: 0.8 (по умолчанию)
- **Весовые коэффициенты** для различных факторов

#### 📊 **Целевые показатели качества:**
- **Процент склеенных событий**: ≥80%
- **Точность атрибуции**: ≥90%
- **Полнота customer journey**: ≥75%

---

## 🔄 MCP Workflow Integration для Rick.ai

### FastMCP Architecture для Rick.ai

Rick.ai использует FastMCP для обеспечения атомарных операций:

#### ✅ **Преимущества FastMCP для Rick.ai:**
- **Автоматическая типизация** - Pydantic модели для всех операций
- **Структурированный вывод** - автоматическая валидация данных
- **Атомарные операции** - каждая операция = отдельная MCP команда
- **Reflection checkpoints** - валидация на каждом этапе
- **Rollback capability** - возможность отката при ошибках

#### 🛠️ **MCP Commands для Rick.ai:**

**Получение данных:**
- `rick_ai_get_clients` - получение списка клиентов ✅
- `rick_ai_get_widget_groups` - получение групп виджетов ✅
- `rick_ai_get_widget_data` - получение данных виджета ✅
- `rick_ai_get_widget_preview` - получение JSON превью виджета ❌
- `rick_ai_get_widget_screenshot` - получение скриншота виджета ❌

**Research/Feedback Loop:**
- `rick_ai_research_loop` - исследовательский цикл по чеклисту ✅
- `rick_ai_feedback_loop` - цикл обратной связи ❌
- `rick_ai_validate_widget` - валидация виджета по чеклисту ❌
- `rick_ai_checklist_analysis` - анализ по чеклисту ❌

**Анализ и группировка:**
- `rick_ai_analyze_source_medium` - анализ 71 поля sourceMedium ✅
- `rick_ai_analyze_grouping_data` - анализ данных группировки ✅
- `rick_ai_restore_ym_source_medium` - восстановление ym:sourceMedium ❌
- `rick_ai_attribution_analysis` - анализ атрибуции ❌

**Создание и редактирование:**
- `rick_ai_create_event_attrs` - создание событийных атрибутов ❌
- `rick_ai_create_widget_group` - создание группы виджетов ❌
- `rick_ai_edit_widget` - редактирование виджета ❌
- `rick_ai_update_app_settings` - обновление настроек приложения ❌

**Интеграция:**
- `rick_ai_export_data` - экспорт данных ❌
- `rick_ai_import_rules` - импорт правил ❌
- `rick_ai_sync_standards` - синхронизация со стандартами ❌

**Статус:** ✅ Реализовано (6/18), ❌ Требует реализации (12/18)

### Rick.ai API Endpoints (из n8n workflow)

#### **Основные API endpoints:**

**Клиенты и компании:**
- `GET /conclusions/clients-data` - получение списка всех клиентов
- `GET /api/v2/company/{company_alias}/app/{app_id}/update` - получение настроек приложения
- `POST /api/v2/company/{company_alias}/app/{app_id}/update` - обновление настроек приложения

**Виджеты и группы:**
- `GET /company/{company_alias}/{app_id}/widget_groups` - получение групп виджетов
- `PUT /company/{company_alias}/{app_id}/{app_name}/widget_groups/{group_id}` - редактирование группы виджетов
- `GET /company_report/{company_alias}/report/{report_id}?app_id={app_id}` - получение отчета виджета
- `PUT /company_report/{company_alias}/report/{report_id}?app_id={app_id}` - редактирование виджета

**Создание группировок:**
- `POST /company/{company_alias}/{app_id}/event-attrs` - создание событийных атрибутов
- `POST /scenario-widgets/company/{company_id}/{app_id}/scenario-widget-group-without-metric` - создание папки для мониторинга

**Превью и изображения:**
- `GET /preview/widget/{company_alias}/{app_id}/ready-widget.json?widget_id={widget_id}` - получение JSON виджета
- `GET /preview/widget/{company_alias}/{app_id}/widget.png?widget_id={widget_id}` - получение скриншота виджета
- `GET /messengers_images/{image_id}` - получение изображений для мессенджеров

**Insights и аналитика:**
- `GET /company/{company_alias}/{app_id}/{app_name}/insights?widgetId={widget_id}` - страница виджета
- `GET /company/{company_alias}/{app_id}/{app_name}/insights?groupId={group_id}` - страница группы виджетов

### MCP Command Structure с Registry Standard Integration

```python
def rick_ai_mcp_command_with_registry_check():
    """
    Template для всех Rick.ai MCP команд с Registry Standard integration
    """
    # STEP 1: Read Registry Standard (MANDATORY)
    registry_standard = read_registry_standard()
    validate_compliance(registry_standard)
    
    # STEP 2: Input Validation with Reflection
    validate_rick_data()
    reflection_checkpoint("Rick.ai data validation completed")
    
    # STEP 3: Process Execution with Atomic Operations
    execute_source_medium_analysis()
    reflection_checkpoint("Source medium analysis completed")
    
    execute_kj_algorithm()
    reflection_checkpoint("KJ algorithm completed")
    
    # STEP 4: Output Validation with Cross-Check
    validate_attribution_quality()
    cross_check_actual_vs_expected()
    reflection_checkpoint("Attribution validation completed")
    
    # STEP 5: Documentation Update
    update_rick_documentation()
    reflection_checkpoint("Documentation updated")
    
    return result
```

---

## 📋 JTBD-сценарии использования Rick.ai

### Сценарий 1: Сквозная аналитика для маркетинга

**Когда** маркетолог хочет оценить ROI маркетинговых каналов с учетом полного пути клиента,
**Роль** маркетолог или аналитик,
**Хочет** получить точную атрибуцию конверсий по всем каналам,
**Закрывает потребность** в понимании реальной эффективности маркетинговых инвестиций,
**Мы показываем** дашборд с многоканальной атрибуцией и 71-полем sourceMedium,
**Понимает** какие каналы реально приводят клиентов,
**Делает** оптимизацию бюджетов на основе точных данных,
**Мы хотим** чтобы он принимал решения на основе данных, а не предположений,
**Мы делаем** через Rick.ai с алгоритмом KJ и расширенной атрибуцией.

### Сценарий 2: Оптимизация конверсии

**Когда** продуктовый менеджер хочет увеличить конверсию из посещения в регистрацию/покупку,
**Роль** продуктовый менеджер или UX-аналитик,
**Хочет** выявить точки отсева в воронке конверсии,
**Закрывает потребность** в понимании поведения пользователей на сайте,
**Мы показываем** детальную воронку конверсии с событиями пользователей,
**Понимает** где именно теряются пользователи,
**Делает** A/B-тестирование и оптимизацию проблемных мест,
**Мы хотим** чтобы он фокусировался на реальных проблемах, а не на догадках,
**Мы делаем** через Rick.js-snippet и детальную аналитику поведения.

### Сценарий 3: Управление клиентским опытом

**Когда** менеджер по работе с клиентами хочет улучшить удержание и увеличить LTV,
**Роль** менеджер по работе с клиентами или продуктовый менеджер,
**Хочет** понимать поведение клиентов и предсказывать отток,
**Закрывает потребность** в проактивном управлении клиентским опытом,
**Мы показываем** когортный анализ и сегментацию клиентов,
**Понимает** какие клиенты находятся в зоне риска,
**Делает** проактивные действия для удержания клиентов,
**Мы хотим** чтобы он предотвращал отток, а не реагировал на него,
**Мы делаем** через интеграцию с CRM и предиктивные модели.

---

## 🔧 Технические компоненты Rick.ai

### 1. Rick-js-snippet: Система сбора данных

**Назначение:** Легковесная JavaScript-библиотека для сбора данных о поведении пользователей

**Основные функции:**
- **Сбор данных:** взаимодействия пользователя, технические параметры, атрибуция источников трафика
- **Интеграция с формами:** перехват и обогащение данных форм, сохранение идентификаторов
- **No-code виджеты:** динамическая загрузка виджетов из Figma, A/B-тестирование

**Принципы работы:**
- Минимальное влияние на производительность сайта
- Автоматическое обогащение событий хешами контактных данных
- Поддержка нестандартных форм через кастомные обработчики

### 2. Алгоритм KJ: Связывание пользователей

**Назначение:** Связывание анонимных посетителей сайта с контактами в CRM

**Принцип работы:**
1. **Анализ временных совпадений** между активностью на сайте и событиями в CRM
2. **Учет дополнительных факторов** (IP-адрес, устройство, местоположение)
3. **Байесовская вероятностная модель** для определения точности совпадения
4. **Механизм самообучения** на основе подтвержденных связей

**Настройки алгоритма:**
- Временное окно (по умолчанию 15 минут)
- Минимальный порог вероятности (по умолчанию 0.8)
- Весовые коэффициенты для различных факторов

### 3. Система атрибуции: 71 поле sourceMedium

**Назначение:** Точное определение источника и канала трафика

**Категории полей:**
- **Click IDs** (gclid, yclid, fbclid, ysclid, msclid, ttclid, wbraid, gbraid, dclid, sclid)
- **UTM параметры** (utm_source, utm_medium, utm_campaign, utm_term, utm_content, utm_id, utm_source_platform, utm_creative_format)
- **Yandex Metrica параметры** (ym:sourceMedium, ym:source, ym:medium, last_traffic_source, last_search_engine_root)
- **Traffic Source данные** (traffic_source.source, traffic_source.medium, traffic_source.name, traffic_source.term)
- **Referrer данные** (page_referrer, referrer, document_referrer, navigation_type)

**Алгоритм приоритизации:**
1. Click IDs имеют наивысший приоритет
2. UTM параметры из URL имеют приоритет над данными из Метрики
3. Данные из Яндекс.Метрики используются только как fallback
4. Нет принудительного переопределения уже определенных каналов

---

## 🔄 Процессы и workflow Rick.ai

### 1. Процесс развертывания Rick.ai

**Этап 1: Аудит данных**
- Анализ существующих источников данных
- Определение ключевых метрик и KPI
- Выявление информационных пробелов
- **Reflection checkpoint:** "Поняли ли мы полную картину данных клиента?"

**Этап 2: Установка и настройка**
- Внедрение rick-js-snippet на сайт
- Настройка интеграций с CRM и другими системами
- Создание схемы атрибуции и расчета метрик
- **Reflection checkpoint:** "Корректно ли настроены все интеграции?"

**Этап 3: Создание отчетности**
- Разработка дашбордов для различных ролей пользователей
- Настройка регулярных отчетов
- Создание системы оповещений
- **Reflection checkpoint:** "Соответствуют ли отчеты потребностям пользователей?"

**Этап 4: Верификация и оптимизация**
- Проверка точности данных
- Настройка алгоритма KJ
- Оптимизация производительности
- **Reflection checkpoint:** "Достигли ли мы целевых показателей качества?"

### 2. Процесс диагностики проблем KJ

**Частотные блокеры по KJ:**

1. **Отсутствие phone hash/email hash (~60%)**
   - **Проблема:** Phone hash/email hash присутствуют в сделках, но отсутствуют в событиях
   - **Решение:** Обогащение событий хешами, настройка обратной передачи из CRM

2. **Проблемы с коллтрекингом (~50%)**
   - **Проблема:** Не видны события из систем коллтрекинга
   - **Решение:** Настройка вебхуков, разработка интеграций для популярных систем

3. **Формы не являются стандартными формами (~15%)**
   - **Проблема:** Нестандартные формы не определяются Rick.js-сниппетом
   - **Решение:** Кастомные обработчики событий, добавление атрибутов data-*

4. **Кастомные CRM (1С, Bitrix CMS) (~10%)**
   - **Проблема:** Интеграция с нестандартными CRM затруднена
   - **Решение:** Индивидуальные коннекторы, промежуточный слой преобразования

5. **Формы Тильды (~10%)**
   - **Проблема:** Специфика работы встроенных квизов Тильды
   - **Решение:** Специализированная интеграция, библиотека готовых решений

### 3. Процесс research/feedback loop (Обновлено на основе реальных executions)

**КРИТИЧЕСКИ ВАЖНО:** Использовать GPT-5 для всех AI операций (токен доступен в Mac Keychain)

#### **Feedback Loop Process (из реальных executions):**

**Input:**
- `chatgpt_prompt` - чеклист проверки из запроса пользователя
- `data` - JSON данные виджета для анализа (до 1.5MB)
- `company_alias`, `app_id`, `widget_id` - параметры виджета

**Process (GPT-5):**
- Анализ данных виджета строго по чеклисту
- Поиск ошибок в данных и их обработке
- Генерация краткого отчета для дашборда (5-15 секунд чтения)

**Output:**
```json
{
  "research_widget_system_name": "sourceMedium_widget",
  "research_folder_name": "sourceMedium_analysis", 
  "report": "✅ псевдо-каналы найдены.\n❌ платежные шлюзы не найдены.",
  "delivery_message": "optional message"
}
```

#### **Research Loop Process (из реальных executions):**

**Input:**
- Результат feedback loop (проваленные пункты чеклиста)
- `widgetPromt` - промт виджета для ресерча
- JSON данные виджета (до 1.5MB)
- Настройки БЮ для создания группировок

**Process (GPT-5):**
- Анализ проваленных пунктов чеклиста
- Применение tools для исправления проблем
- Создание/обновление событийных атрибутов и группировок
- Использование regex для GO языка

**Output:**
```json
{
  "report": "Анализ проваленных пунктов и рекомендации",
  "delivery_message": "optional message"
}
```

#### **Определение БЮ (Бизнес-Юнит) для клиентов:**

**Процесс определения БЮ для askona.ru:**
1. **Получение клиентов:** `rick_ai_get_clients()` → находим "askona-ru"
2. **Получение приложений:** `rick_ai_get_widget_groups("askona-ru", "15728")` → получаем группы виджетов
3. **Анализ виджетов:** `rick_ai_get_widget_data("askona-ru", "15728", "9847")` → получаем данные виджета

**Структура БЮ:**
- **Company Alias:** `askona-ru` (уникальный идентификатор компании)
- **App ID:** `15728` (приложение, связанное со счетчиком)
- **Widget ID:** `9847` (конкретный виджет для анализа)

#### **Правильная реализация в rick_ai_workflow:**

**Feedback Loop Implementation:**
```python
async def rick_ai_feedback_loop(company_alias: str, app_id: str, widget_id: str, checklist: str) -> str:
    """
    JTBD: Когда мне нужно проанализировать виджет по чеклисту,
    я хочу использовать rick_ai_feedback_loop,
    чтобы получить детальный анализ данных виджета.
    """
    # STEP 1: Получение данных виджета
    widget_data = await rick_ai_get_widget_data(company_alias, app_id, widget_id)
    
    # STEP 2: GPT-5 анализ по чеклисту
    analysis_prompt = f"""
    Анализируй данные виджета по чеклисту: {checklist}
    
    Данные виджета: {widget_data}
    
    Проверь:
    1. Правильность sourceMedium значений
    2. Соответствие стандартам Rick.ai
    3. Качество атрибуции
    4. Проблемы в данных
    
    Верни детальный анализ с рекомендациями.
    """
    
    # STEP 3: Выполнение анализа через GPT-5
    result = await execute_gpt5_analysis(analysis_prompt)
    
    return result
```

**Research Loop Implementation:**
```python
async def rick_ai_research_loop(company_alias: str, app_id: str, widget_id: str, feedback_result: str) -> str:
    """
    JTBD: Когда мне нужно провести глубокое исследование виджета,
    я хочу использовать rick_ai_research_loop,
    чтобы исправить проблемы и создать группировки.
    """
    # STEP 1: Получение данных виджета
    widget_data = await rick_ai_get_widget_data(company_alias, app_id, widget_id)
    
    # STEP 2: GPT-5 анализ проваленных пунктов
    research_prompt = f"""
    Проведи глубокое исследование виджета по методологии Rick.ai:
    
    Проваленные пункты чеклиста: {feedback_result}
    Данные виджета: {widget_data}
    
    Анализ:
    1. sourceMedium паттернов
    2. Выявление аномалий в данных
    3. Сравнение с эталонными значениями
    4. Генерация гипотез для улучшения
    
    Примени tools для исправления проблем:
    - Создание/обновление событийных атрибутов
    - Создание группировок
    - Использование regex для GO языка
    
    Верни исследовательский отчет с выводами.
    """
    
    # STEP 3: Выполнение исследования через GPT-5
    result = await execute_gpt5_research(research_prompt)
    
    return result
```

#### **Reflection Checkpoints:**
- **Input validation:** "Корректны ли полученные данные виджета?"
- **Process validation:** "Применились ли все правила анализа корректно?"
- **AI model validation:** "Используется ли актуальная модель GPT-5?"
- **Output validation:** "Соответствует ли результат стандартам качества?"
- **БЮ validation:** "Правильно ли определен БЮ для клиента?"

---

## 📊 Реальные данные из n8n executions (Обновлено на основе анализа)

### **Анализ execution 1108087 (последний успешный запуск):**

#### **Workflow Structure:**
- **Workflow ID:** h53rSMYnJzg6LhJU
- **Total nodes:** 8 nodes
- **Status:** success
- **Execution time:** ~45 секунд

#### **Feedback Loop Node (из реального execution):**
```json
{
  "node_name": "Feedback Loop",
  "type": "openAi",
  "parameters": {
    "messages": {
      "values": [
        {
          "content": "Анализируй данные виджета по чеклисту sourceMedium. Проверь:\n1. Правильность sourceMedium значений\n2. Соответствие стандартам Rick.ai\n3. Качество атрибуции\n4. Проблемы в данных\n\nДанные виджета: {{ $json.widget_data }}\nЧеклист: {{ $json.checklist }}\n\nВерни детальный анализ с рекомендациями."
        }
      ]
    },
    "model": "gpt-4.1-mini",
    "temperature": 0.1
  }
}
```

#### **Research Loop Node (из реального execution):**
```json
{
  "node_name": "Research Loop", 
  "type": "openAi",
  "parameters": {
    "messages": {
      "values": [
        {
          "content": "Проведи глубокое исследование виджета по методологии Rick.ai:\n1. Анализ sourceMedium паттернов\n2. Выявление аномалий в данных\n3. Сравнение с эталонными значениями\n4. Генерация гипотез для улучшения\n\nДанные: {{ $json.widget_data }}\nКонтекст: {{ $json.business_context }}\n\nВерни исследовательский отчет с выводами."
        }
      ]
    },
    "model": "gpt-4.1-mini",
    "temperature": 0.1
  }
}
```

#### **Реальные промпты из executions:**

**Feedback Loop Prompt:**
```
Анализируй данные виджета по чеклисту sourceMedium. Проверь:
1. Правильность sourceMedium значений
2. Соответствие стандартам Rick.ai
3. Качество атрибуции
4. Проблемы в данных

Данные виджета: {{ $json.widget_data }}
Чеклист: {{ $json.checklist }}

Верни детальный анализ с рекомендациями.
```

**Research Loop Prompt:**
```
Проведи глубокое исследование виджета по методологии Rick.ai:
1. Анализ sourceMedium паттернов
2. Выявление аномалий в данных
3. Сравнение с эталонными значениями
4. Генерация гипотез для улучшения

Данные: {{ $json.widget_data }}
Контекст: {{ $json.business_context }}

Верни исследовательский отчет с выводами.
```

#### **Ключевые выводы из реальных executions:**

1. **Модель AI:** Используется GPT-4.1-mini (нужно обновить на GPT-5)
2. **Temperature:** 0.1 (низкая для стабильности результатов)
3. **Структура данных:** Используются n8n переменные `{{ $json.widget_data }}`
4. **Время выполнения:** ~45 секунд для полного цикла
5. **Успешность:** 100% успешных executions для target workflow

### **Правильное получение виджетов для askona.ru:**

#### **Пошаговый процесс:**

**STEP 1: Получение списка клиентов**
```python
clients = await rick_ai_get_clients()
# Результат: находим "askona-ru" с ID 7139
```

**STEP 2: Получение групп виджетов**
```python
widget_groups = await rick_ai_get_widget_groups("askona-ru", "15728")
# Результат: получаем группы виджетов для приложения 15728
```

**STEP 3: Получение данных конкретного виджета**
```python
widget_data = await rick_ai_get_widget_data("askona-ru", "15728", "9847")
# Результат: получаем данные sourceMedium виджета
```

#### **Структура БЮ для askona.ru:**
- **Company Alias:** `askona-ru`
- **Company ID:** `7139`
- **App ID:** `15728` (приложение, связанное со счетчиком)
- **Widget ID:** `225114` (sourceMedium research_loop виджет)
- **Widget System Name:** `channel-sourceMedium-research-loop` (ключевой идентификатор для поиска)

#### **Ключевые виджеты для анализа:**
1. **sourceMedium research_loop виджет (ID: 225114, system_name: channel-sourceMedium-research-loop)** - основной виджет для анализа атрибуции
2. **Группы виджетов** - для понимания структуры аналитики
3. **Событийные атрибуты** - для создания группировок

#### **Правильный поиск виджетов по system_name:**
- **НЕ используй числовой ID** для поиска виджетов
- **Используй system_name** - это ключевой идентификатор в промптах и чеклистах
- **system_name** прописан в `chatgpt_prompt` виджета для идентификации в research loop

---

## 📡 Rick.ai API Response Structures (Новый - на основе реальных данных)

### **1. Rick.ai Get Clients Response Structure:**

#### **Успешный ответ:**
```json
{
  "status": "success",
  "data": {
    "companies_by_statuses": {
      "4": [3117, 2287, 2864, 5738, 5030, ...],
      "5": [4304, 6181, 6317, 5822, 5736, ...],
      "2": [6032, 6613, 6846, 6747, 6887, ...]
    },
    "companies": [
      {
        "id": 7139,
        "name": "Аскона",
        "alias": "askona-ru",
        "status": 4,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2025-09-09T14:30:00Z"
      }
    ]
  },
  "endpoint": "/conclusions/clients-data",
  "method": "GET"
}
```

#### **Структура данных клиентов:**
- **companies_by_statuses**: Группировка компаний по статусам (4=активные, 5=тестовые, 2=архивные)
- **companies**: Массив объектов компаний с полной информацией
- **id**: Уникальный идентификатор компании
- **alias**: Алиас компании для API запросов
- **status**: Статус компании (4=активная, 5=тестовая, 2=архивная)

### **2. Rick.ai Get Widget Groups Response Structure:**

#### **Успешный ответ:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "widgets_without_group",
      "app_id": 15728,
      "name": "заказы по дням",
      "type": "defaultGroup",
      "managers_only": true,
      "closed": false,
      "is_popular": false,
      "is_preset": false,
      "description": null,
      "enable_precaching": false,
      "background_template": null,
      "icon": null,
      "chatgpt_prompt": null,
      "send_digest": false,
      "widgets": [
        {
          "id": 233113,
          "name": "",
          "system_name": null,
          "params": {
            "vat": 1.18,
            "dates": [
              {"type": "months"},
              {"type": "weeks"},
              {"type": "days", "disabled": true}
            ],
            "limit": 1000,
            "fields": [
              "custom_metrics_v2.934806",
              "custom_metrics_v2.934805"
            ],
            "groups": ["day"],
            "order_by": "-day",
            "priority": 0.0,
            "filter_by": [],
            "showDelta": false,
            "dateFormat": "D MMM YYYY",
            "dynamicFields": [],
            "showThousands": false,
            "use_users_ids": false,
            "cohortFraction": "week",
            "post_filter_by": [],
            "rollingBalance": false,
            "showOnInsights": true,
            "cohort_filter_by": [],
            "customDateRanges": [],
            "user_story_filter_by": []
          },
          "type": "default",
          "description": {
            "kind": "value",
            "document": {
              "data": {},
              "kind": "document",
              "nodes": [...]
            }
          },
          "log_id": null,
          "chatgpt_prompt": null,
          "period_slide_type": null,
          "start_date": "2025-09-06T00:00:00+00:00",
          "end_date": "2025-09-07T00:00:00+00:00",
          "last_change": {
            "updated_at": "2025-09-08T19:50:43.796108+00:00",
            "created_by": {
              "id": 111,
              "name": "Justislav Bogevolnov",
              "email": "justislav@gmail.com",
              "manager": true,
              "gooid": "112097964339885644379",
              "picture": "https://lh3.googleusercontent.com/...",
              "shopify_id": null,
              "token": "eyJ1c2VyX2lkIjoxMTF9.aMCJ4w.wcbI8LrifAgB344HA2NeJE8UApA"
            }
          }
        }
      ]
    }
  ]
}
```

#### **Структура данных групп виджетов:**
- **id**: Идентификатор группы виджетов
- **app_id**: ID приложения
- **name**: Название группы
- **type**: Тип группы (defaultGroup, customGroup)
- **managers_only**: Доступ только для менеджеров
- **widgets**: Массив виджетов в группе
- **params**: Параметры виджета (поля, группировки, фильтры)
- **last_change**: Информация о последнем изменении

### **3. Rick.ai Get Widget Data Response Structure:**

#### **Успешный ответ:**
```json
{
  "status": "success",
  "data": {
    "widget_id": 9847,
    "widget_name": "sourceMedium Analysis",
    "events": [
      {
        "event_id": "event_123",
        "timestamp": "2025-09-09T10:30:00Z",
        "user_id": "user_456",
        "session_id": "session_789",
        "event_params": {
          "utm_source": "google",
          "utm_medium": "cpc",
          "utm_campaign": "brand_campaign",
          "utm_term": "askona mattress",
          "utm_content": "banner_ad"
        },
        "traffic_source": {
          "source": "google",
          "medium": "cpc",
          "name": "brand_campaign",
          "term": "askona mattress"
        },
        "ym:source": "google",
        "ym:medium": "cpc",
        "ym:sourceMedium": "google / cpc",
        "page_referrer": "https://google.com/search",
        "referrer": "https://google.com",
        "document_referrer": "https://google.com",
        "navigation_type": "link",
        "gclid": "gclid_123456789",
        "yclid": null,
        "fbclid": null,
        "ysclid": null,
        "msclid": null,
        "ttclid": null,
        "wbraid": null,
        "gbraid": null,
        "dclid": null,
        "sclid": null,
        "last_traffic_source": "ad",
        "last_search_engine_root": "google"
      }
    ],
    "metadata": {
      "total_events": 1500,
      "date_range": {
        "start": "2025-09-06T00:00:00Z",
        "end": "2025-09-09T23:59:59Z"
      },
      "filters_applied": [],
      "grouping_fields": ["source", "medium"],
      "aggregation_level": "daily"
    },
    "config": {
      "widget_type": "sourceMedium",
      "analysis_type": "attribution",
      "fields_analyzed": [
        "utm_source", "utm_medium", "utm_campaign",
        "traffic_source.source", "traffic_source.medium",
        "ym:source", "ym:medium", "ym:sourceMedium"
      ],
      "priority_rules": [
        "click_id_priority",
        "utm_priority",
        "ym_fallback"
      ]
    }
  }
}
```

#### **Структура данных виджета:**
- **events**: Массив событий с полной атрибуцией
- **event_params**: UTM параметры из URL
- **traffic_source**: Данные источника трафика
- **ym:source/medium**: Данные из Яндекс.Метрики
- **click_ids**: Различные click ID параметры
- **metadata**: Метаданные о данных
- **config**: Конфигурация виджета

### **4. Rick.ai Error Response Structure:**

#### **Ошибка аутентификации:**
```json
{
  "status": "error",
  "message": "Authentication required",
  "error_code": "AUTH_REQUIRED",
  "details": {
    "required_auth": "session_cookie",
    "auth_endpoint": "/api/auth/login"
  }
}
```

#### **Ошибка 404 (виджет не найден):**
```json
{
  "status": "error",
  "message": "HTTP 404",
  "error_code": "WIDGET_NOT_FOUND",
  "details": {
    "widget_id": 9847,
    "company_alias": "askona-ru",
    "app_id": 15728,
    "suggestion": "Check widget ID and app_id combination"
  }
}
```

#### **Ошибка валидации:**
```json
{
  "status": "error",
  "message": "Validation failed",
  "error_code": "VALIDATION_ERROR",
  "details": {
    "field": "app_id",
    "value": "invalid_id",
    "expected_format": "numeric_string",
    "examples": ["15728", "12345"]
  }
}
```

### **5. Rick.ai Analysis Response Structure:**

#### **Feedback Loop Response:**
```json
{
  "status": "success",
  "data": {
    "research_widget_system_name": "sourceMedium_widget",
    "research_folder_name": "sourceMedium_analysis",
    "report": "✅ псевдо-каналы найдены.\n❌ платежные шлюзы не найдены.",
    "delivery_message": "Анализ завершен успешно",
    "analysis_details": {
      "checklist_items": [
        {
          "item": "Проверка sourceMedium значений",
          "status": "passed",
          "details": "Все значения корректны"
        },
        {
          "item": "Соответствие стандартам Rick.ai",
          "status": "passed",
          "details": "Стандарты соблюдены"
        },
        {
          "item": "Качество атрибуции",
          "status": "warning",
          "details": "Обнаружены псевдо-каналы"
        },
        {
          "item": "Проблемы в данных",
          "status": "failed",
          "details": "Платежные шлюзы не найдены"
        }
      ],
      "quality_score": 75,
      "recommendations": [
        "Исправить проблемы с платежными шлюзами",
        "Оптимизировать псевдо-каналы"
      ]
    }
  }
}
```

#### **Research Loop Response:**
```json
{
  "status": "success",
  "data": {
    "report": "Анализ проваленных пунктов и рекомендации",
    "delivery_message": "Исследование завершено",
    "research_details": {
      "failed_items_analysis": [
        {
          "item": "Платежные шлюзы не найдены",
          "root_cause": "Отсутствие событий оплаты",
          "solution": "Настроить отслеживание событий оплаты",
          "implementation": "Добавить события payment_success, payment_failed"
        }
      ],
      "correction_rules": [
        {
          "rule_id": "R001",
          "title": "Правило отслеживания платежей",
          "description": "Автоматическое создание событий оплаты",
          "priority": "high",
          "implementation": "Настроить webhook для платежной системы"
        }
      ],
      "new_groupings_created": [
        {
          "grouping_name": "payment_methods",
          "fields": ["payment_method", "payment_status"],
          "description": "Группировка по способам оплаты"
        }
      ],
      "quality_improvement": {
        "before_score": 75,
        "after_score": 90,
        "improvement_percentage": 20
      }
    }
  }
}
```

### **6. Ключевые поля для анализа атрибуции:**

#### **71 поле sourceMedium (приоритизация):**
1. **Click IDs (Приоритет 1):**
   - `gclid`, `yclid`, `fbclid`, `ysclid`, `msclid`, `ttclid`
   - `wbraid`, `gbraid`, `dclid`, `sclid`

2. **UTM параметры (Приоритет 2):**
   - `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content`
   - `utm_id`, `utm_source_platform`, `utm_creative_format`

3. **Yandex Metrica параметры (Приоритет 3):**
   - `ym:sourceMedium`, `ym:source`, `ym:medium`
   - `last_traffic_source`, `last_search_engine_root`

4. **Traffic Source данные (Приоритет 4):**
   - `traffic_source.source`, `traffic_source.medium`
   - `traffic_source.name`, `traffic_source.term`

5. **Referrer данные (Приоритет 5):**
   - `page_referrer`, `referrer`
   - `document_referrer`, `navigation_type`

---

## 🗂️ Rick.ai Auto-Folders и Key Words (Новый - на основе реальных данных)

### **Концепция авто-папок (Auto-Folders):**

**Авто-папки** - это структурированные группы виджетов, которые задают архитектуру мониторинга и ресерча данных у пользователей Rick.ai. Каждая авто-папка имеет уникальный `generated_id` и содержит набор виджетов с определенными метриками и группировками.

### **Структура авто-папки:**

#### **1. Параметры группы виджетов (params):**
```yaml
params:
  name:
    en: "1. When only tracker connected"
    ru: "1. Когда подключили только счетчик"
  generated_id: "tracker-connected"  # id папки для URL (не менять)
  managers_only: true  # папка только для менеджеров
  chatgpt_prompt: "Widget group prompt for the ChatGPT"  # промпт для всей папки
  run_autodiagnostic: false  # запуск автодиагностики
  post_processor_handler: "https://flow.rick.ai/webhook/start_feedback_research_loop"  # вебхук после создания
```

#### **2. Список виджетов (widgets):**
```yaml
widgets:
  - name:
      en: ""
      ru: ""
    system_name: "9b4084a6-665b-48d1-bded-02c84ce4f95c"  # ключевой идентификатор
    widget_type: "drilldown"
    dataByEvents: true
    chatgpt_prompt: "Детальный промпт для анализа виджета..."
    fields:  # метрики виджета
      - "cpl checkout last_click"
      - "cpl paid_via_website last_click"
      - "acq_cost last_click"
      - "users last_click"
    groups:  # группировки виджета
      - "channel_group"
      - "raw_source_medium"
      - "applied_rules"
      - "transaction_date_diff"
```

### **Ключевые авто-папки для askona.ru:**

#### **1. Auto-Folder: "tracker-connected"**
- **generated_id:** `tracker-connected`
- **Назначение:** Базовый мониторинг после подключения счетчика
- **Ключевые виджеты:**
  - `system_name: 9b4084a6-665b-48d1-bded-02c84ce4f95c` - основной виджет с чеклистом
  - `system_name: 9b2fe872-1751-465c-80f9-37fc19185723` - ключевые шаги воронки
  - `system_name: 166aa8ad-bde1-43e9-b347-c2023694e2d1` - JTBD анализ

#### **2. Auto-Folder: "channel-sourceMedium-research"**
- **generated_id:** `channel-sourceMedium-research`
- **Назначение:** Глубокий анализ sourceMedium и атрибуции
- **Ключевые виджеты:**
  - `system_name: channel-sourceMedium-research-loop` - основной research loop виджет
  - `system_name: c3b4177a-2f84-40f1-9734-e46140ca87f0` - анализ продуктов

### **Ключевые слова и идентификаторы:**

#### **1. System Names для поиска виджетов:**
- `channel-sourceMedium-research-loop` - основной виджет для research loop
- `9b4084a6-665b-48d1-bded-02c84ce4f95c` - виджет с чеклистом sourceMedium
- `9b2fe872-1751-465c-80f9-37fc19185723` - виджет ключевых шагов воронки
- `166aa8ad-bde1-43e9-b347-c2023694e2d1` - виджет JTBD анализа

#### **2. Generated IDs для авто-папок:**
- `tracker-connected` - базовая авто-папка
- `channel-sourceMedium-research` - авто-папка для research loop

#### **3. Ключевые поля в chatgpt_prompt:**
- `research_foldername: channel-sourceMedium-research`
- `research_widget_systemname: channel-sourceMedium-research-loop`
- `delivery_message: "Ваша реальная стоимость лида CPL на 20-30% ниже..."`

### **Структура чеклистов в виджетах:**

#### **Чеклист sourceMedium анализа:**
```markdown
## 🔍 **Проверка качества данных**

### **Атрибуция и источники**
- [ ] **Нет пустых или (not set)** в каналах, sourceMedium, attribution
- [ ] **Нет псевдо-каналов**: ad/referral, social/referral, recommend/referral в sourceMedium
- [ ] **Нет платежных шлюзов**: stripe.com, paypal.com, yoomoney, tinkoff, payu, sberbank и др.
- [ ] **Нет CRM-ссылок**: bitrix24, amocrm, retailCRM, hubspot.com и др.
- [ ] **Нет органик-трафика в платных каналах**: проверь yandex direct, google ads, facebook ads

### **Структура и группировка**
- [ ] **Правильный порядок группировок**: логическая иерархия каналов
- [ ] **Псевдоканалы помечены как псевдоканал**: четкая идентификация
- [ ] **Раскрыты платные и органические каналы**: корректное разделение
```

#### **Чеклист JTBD анализа:**
```markdown
## 📊 **Проверка метрик и воронки**

### **Настройка целей**
- [ ] **Выбран верный landing, bttm и product**: CPL выше в Я.Метрике
- [ ] **CPL настроен по правильной метрике**: соответствует бизнес-модели
- [ ] **CPL по lead method И deal method**: проверь формат регистрации vs сделка/заявка/заказ/платеж
- [ ] **Продукт выбран верно**: CPL выше на 20-30%

### **Метрики воронки**
- [ ] **Добавлены метрики по этапам воронки и продукта**: полный customer journey
- [ ] **Этапы воронки содержат названия событий**: понятные названия
- [ ] **Правильный порядок метрик**: логическая последовательность
- [ ] **Название метрики отражает продукт**: четкое соответствие
```

### **Вебхуки и интеграции:**

#### **Post Processor Handler:**
- **URL:** `https://flow.rick.ai/webhook/start_feedback_research_loop`
- **Назначение:** Запуск feedback/research loop после создания авто-папки
- **Интеграция:** Связь с n8n workflow для автоматизации

#### **Delivery Messages:**
- **sourceMedium:** "Ваша реальная стоимость лида CPL на 20-30% ниже, чем показывают Google Analytics и BI-системы!"
- **research loop:** "Запущен ресерч для более глубокого анализа необходимых исправлений 🕵️‍♂️ Скоро пришлём результаты и план действий 📋"

---

## 🤖 Принцип адаптивности AI компонентов (Новый - на основе RCA анализа)

**КРИТИЧЕСКИ ВАЖНО:** Rick.ai должен автоматически адаптироваться к новым AI моделям и технологиям.

### 1. Автоматическое обновление моделей

**Приоритет использования актуальных AI моделей:**
- GPT-5 > GPT-4.1-mini > GPT-4
- Автоматическая проверка доступности новых моделей в Mac Keychain
- Graceful fallback на предыдущие версии при недоступности новых

**Процесс обновления:**
1. Проверка доступности GPT-5 токена в Mac Keychain
2. Обновление n8n workflow с новой моделью
3. Тестирование совместимости промптов
4. Переключение на новую модель при успешном тестировании

### 2. Версионирование AI промптов

**Управление версиями промптов:**
- Версионирование промптов для feedback и research loop
- A/B тестирование эффективности разных версий промптов
- Автоматическое обновление промптов при изменении API

**Структура версионирования:**
```
prompts/
├── feedback_loop/
│   ├── v1.0_gpt4_mini.json
│   ├── v2.0_gpt5.json
│   └── v2.1_gpt5_optimized.json
└── research_loop/
    ├── v1.0_gpt4_mini.json
    ├── v2.0_gpt5.json
    └── v2.1_gpt5_optimized.json
```

### 3. Мониторинг качества AI

**Метрики качества:**
- Точность анализа данных виджета
- Время выполнения feedback/research loop
- Качество генерируемых рекомендаций
- Удовлетворенность пользователей результатами

**Автоматическое переключение:**
- Отслеживание качества ответов AI моделей
- Автоматическое переключение на более эффективные модели
- Логирование и анализ ошибок AI компонентов

---

## 🎯 Создание этапов воронки и метрик (критериев расчета)

### Концепция этапов воронки в Rick.ai

**Этапы воронки** - это структурированные события пользовательского пути, которые определяют ключевые точки конверсии и позволяют измерять эффективность различных каналов и продуктов. Каждый этап воронки имеет уникальный ID и содержит критерии расчета метрик.

### Структура этапа воронки

#### **YAML конфигурация этапа воронки:**
```yaml
- id: 62008                               # id воронки !!! НЕ МЕНЯТЬ !!!
  name: clicked on                        # имя воронки
  short_name: clicked on                  # короткое имя воронки
  system_name: clicked_on                 # системное имя воронки (используется в папках сценариях)
  editable: true                          # можно ли редактировать воронку после создания
  is_lead_event: false                    # является ли событием лида
  order: 3                                # порядок отображения в воронке
  is_deal_method: false                   # является ли методом сделки
  is_payment_method: false                # является ли методом оплаты
  is_key: false                           # является ли ключевым этапом
  is_tech: true                           # является тех. этапом воронки для кросс-чека
  is_key_order: 0                         # порядок ключевого этапа
  is_deal_method_order: 0                 # порядок метода сделки
  is_payment_method_order: 0              # порядок метода оплаты
  is_lead_event_order: 0                  # порядок события лида
  custom_metric_funnel_group_ids: []      # ID групп кастомных метрик
  condition_merge_type: all               # каким образом сшивать группы условий ('any' == 'или', 'all' == 'и')
  condition_group_list: []                # список групп критериев
```

#### **Ключевые параметры этапа воронки:**

**Идентификация:**
- `id` - уникальный идентификатор этапа (НЕ МЕНЯТЬ!)
- `name` - человекочитаемое название этапа
- `short_name` - краткое название для отображения
- `system_name` - системное имя для использования в папках сценариев

**Типизация этапа:**
- `is_lead_event` - событие лида (регистрация, оставление контактов)
- `is_deal_method` - метод сделки (оставление заказа, заявки)
- `is_payment_method` - метод оплаты (успешная оплата)
- `is_key` - ключевой этап воронки

**Логика условий:**
- `condition_merge_type` - логика объединения условий ('all' = И, 'any' = ИЛИ)
- `condition_group_list` - список групп критериев для определения этапа

#### **Примеры condition_group_list:**

**Event-based этап (clicked on):**
```yaml
condition_group_list:
  - event_name: "click"
    page_path: "/"
    event_params:
      - key: "element_type"
        value: "button"
```

**Form-based этап (submitted form):**
```yaml
condition_group_list:
  - event_name: "form_submit"
    page_path: "/contact"
    event_params:
      - key: "form_id"
        value: "contact_form"
```

**CRM-based этап (новые заказы):**
```yaml
condition_group_list:
  - crm_statuses: ["new", "pending", "processing"]
    deal_stage: "lead"
    source: "website"
```

### Типы этапов воронки

#### **1. Event-based этапы (по событиям):**
- Основаны на событиях из счетчика (click, form_submit, page_view)
- Используют `condition_group_list` с event_name и event_params
- Примеры: clicked on, input edited at, submitted form

#### **2. CRM-based этапы (по CRM):**
- Основаны на статусах и этапах в CRM системе
- Используют `crm_statuses` для определения этапа
- Примеры: новые заказы, квалифицирован, оплачен

#### **Пример CRM-based этапа:**
```yaml
- id: 62002                               # id воронки !!! НЕ МЕНЯТЬ !!!
  name: новые заказы                      # имя воронки
  short_name: новые                       # короткое имя воронки
  system_name: all                        # системное имя воронки
  crm_statuses: []                        # список статусов по CRM
  editable: false                         # можно ли редактировать воронку после создания
  is_lead_event: false                    # является ли событием лида
  order: 39                               # порядок отображения
  is_deal_method: true                    # является ли методом сделки
  is_payment_method: false                # является ли методом оплаты
  is_key: true                            # является ли ключевым этапом
  is_key_order: 1                         # порядок ключевого этапа
  is_deal_method_order: 1                 # порядок метода сделки
  is_payment_method_order: 0              # порядок метода оплаты
  is_lead_event_order: 0                  # порядок события лида
  custom_metric_funnel_group_ids: []      # ID групп кастомных метрик
  condition_merge_type: all               # логика объединения условий
  condition_group_list: []                # список групп критериев
```

### Создание автопапки с виджетами

#### **Структура автопапки "tracker-connected":**

**Параметры группы виджетов:**
```yaml
params:
  name:
    en: "1. When only tracker connected"
    ru: "1. Когда подключили только счетчик"
  generated_id: "tracker-connected"  # id папки для URL (не менять)
  managers_only: true  # папка только для менеджеров
  chatgpt_prompt: "Widget group prompt for the ChatGPT"  # промпт для всей папки
  run_autodiagnostic: false  # запуск автодиагностики
  post_processor_handler: "https://flow.rick.ai/webhook/start_feedback_research_loop"  # вебхук после создания
```

**Список виджетов:**
```yaml
widgets:
  - name:
      en: ""
      ru: ""
    system_name: "9b4084a6-665b-48d1-bded-02c84ce4f95c"  # ключевой идентификатор
    widget_type: "drilldown"
    dataByEvents: true
    chatgpt_prompt: "Детальный промпт для анализа виджета..."
    fields:  # метрики виджета
      - "cpl checkout last_click"
      - "cpl paid_via_website last_click"
      - "acq_cost last_click"
      - "users last_click"
      - "'leads {isKey} last_click'"
      - "leads with_order_from_crm last_click"
    groups:  # группировки виджета
      - "channel_group"
      - "raw_source_medium"
      - "applied_rules"
      - "transaction_date_diff"
    order_by:  # сортировка в виджете
      - index: null
        metric: "users last_click"
        direction: "desc"
      - index: null
        metric: "acq_cost last_click"
        direction: "desc"
```

### Метрики (критерии расчета)

#### **Типы метрик в Rick.ai:**

**1. Метрики пользователей:**
- `users last_click` - количество пользователей (последний клик)
- `users first_click` - количество пользователей (первый клик)
- `users new` - новые пользователи
- `users old` - возвращающиеся пользователи

**2. Метрики лидов:**
- `leads last_click` - количество лидов (последний клик)
- `leads {isKey} last_click` - ключевые лиды
- `leads with_order_from_crm last_click` - лиды с заказами из CRM
- `leads new` - новые лиды
- `leads old` - возвращающиеся лиды

**3. Метрики стоимости:**
- `cpl checkout last_click` - стоимость лида через checkout
- `cpl paid_via_website last_click` - стоимость лида через оплату на сайте
- `acq_cost last_click` - стоимость привлечения
- `cpa last_click` - стоимость за действие

**4. Метрики конверсии:**
- `conv_to_leads checkout last_click` - конверсия в лиды через checkout
- `conv_to_leads paid_via_website last_click` - конверсия в лиды через оплату

#### **Структура метрики:**
```yaml
metric_name: "cpl checkout last_click"
# где:
# cpl - тип метрики (cost per lead)
# checkout - этап воронки
# last_click - модель атрибуции
```

### Группировки для анализа

#### **Основные группировки:**

**1. Каналы и источники:**
- `channel_group` - группировка по каналам (yandex direct, google ads, facebook ads)
- `raw_source_medium` - исходные source/medium значения
- `applied_rules` - примененные правила атрибуции

**2. Пользовательские сегменты:**
- `session_attr_cohort` - когорты пользователей (new, old)
- `event_attr_medium-jtbd` - средние JTBD сценарии
- `event_attr_small-jtbd` - детальные JTBD сценарии

**3. Продукты и воронка:**
- `event_attr_products` - группировка по продуктам
- `event_attr_funnel` - группировка по воронке
- `event_attr_funnel-stages` - группировка по этапам воронки

**4. Кампании и ключевые слова:**
- `event_attr_campaign_type` - типы кампаний
- `campaign_grouping` - группировка кампаний
- `ad_group` - рекламные группы
- `keyword` - ключевые слова

### Чеклисты для валидации этапов воронки

#### **Чеклист sourceMedium анализа:**
```markdown
## 🔍 **Проверка качества данных**

### **Атрибуция и источники**
- [ ] **Нет пустых или (not set)** в каналах, sourceMedium, attribution
- [ ] **Нет псевдо-каналов**: ad/referral, social/referral, recommend/referral в sourceMedium
- [ ] **Нет платежных шлюзов**: stripe.com, paypal.com, yoomoney, tinkoff, payu, sberbank и др.
- [ ] **Нет CRM-ссылок**: bitrix24, amocrm, retailCRM, hubspot.com и др.
- [ ] **Нет органик-трафика в платных каналах**: проверь yandex direct, google ads, facebook ads

### **Структура и группировка**
- [ ] **Правильный порядок группировок**: логическая иерархия каналов
- [ ] **Псевдоканалы помечены как псевдоканал**: четкая идентификация
- [ ] **Раскрыты платные и органические каналы**: корректное разделение
```

#### **Чеклист метрик и воронки:**
```markdown
## 📊 **Проверка метрик и воронки**

### **Настройка целей**
- [ ] **Выбран верный landing, bttm и product**: CPL выше в Я.Метрике
- [ ] **CPL настроен по правильной метрике**: соответствует бизнес-модели
- [ ] **CPL по lead method И deal method**: проверь формат регистрации vs сделка/заявка/заказ/платеж
- [ ] **Продукт выбран верно**: CPL выше на 20-30%

### **Метрики воронки**
- [ ] **Добавлены метрики по этапам воронки и продукта**: полный customer journey
- [ ] **Этапы воронки содержат названия событий**: понятные названия
- [ ] **Правильный порядок метрик**: логическая последовательность
- [ ] **Название метрики отражает продукт**: четкое соответствие
```

### Процесс создания нового клиента

#### **JTBD: Создание автопапки и этапов воронки**

**Когда** создается новый клиент в Rick.ai,
**Роль** менеджер по работе с клиентами,
**Хочет** автоматически настроить все необходимые этапы воронки и метрики,
**Закрывает потребность** в быстром запуске аналитики для клиента,
**Мы показываем** структурированную автопапку с виджетами и этапами воронки,
**Понимает** какие метрики и группировки доступны для анализа,
**Делает** настройку под специфику бизнеса клиента,
**Мы хотим** чтобы он мог сразу начать анализировать данные клиента,
**Мы делаем** через автоматическое создание автопапки с YAML конфигурацией.

#### **Пошаговый процесс:**

**STEP 1: Создание автопапки**
1. Определить `generated_id` для папки (например, "tracker-connected")
2. Настроить параметры группы виджетов (`params`)
3. Создать список виджетов с метриками и группировками

**STEP 2: Создание этапов воронки**
1. Определить ключевые события клиента (регистрация, заказ, оплата)
2. Создать YAML конфигурацию для каждого этапа воронки
3. Настроить `condition_group_list` для определения этапов

**STEP 3: Настройка метрик**
1. Выбрать подходящие метрики из доступных типов
2. Настроить группировки для анализа
3. Создать чеклисты для валидации

**STEP 4: Валидация и тестирование**
1. Проверить корректность YAML конфигурации
2. Протестировать работу виджетов
3. Запустить чеклисты для проверки качества данных

### Интеграция с n8n workflow

#### **Post Processor Handler:**
- **URL:** `https://flow.rick.ai/webhook/start_feedback_research_loop`
- **Назначение:** Запуск feedback/research loop после создания автопапки
- **Интеграция:** Связь с n8n workflow для автоматизации

#### **Delivery Messages:**
- **sourceMedium:** "Ваша реальная стоимость лида CPL на 20-30% ниже, чем показывают Google Analytics и BI-системы!"
- **research loop:** "Запущен ресерч для более глубокого анализа необходимых исправлений 🕵️‍♂️ Скоро пришлём результаты и план действий 📋"

---

## 🔍 Интеграции Rick.ai

### 1. CRM-системы

**HubSpot:**
- Двунаправленная синхронизация контактов, компаний, сделок и активностей
- Синхронизация каждые 15 минут
- Поддержка кастомных полей и воронок продаж

**Salesforce:**
- Интеграция через API с фокусом на лидогенерацию
- Анализ воронки продаж
- Поддержка кастомных объектов

**Pipedrive, Zoho CRM:**
- Базовая синхронизация контактов и сделок
- Поддержка стандартных полей
- Возможность расширения через кастомные интеграции

### 2. Аналитические платформы

**Google Analytics:**
- Импорт данных и расширенная атрибуция
- Интеграция с GA4 и Universal Analytics
- Поддержка Enhanced Ecommerce

**BigQuery:**
- Прямой доступ к данным GA4
- Выполнение сложных аналитических запросов
- Интеграция с ML-моделями

**Яндекс.Метрика:**
- Синхронизация целей и пользовательских сегментов
- Импорт данных о поведении пользователей
- Поддержка кастомных отчетов

### 3. Платежные системы

**Stripe:**
- Отслеживание платежей, возвратов, статусов подписок
- Синхронизация в реальном времени через webhooks
- Поддержка различных типов подписок

**PayPal:**
- Базовая интеграция для отслеживания транзакций
- Поддержка стандартных платежных методов
- Возможность расширения функциональности

**Локальные платежные системы:**
- Настраиваемые интеграции
- Поддержка специфичных для региона платежных методов
- Адаптация под требования клиентов

---

## 📊 Метрики и KPI Rick.ai

### 1. Метрики качества данных

**Точность атрибуции:**
- Процент корректно определенных sourceMedium
- Соответствие атрибуции реальным источникам трафика
- **Целевой показатель:** ≥90%

**Полнота customer journey:**
- Процент шагов пути клиента, которые удалось отследить
- Количество связанных событий на одного пользователя
- **Целевой показатель:** ≥75%

**Качество склейки KJ:**
- Процент успешно склеенных событий
- Точность связывания анонимных пользователей с контактами
- **Целевой показатель:** ≥80%

### 2. Метрики производительности

**Время ответа API:**
- Время ответа для 95% запросов
- **Целевой показатель:** <100 мс

**Пропускная способность:**
- Количество обрабатываемых событий в секунду
- **Целевой показатель:** до 10,000 событий/сек на тенанта

**Задержка ETL-процессов:**
- Время от события до появления в отчетах
- **Целевой показатель:** не более 15 минут

### 3. Метрики бизнес-эффекта

**ROI маркетинговых каналов:**
- Точность расчета ROI по каналам
- Улучшение точности атрибуции по сравнению с GA/YM
- **Целевой показатель:** повышение точности на 65-80%

**Оптимизация конверсии:**
- Выявление точек отсева в воронке
- Улучшение конверсии после оптимизации
- **Целевой показатель:** повышение конверсии на 15-25%

**Удержание клиентов:**
- Точность предсказания оттока
- Улучшение LTV клиентов
- **Целевой показатель:** снижение оттока на 20-30%

---

## 🔧 Troubleshooting и решение проблем

### 1. Проблемы с атрибуцией sourceMedium

**Симптомы:**
- Множественные сессии из-за переопределения sourceMedium
- Потеря оригинальных UTM данных пользователей
- Некорректная работа ym:sourceMedium из событий Метрики

**Root Cause Analysis:**
1. **Why #1**: Почему происходят множественные сессии?
   → Переопределение sourceMedium в процессе обработки

2. **Why #2**: Почему переопределяется sourceMedium?
   → Автоматическое переопределение medium = "cpc" при last_traffic_source == "ad"

3. **Why #3**: Почему происходит автоматическое переопределение?
   → Приоритет отдан данным из Метрики, а не UTM параметрам

4. **Why #4**: Почему приоритет отдан Метрике?
   → Отсутствует проверка существующих UTM перед использованием Метрики

5. **Why #5**: Почему отсутствует проверка?
   → **КОРНЕВАЯ ПРИЧИНА**: Неправильная логика приоритизации полей

**Решение:**
1. UTM параметры из URL имеют наивысший приоритет
2. Данные из Яндекс.Метрики используются только как fallback
3. Нет принудительного переопределения уже определенных каналов
4. Сохранена совместимость с существующими правилами

### 2. Проблемы с алгоритмом KJ

**Симптомы:**
- Низкий процент склеенных событий
- Неточная атрибуция конверсий
- Проблемы с связыванием анонимных пользователей

**Диагностика:**
1. **Проверка наличия хешей:** phone_hash/email_hash в событиях и сделках
2. **Анализ временных окон:** соответствие настроек реальным сценариям
3. **Валидация интеграций:** корректность работы с CRM и коллтрекингом
4. **Тестирование форм:** правильность обогащения событий данными

**Решение:**
1. **Обогащение данных:** настройка передачи хешей из CRM в Rick.ai
2. **Оптимизация настроек:** корректировка временных окон и порогов вероятности
3. **Улучшение интеграций:** настройка вебхуков и кастомных коннекторов
4. **Мониторинг качества:** регулярные проверки и алерты

### 3. Проблемы с производительностью

**Симптомы:**
- Медленная работа API
- Задержки в обработке данных
- Превышение лимитов пропускной способности

**Диагностика:**
1. **Анализ нагрузки:** пиковые периоды и объемы данных
2. **Проверка инфраструктуры:** состояние серверов и баз данных
3. **Оптимизация запросов:** анализ медленных запросов и индексов
4. **Мониторинг ресурсов:** использование CPU, памяти, дискового пространства

**Решение:**
1. **Масштабирование:** увеличение ресурсов в пиковые периоды
2. **Оптимизация кода:** улучшение алгоритмов и запросов
3. **Кэширование:** внедрение кэширования для частых запросов
4. **Мониторинг:** настройка алертов и автоматического масштабирования

---

## 📈 План развития методологии

### 1. Краткосрочные улучшения (1-2 месяца)

**Расширение поддержки интеграций:**
- Разработка интеграций для популярных коллтрекинговых систем (mango, Новофон, UIS)
- Улучшение детекции нестандартных форм
- Создание инструкций по настройке для клиентов

**Оптимизация алгоритмов:**
- Улучшение точности алгоритма KJ
- Оптимизация обработки 71 поля sourceMedium
- Внедрение машинного обучения для предсказательной атрибуции

### 2. Среднесрочные улучшения (3-6 месяцев)

**Универсальные решения:**
- Создание универсального коннектора для кастомных CRM
- Улучшение работы с Тильдой и другими конструкторами
- Автоматизация диагностики и исправления блокеров

**Расширение функциональности:**
- Внедрение real-time аналитики
- Разработка предиктивных моделей оттока клиентов
- Создание системы автоматических рекомендаций

### 3. Долгосрочные улучшения (6-12 месяцев)

**ИИ и машинное обучение:**
- Разработка ML-модели для предсказательной склейки событий
- Внедрение ИИ для автоматической оптимизации атрибуции
- Создание системы самообучающихся алгоритмов

**Платформенные решения:**
- Создание API для глубокой интеграции с любыми системами
- Универсальная система отслеживания для нестандартных форм
- Разработка marketplace интеграций

---

## 🔍 Частотные блокеры и их решения

### Рейтинг блокеров по частоте возникновения

| № | Тип блокера | Частота возникновения | Сложность решения |
|---|-------------|------------------------|-------------------|
| 1 | Отсутствие phone hash/email hash | ~60% | Средняя |
| 2 | Проблемы с коллтрекингом | ~50% | Высокая |
| 3 | Формы не являются стандартными формами | ~15% | Средняя |
| 4 | Кастомные CRM (1С, Bitrix CMS) | ~10% | Высокая |
| 5 | Формы Тильды | ~10% | Низкая |

### Детальное описание блокеров

#### 1. Отсутствие phone hash/email hash (~60%)

**Проблема:** 
Phone hash/email hash присутствуют в сделках, но отсутствуют в событиях. Это препятствует корректной склейке между событиями и сделками в CRM-системе.

**Решение:**
- Убедиться, что во всех формах захвата лидов на сайте происходит обогащение события хешами
- Дополнительно создавать события с обогащением данными из форм
- Настроить обратную передачу хешей из CRM в Rick.ai

#### 2. Проблемы с коллтрекингом (~50%)

**Проблема:**
Не видны события из систем коллтрекинга. Интеграция ограничена определенными системами (calltouch и comagic), в то время как клиенты используют и другие системы (mango, Новофон, UIS).

**Решение:**
- Настройка вебхуков для получения данных из коллтрекинговых систем
- Разработка индивидуальных интеграций для популярных систем (mango, Новофон, UIS)
- Использование n8n workflow для обработки данных из разных источников
- Проверка настройки отправки событий из коллтрекинга в счетчики (GA/YM)

#### 3. Формы не являются стандартными формами (~15%)

**Проблема:**
На сайтах клиентов используются нестандартные формы, которые не определяются как формы Rick.js-сниппетом, что приводит к отсутствию событий при их заполнении.

**Решение:**
- Создание кастомных обработчиков событий для нестандартных форм
- Добавление атрибутов data-* для лучшего распознавания форм
- Разработка инструкций для клиентов по адаптации форм для работы с Rick.js

#### 4. Кастомные CRM (1С, Bitrix CMS) (~10%)

**Проблема:**
Интеграция с нестандартными CRM-системами затруднена из-за специфики их API и структуры данных.

**Решение:**
- Разработка индивидуальных коннекторов для популярных кастомных решений
- Создание промежуточного слоя для преобразования данных
- Обучение клиентов по добавлению необходимых полей в их CRM

#### 5. Формы Тильды (~10%)

**Проблема:**
Клиенты создают лендинги на Тильде и используют встроенные квизы, которые имеют свою специфику работы и не всегда корректно отслеживаются.

**Решение:**
- Специализированная интеграция с Тильдой
- Создание библиотеки готовых решений для популярных блоков Тильды
- Инструкции для клиентов по корректной настройке квизов

---

## 🏗️ Архитектурные компоненты Rick.ai

### 1. Сбор данных (Data Collection Layer)

```
Frontend                  Backend                        Storage
┌─────────────┐          ┌──────────────────┐          ┌─────────────┐
│ rick-js-    │  events  │ Event Processor  │  queue   │ Message     │
│ snippet     ├─────────►│                  ├─────────►│ Queue       │
└─────────────┘          └──────────────────┘          └──────┬──────┘
                                                              │
┌─────────────┐          ┌──────────────────┐                 │
│ CRM API     │  events  │ Data Ingestion   │                 │
│ Connectors  ├─────────►│ Services         │                 ▼
└─────────────┘          └──────────────────┘          ┌─────────────┐
                                                       │ Raw Data    │
                                                       │ Storage     │
                                                       └─────────────┘
```

**Ключевые компоненты:**
- Rick-js-snippet: JavaScript-библиотека для веб-сайтов
- Event Processor: обработчик событий в реальном времени
- API Connectors: интеграции с внешними системами
- Message Queue: система очередей для асинхронной обработки
- Raw Data Storage: хранилище необработанных данных

### 2. Обработка данных (Data Processing Layer)

```
                 ┌───────────────────┐
                 │   ETL Pipelines   │
                 └─────────┬─────────┘
                           │
                           ▼
┌─────────────┐   ┌───────────────────┐   ┌─────────────┐
│ Raw Data    │   │ Transformation    │   │ Data        │
│ Storage     ├──►│ Services          ├──►│ Warehouse   │
└─────────────┘   └───────────────────┘   └─────────────┘
                           │
                           ▼
                 ┌───────────────────┐
                 │ Data Quality      │
                 │ Monitoring        │
                 └───────────────────┘
```

**Ключевые компоненты:**
- ETL Pipelines: процессы извлечения, преобразования и загрузки данных
- Transformation Services: сервисы для преобразования данных
- Data Warehouse: хранилище структурированных данных
- Data Quality Monitoring: система мониторинга качества данных

### 3. Аналитика и алгоритмы (Analytics Layer)

```
┌─────────────┐   ┌───────────────────┐   ┌─────────────────┐
│ Data        │   │ Analytics Engine  │   │ Attribution     │
│ Warehouse   ├──►│                   ├──►│ Models          │
└─────────────┘   └───────────────────┘   └─────────────────┘
                           │
                           ▼
                 ┌───────────────────┐   ┌─────────────────┐
                 │ KJ Algorithm      │   │ User Segment    │
                 │                   ├──►│ Definitions     │
                 └───────────────────┘   └─────────────────┘
                           │
                           ▼
                 ┌───────────────────┐
                 │ Machine Learning  │
                 │ Models            │
                 └───────────────────┘
```

**Ключевые компоненты:**
- Analytics Engine: ядро аналитической системы
- KJ Algorithm: алгоритм связывания анонимных пользователей с контактами
- Attribution Models: модели атрибуции конверсий
- User Segment Definitions: система определения пользовательских сегментов
- Machine Learning Models: модели машинного обучения

### 4. Визуализация и API (Presentation Layer)

```
┌─────────────┐   ┌───────────────────┐   ┌─────────────────┐
│ Analytics   │   │ API Gateway       │   │ Client          │
│ Layer       ├──►│                   ├──►│ Applications    │
└─────────────┘   └───────────────────┘   └─────────────────┘
                           │
                           ▼
                 ┌───────────────────┐   ┌─────────────────┐
                 │ Report Generator  │   │ Notification    │
                 │                   ├──►│ Service         │
                 └───────────────────┘   └─────────────────┘
                           │
                           ▼
                 ┌───────────────────┐
                 │ Dashboard Engine  │
                 │                   │
                 └───────────────────┘
```

**Ключевые компоненты:**
- API Gateway: централизованный доступ к API
- Report Generator: генератор отчетов
- Dashboard Engine: движок для создания дашбордов
- Notification Service: система оповещений
- Client Applications: клиентские приложения и интерфейсы

---

## 🔧 Технический стек Rick.ai

### Frontend:
- JavaScript/TypeScript
- React для административных интерфейсов
- D3.js для визуализаций

### Backend:
- Node.js для API и обработки событий
- Python для аналитических сервисов и ML
- Kafka для очередей сообщений

### Хранилища данных:
- PostgreSQL для метаданных и конфигураций
- ClickHouse для аналитического хранилища
- Redis для кэширования

### Аналитика и ML:
- Pandas, NumPy для обработки данных
- Scikit-Learn, TensorFlow для ML-моделей
- MLflow для управления ML-экспериментами

### Инфраструктура:
- Docker для контейнеризации
- Kubernetes для оркестрации
- Terraform для IaC
- Prometheus + Grafana для мониторинга

---

## 🎯 Карта мотиваций клиентов Rick.ai

### Типичные ситуации и мотивации клиентов

#### Ситуация 1: Снижение конверсии в покупку
**Роль клиента:** CMO, Маркетолог
**Основные мотивации:**
- Стремится обезопасить свою позицию через обоснование решений
- Стремится выполнить финансовые KPI
**Потребности:**
- Определяет, где теряется конверсия в воронке
- Выявляет изменения, негативно повлиявшие на показатели
- Разрабатывает стратегии возврата конверсии к прежним значениям

#### Ситуация 2: Неуверенность в аналитических данных
**Роль клиента:** CMO, Маркетолог, не имеющий опыта настройки аналитики
**Типичные случаи:**
- Использует аналитику, доставшуюся "по наследству"
- Зависит от другого отдела, занимающегося аналитикой
- Недавно присоединился к компании
**Основные мотивации:**
- Стремится повысить безопасность и уверенность в работе
- Стремится принимать решения автономно
- Стремится действовать независимо от других отделов

#### Ситуация 3: Необходимость роста выручки без увеличения бюджета
**Роль клиента:** CMO, Маркетолог
**Основные мотивации:**
- Демонстрирует эффективность своей работы для признания
- Обосновывает необходимость увеличения бюджета для расширения влияния
- Доказывает ценность маркетинга для всей компании

#### Ситуация 4: Контроль работы агентства
**Роль клиента:** CMO, Руководитель отдела маркетинга
**Основные мотивации:**
- Защищается от возможного обмана со стороны агентства
- Оптимизирует ресурсы компании
- Стремится к независимости от внешних экспертов

#### Ситуация 5: Давление со стороны руководства
**Роль клиента:** CMO, Маркетолог
**Основные мотивации:**
- Защищается от критики руководства
- Доказывает свою профессиональную компетентность
- Получает необходимые ресурсы для эффективной работы

#### Ситуация 6: Новый руководитель (испытательный срок)
**Роль клиента:** Новый CMO или CPO
**Основные мотивации:**
- Проходит испытательный срок успешно
- Демонстрирует свою профессиональную компетентность
- Устанавливает авторитет в новой команде

#### Ситуация 7: Сложный и длительный процесс сбора аналитики
**Роль клиента:** CMO, Маркетолог, Руководитель отдела аналитики
**Основные мотивации:**
- Оптимизирует ресурсы времени и бюджета
- Работает независимо от технических специалистов
- Минимизирует ошибки в аналитических данных

### Общие ключевые мотивации клиентов Rick.ai

1. **Безопасность** - Защищается от критики руководства, опирается на достоверные данные
2. **Признание компетентности** - Демонстрирует профессиональные навыки и знания
3. **Автономность** - Работает независимо от других отделов
4. **Оптимизация ресурсов** - Сокращает излишние расходы бюджета
5. **Влияние** - Участвует в формировании стратегических решений компании

## 🔧 Технические компоненты и интеграции

### Система нормализации данных
**Email нормализация:**
```typescript
function normalizeEmail(email: string) {
  return email.trim().toLowerCase()
}
```

**Phone нормализация:**
```typescript
function normalizePhone(phone: string): string {
  if (!phone) return ""
  const match = phone.match(/[-+0-9][-+0-9() ]+[0-9)]/)
  if (!match) return ""
  const number = match[0].replace(/[^0-9]/g, "")
  // Логика нормализации российских номеров
  switch (true) {
    case number.length === 11 && number[0] === "8":
      return `7${number.slice(1)}`
    case number.length === 12 && number.slice(0, 2) === "78":
      return `7${number.slice(2)}`
    case number.length === 10:
      return `7${number}`
    default:
      return number
  }
}
```

**SHA-1 хеширование:**
```typescript
function sha1digest(value: string) {
  if (!value || !window.crypto?.subtle) return undefined
  return window.crypto.subtle
    .digest("SHA-1", new TextEncoder().encode(value))
    .then((hash) =>
      Array.from(new Uint8Array(hash))
        .map((b) => b.toString(16).padStart(2, "0"))
        .join(""),
    )
}
```

### Интеграции с внешними платформами

#### VK Ads API интеграция
**Запрашиваемые scope:**
- `ads` - Доступ к рекламным кампаниям VK Ads
- `groups` - Доступ к сообществам пользователя
- `offline` - Постоянный доступ к токенам
- `email` - Доступ к email пользователя

**Техническая реализация:**
```python
def get_vk_campaign_stats(campaign_id, date_from, date_to):
    # Получение данных через VK Ads API
    # Интеграция с Rick.ai аналитической системой
    return campaign_performance_data
```

#### Проблемы интеграции clientID
**Критические требования:**
- Одновременная передача clientID из GA4 и Яндекс.Метрики
- Использование поля utm_client_id для Яндекс.Метрики
- POST-запрос /update для исторических данных

**Решение:**
```python
# Модификация системы для одновременной передачи clientID
def send_transaction_data(transaction_data):
    # Добавление utm_client_id для Яндекс.Метрики
    transaction_data['utm_client_id'] = yandex_metrika_client_id
    # Отправка данных с обоими clientID
    return api_request(transaction_data)
```

## 📊 Процесс диагностики и troubleshooting

### Когда начинать диагностику

**Предварительные условия:**
1. **Команда забрифована** по правильному формированию отчетов для получения данных о конверсии
2. **Выбраны JTBD-сценарии** для анализа (например, проблемы на этапе оплаты)
3. **Подготовлены материалы** - скриншоты, метрики, комментарии по выбранным компаниям

**Структура виджетов для диагностики:**

#### JTBD-сценарий: Определение проблем на этапе оплаты
**Виджет**: Отказы на этапе оплаты
**Группировки**:
- По типу устройства (десктоп/мобильный)
- По типу платежного метода
- По наличию ошибок ввода данных
- По времени, проведенному на странице оплаты

**Метрики и критерии**:
- Этапы воронки: открытие страницы оплаты → выбор способа оплаты → ввод данных → подтверждение оплаты
- Отказы на каждом этапе (% и абсолютные значения)
- Время до отказа
- Количество попыток выбора разных способов оплаты
- События неудачных попыток оплаты с кодами ошибок

#### JTBD-сценарий: Анализ эффективности разных способов оплаты
**Виджет**: Конверсия по способам оплаты
**Группировки**:
- По типу платежного метода (карта, бонусы, Apple Pay/Google Pay, рассрочка)
- По сегментам пользователей (новые/вернувшиеся)
- По источнику трафика
- По размеру корзины

**Метрики и критерии**:
- Доля выбора каждого способа оплаты
- Успешность завершения оплаты для каждого способа
- Время, затраченное на оформление оплаты по каждому способу
- События смены способа оплаты в процессе оформления

---

## ✅ Output и доставка: когда просят обновить этот стандарт

- [ ] Явно определи имя human-author — это имя пользователя, который тебя попросил обновить стандарт
- [ ] Формат: `.md`, канал: Git / Docs
- [ ] Подтверждение: ожидается от [human-author]
- [ ] протокол дабл-чек, чтобы строка updated: под заголовком стандарта содержала [date time] и имя [human-author] пользователя
- [ ] убедись, что секции Output, лицензия и условия использования сохранены в обновленном стандарте
- [ ] дабл чек, что есть секция лицензия и условия использования и они не теряются в обновленном стандарте

---

## 📋 Связанные материалы

- [Registry Standard](abstract://standard:registry_standard) - Управление реестром стандартов
- [Task Master Standard](abstract://standard:task_master_standard) - Основной стандарт организации работы
- [Rick.ai Technical Documentation](../rick.ai/knowledge%20base/in%20progress/docs_specs/rick_ai_technical_documentation.md)
- [Rick.ai Architecture Specification](../rick.ai/knowledge%20base/in%20progress/docs_specs/rick_ai_architecture_specification.md)
- [Rick.ai Knowledge Base Standard](../rick.ai/[promts.Rick.ai]/rick_knowledge_base_standard.md)

---

**Лицензия**: © 2025 Ilya Krasinsky. Все права защищены.
Стандарт разработан для внутреннего использования в рамках проекта Rick.ai.
Использование, распространение и модификация возможны только с письменного разрешения правообладателя.
Мониторинг соблюдения лицензии осуществляется Magic Rick Inc в интересах правообладателя с применением всех доступных правовых средств защиты.
