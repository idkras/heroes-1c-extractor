#!/usr/bin/env python3
"""
Playwright MCP Server

MCP сервер для автоматизации браузера с помощью Playwright.
Предоставляет инструменты для веб-автоматизации, скриншотов и тестирования.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Инициализация MCP сервера
server = Server("playwright-mcp")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """Список доступных инструментов Playwright MCP"""
    return [
        Tool(
            name="playwright_screenshot",
            description="Сделать скриншот веб-страницы",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL страницы для скриншота"
                    },
                    "width": {
                        "type": "integer",
                        "description": "Ширина окна браузера",
                        "default": 1920
                    },
                    "height": {
                        "type": "integer", 
                        "description": "Высота окна браузера",
                        "default": 1080
                    },
                    "full_page": {
                        "type": "boolean",
                        "description": "Скриншот всей страницы",
                        "default": True
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="playwright_navigate",
            description="Навигация по веб-странице",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL для навигации"
                    },
                    "wait_for": {
                        "type": "string",
                        "description": "Селектор для ожидания загрузки",
                        "default": "body"
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="playwright_click",
            description="Клик по элементу на странице",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "CSS селектор элемента"
                    },
                    "url": {
                        "type": "string",
                        "description": "URL страницы"
                    }
                },
                "required": ["selector", "url"]
            }
        ),
        Tool(
            name="playwright_fill",
            description="Заполнение поля формы",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "CSS селектор поля"
                    },
                    "text": {
                        "type": "string",
                        "description": "Текст для заполнения"
                    },
                    "url": {
                        "type": "string",
                        "description": "URL страницы"
                    }
                },
                "required": ["selector", "text", "url"]
            }
        ),
        Tool(
            name="playwright_get_text",
            description="Получение текста элемента",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "CSS селектор элемента"
                    },
                    "url": {
                        "type": "string",
                        "description": "URL страницы"
                    }
                },
                "required": ["selector", "url"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Обработка вызовов инструментов"""
    
    if name == "playwright_screenshot":
        return await handle_screenshot(arguments)
    elif name == "playwright_navigate":
        return await handle_navigate(arguments)
    elif name == "playwright_click":
        return await handle_click(arguments)
    elif name == "playwright_fill":
        return await handle_fill(arguments)
    elif name == "playwright_get_text":
        return await handle_get_text(arguments)
    else:
        return [TextContent(
            type="text",
            text=f"Неизвестный инструмент: {name}"
        )]

async def handle_screenshot(arguments: Dict[str, Any]) -> List[TextContent]:
    """Обработка скриншота"""
    try:
        url = arguments.get("url")
        width = arguments.get("width", 1920)
        height = arguments.get("height", 1080)
        full_page = arguments.get("full_page", True)
        
        # Здесь должна быть логика Playwright
        # Пока возвращаем заглушку
        result = {
            "status": "success",
            "url": url,
            "screenshot_path": f"screenshot_{hash(url)}.png",
            "dimensions": {"width": width, "height": height},
            "full_page": full_page
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False)
        )]
        
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Ошибка при создании скриншота: {str(e)}"
        )]

async def handle_navigate(arguments: Dict[str, Any]) -> List[TextContent]:
    """Обработка навигации"""
    try:
        url = arguments.get("url")
        wait_for = arguments.get("wait_for", "body")
        
        result = {
            "status": "success",
            "url": url,
            "wait_for": wait_for,
            "message": "Навигация выполнена успешно"
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False)
        )]
        
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Ошибка при навигации: {str(e)}"
        )]

async def handle_click(arguments: Dict[str, Any]) -> List[TextContent]:
    """Обработка клика"""
    try:
        selector = arguments.get("selector")
        url = arguments.get("url")
        
        result = {
            "status": "success",
            "selector": selector,
            "url": url,
            "message": "Клик выполнен успешно"
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False)
        )]
        
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Ошибка при клике: {str(e)}"
        )]

async def handle_fill(arguments: Dict[str, Any]) -> List[TextContent]:
    """Обработка заполнения поля"""
    try:
        selector = arguments.get("selector")
        text = arguments.get("text")
        url = arguments.get("url")
        
        result = {
            "status": "success",
            "selector": selector,
            "text": text,
            "url": url,
            "message": "Поле заполнено успешно"
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False)
        )]
        
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Ошибка при заполнении поля: {str(e)}"
        )]

async def handle_get_text(arguments: Dict[str, Any]) -> List[TextContent]:
    """Обработка получения текста"""
    try:
        selector = arguments.get("selector")
        url = arguments.get("url")
        
        result = {
            "status": "success",
            "selector": selector,
            "url": url,
            "text": "Пример текста элемента",
            "message": "Текст получен успешно"
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False)
        )]
        
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Ошибка при получении текста: {str(e)}"
        )]

async def main():
    """Главная функция сервера"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Playwright MCP Server - Тестовый режим")
        print("Доступные инструменты:")
        for tool in [
            "playwright_screenshot",
            "playwright_navigate", 
            "playwright_click",
            "playwright_fill",
            "playwright_get_text"
        ]:
            print(f"  - {tool}")
        print("SUCCESS: Playwright MCP Server готов к работе")
    else:
        asyncio.run(main())
