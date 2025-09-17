#!/usr/bin/env python3
"""
Migration Backup - Методы backup и rollback
Registry Standard v5.8 Compliance
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class MigrationBackup:
    """Backup и rollback для миграции согласно Registry Standard v5.8"""

    def __init__(self, backup_dir: Path) -> None:
        """Initialize backup manager"""
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    async def backup_legacy_config(
        self, legacy_server_path: Path, cursor_config_path: Path
    ) -> dict[str, Any]:
        """STEP 1: Backup legacy configuration"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Backup legacy server
            if legacy_server_path.exists():
                legacy_backup_path = (
                    self.backup_dir / f"mcp_cursor_server_backup_{timestamp}.py"
                )
                shutil.copy2(legacy_server_path, legacy_backup_path)
                logger.info(f"✅ Legacy server backup создан: {legacy_backup_path}")
            else:
                logger.warning("⚠️ Legacy server файл не найден для backup")

            # Backup Cursor config
            if cursor_config_path.exists():
                cursor_backup_path = (
                    self.backup_dir / f"cursor_mcp_backup_{timestamp}.json"
                )
                shutil.copy2(cursor_config_path, cursor_backup_path)
                logger.info(f"✅ Cursor config backup создан: {cursor_backup_path}")
            else:
                logger.warning("⚠️ Cursor config файл не найден для backup")

            return {
                "status": "success",
                "backup_created": True,
                "timestamp": timestamp,
                "backup_dir": str(self.backup_dir),
            }

        except Exception as e:
            logger.error(f"❌ Ошибка создания backup: {e}")
            return {"status": "error", "backup_error": True, "error": str(e)}

    async def update_cursor_config(
        self, cursor_config_path: Path, new_server_path: Path
    ) -> dict[str, Any]:
        """STEP 3: Update Cursor configuration"""
        try:
            if not cursor_config_path.exists():
                logger.warning("⚠️ Cursor config не найден, создаем новый")
                cursor_config_path.parent.mkdir(parents=True, exist_ok=True)

            # Читаем текущий конфиг или создаем новый
            if cursor_config_path.exists():
                with open(cursor_config_path, encoding="utf-8") as f:
                    config = json.load(f)
            else:
                config = {"mcpServers": {}}

            # Обновляем путь к новому серверу
            new_server_relative = new_server_path.relative_to(
                new_server_path.parent.parent.parent.parent.parent
            )

            config["mcpServers"]["heroes_mcp"] = {
                "command": "python",
                "args": [str(new_server_relative)],
                "env": {"PYTHONPATH": str(new_server_path.parent.parent)},
            }

            # Сохраняем обновленный конфиг
            with open(cursor_config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Cursor config обновлен: {cursor_config_path}")
            return {
                "status": "success",
                "config_updated": True,
                "config_path": str(cursor_config_path),
            }

        except Exception as e:
            logger.error(f"❌ Ошибка обновления Cursor config: {e}")
            return {"status": "error", "config_error": True, "error": str(e)}

    async def rollback_migration_if_needed(
        self, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Rollback миграции если нужно"""
        try:
            should_rollback = arguments.get("rollback", False)
            if not should_rollback:
                logger.info("ℹ️ Rollback не требуется")
                return {"status": "success", "rollback_skipped": True}

            logger.info("🔄 Начинаем rollback миграции")

            # Восстанавливаем Cursor config
            config_result = await self._restore_cursor_config()
            if config_result.get("status") != "success":
                return config_result

            logger.info("✅ Rollback миграции завершен успешно")
            return {
                "status": "success",
                "rollback_completed": True,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Ошибка rollback миграции: {e}")
            return {"status": "error", "rollback_error": True, "error": str(e)}

    async def _restore_cursor_config(self) -> dict[str, Any]:
        """Восстановление Cursor config из backup"""
        try:
            # Ищем последний backup
            backup_files = list(self.backup_dir.glob("cursor_mcp_backup_*.json"))
            if not backup_files:
                logger.error("❌ Backup Cursor config не найден")
                return {"status": "error", "backup_not_found": True}

            # Берем самый новый backup
            latest_backup = max(backup_files, key=lambda f: f.stat().st_mtime)

            # Восстанавливаем конфиг
            cursor_config_path = Path.home() / ".cursor" / "mcp.json"
            shutil.copy2(latest_backup, cursor_config_path)

            logger.info(f"✅ Cursor config восстановлен из: {latest_backup}")
            return {
                "status": "success",
                "config_restored": True,
                "backup_file": str(latest_backup),
            }

        except Exception as e:
            logger.error(f"❌ Ошибка восстановления Cursor config: {e}")
            return {"status": "error", "restore_error": True, "error": str(e)}
