#!/usr/bin/env python3
"""
N8N Workflow Monitoring Module для heroes_mcp
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import aiohttp

# Добавляем путь к shared модулям
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "shared"))

from credentials_manager import credentials_manager  # type: ignore

logger = logging.getLogger(__name__)


class N8NWorkflowMonitor:
    """Класс для мониторинга n8n workflow"""

    def __init__(self):
        self.api_key = None
        self.api_url = None
        self._load_credentials()

    def _load_credentials(self):
        """Загружает credentials для n8n API"""
        try:
            api_key_result = credentials_manager.get_credential("N8N_API_KEY")
            api_url_result = credentials_manager.get_credential("N8N_API_URL")

            if api_key_result.success and api_url_result.success:
                self.api_key = api_key_result.value
                self.api_url = api_url_result.value
                logger.info("✅ N8N credentials loaded successfully")
            else:
                logger.error("❌ Failed to load N8N credentials")
        except Exception as e:
            logger.error(f"❌ Error loading N8N credentials: {e}")

    async def _make_api_request(
        self, endpoint: str, method: str = "GET", data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Выполняет запрос к n8n API"""
        if not self.api_key or not self.api_url:
            raise Exception("N8N API credentials not configured")

        url = f"{self.api_url}{endpoint}"
        headers = {
            "X-N8N-API-KEY": self.api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            try:
                if method == "GET":
                    async with session.get(url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
                elif method == "POST":
                    async with session.post(
                        url, headers=headers, json=data
                    ) as response:
                        response.raise_for_status()
                        return await response.json()
                elif method == "PUT":
                    async with session.put(url, headers=headers, json=data) as response:
                        response.raise_for_status()
                        return await response.json()
                elif method == "DELETE":
                    async with session.delete(url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except aiohttp.ClientError as e:
                logger.error(f"❌ API request failed: {e}")
                raise Exception(f"API request failed: {e}")

        # Fallback return (should never be reached)
        return {}

    async def get_workflow_health(self, workflow_id: str = "") -> dict[str, Any]:
        """
        Проверяет здоровье workflow

        Args:
            workflow_id: ID конкретного workflow или None для всех

        Returns:
            Dict с информацией о здоровье workflow
        """
        try:
            if workflow_id:
                # Получаем информацию о конкретном workflow
                workflow_data = await self._make_api_request(
                    f"/api/v1/workflows/{workflow_id}"
                )
                executions_data = await self._make_api_request(
                    f"/api/v1/executions?workflowId={workflow_id}&limit=20"
                )

                return self._analyze_workflow_health(workflow_data, executions_data)
            else:
                # Получаем информацию о всех workflow
                workflows_data = await self._make_api_request("/api/v1/workflows")

                health_summary: dict[str, Any] = {
                    "total_workflows": 0,
                    "active_workflows": 0,
                    "inactive_workflows": 0,
                    "critical_workflows": [],
                    "problem_workflows": [],
                    "healthy_workflows": [],
                    "workflow_details": [],
                }

                workflows = workflows_data.get("data", [])
                health_summary["total_workflows"] = len(workflows)

                for workflow in workflows:
                    workflow_id = workflow.get("id")
                    workflow_name = workflow.get("name", "Unnamed")

                    # Получаем executions для анализа
                    try:
                        executions_data = await self._make_api_request(
                            f"/api/v1/executions?workflowId={workflow_id}&limit=20"
                        )
                        workflow_health = self._analyze_workflow_health(
                            workflow, executions_data
                        )

                        health_summary["workflow_details"].append(
                            {
                                "id": workflow_id,
                                "name": workflow_name,
                                "health": workflow_health,
                            }
                        )

                        # Классифицируем workflow
                        if workflow.get("active", False):
                            health_summary["active_workflows"] += 1
                        else:
                            health_summary["inactive_workflows"] += 1

                        if workflow_health["status"] == "critical":
                            health_summary["critical_workflows"].append(
                                {
                                    "id": workflow_id,
                                    "name": workflow_name,
                                    "issues": workflow_health["issues"],
                                }
                            )
                        elif workflow_health["status"] == "warning":
                            health_summary["problem_workflows"].append(
                                {
                                    "id": workflow_id,
                                    "name": workflow_name,
                                    "issues": workflow_health["issues"],
                                }
                            )
                        else:
                            health_summary["healthy_workflows"].append(
                                {"id": workflow_id, "name": workflow_name}
                            )

                    except Exception as e:
                        logger.warning(
                            f"⚠️ Failed to analyze workflow {workflow_id}: {e}"
                        )
                        health_summary["problem_workflows"].append(
                            {
                                "id": workflow_id,
                                "name": workflow_name,
                                "issues": [f"Analysis failed: {e}"],
                            }
                        )

                return health_summary

        except Exception as e:
            logger.error(f"❌ Error checking workflow health: {e}")
            raise Exception(f"Failed to check workflow health: {e}")

    def _analyze_workflow_health(
        self, workflow_data: dict, executions_data: dict
    ) -> dict[str, Any]:
        """Анализирует здоровье конкретного workflow"""

        workflow_id = workflow_data.get("id")
        workflow_name = workflow_data.get("name", "Unnamed")
        is_active = workflow_data.get("active", False)

        # Анализ executions
        executions = (
            executions_data.get("data", [])
            if isinstance(executions_data.get("data"), list)
            else []
        )

        total_executions = len(executions)
        successful_executions = 0
        failed_executions = 0
        total_execution_time = 0
        errors = []

        for execution in executions:
            if execution.get("finished", False):
                if execution.get("status") == "success":
                    successful_executions += 1
                else:
                    failed_executions += 1
                    if execution.get("data", {}).get("resultData", {}).get("error"):
                        errors.append(execution["data"]["resultData"]["error"])

                # Расчет времени выполнения
                if execution.get("stoppedAt") and execution.get("startedAt"):
                    duration = (execution["stoppedAt"] - execution["startedAt"]) / 1000
                    total_execution_time += duration

        # Расчет метрик
        success_rate = (
            (successful_executions / total_executions * 100)
            if total_executions > 0
            else 0
        )
        error_rate = (
            (failed_executions / total_executions * 100) if total_executions > 0 else 0
        )
        avg_execution_time = (
            (total_execution_time / total_executions) if total_executions > 0 else 0
        )

        # Определение статуса здоровья
        issues = []
        status = "healthy"

        if not is_active:
            issues.append("Workflow is inactive")
            status = "warning"

        if error_rate > 50:
            issues.append(f"Critical error rate: {error_rate:.1f}%")
            status = "critical"
        elif error_rate > 20:
            issues.append(f"High error rate: {error_rate:.1f}%")
            status = "warning"

        if avg_execution_time > 60:
            issues.append(f"Slow execution time: {avg_execution_time:.1f}s")
            if status == "healthy":
                status = "warning"

        if total_executions == 0:
            issues.append("No recent executions")
            if status == "healthy":
                status = "warning"

        return {
            "workflow_id": workflow_id,
            "workflow_name": workflow_name,
            "status": status,
            "is_active": is_active,
            "metrics": {
                "total_executions": total_executions,
                "success_rate": success_rate,
                "error_rate": error_rate,
                "average_execution_time": avg_execution_time,
                "last_execution": executions[0].get("startedAt")
                if executions
                else None,
            },
            "issues": issues,
            "errors": errors[:5] if errors else [],  # Топ-5 ошибок
        }

    async def analyze_workflow(
        self, workflow_id: str, analysis_type: str = "full"
    ) -> dict[str, Any]:
        """
        Анализирует workflow на предмет проблем

        Args:
            workflow_id: ID workflow для анализа
            analysis_type: Тип анализа (full, structure, performance, security)

        Returns:
            Dict с результатами анализа
        """
        try:
            # Получаем данные workflow
            workflow_data = await self._make_api_request(
                f"/api/v1/workflows/{workflow_id}"
            )
            executions_data = await self._make_api_request(
                f"/api/v1/executions?workflowId={workflow_id}&limit=50"
            )

            analysis = {
                "workflow_id": workflow_id,
                "workflow_name": workflow_data.get("name", "Unnamed"),
                "analysis_type": analysis_type,
                "timestamp": datetime.now().isoformat(),
                "structure_analysis": {},
                "performance_analysis": {},
                "security_analysis": {},
                "recommendations": [],
            }

            if analysis_type in ["full", "structure"]:
                analysis["structure_analysis"] = self._analyze_structure(workflow_data)

            if analysis_type in ["full", "performance"]:
                analysis["performance_analysis"] = self._analyze_performance(
                    workflow_data, executions_data
                )

            if analysis_type in ["full", "security"]:
                analysis["security_analysis"] = self._analyze_security(workflow_data)

            # Генерируем рекомендации
            analysis["recommendations"] = self._generate_recommendations(analysis)

            return analysis

        except Exception as e:
            logger.error(f"❌ Error analyzing workflow {workflow_id}: {e}")
            raise Exception(f"Failed to analyze workflow: {e}")

    def _analyze_structure(self, workflow_data: dict) -> dict[str, Any]:
        """Анализирует структуру workflow"""
        nodes = workflow_data.get("nodes", [])
        connections = workflow_data.get("connections", {})

        node_types: dict[str, int] = {}
        triggers = []
        integrations = []
        complexity_score = 0

        for node in nodes:
            node_type = node.get("type", "unknown")
            node_types[node_type] = node_types.get(node_type, 0) + 1

            # Определяем триггеры
            if "trigger" in node_type.lower() or "webhook" in node_type.lower():
                triggers.append(
                    {
                        "type": node_type,
                        "name": node.get("name", "Unnamed"),
                        "parameters": node.get("parameters", {}),
                    }
                )

            # Определяем интеграции
            if "http" in node_type.lower() or "api" in node_type.lower():
                integrations.append(
                    {
                        "type": node_type,
                        "name": node.get("name", "Unnamed"),
                        "url": node.get("parameters", {}).get("url", "N/A"),
                    }
                )

        # Расчет complexity score
        complexity_score = (
            len(nodes) * 1
            + len(connections) * 2
            + len(integrations) * 3
            + len(triggers) * 2
        )

        return {
            "total_nodes": len(nodes),
            "total_connections": len(connections),
            "node_types": node_types,
            "triggers": triggers,
            "integrations": integrations,
            "complexity_score": complexity_score,
            "complexity_level": "high"
            if complexity_score > 50
            else "medium"
            if complexity_score > 20
            else "low",
        }

    def _analyze_performance(
        self, workflow_data: dict, executions_data: dict
    ) -> dict[str, Any]:
        """Анализирует производительность workflow"""
        executions = (
            executions_data.get("data", [])
            if isinstance(executions_data.get("data"), list)
            else []
        )

        if not executions:
            return {"status": "no_data", "message": "No execution data available"}

        execution_times = []
        success_count = 0
        error_count = 0

        for execution in executions:
            if execution.get("finished", False):
                if execution.get("status") == "success":
                    success_count += 1
                else:
                    error_count += 1

                if execution.get("stoppedAt") and execution.get("startedAt"):
                    duration = (execution["stoppedAt"] - execution["startedAt"]) / 1000
                    execution_times.append(duration)

        total_executions = len(executions)
        success_rate = (
            (success_count / total_executions * 100) if total_executions > 0 else 0
        )
        error_rate = (
            (error_count / total_executions * 100) if total_executions > 0 else 0
        )

        avg_time = sum(execution_times) / len(execution_times) if execution_times else 0
        max_time = max(execution_times) if execution_times else 0
        min_time = min(execution_times) if execution_times else 0

        # Анализ проблем производительности
        performance_issues = []
        if error_rate > 20:
            performance_issues.append(f"High error rate: {error_rate:.1f}%")
        if avg_time > 30:
            performance_issues.append(f"Slow average execution: {avg_time:.1f}s")
        if max_time > 120:
            performance_issues.append(f"Very slow execution detected: {max_time:.1f}s")

        return {
            "total_executions": total_executions,
            "success_rate": success_rate,
            "error_rate": error_rate,
            "execution_times": {
                "average": avg_time,
                "maximum": max_time,
                "minimum": min_time,
            },
            "performance_issues": performance_issues,
            "status": "critical"
            if error_rate > 50
            else "warning"
            if performance_issues
            else "good",
        }

    def _analyze_security(self, workflow_data: dict) -> dict[str, Any]:
        """Анализирует безопасность workflow"""
        nodes = workflow_data.get("nodes", [])

        security_issues = []
        secrets_found = []
        external_apis = []

        for node in nodes:
            parameters = node.get("parameters", {})
            node_type = node.get("type", "")

            # Проверка на секреты в параметрах
            for key, value in parameters.items():
                if isinstance(value, str):
                    if any(
                        secret in value.lower()
                        for secret in ["password", "token", "key", "secret"]
                    ):
                        if not value.startswith("{{") and not value.startswith(
                            "$"
                        ):  # Не переменная окружения
                            secrets_found.append(
                                {
                                    "node": node.get("name", "Unnamed"),
                                    "parameter": key,
                                    "value_preview": value[:20] + "..."
                                    if len(value) > 20
                                    else value,
                                }
                            )

            # Проверка внешних API
            if "http" in node_type.lower():
                url = parameters.get("url", "")
                if url and not url.startswith("{{") and not url.startswith("$"):
                    external_apis.append(
                        {"node": node.get("name", "Unnamed"), "url": url}
                    )

        if secrets_found:
            security_issues.append(
                f"Found {len(secrets_found)} potential secrets in parameters"
            )

        if external_apis:
            security_issues.append(f"Found {len(external_apis)} external API calls")

        return {
            "security_issues": security_issues,
            "secrets_found": secrets_found,
            "external_apis": external_apis,
            "status": "critical"
            if secrets_found
            else "warning"
            if security_issues
            else "good",
        }

    def _generate_recommendations(self, analysis: dict) -> list[str]:
        """Генерирует рекомендации на основе анализа"""
        recommendations = []

        # Рекомендации по структуре
        structure = analysis.get("structure_analysis", {})
        if structure.get("complexity_score", 0) > 50:
            recommendations.append(
                "Consider refactoring workflow - high complexity detected"
            )

        if len(structure.get("triggers", [])) > 3:
            recommendations.append(
                "Multiple triggers detected - consider consolidating"
            )

        # Рекомендации по производительности
        performance = analysis.get("performance_analysis", {})
        if performance.get("error_rate", 0) > 20:
            recommendations.append("High error rate - investigate and fix issues")

        if performance.get("execution_times", {}).get("average", 0) > 30:
            recommendations.append(
                "Slow execution time - optimize workflow performance"
            )

        # Рекомендации по безопасности
        security = analysis.get("security_analysis", {})
        if security.get("secrets_found"):
            recommendations.append("Move secrets to environment variables")

        if security.get("external_apis"):
            recommendations.append("Review external API integrations for security")

        return recommendations


# Глобальный экземпляр монитора
workflow_monitor = N8NWorkflowMonitor()
