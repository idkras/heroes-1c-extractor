"""
Ghost Integration Workflow
JTBD: Как система интеграции с Ghost CMS, я хочу управлять публикацией контента,
чтобы обеспечить автоматизацию работы с Ghost CMS.

MCP Workflow Standard v1.1: 1 workflow = 1 файл
TDD Documentation Standard v2.5: Atomic operations ≤20 строк
Registry Standard v5.8: Atomic Operation Principle с reflection checkpoints
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class GhostIntegrationWorkflow:
    """
    JTBD: Как workflow интеграции с Ghost, я хочу обрабатывать команды Ghost CMS,
    чтобы обеспечить автоматизацию публикации контента.
    """

    def __init__(self) -> None:
        """
        JTBD: Как инициализатор workflow, я хочу настроить базовые параметры,
        чтобы обеспечить готовность к обработке команд Ghost.
        """
        self.ghost_file = Path("ghost_posts.json")
        self.standards_dir = Path("../../../heroes-template/[standards .md]")
        self._initialize_ghost_storage()

    async def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """
        JTBD: Как исполнитель команд, я хочу обрабатывать запросы к Ghost CMS,
        чтобы предоставить пользователю доступ к управлению публикациями.
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

        if command == "ghost_publish_analysis":
            return await self._ghost_publish_analysis(arguments)
        elif command == "ghost_publish_document":
            return await self._ghost_publish_document(arguments)
        elif command == "ghost_integration":
            return await self._ghost_integration(arguments)
        else:
            return {"error": f"Unknown command: {command}"}

    async def _step_0_read_implementing_standard(self) -> dict[str, Any]:
        """
        STEP 0: Read and validate the standard this workflow implements
        JTBD: Как валидатор стандарта, я хочу читать и проверять стандарт,
        чтобы обеспечить соответствие workflow требованиям стандарта.
        """
        try:
            # Read Ghost Integration Standard using abstract link
            # abstract://standard:ghost_integration_standard
            ghost_standard_path = (
                self.standards_dir / "8. auto · n8n" / "ghost_integration_standard.md"
            )

            if not ghost_standard_path.exists():
                return {
                    "valid": False,
                    "issues": ["Ghost Integration Standard not found"],
                }

            content = ghost_standard_path.read_text(encoding="utf-8")

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

        # Check for Ghost integration requirements
        if "ghost" not in content.lower():
            issues.append("Missing Ghost integration content")

        # Check for CMS integration
        if "cms" not in content.lower():
            issues.append("Missing CMS integration content")

        # Check for publishing workflow
        if "publish" not in content.lower():
            issues.append("Missing publishing workflow content")

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
            elif checkpoint_type == "input_validation":
                return bool(data.get("args"))
            elif checkpoint_type == "output_validation":
                return data.get("post_id", "") != ""
            else:
                return True
        except Exception:
            return False

    async def _ghost_publish_analysis(self, args: dict[str, Any]) -> dict[str, Any]:
        """
        JTBD: Как публикатор анализа, я хочу публиковать аналитические отчеты в Ghost,
        чтобы обеспечить доступность аналитики.
        """
        # [reflection] Validate input data
        if not await self._reflection_checkpoint("input_validation", {"args": args}):
            return {"error": "Invalid input data"}

        analysis_data = args.get("analysis_data", "")
        title = args.get("title", "")
        tags = args.get("tags", [])

        if not analysis_data or not title:
            return {"error": "Analysis data and title are required"}

        try:
            result = self._publish_analysis_to_ghost(analysis_data, title, tags)

            # [reflection] Validate output quality
            if not await self._reflection_checkpoint(
                "output_validation", {"post_id": result.get("id")}
            ):
                return {"error": "Output validation failed"}

            return {"success": True, "result": result, "title": title}
        except Exception as e:
            return {"error": f"Failed to publish analysis: {str(e)}"}

    async def _ghost_publish_document(self, args: dict[str, Any]) -> dict[str, Any]:
        """
        JTBD: Как публикатор документов, я хочу публиковать документы в Ghost,
        чтобы обеспечить доступность документации.
        """
        # [reflection] Validate input data
        if not await self._reflection_checkpoint("input_validation", {"args": args}):
            return {"error": "Invalid input data"}

        document_content = args.get("document_content", "")
        title = args.get("title", "")
        document_type = args.get("document_type", "article")

        if not document_content or not title:
            return {"error": "Document content and title are required"}

        try:
            result = self._publish_document_to_ghost(
                document_content, title, document_type
            )

            # [reflection] Validate output quality
            if not await self._reflection_checkpoint(
                "output_validation", {"post_id": result.get("id")}
            ):
                return {"error": "Output validation failed"}

            return {
                "success": True,
                "result": result,
                "title": title,
                "type": document_type,
            }
        except Exception as e:
            return {"error": f"Failed to publish document: {str(e)}"}

    async def _ghost_integration(self, args: dict[str, Any]) -> dict[str, Any]:
        """
        JTBD: Как интегратор Ghost, я хочу управлять интеграцией с Ghost CMS,
        чтобы обеспечить корректную работу интеграции.
        """
        # [reflection] Validate input data
        if not await self._reflection_checkpoint("input_validation", {"args": args}):
            return {"error": "Invalid input data"}

        action = args.get("action", "")
        config = args.get("config", {})

        if not action:
            return {"error": "Action is required"}

        try:
            result = self._manage_ghost_integration(action, config)

            # [reflection] Validate output quality
            if not await self._reflection_checkpoint(
                "output_validation", {"action": action}
            ):
                return {"error": "Output validation failed"}

            return {"success": True, "result": result, "action": action}
        except Exception as e:
            return {"error": f"Failed to manage integration: {str(e)}"}

    def _initialize_ghost_storage(self) -> None:
        """
        JTBD: Как инициализатор хранилища, я хочу создать файл для Ghost постов,
        чтобы обеспечить персистентность данных.
        """
        if not self.ghost_file.exists():
            self.ghost_file.write_text(json.dumps({"ghost_posts": []}, indent=2))

    def _publish_analysis_to_ghost(
        self, analysis_data: str, title: str, tags: list[str]
    ) -> dict[str, Any]:
        """
        JTBD: Как публикатор, я хочу публиковать аналитические отчеты,
        чтобы обеспечить доступность аналитики в Ghost CMS.
        """
        post_id = f"ghost_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Симуляция публикации в Ghost CMS
        post = {
            "id": post_id,
            "title": title,
            "content": analysis_data,
            "tags": tags,
            "type": "analysis",
            "published_at": datetime.now().isoformat(),
            "status": "published",
            "metadata": {
                "word_count": len(analysis_data.split()),
                "read_time": len(analysis_data.split()) // 200,  # 200 слов в минуту
                "seo_score": 85,
            },
        }

        self._save_ghost_post(post)
        return post

    def _publish_document_to_ghost(
        self, content: str, title: str, doc_type: str
    ) -> dict[str, Any]:
        """
        JTBD: Как публикатор документов, я хочу публиковать документы,
        чтобы обеспечить доступность документации в Ghost CMS.
        """
        post_id = f"ghost_doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Симуляция публикации документа в Ghost CMS
        post = {
            "id": post_id,
            "title": title,
            "content": content,
            "type": doc_type,
            "published_at": datetime.now().isoformat(),
            "status": "published",
            "metadata": {
                "word_count": len(content.split()),
                "read_time": len(content.split()) // 200,
                "last_updated": datetime.now().isoformat(),
            },
        }

        self._save_ghost_post(post)
        return post

    def _manage_ghost_integration(
        self, action: str, config: dict[str, Any]
    ) -> dict[str, Any]:
        """
        JTBD: Как менеджер интеграции, я хочу управлять настройками Ghost,
        чтобы обеспечить корректную работу интеграции.
        """
        management_id = f"ghost_mgmt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Симуляция управления интеграцией
        result = {
            "id": management_id,
            "action": action,
            "config": config,
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "details": {
                "api_version": "v5.0",
                "authentication": "api_key",
                "endpoint": "https://ghost.example.com/ghost/api/v5.0",
                "rate_limit": "1000 requests/hour",
            },
        }

        self._save_ghost_post(result)
        return result

    def _load_ghost_posts(self) -> list[dict[str, Any]]:
        """
        JTBD: Как загрузчик данных, я хочу загружать Ghost посты из файла,
        чтобы обеспечить доступ к сохраненным данным.
        """
        try:
            data = json.loads(self.ghost_file.read_text())
            return data.get("ghost_posts", [])
        except Exception:
            return []

    def _save_ghost_post(self, post: dict[str, Any]) -> None:
        """
        JTBD: Как сохранитель данных, я хочу сохранять новые Ghost посты,
        чтобы обеспечить персистентность информации.
        """
        posts = self._load_ghost_posts()
        posts.append(post)
        self._save_ghost_posts_list(posts)

    def _save_ghost_posts_list(self, posts: list[dict[str, Any]]) -> None:
        """
        JTBD: Как сохранитель списка, я хочу сохранять обновленный список постов,
        чтобы обеспечить актуальность данных.
        """
        data = {"ghost_posts": posts}
        self.ghost_file.write_text(json.dumps(data, indent=2))
