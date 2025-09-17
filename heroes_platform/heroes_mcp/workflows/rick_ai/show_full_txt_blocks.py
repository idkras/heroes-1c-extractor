#!/usr/bin/env python3
"""
Показать все 71 поле для каждого кейса в txt блоках
"""

import json
import random
import sys
import os
from collections import defaultdict

def show_full_txt_blocks():
    """Показать все 71 поле для каждого кейса в txt блоках"""
    
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
    
    # Группируем события по client_id
    sessions = defaultdict(list)
    for event in events:
        client_id = event.get('client_id', '')
        if client_id:
            sessions[client_id].append(event)
    
    # Выбираем 3 случайных сессии для анализа
    random.seed(42)
    random_sessions = random.sample(list(sessions.keys()), min(3, len(sessions)))
    
    for i, client_id in enumerate(random_sessions, 1):
        session_events = sessions[client_id]
        
        # Сортируем события по времени
        session_events.sort(key=lambda x: x.get('event_param_date_hour_minute', ''))
        
        print(f"\n🔍 СЕССИЯ {i} - CLIENT_ID: {client_id}")
        print(f"📊 Событий в сессии: {len(session_events)}")
        print("=" * 120)
        
        # Показываем каждое событие в сессии
        for j, event in enumerate(session_events):
            print(f"\n📅 СОБЫТИЕ {j+1} в сессии:")
            print("=" * 120)
            
            # Выводим все 71 поле в txt блоке
            print("```txt")
            print(f"day: {event.get('day', '')}")
            print(f"event_param_date_hour_minute: {event.get('event_param_date_hour_minute', '')}")
            print()
            print(f"client_id: {event.get('client_id', '')}")
            print(f"event_param_rick_rid: {event.get('event_param_rick_rid', '')}")
            print()
            print(f"channel_group: {event.get('channel_group', '')}")
            print(f"source_medium: {event.get('source_medium', '')}")
            print(f"raw_source_medium: {event.get('raw_source_medium', '')}")
            print(f"applied_rules: {event.get('applied_rules', '')}")
            print()
            print(f"click_id: {event.get('click_id', '')}")
            print()
            print(f"event_param_source: {event.get('event_param_source', '')}")
            print(f"event_param_medium: {event.get('event_param_medium', '')}")
            print(f"event_param_last_search_engine: {event.get('event_param_last_search_engine', '')}")
            print(f"event_param_last_search_engine_root: {event.get('event_param_last_search_engine_root', '')}")
            print(f"event_param_last_adv_engine: {event.get('event_param_last_adv_engine', '')}")
            print(f"event_param_last_traffic_source: {event.get('event_param_last_traffic_source', '')}")
            print(f"event_param_last_social_network: {event.get('event_param_last_social_network', '')}")
            print(f"event_param_last_social_network_profile: {event.get('event_param_last_social_network_profile', '')}")
            print()
            print(f"device_category: {event.get('device_category', '')}")
            print(f"all_landing_page_path: {event.get('all_landing_page_path', '')}")
            print(f"page_location: {event.get('page_location', '')}")
            print(f"event_param_page_referrer: {event.get('event_param_page_referrer', '')}")
            print()
            print(f"event_param_rick_user_agent: {event.get('event_param_rick_user_agent', '')}")
            print(f"event_param_rick_url: {event.get('event_param_rick_url', '')}")
            print()
            print(f"campaign_id: {event.get('campaign_id', '')}")
            print(f"event_param_campaign: {event.get('event_param_campaign', '')}")
            print(f"custom_group_campaign_grouping: {event.get('custom_group_campaign_grouping', '')}")
            print(f"campaign: {event.get('campaign', '')}")
            print()
            print(f"ad_group_combined: {event.get('ad_group_combined', '')}")
            print(f"ad_group: {event.get('ad_group', '')}")
            print(f"keyword: {event.get('keyword', '')}")
            print(f"ad_content: {event.get('ad_content', '')}")
            print(f"ad_utm_source_medium: {event.get('ad_utm_source_medium', '')}")
            print(f"campaign_name: {event.get('campaign_name', '')}")
            print(f"campaign_status: {event.get('campaign_status', '')}")
            print(f"ad_utm_keyword: {event.get('ad_utm_keyword', '')}")
            print(f"ad_combined: {event.get('ad_combined', '')}")
            print(f"ad_group_name: {event.get('ad_group_name', '')}")
            print(f"ad_group_status: {event.get('ad_group_status', '')}")
            print(f"ad_campaign_type: {event.get('ad_campaign_type', '')}")
            print(f"ad_group_type: {event.get('ad_group_type', '')}")
            print(f"ad_name: {event.get('ad_name', '')}")
            print(f"ad_status: {event.get('ad_status', '')}")
            print(f"ad_placement_domain: {event.get('ad_placement_domain', '')}")
            print(f"ad_placement_url: {event.get('ad_placement_url', '')}")
            print(f"ad_utm_campaign: {event.get('ad_utm_campaign', '')}")
            print(f"ad_subtype: {event.get('ad_subtype', '')}")
            print(f"ad_utm_content: {event.get('ad_utm_content', '')}")
            print(f"ad_title: {event.get('ad_title', '')}")
            print(f"ad_text: {event.get('ad_text', '')}")
            print(f"ad_url: {event.get('ad_url', '')}")
            print(f"ad_thumbnail_url: {event.get('ad_thumbnail_url', '')}")
            print(f"ad_preview_url: {event.get('ad_preview_url', '')}")
            print(f"ad_source: {event.get('ad_source', '')}")
            print(f"ga_data_import_id: {event.get('ga_data_import_id', '')}")
            print(f"ad_group_id: {event.get('ad_group_id', '')}")
            print(f"ad_type: {event.get('ad_type', '')}")
            print(f"ad_landing_page: {event.get('ad_landing_page', '')}")
            print(f"ad_id: {event.get('ad_id', '')}")
            print(f"ad_erid: {event.get('ad_erid', '')}")
            print()
            print(f"event_param_ad_source: {event.get('event_param_ad_source', '')}")
            print(f"event_param_content: {event.get('event_param_content', '')}")
            print(f"event_param_term: {event.get('event_param_term', '')}")
            print(f"event_param_rick_ad_channel_identifiers: {event.get('event_param_rick_ad_channel_identifiers', '')}")
            print(f"event_param_rick_additional_campaign_data: {event.get('event_param_rick_additional_campaign_data', '')}")
            print(f"event_param_rick_ad_identifiers: {event.get('event_param_rick_ad_identifiers', '')}")
            print(f"event_param_rick_campaign_attribution: {event.get('event_param_rick_campaign_attribution', '')}")
            print(f"event_param_rick_fb_client_id: {event.get('event_param_rick_fb_client_id', '')}")
            print("```")
            print()
            
            # Анализ противоречий для этого события
            print("🔍 АНАЛИЗ ПРОТИВОРЕЧИЙ:")
            source_medium = event.get("source_medium", "")
            raw_source_medium = event.get("raw_source_medium", "")
            custom_group = event.get("custom_group_campaign_grouping", "")
            campaign = event.get("campaign", "")
            
            print(f"📝 Rick.ai записал:")
            print(f"   sourceMedium: '{source_medium}'")
            print(f"   raw_source_medium: '{raw_source_medium}'")
            
            # Определяем что должно быть
            expected_source_medium = ""
            if custom_group:
                if custom_group == "google.ru":
                    expected_source_medium = "google / organic"
                elif custom_group == "(direct type-in)":
                    expected_source_medium = "(direct type-in) / organic"
                else:
                    expected_source_medium = f"{custom_group} / organic"
            elif campaign:
                if campaign == "google.ru":
                    expected_source_medium = "google / organic"
                else:
                    expected_source_medium = f"{campaign} / organic"
            else:
                expected_source_medium = "direct / none"
            
            print(f"🎯 Должно быть: '{expected_source_medium}'")
            
            # Сравниваем
            if source_medium != expected_source_medium:
                print(f"🚨 ПРОТИВОРЕЧИЕ: '{source_medium}' vs '{expected_source_medium}'")
            else:
                print(f"✅ Совпадает")
            
            print("-" * 120)

if __name__ == "__main__":
    show_full_txt_blocks()
