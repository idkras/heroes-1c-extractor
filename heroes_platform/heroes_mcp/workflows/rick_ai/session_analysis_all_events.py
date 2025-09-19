#!/usr/bin/env python3
"""
Сессионный анализ всех событий clientID - анализ всех строчек сессии
"""

import json
import os
import random
import sys
from collections import defaultdict

# Добавляем путь к модулям
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)

from heroes_platform.heroes_mcp.workflows.rick_ai.analysis_manager import (
    SourceMediumRules,
)


def analyze_all_events_in_session():
    """Анализ всех событий в сессии по clientID"""

    # Загружаем реальные данные
    data_file = "[rick.ai]/knowledge base/in progress/1. when new lead come/when sourceMedium, ym_sourceMedium analise/widget_225114_sourcemedium_data.json"

    try:
        with open(data_file, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Файл {data_file} не найден!")
        return

    # Получаем все события
    events = data.get("groups", {}).get(
        "applied_rules,day,client_id,event_param_date_hour_minute,click_id,channel_group,source_medium,raw_source_medium,event_param_source,event_param_medium,event_param_page_referrer,page_location,event_param_last_search_engine,event_param_last_search_engine_root,event_param_last_adv_engine,event_param_last_traffic_source,event_param_last_social_network,event_param_last_social_network_profile,event_param_campaign,custom_group_campaign_grouping,campaign,ad_group_combined,ad_group,keyword,ad_content,ad_utm_source_medium,campaign_name,campaign_status,ad_utm_keyword,ad_combined,ad_group_name,ad_group_status,ad_campaign_type,ad_group_type,ad_name,ad_status,ad_placement_domain,ad_placement_url,ad_utm_campaign,ad_subtype,ad_utm_content,ad_title,ad_text,ad_url,ad_thumbnail_url,ad_preview_url,ad_source,ga_data_import_id,all_landing_page_path,ad_group_id,ad_type,ad_landing_page,ad_id,ad_erid,event_param_ad_source,event_param_content,event_param_term,event_param_rick_ad_channel_identifiers,event_param_rick_additional_campaign_data,event_param_rick_ad_identifiers,event_param_rick_campaign_attribution,event_param_rick_fb_client_id,event_param_rick_rid,event_param_rick_user_agent,event_param_rick_url,device_category,campaign_id",
        [],
    )

    print("📊 СЕССИОННЫЙ АНАЛИЗ ВСЕХ СОБЫТИЙ ПО CLIENTID")
    print(f"📊 Всего событий: {len(events)}")
    print("=" * 120)

    # Создаем экземпляр правил
    rules = SourceMediumRules()

    # Группируем события по client_id
    sessions = defaultdict(list)
    for event in events:
        client_id = event.get("client_id", "")
        if client_id:
            sessions[client_id].append(event)

    print(f"📊 Найдено сессий: {len(sessions)}")
    print("=" * 120)

    # Выбираем 3 случайные сессии для детального анализа
    random.seed(42)
    random_sessions = random.sample(list(sessions.keys()), min(3, len(sessions)))

    for i, client_id in enumerate(random_sessions, 1):
        session_events = sessions[client_id]

        # Сортируем события по времени
        session_events.sort(key=lambda x: x.get("event_param_date_hour_minute", ""))

        print(f"\n🔍 СЕССИЯ {i} - CLIENT_ID: {client_id}")
        print(f"📊 Событий в сессии: {len(session_events)}")
        print("=" * 120)

        # Анализируем каждое событие в сессии
        for j, event in enumerate(session_events):
            print(f"\n📅 СОБЫТИЕ {j + 1} в сессии:")
            print(f"   Время: {event.get('event_param_date_hour_minute', '')}")
            print(f"   Страница: {event.get('page_location', '')}")
            print(f"   sourceMedium: {event.get('source_medium', '')}")
            print(f"   raw_source_medium: {event.get('raw_source_medium', '')}")
            print(f"   applied_rules: {event.get('applied_rules', '')}")

            # Анализируем все 71 поле с учетом сессии
            analysis_result = rules.analyze_all_71_fields(event, session_events)

            print("\n🎯 АНАЛИЗ 71 ПОЛЯ:")
            print(
                f"   Ожидаемое sourceMedium: {analysis_result.get('expected_source_medium', '')}"
            )
            print(
                f"   Ожидаемое rawSourceMedium: {analysis_result.get('expected_raw_source_medium', '')}"
            )

            # Проверяем противоречия
            contradictions = analysis_result.get("contradictions", [])
            if contradictions:
                print("   🚨 ПРОТИВОРЕЧИЯ:")
                for contradiction in contradictions:
                    print(f"      - {contradiction}")
            else:
                print("   ✅ Противоречий не найдено")

            # Выводим ключевые поля для анализа
            print("\n🔍 КЛЮЧЕВЫЕ ПОЛЯ:")
            print(
                f"   custom_group_campaign_grouping: {event.get('custom_group_campaign_grouping', '')}"
            )
            print(f"   campaign: {event.get('campaign', '')}")
            print(
                f"   event_param_last_traffic_source: {event.get('event_param_last_traffic_source', '')}"
            )
            print(
                f"   event_param_page_referrer: {event.get('event_param_page_referrer', '')}"
            )

            # Click ID анализ
            rick_ad_identifiers = event.get(
                "event_param_rick_ad_channel_identifiers", ""
            )
            if (
                rick_ad_identifiers
                and rick_ad_identifiers != "gclid:;fbclid:;yclid:;ysclid:"
            ):
                print(
                    f"   event_param_rick_ad_channel_identifiers: {rick_ad_identifiers}"
                )

            # UTM анализ
            utm_source = event.get("event_param_source", "")
            utm_medium = event.get("event_param_medium", "")
            if utm_source or utm_medium:
                print(f"   UTM: source='{utm_source}', medium='{utm_medium}'")

            print("-" * 80)

        # Анализ наследования sourceMedium в сессии
        print("\n🔄 АНАЛИЗ НАСЛЕДОВАНИЯ SOURCEMEDIUM В СЕССИИ:")

        # Проверяем, наследуется ли sourceMedium от предыдущих событий
        for j in range(1, len(session_events)):
            current_event = session_events[j]
            previous_event = session_events[j - 1]

            current_source_medium = current_event.get("source_medium", "")
            previous_source_medium = previous_event.get("source_medium", "")

            if current_source_medium == previous_source_medium:
                print(
                    f"   Событие {j + 1}: sourceMedium наследуется от события {j} = '{current_source_medium}'"
                )
            else:
                print(
                    f"   Событие {j + 1}: sourceMedium изменилось с '{previous_source_medium}' на '{current_source_medium}'"
                )

        print("=" * 120)


if __name__ == "__main__":
    analyze_all_events_in_session()
