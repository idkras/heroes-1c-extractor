#!/usr/bin/env python3
"""
n8n Integration Module

Модуль для интеграции с n8n API через MCP команды.
Основан на n8n-mcp от czlonkowski.
"""

import logging
from typing import Any, Optional

import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class N8nConfig(BaseModel):
    """Конфигурация для подключения к n8n"""

    base_url: str = Field(default="http://localhost:5678")
    api_key: Optional[str] = Field(default=None)
    username: Optional[str] = Field(default=None)
    password: Optional[str] = Field(default=None)
    timeout: int = Field(default=30)


class N8nNode(BaseModel):
    """Модель n8n узла"""

    id: str
    name: str
    type: str
    typeVersion: int
    position: list[int]
    parameters: dict[str, Any] = Field(default_factory=dict)


class N8nWorkflow(BaseModel):
    """Модель n8n workflow"""

    id: Optional[str] = None
    name: str
    active: bool = False
    nodes: list[N8nNode] = Field(default_factory=list)
    connections: dict[str, Any] = Field(default_factory=dict)
    settings: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)


class N8nIntegration:
    """Класс для интеграции с n8n API"""

    def __init__(self, config: N8nConfig):
        self.config = config
        self.client = None
        self._headers = {}

        # Настройка заголовков для аутентификации
        if config.api_key:
            self._headers["X-N8N-API-KEY"] = config.api_key
        elif config.username and config.password:
            # Basic auth будет добавлен в httpx client
            pass

    async def _get_client(self) -> httpx.AsyncClient:
        """Получить HTTP клиент с настройками аутентификации"""
        if self.client is None:
            auth = None
            if self.config.username and self.config.password:
                auth = (self.config.username, self.config.password)

            self.client = httpx.AsyncClient(  # type: ignore
                base_url=self.config.base_url,
                headers=self._headers,
                auth=auth,
                timeout=self.config.timeout,
            )
        return self.client  # type: ignore

    async def health_check(self) -> dict[str, Any]:
        """Проверка здоровья n8n сервера"""
        try:
            client = await self._get_client()
            response = await client.get("/healthz")
            response.raise_for_status()

            return {
                "status": "healthy",
                "n8n_version": response.headers.get("x-n8n-version", "unknown"),
                "response_time": response.elapsed.total_seconds(),
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}

    async def list_workflows(self, limit: int = 50, offset: int = 0) -> dict[str, Any]:
        """Получить список workflow"""
        try:
            client = await self._get_client()
            response = await client.get(
                "/api/v1/workflows", params={"limit": limit, "offset": offset}
            )
            response.raise_for_status()

            data = response.json()
            return {
                "workflows": data.get("data", []),
                "total": data.get("meta", {}).get("total", 0),
                "limit": limit,
                "offset": offset,
            }
        except Exception as e:
            logger.error(f"Failed to list workflows: {e}")
            return {"error": str(e)}

    async def get_workflow(self, workflow_id: str) -> dict[str, Any]:
        """Получить конкретный workflow по ID"""
        try:
            client = await self._get_client()
            response = await client.get(f"/api/v1/workflows/{workflow_id}")
            response.raise_for_status()

            return response.json()
        except Exception as e:
            logger.error(f"Failed to get workflow {workflow_id}: {e}")
            return {"error": str(e)}

    async def create_workflow(self, workflow_data: dict[str, Any]) -> dict[str, Any]:
        """Создать новый workflow"""
        try:
            client = await self._get_client()
            response = await client.post("/api/v1/workflows", json=workflow_data)
            response.raise_for_status()

            return response.json()
        except Exception as e:
            logger.error(f"Failed to create workflow: {e}")
            return {"error": str(e)}

    async def update_workflow(
        self, workflow_id: str, workflow_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Обновить существующий workflow"""
        try:
            client = await self._get_client()
            response = await client.put(
                f"/api/v1/workflows/{workflow_id}", json=workflow_data
            )
            response.raise_for_status()

            return response.json()
        except Exception as e:
            logger.error(f"Failed to update workflow {workflow_id}: {e}")
            return {"error": str(e)}

    async def delete_workflow(self, workflow_id: str) -> dict[str, Any]:
        """Удалить workflow"""
        try:
            client = await self._get_client()
            response = await client.delete(f"/api/v1/workflows/{workflow_id}")
            response.raise_for_status()

            return {"success": True, "message": f"Workflow {workflow_id} deleted"}
        except Exception as e:
            logger.error(f"Failed to delete workflow {workflow_id}: {e}")
            return {"error": str(e)}

    async def activate_workflow(self, workflow_id: str) -> dict[str, Any]:
        """Активировать workflow"""
        try:
            client = await self._get_client()
            response = await client.post(f"/api/v1/workflows/{workflow_id}/activate")
            response.raise_for_status()

            return {"success": True, "message": f"Workflow {workflow_id} activated"}
        except Exception as e:
            logger.error(f"Failed to activate workflow {workflow_id}: {e}")
            return {"error": str(e)}

    async def deactivate_workflow(self, workflow_id: str) -> dict[str, Any]:
        """Деактивировать workflow"""
        try:
            client = await self._get_client()
            response = await client.post(f"/api/v1/workflows/{workflow_id}/deactivate")
            response.raise_for_status()

            return {"success": True, "message": f"Workflow {workflow_id} deactivated"}
        except Exception as e:
            logger.error(f"Failed to deactivate workflow {workflow_id}: {e}")
            return {"error": str(e)}

    async def trigger_workflow(
        self, workflow_id: str, data: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Запустить workflow через webhook"""
        try:
            client = await self._get_client()

            # Получаем webhook URL для workflow
            workflow = await self.get_workflow(workflow_id)
            if "error" in workflow:
                return workflow

            # Ищем webhook узлы
            webhook_nodes = []
            for node in workflow.get("nodes", []):
                if node.get("type") == "n8n-nodes-base.webhook":
                    webhook_nodes.append(node)

            if not webhook_nodes:
                return {"error": "No webhook nodes found in workflow"}

            # Используем первый webhook узел
            webhook_node = webhook_nodes[0]
            webhook_path = webhook_node.get("parameters", {}).get("path", "")

            if not webhook_path:
                return {"error": "Webhook path not configured"}

            # Отправляем запрос к webhook
            webhook_url = f"{self.config.base_url}/webhook/{webhook_path}"
            response = await client.post(webhook_url, json=data or {})
            response.raise_for_status()

            return {
                "success": True,
                "execution_id": response.headers.get("x-execution-id"),
                "response": response.json() if response.content else None,
            }
        except Exception as e:
            logger.error(f"Failed to trigger workflow {workflow_id}: {e}")
            return {"error": str(e)}

    async def get_executions(
        self, workflow_id: Optional[str] = None, limit: int = 50
    ) -> dict[str, Any]:
        """Получить список выполнений"""
        try:
            client = await self._get_client()
            params = {"limit": limit}
            if workflow_id:
                params["workflowId"] = str(workflow_id)  # type: ignore

            response = await client.get("/api/v1/executions", params=params)
            response.raise_for_status()

            data = response.json()
            return {
                "executions": data.get("data", []),
                "total": data.get("meta", {}).get("total", 0),
            }
        except Exception as e:
            logger.error(f"Failed to get executions: {e}")
            return {"error": str(e)}

    async def get_execution(self, execution_id: str) -> dict[str, Any]:
        """Получить конкретное выполнение по ID"""
        try:
            client = await self._get_client()
            response = await client.get(f"/api/v1/executions/{execution_id}")
            response.raise_for_status()

            return response.json()
        except Exception as e:
            logger.error(f"Failed to get execution {execution_id}: {e}")
            return {"error": str(e)}

    async def delete_execution(self, execution_id: str) -> dict[str, Any]:
        """Удалить выполнение по ID"""
        try:
            client = await self._get_client()
            response = await client.delete(f"/api/v1/executions/{execution_id}")
            response.raise_for_status()

            return {"success": True, "message": f"Execution {execution_id} deleted"}
        except Exception as e:
            logger.error(f"Failed to delete execution {execution_id}: {e}")
            return {"error": str(e)}

    async def get_workflow_details(self, workflow_id: str) -> dict[str, Any]:
        """Получить детальную информацию о workflow с метаданными"""
        try:
            client = await self._get_client()
            response = await client.get(f"/api/v1/workflows/{workflow_id}")
            response.raise_for_status()

            workflow_data = response.json()

            # Добавляем дополнительную информацию
            details = {
                "id": workflow_data.get("id"),
                "name": workflow_data.get("name"),
                "active": workflow_data.get("active"),
                "version": workflow_data.get("versionId"),
                "created_at": workflow_data.get("createdAt"),
                "updated_at": workflow_data.get("updatedAt"),
                "nodes_count": len(workflow_data.get("nodes", [])),
                "connections_count": len(workflow_data.get("connections", {})),
                "tags": workflow_data.get("tags", []),
                "settings": workflow_data.get("settings", {}),
                "meta": workflow_data.get("meta", {}),
            }

            return details
        except Exception as e:
            logger.error(f"Failed to get workflow details {workflow_id}: {e}")
            return {"error": str(e)}

    async def get_workflow_structure(self, workflow_id: str) -> dict[str, Any]:
        """Получить структуру workflow (только nodes и connections)"""
        try:
            client = await self._get_client()
            response = await client.get(f"/api/v1/workflows/{workflow_id}")
            response.raise_for_status()

            workflow_data = response.json()

            # Извлекаем только структуру
            structure = {
                "id": workflow_data.get("id"),
                "name": workflow_data.get("name"),
                "nodes": workflow_data.get("nodes", []),
                "connections": workflow_data.get("connections", {}),
            }

            return structure
        except Exception as e:
            logger.error(f"Failed to get workflow structure {workflow_id}: {e}")
            return {"error": str(e)}

    async def get_workflow_minimal(self, workflow_id: str) -> dict[str, Any]:
        """Получить минимальную информацию о workflow"""
        try:
            client = await self._get_client()
            response = await client.get(f"/api/v1/workflows/{workflow_id}")
            response.raise_for_status()

            workflow_data = response.json()

            # Только основная информация
            minimal = {
                "id": workflow_data.get("id"),
                "name": workflow_data.get("name"),
                "active": workflow_data.get("active"),
                "tags": workflow_data.get("tags", []),
            }

            return minimal
        except Exception as e:
            logger.error(f"Failed to get workflow minimal {workflow_id}: {e}")
            return {"error": str(e)}

    async def validate_workflow(
        self, workflow_id: str, options: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Валидация workflow"""
        try:
            client = await self._get_client()
            response = await client.get(f"/api/v1/workflows/{workflow_id}")
            response.raise_for_status()

            workflow_data = response.json()
            validation_result = {
                "workflow_id": workflow_id,
                "valid": True,
                "errors": [],
                "warnings": [],
                "suggestions": [],
            }

            # Проверяем nodes
            if options is None or options.get("validateNodes", True):
                for node in workflow_data.get("nodes", []):
                    if not node.get("id"):
                        errors = validation_result.get("errors", [])
                        if isinstance(errors, list):
                            errors.append(
                                f"Node missing ID: {node.get('name', 'Unknown')}"
                            )
                    if not node.get("type"):
                        errors = validation_result.get("errors", [])
                        if isinstance(errors, list):
                            errors.append(
                                f"Node missing type: {node.get('name', 'Unknown')}"
                            )

            # Проверяем connections
            if options is None or options.get("validateConnections", True):
                connections = workflow_data.get("connections", {})
                for source_id, _targets in connections.items():
                    if not any(
                        node["id"] == source_id
                        for node in workflow_data.get("nodes", [])
                    ):
                        warnings = validation_result.get("warnings", [])
                        if isinstance(warnings, list):
                            warnings.append(
                                f"Connection from non-existent node: {source_id}"
                            )

            # Проверяем expressions
            if options is None or options.get("validateExpressions", True):
                for node in workflow_data.get("nodes", []):
                    parameters = node.get("parameters", {})
                    for _key, value in parameters.items():
                        if isinstance(value, str) and "{{" in value and "}}" in value:
                            # Простая проверка выражений
                            if value.count("{{") != value.count("}}"):
                                warnings = validation_result.get("warnings", [])
                                if isinstance(warnings, list):
                                    warnings.append(
                                        f"Unbalanced expressions in node {node.get('name')}"
                                    )

            errors = validation_result.get("errors", [])
            validation_result["valid"] = (
                len(errors) if isinstance(errors, list) else 0 == 0
            )

            return validation_result
        except Exception as e:
            logger.error(f"Failed to validate workflow {workflow_id}: {e}")
            return {"error": str(e)}

    async def list_available_tools(self) -> dict[str, Any]:
        """Получить список доступных инструментов"""
        try:
            client = await self._get_client()
            response = await client.get("/api/v1/nodes")
            response.raise_for_status()

            nodes_data = response.json()
            tools = []

            for node in nodes_data.get("data", []):
                tools.append(
                    {
                        "name": node.get("name"),
                        "type": node.get("type"),
                        "version": node.get("version"),
                        "description": node.get("description", ""),
                    }
                )

            return {"tools": tools, "total": len(tools)}
        except Exception as e:
            logger.error(f"Failed to list available tools: {e}")
            return {"error": str(e)}

    async def diagnostic(self) -> dict[str, Any]:
        """Диагностика n8n API конфигурации"""
        try:
            client = await self._get_client()

            diagnostic_result = {
                "status": "unknown",
                "api_url": self.config.base_url,
                "auth_type": "none",
                "features": [],
                "errors": [],
            }

            # Проверяем аутентификацию
            if self.config.api_key:
                diagnostic_result["auth_type"] = "api_key"
            elif self.config.username and self.config.password:
                diagnostic_result["auth_type"] = "basic_auth"

            # Проверяем доступность API
            try:
                health_response = await client.get("/healthz")
                if health_response.status_code == 200:
                    diagnostic_result["status"] = "healthy"
                    features = diagnostic_result.get("features", [])
                    if isinstance(features, list):
                        features.append("health_check")
                else:
                    diagnostic_result["status"] = "unhealthy"
                    errors = diagnostic_result.get("errors", [])
                    if isinstance(errors, list):
                        errors.append(
                            f"Health check failed: {health_response.status_code}"
                        )
            except Exception as e:
                diagnostic_result["status"] = "error"
                errors = diagnostic_result.get("errors", [])
                if isinstance(errors, list):
                    errors.append(f"Health check error: {str(e)}")

            # Проверяем доступ к workflows
            try:
                workflows_response = await client.get(
                    "/api/v1/workflows", params={"limit": 1}
                )
                if workflows_response.status_code == 200:
                    features = diagnostic_result.get("features", [])
                    if isinstance(features, list):
                        features.append("workflows_access")
                else:
                    errors = diagnostic_result.get("errors", [])
                    if isinstance(errors, list):
                        errors.append(
                            f"Workflows access failed: {workflows_response.status_code}"
                        )
            except Exception as e:
                errors = diagnostic_result.get("errors", [])
                if isinstance(errors, list):
                    errors.append(f"Workflows access error: {str(e)}")

            # Проверяем доступ к executions
            try:
                executions_response = await client.get(
                    "/api/v1/executions", params={"limit": 1}
                )
                if executions_response.status_code == 200:
                    features = diagnostic_result.get("features", [])
                    if isinstance(features, list):
                        features.append("executions_access")
                else:
                    errors = diagnostic_result.get("errors", [])
                    if isinstance(errors, list):
                        errors.append(
                            f"Executions access failed: {executions_response.status_code}"
                        )
            except Exception as e:
                errors = diagnostic_result.get("errors", [])
                if isinstance(errors, list):
                    errors.append(f"Executions access error: {str(e)}")

            return diagnostic_result
        except Exception as e:
            logger.error(f"Failed to run diagnostic: {e}")
            return {"error": str(e)}

    async def close(self):
        """Закрыть HTTP клиент"""
        if self.client:
            await self.client.aclose()
            self.client = None


# Глобальный экземпляр интеграции
_n8n_integration: Optional[N8nIntegration] = None


def get_n8n_integration() -> Optional[N8nIntegration]:
    """Получить глобальный экземпляр n8n интеграции"""
    return _n8n_integration


def init_n8n_integration(config: N8nConfig) -> N8nIntegration:
    """Инициализировать n8n интеграцию"""
    global _n8n_integration
    _n8n_integration = N8nIntegration(config)
    return _n8n_integration
