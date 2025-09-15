#!/usr/bin/env python3
"""
MCP-to-Chat Bridge Service
Перехватывает результаты MCP команд и отправляет в chat интерфейс
"""

import asyncio
import json
import sys
import time
from typing import Dict, Any, Optional
from pathlib import Path
import websockets
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPChatBridge:
    """Bridge для передачи результатов MCP команд в chat интерфейс"""
    
    def __init__(self, websocket_port: int = 5001):
        self.websocket_port = websocket_port
        self.active_connections = set()
        self.mcp_results_queue = asyncio.Queue()
        
    async def start_bridge_server(self):
        """Запускает WebSocket сервер для bridge"""
        logger.info(f"🌉 Starting MCP-to-Chat Bridge on port {self.websocket_port}")
        
        async def handle_client(websocket, path):
            """Обработка подключений клиентов"""
            self.active_connections.add(websocket)
            logger.info(f"📱 Chat client connected: {websocket.remote_address}")
            
            try:
                await websocket.wait_closed()
            finally:
                self.active_connections.remove(websocket)
                logger.info(f"📱 Chat client disconnected")
        
        # Запуск WebSocket сервера
        server = await websockets.serve(handle_client, "0.0.0.0", self.websocket_port)
        logger.info(f"✅ MCP Bridge Server running on ws://0.0.0.0:{self.websocket_port}")
        
        # Запуск обработчика результатов
        asyncio.create_task(self._process_mcp_results())
        
        await server.wait_closed()
    
    async def _process_mcp_results(self):
        """Обрабатывает очередь результатов MCP и отправляет в chat"""
        while True:
            try:
                # Получаем результат из очереди
                result = await self.mcp_results_queue.get()
                
                # Форматируем для отправки в chat
                chat_message = self._format_for_chat(result)
                
                # Отправляем всем подключенным клиентам
                if self.active_connections:
                    await self._broadcast_to_chat(chat_message)
                
                self.mcp_results_queue.task_done()
                
            except Exception as e:
                logger.error(f"❌ Error processing MCP result: {e}")
                await asyncio.sleep(1)
    
    def _format_for_chat(self, mcp_result: Dict[str, Any]) -> Dict[str, Any]:
        """Форматирует результат MCP для отображения в chat"""
        return {
            "type": "mcp_result",
            "timestamp": time.time(),
            "command": mcp_result.get("command", "unknown"),
            "status": mcp_result.get("status", "completed"),
            "result": mcp_result.get("result", {}),
            "duration_ms": mcp_result.get("duration_ms", 0),
            "formatted_output": self._create_formatted_output(mcp_result)
        }
    
    def _create_formatted_output(self, mcp_result: Dict[str, Any]) -> str:
        """Создает форматированный вывод для chat интерфейса"""
        command = mcp_result.get("command", "unknown")
        status = mcp_result.get("status", "completed")
        result = mcp_result.get("result", {})
        duration = mcp_result.get("duration_ms", 0)
        
        output = f"🤖 **MCP Command**: `{command}`\n"
        output += f"⏱️ **Duration**: {duration}ms\n"
        output += f"📊 **Status**: {status}\n\n"
        
        if isinstance(result, dict):
            output += "📋 **Result**:\n```json\n"
            output += json.dumps(result, indent=2, ensure_ascii=False)
            output += "\n```"
        else:
            output += f"📋 **Result**: {result}"
        
        return output
    
    async def _broadcast_to_chat(self, message: Dict[str, Any]):
        """Отправляет сообщение всем подключенным chat клиентам"""
        if not self.active_connections:
            return
        
        message_json = json.dumps(message, ensure_ascii=False)
        
        # Отправляем всем активным подключениям
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send(message_json)
                logger.info(f"📤 Sent MCP result to chat: {message['command']}")
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(connection)
            except Exception as e:
                logger.error(f"❌ Error sending to chat: {e}")
                disconnected.add(connection)
        
        # Удаляем отключенные соединения
        self.active_connections -= disconnected
    
    async def send_mcp_result(self, command: str, result: Dict[str, Any], 
                            duration_ms: float = 0, status: str = "completed"):
        """Отправляет результат MCP команды в chat"""
        mcp_result = {
            "command": command,
            "result": result,
            "duration_ms": duration_ms,
            "status": status,
            "timestamp": time.time()
        }
        
        await self.mcp_results_queue.put(mcp_result)
        logger.info(f"📥 Queued MCP result for chat: {command}")

# Глобальный экземпляр bridge
_bridge_instance: Optional[MCPChatBridge] = None

def get_bridge() -> MCPChatBridge:
    """Получает глобальный экземпляр bridge"""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = MCPChatBridge()
    return _bridge_instance

async def start_bridge_service():
    """Запускает bridge service"""
    bridge = get_bridge()
    await bridge.start_bridge_server()

def send_to_chat_sync(command: str, result: Dict[str, Any], 
                     duration_ms: float = 0, status: str = "completed"):
    """Синхронная отправка в chat (для использования в MCP модулях)"""
    bridge = get_bridge()
    
    # Если event loop уже запущен, добавляем в очередь
    try:
        loop = asyncio.get_running_loop()
        asyncio.create_task(bridge.send_mcp_result(command, result, duration_ms, status))
    except RuntimeError:
        # Если event loop не запущен, создаем новый
        asyncio.run(bridge.send_mcp_result(command, result, duration_ms, status))

if __name__ == "__main__":
    """Запуск bridge сервера"""
    print("🌉 Starting MCP-to-Chat Bridge Service...")
    try:
        asyncio.run(start_bridge_service())
    except KeyboardInterrupt:
        print("🛑 MCP Bridge Service stopped")
    except Exception as e:
        print(f"❌ Bridge Service error: {e}")