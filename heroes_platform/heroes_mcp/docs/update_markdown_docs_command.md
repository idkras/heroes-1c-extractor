# MCP Command: update_markdown_docs

## 📋 Обзор

**JTBD:** Как разработчик документации, я хочу обновить markdown документы в локальном сервере, показать результат в чат, использовать validate_actual_outcome и опубликовать в GitHub Pages, чтобы обеспечить актуальность документации с автоматической валидацией.

## 🚀 Использование

### Базовое использование:
```python
# Обновить markdown документ без валидации
result = await update_markdown_docs(
    source_file="[rick.ai]/knowledge base/in progress/1. when new lead come/when mobile · appmetric · ajust/vipavenue.ru/vipavenue.adjust_appmetrica.md",
    target_project="rickai-mkdocs"
)
```

### С валидацией:
```python
# Обновить с валидацией результата
result = await update_markdown_docs(
    source_file="[rick.ai]/knowledge base/in progress/1. when new lead come/when mobile · appmetric · ajust/vipavenue.ru/vipavenue.adjust_appmetrica.md",
    target_project="rickai-mkdocs",
    validate_url="https://idkras.github.io/rickai-docs/technical/vipavenue.adjust_appmetrica/",
    publish_to_github=False,
    show_preview=True
)
```

### С публикацией в GitHub:
```python
# Обновить и опубликовать в GitHub Pages
result = await update_markdown_docs(
    source_file="[rick.ai]/knowledge base/in progress/1. when new lead come/when mobile · appmetric · ajust/vipavenue.ru/vipavenue.adjust_appmetrica.md",
    target_project="rickai-mkdocs",
    validate_url="https://idkras.github.io/rickai-docs/technical/vipavenue.adjust_appmetrica/",
    publish_to_github=True,
    show_preview=True
)
```

## 📝 Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `source_file` | str | ✅ | Путь к исходному markdown файлу |
| `target_project` | str | ❌ | Название проекта документации (по умолчанию "rickai-mkdocs") |
| `validate_url` | str | ❌ | URL для валидации после обновления |
| `publish_to_github` | bool | ❌ | Публиковать в GitHub Pages (по умолчанию False) |
| `show_preview` | bool | ❌ | Показать превью результата (по умолчанию True) |

## 🔄 Процесс выполнения

### Шаг 1: Создание символической ссылки
- Проверяет существование исходного файла
- Создает символическую ссылку в target_project/docs/
- Автоматически определяет подкаталог (technical/guides/clients)

### Шаг 2: Сборка документации
- Запускает `make_mkdoc` для сборки MkDocs
- Очищает предыдущую сборку если clean=True
- Проверяет успешность сборки

### Шаг 3: Валидация результата (опционально)
- Вызывает `validate_actual_outcome` с указанным URL
- Создает скриншот для визуальной валидации
- Анализирует качество документации

### Шаг 4: Публикация в GitHub (опционально)
- Добавляет изменения в git
- Создает коммит с описанием изменений
- Пушит изменения в репозиторий

## 📊 Возвращаемый результат

```json
{
  "success": true,
  "source_file": "/path/to/source.md",
  "target_file": "/path/to/target.md",
  "target_project": "/path/to/project",
  "jtbd_scenario": {
    "when": "Разработчик обновляет markdown документ",
    "role": "Technical Writer / Developer",
    "wants": "автоматически обновить документацию с валидацией",
    "so_that": "обеспечить актуальность и качество документации",
    "sees": "результат обновления с evidence и возможностью публикации",
    "injection_point": "момент изменения markdown файла - сразу обновить документацию"
  },
  "steps": [
    {
      "step": "create_symlink",
      "status": "success",
      "source": "/path/to/source.md",
      "target": "/path/to/target.md",
      "relative_path": "../../source.md",
      "message": "Symbolic link created successfully"
    },
    {
      "step": "build_documentation",
      "status": "success",
      "result": {...},
      "message": "Documentation built successfully"
    }
  ],
  "validation_result": {...},
  "publish_result": {...},
  "evidence_links": {
    "source_file": "/path/to/source.md",
    "target_file": "/path/to/target.md",
    "validation_url": "https://example.com",
    "screenshot_command": "read_cleanshot https://example.com",
    "validation_command": "validate_output_artefact /path/to/target.md"
  },
  "next_actions": [
    "1. Проверить результат в браузере",
    "2. Валидировать качество документации",
    "3. Исправить найденные проблемы",
    "4. Опубликовать в GitHub Pages если нужно"
  ]
}
```

## 🎯 JTBD Сценарии

### Для разработчика документации:
- **Когда:** После обновления markdown файла
- **Роль:** Technical Writer
- **Хочет:** автоматически обновить документацию
- **Чтобы:** обеспечить актуальность
- **Видит:** результат с валидацией и evidence

### Для менеджера проекта:
- **Когда:** При получении обновленной документации
- **Роль:** Project Manager
- **Хочет:** убедиться в качестве результата
- **Чтобы:** принять решение о публикации
- **Видит:** скриншот и анализ качества

## 🔧 Интеграция с другими командами

### Использует:
- `make_mkdoc` - для сборки документации
- `validate_actual_outcome` - для валидации результата
- `read_cleanshot` - для создания скриншотов
- `validate_output_artefact` - для валидации артефактов

### Связанные команды:
- `execute_output_gap_workflow` - для анализа gap между ожидаемым и фактическим
- `cross_check_result` - для независимой проверки
- `generate_evidence_links` - для создания ссылок на evidence

## 🚨 Обработка ошибок

### Типичные ошибки:
- **Файл не найден:** Проверяет существование исходного файла
- **Неправильный формат:** Проверяет расширение .md
- **Ошибка сборки:** Логирует ошибки MkDocs
- **Ошибка валидации:** Создает fallback результат
- **Ошибка публикации:** Логирует git ошибки

### Fallback механизмы:
- При недоступности Playwright создает placeholder скриншот
- При ошибке сборки возвращает детальную информацию об ошибке
- При ошибке git сохраняет изменения локально

## 📈 Метрики качества

### Автоматические проверки:
- ✅ Существование исходного файла
- ✅ Корректность символической ссылки
- ✅ Успешность сборки MkDocs
- ✅ Доступность валидационного URL
- ✅ Качество скриншота

### Ручные проверки:
- 📝 Читаемость документации
- 🎨 Визуальное качество
- 🔗 Работоспособность ссылок
- 📱 Адаптивность дизайна

## 🔗 Полезные ссылки

- [MkDocs Documentation](https://www.mkdocs.org/)
- [GitHub Pages](https://pages.github.com/)
- [validate_actual_outcome Command](./validate_actual_outcome.md)
- [make_mkdoc Command](./make_mkdoc_command.md)
