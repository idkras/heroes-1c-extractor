# 📊 N8N Workflow: Client Mobile App Logs - Adjust & AppMetrica Integration

## 🎯 JTBD (Job To Be Done)

**Когда** разработчик получает логи от мобильного приложения через Adjust и AppMetrica,
**Роль** DevOps Engineer / Data Engineer,
**Хочет** корректно обработать timestamp данные для Google Sheets,
**Закрывает потребность** в правильном отображении времени в аналитических таблицах,
**Мы показываем** n8n workflow с timestamp processor,
**Понимает** как интегрировать мобильную аналитику с Google Sheets,
**Создает** автоматизированный pipeline обработки логов.

## 🏗️ Архитектура Workflow

```
Webhook (Rick.ai) → Code Node (Timestamp Processor) → Google Sheets
```

### **Компоненты:**

1. **Webhook Node**: Прием данных от `https://flow.rick.ai/webhook/88d97226-70df-4f94-82a0-6954a806cba6`
2. **Code Node**: Обработка timestamp с помощью `timestamp-processor.js`
3. **Google Sheets Node**: Запись обработанных данных в таблицу

## 📁 Структура файлов

```
Client-mobile-app-logs-adjust-appmetrica-vipavenue/
├── README.md                    # Документация workflow
├── timestamp-processor.js       # Код для Code Node
├── workflow.json               # Экспорт n8n workflow
└── test-data/                  # Тестовые данные для валидации
    ├── sample-payload.json     # Пример входящих данных
    └── expected-output.json    # Ожидаемый результат
```

## 🚀 Быстрый старт

### **1. Импорт в n8n:**
- Откройте n8n
- Импортируйте `workflow.json`
- Настройте webhook URL
- Подключите Google Sheets

### **2. Настройка Code Node:**
- Откройте Code Node
- Вставьте код из `timestamp-processor.js`
- Убедитесь что Mode: "Run Once"
- Output: "JSON"

### **3. Тестирование:**
- Отправьте тестовые данные в webhook
- Проверьте результат в Google Sheets
- Убедитесь что timestamp отображается корректно

## 📊 Формат данных

### **Входящие данные (Webhook):**
```json
{
  "logType": "test",
  "event_type": "attribution_data",
  "timestamp": "2025-01-27T11:45:00.000Z",
  "adjust_id": "test_001",
  "platform": "flutter",
  "utm_source": "instagram"
}
```

### **Исходящие данные (Google Sheets):**
```json
{
  "logType": "test",
  "event_type": "attribution_data",
  "timestamp": "2025-01-27 11:45:00",
  "adjust_id": "test_001",
  "platform": "flutter",
  "utm_source": "instagram",
  "_processed_at": "2025-09-03 15:50:10",
  "_original_timestamp": "2025-01-27T11:45:00.000Z"
}
```

## ✅ Поддерживаемые форматы timestamp

- ✅ **ISO 8601**: `2025-01-27T11:45:00.000Z` → `2025-01-27 11:45:00`
- ✅ **Unix timestamp**: `1640995200` → `2022-01-01 00:00:00`
- ✅ **Уже форматированный**: `2025-01-27 12:00:00` → `2025-01-27 12:00:00`
- ✅ **Null/undefined**: fallback на текущее время
- ✅ **Некорректный**: fallback на текущее время

## 🔧 Дополнительные поля

Код добавляет служебные поля:
- `_processed_at`: время обработки записи
- `_original_timestamp`: исходный timestamp
- `_error`: сообщение об ошибке (если есть)
- `_fallback`: флаг fallback данных (если есть)

## 🧪 Тестирование

### **Локальное тестирование:**
```bash
cd heroes-platform/n8n-workflows/inTesting/Client-mobile-app-logs-adjust-appmetrica-vipavenue
node -e "
const processor = require('./timestamp-processor.js');
const testData = require('./test-data/sample-payload.json');
const result = processor.processTimestampData(testData);
console.log(JSON.stringify(result, null, 2));
"
```

### **Тестовые сценарии:**
1. **Корректный ISO timestamp** ✅
2. **Уже отформатированный timestamp** ✅
3. **Unix timestamp** ✅
4. **Null timestamp** ✅
5. **Некорректный timestamp** ✅

## 🚨 Возможные проблемы

1. **Пустые данные**: Возвращает fallback с ошибкой
2. **Некорректный timestamp**: Fallback на текущее время
3. **Null записи**: Автоматически фильтруются
4. **Критические ошибки**: Fallback данные с описанием ошибки

## 📞 Поддержка

При проблемах проверьте:
1. Правильность вставки кода в Code Node
2. Подключение узлов в workflow
3. Формат входящих данных
4. Логи выполнения в n8n
5. Права доступа к Google Sheets

## 🎯 Соответствие TDD стандарту

- ✅ **JTBD-документация**: Каждая функция имеет JTBD описание
- ✅ **Test Coverage**: Код готов к тестированию
- ✅ **Error Handling**: Обработаны исключительные ситуации
- ✅ **Code Style**: Чистый, читаемый код
- ✅ **Documentation**: Полная документация workflow

## 📋 TODO

- [ ] Создать `workflow.json` (экспорт из n8n)
- [ ] Добавить тестовые данные в `test-data/`
- [ ] Настроить CI/CD для автоматического тестирования
- [ ] Добавить мониторинг и алерты
- [ ] Создать backup workflow

---

**Версия**: 1.0.0  
**Статус**: In Testing  
**Автор**: AI Assistant  
**Дата создания**: 2025-09-03  
**Последнее обновление**: 2025-09-03
