"""
MCP Module: Chat Integration
Интеграция MCP команд с пользовательским интерфейсом чата
"""

import json
import time
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


def report_progress(summary: str) -> Dict[str, Any]:
    """
    Выводит результаты MCP команд в чат пользователя
    """
    start_time = time.time()
    
    result = {
        "command": "report-progress",
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
        "chat_output": True,
        "success": True
    }
    
    # Форматируем вывод для чата
    chat_message = f"""
🤖 MCP Command Execution Report

{summary}

⏱️ Timestamp: {datetime.now().strftime('%H:%M:%S')}
✅ Command completed successfully
"""
    
    # Выводим в консоль (будет видно в чате)
    print(chat_message)
    
    result["execution_time_ms"] = round((time.time() - start_time) * 1000, 2)
    return result


def mcp_execute_with_chat_output(command_name: str, command_function, *args, **kwargs) -> Dict[str, Any]:
    """
    Выполняет MCP команду с выводом результатов в чат
    """
    print(f"🔄 Executing MCP command: {command_name}")
    
    try:
        # Выполняем команду
        result = command_function(*args, **kwargs)
        
        # Форматируем результат для чата
        summary = f"""
✅ {command_name} completed successfully

📊 Results:
{json.dumps(result, indent=2, ensure_ascii=False)}
"""
        
        # Выводим через report_progress
        report_progress(summary)
        
        return result
        
    except Exception as e:
        error_summary = f"""
❌ {command_name} failed

🚨 Error: {str(e)}
"""
        report_progress(error_summary)
        raise


def mcp_falsify_hypothesis_with_chat(hypothesis_file: str, test_results_file: str) -> Dict[str, Any]:
    """
    Фальсификация гипотезы с выводом в чат
    """
    from falsify_or_confirm import mcp_falsify_or_confirm
    
    print("🧪 Starting hypothesis falsification...")
    
    try:
        result = mcp_falsify_or_confirm(hypothesis_file, test_results_file)
        
        decision = result.get('final_decision', {}).get('decision', 'UNKNOWN')
        confidence = result.get('final_decision', {}).get('confidence', 0) * 100
        
        summary = f"""
🧪 Hypothesis Falsification Complete

🎯 Decision: {decision}
📊 Confidence: {confidence:.0f}%
📁 Hypothesis: {hypothesis_file}
📁 Test Results: {test_results_file}

{'✅ Hypothesis CONFIRMED' if decision == 'CONFIRMED' else '❌ Hypothesis FALSIFIED'}
"""
        
        report_progress(summary)
        return result
        
    except Exception as e:
        error_summary = f"""
❌ Hypothesis falsification failed

🚨 Error: {str(e)}
📁 Files: {hypothesis_file}, {test_results_file}
"""
        report_progress(error_summary)
        raise


def mcp_task_management_with_chat(action: str, task_id: str = None) -> Dict[str, Any]:
    """
    Управление задачами с выводом в чат
    """
    print(f"📋 Task management: {action}")
    
    try:
        if action == "next":
            from next_task import mcp_next_task
            result = mcp_next_task()
            
            next_task = result.get('next_task', {})
            summary = f"""
📋 Next Task Retrieved

🎯 Task: {next_task.get('title', 'No tasks available')}
🚨 Priority: {next_task.get('priority', 'N/A')}
📝 Status: {next_task.get('status', 'N/A')}
"""
            
        elif action == "complete" and task_id:
            from complete_task import mcp_complete_task
            result = mcp_complete_task(task_id)
            
            summary = f"""
✅ Task Completed

📋 Task ID: {task_id}
✅ Status: {"Completed successfully" if result.get('task_completed') else "Task not found"}
"""
            
        elif action == "status":
            from task_status import mcp_task_status
            result = mcp_task_status()
            
            task_summary = result.get('task_summary', {})
            summary = f"""
📊 Task Status Overview

📋 Total Tasks: {task_summary.get('total_tasks', 0)}
✅ Completed: {task_summary.get('completed', 0)}
🔄 In Progress: {task_summary.get('in_progress', 0)}
⏳ Pending: {task_summary.get('pending', 0)}
📈 Completion Rate: {task_summary.get('completion_rate', 0)}%
"""
            
        else:
            raise ValueError(f"Unknown action: {action}")
        
        report_progress(summary)
        return result
        
    except Exception as e:
        error_summary = f"""
❌ Task management failed

🚨 Error: {str(e)}
🔧 Action: {action}
📋 Task ID: {task_id or 'N/A'}
"""
        report_progress(error_summary)
        raise