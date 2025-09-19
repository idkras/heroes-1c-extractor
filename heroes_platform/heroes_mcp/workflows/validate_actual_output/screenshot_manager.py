#!/usr/bin/env python3
"""
Screenshot Manager Module
MCP Workflow Standard v2.3 Compliance

JTBD: Когда мне нужно создать скриншот страницы для валидации,
я хочу использовать ScreenshotManager,
чтобы автоматически создавать качественные скриншоты с метаданными.

COMPLIANCE: MCP Workflow Standard v2.3, TDD Documentation Standard v2.5
"""

import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ScreenshotManager:
    """Screenshot Manager - MCP Workflow Standard v2.3"""

    def __init__(self):
        # Создаем папку в корне проекта
        project_root = Path(__file__).parent.parent.parent.parent.parent
        self.output_dir = project_root / "output_screenshot"
        self.output_dir.mkdir(exist_ok=True)

    async def create_screenshot(
        self,
        url: str,
        output_type: str = "validation",
        outcome: str = "success",
        description: str = "screenshot",
    ) -> Optional[dict[str, Any]]:
        """Создание скриншота с правильным именованием (≤20 строк)"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Новый формат: {дата}_{время}_{output}_{outcome}_{описание}.png
            filename = f"{timestamp}_{output_type}_{outcome}_{description}.png"
            filepath = self.output_dir / filename

            # Пытаемся создать реальный скриншот через Playwright
            playwright_result = await self._call_playwright_mcp(url, str(filepath))

            if playwright_result.get("success"):
                logger.info(f"Real screenshot created: {filepath}")
                return {
                    "filepath": str(filepath),
                    "filename": filename,
                    "url": url,
                    "timestamp": timestamp,
                    "size": filepath.stat().st_size if filepath.exists() else 0,
                    "status": "real_screenshot",
                    "playwright_result": playwright_result,
                }
            else:
                # Fallback: создаем placeholder файл
                logger.warning(
                    f"Playwright failed, creating placeholder: {playwright_result.get('error')}"
                )
                return await self._create_placeholder_screenshot(
                    url, filepath, timestamp
                )

        except Exception as e:
            logger.error(f"Screenshot creation failed: {e}")
            return await self._create_placeholder_screenshot(url, filepath, timestamp)

    async def _create_placeholder_screenshot(
        self, url: str, filepath: Path, timestamp: str
    ) -> dict[str, Any]:
        """Создание placeholder скриншота как fallback"""
        try:
            # Создаем простой PNG файл через PIL или fallback
            try:
                from PIL import Image, ImageDraw, ImageFont

                # Создаем изображение 800x600
                img = Image.new("RGB", (800, 600), color="white")
                draw = ImageDraw.Draw(img)

                # Добавляем текст
                text = f"Screenshot placeholder for {url}\nCreated: {datetime.now().isoformat()}\nStatus: Fallback mode (Playwright not available)"
                draw.text((10, 10), text, fill="black")

                # Сохраняем как PNG
                img.save(filepath, "PNG")

            except ImportError:
                # Fallback: создаем простой PNG файл
                with open(filepath, "wb") as f:
                    # Простой PNG заголовок
                    f.write(b"\x89PNG\r\n\x1a\n")
                    # Минимальный PNG файл
                    f.write(
                        b"\x00\x00\x00\rIHDR\x00\x00\x03\x20\x00\x00\x02X\x08\x02\x00\x00\x00"
                    )
                    f.write(b"\x00\x00\x00\x00IEND\xaeB`\x82")

            return {
                "filepath": str(filepath),
                "filename": filepath.name,
                "url": url,
                "timestamp": timestamp,
                "size": filepath.stat().st_size if filepath.exists() else 0,
                "status": "fallback_placeholder",
                "error": "Playwright not available",
            }
        except Exception as e:
            logger.error(f"Placeholder creation failed: {e}")
            return {"success": False, "error": str(e), "status": "failed"}

    async def _call_playwright_mcp(self, url: str, filepath: str) -> dict[str, Any]:
        """Вызов Playwright MCP сервера (≤20 строк)"""
        try:
            # Сначала пытаемся использовать Playwright напрямую
            playwright_result = await self._use_playwright_directly(url, filepath)

            if playwright_result.get("success"):
                return playwright_result

            # Fallback: пытаемся через subprocess
            subprocess_result = await self._use_playwright_subprocess(url, filepath)

            if subprocess_result.get("success"):
                return subprocess_result

            return {"success": False, "error": "All Playwright methods failed"}

        except Exception as e:
            logger.error(f"Playwright call failed: {e}")
            return {"success": False, "error": str(e)}

    async def _use_playwright_directly(self, url: str, filepath: str) -> dict[str, Any]:
        """Использование Playwright напрямую"""
        try:
            # Пытаемся импортировать и использовать Playwright
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                # Настраиваем viewport для полноэкранного скриншота
                await page.set_viewport_size({"width": 1920, "height": 1080})

                # Переходим на страницу
                await page.goto(url, wait_until="networkidle", timeout=30000)

                # Делаем полноэкранный скриншот
                await page.screenshot(path=filepath, full_page=True)

                await browser.close()

                return {
                    "success": True,
                    "filepath": filepath,
                    "method": "direct_playwright",
                }

        except ImportError:
            return {"success": False, "error": "Playwright not installed"}
        except Exception as e:
            return {"success": False, "error": f"Direct Playwright failed: {str(e)}"}

    async def _use_playwright_subprocess(
        self, url: str, filepath: str
    ) -> dict[str, Any]:
        """Использование Playwright через subprocess"""
        try:
            # Создаем Python скрипт для создания скриншота
            script_content = f"""
import asyncio
from playwright.async_api import async_playwright

async def take_screenshot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.set_viewport_size({{"width": 1920, "height": 1080}})
        await page.goto("{url}", wait_until='networkidle', timeout=30000)
        await page.screenshot(path="{filepath}", full_page=True)
        await browser.close()

asyncio.run(take_screenshot())
"""

            # Сохраняем временный скрипт
            temp_script = Path("temp_screenshot.py")
            temp_script.write_text(script_content)

            # Запускаем скрипт
            result = subprocess.run(
                ["python", str(temp_script)], capture_output=True, text=True, timeout=60
            )

            # Удаляем временный скрипт
            temp_script.unlink(missing_ok=True)

            if result.returncode == 0 and Path(filepath).exists():
                return {
                    "success": True,
                    "filepath": filepath,
                    "method": "subprocess_playwright",
                }
            else:
                return {"success": False, "error": result.stderr}

        except Exception as e:
            return {
                "success": False,
                "error": f"Subprocess Playwright failed: {str(e)}",
            }

    def get_screenshot_info(self, filepath: str) -> dict[str, Any]:
        """Получение информации о скриншоте (≤20 строк)"""
        try:
            path = Path(filepath)
            if path.exists():
                return {
                    "exists": True,
                    "size": path.stat().st_size,
                    "created": datetime.fromtimestamp(path.stat().st_ctime).isoformat(),
                    "path": str(path.absolute()),
                    "is_real_image": self._is_real_image(path),
                }
            else:
                return {"exists": False, "error": "File not found"}

        except Exception as e:
            return {"exists": False, "error": str(e)}

    def _is_real_image(self, filepath: Path) -> bool:
        """Проверка, является ли файл реальным изображением"""
        try:
            # Проверяем размер файла (должен быть больше 1KB для изображения)
            if filepath.stat().st_size < 1024:
                return False

            # Проверяем первые байты файла (PNG signature)
            with open(filepath, "rb") as f:
                header = f.read(8)
                return header.startswith(b"\x89PNG\r\n\x1a\n")

        except Exception:
            return False
