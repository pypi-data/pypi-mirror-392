"""Project Explorer MCP configuration package."""

from .logging import setup_logging
from .settings import get_settings

__all__ = [
    "setup_logging",
    "get_settings",
]
