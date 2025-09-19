#!/usr/bin/env python3
"""
CLI для управления документацией Heroes Platform.

Использует только отраслевые стандарты:
- Typer для CLI
- MkDocs для документации
- Rich для красивого вывода
"""

import subprocess
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

app = typer.Typer(help="Heroes Platform Documentation CLI")
console = Console()


@app.command()
def build():
    """Сборка документации с MkDocs."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Сборка документации...", total=None)

        try:
            result = subprocess.run(
                ["mkdocs", "build"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent,
            )

            if result.returncode == 0:
                progress.update(task, description="✅ Документация собрана успешно")
                console.print(
                    Panel(
                        "Документация собрана в папке site/",
                        title="🎉 Успех",
                        border_style="green",
                    )
                )
            else:
                progress.update(task, description="ERROR: Ошибка сборки")
                console.print(
                    Panel(result.stderr, title="ERROR: Ошибка", border_style="red")
                )
                sys.exit(1)

        except FileNotFoundError:
            progress.update(task, description="ERROR: MkDocs не найден")
            console.print(
                Panel(
                    "Установите MkDocs: pip install mkdocs mkdocstrings[python] mkdocs-material",
                    title="ERROR: MkDocs не установлен",
                    border_style="red",
                )
            )
            sys.exit(1)


@app.command()
def serve():
    """Запуск локального сервера документации."""
    console.print(
        Panel(
            "Запуск сервера документации на http://localhost:8000",
            title="🚀 MkDocs Server",
            border_style="blue",
        )
    )

    try:
        subprocess.run(["mkdocs", "serve"], cwd=Path(__file__).parent)
    except KeyboardInterrupt:
        console.print("\nSTOPPED: Сервер остановлен")
    except FileNotFoundError:
        console.print(
            Panel(
                "Установите MkDocs: pip install mkdocs mkdocstrings[python] mkdocs-material",
                title="ERROR: MkDocs не установлен",
                border_style="red",
            )
        )
        sys.exit(1)


@app.command()
def validate():
    """Валидация документации."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Валидация документации...", total=None)

        try:
            result = subprocess.run(
                ["mkdocs", "build", "--strict"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent,
            )

            if result.returncode == 0:
                progress.update(task, description="✅ Валидация пройдена")
                console.print(
                    Panel(
                        "Документация прошла строгую валидацию",
                        title="✅ Валидация",
                        border_style="green",
                    )
                )
            else:
                progress.update(task, description="ERROR: Ошибки валидации")
                console.print(
                    Panel(
                        result.stderr,
                        title="ERROR: Ошибки валидации",
                        border_style="red",
                    )
                )
                sys.exit(1)

        except FileNotFoundError:
            progress.update(task, description="ERROR: MkDocs не найден")
            console.print(
                Panel(
                    "Установите MkDocs: pip install mkdocs mkdocstrings[python] mkdocs-material",
                    title="ERROR: MkDocs не установлен",
                    border_style="red",
                )
            )
            sys.exit(1)


@app.command()
def status():
    """Статус документации."""
    site_dir = Path(__file__).parent / "site"

    table = Table(title="📊 Статус документации")
    table.add_column("Метрика", style="cyan")
    table.add_column("Значение", style="magenta")

    if site_dir.exists():
        html_files = list(site_dir.rglob("*.html"))
        total_size = sum(f.stat().st_size for f in html_files)

        table.add_row("Собрана", "✅ Да")
        table.add_row("HTML файлов", str(len(html_files)))
        table.add_row("Общий размер", f"{total_size / 1024:.1f} KB")
        table.add_row("Папка", str(site_dir))
    else:
        table.add_row("Собрана", "ERROR: Нет")
        table.add_row("HTML файлов", "0")
        table.add_row("Общий размер", "0 KB")
        table.add_row("Папка", "Не найдена")

    console.print(table)


@app.command()
def clean():
    """Очистка собранной документации."""
    site_dir = Path(__file__).parent / "site"

    if site_dir.exists():
        import shutil

        shutil.rmtree(site_dir)
        console.print(
            Panel(
                f"Папка {site_dir} удалена", title="🧹 Очистка", border_style="yellow"
            )
        )
    else:
        console.print(
            Panel("Папка site/ не найдена", title="ℹ️ Информация", border_style="blue")
        )


if __name__ == "__main__":
    app()
