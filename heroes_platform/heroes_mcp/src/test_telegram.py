#!/usr/bin/env python3
"""
Simple Telegram test script
"""

import subprocess


def get_credentials():
    """Get credentials from Mac Keychain"""
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
        print(f"Error getting credentials: {e}")
        return None


async def test_telegram_async():
    """Test Telegram connection"""
    credentials = get_credentials()
    if not credentials:
        print("❌ No credentials available")
        return

    print("✅ Credentials loaded")

    try:
        from telethon import TelegramClient
        from telethon.sessions import StringSession

        # Create client
        client = TelegramClient(
            StringSession(credentials["session_string"]),
            int(credentials["api_id"]),
            credentials["api_hash"],
        )

        # Start client
        await client.start()

        # Get user info
        me = await client.get_me()
        print(f"✅ Connected! User: {me.first_name} (@{me.username or 'no username'})")

        # Get some dialogs
        dialogs = await client.get_dialogs(limit=5)
        print(f"✅ Found {len(dialogs)} dialogs")

        for dialog in dialogs:
            entity = dialog.entity
            title = getattr(entity, "title", None) or getattr(
                entity, "first_name", "Unknown"
            )
            print(f"  - {title} (ID: {entity.id})")

        await client.disconnect()
        print("✅ Test completed successfully")

    except Exception as e:
        print(f"❌ Error: {e}")


def test_telegram():
    """Test Telegram connection"""
    import asyncio

    asyncio.run(test_telegram_async())


if __name__ == "__main__":
    test_telegram()
