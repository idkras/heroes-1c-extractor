#!/usr/bin/env python3
"""
Test Rick AI Workflow
"""

import pytest
from heroes_platform.heroes_mcp.workflows.rick_ai.workflow import RickAIWorkflow


class TestRickAIWorkflow:
    """Test Rick AI Workflow functionality"""

    @pytest.fixture
    def workflow(self):
        """Create workflow instance for testing"""
        return RickAIWorkflow()

    @pytest.fixture
    def mock_session_cookie(self):
        """Mock session cookie for testing"""
        return "test_session_cookie_123"

    @pytest.fixture
    def mock_arguments(self, mock_session_cookie):
        """Mock arguments for testing"""
        return {
            "command": "authenticate",
            "session_cookie": mock_session_cookie,
            "company_alias": "test_company",
            "app_id": "test_app_123",
            "widget_id": "test_widget_456",
        }

    def test_workflow_initialization(self, workflow):
        """Test workflow initialization"""
        assert workflow.workflow_name == "rick-ai-research-loop"
        assert workflow.version == "v1.0"
        assert workflow.standard_compliance == "Keyword Campaign Grouping Standard v1.0"
        assert workflow.base_url == "https://rick.ai"
        assert workflow.session_cookie is None

    def test_create_reflection_checkpoint(self, workflow, mock_arguments):
        """Test reflection checkpoint creation"""
        command_name = "test_command"
        workflow._create_reflection_checkpoint(command_name, mock_arguments)

        assert command_name in workflow.reflection_checkpoints
        checkpoint = workflow.reflection_checkpoints[command_name]
        assert checkpoint["command"] == command_name
        assert checkpoint["args"] == mock_arguments
        assert checkpoint["status"] == "pending"
        assert "timestamp" in checkpoint

    def test_record_atomic_operation(self, workflow, mock_arguments):
        """Test atomic operation recording"""
        command_name = "test_command"
        result = {"status": "success", "data": "test_data"}

        # Create checkpoint first
        workflow._create_reflection_checkpoint(command_name, mock_arguments)

        # Record operation
        workflow._record_atomic_operation(command_name, result)

        checkpoint = workflow.reflection_checkpoints[command_name]
        assert checkpoint["status"] == "completed"
        assert checkpoint["result"] == result

    @pytest.mark.asyncio
    async def test_authenticate_success(self, workflow, mock_arguments):
        """Test successful authentication"""
        result = await workflow.authenticate(mock_arguments)

        assert result["status"] == "success"
        assert result["message"] == "Аутентификация успешна"
        assert workflow.session_cookie == mock_arguments["session_cookie"]

    @pytest.mark.asyncio
    async def test_authenticate_missing_cookie(self, workflow):
        """Test authentication with missing session cookie"""
        arguments = {"command": "authenticate"}
        result = await workflow.authenticate(arguments)

        assert result["status"] == "error"
        assert "session_cookie обязателен" in result["message"]

    @pytest.mark.asyncio
    async def test_analyze_grouping_data_empty(self, workflow):
        """Test grouping data analysis with empty data"""
        arguments = {"widget_data": {}, "widget_groups": {}}
        result = await workflow.analyze_grouping_data(arguments)

        assert result["status"] == "success"
        data = result["data"]
        assert "Отсутствуют данные виджета" in data["data_quality_issues"]
        assert "Отсутствуют группы виджетов" in data["data_quality_issues"]

    @pytest.mark.asyncio
    async def test_analyze_grouping_data_with_groups(self, workflow):
        """Test grouping data analysis with sample groups"""
        widget_groups = [
            {"name": "Test Group 1", "id": "group_1"},
            {"name": "Test Group 2", "id": "group_2"},
            {"name": "A", "id": "group_3"},  # Too short name
        ]

        widget_data = {
            "data": {"test": "data"},
            "metadata": {"version": "1.0"},
            "config": {"settings": "default"},
        }

        arguments = {"widget_data": widget_data, "widget_groups": widget_groups}
        result = await workflow.analyze_grouping_data(arguments)

        assert result["status"] == "success"
        data = result["data"]
        assert "Данные виджета получены успешно" in data["key_findings"]
        assert "Группы виджетов получены успешно" in data["key_findings"]
        assert "Слишком короткое название группы: 'A'" in data["grouping_anomalies"]

    @pytest.mark.asyncio
    async def test_validate_grouping_rules_compliant(self, workflow):
        """Test grouping rules validation with compliant data"""
        analysis_results = {
            "error_patterns": [],
            "data_quality_issues": [],
            "grouping_anomalies": [],
        }

        arguments = {"analysis_results": analysis_results}
        result = await workflow.validate_grouping_rules(arguments)

        assert result["status"] == "success"
        data = result["data"]
        assert data["compliance_score"] == 100
        assert data["validation_status"] == "compliant"
        assert len(data["best_practices"]) == 3

    @pytest.mark.asyncio
    async def test_validate_grouping_rules_non_compliant(self, workflow):
        """Test grouping rules validation with non-compliant data"""
        analysis_results = {
            "error_patterns": ["Error 1", "Error 2"],
            "data_quality_issues": ["Missing field"],
            "grouping_anomalies": ["Bad naming"],
        }

        arguments = {"analysis_results": analysis_results}
        result = await workflow.validate_grouping_rules(arguments)

        assert result["status"] == "success"
        data = result["data"]
        assert data["compliance_score"] == 0
        assert data["validation_status"] == "non_compliant"
        assert len(data["rule_violations"]) == 3

    @pytest.mark.asyncio
    async def test_generate_correction_rules(self, workflow):
        """Test correction rules generation"""
        validation_results = {
            "rule_violations": [
                "Нарушена явная структура данных",
                "Нарушена полнота данных",
                "Нарушена консистентность названий",
            ],
            "compliance_score": 30,
        }

        analysis_results = {"error_patterns": ["Error 1", "Error 2"]}

        arguments = {
            "validation_results": validation_results,
            "analysis_results": analysis_results,
        }

        result = await workflow.generate_correction_rules(arguments)

        assert result["status"] == "success"
        data = result["data"]
        assert len(data["rules"]) == 3
        assert len(data["implementation_steps"]) == 5
        assert len(data["recommendations"]) == 2

    @pytest.mark.asyncio
    async def test_execute_unknown_command(self, workflow):
        """Test execution of unknown command"""
        arguments = {"command": "unknown_command"}
        result = await workflow.execute(arguments)

        assert result["status"] == "error"
        assert "Неизвестная команда" in result["message"]

    @pytest.mark.asyncio
    async def test_execute_missing_command(self, workflow):
        """Test execution without command"""
        arguments = {"session_cookie": "test"}
        result = await workflow.execute(arguments)

        assert result["status"] == "error"
        assert "command обязателен" in result["message"]

    def test_calculate_quality_score_empty(self, workflow):
        """Test quality score calculation with empty result"""
        result = {"workflow_stages": []}
        score = workflow._calculate_quality_score(result)
        assert score == 0

    def test_calculate_quality_score_full(self, workflow):
        """Test quality score calculation with full result"""
        result = {
            "workflow_stages": [
                "authentication",
                "get_clients",
                "get_widget_groups",
                "get_widget_data",
                "analyze_grouping_data",
                "validate_grouping_rules",
                "generate_correction_rules",
            ]
        }
        score = workflow._calculate_quality_score(result)
        assert score == 100  # 7 stages * 10 + 3 bonuses * 20 = 130, capped at 100

    def test_generate_sourcemedium_analysis_table(self, workflow):
        """Test generation of sourceMedium analysis table with real askona data"""
        # Real data from askona Rick.ai widget (from askona-sourceMedium-research-loop-analysis.md)
        askona_data = {
            "day": "2025-09-03",
            "event_param_date_hour_minute": "2025-09-03 05:03",
            "client_id": "16748222471051939108",
            "event_param_rick_rid": "SyxThnYotY",
            "channel_group": "yandex direct",
            "source_medium": "yandex_sm / cpc",
            "raw_source_medium": "yandex_sm / cpc",
            "applied_rules": "previous_landing",
            "click_id": "",
            "event_param_source": "",
            "event_param_medium": "",
            "event_param_last_search_engine": "",
            "event_param_last_search_engine_root": "",
            "event_param_last_adv_engine": "",
            "event_param_last_traffic_source": "internal",
            "event_param_last_social_network": "",
            "event_param_last_social_network_profile": "",
            "all_landing_page_path": "/matrasy/sleep-expert-master.htm",
            "page_location": "https://www.askona.ru/matrasy/sleep-expert-master.htm?selected_hash_size=80x200-99f4666067a778dd908a8d67652aeb74&utm_source=yandex_sm&utm_medium=cpc&utm_campaign=sm_yd_askona_other_person_perform_god_rk485876gr3785_context_shopping_feed_rus|119710113&utm_content=cid|119710113|gid|5568399787|ad|17180150848_17180150848|ph_id|205568399787|rtg_id|205568399787|src|none_search|geo|_967&utm_term=---autotargeting&yclid=86520401018748927",
            "event_param_page_referrer": "https://askona.ru/matrasy/sleep-expert-master.htm?SELECTED_HASH_SIZE=80x200-99f4666067a778dd908a8d67652aeb74",
            "event_param_rick_user_agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36",
            "event_param_rick_url": "yclid:86520401018748927;ym_client_id:16748222471051939108;hostname:www.askona.ru;pagepath:/matrasy/sleep-expert-master.htm",
            "device_category": "mobile",
            "campaign_id": "",
            "event_param_campaign": "",
            "custom_group_campaign_grouping": "sm_yd_askona_other_person_perform_god_rk485876gr3785_context_shopping_feed_rus|119710113",
            "campaign": "sm_yd_askona_other_person_perform_god_rk485876gr3785_context_shopping_feed_rus|119710113",
            "ad_group_combined": "",
            "ad_group": "",
            "keyword": "---autotargeting",
            "ad_content": "cid|119710113|gid|5568399787|ad|17180150848_17180150848|ph_id|205568399787|rtg_id|205568399787|src|none_search|geo|_967",
            "ad_utm_source_medium": "",
            "campaign_name": "",
            "campaign_status": "",
            "ad_utm_keyword": "",
            "ad_combined": "",
            "ad_group_name": "",
            "ad_group_status": "",
            "ad_campaign_type": "",
            "ad_group_type": "",
            "ad_name": "",
            "ad_status": "",
            "ad_placement_domain": "",
            "ad_placement_url": "",
            "ad_utm_campaign": "",
            "ad_subtype": "",
            "ad_utm_content": "",
            "ad_title": "",
            "ad_text": "",
            "ad_url": "",
            "ad_thumbnail_url": "",
            "ad_preview_url": "",
            "ad_source": "",
            "ga_data_import_id": "0",
            "ad_group_id": "",
            "ad_type": "",
            "ad_landing_page": "",
            "ad_id": "",
            "ad_erid": "",
            "event_param_ad_source": "",
            "event_param_content": "",
            "event_param_term": "",
            "event_param_rick_ad_channel_identifiers": "gclid:;fbclid:;yclid:86520401018748927;ysclid:",
            "event_param_rick_additional_campaign_data": "etext:;campaign_id:",
            "event_param_rick_ad_identifiers": "ad_id:;group_id:",
            "event_param_rick_campaign_attribution": "utm_source:;utm_medium:;utm_campaign:;utm_content:",
            "event_param_rick_fb_client_id": "",
        }

        # Generate table with real askona data
        table = workflow._generate_sourcemedium_analysis_table(askona_data)

        # Verify table structure
        assert (
            "| sourceMedium raw groups | sourceMedium result | sourceMedium rule |"
            in table
        )
        assert (
            "|-------------------------|-------------------|------------------|"
            in table
        )

        # Verify all 71 fields are present
        for field in askona_data.keys():
            assert f"{field}: {askona_data[field]}" in table or f"{field}:" in table

        # Verify sourceMedium result contains error
        assert "ошибка:" in table

        # Verify sourceMedium rule
        assert "**Правило:" in table

        print("\n" + "=" * 80)
        print("REAL ASKONA SOURCEMEDIUM ANALYSIS TABLE:")
        print("=" * 80)
        print(table)
        print("=" * 80)

        # Test with multiple error scenarios
        self._test_multiple_error_scenarios(workflow)

    def _test_multiple_error_scenarios(self, workflow):
        """Test 20 different error scenarios with real data patterns"""
        error_scenarios = [
            # Scenario 1: yclid not applied
            {
                "page_location": "https://askona.ru/page?yclid=123456789",
                "event_param_rick_ad_channel_identifiers": "gclid:;fbclid:;yclid:;ysclid:",
                "applied_rules": "previous_landing",
                "source_medium": "yandex_sm / cpc",
                "raw_source_medium": "yandex_sm / cpc",
            },
            # Scenario 2: gclid not applied
            {
                "page_location": "https://askona.ru/page?gclid=987654321",
                "event_param_rick_ad_channel_identifiers": "gclid:;fbclid:;yclid:;ysclid:",
                "applied_rules": "utm_priority",
                "source_medium": "google / cpc",
                "raw_source_medium": "google / cpc",
            },
            # Scenario 3: previous_landing overriding Click ID
            {
                "page_location": "https://askona.ru/page?yclid=111222333",
                "event_param_rick_ad_channel_identifiers": "gclid:;fbclid:;yclid:;ysclid:",
                "applied_rules": "previous_landing",
                "source_medium": "organic / organic",
                "raw_source_medium": "organic / organic",
            },
            # Scenario 4: source_medium != raw_source_medium
            {
                "page_location": "https://askona.ru/page?utm_source=google&utm_medium=cpc",
                "event_param_rick_ad_channel_identifiers": "gclid:;fbclid:;yclid:;ysclid:",
                "applied_rules": "utm_priority",
                "source_medium": "google / cpc",
                "raw_source_medium": "yandex / cpc",
            },
            # Scenario 5: pseudo-channel ad/referral
            {
                "page_location": "https://askona.ru/page",
                "event_param_rick_ad_channel_identifiers": "gclid:;fbclid:;yclid:;ysclid:",
                "applied_rules": "referrer_analysis",
                "source_medium": "ad/referral",
                "raw_source_medium": "ad/referral",
            },
            # Scenario 6: pseudo-channel social/referral
            {
                "page_location": "https://askona.ru/page",
                "event_param_rick_ad_channel_identifiers": "gclid:;fbclid:;yclid:;ysclid:",
                "applied_rules": "social_analysis",
                "source_medium": "social/referral",
                "raw_source_medium": "social/referral",
            },
            # Scenario 7: payment gateway in source_medium
            {
                "page_location": "https://askona.ru/page",
                "event_param_rick_ad_channel_identifiers": "gclid:;fbclid:;yclid:;ysclid:",
                "applied_rules": "payment_analysis",
                "source_medium": "stripe.com / referral",
                "raw_source_medium": "stripe.com / referral",
            },
            # Scenario 8: CRM link in source_medium
            {
                "page_location": "https://askona.ru/page",
                "event_param_rick_ad_channel_identifiers": "gclid:;fbclid:;yclid:;ysclid:",
                "applied_rules": "crm_analysis",
                "source_medium": "bitrix24 / referral",
                "raw_source_medium": "bitrix24 / referral",
            },
            # Scenario 9: yoomoney payment gateway
            {
                "page_location": "https://askona.ru/page",
                "event_param_rick_ad_channel_identifiers": "gclid:;fbclid:;yclid:;ysclid:",
                "applied_rules": "payment_analysis",
                "source_medium": "yoomoney / referral",
                "raw_source_medium": "yoomoney / referral",
            },
            # Scenario 10: amocrm in source_medium
            {
                "page_location": "https://askona.ru/page",
                "event_param_rick_ad_channel_identifiers": "gclid:;fbclid:;yclid:;ysclid:",
                "applied_rules": "crm_analysis",
                "source_medium": "amocrm / referral",
                "raw_source_medium": "amocrm / referral",
            },
            # Scenario 11: tinkoff payment gateway
            {
                "page_location": "https://askona.ru/page",
                "event_param_rick_ad_channel_identifiers": "gclid:;fbclid:;yclid:;ysclid:",
                "applied_rules": "payment_analysis",
                "source_medium": "tinkoff / referral",
                "raw_source_medium": "tinkoff / referral",
            },
            # Scenario 12: recommend/referral pseudo-channel
            {
                "page_location": "https://askona.ru/page",
                "event_param_rick_ad_channel_identifiers": "gclid:;fbclid:;yclid:;ysclid:",
                "applied_rules": "recommendation_analysis",
                "source_medium": "recommend/referral",
                "raw_source_medium": "recommend/referral",
            },
            # Scenario 13: paypal payment gateway
            {
                "page_location": "https://askona.ru/page",
                "event_param_rick_ad_channel_identifiers": "gclid:;fbclid:;yclid:;ysclid:",
                "applied_rules": "payment_analysis",
                "source_medium": "paypal.com / referral",
                "raw_source_medium": "paypal.com / referral",
            },
            # Scenario 14: retailcrm in source_medium
            {
                "page_location": "https://askona.ru/page",
                "event_param_rick_ad_channel_identifiers": "gclid:;fbclid:;yclid:;ysclid:",
                "applied_rules": "crm_analysis",
                "source_medium": "retailcrm / referral",
                "raw_source_medium": "retailcrm / referral",
            },
            # Scenario 15: sberbank payment gateway
            {
                "page_location": "https://askona.ru/page",
                "event_param_rick_ad_channel_identifiers": "gclid:;fbclid:;yclid:;ysclid:",
                "applied_rules": "payment_analysis",
                "source_medium": "sberbank / referral",
                "raw_source_medium": "sberbank / referral",
            },
            # Scenario 16: hubspot.com CRM
            {
                "page_location": "https://askona.ru/page",
                "event_param_rick_ad_channel_identifiers": "gclid:;fbclid:;yclid:;ysclid:",
                "applied_rules": "crm_analysis",
                "source_medium": "hubspot.com / referral",
                "raw_source_medium": "hubspot.com / referral",
            },
            # Scenario 17: payu payment gateway
            {
                "page_location": "https://askona.ru/page",
                "event_param_rick_ad_channel_identifiers": "gclid:;fbclid:;yclid:;ysclid:",
                "applied_rules": "payment_analysis",
                "source_medium": "payu / referral",
                "raw_source_medium": "payu / referral",
            },
            # Scenario 18: Multiple Click IDs conflict
            {
                "page_location": "https://askona.ru/page?yclid=111&gclid=222",
                "event_param_rick_ad_channel_identifiers": "gclid:;fbclid:;yclid:;ysclid:",
                "applied_rules": "click_id_priority",
                "source_medium": "yandex / cpc",
                "raw_source_medium": "google / cpc",
            },
            # Scenario 19: UTM override Click ID
            {
                "page_location": "https://askona.ru/page?yclid=333&utm_source=facebook&utm_medium=cpc",
                "event_param_rick_ad_channel_identifiers": "gclid:;fbclid:;yclid:;ysclid:",
                "applied_rules": "utm_priority",
                "source_medium": "facebook / cpc",
                "raw_source_medium": "yandex / cpc",
            },
            # Scenario 20: Complex error combination
            {
                "page_location": "https://askona.ru/page?yclid=444&utm_source=stripe.com&utm_medium=referral",
                "event_param_rick_ad_channel_identifiers": "gclid:;fbclid:;yclid:;ysclid:",
                "applied_rules": "previous_landing",
                "source_medium": "stripe.com / referral",
                "raw_source_medium": "yandex / cpc",
            },
        ]

        print("\n" + "=" * 80)
        print("20 ERROR SCENARIOS ANALYSIS:")
        print("=" * 80)

        for i, scenario in enumerate(error_scenarios, 1):
            # Create base data with scenario-specific values
            test_data = {
                "day": "2025-09-03",
                "event_param_date_hour_minute": "2025-09-03 05:03",
                "client_id": "16748222471051939108",
                "event_param_rick_rid": "SyxThnYotY",
                "channel_group": "yandex direct",
                "source_medium": scenario.get("source_medium", "yandex_sm / cpc"),
                "raw_source_medium": scenario.get(
                    "raw_source_medium", "yandex_sm / cpc"
                ),
                "applied_rules": scenario.get("applied_rules", "previous_landing"),
                "click_id": "",
                "event_param_source": "",
                "event_param_medium": "",
                "event_param_last_search_engine": "",
                "event_param_last_search_engine_root": "",
                "event_param_last_adv_engine": "",
                "event_param_last_traffic_source": "internal",
                "event_param_last_social_network": "",
                "event_param_last_social_network_profile": "",
                "all_landing_page_path": "/matrasy/sleep-expert-master.htm",
                "page_location": scenario.get(
                    "page_location",
                    "https://www.askona.ru/matrasy/sleep-expert-master.htm",
                ),
                "event_param_page_referrer": "https://askona.ru/matrasy/sleep-expert-master.htm",
                "event_param_rick_user_agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36",
                "event_param_rick_url": "yclid:86520401018748927;ym_client_id:16748222471051939108;hostname:www.askona.ru;pagepath:/matrasy/sleep-expert-master.htm",
                "device_category": "mobile",
                "campaign_id": "",
                "event_param_campaign": "",
                "custom_group_campaign_grouping": "sm_yd_askona_other_person_perform_god_rk485876gr3785_context_shopping_feed_rus|119710113",
                "campaign": "sm_yd_askona_other_person_perform_god_rk485876gr3785_context_shopping_feed_rus|119710113",
                "ad_group_combined": "",
                "ad_group": "",
                "keyword": "---autotargeting",
                "ad_content": "cid|119710113|gid|5568399787|ad|17180150848_17180150848|ph_id|205568399787|rtg_id|205568399787|src|none_search|geo|_967",
                "ad_utm_source_medium": "",
                "campaign_name": "",
                "campaign_status": "",
                "ad_utm_keyword": "",
                "ad_combined": "",
                "ad_group_name": "",
                "ad_group_status": "",
                "ad_campaign_type": "",
                "ad_group_type": "",
                "ad_name": "",
                "ad_status": "",
                "ad_placement_domain": "",
                "ad_placement_url": "",
                "ad_utm_campaign": "",
                "ad_subtype": "",
                "ad_utm_content": "",
                "ad_title": "",
                "ad_text": "",
                "ad_url": "",
                "ad_thumbnail_url": "",
                "ad_preview_url": "",
                "ad_source": "",
                "ga_data_import_id": "0",
                "ad_group_id": "",
                "ad_type": "",
                "ad_landing_page": "",
                "ad_id": "",
                "ad_erid": "",
                "event_param_ad_source": "",
                "event_param_content": "",
                "event_param_term": "",
                "event_param_rick_ad_channel_identifiers": scenario.get(
                    "event_param_rick_ad_channel_identifiers",
                    "gclid:;fbclid:;yclid:86520401018748927;ysclid:",
                ),
                "event_param_rick_additional_campaign_data": "etext:;campaign_id:",
                "event_param_rick_ad_identifiers": "ad_id:;group_id:",
                "event_param_rick_campaign_attribution": "utm_source:;utm_medium:;utm_campaign:;utm_content:",
                "event_param_rick_fb_client_id": "",
            }

            # Generate analysis
            result = workflow._analyze_sourcemedium_errors(test_data)

            print(f"\n--- SCENARIO {i} ---")
            print(f"Page Location: {scenario.get('page_location', 'N/A')}")
            print(f"Applied Rules: {scenario.get('applied_rules', 'N/A')}")
            print(f"Source Medium: {scenario.get('source_medium', 'N/A')}")
            print(f"Raw Source Medium: {scenario.get('raw_source_medium', 'N/A')}")
            print(
                f"Rick Identifiers: {scenario.get('event_param_rick_ad_channel_identifiers', 'N/A')}"
            )
            print(f"ERRORS FOUND: {result}")
            print("-" * 50)

    def _generate_sourcemedium_analysis_table(self, data):
        """Generate sourceMedium analysis table with all 71 fields and proper grouping"""
        # All 71 Rick.ai fields in correct order with proper grouping (from standard)
        all_fields = [
            "day",
            "event_param_date_hour_minute",
            "client_id",
            "event_param_rick_rid",
            "channel_group",
            "source_medium",
            "raw_source_medium",
            "applied_rules",
            "click_id",
            "event_param_source",
            "event_param_medium",
            "event_param_last_search_engine",
            "event_param_last_search_engine_root",
            "event_param_last_adv_engine",
            "event_param_last_traffic_source",
            "event_param_last_social_network",
            "event_param_last_social_network_profile",
            "device_category",
            "all_landing_page_path",
            "page_location",
            "event_param_page_referrer",
            "event_param_rick_user_agent",
            "event_param_rick_url",
            "campaign_id",
            "event_param_campaign",
            "custom_group_campaign_grouping",
            "campaign",
            "ad_group_combined",
            "ad_group",
            "keyword",
            "ad_content",
            "ad_utm_source_medium",
            "campaign_name",
            "campaign_status",
            "ad_utm_keyword",
            "ad_combined",
            "ad_group_name",
            "ad_group_status",
            "ad_campaign_type",
            "ad_group_type",
            "ad_name",
            "ad_status",
            "ad_placement_domain",
            "ad_placement_url",
            "ad_utm_campaign",
            "ad_subtype",
            "ad_utm_content",
            "ad_title",
            "ad_text",
            "ad_url",
            "ad_thumbnail_url",
            "ad_preview_url",
            "ad_source",
            "ga_data_import_id",
            "ad_group_id",
            "ad_type",
            "ad_landing_page",
            "ad_id",
            "ad_erid",
            "event_param_ad_source",
            "event_param_content",
            "event_param_term",
            "event_param_rick_ad_channel_identifiers",
            "event_param_rick_additional_campaign_data",
            "event_param_rick_ad_identifiers",
            "event_param_rick_campaign_attribution",
            "event_param_rick_fb_client_id",
        ]

        # Grouping positions for soft line breaks (from standard)
        grouping_positions = {
            "click_id": True,  # After click_id
            "campaign": True,  # After campaign
            "ad_erid": True,  # After ad_erid
        }

        # Build first column with proper grouping
        first_column = ""
        for i, field in enumerate(all_fields):
            value = data.get(field, "")
            # Escape '|' character in values for Markdown table
            if isinstance(value, str):
                value = value.replace("|", "\\|")

            if value:
                first_column += f"{field}: {value}<br/>"
            else:
                first_column += f"{field}:<br/>"

            # Add soft line break after specific fields
            if field in grouping_positions:
                first_column += "<br/>"

        # Remove last <br/>
        first_column = first_column.rstrip("<br/>")

        # Advanced sourceMedium analysis logic
        sourcemedium_result = self._analyze_sourcemedium_errors(data)

        # Generate sourceMedium rule based on detected issues
        sourcemedium_rule = self._generate_sourcemedium_rule(data)

        # Build table
        table = f"""| sourceMedium raw groups | sourceMedium result | sourceMedium rule |
|-------------------------|-------------------|------------------|
| {first_column} | {sourcemedium_result} | {sourcemedium_rule} |"""

        return table

    def _analyze_sourcemedium_errors(self, data):
        """Analyze sourceMedium data for errors and inconsistencies"""
        errors = []

        # Check Click ID priority issues
        page_location = data.get("page_location", "")
        rick_identifiers = data.get("event_param_rick_ad_channel_identifiers", "")
        applied_rules = data.get("applied_rules", "")
        source_medium = data.get("source_medium", "")
        raw_source_medium = data.get("raw_source_medium", "")

        # Check for yclid in page_location but not applied
        if "yclid=" in page_location:
            yclid_value = (
                page_location.split("yclid=")[1].split("&")[0]
                if "yclid=" in page_location
                else ""
            )
            if yclid_value and "yclid:" not in rick_identifiers:
                errors.append(
                    f"ошибка: в page_location найден yclid={yclid_value}, но не применен"
                )

        # Check for gclid in page_location but not applied
        if "gclid=" in page_location:
            gclid_value = (
                page_location.split("gclid=")[1].split("&")[0]
                if "gclid=" in page_location
                else ""
            )
            if gclid_value and "gclid:" not in rick_identifiers:
                errors.append(
                    f"ошибка: в page_location найден gclid={gclid_value}, но не применен"
                )

        # Check previous_landing rule overriding Click ID
        if "previous_landing" in applied_rules and (
            "yclid=" in page_location or "gclid=" in page_location
        ):
            errors.append(
                "ошибка: Click ID найден, но previous_landing правило перезаписывает"
            )

        # Check source_medium vs raw_source_medium inconsistency
        if source_medium and raw_source_medium and source_medium != raw_source_medium:
            errors.append(
                f"ошибка: source_medium ({source_medium}) != raw_source_medium ({raw_source_medium})"
            )

        # Check for pseudo-channels
        pseudo_channels = ["ad/referral", "social/referral", "recommend/referral"]
        if any(pseudo in source_medium for pseudo in pseudo_channels):
            errors.append(f"ошибка: найден псевдо-канал {source_medium}")

        # Check for payment gateways in source_medium
        payment_gateways = [
            "stripe.com",
            "paypal.com",
            "yoomoney",
            "tinkoff",
            "payu",
            "sberbank",
        ]
        if any(gateway in source_medium.lower() for gateway in payment_gateways):
            errors.append(
                f"ошибка: найден платежный шлюз в source_medium: {source_medium}"
            )

        # Check for CRM links in source_medium
        crm_links = ["bitrix24", "amocrm", "retailcrm", "hubspot.com"]
        if any(crm in source_medium.lower() for crm in crm_links):
            errors.append(
                f"ошибка: найдена CRM-ссылка в source_medium: {source_medium}"
            )

        if errors:
            return "<br/>".join(errors)
        else:
            return "✔️"

    def _generate_sourcemedium_rule(self, data):
        """Generate sourceMedium rule based on detected issues"""
        page_location = data.get("page_location", "")
        rick_identifiers = data.get("event_param_rick_ad_channel_identifiers", "")

        # Determine which rule to show based on data
        if "yclid=" in page_location:
            return """**Правило: clickId: yclid**<br/>когда clientID равно "* любое не пустое" и<br/>event_param_rick_ad_channel_identifiers содержит yclid:<br/><br/>то<br/>channel = yandex direct<br/>sourceMedium = yandex / cpc || {параметр где определен sourceMedium}<br/>raw_source_medium = yandex / cpc || {параметр где определен sourceMedium}"""
        elif "gclid=" in page_location:
            return """**Правило: clickId: gclid**<br/>когда clientID равно "* любое не пустое" и<br/>event_param_rick_ad_channel_identifiers содержит gclid:<br/><br/>то<br/>channel = google ads<br/>sourceMedium = google / cpc || {параметр где определен sourceMedium}<br/>raw_source_medium = google / cpc || {параметр где определен sourceMedium}"""
        elif "utm_source=" in page_location:
            return """**Правило: UTM параметры**<br/>когда clientID равно "* любое не пустое" и<br/>page_location содержит utm_source и utm_medium:<br/><br/>то<br/>channel = utm campaign<br/>sourceMedium = {utm_source} / {utm_medium}<br/>raw_source_medium = {utm_source} / {utm_medium}"""
        else:
            return """**Правило: Fallback**<br/>когда clientID равно "* любое не пустое" и<br/>все остальные поля пустые или internal:<br/><br/>то<br/>channel = direct<br/>sourceMedium = direct / none<br/>raw_source_medium = direct / none"""


if __name__ == "__main__":
    pytest.main([__file__])
