#!/usr/bin/env python3
"""
Documentation Validator Module
Автоматическое обновление документации при изменениях MCP команд
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class DocumentationValidator:
    """Валидатор и обновлятель документации MCP"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.documentation_log = project_root / "logs" / "documentation_updates.json"
        self.documentation_log.parent.mkdir(exist_ok=True)
        
    def update_documentation(self, command_name: str, metadata: Dict[str, Any]) -> bool:
        """Обновляет документацию для критических MCP команд"""
        try:
            # Логируем обновление документации
            update_entry = {
                "timestamp": datetime.now().isoformat(),
                "command": command_name,
                "metadata": metadata,
                "action": "documentation_update"
            }
            
            # Добавляем в лог
            self._append_to_log(update_entry)
            
            # Для критических команд обновляем соответствующие разделы
            if command_name in ["create_task", "create_incident", "heroes_workflow"]:
                self._update_critical_documentation(command_name, metadata)
            
            logger.info(f"Documentation updated for command: {command_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update documentation for {command_name}: {e}")
            return False
    
    def _append_to_log(self, entry: Dict[str, Any]) -> None:
        """Добавляет запись в лог документации"""
        try:
            # Читаем существующий лог
            if self.documentation_log.exists():
                with open(self.documentation_log, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            else:
                log_data = {"updates": []}
            
            # Добавляем новую запись
            log_data["updates"].append(entry)
            
            # Оставляем только последние 1000 записей
            if len(log_data["updates"]) > 1000:
                log_data["updates"] = log_data["updates"][-1000:]
            
            # Сохраняем обновленный лог
            with open(self.documentation_log, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.warning(f"Failed to append to documentation log: {e}")
    
    def _update_critical_documentation(self, command_name: str, metadata: Dict[str, Any]) -> None:
        """Обновляет документацию для критических команд"""
        try:
            # Определяем файл для обновления
            readme_path = self.project_root / "README.md"
            
            if not readme_path.exists():
                return
            
            # Читаем README
            content = readme_path.read_text(encoding='utf-8')
            
            # Создаем отметку об обновлении
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            update_marker = f"<!-- Last updated by {command_name}: {timestamp} -->"
            
            # Добавляем маркер в конец файла, если его еще нет
            if update_marker not in content:
                content += f"\n\n{update_marker}\n"
                readme_path.write_text(content, encoding='utf-8')
                
        except Exception as e:
            logger.warning(f"Failed to update critical documentation: {e}")
    
    def validate_registry_compliance(self) -> Dict[str, bool]:
        """Проверяет соответствие Registry Standard"""
        results = {
            "has_workflow_trees": False,
            "has_input_output_specs": False,
            "has_reflections": False,
            "documentation_consistent": False
        }
        
        try:
            # Проверяем наличие complete_mcp_workflow_trees.md
            workflow_trees_path = self.project_root / "complete_mcp_workflow_trees.md"
            if workflow_trees_path.exists():
                content = workflow_trees_path.read_text(encoding='utf-8')
                results["has_workflow_trees"] = True
                results["has_input_output_specs"] = "INPUT:" in content and "OUTPUT:" in content
                results["has_reflections"] = "[reflections]" in content
            
            # Проверяем консистентность документации
            results["documentation_consistent"] = self._check_documentation_consistency()
            
        except Exception as e:
            logger.error(f"Registry compliance validation failed: {e}")
        
        return results
    
    def _check_documentation_consistency(self) -> bool:
        """Проверяет консистентность документации"""
        try:
            # Простая проверка - существуют ли основные файлы
            required_files = [
                "README.md",
                "complete_mcp_workflow_trees.md"
            ]
            
            for file_name in required_files:
                file_path = self.project_root / file_name
                if not file_path.exists():
                    return False
            
            return True
            
        except Exception:
            return False

def update_documentation(command_name: str, metadata: Dict[str, Any]) -> bool:
    """Функция для обновления документации (используется в MCP командах)"""
    try:
        project_root = Path(__file__).parent.parent.parent.parent
        validator = DocumentationValidator(project_root)
        return validator.update_documentation(command_name, metadata)
    except Exception as e:
        logger.warning(f"Documentation update failed: {e}")
        return False

def validate_registry_compliance() -> Dict[str, bool]:
    """Функция для валидации соответствия Registry Standard"""
    try:
        project_root = Path(__file__).parent.parent.parent.parent
        validator = DocumentationValidator(project_root)
        return validator.validate_registry_compliance()
    except Exception as e:
        logger.error(f"Registry compliance validation failed: {e}")
        return {"error": True, "message": str(e)}

if __name__ == "__main__":
    # Тестирование модуля
    project_root = Path(__file__).parent.parent.parent.parent
    validator = DocumentationValidator(project_root)
    
    # Тестовое обновление
    result = validator.update_documentation("test_command", {"test": "data"})
    print(f"Documentation update result: {result}")
    
    # Тестовая валидация
    compliance = validator.validate_registry_compliance()
    print(f"Registry compliance: {compliance}")