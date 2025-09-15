#!/bin/bash
# context_file_naming_checker.sh
# Скрипт для проверки соответствия имен контекстных файлов стандарту именования
# created: 12 May 2025 by AI Assistant
# based on: Context Naming Standard 3.5

echo "Проверка соответствия контекстных файлов стандарту именования..."
echo "======================================================================"

# Поиск контекстных файлов
context_files=$(find ./projects -name "*context*.md" | grep -v "archive" | grep -v "md~")

# Счетчики для итогового отчета
count_total=0
count_incorrect=0
count_with_duplicates=0
projects_with_duplicates=()

for file in $context_files; do
  ((count_total++))
  dir=$(dirname "$file")
  name=$(basename "$file")
  project=$(basename "$dir")
  
  echo "Проверка файла: $file"
  
  # Проверка формата имени
  if [[ ! $name =~ ^[a-z0-9.-]+\ context\.md$ ]]; then
    ((count_incorrect++))
    echo "  ⚠️ ОШИБКА: Неправильный формат имени"
    
    # Определение нарушений
    if [[ $name =~ [A-Z] ]]; then
      echo "    - Содержит заглавные буквы"
    fi
    
    if [[ ! $name =~ \ context\.md$ ]]; then
      echo "    - Неверный формат 'context.md' части"
    fi
    
    if [[ $name =~ _context ]]; then
      echo "    - Использовано подчеркивание вместо пробела"
    fi
    
    # Проверка, является ли проект веб-сайтом
    if [[ $project =~ \. ]]; then
      # Если проект содержит точку, предполагаем что это домен
      if [[ ! $name =~ ^$project\ context\.md ]]; then
        echo "    - Название проекта не соответствует имени папки '$project'"
      fi
    fi
    
    echo "    ✅ Рекомендуемое имя: '$project context.md'"
  else
    echo "  ✅ Формат имени соответствует стандарту"
  fi
  
  # Проверка на дубликаты
  duplicates=$(find "$dir" -name "*context*.md" | grep -v "archive" | grep -v "md~" | wc -l)
  if [ $duplicates -gt 1 ]; then
    ((count_with_duplicates++))
    projects_with_duplicates+=("$project")
    echo "  ⚠️ ПРЕДУПРЕЖДЕНИЕ: Обнаружены возможные дубликаты в $dir:"
    find "$dir" -name "*context*.md" | grep -v "archive" | grep -v "md~" | sed 's/^/    - /'
    echo "    Необходимо объединить файлы в один по стандарту именования"
  fi
  
  # Проверка на наличие метаданных в файле
  echo "  Проверка метаданных..."
  has_updated=$(grep -l "updated:" "$file")
  has_based_on=$(grep -l "based on:" "$file")
  
  if [ -z "$has_updated" ]; then
    echo "    ⚠️ ОШИБКА: Отсутствует строка 'updated:'"
  else
    echo "    ✅ Строка 'updated:' присутствует"
  fi
  
  if [ -z "$has_based_on" ]; then
    echo "    ⚠️ ОШИБКА: Отсутствует строка 'based on:'"
  else
    echo "    ✅ Строка 'based on:' присутствует"
  fi
  
  echo ""
done

# Итоговый отчет
echo "======================================================================"
echo "ИТОГОВЫЙ ОТЧЕТ:"
echo "--------------------------------------------------------------------"
echo "Всего проверено файлов: $count_total"
echo "Файлов с некорректными именами: $count_incorrect"
echo "Проектов с дублирующимися файлами: $count_with_duplicates"

if [ $count_with_duplicates -gt 0 ]; then
  echo ""
  echo "Проекты с дубликатами контекстных файлов:"
  for project in "${projects_with_duplicates[@]}"; do
    echo "  - $project"
  done
fi

echo ""
if [ $count_incorrect -eq 0 ] && [ $count_with_duplicates -eq 0 ]; then
  echo "🎉 Все контекстные файлы соответствуют стандарту именования!"
else
  echo "⚠️ Требуется исправление обнаруженных проблем в соответствии со стандартом именования контекстных файлов (3.5)."
fi
echo "======================================================================"