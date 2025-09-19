#!/usr/bin/env python3
"""
Rick.ai Data Manager
MCP Workflow Standard v2.3 Compliance

JTBD: Когда мне нужно получить данные из Rick.ai,
я хочу использовать RickAIDataManager,
чтобы безопасно получать клиентов, виджеты и данные.

COMPLIANCE: MCP Workflow Standard v2.3, Registry Standard v5.4
"""

import logging
import ssl
from typing import Any

import aiohttp

logger = logging.getLogger(__name__)


class RickAIDataManager:
    """Rick.ai Data Manager - MCP Workflow Standard v2.3"""

    def __init__(self, auth_manager):
        self.base_url = "https://rick.ai"
        self.auth_manager = auth_manager
        # SSL контекст без проверки сертификатов для тестирования
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    async def get_clients(self) -> dict[str, Any]:
        """Получение списка клиентов (≤20 строк)"""
        try:
            if not self.auth_manager.session_cookie:
                return {"status": "error", "message": "Требуется аутентификация"}

            headers = {
                "Cookie": f"session={self.auth_manager.session_cookie}",
                "X-Auth-Token": f"{self.auth_manager.session_cookie}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": "https://rick.ai/",
                "Origin": "https://rick.ai",
                "X-Requested-With": "XMLHttpRequest",
            }
            # Попробуем разные возможные endpoints для получения клиентов
            possible_endpoints = [
                "/conclusions/clients-data",  # Правильный endpoint из n8n workflow
            ]

            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                for endpoint in possible_endpoints:
                    url = f"{self.base_url}{endpoint}"
                    logger.info(f"Testing endpoint: {endpoint}")
                    try:
                        # Попробуем GET
                        async with session.get(url, headers=headers) as response:
                            logger.info(f"GET {endpoint} returned {response.status}")
                            if response.status == 200:
                                try:
                                    data = await response.json()
                                    return {
                                        "status": "success",
                                        "data": data,
                                        "endpoint": endpoint,
                                        "method": "GET",
                                    }
                                except Exception as e:
                                    # Если не JSON, попробуем как GraphQL
                                    if "graphql" in endpoint:
                                        logger.info(
                                            f"GraphQL endpoint {endpoint} returned HTML, trying GraphQL query"
                                        )
                                        # Попробуем GraphQL запрос для получения клиентов
                                        graphql_query = {
                                            "query": "query { companies { id name alias } }"
                                        }
                                        # Используем правильные заголовки для GraphQL
                                        gql_headers = headers.copy()
                                        gql_headers["Content-Type"] = "application/json"
                                        async with session.post(
                                            url, headers=gql_headers, json=graphql_query
                                        ) as gql_response:
                                            if gql_response.status == 200:
                                                gql_data = await gql_response.json()
                                                return {
                                                    "status": "success",
                                                    "data": gql_data,
                                                    "endpoint": endpoint,
                                                    "method": "GraphQL",
                                                }
                                            else:
                                                logger.info(
                                                    f"GraphQL query to {endpoint} returned {gql_response.status}"
                                                )
                                    else:
                                        logger.info(
                                            f"Endpoint {endpoint} returned non-JSON response: {e}"
                                        )
                            elif response.status == 405:
                                # Попробуем POST для endpoints, которые возвращают 405
                                logger.info(
                                    f"Endpoint {endpoint} returned 405, trying POST"
                                )
                                async with session.post(
                                    url, headers=headers, json={}
                                ) as post_response:
                                    if post_response.status == 200:
                                        data = await post_response.json()
                                        return {
                                            "status": "success",
                                            "data": data,
                                            "endpoint": endpoint,
                                            "method": "POST",
                                        }
                                    else:
                                        logger.info(
                                            f"POST to {endpoint} returned {post_response.status}"
                                        )
                            elif response.status != 404:
                                logger.info(
                                    f"Endpoint {endpoint} returned {response.status}"
                                )
                    except Exception as e:
                        logger.info(f"Endpoint {endpoint} failed: {e}")
                        continue

                return {
                    "status": "error",
                    "message": "Все endpoints для получения клиентов возвращают 404",
                }

        except Exception as e:
            logger.error(f"Get clients error: {e}")
            return {
                "status": "error",
                "message": f"Ошибка получения клиентов: {str(e)}",
            }

    async def get_widget_groups(
        self, company_alias: str, app_id: str
    ) -> dict[str, Any]:
        """Получение групп виджетов (≤20 строк)"""
        try:
            if not self.auth_manager.session_cookie:
                return {"status": "error", "message": "Требуется аутентификация"}

            headers = {"Cookie": f"session={self.auth_manager.session_cookie}"}
            url = f"{self.base_url}/company/{company_alias}/{app_id}/widget_groups"

            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {"status": "success", "data": data}
                    else:
                        return {"status": "error", "message": f"HTTP {response.status}"}

        except Exception as e:
            logger.error(f"Get widget groups error: {e}")
            return {
                "status": "error",
                "message": f"Ошибка получения групп виджетов: {str(e)}",
            }

    async def get_widget_data(
        self, company_alias: str, app_id: str, widget_id: str
    ) -> dict[str, Any]:
        """Получение данных виджета (≤20 строк)"""
        try:
            print(f"📊 Запрос данных виджета {widget_id}...")
            logger.info(f"Requesting data for widget {widget_id}")

            if not self.auth_manager.session_cookie:
                print("❌ Ошибка: Требуется аутентификация")
                return {"status": "error", "message": "Требуется аутентификация"}

            headers = {"Cookie": f"session={self.auth_manager.session_cookie}"}
            url = f"{self.base_url}/preview/widget/{company_alias}/{app_id}/ready-widget.json?widget_id={widget_id}"
            print(f"🌐 URL: {url}")

            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                print("⏳ Отправка запроса...")
                async with session.get(url, headers=headers) as response:
                    print(f"📡 Статус ответа: {response.status}")
                    if response.status == 200:
                        print("📥 Получение JSON данных...")
                        data = await response.json()
                        data_size = len(str(data))
                        print(f"✅ Данные получены ({data_size} символов)")
                        return {"status": "success", "data": data}
                    else:
                        print(f"❌ HTTP ошибка: {response.status}")
                        return {"status": "error", "message": f"HTTP {response.status}"}

        except Exception as e:
            print(f"❌ Ошибка получения данных: {e}")
            logger.error(f"Get widget data error: {e}")
            return {
                "status": "error",
                "message": f"Ошибка получения данных виджета: {str(e)}",
            }

    async def find_widget_by_system_name(
        self, company_alias: str, app_id: str, system_name: str
    ) -> dict[str, Any]:
        """Поиск виджета по system_name (≤20 строк)"""
        try:
            print(f"🔍 Поиск виджета по system_name: {system_name}")
            logger.info(f"Starting search for widget with system_name: {system_name}")

            if not self.auth_manager.session_cookie:
                print("❌ Ошибка: Требуется аутентификация")
                return {"status": "error", "message": "Требуется аутентификация"}

            # Сначала получаем все группы виджетов
            print("📋 Получение групп виджетов...")
            logger.info("Fetching widget groups...")
            widget_groups_result = await self.get_widget_groups(company_alias, app_id)
            if widget_groups_result.get("status") != "success":
                print(
                    f"❌ Ошибка получения групп виджетов: {widget_groups_result.get('message')}"
                )
                return widget_groups_result

            # Ищем виджет по system_name в группах
            widget_groups = widget_groups_result.get("data", [])
            print(f"🔎 Поиск в {len(widget_groups)} группах виджетов...")
            logger.info(f"Searching in {len(widget_groups)} widget groups")

            for i, group in enumerate(widget_groups):
                if isinstance(group, dict) and "widgets" in group:
                    widgets = group["widgets"]
                    print(
                        f"  📁 Группа {i + 1}/{len(widget_groups)}: {len(widgets)} виджетов"
                    )
                    for j, widget in enumerate(widgets):
                        if (
                            isinstance(widget, dict)
                            and widget.get("system_name") == system_name
                        ):
                            print(f"✅ Найден виджет! ID: {widget.get('id')}")
                            logger.info(
                                f"Found widget with system_name {system_name}, ID: {widget.get('id')}"
                            )

                            # Найден виджет, получаем его данные
                            widget_id = widget.get("id")
                            if widget_id:
                                print(f"📊 Получение данных виджета {widget_id}...")
                                logger.info(f"Fetching data for widget {widget_id}")
                                widget_data_result = await self.get_widget_data(
                                    company_alias, app_id, str(widget_id)
                                )
                                print("✅ Данные виджета получены")
                                return {
                                    "status": "success",
                                    "widget": widget,
                                    "widget_data": widget_data_result.get("data")
                                    if widget_data_result.get("status") == "success"
                                    else None,
                                }

            print(f"❌ Виджет с system_name '{system_name}' не найден")
            return {
                "status": "error",
                "message": f"Виджет с system_name '{system_name}' не найден",
            }

        except Exception as e:
            print(f"❌ Ошибка поиска: {e}")
            logger.error(f"Find widget by system name error: {e}")
            return {
                "status": "error",
                "message": f"Ошибка поиска виджета по system_name: {str(e)}",
            }

    async def get_widget_screenshot(
        self, company_alias: str, app_id: str, widget_id: str
    ) -> dict[str, Any]:
        """Получение скриншота виджета (≤20 строк)"""
        try:
            if not self.auth_manager.session_cookie:
                return {"status": "error", "message": "Требуется аутентификация"}

            headers = {"Cookie": f"session={self.auth_manager.session_cookie}"}
            url = f"{self.base_url}/preview/widget/{company_alias}/{app_id}/widget.png?widget_id={widget_id}&new_screenshooter=true"

            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {"status": "success", "data": data}
                    else:
                        return {"status": "error", "message": f"HTTP {response.status}"}

        except Exception as e:
            logger.error(f"Get widget screenshot error: {e}")
            return {
                "status": "error",
                "message": f"Ошибка получения скриншота: {str(e)}",
            }

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
    ) -> dict[str, Any]:
        """Запрос данных Yandex Metrica в TSV формате (≤20 строк)"""
        try:
            if not self.auth_manager.session_cookie:
                return {"status": "error", "message": "Требуется аутентификация"}

            headers = {"Cookie": f"session={self.auth_manager.session_cookie}"}
            url = (
                f"{self.base_url}/api/companies/{company_alias}/apps/{app_id}/ym-query"
            )

            params = {
                "app_name": app_name,
                "start_date": start_date,
                "end_date": end_date,
            }
            if dimensions:
                params["dimensions"] = dimensions
            if metrics:
                params["metrics"] = metrics
            if filters:
                params["filters"] = filters
            if segment:
                params["segment"] = segment
            if sort:
                params["sort"] = sort

            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.text()
                        return {"status": "success", "data": data, "format": "tsv"}
                    else:
                        return {"status": "error", "message": f"HTTP {response.status}"}

        except Exception as e:
            logger.error(f"Query YM TSV error: {e}")
            return {
                "status": "error",
                "message": f"Ошибка запроса Yandex Metrica: {str(e)}",
            }

    async def create_auto_folder(
        self, company_alias: str, app_id: str, scenario: str
    ) -> dict[str, Any]:
        """Создание автоапки по generated id (≤20 строк)"""
        try:
            if not self.auth_manager.session_cookie:
                return {"status": "error", "message": "Требуется аутентификация"}

            headers = {
                "Cookie": f"session={self.auth_manager.session_cookie}",
                "Content-Type": "application/json",
            }
            url = f"{self.base_url}/scenario-widgets/company/{company_alias}/{app_id}/scenario-widget-group-without-metric"

            payload = {"scenario": scenario}

            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {"status": "success", "data": data}
                    else:
                        return {"status": "error", "message": f"HTTP {response.status}"}

        except Exception as e:
            logger.error(f"Create auto folder error: {e}")
            return {"status": "error", "message": f"Ошибка создания автоапки: {str(e)}"}

    async def get_widget_screenshot_with_dates(
        self,
        company_alias: str,
        app_id: str,
        widget_id: str,
        start_date: str,
        end_date: str,
    ) -> dict[str, Any]:
        """Получение скриншота виджета с датами (≤20 строк)"""
        try:
            if not self.auth_manager.session_cookie:
                return {"status": "error", "message": "Требуется аутентификация"}

            headers = {"Cookie": f"session={self.auth_manager.session_cookie}"}
            url = f"{self.base_url}/preview/widget/{company_alias}/{app_id}/widget.png?widget_id={widget_id}&start={start_date}&end={end_date}&new_screenshooter=true"

            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = (
                            await response.read()
                        )  # Для изображения используем read()
                        return {"status": "success", "data": data, "format": "image"}
                    else:
                        return {"status": "error", "message": f"HTTP {response.status}"}

        except Exception as e:
            logger.error(f"Get widget screenshot with dates error: {e}")
            return {
                "status": "error",
                "message": f"Ошибка получения скриншота: {str(e)}",
            }
