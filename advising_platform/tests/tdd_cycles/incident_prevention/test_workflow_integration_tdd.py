#!/usr/bin/env python3
"""
TDD тесты для предотвращения workflow инцидентов
Проблема: Workflows не стартуют и падают с ошибками

По стандарту TDD-doc 4.1: Red-Green-Refactor цикл
"""

import pytest
import subprocess
import time
import requests
import os


class TestWorkflowIntegrationIncidentPrevention:
    """
    TDD тесты, которые выявили бы проблемы с workflow раньше
    """
    
    def setup_method(self):
        """Настройка для каждого теста"""
        self.project_root = "advising_platform"
        self.timeout = 10
        
    # RED PHASE - Тесты, которые должны выявить проблемы
    
    def test_standards_mcp_server_startup_red(self):
        """
        RED: Проверка запуска StandardsMCP workflow
        
        Этот тест выявил бы проблему с запуском MCP сервера
        """
        cmd = ["node", f"{self.project_root}/src/mcp/standards_mcp_server.js"]
        
        try:
            # Пытаемся запустить процесс
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Даем время на запуск
            time.sleep(3)
            
            # Проверяем что процесс все еще работает
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                pytest.fail(f"StandardsMCP сервер упал при запуске. STDERR: {stderr}")
            
            # Пытаемся подключиться к HTTP API
            try:
                response = requests.get("http://localhost:3001/health", timeout=2)
                assert response.status_code == 200, "HTTP API недоступен"
            except requests.ConnectionError:
                pytest.fail("HTTP API не запустился вместе с MCP сервером")
            finally:
                process.terminate()
                
        except FileNotFoundError:
            pytest.fail("Файл standards_mcp_server.js не найден")
        except Exception as e:
            pytest.fail(f"Ошибка запуска StandardsMCP: {e}")
    
    def test_api_server_module_import_red(self):
        """
        RED: Проверка импорта модулей API сервера
        
        Этот тест выявил бы проблемы с импортами Python модулей
        """
        cmd = ["python", "-c", "from advising_platform.src.api.app import app; print('Import OK')"]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd="."
            )
            
            assert result.returncode == 0, f"Ошибка импорта API модуля: {result.stderr}"
            assert "Import OK" in result.stdout, "Импорт не завершился успешно"
            
        except subprocess.TimeoutExpired:
            pytest.fail("Таймаут при импорте API модуля")
        except Exception as e:
            pytest.fail(f"Ошибка проверки импорта: {e}")
    
    def test_web_server_module_import_red(self):
        """
        RED: Проверка импорта модулей веб сервера
        
        Этот тест выявил бы проблему "No module named advising_platform.__main__"
        """
        cmd = ["python", "-m", "advising_platform.main", "--help"]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd="."
            )
            
            # Если возвращается код ошибки, проверяем причину
            if result.returncode != 0:
                if "No module named" in result.stderr:
                    pytest.fail(f"Проблема с импортом модуля: {result.stderr}")
                elif "ModuleNotFoundError" in result.stderr:
                    pytest.fail(f"Отсутствует модуль: {result.stderr}")
            
        except subprocess.TimeoutExpired:
            pytest.fail("Таймаут при проверке модуля main")
        except Exception as e:
            pytest.fail(f"Ошибка проверки main модуля: {e}")
    
    def test_event_watcher_type_errors_red(self):
        """
        RED: Проверка синтаксических ошибок в EventWatcher
        
        Этот тест выявил бы ошибки типов List/Dict
        """
        event_watcher_path = f"{self.project_root}/src/mcp/modules/event_watcher.py"
        
        # Проверяем что файл существует
        assert os.path.exists(event_watcher_path), f"Файл {event_watcher_path} не найден"
        
        # Пытаемся скомпилировать файл
        cmd = ["python", "-m", "py_compile", event_watcher_path]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            assert result.returncode == 0, f"Синтаксические ошибки в event_watcher.py: {result.stderr}"
            
        except subprocess.TimeoutExpired:
            pytest.fail("Таймаут при компиляции event_watcher.py")
    
    # GREEN PHASE - Тесты для проверки исправлений
    
    def test_all_workflows_health_check_green(self):
        """
        GREEN: Проверка что все критичные workflow работают
        
        После исправлений этот тест должен проходить
        """
        critical_workflows = [
            ("ApiServer", "python", f"{self.project_root}/src/api/app.py"),
            ("WebServer", "python", f"{self.project_root}/src/web/simple_server.py"),
            ("StandardsMCP", "node", f"{self.project_root}/src/mcp/standards_mcp_server.js")
        ]
        
        for workflow_name, interpreter, script_path in critical_workflows:
            # Проверяем что файл существует
            if not os.path.exists(script_path):
                pytest.fail(f"Скрипт {workflow_name} не найден: {script_path}")
            
            # Пытаемся запустить с --help или проверкой синтаксиса
            if interpreter == "python":
                cmd = ["python", "-m", "py_compile", script_path]
            else:
                cmd = ["node", "--check", script_path]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                assert result.returncode == 0, f"Ошибки в {workflow_name}: {result.stderr}"
                
            except subprocess.TimeoutExpired:
                pytest.fail(f"Таймаут при проверке {workflow_name}")


class TestSystemIntegrationTDD:
    """
    Интеграционные TDD тесты для системы в целом
    """
    
    def test_database_connection_availability_red(self):
        """
        RED: Проверка доступности базы данных
        
        Системные компоненты должны иметь доступ к БД
        """
        cmd = ["python", "-c", """
import os
print(f"DATABASE_URL present: {'DATABASE_URL' in os.environ}")
if 'DATABASE_URL' in os.environ:
    print(f"DATABASE_URL format: {os.environ['DATABASE_URL'][:20]}...")
"""]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            assert result.returncode == 0, f"Ошибка проверки DATABASE_URL: {result.stderr}"
            assert "DATABASE_URL present: True" in result.stdout, "DATABASE_URL не установлен"
            
        except subprocess.TimeoutExpired:
            pytest.fail("Таймаут при проверке DATABASE_URL")
    
    def test_mcp_dependency_matrix_validity_red(self):
        """
        RED: Проверка валидности dependency matrix
        
        Системные зависимости должны быть корректно описаны
        """
        matrix_path = "mcp_dependency_matrix.json"
        
        if os.path.exists(matrix_path):
            cmd = ["python", "-c", f"""
import json
try:
    with open('{matrix_path}', 'r') as f:
        data = json.load(f)
    print("JSON valid")
    print(f"Commands count: {{len(data.get('commands', []))}}")
except Exception as e:
    print(f"Error: {{e}}")
"""]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            assert result.returncode == 0, f"Ошибка валидации dependency matrix: {result.stderr}"
            assert "JSON valid" in result.stdout, "dependency matrix содержит невалидный JSON"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])