#!/usr/bin/env python3
"""
WebSocket Event Streaming для MCP результатов
Real-time передача MCP результатов в frontend
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Set
import websockets
from websockets.server import WebSocketServerProtocol

logger = logging.getLogger(__name__)

class MCPWebSocketStreamer:
    """WebSocket streamer для real-time передачи MCP events"""
    
    def __init__(self, port: int = 5001):
        self.port = port
        self.clients: Set[WebSocketServerProtocol] = set()
        self.event_queue = asyncio.Queue()
        
    async def start_streaming_server(self):
        """Запускает WebSocket сервер для streaming"""
        logger.info(f"🌊 Starting MCP WebSocket Streamer on port {self.port}")
        
        async def handle_websocket(websocket, path):
            """Обработка WebSocket подключений"""
            await self.register_client(websocket)
            try:
                await websocket.wait_closed()
            finally:
                await self.unregister_client(websocket)
        
        server = await websockets.serve(
            handle_websocket, 
            "0.0.0.0", 
            self.port,
            ping_interval=20,
            ping_timeout=10
        )
        
        # Запуск event broadcaster
        asyncio.create_task(self.event_broadcaster())
        
        logger.info(f"✅ MCP WebSocket Streamer ready on ws://0.0.0.0:{self.port}")
        await server.wait_closed()
    
    async def register_client(self, websocket: WebSocketServerProtocol):
        """Регистрирует нового WebSocket клиента"""
        self.clients.add(websocket)
        client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"📱 WebSocket client connected: {client_info}")
        
        # Отправляем приветственное сообщение
        welcome_message = {
            "type": "connection_established",
            "message": "Connected to MCP Event Stream",
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.send_to_client(websocket, welcome_message)
    
    async def unregister_client(self, websocket: WebSocketServerProtocol):
        """Отменяет регистрацию WebSocket клиента"""
        self.clients.discard(websocket)
        logger.info(f"📱 WebSocket client disconnected")
    
    async def send_to_client(self, websocket: WebSocketServerProtocol, message: Dict[str, Any]):
        """Отправляет сообщение конкретному клиенту"""
        try:
            await websocket.send(json.dumps(message, ensure_ascii=False))
        except websockets.exceptions.ConnectionClosed:
            self.clients.discard(websocket)
        except Exception as e:
            logger.error(f"❌ Error sending to client: {e}")
            self.clients.discard(websocket)
    
    async def broadcast_mcp_event(self, event: Dict[str, Any]):
        """Добавляет MCP event в очередь для broadcast"""
        await self.event_queue.put(event)
    
    async def event_broadcaster(self):
        """Основной цикл broadcast events"""
        while True:
            try:
                # Получаем event из очереди
                event = await self.event_queue.get()
                
                if not self.clients:
                    self.event_queue.task_done()
                    continue
                
                # Форматируем event для WebSocket
                ws_message = self.format_websocket_message(event)
                
                # Отправляем всем подключенным клиентам
                disconnected_clients = set()
                for client in self.clients.copy():
                    try:
                        await client.send(json.dumps(ws_message, ensure_ascii=False))
                    except websockets.exceptions.ConnectionClosed:
                        disconnected_clients.add(client)
                    except Exception as e:
                        logger.error(f"❌ Broadcast error: {e}")
                        disconnected_clients.add(client)
                
                # Удаляем отключенных клиентов
                self.clients -= disconnected_clients
                
                if self.clients:
                    logger.info(f"📤 Broadcasted MCP event to {len(self.clients)} clients")
                
                self.event_queue.task_done()
                
            except Exception as e:
                logger.error(f"❌ Event broadcaster error: {e}")
                await asyncio.sleep(1)
    
    def format_websocket_message(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Форматирует event для WebSocket transmission"""
        return {
            "type": "mcp_event",
            "timestamp": asyncio.get_event_loop().time(),
            "event_data": event,
            "client_count": len(self.clients)
        }

# Глобальный streamer instance
_streamer_instance = None

def get_streamer() -> MCPWebSocketStreamer:
    """Получает глобальный streamer instance"""
    global _streamer_instance
    if _streamer_instance is None:
        _streamer_instance = MCPWebSocketStreamer()
    return _streamer_instance

async def stream_mcp_event(event: Dict[str, Any]):
    """Streams MCP event через WebSocket"""
    streamer = get_streamer()
    await streamer.broadcast_mcp_event(event)

if __name__ == "__main__":
    """Запуск WebSocket streaming сервера"""
    print("🌊 Starting MCP WebSocket Streamer...")
    try:
        streamer = MCPWebSocketStreamer()
        asyncio.run(streamer.start_streaming_server())
    except KeyboardInterrupt:
        print("🛑 MCP WebSocket Streamer stopped")
    except Exception as e:
        print(f"❌ Streamer error: {e}")