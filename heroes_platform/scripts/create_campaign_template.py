#!/usr/bin/env python3
"""
Скрипт для создания Google Sheets шаблона разметки рекламных кампаний

JTBD: Как маркетолог, я хочу иметь готовый шаблон для разметки кампаний,
чтобы стандартизировать процесс и избежать ошибок.
"""

# Import credentials manager
import sys

import requests

try:
    from shared.credentials_manager import (
        _get_google_access_token,
        get_google_credentials,
    )
except ImportError:
    print("❌ Не удалось импортировать credentials_manager")
    sys.exit(1)


def create_campaign_template_sheet() -> str:
    """Создать Google Sheets шаблон для разметки кампаний"""

    try:
        # Получаем credentials
        credentials = get_google_credentials()
        if not credentials:
            return "❌ Google credentials not found"

        # Получаем access token
        if "client_id" in credentials:
            access_token = _get_google_access_token(credentials)
            if not access_token:
                return "❌ Failed to get access token"
        else:
            return "❌ OAuth 2.0 credentials required"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        # Создаем новый spreadsheet
        create_url = "https://sheets.googleapis.com/v4/spreadsheets"
        spreadsheet_data = {
            "properties": {"title": "Шаблон разметки рекламных кампаний - Rick.ai"},
            "sheets": [
                {
                    "properties": {
                        "title": "Кампании",
                        "gridProperties": {"rowCount": 1000, "columnCount": 20},
                    }
                },
                {
                    "properties": {
                        "title": "Шаблоны",
                        "gridProperties": {"rowCount": 100, "columnCount": 20},
                    }
                },
                {
                    "properties": {
                        "title": "Инструкции",
                        "gridProperties": {"rowCount": 100, "columnCount": 10},
                    }
                },
            ],
        }

        response = requests.post(create_url, headers=headers, json=spreadsheet_data)

        if response.status_code != 200:
            return f"❌ Error creating spreadsheet: {response.status_code} - {response.text}"

        spreadsheet = response.json()
        spreadsheet_id = spreadsheet["spreadsheetId"]

        # Добавляем заголовки в лист "Кампании"
        headers_data = [
            [
                "campaign_name",
                "campaign_type",
                "platform",
                "budget",
                "start_date",
                "end_date",
                "target_audience",
                "utm_source",
                "utm_medium",
                "utm_campaign",
                "utm_content",
                "utm_term",
                "adjust_tracker",
                "adjust_network",
                "adjust_campaign",
                "adjust_creative",
                "adjust_click_label",
                "appmetrica_source",
                "appmetrica_campaign",
                "appmetrica_content",
            ]
        ]

        update_url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/Кампании!A1:T1?valueInputOption=RAW"
        update_data = {"values": headers_data}

        response = requests.put(update_url, headers=headers, json=update_data)

        if response.status_code != 200:
            return (
                f"❌ Error updating headers: {response.status_code} - {response.text}"
            )

        # Добавляем примеры данных
        example_data = [
            [
                "vipavenue_ios_black_friday_2025",
                "yandex_direct",
                "ios",
                "50000",
                "2025-01-15",
                "2025-02-15",
                "women_25_45_fashion",
                "yandex_direct",
                "cpc",
                "vipavenue_ios_black_friday_2025",
                "banner_1200x628_red",
                "платье_вечернее",
                "abc123",
                "yandex_direct",
                "vipavenue_ios_black_friday_2025",
                "banner_1200x628_red",
                "women_25_45_fashion",
                "yandex_direct",
                "vipavenue_ios_black_friday_2025",
                "banner_1200x628_red",
            ],
            [
                "vipavenue_android_cpa_lead_2025",
                "cpa_network",
                "android",
                "30000",
                "2025-01-15",
                "2025-02-15",
                "men_18_35_tech",
                "cpa_network",
                "banner",
                "vipavenue_android_cpa_lead_2025",
                "banner_728x90_blue",
                "смартфон_android",
                "def456",
                "cpa_network",
                "vipavenue_android_cpa_lead_2025",
                "banner_728x90_blue",
                "men_18_35_tech",
                "cpa_network",
                "vipavenue_android_cpa_lead_2025",
                "banner_728x90_blue",
            ],
        ]

        update_url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/Кампании!A2:T3?valueInputOption=RAW"
        update_data = {"values": example_data}

        response = requests.put(update_url, headers=headers, json=update_data)

        if response.status_code != 200:
            return (
                f"❌ Error updating examples: {response.status_code} - {response.text}"
            )

        # Добавляем инструкции в лист "Инструкции"
        instructions_data = [
            ["ИНСТРУКЦИИ ПО ЗАПОЛНЕНИЮ ШАБЛОНА"],
            [""],
            ["ОБЯЗАТЕЛЬНЫЕ ПОЛЯ:"],
            [
                "campaign_name",
                "Название кампании (без пробелов, используйте подчеркивания)",
            ],
            ["campaign_type", "Тип кампании: yandex_direct, cpa_network, social"],
            ["platform", "Платформа: ios, android, desktop, multi"],
            [
                "utm_source",
                "Источник трафика: yandex_direct, cpa_network, facebook, etc.",
            ],
            ["utm_medium", "Канал: cpc, banner, video, email"],
            ["utm_campaign", "Название кампании (должно совпадать с campaign_name)"],
            ["adjust_tracker", "Трекер в Adjust (получить из Adjust dashboard)"],
            ["adjust_network", "Сеть в Adjust (должна совпадать с utm_source)"],
            [
                "adjust_campaign",
                "Название кампании в Adjust (должно совпадать с campaign_name)",
            ],
            [""],
            ["РЕКОМЕНДУЕМЫЕ ПОЛЯ:"],
            [
                "utm_content",
                "Описание креатива: banner_1200x628_red, video_15s_fashion",
            ],
            ["utm_term", "Ключевые слова (для поисковых кампаний)"],
            ["adjust_creative", "Название креатива в Adjust"],
            ["adjust_click_label", "Метка для сегментации аудитории"],
            [""],
            ["ПРАВИЛА НАИМЕНОВАНИЯ:"],
            ["- Используйте подчеркивания вместо пробелов"],
            ["- Используйте нижний регистр"],
            ["- Добавляйте год в название кампании"],
            ["- Указывайте платформу в названии"],
            ["- Пример: vipavenue_ios_black_friday_2025"],
        ]

        update_url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/Инструкции!A1:A25?valueInputOption=RAW"
        update_data = {"values": instructions_data}

        response = requests.put(update_url, headers=headers, json=update_data)

        if response.status_code != 200:
            return f"❌ Error updating instructions: {response.status_code} - {response.text}"

        # Форматируем заголовки
        format_url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}:batchUpdate"
        format_data = {
            "requests": [
                {
                    "repeatCell": {
                        "range": {"sheetId": 0, "startRowIndex": 0, "endRowIndex": 1},
                        "cell": {
                            "userEnteredFormat": {
                                "backgroundColor": {
                                    "red": 0.2,
                                    "green": 0.6,
                                    "blue": 0.8,
                                },
                                "textFormat": {
                                    "bold": True,
                                    "foregroundColor": {
                                        "red": 1,
                                        "green": 1,
                                        "blue": 1,
                                    },
                                },
                            }
                        },
                        "fields": "userEnteredFormat(backgroundColor,textFormat)",
                    }
                }
            ]
        }

        response = requests.post(format_url, headers=headers, json=format_data)

        spreadsheet_url = (
            f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
        )

        return f"✅ Google Sheets шаблон создан успешно!\n\n📊 URL: {spreadsheet_url}\n\n📋 Структура:\n- Лист 'Кампании': Основная таблица с данными\n- Лист 'Шаблоны': Готовые шаблоны для разных типов кампаний\n- Лист 'Инструкции': Подробные инструкции по заполнению"

    except Exception as e:
        return f"❌ Error: {str(e)}"


def main():
    """Главная функция"""
    print("🚀 Создание Google Sheets шаблона для разметки рекламных кампаний...")
    print("=" * 60)

    result = create_campaign_template_sheet()
    print(result)

    if "✅" in result:
        print("\n🎯 Следующие шаги:")
        print("1. Откройте созданный Google Sheets")
        print("2. Изучите инструкции на листе 'Инструкции'")
        print("3. Заполните данные в листе 'Кампании'")
        print("4. Используйте шаблоны для быстрого создания новых кампаний")


if __name__ == "__main__":
    main()
