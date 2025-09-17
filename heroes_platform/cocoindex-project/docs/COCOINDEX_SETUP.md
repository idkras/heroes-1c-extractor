# CocoIndex Setup Guide

## Обзор

CocoIndex - это ультра-производительный фреймворк для трансформации данных в реальном времени для AI с инкрементальной обработкой.

## Установка и настройка

### 1. Зависимости

```bash
# Основная установка
pip install cocoindex

# С поддержкой embeddings
pip install 'cocoindex[embeddings]'
```

### 2. База данных

CocoIndex требует PostgreSQL с расширением pgvector:

```bash
# Запуск PostgreSQL с pgvector через Docker
docker compose up -d
```

**Конфигурация базы данных:**
- Host: localhost
- Port: 5432
- Database: cocoindex
- User: cocoindex
- Password: cocoindex

### 3. Переменные окружения

Создайте `.env` файл:
```bash
COCOINDEX_DATABASE_URL=postgresql://cocoindex:cocoindex@localhost:5432/cocoindex
```

### 4. Создание flow

Создайте Python файл с определением flow (например, `quickstart.py`):

```python
import cocoindex

@cocoindex.flow_def(name="TextEmbedding")
def text_embedding_flow(flow_builder: cocoindex.FlowBuilder, data_scope: cocoindex.DataScope):
    # Добавляем источник данных
    data_scope["documents"] = flow_builder.add_source(
        cocoindex.sources.LocalFile(path="markdown_files")
    )

    # Добавляем коллектор для данных
    doc_embeddings = data_scope.add_collector()

    # Трансформируем данные
    with data_scope["documents"].row() as doc:
        # Разбиваем документ на чанки
        doc["chunks"] = doc["content"].transform(
            cocoindex.functions.SplitRecursively(),
            language="markdown", chunk_size=2000, chunk_overlap=500
        )

        # Обрабатываем каждый чанк
        with doc["chunks"].row() as chunk:
            # Создаем embeddings
            chunk["embedding"] = chunk["text"].transform(
                cocoindex.functions.SentenceTransformerEmbed(
                    model="sentence-transformers/all-MiniLM-L6-v2"
                )
            )

            # Собираем данные
            doc_embeddings.collect(
                filename=doc["filename"],
                location=chunk["location"],
                text=chunk["text"],
                embedding=chunk["embedding"]
            )

    # Экспортируем в векторный индекс
    doc_embeddings.export(
        "doc_embeddings",
        cocoindex.targets.Postgres(),
        primary_key_fields=["filename", "location"],
        vector_indexes=[
            cocoindex.VectorIndexDef(
                field_name="embedding",
                metric=cocoindex.VectorSimilarityMetric.COSINE_SIMILARITY
            )
        ]
    )
```

### 5. Настройка flow

```bash
# Настройка flow в базе данных
PYTHONPATH=. cocoindex setup quickstart
```

### 6. Обновление индекса

```bash
# Обновление индекса с новыми данными
PYTHONPATH=. cocoindex update quickstart
```

## Основные команды

- `cocoindex ls` - список всех flows
- `cocoindex setup <module>` - настройка flow
- `cocoindex update <module>` - обновление индекса
- `cocoindex show <flow_name>` - показать схему flow
- `cocoindex evaluate <module>` - оценить flow
- `cocoindex server` - запустить HTTP сервер

## Структура проекта

```
project/
├── docker-compose.yml          # PostgreSQL конфигурация
├── .env                        # Переменные окружения
├── quickstart.py              # Определение flow
├── markdown_files/            # Исходные файлы
│   └── test.md
└── COCOINDEX_SETUP.md         # Эта документация
```

## Возможные проблемы

1. **Ошибка подключения к базе данных**: Убедитесь, что PostgreSQL запущен
2. **Отсутствуют зависимости**: Установите `cocoindex[embeddings]`
3. **Проблемы с импортом модуля**: Используйте `PYTHONPATH=.` перед командами

## Тестирование

После настройки вы можете:
1. Добавить файлы в `markdown_files/`
2. Запустить `cocoindex update quickstart`
3. Проверить результаты в базе данных PostgreSQL
