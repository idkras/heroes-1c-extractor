#!/usr/bin/env python3
"""
Яндекс.Директ интеграция через OAuth 2.0

JTBD: Как интегратор рекламных систем, я хочу подключаться к Яндекс.Директ через OAuth 2.0,
чтобы выгружать данные кампаний и групп объявлений для анализа эффективности.

Основано на продакшн коде из raw/yandex_direct_report_code.py
"""

import asyncio
import json
import logging
from decimal import Decimal
from typing import Any, Optional

import requests
from raw.consts import (
    API_REPORTS,
    REPORT_TYPES,
)

# Импорты из raw модуля
from raw.lib import ImportApiError

logger = logging.getLogger(__name__)


class YandexDirectOAuth2Client:
    """
    Клиент для работы с Яндекс.Директ API через OAuth 2.0

    JTBD: Как OAuth клиент, я хочу управлять токенами и запросами к Яндекс.Директ API,
    чтобы обеспечить безопасный доступ к данным рекламных кампаний.
    """

    def __init__(self, access_token: str, client_id: str, client_secret: str):
        """
        Инициализация клиента

        Args:
            access_token: OAuth 2.0 access token
            client_id: OAuth 2.0 client ID
            client_secret: OAuth 2.0 client secret
        """
        self.access_token = access_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api.direct.yandex.com/json/v5"
        self.reports_url = "https://api.direct.yandex.com/reports"

        # Заголовки для запросов
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        logger.info("✅ YandexDirectOAuth2Client инициализирован")

    async def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Обновление access token через refresh token

        Args:
            refresh_token: OAuth 2.0 refresh token

        Returns:
            Новый access token или None при ошибке
        """
        try:
            token_url = "https://oauth.yandex.ru/token"
            data = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }

            response = requests.post(token_url, data=data)
            response.raise_for_status()

            token_data = response.json()
            new_access_token = token_data.get("access_token")

            if new_access_token:
                self.access_token = new_access_token
                self.headers["Authorization"] = f"Bearer {new_access_token}"
                logger.info("✅ Access token обновлен")
                return new_access_token
            else:
                logger.error("❌ Не удалось получить новый access token")
                return None

        except Exception as e:
            logger.error(f"❌ Ошибка обновления access token: {e}")
            return None

    async def query_yandex(
        self,
        query: str,
        api_type: str = "campaigns",
        result_as_json: bool = True,
        dumps_response_data: bool = True,
    ) -> Any:
        """
        Выполнение запроса к Яндекс.Директ API

        Args:
            query: JSON строка с запросом
            api_type: Тип API (campaigns, adgroups, ads, reports)
            result_as_json: Возвращать результат как JSON
            dumps_response_data: Дамп данных ответа

        Returns:
            Результат запроса
        """
        try:
            # Определяем URL в зависимости от типа API
            if api_type == API_REPORTS:
                url = self.reports_url
            else:
                url = f"{self.base_url}/{api_type}"

            # Парсим JSON запрос
            if isinstance(query, str):
                query_data = json.loads(query)
            else:
                query_data = query

            # Выполняем запрос
            response = requests.post(url, headers=self.headers, json=query_data)
            response.raise_for_status()

            if result_as_json:
                result = response.json()
                if dumps_response_data:
                    logger.debug(f"Response data: {json.dumps(result, indent=2)}")
                return result
            else:
                return response.text

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logger.error(
                    "❌ Ошибка авторизации (401). Возможно, нужно обновить токен."
                )
                raise ImportApiError(401, "Unauthorized", "yandex_direct")
            elif e.response.status_code == 403:
                logger.error(
                    "❌ Ошибка доступа (403). Проверьте права доступа к аккаунту."
                )
                raise ImportApiError(403, "Forbidden", "yandex_direct")
            else:
                logger.error(f"❌ HTTP ошибка: {e}")
                raise ImportApiError(e.response.status_code, str(e), "yandex_direct")
        except Exception as e:
            logger.error(f"❌ Ошибка запроса к API: {e}")
            raise ImportApiError(0, str(e), "yandex_direct")

    async def get_campaigns(
        self, selection_criteria: Optional[dict] = None
    ) -> list[dict]:
        """
        Получение списка кампаний

        Args:
            selection_criteria: Критерии отбора кампаний

        Returns:
            Список кампаний
        """
        if selection_criteria is None:
            selection_criteria = {}

        query = {
            "method": "get",
            "params": {
                "SelectionCriteria": selection_criteria,
                "FieldNames": [
                    "Id",
                    "Name",
                    "Type",
                    "Status",
                    "StatusPayment",
                    "StatusClarification",
                    "StartDate",
                    "EndDate",
                    "DailyBudget",
                    "DailyBudgetMode",
                    "Currency",
                    "Funds",
                    "FundsMode",
                    "FundsAmount",
                    "FundsSpent",
                    "FundsBalance",
                ],
            },
        }

        try:
            result = await self.query_yandex(json.dumps(query), "campaigns")
            campaigns = result.get("result", {}).get("Campaigns", [])
            logger.info(f"✅ Получено {len(campaigns)} кампаний")
            return campaigns
        except Exception as e:
            logger.error(f"❌ Ошибка получения кампаний: {e}")
            return []

    async def get_ad_groups(self, campaign_ids: list[int]) -> list[dict]:
        """
        Получение списка групп объявлений

        Args:
            campaign_ids: Список ID кампаний

        Returns:
            Список групп объявлений
        """
        query = {
            "method": "get",
            "params": {
                "SelectionCriteria": {"CampaignIds": campaign_ids},
                "FieldNames": [
                    "Id",
                    "CampaignId",
                    "Name",
                    "Status",
                    "StatusClarification",
                    "Type",
                    "ServingStatus",
                    "NegativeKeywords",
                    "TrackingParams",
                ],
            },
        }

        try:
            result = await self.query_yandex(json.dumps(query), "adgroups")
            ad_groups = result.get("result", {}).get("AdGroups", [])
            logger.info(f"✅ Получено {len(ad_groups)} групп объявлений")
            return ad_groups
        except Exception as e:
            logger.error(f"❌ Ошибка получения групп объявлений: {e}")
            return []

    async def get_ads(self, ad_group_ids: list[int]) -> list[dict]:
        """
        Получение списка объявлений

        Args:
            ad_group_ids: Список ID групп объявлений

        Returns:
            Список объявлений
        """
        query = {
            "method": "get",
            "params": {
                "SelectionCriteria": {"AdGroupIds": ad_group_ids},
                "FieldNames": [
                    "Id",
                    "AdGroupId",
                    "CampaignId",
                    "Status",
                    "StatusClarification",
                    "Type",
                    "ServingStatus",
                    "TextAd",
                    "MobileAppAd",
                    "DynamicTextAd",
                    "TextImageAd",
                    "MobileAppImageAd",
                    "TextAdBuilderAd",
                    "MobileAppAdBuilderAd",
                    "CpcVideoAdBuilderAd",
                    "CpmBannerAdBuilderAd",
                    "CpmVideoAdBuilderAd",
                ],
            },
        }

        try:
            result = await self.query_yandex(json.dumps(query), "ads")
            ads = result.get("result", {}).get("Ads", [])
            logger.info(f"✅ Получено {len(ads)} объявлений")
            return ads
        except Exception as e:
            logger.error(f"❌ Ошибка получения объявлений: {e}")
            return []

    async def get_campaign_report(
        self, date_from: str, date_to: str, campaign_ids: Optional[list[int]] = None
    ) -> list[dict]:
        """
        Получение отчета по кампаниям

        Args:
            date_from: Дата начала (YYYY-MM-DD)
            date_to: Дата окончания (YYYY-MM-DD)
            campaign_ids: Список ID кампаний (опционально)

        Returns:
            Данные отчета
        """
        from raw.yandex_direct_report_code import get_report_data

        selection_criteria = {}
        if campaign_ids:
            selection_criteria["CampaignIds"] = campaign_ids

        # Используем основные поля для отчета кампаний
        fields = [
            "CampaignId",
            "CampaignName",
            "CampaignType",
            "Status",
            "StartDate",
            "EndDate",
            "DailyBudget",
            "DailyBudgetMode",
            "Currency",
            "Funds",
            "FundsMode",
            "FundsAmount",
            "FundsSpent",
            "FundsBalance",
            "Clicks",
            "Impressions",
            "Cost",
            "Ctr",
            "AvgCpc",
            "AvgCpm",
            "AvgPosition",
            "Conversions",
            "ConversionRate",
            "AvgConversionPrice",
        ]

        try:
            report_data = await get_report_data(
                query_yandex=self.query_yandex,
                date_from=date_from,
                date_to=date_to,
                selection_criterias=selection_criteria,
                fields=fields,
                order_by=["CampaignId"],
                report_type=REPORT_TYPES["CAMPAIGN_PERFORMANCE_REPORT"],
            )

            logger.info(f"✅ Получен отчет по кампаниям: {len(report_data)} записей")
            return report_data
        except Exception as e:
            logger.error(f"❌ Ошибка получения отчета по кампаниям: {e}")
            return []

    async def get_adgroup_report(
        self, date_from: str, date_to: str, campaign_ids: Optional[list[int]] = None
    ) -> list[dict]:
        """
        Получение отчета по группам объявлений

        Args:
            date_from: Дата начала (YYYY-MM-DD)
            date_to: Дата окончания (YYYY-MM-DD)
            campaign_ids: Список ID кампаний (опционально)

        Returns:
            Данные отчета
        """
        from raw.yandex_direct_report_code import get_report_data

        selection_criteria = {}
        if campaign_ids:
            selection_criteria["CampaignIds"] = campaign_ids

        # Используем основные поля для отчета групп объявлений
        fields = [
            "CampaignId",
            "CampaignName",
            "AdGroupId",
            "AdGroupName",
            "Status",
            "Type",
            "ServingStatus",
            "Clicks",
            "Impressions",
            "Cost",
            "Ctr",
            "AvgCpc",
            "AvgCpm",
            "AvgPosition",
            "Conversions",
            "ConversionRate",
            "AvgConversionPrice",
        ]

        try:
            report_data = await get_report_data(
                query_yandex=self.query_yandex,
                date_from=date_from,
                date_to=date_to,
                selection_criterias=selection_criteria,
                fields=fields,
                order_by=["CampaignId", "AdGroupId"],
                report_type=REPORT_TYPES["ADGROUP_PERFORMANCE_REPORT"],
            )

            logger.info(
                f"✅ Получен отчет по группам объявлений: {len(report_data)} записей"
            )
            return report_data
        except Exception as e:
            logger.error(f"❌ Ошибка получения отчета по группам объявлений: {e}")
            return []

    async def get_comprehensive_data(
        self, date_from: str, date_to: str, campaign_ids: Optional[list[int]] = None
    ) -> dict[str, Any]:
        """
        Получение комплексных данных по кампаниям и группам объявлений

        Args:
            date_from: Дата начала (YYYY-MM-DD)
            date_to: Дата окончания (YYYY-MM-DD)
            campaign_ids: Список ID кампаний (опционально)

        Returns:
            Словарь с данными кампаний, групп объявлений и отчетов
        """
        logger.info(
            f"🔄 Получение комплексных данных за период {date_from} - {date_to}"
        )

        # Получаем базовые данные
        campaigns = await self.get_campaigns(
            {"Ids": campaign_ids} if campaign_ids else {}
        )

        if not campaigns:
            logger.warning("⚠️ Кампании не найдены")
            return {
                "campaigns": [],
                "ad_groups": [],
                "ads": [],
                "campaign_report": [],
                "adgroup_report": [],
            }

        campaign_ids_list = [campaign["Id"] for campaign in campaigns]

        # Получаем группы объявлений
        ad_groups = await self.get_ad_groups(campaign_ids_list)

        # Получаем объявления
        ad_group_ids = [group["Id"] for group in ad_groups]
        ads = await self.get_ads(ad_group_ids) if ad_group_ids else []

        # Получаем отчеты
        campaign_report = await self.get_campaign_report(
            date_from, date_to, campaign_ids_list
        )
        adgroup_report = await self.get_adgroup_report(
            date_from, date_to, campaign_ids_list
        )

        result = {
            "campaigns": campaigns,
            "ad_groups": ad_groups,
            "ads": ads,
            "campaign_report": campaign_report,
            "adgroup_report": adgroup_report,
            "summary": {
                "total_campaigns": len(campaigns),
                "total_ad_groups": len(ad_groups),
                "total_ads": len(ads),
                "campaign_report_records": len(campaign_report),
                "adgroup_report_records": len(adgroup_report),
                "date_from": date_from,
                "date_to": date_to,
            },
        }

        logger.info(f"✅ Комплексные данные получены: {result['summary']}")
        return result


# Функция для создания клиента из credentials manager
async def create_yandex_direct_client() -> Optional[YandexDirectOAuth2Client]:
    """
    Создание клиента Яндекс.Директ из credentials manager

    Returns:
        Клиент Яндекс.Директ или None при ошибке
    """
    try:
        from heroes_platform.shared.credentials_manager import get_credential

        # Получаем credentials
        access_token = get_credential("yandex_direct_access_token")
        client_id = get_credential("yandex_direct_client_id")
        client_secret = get_credential("yandex_direct_client_secret")

        if not access_token or not client_id or not client_secret:
            logger.error("❌ Не найдены credentials для Яндекс.Директ")
            return None

        client = YandexDirectOAuth2Client(access_token, client_id, client_secret)
        logger.info("✅ Клиент Яндекс.Директ создан из credentials")
        return client

    except Exception as e:
        logger.error(f"❌ Ошибка создания клиента Яндекс.Директ: {e}")
        return None

    async def get_banners_stat_for_keywords(
        self, start_date: str, end_date: str, campaign_ids: Optional[list[int]] = None
    ) -> list[dict]:
        """
        Получение статистики баннеров по ключевым словам

        Args:
            start_date: Дата начала (YYYY-MM-DD)
            end_date: Дата окончания (YYYY-MM-DD)
            campaign_ids: Список ID кампаний (опционально)

        Returns:
            Список статистики баннеров
        """
        try:
            from raw.consts import (
                AD_NETWORK_TYPE_MAP,
                REPORT_FIELDS,
                SEARCH_REPORT_FIELDS,
                SMART_CAMPAIGN,
                SMART_CAMPAIGN_REPORT_FIELDS,
                UTM_CONTENT_MACROS_MAP,
            )
            from raw.models import YandexDirectImportReportStat
            from raw.utils import create_date_currency_converters, parse_keyword
            from raw.yandex_direct_report_code import get_report_data

            # Создаем конвертеры валют
            currency_converters = create_date_currency_converters(start_date, end_date)

            # Получаем информацию о кампаниях
            campaigns = await self.get_campaigns(
                {"Ids": campaign_ids} if campaign_ids else {}
            )
            campaigns_stat = {campaign["Id"]: campaign for campaign in campaigns}

            # Параметры аккаунта (в реальном приложении можно получить из API)
            ad_account_params = {"VatRate": 20}  # 20% НДС

            banners_stats = []
            order_by = ("Date",)

            # Определяем поля для отчетов
            all_campaign_fields = sorted(
                set(REPORT_FIELDS + list(dict(UTM_CONTENT_MACROS_MAP).values()))
            )
            smart_campaign_fields = sorted(
                set(
                    SMART_CAMPAIGN_REPORT_FIELDS
                    + list(dict(UTM_CONTENT_MACROS_MAP).values())
                )
            )

            parsed_report_results = []
            parsed_search_report_results = []

            # Получаем данные для каждой кампании
            for campaign_id, campaign in campaigns_stat.items():
                selection_criteria = (
                    {
                        "Field": "CampaignId",
                        "Operator": "EQUALS",
                        "Values": [str(campaign_id)],
                    },
                )

                # Выбираем поля в зависимости от типа кампании
                fields = (
                    smart_campaign_fields
                    if campaign.get("CampaignType") == SMART_CAMPAIGN
                    else all_campaign_fields
                )

                # Получаем основные отчеты и поисковые отчеты параллельно
                report_func = get_report_data(
                    self.query_yandex,
                    start_date,
                    end_date,
                    selection_criteria,
                    fields,
                    order_by,
                )
                search_report_func = get_report_data(
                    self.query_yandex,
                    start_date,
                    end_date,
                    selection_criteria,
                    SEARCH_REPORT_FIELDS,
                    order_by,
                    report_type="SEARCH_QUERY_PERFORMANCE_REPORT",
                )

                report_result, search_report_result = await asyncio.gather(
                    report_func, search_report_func
                )

                parsed_report_results += report_result
                parsed_search_report_results += search_report_result

            # Создаем маппинг ключевых слов
            matched_keyword_data = {}
            for search_data in parsed_search_report_results:
                matched_keyword_data[
                    (search_data["AdId"], search_data["Criterion"], search_data["Date"])
                ] = search_data["MatchedKeyword"]

            # Обрабатываем статистику баннеров
            for banner_stat in parsed_report_results:
                banner_stat["AdNetworkType"] = AD_NETWORK_TYPE_MAP.get(
                    banner_stat.get("AdNetworkType")
                )

                date = banner_stat["Date"]
                convert_currency = currency_converters.get(date, lambda x: x)
                keyword = parse_keyword(banner_stat.get("Criterion", ""))
                campaign_id = (
                    str(banner_stat["CampaignId"])
                    if str(banner_stat["CampaignId"]) != "--"
                    else None
                )

                banner_stat["MatchedKeyword"] = matched_keyword_data.get(
                    (
                        banner_stat["AdId"],
                        banner_stat.get("Criterion", ""),
                        banner_stat["Date"],
                    )
                )

                # Парсим числовые значения
                try:
                    banner_clicks = int(banner_stat.get("Clicks", 0))
                except ValueError:
                    banner_clicks = 0

                try:
                    banner_impressions = int(banner_stat.get("Impressions", 0))
                except ValueError:
                    banner_impressions = 0

                # Конвертируем стоимость (из копеек в рубли с учетом НДС)
                cost_micros = Decimal(banner_stat.get("Cost", 0)) / Decimal(1_000_000)
                price = convert_currency(cost_micros) / Decimal(
                    (ad_account_params.get("VatRate", 0) + 100) / 100
                )

                # Создаем объект статистики
                stat = YandexDirectImportReportStat(
                    ad_id=(
                        str(banner_stat["AdId"])
                        if banner_stat["AdId"] != "--"
                        else None
                    ),
                    ad_group_id=(
                        str(banner_stat["AdGroupId"])
                        if banner_stat["AdGroupId"] != "--"
                        else None
                    ),
                    clicks=banner_clicks,
                    impressions=banner_impressions,
                    price=price,
                    campaign_id=campaign_id if campaign_id != "--" else None,
                    campaign_name=str(banner_stat["CampaignName"]),
                    campaign_url=(
                        banner_stat["CampaignUrlPath"]
                        if banner_stat["CampaignUrlPath"] != "--"
                        else None
                    ),
                    date=date,
                    params=banner_stat,
                    phrase=keyword,
                    phrase_id=banner_stat.get("Placement", ""),
                    criteria=banner_stat.get("Criterion", ""),
                    show_type=banner_stat.get("CriterionType", ""),
                    placement="https://" + banner_stat.get("Placement", ""),
                )

                # Конвертируем в словарь для JSON сериализации
                banners_stats.append(
                    {
                        "ad_id": stat.ad_id,
                        "ad_group_id": stat.ad_group_id,
                        "clicks": stat.clicks,
                        "impressions": stat.impressions,
                        "price": float(stat.price),
                        "campaign_id": stat.campaign_id,
                        "campaign_name": stat.campaign_name,
                        "campaign_url": stat.campaign_url,
                        "date": stat.date,
                        "phrase": stat.phrase,
                        "phrase_id": stat.phrase_id,
                        "criteria": stat.criteria,
                        "show_type": stat.show_type,
                        "placement": stat.placement,
                        "matched_keyword": banner_stat.get("MatchedKeyword"),
                        "ad_network_type": banner_stat.get("AdNetworkType"),
                    }
                )

            logger.info(
                f"✅ Получена статистика баннеров: {len(banners_stats)} записей"
            )
            return banners_stats

        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики баннеров: {e}")
            return []
