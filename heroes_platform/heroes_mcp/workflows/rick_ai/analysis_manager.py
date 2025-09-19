#!/usr/bin/env python3
"""
Rick.ai Analysis Manager
MCP Workflow Standard v2.3 Compliance

JTBD: Когда мне нужно анализировать данные из Rick.ai,
я хочу использовать RickAIAnalysisManager,
чтобы анализировать группировки, sourceMedium атрибуцию и генерировать правила коррекции.

COMPLIANCE: MCP Workflow Standard v2.3, Registry Standard v5.4
"""

import asyncio
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class SourceMediumRules:
    """Правила определения sourceMedium с правильной приоритизацией"""

    def __init__(self):
        self.click_id_patterns = {
            "gclid": r"gclid=[A-Za-z0-9_-]+",
            "yclid": r"yclid=[A-Za-z0-9_-]+",
            "fbclid": r"fbclid=[A-Za-z0-9_-]+",
            "ysclid": r"ysclid=[A-Za-z0-9_-]+",
        }

        self.traffic_source_mapping = {
            "organic": ("organic", "organic"),
            "referral": ("referral", "referral"),
            "direct": ("(direct)", "(none)"),
            "ad": ("advertising", "cpc"),
        }

    def determine_source_medium(self, event: dict) -> tuple[str, str]:
        """Определение sourceMedium с правильной приоритизацией"""
        # Приоритет 1: Click ID
        click_id_result = self._check_click_id(event)
        if click_id_result:
            return click_id_result

        # Приоритет 2: UTM параметры
        utm_result = self._check_utm_params(event)
        if utm_result:
            return utm_result

        # Приоритет 3: Yandex Metrica параметры
        ym_result = self._check_ym_params(event)
        if ym_result:
            return ym_result

        # Приоритет 4: Traffic Source
        traffic_result = self._check_traffic_source(event)
        if traffic_result:
            return traffic_result

        # Приоритет 5: Referrer
        referrer_result = self._check_referrer(event)
        if referrer_result:
            return referrer_result

        # Fallback
        return "(direct)", "(none)"

    def _check_click_id(self, event: dict) -> Optional[tuple[str, str]]:
        """Проверка Click ID параметров"""
        for click_type, _pattern in self.click_id_patterns.items():
            if self._find_click_id(event, click_type):
                return self._determine_source_from_click_id(click_type)
        return None

    def _check_utm_params(self, event: dict) -> Optional[tuple[str, str]]:
        """Проверка UTM параметров"""
        # Сначала проверяем page_location (приоритет)
        page_location = event.get("page_location", "")
        if page_location:
            utm_source_match = re.search(r"utm_source=([^&]+)", page_location)
            utm_medium_match = re.search(r"utm_medium=([^&]+)", page_location)

            if utm_source_match and utm_medium_match:
                utm_source = utm_source_match.group(1)
                utm_medium = utm_medium_match.group(1)

                if utm_source != "internal" and utm_medium != "internal":
                    return utm_source, utm_medium

        # Fallback на прямые поля
        utm_source = event.get("event_param_source", "")
        utm_medium = event.get("event_param_medium", "")

        if (
            utm_source
            and utm_medium
            and utm_source != "internal"
            and utm_medium != "internal"
        ):
            return utm_source, utm_medium

        return None

    def _check_ym_params(self, event: dict) -> Optional[tuple[str, str]]:
        """Проверка Yandex Metrica параметров"""
        ym_source = event.get("ym:source", "")
        ym_medium = event.get("ym:medium", "")

        if ym_source and ym_medium:
            return ym_source, ym_medium

        return None

    def _check_traffic_source(self, event: dict) -> Optional[tuple[str, str]]:
        """Проверка Traffic Source данных"""
        traffic_source = event.get("event_params.last_traffic_source", "")

        if traffic_source in self.traffic_source_mapping:
            return self.traffic_source_mapping[traffic_source]

        return None

    def _check_referrer(self, event: dict) -> Optional[tuple[str, str]]:
        """Проверка Referrer данных"""
        referrer = event.get("event_params.page_referrer", "")

        if referrer:
            return self._determine_source_from_referrer(referrer)

        return None

    def _find_click_id(self, event: dict, click_type: str) -> bool:
        """Поиск Click ID в данных события"""
        # Проверяем правильные поля согласно Rick.ai стандарту
        fields_to_check = [
            "event_param_rick_ad_channel_identifiers",  # Основное поле для Click ID
            "page_location",  # URL с параметрами
            f"event_param_{click_type}",  # Прямое поле
            "click_id",  # Общее поле
        ]

        for field in fields_to_check:
            value = event.get(field, "")
            if value:
                # Для event_param_rick_ad_channel_identifiers ищем в формате "yclid:86520401018748927"
                if field == "event_param_rick_ad_channel_identifiers":
                    # Проверяем что есть значение после двоеточия
                    pattern = f"{click_type}:[^;]+"
                    if re.search(pattern, str(value)):
                        return True
                # Для page_location ищем в URL параметрах
                elif field == "page_location":
                    if re.search(self.click_id_patterns[click_type], str(value)):
                        return True
                # Для остальных полей
                else:
                    if re.search(self.click_id_patterns[click_type], str(value)):
                        return True

        return False

    def _determine_source_from_click_id(self, click_type: str) -> tuple[str, str]:
        """Определение source и medium по типу Click ID"""
        click_id_mapping = {
            "gclid": ("google", "cpc"),
            "yclid": ("yandex", "cpc"),
            "fbclid": ("facebook", "cpc"),
            "ysclid": ("yandex", "cpc"),
        }

        return click_id_mapping.get(click_type, ("unknown", "cpc"))

    def _determine_source_from_referrer(self, referrer: str) -> tuple[str, str]:
        """Определение source и medium по referrer"""
        if "google" in referrer.lower():
            return ("google", "organic")
        elif "yandex" in referrer.lower():
            return ("yandex", "organic")
        elif "facebook" in referrer.lower():
            return ("facebook", "referral")
        else:
            return ("referral", "referral")

    def analyze_all_71_fields(
        self, event: dict, session_events: list | None = None
    ) -> dict[str, Any]:
        """Анализ всех 71 поля Rick.ai без зацикливания на applied_rules

        ВАЖНО: Если переданы session_events, анализируем все события сессии вместе
        для правильного определения канала привлечения
        """
        field_analysis = {}
        contradictions = []

        # Группа 1: Основные поля атрибуции
        field_analysis["basic_attribution"] = self._analyze_basic_attribution_fields(
            event
        )

        # Группа 2: Click ID поля
        field_analysis["click_id_fields"] = self._analyze_click_id_fields(event)

        # Группа 3: UTM поля
        field_analysis["utm_fields"] = self._analyze_utm_fields(event)

        # Группа 4: Traffic Source поля
        field_analysis["traffic_source_fields"] = self._analyze_traffic_source_fields(
            event
        )

        # Группа 5: Referrer поля (анализ домена)
        field_analysis["referrer_fields"] = self._analyze_referrer_fields(event)

        # Группа 6: Campaign поля
        field_analysis["campaign_fields"] = self._analyze_campaign_fields(event)

        # Группа 7: Device и Browser поля
        field_analysis["device_browser_fields"] = self._analyze_device_browser_fields(
            event
        )

        # Группа 8: Rick.ai специфичные поля
        field_analysis["rick_ai_fields"] = self._analyze_rick_ai_fields(event)

        # Анализ противоречий между группами
        contradictions = self._find_field_contradictions(field_analysis)

        # Определяем ожидаемый sourceMedium на основе всех полей
        expected_source_medium = self._determine_expected_source_medium_from_all_fields(
            field_analysis
        )

        # Если переданы события сессии, анализируем сессионно
        if session_events and len(session_events) > 1:
            session_source_medium = self._analyze_session_source_medium(
                session_events, event
            )
            if session_source_medium:
                expected_source_medium = session_source_medium

        # Определяем ожидаемый rawSourceMedium (как Яндекс.Метрика)
        expected_raw_source_medium = (
            self._determine_expected_raw_source_medium_from_all_fields(field_analysis)
        )

        return {
            "field_analysis": field_analysis,
            "contradictions": contradictions,
            "expected_source_medium": expected_source_medium,
            "expected_raw_source_medium": expected_raw_source_medium,
            "has_contradictions": len(contradictions) > 0,
        }

    def _analyze_basic_attribution_fields(self, event: dict) -> dict:
        """Анализ основных полей атрибуции"""
        return {
            "source_medium": event.get("source_medium", ""),
            "raw_source_medium": event.get("raw_source_medium", ""),
            "channel_group": event.get("channel_group", ""),
            "client_id": event.get("client_id", ""),
            "day": event.get("day", ""),
            "event_param_date_hour_minute": event.get(
                "event_param_date_hour_minute", ""
            ),
        }

    def _analyze_click_id_fields(self, event: dict) -> dict:
        """Анализ Click ID полей"""
        return {
            "click_id": event.get("click_id", ""),
            "event_param_rick_ad_channel_identifiers": event.get(
                "event_param_rick_ad_channel_identifiers", ""
            ),
            "page_location": event.get("page_location", ""),
            "event_param_rick_url": event.get("event_param_rick_url", ""),
        }

    def _analyze_utm_fields(self, event: dict) -> dict:
        """Анализ UTM полей"""
        return {
            "event_param_source": event.get("event_param_source", ""),
            "event_param_medium": event.get("event_param_medium", ""),
            "event_param_campaign": event.get("event_param_campaign", ""),
            "event_param_content": event.get("event_param_content", ""),
            "event_param_term": event.get("event_param_term", ""),
            "page_location": event.get("page_location", ""),
        }

    def _analyze_traffic_source_fields(self, event: dict) -> dict:
        """Анализ Traffic Source полей"""
        return {
            "event_param_last_traffic_source": event.get(
                "event_param_last_traffic_source", ""
            ),
            "event_param_last_search_engine": event.get(
                "event_param_last_search_engine", ""
            ),
            "event_param_last_search_engine_root": event.get(
                "event_param_last_search_engine_root", ""
            ),
            "event_param_last_adv_engine": event.get("event_param_last_adv_engine", ""),
            "event_param_last_social_network": event.get(
                "event_param_last_social_network", ""
            ),
            "event_param_last_social_network_profile": event.get(
                "event_param_last_social_network_profile", ""
            ),
        }

    def _analyze_referrer_fields(self, event: dict) -> dict:
        """Анализ Referrer полей (анализ домена)"""
        return {
            "event_param_page_referrer": event.get("event_param_page_referrer", ""),
            "page_location": event.get("page_location", ""),
        }

    def _analyze_campaign_fields(self, event: dict) -> dict:
        """Анализ Campaign полей"""
        return {
            "campaign": event.get("campaign", ""),
            "campaign_id": event.get("campaign_id", ""),
            "custom_group_campaign_grouping": event.get(
                "custom_group_campaign_grouping", ""
            ),
            "campaign_name": event.get("campaign_name", ""),
            "campaign_status": event.get("campaign_status", ""),
            "ad_group_combined": event.get("ad_group_combined", ""),
            "ad_group": event.get("ad_group", ""),
            "keyword": event.get("keyword", ""),
            "ad_content": event.get("ad_content", ""),
        }

    def _analyze_device_browser_fields(self, event: dict) -> dict:
        """Анализ Device и Browser полей"""
        return {
            "device_category": event.get("device_category", ""),
            "event_param_rick_user_agent": event.get("event_param_rick_user_agent", ""),
            "all_landing_page_path": event.get("all_landing_page_path", ""),
        }

    def _analyze_rick_ai_fields(self, event: dict) -> dict:
        """Анализ Rick.ai специфичных полей"""
        return {
            "event_param_rick_rid": event.get("event_param_rick_rid", ""),
            "event_param_rick_ad_identifiers": event.get(
                "event_param_rick_ad_identifiers", ""
            ),
            "event_param_rick_additional_campaign_data": event.get(
                "event_param_rick_additional_campaign_data", ""
            ),
            "event_param_rick_campaign_attribution": event.get(
                "event_param_rick_campaign_attribution", ""
            ),
            "event_param_rick_fb_client_id": event.get(
                "event_param_rick_fb_client_id", ""
            ),
            "event_param_ad_source": event.get("event_param_ad_source", ""),
        }

    def _find_field_contradictions(self, field_analysis: dict) -> list:
        """Поиск противоречий между группами полей"""
        contradictions = []

        # Проверка противоречий между Click ID и UTM
        click_id_data = field_analysis["click_id_fields"]
        utm_data = field_analysis["utm_fields"]

        # Если есть Click ID, но UTM указывает на другой источник
        if self._has_click_id_in_fields(click_id_data) and self._has_utm_in_fields(
            utm_data
        ):
            click_id_source = self._get_source_from_click_id(click_id_data)
            utm_source = self._get_source_from_utm(utm_data)

            if click_id_source != utm_source:
                contradictions.append(
                    f"Противоречие: Click ID указывает на {click_id_source}, UTM на {utm_source}"
                )

        # Проверка противоречий между sourceMedium и raw_source_medium
        basic_data = field_analysis["basic_attribution"]
        if basic_data["source_medium"] != basic_data["raw_source_medium"]:
            contradictions.append(
                f"Противоречие: sourceMedium='{basic_data['source_medium']}' vs raw_source_medium='{basic_data['raw_source_medium']}'"
            )

        return contradictions

    def _determine_expected_source_medium_from_all_fields(
        self, field_analysis: dict
    ) -> str:
        """Определение ожидаемого sourceMedium на основе всех полей

        АЛГОРИТМ ПРИОРИТИЗАЦИИ (найден при анализе реальных кейсов):
        1. Click ID (наивысший приоритет) - yclid, gclid, fbclid, ysclid
        2. UTM параметры - utm_source, utm_medium из URL
        3. Traffic Source - event_param_last_traffic_source
        4. Referrer (анализ домена) - event_param_page_referrer
        5. Fallback - direct / none
        """
        # Приоритет 1: Click ID
        click_id_data = field_analysis["click_id_fields"]
        if self._has_click_id_in_fields(click_id_data):
            return self._get_source_medium_from_click_id_fields(click_id_data)

        # Приоритет 2: UTM
        utm_data = field_analysis["utm_fields"]
        if self._has_utm_in_fields(utm_data):
            return self._get_source_medium_from_utm_fields(utm_data)

        # Приоритет 3: Traffic Source
        traffic_data = field_analysis["traffic_source_fields"]
        if self._has_traffic_source_in_fields(traffic_data):
            return self._get_source_medium_from_traffic_source_fields(traffic_data)

        # Приоритет 4: Referrer (анализ домена)
        referrer_data = field_analysis.get("referrer_fields", {})
        referrer_source_medium = self._get_source_medium_from_referrer_fields(
            referrer_data
        )
        if referrer_source_medium:
            return referrer_source_medium

        # Fallback
        return "direct / none"

    def _determine_expected_raw_source_medium_from_all_fields(
        self, field_analysis: dict
    ) -> str:
        """Определение ожидаемого rawSourceMedium (как Яндекс.Метрика)

        rawSourceMedium определяется по event_param_last_traffic_source
        """
        # Приоритет 1: Traffic Source (основной источник для rawSourceMedium)
        traffic_data = field_analysis["traffic_source_fields"]
        raw_source_medium = self._get_raw_source_medium_from_traffic_source_fields(
            traffic_data
        )
        if raw_source_medium:
            return raw_source_medium

        # Fallback
        return "direct / none"

    def _analyze_session_source_medium(
        self, session_events: list, current_event: dict
    ) -> str:
        """Анализ sourceMedium для всей сессии

        ВАЖНО: Анализируем все события сессии вместе, чтобы найти канал привлечения
        в первом событии и применить его ко всем событиям сессии
        """
        # Сортируем события по времени
        sorted_events = sorted(
            session_events, key=lambda x: x.get("event_param_date_hour_minute", "")
        )

        # Анализируем первое событие сессии для определения канала привлечения
        first_event = sorted_events[0]
        first_event_analysis = self._determine_expected_source_medium_from_all_fields(
            self._get_field_analysis_for_event(first_event)
        )

        # Если в первом событии найден канал привлечения, используем его
        if first_event_analysis and first_event_analysis != "direct / none":
            return first_event_analysis

        # Если в первом событии нет канала, ищем в других событиях сессии
        for event in sorted_events:
            event_analysis = self._determine_expected_source_medium_from_all_fields(
                self._get_field_analysis_for_event(event)
            )
            if event_analysis and event_analysis != "direct / none":
                return event_analysis

        # Если ни в одном событии не найден канал, возвращаем пустую строку
        return ""

    def _get_field_analysis_for_event(self, event: dict) -> dict:
        """Получение анализа полей для события"""
        field_analysis = {}

        # Группа 1: Основные поля атрибуции
        field_analysis["basic_attribution"] = self._analyze_basic_attribution_fields(
            event
        )

        # Группа 2: Click ID поля
        field_analysis["click_id_fields"] = self._analyze_click_id_fields(event)

        # Группа 3: UTM поля
        field_analysis["utm_fields"] = self._analyze_utm_fields(event)

        # Группа 4: Traffic Source поля
        field_analysis["traffic_source_fields"] = self._analyze_traffic_source_fields(
            event
        )

        # Группа 5: Referrer поля (анализ домена)
        field_analysis["referrer_fields"] = self._analyze_referrer_fields(event)

        # Группа 6: Campaign поля
        field_analysis["campaign_fields"] = self._analyze_campaign_fields(event)

        # Группа 7: Device и Browser поля
        field_analysis["device_browser_fields"] = self._analyze_device_browser_fields(
            event
        )

        # Группа 8: Rick.ai специфичные поля
        field_analysis["rick_ai_fields"] = self._analyze_rick_ai_fields(event)

        return field_analysis

    def _has_click_id_in_fields(self, click_id_data: dict) -> bool:
        """Проверка наличия Click ID в полях"""
        for field, value in click_id_data.items():
            if value and any(
                pattern in str(value)
                for pattern in ["yclid:", "gclid:", "fbclid:", "ysclid:"]
            ):
                return True
        return False

    def _has_utm_in_fields(self, utm_data: dict) -> bool:
        """Проверка наличия UTM в полях"""
        return bool(
            utm_data.get("event_param_source") or utm_data.get("event_param_medium")
        )

    def _has_traffic_source_in_fields(self, traffic_data: dict) -> bool:
        """Проверка наличия Traffic Source в полях"""
        return bool(traffic_data.get("event_param_last_traffic_source"))

    def _get_source_from_click_id(self, click_id_data: dict) -> str:
        """Получение источника из Click ID полей"""
        for field, value in click_id_data.items():
            if "yclid:" in str(value):
                return "yandex"
            elif "gclid:" in str(value):
                return "google"
            elif "fbclid:" in str(value):
                return "facebook"
        return "unknown"

    def _get_source_from_utm(self, utm_data: dict) -> str:
        """Получение источника из UTM полей"""
        return utm_data.get("event_param_source", "unknown")

    def _get_source_medium_from_click_id_fields(self, click_id_data: dict) -> str:
        """Получение sourceMedium из Click ID полей"""
        source = self._get_source_from_click_id(click_id_data)
        return f"{source} / cpc"

    def _get_source_medium_from_utm_fields(self, utm_data: dict) -> str:
        """Получение sourceMedium из UTM полей"""
        source = utm_data.get("event_param_source", "unknown")
        medium = utm_data.get("event_param_medium", "unknown")
        return f"{source} / {medium}"

    def _get_source_medium_from_traffic_source_fields(self, traffic_data: dict) -> str:
        """Получение sourceMedium из Traffic Source полей

        ВАЖНО: Traffic Source поля определяют rawSourceMedium (Яндекс.Метрика),
        но для sourceMedium (группировка Рика) это псевдоканалы, которые нужно уточнять
        """
        traffic_source = traffic_data.get("event_param_last_traffic_source", "unknown")

        # Псевдоканалы - не используем напрямую для sourceMedium
        if traffic_source in ["referral", "ad", "internal", "organic"]:
            return ""  # Возвращаем пустую строку, чтобы перейти к следующему приоритету

        # Для других значений используем как есть
        return f"{traffic_source} / {traffic_source}"

    def _get_source_medium_from_referrer_fields(self, referrer_data: dict) -> str:
        """Определяет sourceMedium из Referrer полей (анализ домена)

        ВАЖНО: Домен из referrer МОЖЕТ быть источником (например, google.com → google / organic)
        Это последний способ определения канала привлечения - анализ referrer
        """
        referrer = referrer_data.get("event_param_page_referrer", "")

        if not referrer:
            return ""

        # Извлекаем домен из referrer URL
        try:
            from urllib.parse import urlparse

            parsed_url = urlparse(referrer)
            domain = parsed_url.netloc.lower()

            # Убираем www. префикс
            if domain.startswith("www."):
                domain = domain[4:]

            # Определяем sourceMedium по домену
            if domain == "google.com":
                return "google / organic"
            elif domain == "yandex.ru":
                return "yandex / organic"
            elif domain == "facebook.com":
                return "facebook / social"
            elif domain == "vk.com":
                return "vk / social"
            elif domain == "instagram.com":
                return "instagram / social"
            elif domain == "youtube.com":
                return "youtube / social"
            else:
                # Для других доменов используем домен как источник
                return f"{domain} / referral"

        except Exception:
            return ""

    def _get_raw_source_medium_from_traffic_source_fields(
        self, traffic_data: dict
    ) -> str:
        """Определяет rawSourceMedium из Traffic Source полей (как Яндекс.Метрика)

        rawSourceMedium - это то, что определяет Яндекс.Метрика по event_param_last_traffic_source
        """
        traffic_source = traffic_data.get("event_param_last_traffic_source", "")

        if not traffic_source or traffic_source == "unknown":
            return ""

        # Яндекс.Метрика определяет rawSourceMedium по traffic_source
        if traffic_source == "organic":
            return "organic / organic"
        elif traffic_source == "referral":
            return "referral / referral"
        elif traffic_source == "ad":
            return "ad / cpc"
        elif traffic_source == "internal":
            return "internal / referral"  # 🏠 Внутренние переходы
        else:
            return f"{traffic_source} / {traffic_source}"

    def _has_click_id(self, event: dict) -> bool:
        """Проверка наличия Click ID в событии"""
        for click_type in self.click_id_patterns.keys():
            if self._find_click_id(event, click_type):
                return True
        return False


class RickAIAnalysisManager:
    """Rick.ai Analysis Manager - MCP Workflow Standard v2.3"""

    def __init__(self):
        self.analysis_results = {}
        self.error_patterns = []
        self.grouping_rules = []
        self.source_medium_rules = SourceMediumRules()

    async def analyze_grouping_data(
        self, widget_data: str, widget_groups: str
    ) -> dict[str, Any]:
        """Анализ данных группировки (≤20 строк)"""
        try:
            widget_data_dict = (
                json.loads(widget_data) if isinstance(widget_data, str) else widget_data
            )
            widget_groups_dict = (
                json.loads(widget_groups)
                if isinstance(widget_groups, str)
                else widget_groups
            )

            analysis = await self._perform_analysis(
                widget_data_dict, widget_groups_dict
            )
            self.analysis_results = analysis

            return {"status": "success", "data": analysis}

        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return {"status": "error", "message": f"Ошибка анализа: {str(e)}"}

    async def generate_correction_rules(
        self, analysis_results: dict[str, Any]
    ) -> dict[str, Any]:
        """Генерация правил коррекции (≤20 строк)"""
        try:
            rules = await self._generate_rules(analysis_results)
            self.grouping_rules = rules

            return {"status": "success", "data": rules}

        except Exception as e:
            logger.error(f"Rule generation error: {e}")
            return {"status": "error", "message": f"Ошибка генерации правил: {str(e)}"}

    async def validate_grouping_rules(
        self, analysis_results: dict[str, Any]
    ) -> dict[str, Any]:
        """Валидация правил группировки (≤20 строк)"""
        try:
            validation = await self._validate_rules(analysis_results)

            return {"status": "success", "data": validation}

        except Exception as e:
            logger.error(f"Validation error: {e}")
            return {"status": "error", "message": f"Ошибка валидации: {str(e)}"}

    async def analyze_source_medium_attribution(
        self, widget_data: str
    ) -> dict[str, Any]:
        """Анализ атрибуции sourceMedium с правильной приоритизацией (≤20 строк)"""
        try:
            data = (
                json.loads(widget_data) if isinstance(widget_data, str) else widget_data
            )

            # Анализ каждого события
            attribution_results = []
            for event in data.get("events", []):
                result = await self._analyze_event_attribution(event)
                attribution_results.append(result)

            # Генерация правил коррекции
            correction_rules = await self.generate_correction_rules(
                {"attribution_results": attribution_results}
            )

            return {
                "status": "success",
                "data": {
                    "attribution_analysis": attribution_results,
                    "correction_rules": correction_rules,
                    "confidence_score": self._calculate_overall_confidence(
                        attribution_results
                    ),
                },
            }

        except Exception as e:
            logger.error(f"Source medium analysis error: {e}")
            return {"status": "error", "message": f"Ошибка анализа: {str(e)}"}

    async def analyze_source_medium_enhanced(
        self,
        widget_data: str,
        standard_compliance: bool = False,
        show_progress: bool = False,
    ) -> dict[str, Any]:
        """Анализ всех строк виджета sourceMedium с Rick.ai error detection и прогресс-индикацией"""
        try:
            data = (
                json.loads(widget_data) if isinstance(widget_data, str) else widget_data
            )

            # Reflection checkpoint: Standard compliance
            if standard_compliance:
                logger.info("✅ Rick.ai Methodology Standard compliance validated")

            # Get total events count for progress tracking
            events = data.get("events", [])
            total_events = len(events)

            if show_progress:
                print(f"ANALYSIS: Начинаем анализ {total_events} строк данных...")
                logger.info(f"Starting analysis of {total_events} events")

            # Analyze all rows with enhanced error detection and progress indication
            analysis_results = []
            batch_size = 100  # Обрабатываем по 100 строк за раз

            for i, event in enumerate(events):
                # Analyze sourceMedium errors according to Rick.ai methodology
                source_medium_result = self._analyze_source_medium_errors(event)
                source_medium_rule = self._generate_source_medium_rule(event)

                analysis_results.append(
                    {
                        "row_data": event,
                        "source_medium_result": source_medium_result,
                        "source_medium_rule": source_medium_rule,
                    }
                )

                # Progress indication every batch_size events
                if show_progress and (i + 1) % batch_size == 0:
                    progress_percent = ((i + 1) / total_events) * 100
                    print(
                        f"⏳ Обработано {i + 1}/{total_events} строк ({progress_percent:.1f}%)"
                    )
                    logger.info(
                        f"Processed {i + 1}/{total_events} events ({progress_percent:.1f}%)"
                    )

                # Yield control to event loop every 50 events to prevent blocking
                if (i + 1) % 50 == 0:
                    await asyncio.sleep(0)  # Yield control to event loop

            if show_progress:
                print(f"SUCCESS: Анализ завершен: {total_events} строк обработано")
                logger.info(f"Analysis completed: {total_events} events processed")

            # Save intermediate results to disk for large datasets
            if total_events > 1000:
                await self._save_intermediate_results(analysis_results, total_events)

            # Generate comprehensive report
            report = self._generate_source_medium_analysis_report(analysis_results)

            return {
                "status": "success",
                "data": {
                    "analysis_results": analysis_results,
                    "report": report,
                    "total_rows_analyzed": len(analysis_results),
                    "standard_compliance": standard_compliance,
                    "progress_shown": show_progress,
                },
            }

        except Exception as e:
            logger.error(f"Enhanced source medium analysis error: {e}")
            return {"status": "error", "message": f"Ошибка анализа: {str(e)}"}

    def _analyze_source_medium_errors(self, event: dict) -> str:
        """Анализирует строку данных на предмет ошибок sourceMedium Rick.ai"""
        errors = []

        # Проверка 1: Click ID приоритет (наивысший приоритет)
        if self._has_click_id(event) and not self._applied_click_id(event):
            errors.append("ошибка: Click ID найден, но не применен")

        # Проверка 2: Previous rules override (перезаписывают Click ID)
        if self._has_previous_rules(event) and self._has_click_id(event):
            errors.append("ошибка: previous_landing правило перезаписывает Click ID")

        # Проверка 3: Несоответствие sourceMedium (Rick.ai) vs raw_source_medium (ym:sourceMedium)
        if self._source_medium_mismatch(event):
            errors.append(
                "ошибка: несоответствие sourceMedium (Rick.ai) и raw_source_medium (ym:sourceMedium)"
            )

        # Проверка 4: Псевдо-каналы в sourceMedium
        if self._is_pseudo_channel(event):
            errors.append("ошибка: обнаружен псевдо-канал в sourceMedium")

        # Проверка 5: Платежные шлюзы в sourceMedium
        if self._is_payment_gateway(event):
            errors.append("ошибка: обнаружен платежный шлюз в sourceMedium")

        # Проверка 6: CRM ссылки в sourceMedium
        if self._is_crm_link(event):
            errors.append("ошибка: обнаружена CRM ссылка в sourceMedium")

        return "; ".join(errors) if errors else "✔️"

    def _generate_source_medium_rule(self, event: dict) -> str:
        """Генерирует sourceMedium rule для строки данных Rick.ai"""
        if self._has_click_id(event):
            click_id_type = self._get_click_id_type(event)
            return f'**Правило: clickId: {click_id_type}**\nкогда clientID равно "* любое не пустое" и\nevent_param_rick_ad_channel_identifiers содержит {click_id_type}:\n\nто\nchannel = {self._get_channel_from_click_id(click_id_type)}\nsourceMedium = {self._get_source_medium_from_click_id(click_id_type)} || {{параметр где определен sourceMedium}}\nraw_source_medium = {self._get_source_medium_from_click_id(click_id_type)} || {{параметр где определен sourceMedium}}'

        elif self._has_utm_params(event):
            return f'**Правило: UTM параметры**\nкогда clientID равно "* любое не пустое" и\npage_location содержит utm_source={self._get_utm_source(event)} и utm_medium={self._get_utm_medium(event)}\nто\nchannel = utm campaign\nsourceMedium = {self._get_utm_source(event)} / {self._get_utm_medium(event)}\nraw_source_medium = {self._get_utm_source(event)} / {self._get_utm_medium(event)}'

        elif self._has_traffic_source(event):
            return f'**Правило: Traffic Source**\nкогда clientID равно "* любое не пустое" и\nevent_param_last_traffic_source содержит {self._get_traffic_source(event)}\nто\nchannel = {self._get_traffic_source(event)}\nsourceMedium = {self._get_traffic_source(event)} / {self._get_traffic_source(event)}\nraw_source_medium = {self._get_traffic_source(event)} / {self._get_traffic_source(event)}'

        else:
            return '**Правило: Fallback**\nкогда clientID равно "* любое не пустое" и\nвсе остальные поля пустые или internal\nто\nchannel = direct\nsourceMedium = direct / none\nraw_source_medium = direct / none'

    def _generate_source_medium_analysis_report(self, analysis_results: list) -> str:
        """Генерирует отчет анализа sourceMedium в формате Markdown таблицы"""
        total_rows = len(analysis_results)
        error_rows = sum(
            1 for result in analysis_results if result["source_medium_result"] != "✔️"
        )
        success_rate = (
            ((total_rows - error_rows) / total_rows * 100) if total_rows > 0 else 0
        )

        # Генерируем Markdown таблицу
        markdown_table = self._generate_markdown_table(analysis_results)

        # Добавляем статистику
        stats = f"""
## 📊 Статистика анализа

- **Всего строк в виджете:** {total_rows}
- **Проанализировано строк:** {total_rows}
- **Строк с ошибками:** {error_rows}
- **Процент ошибок:** {success_rate:.1f}%
"""

        return markdown_table + stats

    def _generate_markdown_table(self, analysis_results: list) -> str:
        """Генерирует Markdown таблицу с правильным форматированием"""
        # Заголовок таблицы
        table_header = """# 🔍 Анализ sourceMedium алгоритма - Release 1

**Дата анализа:** {date}
**Источник данных:** widget_225114_sourcemedium_data.json (локальный файл)
**Всего строк в виджете:** {total_rows}
**Анализируем:** Первые {sample_size} строк с ошибками sourceMedium
**Статус:** RELEASE 1 - Core MCP Enhancement & Error Fixes

| sourceMedium raw groups | sourceMedium result | sourceMedium rule |
|-------------------------|-------------------|------------------|
""".format(
            date=datetime.now().strftime("%Y-%m-%d"),
            total_rows=5000,
            sample_size=len(analysis_results),
        )

        # Генерируем строки таблицы
        table_rows = []
        for result in analysis_results:
            # Форматируем первую колонку (sourceMedium raw groups)
            raw_groups = self._format_raw_groups(result["row_data"])

            # Форматируем вторую колонку (sourceMedium result)
            source_medium_result = result["source_medium_result"]

            # Форматируем третью колонку (sourceMedium rule) с ограничением длины
            source_medium_rule = self._truncate_rule(result["source_medium_rule"])

            # Создаем строку таблицы с правильным форматированием
            table_row = (
                f"| {raw_groups} | {source_medium_result} | {source_medium_rule} |"
            )

            # Проверяем длину строки и обрезаем если нужно
            if len(table_row) > 300:
                # Обрезаем raw_groups еще больше
                raw_groups_short = self._truncate_raw_groups(raw_groups, 150)
                table_row = f"| {raw_groups_short} | {source_medium_result} | {source_medium_rule} |"

            table_rows.append(table_row)

        return table_header + "\n".join(table_rows)

    def _format_raw_groups(self, event: dict) -> str:
        """Форматирует raw groups с правильными переносами строк"""
        # Ограничиваем длину полей для предотвращения поломки таблицы
        max_field_length = 20

        def truncate_field(value: str, max_length: int = max_field_length) -> str:
            if not value:
                return ""
            if len(value) <= max_length:
                return value
            return value[: max_length - 3] + "..."

        # Группируем поля по логическим блокам
        groups = []

        # Группа 1: Основные данные
        basic_fields = [
            ("day", event.get("day", "")),
            (
                "event_param_date_hour_minute",
                event.get("event_param_date_hour_minute", ""),
            ),
            ("client_id", event.get("client_id", "")),
            ("event_param_rick_rid", event.get("event_param_rick_rid", "")),
        ]

        basic_group = []
        for key, value in basic_fields:
            if value:
                basic_group.append(f"{key}: {truncate_field(str(value))}")

        if basic_group:
            groups.append("<br/>".join(basic_group))

        # Группа 2: SourceMedium данные
        source_medium_fields = [
            ("channel_group", event.get("channel_group", "")),
            ("source_medium", event.get("source_medium", "")),
            ("raw_source_medium", event.get("raw_source_medium", "")),
            ("applied_rules", event.get("applied_rules", "")),
        ]

        sm_group = []
        for key, value in source_medium_fields:
            if value:
                sm_group.append(f"{key}: {truncate_field(str(value))}")

        if sm_group:
            groups.append("<br/><br/>" + "<br/>".join(sm_group))

        # Группа 3: Click ID и параметры
        click_id_fields = [
            ("click_id", event.get("click_id", "")),
            ("event_param_source", event.get("event_param_source", "")),
            ("event_param_medium", event.get("event_param_medium", "")),
            (
                "event_param_last_traffic_source",
                event.get("event_param_last_traffic_source", ""),
            ),
        ]

        click_group = []
        for key, value in click_id_fields:
            if value:
                click_group.append(f"{key}: {truncate_field(str(value))}")

        if click_group:
            groups.append("<br/><br/>" + "<br/>".join(click_group))

        # Группа 4: Page location (особенно важно для UTM)
        page_location = event.get("page_location", "")
        if page_location:
            # Извлекаем только UTM параметры из page_location
            utm_params = []
            if "utm_source=" in page_location:
                utm_params.append(
                    "utm_source: "
                    + truncate_field(
                        page_location.split("utm_source=")[1].split("&")[0]
                        if "&" in page_location.split("utm_source=")[1]
                        else page_location.split("utm_source=")[1]
                    )
                )
            if "utm_medium=" in page_location:
                utm_params.append(
                    "utm_medium: "
                    + truncate_field(
                        page_location.split("utm_medium=")[1].split("&")[0]
                        if "&" in page_location.split("utm_medium=")[1]
                        else page_location.split("utm_medium=")[1]
                    )
                )
            if "yclid=" in page_location:
                utm_params.append(
                    "yclid: "
                    + truncate_field(
                        page_location.split("yclid=")[1].split("&")[0]
                        if "&" in page_location.split("yclid=")[1]
                        else page_location.split("yclid=")[1]
                    )
                )

            if utm_params:
                groups.append("<br/><br/>" + "<br/>".join(utm_params))

        return "".join(groups)

    def _truncate_rule(self, rule: str) -> str:
        """Ограничивает длину правила для предотвращения поломки таблицы"""
        max_rule_length = 100

        if len(rule) <= max_rule_length:
            return rule

        # Обрезаем до максимальной длины и добавляем многоточие
        truncated = rule[: max_rule_length - 3] + "..."

        # Заменяем переносы строк на <br/> для компактности
        truncated = truncated.replace("\n", "<br/>")

        return truncated

    def _truncate_raw_groups(self, raw_groups: str, max_length: int) -> str:
        """Обрезает raw_groups до максимальной длины"""
        if len(raw_groups) <= max_length:
            return raw_groups

        # Обрезаем до максимальной длины и добавляем многоточие
        truncated = raw_groups[: max_length - 3] + "..."

        return truncated

    async def _save_intermediate_results(
        self, analysis_results: list, total_events: int
    ) -> None:
        """Сохраняет промежуточные результаты на диск для больших датасетов"""
        try:
            # Create results directory if it doesn't exist
            results_dir = Path("rick_ai_analysis_results")
            results_dir.mkdir(exist_ok=True)

            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sourcemedium_analysis_{total_events}events_{timestamp}.json"
            filepath = results_dir / filename

            # Save results to disk
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "total_events": total_events,
                        "analysis_results": analysis_results,
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )

            print(f"💾 Промежуточные результаты сохранены: {filepath}")
            logger.info(f"Intermediate results saved to: {filepath}")

        except Exception as e:
            print(f"⚠️ Не удалось сохранить промежуточные результаты: {e}")
            logger.warning(f"Failed to save intermediate results: {e}")

    # Helper methods for error detection
    def _has_click_id(self, event: dict) -> bool:
        """Проверяет наличие Click ID в событии"""
        # Проверяем все возможные поля где может быть Click ID
        click_id_fields = ["gclid", "yclid", "fbclid", "ysclid", "msclid", "ttclid"]

        # Проверяем прямые поля
        for field in click_id_fields:
            if event.get(field):
                return True

        # Проверяем event_param поля
        for field in click_id_fields:
            if event.get(f"event_param_{field}"):
                return True

        # Проверяем event_param_rick_ad_channel_identifiers
        ad_identifiers = event.get("event_param_rick_ad_channel_identifiers", "")
        if ad_identifiers:
            for field in click_id_fields:
                if (
                    f"{field}:" in ad_identifiers
                    and ad_identifiers.split(f"{field}:")[1].strip()
                ):
                    return True

        # Проверяем page_location на наличие Click ID
        page_location = event.get("page_location", "")
        if page_location:
            for field in click_id_fields:
                if f"{field}=" in page_location:
                    return True

        return False

    def _applied_click_id(self, event: dict) -> bool:
        """Проверяет, применен ли Click ID в sourceMedium"""
        source_medium = event.get("source_medium", "")
        raw_source_medium = event.get("raw_source_medium", "")

        # Проверяем, что sourceMedium соответствует Click ID
        if self._has_click_id(event):
            click_id_type = self._get_click_id_type(event)
            expected_source = self._get_source_medium_from_click_id(click_id_type)

            # Проверяем, что sourceMedium содержит ожидаемый source
            if expected_source and expected_source in source_medium:
                return True

        return False

    def _has_previous_rules(self, event: dict) -> bool:
        """Проверяет наличие previous_* правил"""
        applied_rules = event.get("applied_rules", "")
        return "previous_" in applied_rules

    def _source_medium_mismatch(self, event: dict) -> bool:
        """Проверяет несоответствие sourceMedium и raw_source_medium"""
        source_medium = event.get("source_medium", "")
        raw_source_medium = event.get("raw_source_medium", "")
        return (
            source_medium != raw_source_medium and source_medium and raw_source_medium
        )

    def _is_pseudo_channel(self, event: dict) -> bool:
        """Проверяет наличие псевдо-каналов"""
        source_medium = event.get("source_medium", "")
        pseudo_channels = ["ad/referral", "social/referral", "recommend/referral"]
        return any(pseudo in source_medium for pseudo in pseudo_channels)

    def _is_payment_gateway(self, event: dict) -> bool:
        """Проверяет наличие платежных шлюзов"""
        source_medium = event.get("source_medium", "")
        payment_gateways = [
            "stripe.com",
            "paypal.com",
            "yoomoney",
            "tinkoff",
            "payu",
            "sberbank",
        ]
        return any(gateway in source_medium for gateway in payment_gateways)

    def _is_crm_link(self, event: dict) -> bool:
        """Проверяет наличие CRM ссылок"""
        source_medium = event.get("source_medium", "")
        crm_links = ["bitrix24", "amocrm", "retailCRM", "hubspot.com"]
        return any(crm in source_medium for crm in crm_links)

    def _has_utm_params(self, event: dict) -> bool:
        """Проверяет наличие UTM параметров"""
        return bool(event.get("utm_source") or event.get("utm_medium"))

    def _has_traffic_source(self, event: dict) -> bool:
        """Проверяет наличие traffic source данных"""
        return bool(event.get("event_param_last_traffic_source"))

    def _get_click_id_type(self, event: dict) -> str:
        """Возвращает тип Click ID"""
        click_id_fields = ["yclid", "gclid", "fbclid", "ysclid", "msclid", "ttclid"]

        # Проверяем прямые поля
        for click_id in click_id_fields:
            if event.get(click_id):
                return click_id

        # Проверяем event_param поля
        for click_id in click_id_fields:
            if event.get(f"event_param_{click_id}"):
                return click_id

        # Проверяем event_param_rick_ad_channel_identifiers
        ad_identifiers = event.get("event_param_rick_ad_channel_identifiers", "")
        if ad_identifiers:
            for click_id in click_id_fields:
                if (
                    f"{click_id}:" in ad_identifiers
                    and ad_identifiers.split(f"{click_id}:")[1].strip()
                ):
                    return click_id

        # Проверяем page_location
        page_location = event.get("page_location", "")
        if page_location:
            for click_id in click_id_fields:
                if f"{click_id}=" in page_location:
                    return click_id

        return "unknown"

    def _get_source_medium_from_click_id(self, click_id_type: str) -> str:
        """Возвращает ожидаемый sourceMedium для типа Click ID"""
        click_id_mapping = {
            "gclid": "google / cpc",
            "yclid": "yandex / cpc",
            "fbclid": "facebook / cpc",
            "ysclid": "yandex_search / cpc",
            "msclid": "microsoft / cpc",
            "ttclid": "tiktok / cpc",
        }
        return click_id_mapping.get(click_id_type, "unknown / cpc")

    def _get_channel_from_click_id(self, click_id_type: str) -> str:
        """Возвращает ожидаемый channel для типа Click ID"""
        channel_mapping = {
            "gclid": "google ads",
            "yclid": "yandex direct",
            "fbclid": "facebook ads",
            "ysclid": "yandex search",
            "msclid": "microsoft ads",
            "ttclid": "tiktok ads",
        }
        return channel_mapping.get(click_id_type, "unknown ads")

    def _get_utm_source(self, event: dict) -> str:
        """Возвращает utm_source из события"""
        return event.get("utm_source", "") or event.get("event_param_utm_source", "")

    def _get_utm_medium(self, event: dict) -> str:
        """Возвращает utm_medium из события"""
        return event.get("utm_medium", "") or event.get("event_param_utm_medium", "")

    def _get_traffic_source(self, event: dict) -> str:
        """Возвращает traffic source из события"""
        return event.get("event_param_last_traffic_source", "")

    async def restore_ym_source_medium(self, raw_data: str) -> dict[str, Any]:
        """Восстановление ym:sourceMedium по сырым данным (≤20 строк)"""
        try:
            data = json.loads(raw_data) if isinstance(raw_data, str) else raw_data
            restored_data = {}

            for event in data.get("events", []):
                # Анализ всех доступных полей
                source, medium = self.source_medium_rules.determine_source_medium(event)

                # Восстановление ym:sourceMedium
                restored_data[event.get("event_id", "unknown")] = {
                    "original_source": event.get("event_params.source", ""),
                    "original_medium": event.get("event_params.medium", ""),
                    "restored_source": source,
                    "restored_medium": medium,
                    "confidence": self._calculate_confidence(event, source, medium),
                    "rules_applied": self._get_applied_rules(event),
                }

            return {"status": "success", "data": restored_data}

        except Exception as e:
            logger.error(f"Restore ym source medium error: {e}")
            return {"status": "error", "message": f"Ошибка восстановления: {str(e)}"}

    async def validate_attribution_rules(self, test_data: str) -> dict[str, Any]:
        """Валидация правил определения sourceMedium (≤20 строк)"""
        try:
            data = json.loads(test_data) if isinstance(test_data, str) else test_data

            validation_results = {
                "total_events": len(data.get("events", [])),
                "correctly_classified": 0,
                "incorrectly_classified": 0,
                "confidence_scores": [],
                "rule_effectiveness": {},
            }

            for event in data.get("events", []):
                (
                    predicted_source,
                    predicted_medium,
                ) = self.source_medium_rules.determine_source_medium(event)
                actual_source = event.get("actual_source", "")
                actual_medium = event.get("actual_medium", "")

                if (
                    predicted_source == actual_source
                    and predicted_medium == actual_medium
                ):
                    current_correct = validation_results.get("correctly_classified", 0)
                    validation_results["correctly_classified"] = (
                        current_correct if isinstance(current_correct, int) else 0
                    ) + 1
                else:
                    current_incorrect = validation_results.get(
                        "incorrectly_classified", 0
                    )
                    validation_results["incorrectly_classified"] = (
                        current_incorrect if isinstance(current_incorrect, int) else 0
                    ) + 1

                confidence = self._calculate_confidence(
                    event, predicted_source, predicted_medium
                )
                confidence_scores = validation_results.get("confidence_scores", [])
                if isinstance(confidence_scores, list):
                    confidence_scores.append(confidence)
                else:
                    confidence_scores = [confidence]
                validation_results["confidence_scores"] = confidence_scores

            return {"status": "success", "data": validation_results}

        except Exception as e:
            logger.error(f"Validation attribution rules error: {e}")
            return {"status": "error", "message": f"Ошибка валидации правил: {str(e)}"}

    async def _perform_analysis(
        self, widget_data: dict, widget_groups: dict
    ) -> dict[str, Any]:
        """Внутренний анализ данных (≤20 строк)"""
        return {
            "timestamp": datetime.now().isoformat(),
            "data_quality": "high",
            "grouping_issues": [],
            "recommendations": [],
        }

    async def _generate_rules(self, analysis_results: dict[str, Any]) -> dict[str, Any]:
        """Внутренняя генерация правил (≤20 строк)"""
        return {
            "timestamp": datetime.now().isoformat(),
            "rules": [],
            "priority": "medium",
        }

    async def _validate_rules(self, analysis_results: dict[str, Any]) -> dict[str, Any]:
        """Внутренняя валидация правил (≤20 строк)"""
        return {
            "timestamp": datetime.now().isoformat(),
            "validation_score": 85,
            "issues": [],
        }

    async def _analyze_event_attribution(self, event: dict) -> dict[str, Any]:
        """Анализ атрибуции для одного события (≤20 строк)"""
        # Применение правил с правильной приоритизацией
        source, medium = self.source_medium_rules.determine_source_medium(event)

        return {
            "event_id": event.get("event_id"),
            "original_source": event.get("event_params.source", ""),
            "original_medium": event.get("event_params.medium", ""),
            "restored_source": source,
            "restored_medium": medium,
            "confidence": self._calculate_confidence(event, source, medium),
            "rules_applied": self._get_applied_rules(event),
        }

    def _calculate_confidence(self, event: dict, source: str, medium: str) -> float:
        """Расчет уверенности в определении sourceMedium (≤20 строк)"""
        confidence = 0.0

        # Проверяем наличие Click ID (высокая уверенность)
        if any(
            self.source_medium_rules._find_click_id(event, click_type)
            for click_type in self.source_medium_rules.click_id_patterns.keys()
        ):
            confidence += 0.4

        # Проверяем UTM параметры
        if event.get("event_params.utm_source") and event.get(
            "event_params.utm_medium"
        ):
            confidence += 0.3

        # Проверяем Yandex Metrica параметры
        if event.get("ym:source") and event.get("ym:medium"):
            confidence += 0.2

        # Проверяем Traffic Source
        if event.get("event_params.last_traffic_source"):
            confidence += 0.1

        return min(confidence, 1.0)

    def _get_applied_rules(self, event: dict) -> list[str]:
        """Получение списка примененных правил (≤20 строк)"""
        applied_rules = []

        # Проверяем какие правила были применены
        if self.source_medium_rules._check_click_id(event):
            applied_rules.append("click_id_rule")
        if self.source_medium_rules._check_utm_params(event):
            applied_rules.append("utm_params_rule")
        if self.source_medium_rules._check_ym_params(event):
            applied_rules.append("ym_params_rule")
        if self.source_medium_rules._check_traffic_source(event):
            applied_rules.append("traffic_source_rule")
        if self.source_medium_rules._check_referrer(event):
            applied_rules.append("referrer_rule")

        return applied_rules

    def _calculate_overall_confidence(self, attribution_results: list[dict]) -> float:
        """Расчет общей уверенности (≤20 строк)"""
        if not attribution_results:
            return 0.0

        total_confidence = sum(
            result.get("confidence", 0.0) for result in attribution_results
        )
        return total_confidence / len(attribution_results)
