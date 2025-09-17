#!/usr/bin/env python3
"""
Markdown MkDocs Workflow

JTBD: Как продакт, я хочу публиковать .md документы,
чтобы они были чистыми и красивыми для пользователей с инструкциями, анализами и планами.

Основан на существующих скриптах:
- rickai-mkdocs/deploy_and_test.py
- rickai-mkdocs/create_symlinks.py
"""

import json
import logging
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MkDocsConfig(BaseModel):
    """Конфигурация MkDocs проекта"""

    project_path: str = Field(description="Путь к проекту с mkdocs.yml")
    clean: bool = Field(default=True, description="Очищать предыдущую сборку")
    github_repo: str = Field(
        default="idkras/cursor-template-project", description="GitHub репозиторий"
    )
    github_pages_url: str = Field(
        default="https://idkras.github.io/cursor-template-project/",
        description="URL GitHub Pages",
    )


class MkDocsResult(BaseModel):
    """Результат выполнения MkDocs операции"""

    status: str = Field(description="Статус операции")
    operation: str = Field(description="Тип операции")
    project_path: str = Field(description="Путь к проекту")
    output_path: Optional[str] = Field(default=None, description="Путь к результату")
    deploy_url: Optional[str] = Field(default=None, description="URL деплоя")
    execution_time: float = Field(description="Время выполнения")
    timestamp: str = Field(description="Временная метка")
    validation_result: Optional[dict[str, Any]] = Field(
        default=None, description="Результаты валидации"
    )


class SymlinkManager:
    """Управление символическими ссылками для mkdocs"""

    def __init__(self, mkdocs_root: Path):
        self.mkdocs_root = mkdocs_root
        self.docs_dir = mkdocs_root / "docs"
        self.technical_dir = self.docs_dir / "technical"

    def create_symlink(self, source_path: str, target_name: str) -> bool:
        """Создать символическую ссылку"""
        try:
            source_file = Path(source_path)
            target_file = self.technical_dir / target_name

            if not source_file.exists():
                logger.error(f"❌ Исходный файл не найден: {source_path}")
                return False

            if target_file.exists() and not target_file.is_symlink():
                logger.warning(f"⚠️ Удаляю копию файла: {target_file}")
                target_file.unlink()

            relative_path = os.path.relpath(source_file, target_file.parent)
            target_file.symlink_to(relative_path)

            logger.info(f"✅ Создана ссылка: {target_name} -> {relative_path}")
            return True

        except Exception as e:
            logger.error(f"❌ Ошибка создания ссылки: {e}")
            return False


class MarkdownMkDocWorkflow:
    """
    JTBD: Как продакт, я хочу публиковать .md документы,
    чтобы они были чистыми и красивыми для пользователей с инструкциями, анализами и планами.
    """

    def __init__(self):
        self.config = None
        self.symlink_manager = None

    async def _atomic_validate_mkdocs_project(self, project_path: str) -> None:
        """Атомарная валидация MkDocs проекта"""
        project_dir = Path(project_path)
        mkdocs_yml = project_dir / "mkdocs.yml"

        if not project_dir.exists():
            raise ValueError(f"Проект не найден: {project_path}")

        if not mkdocs_yml.exists():
            raise ValueError(f"mkdocs.yml не найден в: {project_path}")

        logger.info(f"MkDocs project validation passed: {project_path}")

    async def _atomic_create_symlinks(self, project_path: str) -> None:
        """Атомарное создание символических ссылок"""
        project_dir = Path(project_path)
        self.symlink_manager = SymlinkManager(project_dir)

        # Создаем техническую директорию если её нет
        technical_dir = project_dir / "docs" / "technical"
        technical_dir.mkdir(parents=True, exist_ok=True)

        # Создаем ссылки на существующие документы
        symlink_mappings: dict[str, str] = {
            # Временно отключено: "vipavenue_adjust_appmetrica.md": "../../[rick.ai]/knowledge base/in progress/1. when new lead come/when mobile · appmetric · ajust/vipavenue.ru/vipavenue.adjust_appmetrica.md"
        }

        for target_name, source_path in symlink_mappings.items():
            full_source_path = project_dir.parent.parent / source_path
            if full_source_path.exists():
                self.symlink_manager.create_symlink(str(full_source_path), target_name)

        logger.info("Symlinks creation completed")

    async def _atomic_build_mkdocs(
        self, project_path: str, clean: bool
    ) -> MkDocsResult:
        """Атомарная сборка MkDocs"""
        start_time = time.time()

        try:
            # Создаем символические ссылки
            await self._atomic_create_symlinks(project_path)

            # Очищаем предыдущую сборку если нужно
            if clean:
                site_dir = Path(project_path) / "site"
                if site_dir.exists():
                    import shutil

                    shutil.rmtree(site_dir)
                    logger.info("Previous build cleaned")

            # Собираем документацию
            subprocess.run(
                ["mkdocs", "build"],
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True,
            )

            execution_time = time.time() - start_time
            output_path = str(Path(project_path) / "site")

            logger.info("Build result validation passed")

            return MkDocsResult(
                status="success",
                operation="make_mkdoc",
                project_path=project_path,
                output_path=output_path,
                execution_time=execution_time,
                timestamp=datetime.now().isoformat(),
            )

        except subprocess.CalledProcessError as e:
            execution_time = time.time() - start_time
            logger.error(f"Build failed: {e.stderr}")
            raise Exception(f"MkDocs build failed: {e.stderr}")

    async def _atomic_validate_build_result(self, result: MkDocsResult) -> None:
        """Атомарная валидация результата сборки"""
        output_path = Path(result.output_path) if result.output_path else Path(".")

        if not output_path.exists():
            raise ValueError("Build output directory not found")

        index_html = output_path / "index.html"
        if not index_html.exists():
            raise ValueError("index.html not found in build output")

        logger.info("Build result validation passed")

    async def _atomic_deploy_to_github_pages(
        self, project_path: str, build_result: MkDocsResult
    ) -> dict[str, Any]:
        """Атомарный деплой на GitHub Pages"""
        start_time = time.time()

        try:
            # Проверяем, есть ли отдельный репозиторий для документации
            rickai_mkdocs_path = Path(project_path).resolve() / "rickai-mkdocs"

            if rickai_mkdocs_path.exists():
                # Используем существующую архитектуру rickai-mkdocs
                logger.info("Using rickai-mkdocs deployment architecture")
                deploy_url = "https://idkras.github.io/rickai-docs/"
                method = "rickai-mkdocs"

                # Копируем собранные файлы в rickai-mkdocs
                source_site = Path(project_path) / "site"
                target_site = rickai_mkdocs_path / "site"

                if target_site.exists():
                    import shutil

                    shutil.rmtree(target_site)
                    logger.info("Removed existing site directory in rickai-mkdocs")

                shutil.copytree(source_site, target_site)
                logger.info(f"Copied site from {source_site} to {target_site}")

                # Переключаемся в rickai-mkdocs для деплоя
                os.chdir(str(rickai_mkdocs_path))
                logger.info(
                    f"Switched to rickai-mkdocs directory: {rickai_mkdocs_path}"
                )

                # Проверяем статус git в rickai-mkdocs
                result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=rickai_mkdocs_path,
                    capture_output=True,
                    text=True,
                )

                if not result.stdout.strip():
                    logger.info("No changes to commit in rickai-mkdocs")
                    return {
                        "status": "no_changes",
                        "message": "No changes detected in rickai-mkdocs",
                    }

                # Добавляем все файлы в rickai-mkdocs
                subprocess.run(["git", "add", "."], cwd=rickai_mkdocs_path, check=True)

                # Коммитим изменения в rickai-mkdocs
                commit_message = f"Auto-deploy from heroes-platform: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                subprocess.run(
                    ["git", "commit", "-m", commit_message],
                    cwd=rickai_mkdocs_path,
                    check=True,
                )

                # Пушим в rickai-docs репозиторий
                subprocess.run(
                    ["git", "push", "origin", "main"],
                    cwd=rickai_mkdocs_path,
                    check=True,
                )

            else:
                # Используем стандартный деплой в текущий репозиторий
                logger.info("Using standard deployment to current repository")
                deploy_url = "https://idkras.github.io/cursor-template-project/"
                method = "standard"

                # Проверяем статус git
                result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                )

                if not result.stdout.strip():
                    logger.info("No changes to commit")
                    return {"status": "no_changes", "message": "No changes detected"}

                # Добавляем все файлы
                subprocess.run(["git", "add", "."], cwd=project_path, check=True)

                # Коммитим изменения
                commit_message = (
                    f"Auto-deploy: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                subprocess.run(
                    ["git", "commit", "-m", commit_message],
                    cwd=project_path,
                    check=True,
                )

                # Определяем основную ветку автоматически
                branch_result = subprocess.run(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    check=True,
                )
                current_branch = branch_result.stdout.strip()

                # Пушим в GitHub (используем текущую ветку)
                subprocess.run(
                    ["git", "push", "origin", current_branch],
                    cwd=project_path,
                    check=True,
                )

            execution_time = time.time() - start_time

            logger.info(f"Deployed to GitHub Pages: {deploy_url}")

            return {
                "status": "success",
                "deploy_url": deploy_url,
                "method": method,
                "execution_time": execution_time,
                "message": "Successfully deployed to GitHub Pages",
            }

        except subprocess.CalledProcessError as e:
            execution_time = time.time() - start_time
            logger.error(f"Deploy failed: {e}")
            raise Exception(f"GitHub Pages deployment failed: {e}")

    async def _atomic_validate_deploy_result(
        self, deploy_result: dict[str, Any]
    ) -> None:
        """Атомарная валидация результата деплоя"""
        if deploy_result.get("status") != "success":
            raise ValueError(
                f"Deploy failed: {deploy_result.get('message', 'Unknown error')}"
            )

        logger.info("Deploy result validation passed")

    async def make_mkdoc(self, project_path: str, clean: bool = True) -> str:
        """
        JTBD: Как продакт, я хочу собирать .md документы в красивую документацию,
        чтобы пользователи могли легко читать инструкции, анализы и планы.

        Args:
            project_path: Путь к проекту с mkdocs.yml
            clean: Очищать предыдущую сборку

        Returns:
            str: JSON результат сборки
        """
        start_time = time.time()

        try:
            # Атомарные операции
            await self._atomic_validate_mkdocs_project(project_path)
            build_result = await self._atomic_build_mkdocs(project_path, clean)
            await self._atomic_validate_build_result(build_result)

            # Автоматическая валидация локальной документации
            try:
                validation_result = await self._atomic_validate_local_documentation(
                    project_path, build_result
                )
                build_result.validation_result = validation_result
                logger.info(
                    f"Local validation completed: {validation_result.get('validation_status', 'unknown')}"
                )
            except Exception as validation_error:
                logger.warning(f"Local validation failed: {validation_error}")
                build_result.validation_result = {
                    "validation_status": "error",
                    "error": str(validation_error),
                }

            return json.dumps(build_result.dict(), ensure_ascii=False)

        except Exception as e:
            execution_time = time.time() - start_time
            error_result = MkDocsResult(
                status="error",
                operation="make_mkdoc",
                project_path=project_path,
                execution_time=execution_time,
                timestamp=datetime.now().isoformat(),
            )

            logger.error(f"Error in make_mkdoc: {e}")
            return json.dumps(
                {**error_result.dict(), "error": str(e)}, ensure_ascii=False
            )

    async def update_mkdoc(self, project_path: str, clean: bool = True) -> str:
        """
        JTBD: Как продакт, я хочу публиковать обновленные .md документы на GitHub Pages,
        чтобы пользователи всегда имели доступ к актуальным инструкциям, анализам и планам.

        Args:
            project_path: Путь к проекту с mkdocs.yml
            clean: Очищать предыдущую сборку

        Returns:
            str: JSON результат обновления
        """
        start_time = time.time()

        try:
            # Атомарные операции
            await self._atomic_validate_mkdocs_project(project_path)
            build_result = await self._atomic_build_mkdocs(project_path, clean)
            await self._atomic_validate_build_result(build_result)

            deploy_result = await self._atomic_deploy_to_github_pages(
                project_path, build_result
            )
            await self._atomic_validate_deploy_result(deploy_result)

            # Объединяем результаты
            result = MkDocsResult(
                status="success",
                operation="update_mkdoc",
                project_path=project_path,
                output_path=build_result.output_path,
                deploy_url=deploy_result.get("deploy_url"),
                execution_time=time.time() - start_time,
                timestamp=datetime.now().isoformat(),
            )

            return json.dumps(result.dict(), ensure_ascii=False)

        except Exception as e:
            execution_time = time.time() - start_time
            error_result = MkDocsResult(
                status="error",
                operation="update_mkdoc",
                project_path=project_path,
                execution_time=execution_time,
                timestamp=datetime.now().isoformat(),
            )

            logger.error(f"Error in update_mkdoc: {e}")
            return json.dumps(
                {**error_result.dict(), "error": str(e)}, ensure_ascii=False
            )

    async def _atomic_validate_local_documentation(
        self, project_path: str, build_result: MkDocsResult
    ) -> dict[str, Any]:
        """Атомарная валидация локальной документации через validate_actual_outcome"""
        try:
            # Запускаем локальный сервер для валидации
            import subprocess
            import time

            import requests

            # Запускаем mkdocs serve в фоне
            server_process = subprocess.Popen(
                ["mkdocs", "serve", "--dev-addr=127.0.0.1:8000"],
                cwd=project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Ждем запуска сервера
            time.sleep(5)

            # Проверяем доступность сервера
            try:
                response = requests.get("http://127.0.0.1:8000/", timeout=10)
                if response.status_code == 200:
                    logger.info("Local MkDocs server started successfully")

                    # Вызываем validate_actual_outcome MCP команду
                    try:
                        # Импорт MCP команды через workflow
                        from heroes_platform.heroes_mcp.workflows.validate_actual_output_workflow import ValidateActualOutputWorkflow
                        validate_workflow = ValidateActualOutputWorkflow()

                        validation_result = await validate_workflow.execute({
                            "artifact_path": "http://127.0.0.1:8000/",
                            "artifact_type": "url",
                            "expected_features": "documentation, navigation, search",
                            "test_cases": "visual quality, functionality, responsiveness",
                            "take_screenshot": True,
                        })

                        # Останавливаем сервер
                        server_process.terminate()
                        server_process.wait(timeout=10)

                        return {
                            "validation_status": "success",
                            "validation_result": validation_result,
                            "local_url": "http://127.0.0.1:8000/",
                        }

                    except Exception as validation_error:
                        logger.warning(f"Validation failed: {validation_error}")
                        # Останавливаем сервер
                        server_process.terminate()
                        server_process.wait(timeout=10)

                        return {
                            "validation_status": "warning",
                            "validation_error": str(validation_error),
                            "local_url": "http://127.0.0.1:8000/",
                        }

                else:
                    logger.warning(
                        f"Server responded with status: {response.status_code}"
                    )
                    server_process.terminate()
                    server_process.wait(timeout=10)
                    return {
                        "validation_status": "warning",
                        "message": "Server not responding properly",
                    }

            except requests.exceptions.RequestException as e:
                logger.warning(f"Could not connect to local server: {e}")
                server_process.terminate()
                server_process.wait(timeout=10)
                return {
                    "validation_status": "warning",
                    "message": f"Server connection failed: {e}",
                }

        except Exception as e:
            logger.error(f"Local validation failed: {e}")
            return {"validation_status": "error", "error": str(e)}
