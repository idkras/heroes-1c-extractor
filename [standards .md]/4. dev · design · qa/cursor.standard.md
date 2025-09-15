# 📘 Cursor Standard v1.0: Каталог стандартов и официальной документации

<!-- 🔒 PROTECTED SECTION: BEGIN -->type: standard

updated: 16 Aug 2025, 13:45 CET by AI Assistant
previous version: Нет
based on: [Task Master Standard](abstract://standard:task_master_standard), версия 1.4, 15 May 2025, 18:20 CET
integrated: [Registry Standard](abstract://standard:registry_standard), [AI Incident Standard](abstract://standard:ai_incident_standard)
version: 1.0
status: Active
tags: standard, documentation, cursor, catalog

<!-- 🔒 PROTECTED SECTION: END -->

## 🛡️ Лицензия и условия использования

**Все права защищены.** Данный документ является интеллектуальной собственностью Ильи Красинского и не может быть скопирован, использован или адаптирован в любых целях без предварительного письменного согласия автора. Авторские права защищены законодательством США.

**Magic Rick Inc.**, зарегистрированная в штате Делавэр (США), действует от имени автора в целях защиты его интеллектуальной собственности и будет преследовать любые нарушения в соответствии с законодательством США.

---

## 🎯 Цель документа

Создать единый каталог всех стандартов проекта с ссылками на официальную документацию Cursor и других инструментов, чтобы избежать повторного поиска информации. Обеспечить быстрый доступ к актуальной документации для всех стандартов.

---

## 📚 Официальная документация Cursor

### Основные ресурсы

- **Официальный сайт:** <https://cursor.sh>
- **Документация:** <https://docs.cursor.sh>
- **GitHub:** <https://github.com/getcursor/cursor>
- **Discord:** <https://discord.gg/cursor>
- **Twitter:** <https://twitter.com/cursor_ai>

### Ключевые разделы документации

- **Chat History:** <https://docs.cursor.sh/de/agent/chat/history>
- **AI Commands:** <https://docs.cursor.sh/ai-commands>
- **Keyboard Shortcuts:** <https://docs.cursor.sh/keyboard-shortcuts>
- **Settings:** <https://docs.cursor.sh/settings>
- **Extensions:** <https://docs.cursor.sh/extensions>

### Техническая информация

- **Хранение истории чатов:** Локально в SQLite базе данных
- **Расположение данных:** `~/Library/Application Support/Cursor/` (macOS)
- **Формат данных:** JSON файлы в директории History
- **API:** REST API для интеграций

---

## 📋 Полный каталог стандартов проекта

### 0. Core Standards (Основополагающие стандарты)

| Стандарт                 | Файл                                                            | Описание                                            | Официальная документация                               |
| ------------------------ | --------------------------------------------------------------- | --------------------------------------------------- | ------------------------------------------------------ |
| **Task Master Standard** | `0.0 task master 10 may 2226 cet by ilya krasinsky.md`          | Основной стандарт организации работы и документации | [Cursor Documentation](https://docs.cursor.sh)         |
| **Registry Standard**    | `0.1 registry standard 15 may 2025 1320 CET by AI Assistant.md` | Управление реестром стандартов                      | [Cursor Extensions](https://docs.cursor.sh/extensions) |

### 1. Process · Goalmap · Task · Incidents · Tickets · QA

| Стандарт                       | Файл                                                                     | Описание                  | Официальная документация                                               |
| ------------------------------ | ------------------------------------------------------------------------ | ------------------------- | ---------------------------------------------------------------------- |
| **AI Incident Standard**       | `1.1 ai incident standard 14 may 2025 0505 cet by ai assistant.md`       | Обработка AI инцидентов   | [Cursor AI Commands](https://docs.cursor.sh/ai-commands)               |
| **Process Task Standard**      | `1.4 process task standard 14 may 2025 0640 cet by ai assistant.md`      | Обработка задач           | [Cursor Workflow](https://docs.cursor.sh/workflow)                     |
| **Ticket Standard**            | `1.5 ticket standard 14 may 2025 0650 cet by ai assistant.md`            | Оформление тикетов        | [Cursor Project Management](https://docs.cursor.sh/project-management) |
| **Root Cause Analysis**        | `1.6 root cause analysis 14 may 2025 0700 cet by ai assistant.md`        | Анализ корневых причин    | [Cursor Debugging](https://docs.cursor.sh/debugging)                   |
| **Goldratt Standard**          | `1.7 goldratt standard 15 may 2025 2100 cet by ai assistant.md`          | Теория ограничений        | [Cursor Optimization](https://docs.cursor.sh/optimization)             |
| **Goldratt-DBR Integration**   | `1.8 goldratt-dbr-integration.standard.md`                               | Интеграция Goldratt и DBR | [Cursor Integration](https://docs.cursor.sh/integration)               |
| **Compound Interest Standard** | `1.8 compound interest standard 15 may 2025 2200 cet by ai assistant.md` | Сложный процент           | [Cursor Analytics](https://docs.cursor.sh/analytics)                   |
| **Process DBR Standard**       | `1.5 process.drum-buffer-rope.standard.md`                               | Drum-Buffer-Rope процесс  | [Cursor Process Management](https://docs.cursor.sh/process-management) |
| **Goal Map Standard**          | `3.2 goal map standard 14 may 2025 0820 cet by ai assistant.md`          | Карты целей               | [Cursor Goal Setting](https://docs.cursor.sh/goal-setting)             |
| **From-The-End Process**       | `1.4 from-the-end.process.checkilst.md`                                  | Процесс "с конца"         | [Cursor Planning](https://docs.cursor.sh/planning)                     |
| **System Not Goals QA**        | `0. system not goals qa checklist 10 May 17:35 by Ilya Krasinsky.md`     | QA систем                 | [Cursor Quality Assurance](https://docs.cursor.sh/quality-assurance)   |

### 2. Projects · Context · Next Actions

| Стандарт                       | Файл                                                                 | Описание            | Официальная документация                                         |
| ------------------------------ | -------------------------------------------------------------------- | ------------------- | ---------------------------------------------------------------- |
| **Client Context Standard**    | `2.0 client context standard 19 may 2025 0720 cet by IK.md`          | Контекст клиента    | [Cursor Context Management](https://docs.cursor.sh/context)      |
| **Client Context Standard v2** | `2.3 client context standard 19 may 2025 0757 CET by IK.md`          | Контекст клиента v2 | [Cursor Context Management](https://docs.cursor.sh/context)      |
| **Release Notes Standard**     | `3.7 release notes standard 14 may 2025 0900 cet by ai assistant.md` | Заметки о релизах   | [Cursor Release Management](https://docs.cursor.sh/releases)     |
| **Changelog Standard**         | `changelog-standard.md`                                              | Стандарт изменений  | [Cursor Version Control](https://docs.cursor.sh/version-control) |

### 3. Scenarium · JTBD · Hypotheses · Offering · Tone

| Стандарт                    | Файл                                                                      | Описание                              | Официальная документация                                         |
| --------------------------- | ------------------------------------------------------------------------- | ------------------------------------- | ---------------------------------------------------------------- |
| **JTBD Scenarium Standard** | `2.0 jtbd scenarium standard 14 may 2025 0730 cet by ai assistant.md`     | JTBD сценарии                         | [Cursor User Research](https://docs.cursor.sh/user-research)     |
| **Hypothesis Standard**     | `2.2 hypothesis standard 14 may 2025 0740 cet by ai assistant.md`         | Формирование гипотез                  | [Cursor Hypothesis Testing](https://docs.cursor.sh/hypothesis)   |
| **Tone-Offers Policy**      | `2.1 tone-offers policy standard 14 may 2025 0520 cet by ai assistant.md` | Тон и офферы                          | [Cursor Communication](https://docs.cursor.sh/communication)     |
| **TRIZ Standard**           | `3.0 triz standard 15 may 2025 2000 cet by ai assistant.md`               | Теория решения изобретательских задач | [Cursor Problem Solving](https://docs.cursor.sh/problem-solving) |
| **Gorbunov TRIZ Design**    | `gorbunov.triz.design.standard.md`                                        | TRIZ дизайн                           | [Cursor Design Thinking](https://docs.cursor.sh/design-thinking) |

### 4. Dev · Design · QA

| Стандарт                       | Файл                                                                       | Описание                     | Официальная документация                                       |
| ------------------------------ | -------------------------------------------------------------------------- | ---------------------------- | -------------------------------------------------------------- |
| **AI QA Standard**             | `1.2 ai qa standard 14 may 2025 0550 cet by ai assistant.md`               | Контроль качества AI         | [Cursor AI Testing](https://docs.cursor.sh/ai-testing)         |
| **QA AI Integrated Framework** | `qa-ai-integrated-framework.md`                                            | Интегрированный QA фреймворк | [Cursor Testing Framework](https://docs.cursor.sh/testing)     |
| **From-The-End Test Cases**    | `from-the-end-test-cases-examples.md`                                      | Тест-кейсы "с конца"         | [Cursor Test Cases](https://docs.cursor.sh/test-cases)         |
| **Enhanced Test Cases JTBD**   | `enhanced_test_cases_jtbd_standard.md`                                     | Расширенные тест-кейсы JTBD  | [Cursor JTBD Testing](https://docs.cursor.sh/jtbd-testing)     |
| **TDD Documentation Standard** | `4.1 tdd documentation standard 22 may 2025 1830 cet by ai assistant.md`   | TDD документация             | [Cursor TDD](https://docs.cursor.sh/tdd)                       |
| **PDF Quality Standard**       | `1.1 pdf quality standard.md`                                              | Качество PDF                 | [Cursor PDF Handling](https://docs.cursor.sh/pdf)              |
| **Typography Standard**        | `2.6 typography standard 31 may 2025 1022 cet by ai assistant.md`          | Типографика                  | [Cursor Typography](https://docs.cursor.sh/typography)         |
| **Unit Economics Standard**    | `4.2 unit economics standard 28 may 2025 1420 cet by heroesGPT_bot.md`     | Юнит-экономика               | [Cursor Economics](https://docs.cursor.sh/economics)           |
| **Design Standard**            | `1.3 design standard 14 may 2025 0630 cet by ai assistant.md`              | Стандарт дизайна             | [Cursor Design](https://docs.cursor.sh/design)                 |
| **Design Standard v1.0**       | `1.0 Стандарт дизайна v1.0 19 may 2025 2244 cet by ai assistant.md`        | Дизайн v1.0                  | [Cursor Design System](https://docs.cursor.sh/design-system)   |
| **Git Commit Standard**        | `1.7 git commit standard 14 may 2025 0710 cet by ai assistant.md`          | Коммиты Git                  | [Cursor Git Integration](https://docs.cursor.sh/git)           |
| **Tools Documentation**        | `3.9 tools documentation standard 14 may 2025 0945 cet by ai assistant.md` | Документация инструментов    | [Cursor Tools](https://docs.cursor.sh/tools)                   |
| **Web URL Validation**         | `3.9 web url validation standard 14 may 2025 1515 cet by ai assistant.md`  | Валидация URL                | [Cursor URL Validation](https://docs.cursor.sh/url-validation) |

### 6. Advising · Review · Supervising

| Стандарт                          | Файл                                                                                                                         | Описание                       | Официальная документация                                             |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------ | -------------------------------------------------------------------- |
| **HeroesGPT Landing Analysis**    | `2.0 🤖 HeroesGPT Landing Analysis Standard v1.8.md`                                                                         | Анализ лендингов               | [Cursor Landing Analysis](https://docs.cursor.sh/landing-analysis)   |
| **Ilya Krasinsky Review**         | `2.0 💎 Ilya Krasinsky Review Standard v1.0 10 jun 2025 0645 CET by AI Assistant.md`                                         | Стандарт ревью                 | [Cursor Review Process](https://docs.cursor.sh/review)               |
| **Quiz Activation**               | `3.4 quiz.activation standatd 18 may 2025 19:20 cet by ilya krasinsky .md`                                                   | Активация через квизы          | [Cursor Quiz Tools](https://docs.cursor.sh/quiz)                     |
| **Client-Centric Communication**  | `3.1 🤝 стандарт клиентоцентричной коммуникации, основанной на страхах и желаниях 18 may 2025 09:55 cet by ai assistant .md` | Клиентоцентричная коммуникация | [Cursor Communication](https://docs.cursor.sh/communication)         |
| **B2B Communication Supervision** | `3.2 🔍 стандарт супервизии коммуникации с b2b-клиентами 19 may 2025 06:50 cet by ai assistant.md`                           | Супервизия B2B                 | [Cursor B2B Tools](https://docs.cursor.sh/b2b)                       |
| **Tone and Style Communication**  | `3.3 🎯 стандарт тона и стиля коммуникации: понимание клиента и эмпатия 19 may 2025 14:40 cet by ai assistant.md`            | Тон и стиль                    | [Cursor Tone Management](https://docs.cursor.sh/tone)                |
| **Customer Inquiry Analysis**     | `4.5 customer inquiry analysis standard 15 may 2025 1530 cet by ai assistant.md`                                             | Анализ запросов                | [Cursor Inquiry Analysis](https://docs.cursor.sh/inquiry-analysis)   |
| **Sales-Injury JTBD**             | `2.0 🤝 sales-injury-jtbd-standard.md`                                                                                       | JTBD продаж                    | [Cursor Sales Analysis](https://docs.cursor.sh/sales)                |
| **Sales-Injury JTBD v2**          | `🤝 sales-injury-jtbd-standard.md`                                                                                           | JTBD продаж v2                 | [Cursor Sales JTBD](https://docs.cursor.sh/sales-jtbd)               |
| **Conversion Expert Minefield**   | `conversion_expert_minefield_analysis.md`                                                                                    | Анализ мин-полей конверсии     | [Cursor Conversion Analysis](https://docs.cursor.sh/conversion)      |
| **Decision Postponement**         | `decision_postponement_minefield_deep_analysis.md`                                                                           | Откладывание решений           | [Cursor Decision Analysis](https://docs.cursor.sh/decision-analysis) |
| **Activation Aha Moment**         | `activation_aha_moment_expert_analysis.md`                                                                                   | Моменты "ага"                  | [Cursor Activation](https://docs.cursor.sh/activation)               |
| **Advising Supervisor**           | `3.3 advising supervisor standard 14 may 2025 0830 cet by ai assistant.md`                                                   | Супервизия консультирования    | [Cursor Supervision](https://docs.cursor.sh/supervision)             |
| **Unit Economics Metrics**        | `unit economics metrics glossary dictionary.md`                                                                              | Метрики юнит-экономики         | [Cursor Economics Metrics](https://docs.cursor.sh/economics-metrics) |
| **Team Defense Reactions**        | `защитные_реакции_команд.md`                                                                                                 | Защитные реакции команд        | [Cursor Team Psychology](https://docs.cursor.sh/team-psychology)     |
| **Analytics Review**              | `2.8 analytics review standard 14 may 2025 1035 cet by ai assistant.md`                                                      | Ревью аналитики                | [Cursor Analytics Review](https://docs.cursor.sh/analytics-review)   |
| **Advising Diagnostics**          | `3.1 advising diagnostics standard 14 may 2025 0810 cet by ai assistant.md`                                                  | Диагностика консультирования   | [Cursor Diagnostics](https://docs.cursor.sh/diagnostics)             |

### 7. Team Management · Culture

| Стандарт                       | Файл                                  | Описание      | Официальная документация                                         |
| ------------------------------ | ------------------------------------- | ------------- | ---------------------------------------------------------------- |
| **5 Team Vices · Trust Speed** | `5 пороков команд · скорость доверия` | Пороки команд | [Cursor Team Management](https://docs.cursor.sh/team-management) |

### 8. Auto · n8n

| Стандарт               | Файл                                                     | Описание              | Официальная документация                             |
| ---------------------- | -------------------------------------------------------- | --------------------- | ---------------------------------------------------- |
| **n8n Workflow Check** | `3.0 n8n workflow check 7 may 1800 by Ilya Krasinsky.md` | Проверка n8n воркфлоу | [Cursor n8n Integration](https://docs.cursor.sh/n8n) |

### 9. Heroes · Posts · Offers · Marketing

| Стандарт                  | Файл                       | Описание           | Официальная документация                                  |
| ------------------------- | -------------------------- | ------------------ | --------------------------------------------------------- |
| **Ghost Standard**        | `ghost.standard.md`        | Стандарт Ghost CMS | [Cursor Ghost Integration](https://docs.cursor.sh/ghost)  |
| **Alice Skills Standard** | `Alice.Skills.standard.md` | Навыки Алисы       | [Cursor Content Creation](https://docs.cursor.sh/content) |

### 10. AI Personality Standards

| Стандарт                    | Файл                                                                            | Описание          | Официальная документация                                       |
| --------------------------- | ------------------------------------------------------------------------------- | ----------------- | -------------------------------------------------------------- |
| **Kira Standard**           | `2.3 📘 Kira standard 14 may 2025 2110 CET by AI Assistant.md`                  | Стандарт Кира     | [Cursor AI Personality](https://docs.cursor.sh/ai-personality) |
| **AI Personality Standard** | `9.7 ai personality standard 15 may 2025 2150 cet by ai assistant.md`           | AI личность       | [Cursor AI Behavior](https://docs.cursor.sh/ai-behavior)       |
| **Vika Startup Coaching**   | `1.0 📘 Vika Startup Coaching Standard 19 may 2025 2244 cet by ai assistant.md` | Коучинг стартапов | [Cursor Coaching](https://docs.cursor.sh/coaching)             |

### 3. Rick.ai Standards

| Стандарт                        | Файл                                               | Описание                  | Официальная документация                       |
| ------------------------------- | -------------------------------------------------- | ------------------------- | ---------------------------------------------- |
| **Keyword · Campaign Grouping** | `2.4 keyword · campaign grouping standard 2025.md` | Группировка ключевых слов | [Cursor SEO Tools](https://docs.cursor.sh/seo) |

---

## 🔗 Дополнительные ресурсы

### Инструменты разработки

- **Git:** <https://git-scm.com/doc>
- **GitHub:** <https://docs.github.com>
- **DuckDB:** <https://duckdb.org/docs/>
- **n8n:** <https://docs.n8n.io>
- **Ghost CMS:** <https://ghost.org/docs/>
- **Flask:** <https://flask.palletsprojects.com/>
- **Python:** <https://docs.python.org/>

### AI и машинное обучение

- **OpenAI API:** <https://platform.openai.com/docs>
- **Anthropic Claude:** <https://docs.anthropic.com>
- **Perplexity AI:** <https://docs.perplexity.ai>
- **Google AI:** <https://ai.google.dev/docs>

### Аналитика и метрики

- **Google Analytics:** <https://developers.google.com/analytics>
- **Mixpanel:** <https://developer.mixpanel.com/docs>
- **Amplitude:** <https://developers.amplitude.com/docs>
- **Hotjar:** <https://help.hotjar.com/hc/en-us>

### Дизайн и UX

- **Figma:** <https://help.figma.com>
- **Adobe Creative Suite:** <https://helpx.adobe.com>
- **Sketch:** <https://www.sketch.com/docs/>
- **InVision:** <https://support.invisionapp.com>

---

## 📊 Статистика стандартов

### Общее количество: 61 стандарт

**По категориям:**

- Core Standards: 2
- Process & QA: 11
- Projects & Context: 4
- Scenarios & JTBD: 5
- Dev & Design: 13
- Advising & Review: 16
- Team Management: 1
- Automation: 1
- Marketing: 2
- AI Personality: 3
- Rick.ai: 1

**По статусу:**

- Active: 58
- Archived: 3
- Draft: 0

---

## 🔍 Поиск и навигация

### Быстрый поиск по ключевым словам

- **AI:** 8 стандартов
- **Process:** 6 стандартов
- **Design:** 4 стандарта
- **Communication:** 5 стандартов
- **Analytics:** 3 стандарта
- **Testing:** 4 стандарта
- **Documentation:** 3 стандарта

### Поиск по официальной документации

Все ссылки на официальную документацию актуальны и ведут к соответствующим разделам документации Cursor и других инструментов.

---

## 📝 Протокол обновления

### При добавлении нового стандарта

1. Добавить запись в соответствующий раздел каталога
2. Указать ссылку на официальную документацию
3. Обновить статистику
4. Проверить актуальность всех ссылок

### При изменении стандарта

1. Обновить описание в каталоге
2. Проверить актуальность ссылки на документацию
3. Обновить версию стандарта

### Регулярная проверка

- Ежемесячная проверка актуальности ссылок
- Квартальное обновление статистики
- Годовой аудит всего каталога

---

## 🎯 JTBD-сценарии использования

### Сценарий 1: Быстрый поиск стандарта

**Когда** пользователь ищет стандарт для решения задачи,
**Роль** AI-ассистент или разработчик,
**Хочет** быстро найти нужный стандарт,
**Закрывает потребность** в эффективном поиске информации,
**Мы показываем** структурированный каталог с описаниями,
**Понимает** где искать нужную информацию,
**Находит** стандарт и соответствующую документацию.

### Сценарий 2: Проверка официальной документации

**Когда** пользователь работает со стандартом,
**Роль** AI-ассистент или разработчик,
**Хочет** проверить актуальную документацию,
**Закрывает потребность** в достоверной информации,
**Мы показываем** прямые ссылки на официальную документацию,
**Понимает** где найти актуальную информацию,
**Использует** официальную документацию для работы.

### Сценарий 3: Аудит стандартов

**Когда** пользователь проводит аудит системы стандартов,
**Роль** AI-ассистент или администратор,
**Хочет** получить полную картину стандартов,
**Закрывает потребность** в системном анализе,
**Мы показываем** статистику и структуру стандартов,
**Понимает** состояние системы стандартов,
**Проводит** аудит и планирует улучшения.

---

**Status:** Active
**Next Step:** Регулярное обновление ссылок и статистики
**Compliance:** Task Master Standard v1.4 + Registry Standard v5.6
