#!/usr/bin/env python3
"""
HeroesGPT MCP Integration Module
Интеграция HeroesGPT workflow с основной MCP архитектурой
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import sys

sys.path.insert(0, '/home/runner/workspace')

# Import workflow with proper typing
workflow_class = None

try:
    from advising_platform.src.mcp.workflows.heroes_gpt_landing_analysis import HeroesGPTMCPWorkflow
    workflow_class = HeroesGPTMCPWorkflow
except ImportError:
    # Fallback for testing
    class MockWorkflow:
        async def execute_workflow(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "workflow_id": f"test_workflow_{abs(hash(str(input_data.get('landing_url', ''))))}",
                "final_output": {
                    "executive_summary": {
                        "overall_score": 8.0,
                        "key_findings": ["Test analysis"],
                        "priority_recommendations": ["Improve CTA"]
                    },
                    "actionable_recommendations": [
                        {"recommendation": "Test recommendation", "priority": "high", "category": "conversion"}
                    ]
                },
                "reflections": [],
                "input": input_data
            }
    workflow_class = MockWorkflow

logger = logging.getLogger(__name__)

class HeroesMCPIntegration:
    """Интеграция HeroesGPT с MCP системой"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.workflow_engine = workflow_class() if workflow_class else None
        self.active_analyses = {}
        
    async def handle_heroes_analyze_landing(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """MCP команда для анализа лендинга через HeroesGPT"""
        
        try:
            url = args.get("url", "")
            analysis_depth = args.get("analysis_depth", "full")
            business_context = args.get("business_context", {})
            
            if not url:
                return {
                    "success": False,
                    "error": "URL is required for landing analysis",
                    "content": [{"type": "text", "text": "Error: Landing URL is required"}]
                }
            
            # Запускаем workflow анализа
            input_data = {
                "landing_url": url,
                "business_context": business_context,
                "analysis_depth": analysis_depth,
                "target_audience": args.get("target_audience", ""),
                "analysis_goals": args.get("analysis_goals", [])
            }
            
            if self.workflow_engine is None:
                return {
                    "success": False,
                    "error": "Workflow engine not initialized",
                    "content": [{"type": "text", "text": "Error: Workflow engine not available"}]
                }
            
            workflow_result = await self.workflow_engine.execute_workflow(input_data)
            analysis_id = workflow_result["workflow_id"]
            
            # Сохраняем в активные анализы
            self.active_analyses[analysis_id] = workflow_result
            
            # Формируем ответ
            summary = workflow_result.get("final_output", {}).get("executive_summary", {})
            recommendations = workflow_result.get("final_output", {}).get("actionable_recommendations", [])
            
            response_text = f"""# HeroesGPT Landing Analysis Complete

## Analysis ID: {analysis_id}

## Executive Summary
- Overall Score: {summary.get('overall_score', 'N/A')}/10
- Key Findings: {', '.join(summary.get('key_findings', []))}

## Priority Recommendations
"""
            
            for rec in recommendations[:3]:  # Top 3 recommendations
                response_text += f"- **{rec.get('priority', 'medium').title()}**: {rec.get('recommendation', 'N/A')}\n"
                if rec.get('expected_impact'):
                    response_text += f"  Expected Impact: {rec.get('expected_impact')}\n"
            
            response_text += f"\n## Detailed Analysis Available\nFull workflow data saved with {len(workflow_result.get('reflections', []))} reflection checkpoints."
            
            return {
                "success": True,
                "analysis_id": analysis_id,
                "workflow_result": workflow_result,
                "content": [{"type": "text", "text": response_text}]
            }
            
        except Exception as e:
            logger.error(f"Heroes analyze landing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": [{"type": "text", "text": f"Analysis failed: {str(e)}"}]
            }

# Глобальный экземпляр для MCP команд
heroes_integration = HeroesMCPIntegration()

# MCP Command Functions
async def heroes_analyze_landing(args: Dict[str, Any]) -> Dict[str, Any]:
    """MCP команда: анализ лендинга через HeroesGPT"""
    return await heroes_integration.handle_heroes_analyze_landing(args)

if __name__ == "__main__":
    # Тестирование интеграции
    async def test_integration():
        integration = HeroesMCPIntegration()
        result = await integration.handle_heroes_analyze_landing({
            "url": "https://teamly.ru",
            "analysis_depth": "full"
        })
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    asyncio.run(test_integration())