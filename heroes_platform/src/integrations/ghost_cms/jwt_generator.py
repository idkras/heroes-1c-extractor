"""
Ghost CMS JWT Generator
JTBD: Как JWT генератор, я хочу создавать валидные токены для Ghost API,
чтобы обеспечить аутентификацию для публикации контента.

КРИТИЧЕСКИЕ ИСПРАВЛЕНИЯ:
- Convert secret to hex bytes: bytes.fromhex(secret)
- Different audience for different API versions: /v2/admin/ vs /admin/
"""

import re
import time
from typing import Optional


class GhostJWTGenerator:
    """
    JTBD: Как генератор JWT токенов, я хочу создавать валидные токены,
    чтобы обеспечить аутентификацию для Ghost CMS API.
    """

    def __init__(self):
        """
        JTBD: Как инициализатор, я хочу настроить генератор,
        чтобы обеспечить готовность к созданию токенов.
        """
        self.default_expiry = 300  # 5 minutes
        self.default_iat_offset = 60  # 1 minute

    def generate_jwt(self, api_key: str, api_version: str = "v5.0") -> str:
        """
        JTBD: Как генератор токенов, я хочу создавать JWT для Ghost API,
        чтобы обеспечить аутентификацию.

        Args:
            api_key: Admin key в формате "id:secret"
            api_version: Версия API ("v2" или "v5.0")

        Returns:
            JWT токен для аутентификации
        """
        try:
            import jwt
        except ImportError as e:
            raise ImportError(
                "PyJWT library is required. Install with: pip install PyJWT"
            ) from e

        try:
            # Clean and split API key
            api_key = re.sub(r"\s+", "", api_key)
            if ":" not in api_key:
                raise ValueError("Admin key must be in 'id:secret' format")

            key_id, secret = api_key.split(":", 1)

            # ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Convert secret to hex bytes
            secret_bytes = None
            try:
                secret_bytes = bytes.fromhex(secret)  # Convert hex string to bytes
            except ValueError:
                # Fallback to string encoding if not hex
                secret_bytes = secret.encode()

            # ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Different audience for different API versions
            current_time = int(time.time())
            if api_version == "v2":
                payload = {
                    "iat": current_time - self.default_iat_offset,
                    "exp": current_time + self.default_expiry,
                    "aud": "/v2/admin/",  # Correct audience for v2
                }
            else:  # v5.0
                payload = {
                    "iat": current_time - self.default_iat_offset,
                    "exp": current_time + self.default_expiry,
                    "aud": "/admin/",  # Correct audience for v5.0
                }

            # Generate JWT token with kid in header (correct format)
            headers = {"kid": key_id, "alg": "HS256", "typ": "JWT"}
            token = jwt.encode(
                payload, secret_bytes, algorithm="HS256", headers=headers
            )
            return str(token)

        except Exception as e:
            # Re-raise the original exception instead of fallback
            raise e

    def validate_jwt(self, token: str) -> bool:
        """
        JTBD: Как валидатор, я хочу проверять JWT токены,
        чтобы обеспечить их корректность.

        Args:
            token: JWT токен для проверки

        Returns:
            True если токен валиден, False иначе
        """
        try:
            import jwt

            # Decode without verification to check structure
            decoded = jwt.decode(token, options={"verify_signature": False})
            required_fields = ["iat", "exp", "aud"]
            return all(field in decoded for field in required_fields)
        except Exception:
            return False

    def get_token_info(self, token: str) -> Optional[dict]:
        """
        JTBD: Как анализатор, я хочу извлекать информацию из JWT токена,
        чтобы обеспечить диагностику.

        Args:
            token: JWT токен для анализа

        Returns:
            Информация о токене или None
        """
        try:
            import jwt

            decoded = jwt.decode(token, options={"verify_signature": False})
            return {
                "audience": decoded.get("aud"),
                "issued_at": decoded.get("iat"),
                "expires_at": decoded.get("exp"),
                "key_id": decoded.get("kid"),
            }
        except Exception:
            return None
