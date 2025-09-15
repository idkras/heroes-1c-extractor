#!/usr/bin/env python3
"""
MCP HTTP Adapter: Единый HTTP/WebSocket API для всех MCP операций

JTBD: Я хочу единый HTTP endpoint для всех MCP команд,
чтобы заменить отдельные MCPChatAPI и MCPChatBridge endpoints.

Based on: advising_platform/src/mcp/mcp_orchestrator.py (класс MCPOrchestrator)
Replaces: 
- http://localhost:5002 (MCPChatAPI) 
- ws://localhost:5001 (MCPChatBridge)
Integration: с существующими workflow (ApiServer, DuckDBCacheAPI)
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from advising_platform.src.mcp.mcp_orchestrator import MCPOrchestrator
except ImportError:
    # Alternative import path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from mcp.mcp_orchestrator import MCPOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPHTTPAdapter:
    """Единый HTTP/WebSocket адаптер для всех MCP операций"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 5005):
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Initialize MCP Orchestrator
        self.orchestrator = MCPOrchestrator()
        
        # Register routes
        self._register_http_routes()
        
        logger.info(f"🚀 MCP HTTP Adapter initialized on {host}:{port}")
    
    def _register_http_routes(self):
        """Регистрация HTTP маршрутов"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Проверка работоспособности адаптера"""
            return jsonify({
                "status": "healthy",
                "service": "MCP HTTP Adapter", 
                "timestamp": datetime.now().isoformat(),
                "mcp_commands_available": len(self.orchestrator.get_mcp_commands()),
                "python_backends_count": 22
            })
        
        @self.app.route('/mcp/commands', methods=['GET'])
        def list_mcp_commands():
            """Список всех доступных MCP команд"""
            try:
                commands = self.orchestrator.get_mcp_commands()
                return jsonify({
                    "success": True,
                    "commands": list(commands.keys()),
                    "total_count": len(commands),
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error listing commands: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/mcp/execute/<command_name>', methods=['POST'])
        def execute_mcp_command(command_name: str):
            """Выполнение конкретной MCP команды"""
            try:
                data = request.get_json() or {}
                
                # Validate command exists
                available_commands = self.orchestrator.get_mcp_commands()
                if command_name not in available_commands:
                    return jsonify({
                        "success": False,
                        "error": f"Command '{command_name}' not found",
                        "available_commands": list(available_commands.keys())
                    }), 404
                
                # Execute command via orchestrator
                result = available_commands[command_name](data)
                
                return jsonify({
                    "success": True,
                    "command": command_name,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Error executing command {command_name}: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e),
                    "command": command_name
                }), 500
        
        @self.app.route('/mcp/python-module/<module_name>', methods=['POST'])
        def call_python_module(module_name: str):
            """Прямой вызов Python модуля из backends"""
            try:
                data = request.get_json() or {}
                
                # Call module via orchestrator
                result = self.orchestrator.call_python_module(module_name, data)
                
                return jsonify({
                    "success": True,
                    "module": module_name,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Error calling module {module_name}: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e),
                    "module": module_name
                }), 500
        
        @self.app.route('/mcp/workflow/execute', methods=['POST'])
        def execute_full_workflow():
            """Выполнение полного MCP workflow цикла"""
            try:
                data = request.get_json() or {}
                initial_input = json.dumps(data)
                
                # Execute full cycle via orchestrator
                result = self.orchestrator.execute_full_cycle(initial_input)
                
                return jsonify({
                    "success": True,
                    "workflow_result": result,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Error executing workflow: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/mcp/status', methods=['GET'])
        def get_workflow_status():
            """Получение статуса текущего workflow"""
            try:
                status = self.orchestrator.get_workflow_status()
                return jsonify({
                    "success": True,
                    "status": status,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error getting status: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        # BACKWARD COMPATIBILITY: Bridge с MCPChatAPI endpoints
        @self.app.route('/chat/send', methods=['POST'])
        def chat_send_compatibility():
            """Совместимость с MCPChatAPI /chat/send"""
            try:
                data = request.get_json() or {}
                message = data.get('message', '')
                
                # Convert chat message to MCP workflow
                workflow_input = {
                    "type": "chat_message",
                    "content": message,
                    "timestamp": datetime.now().isoformat()
                }
                
                result = self.orchestrator.execute_full_cycle(json.dumps(workflow_input))
                
                return jsonify({
                    "success": True,
                    "response": result.get("final_result", "Workflow executed"),
                    "workflow_id": result.get("workflow_id"),
                    "compatibility_mode": "MCPChatAPI"
                })
                
            except Exception as e:
                logger.error(f"Error in chat compatibility mode: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
    
    # NOTE: WebSocket functionality removed to focus on HTTP API first
    # Can be added later with flask-socketio or similar extension
    
    def run(self, debug: bool = False):
        """Запуск HTTP/WebSocket сервера"""
        logger.info(f"🚀 Starting MCP HTTP Adapter on {self.host}:{self.port}")
        logger.info("📋 Available endpoints:")
        logger.info("   GET  /health - Health check")
        logger.info("   GET  /mcp/commands - List MCP commands")
        logger.info("   POST /mcp/execute/<command> - Execute MCP command")
        logger.info("   POST /mcp/python-module/<module> - Call Python module")
        logger.info("   POST /mcp/workflow/execute - Execute full workflow")
        logger.info("   GET  /mcp/status - Get workflow status")
        logger.info("   POST /chat/send - Compatibility with MCPChatAPI")
        logger.info("   NOTE: WebSocket support planned for future implementation")
        self.app.run(host=self.host, port=self.port, debug=debug)


def main():
    """Main entry point"""
    adapter = MCPHTTPAdapter(host="0.0.0.0", port=5005)
    adapter.run(debug=False)


if __name__ == "__main__":
    main()