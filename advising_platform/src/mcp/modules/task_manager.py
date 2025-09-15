"""
Task Manager MCP Module - управление задачами через MCP команды.

Интегрируется с duck.todo.md для автоматизации workflow управления задачами.
"""

import sys
import json
import time
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Добавляем путь к системе стандартов
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from mcp.python_backends.standards_integration import StandardsIntegration
    STANDARDS_AVAILABLE = True
except ImportError:
    STANDARDS_AVAILABLE = False

class TaskManager:
    """MCP модуль для управления задачами"""
    
    def __init__(self):
        """Инициализация task manager"""
        self.todo_file = Path("[todo · incidents]/duck.todo.md")
        self.standards_integration = None
        
        if STANDARDS_AVAILABLE:
            try:
                self.standards_integration = StandardsIntegration()
            except Exception as e:
                print(f"Standards integration unavailable: {e}")
    
    def get_next_task(self) -> Dict[str, Any]:
        """
        MCP команда: next-task
        Получает следующую незавершенную задачу из списка.
        """
        start_time = time.time()
        
        result = {
            "command": "next-task",
            "success": False,
            "next_task": None,
            "task_number": None,
            "subtasks": [],
            "context": ""
        }
        
        try:
            if not self.todo_file.exists():
                result["error"] = f"Todo file not found: {self.todo_file}"
                return result
            
            with open(self.todo_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Ищем незавершенные задачи
            tasks = self._parse_incomplete_tasks(content)
            
            if tasks:
                next_task = tasks[0]  # Берем первую незавершенную
                result.update({
                    "success": True,
                    "next_task": next_task["title"],
                    "task_number": next_task["number"],
                    "subtasks": next_task["subtasks"],
                    "context": f"Найдено {len(tasks)} незавершенных задач"
                })
            else:
                result.update({
                    "success": True,
                    "context": "Все задачи выполнены! 🎉"
                })
                
        except Exception as e:
            result["error"] = str(e)
        
        result["duration_ms"] = (time.time() - start_time) * 1000
        return result
    
    def complete_task(self, task_number: int, completion_note: str = "") -> Dict[str, Any]:
        """
        MCP команда: complete-task
        Отмечает задачу как выполненную.
        """
        start_time = time.time()
        
        result = {
            "command": "complete-task",
            "task_number": task_number,
            "success": False,
            "updated_lines": 0
        }
        
        try:
            if not self.todo_file.exists():
                result["error"] = f"Todo file not found: {self.todo_file}"
                return result
            
            with open(self.todo_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Обновляем статус задачи
            updated_content, updated_lines = self._mark_task_complete(
                content, task_number, completion_note
            )
            
            if updated_lines > 0:
                # Сохраняем обновленный файл
                with open(self.todo_file, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                result.update({
                    "success": True,
                    "updated_lines": updated_lines,
                    "message": f"Задача {task_number} отмечена как выполненная"
                })
            else:
                result["error"] = f"Задача {task_number} не найдена или уже выполнена"
                
        except Exception as e:
            result["error"] = str(e)
        
        result["duration_ms"] = (time.time() - start_time) * 1000
        return result
    
    def report_progress(self) -> Dict[str, Any]:
        """
        MCP команда: report-progress
        Выводит прогресс и следующие задачи для пользователя.
        """
        start_time = time.time()
        
        result = {
            "command": "report-progress",
            "success": False,
            "progress_summary": "",
            "next_actions": [],
            "completed_count": 0,
            "remaining_count": 0
        }
        
        try:
            if not self.todo_file.exists():
                result["error"] = f"Todo file not found: {self.todo_file}"
                return result
            
            with open(self.todo_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Анализируем прогресс
            completed_tasks = self._parse_completed_tasks(content)
            incomplete_tasks = self._parse_incomplete_tasks(content)
            
            # Генерируем отчет о прогрессе
            progress_summary = self._generate_progress_summary(completed_tasks, incomplete_tasks)
            next_actions = self._generate_next_actions(incomplete_tasks)
            
            result.update({
                "success": True,
                "progress_summary": progress_summary,
                "next_actions": next_actions,
                "completed_count": len(completed_tasks),
                "remaining_count": len(incomplete_tasks)
            })
                
        except Exception as e:
            result["error"] = str(e)
        
        result["duration_ms"] = (time.time() - start_time) * 1000
        return result
    
    def get_task_status(self) -> Dict[str, Any]:
        """
        MCP команда: task-status
        Получает статус всех активных задач.
        """
        start_time = time.time()
        
        result = {
            "command": "task-status",
            "success": False,
            "all_tasks": [],
            "summary": {}
        }
        
        try:
            if not self.todo_file.exists():
                result["error"] = f"Todo file not found: {self.todo_file}"
                return result
            
            with open(self.todo_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Парсим все задачи
            all_tasks = self._parse_all_tasks(content)
            summary = self._generate_task_summary(all_tasks)
            
            result.update({
                "success": True,
                "all_tasks": all_tasks,
                "summary": summary
            })
                
        except Exception as e:
            result["error"] = str(e)
        
        result["duration_ms"] = (time.time() - start_time) * 1000
        return result
    
    def _parse_incomplete_tasks(self, content: str) -> List[Dict]:
        """Парсит незавершенные задачи из содержимого"""
        tasks = []
        lines = content.split('\n')
        current_task = None
        task_number = 0
        
        for line in lines:
            if line.startswith('### Задача') and '✅ ЗАВЕРШЕНО' not in line:
                task_number += 1
                current_task = {
                    "number": task_number,
                    "title": line.strip(),
                    "subtasks": []
                }
                tasks.append(current_task)
            elif line.strip().startswith('- [ ]') and current_task:
                current_task["subtasks"].append(line.strip())
        
        return tasks
    
    def _parse_completed_tasks(self, content: str) -> List[Dict]:
        """Парсит завершенные задачи из содержимого"""
        tasks = []
        lines = content.split('\n')
        task_number = 0
        
        for line in lines:
            if line.startswith('### Задача') and '✅ ЗАВЕРШЕНО' in line:
                task_number += 1
                tasks.append({
                    "number": task_number,
                    "title": line.strip()
                })
        
        return tasks
    
    def _parse_all_tasks(self, content: str) -> List[Dict]:
        """Парсит все задачи из содержимого"""
        completed = self._parse_completed_tasks(content)
        incomplete = self._parse_incomplete_tasks(content)
        
        all_tasks = []
        for task in completed:
            task["status"] = "completed"
            all_tasks.append(task)
        for task in incomplete:
            task["status"] = "incomplete"
            all_tasks.append(task)
        
        return all_tasks
    
    def _mark_task_complete(self, content: str, task_number: int, note: str = "") -> tuple:
        """Отмечает задачу как выполненную в содержимом"""
        lines = content.split('\n')
        updated_lines = 0
        task_found = False
        current_task_num = 0
        
        for i, line in enumerate(lines):
            if line.startswith('### Задача'):
                current_task_num += 1
                if current_task_num == task_number and '✅ ЗАВЕРШЕНО' not in line:
                    # Обновляем заголовок задачи
                    lines[i] = line.replace('### Задача', '### Задача') + ' ✅ ЗАВЕРШЕНО'
                    if note:
                        lines[i] += f' - {note}'
                    updated_lines += 1
                    task_found = True
            elif task_found and line.strip().startswith('- [ ]'):
                # Отмечаем подзадачи как выполненные
                lines[i] = line.replace('- [ ]', '- [x] ✅')
                updated_lines += 1
            elif task_found and line.startswith('### Задача'):
                # Переходим к следующей задаче
                break
        
        return '\n'.join(lines), updated_lines
    
    def _generate_progress_summary(self, completed: List, incomplete: List) -> str:
        """Генерирует краткий отчет о прогрессе"""
        total = len(completed) + len(incomplete)
        if total == 0:
            return "Нет задач для отслеживания"
        
        progress_percent = (len(completed) / total) * 100
        
        summary = f"📊 Прогресс: {len(completed)}/{total} задач выполнено ({progress_percent:.1f}%)\n"
        
        if completed:
            summary += f"✅ Завершенные задачи:\n"
            for task in completed[-3:]:  # Показываем последние 3
                summary += f"  • {task['title']}\n"
        
        return summary
    
    def _generate_next_actions(self, incomplete: List) -> List[str]:
        """Генерирует список следующих действий"""
        if not incomplete:
            return ["🎉 Все задачи выполнены! Можно приступать к новым проектам."]
        
        actions = []
        next_task = incomplete[0]
        actions.append(f"🎯 Следующая задача: {next_task['title']}")
        
        if next_task['subtasks']:
            actions.append(f"📋 Подзадачи ({len(next_task['subtasks'])}):")
            for subtask in next_task['subtasks'][:3]:  # Показываем первые 3
                actions.append(f"  {subtask}")
        
        return actions
    
    def _generate_task_summary(self, all_tasks: List) -> Dict:
        """Генерирует сводку по всем задачам"""
        completed = [t for t in all_tasks if t['status'] == 'completed']
        incomplete = [t for t in all_tasks if t['status'] == 'incomplete']
        
        return {
            "total_tasks": len(all_tasks),
            "completed_tasks": len(completed),
            "incomplete_tasks": len(incomplete),
            "completion_rate": (len(completed) / len(all_tasks) * 100) if all_tasks else 0
        }

def test_task_manager():
    """Тест системы управления задачами"""
    print("🧪 Тест Task Manager MCP Module")
    
    manager = TaskManager()
    
    # Тест получения следующей задачи
    print("\n📋 Тест next-task...")
    next_result = manager.get_next_task()
    if next_result["success"]:
        if next_result["next_task"]:
            print(f"   ✅ Следующая задача: {next_result['next_task']}")
            print(f"   📊 Подзадач: {len(next_result['subtasks'])}")
        else:
            print(f"   🎉 {next_result['context']}")
    
    # Тест статуса задач
    print("\n📊 Тест task-status...")
    status_result = manager.get_task_status()
    if status_result["success"]:
        summary = status_result["summary"]
        print(f"   ✅ Всего задач: {summary['total_tasks']}")
        print(f"   ✅ Выполнено: {summary['completed_tasks']}")
        print(f"   📋 Остается: {summary['incomplete_tasks']}")
        print(f"   📈 Прогресс: {summary['completion_rate']:.1f}%")
    
    # Тест отчета о прогрессе
    print("\n📈 Тест report-progress...")
    progress_result = manager.report_progress()
    if progress_result["success"]:
        print(f"   ✅ Отчет сгенерирован")
        print(f"   📊 Выполнено: {progress_result['completed_count']}")
        print(f"   📋 Остается: {progress_result['remaining_count']}")
    
    print("\n✅ Task Manager готов к использованию!")

if __name__ == "__main__":
    test_task_manager()