# Настройка Heroes MCP Server в Cursor IDE

## Проблема решена! ✅

FastMCP сервер был исправлен. Проблема была в конфликте зависимостей Python пакетов.

## Что было сделано:

1. **Создано виртуальное окружение** для изоляции зависимостей
2. **Установлен MCP** в чистом окружении
3. **Создан скрипт-обертка** `run_server.py` для запуска с виртуальным окружением
4. **Протестирован сервер** - все инструменты работают

## Обновление конфигурации Cursor:

1. Откройте **Cursor Settings** (⌘ + ,)
2. Перейдите в раздел **"Tools & Integrations"** > **"MCP Tools"**
3. Найдите сервер **"heroes-mcp"**
4. Измените путь на:
   ```
   /Users/ilyakrasinsky/workspace/vscode.projects/heroes-template/platform/mcp_server/run_server.py
   ```
5. Убедитесь, что переключатель **включен** (зеленый)
6. **Перезапустите Cursor IDE**

## Доступные инструменты:

- ✅ `server_info` - Информация о сервере
- ✅ `telegram_get_credentials` - Telegram учетные данные
- ✅ `telegram_test_connection` - Тест Telegram подключения
- ✅ `telegram_get_chats` - Список чатов Telegram
- ✅ `telegram_search_chats` - Поиск чатов
- ✅ `telegram_export_chat` - Экспорт истории чата
- ✅ `standards_management` - Управление стандартами
- ✅ `heroes_gpt_workflow` - HeroesGPT workflow
- ✅ `performance_monitor` - Мониторинг производительности

## Проверка работы:

После обновления конфигурации красная точка должна исчезнуть, и сервер будет работать нормально.

Если проблемы остаются, перезапустите Cursor IDE полностью.
