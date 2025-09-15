#!/bin/bash
# Скрипт для автоматического обновления статистики задач и синхронизации кеша
# Обновлен: 19 May 2025 AI Assistant - Исправлено 430 проблем синхронизации кеша

set -e # Прерывать скрипт при ошибках
LOG_FILE="cache_sync.log"

echo "Запуск автоматического обновления статистики задач и синхронизации кеша..." | tee -a $LOG_FILE
DATE=$(date +"%Y-%m-%d %H:%M:%S")
echo "Время запуска: $DATE" | tee -a $LOG_FILE

# Создание резервной копии кеша
echo "Создание резервной копии кеша..." | tee -a $LOG_FILE
mkdir -p .checkpoint_backup
cp -f .cache_state.json .checkpoint_backup/cache_state_backup_$(date +"%Y%m%d_%H%M%S").json 2>/dev/null || true
cp -f .cache_detailed_state.pickle .checkpoint_backup/cache_detailed_state_backup_$(date +"%Y%m%d_%H%M%S").pickle 2>/dev/null || true

# Очистка кеша от устаревших записей
echo "Очистка кеша от устаревших записей..." | tee -a $LOG_FILE
python clear_orphaned_cache_entries.py | tee -a $LOG_FILE

# Инициализация кеша
echo "Инициализация кеша..." | tee -a $LOG_FILE
python cache_manager.py init --force | tee -a $LOG_FILE

# Выполнение пробного запуска синхронизации
echo "Запуск верификации синхронизации кеша для определения проблем..." | tee -a $LOG_FILE
python count_files.py | tee -a $LOG_FILE

# Поэтапная предзагрузка директорий для избежания таймаутов
echo "Предзагрузка стандартов в кеш..." | tee -a $LOG_FILE
python cache_manager.py preload --directories "[standards .md]" | tee -a $LOG_FILE

echo "Предзагрузка задач и инцидентов в кеш..." | tee -a $LOG_FILE
python cache_manager.py preload --directories "[todo · incidents]" | tee -a $LOG_FILE

echo "Предзагрузка проектов в кеш..." | tee -a $LOG_FILE
python cache_manager.py preload --directories "[projects]" | tee -a $LOG_FILE

echo "Предзагрузка прикрепленных файлов в кеш..." | tee -a $LOG_FILE
python cache_manager.py preload --directories "attached_assets" | tee -a $LOG_FILE

echo "Предзагрузка документации в кеш..." | tee -a $LOG_FILE
python cache_manager.py preload --directories "docs" "examples" | tee -a $LOG_FILE

# Обновление статистики задач
echo "Обновление статистики задач..." | tee -a $LOG_FILE
python update_task_stats.py | tee -a $LOG_FILE

# Проверка консистентности триггеров
echo "Проверка консистентности триггеров задач и инцидентов..." | tee -a $LOG_FILE
python cache_init.py --verify-triggers | tee -a $LOG_FILE

# Запуск консолидации задач и инцидентов
echo "Запуск консолидации задач и инцидентов..." | tee -a $LOG_FILE
python consolidate_tasks_and_incidents.py | tee -a $LOG_FILE

# Финальная проверка состояния кеша
echo "Проверка состояния кеша после синхронизации..." | tee -a $LOG_FILE
python count_files.py | tee -a $LOG_FILE

echo "Обновление завершено!" | tee -a $LOG_FILE
echo "Лог работы скрипта сохранен в $LOG_FILE" | tee -a $LOG_FILE
echo "----------------------------------------------" | tee -a $LOG_FILE