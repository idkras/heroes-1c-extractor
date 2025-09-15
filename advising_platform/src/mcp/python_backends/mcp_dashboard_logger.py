#!/usr/bin/env python3
"""
MCP Dashboard Logger

JTBD: Я (логгер) хочу записывать MCP операции в dashboard,
чтобы обеспечить визуализацию команд в реальном времени.

Автор: AI Assistant
Дата: 26 May 2025
"""

import sys
import json
from pathlib import Path

# Добавляем путь к модулям advising_platform
current_dir = Path(__file__).parent.resolve()
advising_platform_dir = current_dir.parent.parent
sys.path.insert(0, str(advising_platform_dir))

try:
    from advising_platform.src.mcp.mcp_dashboard import log_mcp_operation
# Direct import
    project_root = current_dir.parent.parent.parent
    sys.path.insert(0, str(project_root))
    from advising_platform.src.mcp.mcp_dashboard import log_mcp_operation

def main():
    """Логирует MCP операцию в dashboard."""
    try:
        if len(sys.argv) != 2:
            raise ValueError("Usage: python mcp_dashboard_logger.py <json_args>")
        
        args = json.loads(sys.argv[1])
        
        log_mcp_operation(
            tool_name=args.get("tool_name"),
            parameters=args.get("parameters", {}),
            result=args.get("result", {}),
            duration_ms=args.get("duration_ms", 0),
            status=args.get("status", "success"),
            error_message=args.get("error_message", "")
        )
        
        # Возвращаем успешный результат
        result = {"success": True, "logged": True}
        print(json.dumps(result, ensure_ascii=False))
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": f"Logging failed: {str(e)}"
        }
        print(json.dumps(error_result, ensure_ascii=False))
        sys.exit(1)

if __name__ == "__main__":
    main()