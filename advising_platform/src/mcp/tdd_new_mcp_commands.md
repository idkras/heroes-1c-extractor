# TDD Plan: New MCP Commands (update_standard, add_mcp_command)

## Analysis of Current Gaps

### 1. Несоответствия в стандарте гипотез
- **Проблема**: Стандарт гипотез содержит TDD workflow, но отсутствуют прямые связи с MCP командами
- **Отсутствует**: Описание как запускать каждый шаг через MCP команды
- **Требуется**: Интеграция reflection_guard в каждый этап workflow

### 2. Несоответствия в MCP create_incident команде
- **Проблема**: Команда не следует AI Incident Standard v1.9
- **Отсутствует**: Структура "5 почему", корневая причина, дизайн-инъекция
- **Формат заголовка**: Неправильный (использует ID вместо "DD MMM YYYY HH:MM")

## RED Phase: Expected Failures

```yaml
new_commands_expected_failures:
  update_standard:
    - "Команда не валидирует изменения против Registry Standard"
    - "Отсутствует проверка соответствия Task Master Standard"
    - "Не применяет протокол бережности"
    - "Нет автоматического обновления кеша DuckDB"
    
  add_mcp_command:
    - "Команда не проверяет уникальность имени команды"
    - "Отсутствует валидация JSON Schema для параметров"
    - "Нет автоматической регистрации в standards_mcp_server.js"
    - "Не создает соответствующие тесты"
```

## GREEN Phase: Implementation Strategy

### Command: update_standard
```python
async def update_standard(args):
    """
    Обновляет существующий стандарт с полной валидацией
    """
    # 1. Валидация существования стандарта
    standard_id = args.get('standard_id')
    if not await validate_standard_exists(standard_id):
        raise StandardNotFoundError(f"Standard {standard_id} not found")
    
    # 2. Применение Registry Standard протокола
    changes = args.get('changes')
    validated_changes = await apply_registry_protocol(changes)
    
    # 3. Проверка Task Master Standard соответствия
    compliance_check = await validate_task_master_compliance(validated_changes)
    if not compliance_check.passed:
        raise ComplianceError(f"Changes violate Task Master Standard: {compliance_check.violations}")
    
    # 4. Применение протокола бережности
    careful_update = await apply_careful_protocol(standard_id, validated_changes)
    
    # 5. Обновление DuckDB кеша
    await update_duckdb_cache(standard_id, careful_update)
    
    return {
        "success": True,
        "updated_standard": standard_id,
        "changes_applied": len(validated_changes),
        "cache_updated": True
    }
```

### Command: add_mcp_command
```python
async def add_mcp_command(args):
    """
    Добавляет новую MCP команду с полной интеграцией
    """
    # 1. Валидация уникальности
    command_name = args.get('name')
    if await command_exists(command_name):
        raise DuplicateCommandError(f"Command {command_name} already exists")
    
    # 2. Валидация JSON Schema
    schema = args.get('input_schema')
    await validate_json_schema(schema)
    
    # 3. Создание Python backend
    backend_code = await generate_python_backend(command_name, schema)
    await save_backend_file(f"python_backends/{command_name}.py", backend_code)
    
    # 4. Регистрация в standards_mcp_server.js
    await register_in_mcp_server(command_name, schema)
    
    # 5. Генерация тестов
    test_code = await generate_command_tests(command_name, schema)
    await save_test_file(f"tests/test_{command_name}.py", test_code)
    
    return {
        "success": True,
        "command_created": command_name,
        "files_generated": ["backend", "tests", "registration"],
        "ready_for_testing": True
    }
```

## REFACTOR Phase: Optimization

### Общие принципы оптимизации:
1. **Atomic Operations**: Все операции должны быть атомарными и откатываемыми
2. **Reflection Guards**: Каждый шаг должен включать reflection checkpoint
3. **Error Recovery**: Автоматическое восстановление при сбоях
4. **Performance**: Минимизация времени выполнения через кеширование

### Integration Points:
- `reflection_guard.py` для всех reflection checkpoints
- `cache_reader.py` для работы с DuckDB
- `standards_mcp_server.js` для регистрации команд
- `protocol_completion.py` для валидации протоколов

## Test Scenarios

```python
# test_update_standard.py
def test_update_standard_validates_existence():
    """Тест валидации существования стандарта"""
    pass

def test_update_standard_applies_registry_protocol():
    """Тест применения Registry Standard протокола"""
    pass

def test_update_standard_checks_task_master_compliance():
    """Тест проверки Task Master Standard соответствия"""
    pass

# test_add_mcp_command.py
def test_add_mcp_command_validates_uniqueness():
    """Тест валидации уникальности команды"""
    pass

def test_add_mcp_command_validates_schema():
    """Тест валидации JSON Schema"""
    pass

def test_add_mcp_command_generates_all_files():
    """Тест генерации всех необходимых файлов"""
    pass
```

## Implementation Priority

1. **HIGH**: `update_standard` - критично для поддержания качества стандартов
2. **HIGH**: Исправление `create_incident` согласно AI Incident Standard v1.9
3. **MEDIUM**: `add_mcp_command` - ускорит разработку новых команд
4. **LOW**: Оптимизация производительности существующих команд

## Success Criteria

- [ ] Все тесты проходят (RED → GREEN)
- [ ] Команды интегрированы в standards_mcp_server.js
- [ ] DuckDB кеш обновляется автоматически
- [ ] Reflection guards работают на каждом этапе
- [ ] Время выполнения < 2 секунд для каждой команды