# Outline - Self-Hosted Installation

[Outline](https://www.getoutline.com/) - это быстрая, совместная база знаний для вашей команды, построенная с использованием React и Node.js.

## 🚀 Быстрый старт

### 1. Подготовка

```bash
# Клонируйте репозиторий или создайте директорию
mkdir outline-self-hosted
cd outline-self-hosted

# Скопируйте файлы docker-compose.yml и env.example
```

### 2. Настройка переменных окружения

```bash
# Скопируйте пример файла окружения
cp env.example .env

# Отредактируйте .env файл
nano .env
```

**Обязательные переменные:**
- `SECRET_KEY` - секретный ключ (минимум 32 символа)
- `UTILS_SECRET` - утилитарный секрет (минимум 32 символа)
- `URL` - URL вашего сервера

### 3. Запуск

```bash
# Запустите сервисы
docker-compose up -d

# Проверьте статус
docker-compose ps
```

### 4. Первоначальная настройка

1. Откройте браузер и перейдите по адресу: `http://localhost:3000`
2. Создайте первого администратора
3. Настройте аутентификацию (Google, GitHub, Slack)

## 📋 Требования

- Docker и Docker Compose
- Минимум 2GB RAM
- 10GB свободного места на диске

## 🔧 Конфигурация

### База данных
PostgreSQL 15 автоматически настраивается в контейнере.

### Redis
Redis 7 используется для кэширования и сессий.

### Файловое хранилище
По умолчанию используется локальное хранилище. Файлы сохраняются в Docker volume `outline_data`.

## 🔐 Аутентификация

Outline поддерживает несколько методов аутентификации:

### Google OAuth
1. Создайте проект в [Google Cloud Console](https://console.cloud.google.com/)
2. Настройте OAuth 2.0
3. Добавьте `GOOGLE_CLIENT_ID` и `GOOGLE_CLIENT_SECRET` в `.env`

### GitHub OAuth
1. Создайте OAuth App в [GitHub Settings](https://github.com/settings/developers)
2. Добавьте `GITHUB_CLIENT_ID` и `GITHUB_CLIENT_SECRET` в `.env`

### Slack OAuth
1. Создайте Slack App в [Slack API](https://api.slack.com/apps)
2. Добавьте `SLACK_CLIENT_ID` и `SLACK_CLIENT_SECRET` в `.env`

## 📧 Email настройка

Для отправки уведомлений настройте SMTP:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@yourdomain.com
```

## 🔄 Обновление

```bash
# Остановите сервисы
docker-compose down

# Обновите образы
docker-compose pull

# Запустите снова
docker-compose up -d
```

## 📊 Мониторинг

```bash
# Просмотр логов
docker-compose logs -f outline

# Статус сервисов
docker-compose ps

# Использование ресурсов
docker stats
```

## 🛠️ Устранение неполадок

### Проблемы с базой данных
```bash
# Проверьте логи PostgreSQL
docker-compose logs postgres

# Подключитесь к базе данных
docker-compose exec postgres psql -U outline -d outline
```

### Проблемы с Redis
```bash
# Проверьте логи Redis
docker-compose logs redis

# Подключитесь к Redis
docker-compose exec redis redis-cli
```

### Сброс данных
```bash
# Остановите сервисы
docker-compose down

# Удалите volumes (ВНИМАНИЕ: это удалит все данные!)
docker-compose down -v

# Запустите заново
docker-compose up -d
```

## 🔗 Полезные ссылки

- [Официальная документация](https://docs.getoutline.com/)
- [GitHub репозиторий](https://github.com/outline/outline)
- [Демо версия](https://www.getoutline.com/)

## 📝 Лицензия

Outline распространяется под лицензией MIT.
