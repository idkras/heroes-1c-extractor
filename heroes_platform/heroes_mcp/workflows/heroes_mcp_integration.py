#!/usr/bin/env python3
"""
Heroes MCP Integration
Интеграция HeroesGPT с MCP системой

JTBD: Я хочу интегрировать HeroesGPT анализ лендингов с MCP системой,
чтобы обеспечить единый интерфейс для запуска и получения результатов анализа.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class HeroesMCPIntegration:
    """Интеграция HeroesGPT с MCP системой"""

    def __init__(self):
        self.standard_version = "v1.8"
        self.mcp_commands = [
            "heroes_analyze_landing",
            "heroes_generate_report",
            "heroes_validate_analysis",
            "heroes_get_recommendations"
        ]

    async def handle_heroes_analyze_landing(
        self,
        landing_url: str,
        business_context: Dict[str, Any],
        analysis_depth: str = "full"
    ) -> Dict[str, Any]:
        """Обрабатывает MCP команду анализа лендинга

        Args:
            landing_url: URL лендинга для анализа
            business_context: Контекст бизнеса
            analysis_depth: Глубина анализа

        Returns:
            Результат анализа в формате MCP
        """
        try:
            logger.info(f"🚀 MCP: Starting HeroesGPT analysis for {landing_url}")

            # Импортируем и запускаем основной workflow
            from .heroes_gpt_landing_analysis import analyze_landing_mcp
            
            # Подготавливаем входные данные
            input_data = {
                "url": landing_url,
                "landing_url": landing_url,
                "business_context": business_context,
                "analysis_depth": analysis_depth
            }

            # Выполняем анализ
            analysis_result = await analyze_landing_mcp(input_data)

            # Форматируем результат для MCP
            mcp_result = await self._format_analysis_result_for_mcp(analysis_result)

            logger.info(f"✅ MCP: HeroesGPT analysis completed for {landing_url}")
            return mcp_result

        except Exception as e:
            logger.error(f"Error in handle_heroes_analyze_landing: {e}")
            return await self._format_error_for_mcp(str(e))

    async def handle_heroes_generate_report(
        self,
        analysis_data: Dict[str, Any],
        report_format: str = "markdown"
    ) -> Dict[str, Any]:
        """Обрабатывает MCP команду генерации отчета

        Args:
            analysis_data: Данные анализа
            report_format: Формат отчета

        Returns:
            Сгенерированный отчет в формате MCP
        """
        try:
            logger.info("📄 MCP: Generating HeroesGPT report")

            # Импортируем и используем document builder
            from .heroes_gpt_document_builder import HeroesGPTDocumentBuilder
            
            builder = HeroesGPTDocumentBuilder()
            
            if report_format == "markdown":
                report_content = builder.generate_markdown_document(analysis_data)
            else:
                report_content = builder.generate_quick_summary(analysis_data)

            # Форматируем результат для MCP
            mcp_result = {
                "success": True,
                "command": "heroes_generate_report",
                "report_format": report_format,
                "report_content": report_content,
                "report_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "analysis_url": analysis_data.get("landing_url", "Unknown"),
                    "standard_version": self.standard_version
                },
                "timestamp": datetime.now().isoformat()
            }

            logger.info("✅ MCP: Report generated successfully")
            return mcp_result

        except Exception as e:
            logger.error(f"Error in handle_heroes_generate_report: {e}")
            return await self._format_error_for_mcp(str(e))

    async def handle_heroes_validate_analysis(
        self,
        analysis_data: Dict[str, Any],
        validation_standard: str = "Ilya Krasinsky Review Standard v1.2"
    ) -> Dict[str, Any]:
        """Обрабатывает MCP команду валидации анализа

        Args:
            analysis_data: Данные анализа
            validation_standard: Стандарт валидации

        Returns:
            Результат валидации в формате MCP
        """
        try:
            logger.info("🔍 MCP: Validating HeroesGPT analysis")

            # Импортируем и используем expert review
            from .expert_review import execute_expert_review_mcp
            
            validation_result = await execute_expert_review_mcp(
                analysis_data, validation_standard
            )

            # Форматируем результат для MCP
            mcp_result = {
                "success": True,
                "command": "heroes_validate_analysis",
                "validation_standard": validation_standard,
                "validation_result": validation_result,
                "validation_metadata": {
                    "validated_at": datetime.now().isoformat(),
                    "analysis_url": analysis_data.get("landing_url", "Unknown"),
                    "standard_version": self.standard_version
                },
                "timestamp": datetime.now().isoformat()
            }

            logger.info("✅ MCP: Analysis validation completed")
            return mcp_result

        except Exception as e:
            logger.error(f"Error in handle_heroes_validate_analysis: {e}")
            return await self._format_error_for_mcp(str(e))

    async def handle_heroes_get_recommendations(
        self,
        analysis_data: Dict[str, Any],
        recommendation_type: str = "all"
    ) -> Dict[str, Any]:
        """Обрабатывает MCP команду получения рекомендаций

        Args:
            analysis_data: Данные анализа
            recommendation_type: Тип рекомендаций

        Returns:
            Рекомендации в формате MCP
        """
        try:
            logger.info("💡 MCP: Getting HeroesGPT recommendations")

            # Генерируем рекомендации на основе анализа
            recommendations = await self._generate_recommendations(
                analysis_data, recommendation_type
            )

            # Форматируем результат для MCP
            mcp_result = {
                "success": True,
                "command": "heroes_get_recommendations",
                "recommendation_type": recommendation_type,
                "recommendations": recommendations,
                "recommendations_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "analysis_url": analysis_data.get("landing_url", "Unknown"),
                    "recommendations_count": len(recommendations),
                    "standard_version": self.standard_version
                },
                "timestamp": datetime.now().isoformat()
            }

            logger.info(f"✅ MCP: Generated {len(recommendations)} recommendations")
            return mcp_result

        except Exception as e:
            logger.error(f"Error in handle_heroes_get_recommendations: {e}")
            return await self._format_error_for_mcp(str(e))

    async def _format_analysis_result_for_mcp(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Форматирует результат анализа для MCP"""
        
        if not analysis_result.get("success", False):
            return await self._format_error_for_mcp(analysis_result.get("error", "Unknown error"))

        data = analysis_result.get("data", {})
        
        return {
            "success": True,
            "command": "heroes_analyze_landing",
            "analysis_result": {
                "landing_url": data.get("landing_url", "Unknown"),
                "business_context": data.get("business_context", {}),
                "analysis_depth": data.get("analysis_depth", "full"),
                "stages_completed": len([s for s in data.get("stages", {}).values() if s.get("completed", False)]),
                "offers_found": len(data.get("offers", [])),
                "segments_identified": len(data.get("segments", [])),
                "reflection_checkpoints": len(data.get("reflections", [])),
                "workflow_version": data.get("workflow_version", self.standard_version)
            },
            "analysis_metadata": {
                "analyzed_at": datetime.now().isoformat(),
                "workflow_id": data.get("workflow_id", "unknown"),
                "standard_version": self.standard_version,
                "analysis_status": "completed"
            },
            "timestamp": datetime.now().isoformat()
        }

    async def _format_error_for_mcp(self, error_message: str) -> Dict[str, Any]:
        """Форматирует ошибку для MCP"""
        
        return {
            "success": False,
            "error": error_message,
            "error_metadata": {
                "error_type": "HeroesGPT Analysis Error",
                "occurred_at": datetime.now().isoformat(),
                "standard_version": self.standard_version
            },
            "timestamp": datetime.now().isoformat()
        }

    async def _generate_recommendations(
        self, analysis_data: Dict[str, Any], recommendation_type: str
    ) -> List[Dict[str, Any]]:
        """Генерирует рекомендации на основе анализа"""
        
        recommendations = []
        
        # Базовые рекомендации
        if recommendation_type in ["all", "basic"]:
            recommendations.extend([
                {
                    "type": "basic",
                    "title": "Провести A/B тестирование",
                    "description": "Протестировать различные варианты предложений",
                    "priority": "high",
                    "category": "testing"
                },
                {
                    "type": "basic",
                    "title": "Мониторить метрики конверсии",
                    "description": "Отслеживать эффективность изменений",
                    "priority": "high",
                    "category": "monitoring"
                }
            ])
        
        # Рекомендации по предложениям
        if recommendation_type in ["all", "offers"]:
            offers = analysis_data.get("offers", [])
            if len(offers) < 3:
                recommendations.append({
                    "type": "offers",
                    "title": "Добавить больше предложений",
                    "description": f"Найдено только {len(offers)} предложений, рекомендуется минимум 3",
                    "priority": "medium",
                    "category": "content"
                })
        
        # Рекомендации по сегментам
        if recommendation_type in ["all", "segments"]:
            segments = analysis_data.get("segments", [])
            if len(segments) < 2:
                recommendations.append({
                    "type": "segments",
                    "title": "Улучшить сегментацию",
                    "description": f"Выявлено только {len(segments)} сегментов, рекомендуется минимум 2",
                    "priority": "medium",
                    "category": "targeting"
                })
        
        # Рекомендации по рефлексии
        if recommendation_type in ["all", "reflection"]:
            reflections = analysis_data.get("reflections", [])
            if len(reflections) < 3:
                recommendations.append({
                    "type": "reflection",
                    "title": "Увеличить рефлексивность",
                    "description": f"Создано только {len(reflections)} reflection checkpoints, рекомендуется минимум 3",
                    "priority": "low",
                    "category": "process"
                })
        
        return recommendations

    async def get_mcp_command_info(self, command: str) -> Dict[str, Any]:
        """Возвращает информацию о MCP команде"""
        
        command_info = {
            "heroes_analyze_landing": {
                "description": "Анализ лендинга через HeroesGPT",
                "parameters": {
                    "landing_url": {"type": "string", "required": True, "description": "URL лендинга для анализа"},
                    "business_context": {"type": "object", "required": True, "description": "Контекст бизнеса"},
                    "analysis_depth": {"type": "string", "required": False, "default": "full", "description": "Глубина анализа"}
                },
                "returns": "Результат анализа лендинга"
            },
            "heroes_generate_report": {
                "description": "Генерация отчета по результатам анализа",
                "parameters": {
                    "analysis_data": {"type": "object", "required": True, "description": "Данные анализа"},
                    "report_format": {"type": "string", "required": False, "default": "markdown", "description": "Формат отчета"}
                },
                "returns": "Сгенерированный отчет"
            },
            "heroes_validate_analysis": {
                "description": "Валидация анализа по стандартам",
                "parameters": {
                    "analysis_data": {"type": "object", "required": True, "description": "Данные анализа"},
                    "validation_standard": {"type": "string", "required": False, "default": "Ilya Krasinsky Review Standard v1.2", "description": "Стандарт валидации"}
                },
                "returns": "Результат валидации"
            },
            "heroes_get_recommendations": {
                "description": "Получение рекомендаций на основе анализа",
                "parameters": {
                    "analysis_data": {"type": "object", "required": True, "description": "Данные анализа"},
                    "recommendation_type": {"type": "string", "required": False, "default": "all", "description": "Тип рекомендаций"}
                },
                "returns": "Список рекомендаций"
            }
        }
        
        return command_info.get(command, {"error": f"Unknown command: {command}"})

    async def list_available_commands(self) -> Dict[str, Any]:
        """Возвращает список доступных MCP команд"""
        
        return {
            "success": True,
            "available_commands": self.mcp_commands,
            "commands_info": {cmd: await self.get_mcp_command_info(cmd) for cmd in self.mcp_commands},
            "integration_version": self.standard_version,
            "timestamp": datetime.now().isoformat()
        }


# MCP Command Interface Functions
async def execute_heroes_mcp_command(
    command: str,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """Выполняет MCP команду HeroesGPT

    Args:
        command: Название команды
        parameters: Параметры команды

    Returns:
        Результат выполнения команды
    """
    try:
        integration = HeroesMCPIntegration()
        
        if command == "heroes_analyze_landing":
            return await integration.handle_heroes_analyze_landing(
                parameters.get("landing_url", ""),
                parameters.get("business_context", {}),
                parameters.get("analysis_depth", "full")
            )
        
        elif command == "heroes_generate_report":
            return await integration.handle_heroes_generate_report(
                parameters.get("analysis_data", {}),
                parameters.get("report_format", "markdown")
            )
        
        elif command == "heroes_validate_analysis":
            return await integration.handle_heroes_validate_analysis(
                parameters.get("analysis_data", {}),
                parameters.get("validation_standard", "Ilya Krasinsky Review Standard v1.2")
            )
        
        elif command == "heroes_get_recommendations":
            return await integration.handle_heroes_get_recommendations(
                parameters.get("analysis_data", {}),
                parameters.get("recommendation_type", "all")
            )
        
        elif command == "list_commands":
            return await integration.list_available_commands()
        
        else:
            return {
                "success": False,
                "error": f"Unknown command: {command}",
                "available_commands": integration.mcp_commands,
                "timestamp": datetime.now().isoformat()
            }

    except Exception as e:
        logger.error(f"Error in execute_heroes_mcp_command: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


def main():
    """Основная функция для тестирования"""
    async def test_mcp_integration():
        # Тестируем список команд
        commands_result = await execute_heroes_mcp_command("list_commands", {})
        print(f"Available commands: {commands_result['success']}")
        
        # Тестируем анализ лендинга
        analysis_result = await execute_heroes_mcp_command("heroes_analyze_landing", {
            "landing_url": "https://test.com",
            "business_context": {"type": "saas", "target_audience": "b2b"},
            "analysis_depth": "full"
        })
        print(f"Analysis result: {analysis_result['success']}")
        
        # Тестируем получение рекомендаций
        if analysis_result["success"]:
            recommendations_result = await execute_heroes_mcp_command("heroes_get_recommendations", {
                "analysis_data": analysis_result["analysis_result"],
                "recommendation_type": "all"
            })
            print(f"Recommendations result: {recommendations_result['success']}")

    asyncio.run(test_mcp_integration())


if __name__ == "__main__":
    main()
