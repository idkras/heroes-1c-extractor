#!/bin/bash

# Self-Hosted Solutions - Start All Script
# Запускает Outline и BookStack одновременно

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

# Проверка наличия Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        error "Docker не установлен. Установите Docker и попробуйте снова."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose не установлен. Установите Docker Compose и попробуйте снова."
        exit 1
    fi
    
    log "Docker и Docker Compose найдены"
}

# Проверка портов
check_ports() {
    local outline_port=3000
    local bookstack_port=6875
    
    if lsof -Pi :$outline_port -sTCP:LISTEN -t >/dev/null ; then
        warn "Порт $outline_port уже занят. Outline может не запуститься."
    fi
    
    if lsof -Pi :$bookstack_port -sTCP:LISTEN -t >/dev/null ; then
        warn "Порт $bookstack_port уже занят. BookStack может не запуститься."
    fi
}

# Запуск Outline
start_outline() {
    log "Запуск Outline..."
    cd outline
    
    # Проверка наличия .env файла
    if [ ! -f .env ]; then
        if [ -f env.example ]; then
            log "Создание .env файла из примера..."
            cp env.example .env
            warn "Отредактируйте .env файл перед запуском в продакшене!"
        else
            error "Файл .env не найден. Создайте его вручную."
            return 1
        fi
    fi
    
    docker-compose up -d
    log "Outline запущен на http://localhost:3000"
    cd ..
}

# Запуск BookStack
start_bookstack() {
    log "Запуск BookStack..."
    cd bookstack
    
    # Проверка наличия .env файла
    if [ ! -f .env ]; then
        if [ -f env.example ]; then
            log "Создание .env файла из примера..."
            cp env.example .env
            warn "Отредактируйте .env файл перед запуском в продакшене!"
        else
            error "Файл .env не найден. Создайте его вручную."
            return 1
        fi
    fi
    
    docker-compose up -d
    log "BookStack запущен на http://localhost:6875"
    cd ..
}

# Проверка статуса
check_status() {
    log "Проверка статуса сервисов..."
    
    echo -e "\n${BLUE}=== Outline ===${NC}"
    cd outline
    docker-compose ps
    cd ..
    
    echo -e "\n${BLUE}=== BookStack ===${NC}"
    cd bookstack
    docker-compose ps
    cd ..
    
    echo -e "\n${GREEN}Сервисы доступны по адресам:${NC}"
    echo "  Outline:   http://localhost:3000"
    echo "  BookStack: http://localhost:6875"
}

# Основная функция
main() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Self-Hosted Solutions Starter${NC}"
    echo -e "${BLUE}================================${NC}"
    
    check_docker
    check_ports
    
    log "Запуск всех сервисов..."
    
    # Запуск Outline
    if start_outline; then
        log "Outline успешно запущен"
    else
        error "Ошибка запуска Outline"
    fi
    
    # Небольшая пауза между запусками
    sleep 5
    
    # Запуск BookStack
    if start_bookstack; then
        log "BookStack успешно запущен"
    else
        error "Ошибка запуска BookStack"
    fi
    
    # Проверка статуса
    sleep 10
    check_status
    
    echo -e "\n${GREEN}Все сервисы запущены!${NC}"
    echo -e "${YELLOW}Не забудьте настроить переменные окружения в .env файлах!${NC}"
}

# Обработка аргументов командной строки
case "${1:-}" in
    "outline")
        check_docker
        start_outline
        ;;
    "bookstack")
        check_docker
        start_bookstack
        ;;
    "status")
        check_status
        ;;
    "stop")
        log "Остановка всех сервисов..."
        cd outline && docker-compose down && cd ..
        cd bookstack && docker-compose down && cd ..
        log "Все сервисы остановлены"
        ;;
    "restart")
        log "Перезапуск всех сервисов..."
        cd outline && docker-compose restart && cd ..
        cd bookstack && docker-compose restart && cd ..
        log "Все сервисы перезапущены"
        ;;
    "logs")
        echo -e "${BLUE}=== Outline Logs ===${NC}"
        cd outline && docker-compose logs -f --tail=50 && cd ..
        echo -e "${BLUE}=== BookStack Logs ===${NC}"
        cd bookstack && docker-compose logs -f --tail=50 && cd ..
        ;;
    "help"|"-h"|"--help")
        echo "Использование: $0 [команда]"
        echo ""
        echo "Команды:"
        echo "  (без аргументов)  Запустить все сервисы"
        echo "  outline           Запустить только Outline"
        echo "  bookstack         Запустить только BookStack"
        echo "  status            Показать статус сервисов"
        echo "  stop              Остановить все сервисы"
        echo "  restart           Перезапустить все сервисы"
        echo "  logs              Показать логи"
        echo "  help              Показать эту справку"
        ;;
    *)
        main
        ;;
esac
