# BookStack - Self-Hosted Installation

[BookStack](https://www.bookstackapp.com/) - это платформа для создания документации/wiki контента, построенная на PHP и Laravel.

## 🚀 Быстрый старт

### 1. Подготовка

```bash
# Клонируйте репозиторий или создайте директорию
mkdir bookstack-self-hosted
cd bookstack-self-hosted

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
- `APP_KEY` - ключ приложения (минимум 32 символа)
- `APP_URL` - URL вашего сервера

### 3. Запуск

```bash
# Запустите сервисы
docker-compose up -d

# Проверьте статус
docker-compose ps
```

### 4. Первоначальная настройка

1. Откройте браузер и перейдите по адресу: `http://localhost:6875`
2. Создайте первого администратора
3. Настройте аутентификацию и другие параметры

## 📋 Требования

- Docker и Docker Compose
- Минимум 1GB RAM
- 5GB свободного места на диске

## 🔧 Конфигурация

### База данных
MySQL 8.0 автоматически настраивается в контейнере.

### Файловое хранилище
По умолчанию используется локальное хранилище. Файлы сохраняются в Docker volumes:
- `bookstack_uploads` - загруженные файлы
- `bookstack_storage` - системные файлы

## 🔐 Аутентификация

BookStack поддерживает несколько методов аутентификации:

### Локальная аутентификация
По умолчанию включена. Пользователи создаются администратором.

### LDAP
Для интеграции с Active Directory или OpenLDAP:

```env
LDAP_SERVER=ldap://your-ldap-server
LDAP_BASE_DN=dc=example,dc=com
LDAP_USERNAME=cn=admin,dc=example,dc=com
LDAP_PASSWORD=your-ldap-password
LDAP_USER_FILTER=(&(uid=%user))
LDAP_VERSION=3
```

### SAML2
Для интеграции с SAML провайдерами:

```env
SAML2_ENABLED=true
SAML2_NAME=your-saml-provider
SAML2_IDP_ENTITY_ID=your-idp-entity-id
SAML2_IDP_SSO_URL=your-idp-sso-url
SAML2_IDP_SLO_URL=your-idp-slo-url
SAML2_IDP_x509=your-idp-x509-certificate
SAML2_SP_x509=your-sp-x509-certificate
SAML2_SP_PRIVATE_KEY=your-sp-private-key
```

## 📧 Email настройка

Для отправки уведомлений настройте SMTP:

```env
MAIL_DRIVER=smtp
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_ENCRYPTION=tls
MAIL_FROM_ADDRESS=noreply@yourdomain.com
MAIL_FROM_NAME=BookStack
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
docker-compose logs -f bookstack

# Статус сервисов
docker-compose ps

# Использование ресурсов
docker stats
```

## 🛠️ Устранение неполадок

### Проблемы с базой данных
```bash
# Проверьте логи MySQL
docker-compose logs mysql

# Подключитесь к базе данных
docker-compose exec mysql mysql -u bookstack -p bookstack
```

### Проблемы с правами доступа
```bash
# Исправьте права доступа к файлам
docker-compose exec bookstack chown -R www-data:www-data /var/www/bookstack
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

## 📚 Структура контента

BookStack организует контент в иерархическую структуру:

- **Books** - книги (основные контейнеры)
- **Chapters** - главы (внутри книг)
- **Pages** - страницы (внутри глав)

## 🔗 Полезные ссылки

- [Официальная документация](https://www.bookstackapp.com/docs/)
- [GitHub репозиторий](https://github.com/BookStackApp/BookStack)
- [Демо версия](https://demo.bookstackapp.com/)

## 📝 Лицензия

BookStack распространяется под лицензией MIT.
