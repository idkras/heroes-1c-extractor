# Workflows Module

JTBD: Как модуль workflows, я хочу предоставить документацию для всех workflow,
чтобы разработчики могли быстро понять архитектуру и использовать workflow правильно.

## 📋 Registry Workflow

### **Описание:**
Registry Workflow предоставляет guidance систему для AI Agent, обеспечивая качественную валидацию и проверку артефактов.

### **Команды:**
- `registry_compliance_check()` - проверка соответствия Registry Standard
- `registry_output_validate(jtbd, artifact)` - чеклист для проверки артефакта
- `registry_docs_audit(paths)` - чеклист для аудита документации
- `registry_gap_report(expected, actual, decision)` - анализ gap между ожидаемым и фактическим
- `registry_release_block(until)` - чеклист для блокировки/разблокировки релиза

### **Архитектура:**
- **Файл:** `registry_workflow.py` (460 строк - требует оптимизации)
- **Методы:** Все ≤20 строк (соответствие стандарту)
- **Тестирование:** 18 тестов (11 unit + 7 integration)
- **Статус:** ЗАВЕРШЕН (требует оптимизации размера)

### **Использование:**
```python
from workflows.registry_workflow import RegistryWorkflow

workflow = RegistryWorkflow()
result = workflow.output_validate("JTBD описание", "path/to/artifact")
```

### **Тестирование:**
```bash
# Unit тесты
pytest workflows/tests/unit/test_registry_workflow.py -v

# Integration тесты  
pytest workflows/tests/integration/test_registry_integration.py -v

# Все тесты
pytest workflows/tests/ -v
```

## 🚧 TODO

### **Registry Workflow:**
- [ ] Оптимизировать размер файла (460 → ≤300 строк)
- [ ] Разбить на подмодули при необходимости
- [ ] Добавить performance тесты
- [ ] Создать актуальные скриншоты evidence

### **Общие улучшения:**
- [ ] Добавить README для каждого workflow
- [ ] Создать общую документацию по архитектуре
- [ ] Добавить примеры использования
- [ ] Создать troubleshooting guide
