# Тест сложного Markdown → Lexical преобразования

Это тест для проверки преобразования сложного Markdown в Lexical формат с таблицами и картинками.

## Таблица данных

| Платформа | API Версия | Статус | URL |
|-----------|------------|--------|-----|
| Ghost 2025 | v5.0 | ✅ Работает | http://5.75.239.205 |
| Ghost 2022_RU | v2 | ✅ Работает | https://rick.ai/blog/ru |
| WordPress | v2 | ❌ Не тестировался | - |

## Сравнение форматов

| Формат | Преимущества | Недостатки |
|--------|--------------|------------|
| **Lexical** | ✅ Нативный для Ghost v5.0<br>✅ Полный контроль<br>✅ Без потерь | ❌ Сложная структура |
| **Mobiledoc** | ✅ Совместимость v2/v5.0<br>✅ Простая структура | ❌ Устаревший формат |
| **HTML** | ✅ Простота<br>✅ Прямая поддержка | ❌ Возможные искажения |

## Картинки

### Логотип Rick.ai
![Rick.ai Logo](https://rick.ai/content/images/2021/10/rick-ai-logo.png)

### Схема интеграции
![Integration Schema](https://rick.ai/content/images/2021/10/integration-schema.png)

## Код блоки

### JavaScript пример
```javascript
// Ghost API интеграция
const ghostClient = {
    publishPost: async (content) => {
        const response = await fetch('/ghost/api/v5.0/admin/posts/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Ghost ${jwtToken}`
            },
            body: JSON.stringify({
                posts: [{
                    title: content.title,
                    lexical: content.lexical,
                    status: 'published'
                }]
            })
        });
        return response.json();
    }
};
```

### Python пример
```python
# Lexical конвертер
def markdown_to_lexical(markdown_content):
    """Преобразует Markdown в Lexical JSON"""
    lexical_structure = {
        "root": {
            "children": [
                {
                    "type": "paragraph",
                    "children": [
                        {
                            "type": "text",
                            "text": markdown_content
                        }
                    ]
                }
            ]
        }
    }
    return json.dumps(lexical_structure)
```

## Списки

### Маркированный список
- ✅ Lexical формат работает
- ✅ Таблицы поддерживаются
- ✅ Картинки отображаются
- ✅ Код блоки работают
- ❓ Сложные элементы тестируются

### Нумерованный список
1. Создать тестовый пост
2. Проверить таблицы
3. Проверить картинки
4. Проверить код блоки
5. Проанализировать результат

## Цитаты

> **Важно**: Lexical формат является предпочтительным для Ghost v5.0
> 
> Это обеспечивает максимальную совместимость и качество отображения контента.

## Ссылки

- [Ghost Documentation](https://ghost.org/docs/)
- [Lexical Editor](https://lexical.dev/)
- [Rick.ai Blog](https://rick.ai/blog/)

## Заключение

Этот тест поможет определить качество преобразования Markdown → Lexical для сложных элементов:

1. **Таблицы** - должны отображаться корректно
2. **Картинки** - должны загружаться и отображаться
3. **Код блоки** - должны иметь подсветку синтаксиса
4. **Списки** - должны сохранять структуру
5. **Ссылки** - должны быть кликабельными

**Ожидаемый результат**: Все элементы должны отображаться корректно в Ghost v5.0 с Lexical форматом.
