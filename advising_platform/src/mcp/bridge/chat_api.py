#!/usr/bin/env python3
"""
Chat Integration API
API endpoint для получения MCP результатов в chat интерфейсе
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import time
import logging
from typing import Dict, Any, List
from pathlib import Path
import threading
from queue import Queue, Empty

logger = logging.getLogger(__name__)

class MCPChatAPI:
    """Flask API для интеграции MCP результатов с chat"""
    
    def __init__(self, port: int = 5002):
        self.port = port
        self.app = Flask(__name__)
        CORS(self.app)  # Разрешаем CORS для frontend
        
        # Очередь результатов MCP
        self.results_queue = Queue()
        self.recent_results = []  # Последние результаты для polling
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Настройка API endpoints"""
        
        @self.app.route('/api/mcp/results', methods=['GET'])
        def get_mcp_results():
            """Получение MCP результатов для chat"""
            try:
                # Получаем параметры запроса
                since = request.args.get('since', type=float, default=0)
                limit = request.args.get('limit', type=int, default=50)
                
                # Фильтруем результаты по времени
                filtered_results = [
                    result for result in self.recent_results
                    if result.get('timestamp', 0) > since
                ]
                
                # Ограничиваем количество
                limited_results = filtered_results[-limit:]
                
                return jsonify({
                    'success': True,
                    'results': limited_results,
                    'count': len(limited_results),
                    'server_time': time.time()
                })
                
            except Exception as e:
                logger.error(f"❌ Error getting MCP results: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/mcp/status', methods=['GET'])
        def get_mcp_status():
            """Статус MCP системы"""
            return jsonify({
                'success': True,
                'status': 'active',
                'pending_results': self.results_queue.qsize(),
                'recent_results_count': len(self.recent_results),
                'server_time': time.time()
            })
        
        @self.app.route('/api/mcp/submit', methods=['POST'])
        def submit_mcp_result():
            """Endpoint для отправки MCP результатов"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({
                        'success': False,
                        'error': 'No JSON data provided'
                    }), 400
                
                # Добавляем timestamp
                data['timestamp'] = time.time()
                data['received_at'] = time.time()
                
                # Добавляем в очередь и recent results
                self.add_mcp_result(data)
                
                return jsonify({
                    'success': True,
                    'message': 'MCP result submitted successfully'
                })
                
            except Exception as e:
                logger.error(f"❌ Error submitting MCP result: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'service': 'MCP Chat API',
                'timestamp': time.time()
            })
    
    def add_mcp_result(self, result: Dict[str, Any]):
        """Добавляет MCP результат в систему"""
        # Добавляем в очередь
        self.results_queue.put(result)
        
        # Добавляем в recent results
        self.recent_results.append(result)
        
        # Ограничиваем размер recent results (последние 100)
        if len(self.recent_results) > 100:
            self.recent_results = self.recent_results[-100:]
        
        logger.info(f"📥 Added MCP result: {result.get('command', 'unknown')}")
    
    def start_api_server(self):
        """Запускает Flask API сервер"""
        logger.info(f"🚀 Starting MCP Chat API on port {self.port}")
        
        try:
            self.app.run(
                host='0.0.0.0',
                port=self.port,
                debug=False,
                threaded=True
            )
        except Exception as e:
            logger.error(f"❌ Failed to start API server: {e}")
            raise
    
    def start_in_background(self):
        """Запускает API сервер в background thread"""
        def run_server():
            self.start_api_server()
        
        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
        logger.info(f"✅ MCP Chat API started in background on port {self.port}")
        return thread

# Глобальный API instance
_api_instance = None

def get_chat_api() -> MCPChatAPI:
    """Получает глобальный API instance"""
    global _api_instance
    if _api_instance is None:
        _api_instance = MCPChatAPI()
    return _api_instance

def submit_mcp_result_to_chat(command: str, result: Dict[str, Any], 
                             duration_ms: float = 0, status: str = "completed"):
    """Отправляет MCP результат в chat API"""
    api = get_chat_api()
    
    mcp_result = {
        "command": command,
        "result": result,
        "duration_ms": duration_ms,
        "status": status,
        "timestamp": time.time()
    }
    
    api.add_mcp_result(mcp_result)

if __name__ == "__main__":
    """Запуск Chat API сервера"""
    print("🚀 Starting MCP Chat API Server...")
    try:
        api = MCPChatAPI()
        api.start_api_server()
    except KeyboardInterrupt:
        print("🛑 MCP Chat API stopped")
    except Exception as e:
        print(f"❌ API Server error: {e}")