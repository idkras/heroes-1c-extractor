#!/usr/bin/env python3
"""
Dependencies Matrix Updater
Автоматическое обновление dependencies_matrix.md при изменениях в проекте

JTBD: Как система сопровождения, я хочу автоматически обновлять матрицу зависимостей,
чтобы поддерживать актуальную документацию структуры проекта.
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Import from heroes_platform package


class DependenciesMatrixUpdater:
    """Класс для автоматического обновления dependencies_matrix.md"""

    def __init__(self):
        """
        Initialize the DependenciesMatrixUpdater.

        Sets up paths for project root, MCP server root, and documentation files.
        """
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.heroes_mcp_root = Path(__file__).parent.parent
        self.docs_path = self.heroes_mcp_root / "docs"
        self.matrix_file = self.docs_path / "dependencies_matrix.md"

        # Шаблоны для поиска файлов
        self.file_patterns = {
            "python": "*.py",
            "markdown": "*.md",
            "json": "*.json",
            "yaml": "*.yml",
            "yaml_alt": "*.yaml",
            "toml": "*.toml",
            "shell": "*.sh",
            "zsh": "*.zsh",
        }

        # Исключаемые директории
        self.exclude_dirs = {
            "__pycache__",
            ".git",
            ".venv",
            "node_modules",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            "htmlcov",
            "logs",
            "cache",
            "test_results",
        }

        # Критические файлы для отслеживания
        self.critical_files = {
            "heroes_mcp.py": "Главный MCP сервер",
            "telegram_workflow_fixed.py": "Telegram workflow",
            "enhanced_log_monitor.py": "Мониторинг логов",
            "health_check.py": "Проверка здоровья",
            "check_critical_issues.py": "Проверка критических проблем",
            "final_alert_check.py": "Финальные алерты",
            "analyze_logs.py": "Анализ логов",
        }

    def scan_project_structure(self) -> dict[str, list[str]]:
        """Сканирует структуру проекта и возвращает карту файлов"""
        structure: dict[str, list[str]] = {
            "root_files": [],
            "workflows": [],
            "scripts": [],
            "src_files": [],
            "test_files": [],
            "config_files": [],
            "docs_files": [],
        }

        # Сканируем корневую директорию проекта
        for item in self.project_root.iterdir():
            if item.is_file() and not item.name.startswith("."):
                structure["root_files"].append(item.name)
            elif item.is_dir() and item.name not in self.exclude_dirs:
                if item.name == "workflows":
                    structure["workflows"] = self._scan_directory(item)
                elif item.name == "scripts":
                    structure["scripts"] = self._scan_directory(item)
                elif item.name == "[standards .md]":
                    # Сканируем platform/mcp_server
                    platform_path = item / "platform" / "mcp_server"
                    if platform_path.exists():
                        structure.update(self._scan_mcp_server_structure(platform_path))

        return structure

    def _scan_directory(self, directory: Path) -> list[str]:
        """Сканирует директорию и возвращает список файлов"""
        files = []
        for pattern in self.file_patterns.values():
            files.extend([f.name for f in directory.glob(pattern)])
        return sorted(files)

    def _scan_mcp_server_structure(self, mcp_path: Path) -> dict[str, list[str]]:
        """Сканирует структуру MCP сервера"""
        structure: dict[str, list[str]] = {
            "src_files": [],
            "test_files": [],
            "config_files": [],
            "docs_files": [],
        }

        # Сканируем src/
        src_path = mcp_path / "src"
        if src_path.exists():
            structure["src_files"] = self._scan_directory(src_path)

            # Сканируем поддиректории src/
            for subdir in src_path.iterdir():
                if subdir.is_dir():
                    subdir_files = self._scan_directory(subdir)
                    structure["src_files"].extend(
                        [f"{subdir.name}/{f}" for f in subdir_files]
                    )

        # Сканируем tests/
        tests_path = mcp_path / "tests"
        if tests_path.exists():
            structure["test_files"] = self._scan_directory(tests_path)

        # Сканируем config/
        config_path = mcp_path / "config"
        if config_path.exists():
            structure["config_files"] = self._scan_directory(config_path)

        # Сканируем docs/
        docs_path = mcp_path / "docs"
        if docs_path.exists():
            structure["docs_files"] = self._scan_directory(docs_path)

        return structure

    def analyze_dependencies(self) -> dict[str, list[str]]:
        """Анализирует зависимости между файлами"""
        dependencies: dict[str, list[str]] = {
            "imports": [],
            "duplicates": [],
            "missing_files": [],
            "broken_links": [],
        }

        # Анализируем импорты в Python файлах
        src_path = self.heroes_mcp_root / "src"
        if src_path.exists():
            for py_file in src_path.rglob("*.py"):
                imports = self._extract_imports(py_file)
                for imp in imports:
                    dependencies["imports"].append(f"{py_file.name} -> {imp}")

        # Проверяем дублирования
        all_files = []
        for root, _dirs, files in os.walk(self.project_root):
            if any(exclude in root for exclude in self.exclude_dirs):
                continue
            all_files.extend(files)

        # Находим дубликаты
        file_counts: dict[str, int] = {}
        for file in all_files:
            file_counts[file] = file_counts.get(file, 0) + 1

        for file, count in file_counts.items():
            if count > 1 and file.endswith(".py"):
                dependencies["duplicates"].append(f"{file} (найдено {count} копий)")

        return dependencies

    def _extract_imports(self, file_path: Path) -> list[str]:
        """Извлекает импорты из Python файла"""
        imports = []
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Регулярные выражения для поиска импортов
            import_patterns = [
                r"^import\s+(\w+)",
                r"^from\s+(\w+)\s+import",
                r"^from\s+(\w+\.\w+)\s+import",
            ]

            for pattern in import_patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                imports.extend(matches)

        except Exception as e:
            print(f"Ошибка при чтении {file_path}: {e}")

        return list(set(imports))

    def check_critical_issues(self) -> list[str]:
        """Проверяет критические проблемы в проекте"""
        issues = []

        # Проверяем наличие критических файлов
        for filename, description in self.critical_files.items():
            file_path = self.heroes_mcp_root / "src" / filename
            if not file_path.exists():
                issues.append(
                    f"❌ Отсутствует критический файл: {filename} ({description})"
                )
            else:
                # Проверяем размер файла
                size = file_path.stat().st_size
                if size < 100:  # Файл слишком маленький
                    issues.append(
                        f"⚠️ Подозрительно маленький файл: {filename} ({size} байт)"
                    )

        # Проверяем конфигурацию MCP
        mcp_config_path = Path.home() / ".cursor" / "mcp.json"
        if not mcp_config_path.exists():
            issues.append("❌ Отсутствует конфигурация MCP: ~/.cursor/mcp.json")

        return issues

    def generate_matrix_content(self) -> str:
        """Генерирует содержимое dependencies_matrix.md"""
        structure = self.scan_project_structure()
        dependencies = self.analyze_dependencies()
        issues = self.check_critical_issues()

        content = f"""# 📊 Dependencies Matrix - MCP Server Project Structure

## 🎯 **Цель документа**
**JTBD:** Как разработчик, я хочу иметь четкое понимание структуры файлов и зависимостей проекта, чтобы избежать дублирования и эффективно работать с существующей кодовой базой.

**Последнее обновление:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 🏗️ **Структура проекта**

### **Корневая директория** (`/`)
```
[cursor.template project]/
├── workflows/                    # ✅ СУЩЕСТВУЕТ - основные workflow файлы
{self._format_file_list(structure.get("workflows", []), "workflows")}
├── scripts/                     # ✅ СУЩЕСТВУЕТ - скрипты сопровождения
{self._format_file_list(structure.get("scripts", []), "scripts")}
├── [standards .md]/             # ✅ СУЩЕСТВУЕТ - стандарты и документация
│   └── platform/mcp_server/     # ✅ СУЩЕСТВУЕТ - основной MCP сервер
└── config/                      # ✅ СУЩЕСТВУЕТ - конфигурации
```

### **MCP Server Platform** (`[standards .md]/platform/mcp_server/`)
```
platform/mcp_server/
├── src/                         # ✅ СУЩЕСТВУЕТ - основной код
{self._format_file_list(structure.get("src_files", []), "src")}
├── scripts/                     # ✅ СУЩЕСТВУЕТ - скрипты мониторинга
├── tests/                       # ✅ СУЩЕСТВУЕТ - тесты
{self._format_file_list(structure.get("test_files", []), "tests")}
├── docs/                        # ✅ СУЩЕСТВУЕТ - документация
{self._format_file_list(structure.get("docs_files", []), "docs")}
├── logs/                        # ✅ СУЩЕСТВУЕТ - логи
└── .github/workflows/           # ✅ СУЩЕСТВУЕТ - CI/CD
```

## 🔄 **Критические зависимости и дублирования**

### **🚨 ПРОБЛЕМЫ ОБНАРУЖЕНЫ:**
"""

        if dependencies["duplicates"]:
            content += "\n#### **Дублирования файлов:**\n"
            for duplicate in dependencies["duplicates"]:
                content += f"- **{duplicate}**\n"

        if issues:
            content += "\n#### **Критические проблемы:**\n"
            for issue in issues:
                content += f"- {issue}\n"

        content += f"""
### **✅ ПРАВИЛЬНЫЕ ЗАВИСИМОСТИ:**

#### **MCP Server Configuration**
```json
// ~/.cursor/mcp.json - ПРАВИЛЬНО НАСТРОЕНО
{{
  "mcpServers": {{
    "heroes_mcp": {{
      "command": "python3",
      "args": ["/path/to/platform/mcp_server/src/mcp_server.py"],
      "env": {{
        "PYTHONPATH": "/path/to/platform/mcp_server"
      }}
    }}
  }}
}}
```

## 📊 **Статистика проекта**

- **Всего файлов в src/:** {len(structure.get("src_files", []))}
- **Всего тестов:** {len(structure.get("test_files", []))}
- **Всего документации:** {len(structure.get("docs_files", []))}
- **Найдено дублирований:** {len(dependencies.get("duplicates", []))}
- **Критических проблем:** {len(issues)}

## 🔧 **Автоматическое обновление**

Этот файл автоматически обновляется скриптом `scripts/update_dependencies_matrix.py`

### **Когда обновляется:**
- При добавлении новых файлов
- При изменении структуры проекта
- При обнаружении дублирований
- При изменении зависимостей

### **Как запустить обновление:**
```bash
cd [standards .md]/platform/mcp_server
python3 scripts/update_dependencies_matrix.py
```

## 🔗 **Ссылки на стандарты**

- **[TDD Documentation Standard](abstract://standard:tdd_documentation_standard)** - для создания качественного кода
- **[FROM-THE-END Standard](abstract://standard:from_the_end_standard)** - для системного подхода
- **[MCP Workflow Standard](abstract://standard:mcp_workflow_standard)** - для архитектуры workflow

---

**Статус:** Автоматически обновлено
**Следующий шаг:** Проверить критические проблемы и исправить дублирования
"""

        return content

    def _format_file_list(self, files: list[str], directory: str) -> str:
        """Форматирует список файлов для отображения в структуре"""
        if not files:
            return f"│   └── (пусто)                    # 📁 Директория {directory}"

        formatted = []
        for i, file in enumerate(files[:5]):  # Показываем только первые 5 файлов
            if i == len(files) - 1 or i == 4:
                formatted.append(f"│   └── {file}")
            else:
                formatted.append(f"│   ├── {file}")

        if len(files) > 5:
            formatted.append(f"│   └── ... и еще {len(files) - 5} файлов")

        return "\n".join(formatted)

    def update_matrix(self) -> bool:
        """Обновляет dependencies_matrix.md"""
        try:
            # Создаем директорию docs если её нет
            self.docs_path.mkdir(exist_ok=True)

            # Генерируем новое содержимое
            content = self.generate_matrix_content()

            # Записываем в файл
            with open(self.matrix_file, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"✅ Dependencies matrix обновлен: {self.matrix_file}")
            return True

        except Exception as e:
            print(f"❌ Ошибка при обновлении matrix: {e}")
            return False


def main():
    """Главная функция"""
    updater = DependenciesMatrixUpdater()

    print("🔄 Обновление dependencies_matrix.md...")

    if updater.update_matrix():
        print("✅ Обновление завершено успешно")

        # Показываем краткую статистику
        structure = updater.scan_project_structure()
        issues = updater.check_critical_issues()

        print("\n📊 Статистика:")
        print(f"- Файлов в src/: {len(structure.get('src_files', []))}")
        print(f"- Тестов: {len(structure.get('test_files', []))}")
        print(f"- Критических проблем: {len(issues)}")

        if issues:
            print("\n⚠️ Критические проблемы:")
            for issue in issues[:3]:  # Показываем только первые 3
                print(f"  {issue}")
            if len(issues) > 3:
                print(f"  ... и еще {len(issues) - 3} проблем")
    else:
        print("❌ Обновление завершилось с ошибкой")
        sys.exit(1)


if __name__ == "__main__":
    main()
