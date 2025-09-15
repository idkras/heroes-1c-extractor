#!/usr/bin/env python
"""
Визуализатор связей между рабочими элементами.

Создает HTML-отчет с интерактивной визуализацией графа связей между
задачами, инцидентами, гипотезами и стандартами.

Автор: AI Assistant
Дата: 20 мая 2025
"""

import os
import sys
import json
import logging
from typing import Dict, List, Set, Any, Optional, Tuple, Union

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("relation_visualizer")

# HTML шаблон для визуализации
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Визуализация связей между рабочими элементами</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.2/vis-network.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/vis-data/7.1.2/vis-data.min.js"></script>
    <style>
        body, html {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            height: 100%;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }
        
        .container {
            display: flex;
            height: 100%;
            flex-direction: column;
        }
        
        .header {
            background-color: #2c3e50;
            color: white;
            padding: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header h1 {
            margin: 0;
            font-size: 1.5rem;
        }
        
        .content-wrapper {
            display: flex;
            flex: 1;
            overflow: hidden;
        }
        
        #visualization {
            flex: 1;
            position: relative;
        }
        
        .sidebar {
            width: 300px;
            background-color: white;
            border-left: 1px solid #ddd;
            padding: 15px;
            overflow-y: auto;
        }
        
        .sidebar h2 {
            margin-top: 0;
            font-size: 1.2rem;
            color: #2c3e50;
        }
        
        .controls {
            padding: 10px;
            background-color: #f9f9f9;
            border-bottom: 1px solid #ddd;
        }
        
        .filter-group {
            margin-bottom: 10px;
        }
        
        .filter-group label {
            font-weight: bold;
            margin-bottom: 5px;
            display: block;
        }
        
        .checkbox-group {
            display: flex;
            flex-wrap: wrap;
        }
        
        .checkbox-item {
            margin-right: 10px;
            margin-bottom: 5px;
        }
        
        #item-details {
            margin-top: 20px;
        }
        
        .detail-card {
            background-color: #fff;
            border-radius: 5px;
            padding: 15px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        
        .detail-title {
            font-size: 1.1rem;
            font-weight: bold;
            margin-bottom: 10px;
            color: #2c3e50;
        }
        
        .detail-property {
            margin-bottom: 5px;
        }
        
        .detail-label {
            font-weight: bold;
            color: #555;
        }
        
        .status-badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: bold;
            color: white;
        }
        
        .status-backlog { background-color: #7f8c8d; }
        .status-todo { background-color: #3498db; }
        .status-in-progress { background-color: #f39c12; }
        .status-review { background-color: #9b59b6; }
        .status-done { background-color: #2ecc71; }
        .status-blocked { background-color: #e74c3c; }
        .status-investigating { background-color: #f39c12; }
        .status-resolved { background-color: #2ecc71; }
        .status-proposed { background-color: #3498db; }
        .status-testing { background-color: #f39c12; }
        .status-validated { background-color: #2ecc71; }
        .status-invalidated { background-color: #e74c3c; }
        .status-draft { background-color: #7f8c8d; }
        .status-review-pending { background-color: #9b59b6; }
        .status-approved { background-color: #2ecc71; }
        .status-deprecated { background-color: #e74c3c; }
        .status-superseded { background-color: #e74c3c; }
        
        .type-badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: bold;
            color: white;
            margin-right: 5px;
        }
        
        .type-task { background-color: #3498db; }
        .type-incident { background-color: #e74c3c; }
        .type-hypothesis { background-color: #9b59b6; }
        .type-standard { background-color: #2ecc71; }
        
        .relations-list {
            margin-top: 10px;
        }
        
        .relation-item {
            padding: 5px 0;
            border-bottom: 1px solid #eee;
        }
        
        .relation-type {
            font-style: italic;
            color: #555;
        }
        
        .search-box {
            margin-bottom: 15px;
        }
        
        .search-box input {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        
        .legend {
            margin-top: 15px;
            padding: 10px;
            background-color: #f9f9f9;
            border-radius: 5px;
        }
        
        .legend-title {
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }
        
        .legend-color {
            width: 15px;
            height: 15px;
            margin-right: 8px;
            border-radius: 50%;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Визуализация связей между рабочими элементами</h1>
            <div>
                <select id="layout-select">
                    <option value="hierarchical">Иерархический</option>
                    <option value="force">Силовой</option>
                    <option value="circular">Круговой</option>
                </select>
                <button id="export-button">Экспорт</button>
            </div>
        </div>
        
        <div class="controls">
            <div class="filter-group">
                <label>Типы элементов:</label>
                <div class="checkbox-group" id="type-filters">
                    <div class="checkbox-item">
                        <input type="checkbox" id="type-task" checked>
                        <label for="type-task">Задачи</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="checkbox" id="type-incident" checked>
                        <label for="type-incident">Инциденты</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="checkbox" id="type-hypothesis" checked>
                        <label for="type-hypothesis">Гипотезы</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="checkbox" id="type-standard" checked>
                        <label for="type-standard">Стандарты</label>
                    </div>
                </div>
            </div>
            
            <div class="filter-group">
                <label>Статусы:</label>
                <div class="checkbox-group" id="status-filters">
                    <div class="checkbox-item">
                        <input type="checkbox" id="status-backlog" checked>
                        <label for="status-backlog">Бэклог</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="checkbox" id="status-todo" checked>
                        <label for="status-todo">К выполнению</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="checkbox" id="status-in-progress" checked>
                        <label for="status-in-progress">В работе</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="checkbox" id="status-done" checked>
                        <label for="status-done">Выполнено</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="checkbox" id="status-other" checked>
                        <label for="status-other">Прочие</label>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="content-wrapper">
            <div id="visualization"></div>
            
            <div class="sidebar">
                <div class="search-box">
                    <input type="text" id="search-input" placeholder="Поиск элементов...">
                </div>
                
                <div id="item-details">
                    <p>Выберите элемент на графе для просмотра дополнительной информации.</p>
                </div>
                
                <div class="legend">
                    <div class="legend-title">Типы элементов:</div>
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: #3498db;"></div>
                        <span>Задачи</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: #e74c3c;"></div>
                        <span>Инциденты</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: #9b59b6;"></div>
                        <span>Гипотезы</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: #2ecc71;"></div>
                        <span>Стандарты</span>
                    </div>
                    
                    <div class="legend-title" style="margin-top: 10px;">Типы связей:</div>
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: #3498db;"></div>
                        <span>Relates To</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: #e74c3c;"></div>
                        <span>Blocks</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: #f39c12;"></div>
                        <span>Depends On</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: #2ecc71;"></div>
                        <span>Parent/Child</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Данные графа
        const graphData = JSON.parse('$GRAPH_DATA');
        
        // Инициализация элементов графа
        const nodes = new vis.DataSet(graphData.nodes);
        const edges = new vis.DataSet(graphData.edges);
        
        // Создание графа
        const container = document.getElementById('visualization');
        const data = { nodes, edges };
        
        // Параметры визуализации
        const options = {
            nodes: {
                shape: 'box',
                margin: 10,
                font: {
                    size: 14
                },
                borderWidth: 2,
                shadow: true
            },
            edges: {
                width: 2,
                shadow: true,
                smooth: {
                    type: 'continuous'
                },
                arrows: {
                    to: {
                        enabled: true,
                        scaleFactor: 0.5
                    }
                }
            },
            physics: {
                stabilization: true,
                barnesHut: {
                    gravitationalConstant: -2000,
                    springConstant: 0.04,
                    springLength: 95
                }
            },
            interaction: {
                hover: true,
                tooltipDelay: 200,
                zoomView: true,
                dragView: true
            },
            layout: {
                improvedLayout: true
            }
        };
        
        // Создание сети
        const network = new vis.Network(container, data, options);
        
        // Обработка событий
        network.on('click', function(params) {
            if (params.nodes.length > 0) {
                const nodeId = params.nodes[0];
                const node = nodes.get(nodeId);
                displayItemDetails(node);
            } else {
                document.getElementById('item-details').innerHTML = '<p>Выберите элемент на графе для просмотра дополнительной информации.</p>';
            }
        });
        
        // Отображение информации о выбранном элементе
        function displayItemDetails(node) {
            const statusClass = 'status-' + node.status;
            const typeClass = 'type-' + node.type;
            
            let html = `
                <div class="detail-card">
                    <div class="detail-title">
                        <span class="type-badge ${typeClass}">${formatItemType(node.type)}</span>
                        ${node.label}
                    </div>
                    <div class="detail-property">
                        <span class="detail-label">ID:</span> ${node.id}
                    </div>
                    <div class="detail-property">
                        <span class="detail-label">Статус:</span> 
                        <span class="status-badge ${statusClass}">${formatStatus(node.status)}</span>
                    </div>`;
            
            if (node.author) {
                html += `<div class="detail-property">
                    <span class="detail-label">Автор:</span> ${node.author}
                </div>`;
            }
            
            if (node.assignee) {
                html += `<div class="detail-property">
                    <span class="detail-label">Ответственный:</span> ${node.assignee}
                </div>`;
            }
            
            if (node.filePath) {
                html += `<div class="detail-property">
                    <span class="detail-label">Файл:</span> ${node.filePath}
                </div>`;
            }
            
            if (node.description) {
                html += `<div class="detail-property">
                    <span class="detail-label">Описание:</span><br>
                    <div style="margin-top: 5px; max-height: 150px; overflow-y: auto;">
                        ${node.description.replace(/\\n/g, '<br>')}
                    </div>
                </div>`;
            }
            
            // Связи
            const connections = getConnections(node.id);
            if (connections.length > 0) {
                html += `<div class="detail-property">
                    <span class="detail-label">Связи:</span>
                    <div class="relations-list">`;
                
                connections.forEach(conn => {
                    const targetNode = nodes.get(conn.to === node.id ? conn.from : conn.to);
                    const direction = conn.from === node.id ? 'с' : 'от';
                    
                    html += `<div class="relation-item">
                        <span class="relation-type">${formatRelationType(conn.label)}</span> ${direction}
                        <strong>${targetNode.label}</strong> (${targetNode.id})
                    </div>`;
                });
                
                html += `</div></div>`;
            }
            
            html += `</div>`;
            
            document.getElementById('item-details').innerHTML = html;
        }
        
        // Получение всех связей выбранного элемента
        function getConnections(nodeId) {
            return edges.get().filter(edge => edge.from === nodeId || edge.to === nodeId);
        }
        
        // Форматирование типа элемента
        function formatItemType(type) {
            const types = {
                'task': 'Задача',
                'incident': 'Инцидент',
                'hypothesis': 'Гипотеза',
                'standard': 'Стандарт'
            };
            return types[type] || type;
        }
        
        // Форматирование статуса
        function formatStatus(status) {
            const statuses = {
                'backlog': 'Бэклог',
                'todo': 'К выполнению',
                'in_progress': 'В работе',
                'done': 'Выполнено',
                'review': 'На проверке',
                'blocked': 'Заблокировано',
                'investigating': 'Исследуется',
                'resolved': 'Решено',
                'proposed': 'Предложено',
                'testing': 'Тестируется',
                'validated': 'Подтверждено',
                'invalidated': 'Опровергнуто',
                'draft': 'Черновик',
                'review_pending': 'Ожидает проверки',
                'approved': 'Одобрено',
                'deprecated': 'Устарело',
                'superseded': 'Заменено'
            };
            return statuses[status] || status;
        }
        
        // Форматирование типа связи
        function formatRelationType(type) {
            const types = {
                'relates_to': 'Связан с',
                'blocks': 'Блокирует',
                'blocked_by': 'Блокируется',
                'depends_on': 'Зависит от',
                'parent_of': 'Родитель для',
                'child_of': 'Потомок от',
                'derived_from': 'Получен из',
                'supersedes': 'Заменяет',
                'superseded_by': 'Заменен'
            };
            return types[type] || type;
        }
        
        // Изменение макета графа
        document.getElementById('layout-select').addEventListener('change', function(event) {
            const layout = event.target.value;
            
            if (layout === 'hierarchical') {
                network.setOptions({
                    layout: {
                        hierarchical: {
                            direction: 'UD',
                            sortMethod: 'directed',
                            nodeSpacing: 150,
                            levelSeparation: 150
                        }
                    }
                });
            } else if (layout === 'force') {
                network.setOptions({
                    layout: {
                        hierarchical: false
                    },
                    physics: {
                        enabled: true,
                        barnesHut: {
                            gravitationalConstant: -2000,
                            springConstant: 0.04,
                            springLength: 95
                        }
                    }
                });
            } else if (layout === 'circular') {
                network.setOptions({
                    layout: {
                        hierarchical: false
                    },
                    physics: {
                        enabled: true,
                        barnesHut: {
                            gravitationalConstant: -10000,
                            springConstant: 0.04,
                            springLength: 195
                        }
                    }
                });
                
                // Устанавливаем круговое расположение
                const positions = {};
                const nodeIds = nodes.getIds();
                const radius = Math.min(container.clientWidth, container.clientHeight) * 0.4;
                const center = {
                    x: container.clientWidth / 2,
                    y: container.clientHeight / 2
                };
                
                nodeIds.forEach((id, index) => {
                    const angle = 2 * Math.PI * index / nodeIds.length;
                    positions[id] = {
                        x: center.x + radius * Math.cos(angle),
                        y: center.y + radius * Math.sin(angle)
                    };
                });
                
                network.setOptions({ physics: false });
                network.setPositions(positions);
                setTimeout(() => {
                    network.setOptions({ physics: true });
                }, 500);
            }
        });
        
        // Фильтрация по типу элемента
        document.querySelectorAll('#type-filters input').forEach(checkbox => {
            checkbox.addEventListener('change', applyFilters);
        });
        
        // Фильтрация по статусу
        document.querySelectorAll('#status-filters input').forEach(checkbox => {
            checkbox.addEventListener('change', applyFilters);
        });
        
        // Поиск элементов
        document.getElementById('search-input').addEventListener('input', function(event) {
            applyFilters();
        });
        
        // Применение фильтров
        function applyFilters() {
            const searchText = document.getElementById('search-input').value.toLowerCase();
            
            // Получаем выбранные типы элементов
            const selectedTypes = Array.from(document.querySelectorAll('#type-filters input:checked'))
                .map(checkbox => checkbox.id.replace('type-', ''));
            
            // Получаем выбранные статусы
            const selectedStatuses = Array.from(document.querySelectorAll('#status-filters input:checked'))
                .map(checkbox => checkbox.id.replace('status-', ''));
            
            // Фильтруем узлы
            const filteredNodeIds = graphData.nodes
                .filter(node => {
                    // Фильтрация по типу
                    if (!selectedTypes.includes(node.type)) {
                        return false;
                    }
                    
                    // Фильтрация по статусу
                    if (selectedStatuses.includes('other')) {
                        if (!['backlog', 'todo', 'in_progress', 'done'].includes(node.status) && 
                            !selectedStatuses.includes(node.status)) {
                            return true;
                        }
                    }
                    
                    if (!selectedStatuses.includes(node.status) && 
                        !selectedStatuses.includes('other')) {
                        return false;
                    }
                    
                    // Фильтрация по поисковому запросу
                    if (searchText && !node.label.toLowerCase().includes(searchText) && 
                        !node.id.toLowerCase().includes(searchText)) {
                        return false;
                    }
                    
                    return true;
                })
                .map(node => node.id);
            
            // Обновляем видимость узлов
            nodes.forEach(node => {
                const isVisible = filteredNodeIds.includes(node.id);
                nodes.update({ id: node.id, hidden: !isVisible });
            });
            
            // Обновляем видимость рёбер
            edges.forEach(edge => {
                const isSourceVisible = filteredNodeIds.includes(edge.from);
                const isTargetVisible = filteredNodeIds.includes(edge.to);
                edges.update({ id: edge.id, hidden: !(isSourceVisible && isTargetVisible) });
            });
        }
        
        // Экспорт графа
        document.getElementById('export-button').addEventListener('click', function() {
            const exportData = {
                nodes: nodes.get(),
                edges: edges.get()
            };
            
            const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = 'work-items-relations.json';
            a.click();
            
            URL.revokeObjectURL(url);
        });
    </script>
</body>
</html>
"""


def get_registry_data():
    """
    Получает данные из реестра задач.
    
    Returns:
        Кортеж (список элементов, словарь со связями)
    """
    try:
        from advising_platform.src.core.registry.task_registry import get_registry, WorkItemRelationType
        
        # Получаем реестр
        registry = get_registry()
        
        # Получаем все элементы
        items = list(registry.items.values())
        
        # Собираем все связи
        relations = {}
        for item in items:
            # Получаем исходящие связи для каждого элемента
            outgoing_relations = registry.get_outgoing_relations(item.id)
            if outgoing_relations:
                relations[item.id] = outgoing_relations
                
            # Также получаем входящие связи для полноты картины
            incoming_relations = registry.get_incoming_relations(item.id)
            if incoming_relations:
                for relation in incoming_relations:
                    if relation.source_id not in relations:
                        relations[relation.source_id] = []
                    # Проверяем, нет ли дубликатов
                    existing_targets = [r.target_id for r in relations[relation.source_id]]
                    if relation.target_id not in existing_targets:
                        relations[relation.source_id].append(relation)
        
        logger.info(f"Получено {len(items)} элементов и {sum(len(rels) for rels in relations.values())} связей из реестра")
        return items, relations
    except Exception as e:
        logger.error(f"Ошибка при получении данных из реестра: {e}")
        return [], {}


def prepare_node_data(item):
    """
    Подготавливает данные узла для визуализации.
    
    Args:
        item: Рабочий элемент
        
    Returns:
        Словарь с данными узла
    """
    # Определяем цвет в зависимости от типа элемента
    color_map = {
        "task": "#3498db",
        "incident": "#e74c3c",
        "hypothesis": "#9b59b6",
        "standard": "#2ecc71"
    }
    
    color = color_map.get(item.type.value, "#7f8c8d")
    
    # Определяем форму в зависимости от типа элемента
    shape_map = {
        "task": "box",
        "incident": "diamond",
        "hypothesis": "ellipse",
        "standard": "database"
    }
    
    shape = shape_map.get(item.type.value, "box")
    
    # Создаем метку с префиксом в зависимости от типа
    prefix_map = {
        "task": "Задача",
        "incident": "Инцидент",
        "hypothesis": "Гипотеза",
        "standard": "Стандарт"
    }
    
    prefix = prefix_map.get(item.type.value, "")
    
    # Создаем данные узла
    node_data = {
        "id": item.id,
        "label": f"{item.title}",
        "title": f"{prefix}: {item.title} ({item.id})\nСтатус: {item.status.value}",
        "color": {
            "background": color,
            "border": "#2c3e50",
            "highlight": {
                "background": color,
                "border": "#34495e"
            }
        },
        "shape": shape,
        "type": item.type.value,
        "status": item.status.value,
        "author": item.author,
        "assignee": item.assignee,
        "filePath": item.file_path,
        "description": item.description
    }
    
    return node_data


def prepare_edge_data(source_id, relation):
    """
    Подготавливает данные ребра для визуализации.
    
    Args:
        source_id: Идентификатор исходного элемента
        relation: Связь
        
    Returns:
        Словарь с данными ребра
    """
    # Определяем цвет в зависимости от типа связи
    color_map = {
        "relates_to": "#3498db",
        "blocks": "#e74c3c",
        "blocked_by": "#e74c3c",
        "depends_on": "#f39c12",
        "parent_of": "#2ecc71",
        "child_of": "#2ecc71",
        "derived_from": "#9b59b6",
        "supersedes": "#8e44ad",
        "superseded_by": "#8e44ad"
    }
    
    color = color_map.get(relation.relation_type.value, "#7f8c8d")
    
    # Создаем данные ребра
    edge_data = {
        "id": f"{source_id}_{relation.target_id}_{relation.relation_type.value}",
        "from": source_id,
        "to": relation.target_id,
        "label": relation.relation_type.value,
        "color": color,
        "arrows": "to"
    }
    
    return edge_data


def generate_visualization_data(items):
    """
    Генерирует данные для визуализации.
    
    Args:
        items: Список рабочих элементов
        
    Returns:
        Словарь с данными узлов и рёбер
    """
    nodes = []
    edges = []
    processed_relations = set()  # Для отслеживания уже обработанных связей
    item_ids = set()  # Для отслеживания уже добавленных узлов
    
    # Добавляем узлы
    for item in items:
        if item.id not in item_ids:
            node = prepare_node_data(item)
            nodes.append(node)
            item_ids.add(item.id)
        
        # Добавляем рёбра
        for relation in item.relations:
            relation_key = f"{item.id}_{relation.target_id}_{relation.relation_type.value}"
            inverse_key = f"{relation.target_id}_{item.id}_{relation.relation_type.value}"
            
            # Проверяем, не обрабатывали ли мы уже эту связь или ее обратную
            if relation_key not in processed_relations and inverse_key not in processed_relations:
                edge = prepare_edge_data(item.id, relation)
                edges.append(edge)
                processed_relations.add(relation_key)
                
                # Проверяем, существует ли целевой элемент
                target_exists = False
                for target_item in items:
                    if target_item.id == relation.target_id:
                        target_exists = True
                        break
                
                # Если целевого элемента нет в нашем списке, создаем заглушку
                if not target_exists:
                    logger.warning(f"Целевой элемент {relation.target_id} не найден для связи {relation_key}")
                    # Создаем заглушку для отображения
                    missing_node = {
                        "id": relation.target_id,
                        "label": f"Неизвестный элемент {relation.target_id}",
                        "title": f"Неизвестный элемент: {relation.target_id}\nСтатус: неизвестно",
                        "color": {
                            "background": "#cccccc",
                            "border": "#999999",
                        },
                        "shape": "question",
                        "type": "unknown",
                        "status": "unknown"
                    }
                    nodes.append(missing_node)
                    item_ids.add(relation.target_id)
    
    logger.info(f"Подготовлено {len(nodes)} узлов и {len(edges)} связей для визуализации")
    return {
        "nodes": nodes,
        "edges": edges
    }


def create_html_report(data, output_file):
    """
    Создает HTML-отчет с визуализацией.
    
    Args:
        data: Данные для визуализации
        output_file: Путь к выходному файлу
        
    Returns:
        True, если отчет успешно создан, иначе False
    """
    try:
        # Преобразуем данные в JSON
        json_data = json.dumps(data)
        
        # Подставляем данные в шаблон
        html = HTML_TEMPLATE.replace('$GRAPH_DATA', json_data)
        
        # Создаем директорию для файла, если она не существует
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        
        # Сохраняем HTML в файл
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)
        
        logger.info(f"Отчет успешно создан: {output_file}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при создании отчета: {e}")
        return False


def main():
    """Основная функция."""
    import argparse
    
    # Настройка парсера аргументов
    parser = argparse.ArgumentParser(description="Визуализатор связей между рабочими элементами")
    parser.add_argument("--output", default="relation_visualization.html", help="Путь к выходному HTML-файлу")
    
    # Разбор аргументов
    args = parser.parse_args()
    
    # Получаем данные из реестра
    items, relations = get_registry_data()
    
    # Проверяем, получены ли данные
    if not items:
        print("Не удалось получить данные из реестра")
        return 1
    
    print(f"Получено {len(items)} элементов из реестра")
    
    # Подготавливаем данные для визуализации
    data = generate_visualization_data(items)
    
    # Создаем HTML-отчет
    if create_html_report(data, args.output):
        print(f"Визуализация успешно создана: {args.output}")
        return 0
    else:
        print("Не удалось создать визуализацию")
        return 1


if __name__ == "__main__":
    sys.exit(main())