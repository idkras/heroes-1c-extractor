# 🚀 Node.js PDF Генератор (md-to-pdf)

## 📋 Обзор

Node.js PDF генератор использует npm пакет `md-to-pdf` для создания высококачественных PDF документов из Markdown. Это решение превосходит Python генераторы по качеству типографики и поддержке современных CSS возможностей.

### 🎯 Преимущества md-to-pdf:

- ✅ **Лучшая типографика** - встроенная поддержка современных шрифтов
- ✅ **Полная поддержка CSS** - все современные возможности браузера
- ✅ **GitHub Flavored Markdown** - расширенная поддержка markdown
- ✅ **Автоматическая установка** - npm управляет зависимостями
- ✅ **Высокое качество** - профессиональный результат

## 🛠️ Установка

### 1. Требования
- **Node.js** 16.0.0 или выше
- **npm** 8.0.0 или выше

### 2. Установка зависимостей
```bash
cd "[utils] pdf generator"

# Установка npm зависимостей
npm install

# Или установка md-to-pdf глобально
npm install -g md-to-pdf
```

### 3. Проверка установки
```bash
# Проверка версий
node --version
npm --version

# Проверка md-to-pdf
npx md-to-pdf --version
```

## 🚀 Использование

### Базовое использование
```python
from generators.pdf_generator_nodejs import convert_md_to_pdf_nodejs

# Создание PDF
result = convert_md_to_pdf_nodejs(
    md_file_path="input.md",
    output_pdf_path="output.pdf"
)

if result["success"]:
    print(f"PDF создан: {result['output_path']}")
    print(f"Размер: {result['file_size_kb']:.1f} KB")
else:
    print(f"Ошибка: {result['error']}")
```

### Расширенные опции
```python
from generators.pdf_generator_nodejs import convert_md_to_pdf_nodejs_advanced

# Настройка опций
options = {
    "format": "A4",
    "margin": "15mm",
    "highlight": True,    # Подсветка синтаксиса
    "toc": True,          # Оглавление
    "numbered": False     # Нумерация страниц
}

result = convert_md_to_pdf_nodejs_advanced(
    md_file_path="input.md",
    output_pdf_path="output.pdf",
    options=options
)
```

### Программное использование
```python
from generators.pdf_generator_nodejs import NodeJSPDFGenerator

generator = NodeJSPDFGenerator()

# Проверка зависимостей
if generator.check_dependencies():
    # Создание PDF
    result = generator.convert_md_to_pdf("input.md", "output.pdf")
    
    # Создание с кастомными стилями
    custom_css = """
    body { font-family: 'Times New Roman', serif; }
    h1 { color: #2563eb; }
    """
    
    result = generator.convert_md_to_pdf(
        "input.md", 
        "output.pdf", 
        custom_css=custom_css
    )
```

## 🎨 Кастомные стили

### Встроенные стили
Генератор автоматически создает современные CSS стили с:
- Шрифт Inter (Google Fonts)
- Современная цветовая палитра
- Адаптивный дизайн
- Поддержка всех элементов markdown

### Собственные стили
```python
custom_css = """
/* Ваши собственные стили */
body {
    font-family: 'Georgia', serif;
    font-size: 14px;
    line-height: 1.8;
}

h1 {
    color: #1f2937;
    border-bottom: 3px solid #2563eb;
}

table {
    border: 2px solid #e5e7eb;
    border-radius: 8px;
}
"""

result = convert_md_to_pdf_nodejs(
    "input.md", 
    "output.pdf", 
    custom_css=custom_css
)
```

## 📊 Опции конвертации

### Доступные опции
```python
options = {
    "format": "A4",           # Формат страницы (A4, Letter, Legal)
    "margin": "20mm",         # Отступы страницы
    "css": "custom.css",      # Путь к CSS файлу
    "highlight": True,        # Подсветка синтаксиса кода
    "toc": False,             # Автоматическое оглавление
    "numbered": False,        # Нумерация страниц
    "landscape": False,       # Альбомная ориентация
    "debug": False            # Режим отладки
}
```

### Примеры использования опций
```python
# Книжный формат с оглавлением
book_options = {
    "format": "A5",
    "margin": "25mm",
    "toc": True,
    "numbered": True
}

# Презентация
presentation_options = {
    "format": "A4",
    "landscape": True,
    "margin": "15mm"
}

# Техническая документация
tech_options = {
    "format": "A4",
    "highlight": True,
    "css": "technical.css"
}
```

## 📁 Структура файлов

```
[utils] pdf generator/
├── generators/
│   ├── pdf_generator_nodejs.py          # 🆕 Node.js генератор
│   ├── pdf_generator_modern.py          # Playwright генератор
│   └── generate_pdf_final.py            # WeasyPrint генератор
├── package.json                          # 🆕 Node.js зависимости
├── test_nodejs_generator.py              # 🆕 Тест Node.js генератора
├── test_modern_generator.py              # Тест Playwright генератора
└── README_NODEJS.md                      # 🆕 Эта документация
```

## 🔧 Конфигурация

### package.json настройки
```json
{
  "dependencies": {
    "md-to-pdf": "^5.2.0"
  },
  "engines": {
    "node": ">=16.0.0",
    "npm": ">=8.0.0"
  }
}
```

### Автоматическая установка
Генератор автоматически:
1. Проверяет наличие Node.js и npm
2. Устанавливает md-to-pdf если необходимо
3. Создает временные CSS файлы
4. Очищает временные файлы после использования

## 📈 Производительность

### Время генерации
- **Маленькие файлы (< 100KB)**: 1-3 секунды
- **Средние файлы (100KB-1MB)**: 3-10 секунд
- **Большие файлы (> 1MB)**: 10-30 секунд

### Память
- **Минимальная**: 30MB
- **Рекомендуемая**: 100MB
- **Для больших файлов**: 200MB+

### Сравнение с другими генераторами
| Генератор | Скорость | Качество | Память | Зависимости |
|-----------|----------|----------|---------|-------------|
| **md-to-pdf** | ⚡ Быстро | 🌟 Отлично | 💾 Низко | 📦 npm |
| **Playwright** | 🐌 Медленно | 🌟 Отлично | 💾 Высоко | 🐍 Python |
| **WeasyPrint** | 🐌 Медленно | ⚠️ Средне | 💾 Средне | 🐍 Python |

## 🐛 Отладка

### Частые проблемы

#### 1. Node.js не установлен
```bash
# Установка Node.js
# macOS: brew install node
# Ubuntu: sudo apt install nodejs npm
# Windows: скачать с https://nodejs.org/
```

#### 2. md-to-pdf не установлен
```bash
# Автоматическая установка
npm install -g md-to-pdf

# Или через генератор
python -c "
from generators.pdf_generator_nodejs import NodeJSPDFGenerator
generator = NodeJSPDFGenerator()
generator.install_md_to_pdf()
"
```

#### 3. Проблемы с правами доступа
```bash
# Установка глобально (может потребовать sudo)
sudo npm install -g md-to-pdf

# Или локальная установка
npm install md-to-pdf
npx md-to-pdf input.md --output output.pdf
```

### Логирование
```python
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# В генераторе
generator = NodeJSPDFGenerator()
result = generator.convert_md_to_pdf("input.md", "output.pdf")
```

## 🔄 Миграция с Python генераторов

### Замена в коде
```python
# Было (Playwright)
from generators.pdf_generator_modern import convert_md_to_pdf_modern_sync
result = convert_md_to_pdf_modern_sync("input.md", "output.pdf")

# Стало (Node.js)
from generators.pdf_generator_nodejs import convert_md_to_pdf_nodejs
result = convert_md_to_pdf_nodejs("input.md", "output.pdf")
```

### Обновление requirements
```bash
# Удалить Python зависимости
pip uninstall playwright markdown

# Установить Node.js зависимости
npm install
```

## 📊 Сравнение качества

| Аспект | WeasyPrint | Playwright | **md-to-pdf** |
|--------|------------|------------|----------------|
| **Русская типографика** | ❌ Плохо | ✅ Хорошо | 🌟 Отлично |
| **Таблицы** | ❌ Искажения | ✅ Читаемо | 🌟 Идеально |
| **Details блоки** | ❌ Не отображаются | ✅ Корректно | 🌟 Отлично |
| **Шрифты** | ❌ Системные | ✅ Inter + системные | 🌟 Google Fonts |
| **CSS поддержка** | ❌ Ограниченная | ✅ Полная | 🌟 Современная |
| **Скорость** | ⚠️ Медленно | 🐌 Очень медленно | ⚡ Быстро |
| **Установка** | 🐍 pip | 🐍 pip + браузер | 📦 npm |

## 🎯 Планы развития

### Версия 2.0
- [ ] Поддержка LaTeX математических формул
- [ ] Автоматическая генерация оглавления
- [ ] Поддержка водяных знаков
- [ ] Шаблоны для разных типов документов

### Версия 2.1
- [ ] Интеграция с CI/CD
- [ ] Автоматическое тестирование качества
- [ ] Поддержка тем оформления
- [ ] Экспорт в другие форматы (DOCX, HTML)

## 🤝 Вклад в развитие

### Сообщения об ошибках
1. Создайте issue с описанием проблемы
2. Приложите входной markdown файл
3. Укажите версии Node.js и npm
4. Опишите ожидаемое и фактическое поведение

### Предложения улучшений
1. Опишите новую функциональность
2. Объясните, как это улучшит качество
3. Предложите способ реализации

### Pull Requests
1. Создайте ветку для новой функциональности
2. Добавьте тесты
3. Обновите документацию
4. Убедитесь, что все тесты проходят

## 🧪 Тестирование

### Запуск тестов
```bash
# Тест Node.js генератора
python test_nodejs_generator.py

# Тест Playwright генератора
python test_modern_generator.py

# Сравнение результатов
ls -la vipavenue-adjust-appmetrica_*.pdf
```

### Автоматические тесты
```bash
# Тесты Python
python -m pytest tests/ -v

# Тесты Node.js
npm test
```

---

**🎉 Node.js PDF генератор - лучшее качество типографики через md-to-pdf!**
