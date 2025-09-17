# 🏠 Self-Hosted Solutions

Готовые к использованию self-hosted решения для локального развертывания популярных платформ.

## 📚 Доступные решения

### Outline - База знаний для команд
- **URL:** http://localhost:3000
- **Технологии:** React, Node.js, PostgreSQL, Redis
- **Описание:** Современная база знаний с совместным редактированием

### BookStack - Платформа документации  
- **URL:** http://localhost:6875
- **Технологии:** PHP, Laravel, MySQL
- **Описание:** Иерархическая система документации

## 🚀 Быстрый запуск

```bash
# Перейдите в директорию
cd self-hosted-solutions

# Запустите все сервисы одной командой
make start
```

## 📋 Что произойдет автоматически

✅ Проверка Docker  
✅ Создание .env файлов  
✅ Запуск Outline на порту 3000  
✅ Запуск BookStack на порту 6875  
✅ Проверка статуса всех сервисов  

## 🛠️ Управление

```bash
make start      # Запустить все
make stop       # Остановить все  
make status     # Показать статус
make logs       # Показать логи
make backup     # Создать резервную копию
make update     # Обновить образы
```

## 📖 Подробная документация

- [Полная документация](./self-hosted-solutions/README.md)
- [Быстрый старт](./self-hosted-solutions/QUICK_START.md)
- [Outline документация](./self-hosted-solutions/outline/README.md)
- [BookStack документация](./self-hosted-solutions/bookstack/README.md)

## 🔐 Безопасность

**ВАЖНО:** Перед использованием в продакшене отредактируйте `.env` файлы и измените пароли по умолчанию.

---

**Готово к использованию!** 🎉
