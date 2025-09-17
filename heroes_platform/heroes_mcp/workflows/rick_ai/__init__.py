"""
Rick.ai Workflow Module
MCP Workflow Standard v2.3 Compliance

JTBD: Когда мне нужно получить данные из Rick.ai для анализа по чеклистам,
я хочу использовать модульную архитектуру rick_ai,
чтобы автоматически получать данные, анализировать их на ошибки и получать правила для правильного определения группировок.

WORKFLOW PROTOCOL: rick_ai_research_loop
COMPLIANCE: MCP Workflow Standard v2.3, Registry Standard v5.4
"""

from .analysis_manager import RickAIAnalysisManager
from .auth_manager import RickAIAuthManager
from .data_manager import RickAIDataManager
from .rickai_workflow import RickAIWorkflow

__all__ = [
    "RickAIAuthManager",
    "RickAIDataManager",
    "RickAIAnalysisManager",
    "RickAIWorkflow",
]
