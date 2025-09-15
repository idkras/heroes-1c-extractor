"""
Registry Protector Module
Защищает MCP registry от несанкционированных изменений
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional, Set
import logging

logger = logging.getLogger(__name__)

class RegistryProtector:
    """Защитник MCP registry с контрольными суммами и валидацией"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.protected_files = {
            'complete_mcp_workflow_trees.md',
            'README.md',
            'dependency_mapping.md'
        }
        self.checksums_file = project_root / '.mcp_registry_checksums.json'
        
    def calculate_file_checksum(self, file_path: Path) -> str:
        """Вычисляет SHA-256 контрольную сумму файла"""
        if not file_path.exists():
            return ""
            
        with open(file_path, 'rb') as f:
            content = f.read()
            return hashlib.sha256(content).hexdigest()
    
    def load_checksums(self) -> Dict[str, str]:
        """Загружает сохраненные контрольные суммы"""
        if not self.checksums_file.exists():
            return {}
            
        try:
            with open(self.checksums_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Не удалось загрузить контрольные суммы: {e}")
            return {}
    
    def save_checksums(self, checksums: Dict[str, str]) -> None:
        """Сохраняет контрольные суммы"""
        try:
            with open(self.checksums_file, 'w') as f:
                json.dump(checksums, f, indent=2)
        except IOError as e:
            logger.error(f"Не удалось сохранить контрольные суммы: {e}")
    
    def update_checksums(self) -> None:
        """Обновляет контрольные суммы для всех защищенных файлов"""
        checksums = {}
        
        for filename in self.protected_files:
            file_path = self.project_root / filename
            if file_path.exists():
                checksums[filename] = self.calculate_file_checksum(file_path)
                logger.info(f"Обновлена контрольная сумма для {filename}")
        
        self.save_checksums(checksums)
        logger.info(f"Сохранены контрольные суммы для {len(checksums)} файлов")
    
    def verify_integrity(self) -> Dict[str, bool]:
        """Проверяет целостность защищенных файлов"""
        saved_checksums = self.load_checksums()
        results = {}
        
        for filename in self.protected_files:
            file_path = self.project_root / filename
            
            if not file_path.exists():
                results[filename] = False
                logger.warning(f"Защищенный файл {filename} не существует")
                continue
            
            current_checksum = self.calculate_file_checksum(file_path)
            saved_checksum = saved_checksums.get(filename, "")
            
            if saved_checksum == "":
                results[filename] = True  # Первый запуск
                logger.info(f"Первый запуск для {filename}")
            elif current_checksum == saved_checksum:
                results[filename] = True
                logger.debug(f"Файл {filename} прошел проверку целостности")
            else:
                results[filename] = False
                logger.error(f"Обнаружено несанкционированное изменение в {filename}")
        
        return results
    
    def detect_unauthorized_changes(self) -> List[str]:
        """Обнаруживает несанкционированные изменения"""
        verification_results = self.verify_integrity()
        return [filename for filename, is_valid in verification_results.items() if not is_valid]
    
    def protect_workflow_trees(self) -> bool:
        """Защищает workflow trees от изменений"""
        workflow_file = self.project_root / 'complete_mcp_workflow_trees.md'
        
        if not workflow_file.exists():
            logger.error("Файл workflow trees не найден для защиты")
            return False
        
        # Проверяем структуру workflow trees
        content = workflow_file.read_text()
        required_sections = [
            '## 🎯 1. BUILD JTBD MCP WORKFLOW',
            '## 🎯 2. CREATE TASK MCP WORKFLOW', 
            '## 🎯 3. CREATE INCIDENT MCP WORKFLOW',
            '## 🎯 4. FORM HYPOTHESIS MCP WORKFLOW',
            '## 🎯 5. BUILD JTBD MCP WORKFLOW',
            '## 🤖 6. HEROES WORKFLOW MCP'
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)
        
        if missing_sections:
            logger.error(f"Отсутствуют обязательные секции: {missing_sections}")
            return False
        
        logger.info("Workflow trees структура валидна")
        return True
    
    def validate_registry_standard_compliance(self) -> bool:
        """Валидирует соответствие Registry Standard"""
        workflow_file = self.project_root / 'complete_mcp_workflow_trees.md'
        
        if not workflow_file.exists():
            return False
        
        content = workflow_file.read_text()
        
        # Проверяем наличие [reflection] checkpoints
        reflection_count = content.count('[reflection]')
        expected_min_reflections = 20  # Минимум по 4 на каждый workflow
        
        if reflection_count < expected_min_reflections:
            logger.error(f"Недостаточно reflection checkpoints: {reflection_count} < {expected_min_reflections}")
            return False
        
        # Проверяем наличие INPUT/OUTPUT stages
        input_stages = content.count('INPUT STAGE')
        output_stages = content.count('OUTPUT STAGE')
        
        if input_stages < 5 or output_stages < 5:
            logger.error(f"Недостаточно INPUT/OUTPUT stages: {input_stages}/{output_stages}")
            return False
        
        logger.info("Registry Standard compliance проверен")
        return True

def create_registry_protector(project_root: Path) -> RegistryProtector:
    """Фабричная функция для создания RegistryProtector"""
    return RegistryProtector(project_root)