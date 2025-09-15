"""
MCP Registry Scanner - сканирует все реальные MCP команды из сервера.

Решает проблему: README.md показывает только 10 базовых команд вместо всех доступных.
"""

import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional

class MCPRegistryScanner:
    """Сканирует все доступные MCP команды из реального сервера"""
    
    def __init__(self):
        """Инициализация scanner"""
        self.mcp_server_path = Path("src/mcp/standards_mcp_server.js")
        self.modules_path = Path("src/mcp/modules")
        self.backends_path = Path("src/mcp/python_backends")
        
    def scan_all_mcp_commands(self) -> Dict[str, Any]:
        """
        Сканирует все доступные MCP команды из всех источников.
        """
        start_time = time.time()
        
        result = {
            "operation": "scan_all_mcp_commands",
            "success": False,
            "commands": [],
            "sources": {},
            "total_commands": 0
        }
        
        try:
            # 1. Сканируем JavaScript MCP сервер
            js_commands = self._scan_javascript_server()
            
            # 2. Сканируем Python модули
            python_commands = self._scan_python_modules()
            
            # 3. Сканируем backend интеграции
            backend_commands = self._scan_backend_integrations()
            
            # 4. Объединяем все команды
            all_commands = []
            all_commands.extend(js_commands)
            all_commands.extend(python_commands)
            all_commands.extend(backend_commands)
            
            # 5. Удаляем дубликаты
            unique_commands = self._deduplicate_commands(all_commands)
            
            result.update({
                "success": True,
                "commands": unique_commands,
                "sources": {
                    "javascript_server": len(js_commands),
                    "python_modules": len(python_commands),
                    "backend_integrations": len(backend_commands)
                },
                "total_commands": len(unique_commands)
            })
            
            print(f"✅ Просканировано {len(unique_commands)} уникальных MCP команд")
            
        except Exception as e:
            result["error"] = str(e)
        
        result["duration_ms"] = (time.time() - start_time) * 1000
        return result
    
    def _scan_javascript_server(self) -> List[Dict]:
        """Сканирует команды из JavaScript MCP сервера"""
        commands = []
        
        try:
            if not self.mcp_server_path.exists():
                return commands
            
            with open(self.mcp_server_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Ищем определения команд в JS файле
            # Паттерны: server.setRequestHandler("command-name", ...)
            import re
            
            patterns = [
                r'server\.setRequestHandler\(["\']([^"\']+)["\']',
                r'addTool\(["\']([^"\']+)["\']',
                r'registerCommand\(["\']([^"\']+)["\']'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    commands.append({
                        "name": match,
                        "source": "javascript_server",
                        "category": "🔧 Core MCP Operations",
                        "description": f"MCP command: {match}",
                        "usage_example": f"Execute {match} via MCP server"
                    })
        
        except Exception as e:
            print(f"Warning: Could not scan JavaScript server: {e}")
        
        return commands
    
    def _scan_python_modules(self) -> List[Dict]:
        """Сканирует команды из Python модулей"""
        commands = []
        
        try:
            if not self.modules_path.exists():
                return commands
            
            # Сканируем все .py файлы в modules/
            for py_file in self.modules_path.glob("*.py"):
                if py_file.name.startswith("__"):
                    continue
                    
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Ищем функции, которые могут быть MCP командами
                import re
                
                # Паттерны для MCP команд
                function_pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*->\s*Dict'
                matches = re.findall(function_pattern, content)
                
                for func_name in matches:
                    if not func_name.startswith('_'):  # Исключаем приватные функции
                        command_name = func_name.replace('_', '-')
                        commands.append({
                            "name": command_name,
                            "source": f"python_module:{py_file.name}",
                            "category": self._categorize_by_module(py_file.name),
                            "description": f"Python module function: {func_name}",
                            "usage_example": f"Execute {command_name} from {py_file.name}"
                        })
        
        except Exception as e:
            print(f"Warning: Could not scan Python modules: {e}")
        
        return commands
    
    def _scan_backend_integrations(self) -> List[Dict]:
        """Сканирует команды из backend интеграций"""
        commands = []
        
        try:
            if not self.backends_path.exists():
                return commands
            
            # Известные backend функции, которые являются MCP командами
            backend_commands = [
                {
                    "name": "load-standards-trigger",
                    "source": "standards_integration",
                    "category": "🔗 Standards Integration",
                    "description": "Автоматическая загрузка и индексация стандартов",
                    "usage_example": "trigger_standards_reload()"
                },
                {
                    "name": "validate-standards-compliance", 
                    "source": "standards_integration",
                    "category": "🔗 Standards Integration",
                    "description": "Валидация соответствия контента стандартам",
                    "usage_example": "validate_against_standards(content)"
                },
                {
                    "name": "root-cause-analysis-trigger",
                    "source": "standards_integration", 
                    "category": "🔗 Standards Integration",
                    "description": "Анализ корневых причин с использованием стандартов",
                    "usage_example": "root_cause_analysis(problem_description)"
                },
                {
                    "name": "quality-assurance-trigger",
                    "source": "standards_integration",
                    "category": "🔗 Standards Integration", 
                    "description": "Контроль качества на основе стандартов",
                    "usage_example": "quality_assurance_check()"
                },
                {
                    "name": "update-readme-from-standards",
                    "source": "readme_updater",
                    "category": "📚 Documentation",
                    "description": "Автообновление README.md из анализа стандартов",
                    "usage_example": "update_documentation_from_standards()"
                },
                {
                    "name": "update-registry-standard",
                    "source": "readme_updater", 
                    "category": "📚 Documentation",
                    "description": "Обновление registry.standard.md с полным реестром команд",
                    "usage_example": "update_mcp_commands_registry()"
                },
                {
                    "name": "get-system-status-for-chat",
                    "source": "readme_updater",
                    "category": "🔧 System Management", 
                    "description": "Получение статуса системы для инициализации чата",
                    "usage_example": "check_system_readiness()"
                },
                {
                    "name": "next-task",
                    "source": "task_manager",
                    "category": "📋 Task Management",
                    "description": "Получить следующую незавершенную задачу",
                    "usage_example": "get_next_task_from_list()"
                },
                {
                    "name": "complete-task", 
                    "source": "task_manager",
                    "category": "📋 Task Management",
                    "description": "Отметить задачу как выполненную",
                    "usage_example": "mark_task_completed(task_id)"
                },
                {
                    "name": "report-progress",
                    "source": "task_manager",
                    "category": "📋 Task Management", 
                    "description": "Вывести прогресс и следующие шаги",
                    "usage_example": "generate_progress_report()"
                },
                {
                    "name": "task-status",
                    "source": "task_manager",
                    "category": "📋 Task Management",
                    "description": "Статус всех активных задач", 
                    "usage_example": "get_all_tasks_status()"
                }
            ]
            
            commands.extend(backend_commands)
        
        except Exception as e:
            print(f"Warning: Could not scan backend integrations: {e}")
        
        return commands
    
    def _categorize_by_module(self, module_name: str) -> str:
        """Категоризует команду по имени модуля"""
        if "hypothesis" in module_name:
            return "🔬 Hypothesis Testing"
        elif "jtbd" in module_name:
            return "🎯 JTBD Analysis"
        elif "prd" in module_name:
            return "📋 Product Requirements"
        elif "test" in module_name:
            return "🧪 Testing"
        elif "task" in module_name:
            return "📋 Task Management"
        else:
            return "🔧 General Operations"
    
    def _deduplicate_commands(self, commands: List[Dict]) -> List[Dict]:
        """Удаляет дубликаты команд"""
        seen_names = set()
        unique_commands = []
        
        for command in commands:
            if command["name"] not in seen_names:
                seen_names.add(command["name"])
                unique_commands.append(command)
        
        return unique_commands
    
    def get_comprehensive_command_registry(self) -> Dict[str, Any]:
        """
        Получает полный реестр всех MCP команд для документации.
        """
        scan_result = self.scan_all_mcp_commands()
        
        if not scan_result["success"]:
            return scan_result
        
        # Группируем команды по категориям
        commands_by_category = {}
        for command in scan_result["commands"]:
            category = command["category"]
            if category not in commands_by_category:
                commands_by_category[category] = []
            commands_by_category[category].append(command)
        
        return {
            "operation": "comprehensive_command_registry",
            "success": True,
            "commands_by_category": commands_by_category,
            "total_commands": scan_result["total_commands"],
            "categories": list(commands_by_category.keys()),
            "sources": scan_result["sources"]
        }

def test_registry_scanner():
    """Тест системы сканирования MCP registry"""
    print("🧪 Тест MCP Registry Scanner")
    
    scanner = MCPRegistryScanner()
    
    # Тест полного сканирования
    print("\n🔍 Полное сканирование MCP команд...")
    scan_result = scanner.scan_all_mcp_commands()
    
    if scan_result["success"]:
        print(f"   ✅ Найдено {scan_result['total_commands']} команд")
        print(f"   📊 Источники: {scan_result['sources']}")
        
        # Показываем несколько примеров
        for i, cmd in enumerate(scan_result["commands"][:5]):
            print(f"   • {cmd['name']} ({cmd['category']})")
    
    # Тест comprehensive registry
    print("\n📋 Тест comprehensive registry...")
    registry_result = scanner.get_comprehensive_command_registry()
    
    if registry_result["success"]:
        print(f"   ✅ {registry_result['total_commands']} команд в {len(registry_result['categories'])} категориях")
        for category in registry_result['categories']:
            count = len(registry_result['commands_by_category'][category])
            print(f"   📂 {category}: {count} команд")
    
    print("\n✅ MCP Registry Scanner готов!")

if __name__ == "__main__":
    test_registry_scanner()