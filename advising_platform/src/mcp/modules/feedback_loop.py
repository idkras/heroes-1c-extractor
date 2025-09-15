"""
MCP Module: Feedback Loop
Генерация новой улучшенной гипотезы на основе результатов
"""

import json
import time
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


def mcp_feedback_loop(previous_results: Dict[str, Any], improvement_focus: str = "quality") -> Dict[str, Any]:
    """
    MCP команда: feedback-loop
    Создает новую улучшенную гипотезу на основе предыдущих результатов
    """
    start_time = time.time()
    
    result = {
        "command": "mcp-feedback-loop",
        "timestamp": datetime.now().isoformat(),
        "new_hypothesis_generated": False,
        "improvement_focus": improvement_focus,
        "new_hypothesis_id": None,
        "execution_time_ms": 0
    }
    
    try:
        # Анализируем предыдущие результаты
        analysis = _analyze_previous_results(previous_results)
        
        # Генерируем новую гипотезу
        new_hypothesis = _generate_improved_hypothesis(analysis, improvement_focus)
        
        # Сохраняем новую гипотезу
        hypothesis_path = _save_new_hypothesis(new_hypothesis)
        
        result.update({
            "new_hypothesis_generated": True,
            "new_hypothesis_id": new_hypothesis["hypothesis_id"],
            "hypothesis_path": str(hypothesis_path),
            "improvements": new_hypothesis.get("improvements", [])
        })
        
    except Exception as e:
        result["error"] = str(e)
    
    result["execution_time_ms"] = round((time.time() - start_time) * 1000, 2)
    return result


def _analyze_previous_results(results: Dict[str, Any]) -> Dict[str, Any]:
    """Анализирует предыдущие результаты для улучшений"""
    
    return {
        "failed_areas": results.get("deviations", []),
        "success_areas": [],
        "improvement_opportunities": []
    }


def _generate_improved_hypothesis(analysis: Dict[str, Any], focus: str) -> Dict[str, Any]:
    """Генерирует улучшенную гипотезу"""
    
    version = f"v{datetime.now().strftime('%m%d')}"
    
    return {
        "hypothesis_id": f"HYP_{version}_{focus}_{datetime.now().strftime('%d%b%Y')}",
        "title": f"Improved hypothesis focused on {focus}",
        "description": f"Enhanced approach targeting {focus} improvements",
        "based_on_analysis": analysis,
        "target_metrics": {},
        "improvements": [f"Focus on {focus}", "Address previous failures"]
    }


def _save_new_hypothesis(hypothesis: Dict[str, Any]) -> Path:
    """Сохраняет новую гипотезу"""
    
    hypothesis_path = Path(f"hypothesis_{hypothesis['hypothesis_id'].lower()}.json")
    
    with open(hypothesis_path, 'w', encoding='utf-8') as f:
        json.dump(hypothesis, f, indent=2, ensure_ascii=False)
    
    return hypothesis_path
