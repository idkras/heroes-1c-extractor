#!/usr/bin/env python3
"""
Migration Registry - Методы работы с registry
Registry Standard v5.8 Compliance
"""

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class RegistryManager:
    """Управление registry согласно Registry Standard v5.8"""

    def __init__(self, project_root: Path) -> None:
        """Initialize registry manager"""
        self.project_root = project_root

    async def update_registry_legacy_deprecated(self) -> dict[str, Any]:
        """Обновление Registry Standard с Legacy Components секцией"""
        try:
            # Читаем Registry Standard
            read_result = await self._read_registry_standard()
            if read_result.get("status") != "success":
                return read_result

            content = read_result["content"]

            # Проверяем, есть ли уже Legacy Components секция
            if "Legacy Components (Deprecated)" in content:
                logger.info("ℹ️ Legacy Components секция уже существует")
                return {
                    "status": "success",
                    "legacy_section_exists": True,
                    "no_changes_needed": True,
                }

            # Добавляем Legacy Components секцию
            add_result = await self._add_legacy_deprecated_section(content)
            if add_result.get("status") != "success":
                return add_result

            updated_content = add_result["updated_content"]

            # Сохраняем обновленный Registry Standard
            save_result = await self._save_registry_standard(updated_content)
            if save_result.get("status") != "success":
                return save_result

            logger.info("✅ Registry Standard обновлен с Legacy Components секцией")
            return {
                "status": "success",
                "registry_updated": True,
                "legacy_section_added": True,
            }

        except Exception as e:
            logger.error(f"❌ Ошибка обновления Registry Standard: {e}")
            return {"status": "error", "registry_error": True, "error": str(e)}

    async def _read_registry_standard(self) -> dict[str, Any]:
        """Чтение Registry Standard"""
        try:
            registry_standard_path = (
                self.project_root
                / "[standards .md]"
                / "0. core standards"
                / "0.1 registry standard 15 may 2025 1320 CET by AI Assistant.md"
            )

            if not registry_standard_path.exists():
                logger.error("❌ Registry Standard файл не найден")
                return {
                    "status": "error",
                    "file_not_found": True,
                    "path": str(registry_standard_path),
                }

            with open(registry_standard_path, encoding="utf-8") as f:
                content = f.read()

            logger.info("✅ Registry Standard прочитан")
            return {
                "status": "success",
                "content": content,
                "file_path": str(registry_standard_path),
            }

        except Exception as e:
            logger.error(f"❌ Ошибка чтения Registry Standard: {e}")
            return {"status": "error", "read_error": True, "error": str(e)}

    async def _add_legacy_deprecated_section(self, content: str) -> dict[str, Any]:
        """Добавление Legacy Components секции"""
        try:
            # Создаем Legacy Components секцию
            legacy_section = """

## Legacy Components (Deprecated)

### MCP Cursor Server (Legacy)

**Статус:** Deprecated (заменен на новый MCP сервер)

**Путь:** `advising_platform/src/mcp/mcp_cursor_server.py`

**Причина deprecation:**
- Монолитная архитектура (6000+ строк)
- Нарушение принципа "1 workflow = 1 файл"
- Отсутствие модульности
- Сложность поддержки и тестирования

**Замена:** Новый MCP сервер с модульной архитектурой
- Путь: `heroes-platform/mcp_server/src/mcp_server.py`
- Модульная структура: `workflows/` директория
- Соответствие стандартам: MCP Workflow Standard v2.3

**Migration Guide:**
1. Backup legacy configuration
2. Validate new server
3. Update Cursor configuration
4. Test migration
5. Update Registry Standard

**Дата deprecation:** 27 января 2025

---

"""

            # Добавляем секцию в конец файла
            updated_content = content + legacy_section

            logger.info("✅ Legacy Components секция добавлена")
            return {
                "status": "success",
                "updated_content": updated_content,
                "section_added": True,
            }

        except Exception as e:
            logger.error(f"❌ Ошибка добавления Legacy Components секции: {e}")
            return {"status": "error", "add_section_error": True, "error": str(e)}

    async def _save_registry_standard(self, content: str) -> dict[str, Any]:
        """Сохранение Registry Standard"""
        try:
            registry_standard_path = (
                self.project_root
                / "[standards .md]"
                / "0. core standards"
                / "0.1 registry standard 15 may 2025 1320 CET by AI Assistant.md"
            )

            # Создаем backup перед изменением
            backup_path = registry_standard_path.with_suffix(".backup.md")
            if registry_standard_path.exists():
                with open(registry_standard_path, encoding="utf-8") as f:
                    original_content = f.read()
                with open(backup_path, "w", encoding="utf-8") as f:
                    f.write(original_content)
                logger.info(f"✅ Backup создан: {backup_path}")

            # Сохраняем обновленный контент
            with open(registry_standard_path, "w", encoding="utf-8") as f:
                f.write(content)

            logger.info("✅ Registry Standard сохранен")
            return {
                "status": "success",
                "file_saved": True,
                "file_path": str(registry_standard_path),
                "backup_path": str(backup_path) if backup_path.exists() else None,
            }

        except Exception as e:
            logger.error(f"❌ Ошибка сохранения Registry Standard: {e}")
            return {"status": "error", "save_error": True, "error": str(e)}

    async def remove_legacy_deprecated_section(self) -> dict[str, Any]:
        """Удаление Legacy Components секции"""
        try:
            # Читаем Registry Standard
            read_result = await self._read_registry_standard()
            if read_result.get("status") != "success":
                return read_result

            content = read_result["content"]

            # Проверяем, есть ли Legacy Components секция
            if "Legacy Components (Deprecated)" not in content:
                logger.info("ℹ️ Legacy Components секция не найдена")
                return {
                    "status": "success",
                    "legacy_section_not_found": True,
                    "no_changes_needed": True,
                }

            # Удаляем Legacy Components секцию
            lines = content.split("\n")
            start_index = None
            end_index = None

            for i, line in enumerate(lines):
                if "## Legacy Components (Deprecated)" in line:
                    start_index = i
                elif (
                    start_index is not None
                    and line.startswith("## ")
                    and i > start_index
                ):
                    end_index = i
                    break

            if start_index is not None:
                if end_index is not None:
                    lines = lines[:start_index] + lines[end_index:]
                else:
                    lines = lines[:start_index]

            updated_content = "\n".join(lines)

            # Сохраняем обновленный Registry Standard
            save_result = await self._save_registry_standard(updated_content)
            if save_result.get("status") != "success":
                return save_result

            logger.info("✅ Legacy Components секция удалена")
            return {
                "status": "success",
                "registry_updated": True,
                "legacy_section_removed": True,
            }

        except Exception as e:
            logger.error(f"❌ Ошибка удаления Legacy Components секции: {e}")
            return {"status": "error", "remove_section_error": True, "error": str(e)}
