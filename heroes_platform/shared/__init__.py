"""
Shared utilities and common functionality for Heroes Platform.
"""

from .credentials_manager import (
    CredentialsManager,
    get_credential,
    store_credential,
    credentials_manager
)

__all__ = [
    "CredentialsManager",
    "get_credential", 
    "store_credential",
    "credentials_manager"
]