"""OpenAPI get operation details tool for the MCP server."""

from pathlib import Path

from fastmcp import FastMCP
from loguru import logger

from ..config.settings import get_settings
from ..utils import (
    get_openapi_operation_details as get_operation_details_util,
)
from ..utils import (
    is_valid_path,
    load_openapi_spec,
)
from ..utils.openapi import format_openapi_details_markdown


def register_openapi_get_operation_details(mcp: FastMCP):
    """Registers the openapi_get_operation_details tool with the MCP server.

    Args:
        mcp: FastMCP server instance.
    """

    @mcp.tool()
    def openapi_get_operation_details(
        spec_path: str,
        selectors: list[str],
        expand_refs: bool = False,
        format_output: str | None = None,
    ) -> dict | str:
        """Get detailed information for specific OpenAPI operations.

        Agent usage guidelines:
            - Use this tool when you need detailed information about specific API operations.
            - Use selectors to target specific operations by operationId, method+path, or path.
            - Set expand_refs=True to resolve schema references for full schema details.
            - Choose format_output="json" for structured data, "markdown" for formatted output.

        Path requirements:
            - The path must not contain URL-encoding (e.g., '%').
            - The path must be absolute.
            - The path must exist on disk and be a valid OpenAPI JSON or YAML file.

        Args:
            spec_path (str): Absolute path to the OpenAPI JSON or YAML file.
            selectors (list[str]): List of selectors. Each selector can be:
                - operationId (exact match)
                - "METHOD /path" (e.g. "GET /users/{id}")
                - just a path (e.g. "/users/{id}") to match all methods on that path
            expand_refs (bool): Whether to resolve local $ref references in schemas. Defaults to False.
            format_output (str | None): Output format ('json' or 'markdown').
                Defaults to server setting.

        Returns:
            dict | str: For format_output="json": Dictionary containing operation details and metadata.
                - details: list of detailed operation records
                - count: number of matching operations
                - error: error message if any, None otherwise
                For format_output="markdown": formatted markdown string
        """
        logger.info(
            "openapi_get_operation_details tool called",
            spec_path=spec_path,
            selectors=selectors,
            expand_refs=expand_refs,
            format_output=format_output,
        )
        # Get default output format from settings if not provided
        if format_output is None:
            settings = get_settings()
            format_output = settings.default_output_format.value

        try:
            # Validate path
            valid, msg = is_valid_path(spec_path)
            if not valid:
                logger.error(
                    "Invalid path for openapi_get_operation_details",
                    spec_path=spec_path,
                    error=msg,
                )
                if format_output == "markdown":
                    return f"**Error:** {msg}"
                else:
                    return {
                        "details": [],
                        "count": 0,
                        "error": msg,
                    }

            path = Path(spec_path)
            spec = load_openapi_spec(path)
            records = get_operation_details_util(spec, selectors, expand_refs)
            logger.info(
                "Successfully retrieved OpenAPI operation details",
                spec_path=spec_path,
                selectors=selectors,
                count=len(records),
            )
            if format_output == "markdown":
                return format_openapi_details_markdown(records)
            else:
                return {"details": records, "count": len(records), "error": None}
        except Exception as e:
            logger.error(
                "Failed to get operation details",
                spec_path=spec_path,
                error=str(e),
                tool="openapi_get_operation_details",
            )
            if format_output == "markdown":
                return f"**Error:** {str(e)}"
            else:
                return {
                    "details": [],
                    "count": 0,
                    "error": str(e),
                }
