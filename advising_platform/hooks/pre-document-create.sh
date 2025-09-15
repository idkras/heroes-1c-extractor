#!/bin/bash
# Хук для запуска проверки соответствия стандартам перед созданием документа

# Получаем путь создаваемого документа
DOCUMENT_PATH="$1"

# Выводим информацию о запуске проверки
echo "🔍 Запуск проверки соответствия стандартам для документа: $DOCUMENT_PATH"

# Запускаем скрипт проверки соответствия стандартам
python scripts/check_standards_compliance.py "$DOCUMENT_PATH"

# Проверяем код возврата
if [ $? -ne 0 ]; then
    echo "❌ Проверка не пройдена. Документ не может быть создан."
    exit 1
fi

# Определяем тип документа по имени файла или пути
if [[ "$DOCUMENT_PATH" == *"incident"* ]]; then
    echo "📋 Определен тип документа: инцидент"
    echo "📋 Копирование шаблона инцидента..."
    cp templates/incident_template.md "$DOCUMENT_PATH"
elif [[ "$DOCUMENT_PATH" == *"task"* ]]; then
    echo "📋 Определен тип документа: задача"
    echo "📋 Копирование шаблона задачи..."
    cp templates/task_template.md "$DOCUMENT_PATH" 
fi

echo "✅ Проверка пройдена. Документ готов к редактированию."
exit 0