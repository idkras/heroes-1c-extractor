# MCP Server Restart Instructions

## Для активации новых CocoIndex commands

После внесения изменений в MCP сервер, Cursor может не видеть новые команды. Для активации новых команд необходимо перезапустить MCP сервер.

### Способ 1: Перезапуск Cursor (Рекомендуется)

1. Закройте Cursor полностью
2. Откройте Cursor заново
3. Откройте проект
4. Проверьте доступность новых команд

### Способ 2: Перезапуск MCP сервера через терминал

1. Остановите текущий MCP сервер (если запущен)
2. Запустите MCP сервер заново:
   ```bash
   cd heroes-platform/mcp_server
   python src/mcp_server.py
   ```

### Способ 3: Проверка через тесты

Перед перезапуском можно проверить, что команды работают локально:

```bash
cd heroes-platform/mcp_server
python tests/integration/test_cocoindex_commands.py
```

### Новые CocoIndex Commands

После перезапуска должны быть доступны следующие команды:

- `cocoindex_search_existing_files` - Поиск существующих файлов
- `cocoindex_validate_file_creation` - Валидация создания файлов
- `cocoindex_get_functionality_map` - Карта функциональности проекта
- `cocoindex_analyze_duplicates` - Анализ дубликатов

### Проверка статуса

Для проверки статуса MCP сервера:

```bash
cd heroes-platform/mcp_server
python scripts/mcp_health_check.py
```

### Troubleshooting

Если команды все еще не видны:

1. Проверьте конфигурацию `.cursor/mcp.json`
2. Убедитесь, что путь к серверу правильный
3. Проверьте логи Cursor на наличие ошибок
4. Попробуйте перезапустить Cursor несколько раз
