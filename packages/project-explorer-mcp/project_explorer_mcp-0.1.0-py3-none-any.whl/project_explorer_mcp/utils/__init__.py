"""Utility functions for the project explorer MCP server."""

from .formatters import (
    format_markdown_outline_as_markdown,
    format_python_outline_as_markdown,
)
from .general import format_output, is_valid_path, strip_empty
from .openapi import (
    format_openapi_details,
    format_openapi_text,
    get_openapi_operation_details,
    iter_openapi_operations,
    load_openapi_spec,
)

__all__ = [
    # General utilities
    "strip_empty",
    "is_valid_path",
    "format_output",
    # Formatters
    "format_python_outline_as_markdown",
    "format_markdown_outline_as_markdown",
    # OpenAPI utilities
    "load_openapi_spec",
    "iter_openapi_operations",
    "get_openapi_operation_details",
    "format_openapi_details",
    "format_openapi_text",
]
