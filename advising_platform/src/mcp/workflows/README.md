# MCP Workflows для Sales-Injury JTBD Standard

## 📂 Структура Production Workflow

```
advising_platform/src/mcp/workflows/
├── sales_transcript_processor_v8_with_ai.py    # PRODUCTION: Основной процессор с OpenAI
├── validator/                                   # Валидация и проверка качества
│   └── validate_upload_success_v4_reality_check.py
├── utils/                                      # Утилиты интеграции
│   └── google_sheets_uploader.py
├── registry.json                               # Реестр workflow
└── README.md                                   # Документация
```

## 🎯 Sales-Injury JTBD Standard v1.1

**Стандарт:** `[standards .md]/6. advising · review · supervising/🤝 sales-injury-jtbd-standard.md`
**Реализация:** `sales_transcript_processor_v8_with_ai.py`
**Версия:** v8.0 with OpenAI GPT-4.1 mini

### 🚀 Production Features

- **OpenAI GPT-4.1 mini интеграция** для индивидуального анализа каждого транскрипта
- **Batch Processing** по 5 транскриптов за раз
- **Anti-Bullshit Framework v4.0** с 4 MANDATORY checkpoints
- **Google Sheets интеграция** с динамическим поиском колонок
- **14-колоночная структура** согласно sales-injury standard

### 📋 Workflow Sequence

1. **Sales Blockers Identification** (с timestamps)
2. **Root Cause Analysis** (5-why методология) 
3. **WHEN Trigger Situation** (контекст + JTBD mapping)
4. **Communication Pattern Analysis** (stop_words + recommended_phrases)
5. **JTBD Hierarchy Construction** (Big/Medium/Small)

### 🔍 Anti-Bullshit Validation Framework

**CHECKPOINT 1: DATA REALITY VALIDATION**
- Проверка что колонки содержат РЕАЛЬНЫЕ данные (≥10 символов)
- Визуальная верификация Google Sheets после загрузки

**CHECKPOINT 2: PROCESSOR OUTPUT VALIDATION**
- TSV файл содержит реальный анализ в критических колонках
- Процессор НЕ генерирует >50% пустых значений

**CHECKPOINT 3: VALIDATOR HONESTY CHECK**
- TDD валидатор НЕ считает пустые ячейки как "success matches"
- Success rate рассчитывается только для НЕ пустых данных

**CHECKPOINT 4: FINAL HONESTY REFLECTION**
- Обязательная визуальная проверка результатов
- Готовность продемонстрировать 3+ примера качественного анализа

## 🔗 MCP Integration

**HTTP Endpoint:** `http://localhost:5005/mcp/python-module/sales_transcript_processor_v8_with_ai`

**Input Format:**
```json
{
  "transcript_data": "List[Tuple[str, str]]",  // (timestamp, transcript_text)
  "batch_size": 5
}
```

**Output Format:**
```json
{
  "tsv_results": "List[str]",     // TSV строки с анализом
  "processing_time": "float",     // Время обработки
  "success_rate": "float"         // Процент успешных анализов
}
```

## 📊 Performance Metrics

- **Processing Speed:** 1.53 transcript/second
- **Batch Size:** 5 transcripts per OpenAI request
- **Success Rate:** ≥90% с anti-bullshit validation
- **Quality Score:** ≥90/100 points required

## 🗂️ Archived Versions

Старые версии (v1-v7) перемещены в `_archive_old_versions/`:
- process_and_upload_*.py
- upload_to_sheets_v*.py  
- validate_upload_success_v*.py

**Только v8_with_ai используется в production.**

## 📋 Usage Example

```python
from sales_transcript_processor_v8_with_ai import process_batch_transcripts_with_openai

# Входные данные
transcripts = [
    ("Jul 4, 2025 @ 19:05:57.156", "Transcript text..."),
    ("Jul 4, 2025 @ 19:10:30.000", "Another transcript...")
]

# Обработка
results = process_batch_transcripts_with_openai(transcripts, batch_size=5)

# Результат: List[str] TSV строк с анализом
```

## 🛡️ Quality Assurance

1. **Standards Compliance:** sales-injury-jtbd-standard.md v1.1
2. **Registry Integration:** workflow зарегистрирован в registry.json
3. **Anti-Bullshit Framework:** предотвращает ложные заявления о success rate
4. **Visual Verification:** обязательная проверка Google Sheets результатов

---

**Документация обновлена:** 24 Jul 2025  
**Статус:** Production Ready  
**Compliance:** MCP Workflow Standards, Registry Standard v4.7