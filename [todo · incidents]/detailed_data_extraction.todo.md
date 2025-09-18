# 🔍 ДЕТАЛЬНОЕ ИЗВЛЕЧЕНИЕ ДАННЫХ 1С - ПЛАН РЕШЕНИЯ

## 🎯 ЦЕЛЬ ПРОЕКТА: detailed_data_extraction

**JTBD**: Как система извлечения данных, я хочу получить полные детализированные данные о цветочном бизнесе в parquet/duckdb формате, чтобы можно было анализировать продажи по цветам, магазинам и временным периодам.

## 📊 ВЫЯВЛЕННАЯ ПРОБЛЕМА:

### **КРИТИЧЕСКИЙ GAP:**
- **Ожидается**: Полные документы с типом, магазином, суммой, товарами, цветами
- **Фактически**: Только метаданные без детального содержимого
- **Причина**: `extract_all_available_data.py` извлекает только структуру, не содержимое

### **КОРНЕВАЯ ПРИЧИНА:**
1. **Неполное извлечение BLOB данных** - только метаданные, не содержимое
2. **Отсутствие парсинга табличных частей** - не извлекаются товары
3. **Нет связи с справочниками** - не извлекаются названия магазинов, товаров
4. **Отсутствие временных меток** - не извлекаются даты операций
5. **Неполная обработка документов** - только основные поля, не детали

## 🎯 ПЛАН РЕШЕНИЯ:

### **ЭТАП 1: АНАЛИЗ ТЕКУЩЕГО СОСТОЯНИЯ** (Приоритет: CRITICAL)
- [ ] Проанализировать что именно извлекается сейчас
- [ ] Выявить какие поля отсутствуют
- [ ] Определить источники детальных данных
- [ ] Создать карту полей для полного извлечения

### **ЭТАП 2: УЛУЧШЕНИЕ ИЗВЛЕЧЕНИЯ BLOB ДАННЫХ** (Приоритет: HIGH)
- [ ] Улучшить методы извлечения BLOB содержимого
- [ ] Добавить парсинг табличных частей документов
- [ ] Извлекать детальную информацию о товарах
- [ ] Добавить извлечение временных меток

### **ЭТАП 3: ИЗВЛЕЧЕНИЕ СВЯЗАННЫХ ДАННЫХ** (Приоритет: HIGH)
- [ ] Извлекать данные из справочников (магазины, товары, контрагенты)
- [ ] Связывать документы с справочниками
- [ ] Добавить полные названия вместо кодов
- [ ] Извлекать детальную информацию о цветах

### **ЭТАП 4: СОЗДАНИЕ ПОЛНОЙ СТРУКТУРЫ ДАННЫХ** (Приоритет: HIGH)
- [ ] Создать структуру для полных документов
- [ ] Добавить все необходимые поля согласно @1c.testcases.md
- [ ] Обеспечить извлечение всех типов документов
- [ ] Добавить валидацию полноты данных

### **ЭТАП 5: ТЕСТИРОВАНИЕ И ВАЛИДАЦИЯ** (Приоритет: CRITICAL)
- [ ] Создать тесты для проверки полноты данных
- [ ] Валидировать что все поля извлечены
- [ ] Проверить качество данных о цветах
- [ ] Убедиться что можно анализировать цветочный бизнес

## 📋 КОНКРЕТНЫЕ ДЕЙСТВИЯ:

### **1. УЛУЧШЕНИЕ ИЗВЛЕЧЕНИЯ BLOB ДАННЫХ:**

**Проблема**: Текущий код извлекает только метаданные BLOB полей
**Решение**: Добавить полное извлечение содержимого BLOB полей

```python
# Текущий код (неполный):
blob_data = {
    "field_type": "blob",
    "size": len(value),
    "extraction_methods": []
}

# Улучшенный код (полный):
def extract_full_blob_content(blob_obj):
    """Извлекает полное содержимое BLOB поля"""
    blob_data = {
        "field_type": "blob",
        "size": len(value),
        "extraction_methods": [],
        "content": "",
        "parsed_data": {}
    }
    
    # Метод 1: Прямое извлечение содержимого
    if hasattr(blob_obj, 'value'):
        content = blob_obj.value
        if isinstance(content, bytes):
            try:
                blob_data["content"] = content.decode("utf-8")
                blob_data["extraction_methods"].append("value_utf8")
            except UnicodeDecodeError:
                try:
                    blob_data["content"] = content.decode("cp1251")
                    blob_data["extraction_methods"].append("value_cp1251")
                except UnicodeDecodeError:
                    blob_data["content"] = content.hex()
                    blob_data["extraction_methods"].append("value_hex")
    
    # Метод 2: Парсинг структурированных данных
    if blob_data["content"]:
        parsed_data = parse_blob_content(blob_data["content"])
        blob_data["parsed_data"] = parsed_data
    
    return blob_data
```

### **2. ИЗВЛЕЧЕНИЕ ТАБЛИЧНЫХ ЧАСТЕЙ ДОКУМЕНТОВ:**

**Проблема**: Не извлекаются товары из табличных частей
**Решение**: Добавить извлечение табличных частей

```python
def extract_table_parts(db, document_id):
    """Извлекает табличные части документа"""
    table_parts = {}
    
    # Ищем табличные части документа
    for table_name in db.tables.keys():
        if table_name.startswith(f"{document_id}_VT"):
            table = db.tables[table_name]
            records = []
            
            for i, row in enumerate(table):
                if not row.is_empty:
                    row_data = row.as_dict()
                    records.append({
                        "row_index": i,
                        "nomenclature": row_data.get("_FLD4241", ""),  # Номенклатура
                        "quantity": row_data.get("_FLD4242", 0),      # Количество
                        "price": row_data.get("_FLD4243", 0),         # Цена
                        "amount": row_data.get("_FLD4244", 0),        # Сумма
                        "flower_name": extract_flower_name(row_data), # Название цветка
                        "flower_color": extract_flower_color(row_data), # Цвет цветка
                    })
            
            table_parts[table_name] = records
    
    return table_parts
```

### **3. ИЗВЛЕЧЕНИЕ ДАННЫХ ИЗ СПРАВОЧНИКОВ:**

**Проблема**: Не извлекаются полные названия магазинов, товаров
**Решение**: Добавить извлечение из справочников

```python
def extract_reference_data(db, reference_id):
    """Извлекает данные из справочника"""
    if reference_id in db.tables:
        table = db.tables[reference_id]
        records = []
        
        for i, row in enumerate(table):
            if not row.is_empty:
                row_data = row.as_dict()
                records.append({
                    "id": row_data.get("_IDRREF", ""),
                    "name": row_data.get("_DESCRIPTION", ""),
                    "code": row_data.get("_CODE", ""),
                    "full_name": row_data.get("_FLD10001", ""),  # Полное название
                    "address": row_data.get("_FLD10002", ""),    # Адрес
                    "contact": row_data.get("_FLD10003", ""),    # Контакт
                })
        
        return records
    return []
```

### **4. СОЗДАНИЕ ПОЛНОЙ СТРУКТУРЫ ДОКУМЕНТА:**

**Проблема**: Отсутствует полная структура документа
**Решение**: Создать полную структуру согласно @1c.testcases.md

```python
def create_full_document_structure(db, document_id, row_index, row_data):
    """Создает полную структуру документа"""
    document = {
        # Основные поля документа
        "document_id": f"{document_id}_{row_index}",
        "document_type": extract_document_type(row_data),
        "document_number": row_data.get("_NUMBER", ""),
        "document_date": extract_document_date(row_data),
        "total_amount": row_data.get("_FLD4239", 0),
        "currency": "RUB",
        "is_posted": row_data.get("_POSTED", False),
        "is_marked": row_data.get("_MARKED", False),
        
        # Данные о магазине
        "store": {
            "code": row_data.get("_FLD4245", ""),
            "name": extract_store_name(db, row_data.get("_FLD4245", "")),
            "address": extract_store_address(db, row_data.get("_FLD4245", "")),
        },
        
        # Данные о контрагенте
        "counterparty": {
            "code": row_data.get("_FLD4246", ""),
            "name": extract_counterparty_name(db, row_data.get("_FLD4246", "")),
            "type": extract_counterparty_type(row_data),
        },
        
        # Товары и цветы
        "items": extract_table_parts(db, document_id),
        "flowers": extract_flower_data(db, document_id),
        
        # Временные метки
        "timestamps": {
            "created": row_data.get("_DATE_TIME", ""),
            "posted": row_data.get("_FLD4247", ""),
            "modified": row_data.get("_FLD4248", ""),
        },
        
        # BLOB данные
        "blob_data": extract_full_blob_content(row_data),
        
        # Метаданные
        "metadata": {
            "extraction_date": datetime.now().isoformat(),
            "source_table": document_id,
            "row_index": row_index,
            "version": row_data.get("_VERSION", ""),
        }
    }
    
    return document
```

## 🧪 ТЕСТЫ ДЛЯ ВАЛИДАЦИИ:

### **ТЕСТ 1: ПРОВЕРКА ПОЛНОТЫ ДАННЫХ**
```python
def test_data_completeness():
    """Проверяет что все необходимые поля извлечены"""
    # Проверяем что есть все обязательные поля
    required_fields = [
        "document_type", "document_number", "document_date",
        "total_amount", "store", "counterparty", "items", "flowers"
    ]
    
    for field in required_fields:
        assert field in document, f"Отсутствует поле: {field}"
```

### **ТЕСТ 2: ПРОВЕРКА ДАННЫХ О ЦВЕТАХ**
```python
def test_flower_data():
    """Проверяет что данные о цветах извлечены"""
    # Проверяем что найдены цветы
    flower_keywords = ["роза", "тюльпан", "хризантема", "лилия"]
    
    for keyword in flower_keywords:
        found = any(keyword in str(document).lower() for document in documents)
        assert found, f"Не найден цветок: {keyword}"
```

### **ТЕСТ 3: ПРОВЕРКА ВРЕМЕННЫХ МЕТОК**
```python
def test_temporal_data():
    """Проверяет что временные данные извлечены"""
    # Проверяем что даты не "N/A"
    for document in documents:
        assert document["document_date"] != "N/A", "Дата документа отсутствует"
        assert document["timestamps"]["created"] != "N/A", "Дата создания отсутствует"
```

### **ТЕСТ 4: ПРОВЕРКА СВЯЗЕЙ С СПРАВОЧНИКАМИ**
```python
def test_reference_links():
    """Проверяет что связи с справочниками работают"""
    for document in documents:
        # Проверяем что есть полное название магазина
        assert document["store"]["name"] != "", "Название магазина отсутствует"
        # Проверяем что есть полное название контрагента
        assert document["counterparty"]["name"] != "", "Название контрагента отсутствует"
```

## 📊 КРИТЕРИИ УСПЕХА:

- ✅ **100% извлечение** всех полей согласно @1c.testcases.md
- ✅ **Найдены данные о цветах** - розы, тюльпаны, хризантемы
- ✅ **Найдены данные о магазинах** - полные названия и адреса
- ✅ **Найдены временные метки** - даты операций
- ✅ **Найдены товары** - детализация по номенклатуре
- ✅ **Работают SQL запросы** - можно анализировать цветочный бизнес

## 🚀 СЛЕДУЮЩИЕ ШАГИ:

1. **Улучшить извлечение BLOB данных** - полное содержимое
2. **Добавить извлечение табличных частей** - товары и цветы
3. **Связать с справочниками** - полные названия
4. **Создать полную структуру** - все поля согласно стандарту
5. **Протестировать и валидировать** - убедиться что все работает

---
**Создано**: 2025-01-10 23:58 CET
**Статус**: В работе
**Приоритет**: CRITICAL
**Следующий шаг**: Улучшить извлечение BLOB данных
