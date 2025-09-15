#!/usr/bin/env python3
"""
TDD Test: MCP Documentation Integrity
Проверяет соответствие README.md, dependency_mapping.md и complete_mcp_workflow_trees.md 
реальным MCP командам и workflow в коде.
"""

import os
import json
import re
import unittest
from pathlib import Path
from typing import Dict, List, Set, Any
import ast


class TestMCPDocumentationIntegrity(unittest.TestCase):
    """TDD тесты для проверки целостности MCP документации"""
    
    def setUp(self):
        """Настройка тестового окружения"""
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.docs_files = {
            'readme': self.project_root / 'README.md',
            'dependency_mapping': self.project_root / '[standards .md]' / 'dependency_mapping.md',
            'complete_workflows': self.project_root / 'complete_mcp_workflow_trees.md'
        }
        self.mcp_source_dirs = {
            'js_server': self.project_root / 'advising_platform' / 'src' / 'mcp' / 'standards_mcp_server.js',
            'python_backends': self.project_root / 'advising_platform' / 'src' / 'mcp' / 'python_backends',
            'python_modules': self.project_root / 'advising_platform' / 'src' / 'mcp' / 'modules'
        }
        
    def test_all_documentation_files_exist(self):
        """TDD: Все файлы документации должны существовать"""
        for doc_name, doc_path in self.docs_files.items():
            with self.subTest(document=doc_name):
                self.assertTrue(doc_path.exists(), 
                              f"Документ {doc_name} не найден: {doc_path}")
                
    def test_mcp_commands_in_js_server_match_documentation(self):
        """TDD: MCP команды в JS сервере должны соответствовать документации"""
        # Извлекаем команды из JavaScript MCP сервера
        js_commands = self._extract_js_mcp_commands()
        
        # Извлекаем команды из документации
        doc_js_commands = self._extract_documented_js_commands()
        
        # Проверяем соответствие
        self.assertEqual(set(js_commands), set(doc_js_commands),
                        f"MCP команды в JS сервере не соответствуют документации.\n"
                        f"В коде: {js_commands}\n"
                        f"В документации: {doc_js_commands}")
        
    def test_python_backend_commands_match_documentation(self):
        """TDD: Python backend команды должны соответствовать документации"""
        # Извлекаем команды из Python backends
        python_commands = self._extract_python_backend_commands()
        
        # Извлекаем команды из документации
        doc_python_commands = self._extract_documented_python_commands()
        
        # Проверяем соответствие
        self.assertEqual(set(python_commands), set(doc_python_commands),
                        f"Python backend команды не соответствуют документации.\n"
                        f"В коде: {python_commands}\n"
                        f"В документации: {doc_python_commands}")
        
    def test_workflow_trees_have_required_structure(self):
        """TDD: Все workflow trees должны иметь требуемую структуру по Registry Standard"""
        workflow_content = self._read_file_content(self.docs_files['complete_workflows'])
        
        # Извлекаем все workflow деревья
        workflows = self._extract_workflow_trees(workflow_content)
        
        for workflow_name, workflow_content in workflows.items():
            with self.subTest(workflow=workflow_name):
                # Проверяем наличие INPUT STAGE
                self.assertIn('📥 INPUT STAGE', workflow_content,
                            f"Workflow {workflow_name} должен содержать INPUT STAGE")
                
                # Проверяем наличие OUTPUT STAGE
                self.assertIn('📤 OUTPUT STAGE', workflow_content,
                            f"Workflow {workflow_name} должен содержать OUTPUT STAGE")
                
                # Проверяем наличие [reflection] checkpoints
                reflection_count = workflow_content.count('[reflection]')
                self.assertGreaterEqual(reflection_count, 1,
                                      f"Workflow {workflow_name} должен содержать минимум 1 [reflection] checkpoint")
                
                # Проверяем наличие типов данных в INPUT
                self.assertTrue(self._has_input_data_types(workflow_content),
                              f"Workflow {workflow_name} должен содержать типы данных в INPUT STAGE")
                
    def test_dependency_mapping_includes_all_documentation_files(self):
        """TDD: dependency_mapping.md должен включать все файлы документации"""
        dependency_content = self._read_file_content(self.docs_files['dependency_mapping'])
        
        expected_files = [
            'README.md',
            'complete_mcp_workflow_trees.md',
            'dependency_mapping.md',
            'standards_system.duckdb',
            'mcp_dependency_matrix.json'
        ]
        
        for expected_file in expected_files:
            with self.subTest(file=expected_file):
                self.assertIn(expected_file, dependency_content,
                            f"dependency_mapping.md должен упоминать {expected_file}")
                
    def test_readme_contains_main_workflow_trees(self):
        """TDD: README.md должен содержать основные workflow trees"""
        readme_content = self._read_file_content(self.docs_files['readme'])
        
        expected_workflows = [
            'create-task',
            'create-incident', 
            'heroes-workflow',
            'form-hypothesis'
        ]
        
        for workflow in expected_workflows:
            with self.subTest(workflow=workflow):
                self.assertIn(f'{workflow} MCP Command', readme_content,
                            f"README.md должен содержать workflow {workflow}")
                
    def test_mcp_workflow_consistency_across_documents(self):
        """TDD: MCP workflow должны быть консистентными между документами"""
        readme_workflows = self._extract_workflow_names_from_readme()
        complete_workflows = self._extract_workflow_names_from_complete()
        
        # Все workflow из README должны быть в complete_mcp_workflow_trees.md
        for workflow in readme_workflows:
            with self.subTest(workflow=workflow):
                self.assertIn(workflow, complete_workflows,
                            f"Workflow {workflow} из README.md должен быть в complete_mcp_workflow_trees.md")
                
    def test_documented_commands_match_actual_file_structure(self):
        """TDD: Документированные команды должны соответствовать реальной файловой структуре"""
        # Проверяем Python backends
        backend_files = list(self.mcp_source_dirs['python_backends'].glob('*.py'))
        documented_backends = self._extract_documented_python_commands()
        
        for backend_file in backend_files:
            if backend_file.name != '__init__.py':
                command_name = self._extract_command_from_filename(backend_file.name)
                if command_name:
                    self.assertIn(command_name, documented_backends,
                                f"Файл {backend_file.name} содержит команду {command_name}, "
                                f"которая должна быть документирована")
                    
    def _extract_js_mcp_commands(self) -> List[str]:
        """Извлекает MCP команды из JavaScript сервера"""
        js_file = self.mcp_source_dirs['js_server']
        if not js_file.exists():
            return []
            
        content = self._read_file_content(js_file)
        
        # Ищем pattern: name: "command-name" в определениях tools
        pattern = r'name:\s*["\']([a-z-]+)["\']'
        matches = re.findall(pattern, content)
        
        # Фильтруем, исключая служебные имена
        filtered_matches = [m for m in matches if m not in ['standards-mcp-server']]
        
        return sorted(list(set(filtered_matches)))
        
    def _extract_python_backend_commands(self) -> List[str]:
        """Извлекает команды из Python backend файлов"""
        backend_dir = self.mcp_source_dirs['python_backends']
        if not backend_dir.exists():
            return []
            
        commands = []
        for py_file in backend_dir.glob('*.py'):
            if py_file.name != '__init__.py':
                command = self._extract_command_from_filename(py_file.name)
                if command:
                    commands.append(command)
                    
        return sorted(commands)
        
    def _extract_documented_js_commands(self) -> List[str]:
        """Извлекает JS команды из документации"""
        complete_content = self._read_file_content(self.docs_files['complete_workflows'])
        
        # Ищем секцию "JavaScript MCP Server"
        js_section_pattern = r'### JavaScript MCP Server.*?### Python Backends'
        js_section_match = re.search(js_section_pattern, complete_content, re.DOTALL)
        
        if not js_section_match:
            return []
            
        js_section = js_section_match.group(0)
        
        # Извлекаем команды (format: **command-name**)
        command_pattern = r'\*\*([a-z-]+)\*\* -'
        commands = re.findall(command_pattern, js_section)
        
        return sorted(commands)
        
    def _extract_documented_python_commands(self) -> List[str]:
        """Извлекает Python команды из документации"""
        complete_content = self._read_file_content(self.docs_files['complete_workflows'])
        
        # Ищем только секцию Python Backends (до Python Modules)
        python_pattern = r'### Python Backends.*?### Python Modules'
        python_match = re.search(python_pattern, complete_content, re.DOTALL)
        
        if not python_match:
            return []
            
        python_backends_section = python_match.group(0)
        
        # Извлекаем команды только из Python Backends секции
        command_pattern = r'\*\*([a-z-]+)\*\* -'
        commands = re.findall(command_pattern, python_backends_section)
        
        return sorted(commands)
        
    def _extract_workflow_trees(self, content: str) -> Dict[str, str]:
        """Извлекает workflow деревья из контента"""
        workflows = {}
        
        # Ищем pattern: ### N. Command Name MCP Workflow
        workflow_pattern = r'### \d+\. (.+?) MCP Workflow\s*```(.*?)```'
        matches = re.findall(workflow_pattern, content, re.DOTALL)
        
        for workflow_name, workflow_content in matches:
            workflows[workflow_name.strip()] = workflow_content.strip()
            
        return workflows
        
    def _extract_workflow_names_from_readme(self) -> List[str]:
        """Извлекает имена workflow из README.md"""
        readme_content = self._read_file_content(self.docs_files['readme'])
        
        # Ищем pattern с эмодзи в начале строки: 📝/🚨/💡/🎯/🤖 command-name MCP Command
        pattern = r'^[📝🚨💡🎯🤖🏗️] ([a-z-]+) MCP Command'
        matches = re.findall(pattern, readme_content, re.MULTILINE)
        
        return sorted(matches)
        
    def _extract_workflow_names_from_complete(self) -> List[str]:
        """Извлекает имена workflow из complete_mcp_workflow_trees.md"""
        complete_content = self._read_file_content(self.docs_files['complete_workflows'])
        
        # Ищем workflow headers с любыми эмодзи: 📝/🚨/💡/🎯/🏗️ command-name MCP Command
        pattern = r'[📝🚨💡🎯🏗️🤖] ([a-z-]+) MCP Command'
        matches = re.findall(pattern, complete_content)
        
        return sorted(matches)
        
    def _extract_command_from_filename(self, filename: str) -> str:
        """Извлекает имя команды из имени файла"""
        # Убираем .py расширение и конвертируем underscore в dash
        command = filename.replace('.py', '').replace('_', '-')
        return command
        
    def _has_input_data_types(self, workflow_content: str) -> bool:
        """Проверяет наличие типов данных в INPUT STAGE"""
        input_section_pattern = r'📥 INPUT STAGE(.*?)├──'
        input_match = re.search(input_section_pattern, workflow_content, re.DOTALL)
        
        if not input_match:
            return False
            
        input_section = input_match.group(1)
        
        # Ищем типы данных: (string), (object), (array), (enum)
        type_pattern = r'\((string|object|array|enum|integer|boolean)[^)]*\)'
        return bool(re.search(type_pattern, input_section))
        
    def _read_file_content(self, file_path: Path) -> str:
        """Читает содержимое файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.fail(f"Не удалось прочитать файл {file_path}: {e}")


if __name__ == '__main__':
    unittest.main()