#!/usr/bin/env python3
"""
Migration Workflow Core - Основные методы миграции
Registry Standard v5.8 Compliance

JTBD: Когда нужно безопасно мигрировать с legacy MCP сервера на новый,
я хочу использовать атомарные команды миграции,
чтобы обеспечить безопасный переход без потери функциональности.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from .backup import MigrationBackup
from .registry import RegistryManager
from .validation import MigrationValidator

logger = logging.getLogger(__name__)


class MigrationWorkflow:
    """
    Migration Workflow для безопасной миграции с legacy на новый MCP сервер

    Atomic operations с reflection checkpoints согласно Registry Standard v5.8
    """

    def __init__(self) -> None:
        """Initialize migration workflow"""
        # Определяем правильные пути относительно текущего файла
        current_file = Path(__file__)
        self.project_root = (
            current_file.parent.parent.parent.parent.parent
        )  # На один уровень выше
        self.legacy_server_path = (
            self.project_root
            / "advising_platform"
            / "src"
            / "mcp"
            / "mcp_cursor_server.py"
        )
        self.new_server_path = (
            self.project_root
            / "[standards .md]"
            / "platform"
            / "mcp_server"
            / "src"
            / "mcp_server.py"
        )
        self.cursor_config_path = self.project_root / ".cursor" / "mcp.json"
        self.backup_dir = self.project_root / "backups" / "migration"

        # Инициализируем компоненты
        self.validator = MigrationValidator(self.project_root)
        self.backup_manager = MigrationBackup(self.backup_dir)
        self.registry_manager = RegistryManager(self.project_root)

        # Создаем backup директорию
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    async def _reflection_checkpoint(
        self, step_name: str, result: dict[str, Any]
    ) -> bool:
        """Reflection checkpoint после каждого шага"""
        logger.info(f"🔍 Reflection checkpoint: {step_name}")

        if result.get("status") == "success":
            logger.info(f"✅ {step_name} - УСПЕШНО")
            return True
        elif result.get("status") == "warning":
            logger.warning(f"⚠️ {step_name} - ПРЕДУПРЕЖДЕНИЕ")
            return True
        else:
            logger.error(f"❌ {step_name} - ОШИБКА")
            return False

    async def migrate_legacy_to_modern(
        self, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Атомарная миграция с legacy на новый сервер"""

        logger.info("🚀 Начинаем атомарную миграцию legacy → новый сервер")

        # STEP 0: Чтение стандарта
        step_0_result = await self.validator.read_implementing_standard()
        if not await self._reflection_checkpoint("step_0_read_standard", step_0_result):
            return {"status": "error", "migration_failed": True, "step": "step_0"}

        # STEP 1: Backup legacy configuration
        step_1_result = await self.backup_manager.backup_legacy_config(
            self.legacy_server_path, self.cursor_config_path
        )
        if not await self._reflection_checkpoint("step_1_backup_legacy", step_1_result):
            return {"status": "error", "migration_failed": True, "step": "step_1"}

        # STEP 2: Validate new server
        step_2_result = await self.validator.validate_new_server(self.new_server_path)
        if not await self._reflection_checkpoint(
            "step_2_validate_new_server", step_2_result
        ):
            return {"status": "error", "migration_failed": True, "step": "step_2"}

        # STEP 3: Update Cursor configuration
        step_3_result = await self.backup_manager.update_cursor_config(
            self.cursor_config_path, self.new_server_path
        )
        if not await self._reflection_checkpoint(
            "step_3_update_cursor_config", step_3_result
        ):
            return {"status": "error", "migration_failed": True, "step": "step_3"}

        # STEP 4: Test migration
        step_4_result = await self.validator.test_migration(self.new_server_path)
        if not await self._reflection_checkpoint(
            "step_4_test_migration", step_4_result
        ):
            return {"status": "error", "migration_failed": True, "step": "step_4"}

        logger.info("✅ Атомарная миграция завершена успешно!")
        return {
            "status": "success",
            "migration_completed": True,
            "timestamp": datetime.now().isoformat(),
            "steps_completed": ["step_0", "step_1", "step_2", "step_3", "step_4"],
        }

    async def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute migration workflow"""
        command = arguments.get("command", "migrate")

        if command == "migrate":
            return await self.migrate_legacy_to_modern(arguments)
        elif command == "validate":
            return await self.validator.validate_migration_success(self.new_server_path)
        elif command == "rollback":
            return await self.backup_manager.rollback_migration_if_needed(arguments)
        elif command == "update_registry":
            return await self.registry_manager.update_registry_legacy_deprecated()
        else:
            return {"status": "error", "unknown_command": command}
