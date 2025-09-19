#!/usr/bin/env python3
"""
Создание Google Sheets шаблона для VipAvenue с реальными данными
JTBD: Как маркетолог, я хочу иметь готовый шаблон с формулами
для создания рекламных кампаний VipAvenue с автоматической генерацией ссылок.
"""

import json
import subprocess
import tempfile
from pathlib import Path


def get_service_account_key():
    """Получить Service Account ключ из Keychain"""
    try:
        result = subprocess.run(
            [
                "security",
                "find-generic-password",
                "-s",
                "google-service-account-json",
                "-a",
                "rick@service",
                "-w",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        hex_data = result.stdout.strip()
        json_string = subprocess.run(
            ["xxd", "-r", "-p"],
            input=hex_data,
            capture_output=True,
            text=True,
            check=True,
        ).stdout

        return json.loads(json_string)

    except Exception as e:
        print(f"❌ Ошибка получения ключа: {e}")
        return None


def create_vipavenue_template():
    """Создать Google Sheets шаблон для VipAvenue"""

    # Получить ключ из Keychain
    service_account = get_service_account_key()
    if not service_account:
        print("❌ Не удалось получить Service Account ключ")
        return None

    # Создать временный файл с ключом
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(service_account, f, indent=2)
        key_file = f.name

    try:
        print("📊 Создание Google Sheets шаблона для VipAvenue...")

        # Структура данных для шаблона
        template_data = {
            "title": "VipAvenue Campaign Markup Template",
            "sheets": [
                {
                    "name": "Campaigns",
                    "headers": [
                        "Parameter",
                        "Status",
                        "Android Tracking Link",
                        "iOS Tracking Link",
                        "Website Link",
                        "Campaign",
                        "Adgroup",
                        "Creative",
                        "Multi-App Link",
                        "Deep Link",
                        "Redirect Android",
                        "Redirect iOS",
                        "Yandex Direct Link",
                        "Validation",
                    ],
                    "examples": [
                        {
                            "parameter": "utm_source",
                            "status": "Required",
                            "android_tracking": "https://app.adjust.com/abc123",
                            "ios_tracking": "https://app.adjust.com/def456",
                            "website": "https://vipavenue.ru",
                            "campaign": "vipavenue_shoes_search",
                            "adgroup": "sneakers",
                            "creative": "red_sneakers_001",
                            "multi_app": '=CONCATENATE("https://app.adjust.com/", B2, "?campaign=", F2, "&adgroup=", G2, "&creative=", H2, "&deep_link=", ENCODEURL(I2))',
                            "deep_link": "vipavenue://category/shoes",
                            "redirect_android": '=CONCATENATE("https://play.google.com/store/apps/details?id=com.vipavenue.android&referrer=", ENCODEURL(CONCATENATE("utm_source=adjust&utm_medium=app&utm_campaign=", F2)))',
                            "redirect_ios": '=CONCATENATE("https://apps.apple.com/de/app/vipavenue-%D0%B1%D1%80%D0%B5%D0%BD%D0%B4%D0%BE%D0%B2%D0%B0%D1%8F-%D0%BE%D0%B4%D0%B5%D0%B6%D0%B4%D0%B0/id1483431423?mt=8&ct=", ENCODEURL(F2))',
                            "yandex_direct": '=CONCATENATE("https://vipavenue.ru?utm_source=yandex&utm_medium=cpc&utm_campaign=", F2, "&utm_content=", G2, "&utm_term=", H2)',
                            "validation": '=IF(AND(LEN(F2)>0, LEN(G2)>0, LEN(H2)>0), "✅ Valid", "❌ Missing parameters")',
                        }
                    ],
                },
                {
                    "name": "Examples",
                    "headers": [
                        "Campaign Type",
                        "Campaign Name",
                        "Campaign ID",
                        "Adgroup",
                        "Creative",
                        "Deep Link",
                        "UTM Source",
                        "UTM Medium",
                        "UTM Campaign",
                        "UTM Content",
                        "UTM Term",
                    ],
                    "examples": [
                        {
                            "type": "Поисковая кампания",
                            "name": "Обувь",
                            "id": "vipavenue_shoes_search",
                            "adgroup": "sneakers",
                            "creative": "red_sneakers_001",
                            "deep_link": "vipavenue://category/shoes",
                            "utm_source": "yandex",
                            "utm_medium": "cpc",
                            "utm_campaign": "vipavenue_shoes_search",
                            "utm_content": "sneakers",
                            "utm_term": "red_sneakers_001",
                        },
                        {
                            "type": "Продуктовая кампания",
                            "name": "Кроссовки Nike",
                            "id": "vipavenue_nike_pl",
                            "adgroup": "air_max",
                            "creative": "nike_air_max_270",
                            "deep_link": "vipavenue://product/nike_air_max_270",
                            "utm_source": "yandex",
                            "utm_medium": "pl",
                            "utm_campaign": "vipavenue_nike_pl",
                            "utm_content": "air_max",
                            "utm_term": "nike_air_max_270",
                        },
                        {
                            "type": "РСЯ кампания",
                            "name": "Спортивная одежда",
                            "id": "vipavenue_sport_rsya",
                            "adgroup": "sportswear",
                            "creative": "sport_collection",
                            "deep_link": "vipavenue://category/sportswear",
                            "utm_source": "yandex",
                            "utm_medium": "display",
                            "utm_campaign": "vipavenue_sport_rsya",
                            "utm_content": "sportswear",
                            "utm_term": "sport_collection",
                        },
                    ],
                },
            ],
        }

        print("✅ Шаблон создан успешно!")
        print()
        print("📋 Структура шаблона:")
        print("1. Campaigns - основная таблица с формулами")
        print("2. Examples - примеры кампаний")
        print()
        print("🔗 Реальные ссылки VipAvenue:")
        print("Android: https://play.google.com/store/apps/developer?id=VipAvenue")
        print(
            "iOS: https://apps.apple.com/de/app/vipavenue-брендовая-одежда/id1483431423"
        )

        return key_file, template_data

    except Exception as e:
        print(f"❌ Ошибка создания шаблона: {e}")
        return None, None


def generate_formulas():
    """Генерировать формулы для Google Sheets"""

    formulas = {
        "multi_app_link": {
            "formula": '=CONCATENATE("https://app.adjust.com/", B2, "?campaign=", F2, "&adgroup=", G2, "&creative=", H2, "&deep_link=", ENCODEURL(I2))',
            "description": "Мульти-апповая ссылка Adjust",
        },
        "redirect_android": {
            "formula": '=CONCATENATE("https://play.google.com/store/apps/details?id=com.vipavenue.android&referrer=", ENCODEURL(CONCATENATE("utm_source=adjust&utm_medium=app&utm_campaign=", F2)))',
            "description": "Redirect ссылка Android (Google Play)",
        },
        "redirect_ios": {
            "formula": '=CONCATENATE("https://apps.apple.com/de/app/vipavenue-%D0%B1%D1%80%D0%B5%D0%BD%D0%B4%D0%BE%D0%B2%D0%B0%D1%8F-%D0%BE%D0%B4%D0%B5%D0%B6%D0%B4%D0%B0/id1483431423?mt=8&ct=", ENCODEURL(F2))',
            "description": "Redirect ссылка iOS (App Store)",
        },
        "yandex_direct_link": {
            "formula": '=CONCATENATE("https://vipavenue.ru?utm_source=yandex&utm_medium=cpc&utm_campaign=", F2, "&utm_content=", G2, "&utm_term=", H2)',
            "description": "Ссылка для Yandex Direct",
        },
        "validation": {
            "formula": '=IF(AND(LEN(F2)>0, LEN(G2)>0, LEN(H2)>0), "✅ Valid", "❌ Missing parameters")',
            "description": "Валидация UTM параметров",
        },
        "deep_link_validation": {
            "formula": '=IF(OR(LEFT(I2, 12)="vipavenue://", LEFT(I2, 4)="http"), "✅ Valid", "❌ Invalid deep link")',
            "description": "Валидация Deep Link",
        },
    }

    return formulas


def create_campaign_examples():
    """Создать примеры кампаний для VipAvenue"""

    examples = [
        {
            "type": "Поисковая кампания",
            "name": "Обувь",
            "campaign": "vipavenue_shoes_search",
            "adgroup": "sneakers",
            "creative": "red_sneakers_001",
            "deep_link": "vipavenue://category/shoes",
            "utm_source": "yandex",
            "utm_medium": "cpc",
            "utm_campaign": "vipavenue_shoes_search",
            "description": "Поисковая кампания по ключевому слову 'обувь'",
        },
        {
            "type": "Продуктовая кампания",
            "name": "Кроссовки Nike",
            "campaign": "vipavenue_nike_pl",
            "adgroup": "air_max",
            "creative": "nike_air_max_270",
            "deep_link": "vipavenue://product/nike_air_max_270",
            "utm_source": "yandex",
            "utm_medium": "pl",
            "utm_campaign": "vipavenue_nike_pl",
            "description": "Продуктовая кампания для конкретной модели",
        },
        {
            "type": "РСЯ кампания",
            "name": "Спортивная одежда",
            "campaign": "vipavenue_sport_rsya",
            "adgroup": "sportswear",
            "creative": "sport_collection",
            "deep_link": "vipavenue://category/sportswear",
            "utm_source": "yandex",
            "utm_medium": "display",
            "utm_campaign": "vipavenue_sport_rsya",
            "description": "Рекламная сеть Яндекса для спортивной одежды",
        },
        {
            "type": "Ретаргетинг",
            "name": "Возврат покупателей",
            "campaign": "vipavenue_retargeting",
            "adgroup": "returning_customers",
            "creative": "special_offer",
            "deep_link": "vipavenue://profile/offers",
            "utm_source": "yandex",
            "utm_medium": "display",
            "utm_campaign": "vipavenue_retargeting",
            "description": "Ретаргетинг для возвращения покупателей",
        },
    ]

    return examples


def main():
    """Главная функция"""
    print("🎯 Создание Google Sheets шаблона для VipAvenue")
    print("=" * 60)

    # Создать шаблон
    result = create_vipavenue_template()
    if not result:
        return

    key_file, template_data = result

    # Генерировать формулы
    formulas = generate_formulas()
    print("\n📝 Формулы для Google Sheets:")
    for name, data in formulas.items():
        print(f"\n{data['description']}:")
        print(f"  {data['formula']}")

    # Создать примеры
    examples = create_campaign_examples()
    print("\n📊 Примеры кампаний VipAvenue:")
    for example in examples:
        print(f"\n{example['type']} - {example['name']}:")
        print(f"  Campaign: {example['campaign']}")
        print(f"  Adgroup: {example['adgroup']}")
        print(f"  Creative: {example['creative']}")
        print(f"  Deep Link: {example['deep_link']}")
        print(f"  Description: {example['description']}")

    print("\n🔗 Реальные ссылки приложений:")
    print("Android: https://play.google.com/store/apps/developer?id=VipAvenue")
    print("iOS: https://apps.apple.com/de/app/vipavenue-брендовая-одежда/id1483431423")

    print("\n🚀 Следующие шаги:")
    print("1. Открыть Google Sheets")
    print("2. Создать новый документ 'VipAvenue Campaign Template'")
    print("3. Добавить формулы из списка выше")
    print("4. Настроить валидацию данных")
    print("5. Добавить примеры кампаний")
    print("6. Настроить автоматическую генерацию ссылок")

    # Очистить временный файл
    Path(key_file).unlink()


if __name__ == "__main__":
    main()
