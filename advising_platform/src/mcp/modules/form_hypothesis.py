#!/usr/bin/env python3
"""
MCP Module: form_hypothesis

JTBD: Я хочу формировать и валидировать гипотезы,
чтобы обеспечить структурированный подход к экспериментам.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import sys
import os

# Добавляем путь к модулям
sys.path.insert(0, '/home/runner/workspace')

# Импорт интеграции стандартов
try:
    sys.path.append(str(Path(__file__).parent.parent / "python_backends"))
    from standards_integration import StandardsIntegration
    STANDARDS_AVAILABLE = True
except ImportError:
    STANDARDS_AVAILABLE = False

class FormHypothesis:
    """Класс для формирования и обработки гипотез с интеграцией стандартов."""
    
    def __init__(self):
        self.schema_path = Path(__file__).parent.parent / "schemas" / "hypothesis.schema.md"
        self.output_dir = Path(__file__).parent.parent / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        # Инициализация интеграции стандартов
        self.standards_integration = None
        if STANDARDS_AVAILABLE:
            try:
                self.standards_integration = StandardsIntegration()
            except Exception as e:
                print(f"Standards integration unavailable: {e}")
    
    def process(self, raw_input: str) -> Dict[str, Any]:
        """Обрабатывает сырой ввод и возвращает структурированную гипотезу с анализом стандартов."""
        # Парсим текст
        parsed_data = parse_hypothesis(raw_input)
        
        # Генерируем ID
        parsed_data["id"] = generate_hypothesis_id()
        
        # Добавляем метаданные
        parsed_data["created_at"] = datetime.now().isoformat()
        parsed_data["status"] = "draft"
        
        # НОВОЕ: Анализ стандартов для гипотезы
        if self.standards_integration:
            try:
                standards_analysis = self.standards_integration.standards_aware_hypothesis(raw_input)
                if standards_analysis["success"]:
                    parsed_data["standards_analysis"] = {
                        "related_standards": standards_analysis["related_standards"],
                        "compliance_check": standards_analysis["compliance_check"],
                        "recommendations": standards_analysis["recommendations"]
                    }
                    # Логируем успешную интеграцию стандартов
                    print(f"✅ Standards analysis completed: {len(standards_analysis['related_standards'])} related standards found")
                else:
                    parsed_data["standards_analysis"] = {"error": standards_analysis.get("error", "Unknown error")}
            except Exception as e:
                parsed_data["standards_analysis"] = {"error": str(e)}
        
        # Валидируем
        if not validate_hypothesis(parsed_data):
            raise ValueError("Hypothesis validation failed")
        
        # Сохраняем
        output_path = self.output_dir / f"{parsed_data['id']}.json"
        save_hypothesis(parsed_data, output_path)
        
        return parsed_data

def parse_hypothesis(text: str) -> Dict[str, Any]:
    """Парсит текст гипотезы в структурированный формат."""
    result = {}
    
    # Извлекаем основные компоненты
    lines = text.strip().split('\n')
    
    # Ищем паттерны
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Гипотеза/Title
        if line.lower().startswith('гипотеза:') or line.lower().startswith('если'):
            result['title'] = line.replace('Гипотеза:', '').replace('гипотеза:', '').strip()
            result['description'] = line.strip()
        
        # Output
        elif line.lower().startswith('output:'):
            result['output'] = line.replace('Output:', '').replace('output:', '').strip()
        
        # Outcome
        elif line.lower().startswith('outcome:'):
            result['outcome'] = line.replace('Outcome:', '').replace('outcome:', '').strip()
        
        # Falsifiable if
        elif line.lower().startswith('falsifiable if:'):
            result['falsifiable_if'] = line.replace('Falsifiable if:', '').replace('falsifiable if:', '').strip()
        
        # Metrics
        elif line.lower().startswith('metrics:'):
            metrics_text = line.replace('Metrics:', '').replace('metrics:', '').strip()
            result['metrics'] = [m.strip() for m in metrics_text.split(',')]
    
    # Извлекаем JTBD если есть
    jtbd = extract_jtbd(text)
    if jtbd:
        result['jtbd'] = jtbd
    
    # Устанавливаем значения по умолчанию
    if 'title' not in result:
        result['title'] = "Untitled Hypothesis"
    if 'description' not in result:
        result['description'] = text[:200] + "..." if len(text) > 200 else text
    if 'metrics' not in result:
        result['metrics'] = []
    
    return result

def validate_hypothesis(hypothesis: Dict[str, Any]) -> bool:
    """Валидирует гипотезу по схеме."""
    required_fields = ['hypothesis', 'output', 'outcome', 'falsifiable_if']
    
    # Проверяем обязательные поля
    for field in required_fields:
        if field not in hypothesis:
            return False
        if not hypothesis[field]:
            return False
    
    return True

def generate_hypothesis_id() -> str:
    """Генерирует уникальный ID для гипотезы."""
    today = datetime.now().strftime('%Y%m%d')
    
    # Микросекунды для уникальности
    timestamp_part = datetime.now().strftime('%H%M%S%f')[:9]
    
    return f"H{today}_{timestamp_part}"

def save_hypothesis(hypothesis: Dict[str, Any], output_path: Path) -> bool:
    """Сохраняет гипотезу в файл."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(hypothesis, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving hypothesis: {e}")
        return False

def save_hypothesis_json(hypothesis_data: Dict[str, Any], output_path: str) -> bool:
    """Алиас для сохранения гипотезы - для совместимости с тестами."""
    return save_hypothesis(hypothesis_data, Path(output_path))

def parse_hypothesis_text(text: str) -> Dict[str, Any]:
    """Парсинг гипотезы из текста - для совместимости с тестами."""
    result = parse_hypothesis(text)
    
    # Переименовываем поля для совместимости
    if 'title' in result:
        result['hypothesis'] = result['title']
    if 'description' in result and 'hypothesis' not in result:
        result['hypothesis'] = result['description']
    
    # Добавляем недостающие поля
    result['id'] = generate_hypothesis_id()
    result['timestamp'] = datetime.now().isoformat()
    
    return result

def form_hypothesis_command(request: Dict[str, Any]) -> Dict[str, Any]:
    """MCP команда для формирования гипотезы."""
    start_time = datetime.now()
    
    try:
        # Импорт Protocol Completion
        try:
            from advising_platform.src.mcp.protocol_completion import report_mcp_progress
        except ImportError:
            def report_mcp_progress(command, params, result, duration): pass
        
        text = request.get("text", "")
        output_path = request.get("output_path", "/tmp/hypothesis.json")
        
        print(f"🔌 MCP ОПЕРАЦИЯ НАЧАТА: form-hypothesis")
        print(f"📥 Параметры: text_length={len(text)}")
        
        if not text:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            result = {
                "success": False,
                "error": "Требуется текст гипотезы",
                "hypothesis_id": None
            }
            
            print(f"❌ MCP ОПЕРАЦИЯ ЗАВЕРШЕНА С ОШИБКОЙ")
            print(f"⏰ Время выполнения: {duration:.1f}мс")
            
            report_mcp_progress("form-hypothesis", request, result, duration)
            return result
        
        # Парсим и валидируем гипотезу
        hypothesis_data = parse_hypothesis_text(text)
        is_valid = validate_hypothesis(hypothesis_data)
        
        if not is_valid:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            result = {
                "success": False,
                "error": "Гипотеза не прошла валидацию",
                "hypothesis_id": hypothesis_data.get("id"),
                "validation_failed": True
            }
            
            print(f"❌ MCP ОПЕРАЦИЯ ЗАВЕРШЕНА С ОШИБКОЙ")
            print(f"⏰ Время выполнения: {duration:.1f}мс")
            
            report_mcp_progress("form-hypothesis", request, result, duration)
            return result
        
        # Сохраняем гипотезу
        saved = save_hypothesis_json(hypothesis_data, output_path)
        
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        result = {
            "success": True,
            "hypothesis_id": hypothesis_data["id"],
            "output_file": output_path,
            "hypothesis_data": hypothesis_data,
            "file_saved": saved,
            "next_steps": ["build_jtbd", "write_prd"],
            "processing_time_ms": duration
        }
        
        print(f"✅ MCP ОПЕРАЦИЯ ЗАВЕРШЕНА УСПЕШНО")
        print(f"⏰ Время выполнения: {duration:.1f}мс")
        print(f"🆔 ID гипотезы: {hypothesis_data['id']}")
        print(f"📝 Гипотеза: {hypothesis_data.get('hypothesis', 'N/A')[:100]}...")
        
        print(f"\n🎯 СЛЕДУЮЩИЕ ШАГИ:")
        print("• build_jtbd - Создать JTBD сценарии")
        print("• write_prd - Написать PRD")
        
        report_mcp_progress("form-hypothesis", request, result, duration)
        return result
        
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds() * 1000
        result = {
            "success": False,
            "error": str(e),
            "hypothesis_id": None
        }
        
        print(f"❌ MCP ОПЕРАЦИЯ ЗАВЕРШЕНА С ОШИБКОЙ")
        print(f"🚨 Ошибка: {str(e)}")
        
        try:
            report_mcp_progress("form-hypothesis", request, result, duration)
        except:
            pass
            
        return result

def extract_jtbd(text: str) -> Optional[Dict[str, str]]:
    """Извлекает JTBD из текста гипотезы."""
    # Паттерн: "Как {user}, я хочу {want}, чтобы {so_that}"
    jtbd_pattern = r'как\s+([^,]+),\s*я\s+хочу\s+([^,]+),\s*чтобы\s+(.+)'
    
    match = re.search(jtbd_pattern, text.lower())
    if match:
        return {
            "user": match.group(1).strip(),
            "want": match.group(2).strip(),
            "so_that": match.group(3).strip()
        }
    
    return None

def calculate_confidence(evidence: Dict[str, List[str]]) -> float:
    """Рассчитывает уверенность в гипотезе на основе доказательств."""
    supporting = len(evidence.get('supporting', []))
    contradicting = len(evidence.get('contradicting', []))
    
    if supporting + contradicting == 0:
        return 0.5  # Нейтральная позиция без доказательств
    
    # Простая формула: поддерживающие / общее количество
    confidence = supporting / (supporting + contradicting)
    
    # Нормализуем в диапазон 0.1-0.9
    return max(0.1, min(0.9, confidence))

if __name__ == "__main__":
    # Тестовый запуск
    if len(sys.argv) > 1:
        # Запуск как MCP команда
        request_data = json.loads(sys.argv[1])
        
        processor = FormHypothesis()
        result = processor.process(request_data.get('text', ''))
        
        print(json.dumps({
            "success": True,
            "hypothesis": result,
            "output_file": f"{result['id']}.json"
        }, indent=2, ensure_ascii=False))
    else:
        print("FormHypothesis module - use with JSON input")