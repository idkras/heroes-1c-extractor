/**
 * Frontend Result Display для MCP команд
 * Отображение MCP результатов в chat interface с real-time updates
 */

class MCPResultDisplay {
    constructor() {
        this.websocket = null;
        this.apiEndpoint = 'http://0.0.0.0:5002/api/mcp';
        this.websocketUrl = 'ws://0.0.0.0:5001';
        this.reconnectInterval = 5000;
        this.maxReconnectAttempts = 10;
        this.reconnectAttempts = 0;
        
        this.init();
    }
    
    init() {
        console.log('🚀 Initializing MCP Result Display...');
        this.setupWebSocket();
        this.setupPolling();
        this.createDisplayContainer();
    }
    
    setupWebSocket() {
        console.log(`🔌 Connecting to MCP WebSocket: ${this.websocketUrl}`);
        
        try {
            this.websocket = new WebSocket(this.websocketUrl);
            
            this.websocket.onopen = (event) => {
                console.log('✅ MCP WebSocket connected');
                this.reconnectAttempts = 0;
                this.showConnectionStatus('connected');
            };
            
            this.websocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMCPEvent(data);
                } catch (error) {
                    console.error('❌ Error parsing WebSocket message:', error);
                }
            };
            
            this.websocket.onclose = (event) => {
                console.log('🔌 MCP WebSocket disconnected');
                this.showConnectionStatus('disconnected');
                this.attemptReconnect();
            };
            
            this.websocket.onerror = (error) => {
                console.error('❌ MCP WebSocket error:', error);
                this.showConnectionStatus('error');
            };
            
        } catch (error) {
            console.error('❌ Failed to setup WebSocket:', error);
            this.showConnectionStatus('error');
        }
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`🔄 Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            
            setTimeout(() => {
                this.setupWebSocket();
            }, this.reconnectInterval);
        } else {
            console.log('❌ Max reconnection attempts reached');
            this.showConnectionStatus('failed');
        }
    }
    
    setupPolling() {
        // Fallback polling если WebSocket не работает
        setInterval(() => {
            if (!this.websocket || this.websocket.readyState !== WebSocket.OPEN) {
                this.pollMCPResults();
            }
        }, 3000);
    }
    
    async pollMCPResults() {
        try {
            const lastTimestamp = this.getLastResultTimestamp();
            const response = await fetch(`${this.apiEndpoint}/results?since=${lastTimestamp}`);
            
            if (response.ok) {
                const data = await response.json();
                if (data.success && data.results.length > 0) {
                    data.results.forEach(result => {
                        this.displayMCPResult(result);
                    });
                }
            }
        } catch (error) {
            console.log('📡 MCP API polling failed (using WebSocket)');
        }
    }
    
    createDisplayContainer() {
        // Создаем контейнер для отображения MCP результатов если его нет
        if (!document.getElementById('mcp-results-container')) {
            const container = document.createElement('div');
            container.id = 'mcp-results-container';
            container.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                width: 400px;
                max-height: 600px;
                background: #1a1a1a;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 16px;
                overflow-y: auto;
                z-index: 10000;
                font-family: 'Monaco', 'Menlo', monospace;
                font-size: 12px;
                color: #e0e0e0;
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            `;
            
            // Заголовок
            const header = document.createElement('div');
            header.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <span style="font-weight: bold; color: #4CAF50;">🤖 MCP Results</span>
                    <span id="mcp-connection-status" style="font-size: 10px; color: #888;">connecting...</span>
                </div>
            `;
            container.appendChild(header);
            
            // Контейнер для результатов
            const resultsContainer = document.createElement('div');
            resultsContainer.id = 'mcp-results-list';
            container.appendChild(resultsContainer);
            
            document.body.appendChild(container);
        }
    }
    
    handleMCPEvent(data) {
        console.log('📥 Received MCP event:', data);
        
        if (data.type === 'mcp_result') {
            this.displayMCPResult(data);
        } else if (data.type === 'connection_established') {
            console.log('✅ MCP connection established');
        }
    }
    
    displayMCPResult(result) {
        const resultsContainer = document.getElementById('mcp-results-list');
        if (!resultsContainer) return;
        
        const resultElement = document.createElement('div');
        resultElement.style.cssText = `
            margin-bottom: 12px;
            padding: 8px;
            background: #2d2d2d;
            border-radius: 4px;
            border-left: 3px solid #4CAF50;
            animation: fadeIn 0.3s ease-in;
        `;
        
        const timestamp = new Date(result.timestamp * 1000).toLocaleTimeString();
        const command = result.command || 'unknown';
        const status = result.status || 'completed';
        const duration = result.duration_ms || 0;
        
        resultElement.innerHTML = `
            <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 4px;">
                <span style="color: #4CAF50; font-weight: bold;">${command}</span>
                <span style="color: #888; font-size: 10px;">${timestamp}</span>
            </div>
            <div style="margin-bottom: 4px;">
                <span style="color: #FFC107;">Status:</span> ${status}
                <span style="color: #888; margin-left: 12px;">${duration}ms</span>
            </div>
            <div style="background: #1a1a1a; padding: 4px; border-radius: 2px; font-size: 11px; max-height: 100px; overflow-y: auto;">
                <pre style="margin: 0; white-space: pre-wrap;">${this.formatResult(result.result)}</pre>
            </div>
        `;
        
        // Добавляем CSS для анимации если его нет
        if (!document.getElementById('mcp-animation-styles')) {
            const style = document.createElement('style');
            style.id = 'mcp-animation-styles';
            style.textContent = `
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(10px); }
                    to { opacity: 1; transform: translateY(0); }
                }
            `;
            document.head.appendChild(style);
        }
        
        // Добавляем в начало списка (новые результаты сверху)
        resultsContainer.insertBefore(resultElement, resultsContainer.firstChild);
        
        // Ограничиваем количество отображаемых результатов
        while (resultsContainer.children.length > 20) {
            resultsContainer.removeChild(resultsContainer.lastChild);
        }
        
        console.log(`✅ Displayed MCP result: ${command}`);
    }
    
    formatResult(result) {
        if (typeof result === 'object') {
            return JSON.stringify(result, null, 2);
        }
        return String(result);
    }
    
    showConnectionStatus(status) {
        const statusElement = document.getElementById('mcp-connection-status');
        if (!statusElement) return;
        
        const statusConfig = {
            'connecting': { text: 'connecting...', color: '#FFC107' },
            'connected': { text: 'connected', color: '#4CAF50' },
            'disconnected': { text: 'disconnected', color: '#888' },
            'error': { text: 'error', color: '#F44336' },
            'failed': { text: 'failed', color: '#F44336' }
        };
        
        const config = statusConfig[status] || statusConfig['error'];
        statusElement.textContent = config.text;
        statusElement.style.color = config.color;
    }
    
    getLastResultTimestamp() {
        const resultsContainer = document.getElementById('mcp-results-list');
        if (!resultsContainer || !resultsContainer.firstChild) return 0;
        
        // Извлекаем timestamp из последнего результата
        return Date.now() / 1000 - 60; // Последняя минута
    }
}

// Автоматическая инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Starting MCP Result Display...');
    window.mcpDisplay = new MCPResultDisplay();
});

// Экспорт для использования в других модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MCPResultDisplay;
}