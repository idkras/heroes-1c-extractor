#!/usr/bin/env python3
"""
URL Analyzer Module
MCP Workflow Standard v2.3 Compliance

JTBD: Когда мне нужно проанализировать URL и извлечь информацию о странице,
я хочу использовать URLAnalyzer,
чтобы получить структурированную информацию о контенте, CSS, JS и метаданных.

COMPLIANCE: MCP Workflow Standard v2.3, TDD Documentation Standard v2.5
"""

import logging
from typing import Any

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class URLAnalyzer:
    """URL Analyzer - MCP Workflow Standard v2.3"""

    def __init__(self):
        self.timeout = 30
        self.user_agent = "Mozilla/5.0 (compatible; Heroes-MCP/1.0)"

    async def analyze_url(self, url: str) -> dict[str, Any]:
        """Анализ URL (≤20 строк)"""
        try:
            response = requests.get(
                url, timeout=self.timeout, headers={"User-Agent": self.user_agent}
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            analysis = {
                "page_title": self._extract_title(soup),
                "content_length": len(response.text),
                "status_code": response.status_code,
                "css_files": self._extract_css_files(soup),
                "js_files": self._extract_js_files(soup),
                "content_checks": self._analyze_content(soup),
                "meta_tags": self._extract_meta_tags(soup),
            }

            return analysis

        except Exception as e:
            logger.error(f"URL analysis failed: {e}")
            return {"error": str(e)}

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Извлечение заголовка (≤20 строк)"""
        title = soup.title
        if title and title.string:
            return title.string.strip()
        return "No title"

    def _extract_css_files(self, soup: BeautifulSoup) -> list:
        """Извлечение CSS файлов (≤20 строк)"""
        css_links = soup.find_all("link", rel="stylesheet")
        return [link.get("href") for link in css_links if hasattr(link, 'get') and link.get("href")]

    def _extract_js_files(self, soup: BeautifulSoup) -> list:
        """Извлечение JS файлов (≤20 строк)"""
        js_scripts = soup.find_all("script", src=True)
        return [script.get("src") for script in js_scripts if hasattr(script, 'get') and script.get("src")]

    def _analyze_content(self, soup: BeautifulSoup) -> dict[str, bool]:
        """Анализ контента (≤20 строк)"""
        return {
            "has_main_content": bool(soup.find("main") or soup.find(".md-content")),
            "has_navigation": bool(soup.find("nav") or soup.find(".md-nav")),
            "has_code_blocks": bool(soup.find("pre") or soup.find("code")),
            "has_tables": bool(soup.find("table")),
            "has_images": bool(soup.find("img")),
            "has_links": bool(soup.find("a")),
        }

    def _extract_meta_tags(self, soup: BeautifulSoup) -> dict[str, str]:
        """Извлечение мета-тегов (≤20 строк)"""
        meta_tags = {}
        for meta in soup.find_all("meta"):
            if hasattr(meta, 'get'):
                name = meta.get("name") or meta.get("property")
                content = meta.get("content")
                if name and content:
                    meta_tags[str(name)] = str(content)
        return meta_tags
