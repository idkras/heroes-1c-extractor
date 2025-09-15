#!/usr/bin/env python3
"""
Проверка реальности vs пиздежа в системе

JTBD: Я хочу проверить что реально работает на диске,
чтобы выявить фальшивые реализации и исправить их.
"""

import requests
import subprocess
import json
from pathlib import Path
import sys

def check_real_vs_fake():
    """Проверяет что реально работает vs что симулируется."""
    project_root = Path(__file__).parent.parent.parent
    
    checks = {
        "web_server_localhost": False,
        "mcp_server_running": False,
        "mcp_backends_functional": False,
        "cache_system_working": False,
        "dashboard_real": False
    }
    
    # 1. Проверка веб-сервера
    try:
        response = requests.get("http://localhost:5000", timeout=2)
        checks["web_server_localhost"] = response.status_code == 200
    except:
        pass
    
    # 2. Проверка MCP backends
    backend_dir = project_root / "src" / "mcp" / "python_backends"
    if backend_dir.exists():
        try:
            result = subprocess.run([
                "python", str(backend_dir / "standards_resolver.py"), 
                '{"address": "test", "format": "summary"}'
            ], capture_output=True, text=True, timeout=5, cwd=project_root,
            env={"PYTHONPATH": "/home/runner/workspace"})
            
            if result.returncode == 0:
                response = json.loads(result.stdout)
                checks["mcp_backends_functional"] = "success" in response
        except:
            pass
    
    # 3. Проверка кеша
    cache_files = [".cache_state.json", ".cache_detailed_state.json"]
    checks["cache_system_working"] = any((project_root / f).exists() for f in cache_files)
    
    # 4. Проверка dashboard
    dashboard_file = project_root / "src" / "mcp" / "mcp_dashboard.py"
    if dashboard_file.exists():
        try:
            result = subprocess.run([
                "python", "-c", 
                "from advising_platform.src.mcp.mcp_dashboard import report_mcp_progress; print('OK')"
            ], capture_output=True, text=True, timeout=3, cwd=project_root,
            env={"PYTHONPATH": "/home/runner/workspace"})
            checks["dashboard_real"] = result.returncode == 0
        except:
            pass
    
    return checks

def fix_port_issue():
    """Исправляет проблему с портами для Replit."""
    # В Replit нужно использовать специальные порты или proxy
    print("🔧 Исправление проблемы с портами...")
    
    # Проверяем доступные порты
    env_check = subprocess.run([
        "python", "-c", 
        "import os; print('REPL_ID:', os.get('REPL_ID', 'not_found')); print('PORT:', os.get('PORT', 'not_found'))"
    ], capture_output=True, text=True)
    
    return env_check.stdout

if __name__ == "__main__":
    print("🔍 ПРОВЕРКА РЕАЛЬНОСТИ СИСТЕМЫ")
    print("=" * 40)
    
    reality = check_real_vs_fake()
    
    for check, status in reality.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {check}: {'РАБОТАЕТ' if status else 'ПИЗДЕЖЬ'}")
    
    working = sum(reality.values())
    total = len(reality)
    
    print(f"\n📊 Реальность: {working}/{total} компонентов")
    
    if working < total:
        print("🚨 ОБНАРУЖЕН ПИЗДЕЖЬ!")
        print("\n🔧 Исправления:")
        print(fix_port_issue())
    
    # Проверяем MCP операции
    print("\n🔌 MCP ОПЕРАЦИИ:")
    try:
        from advising_platform.src.mcp.mcp_dashboard import mcp_dashboard
        dashboard_data = mcp_dashboard.get_live_dashboard()
        stats = dashboard_data.get("stats", {})
        print(f"   Команд выполнено: {stats.get('total_commands', 0)}")
        print(f"   Последнее обновление: {dashboard_data.get('last_updated', 'never')}")
    except Exception as e:
        print(f"   ❌ Ошибка MCP: {e}")