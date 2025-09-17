#!/usr/bin/env python3
"""
HeroesGPT Documentation Manager

JTBD: Как MCP сервер, я хочу управлять документацией mkdocs,
чтобы автоматически собирать и деплоить документацию из markdown файлов.

Основано на deploy_and_test.py из rickai-mkdocs
"""

import asyncio
import logging
import subprocess
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class MkDocsBuilder:
    """Сборщик документации MkDocs"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.site_dir = self.project_path / "site"

    async def build(self, clean: bool = True) -> dict[str, Any]:
        """
        JTBD: Как сборщик документации, я хочу собрать mkdocs проект,
        чтобы создать статический сайт из markdown файлов.
        """
        if clean and self.site_dir.exists():
            import shutil

            shutil.rmtree(self.site_dir)

        try:
            result = subprocess.run(
                ["mkdocs", "build"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "site_path": str(self.site_dir),
                    "message": "Documentation built successfully",
                }
            else:
                return {"success": False, "error": f"Build failed: {result.stderr}"}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Build timeout after 60 seconds"}
        except Exception as e:
            return {"success": False, "error": f"Build error: {str(e)}"}

    async def serve(self, port: int = 8000) -> dict[str, Any]:
        """
        JTBD: Как сервер документации, я хочу запустить локальный сервер,
        чтобы пользователь мог просматривать документацию в браузере.
        """
        try:
            process = subprocess.Popen(
                ["mkdocs", "serve", "--port", str(port)],
                cwd=self.project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Ждем немного для запуска сервера
            await asyncio.sleep(2)

            if process.poll() is None:
                return {
                    "success": True,
                    "port": port,
                    "url": f"http://localhost:{port}",
                    "pid": process.pid,
                    "message": f"Server started on port {port}",
                }
            else:
                stdout, stderr = process.communicate()
                return {"success": False, "error": f"Server failed to start: {stderr}"}
        except Exception as e:
            return {"success": False, "error": f"Server error: {str(e)}"}


class SymlinkManager:
    """Управление символическими ссылками"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.docs_dir = self.project_path / "docs"

    async def create_symlink(
        self, source_path: str, target_path: str
    ) -> dict[str, Any]:
        """
        JTBD: Как менеджер ссылок, я хочу создать символическую ссылку,
        чтобы избежать дублирования файлов в документации.
        """
        try:
            source = Path(source_path)
            target = self.docs_dir / target_path

            if not source.exists():
                return {
                    "success": False,
                    "error": f"Source file not found: {source_path}",
                }

            if target.exists():
                target.unlink()

            target.parent.mkdir(parents=True, exist_ok=True)
            target.symlink_to(source)

            return {
                "success": True,
                "source": str(source),
                "target": str(target),
                "message": "Symlink created successfully",
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to create symlink: {str(e)}"}

    async def list_symlinks(self) -> dict[str, Any]:
        """
        JTBD: Как менеджер ссылок, я хочу получить список всех ссылок,
        чтобы пользователь мог видеть структуру документации.
        """
        try:
            symlinks = []
            for file_path in self.docs_dir.rglob("*"):
                if file_path.is_symlink():
                    symlinks.append(
                        {
                            "name": file_path.name,
                            "path": str(file_path),
                            "target": str(file_path.resolve()),
                            "size": (
                                file_path.stat().st_size if file_path.exists() else 0
                            ),
                        }
                    )

            return {"success": True, "count": len(symlinks), "symlinks": symlinks}
        except Exception as e:
            return {"success": False, "error": f"Failed to list symlinks: {str(e)}"}


class DocumentationManager:
    """Главный менеджер документации"""

    def __init__(self, project_path: str):
        self.project_path = project_path
        self.builder = MkDocsBuilder(project_path)
        self.symlink_manager = SymlinkManager(project_path)

    async def build_documentation(self, clean: bool = True) -> dict[str, Any]:
        """Сборка документации"""
        return await self.builder.build(clean)

    async def serve_documentation(self, port: int = 8000) -> dict[str, Any]:
        """Запуск сервера документации"""
        return await self.builder.serve(port)

    async def create_symlink(
        self, source_path: str, target_path: str
    ) -> dict[str, Any]:
        """Создание символической ссылки"""
        return await self.symlink_manager.create_symlink(source_path, target_path)

    async def list_symlinks(self) -> dict[str, Any]:
        """Список символических ссылок"""
        return await self.symlink_manager.list_symlinks()

    async def validate_project(self) -> dict[str, Any]:
        """
        JTBD: Как валидатор проекта, я хочу проверить корректность mkdocs проекта,
        чтобы убедиться в готовности к сборке документации.
        """
        try:
            mkdocs_yml = Path(self.project_path) / "mkdocs.yml"
            if not mkdocs_yml.exists():
                return {"success": False, "error": "mkdocs.yml not found"}

            docs_dir = Path(self.project_path) / "docs"
            if not docs_dir.exists():
                return {"success": False, "error": "docs directory not found"}

            # Проверяем наличие markdown файлов
            md_files = list(docs_dir.rglob("*.md"))
            if not md_files:
                return {
                    "success": False,
                    "error": "No markdown files found in docs directory",
                }

            return {
                "success": True,
                "mkdocs_yml": str(mkdocs_yml),
                "docs_dir": str(docs_dir),
                "markdown_files": len(md_files),
                "message": "Project validation passed",
            }
        except Exception as e:
            return {"success": False, "error": f"Validation error: {str(e)}"}


# ЕДИНСТВЕННАЯ публичная MCP функция
async def make_mkdoc(project_path: str, clean: bool = True) -> dict[str, Any]:
    """
    JTBD: Как пользователь, я хочу собрать документацию MkDocs,
    чтобы получить актуальную документацию из markdown файлов.

    Args:
        project_path: Путь к проекту с mkdocs.yml
        clean: Очищать предыдущую сборку

    Returns:
        Dict с результатами сборки
    """
    manager = DocumentationManager(project_path)

    # Валидация проекта
    validation = await manager.validate_project()
    if not validation["success"]:
        return validation

    # Сборка документации
    result = await manager.build_documentation(clean)
    return result


# Внутренние функции для тестирования (НЕ MCP команды)
async def _serve_mkdocs_documentation(
    project_path: str, port: int = 8000
) -> dict[str, Any]:
    """Внутренняя функция для запуска сервера (НЕ MCP команда)"""
    manager = DocumentationManager(project_path)
    return await manager.serve_documentation(port)


async def _create_documentation_symlink(
    project_path: str, source_path: str, target_path: str
) -> dict[str, Any]:
    """Внутренняя функция для создания ссылок (НЕ MCP команда)"""
    manager = DocumentationManager(project_path)
    return await manager.create_symlink(source_path, target_path)


async def _list_documentation_symlinks(project_path: str) -> dict[str, Any]:
    """Внутренняя функция для списка ссылок (НЕ MCP команда)"""
    manager = DocumentationManager(project_path)
    return await manager.list_symlinks()


async def _validate_documentation_project(project_path: str) -> dict[str, Any]:
    """Внутренняя функция для валидации (НЕ MCP команда)"""
    manager = DocumentationManager(project_path)
    return await manager.validate_project()
