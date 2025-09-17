# Self-Hosted Solutions Makefile

.PHONY: help install start stop restart status logs clean backup restore outline bookstack

# Цвета для вывода
GREEN = \033[0;32m
BLUE = \033[0;34m
RED = \033[0;31m
YELLOW = \033[1;33m
NC = \033[0m # No Color

help: ## Показать справку
	@echo "$(BLUE)Self-Hosted Solutions - Доступные команды:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'

install: ## Установить и настроить все сервисы
	@echo "$(BLUE)Установка self-hosted решений...$(NC)"
	@./start-all.sh help
	@echo "$(GREEN)Установка завершена!$(NC)"

start: ## Запустить все сервисы
	@echo "$(BLUE)Запуск всех сервисов...$(NC)"
	@./start-all.sh

stop: ## Остановить все сервисы
	@echo "$(BLUE)Остановка всех сервисов...$(NC)"
	@./start-all.sh stop

restart: ## Перезапустить все сервисы
	@echo "$(BLUE)Перезапуск всех сервисов...$(NC)"
	@./start-all.sh restart

status: ## Показать статус сервисов
	@echo "$(BLUE)Статус сервисов:$(NC)"
	@./start-all.sh status

logs: ## Показать логи всех сервисов
	@echo "$(BLUE)Логи сервисов:$(NC)"
	@./start-all.sh logs

outline: ## Запустить только Outline
	@echo "$(BLUE)Запуск Outline...$(NC)"
	@./start-all.sh outline

bookstack: ## Запустить только BookStack
	@echo "$(BLUE)Запуск BookStack...$(NC)"
	@./start-all.sh bookstack

clean: ## Очистить все данные (ВНИМАНИЕ: удалит все данные!)
	@echo "$(RED)ВНИМАНИЕ: Это удалит все данные!$(NC)"
	@read -p "Вы уверены? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo "$(BLUE)Очистка данных...$(NC)"
	@cd outline && docker-compose down -v && cd ..
	@cd bookstack && docker-compose down -v && cd ..
	@echo "$(GREEN)Данные очищены!$(NC)"

backup: ## Создать резервную копию всех данных
	@echo "$(BLUE)Создание резервной копии...$(NC)"
	@mkdir -p backups/$(shell date +%Y%m%d_%H%M%S)
	@cd outline && docker-compose exec -T postgres pg_dump -U outline outline > ../backups/$(shell date +%Y%m%d_%H%M%S)/outline_backup.sql && cd ..
	@cd bookstack && docker-compose exec -T mysql mysqldump -u bookstack -pbookstack bookstack > ../backups/$(shell date +%Y%m%d_%H%M%S)/bookstack_backup.sql && cd ..
	@echo "$(GREEN)Резервная копия создана в backups/$(shell date +%Y%m%d_%H%M%S)/$(NC)"

restore: ## Восстановить данные из резервной копии
	@echo "$(BLUE)Восстановление данных...$(NC)"
	@if [ -z "$(BACKUP_DIR)" ]; then \
		echo "$(RED)Укажите директорию с резервной копией: make restore BACKUP_DIR=backups/YYYYMMDD_HHMMSS$(NC)"; \
		exit 1; \
	fi
	@if [ ! -d "$(BACKUP_DIR)" ]; then \
		echo "$(RED)Директория $(BACKUP_DIR) не найдена$(NC)"; \
		exit 1; \
	fi
	@cd outline && docker-compose exec -T postgres psql -U outline outline < ../$(BACKUP_DIR)/outline_backup.sql && cd ..
	@cd bookstack && docker-compose exec -T mysql mysql -u bookstack -pbookstack bookstack < ../$(BACKUP_DIR)/bookstack_backup.sql && cd ..
	@echo "$(GREEN)Данные восстановлены из $(BACKUP_DIR)$(NC)"

update: ## Обновить все образы Docker
	@echo "$(BLUE)Обновление образов Docker...$(NC)"
	@cd outline && docker-compose pull && cd ..
	@cd bookstack && docker-compose pull && cd ..
	@echo "$(GREEN)Образы обновлены!$(NC)"

check: ## Проверить состояние системы
	@echo "$(BLUE)Проверка состояния системы...$(NC)"
	@echo "$(BLUE)Docker:$(NC)"
	@docker --version
	@docker-compose --version
	@echo "$(BLUE)Порты:$(NC)"
	@lsof -i :3000 -i :6875 2>/dev/null || echo "Порты свободны"
	@echo "$(BLUE)Статус сервисов:$(NC)"
	@./start-all.sh status

setup-env: ## Настроить переменные окружения
	@echo "$(BLUE)Настройка переменных окружения...$(NC)"
	@cd outline && if [ ! -f .env ]; then cp env.example .env; echo "$(GREEN)Outline .env создан$(NC)"; else echo "$(YELLOW)Outline .env уже существует$(NC)"; fi && cd ..
	@cd bookstack && if [ ! -f .env ]; then cp env.example .env; echo "$(GREEN)BookStack .env создан$(NC)"; else echo "$(YELLOW)BookStack .env уже существует$(NC)"; fi && cd ..
	@echo "$(YELLOW)Не забудьте отредактировать .env файлы!$(NC)"

info: ## Показать информацию о сервисах
	@echo "$(BLUE)Self-Hosted Solutions Information$(NC)"
	@echo ""
	@echo "$(GREEN)Outline:$(NC)"
	@echo "  URL: http://localhost:3000"
	@echo "  Технологии: React, Node.js, PostgreSQL, Redis"
	@echo "  Описание: База знаний для команд"
	@echo ""
	@echo "$(GREEN)BookStack:$(NC)"
	@echo "  URL: http://localhost:6875"
	@echo "  Технологии: PHP, Laravel, MySQL"
	@echo "  Описание: Платформа документации"
	@echo ""
	@echo "$(BLUE)Полезные команды:$(NC)"
	@echo "  make start    - Запустить все сервисы"
	@echo "  make stop     - Остановить все сервисы"
	@echo "  make status   - Показать статус"
	@echo "  make logs     - Показать логи"
	@echo "  make backup   - Создать резервную копию"
