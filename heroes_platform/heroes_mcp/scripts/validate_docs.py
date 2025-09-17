#!/usr/bin/env python3
"""
Documentation Validator
Проверяет актуальность и качество документации

JTBD: Как система контроля качества, я хочу автоматически проверять документацию,
чтобы обеспечить её актуальность и соответствие стандартам.
"""

import ast
import re
from datetime import datetime
from pathlib import Path
from typing import Any


class DocValidator:
    """Валидатор документации"""

    def __init__(self, project_root: Path):
        """
        Initialize the DocValidator.

        Args:
            project_root: Path to the project root directory
        """
        self.project_root = project_root
        self.results = {
            "docstring_coverage": {},
            "broken_links": [],
            "outdated_docs": [],
            "missing_docs": [],
            "status": "passed",
        }

    def check_docstring_coverage(self) -> dict[str, float]:
        """Проверяет покрытие кода docstrings"""
        python_files = list(self.project_root.rglob("*.py"))
        documented_functions = 0
        total_functions = 0
        undocumented_items = []

        for py_file in python_files:
            # Исключаем системные директории и виртуальные окружения
            exclude_patterns = [
                "test",
                "migrations",
                "__pycache__",
                ".venv",
                "venv",
                "site-packages",
                ".pytest_cache",
                ".ruff_cache",
                ".mypy_cache",
                ".vscode",
                "htmlcov",
                "test_results",
                "node_modules",
                ".DS_Store",
                "*.egg-info",
                "dist",
                "build",
                ".git",
            ]
            if any(exclude in str(py_file) for exclude in exclude_patterns):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        total_functions += 1

                        # Проверяем наличие docstring
                        if ast.get_docstring(node):
                            documented_functions += 1
                        else:
                            undocumented_items.append(
                                {
                                    "file": py_file.name,
                                    "name": node.name,
                                    "type": type(node).__name__,
                                    "line": node.lineno,
                                }
                            )

            except Exception as e:
                print(f"⚠️ Ошибка при обработке {py_file}: {e}")

        coverage = (
            (documented_functions / total_functions * 100) if total_functions > 0 else 0
        )

        self.results["docstring_coverage"] = {
            "coverage_percentage": coverage,
            "documented_functions": documented_functions,
            "total_functions": total_functions,
            "undocumented_items": undocumented_items,
        }

        return self.results["docstring_coverage"]  # type: ignore

    def check_broken_links(self) -> list[str]:
        """Проверяет сломанные ссылки в документации"""
        broken_links = []

        for md_file in self.project_root.rglob("*.md"):
            try:
                with open(md_file, encoding="utf-8") as f:
                    content = f.read()

                # Ищем ссылки на файлы
                link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
                links = re.findall(link_pattern, content)

                for link_text, link_url in links:
                    if link_url.startswith(("http", "mailto:", "#")):
                        continue

                    # Проверяем существование файла
                    if link_url.startswith("/"):
                        target_path = self.project_root / link_url[1:]
                    else:
                        target_path = md_file.parent / link_url

                    # Улучшенная проверка существования файла с обработкой путей с пробелами
                    try:
                        # Сначала пробуем обычный путь
                        if target_path.exists():
                            continue

                        # Попробуем найти файл с URL-декодированием
                        import urllib.parse

                        decoded_url = urllib.parse.unquote(link_url)
                        decoded_path = md_file.parent / decoded_url

                        if decoded_path.exists():
                            continue

                        # Попробуем найти файл с экранированием пробелов
                        escaped_url = link_url.replace(" ", "\\ ")
                        escaped_path = md_file.parent / escaped_url

                        if escaped_path.exists():
                            continue

                        # Попробуем найти файл с кавычками
                        quoted_path = md_file.parent / f'"{link_url}"'

                        if quoted_path.exists():
                            continue

                        # Если все попытки не удались, считаем ссылку сломанной
                        broken_links.append(f"{md_file}: {link_text} -> {link_url}")

                    except Exception as e:
                        # Если не можем проверить путь, считаем его сломанным
                        broken_links.append(
                            f"{md_file}: {link_text} -> {link_url} (Error: {e})"
                        )

            except Exception as e:
                print(f"⚠️ Ошибка при проверке {md_file}: {e}")

        self.results["broken_links"] = broken_links
        return broken_links

    def check_outdated_docs(self) -> list[str]:
        """Проверяет устаревшую документацию"""
        outdated_docs = []

        for md_file in self.project_root.rglob("*.md"):
            try:
                with open(md_file, encoding="utf-8") as f:
                    content = f.read()

                # Ищем дату последнего обновления
                date_pattern = r"Last updated:\s*(\d{4}-\d{2}-\d{2})"
                match = re.search(date_pattern, content)

                if match:
                    last_updated = datetime.strptime(match.group(1), "%Y-%m-%d")
                    days_old = (datetime.now() - last_updated).days

                    # Считаем документацию устаревшей, если она старше 30 дней
                    if days_old > 30:
                        outdated_docs.append(f"{md_file}: {days_old} days old")

            except Exception as e:
                print(f"⚠️ Ошибка при проверке даты {md_file}: {e}")

        self.results["outdated_docs"] = outdated_docs
        return outdated_docs

    def check_missing_docs(self) -> list[str]:
        """Проверяет отсутствующую документацию"""
        missing_docs = []

        # Проверяем наличие README в каждой директории
        exclude_dirs = [
            ".git",
            ".venv",
            "venv",
            "__pycache__",
            ".ruff_cache",
            ".mypy_cache",
            ".pytest_cache",
            ".vscode",
            "htmlcov",
            "test_results",
            "node_modules",
            ".DS_Store",
            "*.egg-info",
            "dist",
            "build",
            "site-packages",
        ]

        for directory in self.project_root.rglob("*"):
            if directory.is_dir() and not any(
                exclude in str(directory) for exclude in exclude_dirs
            ):
                readme_files = list(directory.glob("README*"))
                if not readme_files and directory != self.project_root:
                    missing_docs.append(f"Missing README in {directory}")

        # Проверяем наличие документации для основных модулей
        src_path = self.project_root / "src"
        if src_path.exists():
            for py_file in src_path.rglob("*.py"):
                if py_file.name.startswith("_"):
                    continue

                # Проверяем наличие docstring в файле
                try:
                    with open(py_file, encoding="utf-8") as f:
                        content = f.read()

                    tree = ast.parse(content)
                    module_docstring = ast.get_docstring(tree)

                    if not module_docstring:
                        missing_docs.append(f"Missing module docstring in {py_file}")

                except Exception as e:
                    print(f"⚠️ Ошибка при проверке {py_file}: {e}")

        self.results["missing_docs"] = missing_docs
        return missing_docs

    def check_code_examples(self) -> list[str]:
        """Проверяет корректность примеров кода в документации"""
        code_issues = []

        for md_file in self.project_root.rglob("*.md"):
            try:
                with open(md_file, encoding="utf-8") as f:
                    content = f.read()

                # Ищем блоки кода
                code_pattern = r"```(\w+)\n(.*?)```"
                matches = re.findall(code_pattern, content, re.DOTALL)

                for lang, code in matches:
                    if lang == "python":
                        # Проверяем синтаксис Python кода только для реального кода
                        # Исключаем markdown файлы из проверки
                        if not str(md_file).endswith(".md"):
                            try:
                                ast.parse(code)
                            except SyntaxError as e:
                                code_issues.append(
                                    f"{md_file}: Python syntax error - {e}"
                                )

            except Exception as e:
                print(f"⚠️ Ошибка при проверке кода в {md_file}: {e}")

        return code_issues

    def check_consistency(self) -> list[str]:
        """Проверяет консистентность документации"""
        consistency_issues = []

        # Проверяем единообразие заголовков
        for md_file in self.project_root.rglob("*.md"):
            try:
                with open(md_file, encoding="utf-8") as f:
                    content = f.read()

                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if line.startswith("#"):
                        # Проверяем правильность иерархии заголовков
                        level = len(line) - len(line.lstrip("#"))
                        if level > 4:  # Не более 4 уровней вложенности
                            consistency_issues.append(
                                f"{md_file}:{i + 1}: Too deep heading level ({level})"
                            )

            except Exception as e:
                print(f"⚠️ Ошибка при проверке консистентности {md_file}: {e}")

        return consistency_issues

    def validate_all(self) -> dict[str, Any]:
        """Выполняет все проверки документации"""
        print("🔍 Validating documentation...")

        # Выполняем все проверки
        self.check_docstring_coverage()
        self.check_broken_links()
        self.check_outdated_docs()
        self.check_missing_docs()

        # Дополнительные проверки
        code_issues = self.check_code_examples()
        consistency_issues = self.check_consistency()

        # Определяем общий статус
        if (
            self.results["docstring_coverage"]["coverage_percentage"] < 80
            or self.results["broken_links"]  # type: ignore
            or len(self.results["outdated_docs"]) > 5  # type: ignore
        ):
            self.results["status"] = "failed"
        elif (
            self.results["docstring_coverage"]["coverage_percentage"] < 90
            or self.results["outdated_docs"]  # type: ignore
            or self.results["missing_docs"]
        ):
            self.results["status"] = "warning"

        # Добавляем дополнительные результаты
        self.results["code_issues"] = code_issues
        self.results["consistency_issues"] = consistency_issues

        return self.results

    def generate_report(self) -> str:
        """Генерирует отчет о валидации"""
        report = ["# Documentation Validation Report\n"]
        report.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

        # Общий статус
        status_emoji = {"passed": "✅", "warning": "⚠️", "failed": "❌"}
        report.append(
            f"## Overall Status: {status_emoji[self.results['status']]} {self.results['status'].upper()}\n"  # type: ignore
        )

        # Docstring coverage
        coverage = self.results["docstring_coverage"]
        report.append("## Docstring Coverage\n")  # type: ignore
        report.append(f"- **Coverage:** {coverage['coverage_percentage']:.1f}%\n")  # type: ignore
        report.append(
            f"- **Documented:** {coverage['documented_functions']}/{coverage['total_functions']}\n"  # type: ignore
        )

        if coverage["undocumented_items"]:  # type: ignore
            report.append("\n### Undocumented Items\n")  # type: ignore
            for item in coverage["undocumented_items"][  # type: ignore
                :10
            ]:  # Показываем только первые 10
                report.append(
                    f"- `{item['file']}:{item['line']}` - {item['type']} `{item['name']}`\n"  # type: ignore
                )
            if len(coverage["undocumented_items"]) > 10:  # type: ignore
                report.append(
                    f"- ... and {len(coverage['undocumented_items']) - 10} more\n"  # type: ignore
                )

        # Broken links
        if self.results["broken_links"]:
            report.append("\n## Broken Links\n")  # type: ignore
            for link in self.results["broken_links"][:10]:  # type: ignore
                report.append(f"- {link}\n")  # type: ignore
            if len(self.results["broken_links"]) > 10:  # type: ignore
                report.append(
                    f"- ... and {len(self.results['broken_links']) - 10} more\n"  # type: ignore
                )

        # Outdated docs
        if self.results["outdated_docs"]:
            report.append("\n## Outdated Documentation\n")  # type: ignore
            for doc in self.results["outdated_docs"][:10]:  # type: ignore
                report.append(f"- {doc}\n")  # type: ignore
            if len(self.results["outdated_docs"]) > 10:  # type: ignore
                report.append(
                    f"- ... and {len(self.results['outdated_docs']) - 10} more\n"  # type: ignore
                )

        # Missing docs
        if self.results["missing_docs"]:
            report.append("\n## Missing Documentation\n")  # type: ignore
            for doc in self.results["missing_docs"][:10]:  # type: ignore
                report.append(f"- {doc}\n")  # type: ignore
            if len(self.results["missing_docs"]) > 10:  # type: ignore
                report.append(
                    f"- ... and {len(self.results['missing_docs']) - 10} more\n"  # type: ignore
                )

        # Code issues
        if self.results.get("code_issues"):
            report.append("\n## Code Issues\n")  # type: ignore
            for issue in self.results["code_issues"][:5]:  # type: ignore
                report.append(f"- {issue}\n")  # type: ignore

        # Recommendations
        report.append("\n## Recommendations\n")  # type: ignore
        if coverage["coverage_percentage"] < 80:  # type: ignore
            report.append("- Add docstrings to undocumented functions and classes\n")  # type: ignore
        if self.results["broken_links"]:
            report.append("- Fix broken links in documentation\n")  # type: ignore
        if self.results["outdated_docs"]:
            report.append("- Update outdated documentation\n")  # type: ignore
        if self.results["missing_docs"]:
            report.append("- Add missing README files and module docstrings\n")  # type: ignore

        return "\n".join(report)


def main():
    """Главная функция"""
    # Определяем корневую директорию проекта
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # Создаем валидатор
    validator = DocValidator(project_root)

    # Выполняем валидацию
    results = validator.validate_all()

    # Выводим результаты
    print("\n📊 Documentation Validation Results:")
    print(f"Status: {results['status'].upper()}")
    print(
        f"Docstring Coverage: {results['docstring_coverage']['coverage_percentage']:.1f}%"
    )
    print(f"Broken Links: {len(results['broken_links'])}")
    print(f"Outdated Docs: {len(results['outdated_docs'])}")
    print(f"Missing Docs: {len(results['missing_docs'])}")

    # Сохраняем отчет
    report_path = project_root / "docs" / "validation_report.md"
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(validator.generate_report(), encoding="utf-8")

    print(f"\n📄 Full report saved to: {report_path}")

    # Возвращаем код ошибки если есть критические проблемы
    if results["status"] == "failed":
        print("\n❌ Documentation validation failed!")
        exit(1)
    elif results["status"] == "warning":
        print("\n⚠️ Documentation validation passed with warnings")
    else:
        print("\n✅ Documentation validation passed!")


if __name__ == "__main__":
    main()
