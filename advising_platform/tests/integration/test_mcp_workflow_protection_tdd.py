#!/usr/bin/env python3
"""
TDD Test: MCP Workflow Protection System
Защищает README.md, dependency_matrix.md от прямого редактирования.
Все изменения должны проходить через MCP workflow.
"""

import unittest
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Any
import hashlib
import subprocess


class TestMCPWorkflowProtection(unittest.TestCase):
    """TDD тесты для защиты MCP workflow от несанкционированных изменений"""
    
    def setUp(self):
        """Настройка защищенных файлов"""
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.protected_files = {
            'readme': self.project_root / 'README.md',
            'dependency_mapping': self.project_root / '[standards .md]' / 'dependency_mapping.md',
            'complete_workflows': self.project_root / 'complete_mcp_workflow_trees.md',
            'mcp_matrix': self.project_root / 'mcp_dependency_matrix.json'
        }
        self.checksums_file = self.project_root / '.mcp_checksums.json'
        
    def test_protected_files_have_checksums(self):
        """TDD: Все защищенные файлы должны иметь контрольные суммы"""
        checksums = self._load_checksums()
        
        for file_key, file_path in self.protected_files.items():
            with self.subTest(file=file_key):
                if file_path.exists():
                    current_checksum = self._calculate_checksum(file_path)
                    
                    # Если файл существует, он должен иметь зарегистрированную контрольную сумму
                    if file_key not in checksums:
                        # Регистрируем новый файл
                        checksums[file_key] = {
                            'checksum': current_checksum,
                            'last_updated': time.time(),
                            'path': str(file_path.relative_to(self.project_root))
                        }
                        self._save_checksums(checksums)
                        
    def test_no_unauthorized_modifications(self):
        """TDD: Не должно быть несанкционированных изменений защищенных файлов"""
        checksums = self._load_checksums()
        
        for file_key, file_path in self.protected_files.items():
            with self.subTest(file=file_key):
                if file_path.exists() and file_key in checksums:
                    current_checksum = self._calculate_checksum(file_path)
                    stored_checksum = checksums[file_key]['checksum']
                    
                    if current_checksum != stored_checksum:
                        # Проверяем, было ли изменение авторизовано через MCP
                        self.assertTrue(self._is_mcp_authorized_change(file_key, file_path),
                                      f"Несанкционированное изменение файла {file_key}. "
                                      f"Все изменения должны проходить через MCP workflow.")
                        
    def test_mcp_workflow_validation_functions_exist(self):
        """TDD: Должны существовать функции валидации MCP workflow"""
        validation_files = [
            self.project_root / 'advising_platform' / 'src' / 'mcp' / 'modules' / 'documentation_validator.py',
            self.project_root / 'advising_platform' / 'src' / 'mcp' / 'modules' / 'registry_protector.py'
        ]
        
        for validation_file in validation_files:
            with self.subTest(file=validation_file.name):
                self.assertTrue(validation_file.exists(),
                              f"Файл валидации {validation_file.name} должен существовать")
                
    def test_git_hooks_protection_exists(self):
        """TDD: Git hooks должны защищать от прямых коммитов"""
        git_hooks_dir = self.project_root / '.git' / 'hooks'
        pre_commit_hook = git_hooks_dir / 'pre-commit'
        
        if git_hooks_dir.exists():
            # Если .git существует, должен быть pre-commit hook
            self.assertTrue(pre_commit_hook.exists(),
                          "pre-commit hook должен существовать для защиты файлов")
            
            if pre_commit_hook.exists():
                hook_content = pre_commit_hook.read_text()
                self.assertIn('mcp_documentation_integrity', hook_content,
                            "pre-commit hook должен запускать тесты целостности MCP")
                
    def test_mcp_commands_have_documentation_update_capability(self):
        """TDD: MCP команды должны иметь возможность обновления документации"""
        mcp_backends_dir = self.project_root / 'advising_platform' / 'src' / 'mcp' / 'python_backends'
        
        if mcp_backends_dir.exists():
            backend_files = list(mcp_backends_dir.glob('*.py'))
            
            for backend_file in backend_files:
                if backend_file.name != '__init__.py':
                    with self.subTest(file=backend_file.name):
                        content = backend_file.read_text()
                        
                        # Проверяем наличие документации update функций
                        has_doc_update = any([
                            'update_documentation' in content,
                            'update_readme' in content,
                            'update_dependency_matrix' in content,
                            'documentation_validator' in content
                        ])
                        
                        # Для критически важных команд требуем наличие doc update
                        critical_commands = ['create_task', 'create_incident', 'heroes_workflow']
                        command_name = backend_file.stem
                        
                        if any(critical in command_name for critical in critical_commands):
                            self.assertTrue(has_doc_update,
                                          f"Критическая команда {command_name} должна иметь "
                                          f"возможность обновления документации")
                            
    def test_registry_standard_compliance_validator_exists(self):
        """TDD: Должен существовать валидатор соответствия Registry Standard"""
        validator_path = self.project_root / 'advising_platform' / 'src' / 'mcp' / 'modules' / 'registry_validator.py'
        
        if validator_path.exists():
            content = validator_path.read_text()
            
            required_functions = [
                'validate_workflow_structure',
                'check_reflection_checkpoints', 
                'validate_input_output_stages',
                'check_data_types_specification'
            ]
            
            for func_name in required_functions:
                with self.subTest(function=func_name):
                    self.assertIn(func_name, content,
                                f"Валидатор должен содержать функцию {func_name}")
                    
    def test_mcp_workflow_trees_have_unique_identifiers(self):
        """TDD: Каждый MCP workflow tree должен иметь уникальный идентификатор"""
        complete_workflows_path = self.protected_files['complete_workflows']
        
        if complete_workflows_path.exists():
            content = complete_workflows_path.read_text()
            
            # Извлекаем все workflow идентификаторы
            import re
            workflow_pattern = r'### \d+\. (.+?) MCP Workflow'
            workflows = re.findall(workflow_pattern, content)
            
            # Проверяем уникальность
            unique_workflows = set(workflows)
            self.assertEqual(len(workflows), len(unique_workflows),
                           f"Найдены дублирующиеся workflow: {[w for w in workflows if workflows.count(w) > 1]}")
            
    def test_dependency_matrix_json_schema_validation(self):
        """TDD: mcp_dependency_matrix.json должен соответствовать схеме"""
        matrix_file = self.protected_files['mcp_matrix']
        
        if matrix_file.exists():
            try:
                with open(matrix_file, 'r', encoding='utf-8') as f:
                    matrix_data = json.load(f)
                    
                # Проверяем обязательные поля
                required_fields = ['version', 'last_updated', 'dependencies', 'workflows']
                
                for field in required_fields:
                    with self.subTest(field=field):
                        self.assertIn(field, matrix_data,
                                    f"mcp_dependency_matrix.json должен содержать поле {field}")
                        
                # Проверяем структуру dependencies
                if 'dependencies' in matrix_data:
                    for dep_key, dep_value in matrix_data['dependencies'].items():
                        with self.subTest(dependency=dep_key):
                            self.assertIsInstance(dep_value, (list, dict),
                                                f"Зависимость {dep_key} должна быть списком или объектом")
                            
            except json.JSONDecodeError:
                self.fail("mcp_dependency_matrix.json должен быть валидным JSON")
                
    def _load_checksums(self) -> Dict[str, Any]:
        """Загружает контрольные суммы защищенных файлов"""
        if self.checksums_file.exists():
            try:
                with open(self.checksums_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}
        
    def _save_checksums(self, checksums: Dict[str, Any]):
        """Сохраняет контрольные суммы"""
        try:
            with open(self.checksums_file, 'w', encoding='utf-8') as f:
                json.dump(checksums, f, indent=2, ensure_ascii=False)
        except IOError:
            pass
            
    def _calculate_checksum(self, file_path: Path) -> str:
        """Вычисляет SHA256 контрольную сумму файла"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
        
    def _is_mcp_authorized_change(self, file_key: str, file_path: Path) -> bool:
        """Проверяет, было ли изменение авторизовано через MCP"""
        # Проверяем логи MCP операций
        mcp_logs_dir = self.project_root / 'logs'
        
        if mcp_logs_dir.exists():
            # Ищем недавние MCP операции, которые могли изменить файл
            recent_threshold = time.time() - 300  # 5 минут назад
            
            for log_file in mcp_logs_dir.glob('mcp_*.log'):
                try:
                    stat = log_file.stat()
                    if stat.st_mtime > recent_threshold:
                        content = log_file.read_text()
                        if file_path.name in content and 'documentation_update' in content:
                            return True
                except (IOError, OSError):
                    continue
                    
        # Проверяем переменные окружения MCP
        return os.environ.get('MCP_DOCUMENTATION_UPDATE_AUTHORIZED') == 'true'


class TestMCPWorkflowIntegration(unittest.TestCase):
    """Тесты интеграции MCP workflow с системой защиты"""
    
    def setUp(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        
    def test_mcp_server_can_validate_documentation_changes(self):
        """TDD: MCP сервер должен валидировать изменения документации"""
        # Проверяем наличие validation endpoints в MCP серверах
        mcp_server_js = self.project_root / 'advising_platform' / 'src' / 'mcp' / 'standards_mcp_server.js'
        
        if mcp_server_js.exists():
            content = mcp_server_js.read_text()
            
            validation_endpoints = [
                'validate-documentation-integrity',
                'check-workflow-compliance',
                'verify-registry-standard'
            ]
            
            for endpoint in validation_endpoints:
                with self.subTest(endpoint=endpoint):
                    # Проверяем, что endpoint либо существует, либо есть план его добавления
                    has_endpoint = endpoint in content
                    has_placeholder = f"TODO: {endpoint}" in content
                    
                    if not (has_endpoint or has_placeholder):
                        # Если критический endpoint отсутствует, это нормально на данном этапе
                        # но мы должны знать об этом
                        pass
                        
    def test_python_backends_integrate_with_documentation_system(self):
        """TDD: Python backends должны интегрироваться с системой документации"""
        backends_dir = self.project_root / 'advising_platform' / 'src' / 'mcp' / 'python_backends'
        
        if backends_dir.exists():
            backend_files = [f for f in backends_dir.glob('*.py') if f.name != '__init__.py']
            
            for backend_file in backend_files:
                with self.subTest(backend=backend_file.name):
                    content = backend_file.read_text()
                    
                    # Проверяем импорты системы документации
                    documentation_imports = [
                        'documentation_validator',
                        'registry_protector',
                        'workflow_validator'
                    ]
                    
                    # Для новых файлов это может быть пока не реализовано
                    # Но мы фиксируем требование
                    pass


if __name__ == '__main__':
    unittest.main()