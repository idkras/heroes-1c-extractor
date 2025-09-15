#!/usr/bin/env python3
"""
HeroesGPT MCP Workflow Python Backend
Обработчик MCP команд для анализа лендингов
"""

import sys
import json
import asyncio
from pathlib import Path

# Добавляем путь для импорта
sys.path.append(str(Path(__file__).parent.parent.parent))

from heroes.heroes_workflow_orchestrator import analyze_landing, HeroesWorkflowOrchestrator

async def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: heroes_workflow.py <json_args>"}))
        sys.exit(1)
    
    try:
        args = json.loads(sys.argv[1])
        action = args.get('action')
        
        orchestrator = HeroesWorkflowOrchestrator()
        
        if action == 'analyze_landing':
            url = args.get('url')
            screenshot = args.get('screenshot')
            content = args.get('content')
            
            report = await analyze_landing(url, screenshot, content)
            
            result = {
                "success": True,
                "report_id": report.id,
                "rating": report.rating,
                "offers_count": len(report.offers_table),
                "jtbd_count": len(report.jtbd_scenarios),
                "segments_count": len(report.segments),
                "recommendations_count": len(report.recommendations),
                "business_type": report.landing_analysis.business_type,
                "analysis_time": report.landing_analysis.analysis_time
            }
            
        elif action == 'extract_offers':
            landing_data = args.get('landingData')
            offers = await orchestrator._extract_all_offers(landing_data)
            
            result = {
                "success": True,
                "offers": [
                    {
                        "text": offer.offer_text,
                        "type": offer.offer_type,
                        "quantitative_data": offer.quantitative_data,
                        "segment": offer.target_segment,
                        "trigger": offer.emotional_trigger,
                        "rating": offer.value_tax_rating
                    }
                    for offer in offers
                ]
            }
            
        elif action == 'create_jtbd':
            offers_data = args.get('offers')
            scenarios = await orchestrator._create_jtbd_scenarios(offers_data)
            
            result = {
                "success": True,
                "scenarios": [
                    {
                        "big_jtbd": scenario.big_jtbd,
                        "when_trigger": scenario.when_trigger,
                        "medium_jtbd": scenario.medium_jtbd,
                        "small_jtbd": scenario.small_jtbd,
                        "status": scenario.status
                    }
                    for scenario in scenarios
                ]
            }
            
        elif action == 'generate_report':
            analysis_data = args.get('analysisData')
            await orchestrator._save_structured_report(analysis_data)
            
            # Обновляем документацию для критических анализов
            try:
                from advising_platform.src.mcp.modules.documentation_validator import update_documentation
                update_documentation("heroes_workflow", {
                    "analysis_id": analysis_data.get('id', 'unknown'),
                    "rating": analysis_data.get('rating', 0)
                })
            except ImportError:
                pass  # Документация не критична для базовой функциональности
            
            result = {
                "success": True,
                "filename": f"analysis_report_{analysis_data.get('id', 'unknown')}.md",
                "rating": analysis_data.get('rating', 0),
                "auto_saved": True
            }
            
        else:
            result = {"error": f"Unknown action: {action}"}
        
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())