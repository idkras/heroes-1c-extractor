# Gap Analysis и Playwright MCP Integration

## 🎯 **ЦЕЛЬ:** Документация системы анализа gap между expected/actual outcome и интеграции с Playwright MCP

**JTBD:** Как разработчик, я хочу понимать как работает система валидации output и как она интегрируется с Playwright MCP для визуального тестирования.

## 📋 **АРХИТЕКТУРА СИСТЕМЫ**

### **Основные MCP команды для gap analysis:**

1. **`execute_output_gap_workflow`** - комплексный анализ gap
2. **`validate_actual_outcome`** - проверка фактического результата по URL
3. **`registry_gap_report`** - guidance система для анализа gap
4. **`validate_output_artefact`** - валидация output артефактов

### **Связь с Playwright MCP:**

Playwright MCP сервер помогает находить ошибки в HTML верстке через:

- **Визуальная валидация** - создание скриншотов для анализа
- **Анализ визуальных элементов** - проверка структуры страницы
- **Выявление критических дефектов** - overlapping elements, broken CSS
- **Проверка навигации** - функциональность ссылок
- **Анализ layout** - правильность отображения контента

## 🔧 **КАК РАБОТАЕТ execute_output_gap_workflow**

### **Workflow Stages:**

1. **Input Validation** - проверка входных данных
2. **Content Extraction** - извлечение контента из файлов/строк
3. **Gap Analysis** - анализ различий между expected и actual
4. **Quality Assessment** - оценка качества на основе gap score
5. **Screenshot Creation** - создание скриншотов (если URL предоставлен)
6. **Recommendations Generation** - генерация рекомендаций

### **Алгоритм gap analysis:**

```python
# Простой анализ на основе ключевых слов
expected_words = set(expected.lower().split())
actual_words = set(actual.lower().split())

missing_words = expected_words - actual_words
extra_words = actual_words - expected_words
common_words = expected_words & actual_words

gap_score = len(common_words) / len(expected_words)
```

### **Quality Assessment:**

- **≥90%** - Excellent (95 points)
- **≥80%** - Good (85 points)
- **≥70%** - Acceptable (75 points)
- **≥60%** - Needs Improvement (65 points)
- **<60%** - Poor (45 points)

## 🚀 **ИСПОЛЬЗОВАНИЕ**

### **Базовый анализ gap:**

```python
result = await execute_output_gap_workflow(
    expected="Ожидаемый результат с ключевыми словами: анализ, офер, сегмент",
    actual="Фактический результат с некоторыми ключевыми словами: анализ, сегмент",
    analysis_type="comprehensive"
)
```

### **Анализ с файлами:**

```python
result = await execute_output_gap_workflow(
    expected_file="expected_output.md",
    actual_file="actual_output.md",
    analysis_type="comprehensive"
)
```

### **Анализ с URL и скриншотом:**

```python
result = await execute_output_gap_workflow(
    expected="Ожидаемый контент",
    actual="Фактический контент",
    url="https://example.com",
    take_screenshot=True,
    analysis_type="comprehensive"
)
```

## 🔗 **ИНТЕГРАЦИЯ С PLAYWRIGHT MCP**

### **Текущее состояние:**

- ✅ **Параметр `take_screenshot`** добавлен в команды
- ✅ **Placeholder для скриншотов** создается
- ⚠️ **Полная интеграция** требует настройки Playwright MCP сервера

### **Как Playwright помогает находить ошибки в HTML:**

#### **1. Визуальные дефекты:**
```javascript
// Проверка overlapping elements
const overlapping = await page.evaluate(() => {
    const elements = document.querySelectorAll('*');
    const overlaps = [];
    for (let i = 0; i < elements.length; i++) {
        for (let j = i + 1; j < elements.length; j++) {
            const rect1 = elements[i].getBoundingClientRect();
            const rect2 = elements[j].getBoundingClientRect();
            if (rect1.left < rect2.right && rect1.right > rect2.left &&
                rect1.top < rect2.bottom && rect1.bottom > rect2.top) {
                overlaps.push({
                    element1: elements[i].tagName,
                    element2: elements[j].tagName
                });
            }
        }
    }
    return overlaps;
});
```

#### **2. Вертикальный текст (TOC проблемы):**
```javascript
// Проверка вертикального рендеринга текста
const vertical_text = await page.locator('text=/^[А-ЯЁ]$/').all();
if (vertical_text.length > 0) {
    defects.push({
        type: "critical",
        description: "Vertical text rendering detected - TOC broken",
        count: vertical_text.length,
        severity: "critical"
    });
}
```

#### **3. Broken CSS:**
```javascript
// Проверка сломанных CSS стилей
const broken_css = await page.evaluate(() => {
    const styles = document.querySelectorAll('link[rel="stylesheet"]');
    const broken = [];
    styles.forEach(style => {
        if (!style.sheet || style.sheet.cssRules.length === 0) {
            broken.push(style.href);
        }
    });
    return broken;
});
```

#### **4. Навигационные проблемы:**
```javascript
// Проверка навигации
const navigation_check = await page.evaluate(() => {
    const links = document.querySelectorAll('a[href]');
    const broken_links = [];
    links.forEach(link => {
        if (link.href.includes('javascript:') || link.href === '#') {
            broken_links.push(link.href);
        }
    });
    return broken_links;
});
```

## 📊 **СТРУКТУРА РЕЗУЛЬТАТА**

### **Успешный результат:**
```json
{
  "success": true,
  "analysis_id": "GAP_20250828_120243",
  "workflow_status": "completed",
  "overall_score": 75.0,
  "recommendations": [
    "Улучшить соответствие между ожидаемым и фактическим результатом",
    "Добавить недостающие ключевые элементы: офер"
  ],
  "execution_time": 0.001,
  "steps_completed": [
    "input_validation",
    "content_extraction", 
    "gap_analysis",
    "quality_assessment",
    "recommendations_generation"
  ],
  "steps_failed": [],
  "details": {
    "workflow_name": "output_gap_analysis",
    "version": "1.0.0",
    "standard_compliance": "MCP Workflow Standard v2.3",
    "gap_analysis": {
      "gap_score": 0.75,
      "missing_words": ["офер"],
      "similarity_percentage": 75.0
    },
    "quality_assessment": {
      "overall_score": 75.0,
      "quality_level": "acceptable"
    }
  }
}
```

### **Результат с ошибкой:**
```json
{
  "success": false,
  "analysis_id": "GAP_20250828_120243",
  "workflow_status": "failed",
  "overall_score": 0.0,
  "recommendations": ["Invalid input data"],
  "execution_time": 0.001,
  "steps_completed": [],
  "steps_failed": ["input_validation"],
  "details": {
    "error": "Invalid input data"
  }
}
```

## 🔍 **ТЕСТИРОВАНИЕ**

### **Запуск тестов:**
```bash
cd heroes-platform/mcp_server
python test_analyze_output_gap.py
```

### **Результаты тестирования:**
- ✅ **Базовый gap analysis** - работает корректно
- ✅ **Анализ файлов** - работает с файлами
- ✅ **Валидация todo** - обрабатывает ошибки
- ✅ **Анализ URL** - обрабатывает ошибки
- ✅ **Пустые данные** - корректная обработка

## 🚧 **ПЛАН РАЗВИТИЯ**

### **Краткосрочные задачи:**
1. **Полная интеграция с Playwright MCP** - замена placeholder на реальные скриншоты
2. **Улучшение алгоритма gap analysis** - более сложный анализ семантики
3. **Добавление визуального анализа** - анализ скриншотов на дефекты

### **Долгосрочные задачи:**
1. **Machine Learning анализ** - использование ML для оценки качества
2. **Автоматическое исправление** - предложения по исправлению дефектов
3. **Интеграция с CI/CD** - автоматическая валидация в pipeline

## 📚 **ССЫЛКИ**

- [Playwright MCP Documentation](https://github.com/playwright-community/playwright-mcp)
- [MCP Workflow Standard v2.3](../standards/mcp_workflow_standard.md)
- [Validate Actual Outcome Integration](../VALIDATE_ACTUAL_OUTCOME_INTEGRATION.md)
- [Gap Theory Standard](../../[standards%20.md]/1.%20process%20·%20goalmap%20·%20task%20·%20incidents%20·%20tickets%20·%20qa/1.5%20gap%20theory%20standard%2026%20august%202025%202325%20CET%20by%20ilya%20krasinsky.md)
