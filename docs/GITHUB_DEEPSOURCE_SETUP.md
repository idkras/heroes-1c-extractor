# GitHub + DeepSource Integration Setup

## 🚀 Пошаговая настройка

### Шаг 1: Авторизация в DeepSource

1. Перейти на [deepsource.io](https://deepsource.io)
2. Нажать "Sign in with GitHub"
3. Разрешить доступ к репозиториям

### Шаг 2: Установка GitHub App

1. В DeepSource Dashboard → "Add Repository"
2. Выбрать организацию/репозиторий `heroes-1c-extractor`
3. Нажать "Install DeepSource"
4. Подтвердить установку в GitHub

### Шаг 3: Настройка Branch Protection

1. **GitHub → Repository → Settings → Branches**
2. Нажать "Add rule" для ветки `main`
3. Включить опции:
   - ✅ "Require status checks to pass before merging"
   - ✅ "Require branches to be up to date before merging"
4. В "Status checks" добавить:
   - `DeepSource`
5. Сохранить изменения

### Шаг 4: Активация анализа

1. Сделать коммит с `.deepsource.toml`:
   ```bash
   git add .deepsource.toml
   git commit -m "feat: add DeepSource configuration"
   git push origin main
   ```

2. Проверить в GitHub:
   - Перейти в "Actions" или "Checks"
   - Должен появиться статус "DeepSource"

### Шаг 5: Проверка работы

1. Создать тестовый PR:
   ```bash
   git checkout -b test-deepsource
   # Внести изменения в код
   git add .
   git commit -m "test: trigger DeepSource analysis"
   git push origin test-deepsource
   ```

2. Создать Pull Request в GitHub
3. Проверить, что DeepSource оставил комментарии

## 🔧 Troubleshooting

### Если DeepSource не запускается:

1. **Проверить файл `.deepsource.toml`:**
   ```bash
   cat .deepsource.toml
   ```

2. **Проверить GitHub App:**
   - GitHub → Settings → Applications → DeepSource
   - Убедиться, что доступ к репозиторию разрешен

3. **Проверить Branch Protection:**
   - GitHub → Settings → Branches
   - Убедиться, что "DeepSource" в списке обязательных проверок

### Если статус не появляется:

1. **Переустановить GitHub App:**
   - GitHub → Settings → Applications → DeepSource
   - "Uninstall" → "Install" заново

2. **Проверить права доступа:**
   - DeepSource должен иметь доступ к репозиторию
   - Проверить в DeepSource Dashboard

### Если проверки не проходят:

1. **Локальная проверка:**
   ```bash
   make deepsource-local
   ```

2. **Исправить ошибки:**
   - Использовать Cursor AI Agent
   - Запустить `make auto-fix`

## 📊 Ожидаемые результаты

После настройки вы должны увидеть:

1. **В GitHub PR:**
   - Статус "DeepSource" в списке проверок
   - Комментарии с замечаниями по коду
   - Блокировка слияния при критичных проблемах

2. **В DeepSource Dashboard:**
   - Отчеты по качеству кода
   - Метрики покрытия тестами
   - Тренды улучшения качества

3. **Локально:**
   ```bash
   make pre-commit  # Должно проходить без ошибок
   make deepsource-local  # Аналог DeepSource проверок
   ```

## 🎯 Следующие шаги

1. **Настроить команду:**
   - Показать документацию `docs/DEEPSOURCE_CURSOR_INTEGRATION.md`
   - Обучить использованию Cursor AI Agent

2. **Мониторинг:**
   - Проверять отчеты DeepSource еженедельно
   - Анализировать тренды качества кода

3. **Оптимизация:**
   - Настраивать исключения по мере необходимости
   - Добавлять новые правила постепенно

## 🆘 Поддержка

При проблемах:
1. Проверить логи в GitHub Actions
2. Обратиться к DeepSource Support
3. Использовать Cursor AI Agent для диагностики
