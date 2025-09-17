# 🔍 MCP Logs Monitoring Guide

## Обзор

Данное руководство описывает систему мониторинга логов MCP серверов и Output панели Cursor IDE, включая CI/CD тесты и автоматизированные проверки.

## Проблема

**Корневая причина:** credentials_wrapper.py выводит эмодзи и текст в stdout, который Cursor пытается парсить как JSON-RPC, но получает невалидный JSON.

**Типичные ошибки в логах:**
```
[error] Client error for command Unexpected token 'P', "Please ent"... is not valid JSON
[error] Client error for command Unexpected token '✅', "✅ TELEGRAM_API_ID" is not valid JSON
[error] Client error for command Unexpected token '🚀', "🚀 Startin"... is not valid JSON
```

## Решение

### 1. Исправление credentials_wrapper.py

**Проблема:** Все print() выводят в stdout
**Решение:** Перенаправить все логи в stderr

```python
# НЕПРАВИЛЬНО - выводит в stdout
print("🔐 Loading credentials...")

# ПРАВИЛЬНО - выводит в stderr
import sys
print("🔐 Loading credentials...", file=sys.stderr)
```

### 2. Мониторинг логов в Cursor IDE

#### Как открыть логи в Cursor

**Через меню:**
- `Cursor` → `Help` → `Show Logs` (macOS)
- `Help` → `Show Logs` (Windows/Linux)

**Через Command Palette:**
- `Cmd+Shift+P` (macOS) / `Ctrl+Shift+P` (Windows/Linux)
- Ввести: `Developer: Show Logs`

**Прямой доступ:**
```bash
# macOS
open ~/Library/Application\ Support/Cursor/logs/

# Windows
explorer %APPDATA%\Cursor\logs\

# Linux
xdg-open ~/.config/Cursor/logs/
```

#### Как открыть Output панель

**Через меню:**
- `View` → `Output`

**Через Command Palette:**
- `Cmd+Shift+P` / `Ctrl+Shift+P`
- Ввести: `View: Toggle Output`

**Горячие клавиши:**
- `Cmd+Shift+U` (macOS) / `Ctrl+Shift+U` (Windows/Linux)

#### Выбор правильного Output канала

1. В Output панели найти выпадающий список каналов
2. Выбрать нужный канал:
   - `MCP` - для MCP серверов
   - `Extension Host` - для расширений
   - `Language Server Protocol` - для языковых серверов
   - `Terminal` - для терминала

### 3. Автоматизированное тестирование

#### Запуск тестов мониторинга

```bash
# Запуск всех тестов
cd heroes_platform
python scripts/test_mcp_logs_monitoring.py

# Запуск с переменной окружения для тестирования
CURSOR_LOGS_PATH=/path/to/test/logs python scripts/test_mcp_logs_monitoring.py
```

#### CI/CD интеграция

GitHub Actions workflow автоматически:
- Запускается при изменениях в MCP серверах
- Тестирует на всех платформах (Ubuntu, macOS, Windows)
- Создает отчеты с детальным анализом
- Создает issues для критических ошибок
- Комментирует PR с результатами

### 4. Типичные ошибки и решения

| Ошибка | Причина | Решение |
|--------|---------|---------|
| `Unexpected token 'P', "Please ent"...` | credentials_wrapper.py выводит в stdout | Перенаправить в stderr |
| `Unexpected token '✅', "✅ TELEGRAM_API_ID"` | Эмодзи в stdout | Использовать stderr для логов |
| `Client error for command` | Нарушение JSON-RPC протокола | Исправить MCP сервер |
| `spawn python ENOENT` | Неправильный путь к Python | Использовать абсолютный путь |

### 5. Мониторинг в реальном времени

#### Через терминал

```bash
# macOS - мониторинг логов Cursor
tail -f ~/Library/Application\ Support/Cursor/logs/*/main.log

# Мониторинг MCP логов
tail -f ~/Library/Application\ Support/Cursor/logs/*/window*/exthost/*/MCP*.log

# Поиск ошибок в реальном времени
tail -f ~/Library/Application\ Support/Cursor/logs/*/main.log | grep -i error
```

#### Фильтрация логов

```bash
# Только ошибки
grep -r "error" ~/Library/Application\ Support/Cursor/logs/

# Только MCP ошибки
grep -r "MCP" ~/Library/Application\ Support/Cursor/logs/ | grep -i error

# Только JSON-RPC ошибки
grep -r "Unexpected token" ~/Library/Application\ Support/Cursor/logs/
```

### 6. Структура тестов

#### Тест 1: Доступность логов Cursor
- Проверяет существование директории логов
- Проверяет права доступа
- Подсчитывает количество лог-файлов

#### Тест 2: Анализ логов MCP серверов
- Ищет логи MCP серверов
- Анализирует типичные ошибки
- Выявляет проблемы JSON-RPC

#### Тест 3: Симуляция Output панели
- Проверяет наличие MCP каналов
- Анализирует доступность каналов

#### Тест 4: Проверка credentials_wrapper.py
- Проверяет использование stderr
- Выявляет эмодзи в коде
- Валидирует правильность вывода

### 7. Отчеты и метрики

#### Структура отчета

```json
{
  "timestamp": "2025-09-10T19:30:00Z",
  "summary": {
    "total_tests": 4,
    "passed": 3,
    "warnings": 1,
    "failed": 0,
    "success_rate": "75.0%"
  },
  "errors": {
    "total": 2,
    "critical": 0,
    "high": 1,
    "medium": 1,
    "low": 0
  },
  "recommendations": [
    "Исправьте credentials_wrapper.py - перенаправьте логи в stderr"
  ]
}
```

#### Метрики качества

- **Success Rate**: Процент успешных тестов
- **Error Distribution**: Распределение ошибок по критичности
- **Response Time**: Время выполнения тестов
- **Coverage**: Покрытие различных типов ошибок

### 8. Интеграция с CTO Lead стандартом

#### Соответствие принципам

1. **Автоматизация**: Все проверки автоматизированы
2. **Мониторинг**: Непрерывный мониторинг логов
3. **Документация**: Полная документация процессов
4. **Метрики**: Количественные показатели качества
5. **Алерты**: Автоматические уведомления об ошибках

#### Процессы

1. **Prevention**: Предотвращение ошибок через тесты
2. **Detection**: Раннее обнаружение проблем
3. **Response**: Быстрое реагирование на инциденты
4. **Recovery**: Восстановление после ошибок
5. **Learning**: Обучение на основе инцидентов

### 9. Лучшие практики

#### Для разработчиков

1. **Всегда используйте stderr для логов**
2. **Тестируйте MCP серверы локально**
3. **Проверяйте логи после изменений**
4. **Используйте абсолютные пути в конфигурации**

#### Для DevOps

1. **Настройте мониторинг логов**
2. **Создайте алерты для критических ошибок**
3. **Регулярно проверяйте отчеты**
4. **Обновляйте тесты при изменении архитектуры**

#### Для QA

1. **Запускайте тесты перед релизом**
2. **Анализируйте отчеты тестирования**
3. **Документируйте новые типы ошибок**
4. **Обновляйте тест-кейсы**

### 10. Troubleshooting

#### Частые проблемы

**Проблема**: Логи не найдены
**Решение**: Убедитесь, что Cursor IDE запущен и создал лог-файлы

**Проблема**: Нет прав доступа к логам
**Решение**: Предоставьте права на чтение директории логов

**Проблема**: Тесты не находят ошибки
**Решение**: Проверьте, что MCP серверы настроены и запущены

#### Отладка

1. **Проверьте переменные окружения**
2. **Убедитесь в правильности путей**
3. **Проверьте права доступа к файлам**
4. **Анализируйте детальные логи тестов**

## Заключение

Система мониторинга логов MCP серверов обеспечивает:

- **Раннее обнаружение** проблем в MCP серверах
- **Автоматизированное тестирование** на всех платформах
- **Детальную отчетность** с рекомендациями
- **Интеграцию с CI/CD** для непрерывного мониторинга
- **Соответствие стандартам** качества и надежности

Регулярное использование этой системы поможет поддерживать высокое качество MCP серверов и предотвращать проблемы в production среде.
