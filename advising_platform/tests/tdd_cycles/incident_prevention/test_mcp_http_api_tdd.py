#!/usr/bin/env python3
"""
TDD тесты для предотвращения инцидента MCP HTTP API
Инцидент: MCP Standards Server недоступен через HTTP (28 мая 2025)

По стандарту TDD-doc 4.1: Red-Green-Refactor цикл
"""

import pytest
import requests
import json
import time


class TestMCPHTTPAPIIncidentPrevention:
    """
    TDD тесты, которые выявили бы проблему MCP HTTP API раньше
    """
    
    def setup_method(self):
        """Настройка для каждого теста"""
        self.mcp_server_url = "http://localhost:3001"
        self.api_timeout = 5
        
    # RED PHASE - Тесты, которые должны были ПРОВАЛИТЬСЯ и выявить проблему
    
    def test_mcp_server_http_accessibility_red(self):
        """
        RED: Проверка доступности MCP сервера через HTTP
        
        Этот тест выявил бы проблему сразу:
        MCP сервер запущен, но HTTP API недоступен
        """
        try:
            response = requests.get(f"{self.mcp_server_url}/health", timeout=self.api_timeout)
            assert response.status_code == 200, "MCP HTTP API недоступен"
            
            health_data = response.json()
            assert "status" in health_data, "Health endpoint не возвращает статус"
            assert health_data["status"] == "healthy", "MCP сервер не в здоровом состоянии"
            
        except requests.ConnectionError:
            pytest.fail("КРИТИЧНО: MCP сервер недоступен через HTTP - Connection Refused")
        except requests.Timeout:
            pytest.fail("КРИТИЧНО: MCP сервер не отвечает - таймаут")
    
    def test_standards_creation_endpoint_red(self):
        """
        RED: Проверка endpoint для создания стандартов
        
        Этот тест выявил бы отсутствие POST /standards endpoint
        """
        standard_data = {
            "title": "Unit Economics Standard",
            "content": "Test standard content",
            "category": "economics",
            "author": "AI Assistant"
        }
        
        try:
            response = requests.post(
                f"{self.mcp_server_url}/standards",
                json=standard_data,
                timeout=self.api_timeout
            )
            
            assert response.status_code in [200, 201], f"Endpoint POST /standards не работает: {response.status_code}"
            
            response_data = response.json()
            assert "id" in response_data, "Создание стандарта не возвращает ID"
            assert "title" in response_data, "Ответ не содержит title стандарта"
            
        except requests.ConnectionError:
            pytest.fail("КРИТИЧНО: Endpoint POST /standards недоступен - Connection Refused")
    
    def test_mcp_to_http_bridge_integration_red(self):
        """
        RED: Проверка интеграции между MCP командами и HTTP API
        
        Этот тест выявил бы разрыв между MCP протоколом и HTTP
        """
        mcp_commands_endpoint = f"{self.mcp_server_url}/mcp/commands"
        
        try:
            response = requests.get(mcp_commands_endpoint, timeout=self.api_timeout)
            assert response.status_code == 200, "MCP команды недоступны через HTTP"
            
            data = response.json()
            assert "commands" in data, "Ответ не содержит список команд"
            commands = data["commands"]
            assert "standards-resolver" in [cmd["name"] for cmd in commands], "MCP команда standards-resolver недоступна"
            
        except requests.ConnectionError:
            pytest.fail("КРИТИЧНО: MCP-HTTP bridge не реализован")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])