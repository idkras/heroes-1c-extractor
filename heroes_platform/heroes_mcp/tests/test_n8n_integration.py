#!/usr/bin/env python3
"""
Tests for n8n integration
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from src.n8n_integration import N8nConfig, N8nIntegration, N8nNode, N8nWorkflow


class TestN8nConfig:
    """Test N8nConfig class"""

    def test_default_config(self):
        """Test default configuration"""
        config = N8nConfig()
        assert config.base_url == "http://localhost:5678"
        assert config.api_key is None
        assert config.username is None
        assert config.password is None
        assert config.timeout == 30

    def test_custom_config(self):
        """Test custom configuration"""
        config = N8nConfig(
            base_url="https://n8n.example.com",
            api_key="test_key",
            username="admin",
            password="password",
            timeout=60,
        )
        assert config.base_url == "https://n8n.example.com"
        assert config.api_key == "test_key"
        assert config.username == "admin"
        assert config.password == "password"
        assert config.timeout == 60


class TestN8nNode:
    """Test N8nNode class"""

    def test_node_creation(self):
        """Test node creation"""
        node = N8nNode(
            id="test-node",
            name="Test Node",
            type="n8n-nodes-base.webhook",
            typeVersion=1,
            position=[100, 200],
            parameters={"path": "/test"},
        )
        assert node.id == "test-node"
        assert node.name == "Test Node"
        assert node.type == "n8n-nodes-base.webhook"
        assert node.typeVersion == 1
        assert node.position == [100, 200]
        assert node.parameters == {"path": "/test"}


class TestN8nWorkflow:
    """Test N8nWorkflow class"""

    def test_workflow_creation(self):
        """Test workflow creation"""
        workflow = N8nWorkflow(
            name="Test Workflow",
            active=False,
            nodes=[],
            connections={},
            settings={},
            tags=["test"],
        )
        assert workflow.name == "Test Workflow"
        assert workflow.active is False
        assert workflow.nodes == []
        assert workflow.connections == {}
        assert workflow.settings == {}
        assert workflow.tags == ["test"]


class TestN8nIntegration:
    """Test N8nIntegration class"""

    @pytest.fixture
    def config(self):
        """Create test configuration"""
        return N8nConfig(base_url="http://localhost:5678", api_key="test_key")

    @pytest.fixture
    def integration(self, config):
        """Create test integration"""
        return N8nIntegration(config)

    def test_init_with_api_key(self, config):
        """Test initialization with API key"""
        integration = N8nIntegration(config)
        assert integration.config == config
        assert integration._headers["X-N8N-API-KEY"] == "test_key"

    def test_init_with_basic_auth(self):
        """Test initialization with basic auth"""
        config = N8nConfig(
            base_url="http://localhost:5678", username="admin", password="password"
        )
        integration = N8nIntegration(config)
        assert integration.config == config
        assert "X-N8N-API-KEY" not in integration._headers

    @pytest.mark.asyncio
    async def test_health_check_success(self, integration):
        """Test successful health check"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.headers.get.return_value = "1.0.0"
        mock_response.elapsed.total_seconds.return_value = 0.123

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        with patch.object(integration, "_get_client", return_value=mock_client):
            result = await integration.health_check()

            assert result["status"] == "healthy"
            assert result["n8n_version"] == "1.0.0"
            assert result["response_time"] == 0.123

    @pytest.mark.asyncio
    async def test_health_check_failure(self, integration):
        """Test failed health check"""
        mock_client = AsyncMock()
        mock_client.get.side_effect = Exception("Connection failed")

        with patch.object(integration, "_get_client", return_value=mock_client):
            result = await integration.health_check()

            assert result["status"] == "unhealthy"
            assert "error" in result

    @pytest.mark.asyncio
    async def test_list_workflows_success(self, integration):
        """Test successful workflow listing"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "data": [{"id": "1", "name": "Test"}],
            "meta": {"total": 1},
        }

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        with patch.object(integration, "_get_client", return_value=mock_client):
            result = await integration.list_workflows(limit=10, offset=0)

            assert result["workflows"] == [{"id": "1", "name": "Test"}]
            assert result["total"] == 1
            assert result["limit"] == 10
            assert result["offset"] == 0

    @pytest.mark.asyncio
    async def test_get_workflow_success(self, integration):
        """Test successful workflow retrieval"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"id": "1", "name": "Test Workflow"}

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        with patch.object(integration, "_get_client", return_value=mock_client):
            result = await integration.get_workflow("1")

            assert result["id"] == "1"
            assert result["name"] == "Test Workflow"

    @pytest.mark.asyncio
    async def test_create_workflow_success(self, integration):
        """Test successful workflow creation"""
        workflow_data = {"name": "New Workflow", "nodes": []}

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"id": "2", "name": "New Workflow"}

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        with patch.object(integration, "_get_client", return_value=mock_client):
            result = await integration.create_workflow(workflow_data)

            assert result["id"] == "2"
            assert result["name"] == "New Workflow"

    @pytest.mark.asyncio
    async def test_update_workflow_success(self, integration):
        """Test successful workflow update"""
        workflow_data = {"name": "Updated Workflow", "nodes": []}

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"id": "1", "name": "Updated Workflow"}

        mock_client = AsyncMock()
        mock_client.put.return_value = mock_response

        with patch.object(integration, "_get_client", return_value=mock_client):
            result = await integration.update_workflow("1", workflow_data)

            assert result["id"] == "1"
            assert result["name"] == "Updated Workflow"

    @pytest.mark.asyncio
    async def test_delete_workflow_success(self, integration):
        """Test successful workflow deletion"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.delete.return_value = mock_response

        with patch.object(integration, "_get_client", return_value=mock_client):
            result = await integration.delete_workflow("1")

            assert result["success"] is True
            assert "deleted" in result["message"]

    @pytest.mark.asyncio
    async def test_activate_workflow_success(self, integration):
        """Test successful workflow activation"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        with patch.object(integration, "_get_client", return_value=mock_client):
            result = await integration.activate_workflow("1")

            assert result["success"] is True
            assert "activated" in result["message"]

    @pytest.mark.asyncio
    async def test_deactivate_workflow_success(self, integration):
        """Test successful workflow deactivation"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        with patch.object(integration, "_get_client", return_value=mock_client):
            result = await integration.deactivate_workflow("1")

            assert result["success"] is True
            assert "deactivated" in result["message"]

    @pytest.mark.asyncio
    async def test_trigger_workflow_success(self, integration):
        """Test successful workflow triggering"""
        # Mock workflow data
        workflow_data = {
            "nodes": [
                {
                    "type": "n8n-nodes-base.webhook",
                    "parameters": {"path": "test-webhook"},
                }
            ]
        }

        mock_workflow_response = Mock()
        mock_workflow_response.json.return_value = workflow_data

        mock_webhook_response = Mock()
        mock_webhook_response.raise_for_status.return_value = None
        mock_webhook_response.headers.get.return_value = "exec-123"
        mock_webhook_response.json.return_value = {"result": "success"}

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_workflow_response
        mock_client.post.return_value = mock_webhook_response

        with patch.object(integration, "_get_client", return_value=mock_client):
            result = await integration.trigger_workflow("1", {"test": "data"})

            assert result["success"] is True
            assert result["execution_id"] == "exec-123"

    @pytest.mark.asyncio
    async def test_get_executions_success(self, integration):
        """Test successful executions retrieval"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "data": [{"id": "exec-1", "status": "success"}],
            "meta": {"total": 1},
        }

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        with patch.object(integration, "_get_client", return_value=mock_client):
            result = await integration.get_executions(workflow_id="1", limit=10)

            assert result["executions"] == [{"id": "exec-1", "status": "success"}]
            assert result["total"] == 1

    @pytest.mark.asyncio
    async def test_get_execution_success(self, integration):
        """Test successful execution retrieval"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"id": "exec-1", "status": "success"}

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        with patch.object(integration, "_get_client", return_value=mock_client):
            result = await integration.get_execution("exec-1")

            assert result["id"] == "exec-1"
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_close(self, integration):
        """Test client closure"""
        mock_client = AsyncMock()
        integration.client = mock_client

        await integration.close()

        mock_client.aclose.assert_called_once()
        assert integration.client is None


def test_get_n8n_integration():
    """Test get_n8n_integration function"""
    from src.n8n_integration import _n8n_integration, get_n8n_integration

    # Initially should be None
    assert get_n8n_integration() is None

    # Set global instance
    import src.n8n_integration as n8n_module

    n8n_module._n8n_integration = "test_instance"

    assert get_n8n_integration() == "test_instance"

    # Reset
    _n8n_integration = None


def test_init_n8n_integration():
    """Test init_n8n_integration function"""
    from src.n8n_integration import get_n8n_integration, init_n8n_integration

    config = N8nConfig(base_url="http://test.com")
    integration = init_n8n_integration(config)

    assert isinstance(integration, N8nIntegration)
    assert integration.config == config
    assert get_n8n_integration() == integration


if __name__ == "__main__":
    pytest.main([__file__])
