#!/usr/bin/env python3
"""
Анализ сессий по clientID - группировка событий и анализ предыдущих событий
"""

import json
import random
import sys
import os
from collections import defaultdict
from datetime import datetime

def analyze_sessions_by_client_id():
    """Анализ сессий по clientID с группировкой событий"""

    # Загружаем реальные данные
    data_file = "[rick.ai]/knowledge base/in progress/1. when new lead come/when sourceMedium, ym_sourceMedium analise/widget_225114_sourcemedium_data.json"

    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Файл {data_file} не найден!")
        return

    # Получаем все события
    events = data.get("groups", {}).get("applied_rules,day,client_id,event_param_date_hour_minute,click_id,channel_group,source_medium,raw_source_medium,event_param_source,event_param_medium,event_param_page_referrer,page_location,event_param_last_search_engine,event_param_last_search_engine_root,event_param_last_adv_engine,event_param_last_traffic_source,event_param_last_social_network,event_param_last_social_network_profile,event_param_campaign,custom_group_campaign_grouping,campaign,ad_group_combined,ad_group,keyword,ad_content,ad_utm_source_medium,campaign_name,campaign_status,ad_utm_keyword,ad_combined,ad_group_name,ad_group_status,ad_campaign_type,ad_group_type,ad_name,ad_status,ad_placement_domain,ad_placement_url,ad_utm_campaign,ad_subtype,ad_utm_content,ad_title,ad_text,ad_url,ad_thumbnail_url,ad_preview_url,ad_source,ga_data_import_id,all_landing_page_path,ad_group_id,ad_type,ad_landing_page,ad_id,ad_erid,event_param_ad_source,event_param_content,event_param_term,event_param_rick_ad_channel_identifiers,event_param_rick_additional_campaign_data,event_param_rick_ad_identifiers,event_param_rick_campaign_attribution,event_param_rick_fb_client_id,event_param_rick_rid,event_param_rick_user_agent,event_param_rick_url,device_category,campaign_id", [])

    print(f"📊 Анализ сессий по clientID - группировка событий")
    print(f"📊 Всего событий: {len(events)}")
    print("=" * 120)

    # Группируем события по client_id
    sessions = defaultdict(list)
    for event in events:
        client_id = event.get('client_id', '')
        if client_id:
            sessions[client_id].append(event)

    print(f"📊 Найдено сессий: {len(sessions)}")
    print("=" * 120)

    # Выбираем 5 случайных сессий для анализа
    random.seed(42)
    random_sessions = random.sample(list(sessions.keys()), min(5, len(sessions)))

    for i, client_id in enumerate(random_sessions, 1):
        session_events = sessions[client_id]

        # Сортируем события по времени
        session_events.sort(key=lambda x: x.get('event_param_date_hour_minute', ''))

        print(f"\n🔍 СЕССИЯ {i} - CLIENT_ID: {client_id}")
        print(f"📊 Событий в сессии: {len(session_events)}")
        print("=" * 120)

        # Анализируем каждое событие в сессии
        for j, event in enumerate(session_events):
            print(f"\n📅 СОБЫТИЕ {j+1} в сессии:")
            print(f"   Время: {event.get('event_param_date_hour_minute', '')}")
            print(f"   Страница: {event.get('page_location', '')}")
            print(f"   sourceMedium: {event.get('source_medium', '')}")
            print(f"   raw_source_medium: {event.get('raw_source_medium', '')}")
            print(f"   applied_rules: {event.get('applied_rules', '')}")

            # Ключевые поля для анализа
            print(f"   custom_group_campaign_grouping: {event.get('custom_group_campaign_grouping', '')}")
            print(f"   campaign: {event.get('campaign', '')}")
            print(f"   event_param_last_traffic_source: {event.get('event_param_last_traffic_source', '')}")
            print(f"   event_param_page_referrer: {event.get('event_param_page_referrer', '')}")

            # Click ID анализ
            rick_ad_identifiers = event.get("event_param_rick_ad_channel_identifiers", "")
            if rick_ad_identifiers and rick_ad_identifiers != "gclid:;fbclid:;yclid:;ysclid:":
                print(f"   event_param_rick_ad_channel_identifiers: {rick_ad_identifiers}")

            # UTM анализ
            utm_source = event.get("event_param_source", "")
            utm_medium = event.get("event_param_medium", "")
            if utm_source or utm_medium:
                print(f"   UTM: source='{utm_source}', medium='{utm_medium}'")

            print("-" * 80)

        # Анализ противоречий в сессии
        print(f"\n🔍 АНАЛИЗ ПРОТИВОРЕЧИЙ В СЕССИИ:")

        # Берем последнее событие для анализа
        last_event = session_events[-1]
        source_medium = last_event.get("source_medium", "")
        raw_source_medium = last_event.get("raw_source_medium", "")

        print(f"📝 ПОСЛЕДНЕЕ СОБЫТИЕ:")
        print(f"   sourceMedium: '{source_medium}'")
        print(f"   raw_source_medium: '{raw_source_medium}'")

        # Анализируем что должно быть
        print(f"\n🎯 ЧТО ДОЛЖНО БЫТЬ:")

        # Проверяем custom_group_campaign_grouping
        custom_group = last_event.get("custom_group_campaign_grouping", "")
        campaign = last_event.get("campaign", "")

        if custom_group and custom_group != "google.ru":
            print(f"   custom_group_campaign_grouping: '{custom_group}' - указывает на источник")
        elif campaign and campaign != "google.ru":
            print(f"   campaign: '{campaign}' - указывает на источник")

        # Проверяем предыдущие события в сессии
        if len(session_events) > 1:
            print(f"\n📚 ПРЕДЫДУЩИЕ СОБЫТИЯ В СЕССИИ:")
            for k, prev_event in enumerate(session_events[:-1]):
                prev_source_medium = prev_event.get("source_medium", "")
                prev_time = prev_event.get("event_param_date_hour_minute", "")
                print(f"   Событие {k+1} ({prev_time}): sourceMedium='{prev_source_medium}'")

        # Определяем ожидаемое значение
        expected_source_medium = ""
        expected_raw_source_medium = ""

        # Приоритет 1: Click ID
        click_id_found = False
        rick_ad_identifiers = last_event.get("event_param_rick_ad_channel_identifiers", "")
        if rick_ad_identifiers and rick_ad_identifiers != "gclid:;fbclid:;yclid:;ysclid:":
            if "yclid:" in rick_ad_identifiers:
                click_id_found = True
                expected_source_medium = "yandex / cpc"
                expected_raw_source_medium = "yandex / cpc"
            elif "gclid:" in rick_ad_identifiers:
                click_id_found = True
                expected_source_medium = "google / cpc"
                expected_raw_source_medium = "google / cpc"
            elif "fbclid:" in rick_ad_identifiers:
                click_id_found = True
                expected_source_medium = "facebook / cpc"
                expected_raw_source_medium = "facebook / cpc"

        # Приоритет 2: UTM
        if not click_id_found:
            utm_source = last_event.get("event_param_source", "")
            utm_medium = last_event.get("event_param_medium", "")
            if utm_source and utm_medium:
                expected_source_medium = f"{utm_source} / {utm_medium}"
                expected_raw_source_medium = f"{utm_source} / {utm_medium}"

        # Приоритет 3: custom_group_campaign_grouping
        if not click_id_found and not expected_source_medium:
            if custom_group:
                # Исправляем google.ru на google
                if custom_group == "google.ru":
                    expected_source_medium = "google / organic"
                    expected_raw_source_medium = "google / organic"
                else:
                    expected_source_medium = f"{custom_group} / organic"
                    expected_raw_source_medium = f"{custom_group} / organic"

        # Приоритет 4: campaign
        if not expected_source_medium and campaign:
            if campaign == "google.ru":
                expected_source_medium = "google / organic"
                expected_raw_source_medium = "google / organic"
            else:
                expected_source_medium = f"{campaign} / organic"
                expected_raw_source_medium = f"{campaign} / organic"

        # Приоритет 5: Traffic Source
        if not expected_source_medium:
            traffic_source = last_event.get("event_param_last_traffic_source", "")
            if traffic_source and traffic_source != "internal":
                expected_source_medium = f"{traffic_source} / {traffic_source}"
                expected_raw_source_medium = f"{traffic_source} / {traffic_source}"

        # Fallback
        if not expected_source_medium:
            expected_source_medium = "direct / none"
            expected_raw_source_medium = "direct / none"

        print(f"   Ожидаемое: '{expected_source_medium}'")

        # Сравниваем
        print(f"\n⚖️ СРАВНЕНИЕ:")
        source_medium_match = source_medium == expected_source_medium
        raw_source_medium_match = raw_source_medium == expected_raw_source_medium

        print(f"   sourceMedium: '{source_medium}' vs '{expected_source_medium}' = {'✅' if source_medium_match else '❌'}")
        print(f"   raw_source_medium: '{raw_source_medium}' vs '{expected_raw_source_medium}' = {'✅' if raw_source_medium_match else '❌'}")

        if not source_medium_match or not raw_source_medium_match:
            print(f"   🚨 ПРОТИВОРЕЧИЕ НАЙДЕНО!")
            if not source_medium_match:
                print(f"      sourceMedium: Rick.ai записал '{source_medium}', должно быть '{expected_source_medium}'")
            if not raw_source_medium_match:
                print(f"      raw_source_medium: Rick.ai записал '{raw_source_medium}', должно быть '{expected_raw_source_medium}'")
        else:
            print(f"   ✅ Противоречий не найдено")

        print("=" * 120)

if __name__ == "__main__":
    analyze_sessions_by_client_id()