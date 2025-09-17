"""
Validate Actual Output Workflow Module
MCP Workflow Standard v2.3 Compliance

JTBD: Когда мне нужно проверить фактический результат по URL и сравнить с ожидаемым,
я хочу использовать модульную архитектуру validate_actual_output,
чтобы автоматически анализировать страницы, создавать скриншоты и генерировать отчеты о качестве.

WORKFLOW PROTOCOL: validate_actual_outcome
COMPLIANCE: MCP Workflow Standard v2.3, TDD Documentation Standard v2.5
"""

from .quality_validator import QualityValidator
from .screenshot_manager import ScreenshotManager
from .url_analyzer import URLAnalyzer
from .workflow import ValidateActualOutputWorkflow

__all__ = [
    "URLAnalyzer",
    "ScreenshotManager",
    "QualityValidator",
    "ValidateActualOutputWorkflow",
]
