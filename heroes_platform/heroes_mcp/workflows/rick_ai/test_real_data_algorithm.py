#!/usr/bin/env python3
"""
Тест алгоритма анализа 71 поля с реальными данными Асконы
"""

import json
import os
import random
import sys

# Добавляем путь к модулям
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)

from heroes_platform.heroes_mcp.workflows.rick_ai.analysis_manager import (
    SourceMediumRules,
)


def test_real_data_algorithm():
    """Тест алгоритма анализа 71 поля с реальными данными"""

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

    print("📊 Тест алгоритма анализа 71 поля с реальными данными")
    print(f"📊 Всего событий: {len(events)}")
    print("=" * 120)

    # Создаем экземпляр правил
    rules = SourceMediumRules()

    # Выбираем 10 случайных событий для анализа
    random.seed(42)
    random_events = random.sample(events, min(10, len(events)))

    contradictions_found = 0
    total_analyzed = 0

    for i, event in enumerate(random_events, 1):
        print(f"\n🔍 КЕЙС {i}:")
        print("=" * 120)

        # Анализируем событие
        analysis_result = rules.analyze_all_71_fields(event)

        total_analyzed += 1

        # Выводим результаты анализа
        print("📝 АНАЛИЗ ПОЛЕЙ:")
        for group_name, group_data in analysis_result.get("field_groups", {}).items():
            print(f"   {group_name}: {group_data}")

        # Проверяем противоречия
        contradictions = analysis_result.get("contradictions", [])
        if contradictions:
            contradictions_found += 1
            print("\n🚨 НАЙДЕНЫ ПРОТИВОРЕЧИЯ:")
            for contradiction in contradictions:
                print(f"   - {contradiction}")
        else:
            print("\n✅ Противоречий не найдено")

        # Сравниваем с ожидаемым
        expected = analysis_result.get("expected_source_medium", "")
        actual = event.get("source_medium", "")

        print("\n⚖️ СРАВНЕНИЕ:")
        print(f"   Rick.ai записал: '{actual}'")
        print(f"   Ожидалось: '{expected}'")

        if actual != expected:
            print("   ❌ НЕСООТВЕТСТВИЕ!")
        else:
            print("   ✅ СООТВЕТСТВУЕТ")

        print("=" * 120)

    # Итоговая статистика
    print("\n📊 ИТОГОВАЯ СТАТИСТИКА:")
    print(f"   Проанализировано событий: {total_analyzed}")
    print(f"   Найдено противоречий: {contradictions_found}")
    print(
        f"   Процент противоречий: {(contradictions_found / total_analyzed) * 100:.1f}%"
    )


if __name__ == "__main__":
    test_real_data_algorithm()
