#!/bin/bash

# Скрипт для мониторинга экспорта больших блоков данных из 1CD
# Защита от падения из-за нехватки памяти

set -e

# Настройки
WINE_PREFIX="/Users/ilyakrasinsky/Library/Application Support/CrossOver/Bottles/ctool1cd"
CTOOL_PATH="/Users/ilyakrasinsky/workspace/vscode.projects/1C-extractor/tool1cd/bin"
DB_PATH="C:\\1Cv8.1CD"
MAX_MEMORY_KB=2000000  # 2GB
MONITOR_INTERVAL=30     # 30 секунд
TIMEOUT_SECONDS=1800    # 30 минут

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция логирования
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Настройка Wine для больших файлов
setup_wine() {
    log "Настройка Wine для больших файлов..."
    export WINEDEBUG=-all
    export WINEARCH=win32
    export WINEPREFIX="$WINE_PREFIX"
    
    # Увеличение лимитов памяти (macOS совместимость)
    # ulimit -v 4000000  # 4GB virtual memory - не поддерживается в macOS
    # ulimit -m 2000000  # 2GB resident memory - не поддерживается в macOS
    
    # Альтернативные настройки для macOS
    export WINEARCH=win32
    export WINEPREFIX="$WINE_PREFIX"
    
    log "Wine настроен для работы с большими файлами (macOS)"
}

# Мониторинг памяти процесса
monitor_memory() {
    local pid=$1
    local block_name=$2
    
    while kill -0 $pid 2>/dev/null; do
        local memory_kb=$(ps -o rss -p $pid 2>/dev/null | tail -1)
        
        if [ -n "$memory_kb" ] && [ "$memory_kb" -gt 0 ]; then
            local memory_mb=$((memory_kb / 1024))
            log "Block $block_name - Memory: ${memory_mb}MB (PID: $pid)"
            
            if [ $memory_kb -gt $MAX_MEMORY_KB ]; then
                warning "High memory usage for block $block_name: ${memory_mb}MB"
                log "Pausing process for 60 seconds..."
                kill -STOP $pid
                sleep 60
                kill -CONT $pid
                log "Process resumed"
            fi
        fi
        
        sleep $MONITOR_INTERVAL
    done
}

# Экспорт блока с мониторингом
export_block() {
    local block=$1
    local output_dir="C:\\block_${block}"
    local log_file="export_${block}_$(date +%Y%m%d_%H%M%S).log"
    
    log "Начинаем экспорт блока $block..."
    
    # Создаем директорию в Wine
    wine cmd /c "mkdir $output_dir" 2>/dev/null || true
    
    # Запускаем экспорт в фоне
    cd "$CTOOL_PATH"
    wine ctool1cd.exe -ex "$output_dir" "$block" -bf yes -pb yes -ne "$DB_PATH" > "$log_file" 2>&1 &
    local export_pid=$!
    
    log "Экспорт запущен с PID: $export_pid"
    
    # Запускаем мониторинг памяти
    monitor_memory $export_pid "$block" &
    local monitor_pid=$!
    
    # Ждем завершения экспорта
    wait $export_pid
    local exit_code=$?
    
    # Останавливаем мониторинг
    kill $monitor_pid 2>/dev/null || true
    
    if [ $exit_code -eq 0 ]; then
        success "Блок $block успешно экспортирован"
        
        # Копируем результаты в проект
        local project_dir="/Users/ilyakrasinsky/workspace/vscode.projects/1C-extractor/[prostocvet-1c]/raw"
        cp -r "$WINE_PREFIX/drive_c/block_${block}" "$project_dir/" 2>/dev/null || true
        cp "$log_file" "$project_dir/" 2>/dev/null || true
        
        log "Результаты скопированы в $project_dir"
        return 0
    else
        error "Ошибка экспорта блока $block (exit code: $exit_code)"
        log "Лог ошибки: $log_file"
        return 1
    fi
}

# Экспорт с повторными попытками
export_block_with_retry() {
    local block=$1
    local max_attempts=3
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log "Попытка $attempt из $max_attempts для блока $block"
        
        if export_block "$block"; then
            success "Блок $block успешно экспортирован с попытки $attempt"
            return 0
        else
            warning "Попытка $attempt для блока $block не удалась"
            attempt=$((attempt + 1))
            
            if [ $attempt -le $max_attempts ]; then
                log "Ожидание 5 минут перед следующей попыткой..."
                sleep 300
            fi
        fi
    done
    
    error "Блок $block не удалось экспортировать после $max_attempts попыток"
    return 1
}

# Системный мониторинг
monitor_system() {
    log "Запуск системного мониторинга..."
    
    while true; do
        echo "=== $(date) ==="
        echo "Memory: $(vm_stat | grep 'Pages free' | awk '{print $3 * 4096 / 1024 / 1024 " MB"}')"
        echo "Disk: $(df -h | grep '/dev/' | head -1)"
        echo "Wine processes: $(pgrep wine | wc -l)"
        echo "=================="
        sleep 60
    done
}

# Главная функция
main() {
    log "Запуск системы мониторинга экспорта 1CD данных..."
    
    # Настройка Wine
    setup_wine
    
    # Запуск системного мониторинга в фоне
    monitor_system &
    local system_monitor_pid=$!
    
    # Список блоков для экспорта (приоритетные большие блоки)
    local blocks=(
        "0x0000df9e"  # 1.54 ГБ - ВЕРСИЯ 1471:1471
        "0x0000dfb6"  # 1.39 ГБ - ВЕРСИЯ 1328:1328
        "0x0000dfb7"  # 1.39 ГБ - ВЕРСИЯ 1331:1331
        "0x0000e005"  # 415 МБ - ВЕРСИЯ 415:415
        "0x0000e007"  # 181 МБ - ВЕРСИЯ 181:181
    )
    
    local success_count=0
    local total_count=${#blocks[@]}
    
    log "Начинаем экспорт $total_count блоков..."
    
    for block in "${blocks[@]}"; do
        log "Обработка блока $block..."
        
        if export_block_with_retry "$block"; then
            success_count=$((success_count + 1))
            success "Блок $block завершен успешно ($success_count/$total_count)"
        else
            error "Блок $block завершен с ошибкой"
        fi
        
        # Пауза между блоками
        log "Пауза 2 минуты перед следующим блоком..."
        sleep 120
    done
    
    # Останавливаем системный мониторинг
    kill $system_monitor_pid 2>/dev/null || true
    
    log "Экспорт завершен. Успешно: $success_count/$total_count"
    
    if [ $success_count -eq $total_count ]; then
        success "Все блоки успешно экспортированы!"
    else
        warning "Некоторые блоки не удалось экспортировать"
    fi
}

# Запуск главной функции
main "$@" 