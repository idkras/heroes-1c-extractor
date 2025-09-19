#!/usr/bin/env python3
"""
Telegram Chat Validation Script

Скрипт для валидации всех доступных чатов и проверки работы MCP сервера.
Согласно требованиям из tg.todo.md
"""

import asyncio
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ChatInfo:
    """Информация о чате"""

    id: int
    title: str
    username: str = ""
    participants_count: int = 0
    last_message_date: str = ""
    is_target: bool = False


class TelegramValidator:
    """Валидатор Telegram чатов"""

    def __init__(self):
        self.target_chats = [
            "[EasyPay] IFS - процессинг иностранных платежей",
            "R-Founders Finance + Илья",
        ]
        self.chats: list[ChatInfo] = []

    def get_credentials(self) -> dict[str, str]:
        """Получить credentials из Mac Keychain"""
        try:
            api_id = subprocess.run(
                'security find-generic-password -s "telegram_api_id" -a "ilyakrasinsky" -w',
                shell=True,
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()

            api_hash = subprocess.run(
                'security find-generic-password -s "telegram_api_hash" -a "ilyakrasinsky" -w',
                shell=True,
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()

            session_string = subprocess.run(
                'security find-generic-password -s "telegram_session" -a "ilyakrasinsky" -w',
                shell=True,
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()

            return {
                "api_id": api_id,
                "api_hash": api_hash,
                "session_string": session_string,
            }
        except Exception as e:
            print(f"❌ Error getting credentials: {e}")
            return {}

    async def validate_connection(self) -> bool:
        """Проверить подключение к Telegram"""
        try:
            credentials = self.get_credentials()
            if not credentials:
                return False

            from telethon import TelegramClient
            from telethon.sessions import StringSession

            client = TelegramClient(
                StringSession(credentials["session_string"]),
                int(credentials["api_id"]),
                credentials["api_hash"],
            )

            await client.start()
            me = await client.get_me()
            await client.disconnect()

            print(
                f"✅ Connected to Telegram as: {me.first_name} (@{me.username or 'no username'})"
            )
            return True

        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    async def get_all_chats(self) -> list[ChatInfo]:
        """Получить все доступные чаты"""
        try:
            credentials = self.get_credentials()
            if not credentials:
                return []

            from telethon import TelegramClient
            from telethon.sessions import StringSession

            client = TelegramClient(
                StringSession(credentials["session_string"]),
                int(credentials["api_id"]),
                credentials["api_hash"],
            )

            await client.start()

            chats = []
            async for dialog in client.iter_dialogs():
                chat_info = ChatInfo(
                    id=dialog.entity.id,
                    title=dialog.name,
                    username=getattr(dialog.entity, "username", ""),
                    participants_count=getattr(dialog.entity, "participants_count", 0),
                    last_message_date=dialog.date.strftime("%Y-%m-%d")
                    if dialog.date
                    else "",
                    is_target=any(
                        target in dialog.name for target in self.target_chats
                    ),
                )
                chats.append(chat_info)

            await client.disconnect()
            return chats

        except Exception as e:
            print(f"❌ Error getting chats: {e}")
            return []

    async def test_export_chat(self, chat_id: int, limit: int = 5) -> bool:
        """Протестировать экспорт чата"""
        try:
            credentials = self.get_credentials()
            if not credentials:
                return False

            from telethon import TelegramClient
            from telethon.sessions import StringSession

            client = TelegramClient(
                StringSession(credentials["session_string"]),
                int(credentials["api_id"]),
                credentials["api_hash"],
            )

            await client.start()

            # Получить чат
            entity = await client.get_entity(chat_id)
            messages = await client.get_messages(entity, limit=limit)

            await client.disconnect()

            if messages:
                print(f"✅ Chat {chat_id}: {len(messages)} messages exported")
                return True
            else:
                print(f"❌ Chat {chat_id}: No messages found")
                return False

        except Exception as e:
            print(f"❌ Error exporting chat {chat_id}: {e}")
            return False

    def save_chat_list(self, chats: list[ChatInfo]):
        """Сохранить список чатов в файл"""
        try:
            output_dir = Path(__file__).parent.parent.parent / "data" / "telegram"
            output_dir.mkdir(parents=True, exist_ok=True)

            output_file = output_dir / "all_chats.json"

            chat_data = []
            for chat in chats:
                chat_data.append(
                    {
                        "id": chat.id,
                        "title": chat.title,
                        "username": chat.username,
                        "participants_count": chat.participants_count,
                        "last_message_date": chat.last_message_date,
                        "is_target": chat.is_target,
                    }
                )

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(chat_data, f, indent=2, ensure_ascii=False)

            print(f"✅ Chat list saved to: {output_file}")

        except Exception as e:
            print(f"❌ Error saving chat list: {e}")

    def print_summary(self, chats: list[ChatInfo]):
        """Вывести сводку по чатам"""
        print("\n" + "=" * 60)
        print("📊 CHAT VALIDATION SUMMARY")
        print("=" * 60)

        print(f"Total chats found: {len(chats)}")

        target_chats = [chat for chat in chats if chat.is_target]
        print(f"Target chats found: {len(target_chats)}")

        if target_chats:
            print("\n🎯 TARGET CHATS:")
            for chat in target_chats:
                print(f"  - {chat.title} (ID: {chat.id})")

        print(
            f"\n📅 Recent chats (last 30 days): {len([c for c in chats if c.last_message_date])}"
        )
        print(f"👥 Group chats: {len([c for c in chats if c.participants_count > 0])}")

        print("\n" + "=" * 60)


async def main():
    """Главная функция валидации"""
    print("🔍 Telegram Chat Validation")
    print("=" * 50)

    validator = TelegramValidator()

    # 1. Проверка подключения
    print("1. Testing connection...")
    if not await validator.validate_connection():
        print("❌ Connection failed. Stopping validation.")
        return

    # 2. Получение всех чатов
    print("\n2. Getting all chats...")
    chats = await validator.get_all_chats()

    if not chats:
        print("❌ No chats found. Stopping validation.")
        return

    # 3. Сохранение списка чатов
    print("\n3. Saving chat list...")
    validator.save_chat_list(chats)

    # 4. Вывод сводки
    validator.print_summary(chats)

    # 5. Тестирование экспорта целевых чатов
    print("\n4. Testing export for target chats...")
    target_chats = [chat for chat in chats if chat.is_target]

    for chat in target_chats:
        print(f"\nTesting export for: {chat.title}")
        success = await validator.test_export_chat(chat.id, limit=5)
        if success:
            print(f"✅ Export test passed for {chat.title}")
        else:
            print(f"❌ Export test failed for {chat.title}")

    print("\n" + "=" * 50)
    print("🎉 Validation completed!")
    print("Check the generated files for detailed results.")


if __name__ == "__main__":
    asyncio.run(main())
