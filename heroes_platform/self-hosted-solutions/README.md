# Self-Hosted Solutions

Коллекция self-hosted решений для локального развертывания популярных платформ.

## 📚 Доступные решения

### 1. [Outline](./outline/) - База знаний для команд

**Описание:** Быстрая, совместная база знаний для вашей команды, построенная с использованием React и Node.js.

**Особенности:**
- ✨ Современный интерфейс
- 🔍 Мощный поиск
- 👥 Совместное редактирование
- 🔐 Множественные методы аутентификации
- 📱 Адаптивный дизайн

**Технологии:** React, Node.js, PostgreSQL, Redis

**Порт:** 3000

**Ссылки:**
- [Документация](./outline/README.md)
- [Официальный сайт](https://www.getoutline.com/)
- [GitHub](https://github.com/outline/outline)

---

### 2. [BookStack](./bookstack/) - Платформа документации

**Описание:** Платформа для создания документации/wiki контента, построенная на PHP и Laravel.

**Особенности:**
- 📖 Иерархическая структура (Книги → Главы → Страницы)
- 🎨 Простой WYSIWYG редактор
- 🔍 Встроенный поиск
- 📊 Управление ролями и правами
- 🌙 Темная и светлая темы

**Технологии:** PHP, Laravel, MySQL

**Порт:** 6875

**Ссылки:**
- [Документация](./bookstack/README.md)
- [Официальный сайт](https://www.bookstackapp.com/)
- [GitHub](https://github.com/BookStackApp/BookStack)

## 🚀 Быстрый старт

### Предварительные требования

- Docker и Docker Compose
- Минимум 2GB RAM (для обеих платформ)
- 15GB свободного места на диске

### Установка

1. **Выберите платформу:**
   ```bash
   cd heroes-platform/self-hosted-solutions/outline    # или bookstack
   ```

2. **Настройте переменные окружения:**
   ```bash
   cp env.example .env
   nano .env  # отредактируйте необходимые переменные
   ```

3. **Запустите:**
   ```bash
   docker-compose up -d
   ```

4. **Откройте в браузере:**
   - Outline: http://localhost:3000
   - BookStack: http://localhost:6875

## 🔧 Управление

### Общие команды

```bash
# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Просмотр логов
docker-compose logs -f

# Обновление
docker-compose pull
docker-compose up -d

# Статус
docker-compose ps
```

### Резервное копирование

```bash
# Создание бэкапа
docker-compose exec postgres pg_dump -U outline outline > outline_backup.sql
docker-compose exec mysql mysqldump -u bookstack -p bookstack > bookstack_backup.sql

# Восстановление
docker-compose exec -T postgres psql -U outline outline < outline_backup.sql
docker-compose exec -T mysql mysql -u bookstack -p bookstack < bookstack_backup.sql
```

## 🔐 Безопасность

### Рекомендации для продакшена

1. **Измените пароли по умолчанию**
2. **Настройте HTTPS** (через reverse proxy)
3. **Ограничьте доступ к портам** (используйте firewall)
4. **Регулярно обновляйте** образы Docker
5. **Настройте мониторинг** и логирование

### Reverse Proxy (Nginx)

Пример конфигурации для Nginx:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:3000;  # или 6875 для BookStack
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📊 Мониторинг

### Docker Stats

```bash
# Мониторинг ресурсов
docker stats

# Просмотр использования диска
docker system df
```

### Логирование

```bash
# Просмотр логов приложения
docker-compose logs -f outline    # или bookstack

# Просмотр логов базы данных
docker-compose logs -f postgres   # или mysql
```

## 🛠️ Устранение неполадок

### Общие проблемы

1. **Порт уже занят:**
   ```bash
   # Измените порт в docker-compose.yml
   ports:
     - "3001:3000"  # вместо 3000:3000
   ```

2. **Проблемы с правами доступа:**
   ```bash
   # Исправьте права на файлы
   sudo chown -R $USER:$USER .
   ```

3. **Недостаточно памяти:**
   ```bash
   # Увеличьте swap или RAM
   # Остановите неиспользуемые контейнеры
   docker system prune
   ```

### Получение помощи

- [Outline Issues](https://github.com/outline/outline/issues)
- [BookStack Issues](https://github.com/BookStackApp/BookStack/issues)
- [Docker Documentation](https://docs.docker.com/)

## 📝 Лицензии

- **Outline:** MIT License
- **BookStack:** MIT License

## 🤝 Вклад в проект

Если вы нашли ошибки или хотите добавить новые платформы:

1. Создайте issue с описанием проблемы
2. Предложите pull request с исправлениями
3. Обновите документацию при необходимости

---

**Примечание:** Эти решения предназначены для локального использования. Для продакшена рекомендуется дополнительная настройка безопасности и мониторинга.
