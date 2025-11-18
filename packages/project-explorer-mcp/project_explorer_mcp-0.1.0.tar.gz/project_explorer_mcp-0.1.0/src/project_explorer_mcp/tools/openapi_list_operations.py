"""OpenAPI list operations tool for the MCP server."""

from pathlib import Path

from fastmcp import FastMCP
from loguru import logger

from ..config.settings import get_settings
from ..utils import is_valid_path, iter_openapi_operations, load_openapi_spec
from ..utils.openapi import format_openapi_markdown


def register_openapi_list_operations(mcp: FastMCP):
    """Registers the openapi_list_operations tool with the MCP server.

    Args:
        mcp: FastMCP server instance.
    """

    @mcp.tool()
    def openapi_list_operations(
        spec_path: str,
        output_format: str | None = None,
        filter_by_tag: str | None = None,
        filter_by_method: str | None = None,
        filter_by_path: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict | str:
        """List operations from an OpenAPI specification file.

        Agent usage guidelines:
            - Use this tool when you need to explore the available API operations in an OpenAPI spec.
            - Use when you want to see endpoints, methods, and summaries without detailed schemas.
            - Do not use for getting detailed parameter or response information.

        Path requirements:
            - The path must not contain URL-encoding (e.g., '%').
            - The path must be absolute.
            - The path must exist on disk and be a valid OpenAPI JSON or YAML file.

        Args:
            spec_path (str): Absolute path to the OpenAPI JSON or YAML file.
            output_format (str | None): Output format ('json' or 'markdown').
                Defaults to server setting.
            filter_by_tag (str | None): Filter operations by tag. Only operations with this tag will be included.
            filter_by_method (str | None): Filter operations by HTTP method (e.g., 'GET', 'POST').
            filter_by_path (str | None): Filter operations by path containing this substring (case-insensitive).
            limit (int): Maximum number of operations to return. Defaults to 50.
            offset (int): Number of operations to skip from the start. Defaults to 0.

        Examples:
            - To get operations related to users: {"spec_path": "/path/to/spec.json", "filter_by_path": "user"}
            - To get all GET operations: {"spec_path": "/path/to/spec.json", "filter_by_method": "GET"}
            - To get operations with a specific tag: {"spec_path": "/path/to/spec.json", "filter_by_tag": "users"}
            - To paginate through results: {"spec_path": "/path/to/spec.json", "limit": 20, "offset": 40}

        Returns:
            dict | str: For format_output="json": Dictionary containing operations list and metadata.
                - operations: list of operation dicts with method, path, operation_id, summary, tags
                - count: number of operations returned (after filtering and pagination)
                - total_count: total number of operations matching filters (before pagination)
                - error: error message if any, None otherwise
                For format_output="markdown": formatted markdown string
        """
        logger.info(
            "openapi_list_operations tool called",
            spec_path=spec_path,
            output_format=output_format,
            filter_by_tag=filter_by_tag,
            filter_by_method=filter_by_method,
            filter_by_path=filter_by_path,
            limit=limit,
            offset=offset,
        )
        # Get default output format from settings if not provided
        if output_format is None:
            settings = get_settings()
            output_format = settings.default_output_format.value

        try:
            # Validate path
            valid, msg = is_valid_path(spec_path)
            if not valid:
                logger.error(
                    "Invalid path for openapi_list_operations",
                    spec_path=spec_path,
                    error=msg,
                )
                if output_format == "markdown":
                    return f"**Error:** {msg}"
                else:
                    return {
                        "operations": [],
                        "count": 0,
                        "total_count": 0,
                        "error": msg,
                    }

            path = Path(spec_path)
            spec = load_openapi_spec(path)
            all_operations = list(iter_openapi_operations(spec))

            # Apply filters
            filtered_operations = []
            for op in all_operations:
                tags = op.get("tags", [])
                if (
                    isinstance(tags, list)
                    and filter_by_tag
                    and filter_by_tag not in tags
                ):
                    continue
                if filter_by_method and op.get("method") != filter_by_method.upper():
                    continue
                path_str = op.get("path", "")
                if (
                    filter_by_path
                    and isinstance(path_str, str)
                    and filter_by_path.lower() not in path_str.lower()
                ):
                    continue
                filtered_operations.append(op)

            total_count = len(filtered_operations)

            # Apply pagination
            if offset:
                filtered_operations = filtered_operations[offset:]
            if limit:
                filtered_operations = filtered_operations[:limit]

            count = len(filtered_operations)

            logger.info(
                "Successfully listed OpenAPI operations",
                spec_path=spec_path,
                total_count=total_count,
                returned_count=count,
            )
            if output_format == "markdown":
                return format_openapi_markdown(filtered_operations)
            else:
                return {
                    "operations": filtered_operations,
                    "count": count,
                    "total_count": total_count,
                    "error": None,
                }
        except Exception as e:
            logger.error(
                "Failed to list operations",
                spec_path=spec_path,
                error=str(e),
                tool="openapi_list_operations",
            )
            if output_format == "markdown":
                return f"**Error:** {str(e)}"
            else:
                return {"operations": [], "count": 0, "total_count": 0, "error": str(e)}
