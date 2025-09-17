"""
MCP Server Configuration
Handles environment variables and paths configuration.
"""

import os
from pathlib import Path
from typing import Optional


class Settings:
    """Configuration settings for MCP Server"""

    def __init__(self):
        self.workspace_root = self._get_workspace_root()

    def _get_workspace_root(self) -> Path:
        """Find workspace root by looking for common indicators"""
        current = Path(__file__).parent
        while current.parent != current:
            if (current / ".git").exists() or (current / "package.json").exists():
                return current
            current = current.parent
        # Fallback to hardcoded path if not found
        return Path("/Users/ilyakrasinsky/workspace/vscode.projects/heroes-template")

    @property
    def standards_dir(self) -> Path:
        """Get standards directory path"""
        custom_path = os.getenv("STANDARDS_DIR")
        if custom_path:
            return Path(custom_path)
        # Try common locations relative to detected workspace_root
        candidates = [
            self.workspace_root / "[standards .md]",
            self.workspace_root.parent / "[standards .md]",
            self.workspace_root.parent.parent / "[standards .md]",
            Path(
                "/Users/ilyakrasinsky/workspace/vscode.projects/heroes-template/[standards .md]"
            ),
        ]
        for p in candidates:
            if p.exists():
                return p
        # Fallback
        return candidates[0]

    @property
    def cursor_rules_dir(self) -> Path:
        """Get cursor rules directory path"""
        custom_path = os.getenv("CURSOR_RULES_DIR")
        if custom_path:
            return Path(custom_path)
        return self.workspace_root / ".cursor" / "rules"

    @property
    def ghost_cms_url(self) -> Optional[str]:
        """Get Ghost CMS URL from environment"""
        return os.getenv("GHOST_CMS_URL")

    @property
    def ghost_admin_key(self) -> Optional[str]:
        """Get Ghost Admin API key from environment"""
        return os.getenv("GHOST_ADMIN_KEY")

    @property
    def telegram_api_id(self) -> Optional[str]:
        """Get Telegram API ID from environment"""
        return os.getenv("TELEGRAM_API_ID")

    @property
    def telegram_api_hash(self) -> Optional[str]:
        """Get Telegram API hash from environment"""
        return os.getenv("TELEGRAM_API_HASH")

    @property
    def telegram_session(self) -> Optional[str]:
        """Get Telegram session string from environment"""
        return os.getenv("TELEGRAM_SESSION")

    @property
    def log_level(self) -> str:
        """Get log level from environment"""
        return os.getenv("LOG_LEVEL", "INFO")


# Global settings instance
settings = Settings()
