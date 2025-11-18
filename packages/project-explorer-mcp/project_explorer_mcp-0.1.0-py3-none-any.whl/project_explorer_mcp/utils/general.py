"""General utility functions for the project explorer MCP server."""

import json
import os
import urllib.parse

from loguru import logger


def strip_empty(d):
    """Recursively removes empty fields and lists from a dictionary/list."""
    if isinstance(d, dict):
        return {
            k: strip_empty(v)
            for k, v in d.items()
            if v not in (None, "", [], {}, False)
        }
    if isinstance(d, list):
        return [strip_empty(x) for x in d if x not in (None, "", [], {}, False)]
    return d


def is_valid_path(path: str) -> tuple[bool, str]:
    """Checks the path for validity: no URL-encoding, absolute, exists.

    Args:
        path: Path to validate.

    Returns:
        Tuple of (is_valid, error_message).
    """
    # URL-encoding check
    if "%" in path or urllib.parse.unquote(path) != path:
        logger.warning("Path contains URL-encoding", path=path)
        return False, "The path contains URL-encoding or invalid characters."
    # Absolute path check
    if not os.path.isabs(path):
        logger.warning("Path is not absolute", path=path)
        return False, "The path is not absolute."
    # Existence check
    if not os.path.exists(path):
        logger.warning("Path does not exist", path=path)
        return False, "The path does not exist on disk."
    logger.debug("Path validation passed", path=path)
    return True, ""


def format_output(data: dict | str, output_format: str) -> dict | str:
    """Formats output based on the specified format.

    Args:
        data: The data to format (dict or str).
        output_format: Output format ('json' or 'markdown').

    Returns:
        Formatted output as dict (for JSON) or str (for markdown).
    """
    if output_format == "json":
        return data

    # For markdown format, return string representation
    if isinstance(data, str):
        return data

    if isinstance(data, dict):
        # If it's an error dict, return JSON representation
        if "error" in data and len(data) == 1:
            return json.dumps(data, indent=2)

        return json.dumps(data, indent=2)

    return str(data)
