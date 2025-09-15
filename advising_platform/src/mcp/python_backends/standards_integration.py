"""
Standards Integration для MCP сервера - мост между MCP и DuckDB системой стандартов.

Обеспечивает полное покрытие аспектов стандартов через MCP триггеры.
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

# Добавляем путь к системе стандартов
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from standards_system import UnifiedStandardsSystem
    STANDARDS_AVAILABLE = True
except ImportError:
    STANDARDS_AVAILABLE = False

class StandardsIntegration:
    """Интеграция MCP сервера с системой стандартов"""
    
    def __init__(self):
        """Инициализация интеграции"""
        self.standards_system = None
        self.operation_log = []
        
        if STANDARDS_AVAILABLE:
            try:
                self.standards_system = UnifiedStandardsSystem()
                self._log_operation("standards_integration_init", {}, {"success": True}, 0)
            except Exception as e:
                self._log_operation("standards_integration_init", {}, {"error": str(e)}, 0)
        else:
            self._log_operation("standards_integration_init", {}, {"error": "Standards system not available"}, 0)
    
    def load_standards_trigger(self) -> Dict[str, Any]:
        """
        Триггер загрузки стандартов.
        Автоматическое обнаружение и загрузка стандартов в DuckDB.
        """
        start_time = time.time()
        
        result = {
            "trigger": "load_standards",
            "success": False,
            "standards_loaded": 0,
            "dependencies_found": 0,
            "errors": []
        }
        
        if not self.standards_system:
            result["errors"].append("Standards system not available")
            return result
        
        try:
            # Загрузка стандартов
            ecosystem = self.standards_system.analyze_ecosystem()
            
            if ecosystem["success"]:
                result.update({
                    "success": True,
                    "standards_loaded": ecosystem["overview"]["total_standards"],
                    "categories": ecosystem["overview"]["categories"],
                    "jtbd_coverage": ecosystem["overview"]["jtbd_coverage"],
                    "connectivity": ecosystem["dependency_analysis"]["connectivity_ratio"]
                })
                
                # Проверяем качество стандартов
                compliance = self.standards_system.validate_compliance()
                if compliance["success"]:
                    result["compliance_score"] = compliance["compliance_score"]
                    result["compliance_issues"] = len(compliance["issues"])
            
        except Exception as e:
            result["errors"].append(str(e))
        
        duration = (time.time() - start_time) * 1000
        self._log_operation("load_standards_trigger", {}, result, duration)
        
        return result
    
    def standards_aware_hypothesis(self, hypothesis_text: str) -> Dict[str, Any]:
        """
        Триггер формирования гипотезы с учетом стандартов.
        Анализирует связанные стандарты и проверяет соответствие.
        """
        start_time = time.time()
        
        result = {
            "trigger": "standards_aware_hypothesis",
            "hypothesis": hypothesis_text,
            "success": False,
            "related_standards": [],
            "compliance_check": {},
            "recommendations": []
        }
        
        if not self.standards_system:
            result["error"] = "Standards system not available"
            return result
        
        try:
            # Поиск связанных стандартов
            search_result = self.standards_system.search_standards_semantic(
                hypothesis_text, 
                {"has_jtbd": True}
            )
            
            if search_result["success"]:
                result["related_standards"] = [
                    {
                        "name": std["name"],
                        "category": std["category"],
                        "complexity": std["complexity_score"],
                        "relevance": "high" if "hypothesis" in std["content"].lower() else "medium"
                    }
                    for std in search_result["results"][:5]
                ]
                
                # Проверка соответствия стандартам гипотез
                hypothesis_standards = [std for std in search_result["results"] 
                                      if "hypothesis" in std["name"].lower() or "гипотез" in std["content"].lower()]
                
                if hypothesis_standards:
                    result["compliance_check"] = {
                        "found_hypothesis_standards": len(hypothesis_standards),
                        "compliance_status": "compliant" if len(hypothesis_standards) > 0 else "needs_review"
                    }
                
                # Генерация рекомендаций
                if result["related_standards"]:
                    result["recommendations"].append("Рассмотрите связанные стандарты при разработке гипотезы")
                
                if not hypothesis_standards:
                    result["recommendations"].append("Добавьте ссылки на стандарты формирования гипотез")
                
                result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
        
        duration = (time.time() - start_time) * 1000
        self._log_operation("standards_aware_hypothesis", {"hypothesis_length": len(hypothesis_text)}, result, duration)
        
        return result
    
    def jtbd_standards_validation(self, jtbd_content: str) -> Dict[str, Any]:
        """
        Триггер валидации JTBD по стандартам.
        Проверяет соответствие jtbd.standard.md и дополняет недостающие элементы.
        """
        start_time = time.time()
        
        result = {
            "trigger": "jtbd_standards_validation",
            "success": False,
            "validation_results": {},
            "missing_elements": [],
            "recommendations": []
        }
        
        if not self.standards_system:
            result["error"] = "Standards system not available"
            return result
        
        try:
            # Поиск JTBD стандарта
            jtbd_standard = self.standards_system.search_standards_semantic("jtbd standard")
            
            if jtbd_standard["success"] and jtbd_standard["results"]:
                standard = jtbd_standard["results"][0]
                
                # Анализ структуры JTBD
                validation = self._validate_jtbd_structure(jtbd_content, standard["content"])
                result["validation_results"] = validation
                
                # Проверка обязательных элементов
                required_elements = ["когда", "роль", "хочет", "чтобы"]
                missing = []
                
                for element in required_elements:
                    if element.lower() not in jtbd_content.lower():
                        missing.append(element)
                
                result["missing_elements"] = missing
                
                # Рекомендации
                if missing:
                    result["recommendations"].append(f"Добавьте недостающие элементы: {', '.join(missing)}")
                
                if validation["completeness_score"] < 0.8:
                    result["recommendations"].append("Улучшите детализацию JTBD сценариев")
                
                result["success"] = True
            else:
                result["error"] = "JTBD standard not found"
        
        except Exception as e:
            result["error"] = str(e)
        
        duration = (time.time() - start_time) * 1000
        self._log_operation("jtbd_standards_validation", {"content_length": len(jtbd_content)}, result, duration)
        
        return result
    
    def test_standards_enforcement(self, test_content: str) -> Dict[str, Any]:
        """
        Триггер применения стандартов тестирования.
        Проверяет соответствие test.standard.md и TDD пирамиде.
        """
        start_time = time.time()
        
        result = {
            "trigger": "test_standards_enforcement",
            "success": False,
            "tdd_pyramid_check": {},
            "test_standards_compliance": {},
            "recommendations": []
        }
        
        if not self.standards_system:
            result["error"] = "Standards system not available"
            return result
        
        try:
            # Поиск стандартов тестирования
            test_standards = self.standards_system.search_standards_semantic("test standard tdd")
            
            if test_standards["success"]:
                # Анализ TDD пирамиды
                pyramid_analysis = self._analyze_tdd_pyramid(test_content)
                result["tdd_pyramid_check"] = pyramid_analysis
                
                # Проверка соответствия стандартам
                compliance = self._check_test_compliance(test_content, test_standards["results"])
                result["test_standards_compliance"] = compliance
                
                # Рекомендации
                if pyramid_analysis["missing_levels"]:
                    result["recommendations"].append(f"Добавьте тесты уровня: {', '.join(pyramid_analysis['missing_levels'])}")
                
                if compliance["coverage_score"] < 0.7:
                    result["recommendations"].append("Улучшите покрытие тестовых стандартов")
                
                result["success"] = True
        
        except Exception as e:
            result["error"] = str(e)
        
        duration = (time.time() - start_time) * 1000
        self._log_operation("test_standards_enforcement", {"content_length": len(test_content)}, result, duration)
        
        return result
    
    def standards_informed_rca(self, incident_description: str) -> Dict[str, Any]:
        """
        Триггер RCA с использованием стандартов.
        Ищет похожие инциденты и применяет best practices из стандартов.
        """
        start_time = time.time()
        
        result = {
            "trigger": "standards_informed_rca",
            "success": False,
            "similar_cases": [],
            "applicable_standards": [],
            "root_cause_analysis": {},
            "recommendations": []
        }
        
        if not self.standards_system:
            result["error"] = "Standards system not available"
            return result
        
        try:
            # Поиск похожих случаев в стандартах
            similar_search = self.standards_system.search_standards_semantic(incident_description)
            
            if similar_search["success"]:
                result["similar_cases"] = [
                    {
                        "standard": std["name"],
                        "category": std["category"],
                        "relevance": "high" if any(word in std["content"].lower() 
                                                 for word in ["incident", "problem", "issue", "error"]) else "medium"
                    }
                    for std in similar_search["results"][:3]
                ]
                
                # Поиск RCA стандартов
                rca_standards = self.standards_system.search_standards_semantic("root cause 5 why analysis")
                
                if rca_standards["success"]:
                    result["applicable_standards"] = [
                        {
                            "name": std["name"],
                            "category": std["category"]
                        }
                        for std in rca_standards["results"][:2]
                    ]
                
                # Рекомендации на основе стандартов
                result["recommendations"] = [
                    "Примените методику 5 Почему согласно стандартам",
                    "Проверьте похожие инциденты в найденных стандартах",
                    "Документируйте выводы для обновления стандартов"
                ]
                
                result["success"] = True
        
        except Exception as e:
            result["error"] = str(e)
        
        duration = (time.time() - start_time) * 1000
        self._log_operation("standards_informed_rca", {"description_length": len(incident_description)}, result, duration)
        
        return result
    
    def standards_quality_check(self) -> Dict[str, Any]:
        """
        Триггер мониторинга качества стандартов.
        Выявляет устаревшие, изолированные стандарты и дает рекомендации.
        """
        start_time = time.time()
        
        result = {
            "trigger": "standards_quality_check",
            "success": False,
            "quality_metrics": {},
            "issues_found": [],
            "recommendations": []
        }
        
        if not self.standards_system:
            result["error"] = "Standards system not available"
            return result
        
        try:
            # Анализ экосистемы стандартов
            ecosystem = self.standards_system.analyze_ecosystem()
            
            if ecosystem["success"]:
                result["quality_metrics"] = {
                    "total_standards": ecosystem["overview"]["total_standards"],
                    "avg_complexity": ecosystem["overview"]["avg_complexity"],
                    "jtbd_coverage": ecosystem["overview"]["jtbd_coverage"],
                    "connectivity_ratio": ecosystem["dependency_analysis"]["connectivity_ratio"]
                }
                
                # Проверка соответствия
                compliance = self.standards_system.validate_compliance()
                if compliance["success"]:
                    result["quality_metrics"]["compliance_score"] = compliance["compliance_score"]
                    
                    # Анализ проблем
                    if compliance["compliance_score"] < 80:
                        result["issues_found"].append("Низкая оценка соответствия стандартам")
                    
                    if len(compliance["issues"]) > 5:
                        result["issues_found"].append("Множественные проблемы соответствия")
                
                # Рекомендации
                jtbd_coverage = float(ecosystem["overview"]["jtbd_coverage"].replace('%', ''))
                if jtbd_coverage < 70:
                    result["recommendations"].append("Улучшите JTBD покрытие стандартов")
                
                connectivity = float(ecosystem["dependency_analysis"]["connectivity_ratio"].replace('%', ''))
                if connectivity < 50:
                    result["recommendations"].append("Увеличьте связанность между стандартами")
                
                if ecosystem["overview"]["avg_complexity"] < 3:
                    result["recommendations"].append("Углубите детализацию стандартов")
                
                result["success"] = True
        
        except Exception as e:
            result["error"] = str(e)
        
        duration = (time.time() - start_time) * 1000
        self._log_operation("standards_quality_check", {}, result, duration)
        
        return result
    
    def _validate_jtbd_structure(self, jtbd_content: str, standard_content: str) -> Dict[str, Any]:
        """Валидация структуры JTBD"""
        
        # Простая проверка структуры
        has_when = "когда" in jtbd_content.lower() or "when" in jtbd_content.lower()
        has_role = "роль" in jtbd_content.lower() or "role" in jtbd_content.lower()
        has_want = "хочет" in jtbd_content.lower() or "want" in jtbd_content.lower()
        has_so_that = "чтобы" in jtbd_content.lower() or "so that" in jtbd_content.lower()
        
        elements_present = sum([has_when, has_role, has_want, has_so_that])
        completeness_score = elements_present / 4.0
        
        return {
            "has_when": has_when,
            "has_role": has_role,
            "has_want": has_want,
            "has_so_that": has_so_that,
            "completeness_score": completeness_score,
            "structure_quality": "good" if completeness_score >= 0.75 else "needs_improvement"
        }
    
    def _analyze_tdd_pyramid(self, test_content: str) -> Dict[str, Any]:
        """Анализ TDD пирамиды"""
        
        has_unit = "unit" in test_content.lower() or "test_" in test_content.lower()
        has_integration = "integration" in test_content.lower() or "интеграционн" in test_content.lower()
        has_e2e = "e2e" in test_content.lower() or "end-to-end" in test_content.lower()
        
        present_levels = []
        missing_levels = []
        
        levels = {
            "unit": has_unit,
            "integration": has_integration,
            "e2e": has_e2e
        }
        
        for level, present in levels.items():
            if present:
                present_levels.append(level)
            else:
                missing_levels.append(level)
        
        return {
            "present_levels": present_levels,
            "missing_levels": missing_levels,
            "pyramid_completeness": len(present_levels) / 3.0,
            "pyramid_quality": "complete" if len(present_levels) == 3 else "incomplete"
        }
    
    def _check_test_compliance(self, test_content: str, test_standards: List[Dict]) -> Dict[str, Any]:
        """Проверка соответствия тестовым стандартам"""
        
        compliance_indicators = [
            "red.*green.*blue",
            "tdd",
            "assert",
            "test.*fail",
            "setup.*teardown"
        ]
        
        matches = 0
        for indicator in compliance_indicators:
            if indicator.lower() in test_content.lower():
                matches += 1
        
        coverage_score = matches / len(compliance_indicators)
        
        return {
            "compliance_indicators_found": matches,
            "total_indicators": len(compliance_indicators),
            "coverage_score": coverage_score,
            "compliance_level": "high" if coverage_score >= 0.7 else "medium" if coverage_score >= 0.4 else "low"
        }
    
    def _log_operation(self, operation: str, params: Dict, result: Dict, duration_ms: float):
        """Логирование операций интеграции"""
        log_entry = {
            "timestamp": time.time(),
            "operation": operation,
            "params": params,
            "success": result.get("success", False),
            "duration_ms": duration_ms
        }
        
        self.operation_log.append(log_entry)
        
        # Ограничиваем размер лога
        if len(self.operation_log) > 50:
            self.operation_log = self.operation_log[-25:]
    
    def get_integration_report(self) -> Dict[str, Any]:
        """Отчет об интеграции стандартов с MCP"""
        
        if not self.operation_log:
            return {"error": "No operations logged"}
        
        operations_by_type = {}
        for op in self.operation_log:
            op_type = op["operation"]
            if op_type not in operations_by_type:
                operations_by_type[op_type] = []
            operations_by_type[op_type].append(op)
        
        report = {
            "integration_status": "active" if self.standards_system else "inactive",
            "total_operations": len(self.operation_log),
            "success_rate": sum(1 for op in self.operation_log if op["success"]) / len(self.operation_log) * 100,
            "operations_summary": {}
        }
        
        for op_type, ops in operations_by_type.items():
            durations = [op["duration_ms"] for op in ops]
            report["operations_summary"][op_type] = {
                "count": len(ops),
                "success_rate": sum(1 for op in ops if op["success"]) / len(ops) * 100,
                "avg_duration_ms": sum(durations) / len(durations) if durations else 0
            }
        
        return report
    
    def close(self):
        """Закрытие интеграции"""
        if self.standards_system:
            self.standards_system.close()

def test_standards_integration():
    """Тест интеграции стандартов с MCP"""
    print("🧪 Тест Standards Integration для MCP")
    
    integration = StandardsIntegration()
    
    if not integration.standards_system:
        print("❌ Standards system недоступен")
        return
    
    # Тест загрузки стандартов
    print("\n📥 Тест загрузки стандартов...")
    load_result = integration.load_standards_trigger()
    if load_result["success"]:
        print(f"   ✅ Загружено стандартов: {load_result['standards_loaded']}")
        print(f"   📊 JTBD покрытие: {load_result.get('jtbd_coverage', 'N/A')}")
    
    # Тест анализа гипотезы
    print("\n🎯 Тест анализа гипотезы...")
    hypothesis_test = "Если реализовать JTBD сценарии с TDD подходом, то получим лучшее качество"
    hypothesis_result = integration.standards_aware_hypothesis(hypothesis_test)
    if hypothesis_result["success"]:
        print(f"   ✅ Найдено связанных стандартов: {len(hypothesis_result['related_standards'])}")
        print(f"   📋 Рекомендаций: {len(hypothesis_result['recommendations'])}")
    
    # Тест JTBD валидации
    print("\n📝 Тест JTBD валидации...")
    jtbd_test = "Когда разработчик роль хочет создать тесты чтобы обеспечить качество"
    jtbd_result = integration.jtbd_standards_validation(jtbd_test)
    if jtbd_result["success"]:
        print(f"   ✅ Отсутствующих элементов: {len(jtbd_result['missing_elements'])}")
        print(f"   📊 Валидация: {jtbd_result['validation_results']['structure_quality']}")
    
    # Тест качества стандартов
    print("\n🔍 Тест мониторинга качества...")
    quality_result = integration.standards_quality_check()
    if quality_result["success"]:
        print(f"   ✅ Оценка соответствия: {quality_result['quality_metrics'].get('compliance_score', 'N/A')}%")
        print(f"   🔧 Проблем найдено: {len(quality_result['issues_found'])}")
    
    # Отчет интеграции
    print("\n📊 Отчет интеграции...")
    report = integration.get_integration_report()
    print(f"   📈 Статус: {report['integration_status']}")
    print(f"   ⚡ Успешность: {report['success_rate']:.1f}%")
    print(f"   🔄 Операций: {report['total_operations']}")
    
    integration.close()
    print("\n✅ Standards Integration готова для MCP!")

if __name__ == "__main__":
    test_standards_integration()