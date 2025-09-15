#!/usr/bin/env python3
"""
Модуль автоматической проверки соответствия стандартов Registry Standard.

Интегрируется с триггерами создания, обновления и архивирования стандартов
для обеспечения целостности системы стандартов.

Автор: AI Assistant
Дата: 22 May 2025
"""

import os
import re
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class RegistryComplianceChecker:
    """
    Класс для проверки соответствия стандартов требованиям Registry Standard.
    """
    
    def __init__(self, standards_dir: str = "[standards .md]"):
        self.standards_dir = standards_dir
        self.registry_structure = self._load_registry_structure()
        
    def _load_registry_structure(self) -> Dict[str, Any]:
        """
        Загружает официальную структуру из Registry Standard.
        
        Returns:
            Dict: Структура папок согласно Registry Standard
        """
        return {
            "folders": {
                "0. core standards": {
                    "description": "Основополагающие стандарты",
                    "priority": "Высший",
                    "expected_count": 6
                },
                "1. process · goalmap · task · incidents · tickets · qa": {
                    "description": "Обязательные рабочие стандарты",
                    "priority": "Высокий",
                    "expected_count": 6
                },
                "2. projects · context · next actions": {
                    "description": "Проектные стандарты и контекст",
                    "priority": "Средний",
                    "expected_count": 4
                },
                "3. scenarium · jtbd · hipothises · offering · tone": {
                    "description": "Руководства по контенту и сценариям",
                    "priority": "Средний",
                    "expected_count": 8
                },
                "4. dev · design · qa": {
                    "description": "Объединенные стандарты разработки, дизайна и QA",
                    "priority": "Средний",
                    "expected_count": 18
                },
                "6. advising · review · supervising": {
                    "description": "Стандарты проверки и мониторинга",
                    "priority": "Средний",
                    "expected_count": 7
                },
                "8. auto · n8n": {
                    "description": "Стандарты автоматизации и интеграций",
                    "priority": "Низкий",
                    "expected_count": 1
                },
                "9. development · documentation": {
                    "description": "Стандарты разработки и документирования",
                    "priority": "Низкий",
                    "expected_count": 0
                }
            }
        }
    
    def check_folder_structure(self) -> Dict[str, Any]:
        """
        Проверяет соответствие структуры папок Registry Standard.
        
        Returns:
            Dict: Результаты проверки структуры
        """
        results = {
            "compliant": True,
            "missing_folders": [],
            "unexpected_folders": [],
            "folder_counts": {},
            "errors": []
        }
        
        try:
            if not os.path.exists(self.standards_dir):
                results["compliant"] = False
                results["errors"].append(f"Директория стандартов не найдена: {self.standards_dir}")
                return results
            
            # Получаем список фактических папок
            actual_folders = []
            for item in os.listdir(self.standards_dir):
                item_path = os.path.join(self.standards_dir, item)
                if os.path.isdir(item_path) and not item.startswith('.'):
                    actual_folders.append(item)
            
            expected_folders = set(self.registry_structure["folders"].keys())
            actual_folders_set = set(actual_folders)
            
            # Проверяем отсутствующие папки
            results["missing_folders"] = list(expected_folders - actual_folders_set)
            
            # Проверяем неожиданные папки
            results["unexpected_folders"] = list(actual_folders_set - expected_folders)
            
            # Считаем файлы в каждой папке
            for folder in actual_folders:
                folder_path = os.path.join(self.standards_dir, folder)
                md_files = [f for f in os.listdir(folder_path) if f.endswith('.md')]
                results["folder_counts"][folder] = len(md_files)
            
            # Определяем общее соответствие
            if results["missing_folders"] or results["unexpected_folders"]:
                results["compliant"] = False
                
            logger.info(f"Проверка структуры завершена. Соответствие: {results['compliant']}")
            
        except Exception as e:
            results["compliant"] = False
            results["errors"].append(f"Ошибка при проверке структуры: {e}")
            logger.error(f"Ошибка при проверке структуры папок: {e}")
        
        return results
    
    def validate_standard_placement(self, file_path: str, content: str) -> Tuple[bool, List[str]]:
        """
        Проверяет правильность размещения стандарта в структуре папок.
        
        Args:
            file_path: Путь к файлу стандарта
            content: Содержимое стандарта
            
        Returns:
            Tuple[bool, List[str]]: (соответствует, список ошибок)
        """
        errors = []
        
        try:
            # Определяем папку стандарта
            rel_path = os.path.relpath(file_path, self.standards_dir)
            folder = os.path.dirname(rel_path)
            
            if not folder:
                folder = "root"
            
            # Проверяем, что папка существует в Registry
            if folder not in self.registry_structure["folders"]:
                errors.append(f"Стандарт размещен в неизвестной папке: {folder}")
                return False, errors
            
            # Извлекаем тип стандарта из содержимого
            standard_type = self._extract_standard_type(content)
            folder_info = self.registry_structure["folders"][folder]
            
            # Проверяем соответствие типа стандарта папке
            if not self._is_appropriate_folder(standard_type, folder, folder_info):
                errors.append(f"Тип стандарта '{standard_type}' не соответствует папке '{folder}'")
                return False, errors
            
            logger.info(f"Стандарт {file_path} правильно размещен в папке {folder}")
            return True, []
            
        except Exception as e:
            errors.append(f"Ошибка при проверке размещения: {e}")
            logger.error(f"Ошибка при проверке размещения стандарта {file_path}: {e}")
            return False, errors
    
    def _extract_standard_type(self, content: str) -> str:
        """
        Извлекает тип стандарта из его содержимого.
        
        Args:
            content: Содержимое стандарта
            
        Returns:
            str: Тип стандарта
        """
        # Проверяем заголовок для определения типа
        lines = content.split('\n')
        title = ""
        
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip().lower()
                break
        
        # Определяем тип на основе заголовка и содержимого
        content_lower = content.lower()
        
        if any(keyword in title for keyword in ['task master', 'registry', 'audit', 'meta']):
            return "core"
        elif any(keyword in title for keyword in ['incident', 'task', 'ticket', 'qa', 'goal']):
            return "process"
        elif any(keyword in title for keyword in ['project', 'context', 'release']):
            return "project"
        elif any(keyword in title for keyword in ['jtbd', 'scenarium', 'hypothesis', 'tone']):
            return "content"
        elif any(keyword in title for keyword in ['dev', 'design', 'tdd', 'code', 'interface']):
            return "development"
        elif any(keyword in title for keyword in ['heroes', 'review', 'advising']):
            return "review"
        elif any(keyword in title for keyword in ['auto', 'n8n', 'workflow']):
            return "automation"
        else:
            return "unknown"
    
    def _is_appropriate_folder(self, standard_type: str, folder: str, folder_info: Dict) -> bool:
        """
        Проверяет соответствие типа стандарта папке.
        
        Args:
            standard_type: Тип стандарта
            folder: Имя папки
            folder_info: Информация о папке
            
        Returns:
            bool: True, если стандарт размещен правильно
        """
        type_to_folder = {
            "core": "0. core standards",
            "process": "1. process · goalmap · task · incidents · tickets · qa",
            "project": "2. projects · context · next actions",
            "content": "3. scenarium · jtbd · hipothises · offering · tone",
            "development": "4. dev · design · qa",
            "review": "6. advising · review · supervising",
            "automation": "8. auto · n8n"
        }
        
        expected_folder = type_to_folder.get(standard_type)
        return expected_folder == folder or standard_type == "unknown"
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """
        Генерирует полный отчет о соответствии Registry Standard.
        
        Returns:
            Dict: Детальный отчет о соответствии
        """
        report = {
            "timestamp": "22 May 2025, 19:15 CET",
            "overall_compliance": True,
            "structure_check": self.check_folder_structure(),
            "standards_validation": [],
            "recommendations": []
        }
        
        try:
            # Проверяем каждый стандарт в каждой папке
            for folder in self.registry_structure["folders"]:
                folder_path = os.path.join(self.standards_dir, folder)
                
                if not os.path.exists(folder_path):
                    continue
                
                for file in os.listdir(folder_path):
                    if file.endswith('.md'):
                        file_path = os.path.join(folder_path, file)
                        
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            is_valid, errors = self.validate_standard_placement(file_path, content)
                            
                            validation_result = {
                                "file": file,
                                "folder": folder,
                                "valid": is_valid,
                                "errors": errors
                            }
                            
                            report["standards_validation"].append(validation_result)
                            
                            if not is_valid:
                                report["overall_compliance"] = False
                                
                        except Exception as e:
                            logger.error(f"Ошибка при проверке файла {file_path}: {e}")
            
            # Генерируем рекомендации
            report["recommendations"] = self._generate_recommendations(report)
            
        except Exception as e:
            report["overall_compliance"] = False
            report["error"] = f"Ошибка при генерации отчета: {e}"
            logger.error(f"Ошибка при генерации отчета соответствия: {e}")
        
        return report
    
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """
        Генерирует рекомендации на основе результатов проверки.
        
        Args:
            report: Отчет о проверке
            
        Returns:
            List[str]: Список рекомендаций
        """
        recommendations = []
        
        # Рекомендации по структуре папок
        if report["structure_check"]["missing_folders"]:
            recommendations.append(
                f"Создать отсутствующие папки: {', '.join(report['structure_check']['missing_folders'])}"
            )
        
        if report["structure_check"]["unexpected_folders"]:
            recommendations.append(
                f"Проверить необходимость папок: {', '.join(report['structure_check']['unexpected_folders'])}"
            )
        
        # Рекомендации по стандартам
        invalid_standards = [s for s in report["standards_validation"] if not s["valid"]]
        if invalid_standards:
            recommendations.append(f"Исправить размещение {len(invalid_standards)} стандартов")
        
        # Общие рекомендации
        if not report["overall_compliance"]:
            recommendations.append("Обновить Registry Standard для отражения текущей структуры")
            recommendations.append("Добавить автоматическую проверку соответствия в триггеры")
        
        return recommendations

def check_registry_compliance_on_trigger(file_path: str, operation: str = "create") -> bool:
    """
    JTBD: Я (триггер системы) хочу автоматически проверять соответствие Registry Standard
    при создании/обновлении стандартов, чтобы поддерживать целостность системы.
    
    Функция для интеграции с триггерами создания/обновления стандартов.
    
    Args:
        file_path: Путь к файлу стандарта
        operation: Тип операции (create, update, archive)
        
    Returns:
        bool: True, если стандарт соответствует Registry
    """
    try:
        checker = RegistryComplianceChecker()
        
        if not os.path.exists(file_path):
            logger.warning(f"Файл не найден для проверки: {file_path}")
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        is_valid, errors = checker.validate_standard_placement(file_path, content)
        
        if not is_valid:
            logger.warning(f"Стандарт {file_path} не соответствует Registry Standard:")
            for error in errors:
                logger.warning(f"  - {error}")
        else:
            logger.info(f"Стандарт {file_path} соответствует Registry Standard")
        
        return is_valid
        
    except Exception as e:
        logger.error(f"Ошибка при проверке соответствия Registry для {file_path}: {e}")
        return False

def main():
    """
    Основная функция для запуска проверки соответствия.
    """
    checker = RegistryComplianceChecker()
    report = checker.generate_compliance_report()
    
    print("=== ОТЧЕТ О СООТВЕТСТВИИ REGISTRY STANDARD ===")
    print(f"Время: {report['timestamp']}")
    print(f"Общее соответствие: {'✅ ДА' if report['overall_compliance'] else '❌ НЕТ'}")
    print()
    
    # Структура папок
    structure = report["structure_check"]
    print("📁 СТРУКТУРА ПАПОК:")
    print(f"Соответствие: {'✅' if structure['compliant'] else '❌'}")
    
    if structure["missing_folders"]:
        print(f"Отсутствующие папки: {', '.join(structure['missing_folders'])}")
    
    if structure["unexpected_folders"]:
        print(f"Неожиданные папки: {', '.join(structure['unexpected_folders'])}")
    
    print()
    
    # Рекомендации
    if report["recommendations"]:
        print("💡 РЕКОМЕНДАЦИИ:")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"{i}. {rec}")

if __name__ == "__main__":
    main()