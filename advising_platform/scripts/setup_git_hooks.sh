#!/bin/bash
# Настройка Git hooks для защиты MCP documentation

set -e

HOOKS_DIR=".git/hooks"
PROJECT_ROOT="$(pwd)"

echo "🔒 Настройка Git hooks для защиты MCP documentation..."

# Создаем директорию hooks если не существует
mkdir -p "$HOOKS_DIR"

# Pre-commit hook
cat > "$HOOKS_DIR/pre-commit" << 'EOF'
#!/bin/bash
# MCP Documentation Protection Pre-commit Hook

set -e

echo "🔍 Проверка MCP documentation integrity..."

# Проверяем изменения в защищенных файлах
PROTECTED_FILES=(
    "README.md"
    "[standards .md]/dependency_mapping.md" 
    "complete_mcp_workflow_trees.md"
    "mcp_dependency_matrix.json"
)

CHANGED_PROTECTED_FILES=()

for file in "${PROTECTED_FILES[@]}"; do
    if git diff --cached --name-only | grep -q "^$file$"; then
        CHANGED_PROTECTED_FILES+=("$file")
    fi
done

if [ ${#CHANGED_PROTECTED_FILES[@]} -gt 0 ]; then
    echo "⚠️  Обнаружены изменения в защищенных файлах:"
    printf '   - %s\n' "${CHANGED_PROTECTED_FILES[@]}"
    
    # Проверяем commit message на наличие MCP authorization
    if git log --format=%B -n 1 HEAD | grep -qE "\[MCP-AUTHORIZED\]|\[mcp-workflow\]"; then
        echo "✅ MCP workflow authorization найден в commit message"
    else
        echo "❌ Изменения защищенных файлов требуют MCP workflow authorization"
        echo "   Добавьте [MCP-AUTHORIZED] или [mcp-workflow] в commit message"
        exit 1
    fi
    
    # Запускаем тесты целостности
    echo "🧪 Запуск тестов MCP documentation integrity..."
    
    if command -v python3 >/dev/null 2>&1; then
        python3 -m pytest advising_platform/tests/integration/test_mcp_documentation_integrity_tdd.py -v --tb=short || {
            echo "❌ Тесты целостности MCP documentation провалились"
            exit 1
        }
    else
        echo "⚠️  Python3 не найден, пропускаем автоматические тесты"
    fi
    
    echo "✅ MCP documentation integrity проверен"
fi

echo "✅ Pre-commit проверки пройдены"
EOF

# Делаем pre-commit executable
chmod +x "$HOOKS_DIR/pre-commit"

# Pre-push hook
cat > "$HOOKS_DIR/pre-push" << 'EOF'
#!/bin/bash
# MCP Documentation Protection Pre-push Hook

set -e

echo "🚀 Pre-push проверка MCP documentation..."

# Проверяем, что все MCP workflow trees соответствуют стандарту
if [ -f "advising_platform/src/mcp/modules/documentation_validator.py" ]; then
    echo "🔍 Запуск полной валидации MCP documentation..."
    
    python3 advising_platform/src/mcp/modules/documentation_validator.py || {
        echo "❌ MCP documentation validation провалилась"
        echo "   Исправьте ошибки перед push"
        exit 1
    }
    
    echo "✅ MCP documentation validation пройдена"
fi

echo "✅ Pre-push проверки пройдены"
EOF

chmod +x "$HOOKS_DIR/pre-push"

# Commit-msg hook
cat > "$HOOKS_DIR/commit-msg" << 'EOF'
#!/bin/bash
# MCP Documentation Protection Commit Message Hook

COMMIT_MSG_FILE="$1"
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

# Проверяем изменения в защищенных файлах
PROTECTED_FILES_CHANGED=$(git diff --cached --name-only | grep -E "(README\.md|dependency_mapping\.md|complete_mcp_workflow_trees\.md|mcp_dependency_matrix\.json)" | wc -l)

if [ "$PROTECTED_FILES_CHANGED" -gt 0 ]; then
    # Если изменяются защищенные файлы, требуем MCP authorization
    if ! echo "$COMMIT_MSG" | grep -qE "\[MCP-AUTHORIZED\]|\[mcp-workflow\]"; then
        echo "❌ Commit message должен содержать [MCP-AUTHORIZED] или [mcp-workflow]"
        echo "   для изменений защищенных MCP файлов"
        exit 1
    fi
fi
EOF

chmod +x "$HOOKS_DIR/commit-msg"

echo "✅ Git hooks настроены успешно"
echo ""
echo "Установленные hooks:"
echo "  - pre-commit: Проверка MCP authorization и integrity tests"
echo "  - pre-push: Полная валидация MCP documentation"  
echo "  - commit-msg: Проверка authorization в commit message"
echo ""
echo "Для изменения защищенных файлов используйте в commit message:"
echo "  [MCP-AUTHORIZED] или [mcp-workflow]"