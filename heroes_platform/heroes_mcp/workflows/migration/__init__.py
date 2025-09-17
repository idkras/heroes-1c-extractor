"""
Migration Workflow Module

Атомарная миграция с legacy на новый MCP сервер
Registry Standard v5.8 Compliance

JTBD: Когда нужно безопасно мигрировать с legacy MCP сервера на новый,
я хочу использовать атомарные команды миграции,
чтобы обеспечить безопасный переход без потери функциональности.
"""

from .core import MigrationWorkflow

__all__ = ["MigrationWorkflow"]
