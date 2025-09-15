#!/bin/bash
# Скрипт для запуска инструментов аудита

# Переходим в корневую директорию проекта
cd "$(dirname "$0")/.."

# Определяем тип аудита
audit_type=${1:-"all"}

# Функция для вывода справки
show_help() {
  echo "Использование: $0 [тип_аудита]"
  echo ""
  echo "Типы аудита:"
  echo "  document_types - Аудит типов документов"
  echo "  indexing       - Аудит индексации"
  echo "  all            - Запуск всех типов аудита (по умолчанию)"
  echo ""
  exit 1
}

# Обработка аргументов командной строки
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
  show_help
fi

# Запуск аудита типов документов
run_document_types_audit() {
  echo "Запуск аудита типов документов..."
  python -m advising_platform.src.tools.analysis.audit_document_types
  echo "Аудит типов документов завершен"
}

# Запуск аудита индексации
run_indexing_audit() {
  echo "Запуск аудита индексации..."
  python -m advising_platform.src.tools.analysis.audit_indexing
  echo "Аудит индексации завершен"
}

# Запуск всех типов аудита
run_all_audits() {
  run_document_types_audit
  echo ""
  run_indexing_audit
}

# Выполнение аудита в зависимости от выбранного типа
case "$audit_type" in
  "document_types")
    run_document_types_audit
    ;;
  "indexing")
    run_indexing_audit
    ;;
  "all")
    run_all_audits
    ;;
  *)
    echo "Неизвестный тип аудита: $audit_type"
    show_help
    ;;
esac

echo ""
echo "Все операции аудита успешно завершены"