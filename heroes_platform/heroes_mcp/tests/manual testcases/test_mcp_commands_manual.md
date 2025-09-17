# 🧪 Manual Test Cases: MCP Commands Testing
## Тестовые сценарии для проверки работы MCP команд согласно AI QA Standard v1.2

<!-- 🔒 PROTECTED SECTION: BEGIN -->
type: manual_test_cases
updated: 10 August 2025, 22:30 CET by AI Assistant
based on: AI QA Standard v1.2, From-The-End Standard v2.7, Registry Standard v5.8
version: 1.0
status: Active
tags: manual_testing, mcp_commands, quality_assurance, ai_qa_standard
<!-- 🔒 PROTECTED SECTION: END -->

---

## 🎯 Цель тестирования

Проверить работу базовых MCP команд через прямое тестирование MCP протокола без веб-интерфейса, согласно принципам AI QA Standard v1.2 и From-The-End Standard v2.7.

---

## 📋 Test Case 1: MCP Server Connection

### **ID**: TC-MCP-001
**JTBD**: Когда я запускаю MCP сервер, я хочу убедиться что он отвечает на базовые запросы, чтобы продолжить разработку команд
**Priority**: High
**Type**: Manual
**Automation**: None (прямое тестирование MCP протокола)

### **Manual Testing Steps**
1. Запустить MCP сервер: `python -m mcp_server`
2. Отправить JSON-RPC 2.0 запрос на инициализацию
3. Проверить ответ сервера
4. Отправить запрос на получение списка доступных инструментов
5. Проверить что сервер возвращает список инструментов

### **JSON-RPC 2.0 Test Requests**

#### **Initialize Request**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {}
    },
    "clientInfo": {
      "name": "test-client",
      "version": "1.0.0"
    }
  }
}
```

#### **Expected Response**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {}
    },
    "serverInfo": {
      "name": "standards-mcp-server",
      "version": "1.0.0"
    }
  }
}
```

#### **Tools List Request**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list"
}
```

### **Success Criteria**
- [ ] Сервер запускается без ошибок
- [ ] Initialize запрос возвращает корректный ответ
- [ ] Tools/list возвращает список доступных инструментов
- [ ] Время ответа < 5 секунд
- [ ] Нет критических ошибок в логах

---

## 📋 Test Case 2: Get Standards Command

### **ID**: TC-MCP-002
**JTBD**: Когда я хочу получить список стандартов, я хочу использовать MCP команду get_standards, чтобы быстро найти нужный стандарт
**Priority**: High
**Type**: Manual
**Automation**: None (прямое тестирование MCP протокола)

### **Manual Testing Steps**
1. Убедиться что MCP сервер запущен
2. Отправить запрос на выполнение get_standards команды
3. Проверить что возвращается список стандартов
4. Проверить формат ответа
5. Проверить что список не пустой

### **JSON-RPC 2.0 Test Request**

#### **Get Standards Request**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "get_standards",
    "arguments": {}
  }
}
```

#### **Expected Response Format**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Список стандартов:\n- Registry Standard v5.8\n- From-The-End Standard v2.7\n- MCP Workflow Standard v1.1\n- TDD Documentation Standard v2.5\n- AI QA Standard v1.2"
      }
    ]
  }
}
```

### **Success Criteria**
- [ ] Команда выполняется без ошибок
- [ ] Возвращается список стандартов
- [ ] Список содержит минимум 5 стандартов
- [ ] Формат ответа соответствует MCP протоколу
- [ ] Время выполнения < 3 секунд

---

## 📋 Test Case 3: Validate Standard Command

### **ID**: TC-MCP-003
**JTBD**: Когда я хочу проверить соответствие документа стандарту, я хочу использовать validate_standard команду, чтобы убедиться в качестве
**Priority**: Medium
**Type**: Manual
**Automation**: None (прямое тестирование MCP протокола)

### **Manual Testing Steps**
1. Убедиться что MCP сервер запущен
2. Отправить запрос на валидацию стандарта с корректными параметрами
3. Проверить что возвращается результат валидации
4. Отправить запрос с некорректными параметрами
5. Проверить обработку ошибок

### **JSON-RPC 2.0 Test Requests**

#### **Valid Standard Validation Request**
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "validate_standard",
    "arguments": {
      "standard_name": "Registry Standard v5.8",
      "file_path": "0.1 registry standard 15 may 2025 1320 CET by AI Assistant.md"
    }
  }
}
```

#### **Expected Success Response**
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "✅ Валидация стандарта 'Registry Standard v5.8' завершена успешно!\n📊 Результат: Соответствует всем требованиям\n🔗 Проверить: 0.1 registry standard 15 may 2025 1320 CET by AI Assistant.md"
      }
    ]
  }
}
```

#### **Invalid Parameters Request**
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "tools/call",
  "params": {
    "name": "validate_standard",
    "arguments": {
      "standard_name": "Non-existent Standard",
      "file_path": "non-existent-file.md"
    }
  }
}
```

#### **Expected Error Response**
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "error": {
    "code": -32602,
    "message": "Invalid parameters",
    "data": {
      "details": "Standard 'Non-existent Standard' not found or file 'non-existent-file.md' does not exist"
    }
  }
}
```

### **Success Criteria**
- [ ] Команда корректно валидирует существующие стандарты
- [ ] Возвращается понятный результат валидации
- [ ] Обрабатываются некорректные параметры
- [ ] Возвращается информативное сообщение об ошибке
- [ ] Время выполнения < 10 секунд

---

## 📋 Test Case 4: Create Standard Command

### **ID**: TC-MCP-004
**JTBD**: Когда я хочу создать новый стандарт, я хочу использовать create_standard команду, чтобы быстро создать структурированный документ
**Priority**: Medium
**Type**: Manual
**Automation**: None (прямое тестирование MCP протокола)

### **Manual Testing Steps**
1. Убедиться что MCP сервер запущен
2. Отправить запрос на создание стандарта с корректными параметрами
3. Проверить что файл создается
4. Проверить содержимое созданного файла
5. Проверить что файл соответствует шаблону

### **JSON-RPC 2.0 Test Request**

#### **Create Standard Request**
```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "tools/call",
  "params": {
    "name": "create_standard",
    "arguments": {
      "standard_name": "Test Standard v1.0",
      "description": "Тестовый стандарт для проверки функциональности",
      "category": "testing",
      "author": "AI Assistant"
    }
  }
}
```

#### **Expected Success Response**
```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "✅ Стандарт 'Test Standard v1.0' создан успешно!\n📝 Результат: Файл создан с базовой структурой\n🔗 Проверить: [standards .md]/test_standard_v1_0.md\n📊 Статистика: Стандарт готов к заполнению"
      }
    ]
  }
}
```

### **Success Criteria**
- [ ] Команда создает файл стандарта
- [ ] Файл содержит базовую структуру
- [ ] Структура соответствует шаблону стандартов
- [ ] Возвращается ссылка на созданный файл
- [ ] Время выполнения < 5 секунд

---

## 📋 Test Case 5: Error Handling and Recovery

### **ID**: TC-MCP-005
**JTBD**: Когда я отправляю некорректный запрос, я хочу получить понятное сообщение об ошибке, чтобы исправить проблему
**Priority**: High
**Type**: Manual
**Automation**: None (прямое тестирование MCP протокола)

### **Manual Testing Steps**
1. Убедиться что MCP сервер запущен
2. Отправить запрос с некорректным JSON
3. Проверить обработку JSON ошибок
4. Отправить запрос к несуществующей команде
5. Проверить обработку неизвестных команд
6. Отправить запрос с некорректными параметрами
7. Проверить валидацию параметров

### **JSON-RPC 2.0 Test Requests**

#### **Invalid JSON Request**
```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "method": "tools/call",
  "params": {
    "name": "get_standards",
    "arguments": {
      "invalid": "json"
    }
  }
}
```

#### **Non-existent Command Request**
```json
{
  "jsonrpc": "2.0",
  "id": 8,
  "method": "tools/call",
  "params": {
    "name": "non_existent_command",
    "arguments": {}
  }
}
```

#### **Expected Error Responses**

**For Invalid JSON:**
```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "error": {
    "code": -32700,
    "message": "Parse error",
    "data": {
      "details": "Invalid JSON format"
    }
  }
}
```

**For Non-existent Command:**
```json
{
  "jsonrpc": "2.0",
  "id": 8,
  "error": {
    "code": -32601,
    "message": "Method not found",
    "data": {
      "details": "Command 'non_existent_command' not found"
    }
  }
}
```

### **Success Criteria**
- [ ] Некорректный JSON обрабатывается корректно
- [ ] Несуществующие команды возвращают понятную ошибку
- [ ] Некорректные параметры валидируются
- [ ] Ошибки содержат полезную информацию
- [ ] Сервер не падает при ошибках

---

## 📋 Test Case 6: Performance and Response Time

### **ID**: TC-MCP-006
**JTBD**: Когда я использую MCP команды, я хочу получать быстрые ответы, чтобы не тратить время на ожидание
**Priority**: Medium
**Type**: Manual
**Automation**: None (прямое тестирование MCP протокола)

### **Manual Testing Steps**
1. Убедиться что MCP сервер запущен
2. Измерить время ответа для get_standards команды
3. Измерить время ответа для validate_standard команды
4. Измерить время ответа для create_standard команды
5. Проверить стабильность времени ответа при повторных запросах

### **Performance Test Script**
```bash
#!/bin/bash
# Performance test script for MCP commands

echo "Testing MCP Commands Performance..."

# Test get_standards
echo "Testing get_standards..."
time curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_standards","arguments":{}}}'

# Test validate_standard
echo "Testing validate_standard..."
time curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"validate_standard","arguments":{"standard_name":"Registry Standard v5.8","file_path":"0.1 registry standard 15 may 2025 1320 CET by AI Assistant.md"}}}'

# Test create_standard
echo "Testing create_standard..."
time curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"create_standard","arguments":{"standard_name":"Performance Test Standard","description":"Test","category":"testing","author":"AI Assistant"}}}'
```

### **Success Criteria**
- [ ] get_standards: время ответа < 3 секунд
- [ ] validate_standard: время ответа < 10 секунд
- [ ] create_standard: время ответа < 5 секунд
- [ ] Стабильное время ответа при повторных запросах
- [ ] Нет утечек памяти при длительной работе

---

## 📊 Test Execution Summary

### **Test Results Template**
```markdown
## Test Execution Results

**Date:** [Дата выполнения тестов]
**Tester:** [Имя тестировщика]
**Environment:** [Описание окружения]

### Test Results
- [ ] TC-MCP-001: MCP Server Connection - ✅/❌
- [ ] TC-MCP-002: Get Standards Command - ✅/❌
- [ ] TC-MCP-003: Validate Standard Command - ✅/❌
- [ ] TC-MCP-004: Create Standard Command - ✅/❌
- [ ] TC-MCP-005: Error Handling and Recovery - ✅/❌
- [ ] TC-MCP-006: Performance and Response Time - ✅/❌

### Issues Found
- [Issue 1]: [Описание проблемы]
- [Issue 2]: [Описание проблемы]

### Recommendations
- [Recommendation 1]: [Рекомендация]
- [Recommendation 2]: [Рекомендация]

### Overall Assessment
**Pass/Fail:** [Общий результат]
**Confidence Level:** [Уровень уверенности 0-1]
```

---

## 🔄 Continuous Testing Process

### **Daily Testing**
- [ ] Проверка базовой функциональности MCP сервера
- [ ] Валидация времени ответа команд
- [ ] Проверка обработки ошибок

### **Weekly Testing**
- [ ] Полное выполнение всех manual test cases
- [ ] Анализ производительности
- [ ] Обновление тестовых сценариев

### **Monthly Testing**
- [ ] Комплексное тестирование всех функций
- [ ] Анализ трендов производительности
- [ ] Обновление критериев успеха

---

**Manual Test Cases готовы к использованию** ✅

Все тесты соответствуют:
- ✅ AI QA Standard v1.2
- ✅ From-The-End Standard v2.7
- ✅ Registry Standard v5.8
- ✅ MCP Workflow Standard v1.1

**Тесты готовы к применению в production среде** 🚀
