#!/usr/bin/env python3
"""
Credentials Manager for MCP Server
Unified credentials management with support for Mac Keychain, GitHub Secrets, and Environment Variables

JTBD: Как MCP сервер, я хочу централизованно управлять всеми секретами и ключами,
чтобы обеспечить безопасность и упростить интеграцию с различными сервисами.

TDD Documentation Standard v2.5 Compliance:
- Atomic Functions Architecture (≤20 строк на функцию)
- Security First (валидация всех входных данных)
- Modern Python Development (type hints, dataclasses)
- Testing Pyramid Compliance (unit, integration, e2e)
"""

import os
import subprocess
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import json

logger = logging.getLogger(__name__)

@dataclass
class CredentialConfig:
    """Configuration for credential source"""
    name: str
    source: str  # 'keychain', 'github_secrets', 'env', 'file'
    key: str
    fallback_sources: Optional[list[str]] = None
    validation_rules: Optional[Dict[str, Any]] = None

@dataclass
class CredentialResult:
    """Result of credential retrieval"""
    success: bool
    value: Optional[str] = None
    source: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class CredentialsManager:
    """
    Unified credentials manager for MCP server

    JTBD: Как менеджер секретов, я хочу предоставлять безопасный доступ к credentials,
    чтобы MCP команды могли работать с различными API и сервисами.
    """

    def __init__(self) -> None:
        self._cache: Dict[str, CredentialResult] = {}
        self._configs: Dict[str, CredentialConfig] = {}
        self._setup_default_configs()

    def _setup_default_configs(self) -> None:
        """Setup default credential configurations"""
        self._configs = {
            # Telegram credentials
            "telegram_api_id": CredentialConfig(
                name="Telegram API ID",
                source="keychain",
                key="telegram_api_id",
                fallback_sources=["env", "github_secrets"],
                validation_rules={"type": "int", "min_length": 1}
            ),
            "telegram_api_hash": CredentialConfig(
                name="Telegram API Hash",
                source="keychain",
                key="telegram_api_hash",
                fallback_sources=["env", "github_secrets"],
                validation_rules={"type": "str", "min_length": 32}
            ),
            "telegram_session": CredentialConfig(
                name="Telegram Session String",
                source="keychain",
                key="telegram_session",
                fallback_sources=["env", "github_secrets"],
                validation_rules={"type": "str", "min_length": 10}
            ),

            # OpenAI/GPT credentials
            "openai_api_key": CredentialConfig(
                name="OpenAI API Key",
                source="keychain",
                key="openai_api_key",
                fallback_sources=["env", "github_secrets"],
                validation_rules={"type": "str", "min_length": 20, "prefix": "sk-"}
            ),

            # GitHub credentials
            "github_token": CredentialConfig(
                name="GitHub Token",
                source="keychain",
                key="github_token",
                fallback_sources=["env", "github_secrets"],
                validation_rules={"type": "str", "min_length": 40}
            ),

            # Other API keys
            "linear_api_key": CredentialConfig(
                name="Linear API Key",
                source="keychain",
                key="linear_mcp",
                fallback_sources=["env", "github_secrets"],
                validation_rules={"type": "str", "min_length": 20, "prefix": "lin_api_"}
            ),

            # Rick.ai credentials
            "rick_session_cookie": CredentialConfig(
                name="Rick.ai Session Cookie",
                source="keychain",
                key="rick_session_cookie",
                fallback_sources=["env", "github_secrets"],
                validation_rules={"type": "str", "min_length": 50}
            ),

            # Ghost CMS credentials
            "ghost_admin_key_2025": CredentialConfig(
                name="Ghost Admin Key 2025",
                source="keychain",
                key="GHOST_ADMIN_KEY_2025",
                fallback_sources=["env", "github_secrets"],
                validation_rules={"type": "str", "min_length": 20}
            ),
            "ghost_content_key_2025": CredentialConfig(
                name="Ghost Content Key 2025",
                source="keychain",
                key="GHOST_CONTENT_KEY_2025",
                fallback_sources=["env", "github_secrets"],
                validation_rules={"type": "str", "min_length": 20}
            ),
            "ghost_admin_key_2022_ru": CredentialConfig(
                name="Ghost Admin Key 2022 RU",
                source="keychain",
                key="GHOST_ADMIN_KEY_2022_RU",
                fallback_sources=["env", "github_secrets"],
                validation_rules={"type": "str", "min_length": 20}
            ),
            "ghost_content_key_2022_ru": CredentialConfig(
                name="Ghost Content Key 2022 RU",
                source="keychain",
                key="GHOST_CONTENT_KEY_2022_RU",
                fallback_sources=["env", "github_secrets"],
                validation_rules={"type": "str", "min_length": 20}
            ),
            "ghost_url_2025": CredentialConfig(
                name="Ghost URL 2025",
                source="keychain",
                key="GHOST_API_URL_2025",
                fallback_sources=["env", "github_secrets"],
                validation_rules={"type": "str", "min_length": 10}
            ),
            "ghost_url_2022_ru": CredentialConfig(
                name="Ghost URL 2022 RU",
                source="keychain",
                key="GHOST_API_URL_2022_RU",
                fallback_sources=["env", "github_secrets"],
                validation_rules={"type": "str", "min_length": 10}
            ),

            # Yandex Direct OAuth 2.0 credentials
            "yandex_direct_access_token": CredentialConfig(
                name="Yandex Direct Access Token",
                source="keychain",
                key="yandex_direct_access_token",
                fallback_sources=["env", "github_secrets"],
                validation_rules={"type": "str", "min_length": 50}
            ),
            "yandex_direct_client_id": CredentialConfig(
                name="Yandex Direct Client ID",
                source="keychain",
                key="yandex_direct_client_id",
                fallback_sources=["env", "github_secrets"],
                validation_rules={"type": "str", "min_length": 20}
            ),
            "yandex_direct_client_secret": CredentialConfig(
                name="Yandex Direct Client Secret",
                source="keychain",
                key="yandex_direct_client_secret",
                fallback_sources=["env", "github_secrets"],
                validation_rules={"type": "str", "min_length": 20}
            ),
            "yandex_direct_refresh_token": CredentialConfig(
                name="Yandex Direct Refresh Token",
                source="keychain",
                key="yandex_direct_refresh_token",
                fallback_sources=["env", "github_secrets"],
                validation_rules={"type": "str", "min_length": 50}
            ),

            # Ghost CMS credentials

            # Google OAuth 2.0 credentials
            "google_oauth_client_id": CredentialConfig(
                name="Google OAuth Client ID",
                source="keychain",
                key="google-bigquery",
                fallback_sources=["env", "github_secrets"],
                validation_rules={"type": "str", "min_length": 50, "pattern": r".*\.apps\.googleusercontent\.com$"}
            ),
            "google_oauth_client_secret": CredentialConfig(
                name="Google OAuth Client Secret",
                source="keychain",
                key="google_oauth_client_secret",
                fallback_sources=["env", "github_secrets"],
                validation_rules={"type": "str", "min_length": 20}
            ),
            "google_refresh_token": CredentialConfig(
                name="Google Refresh Token",
                source="keychain",
                key="google_refresh_token",
                fallback_sources=["env", "github_secrets"],
                validation_rules={"type": "str", "min_length": 50}
            ),

            # Google Service Account JSON
            "google_service_account_json": CredentialConfig(
                name="Google Service Account JSON",
                source="keychain",
                key="google-service-account-json",
                fallback_sources=["env", "file"],
                validation_rules={"type": "json", "required_fields": ["type", "project_id", "private_key_id", "private_key", "client_email"]}
            ),

            # N8N credentials
            "N8N_API_KEY": CredentialConfig(
                name="N8N API Key",
                source="keychain",
                key="N8N_API_KEY",
                fallback_sources=["env", "github_secrets"],
                validation_rules={"type": "str", "min_length": 20}
            ),
            "N8N_API_URL": CredentialConfig(
                name="N8N API URL",
                source="keychain",
                key="N8N_API_URL",
                fallback_sources=["env", "github_secrets"],
                validation_rules={"type": "str", "min_length": 10}
            ),

            # HH.ru credentials
            "hh_oauth_client_id": CredentialConfig(
                name="HH.ru OAuth Client ID",
                source="keychain",
                key="hh_oauth_client_id",
                fallback_sources=["env", "github_secrets"],
                validation_rules={"type": "str", "min_length": 20}
            ),
            "hh_oauth_client_secret": CredentialConfig(
                name="HH.ru OAuth Client Secret",
                source="keychain",
                key="hh_oauth_client_secret",
                fallback_sources=["env", "github_secrets"],
                validation_rules={"type": "str", "min_length": 20}
            ),

            # Playwright credentials
            "PLAYWRIGHT_BROWSER_TOKEN": CredentialConfig(
                name="Playwright Browser Token",
                source="keychain",
                key="PLAYWRIGHT_BROWSER_TOKEN",
                fallback_sources=["env", "github_secrets"],
                validation_rules={"type": "str", "min_length": 20}
            ),

            # Figma API credentials
            "figma_api_key": CredentialConfig(
                name="Figma API Key",
                source="keychain",
                key="figma_api_key",
                fallback_sources=["env", "github_secrets"],
                validation_rules={"type": "str", "min_length": 20}
            ),

            # BookStack API credentials
            "bookstack_token_id": CredentialConfig(
                name="BookStack Token ID",
                source="keychain",
                key="bookstack_token_id",
                fallback_sources=["env", "github_secrets"],
                validation_rules={"type": "str", "min_length": 20}
            ),
            "bookstack_token_secret": CredentialConfig(
                name="BookStack Token Secret",
                source="keychain",
                key="bookstack_token_secret",
                fallback_sources=["env", "github_secrets"],
                validation_rules={"type": "str", "min_length": 20}
            ),
            "bookstack_url": CredentialConfig(
                name="BookStack URL",
                source="keychain",
                key="bookstack_url",
                fallback_sources=["env", "github_secrets"],
                validation_rules={"type": "str", "min_length": 10}
            )
        }

    def get_credential(self, credential_name: str) -> CredentialResult:
        """
        Get credential with fallback chain

        JTBD: Как система безопасности, я хочу получать credentials с fallback цепочкой,
        чтобы обеспечить надежность доступа к секретам.
        """
        # Check cache first
        if credential_name in self._cache:
            return self._cache[credential_name]

        config = self._configs.get(credential_name)
        if not config:
            return CredentialResult(
                success=False,
                error=f"Unknown credential: {credential_name}"
            )

        # Try primary source
        result = self._get_from_source(config, config.source)
        if result.success:
            self._cache[credential_name] = result
            return result

        # Try fallback sources
        for fallback_source in config.fallback_sources or []:
            result = self._get_from_source(config, fallback_source)
            if result.success:
                self._cache[credential_name] = result
                return result

        # All sources failed
        error_result = CredentialResult(
            success=False,
            error=f"Failed to get {credential_name} from all sources"
        )
        self._cache[credential_name] = error_result
        return error_result

    def clear_credentials_cache(self) -> None:
        """Clear credentials cache"""
        self._cache.clear()

    def _get_from_source(self, config: CredentialConfig, source: str) -> CredentialResult:
        """Get credential from specific source"""
        try:
            if source == "keychain":
                return self._get_from_keychain(config)
            elif source == "env":
                return self._get_from_env(config)
            elif source == "github_secrets":
                return self._get_from_github_secrets(config)
            elif source == "file":
                return self._get_from_file(config)
            else:
                return CredentialResult(
                    success=False,
                    error=f"Unknown source: {source}"
                )
        except Exception as e:
            return CredentialResult(
                success=False,
                error=f"Error getting from {source}: {str(e)}"
            )

    def _get_from_keychain(self, config: CredentialConfig) -> CredentialResult:
        """Get credential from Mac Keychain"""
        try:
            # Use different account for Google Service Account JSON
            if config.key == "google-service-account-json":
                command = f'security find-generic-password -s "{config.key}" -a "rick@service" -w'
            else:
                command = f'security find-generic-password -s "{config.key}" -a "ilyakrasinsky" -w'

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            value = result.stdout.strip()

            # Decode hex-encoded data from Keychain
            if value:
                try:
                    # Try to decode as hex first (for binary data like JSON)
                    import subprocess as sp
                    decode_result = sp.run(
                        f'echo "{value}" | xxd -r -p',
                        shell=True,
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    decoded_value = decode_result.stdout.strip()

                    # If decoded value is valid JSON, use it
                    try:
                        json.loads(decoded_value)
                        value = decoded_value
                    except json.JSONDecodeError:
                        # If not JSON, use original value (for plain text credentials)
                        pass
                except Exception:
                    # If hex decode fails, use original value
                    pass

            if value and self._validate_credential(config, value):
                return CredentialResult(
                    success=True,
                    value=value,
                    source="keychain",
                    metadata={"method": "mac_keychain"}
                )
            else:
                return CredentialResult(
                    success=False,
                    error="Invalid credential from keychain"
                )
        except subprocess.CalledProcessError:
            return CredentialResult(
                success=False,
                error="Credential not found in keychain"
            )

    def _get_from_env(self, config: CredentialConfig) -> CredentialResult:
        """Get credential from environment variables"""
        env_key = config.key.upper()
        value = os.getenv(env_key)

        if value and self._validate_credential(config, value):
            return CredentialResult(
                success=True,
                value=value,
                source="env",
                metadata={"env_key": env_key}
            )
        else:
            return CredentialResult(
                success=False,
                error=f"Environment variable {env_key} not found or invalid"
            )

    def _get_from_github_secrets(self, config: CredentialConfig) -> CredentialResult:
        """Get credential from GitHub Secrets (when running in GitHub Actions)"""
        if not os.getenv("GITHUB_ACTIONS"):
            return CredentialResult(
                success=False,
                error="Not running in GitHub Actions"
            )

        env_key = config.key.upper()
        value = os.getenv(env_key)

        if value and self._validate_credential(config, value):
            return CredentialResult(
                success=True,
                value=value,
                source="github_secrets",
                metadata={"github_secret": env_key}
            )
        else:
            return CredentialResult(
                success=False,
                error=f"GitHub secret {env_key} not found or invalid"
            )

    def _get_from_file(self, config: CredentialConfig) -> CredentialResult:
        """Get credential from file (for development/testing)"""
        file_path = Path.home() / ".heroes" / f"{config.key}.txt"

        if file_path.exists():
            try:
                value = file_path.read_text().strip()
                if value and self._validate_credential(config, value):
                    return CredentialResult(
                        success=True,
                        value=value,
                        source="file",
                        metadata={"file_path": str(file_path)}
                    )
            except Exception as e:
                return CredentialResult(
                    success=False,
                    error=f"Error reading file: {str(e)}"
                )

        return CredentialResult(
            success=False,
            error=f"File not found: {file_path}"
        )

    def _validate_credential(self, config: CredentialConfig, value: str) -> bool:
        """Validate credential according to rules"""
        if not config.validation_rules:
            return True

        rules = config.validation_rules

        # JSON validation
        if rules.get("type") == "json":
            try:
                json_data = json.loads(value)
                required_fields = rules.get("required_fields", [])
                for field in required_fields:
                    if field not in json_data:
                        return False
                return True
            except json.JSONDecodeError:
                return False

        # Type validation
        if rules.get("type") == "int":
            try:
                int(value)
            except ValueError:
                return False

        # Length validation
        if "min_length" in rules and len(value) < rules["min_length"]:
            return False

        if "max_length" in rules and len(value) > rules["max_length"]:
            return False

        # Prefix validation
        if "prefix" in rules and not value.startswith(rules["prefix"]):
            return False

        # Pattern validation
        if "pattern" in rules:
            import re
            if not re.match(rules["pattern"], value):
                return False

        return True

    def store_credential(self, credential_name: str, value: str, source: str = "keychain") -> bool:
        """
        Store credential in specified source

        JTBD: Как администратор безопасности, я хочу сохранять credentials в безопасном месте,
        чтобы обеспечить их доступность для MCP команд.
        """
        config = self._configs.get(credential_name)
        if not config:
            logger.error(f"Unknown credential: {credential_name}")
            return False

        if not self._validate_credential(config, value):
            logger.error(f"Invalid credential value for {credential_name}")
            return False

        try:
            if source == "keychain":
                return self._store_in_keychain(config, value)
            elif source == "env":
                return self._store_in_env(config, value)
            elif source == "file":
                return self._store_in_file(config, value)
            else:
                logger.error(f"Unsupported storage source: {source}")
                return False
        except Exception as e:
            logger.error(f"Error storing credential: {e}")
            return False

    def _store_in_keychain(self, config: CredentialConfig, value: str) -> bool:
        """Store credential in Mac Keychain"""
        try:
            # Delete existing entry first
            delete_cmd = f'security delete-generic-password -s "{config.key}" -a "ilyakrasinsky" 2>/dev/null || true'
            subprocess.run(delete_cmd, shell=True)

            # Store new entry
            store_cmd = f'security add-generic-password -s "{config.key}" -a "ilyakrasinsky" -w "{value}"'
            subprocess.run(store_cmd, shell=True, check=True)

            logger.info(f"✅ Stored {config.name} in Mac Keychain")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to store in keychain: {e}")
            return False

    def _store_in_env(self, config: CredentialConfig, value: str) -> bool:
        """Store credential in environment variable (for current session)"""
        env_key = config.key.upper()
        os.environ[env_key] = value
        logger.info(f"✅ Stored {config.name} in environment variable {env_key}")
        return True

    def _store_in_file(self, config: CredentialConfig, value: str) -> bool:
        """Store credential in file (for development/testing)"""
        try:
            file_path = Path.home() / ".heroes"
            file_path.mkdir(exist_ok=True)

            credential_file = file_path / f"{config.key}.txt"
            credential_file.write_text(value)

            logger.info(f"✅ Stored {config.name} in file {credential_file}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to store in file: {e}")
            return False

    def get_all_credentials(self) -> Dict[str, CredentialResult]:
        """Get all configured credentials"""
        results = {}
        for credential_name in self._configs.keys():
            results[credential_name] = self.get_credential(credential_name)
        return results

    def test_credentials(self) -> Dict[str, bool]:
        """Test all credentials for validity"""
        results = {}
        for credential_name in self._configs.keys():
            result = self.get_credential(credential_name)
            results[credential_name] = result.success
        return results

# Global instance
credentials_manager = CredentialsManager()

def get_credential(credential_name: str) -> Optional[str]:
    """
    Convenience function to get credential value

    JTBD: Как разработчик MCP команд, я хочу легко получать credentials,
    чтобы интегрировать их в свои команды.
    """
    result = credentials_manager.get_credential(credential_name)
    return result.value if result.success else None

def store_credential(credential_name: str, value: str, source: str = "keychain") -> bool:
    """
    Convenience function to store credential

    JTBD: Как администратор, я хочу легко сохранять credentials,
    чтобы настроить MCP сервер для работы с различными API.
    """
    return credentials_manager.store_credential(credential_name, value, source)

def create_google_oauth_config() -> Optional[Dict[str, str]]:
    """
    Create Google OAuth 2.0 configuration from credentials

    JTBD: Как интегратор Google API, я хочу создавать OAuth конфигурацию из credentials,
    чтобы MCP команды могли работать с Google Sheets и Drive API.
    """
    client_id = get_credential("google_oauth_client_id")
    client_secret = get_credential("google_oauth_client_secret")
    refresh_token = get_credential("google_refresh_token")

    if not client_id:
        logger.error("❌ Google OAuth Client ID not found")
        return None

    if not client_secret:
        logger.error("❌ Google OAuth Client Secret not found")
        return None

    if not refresh_token:
        logger.error("❌ Google Refresh Token not found")
        return None

    config = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth"
    }

    logger.info("✅ Google OAuth 2.0 configuration created")
    return config

def get_google_credentials() -> Optional[Dict[str, str]]:
    """
    Get Google credentials (OAuth 2.0 or Service Account)

    JTBD: Как универсальный менеджер Google API, я хочу получать credentials
    в любом формате, чтобы обеспечить гибкость интеграции.
    """
    # Try Service Account JSON first (from Keychain)
    service_account_result = credentials_manager.get_credential("google_service_account_json")
    if service_account_result.success:
        try:
            if service_account_result.value is None:
                logger.error("❌ Service Account JSON value is None")
                return None
            service_account_data = json.loads(service_account_result.value)
            logger.info("✅ Google Service Account JSON loaded from Keychain")
            return service_account_data
        except json.JSONDecodeError as e:
            logger.error(f"❌ Error parsing Service Account JSON: {e}")

    # Try OAuth 2.0 as fallback
    oauth_config = create_google_oauth_config()
    if oauth_config:
        logger.info("✅ Google OAuth 2.0 configuration loaded")
        return oauth_config

    # Fallback to service account file
    service_account_path = Path("heroes-platform/config/rick-google-service-account.json")
    if service_account_path.exists():
        try:
            with open(service_account_path, 'r') as f:
                service_account_data = json.load(f)
                logger.info("✅ Google Service Account loaded from file")
                return service_account_data
        except Exception as e:
            logger.error(f"❌ Error reading service account file: {e}")

    logger.error("❌ No Google credentials found")
    return None

def get_google_service_account_private_key() -> Optional[str]:
    """
    Extract private_key from Google Service Account JSON in Keychain

    JTBD: Как MCP команда, я хочу получать private_key из Service Account JSON,
    чтобы использовать его для аутентификации в Google API.
    """
    service_account_result = credentials_manager.get_credential("google_service_account_json")
    if not service_account_result.success:
        logger.error("❌ Google Service Account JSON not found in Keychain")
        return None

    try:
        if service_account_result.value is None:
            logger.error("❌ Service Account JSON value is None")
            return None
        service_account_data = json.loads(service_account_result.value)
        private_key = service_account_data.get("private_key")

        if not private_key:
            logger.error("❌ private_key not found in Service Account JSON")
            return None

        if "YOUR_PRIVATE_KEY_HERE" in private_key:
            logger.error("❌ private_key contains placeholder - need real private_key from Google Cloud Console")
            return None

        logger.info("✅ Google Service Account private_key extracted from Keychain")
        return private_key

    except json.JSONDecodeError as e:
        logger.error(f"❌ Error parsing Service Account JSON: {e}")
        return None

def get_google_service_account_info() -> Optional[Dict[str, str]]:
    """
    Get Google Service Account info (without private_key) for debugging

    JTBD: Как отладчик, я хочу получать информацию о Service Account без private_key,
    чтобы проверить конфигурацию без раскрытия секретов.
    """
    service_account_result = credentials_manager.get_credential("google_service_account_json")
    if not service_account_result.success:
        logger.error("❌ Google Service Account JSON not found in Keychain")
        return None

    try:
        if service_account_result.value is None:
            logger.error("❌ Service Account JSON value is None")
            return None
        service_account_data = json.loads(service_account_result.value)

        # Return info without private_key
        info = {
            "type": service_account_data.get("type"),
            "project_id": service_account_data.get("project_id"),
            "private_key_id": service_account_data.get("private_key_id"),
            "client_email": service_account_data.get("client_email"),
            "client_id": service_account_data.get("client_id"),
            "auth_uri": service_account_data.get("auth_uri"),
            "token_uri": service_account_data.get("token_uri"),
            "auth_provider_x509_cert_url": service_account_data.get("auth_provider_x509_cert_url"),
            "client_x509_cert_url": service_account_data.get("client_x509_cert_url"),
            "universe_domain": service_account_data.get("universe_domain")
        }

        # Check if private_key is placeholder
        private_key = service_account_data.get("private_key", "")
        if "YOUR_PRIVATE_KEY_HERE" in private_key:
            info["private_key_status"] = "placeholder"
        else:
            info["private_key_status"] = "real"

        logger.info("✅ Google Service Account info extracted from Keychain")
        return info

    except json.JSONDecodeError as e:
        logger.error(f"❌ Error parsing Service Account JSON: {e}")
        return None

def get_bookstack_config() -> Optional[Dict[str, str]]:
    """
    Create BookStack API configuration from credentials

    JTBD: Как интегратор BookStack API, я хочу создавать конфигурацию из credentials,
    чтобы MCP команды могли работать с BookStack API.
    """
    token_id = get_credential("bookstack_token_id")
    token_secret = get_credential("bookstack_token_secret")
    url = get_credential("bookstack_url")

    if not token_id:
        logger.error("❌ BookStack Token ID not found")
        return None

    if not token_secret:
        logger.error("❌ BookStack Token Secret not found")
        return None

    if not url:
        logger.error("❌ BookStack URL not found")
        return None

    config = {
        "token_id": token_id,
        "token_secret": token_secret,
        "url": url,
        "api_url": f"{url}/api"
    }

    logger.info("✅ BookStack API configuration created")
    return config
