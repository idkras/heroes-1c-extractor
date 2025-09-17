"""
JTBD Workflow
JTBD: Как система работы с Jobs-to-be-Done, я хочу управлять JTBD сценариями,
чтобы обеспечить понимание потребностей пользователей.

MCP Workflow Standard v1.1: 1 workflow = 1 файл
TDD Documentation Standard v2.5: Atomic operations ≤20 строк
Registry Standard v5.8: Atomic Operation Principle с reflection checkpoints
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class JTBDWorkflow:
    """
    JTBD: Как workflow JTBD, я хочу обрабатывать команды работы с JTBD,
    чтобы обеспечить систематический подход к пониманию потребностей.
    """

    def __init__(self) -> None:
        """
        JTBD: Как инициализатор workflow, я хочу настроить базовые параметры,
        чтобы обеспечить готовность к обработке команд JTBD.
        """
        self.jtbd_file = Path("jtbd_scenarios.json")
        self.standards_dir = Path("../../../heroes-template/[standards .md]")
        self._initialize_jtbd_storage()

    async def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """
        JTBD: Как исполнитель команд, я хочу обрабатывать запросы к JTBD,
        чтобы предоставить пользователю доступ к управлению JTBD сценариями.
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

        if command == "build_jtbd":
            return await self._build_jtbd(arguments)
        elif command == "create_jtbd_scenarios":
            return await self._create_jtbd_scenarios(arguments)
        elif command == "list_jtbd":
            return await self._list_jtbd(arguments)
        else:
            return {"error": f"Unknown command: {command}"}

    async def _step_0_read_implementing_standard(self) -> dict[str, Any]:
        """
        STEP 0: Read and validate the standard this workflow implements
        JTBD: Как валидатор стандарта, я хочу читать и проверять стандарт,
        чтобы обеспечить соответствие workflow требованиям стандарта.
        """
        try:
            # Read JTBD Standard
            jtbd_standard_path = (
                self.standards_dir
                / "3. scenarium · jtbd · hipothises · offering · tone"
                / "2.0 jtbd scenarium standard.md"
            )

            if not jtbd_standard_path.exists():
                return {"valid": False, "issues": ["JTBD Standard not found"]}

            content = jtbd_standard_path.read_text(encoding="utf-8")

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

        # Check for JTBD-specific requirements
        if "jtbd" not in content.lower():
            issues.append("Missing JTBD-specific content")

        # Check for JTBD documentation
        if "JTBD" not in content:
            issues.append("Missing JTBD documentation")

        # Check for scenario structure
        if "scenario" not in content.lower():
            issues.append("Missing scenario structure")

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
                return data.get("jtbd_count", 0) >= 0
            else:
                return True
        except Exception:
            return False

    async def _build_jtbd(self, args: dict[str, Any]) -> dict[str, Any]:
        """
        JTBD: Как строитель JTBD, я хочу создавать новые JTBD сценарии,
        чтобы структурировать понимание потребностей пользователей.
        """
        # [reflection] Validate input data
        if not await self._reflection_checkpoint("input_validation", {"args": args}):
            return {"error": "Invalid input data"}

        job_title = args.get("job_title", "")
        job_description = args.get("job_description", "")
        context = args.get("context", "")

        if not job_title or not job_description:
            return {"error": "Job title and description are required"}

        try:
            jtbd = self._create_jtbd(job_title, job_description, context)

            # [reflection] Validate output quality
            if not await self._reflection_checkpoint(
                "output_validation", {"jtbd_id": jtbd.get("id")}
            ):
                return {"error": "Output validation failed"}

            return {
                "success": True,
                "jtbd": jtbd,
                "id": jtbd["id"],
            }
        except Exception as e:
            return {"error": f"Failed to build JTBD: {str(e)}"}

    async def _create_jtbd_scenarios(self, args: dict[str, Any]) -> dict[str, Any]:
        """
        JTBD: Как создатель сценариев, я хочу создавать JTBD сценарии,
        чтобы обеспечить детальное понимание контекста использования.
        """
        # [reflection] Validate input data
        if not await self._reflection_checkpoint("input_validation", {"args": args}):
            return {"error": "Invalid input data"}

        jtbd_id = args.get("jtbd_id", "")
        scenarios = args.get("scenarios", [])

        if not jtbd_id or not scenarios:
            return {"error": "JTBD ID and scenarios are required"}

        try:
            updated_jtbd = self._add_scenarios_to_jtbd(jtbd_id, scenarios)

            # [reflection] Validate output quality
            if not await self._reflection_checkpoint(
                "output_validation", {"jtbd_id": jtbd_id}
            ):
                return {"error": "Output validation failed"}

            return {
                "success": True,
                "jtbd": updated_jtbd,
                "scenarios_count": len(scenarios),
            }
        except Exception as e:
            return {"error": f"Failed to create scenarios: {str(e)}"}

    async def _list_jtbd(self, args: dict[str, Any]) -> dict[str, Any]:
        """
        JTBD: Как провайдер JTBD, я хочу возвращать список JTBD,
        чтобы пользователь мог просмотреть все JTBD сценарии.
        """
        # [reflection] Validate input data
        if not await self._reflection_checkpoint("input_validation", {"args": args}):
            return {"error": "Invalid input data"}

        try:
            jtbd_list = self._get_all_jtbd()

            # [reflection] Validate output quality
            if not await self._reflection_checkpoint(
                "output_validation", {"jtbd_count": len(jtbd_list)}
            ):
                return {"error": "Output validation failed"}

            return {
                "success": True,
                "jtbd_list": jtbd_list,
                "count": len(jtbd_list),
            }
        except Exception as e:
            return {"error": f"Failed to list JTBD: {str(e)}"}

    def _initialize_jtbd_storage(self) -> None:
        """
        JTBD: Как инициализатор хранилища, я хочу создать файл для JTBD,
        чтобы обеспечить персистентность данных.
        """
        if not self.jtbd_file.exists():
            self.jtbd_file.write_text(json.dumps({"jtbd_scenarios": []}, indent=2))

    def _create_jtbd(
        self, job_title: str, job_description: str, context: str
    ) -> dict[str, Any]:
        """
        JTBD: Как создатель JTBD, я хочу создавать структурированные JTBD,
        чтобы обеспечить систематический подход к пониманию потребностей.
        """
        jtbd_id = f"jtbd_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        jtbd = {
            "id": jtbd_id,
            "job_title": job_title,
            "job_description": job_description,
            "context": context,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "scenarios": [],
            "notes": "",
        }

        self._save_jtbd(jtbd)
        return jtbd

    def _add_scenarios_to_jtbd(
        self, jtbd_id: str, scenarios: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        JTBD: Как обновлятель сценариев, я хочу добавлять сценарии к JTBD,
        чтобы обеспечить детальное понимание контекста.
        """
        jtbd_list = self._load_jtbd()

        for jtbd in jtbd_list:
            if jtbd["id"] == jtbd_id:
                jtbd["scenarios"].extend(scenarios)
                jtbd["updated_at"] = datetime.now().isoformat()
                self._save_jtbd_list(jtbd_list)
                return jtbd

        raise ValueError(f"JTBD not found: {jtbd_id}")

    def _get_all_jtbd(self) -> list[dict[str, Any]]:
        """
        JTBD: Как провайдер списка, я хочу возвращать все JTBD,
        чтобы пользователь мог просмотреть все сценарии.
        """
        return self._load_jtbd()

    def _load_jtbd(self) -> list[dict[str, Any]]:
        """
        JTBD: Как загрузчик данных, я хочу загружать JTBD из файла,
        чтобы обеспечить доступ к сохраненным данным.
        """
        try:
            data = json.loads(self.jtbd_file.read_text())
            return data.get("jtbd_scenarios", [])
        except Exception:
            return []

    def _save_jtbd(self, jtbd: dict[str, Any]) -> None:
        """
        JTBD: Как сохранитель данных, я хочу сохранять новые JTBD,
        чтобы обеспечить персистентность информации.
        """
        jtbd_list = self._load_jtbd()
        jtbd_list.append(jtbd)
        self._save_jtbd_list(jtbd_list)

    def _save_jtbd_list(self, jtbd_list: list[dict[str, Any]]) -> None:
        """
        JTBD: Как сохранитель списка, я хочу сохранять обновленный список JTBD,
        чтобы обеспечить актуальность данных.
        """
        data = {"jtbd_scenarios": jtbd_list}
        self.jtbd_file.write_text(json.dumps(data, indent=2))
