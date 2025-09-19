#!/bin/bash

# Настройка git hooks для автоматического исправления ошибок линтера
# JTBD: Как система настройки git hooks, я хочу настроить автоматическое
# исправление ошибок линтера при коммите, чтобы код всегда соответствовал стандартам.

echo "🔧 Настройка git hooks для автоматического исправления ошибок линтера..."

# Создаем директорию для hooks если её нет
mkdir -p .git/hooks

# Копируем pre-commit hook
if [ -f ".githooks/pre-commit" ]; then
    cp .githooks/pre-commit .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit
    echo "✅ Pre-commit hook установлен"
else
    echo "❌ Файл .githooks/pre-commit не найден"
    exit 1
fi

# Устанавливаем pre-commit если не установлен
if ! command -v pre-commit &> /dev/null; then
    echo "📦 Установка pre-commit..."
    pip install pre-commit
fi

# Устанавливаем pre-commit hooks
echo "🔧 Установка pre-commit hooks..."
pre-commit install

echo "✅ Git hooks настроены успешно!"
echo ""
echo "🎯 Теперь при каждом коммите будет автоматически:"
echo "   - Исправляться ошибки линтера"
echo "   - Форматироваться код"
echo "   - Проверяться качество кода"
echo ""
echo "💡 Для ручного исправления используйте:"
echo "   make auto-fix"
echo "   или"
echo "   python scripts/fix_linter_errors.py"
