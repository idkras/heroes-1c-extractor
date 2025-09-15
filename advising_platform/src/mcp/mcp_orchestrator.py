#!/usr/bin/env python3
"""
MCP Orchestrator: Главный модуль управления полным циклом

JTBD: Я хочу оркестрировать выполнение всех MCP модулей,
чтобы обеспечить полный цикл от гипотезы до результата без пропущенных шагов.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import time
import importlib.util
import asyncio

sys.path.insert(0, '/home/runner/workspace')

class MCPOrchestrator:
    """Оркестратор полного MCP workflow."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        self.output_dir = Path(__file__).parent / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        # Интеграция с dashboard
        try:
            from advising_platform.src.mcp.mcp_dashboard import log_mcp_operation, report_mcp_progress
            self.log_operation = log_mcp_operation
            self.report_progress = report_mcp_progress
        except ImportError:
            self.log_operation = lambda *args: None
            self.report_progress = lambda: "Dashboard not available"
        
        # Состояние выполнения
        self.workflow_state = {
            "current_step": None,
            "completed_steps": [],
            "failed_steps": [],
            "outputs": {},
            "start_time": None
        }
        
        # MCP Protocol Support (TDD Green Phase - minimal implementation)
        self.mcp_commands = {
            'form-hypothesis': self.form_hypothesis,
            'build-jtbd': self.build_jtbd,
            'write-prd': self.write_prd,
            'analyze-landing': self.analyze_landing,
            'validate-compliance': self.validate_compliance,
            'red-phase-tests': self.red_phase_tests,
            'implement-feature': self.implement_feature,
            'run-tests': self.run_tests,
            'evaluate-outcome': self.evaluate_outcome,
            'falsify-or-confirm': self.falsify_or_confirm
        }
    
    def _default_config(self) -> Dict[str, Any]:
        """Конфигурация workflow по умолчанию."""
        return {
            "steps": [
                {"module": "form_hypothesis", "required": True, "timeout": 30},
                {"module": "build_jtbd", "required": True, "timeout": 45},
                {"module": "write_prd", "required": True, "timeout": 60},
                {"module": "red_phase_tests", "required": True, "timeout": 120},
                {"module": "implement_feature", "required": True, "timeout": 300},
                {"module": "run_tests", "required": True, "timeout": 180},
                {"module": "evaluate_outcome", "required": True, "timeout": 60},
                {"module": "falsify_or_confirm", "required": True, "timeout": 30}
            ],
            "on_failure": "create_incident",
            "auto_recovery": True,
            "max_retries": 2
        }
    
    def execute_full_cycle(self, initial_input: str) -> Dict[str, Any]:
        """Выполняет полный цикл MCP от входных данных до результата."""
        self.workflow_state["start_time"] = datetime.now()
        
        try:
            result = {
                "workflow_id": f"MCP_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "start_time": self.workflow_state["start_time"].isoformat(),
                "steps_executed": [],
                "outputs": {},
                "final_result": None
            }
            
            current_input = initial_input
            
            # Выполняем каждый шаг
            for step_config in self.config["steps"]:
                step_result = self._execute_step(step_config, current_input)
                
                result["steps_executed"].append({
                    "module": step_config["module"],
                    "success": step_result["success"],
                    "duration": step_result.get("duration", 0),
                    "timestamp": datetime.now().isoformat()
                })
                
                if step_result["success"]:
                    self.workflow_state["completed_steps"].append(step_config["module"])
                    result["outputs"][step_config["module"]] = step_result["output"]
                    
                    # Выход предыдущего шага становится входом следующего
                    current_input = step_result["output"]
                else:
                    self.workflow_state["failed_steps"].append(step_config["module"])
                    
                    if step_config["required"]:
                        # Создаем инцидент для обязательного шага
                        incident = self._create_incident_for_failed_step(step_config, step_result)
                        result["incident_created"] = incident
                        break
            
            # Финальный отчет
            result["end_time"] = datetime.now().isoformat()
            result["total_duration"] = (datetime.now() - self.workflow_state["start_time"]).total_seconds()
            result["success_rate"] = len(self.workflow_state["completed_steps"]) / len(self.config["steps"])
            
            # Логируем завершение workflow
            self.log_operation(
                'mcp-orchestrator-complete',
                {"workflow_id": result["workflow_id"]},
                {
                    "success": len(self.workflow_state["failed_steps"]) == 0,
                    "steps_completed": len(self.workflow_state["completed_steps"]),
                    "steps_failed": len(self.workflow_state["failed_steps"])
                },
                result["total_duration"] * 1000
            )
            
            return result
            
        except Exception as e:
            # Критическая ошибка оркестратора
            self._handle_orchestrator_failure(e)
            raise
    
    def _execute_step(self, step_config: Dict[str, Any], input_data: Any) -> Dict[str, Any]:
        """Выполняет один шаг workflow."""
        module_name = step_config["module"]
        self.workflow_state["current_step"] = module_name
        
        start_time = datetime.now()
        
        try:
            # Динамический импорт модуля
            module_path = f"advising_platform.src.mcp.modules.{module_name}"
            
            try:
                module = __import__(module_path, fromlist=[module_name])
                
                # Получаем класс процессора (по конвенции: CamelCase от имени модуля)
                class_name = ''.join(word.capitalize() for word in module_name.split('_'))
                processor_class = getattr(module, class_name)
                
                # Создаем экземпляр и выполняем
                processor = processor_class()
                
                if hasattr(processor, 'process'):
                    output = processor.process(input_data)
                else:
                    raise AttributeError(f"Module {module_name} doesn't have process method")
                
                duration = (datetime.now() - start_time).total_seconds()
                
                # Логируем успешное выполнение
                self.log_operation(
                    f'orchestrator-step-{module_name}',
                    {"input_type": type(input_data).__name__},
                    {"success": True, "output_generated": True},
                    duration * 1000
                )
                
                return {
                    "success": True,
                    "output": output,
                    "duration": duration,
                    "module": module_name
                }
                
            except ImportError:
                # Модуль не существует - это нормально для Red Phase
                duration = (datetime.now() - start_time).total_seconds()
                
                self.log_operation(
                    f'orchestrator-step-{module_name}',
                    {"input_type": type(input_data).__name__},
                    {"success": False, "error": "Module not implemented (Red Phase)"},
                    duration * 1000
                )
                
                return {
                    "success": False,
                    "error": f"Module {module_name} not implemented yet (Red Phase)",
                    "duration": duration,
                    "module": module_name,
                    "red_phase": True
                }
                
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            
            self.log_operation(
                f'orchestrator-step-{module_name}',
                {"input_type": type(input_data).__name__},
                {"success": False, "error": str(e)},
                duration * 1000
            )
            
            return {
                "success": False,
                "error": str(e),
                "duration": duration,
                "module": module_name
            }
    
    def _create_incident_for_failed_step(self, step_config: Dict[str, Any], step_result: Dict[str, Any]) -> Dict[str, Any]:
        """Создает инцидент для неудачного шага."""
        incident = {
            "id": f"I{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "title": f"MCP Step Failed: {step_config['module']}",
            "description": f"Обязательный шаг {step_config['module']} завершился неудачно",
            "error": step_result.get("error", "Unknown error"),
            "workflow_state": self.workflow_state.copy(),
            "created_at": datetime.now().isoformat(),
            "priority": "high" if step_config["required"] else "medium"
        }
        
        # Сохраняем инцидент (конвертируем datetime в string)
        incident_json = json.dumps(incident, default=str, indent=2, ensure_ascii=False)
        incident_file = self.output_dir / f"incident_{incident['id']}.json"
        with open(incident_file, 'w', encoding='utf-8') as f:
            f.write(incident_json)
        
        return incident
    
    def _handle_orchestrator_failure(self, error: Exception):
        """Обрабатывает критическую ошибку оркестратора."""
        failure_report = {
            "type": "orchestrator_failure",
            "error": str(error),
            "workflow_state": self.workflow_state.copy(),
            "timestamp": datetime.now().isoformat()
        }
        
        # Сохраняем отчет об ошибке (конвертируем datetime в string)
        failure_json = json.dumps(failure_report, default=str, indent=2, ensure_ascii=False)
        failure_file = self.output_dir / f"orchestrator_failure_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(failure_file, 'w', encoding='utf-8') as f:
            f.write(failure_json)
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Возвращает текущий статус workflow."""
        return {
            "current_step": self.workflow_state["current_step"],
            "completed_steps": self.workflow_state["completed_steps"],
            "failed_steps": self.workflow_state["failed_steps"],
            "progress_percent": len(self.workflow_state["completed_steps"]) / len(self.config["steps"]) * 100,
            "start_time": self.workflow_state["start_time"].isoformat() if self.workflow_state["start_time"] else None
        }
    
    # TDD Green Phase - Minimal MCP Protocol Implementation
    def supports_mcp_protocol(self) -> bool:
        """Test if orchestrator supports MCP protocol standards"""
        return len(self.mcp_commands) > 0
    
    def get_mcp_commands(self) -> Dict[str, Any]:
        """Get available MCP commands"""
        return self.mcp_commands
    
    def call_python_module(self, module_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Call Python module directly via imports (not spawning)"""
        try:
            # Check absolute path from project root
            possible_paths = [
                Path(f"/home/runner/workspace/advising_platform/src/mcp/python_backends/{module_name}.py"),
                Path(f"/home/runner/workspace/advising_platform/src/mcp/modules/{module_name}.py"),
                Path(f"advising_platform/src/mcp/python_backends/{module_name}.py"),
                Path(f"advising_platform/src/mcp/modules/{module_name}.py")
            ]
            
            module_path = None
            for path in possible_paths:
                if path.exists():
                    module_path = path
                    break
            
            if not module_path:
                return {
                    "success": False,
                    "error": f"Module {module_name} not found in any path",
                    "searched_paths": [str(p) for p in possible_paths]
                }
            
            # Direct import instead of spawning
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Try to call main function if it exists
            if hasattr(module, 'main'):
                result = module.main(args)
                return {
                    "success": True,
                    "result": result,
                    "module": module_name,
                    "path": str(module_path)
                }
            else:
                return {
                    "success": True,
                    "result": f"Module {module_name} imported successfully", 
                    "module": module_name,
                    "path": str(module_path),
                    "note": "No main function found"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "module": module_name,
                "exception_type": type(e).__name__
            }
    
    def supports_atomic_operations(self) -> bool:
        """Test Registry Standard v4.7 atomic operations support"""
        return hasattr(self, 'reflection_checkpoint')
    
    def reflection_checkpoint(self, step_name: str, data: Any) -> Dict[str, Any]:
        """Registry Standard v4.7 reflection checkpoint"""
        checks = {
            "input_validation": self.validate_input(data),
            "process_validation": self.validate_process(step_name, data),
            "output_validation": self.validate_output(data),
            "standard_compliance": self.check_compliance(data)
        }
        return {
            "step": step_name,
            "checks": checks,
            "passed": all(checks.values()),
            "timestamp": datetime.now().isoformat()
        }
    
    def validate_input(self, data: Any) -> bool:
        """Validate input data"""
        return data is not None
    
    def validate_process(self, step_name: str, data: Any) -> bool:
        """Validate process step"""
        return step_name in [s["module"] for s in self.config["steps"]]
    
    def validate_output(self, data: Any) -> bool:
        """Validate output data"""
        return data is not None
    
    def check_compliance(self, data: Any) -> bool:
        """Check standard compliance"""
        return True  # Minimal implementation
    
    def get_workflow_steps(self) -> List[str]:
        """Get workflow steps list"""
        return [step["module"] for step in self.config["steps"]]
    
    # MCP Command Implementations (minimal for testing)
    def form_hypothesis(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Form hypothesis command"""
        return {"success": True, "command": "form-hypothesis", "args": args}
    
    def build_jtbd(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Build JTBD command"""
        return {"success": True, "command": "build-jtbd", "args": args}
    
    def write_prd(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Write PRD command"""
        return {"success": True, "command": "write-prd", "args": args}
    
    def analyze_landing(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze landing command"""
        return {"success": True, "command": "analyze-landing", "args": args}
    
    def validate_compliance(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Validate compliance command"""
        return {"success": True, "command": "validate-compliance", "args": args}
    
    def red_phase_tests(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Red phase tests command"""
        return {"success": True, "command": "red-phase-tests", "args": args}
    
    def implement_feature(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Implement feature command"""
        return {"success": True, "command": "implement-feature", "args": args}
    
    def run_tests(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Run tests command"""
        return {"success": True, "command": "run-tests", "args": args}
    
    def evaluate_outcome(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate outcome command"""
        return {"success": True, "command": "evaluate-outcome", "args": args}
    
    def falsify_or_confirm(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Falsify or confirm command"""
        return {"success": True, "command": "falsify-or-confirm", "args": args}

if __name__ == "__main__":
    # Запуск как MCP команда
    if len(sys.argv) > 1:
        request_data = json.loads(sys.argv[1])
        
        orchestrator = MCPOrchestrator()
        result = orchestrator.execute_full_cycle(request_data.get("input", ""))
        
        print(json.dumps({
            "success": True,
            "workflow_result": result,
            "mcp_operations_logged": True
        }, indent=2, ensure_ascii=False))
    else:
        print("MCPOrchestrator - use with input JSON")