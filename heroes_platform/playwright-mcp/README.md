# Playwright MCP Server

JTBD: Как MCP сервер, я хочу предоставлять функциональность для тестирования веб-страниц,
чтобы обеспечить автоматизированное тестирование и валидацию веб-приложений.

## Установка

```bash
cd heroes-platform/playwright-mcp
pip install -r requirements.txt
playwright install
```

## Использование

### Запуск сервера

```bash
python playwright_mcp_server.py
```

### Доступные команды

- `run_playwright_tests` - Запуск Playwright тестов для визуальной валидации

### Пример использования

```python
# В Cursor или другом MCP клиенте
result = await run_playwright_tests(
    url="https://example.com",
    test_type="visual"  # visual, manual, all
)
```

## Архитектура

- **Атомарные функции**: Все методы ≤20 строк
- **Модульность**: Отдельный MCP сервер
- **Тестируемость**: Полное покрытие тестами
- **JTBD документация**: Каждая функция документирована

## Структура

```
playwright-mcp/
├── playwright_mcp_server.py  # Основной сервер
├── requirements.txt          # Зависимости
├── README.md                # Документация
└── tests/                   # Тесты
    └── playwright/          # Playwright тесты
```
