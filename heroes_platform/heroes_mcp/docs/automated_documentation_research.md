# 🔍 Deep Research: Автоматическое обновление документации

## 🎯 **Цель исследования**

**JTBD:** Как архитектор системы документации, я хочу изучить современные подходы к автоматическому обновлению документации, чтобы создать эффективную систему сопровождения кода.

## 📊 **Современные подходы к автоматической документации**

### **1. Swagger/OpenAPI подходы**

#### **FastAPI + Pydantic (Python)**

```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(
    title="Heroes MCP Server",
    description="MCP Server with automated documentation",
    version="2.0.0"
)

class WorkflowRequest(BaseModel):
    command: str
    arguments: dict

@app.post("/workflows/execute")
async def execute_workflow(request: WorkflowRequest):
    """
    Execute MCP workflow with automatic OpenAPI documentation
    """
    return {"status": "success", "result": "workflow executed"}
```

**Преимущества:**

- ✅ Автоматическая генерация OpenAPI спецификации
- ✅ Интерактивная документация (Swagger UI)
- ✅ Валидация запросов/ответов
- ✅ Автоматические тесты из документации

#### **Django REST Framework (Python)**

```python
from rest_framework import serializers, viewsets
from drf_spectacular.views import SpectacularAPIView

class WorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workflow
        fields = '__all__'

class WorkflowViewSet(viewsets.ModelViewSet):
    queryset = Workflow.objects.all()
    serializer_class = WorkflowSerializer
```

### **2. TypeScript/JavaScript подходы**

#### **TypeDoc (TypeScript)**

```typescript
/**
 * MCP Workflow Executor
 * @description Executes MCP workflows with automatic documentation
 */
export class MCPWorkflowExecutor {
  /**
   * Execute a workflow
   * @param workflowName - Name of the workflow to execute
   * @param arguments - Arguments for the workflow
   * @returns Promise<WorkflowResult>
   */
  async executeWorkflow(
    workflowName: string,
    arguments: WorkflowArgs,
  ): Promise<WorkflowResult> {
    // Implementation
  }
}
```

#### **JSDoc + Swagger (Node.js)**

```javascript
/**
 * @swagger
 * /api/workflows:
 *   post:
 *     summary: Execute MCP workflow
 *     tags: [Workflows]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               command:
 *                 type: string
 *               arguments:
 *                 type: object
 */
app.post("/api/workflows", executeWorkflow);
```

### **3. Python-специфичные подходы**

#### **Sphinx + autodoc**

```python
# conf.py
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
]

# В коде
class MCPWorkflow:
    """
    MCP Workflow base class with automatic documentation.

    This class provides the foundation for all MCP workflows
    with automatic Sphinx documentation generation.

    Attributes:
        name (str): The name of the workflow
        version (str): The version of the workflow

    Example:
        >>> workflow = MCPWorkflow("telegram", "1.0.0")
        >>> result = await workflow.execute({"command": "get_chats"})
    """

    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version

    async def execute(self, arguments: dict) -> dict:
        """
        Execute the workflow with given arguments.

        Args:
            arguments: Dictionary containing workflow arguments

        Returns:
            dict: Result of workflow execution

        Raises:
            WorkflowError: If workflow execution fails
        """
        pass
```

#### **MkDocs + Material**

```yaml
# mkdocs.yml
site_name: Heroes MCP Server
theme:
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - search.highlight

plugins:
  - search
  - mkdocstrings:
      default_handler: python
      handlers:
        python:
          paths: [src]
          options:
            show_source: true
            show_root_heading: true
```

### **4. Инновационные подходы**

#### **GitBook + GitHub Actions**

```yaml
# .github/workflows/docs.yml
name: Update Documentation
on:
  push:
    branches: [main]
    paths: ["src/**", "docs/**"]

jobs:
  update-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Generate API docs
        run: |
          python scripts/generate_api_docs.py
          python scripts/update_dependencies_matrix.py
      - name: Deploy to GitBook
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
```

#### **Docusaurus + MDX**

````jsx
// docs/api/workflows.mdx
import ApiDocMixin from '@theme/ApiDocMixin';

# MCP Workflows API

<ApiDocMixin id="workflows" />

## Example Usage

```python
from mcp_server import MCPWorkflow

workflow = MCPWorkflow("telegram")
result = await workflow.execute({
    "command": "get_chats",
    "arguments": {"limit": 10}
})
````

```

## 🔧 **Практические решения для нашего проекта**

### **1. Интегрированная система документации**

#### **Структура автоматической документации:**
```

[standards .md]/platform/mcp_server/
├── docs/
│ ├── api/ # Автоматически генерируемая API документация
│ │ ├── workflows.md # Из docstrings
│ │ ├── tools.md # Из MCP tools
│ │ └── schemas.md # Из Pydantic моделей
│ ├── architecture/ # Архитектурная документация
│ │ ├── dependencies_matrix.md # Автоматически обновляемая
│ │ ├── workflow_diagram.md # Из кода
│ │ └── system_overview.md # Ручная документация
│ └── guides/ # Руководства пользователя
├── scripts/
│ ├── generate_api_docs.py # Генерация API документации
│ ├── update_dependencies_matrix.py # Обновление матрицы зависимостей
│ ├── extract_docstrings.py # Извлечение docstrings
│ └── validate_docs.py # Валидация документации
└── mkdocs.yml # Конфигурация MkDocs

````

#### **Автоматический генератор API документации:**
```python
#!/usr/bin/env python3
"""
API Documentation Generator
Автоматически генерирует API документацию из кода
"""

import ast
import inspect
from pathlib import Path
from typing import Dict, List, Any

class APIDocGenerator:
    """Генератор API документации из Python кода"""

    def __init__(self, src_path: Path, docs_path: Path):
        self.src_path = src_path
        self.docs_path = docs_path

    def extract_docstrings(self, file_path: Path) -> Dict[str, Any]:
        """Извлекает docstrings из Python файла"""
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())

        docstrings = {}

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                if ast.get_docstring(node):
                    docstrings[node.name] = {
                        'docstring': ast.get_docstring(node),
                        'type': type(node).__name__,
                        'file': file_path.name
                    }

        return docstrings

    def generate_workflow_docs(self) -> str:
        """Генерирует документацию для workflow"""
        workflows_path = self.src_path / "workflows"
        docs = []

        for py_file in workflows_path.glob("*.py"):
            if py_file.name.startswith('_'):
                continue

            docstrings = self.extract_docstrings(py_file)

            for name, info in docstrings.items():
                if info['type'] == 'ClassDef':
                    docs.append(f"""
## {name}

{info['docstring']}

**File:** `{info['file']}`

### Methods

""")

        return "\n".join(docs)

    def generate_tools_docs(self) -> str:
        """Генерирует документацию для MCP tools"""
        # Извлекаем информацию о tools из mcp_server.py
        server_file = self.src_path / "mcp_server.py"

        # Парсим _workflow_spec для получения информации о tools
        # Генерируем документацию

        return "# MCP Tools Documentation\n\n..."

    def update_all_docs(self):
        """Обновляет всю документацию"""
        # Генерируем API документацию
        api_docs = self.generate_workflow_docs()
        tools_docs = self.generate_tools_docs()

        # Записываем файлы
        (self.docs_path / "api" / "workflows.md").write_text(api_docs)
        (self.docs_path / "api" / "tools.md").write_text(tools_docs)

        print("✅ API documentation updated")

def main():
    generator = APIDocGenerator(
        Path("src"),
        Path("docs")
    )
    generator.update_all_docs()

if __name__ == "__main__":
    main()
````

### **2. Интеграция с CI/CD**

#### **GitHub Actions для автоматической документации:**

```yaml
# .github/workflows/docs.yml
name: Update Documentation
on:
  push:
    branches: [main]
    paths: ["src/**", "docs/**"]
  pull_request:
    branches: [main]

jobs:
  update-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install mkdocs mkdocs-material pydantic

      - name: Generate API documentation
        run: |
          python scripts/generate_api_docs.py

      - name: Update dependencies matrix
        run: |
          python scripts/update_dependencies_matrix.py

      - name: Validate documentation
        run: |
          python scripts/validate_docs.py

      - name: Build documentation
        run: |
          mkdocs build

      - name: Deploy to GitHub Pages
        if: github.ref == 'refs/heads/main'
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./site
```

### **3. Валидация документации**

#### **Скрипт валидации документации:**

```python
#!/usr/bin/env python3
"""
Documentation Validator
Проверяет актуальность и качество документации
"""

import re
from pathlib import Path
from typing import List, Dict

class DocValidator:
    """Валидатор документации"""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def check_docstring_coverage(self) -> Dict[str, float]:
        """Проверяет покрытие кода docstrings"""
        python_files = list(self.project_root.rglob("*.py"))
        documented_functions = 0
        total_functions = 0

        for py_file in python_files:
            if "test" in py_file.name or "migrations" in str(py_file):
                continue

            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Подсчитываем функции и классы
            function_pattern = r'^def\s+\w+'
            class_pattern = r'^class\s+\w+'

            functions = re.findall(function_pattern, content, re.MULTILINE)
            classes = re.findall(class_pattern, content, re.MULTILINE)

            total_functions += len(functions) + len(classes)

            # Подсчитываем docstrings
            docstring_pattern = r'""".*?"""'
            docstrings = re.findall(docstring_pattern, content, re.DOTALL)

            documented_functions += len(docstrings)

        coverage = (documented_functions / total_functions * 100) if total_functions > 0 else 0

        return {
            "coverage_percentage": coverage,
            "documented_functions": documented_functions,
            "total_functions": total_functions
        }

    def check_broken_links(self) -> List[str]:
        """Проверяет сломанные ссылки в документации"""
        broken_links = []

        for md_file in self.project_root.rglob("*.md"):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Ищем ссылки на файлы
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            links = re.findall(link_pattern, content)

            for link_text, link_url in links:
                if link_url.startswith('http'):
                    continue

                # Проверяем существование файла
                if not (self.project_root / link_url).exists():
                    broken_links.append(f"{md_file}: {link_text} -> {link_url}")

        return broken_links

    def validate_all(self) -> Dict[str, Any]:
        """Выполняет все проверки документации"""
        results = {
            "docstring_coverage": self.check_docstring_coverage(),
            "broken_links": self.check_broken_links(),
            "status": "passed"
        }

        # Определяем статус
        if results["docstring_coverage"]["coverage_percentage"] < 80:
            results["status"] = "warning"

        if results["broken_links"]:
            results["status"] = "failed"

        return results

def main():
    validator = DocValidator(Path("."))
    results = validator.validate_all()

    print(f"📊 Documentation Validation Results:")
    print(f"Docstring Coverage: {results['docstring_coverage']['coverage_percentage']:.1f}%")
    print(f"Broken Links: {len(results['broken_links'])}")
    print(f"Status: {results['status']}")

    if results['broken_links']:
        print("\n❌ Broken Links:")
        for link in results['broken_links']:
            print(f"  - {link}")

    if results['status'] == 'failed':
        exit(1)

if __name__ == "__main__":
    main()
```

## 🎯 **Рекомендации для нашего проекта**

### **1. Немедленные действия:**

#### **Создать интегрированную систему документации:**

```bash
# Структура
mkdir -p docs/{api,architecture,guides}
mkdir -p scripts/documentation

# Скрипты
touch scripts/generate_api_docs.py
touch scripts/validate_docs.py
touch mkdocs.yml
```

#### **Добавить в Makefile:**

```makefile
# Documentation
docs-generate:
 @echo "📚 Generating API documentation..."
 python scripts/generate_api_docs.py
 python scripts/update_dependencies_matrix.py

docs-validate:
 @echo "🔍 Validating documentation..."
 python scripts/validate_docs.py

docs-build:
 @echo "🏗️ Building documentation..."
 mkdocs build

docs-serve:
 @echo "🌐 Serving documentation..."
 mkdocs serve

docs: docs-generate docs-validate docs-build
 @echo "✅ Documentation updated"
```

### **2. Долгосрочные улучшения:**

#### **Интеграция с IDE:**

- **VSCode Extensions:** Python Docstring Generator, Markdown All in One
- **Pre-commit hooks:** Автоматическая проверка docstrings
- **Git hooks:** Автоматическое обновление документации при коммите

#### **Мониторинг качества:**

- **Coverage tracking:** Отслеживание покрытия документацией
- **Broken link detection:** Автоматическое обнаружение сломанных ссылок
- **Documentation freshness:** Проверка актуальности документации

## 🔗 **Полезные ресурсы**

### **Инструменты:**

- [MkDocs](https://www.mkdocs.org/) - Статический генератор документации
- [Sphinx](https://www.sphinx-doc.org/) - Продвинутый генератор документации
- [TypeDoc](https://typedoc.org/) - Генератор документации для TypeScript
- [JSDoc](https://jsdoc.app/) - Документирование JavaScript

### **Подходы:**

- [Documentation-Driven Development](https://en.wikipedia.org/wiki/Documentation-driven_development)
- [API-First Design](https://swagger.io/blog/api-design/api-first-design/)
- [Living Documentation](https://martinfowler.com/bliki/LivingDocumentation.html)

---

**Статус:** Research завершен
**Следующий шаг:** Внедрить интегрированную систему документации
