#!/bin/bash

# Скрипт для работы с GUI версией gtool1cd.exe
# Альтернативный подход для экспорта больших блоков данных

set -e

# Настройки
WINE_PREFIX="/Users/ilyakrasinsky/Library/Application Support/CrossOver/Bottles/ctool1cd"
CTOOL_PATH="/Users/ilyakrasinsky/workspace/vscode.projects/1C-extractor/tool1cd/bin"
DB_PATH="C:\\1Cv8.1CD"
PROJECT_DIR="/Users/ilyakrasinsky/workspace/vscode.projects/1C-extractor/[prostocvet-1c]/raw"

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

# Настройка Wine для GUI
setup_wine_gui() {
    log "Настройка Wine для GUI приложения..."
    export WINEDEBUG=-all
    export WINEARCH=win32
    export WINEPREFIX="$WINE_PREFIX"
    
    # Настройки для GUI
    export DISPLAY=:0
    
    log "Wine настроен для GUI приложений"
}

# Запуск GUI версии с мониторингом
launch_gui_export() {
    log "Запуск GUI версии gtool1cd.exe..."
    
    cd "$CTOOL_PATH"
    
    # Запускаем GUI в фоне
    wine gtool1cd.exe &
    local gui_pid=$!
    
    log "GUI запущен с PID: $gui_pid"
    
    # Мониторинг GUI процесса
    monitor_gui_process $gui_pid
    
    return $?
}

# Мониторинг GUI процесса
monitor_gui_process() {
    local pid=$1
    local start_time=$(date +%s)
    local max_runtime=3600  # 1 час максимум
    
    log "Начинаем мониторинг GUI процесса (PID: $pid)"
    
    while kill -0 $pid 2>/dev/null; do
        local current_time=$(date +%s)
        local runtime=$((current_time - start_time))
        
        # Проверяем время работы
        if [ $runtime -gt $max_runtime ]; then
            warning "GUI процесс работает слишком долго ($runtime секунд), завершаем..."
            kill $pid
            break
        fi
        
        # Проверяем память
        local memory_kb=$(ps -o rss -p $pid 2>/dev/null | tail -1)
        if [ -n "$memory_kb" ] && [ "$memory_kb" -gt 0 ]; then
            local memory_mb=$((memory_kb / 1024))
            log "GUI Memory: ${memory_mb}MB (Runtime: ${runtime}s)"
            
            if [ $memory_kb -gt 3000000 ]; then  # 3GB limit for GUI
                warning "High memory usage: ${memory_mb}MB"
            fi
        fi
        
        # Проверяем наличие файлов экспорта
        check_export_files
        
        sleep 30
    done
    
    local exit_code=$?
    log "GUI процесс завершен (exit code: $exit_code)"
    return $exit_code
}

# Проверка файлов экспорта
check_export_files() {
    local wine_drive_c="$WINE_PREFIX/drive_c"
    
    # Ищем новые файлы экспорта
    find "$wine_drive_c" -name "*.xml" -newer "$wine_drive_c" 2>/dev/null | while read file; do
        local file_size=$(stat -f%z "$file" 2>/dev/null || echo "0")
        local file_size_mb=$((file_size / 1024 / 1024))
        
        if [ $file_size_mb -gt 10 ]; then  # Файлы больше 10MB
            log "Найден большой файл экспорта: $(basename "$file") (${file_size_mb}MB)"
            
            # Копируем в проект
            cp "$file" "$PROJECT_DIR/" 2>/dev/null && \
            success "Файл $(basename "$file") скопирован в проект"
        fi
    done
}

# Создание инструкций для GUI
create_gui_instructions() {
    local instructions_file="$PROJECT_DIR/gui_export_instructions.txt"
    
    cat > "$instructions_file" << 'EOF'
ИНСТРУКЦИИ ДЛЯ GUI ЭКСПОРТА (gtool1cd.exe)

1. ЗАПУСК GUI:
   - GUI версия запущена автоматически
   - Окно должно открыться на экране

2. ОТКРЫТИЕ БАЗЫ ДАННЫХ:
   - File -> Open Database
   - Выберите файл: C:\1Cv8.1CD
   - Нажмите OK

3. ЭКСПОРТ БОЛЬШИХ БЛОКОВ:
   - В дереве таблиц найдите большие блоки:
     * 0x0000df9e (1.54 ГБ) - ВЕРСИЯ 1471:1471
     * 0x0000dfb6 (1.39 ГБ) - ВЕРСИЯ 1328:1328
     * 0x0000dfb7 (1.39 ГБ) - ВЕРСИЯ 1331:1331
     * 0x0000e005 (415 МБ) - ВЕРСИЯ 415:415
     * 0x0000e007 (181 МБ) - ВЕРСИЯ 181:181

4. ЭКСПОРТ ТАБЛИЦ:
   - Выберите таблицу в дереве
   - Правый клик -> Export
   - Выберите формат: XML
   - Включите опции: Binary Data, Page Bodies
   - Укажите папку: C:\gui_export
   - Нажмите Export

5. МОНИТОРИНГ:
   - Следите за прогрессом в окне
   - При высокой нагрузке на память - пауза
   - Файлы автоматически копируются в проект

6. ЗАВЕРШЕНИЕ:
   - Дождитесь завершения всех экспортов
   - Закройте GUI
   - Проверьте результаты в папке проекта

ПРИМЕЧАНИЯ:
- GUI может работать медленнее, но стабильнее
- При зависании - перезапустите процесс
- Большие файлы экспортируются долго
- Следите за свободным местом на диске
EOF

    log "Инструкции созданы: $instructions_file"
}

# Создание папок для экспорта
setup_export_dirs() {
    log "Создание папок для экспорта..."
    
    # Создаем папки в Wine
    wine cmd /c "mkdir C:\\gui_export" 2>/dev/null || true
    wine cmd /c "mkdir C:\\gui_export\\blocks" 2>/dev/null || true
    wine cmd /c "mkdir C:\\gui_export\\tables" 2>/dev/null || true
    
    # Создаем папки в проекте
    mkdir -p "$PROJECT_DIR/gui_export"
    mkdir -p "$PROJECT_DIR/gui_export/blocks"
    mkdir -p "$PROJECT_DIR/gui_export/tables"
    
    log "Папки для экспорта созданы"
}

# Главная функция
main() {
    log "Запуск GUI экспорта 1CD данных..."
    
    # Настройка Wine
    setup_wine_gui
    
    # Создание папок
    setup_export_dirs
    
    # Создание инструкций
    create_gui_instructions
    
    # Запуск GUI экспорта
    if launch_gui_export; then
        success "GUI экспорт завершен успешно"
        
        # Копируем все результаты
        log "Копирование результатов экспорта..."
        cp -r "$WINE_PREFIX/drive_c/gui_export"/* "$PROJECT_DIR/gui_export/" 2>/dev/null || true
        
        success "Результаты скопированы в $PROJECT_DIR/gui_export"
    else
        error "GUI экспорт завершен с ошибкой"
    fi
}

# Запуск главной функции
main "$@" 