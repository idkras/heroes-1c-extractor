#!/usr/bin/env python3
"""
AI Quality Assistant for MCP Server

This script provides AI-powered code quality improvements including:
- Automatic documentation generation
- Duplicate code detection and refactoring
- Code style improvements
- Security vulnerability detection
- Performance optimization suggestions
"""

import argparse
import asyncio
import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console
from rich.table import Table

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()


class AIQualityAssistant:
    """AI-powered quality assistant for code improvement"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.src_path = project_root / "src"
        self.docs_path = project_root / "docs"
        self.quality_report: dict[str, Any] = {}

    async def run_comprehensive_analysis(self) -> dict[str, Any]:
        """Run comprehensive code quality analysis"""
        console.print(
            "[bold blue]🔍 Running comprehensive code quality analysis...[/bold blue]"
        )

        analysis_results = {
            "documentation": await self.analyze_documentation(),
            "duplicates": await self.detect_duplicates(),
            "security": await self.security_scan(),
            "performance": await self.performance_analysis(),
            "style": await self.style_analysis(),
            "ai_suggestions": await self.generate_ai_suggestions(),
        }

        self.quality_report = analysis_results
        return analysis_results

    async def analyze_documentation(self) -> dict[str, Any]:
        """Analyze and improve documentation"""
        console.print("[yellow]📚 Analyzing documentation...[/yellow]")

        results: Dict[str, List[str]] = {"missing_docstrings": [], "outdated_docs": [], "suggestions": []}

        # Check for missing docstrings
        for py_file in self.src_path.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue

            content = py_file.read_text()
            if "def " in content and '"""' not in content and "'''" not in content:
                results["missing_docstrings"].append(str(py_file))

        # Generate documentation suggestions
        if results["missing_docstrings"]:
            results["suggestions"].append(
                "Run 'write-the' to generate missing docstrings automatically"
            )

        return results

    async def detect_duplicates(self) -> dict[str, Any]:
        """Detect duplicate code patterns"""
        console.print("[yellow]🔍 Detecting code duplicates...[/yellow]")

        try:
            # Run jscpd for duplicate detection
            result = subprocess.run(
                ["jscpd", "--threshold", "5", "--reporters", "json"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0 and result.stdout.strip():
                try:
                    duplicates = json.loads(result.stdout)
                    return {
                        "duplicate_files": duplicates.get("duplicates", []),
                        "total_duplicates": len(duplicates.get("duplicates", [])),
                        "suggestions": self._generate_duplicate_suggestions(duplicates),
                    }
                except json.JSONDecodeError:
                    return {
                        "duplicate_files": [],
                        "total_duplicates": 0,
                        "suggestions": [],
                    }
        except FileNotFoundError:
            console.print(
                "[red]⚠️  jscpd not found. Install with: npm install -g jscpd[/red]"
            )

        return {"duplicate_files": [], "total_duplicates": 0, "suggestions": []}

    async def security_scan(self) -> dict[str, Any]:
        """Run security vulnerability scan"""
        console.print("[yellow]🔒 Running security scan...[/yellow]")

        results: Dict[str, List[str]] = {"vulnerabilities": [], "suggestions": []}

        try:
            # Run bandit
            bandit_result = subprocess.run(
                ["bandit", "-r", "src", "-f", "json"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if bandit_result.returncode == 0:
                bandit_data = json.loads(bandit_result.stdout)
                results["vulnerabilities"] = bandit_data.get("results", [])

                if results["vulnerabilities"]:
                    results["suggestions"].append(
                        "Review and fix security vulnerabilities detected by bandit"
                    )
        except FileNotFoundError:
            console.print(
                "[red]⚠️  bandit not found. Install with: pip install bandit[/red]"
            )

        return results

    async def performance_analysis(self) -> dict[str, Any]:
        """Analyze code performance patterns"""
        console.print("[yellow]⚡ Analyzing performance...[/yellow]")

        results: Dict[str, List[str]] = {"performance_issues": [], "suggestions": []}

        # Check for common performance anti-patterns
        performance_patterns = [
            ("import *", "Avoid wildcard imports"),
            ("for i in range(len(", "Use enumerate() instead"),
            ("list.append() in loop", "Consider list comprehension"),
            ("global ", "Avoid global variables"),
        ]

        for py_file in self.src_path.rglob("*.py"):
            content = py_file.read_text()
            for pattern, suggestion in performance_patterns:
                if pattern in content:
                    results["performance_issues"].append(
                        f"{str(py_file)}: {suggestion} (pattern: {pattern})"
                    )

        return results

    async def style_analysis(self) -> dict[str, Any]:
        """Analyze code style and formatting"""
        console.print("[yellow]🎨 Analyzing code style...[/yellow]")

        results: Dict[str, List[str]] = {"style_issues": [], "suggestions": []}

        try:
            # Run ruff
            ruff_result = subprocess.run(
                ["ruff", "check", "src", "--output-format", "json"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if ruff_result.returncode != 0:
                ruff_data = json.loads(ruff_result.stdout)
                results["style_issues"] = ruff_data
                results["suggestions"].append(
                    "Run 'ruff check --fix src' to auto-fix style issues"
                )
        except FileNotFoundError:
            console.print(
                "[red]⚠️  ruff not found. Install with: pip install ruff[/red]"
            )

        return results

    async def generate_ai_suggestions(self) -> dict[str, Any]:
        """Generate AI-powered improvement suggestions"""
        console.print("[yellow]🤖 Generating AI suggestions...[/yellow]")

        suggestions = [
            "Consider using type hints for all function parameters and return values",
            "Add comprehensive error handling with specific exception types",
            "Implement logging with structured JSON format for better observability",
            "Add unit tests for all public functions and methods",
            "Consider using dataclasses for data transfer objects",
            "Implement async/await patterns for I/O operations",
            "Add docstrings following Google or NumPy style",
            "Consider using dependency injection for better testability",
            "Implement proper resource cleanup in context managers",
            "Add performance monitoring and metrics collection",
        ]

        return {"suggestions": suggestions, "priority": "high"}

    def _generate_duplicate_suggestions(self, duplicates: dict[str, Any]) -> list[str]:
        """Generate suggestions for duplicate code"""
        suggestions = []

        if duplicates.get("duplicates"):
            suggestions.append("Consider extracting common code into utility functions")
            suggestions.append(
                "Use inheritance or composition to reduce code duplication"
            )
            suggestions.append(
                "Implement design patterns to share common functionality"
            )

        return suggestions

    def generate_report(self) -> str:
        """Generate comprehensive quality report"""
        console.print("[bold green]📊 Generating quality report...[/bold green]")

        # Create summary table
        table = Table(title="Code Quality Analysis Summary")
        table.add_column("Category", style="cyan")
        table.add_column("Issues Found", style="magenta")
        table.add_column("Status", style="green")

        for category, data in self.quality_report.items():
            if isinstance(data, dict):
                issues_count = len(data.get("suggestions", []))
                status = "⚠️  Needs Attention" if issues_count > 0 else "✅ Good"
                table.add_row(category.title(), str(issues_count), status)

        console.print(table)

        # Generate detailed report
        report_path = self.project_root / "quality_report.md"
        with open(report_path, "w") as f:
            f.write("# Code Quality Report\n\n")

            for category, data in self.quality_report.items():
                f.write(f"## {category.title()}\n\n")

                if isinstance(data, dict):
                    for key, value in data.items():
                        if value:  # Only show non-empty results
                            f.write(f"### {key.replace('_', ' ').title()}\n\n")
                            if isinstance(value, list):
                                for item in value:
                                    f.write(f"- {item}\n")
                            else:
                                f.write(f"{value}\n")
                            f.write("\n")

        console.print(f"[green]✅ Quality report saved to: {report_path}[/green]")
        return str(report_path)

    async def auto_fix_issues(self) -> dict[str, Any]:
        """Automatically fix common issues"""
        console.print("[bold blue]🔧 Running auto-fix...[/bold blue]")

        fixes_applied = {"documentation": False, "style": False, "imports": False}

        try:
            # Auto-fix style issues
            subprocess.run(["ruff", "check", "--fix", "src"], cwd=self.project_root)
            fixes_applied["style"] = True

            # Auto-fix imports
            subprocess.run(
                ["ruff", "check", "--fix", "--select", "I", "src"],
                cwd=self.project_root,
            )
            fixes_applied["imports"] = True

            # Format code
            subprocess.run(["black", "src"], cwd=self.project_root)

        except FileNotFoundError as e:
            console.print(f"[red]❌ Error during auto-fix: {e}[/red]")

        return fixes_applied


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AI Quality Assistant for MCP Server")
    parser.add_argument(
        "--auto-fix", action="store_true", help="Automatically fix common issues"
    )
    parser.add_argument(
        "--generate-docs", action="store_true", help="Generate documentation"
    )
    parser.add_argument(
        "--project-root", type=Path, default=Path.cwd(), help="Project root directory"
    )

    args = parser.parse_args()

    assistant = AIQualityAssistant(args.project_root)

    # Run analysis
    await assistant.run_comprehensive_analysis()

    # Generate report
    assistant.generate_report()

    # Auto-fix if requested
    if args.auto_fix:
        fixes = await assistant.auto_fix_issues()
        console.print(f"[green]✅ Applied fixes: {fixes}[/green]")

    # Generate docs if requested
    if args.generate_docs:
        console.print("[yellow]📚 Generating documentation...[/yellow]")
        try:
            subprocess.run(
                ["sphinx-build", "-b", "html", "docs", "docs/_build/html"],
                cwd=args.project_root,
            )
            console.print("[green]✅ Documentation generated successfully[/green]")
        except FileNotFoundError:
            console.print(
                "[red]❌ Sphinx not found. Install with: pip install sphinx[/red]"
            )


if __name__ == "__main__":
    asyncio.run(main())
