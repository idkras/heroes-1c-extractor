#!/bin/bash
# Скрипт для регулярной проверки и синхронизации кеша
# Предназначен для запуска из cron или аналогичного планировщика
# Создан: 19 May 2025 AI Assistant

# Директория проекта
PROJECT_DIR=$(pwd)
LOG_FILE="$PROJECT_DIR/cache_sync_cron.log"
DATE=$(date +"%Y-%m-%d %H:%M:%S")

# Функция для логирования
log() {
  echo "[$DATE] $1" >> "$LOG_FILE"
  echo "[$DATE] $1"
}

# Переходим в директорию проекта
cd "$PROJECT_DIR" || {
  log "Ошибка: не удалось перейти в директорию проекта $PROJECT_DIR"
  exit 1
}

log "Запуск автоматической проверки и синхронизации кеша..."

# Проверяем состояние кеша
log "Проверка состояния кеша..."
python count_files.py > temp_stats.txt

# Извлекаем количество файлов и документов в кеше
TOTAL_FILES=$(grep "Всего файлов в проекте:" temp_stats.txt | awk '{print $5}')
TOTAL_CACHE=$(grep "Всего документов в кеше:" temp_stats.txt | awk '{print $5}')

log "Всего файлов в проекте: $TOTAL_FILES"
log "Всего документов в кеше: $TOTAL_CACHE"

# Определяем порог синхронизации (80% от общего количества файлов)
THRESHOLD=$((TOTAL_FILES * 80 / 100))

# Проверяем, нужна ли синхронизация
if [ "$TOTAL_CACHE" -lt "$THRESHOLD" ]; then
  log "Обнаружена рассинхронизация: в кеше $TOTAL_CACHE из $TOTAL_FILES файлов (порог: $THRESHOLD)"
  log "Запуск принудительной синхронизации..."
  
  # Создаем резервную копию кеша
  log "Создание резервной копии кеша..."
  mkdir -p .checkpoint_backup
  cp -f .cache_state.json .checkpoint_backup/cache_state_backup_$(date +"%Y%m%d_%H%M%S").json 2>/dev/null || true
  cp -f .cache_detailed_state.pickle .checkpoint_backup/cache_detailed_state_backup_$(date +"%Y%m%d_%H%M%S").pickle 2>/dev/null || true
  
  # Запускаем принудительную синхронизацию
  python force_cache_sync.py >> "$LOG_FILE" 2>&1
  
  if [ $? -eq 0 ]; then
    log "Принудительная синхронизация успешно завершена"
  else
    log "ОШИБКА: Принудительная синхронизация не удалась"
  fi
else
  log "Кеш в хорошем состоянии: $TOTAL_CACHE документов из $TOTAL_FILES файлов"
  
  # Проверяем наличие небольших несоответствий
  MISSING_STANDARDS=$(grep "Стандарты:" temp_stats.txt | grep "отсутствуют в кеше" | awk '{print $2}')
  MISSING_TASKS=$(grep "Задачи:" temp_stats.txt | grep "отсутствуют в кеше" | awk '{print $2}')
  
  if [ -n "$MISSING_STANDARDS" ] && [ "$MISSING_STANDARDS" -gt 0 ] || [ -n "$MISSING_TASKS" ] && [ "$MISSING_TASKS" -gt 0 ]; then
    log "Обнаружены небольшие несоответствия: отсутствуют $MISSING_STANDARDS стандартов и $MISSING_TASKS задач"
    log "Запуск обновления кеша..."
    
    # Запускаем обновление кеша
    python cache_manager.py preload --directories "[standards .md]" "[todo · incidents]" >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
      log "Обновление кеша успешно завершено"
    else
      log "ОШИБКА: Обновление кеша не удалось"
    fi
  else
    log "Несоответствий не обнаружено, обновление не требуется"
  fi
fi

# Очистка временных файлов
rm -f temp_stats.txt

log "Проверка и синхронизация кеша завершена"
log "-------------------------------------------"