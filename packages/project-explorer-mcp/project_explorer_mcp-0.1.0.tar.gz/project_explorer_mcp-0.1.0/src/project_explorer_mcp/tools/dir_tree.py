"""Directory tree tool for the MCP server."""

import os

from fastmcp import FastMCP
from loguru import logger

from ..config.settings import get_settings
from ..utils import is_valid_path


def register_dir_tree(mcp: FastMCP):
    """Registers the dir_tree tool with the MCP server.

    Args:
        mcp: FastMCP server instance.
    """

    @mcp.tool()
    def dir_tree(
        root_path: str, max_depth: int = 1, output_format: str | None = None
    ) -> str | dict:
        """Returns a compact file and folder tree with depth limitation.

        Agent usage guidelines:
            - Use this tool when you need to get a quick overview of the file and folder structure of a project or directory.
            - Use when you need to display or analyze the hierarchy of files and folders up to a certain depth.
            - Do not use for reading file contents or for non-existent/relative paths.

        Path requirements:
            - The path must not contain URL-encoding (e.g., '%').
            - The path must be absolute.
            - The path must exist on disk.
        Example paths:
            - Windows: "C:\\Users\\User\\project"
            - Linux: "/home/user/project"

        Args:
            root_path (str): Absolute path to the root directory.
            max_depth (int): Maximum nesting depth. Default is 1.
            output_format (str | None): Output format ('json' or 'markdown').
                Defaults to server setting (markdown by default).

        Returns:
            str | dict: File and folder tree in the requested format or error dict.
        """
        logger.info(
            "dir_tree tool called",
            root_path=root_path,
            max_depth=max_depth,
            output_format=output_format,
        )
        # Get default output format from settings if not provided
        if output_format is None:
            settings = get_settings()
            output_format = settings.default_output_format.value

        # Path check
        valid, msg = is_valid_path(root_path)
        if not valid:
            logger.error("Invalid path for dir_tree", root_path=root_path, error=msg)
            return {"error": msg}
        try:

            def walk_text(path, depth, prefix=""):
                """Walk directory tree and return text representation."""
                if depth < 0:
                    return ""
                try:
                    entries = sorted(os.listdir(path))
                except Exception:
                    return ""
                lines = []
                for entry in entries:
                    full_path = os.path.join(path, entry)
                    lines.append(
                        f"{prefix}{entry}/"
                        if os.path.isdir(full_path)
                        else f"{prefix}{entry}"
                    )
                    if os.path.isdir(full_path) and depth > 0:
                        sub = walk_text(full_path, depth - 1, prefix + "  ")
                        if sub:
                            lines.append(sub)
                return "\n".join(lines)

            def walk_json(path, depth):
                """Walk directory tree and return JSON representation."""
                if depth < 0:
                    return []
                try:
                    entries = sorted(os.listdir(path))
                except Exception:
                    return []

                result = []
                for entry in entries:
                    full_path = os.path.join(path, entry)
                    is_dir = os.path.isdir(full_path)
                    item = {"name": entry, "type": "directory" if is_dir else "file"}

                    if is_dir and depth > 0:
                        children = walk_json(full_path, depth - 1)
                        if children:
                            item["children"] = children

                    result.append(item)
                return result

            if output_format == "json":
                tree_data = walk_json(root_path, max_depth)
                return {"root": root_path, "tree": tree_data}

            # Markdown format
            tree = walk_text(root_path, max_depth)
            result = tree.strip()
            return f"## Directory Tree: {root_path}\n\n```\n{result}\n```"
        except Exception as e:
            logger.error(
                "Error generating directory tree", root_path=root_path, error=str(e)
            )
            return {"error": str(e)}
