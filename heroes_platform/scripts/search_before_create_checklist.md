# 🔍 Чеклист "Поиск перед созданием"

## Обязательные шаги перед созданием нового файла

### 1. Семантический поиск (ПРИОРИТЕТ #1)

**Уверенность:** 0.9 - семантический поиск по функциональности

```python
# ✅ ПРАВИЛЬНО: Семантический поиск по смыслу
codebase_search({
    query: "How does user authentication work?",
    target_directories: ["backend/auth/"],
    explanation: "Find authentication implementation",
});

# ❌ НЕПРАВИЛЬНО: Точный поиск по названию
grep_search({
    query: "AuthService",
    explanation: "Find AuthService class",
});
```

**Когда использовать:**
- Поиск по функциональности и смыслу
- Исследование незнакомой кодовой базы
- Поиск паттернов и архитектурных решений
- Вопросы "как работает X?" или "где обрабатывается Y?"

**Стратегия запросов:**
- Начинать с широких запросов: `"How does authentication work?"`
- Уточнять по результатам: `"Where are user roles checked?"`
- Использовать контекстные директории для фокусировки

### 2. File Search (ПРИОРИТЕТ #2)

**Уверенность:** 0.8 - поиск по части имени файла

```python
# ✅ ПРАВИЛЬНО: Поиск по части имени файла
file_search({
    query: "auth",
    explanation: "Find authentication related files",
});

# ❌ НЕПРАВИЛЬНО: Точное имя файла
file_search({
    query: "UserAuthenticationService.ts",
    explanation: "Find specific file",
});
```

**Когда использовать:**
- Знаете часть имени файла
- Поиск файлов определенного типа
- Быстрый поиск по структуре проекта

### 3. Grep Search (ПРИОРИТЕТ #3)

**Уверенность:** 0.7 - точный поиск по коду

```python
# ✅ ПРАВИЛЬНО: Точный поиск по коду
grep_search({
    query: "class\\s+AuthService",
    include_pattern: "*.ts",
    explanation: "Find AuthService class definition",
});

# ❌ НЕПРАВИЛЬНО: Семантический поиск через grep
grep_search({
    query: "authentication",
    explanation: "Find authentication code",
});
```

**Когда использовать:**
- Точный поиск по коду
- Поиск конкретных функций/классов
- Регулярные выражения для сложных паттернов

## Confidence Levels для создания файлов

### Уровни уверенности:

```python
enum CreationConfidence {
    VERY_LOW = 0.2, // НЕ СОЗДАВАТЬ - продолжить поиск
    LOW = 0.4,      // НЕ СОЗДАВАТЬ - расширить поиск
    MEDIUM = 0.6,   // МОЖНО СОЗДАТЬ - но проверить еще раз
    HIGH = 0.8,     // СОЗДАТЬ - с высокой уверенностью
    VERY_HIGH = 1.0 // СОЗДАТЬ - абсолютная уверенность
}
```

### Критерии для каждого уровня:

**VERY_LOW (0.2) - НЕ СОЗДАВАТЬ:**
- Найдено много похожих файлов
- Функциональность уже существует
- Требуется дополнительный поиск

**LOW (0.4) - НЕ СОЗДАВАТЬ:**
- Найдены частично похожие файлы
- Возможно переиспользование с модификацией
- Нужно расширить поиск

**MEDIUM (0.6) - МОЖНО СОЗДАТЬ:**
- Найдено мало похожих файлов
- Функциональность частично отличается
- Требуется проверка перед созданием

**HIGH (0.8) - СОЗДАТЬ:**
- Найдено очень мало похожих файлов
- Функциональность значительно отличается
- Высокая уверенность в необходимости создания

**VERY_HIGH (1.0) - СОЗДАТЬ:**
- Не найдено похожих файлов
- Уникальная функциональность
- Абсолютная уверенность в необходимости создания

## Чеклист перед созданием файла

### Обязательные проверки:

- [ ] **Выполнить семантический поиск** по функциональности
- [ ] **Проверить существующие файлы** через file_search
- [ ] **Поискать похожий код** через grep_search
- [ ] **Оценить уверенность** в необходимости создания (≥0.6)
- [ ] **Проверить DocumentRegistry** на дубликаты (для .md файлов)

### Качественная проверка:

- [ ] **Использовать правильный инструмент** для задачи
- [ ] **Начинать с широких запросов**
- [ ] **Уточнять поиск** по результатам
- [ ] **Проверять релевантность** найденных файлов
- [ ] **Документировать результаты** поиска

### Решение о создании файла:

- [ ] **Оценить пригодность** найденного файла
- [ ] **Проверить возможность** модификации
- [ ] **Рассмотреть создание** только при уверенности ≥0.6
- [ ] **Обновить DocumentRegistry** при создании нового файла

## Примеры использования

### Пример 1: Создание authentication service

```python
// 1. Семантический поиск
codebase_search({
    query: "user authentication login password",
    explanation: "Find existing authentication implementations"
});

// 2. File search
file_search({
    query: "auth",
    explanation: "Find authentication related files"
});

// 3. Grep search
grep_search({
    query: "class.*Auth",
    explanation: "Find authentication classes"
});

// 4. Оценка результатов
// Если найдено много auth файлов → confidence = 0.2 (НЕ СОЗДАВАТЬ)
// Если найдено мало auth файлов → confidence = 0.8 (СОЗДАТЬ)
```

### Пример 2: Создание utility function

```python
// 1. Семантический поиск
codebase_search({
    query: "string formatting utility helper",
    explanation: "Find existing utility functions"
});

// 2. File search
file_search({
    query: "util",
    explanation: "Find utility files"
});

// 3. Grep search
grep_search({
    query: "def.*format",
    explanation: "Find formatting functions"
});

// 4. Оценка результатов
// Если найдено много util файлов → confidence = 0.3 (НЕ СОЗДАВАТЬ)
// Если найдено мало util файлов → confidence = 0.7 (МОЖНО СОЗДАТЬ)
```

## Метрики эффективности

### Целевые показатели:

- **Reuse Rate**: ≥80% переиспользование существующих файлов
- **Search Efficiency**: ≤3 поиска для нахождения нужного файла
- **Creation Confidence**: ≥0.6 уверенность перед созданием нового файла
- **Search Time**: ≤30 секунд на поиск файла
- **Duplicate Prevention**: 100% предотвращение создания дубликатов

### Мониторинг:

- Отслеживать количество созданных файлов
- Измерять время поиска
- Анализировать confidence levels
- Проверять качество поиска

## Интеграция с MCP сервером

### Автоматическая проверка через MCP команды:

```python
# 1. Поиск существующих файлов
result = cocoindex_search(query="authentication service", confidence_threshold=0.6)

# 2. Валидация создания нового файла
validation = cocoindex_validate_creation(
    file_path="src/auth/service.py", 
    content="class AuthService: ..."
)

# 3. Проверка confidence level
if validation["confidence"] < 0.6:
    # НЕ СОЗДАВАТЬ - найти существующий файл
    return "Use existing file: " + validation["similar_files"][0]
```

### MCP команды для CocoIndex:

```python
# Поиск существующих скриптов
cocoindex_search(query="authentication", confidence_threshold=0.6)

# Валидация создания файла
cocoindex_validate_creation(file_path="new_file.py", content="...")

# Получение карты функциональности
cocoindex_functionality_map()

# Анализ дублирований
cocoindex_analyze_duplicates()
```

### Интеграция с AI агентом:

```python
# Автоматическая проверка перед созданием файла
def create_file_with_mcp_validation(file_path: str, content: str) -> bool:
    # 1. Проверка через MCP команду
    validation = cocoindex_validate_creation(file_path, content)
    
    # 2. Проверка confidence level
    if validation["confidence"] < 0.6:
        print(f"❌ DO NOT CREATE: {validation['reason']}")
        return False
    
    # 3. Создание файла
    create_file(file_path, content)
    print(f"✅ File created: {file_path}")
    return True
```

## Заключение

Этот чеклист обеспечивает систематический подход к поиску и переиспользованию существующих файлов, предотвращая дублирование кода и повышая эффективность разработки. Следование этому чеклисту поможет AI агенту работать более эффективно и создавать качественный код.
