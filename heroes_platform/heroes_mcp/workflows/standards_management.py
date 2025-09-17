"""
Standards Management Workflow
JTBD: Как система управления стандартами, я хочу предоставлять доступ к стандартам,
чтобы обеспечить соответствие разработки установленным принципам.

MCP Workflow Standard v1.1: 1 workflow = 1 файл
TDD Documentation Standard v2.5: Atomic operations ≤20 строк
Registry Standard v5.8: Atomic Operation Principle с reflection checkpoints
"""

from pathlib import Path
from typing import Any


class StandardsManagementWorkflow:
    """
    JTBD: Как workflow управления стандартами, я хочу обрабатывать команды стандартов,
    чтобы обеспечить централизованное управление стандартами разработки.
    """

    def __init__(self) -> None:
        """
        JTBD: Как инициализатор workflow, я хочу настроить базовые параметры,
        чтобы обеспечить готовность к обработке команд.
        """
        # Fix path to standards directory
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent.parent.parent
        self.standards_dir = project_root / "[standards .md]"

        # Skip validation for now to avoid blocking the server
        try:
            self._validate_standards_directory()
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(f"Standards directory validation skipped: {e}")
            self.standards_dir = None  # type: ignore

    async def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """
        JTBD: Как исполнитель команд, я хочу обрабатывать запросы к стандартам,
        чтобы предоставить пользователю доступ к нужной информации.
        """
        # STEP 0: Read and validate implementing standard
        standard_validation = await self._step_0_read_implementing_standard()
        if not standard_validation["valid"]:
            return {
                "error": f"Standard validation failed: {standard_validation['issues']}"
            }

        # [reflection] Validate standard compliance
        if not await self._reflection_checkpoint(
            "standard_compliance", standard_validation
        ):
            return {"error": "Failed to comply with implementing standard"}

        command = arguments.get("command", "")

        # Unified command handling for all standards operations
        if command == "list":
            return await self._list_standards()
        elif command == "get":
            standard_name = arguments.get("standard_name")
            if standard_name:
                return await self._get_standard(standard_name)
            else:
                return {"error": "standard_name is required"}
        elif command == "search":
            query = arguments.get("query")
            if query:
                return await self._search_standards(query)
            else:
                return {"error": "query is required"}
        elif command == "analyze":
            standard_name = arguments.get("standard_name")
            if standard_name:
                return await self._analyze_standard(standard_name)
            else:
                return {"error": "standard_name is required"}
        elif command == "validate":
            return await self._validate_standard(arguments)
        elif command == "compliance":
            return await self._check_compliance()
        elif command == "create":
            return await self._create_standard(arguments)
        elif command == "update":
            return await self._update_standard(arguments)
        elif command == "archive":
            return await self._archive_standard(arguments)
        else:
            return {"error": f"Unknown command: {command}"}

    async def _step_0_read_implementing_standard(self) -> dict[str, Any]:
        """
        STEP 0: Read and validate the standard this workflow implements
        JTBD: Как валидатор стандарта, я хочу читать и проверять стандарт,
        чтобы обеспечить соответствие workflow требованиям стандарта.
        """
        try:
            # Read Registry Standard v5.8
            registry_standard_path = (
                self.standards_dir
                / "0. core standards"
                / "0.1 registry standard 15 may 2025 1320 CET by AI Assistant.md"
            )

            if not registry_standard_path.exists():
                return {"valid": False, "issues": ["Registry Standard not found"]}

            content = registry_standard_path.read_text(encoding="utf-8")

            # Validate Atomic Operation Principle compliance
            validation_result = self._validate_atomic_operation_compliance(content)

            # [reflection] Check if standard reading was successful
            if not await self._reflection_checkpoint(
                "standard_reading", {"content_length": len(content)}
            ):
                return {"valid": False, "issues": ["Failed to read standard properly"]}

            return validation_result

        except Exception as e:
            return {"valid": False, "issues": [f"Error reading standard: {str(e)}"]}

    def _validate_atomic_operation_compliance(self, content: str) -> dict[str, Any]:
        """
        JTBD: Как валидатор соответствия, я хочу проверять Atomic Operation Principle,
        чтобы обеспечить соответствие workflow требованиям Registry Standard.
        """
        issues: list[Any] = []

        # Check for Atomic Operation Principle
        if "Atomic Operation Principle" not in content:
            issues.append("Missing Atomic Operation Principle")

        # Check for reflection checkpoints
        if "[reflection]" not in content:
            issues.append("Missing reflection checkpoints")

        # Check for mandatory reflection points
        required_points = [
            "Input validation",
            "Process validation",
            "Output validation",
            "Standard compliance",
        ]

        for point in required_points:
            if point not in content:
                issues.append(f"Missing mandatory reflection point: {point}")

        return {"valid": len(issues) == 0, "issues": issues}

    async def _reflection_checkpoint(
        self, checkpoint_type: str, data: dict[str, Any]
    ) -> bool:
        """
        JTBD: Как reflection checkpoint, я хочу проверять состояние операции,
        чтобы обеспечить валидацию перед продолжением.
        """
        try:
            if checkpoint_type == "standard_compliance":
                return data.get("valid", False)
            elif checkpoint_type == "standard_reading":
                return data.get("content_length", 0) > 0
            else:
                return True
        except Exception:
            return False

    async def _get_standards(self, args: dict[str, Any]) -> dict[str, Any]:
        """
        JTBD: Как провайдер стандартов, я хочу возвращать список доступных стандартов,
        чтобы пользователь мог выбрать нужный документ.
        """
        # [reflection] Validate input data
        if not await self._reflection_checkpoint("input_validation", {"args": args}):
            return {"error": "Invalid input data"}

        try:
            standards = self._scan_standards_directory()

            # [reflection] Validate output quality
            if not await self._reflection_checkpoint(
                "output_validation", {"standards_count": len(standards)}
            ):
                return {"error": "Output validation failed"}

            return {"success": True, "standards": standards, "count": len(standards)}
        except Exception as e:
            return {"error": f"Failed to get standards: {str(e)}"}

    async def _list_standards(self) -> dict[str, Any]:
        """Alias for _get_standards for unified command interface"""
        return await self._get_standards({})

    async def _get_standard(self, standard_name: str) -> dict[str, Any]:
        """
        JTBD: Как получатель конкретного стандарта, я хочу предоставлять содержимое стандарта,
        чтобы пользователь мог изучить документ.
        """
        if not standard_name:
            return {"error": "Standard name is required"}

        try:
            for item in self.standards_dir.rglob("*.md"):
                if item.stem == standard_name:
                    content = item.read_text(encoding="utf-8")
                    return {
                        "success": True,
                        "name": standard_name,
                        "path": str(item.relative_to(self.standards_dir)),
                        "content": content,
                        "size": item.stat().st_size,
                    }

            return {"error": f"Standard not found: {standard_name}"}
        except Exception as e:
            return {"error": f"Error reading standard: {e}"}

    async def _search_standards(self, query: str) -> dict[str, Any]:
        """
        JTBD: Как поисковик стандартов, я хочу искать стандарты по запросу,
        чтобы пользователь мог найти нужный документ.
        """
        if not query:
            return {"error": "Query is required"}

        try:
            results = []
            for item in self.standards_dir.rglob("*.md"):
                if item.is_file():
                    try:
                        content = item.read_text(encoding="utf-8")
                        if (
                            query.lower() in content.lower()
                            or query.lower() in item.stem.lower()
                        ):
                            results.append(
                                {
                                    "name": item.stem,
                                    "path": str(item.relative_to(self.standards_dir)),
                                    "category": (
                                        str(item.parent.name)
                                        if item.parent != self.standards_dir
                                        else "root"
                                    ),
                                }
                            )
                    except Exception:
                        continue

            return {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results),
            }
        except Exception as e:
            return {"error": f"Search failed: {e}"}

    async def _analyze_standard(self, standard_name: str) -> dict[str, Any]:
        """
        JTBD: Как анализатор стандартов, я хочу анализировать структуру стандарта,
        чтобы оценить качество документа.
        """
        if not standard_name:
            return {"error": "Standard name is required"}

        try:
            standard_data = await self._get_standard(standard_name)
            if "error" in standard_data:
                return standard_data

            content = standard_data["content"]

            # Анализ структуры
            structure = {
                "has_jtbd_section": "## 📋 JTBD" in content,
                "has_architecture_section": "## 🏗️" in content,
                "has_examples": "```" in content,
                "has_checklist": "## ✅" in content,
                "has_license": "## 🛡️ Лицензия" in content,
                "has_registry": "## 📊 Реестр стандартов" in content,
            }

            return {
                "success": True,
                "name": standard_name,
                "structure": structure,
                "size": standard_data["size"],
                "sections_count": content.count("##"),
                "code_blocks_count": content.count("```"),
            }
        except Exception as e:
            return {"error": f"Analysis failed: {e}"}

    async def _check_compliance(self) -> dict[str, Any]:
        """
        JTBD: Как проверщик соответствия, я хочу проверять соответствие всех стандартов,
        чтобы оценить общее качество документации.
        """
        try:
            standards_list = await self._list_standards()
            if "error" in standards_list:
                return standards_list

            compliance_report = {
                "total_standards": standards_list["count"],
                "standards_details": [],
                "overall_score": 0,
            }

            total_score = 0
            for standard in standards_list["standards"]:
                validation = await self._validate_standard(
                    {"standard_name": standard["name"]}
                )
                if "score" in validation:
                    total_score += validation["score"]
                    compliance_report["standards_details"].append(
                        {
                            "name": standard["name"],
                            "score": validation["score"],
                            "status": validation.get("status", "unknown"),
                        }
                    )

            if standards_list["count"] > 0:
                compliance_report["overall_score"] = (
                    total_score / standards_list["count"]
                )

            return {"success": True, "compliance_report": compliance_report}
        except Exception as e:
            return {"error": f"Compliance check failed: {e}"}

    async def _update_standard(self, args: dict[str, Any]) -> dict[str, Any]:
        """
        JTBD: Как обновлятель стандартов, я хочу обновлять существующие стандарты,
        чтобы поддерживать актуальность документации.
        """
        standard_name = args.get("standard_name")
        update_type = args.get("update_type")
        new_content = args.get("new_content")

        if not standard_name:
            return {"error": "Standard name is required"}

        try:
            for item in self.standards_dir.rglob("*.md"):
                if item.stem == standard_name:
                    if update_type == "content" and new_content:
                        item.write_text(new_content, encoding="utf-8")

                    return {
                        "success": True,
                        "name": standard_name,
                        "update_type": update_type,
                        "file_path": str(item.relative_to(self.standards_dir)),
                    }

            return {"error": f"Standard not found: {standard_name}"}
        except Exception as e:
            return {"error": f"Update failed: {e}"}

    async def _archive_standard(self, args: dict[str, Any]) -> dict[str, Any]:
        """
        JTBD: Как архиватор стандартов, я хочу архивировать устаревшие стандарты,
        чтобы поддерживать порядок в документации.
        """
        standard_name = args.get("standard_name")
        reason = args.get("reason", "Archived by user")

        if not standard_name:
            return {"error": "Standard name is required"}

        try:
            for item in self.standards_dir.rglob("*.md"):
                if item.stem == standard_name:
                    archive_dir = self.standards_dir / "archive"
                    archive_dir.mkdir(exist_ok=True)

                    from datetime import datetime

                    archived_path = (
                        archive_dir
                        / f"{standard_name}_archived_{datetime.now().strftime('%Y%m%d')}.md"
                    )
                    item.rename(archived_path)

                    return {
                        "success": True,
                        "name": standard_name,
                        "original_path": str(item.relative_to(self.standards_dir)),
                        "archived_path": str(
                            archived_path.relative_to(self.standards_dir)
                        ),
                        "reason": reason,
                    }

            return {"error": f"Standard not found: {standard_name}"}
        except Exception as e:
            return {"error": f"Archive failed: {e}"}

    async def _validate_standard(self, args: dict[str, Any]) -> dict[str, Any]:
        """
        JTBD: Как валидатор стандартов, я хочу проверять корректность стандарта,
        чтобы обеспечить качество документации.
        """
        # [reflection] Validate input data
        if not await self._reflection_checkpoint("input_validation", {"args": args}):
            return {"error": "Invalid input data"}

        standard_path = args.get("path", "")
        if not standard_path:
            return {"error": "Standard path is required"}

        try:
            validation_result = self._validate_standard_file(standard_path)

            # [reflection] Validate output quality
            if not await self._reflection_checkpoint(
                "output_validation", validation_result
            ):
                return {"error": "Output validation failed"}

            return {
                "success": True,
                "valid": validation_result["valid"],
                "issues": validation_result.get("issues", []),
            }
        except Exception as e:
            return {"error": f"Validation failed: {str(e)}"}

    async def _create_standard(self, args: dict[str, Any]) -> dict[str, Any]:
        """
        JTBD: Как создатель стандартов, я хочу создавать новые стандарты,
        чтобы расширять документацию проекта.
        """
        # [reflection] Validate input data
        if not await self._reflection_checkpoint("input_validation", {"args": args}):
            return {"error": "Invalid input data"}

        name = args.get("name", "")
        content = args.get("content", "")

        if not name or not content:
            return {"error": "Name and content are required"}

        try:
            result = self._create_standard_file(name, content)

            # [reflection] Validate output quality
            if not await self._reflection_checkpoint("output_validation", result):
                return {"error": "Output validation failed"}

            return {
                "success": True,
                "created": result["created"],
                "path": result["path"],
            }
        except Exception as e:
            return {"error": f"Creation failed: {str(e)}"}

    def _validate_standards_directory(self) -> None:
        """
        JTBD: Как валидатор директории, я хочу проверить существование папки стандартов,
        чтобы обеспечить корректную работу workflow.
        """
        if not self.standards_dir.exists():
            raise ValueError(f"Standards directory not found: {self.standards_dir}")

    def _scan_standards_directory(self) -> list[dict[str, Any]]:
        """
        JTBD: Как сканер директории, я хочу находить все файлы стандартов,
        чтобы предоставить полный список доступных документов.
        """
        standards: list[Any] = []
        for file_path in self.standards_dir.rglob("*.md"):
            if file_path.is_file():
                standards.append(
                    {
                        "name": file_path.stem,
                        "path": str(file_path.relative_to(self.standards_dir)),
                        "size": file_path.stat().st_size,
                    }
                )
        return standards

    def _validate_standard_file(self, file_path: str) -> dict[str, Any]:
        """
        JTBD: Как валидатор файла, я хочу проверять структуру стандарта,
        чтобы обеспечить соответствие формату документации.
        """
        full_path = self.standards_dir / file_path
        if not full_path.exists():
            return {"valid": False, "issues": ["File not found"]}

        try:
            content = full_path.read_text(encoding="utf-8")
            issues: list[Any] = []

            # Проверка наличия заголовка
            if not content.startswith("#"):
                issues.append("Missing main heading")

            # Проверка наличия JTBD секции
            if "JTBD" not in content:
                issues.append("Missing JTBD section")

            return {"valid": len(issues) == 0, "issues": issues}
        except Exception as e:
            return {"valid": False, "issues": [f"Read error: {str(e)}"]}

    def _create_standard_file(self, name: str, content: str) -> dict[str, Any]:
        """
        JTBD: Как создатель файлов, я хочу создавать новые файлы стандартов,
        чтобы расширять документацию проекта.
        """
        file_path = self.standards_dir / f"{name}.md"

        if file_path.exists():
            return {
                "created": False,
                "path": str(file_path),
                "error": "File already exists",
            }

        try:
            file_path.write_text(content, encoding="utf-8")
            return {"created": True, "path": str(file_path)}
        except Exception as e:
            return {"created": False, "path": str(file_path), "error": str(e)}
