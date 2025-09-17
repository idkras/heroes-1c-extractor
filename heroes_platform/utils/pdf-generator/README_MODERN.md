# 🚀 Современный PDF Генератор

## 📋 Обзор

Современный PDF генератор решает проблемы низкого качества выгрузки, которые были в старых версиях:

### ❌ Проблемы старых генераторов:
- **WeasyPrint ограничения** - плохая поддержка русской типографики
- **Устаревшие CSS** - отсутствие современных принципов дизайна
- **Плохая обработка таблиц** - искажение структуры и читаемости
- **Отсутствие поддержки details блоков** - важные элементы не отображаются
- **Проблемы с переносами** - нечитаемые длинные строки

### ✅ Решения современного генератора:
- **Playwright рендеринг** - качественный браузерный рендеринг
- **Современные CSS принципы** - CSS Grid, Flexbox, CSS Variables
- **Улучшенная типографика** - шрифт Inter, правильные отступы
- **Умная обработка таблиц** - автоматическое улучшение структуры
- **Поддержка details блоков** - корректное отображение всех элементов

## 🛠️ Установка

### 1. Установка зависимостей
```bash
cd "[utils] pdf generator"
pip install -r requirements_modern.txt
```

### 2. Установка Playwright браузеров
```bash
playwright install chromium
```

## 🚀 Использование

### Базовое использование
```python
from generators.pdf_generator_modern import convert_md_to_pdf_modern_sync

# Синхронная версия
result = convert_md_to_pdf_modern_sync(
    md_file_path="input.md",
    output_pdf_path="output.pdf"
)

if result["success"]:
    print(f"PDF создан: {result['output_path']}")
else:
    print(f"Ошибка: {result['error']}")
```

### Асинхронное использование
```python
import asyncio
from generators.pdf_generator_modern import convert_md_to_pdf_modern

async def create_pdf():
    result = await convert_md_to_pdf_modern(
        md_file_path="input.md",
        output_pdf_path="output.pdf"
    )
    return result

# Запуск
result = asyncio.run(create_pdf())
```

### Программное использование
```python
from generators.pdf_generator_modern import ModernPDFGenerator

generator = ModernPDFGenerator()
result = await generator.convert_md_to_pdf("input.md", "output.pdf")
```

## 📊 Тестирование

### Запуск тестов
```bash
# Запуск всех тестов
python -m pytest tests/ -v

# Запуск конкретного теста
python -m pytest tests/test_modern_pdf_generator.py::TestModernPDFGenerator::test_preprocess_markdown -v

# Запуск тестов русской типографики
python -m pytest tests/test_modern_pdf_generator.py::TestRussianTypography -v
```

### Тестирование на реальном файле
```bash
python test_modern_generator.py
```

## 🎨 Особенности

### 1. Предобработка Markdown
- ✅ Исправление неправильных разделителей таблиц
- ✅ Удаление лишних пробелов
- ✅ Исправление пробелов в номерах ФЗ
- ✅ Автоматическое улучшение структуры таблиц

### 2. Постобработка HTML
- ✅ Замена details блоков на стилизованные div'ы
- ✅ Добавление CSS классов для таблиц
- ✅ Улучшение блоков кода
- ✅ Оптимизация для печати

### 3. Современные CSS стили
- ✅ CSS Variables для консистентности
- ✅ Flexbox и Grid для макета
- ✅ Адаптивный дизайн
- ✅ Высокий контраст для читаемости

### 4. Типографика
- ✅ Шрифт Inter (Google Fonts)
- ✅ Оптимальная мера строки (680px)
- ✅ Правильные отступы (модульная сетка 8px)
- ✅ Автоматические переносы

## 📁 Структура файлов

```
[utils] pdf generator/
├── generators/
│   ├── pdf_generator_modern.py          # 🆕 Современный генератор
│   ├── generate_pdf_final.py            # Старый генератор
│   └── generate_pdf_playwright.py       # Старый Playwright генератор
├── tests/
│   └── test_modern_pdf_generator.py     # 🆕 Тесты современного генератора
├── requirements_modern.txt               # 🆕 Зависимости для современного генератора
├── test_modern_generator.py              # 🆕 Скрипт тестирования
└── README_MODERN.md                      # 🆕 Эта документация
```

## 🔧 Конфигурация

### Настройка шрифтов
```python
# В _create_full_html() можно изменить шрифт
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
```

### Настройка цветов
```python
:root {
    --primary-color: #2563eb;      # Основной цвет
    --text-primary: #1f2937;       # Основной текст
    --text-secondary: #6b7280;     # Вторичный текст
    --border-color: #e5e7eb;       # Цвет границ
    --background-light: #f9fafb;   # Светлый фон
    --code-background: #f3f4f6;   # Фон кода
}
```

### Настройка размеров
```python
:root {
    --font-size-base: 16px;        # Базовый размер шрифта
    --line-height-base: 1.6;       # Базовая высота строки
    --spacing-unit: 8px;           # Базовый отступ
}
```

## 📈 Производительность

### Время генерации
- **Маленькие файлы (< 100KB)**: 2-5 секунд
- **Средние файлы (100KB-1MB)**: 5-15 секунд
- **Большие файлы (> 1MB)**: 15-60 секунд

### Память
- **Минимальная**: 50MB
- **Рекомендуемая**: 200MB
- **Для больших файлов**: 500MB+

## 🐛 Отладка

### Частые проблемы

#### 1. Playwright не установлен
```bash
# Решение
pip install playwright
playwright install chromium
```

#### 2. Ошибки с шрифтами
```python
# В _create_full_html() заменить на системные шрифты
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
```

#### 3. Проблемы с памятью
```python
# В _generate_pdf_with_playwright() добавить
args=[
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--no-zygote',
    '--single-process'
]
```

### Логирование
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# В генераторе
logger.debug(f"Обрабатываю файл: {md_file_path}")
```

## 🔄 Миграция со старых генераторов

### Замена в коде
```python
# Было
from generators.generate_pdf_final import convert_md_to_pdf_final
result = convert_md_to_pdf_final("input.md", "output.pdf")

# Стало
from generators.pdf_generator_modern import convert_md_to_pdf_modern_sync
result = convert_md_to_pdf_modern_sync("input.md", "output.pdf")
```

### Обновление requirements.txt
```bash
# Удалить старые зависимости
pip uninstall weasyprint

# Установить новые
pip install -r requirements_modern.txt
```

## 📊 Сравнение качества

| Аспект | Старый генератор | Современный генератор |
|--------|------------------|----------------------|
| **Русская типографика** | ❌ Плохо | ✅ Отлично |
| **Таблицы** | ❌ Искажения | ✅ Читаемо |
| **Details блоки** | ❌ Не отображаются | ✅ Корректно |
| **Шрифты** | ❌ Системные | ✅ Inter + системные |
| **Цвета** | ❌ Базовые | ✅ Современная палитра |
| **Адаптивность** | ❌ Нет | ✅ Да |
| **Производительность** | ⚠️ Средне | ✅ Высокая |

## 🎯 Планы развития

### Версия 2.0
- [ ] Поддержка LaTeX для математических формул
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
3. Укажите версию Python и зависимостей
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

---

**🎉 Современный PDF генератор - качественная типографика для профессиональных документов!**
