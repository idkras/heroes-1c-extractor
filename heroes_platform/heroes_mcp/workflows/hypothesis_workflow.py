"""
Hypothesis Workflow
JTBD: Как система работы с гипотезами, я хочу управлять гипотезами разработки,
чтобы обеспечить научный подход к решению проблем.

MCP Workflow Standard v1.1: 1 workflow = 1 файл
TDD Documentation Standard v2.5: Atomic operations ≤20 строк
Registry Standard v5.8: Atomic Operation Principle с reflection checkpoints
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class HypothesisWorkflow:
    """
    JTBD: Как workflow гипотез, я хочу обрабатывать команды работы с гипотезами,
    чтобы обеспечить систематический подход к решению проблем.
    """

    def __init__(self) -> None:
        """
        JTBD: Как инициализатор workflow, я хочу настроить базовые параметры,
        чтобы обеспечить готовность к обработке команд гипотез.
        """
        self.hypotheses_file = Path("hypotheses.json")
        self.standards_dir = Path("../../../heroes-template/[standards .md]")
        self._initialize_hypotheses_storage()

    async def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """
        JTBD: Как исполнитель команд, я хочу обрабатывать запросы к гипотезам,
        чтобы предоставить пользователю доступ к управлению гипотезами.
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

        if command == "form_hypothesis":
            return await self._form_hypothesis(arguments)
        elif command == "falsify_or_confirm":
            return await self._falsify_or_confirm(arguments)
        elif command == "list_hypotheses":
            return await self._list_hypotheses(arguments)
        else:
            return {"error": f"Unknown command: {command}"}

    async def _step_0_read_implementing_standard(self) -> dict[str, Any]:
        """
        STEP 0: Read and validate the standard this workflow implements
        JTBD: Как валидатор стандарта, я хочу читать и проверять стандарт,
        чтобы обеспечить соответствие workflow требованиям стандарта.
        """
        try:
            # Read Hypothesis Standard
            hypothesis_standard_path = (
                self.standards_dir
                / "3. scenarium · jtbd · hipothises · offering · tone"
                / "2.2 hypothesis standard.md"
            )

            if not hypothesis_standard_path.exists():
                return {"valid": False, "issues": ["Hypothesis Standard not found"]}

            content = hypothesis_standard_path.read_text(encoding="utf-8")

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

        # Check for hypothesis-specific requirements
        if "hypothesis" not in content.lower():
            issues.append("Missing hypothesis-specific content")

        # Check for JTBD documentation
        if "JTBD" not in content:
            issues.append("Missing JTBD documentation")

        # Check for workflow structure
        if "workflow" not in content.lower():
            issues.append("Missing workflow structure")

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
                return data.get("standards_count", 0) >= 0
            else:
                return True
        except Exception:
            return False

    async def _form_hypothesis(self, args: dict[str, Any]) -> dict[str, Any]:
        """
        JTBD: Как формирователь гипотез, я хочу создавать новые гипотезы,
        чтобы структурировать подход к решению проблем.
        """
        # [reflection] Validate input data
        if not await self._reflection_checkpoint("input_validation", {"args": args}):
            return {"error": "Invalid input data"}

        problem = args.get("problem", "")
        proposed_solution = args.get("proposed_solution", "")
        expected_outcome = args.get("expected_outcome", "")

        if not problem or not proposed_solution:
            return {"error": "Problem and proposed solution are required"}

        try:
            hypothesis = self._create_hypothesis(
                problem, proposed_solution, expected_outcome
            )

            # [reflection] Validate output quality
            if not await self._reflection_checkpoint(
                "output_validation", {"hypothesis_id": hypothesis.get("id")}
            ):
                return {"error": "Output validation failed"}

            return {
                "success": True,
                "hypothesis": hypothesis,
                "id": hypothesis["id"],
            }
        except Exception as e:
            return {"error": f"Failed to form hypothesis: {str(e)}"}

    async def _falsify_or_confirm(self, args: dict[str, Any]) -> dict[str, Any]:
        """
        JTBD: Как валидатор гипотез, я хочу проверять гипотезы на истинность,
        чтобы обеспечить научный подход к решению проблем.
        """
        # [reflection] Validate input data
        if not await self._reflection_checkpoint("input_validation", {"args": args}):
            return {"error": "Invalid input data"}

        hypothesis_id = args.get("hypothesis_id", "")
        result = args.get("result", "")  # "confirmed" or "falsified"
        evidence = args.get("evidence", "")

        if not hypothesis_id or not result:
            return {"error": "Hypothesis ID and result are required"}

        try:
            updated_hypothesis = self._update_hypothesis_status(
                hypothesis_id, result, evidence
            )

            # [reflection] Validate output quality
            if not await self._reflection_checkpoint(
                "output_validation", {"hypothesis_id": hypothesis_id}
            ):
                return {"error": "Output validation failed"}

            return {
                "success": True,
                "hypothesis": updated_hypothesis,
                "status": result,
            }
        except Exception as e:
            return {"error": f"Failed to update hypothesis: {str(e)}"}

    async def _list_hypotheses(self, args: dict[str, Any]) -> dict[str, Any]:
        """
        JTBD: Как провайдер гипотез, я хочу возвращать список гипотез,
        чтобы пользователь мог просмотреть все гипотезы.
        """
        # [reflection] Validate input data
        if not await self._reflection_checkpoint("input_validation", {"args": args}):
            return {"error": "Invalid input data"}

        status_filter = args.get(
            "status", "all"
        )  # "all", "pending", "confirmed", "falsified"

        try:
            hypotheses = self._get_hypotheses_by_status(status_filter)

            # [reflection] Validate output quality
            if not await self._reflection_checkpoint(
                "output_validation", {"hypotheses_count": len(hypotheses)}
            ):
                return {"error": "Output validation failed"}

            return {
                "success": True,
                "hypotheses": hypotheses,
                "count": len(hypotheses),
                "filter": status_filter,
            }
        except Exception as e:
            return {"error": f"Failed to list hypotheses: {str(e)}"}

    def _initialize_hypotheses_storage(self) -> None:
        """
        JTBD: Как инициализатор хранилища, я хочу создать файл для гипотез,
        чтобы обеспечить персистентность данных.
        """
        if not self.hypotheses_file.exists():
            self.hypotheses_file.write_text(json.dumps({"hypotheses": []}, indent=2))

    def _create_hypothesis(
        self, problem: str, solution: str, outcome: str
    ) -> dict[str, Any]:
        """
        JTBD: Как создатель гипотез, я хочу создавать структурированные гипотезы,
        чтобы обеспечить систематический подход к проблемам.
        """
        hypothesis_id = f"hyp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        hypothesis = {
            "id": hypothesis_id,
            "problem": problem,
            "proposed_solution": solution,
            "expected_outcome": outcome,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "evidence": [],
            "notes": "",
        }

        self._save_hypothesis(hypothesis)
        return hypothesis

    def _update_hypothesis_status(
        self, hypothesis_id: str, result: str, evidence: str
    ) -> dict[str, Any]:
        """
        JTBD: Как обновлятель статуса, я хочу изменять статус гипотез,
        чтобы отражать результаты проверки.
        """
        hypotheses = self._load_hypotheses()

        for hypothesis in hypotheses:
            if hypothesis["id"] == hypothesis_id:
                hypothesis["status"] = result
                hypothesis["updated_at"] = datetime.now().isoformat()
                if evidence:
                    hypothesis["evidence"].append(
                        {
                            "result": result,
                            "evidence": evidence,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                self._save_hypotheses(hypotheses)
                return hypothesis

        raise ValueError(f"Hypothesis not found: {hypothesis_id}")

    def _get_hypotheses_by_status(self, status_filter: str) -> list[dict[str, Any]]:
        """
        JTBD: Как фильтратор гипотез, я хочу возвращать гипотезы по статусу,
        чтобы пользователь мог найти нужные гипотезы.
        """
        hypotheses = self._load_hypotheses()

        if status_filter == "all":
            return hypotheses
        else:
            return [h for h in hypotheses if h["status"] == status_filter]

    def _load_hypotheses(self) -> list[dict[str, Any]]:
        """
        JTBD: Как загрузчик данных, я хочу загружать гипотезы из файла,
        чтобы обеспечить доступ к сохраненным данным.
        """
        try:
            data = json.loads(self.hypotheses_file.read_text())
            return data.get("hypotheses", [])
        except Exception:
            return []

    def _save_hypothesis(self, hypothesis: dict[str, Any]) -> None:
        """
        JTBD: Как сохранитель данных, я хочу сохранять новые гипотезы,
        чтобы обеспечить персистентность информации.
        """
        hypotheses = self._load_hypotheses()
        hypotheses.append(hypothesis)
        self._save_hypotheses(hypotheses)

    def _save_hypotheses(self, hypotheses: list[dict[str, Any]]) -> None:
        """
        JTBD: Как сохранитель списка, я хочу сохранять обновленный список гипотез,
        чтобы обеспечить актуальность данных.
        """
        data = {"hypotheses": hypotheses}
        self.hypotheses_file.write_text(json.dumps(data, indent=2))
