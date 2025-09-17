"""
Ghost CMS API Client
JTBD: Как API клиент, я хочу взаимодействовать с Ghost CMS API,
чтобы обеспечить публикацию контента в оба блога.

Поддерживает:
- 2025 Blog (API v5.0, Ghost 5.x)
- 2022_RU Blog (API v2, Ghost 3.18)
"""

import os
import sys
import json
from typing import Any
from pathlib import Path

import requests

from .jwt_generator import GhostJWTGenerator

# Import credentials manager
try:
    from heroes_platform.shared.credentials_manager import get_credential
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))
    from heroes_platform.shared.credentials_manager import get_credential


class GhostAPIClient:
    """
    JTBD: Как API клиент, я хочу управлять взаимодействием с Ghost CMS,
    чтобы обеспечить публикацию контента.
    """

    def __init__(self):
        """
        JTBD: Как инициализатор, я хочу настроить API клиент,
        чтобы обеспечить готовность к работе с Ghost CMS.
        """
        self.jwt_generator = GhostJWTGenerator()
        self.session = requests.Session()
        
        # Clear credentials cache to ensure fresh data
        try:
            from heroes_platform.shared.credentials_manager import CredentialsManager
            manager = CredentialsManager()
            manager.clear_cache()
        except Exception:
            pass  # Ignore if credentials manager not available
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Heroes-Ghost-Integration/1.0'
        })

    def _get_ghost_config(self, blog_type: str) -> dict[str, str]:
        """
        JTBD: Как конфигуратор, я хочу получать настройки для блога,
        чтобы обеспечить правильное подключение.

        Args:
            blog_type: Тип блога ("2025" или "2022_RU")

        Returns:
            Конфигурация блога
        """
        if blog_type == "2025":
            return {
                "url": str(get_credential("ghost_url_2025") or os.getenv("GHOST_URL_2025", "http://5.75.239.205/")),
                "admin_key": str(get_credential("ghost_admin_key_2025") or os.getenv("GHOST_ADMIN_KEY_2025") or ""),
                "content_key": str(get_credential("ghost_content_key_2025") or os.getenv("GHOST_CONTENT_KEY_2025") or ""),
                "api_version": "v5.0",
                "admin_endpoint": "/ghost/api/admin",
                "content_endpoint": "/ghost/api/content"
            }
        elif blog_type == "2022_RU":
            return {
                "url": str(get_credential("ghost_url_2022_ru") or os.getenv("GHOST_URL_2022_RU", "https://rick.ai/blog/ru")),
                "admin_key": str(get_credential("ghost_admin_key_2022_ru") or os.getenv("GHOST_ADMIN_KEY_2022_RU") or ""),
                "content_key": str(get_credential("ghost_content_key_2022_ru") or os.getenv("GHOST_CONTENT_KEY_2022_RU") or ""),
                "api_version": "v2",
                "admin_endpoint": "/ghost/api/v2/admin",
                "content_endpoint": "/ghost/api/v2/content"
            }
        else:
            raise ValueError(f"Unknown blog type: {blog_type}")

    def _generate_auth_headers(self, blog_type: str) -> dict[str, str]:
        """
        JTBD: Как генератор заголовков, я хочу создавать заголовки аутентификации,
        чтобы обеспечить доступ к Ghost API.

        Args:
            blog_type: Тип блога ("2025" или "2022_RU")

        Returns:
            Заголовки для аутентификации
        """
        config = self._get_ghost_config(blog_type)

        if not config["admin_key"]:
            raise ValueError(f"Admin key not found for {blog_type} blog")

        jwt_token = self.jwt_generator.generate_jwt(
            config["admin_key"],
            config["api_version"]
        )

        headers = {
            'Authorization': f'Ghost {jwt_token}',
            'Content-Type': 'application/json',
            'Accept-Version': config["api_version"]
        }

        return headers

    def publish_post(self, blog_type: str, post_data: dict[str, Any]) -> dict[str, Any]:
        """
        JTBD: Как публикатор, я хочу публиковать посты в Ghost CMS,
        чтобы обеспечить доступность контента.

        Args:
            blog_type: Тип блога ("2025" или "2022_RU")
            post_data: Данные поста

        Returns:
            Результат публикации
        """
        try:
            config = self._get_ghost_config(blog_type)
            headers = self._generate_auth_headers(blog_type)

            # Use standard URL for Ghost API
            url = f"{config['url'].rstrip('/')}{config['admin_endpoint']}/posts/"

            # Set published_at for published posts
            if post_data.get("status") == "published":
                from datetime import datetime
                post_data["published_at"] = datetime.utcnow().isoformat() + "Z"
            
            # Prepare post data according to API version
            if config["api_version"] == "v2":
                # For Ghost v2, convert HTML to mobiledoc format
                html_content = post_data.get("html", "")
                mobiledoc = {
                    "version": "0.3.1",
                    "markups": [],
                    "atoms": [],
                    "cards": [],
                    "sections": [
                        [1, "p", [[0, [], 0, html_content]]]
                    ]
                }
                post_data["mobiledoc"] = json.dumps(mobiledoc)
                # Remove fields not supported by Ghost v2
                post_data.pop("html", None)
                post_data.pop("lexical", None)  # Ghost v2 doesn't support Lexical
                payload = {"posts": [post_data]}
            else:  # v5.0
                # For Ghost v5.0, use Lexical format (preferred)
                # Ghost v5.0 supports Lexical format natively
                if "lexical" in post_data:
                    # Use Lexical format if available
                    post_data.pop("html", None)  # Remove HTML when using Lexical
                    payload = {"posts": [post_data]}
                else:
                    # Fallback to mobiledoc if no Lexical content
                    html_content = post_data.get("html", "")
                    mobiledoc = {
                        "version": "0.3.1",
                        "markups": [],
                        "atoms": [],
                        "cards": [],
                        "sections": [
                            [1, "p", [[0, [], 0, html_content]]]
                        ]
                    }
                    post_data["mobiledoc"] = json.dumps(mobiledoc)
                    # Remove html field for v5.0
                    post_data.pop("html", None)
                    payload = {"posts": [post_data]}

            response = self.session.post(url, headers=headers, json=payload)
            response.raise_for_status()

            result = response.json()
            # Fix URL by removing port 8080 for public access
            url = result["posts"][0]["url"]
            if ":8080" in url:
                url = url.replace(":8080", "")
            
            return {
                "success": True,
                "blog_type": blog_type,
                "post_id": result["posts"][0]["id"],
                "url": url,
                "status": result["posts"][0]["status"]
            }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "blog_type": blog_type,
                "error": f"Request failed: {str(e)}",
                "status_code": getattr(e.response, 'status_code', None)
            }
        except Exception as e:
            return {
                "success": False,
                "blog_type": blog_type,
                "error": f"Unexpected error: {str(e)}"
            }

    def get_posts(self, blog_type: str, limit: int = 10) -> dict[str, Any]:
        """
        JTBD: Как читатель, я хочу получать список постов,
        чтобы обеспечить мониторинг контента.

        Args:
            blog_type: Тип блога ("2025" или "2022_RU")
            limit: Количество постов

        Returns:
            Список постов
        """
        try:
            config = self._get_ghost_config(blog_type)
            headers = self._generate_auth_headers(blog_type)

            url = f"{config['url'].rstrip('/')}{config['admin_endpoint']}/posts/"
            params = {"limit": limit}

            response = self.session.get(url, headers=headers, params=params)
            response.raise_for_status()

            result = response.json()
            return {
                "success": True,
                "blog_type": blog_type,
                "posts": result["posts"],
                "meta": result.get("meta", {})
            }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "blog_type": blog_type,
                "error": f"Request failed: {str(e)}",
                "status_code": getattr(e.response, 'status_code', None)
            }
        except Exception as e:
            return {
                "success": False,
                "blog_type": blog_type,
                "error": f"Unexpected error: {str(e)}"
            }

    def test_connection(self, blog_type: str) -> dict[str, Any]:
        """
        JTBD: Как тестер, я хочу проверять подключение к блогу,
        чтобы обеспечить диагностику проблем.

        Args:
            blog_type: Тип блога ("2025" или "2022_RU")

        Returns:
            Результат тестирования
        """
        try:
            config = self._get_ghost_config(blog_type)
            headers = self._generate_auth_headers(blog_type)

            # Test basic connectivity
            test_url = f"{config['url'].rstrip('/')}{config['admin_endpoint']}/posts/"
            response = self.session.get(test_url, headers=headers)

            return {
                "success": True,
                "blog_type": blog_type,
                "url": test_url,
                "status_code": response.status_code,
                "api_version": config["api_version"],
                "message": "Connection test completed"
            }

        except Exception as e:
            return {
                "success": False,
                "blog_type": blog_type,
                "error": f"Connection test failed: {str(e)}"
            }

    def dual_publish(self, post_data: dict[str, Any]) -> dict[str, Any]:
        """
        JTBD: Как dual publisher, я хочу публиковать в оба блога,
        чтобы обеспечить максимальный охват.

        Args:
            post_data: Данные поста

        Returns:
            Результаты публикации в оба блога
        """
        results = {}

        # Both blogs now use mobiledoc format
        # 2025 blog: Mobiledoc format (same as v2)
        post_data_2025 = post_data.copy()
        
        # 2022_RU blog: Mobiledoc format (same as v2)
        post_data_2022_ru = post_data.copy()

        # Publish to 2025 blog
        results["2025"] = self.publish_post("2025", post_data_2025)

        # Publish to 2022_RU blog
        results["2022_RU"] = self.publish_post("2022_RU", post_data_2022_ru)

        # Determine overall success
        success_count = sum(1 for r in results.values() if r["success"])
        overall_success = success_count > 0

        return {
            "success": overall_success,
            "results": results,
            "success_count": success_count,
            "total_blogs": len(results)
        }

    def _html_to_lexical(self, html_content: str) -> str:
        """
        Конвертирует простой HTML в Lexical JSON формат
        
        Args:
            html_content: HTML контент
            
        Returns:
            Lexical JSON строка
        """
        # Простая конвертация HTML в Lexical
        # Разбиваем на строки и создаем параграфы
        lines = html_content.split('<br>')
        children = []
        
        for line in lines:
            if line.strip():
                # Создаем параграф для каждой непустой строки
                paragraph_node = {
                    "children": [
                        {
                            "detail": 0,
                            "format": 0,
                            "mode": "normal",
                            "style": "",
                            "text": line.strip(),
                            "type": "text",
                            "version": 1
                        }
                    ],
                    "direction": "ltr",
                    "format": "",
                    "indent": 0,
                    "type": "paragraph",
                    "version": 1
                }
                children.append(paragraph_node)
        
        # Если нет контента, создаем пустой параграф
        if not children:
            children.append({
                "children": [
                    {
                        "detail": 0,
                        "format": 0,
                        "mode": "normal",
                        "style": "",
                        "text": "",
                        "type": "text",
                        "version": 1
                    }
                ],
                "direction": "ltr",
                "format": "",
                "indent": 0,
                "type": "paragraph",
                "version": 1
            })
        
        lexical_structure = {
            "root": {
                "children": children,
                "direction": "ltr",
                "format": "",
                "indent": 0,
                "type": "root",
                "version": 1
            }
        }
        
        return json.dumps(lexical_structure, ensure_ascii=False)

    def _markdown_to_lexical(self, markdown_content: str) -> str:
        """
        Конвертирует Markdown в Lexical JSON формат используя unified + remark-parse
        
        Args:
            markdown_content: Markdown контент
            
        Returns:
            Lexical JSON строка
        """
        try:
            # Используем улучшенный конвертер с unified + remark-parse
            from .lexical_converter_advanced import AdvancedLexicalConverter
            converter = AdvancedLexicalConverter()
            return converter.markdown_to_lexical(markdown_content)
        except Exception as e:
            print(f"Ошибка в улучшенном конвертере: {e}")
            # Fallback к простому конвертеру
            from .lexical_converter import LexicalConverter
            fallback_converter = LexicalConverter()
            return fallback_converter.markdown_to_lexical(markdown_content)

    def delete_post(self, blog_name: str, post_id: str) -> bool:
        """
        Удаляет пост из Ghost блога
        
        Args:
            blog_name: Название блога ('2025' или '2022_RU')
            post_id: ID поста для удаления
            
        Returns:
            bool: True если удаление успешно, False в противном случае
        """
        try:
            # Получаем конфигурацию блога
            blog_config = self._get_ghost_config(blog_name)
            if not blog_config:
                print(f"❌ Не удалось получить конфигурацию для блога {blog_name}")
                return False
            
            # Формируем URL для удаления
            if blog_config['api_version'] == 'v5.0':
                delete_url = f"{blog_config['url']}/ghost/api/admin/posts/{post_id}/"
            else:
                delete_url = f"{blog_config['url']}/ghost/api/v2/admin/posts/{post_id}/"
            
            # Получаем JWT токен
            jwt_token = self.jwt_generator.generate_jwt(
                blog_config["admin_key"],
                blog_config["api_version"]
            )
            if not jwt_token:
                print(f"❌ Не удалось сгенерировать JWT токен для блога {blog_name}")
                return False
            
            # Выполняем DELETE запрос
            headers = {
                'Authorization': f'Ghost {jwt_token}',
                'Content-Type': 'application/json'
            }
            
            response = self.session.delete(delete_url, headers=headers)
            
            if response.status_code == 204:  # Ghost возвращает 204 при успешном удалении
                print(f"✅ Пост {post_id} успешно удален из блога {blog_name}")
                return True
            else:
                print(f"❌ Ошибка удаления поста {post_id}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при удалении поста {post_id}: {e}")
            return False
