# Пример использования абстрактных ссылок

## Форматы абстрактных ссылок

Система поддерживает два формата абстрактных ссылок:

### 1. Прямой формат (тип:идентификатор)

```markdown
[Текст ссылки](task:todo)
```

### 2. URL формат с протоколом abstract://

```markdown
[Текст ссылки](abstract://task:todo)
```

## Примеры абстрактных ссылок:

- [Список задач](abstract://task:todo)
- [Архив задач](abstract://task:todo.archive)
- [Стандарт оформления тикетов](abstract://standard:ticket)
- [Стандарт инцидентов AI](abstract://standard:ai_incident)
- [Стандарт карты целей](abstract://standard:goal_map)

## Использование CLI для конвертации:

### Преобразование в абстрактные ссылки

```bash
python abstract_links_cli.py convert example.md
```

### Преобразование в физические пути

```bash
python abstract_links_cli.py convert example.md --to-physical
```

## Системные абстрактные идентификаторы

Всего зарегистрировано 31 логических идентификаторов, включая:

1. `task:todo` - Список текущих задач
2. `task:todo.archive` - Архив задач
3. `incident:ai` - Инциденты, связанные с AI
4. `standard:registry` - Стандарт реестра
5. `standard:process_task` - Стандарт рабочих задач
6. `standard:ticket` - Стандарт оформления тикетов
7. `standard:goal_map` - Стандарт карты целей
8. `standard:ai_incident` - Стандарт AI-инцидентов