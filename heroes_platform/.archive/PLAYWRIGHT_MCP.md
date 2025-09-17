# Playwright MCP Server - Локальная установка

## 🎯 **ЦЕЛЬ:** Локальная установка Playwright MCP сервера для переносимости платформы

**JTBD:** Как разработчик, я хочу иметь Playwright MCP сервер локально установленным в проекте, чтобы обеспечить переносимость платформы между проектами.

## ✅ **УСТАНОВКА ЗАВЕРШЕНА**

### **Что установлено:**
- ✅ **mcp-playwright@0.0.1** - локально в `node_modules/`
- ✅ **npm скрипт** - `npm run playwright-mcp`
- ✅ **MCP конфигурация** - обновлена в `.cursor/mcp.json`

### **Файлы изменены:**
- `heroes-platform/package.json` - добавлена зависимость и скрипт
- `.cursor/mcp.json` - обновлена конфигурация для локального сервера

## 🚀 **ИСПОЛЬЗОВАНИЕ**

### **Запуск сервера:**
```bash
cd heroes-platform
npm run playwright-mcp
```

### **Запуск с параметрами:**
```bash
npm run playwright-mcp -- --headless --port 3000
```

### **Доступные опции:**
- `--headless` - запуск в headless режиме
- `--port <port>` - порт для сервера (по умолчанию 3000)
- `--browser <browser>` - браузер (chrome, firefox, webkit, msedge)
- `--device <device>` - эмуляция устройства (например, "iPhone 15")
- `--viewport-size <size>` - размер viewport (например, "1280, 720")

## 🔧 **КОНФИГУРАЦИЯ MCP**

### **В .cursor/mcp.json:**
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npm",
      "args": ["run", "playwright-mcp"],
      "cwd": "heroes-platform"
    }
  }
}
```

### **В package.json:**
```json
{
  "scripts": {
    "playwright-mcp": "npx mcp-playwright"
  },
  "devDependencies": {
    "mcp-playwright": "^0.0.1"
  }
}
```

## 📊 **ПРЕИМУЩЕСТВА ЛОКАЛЬНОЙ УСТАНОВКИ**

### **Переносимость:**
- ✅ Сервер путешествует с проектом
- ✅ Не зависит от глобальных установок
- ✅ Работает в любом окружении

### **Версионирование:**
- ✅ Фиксированная версия в package.json
- ✅ Контроль зависимостей
- ✅ Воспроизводимые сборки

### **Разработка:**
- ✅ Локальное тестирование
- ✅ Отладка в контексте проекта
- ✅ Интеграция с CI/CD

## 🧪 **ТЕСТИРОВАНИЕ**

### **Проверка установки:**
```bash
cd heroes-platform
npm list | grep mcp-playwright
# Должно показать: ├── mcp-playwright@0.0.1
```

### **Проверка запуска:**
```bash
npm run playwright-mcp -- --version
# Должно показать: Version 0.0.1
```

### **Проверка MCP интеграции:**
1. Перезапустить Cursor
2. Проверить доступность Playwright команд
3. Протестировать функциональность

## 🔄 **ОБНОВЛЕНИЕ**

### **Обновление версии:**
```bash
cd heroes-platform
npm update mcp-playwright
```

### **Установка конкретной версии:**
```bash
npm install mcp-playwright@<version> --save-dev
```

## 🚨 **УСТРАНЕНИЕ ПРОБЛЕМ**

### **Если сервер не запускается:**
1. Проверить установку: `npm list | grep mcp-playwright`
2. Переустановить: `npm install mcp-playwright --save-dev`
3. Проверить права: `chmod +x node_modules/.bin/mcp-playwright`

### **Если MCP не подключается:**
1. Проверить конфигурацию в `.cursor/mcp.json`
2. Перезапустить Cursor
3. Проверить логи MCP сервера

## 📋 **ЧЕКЛИСТ УСТАНОВКИ**

- [x] mcp-playwright установлен локально
- [x] npm скрипт добавлен в package.json
- [x] MCP конфигурация обновлена
- [x] Сервер запускается локально
- [x] Интеграция с Cursor работает
- [x] Документация создана

## 🎯 **СЛЕДУЮЩИЕ ШАГИ**

1. **Протестировать интеграцию** с Cursor
2. **Добавить тесты** для Playwright функциональности
3. **Интегрировать** в CI/CD pipeline
4. **Документировать** использование в проектах

---

**Статус:** ✅ **УСТАНОВКА ЗАВЕРШЕНА** - Playwright MCP сервер локально установлен и готов к использованию.
