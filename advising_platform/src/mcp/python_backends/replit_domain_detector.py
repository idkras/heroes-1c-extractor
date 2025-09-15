#!/usr/bin/env python3
"""
Replit Domain Auto-Detection для корректных ссылок

JTBD: Я (детектор) хочу автоматически определить правильный Replit domain,
чтобы предоставлять рабочие ссылки пользователю.

Автор: AI Assistant
Дата: 26 May 2025
"""

import sys
import json
import os
import subprocess
from pathlib import Path

def detect_replit_domain() -> str:
    """
    JTBD: Я (функция) хочу определить текущий Replit domain,
    чтобы создать правильные URLs для сервисов.
    """
    # Проверяем environment variables Replit
    repl_id = os.environ.get('REPL_ID')
    repl_slug = os.environ.get('REPL_SLUG') 
    replit_domains = os.environ.get('REPLIT_DOMAINS')
    
    if replit_domains:
        # Извлекаем первый домен из списка
        domains = replit_domains.split(',')
        if domains:
            return f"https://{domains[0].strip()}"
    
    # Fallback: пробуем через repl_id
    if repl_id and repl_slug:
        return f"https://{repl_slug}-{repl_id}.replit.app"
    
    # Последний fallback для тестирования
    return "https://workspace.replit.app"

def generate_service_links(base_domain: str) -> dict:
    """
    JTBD: Я (генератор) хочу создать правильные ссылки на все сервисы,
    чтобы пользователь мог получить доступ к результатам.
    """
    return {
        "web_interface": f"{base_domain}:5000",
        "mcp_dashboard": f"{base_domain}:5000/mcp-dashboard",
        "api_server": f"{base_domain}:8000",
        "standards_browser": f"{base_domain}:5000/standards",
        "testing_reports": f"{base_domain}:5000/tests",
        "cache_status": f"{base_domain}:5000/cache-status",
        "project_docs": f"{base_domain}/docs"
    }

def main():
    """Основная функция domain detection."""
    try:
        if len(sys.argv) != 2:
            raise ValueError("Usage: python replit_domain_detector.py <json_args>")
        
        # Определяем домен
        detected_domain = detect_replit_domain()
        
        # Генерируем ссылки
        service_links = generate_service_links(detected_domain)
        
        # Формируем результат
        result = {
            "success": True,
            "detected_domain": detected_domain,
            "service_links": service_links,
            "environment_info": {
                "repl_id": os.environ.get('REPL_ID', 'not_found'),
                "repl_slug": os.environ.get('REPL_SLUG', 'not_found'),
                "replit_domains": os.environ.get('REPLIT_DOMAINS', 'not_found')
            }
        }
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": f"Domain detection failed: {str(e)}"
        }
        print(json.dumps(error_result, ensure_ascii=False))
        sys.exit(1)

if __name__ == "__main__":
    main()