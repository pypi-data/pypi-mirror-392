"""Markdown outline tool for the MCP server."""

import re

from fastmcp import FastMCP
from loguru import logger

from ..config.settings import get_settings
from ..utils import format_markdown_outline_as_markdown, is_valid_path


def register_markdown_outline(mcp: FastMCP):
    """Registers the markdown_outline tool with the MCP server.

    Args:
        mcp: FastMCP server instance.
    """

    @mcp.tool()
    def markdown_outline(
        paths: list[str], output_format: str | None = None
    ) -> dict | str:
        """Returns an outline for each Markdown file: headings, levels, line.

        Agent usage guidelines:
            - Use this tool when you need to extract or display the structure of Markdown documents, such as for navigation, summary, or documentation analysis.
            - Use when you need to list headings, their levels, and line numbers in Markdown files.
            - Do not use for non-Markdown files or for reading the full content of the file.

        Path requirements:
            - Paths must not contain URL-encoding (e.g., '%').
            - Paths must be absolute.
            - Paths must exist on disk.
        Example paths:
            - Windows: "C:\\Users\\User\\project\\README.md"
            - Linux: "/home/user/project/README.md"

        Args:
            paths (list[str]): List of absolute paths to Markdown files.
            output_format (str | None): Output format ('json' or 'markdown').
                Defaults to server setting (markdown by default).

        Returns:
            dict | str: Outline for each file in the requested format.
        """
        logger.info(
            "markdown_outline tool called", paths=paths, output_format=output_format
        )
        # Get default output format from settings if not provided
        if output_format is None:
            settings = get_settings()
            output_format = settings.default_output_format.value

        # Path check
        for path in paths:
            valid, msg = is_valid_path(path)
            if not valid:
                logger.error("Invalid path for markdown_outline", path=path, error=msg)
                error_result = {path: [{"error": msg}]}
                if output_format == "markdown":
                    return format_markdown_outline_as_markdown(error_result)
                return error_result
        try:
            result = {}
            header_re = re.compile(r"^(#+)\s+(.*)")
            for path in paths:
                outline = []
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        for i, line in enumerate(f, 1):
                            m = header_re.match(line)
                            if m:
                                level = len(m.group(1))
                                text = m.group(2).strip()
                                if text:
                                    outline.append(
                                        {"level": level, "text": text, "line": i}
                                    )
                    logger.debug(
                        "Parsed Markdown file outline", path=path, headings=len(outline)
                    )
                except Exception as e:
                    logger.error("Error parsing Markdown file", path=path, error=str(e))
                    outline = [{"error": str(e)}]
                result[path] = outline

            # Format output based on requested format
            if output_format == "markdown":
                return format_markdown_outline_as_markdown(result)
            return result
        except Exception as e:
            logger.error("Error in markdown_outline tool", error=str(e))
            if output_format == "markdown":
                return f"**Error:** {str(e)}"
            return {"error": str(e)}
