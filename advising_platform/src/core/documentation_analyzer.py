#!/usr/bin/env python3
"""
JTBD:
Я (разработчик) хочу анализировать наличие и качество документации в коде, чтобы поддерживать единый стандарт документирования и улучшать понимание системы.

Взаимодействие:
- Принимает данные от: файлы исходного кода, система триггеров
- Передает данные в: система оповещений, триггеры задач

Автор: AI Assistant
Дата: 21 мая 2025
"""

import os
import re
import ast
import logging
import importlib.util
from typing import Dict, List, Any, Optional, Set, Tuple, Union

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class JTBDDocumentationAnalyzer:
    """
    JTBD:
    Я (разработчик) хочу автоматически проверять соответствие документации стандарту JTBD, чтобы обеспечить единообразие и полноту документирования кода.
    
    Анализатор документации в формате JTBD. Проверяет наличие и качество JTBD-документации
    в исходном коде Python.
    """
    
    def __init__(self, jtbd_pattern: str = r'JTBD:\s*\n?\s*Я\s+\([^)]+\)\s+хочу\s+[^,]+,\s+чтобы\s+[^.]+\.'):
        """
        Инициализирует анализатор JTBD-документации.
        
        Args:
            jtbd_pattern: Регулярное выражение для поиска JTBD-документации
        """
        self.jtbd_pattern = jtbd_pattern
        
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Анализирует файл на наличие JTBD-документации.
        
        Args:
            file_path: Путь к файлу для анализа
            
        Returns:
            Dict[str, Any]: Результаты анализа
        """
        if not os.path.exists(file_path) or not file_path.endswith('.py'):
            return {"status": "skipped", "message": "Не является Python-файлом"}
        
        try:
            # Читаем содержимое файла
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Анализируем содержимое
            result = self._analyze_content(content, file_path)
            return result
        except Exception as e:
            logger.error(f"Ошибка при анализе файла {file_path}: {e}")
            return {"status": "error", "message": str(e)}
    
    def _analyze_content(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Анализирует содержимое файла на наличие JTBD-документации.
        
        Args:
            content: Содержимое файла
            file_path: Путь к файлу (для отчетов)
            
        Returns:
            Dict[str, Any]: Результаты анализа
        """
        try:
            # Парсим файл с помощью ast
            tree = ast.parse(content)
            
            # Результаты анализа
            result = {
                "file_path": file_path,
                "has_module_jtbd": False,
                "has_class_jtbd": [],
                "has_function_jtbd": [],
                "missing_jtbd": [],
                "status": "success"
            }
            
            # Проверяем документацию модуля
            module_docstring = ast.get_docstring(tree)
            if module_docstring:
                result["has_module_jtbd"] = self._check_jtbd(module_docstring)
            else:
                result["missing_jtbd"].append(("module", os.path.basename(file_path)))
            
            # Проверяем классы и методы
            for node in ast.walk(tree):
                # Проверка классов
                if isinstance(node, ast.ClassDef):
                    class_docstring = ast.get_docstring(node)
                    class_has_jtbd = False
                    
                    if class_docstring:
                        class_has_jtbd = self._check_jtbd(class_docstring)
                        
                    result["has_class_jtbd"].append({
                        "name": node.name,
                        "has_jtbd": class_has_jtbd
                    })
                    
                    if not class_has_jtbd:
                        result["missing_jtbd"].append(("class", node.name))
                
                # Проверка функций и методов
                elif isinstance(node, ast.FunctionDef):
                    # Пропускаем "магические" и приватные методы
                    if node.name.startswith('__') or node.name.startswith('_'):
                        continue
                        
                    function_docstring = ast.get_docstring(node)
                    function_has_jtbd = False
                    
                    if function_docstring:
                        function_has_jtbd = self._check_jtbd(function_docstring)
                        
                    result["has_function_jtbd"].append({
                        "name": node.name,
                        "has_jtbd": function_has_jtbd
                    })
                    
                    if not function_has_jtbd:
                        result["missing_jtbd"].append(("function", node.name))
            
            return result
        except SyntaxError as e:
            logger.warning(f"Синтаксическая ошибка в файле {file_path}: {e}")
            return {"status": "syntax_error", "message": str(e), "file_path": file_path}
        except Exception as e:
            logger.error(f"Ошибка при анализе содержимого файла {file_path}: {e}")
            return {"status": "error", "message": str(e), "file_path": file_path}
    
    def _check_jtbd(self, docstring: str) -> bool:
        """
        Проверяет наличие JTBD в документации.
        
        Args:
            docstring: Документация для проверки
            
        Returns:
            bool: True, если документация содержит JTBD, иначе False
        """
        if not docstring:
            return False
            
        return bool(re.search(self.jtbd_pattern, docstring))
    
    def analyze_directory(self, directory_path: str, exclude_dirs: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Анализирует все Python-файлы в указанной директории и её поддиректориях.
        
        Args:
            directory_path: Путь к директории для анализа
            exclude_dirs: Список директорий, которые следует исключить из анализа
            
        Returns:
            Dict[str, Any]: Результаты анализа
        """
        if exclude_dirs is None:
            exclude_dirs = ['__pycache__', 'venv', '.git', '.vscode']
        
        results = {
            "analyzed_files": 0,
            "files_with_jtbd": 0,
            "missing_jtbd_modules": 0,
            "missing_jtbd_classes": 0,
            "missing_jtbd_functions": 0,
            "detailed_results": []
        }
        
        try:
            for root, dirs, files in os.walk(directory_path):
                # Исключаем указанные директории
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        file_result = self.analyze_file(file_path)
                        
                        results["analyzed_files"] += 1
                        
                        if file_result["status"] == "success":
                            # Добавляем результаты анализа файла
                            has_module_jtbd = file_result["has_module_jtbd"]
                            has_class_jtbd = any(c["has_jtbd"] for c in file_result["has_class_jtbd"])
                            has_function_jtbd = any(f["has_jtbd"] for f in file_result["has_function_jtbd"])
                            
                            if has_module_jtbd or has_class_jtbd or has_function_jtbd:
                                results["files_with_jtbd"] += 1
                            
                            # Подсчитываем отсутствующую документацию
                            for missing_type, missing_name in file_result["missing_jtbd"]:
                                if missing_type == "module":
                                    results["missing_jtbd_modules"] += 1
                                elif missing_type == "class":
                                    results["missing_jtbd_classes"] += 1
                                elif missing_type == "function":
                                    results["missing_jtbd_functions"] += 1
                            
                            results["detailed_results"].append(file_result)
            
            # Добавляем сводную статистику
            results["jtbd_coverage_percentage"] = (results["files_with_jtbd"] / results["analyzed_files"] * 100) if results["analyzed_files"] > 0 else 0
            
            return results
        except Exception as e:
            logger.error(f"Ошибка при анализе директории {directory_path}: {e}")
            return {"status": "error", "message": str(e)}
    
    def generate_jtbd_suggestions(self, file_analysis: Dict[str, Any]) -> Dict[str, str]:
        """
        Генерирует предложения JTBD-документации на основе анализа файла.
        
        Args:
            file_analysis: Результаты анализа файла
            
        Returns:
            Dict[str, str]: Предложения по документации для разных компонентов
        """
        suggestions = {}
        
        try:
            file_path = file_analysis["file_path"]
            file_name = os.path.basename(file_path)
            module_name = os.path.splitext(file_name)[0]
            
            # Генерируем предложение для модуля
            if not file_analysis["has_module_jtbd"]:
                module_suggestion = self._generate_module_suggestion(file_path, module_name)
                suggestions["module"] = module_suggestion
            
            # Генерируем предложения для классов
            for class_info in file_analysis.get("has_class_jtbd", []):
                if not class_info["has_jtbd"]:
                    class_suggestion = self._generate_class_suggestion(file_path, class_info["name"])
                    suggestions[f"class_{class_info['name']}"] = class_suggestion
            
            # Генерируем предложения для функций
            for function_info in file_analysis.get("has_function_jtbd", []):
                if not function_info["has_jtbd"]:
                    function_suggestion = self._generate_function_suggestion(file_path, function_info["name"])
                    suggestions[f"function_{function_info['name']}"] = function_suggestion
                    
            return suggestions
        except Exception as e:
            logger.error(f"Ошибка при генерации предложений JTBD: {e}")
            return {"error": str(e)}
    
    def _generate_module_suggestion(self, file_path: str, module_name: str) -> str:
        """
        Генерирует JTBD-документацию для модуля на основе его имени и содержимого.
        
        Args:
            file_path: Путь к файлу модуля
            module_name: Имя модуля
            
        Returns:
            str: Предложение документации
        """
        try:
            # Анализируем содержимое файла для более точной генерации
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Автоматически определяем основную функциональность модуля
            if "cache" in module_name:
                return """JTBD:
Я (разработчик) хочу эффективно управлять кешированием данных, чтобы ускорить доступ к часто используемым ресурсам и снизить нагрузку на систему."""
            elif "trigger" in module_name:
                return """JTBD:
Я (разработчик) хочу автоматически реагировать на определенные события в системе, чтобы обеспечить корректное выполнение бизнес-логики без ручного вмешательства."""
            elif "utils" in module_name or "helpers" in module_name:
                return """JTBD:
Я (разработчик) хочу использовать набор вспомогательных функций, чтобы избежать дублирования кода и упростить решение типовых задач."""
            elif "api" in module_name:
                return """JTBD:
Я (разработчик) хочу предоставить программный интерфейс для взаимодействия с системой, чтобы обеспечить интеграцию с другими компонентами и сервисами."""
            elif "model" in module_name:
                return """JTBD:
Я (разработчик) хочу определить структуру данных для работы с бизнес-объектами, чтобы обеспечить согласованность и целостность данных во всей системе."""
            else:
                return f"""JTBD:
Я (разработчик) хочу использовать функциональность модуля {module_name}, чтобы эффективно решать задачи, связанные с этой частью системы."""
        except Exception as e:
            logger.error(f"Ошибка при генерации JTBD для модуля {module_name}: {e}")
            return f"""JTBD:
Я (разработчик) хочу использовать функциональность модуля {module_name}, чтобы решать соответствующие задачи."""
    
    def _generate_class_suggestion(self, file_path: str, class_name: str) -> str:
        """
        Генерирует JTBD-документацию для класса на основе его имени и функциональности.
        
        Args:
            file_path: Путь к файлу с классом
            class_name: Имя класса
            
        Returns:
            str: Предложение документации
        """
        try:
            # Определяем назначение класса по имени
            if "Manager" in class_name:
                return f"""JTBD:
Я (разработчик) хочу управлять {class_name.replace('Manager', '').lower()}, чтобы обеспечить корректную работу системы и контролировать использование ресурсов."""
            elif "Controller" in class_name:
                return f"""JTBD:
Я (разработчик) хочу контролировать {class_name.replace('Controller', '').lower()}, чтобы обеспечить правильную обработку запросов и соблюдение бизнес-логики."""
            elif "Processor" in class_name:
                return f"""JTBD:
Я (разработчик) хочу обрабатывать {class_name.replace('Processor', '').lower()}, чтобы преобразовать данные в требуемый формат и применить необходимую бизнес-логику."""
            elif "Service" in class_name:
                return f"""JTBD:
Я (разработчик) хочу предоставить сервис для работы с {class_name.replace('Service', '').lower()}, чтобы инкапсулировать сложную бизнес-логику и обеспечить повторное использование."""
            else:
                return f"""JTBD:
Я (разработчик) хочу использовать функциональность класса {class_name}, чтобы эффективно решать соответствующие задачи в системе."""
        except Exception as e:
            logger.error(f"Ошибка при генерации JTBD для класса {class_name}: {e}")
            return f"""JTBD:
Я (разработчик) хочу использовать функциональность класса {class_name}, чтобы решать соответствующие задачи."""
    
    def _generate_function_suggestion(self, file_path: str, function_name: str) -> str:
        """
        Генерирует JTBD-документацию для функции на основе её имени.
        
        Args:
            file_path: Путь к файлу с функцией
            function_name: Имя функции
            
        Returns:
            str: Предложение документации
        """
        try:
            # Определяем назначение функции по имени
            if function_name.startswith("get_"):
                item = function_name.replace("get_", "")
                return f"""JTBD:
Я (разработчик) хочу получить {item}, чтобы использовать эти данные в дальнейших операциях."""
            elif function_name.startswith("set_"):
                item = function_name.replace("set_", "")
                return f"""JTBD:
Я (разработчик) хочу установить {item}, чтобы обновить состояние системы или настроить параметры."""
            elif function_name.startswith("create_"):
                item = function_name.replace("create_", "")
                return f"""JTBD:
Я (разработчик) хочу создать {item}, чтобы добавить новый объект в систему и использовать его функциональность."""
            elif function_name.startswith("update_"):
                item = function_name.replace("update_", "")
                return f"""JTBD:
Я (разработчик) хочу обновить {item}, чтобы отразить изменения в состоянии системы и поддерживать актуальность данных."""
            elif function_name.startswith("delete_") or function_name.startswith("remove_"):
                item = function_name.replace("delete_", "").replace("remove_", "")
                return f"""JTBD:
Я (разработчик) хочу удалить {item}, чтобы освободить ресурсы и поддерживать согласованность системы."""
            elif function_name.startswith("validate_") or function_name.startswith("check_"):
                item = function_name.replace("validate_", "").replace("check_", "")
                return f"""JTBD:
Я (разработчик) хочу проверить {item}, чтобы убедиться в корректности данных и предотвратить ошибки."""
            elif function_name.startswith("process_"):
                item = function_name.replace("process_", "")
                return f"""JTBD:
Я (разработчик) хочу обработать {item}, чтобы выполнить необходимые преобразования и применить бизнес-логику."""
            else:
                return f"""JTBD:
Я (разработчик) хочу использовать функцию {function_name}, чтобы эффективно выполнить соответствующую операцию."""
        except Exception as e:
            logger.error(f"Ошибка при генерации JTBD для функции {function_name}: {e}")
            return f"""JTBD:
Я (разработчик) хочу использовать функцию {function_name}, чтобы выполнить соответствующую операцию."""

# Глобальный экземпляр анализатора
_analyzer: Optional[JTBDDocumentationAnalyzer] = None

def get_analyzer() -> JTBDDocumentationAnalyzer:
    """
    JTBD:
    Я (разработчик) хочу получить единый экземпляр анализатора документации, чтобы использовать его в разных частях системы без создания дублей.
    
    Возвращает глобальный экземпляр анализатора JTBD-документации.
    
    Returns:
        JTBDDocumentationAnalyzer: Экземпляр анализатора
    """
    global _analyzer
    if _analyzer is None:
        _analyzer = JTBDDocumentationAnalyzer()
    return _analyzer

def analyze_file(file_path: str) -> Dict[str, Any]:
    """
    JTBD:
    Я (разработчик) хочу проанализировать наличие JTBD-документации в отдельном файле, чтобы определить необходимость её добавления.
    
    Анализирует файл на наличие JTBD-документации.
    
    Args:
        file_path: Путь к файлу для анализа
        
    Returns:
        Dict[str, Any]: Результаты анализа
    """
    analyzer = get_analyzer()
    return analyzer.analyze_file(file_path)

def generate_jtbd_suggestions(file_analysis: Dict[str, Any]) -> Dict[str, str]:
    """
    JTBD:
    Я (разработчик) хочу получить готовые предложения JTBD-документации, чтобы быстро добавить их к существующему коду.
    
    Генерирует предложения JTBD-документации на основе анализа файла.
    
    Args:
        file_analysis: Результаты анализа файла
        
    Returns:
        Dict[str, str]: Предложения по документации
    """
    analyzer = get_analyzer()
    return analyzer.generate_jtbd_suggestions(file_analysis)

def analyze_directory(directory_path: str, exclude_dirs: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    JTBD:
    Я (разработчик) хочу проанализировать JTBD-документацию во всем проекте, чтобы оценить текущее состояние и выявить места для улучшения.
    
    Анализирует Python-файлы в указанной директории и её поддиректориях.
    
    Args:
        directory_path: Путь к директории для анализа
        exclude_dirs: Список директорий для исключения
        
    Returns:
        Dict[str, Any]: Результаты анализа
    """
    analyzer = get_analyzer()
    return analyzer.analyze_directory(directory_path, exclude_dirs)