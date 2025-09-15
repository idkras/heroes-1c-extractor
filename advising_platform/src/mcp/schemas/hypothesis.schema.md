# Hypothesis Schema

## Структура гипотезы

```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "output": "string - ожидаемый результат",
  "outcome": "string - измеримый исход",
  "falsifiable_if": "string - условия фальсификации",
  "metrics": ["array of strings - метрики для измерения"],
  "created_at": "ISO datetime",
  "status": "draft|testing|confirmed|falsified",
  "confidence_level": "number 0-1",
  "evidence": {
    "supporting": ["array of evidence"],
    "contradicting": ["array of evidence"]
  },
  "next_steps": ["array of actions"],
  "jtbd": {
    "user": "string",
    "situation": "string", 
    "motivation": "string",
    "outcome": "string"
  },
  "reflection": {
    "atomic_design": "boolean",
    "testable": "boolean",
    "measurable": "boolean",
    "actionable": "boolean"
  },
  "tdd_cycle": {
    "red_phase": "string - failing test description",
    "green_phase": "string - implementation approach",
    "refactor_phase": "string - optimization strategy"
  }
}
```

## Примеры использования

### Гипотеза для анализа лендингов
```json
{
  "id": "H20250527_070131874",
  "title": "Автоматизация анализа лендингов с атомарными функциями",
  "description": "Анализ лендингов может быть автоматизирован с помощью атомарных функций для извлечения данных",
  "output": "Система автоматического анализа лендингов с качеством 95%",
  "outcome": "Время анализа сократится с 2 часов до 5 минут",
  "falsifiable_if": "Качество анализа < 85% или время > 10 минут",
  "metrics": ["quality_score", "processing_time", "accuracy_rate"],
  "status": "testing",
  "confidence_level": 0.85,
  "jtbd": {
    "user": "Business analyst",
    "situation": "Analyzing competitor landing pages",
    "motivation": "Need fast, accurate insights",
    "outcome": "Actionable improvement recommendations"
  },
  "reflection": {
    "atomic_design": true,
    "testable": true,
    "measurable": true,
    "actionable": true
  }
}
```

### Валидация схемы

Обязательные поля:
- `id`, `title`, `description`
- `output`, `outcome`
- `falsifiable_if`
- `jtbd` (все подполя)
- `reflection` (все подполя)

Опциональные поля:
- `metrics`, `evidence`, `next_steps`
- `tdd_cycle`, `confidence_level`

## Интеграция с MCP

Схема используется в:
- `form_hypothesis.py` - создание гипотез
- `falsify_or_confirm.py` - валидация результатов
- `build_jtbd.py` - JTBD анализ
- `workflow_with_reflection.py` - рефлексивные циклы