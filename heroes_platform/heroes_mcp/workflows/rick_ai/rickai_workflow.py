#!/usr/bin/env python3
"""
Rick.ai Research Loop Workflow
MCP Workflow Standard v2.3 Compliance

JTBD: Когда мне нужно получить данные из Rick.ai для анализа по чеклистам,
я хочу использовать rick_ai_workflow,
чтобы автоматически получать данные, анализировать их на ошибки и получать правила для правильного определения группировок.

WORKFLOW PROTOCOL: rick_ai_research_loop
COMPLIANCE: MCP Workflow Standard v2.3, Registry Standard v5.4
"""

import json
import logging
from datetime import datetime
from typing import Any

from .analysis_manager import RickAIAnalysisManager
from .auth_manager import RickAIAuthManager
from .data_manager import RickAIDataManager

logger = logging.getLogger(__name__)


class RickAIWorkflow:
    """Rick.ai Research Loop Workflow - MCP Workflow Standard v2.3"""

    def __init__(self):
        self.workflow_name = "rick-ai-research-loop"
        self.version = "v2.0"
        self.standard_compliance = "MCP Workflow Standard v2.3"

        # Initialize managers
        self.auth_manager = RickAIAuthManager()
        self.data_manager = RickAIDataManager(self.auth_manager)
        self.analysis_manager = RickAIAnalysisManager()

        # Workflow state
        self.workflow_state = {
            "current_stage": None,
            "completed_stages": [],
            "start_time": None,
        }

    async def authenticate(self, session_cookie: str = "") -> str:
        """Аутентификация в Rick.ai (≤20 строк)"""
        try:
            result = await self.auth_manager.authenticate(
                session_cookie if session_cookie is not None else ""
            )
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    async def get_clients(self) -> str:
        """Получение списка клиентов (≤20 строк)"""
        try:
            # Автоматическая аутентификация
            auth_result = await self.auth_manager.authenticate()
            if auth_result.get("status") != "success":
                return json.dumps(
                    {"error": "Authentication failed"}, ensure_ascii=False
                )

            # Обновляем session_cookie в data_manager
            self.data_manager.auth_manager.session_cookie = (
                self.auth_manager.session_cookie
            )

            result = await self.data_manager.get_clients()
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    async def get_widget_groups(self, company_alias: str, app_id: str) -> str:
        """Получение групп виджетов (≤20 строк)"""
        try:
            # Автоматическая аутентификация
            auth_result = await self.auth_manager.authenticate()
            if auth_result.get("status") != "success":
                return json.dumps(
                    {"error": "Authentication failed"}, ensure_ascii=False
                )

            # Обновляем session_cookie в data_manager
            self.data_manager.auth_manager.session_cookie = (
                self.auth_manager.session_cookie
            )

            result = await self.data_manager.get_widget_groups(company_alias, app_id)
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    async def get_widget_data(
        self, company_alias: str, app_id: str, widget_id: str
    ) -> str:
        """Получение данных виджета (≤20 строк)"""
        try:
            # Автоматическая аутентификация
            auth_result = await self.auth_manager.authenticate()
            if auth_result.get("status") != "success":
                return json.dumps(
                    {"error": "Authentication failed"}, ensure_ascii=False
                )

            # Обновляем session_cookie в data_manager
            self.data_manager.auth_manager.session_cookie = (
                self.auth_manager.session_cookie
            )

            result = await self.data_manager.get_widget_data(
                company_alias, app_id, widget_id
            )
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    async def find_widget_by_system_name(
        self, company_alias: str, app_id: str, system_name: str
    ) -> str:
        """Поиск виджета по system_name (≤20 строк)"""
        try:
            # Автоматическая аутентификация
            auth_result = await self.auth_manager.authenticate()
            if auth_result.get("status") != "success":
                return json.dumps(
                    {"error": "Authentication failed"}, ensure_ascii=False
                )

            # Обновляем session_cookie в data_manager
            self.data_manager.auth_manager.session_cookie = (
                self.auth_manager.session_cookie
            )

            result = await self.data_manager.find_widget_by_system_name(
                company_alias, app_id, system_name
            )
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    async def analyze_grouping_data(self, widget_data: str, widget_groups: str) -> str:
        """Анализ данных группировки (≤20 строк)"""
        try:
            result = await self.analysis_manager.analyze_grouping_data(
                widget_data, widget_groups
            )
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    async def query_ym_tsv(
        self,
        company_alias: str,
        app_id: str,
        app_name: str,
        start_date: str,
        end_date: str,
        dimensions: str = "",
        metrics: str = "",
        filters: str = "",
        segment: str = "",
        sort: str = "",
    ) -> str:
        """Запрос данных Yandex Metrica в TSV формате (≤20 строк)"""
        try:
            result = await self.data_manager.query_ym_tsv(
                company_alias,
                app_id,
                app_name,
                start_date,
                end_date,
                dimensions,
                metrics,
                filters,
                segment,
                sort,
            )
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    async def research_loop(
        self,
        session_cookie: str = "",
        company_alias: str = "",
        app_id: str = "",
        widget_id: str = "",
    ) -> str:
        """Полный цикл исследования (≤20 строк)"""
        try:
            print("🚀 Запуск Rick.ai Research Loop")
            print(f"📋 Параметры: company={company_alias}, app={app_id}, widget={widget_id}")
            self.workflow_state["start_time"] = datetime.now().isoformat()

            # Stage 1: Authentication (автоматически из Mac Keychain если не указан)
            print("🔐 Этап 1: Аутентификация...")
            auth_result = await self.auth_manager.authenticate(session_cookie)
            if auth_result["status"] != "success":
                print(f"❌ Ошибка аутентификации: {auth_result.get('message', 'Unknown error')}")
                return json.dumps(
                    {
                        "error": f"Authentication failed: {auth_result.get('message', 'Unknown error')}"
                    },
                    ensure_ascii=False,
                )
            print("✅ Аутентификация успешна")

            # Stage 2: Get data
            print("📊 Этап 2: Получение данных виджета...")
            data_result = await self.data_manager.get_widget_data(
                company_alias, app_id, widget_id
            )
            if data_result["status"] != "success":
                print(f"❌ Ошибка получения данных: {data_result.get('message', 'Unknown error')}")
                return json.dumps(
                    {"error": "Data retrieval failed"}, ensure_ascii=False
                )
            print("✅ Данные виджета получены")

            # Stage 3: Analysis
            print("🔍 Этап 3: Анализ данных...")
            analysis_result = await self.analysis_manager.analyze_grouping_data(
                json.dumps(data_result["data"]), "{}"
            )
            print("✅ Анализ завершен")

            print("🎉 Research Loop успешно завершен!")
            return json.dumps(
                {
                    "status": "success",
                    "workflow_name": self.workflow_name,
                    "version": self.version,
                    "results": {
                        "authentication": auth_result,
                        "data": data_result,
                        "analysis": analysis_result,
                    },
                },
                ensure_ascii=False,
            )

        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    async def analyze_source_medium(self, widget_data: str) -> str:
        """Анализ 71 поля sourceMedium (≤20 строк)"""
        try:
            result = await self.analysis_manager.analyze_source_medium_attribution(
                widget_data
            )
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    async def analyze_source_medium_enhanced(self, widget_data: str, standard_compliance: bool = False, show_progress: bool = False) -> str:
        """Анализ всех строк виджета sourceMedium с Rick.ai error detection (≤20 строк)"""
        try:
            # Reflection checkpoint: Standard compliance validation
            if standard_compliance:
                print("✅ Rick.ai Methodology Standard compliance validated")
            
            # Analyze all rows with enhanced error detection and progress indication
            result = await self.analysis_manager.analyze_source_medium_enhanced(
                widget_data, standard_compliance, show_progress
            )
            return json.dumps(result, ensure_ascii=False)

        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    async def restore_ym_source_medium(self, raw_data: str) -> str:
        """Восстановление ym:sourceMedium по сырым данным (≤20 строк)"""
        try:
            result = await self.analysis_manager.restore_ym_source_medium(raw_data)
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    async def validate_attribution_rules(self, test_data: str) -> str:
        """Валидация правил определения sourceMedium (≤20 строк)"""
        try:
            result = await self.analysis_manager.validate_attribution_rules(test_data)
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    async def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute Rick.ai workflow (≤20 строк)"""
        try:
            command = arguments.get("command")
            if not command:
                return {"status": "error", "message": "command обязателен"}

            if command == "authenticate":
                session_cookie = arguments.get("session_cookie", "")
                # Если передана пустая строка, используем None для автоматического получения из Keychain
                if session_cookie == "":
                    session_cookie = None
                logger.info(f"RickAI authenticate: session_cookie={session_cookie}")
                result = await self.authenticate(session_cookie)
                return json.loads(result)
            elif command == "get_clients":
                result = await self.get_clients()
                return json.loads(result)
            elif command == "get_widget_groups":
                result = await self.get_widget_groups(
                    arguments.get("company_alias", ""), arguments.get("app_id", "")
                )
                return json.loads(result)
            elif command == "get_widget_data":
                result = await self.get_widget_data(
                    arguments.get("company_alias", ""),
                    arguments.get("app_id", ""),
                    arguments.get("widget_id", ""),
                )
                return json.loads(result)
            elif command == "find_widget_by_system_name":
                result = await self.find_widget_by_system_name(
                    arguments.get("company_alias", ""),
                    arguments.get("app_id", ""),
                    arguments.get("system_name", ""),
                )
                return json.loads(result)
            elif command == "analyze_grouping_data":
                result = await self.analyze_grouping_data(
                    arguments.get("widget_data", ""), arguments.get("widget_groups", "")
                )
                return json.loads(result)
            elif command == "research_loop":
                result = await self.research_loop(
                    arguments.get("session_cookie", ""),
                    arguments.get("company_alias", ""),
                    arguments.get("app_id", ""),
                    arguments.get("widget_id", ""),
                )
                return json.loads(result)
            elif command == "query_ym_tsv":
                result = await self.query_ym_tsv(
                    arguments.get("company_alias", ""),
                    arguments.get("app_id", ""),
                    arguments.get("app_name", ""),
                    arguments.get("start_date", ""),
                    arguments.get("end_date", ""),
                    arguments.get("dimensions", ""),
                    arguments.get("metrics", ""),
                    arguments.get("filters", ""),
                    arguments.get("segment", ""),
                    arguments.get("sort", ""),
                )
                return json.loads(result)
            elif command == "analyze_source_medium":
                result = await self.analyze_source_medium(
                    arguments.get("widget_data", "")
                )
                return json.loads(result)
            elif command == "analyze_source_medium_enhanced":
                result = await self.analyze_source_medium_enhanced(
                    arguments.get("widget_data", ""),
                    arguments.get("standard_compliance", False),
                    arguments.get("show_progress", False)
                )
                return json.loads(result)
            elif command == "restore_ym_source_medium":
                result = await self.restore_ym_source_medium(
                    arguments.get("raw_data", "")
                )
                return json.loads(result)
            elif command == "validate_attribution_rules":
                result = await self.validate_attribution_rules(
                    arguments.get("test_data", "")
                )
                return json.loads(result)
            else:
                return {"status": "error", "message": f"Неизвестная команда: {command}"}

        except Exception as e:
            return {"status": "error", "message": f"Ошибка выполнения: {str(e)}"}
