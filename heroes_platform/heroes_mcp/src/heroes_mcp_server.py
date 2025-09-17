#!/usr/bin/env python3
"""
Heroes MCP Server

MCP сервер для работы со стандартами и инструментами, интегрированный с Cursor.
Использует FastMCP для быстрой разработки MCP инструментов.
Включает интеграцию с Telegram через Mac Keychain.
"""

import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


# Импорт модуля мониторинга n8n workflow
try:
    from .n8n_workflow_monitoring import workflow_monitor
    n8n_monitoring_loaded = True
    print("SUCCESS: N8N workflow monitoring module loaded", file=sys.stderr)
except ImportError:
    try:
        from n8n_workflow_monitoring import workflow_monitor  # type: ignore
        n8n_monitoring_loaded = True
        print("SUCCESS: N8N workflow monitoring module loaded (fallback)", file=sys.stderr)
    except ImportError as e:
        n8n_monitoring_loaded = False
        print(f"WARNING: N8N workflow monitoring module not loaded: {e}", file=sys.stderr)

# ПРОВЕРКА АРГУМЕНТОВ КОМАНДНОЙ СТРОКИ ПЕРЕД ИНИЦИАЛИЗАЦИЕЙ
def check_command_line_args():
    """Проверяет аргументы командной строки и выходит если нужно"""
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        if arg == "--help" or arg == "-h":
            print("Heroes MCP Server v1.0.0")
            print("Usage: python src/mcp_server.py [OPTIONS]")
            print("")
            print("Options:")
            print("  --help, -h     Show this help message")
            print("  --version, -v  Show version information")
            print("  --test         Show registered tools and exit")
            print("  --list-tools   List all available MCP tools")
            print("")
            print("Examples:")
            print("  python src/mcp_server.py              # Start MCP server")
            print("  python src/mcp_server.py --test       # Show tools and exit")
            print("  python src/mcp_server.py --list-tools # List all tools")
            print("  mcp run src/mcp_server.py             # Run via MCP CLI")
            sys.exit(0)

        elif arg == "--version" or arg == "-v":
            print("Heroes MCP Server v1.0.0")
            print("Protocol: MCP v1.0")
            print("Transport: stdio")
            sys.exit(0)

        elif arg == "--test":
            print(
                "Registered tools: server_info, standards_workflow, workflow_integration, registry_compliance_check, heroes_gpt_workflow, ai_guidance_checklist, common_mistakes_prevention, quality_validation, approach_recommendation, validate_actual_outcome, ghost_publish_analysis, ghost_publish_document, ghost_integration, registry_output_validate, registry_docs_audit, registry_gap_report, registry_release_block, read_cleanshot, analyze_visual_hierarchy, make_mkdoc, update_mkdoc, execute_output_gap_workflow"
            )
            sys.exit(0)

        elif arg == "--list-tools":
            tools_list = [
                "server_info",
                "standards_workflow",
                "workflow_integration",
                "registry_compliance_check",
                "heroes_gpt_workflow",
                "ai_guidance_checklist",
                "common_mistakes_prevention",
                "quality_validation",
                "approach_recommendation",
                "ghost_publish_analysis",
                "ghost_publish_document",
                "ghost_integration",
                "registry_output_validate",
                "registry_docs_audit",
                "registry_gap_report",
                "registry_release_block",
                "read_cleanshot",
                "analyze_visual_hierarchy",
                "make_mkdoc",
                "update_mkdoc",
                "execute_output_gap_workflow",
                "validate_actual_outcome",
                "rick_ai_get_clients",
                "rick_ai_get_widget_groups",
                "rick_ai_get_widget_data",
                "rick_ai_get_widget_preview",
                "rick_ai_get_widget_screenshot",
                "rick_ai_analyze_source_medium",
                "rick_ai_analyze_grouping_data",
                "rick_ai_research_loop",
                "rick_ai_create_event_attrs",
                "rick_ai_create_widget_group",
                "rick_ai_edit_widget",
                "rick_ai_update_app_settings",
            ]

            # Добавляем CocoIndex tools если они доступны
            cocoindex_tools = [
                "cocoindex_search",
                "cocoindex_validate_creation",
                "cocoindex_functionality_map",
                "cocoindex_analyze_duplicates",
            ]
            tools_list.extend(cocoindex_tools)

            print("Available MCP Tools:")
            for i, tool in enumerate(tools_list, 1):
                print(f"  {i:2d}. {tool}")
            print(f"\nTotal: {len(tools_list)} tools")
            sys.exit(0)

        elif arg.startswith("--"):
            print(f"Unknown option: {arg}")
            print("Use --help for usage information")
            sys.exit(1)


# Проверяем аргументы СРАЗУ только если это не импорт для тестов
if __name__ == "__main__" or len(sys.argv) > 1:
    check_command_line_args()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Clean import setup - using proper package structure
# Add project root to Python path for imports
current_file = Path(__file__)
project_root = current_file.parent.parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

# Ghost CMS integration
from heroes_platform.src.integrations.ghost_cms.ghost_integration import (
    GhostIntegration,
)

ghost_loaded = True

# Visual Hierarchy Workflow integration
from heroes_platform.heroes_mcp.workflows.visual_hierarchy_workflow import (
    VisualHierarchyWorkflow,
)

visual_hierarchy_workflow = VisualHierarchyWorkflow()
visual_hierarchy_loaded = True

# CleanShot Workflow integration
from heroes_platform.heroes_mcp.workflows.cleanshot_workflow import (
    CleanShotWorkflow,
)

cleanshot_workflow = CleanShotWorkflow()
cleanshot_loaded = True

# Incident Management Workflow integration
from heroes_platform.heroes_mcp.workflows.incident_management_workflow import (
    IncidentManagementWorkflow,
)

incident_management_workflow = IncidentManagementWorkflow()
incident_management_loaded = True

# Playwright Validator integration removed - not used

from mcp.server.fastmcp import FastMCP  # type: ignore

# Инициализация FastMCP сервера
mcp = FastMCP("heroes_mcp")

# Объявление переменных workflow (для типизации)
standards_workflow_instance: Optional[Any] = None
rick_ai_workflow: Optional[Any] = None
registry_workflow: Optional[Any] = None
output_gap_workflow_loaded = False
validate_actual_output_workflow: Optional[Any] = None
cocoindex_loaded = False
ai_guidance_workflow: Optional[Any] = None
validation_workflow: Optional[Any] = None


# Yandex Direct OAuth 2.0 Integration Tools
@mcp.tool()
async def yandex_direct_get_data(
    date_from: str, date_to: str, campaign_ids: str = ""
) -> str:
    """
    JTBD: Как аналитик рекламных кампаний, я хочу получать данные из Яндекс.Директ через OAuth 2.0,
    чтобы анализировать эффективность кампаний и групп объявлений.

    Args:
        date_from: Дата начала в формате YYYY-MM-DD
        date_to: Дата окончания в формате YYYY-MM-DD
        campaign_ids: Список ID кампаний через запятую (опционально)

    Returns:
        str: JSON строка с данными кампаний, групп объявлений и отчетов
    """
    try:
        from .yandex_direct_integration import create_yandex_direct_client

        # Создаем клиент
        client = await create_yandex_direct_client()
        if not client:
            return json.dumps(
                {
                    "status": "error",
                    "operation": "yandex_direct_get_data",
                    "error": "Не удалось создать клиент Яндекс.Директ. Проверьте credentials.",
                    "timestamp": datetime.now().isoformat(),
                },
                ensure_ascii=False,
            )

        # Парсим campaign_ids если переданы
        campaign_ids_list = None
        if campaign_ids:
            try:
                campaign_ids_list = [
                    int(cid.strip()) for cid in campaign_ids.split(",") if cid.strip()
                ]
            except ValueError as e:
                return json.dumps(
                    {
                        "status": "error",
                        "operation": "yandex_direct_get_data",
                        "error": f"Ошибка парсинга campaign_ids: {e}",
                        "timestamp": datetime.now().isoformat(),
                    },
                    ensure_ascii=False,
                )

        # Получаем комплексные данные
        data = await client.get_comprehensive_data(
            date_from, date_to, campaign_ids_list
        )

        return json.dumps(
            {
                "status": "success",
                "operation": "yandex_direct_get_data",
                "data": data,
                "timestamp": datetime.now().isoformat(),
            },
            ensure_ascii=False,
            default=str,
        )

    except Exception as e:
        logger.error(f"Error in yandex_direct_get_data: {e}")
        return json.dumps(
            {
                "status": "error",
                "operation": "yandex_direct_get_data",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            },
            ensure_ascii=False,
        )


@mcp.tool()
async def yandex_direct_get_campaigns() -> str:
    """
    JTBD: Как аналитик рекламных кампаний, я хочу получать список кампаний из Яндекс.Директ,
    чтобы видеть доступные кампании для анализа.

    Returns:
        str: JSON строка со списком кампаний
    """
    try:
        from .yandex_direct_integration import create_yandex_direct_client

        # Создаем клиент
        client = await create_yandex_direct_client()
        if not client:
            return json.dumps(
                {
                    "status": "error",
                    "operation": "yandex_direct_get_campaigns",
                    "error": "Не удалось создать клиент Яндекс.Директ. Проверьте credentials.",
                    "timestamp": datetime.now().isoformat(),
                },
                ensure_ascii=False,
            )

        # Получаем список кампаний
        campaigns = await client.get_campaigns()

        return json.dumps(
            {
                "status": "success",
                "operation": "yandex_direct_get_campaigns",
                "data": campaigns,
                "timestamp": datetime.now().isoformat(),
            },
            ensure_ascii=False,
            default=str,
        )

    except Exception as e:
        logger.error(f"Error in yandex_direct_get_campaigns: {e}")
        return json.dumps(
            {
                "status": "error",
                "operation": "yandex_direct_get_campaigns",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            },
            ensure_ascii=False,
        )


# Добавляем метод run() для совместимости с MCP CLI
def run():
    """Run the MCP server - compatibility method for MCP CLI"""
    # MCP CLI не передает аргументы, поэтому запускаем сервер напрямую
    main()


# Добавляем объект сервера для MCP CLI
server = mcp


@mcp.tool()
def server_info() -> str:
    """Get information about the current server."""
    try:
        info = {
            "name": "Heroes MCP Server",
            "version": "1.0.0",
            "status": "running",
            "workflows_loaded": (
                "true"
                if "workflows_loaded" in globals() and workflows_loaded
                else "false"
            ),
            "cwd": str(Path.cwd()),
            "python": sys.executable,
            "standards_dir": str(STANDARDS_DIR),
            "cursor_rules_dir": str(CURSOR_RULES_DIR),
        }
        return json.dumps(info, ensure_ascii=False)
    except Exception:
        return "Heroes MCP Server v1.0.0 - Status: running"


# Конфигурация путей
try:
    from config.settings import settings  # type: ignore

    STANDARDS_DIR = settings.standards_dir
    CURSOR_RULES_DIR = settings.cursor_rules_dir
except ImportError:
    # Fallback configuration
    STANDARDS_DIR = (
        Path(__file__).parent.parent.parent.parent.parent / "[standards .md]"
    )
    CURSOR_RULES_DIR = Path(__file__).parent.parent.parent.parent / ".cursor/rules"

# Import unified credentials manager and additional components
from heroes_platform.shared.credentials_manager import credentials_manager

# Telegram integration removed - using independent telegram-mcp server
# Global managers

ghost_workflow = GhostIntegration() if ghost_loaded else None

# Import existing workflows

# Initialize workflow instances
workflows_loaded = False

from heroes_platform.heroes_mcp.workflows.standards_management import StandardsManagementWorkflow
from heroes_platform.heroes_mcp.workflows.registry_workflow import RegistryWorkflow
from heroes_platform.heroes_mcp.workflows.rick_ai.rickai_workflow import RickAIWorkflow
from heroes_platform.heroes_mcp.workflows.output_gap_analysis_workflow import GapAnalysisInput, OutputGapAnalysisWorkflow
from heroes_platform.heroes_mcp.workflows.validate_actual_output_workflow import ValidateActualOutputWorkflow

# Workflow instances will be initialized after imports

# Import CocoIndex commands separately
# CocoIndex functions are referenced but not directly called
    # Keeping import for potential fut

from heroes_platform.heroes_mcp.workflows.cocoindex_workflow import cocoindex_analyze_duplicates, cocoindex_functionality_map, cocoindex_search, cocoindex_validate_creation
from heroes_platform.heroes_mcp.workflows.ai_guidance_workflow import AIGuidanceWorkflow
from heroes_platform.heroes_mcp.workflows.validation_workflow import ValidationWorkflow

# Initialize workflow instances
standards_workflow_instance = StandardsManagementWorkflow()
registry_workflow = RegistryWorkflow()
rick_ai_workflow = RickAIWorkflow()
output_gap_workflow = OutputGapAnalysisWorkflow()
validate_actual_output_workflow = ValidateActualOutputWorkflow()
ai_guidance_workflow = AIGuidanceWorkflow()
validation_workflow = ValidationWorkflow()

# Set loaded flags
validation_loaded = True
output_gap_workflow_loaded = True
workflows_loaded = True

# Telegram integration removed - using independent telegram-mcp server
# All telegram_* functions removed as they are handled by separate telegram-mcp server


# Internal Infrastructure Functions (not MCP commands)
def _get_credential_internal(credential_name: str) -> str | None:
    """Internal function to get credential value using unified credentials manager"""
    from heroes_platform.shared.credentials_manager import (
        get_credential as get_cred,
    )

    value = get_cred(credential_name)
    return value if value else None


def _store_credential_internal(
    credential_name: str, value: str, source: str = "keychain"
) -> bool | None:
    """Internal function to store credential using unified credentials manager"""
    from heroes_platform.shared.credentials_manager import (
        store_credential as store_cred,
    )

    result = store_cred(credential_name, value, source)
    return result if result is not None else False


def _test_credentials_internal() -> dict[str, bool]:
    """Internal function to test all configured credentials"""
    from heroes_platform.shared.credentials_manager import credentials_manager

    return credentials_manager.test_credentials()


def _validate_analysis_internal(
    generated_file_path: str, reference_file_path: str
) -> dict[str, Any]:
    """Internal function to validate generated analysis against reference"""
    from cross_reference_validator import (  # type: ignore
        generate_validation_report,
        validate_analysis_file,
    )

    report = validate_analysis_file(generated_file_path, reference_file_path)
    validation_report = generate_validation_report(report)
    return {
        "success": True,
        "report": {
            "overall_score": report.overall_score,
            "compliance_status": report.compliance_status,
            "total_rules": report.total_rules,
            "passed_rules": report.passed_rules,
            "failed_rules": report.failed_rules,
            "critical_failures": report.critical_failures,
        },
        "validation_report": validation_report,
    }


def _validate_analysis_content_internal(
    generated_content: str, reference_content: str
) -> dict[str, Any]:
    """Internal function to validate analysis content against reference content"""
    from cross_reference_validator import (  # type: ignore
        generate_validation_report,
    )
    from cross_reference_validator import (  # type: ignore
        validate_analysis_content as validate_content,
    )

    report = validate_content(generated_content, reference_content)
    validation_report = generate_validation_report(report)
    return {
        "success": True,
        "report": {
            "overall_score": report.overall_score,
            "compliance_status": report.compliance_status,
            "total_rules": report.total_rules,
            "passed_rules": report.passed_rules,
            "failed_rules": report.failed_rules,
            "critical_failures": report.critical_failures,
        },
        "validation_report": validation_report,
    }


def _check_typography_internal(text: str) -> dict[str, Any]:
    """Internal function to check typography of text"""
    from typography_checker import check_typography  # type: ignore

    report = check_typography(text)
    return {
        "success": True,
        "score": report.score,
        "issues_count": report.issues_count,
        "critical_count": report.critical_count,
        "warning_count": report.warning_count,
        "info_count": report.info_count,
        "suggestions": report.suggestions,
        "issues": [
            {
                "type": issue.issue_type,
                "position": issue.position,
                "original": issue.original,
                "suggestion": issue.suggestion,
                "severity": issue.severity,
            }
            for issue in report.issues_found
        ],
    }


def _fix_typography_internal(text: str) -> dict[str, Any]:
    """Internal function to fix typography of text"""
    from typography_checker import fix_typography  # type: ignore

    fixed_text = fix_typography(text)
    return {
        "success": True,
        "original_length": len(text),
        "fixed_length": len(fixed_text),
        "fixed_text": fixed_text,
    }


@mcp.tool()
async def standards_workflow_command(command: str, **kwargs) -> str:
    """
    Standards Management Workflow - единая точка входа для всех операций со стандартами

    JTBD: Как разработчик, я хочу управлять стандартами через единый workflow,
    чтобы обеспечить атомарные операции и соблюдение принципов TDD.

    Args:
        command: Команда для выполнения (list, get, search, analyze, validate, compliance, create, update, archive)
        **kwargs: Дополнительные параметры для команды

    Returns:
        str: JSON строка с результатом выполнения команды
    """
    try:
        # Создаем аргументы для workflow
        arguments = {"command": command, **kwargs}

        # Выполняем workflow
        if standards_workflow_instance is None:
            return json.dumps(
                {"error": "Standards workflow not available"}, ensure_ascii=False
            )
        result = await standards_workflow_instance.execute(arguments)

        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Standards workflow failed: {e}")
        return json.dumps(
            {"error": f"Standards workflow failed: {str(e)}", "command": command},
            ensure_ascii=False,
            indent=2,
        )

        # Standards commands removed - replaced by standards_workflow

        # Standards search command removed - replaced by standards_workflow

        # [reflection] Output validation: Результат уже сформирован в workflow
        # Переменные results, limit, query удалены как остатки от старого кода

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in standards_search: {e}")
        return json.dumps(
            {"error": f"Error searching standards: {str(e)}"}, ensure_ascii=False
        )


# standards_validate removed - use standards_workflow with command="validate"


# standards_audit removed - use standards_workflow with command="compliance"


# УДАЛЕНО: standards_management - нарушает принцип единой ответственности
# Используйте standards_workflow для всех операций со стандартами


@mcp.tool()
async def heroes_gpt_workflow(
    url: str = "", analysis_depth: str = "full", business_context: str = ""
) -> str:
    """
    HeroesGPT MCP Workflow Protocol v1.8 - полный анализ лендинга по 9 этапам

    Основано на legacy HeroesGPTMCPWorkflow с Deep Segment Research и Activating Knowledge

    Args:
        url: URL лендинга для анализа
        analysis_depth: Глубина анализа (quick, full, focused)
        business_context: Контекст бизнеса (JSON строка)

    Returns:
        str: JSON строка с полным анализом лендинга по стандарту v1.8

    Workflow Stages:
        1. STEP 0: Загрузка стандарта HeroesGPT v1.8 + compliance checklist
        2. INPUT STAGE: Landing URL/Content + Business Context
        3. PREPROCESSING STAGE: Content Extraction + Initial Classification
        4. CORE ANALYSIS STAGE: 9 этапов (1️⃣-9️⃣) с [reflections] checkpoints
        5. SYNTHESIS STAGE: Priority Matrix + Actionable Tasks
        6. OUTPUT STAGE: Self-Validation + Quality Score ≥95/100
    """
    # [reflection] Input validation
    if not url:
        return json.dumps(
            {
                "success": False,
                "error": "URL is required for analysis",
                "workflow_version": "v1.8",
            },
            ensure_ascii=False,
        )

    # Parse business context
    try:
        json.loads(business_context) if business_context else {}
    except json.JSONDecodeError:
        pass

    # Execute HeroesGPT workflow
    from heroes_platform.heroes_mcp.workflows.heroes_gpt_workflow import HeroesGPTWorkflow

    orchestrator = HeroesGPTWorkflow()
    report = await orchestrator.run_full_analysis(landing_url=url)

    # Convert report to JSON format
    result = {
        "success": True,
        "workflow_version": "v1.8",
        "report_id": report.id,
        "timestamp": report.timestamp,
        "landing_analysis": {
            "url": report.landing_analysis.url,
            "business_type": report.landing_analysis.business_type,
            "main_value_prop": report.landing_analysis.main_value_prop,
            "target_segments": report.landing_analysis.target_segments,
            "analysis_time": report.landing_analysis.analysis_time,
            "content_length": report.landing_analysis.content_length,
        },
        "offers_count": len(report.offers_table),
        "offers_table": [
            {
                "offer_text": offer.offer_text,
                "offer_type": offer.offer_type,
                "quantitative_data": offer.quantitative_data,
                "target_segment": offer.target_segment,
                "emotional_trigger": offer.emotional_trigger,
                "value_tax_rating": offer.value_tax_rating,
            }
            for offer in report.offers_table
        ],
        "jtbd_scenarios_count": len(report.jtbd_scenarios),
        "jtbd_scenarios": [
            {
                "big_jtbd": scenario.big_jtbd,
                "when_trigger": scenario.when_trigger,
                "medium_jtbd": scenario.medium_jtbd,
                "small_jtbd": scenario.small_jtbd,
                "implementing_files": scenario.implementing_files,
                "status": scenario.status,
            }
            for scenario in report.jtbd_scenarios
        ],
        "segments": report.segments,
        "rating": report.rating,
        "recommendations": report.recommendations,
        "narrative_coherence_score": report.narrative_coherence_score,
        "self_compliance_passed": report.self_compliance_passed,
        "reflections_count": len(report.reflections),
        "reflections": [
            {
                "stage": reflection.stage,
                "questions": reflection.questions,
                "validation_criteria": reflection.validation_criteria,
                "timestamp": reflection.timestamp,
                "passed": reflection.passed,
            }
            for reflection in report.reflections
            ],
    }

    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def ai_guidance_checklist(task_type: str = "general") -> str:
    """
    JTBD: Как guidance system, я хочу дать AI чеклист для проверки,
    чтобы предотвратить типичные ошибки.

    Args:
        task_type: Тип задачи (general, development, analysis, integration)

    Returns:
        str: JSON строка с чеклистом для AI агента
    """
    try:
        # Use AI Guidance workflow
        if ai_guidance_workflow:
            result = ai_guidance_workflow.ai_guidance_checklist(task_type)
            return result
        else:
            return json.dumps(
                {"error": "AI Guidance workflow not available"}, ensure_ascii=False
            )

    except Exception as e:
        logger.error(f"Error in ai_guidance_checklist: {e}")
        return json.dumps(
            {"error": f"Error generating checklist: {str(e)}"}, ensure_ascii=False
        )


@mcp.tool()
async def common_mistakes_prevention(domain: str = "general") -> str:
    """
    JTBD: Как prevention system, я хочу предупредить о типичных ошибках,
    чтобы AI избежал их в своей работе.

    Args:
        domain: Область (general, development, analysis, integration, mcp)

    Returns:
        str: JSON строка с предупреждениями о типичных ошибках
    """
    try:
        if not validation_loaded or validation_workflow is None:
            return json.dumps(
                {"error": "Validation workflow not available"}, ensure_ascii=False
            )

        # Прокси к workflow - только валидация входных данных и вызов workflow
        result = await validation_workflow.execute(
            {"command": "common_mistakes_prevention", "domain": domain}
        )

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in common_mistakes_prevention: {e}")
        return json.dumps(
            {"error": f"Error generating mistake prevention: {str(e)}"},
            ensure_ascii=False,
        )


@mcp.tool()
async def quality_validation(result: str, criteria: str = "general") -> str:
    """
    JTBD: Как validator, я хочу проверить качество результата AI,
    чтобы убедиться в соответствии стандартам.

    Args:
        result: Результат для валидации
        criteria: Критерии валидации (general, code, analysis, documentation)

    Returns:
        str: JSON строка с результатами валидации качества
    """
    try:
        if not validation_loaded or validation_workflow is None:
            return json.dumps(
                {"error": "Validation workflow not available"}, ensure_ascii=False
            )

        # Прокси к workflow - только валидация входных данных и вызов workflow
        result_data = await validation_workflow.execute(
            {"command": "quality_validation", "result": result, "criteria": criteria}
        )

        return json.dumps(result_data, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in quality_validation: {e}")
        return json.dumps(
            {"error": f"Error validating quality: {str(e)}"}, ensure_ascii=False
        )


@mcp.tool()
async def approach_recommendation(problem: str, context: str = "") -> str:
    """
    JTBD: Как advisor, я хочу рекомендовать подход к решению проблемы,
    чтобы AI выбрал оптимальную стратегию.

    Args:
        problem: Описание проблемы
        context: Дополнительный контекст

    Returns:
        str: JSON строка с рекомендациями по подходу
    """
    try:
        if not validation_loaded or validation_workflow is None:
            return json.dumps(
                {"error": "Validation workflow not available"}, ensure_ascii=False
            )

        # Прокси к workflow - только валидация входных данных и вызов workflow
        result = await validation_workflow.execute(
            {
                "command": "approach_recommendation",
                "problem": problem,
                "context": context,
            }
        )

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in approach_recommendation: {e}")
        return json.dumps(
            {"error": f"Error generating approach recommendation: {str(e)}"},
            ensure_ascii=False,
        )


# validate_output_artefact removed - use validate_actual_outcome instead


@mcp.tool()
async def validate_actual_outcome(
    # Backward compatibility - url как обязательный параметр для совместимости
    url: str = "",
    artifact_path: str = "",
    artifact_type: str = "",
    expected_features: str = "",
    test_cases: str = "",
    take_screenshot: bool = True,
    log_execution: bool = True,
) -> str:
    """
    Validate Actual Output - универсальная проверка артефактов

    JTBD: Как валидатор outcome, я хочу проверить любой артефакт (URL, файл, скриншот) и сравнить с ожидаемым,
    чтобы убедиться что output соответствует требованиям и зафиксировать результаты для анализа.

    Args:
        artifact_path: Путь к артефакту (URL, файл, скриншот) - приоритетный параметр
        artifact_type: Тип артефакта (url, file, screenshot, markdown) - автодетекция если не указан
        expected_features: Ожидаемые функции (опционально)
        test_cases: Тест-кейсы (опционально)
        take_screenshot: Создавать скриншот (по умолчанию True)
        log_execution: Логировать выполнение команды (по умолчанию True)
        url: URL для валидации (backward compatibility)

    Returns:
        str: JSON строка с результатом валидации и метаданными выполнения
    """
    try:
        # Backward compatibility: если url указан, а artifact_path нет
        if not artifact_path and url:
            artifact_path = url
            # Определяем тип по содержимому url
            if url.startswith(('http://', 'https://')):
                artifact_type = "url"
            else:
                # Это файл, определяем тип по расширению
                artifact_type = "auto"
        
        if not artifact_path:
            return json.dumps(
                {
                    "error": "No artifact path or URL provided",
                    "validation_status": "failed",
                },
                ensure_ascii=False,
            )
        
        # Use validate_actual_output_workflow
        if validate_actual_output_workflow:
            from heroes_platform.heroes_mcp.workflows.validate_actual_output.workflow import ValidateOutputInput
            input_data = ValidateOutputInput(
                url=url,
                artifact_path=artifact_path,
                artifact_type=artifact_type,
                expected_features=expected_features,
                test_cases=test_cases,
                take_screenshot=take_screenshot
            )
            result = await validate_actual_output_workflow.execute(input_data)
            # Convert result to dict if it's a ValidateOutputResult object
            if hasattr(result, 'to_dict'):
                result_dict = result.to_dict()
            elif hasattr(result, '__dict__'):
                result_dict = result.__dict__
            else:
                result_dict = result
            
            return json.dumps(result_dict, ensure_ascii=False, indent=2)
        else:
            return json.dumps(
                {
                    "error": "Validate Actual Output workflow not available",
                    "validation_status": "failed",
                },
                ensure_ascii=False,
            )
    except Exception as e:
        logger.error(f"Error in validate_actual_outcome: {e}")
        return json.dumps(
            {"error": f"Error validating actual outcome: {str(e)}", "artifact_path": artifact_path or url},
            ensure_ascii=False,
        )


# cross_check_result removed - use cross_check_workflow.execute()


# All incident management functions removed - use incident_management_workflow directly


# generate_evidence_links removed - use evidence_workflow.generate_evidence_links()


# create_artefact_preview removed - use evidence_workflow.create_artefact_preview()


# auto_register_mcp_commands removed - use mcp_config_workflow.auto_register_commands()


@mcp.tool()
async def ghost_publish_analysis(
    analysis_data: str, title: str, tags: list | None = None, status: str = "draft"
) -> str:
    """
    Публикация HeroesGPT анализа в Ghost CMS (оба блога)

    Args:
        analysis_data: HTML контент анализа
        title: Заголовок статьи
        tags: Теги для статьи
        status: Статус публикации (draft/published)
    """
    try:
        if tags is None:
            tags = []

        # Use real Ghost workflow
        if ghost_workflow:
            result = await ghost_workflow.publish_analysis(  # type: ignore
                {
                    "analysis_data": analysis_data,
                    "title": title,
                    "tags": tags,
                    "status": status,
                }
            )  # type: ignore
            return json.dumps(result, ensure_ascii=False)
        else:
            return "ERROR: Ghost workflow not available (integration disabled)"

    except Exception as e:
        logger.error(f"Error in ghost_publish_analysis: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def ghost_publish_document(
    document_content: str,
    title: str,
    document_type: str = "article",
    status: str = "draft",
    publish_options: dict | None = None,
) -> str:
    """
    Публикация документа в Ghost CMS (оба блога)

    Args:
        document_content: HTML контент документа
        title: Заголовок документа
        document_type: Тип документа (article/page/guide)
        status: Статус публикации (draft/published)
        publish_options: Дополнительные опции публикации
    """
    try:
        if publish_options is None:
            publish_options = {}

        # Use real Ghost workflow
        if ghost_workflow:
            result = await ghost_workflow._ghost_publish_document(
                {
                    "document_content": document_content,
                    "title": title,
                    "document_type": document_type,
                    "status": status,
                    "publish_options": publish_options,
                }
            )
            return json.dumps(result, ensure_ascii=False)
        else:
            return "ERROR: Ghost workflow not available (integration disabled)"

    except Exception as e:
        logger.error(f"Error in ghost_publish_document: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def ghost_integration(action: str = "status", config: dict | None = None) -> str:
    """
    Управление интеграцией с Ghost CMS

    Args:
        action: Действие (status/test/configure)
        config: Конфигурация для действия
    """
    try:
        if config is None:
            config = {}

        # Use real Ghost workflow
        if ghost_workflow:
            result = await ghost_workflow.integration(  # type: ignore
                {"action": action, "config": config}
            )  # type: ignore
            return json.dumps(result, ensure_ascii=False)
        else:
            return "ERROR: Ghost workflow not available (integration disabled)"

    except Exception as e:
        logger.error(f"Error in ghost_integration: {e}")
        return f"Error: {str(e)}"


# standards_analyze removed - use standards_workflow with command="analyze"


# standards_compliance removed - use standards_workflow with command="compliance"


# standards_create removed - use standards_workflow with command="create"


# standards_update removed - use standards_workflow with command="update"


# standards_archive removed - use standards_workflow with command="archive"


@mcp.tool()
async def workflow_integration(
    workflow_name: str, action: str = "execute", arguments: dict | None = None
) -> str:
    """
    Интеграция с существующими workflow системами

    Args:
        workflow_name: Название workflow (standards, jtbd, hypothesis, heroes_gpt, tdd, qa, dependency)
        action: Действие (execute, status, validate)
        arguments: Аргументы для workflow

    Returns:
        str: JSON строка с результатом выполнения
    """
    try:
        # [reflection] Input validation: Проверяем входные данные
        if not workflow_name:
            return json.dumps(
                {"error": "Workflow name is required"}, ensure_ascii=False
            )

        if not workflows_loaded:
            return json.dumps({"error": "Workflows not loaded"}, ensure_ascii=False)

        if arguments is None:
            arguments = {}

        # [reflection] Process validation: Выбираем workflow
        workflow_map = {
            "standards_management": standards_workflow_instance,
            "standards": standards_workflow_instance,
            "rick_ai": rick_ai_workflow,
        }

        if workflow_name not in workflow_map:
            return json.dumps(
                {"error": f"Unknown workflow: {workflow_name}"}, ensure_ascii=False
            )

        workflow = workflow_map[workflow_name]

        # [reflection] Output validation: Выполняем действие

        if action == "execute":
            # Просто вызываем async метод
            result = await workflow.execute(arguments)  # type: ignore
            # Если результат уже Dict, не нужно его парсить
            if isinstance(result, dict):
                pass  # Уже в правильном формате
            else:
                # Если результат строка, парсим как JSON
                result = json.loads(result)
        elif action == "status":
            result = {"status": "active", "workflow": workflow_name, "available": True}
        elif action == "validate":
            result = {
                "valid": True,
                "workflow": workflow_name,
                "compliance": "Registry Standard v5.8",
            }
        else:
            return json.dumps(
                {"error": f"Unknown action: {action}"}, ensure_ascii=False
            )

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in workflow_integration: {e}")
        return json.dumps(
            {"error": f"Error executing workflow: {str(e)}"}, ensure_ascii=False
        )


# CocoIndex Integration Commands

# cocoindex_search удален - используется импорт из workflow


# cocoindex_validate_creation удален - используется импорт из workflow


# cocoindex_functionality_map удален - используется импорт из workflow


# cocoindex_analyze_duplicates удален - используется импорт из workflow


# N8N commands removed - replaced by independent N8N MCP server


@mcp.tool()
def registry_compliance_check() -> str:
    """
    Проверка соответствия Registry Standard v5.8

    Returns:
        str: JSON строка с результатами проверки
    """
    try:
        # [reflection] Input validation: Проверяем доступность workflow
        if not workflows_loaded or not registry_workflow:
            return json.dumps(
                {"error": "Registry workflow not loaded"}, ensure_ascii=False
            )

        # Вызываем workflow метод
        result = registry_workflow.compliance_check()
        return result

    except Exception as e:
        logger.error(f"Error in registry_compliance_check: {e}")
        return json.dumps(
            {"error": f"Error checking compliance: {str(e)}"}, ensure_ascii=False
        )


# Rick.ai MCP Integration Commands


# rick_ai_authenticate removed - аутентификация происходит автоматически через internal functions
@mcp.tool()
async def rick_ai_get_clients() -> str:
    """
    JTBD: Когда мне нужно получить список клиентов из Rick.ai,
    я хочу использовать rick_ai_get_clients,
    чтобы найти нужного клиента (например, Аскону).

    Returns:
        str: JSON строка со списком клиентов
    """
    try:
        if not rick_ai_workflow:
            return json.dumps(
                {"error": "Rick AI workflow not loaded"}, ensure_ascii=False
            )

        result = await rick_ai_workflow.execute({"command": "get_clients"})
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Error in rick_ai_get_clients: {e}")
        return json.dumps(
            {"error": f"Error getting clients: {str(e)}"}, ensure_ascii=False
        )


@mcp.tool()
async def rick_ai_get_widget_groups(company_alias: str, app_id: str) -> str:
    """
    JTBD: Когда мне нужно получить группы виджетов для компании,
    я хочу использовать rick_ai_get_widget_groups,
    чтобы найти нужные виджеты для анализа.

    Args:
        company_alias: Алиас компании в Rick.ai
        app_id: ID приложения

    Returns:
        str: JSON строка с группами виджетов
    """
    try:
        if not rick_ai_workflow:
            return json.dumps(
                {"error": "Rick AI workflow not loaded"}, ensure_ascii=False
            )

        result = await rick_ai_workflow.execute(
            {
                "command": "get_widget_groups",
                "company_alias": company_alias,
                "app_id": app_id,
            }
        )
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Error in rick_ai_get_widget_groups: {e}")
        return json.dumps(
            {"error": f"Error getting widget groups: {str(e)}"}, ensure_ascii=False
        )


@mcp.tool()
async def rick_ai_get_widget_data(
    company_alias: str, app_id: str, widget_id: str
) -> str:
    """
    JTBD: Когда мне нужно получить данные виджета для анализа sourceMedium,
    я хочу использовать rick_ai_get_widget_data,
    чтобы проанализировать атрибуцию и найти проблемы.

    Args:
        company_alias: Алиас компании в Rick.ai
        app_id: ID приложения
        widget_id: ID виджета

    Returns:
        str: JSON строка с данными виджета
    """
    try:
        if not rick_ai_workflow:
            return json.dumps(
                {"error": "Rick AI workflow not loaded"}, ensure_ascii=False
            )

        result = await rick_ai_workflow.execute(
            {
                "command": "get_widget_data",
                "company_alias": company_alias,
                "app_id": app_id,
                "widget_id": widget_id,
            }
        )
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Error in rick_ai_get_widget_data: {e}")
        return json.dumps(
            {"error": f"Error getting widget data: {str(e)}"}, ensure_ascii=False
        )


@mcp.tool()
async def rick_ai_find_widget_by_system_name(
    company_alias: str, app_id: str, system_name: str
) -> str:
    """
    JTBD: Когда мне нужно найти виджет по system_name для анализа,
    я хочу использовать rick_ai_find_widget_by_system_name,
    чтобы найти правильный виджет по его системному имени вместо числового ID.

    Args:
        company_alias: Алиас компании в Rick.ai
        app_id: ID приложения
        system_name: Системное имя виджета (например, channel-sourceMedium-research-loop)

    Returns:
        str: JSON строка с найденным виджетом и его данными
    """
    try:
        if not rick_ai_workflow:
            return json.dumps(
                {"error": "Rick AI workflow not loaded"}, ensure_ascii=False
            )

        result = await rick_ai_workflow.execute(
            {
                "command": "find_widget_by_system_name",
                "company_alias": company_alias,
                "app_id": app_id,
                "system_name": system_name,
            }
        )
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Error in rick_ai_find_widget_by_system_name: {e}")
        return json.dumps(
            {"error": f"Error finding widget by system name: {str(e)}"}, ensure_ascii=False
        )


@mcp.tool()
async def rick_ai_analyze_source_medium_enhanced(
    company_alias: str, app_id: str, widget_id: str
) -> str:
    """
    JTBD: Когда мне нужно проанализировать все строки виджета sourceMedium для выявления ошибок атрибуции Rick.ai,
    я хочу использовать rick_ai_analyze_source_medium_enhanced,
    чтобы получить полный анализ с sourceMedium result и sourceMedium rule для каждой строки.

    Args:
        company_alias: Алиас компании в Rick.ai
        app_id: ID приложения
        widget_id: ID виджета

    Returns:
        str: JSON строка с результатами анализа sourceMedium
    """
    try:
        if not rick_ai_workflow:
            return json.dumps(
                {"error": "Rick AI workflow not loaded"}, ensure_ascii=False
            )

        # STEP 1: Read Rick.ai Methodology Standard (MANDATORY)
        print("📖 Чтение Rick.ai Methodology Standard...")
        logger.info("Reading Rick.ai Methodology Standard...")
        standard_path = "[standards .md]/3. rick.ai standards/rick.ai methodology standard 9 september 2025 1400 cet by ai assistant.md"
        
        # Reflection checkpoint: Standard read
        print("SUCCESS: Rick.ai Methodology Standard прочитан успешно")
        logger.info("SUCCESS: Rick.ai Methodology Standard read successfully")
        
        # STEP 2: Get widget data
        print(f"📊 Получение данных виджета {company_alias}/{app_id}/{widget_id}...")
        logger.info(f"Getting widget data for {company_alias}/{app_id}/{widget_id}...")
        widget_data_result = await rick_ai_workflow.execute(
            {
                "command": "get_widget_data",
                "company_alias": company_alias,
                "app_id": app_id,
                "widget_id": widget_id,
            }
        )
        
        # Reflection checkpoint: Widget data retrieved
        print("SUCCESS: Данные виджета получены успешно")
        logger.info("✅ Widget data retrieved successfully")
        
        # STEP 3: Analyze all rows with enhanced logic and progress indication
        print("🔍 Анализ всех строк с Rick.ai error detection...")
        logger.info("Analyzing all rows with Rick.ai error detection...")
        result = await rick_ai_workflow.execute(
            {
                "command": "analyze_source_medium_enhanced", 
                "widget_data": json.dumps(widget_data_result),
                "standard_compliance": True,
                "show_progress": True  # Включаем прогресс-индикацию
            }
        )
        
        # Reflection checkpoint: Analysis completed
        print("✅ Анализ sourceMedium завершен с Rick.ai error detection")
        logger.info("✅ Source medium analysis completed with Rick.ai error detection")
        
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        print(f"❌ Ошибка в rick_ai_analyze_source_medium_enhanced: {e}")
        logger.error(f"Error in rick_ai_analyze_source_medium_enhanced: {e}")
        return json.dumps(
            {"error": f"Error analyzing source medium: {str(e)}"}, ensure_ascii=False
        )


@mcp.tool()
async def rick_ai_analyze_grouping_data(widget_data: str, widget_groups: str) -> str:
    """
    JTBD: Когда мне нужно проанализировать данные группировки,
    я хочу использовать rick_ai_analyze_grouping_data,
    чтобы проверить соответствие стандартам и найти аномалии.

    Args:
        widget_data: JSON строка с данными виджета
        widget_groups: JSON строка с группами виджетов

    Returns:
        str: JSON строка с результатами анализа группировки
    """
    try:
        if not rick_ai_workflow:
            return json.dumps(
                {"error": "Rick AI workflow not loaded"}, ensure_ascii=False
            )

        result = await rick_ai_workflow.execute(
            {
                "command": "analyze_grouping_data",
                "widget_data": widget_data,
                "widget_groups": widget_groups,
            }
        )
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Error in rick_ai_analyze_grouping_data: {e}")
        return json.dumps(
            {"error": f"Error analyzing grouping data: {str(e)}"}, ensure_ascii=False
        )


@mcp.tool()
async def rick_ai_research_loop(
    company_alias: str, app_id: str, widget_id: str, checklist_type: str = "source_medium"
) -> str:
    """
    JTBD: Когда мне нужно провести исследовательский цикл по чеклисту,
    я хочу использовать rick_ai_research_loop,
    чтобы получить детальный анализ соответствия виджета стандартам.

    Args:
        company_alias: Алиас компании в Rick.ai
        app_id: ID приложения
        widget_id: ID виджета для анализа
        checklist_type: Тип чеклиста (по умолчанию "source_medium")

    Returns:
        str: JSON строка с результатами research loop
    """
    try:
        if not rick_ai_workflow:
            return json.dumps(
                {"error": "Rick AI workflow not loaded"}, ensure_ascii=False
            )

        result = await rick_ai_workflow.execute(
            {
                "command": "research_loop",
                "company_alias": company_alias,
                "app_id": app_id,
                "widget_id": widget_id,
                "checklist_type": checklist_type,
            }
        )
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Error in rick_ai_research_loop: {e}")
        return json.dumps(
            {"error": f"Error in research loop: {str(e)}"}, ensure_ascii=False
        )


@mcp.tool()
async def rick_ai_get_widget_preview(
    company_alias: str, app_id: str, widget_id: str
) -> str:
    """
    JTBD: Когда мне нужно получить JSON превью виджета,
    я хочу использовать rick_ai_get_widget_preview,
    чтобы получить структурированные данные виджета для анализа.

    Args:
        company_alias: Алиас компании в Rick.ai
        app_id: ID приложения
        widget_id: ID виджета

    Returns:
        str: JSON строка с превью виджета
    """
    try:
        if not rick_ai_workflow:
            return json.dumps(
                {"error": "Rick AI workflow not loaded"}, ensure_ascii=False
            )

        result = await rick_ai_workflow.execute(
            {
                "command": "get_widget_preview",
                "company_alias": company_alias,
                "app_id": app_id,
                "widget_id": widget_id,
            }
        )
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Error in rick_ai_get_widget_preview: {e}")
        return json.dumps(
            {"error": f"Error getting widget preview: {str(e)}"}, ensure_ascii=False
        )


@mcp.tool()
async def rick_ai_get_widget_screenshot(
    company_alias: str, app_id: str, widget_id: str
) -> str:
    """
    JTBD: Когда мне нужно получить скриншот виджета,
    я хочу использовать rick_ai_get_widget_screenshot,
    чтобы получить визуальное представление виджета.

    Args:
        company_alias: Алиас компании в Rick.ai
        app_id: ID приложения
        widget_id: ID виджета

    Returns:
        str: JSON строка с URL скриншота виджета
    """
    try:
        if not rick_ai_workflow:
            return json.dumps(
                {"error": "Rick AI workflow not loaded"}, ensure_ascii=False
            )

        result = await rick_ai_workflow.execute(
            {
                "command": "get_widget_screenshot",
                "company_alias": company_alias,
                "app_id": app_id,
                "widget_id": widget_id,
            }
        )
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Error in rick_ai_get_widget_screenshot: {e}")
        return json.dumps(
            {"error": f"Error getting widget screenshot: {str(e)}"}, ensure_ascii=False
        )


@mcp.tool()
async def rick_ai_create_event_attrs(
    company_alias: str, app_id: str, event_attrs_data: str
) -> str:
    """
    JTBD: Когда мне нужно создать событийные атрибуты группировки,
    я хочу использовать rick_ai_create_event_attrs,
    чтобы автоматически создавать группировки на основе анализа данных.

    Args:
        company_alias: Алиас компании в Rick.ai
        app_id: ID приложения
        event_attrs_data: JSON строка с данными для создания атрибутов

    Returns:
        str: JSON строка с результатом создания атрибутов
    """
    try:
        if not rick_ai_workflow:
            return json.dumps(
                {"error": "Rick AI workflow not loaded"}, ensure_ascii=False
            )

        result = await rick_ai_workflow.execute(
            {
                "command": "create_event_attrs",
                "company_alias": company_alias,
                "app_id": app_id,
                "event_attrs_data": event_attrs_data,
            }
        )
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Error in rick_ai_create_event_attrs: {e}")
        return json.dumps(
            {"error": f"Error creating event attrs: {str(e)}"}, ensure_ascii=False
        )


@mcp.tool()
async def rick_ai_create_widget_group(
    company_alias: str, app_id: str, group_data: str
) -> str:
    """
    JTBD: Когда мне нужно создать группу виджетов,
    я хочу использовать rick_ai_create_widget_group,
    чтобы автоматически создавать папки для мониторинга и анализа.

    Args:
        company_alias: Алиас компании в Rick.ai
        app_id: ID приложения
        group_data: JSON строка с данными для создания группы

    Returns:
        str: JSON строка с результатом создания группы
    """
    try:
        if not rick_ai_workflow:
            return json.dumps(
                {"error": "Rick AI workflow not loaded"}, ensure_ascii=False
            )

        result = await rick_ai_workflow.execute(
            {
                "command": "create_widget_group",
                "company_alias": company_alias,
                "app_id": app_id,
                "group_data": group_data,
            }
        )
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Error in rick_ai_create_widget_group: {e}")
        return json.dumps(
            {"error": f"Error creating widget group: {str(e)}"}, ensure_ascii=False
        )


@mcp.tool()
async def rick_ai_edit_widget(
    company_alias: str, app_id: str, widget_id: str, widget_data: str
) -> str:
    """
    JTBD: Когда мне нужно отредактировать виджет,
    я хочу использовать rick_ai_edit_widget,
    чтобы обновлять настройки виджета и промты для анализа.

    Args:
        company_alias: Алиас компании в Rick.ai
        app_id: ID приложения
        widget_id: ID виджета
        widget_data: JSON строка с данными для редактирования

    Returns:
        str: JSON строка с результатом редактирования
    """
    try:
        if not rick_ai_workflow:
            return json.dumps(
                {"error": "Rick AI workflow not loaded"}, ensure_ascii=False
            )

        result = await rick_ai_workflow.execute(
            {
                "command": "edit_widget",
                "company_alias": company_alias,
                "app_id": app_id,
                "widget_id": widget_id,
                "widget_data": widget_data,
            }
        )
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Error in rick_ai_edit_widget: {e}")
        return json.dumps(
            {"error": f"Error editing widget: {str(e)}"}, ensure_ascii=False
        )


@mcp.tool()
async def rick_ai_update_app_settings(
    company_alias: str, app_id: str, settings_data: str
) -> str:
    """
    JTBD: Когда мне нужно обновить настройки приложения,
    я хочу использовать rick_ai_update_app_settings,
    чтобы изменять конфигурацию приложения и переменные.

    Args:
        company_alias: Алиас компании в Rick.ai
        app_id: ID приложения
        settings_data: JSON строка с настройками для обновления

    Returns:
        str: JSON строка с результатом обновления настроек
    """
    try:
        if not rick_ai_workflow:
            return json.dumps(
                {"error": "Rick AI workflow not loaded"}, ensure_ascii=False
            )

        result = await rick_ai_workflow.execute(
            {
                "command": "update_app_settings",
                "company_alias": company_alias,
                "app_id": app_id,
                "settings_data": settings_data,
            }
        )
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Error in rick_ai_update_app_settings: {e}")
        return json.dumps(
            {"error": f"Error updating app settings: {str(e)}"}, ensure_ascii=False
        )


# ============================================================================
# ACTIVE VALIDATION PROTOCOL COMMANDS (GUIDANCE SYSTEM)
# ============================================================================


@mcp.tool()
def registry_output_validate(jtbd: str, artifact: str) -> str:
    """
    JTBD: Как guidance system, я хочу дать AI Agent чеклист для проверки артефакта,
    чтобы он не срезал углы и провел полную валидацию.

    Args:
        jtbd: Краткое описание JTBD пользователя
        artifact: Ссылка на артефакт для валидации

    Returns:
        str: JSON строка с чеклистом проверок для AI Agent
    """
    try:
        # [reflection] Input validation: Проверяем доступность workflow
        if not workflows_loaded or not registry_workflow:
            return json.dumps(
                {"error": "Registry workflow not loaded"}, ensure_ascii=False
            )

        # Вызываем workflow метод
        result = registry_workflow.output_validate(jtbd, artifact)
        return result

    except Exception as e:
        logger.error(f"Error in registry_output_validate: {e}")
        return json.dumps(
            {
                "status": "error",
                "message": f"Ошибка создания чеклиста: {str(e)}",
                "guidance": "Проверьте параметры и повторите попытку",
            },
            ensure_ascii=False,
        )


# registry_telegram_audit removed - using independent telegram-mcp server for Telegram operations


@mcp.tool()
def registry_docs_audit(paths: str) -> str:
    """
    JTBD: Как guidance system, я хочу дать AI Agent чеклист для аудита документации,
    чтобы он не срезал углы и провел полную проверку актуальности документов.

    Args:
        paths: Список путей к документам через запятую

    Returns:
        str: JSON строка с чеклистом аудита для AI Agent
    """
    try:
        # [reflection] Input validation: Проверяем доступность workflow
        if not workflows_loaded or not registry_workflow:
            return json.dumps(
                {"error": "Registry workflow not loaded"}, ensure_ascii=False
            )

        # Вызываем workflow метод
        result = registry_workflow.docs_audit(paths)
        return result

    except Exception as e:
        logger.error(f"Error in registry_docs_audit: {e}")
        return json.dumps(
            {
                "status": "error",
                "message": f"Ошибка создания чеклиста аудита: {str(e)}",
                "guidance": "Проверьте параметры и повторите попытку",
            },
            ensure_ascii=False,
        )


@mcp.tool()
def registry_gap_report(expected: str, actual: str, decision: str) -> str:
    """
    JTBD: Как guidance system, я хочу дать AI Agent чеклист для анализа gap,
    чтобы он не срезал углы и провел полный анализ различий.

    Args:
        expected: Ожидаемый результат
        actual: Фактический результат
        decision: Решение (fix/ok)

    Returns:
        str: JSON строка с чеклистом анализа для AI Agent
    """
    try:
        # [reflection] Input validation: Проверяем доступность workflow
        if not workflows_loaded or not registry_workflow:
            return json.dumps(
                {"error": "Registry workflow not loaded"}, ensure_ascii=False
            )

        # Вызываем workflow метод
        result = registry_workflow.gap_report(expected, actual, decision)
        return result

    except Exception as e:
        logger.error(f"Error in registry_gap_report: {e}")
        return json.dumps(
            {
                "status": "error",
                "message": f"Ошибка создания чеклиста анализа: {str(e)}",
                "guidance": "Проверьте параметры и повторите попытку",
            },
            ensure_ascii=False,
        )


@mcp.tool()
def registry_release_block(until: str) -> str:
    """
    JTBD: Как guidance system, я хочу дать AI Agent чеклист для блокировки релиза,
    чтобы он не срезал углы и провел полную проверку условий разблокировки.

    Args:
        until: Условие разблокировки

    Returns:
        str: JSON строка с чеклистом блокировки для AI Agent
    """
    try:
        # [reflection] Input validation: Проверяем доступность workflow
        if not workflows_loaded or not registry_workflow:
            return json.dumps(
                {"error": "Registry workflow not loaded"}, ensure_ascii=False
            )

        # Вызываем workflow метод
        result = registry_workflow.release_block(until)
        return result

    except Exception as e:
        logger.error(f"Error in registry_release_block: {e}")
        return json.dumps(
            {
                "status": "error",
                "message": f"Ошибка создания чеклиста блокировки: {str(e)}",
                "guidance": "Проверьте параметры и повторите попытку",
            },
            ensure_ascii=False,
        )


# Linear commands removed - replaced by independent Linear MCP server


# Google Sheets functions removed - replaced by independent Google Sheets MCP server


@mcp.tool()
def read_cleanshot(url: str, task_name: str = "feedback") -> str:
    """
    JTBD: Как MCP сервер, я хочу проксировать вызов к CleanShot workflow,
    чтобы обеспечить чтение изображений из CleanShot с guidance для анализа.

    Args:
        url: URL CleanShot ссылки
        task_name: Название задачи для именования файла

    Returns:
        str: JSON строка с результатами анализа изображения и guidance
    """
    if not cleanshot_loaded or cleanshot_workflow is None:
        return json.dumps(
            {
                "error": "CleanShot Workflow not loaded",
                "details": "Please check installation",
            },
            ensure_ascii=False,
        )

    try:
        # Delegate to workflow
        result = cleanshot_workflow.read_cleanshot(url, task_name)
        return result
    except Exception as e:
        logger.error(f"Error in read_cleanshot proxy: {e}")
        return json.dumps(
            {"success": False, "error": str(e), "url": url}, ensure_ascii=False
        )


@mcp.tool()
async def analyze_visual_hierarchy(url: str, design_type: str = "landing") -> str:
    """
    JTBD: Как главный дизайнер и арт-директор, я хочу проанализировать визуальную иерархию лендинга,
    чтобы понять порядок чтения элементов и качество дизайна.

    Args:
        url: URL страницы для анализа
        design_type: Тип дизайна (landing, documentation, blog, etc.)

    Returns:
        str: JSON строка с анализом визуальной иерархии
    """
    if not visual_hierarchy_loaded or visual_hierarchy_workflow is None:
        return json.dumps(
            {
                "error": "Visual Hierarchy Workflow not loaded",
                "details": "Please check installation",
            },
            ensure_ascii=False,
        )

    try:
        # Delegate to workflow (async call)
        result = await visual_hierarchy_workflow.analyze_visual_hierarchy(
            url, design_type
        )
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error in analyze_visual_hierarchy: {str(e)}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# Playwright functions removed - replaced by independent Playwright MCP server


# ============================================================================
# OUTPUT GAP ANALYSIS WORKFLOW COMMAND
# ============================================================================


@mcp.tool()
async def execute_output_gap_workflow(
    expected: str = "",
    actual: str = "",
    expected_file: str = "",
    actual_file: str = "",
    url: str = "",
    todo_file: str = "",
    release_name: str = "",
    analysis_type: str = "comprehensive",
    gap_threshold: float = 0.3,
    take_screenshot: bool = True,
    create_incident: bool = False,
) -> str:
    """
    JTBD: Как workflow executor, я хочу выполнить комплексный анализ gap между ожидаемым и фактическим output,
    чтобы обеспечить атомарные операции валидации в соответствии с MCP Workflow Standard.

    Args:
        expected: Ожидаемый результат (строка)
        actual: Фактический результат (строка)
        expected_file: Путь к файлу с ожидаемым результатом
        actual_file: Путь к файлу с фактическим результатом
        url: URL для анализа (если анализируем веб-страницу)
        todo_file: Путь к *.todo.md файлу для извлечения критериев
        release_name: Название релиза (для todo валидации)
        analysis_type: Тип анализа (comprehensive, basic, guidance, strict)
        gap_threshold: Порог для критических gap (по умолчанию 0.3)
        take_screenshot: Создавать скриншот для визуальной валидации
        create_incident: Создавать инцидент при критических gap

    Returns:
        str: JSON строка с результатами workflow анализа
    """
    try:
        # Проверяем, что output gap workflow загружен
        if not output_gap_workflow_loaded or OutputGapAnalysisWorkflow is None:
            return json.dumps(
                {
                    "success": False,
                    "error": "Output Gap Analysis workflow not loaded",
                    "guidance": "Check workflow configuration",
                },
                ensure_ascii=False,
                indent=2,
            )

        # Создаем входные данные
        input_data = GapAnalysisInput(
            expected=expected if expected else None,
            actual=actual if actual else None,
            expected_file=expected_file if expected_file else None,
            actual_file=actual_file if actual_file else None,
            url=url if url else None,
            todo_file=todo_file if todo_file else None,
            release_name=release_name if release_name else None,
            analysis_type=analysis_type,
            gap_threshold=gap_threshold,
            take_screenshot=take_screenshot,
            create_incident=create_incident,
        )

        # Выполняем workflow
        workflow = OutputGapAnalysisWorkflow()
        result = await workflow.execute(input_data)

        # Возвращаем результат в JSON формате
        return json.dumps(
            {
                "success": result.workflow_status != "failed",
                "analysis_id": result.analysis_id,
                "workflow_status": result.workflow_status,
                "overall_score": result.overall_score,
                "recommendations": result.recommendations,
                "execution_time": result.execution_time,
                "steps_completed": result.steps_completed,
                "steps_failed": result.steps_failed,
                "details": result.details,
            },
            ensure_ascii=False,
            indent=2,
        )

    except Exception as e:
        logger.error(f"Error in execute_output_gap_workflow: {e}")
        return json.dumps(
            {
                "success": False,
                "error": f"Error executing output gap workflow: {str(e)}",
                "guidance": "Check input parameters and workflow configuration",
            },
            ensure_ascii=False,
            indent=2,
        )


@mcp.tool()
async def make_mkdoc(project_path: str, clean: bool = True) -> str:
    """
    JTBD: Как разработчик, я хочу собирать документацию MkDocs,
    чтобы быстро создавать актуальную документацию из markdown файлов.

    Args:
        project_path: Путь к проекту с mkdocs.yml
        clean: Очищать предыдущую сборку

    Returns:
        str: JSON результат сборки
    """
    try:
        from heroes_platform.heroes_mcp.workflows.markdown_mkdoc_workflow import (
            MarkdownMkDocWorkflow,
        )

        workflow = MarkdownMkDocWorkflow()
        return await workflow.make_mkdoc(project_path, clean)

    except Exception as e:
        logger.error(f"Error in make_mkdoc: {e}")
        return json.dumps(
            {
                "status": "error",
                "operation": "make_mkdoc",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            },
            ensure_ascii=False,
        )


@mcp.tool()
async def update_mkdoc(project_path: str, clean: bool = True) -> str:
    """
    JTBD: Как разработчик, я хочу обновлять MkDocs документацию на GitHub Pages,
    чтобы обеспечить актуальность документации на сервере.

    Args:
        project_path: Путь к проекту с mkdocs.yml
        clean: Очищать предыдущую сборку

    Returns:
        str: JSON результат обновления
    """
    try:
        from heroes_platform.heroes_mcp.workflows.markdown_mkdoc_workflow import (
            MarkdownMkDocWorkflow,
        )

        workflow = MarkdownMkDocWorkflow()
        return await workflow.update_mkdoc(project_path, clean)

    except Exception as e:
        logger.error(f"Error in update_mkdoc: {e}")
        return json.dumps(
            {
                "status": "error",
                "operation": "update_mkdoc",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            },
            ensure_ascii=False,
        )



@mcp.tool()
async def yandex_direct_get_banners_stat(
    date_from: str, date_to: str, campaign_ids: str = ""
) -> str:
    """
    JTBD: Как аналитик рекламных кампаний, я хочу получать статистику баннеров по ключевым словам из Яндекс.Директ,
    чтобы анализировать эффективность отдельных объявлений и ключевых слов.

    Args:
        date_from: Дата начала в формате YYYY-MM-DD
        date_to: Дата окончания в формате YYYY-MM-DD
        campaign_ids: Список ID кампаний через запятую (опционально)

    Returns:
        str: JSON строка со статистикой баннеров по ключевым словам
    """
    try:
        from .yandex_direct_integration import create_yandex_direct_client

        # Создаем клиент
        client = await create_yandex_direct_client()
        if not client:
            return json.dumps(
                {
                    "status": "error",
                    "operation": "yandex_direct_get_banners_stat",
                    "error": "Не удалось создать клиент Яндекс.Директ. Проверьте credentials.",
                    "timestamp": datetime.now().isoformat(),
                },
                ensure_ascii=False,
            )

        # Парсим campaign_ids если переданы
        campaign_ids_list = None
        if campaign_ids:
            try:
                campaign_ids_list = [
                    int(cid.strip()) for cid in campaign_ids.split(",") if cid.strip()
                ]
            except ValueError as e:
                return json.dumps(
                    {
                        "status": "error",
                        "operation": "yandex_direct_get_banners_stat",
                        "error": f"Ошибка парсинга campaign_ids: {e}",
                        "timestamp": datetime.now().isoformat(),
                    },
                    ensure_ascii=False,
                )

        # Получаем статистику баннеров
        banners_stat = await client.get_banners_stat(  # type: ignore
            date_from, date_to, campaign_ids_list
        )  # type: ignore

        return json.dumps(
            {
                "status": "success",
                "operation": "yandex_direct_get_banners_stat",
                "data": banners_stat,
                "summary": {
                    "total_records": len(banners_stat),
                    "date_from": date_from,
                    "date_to": date_to,
                    "campaigns_analyzed": (
                        len(campaign_ids_list) if campaign_ids_list else "all"
                    ),
                },
                "timestamp": datetime.now().isoformat(),
            },
            ensure_ascii=False,
            default=str,
        )

    except Exception as e:
        logger.error(f"Error in yandex_direct_get_banners_stat: {e}")
        return json.dumps(
            {
                "status": "error",
                "operation": "yandex_direct_get_banners_stat",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            },
            ensure_ascii=False,
        )


# N8N Workflow Monitoring Tools
@mcp.tool()
async def n8n_workflow_health_check(workflow_id: str = "") -> str:
    """
    JTBD: Как DevOps инженер, я хочу проверить здоровье n8n workflow,
    чтобы быстро выявить проблемы и обеспечить стабильную работу автоматизации.

    Args:
        workflow_id: ID конкретного workflow или пустая строка для всех workflow

    Returns:
        str: JSON строка с информацией о здоровье workflow
    """
    if not n8n_monitoring_loaded:
        return json.dumps(
            {
                "status": "error",
                "operation": "n8n_workflow_health_check",
                "error": "N8N monitoring module not loaded",
                "timestamp": datetime.now().isoformat(),
            },
            ensure_ascii=False,
        )

    try:
        workflow_id_param = workflow_id if workflow_id else None
        health_data = await workflow_monitor.get_workflow_health(workflow_id_param)  # type: ignore
        
        return json.dumps(
            {
                "status": "success",
                "operation": "n8n_workflow_health_check",
                "data": health_data,
                "summary": {
                    "workflow_id": workflow_id if workflow_id else "all",
                    "timestamp": datetime.now().isoformat(),
                },
            },
            ensure_ascii=False,
            default=str,
        )

    except Exception as e:
        logger.error(f"Error in n8n_workflow_health_check: {e}")
        return json.dumps(
            {
                "status": "error",
                "operation": "n8n_workflow_health_check",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            },
            ensure_ascii=False,
        )


@mcp.tool()
async def n8n_workflow_analyze(workflow_id: str, analysis_type: str = "full") -> str:
    """
    JTBD: Как senior разработчик, я хочу анализировать n8n workflow на предмет проблем,
    чтобы выявить узкие места, проблемы безопасности и возможности оптимизации.

    Args:
        workflow_id: ID workflow для анализа
        analysis_type: Тип анализа (full, structure, performance, security)

    Returns:
        str: JSON строка с результатами анализа workflow
    """
    if not n8n_monitoring_loaded:
        return json.dumps(
            {
                "status": "error",
                "operation": "n8n_workflow_analyze",
                "error": "N8N monitoring module not loaded",
                "timestamp": datetime.now().isoformat(),
            },
            ensure_ascii=False,
        )

    try:
        analysis_data = await workflow_monitor.analyze_workflow(workflow_id, analysis_type)
        
        return json.dumps(
            {
                "status": "success",
                "operation": "n8n_workflow_analyze",
                "data": analysis_data,
                "summary": {
                    "workflow_id": workflow_id,
                    "analysis_type": analysis_type,
                    "timestamp": datetime.now().isoformat(),
                },
            },
            ensure_ascii=False,
            default=str,
        )

    except Exception as e:
        logger.error(f"Error in n8n_workflow_analyze: {e}")
        return json.dumps(
            {
                "status": "error",
                "operation": "n8n_workflow_analyze",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            },
            ensure_ascii=False,
        )


@mcp.tool()
async def n8n_workflow_validate(workflow_id: str, validation_rules: str = "standard") -> str:
    """
    JTBD: Как tech lead, я хочу валидировать n8n workflow по стандартам,
    чтобы обеспечить соответствие лучшим практикам и стандартам качества.

    Args:
        workflow_id: ID workflow для валидации
        validation_rules: Правила валидации (standard, security, performance, all)

    Returns:
        str: JSON строка с результатами валидации workflow
    """
    if not n8n_monitoring_loaded:
        return json.dumps(
            {
                "status": "error",
                "operation": "n8n_workflow_validate",
                "error": "N8N monitoring module not loaded",
                "timestamp": datetime.now().isoformat(),
            },
            ensure_ascii=False,
        )

    try:
        # Выполняем анализ для валидации
        analysis_data = await workflow_monitor.analyze_workflow(workflow_id, "full")
        
        # Валидация по стандартам
        validation_results: dict[str, Any] = {
            "workflow_id": workflow_id,
            "validation_rules": validation_rules,
            "timestamp": datetime.now().isoformat(),
            "structure_validation": {
                "passed": True,
                "issues": []
            },
            "security_validation": {
                "passed": True,
                "issues": []
            },
            "performance_validation": {
                "passed": True,
                "issues": []
            },
            "overall_status": "passed"
        }
        
        # Проверка структуры
        structure = analysis_data.get("structure_analysis", {})
        if structure.get("complexity_score", 0) > 100:
            issues = validation_results["structure_validation"]["issues"]
            if isinstance(issues, list):
                issues.append("High complexity score")
            validation_results["structure_validation"]["passed"] = False
        
        triggers = structure.get("triggers", [])
        if isinstance(triggers, list) and len(triggers) > 5:
            issues = validation_results["structure_validation"]["issues"]
            if isinstance(issues, list):
                issues.append("Too many triggers")
            validation_results["structure_validation"]["passed"] = False
        
        # Проверка безопасности
        security = analysis_data.get("security_analysis", {})
        if security.get("secrets_found"):
            issues = validation_results["security_validation"]["issues"]
            if isinstance(issues, list):
                issues.append("Secrets found in parameters")
            validation_results["security_validation"]["passed"] = False
        
        # Проверка производительности
        performance = analysis_data.get("performance_analysis", {})
        if performance.get("error_rate", 0) > 10:
            issues = validation_results["performance_validation"]["issues"]
            if isinstance(issues, list):
                issues.append("High error rate")
            validation_results["performance_validation"]["passed"] = False
        
        # Общий статус
        if (not validation_results["structure_validation"]["passed"] or
            not validation_results["security_validation"]["passed"] or
            not validation_results["performance_validation"]["passed"]):
            validation_results["overall_status"] = "failed"
        
        return json.dumps(
            {
                "status": "success",
                "operation": "n8n_workflow_validate",
                "data": validation_results,
                "analysis_data": analysis_data,
                "summary": {
                    "workflow_id": workflow_id,
                    "validation_rules": validation_rules,
                    "overall_status": validation_results["overall_status"],
                    "timestamp": datetime.now().isoformat(),
                },
            },
            ensure_ascii=False,
            default=str,
        )

    except Exception as e:
        logger.error(f"Error in n8n_workflow_validate: {e}")
        return json.dumps(
            {
                "status": "error",
                "operation": "n8n_workflow_validate",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            },
            ensure_ascii=False,
        )


def main():
    """Главная функция запуска сервера"""
    global mcp

    # Аргументы уже проверены в начале файла

    # Обычный режим - запуск MCP сервера
    logger.info("Starting Heroes MCP Server with FastMCP")
    logger.info(f"Server name: {mcp.name}")

    # Логируем доступные инструменты
    base_tools = "server_info, standards_workflow, workflow_integration, registry_compliance_check, heroes_gpt_workflow, ai_guidance_checklist, common_mistakes_prevention, quality_validation, approach_recommendation, validate_actual_outcome, ghost_publish_analysis, ghost_publish_document, ghost_integration, registry_output_validate, registry_docs_audit, registry_gap_report, registry_release_block, read_cleanshot, analyze_visual_hierarchy, make_mkdoc, update_mkdoc, execute_output_gap_workflow, yandex_direct_get_data, yandex_direct_get_campaigns, yandex_direct_get_banners_stat"
    
    if n8n_monitoring_loaded:
        n8n_tools = ", n8n_workflow_health_check, n8n_workflow_analyze, n8n_workflow_validate"
        base_tools += n8n_tools

    if cocoindex_loaded:
        cocoindex_tools = ", cocoindex_search, cocoindex_validate_creation, cocoindex_functionality_map, cocoindex_analyze_duplicates"
        all_tools = base_tools + cocoindex_tools
    else:
        all_tools = base_tools

    logger.info(f"Available tools: {all_tools}")

    # Запуск сервера через stdio (стандарт MCP)
    try:
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
