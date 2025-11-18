"""Python outline tool for the MCP server."""

import ast

from fastmcp import FastMCP
from loguru import logger

from ..config.settings import get_settings
from ..utils import format_python_outline_as_markdown, is_valid_path, strip_empty


def register_python_outline(mcp: FastMCP):
    """Registers the python_outline tool with the MCP server.

    Args:
        mcp: FastMCP server instance.
    """

    @mcp.tool()
    def python_outline(
        paths: list[str], output_format: str | None = None
    ) -> dict | str:
        """
        Returns an outline for each Python file: imports, classes, functions, docstrings.

        Agent usage guidelines:
            - Use this tool when you need to understand the structure of Python code files, such as for code review, navigation, or documentation generation.
            - Use when you need to extract or display the list of imports, classes, functions, and their docstrings from Python files.
            - Do not use for non-Python files or for reading file contents in detail.

        Path requirements:
            - Paths must not contain URL-encoding (e.g., '%').
            - Paths must be absolute.
            - Paths must exist on disk.
        Example paths:
            - Windows: "C:\\Users\\User\\project\\main.py"
            - Linux: "/home/user/project/main.py"

        Args:
            paths (list[str]): List of absolute paths to Python files.
            output_format (str | None): Output format ('json' or 'markdown').
                Defaults to server setting (markdown by default).
        Returns:
            dict | str: Outline for each file in the requested format.
        """
        logger.info(
            "python_outline tool called", paths=paths, output_format=output_format
        )
        # Get default output format from settings if not provided
        if output_format is None:
            settings = get_settings()
            output_format = settings.default_output_format.value

        # Path check
        for path in paths:
            valid, msg = is_valid_path(path)
            if not valid:
                logger.error("Invalid path for python_outline", path=path, error=msg)
                error_result = {path: {"error": msg}}
                if output_format == "markdown":
                    return format_python_outline_as_markdown(error_result)
                return error_result
        try:
            result = {}
            for path in paths:
                outline: dict[str, object] = {}
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        source = f.read()
                    tree = ast.parse(source)
                    docstring = ast.get_docstring(tree)
                    if docstring:
                        outline["docstring"] = docstring
                    imports: list[dict[str, object]] = []
                    classes: list[dict[str, object]] = []
                    functions: list[dict[str, object]] = []
                    for node in tree.body:
                        if isinstance(node, ast.Import):
                            for n in node.names:
                                imports.append({"name": n.name, "line": node.lineno})
                        elif isinstance(node, ast.ImportFrom):
                            mod = node.module or ""
                            for n in node.names:
                                import_name = f"{mod}.{n.name}" if mod else n.name
                                imports.append(
                                    {"name": import_name, "line": node.lineno}
                                )
                        elif isinstance(node, ast.ClassDef):
                            cls = {"name": node.name, "line": node.lineno}
                            cdoc = ast.get_docstring(node)
                            if cdoc:
                                cls["docstring"] = cdoc
                            methods = []
                            for item in node.body:
                                if isinstance(item, ast.FunctionDef):
                                    mdoc = ast.get_docstring(item)
                                    method = {"name": item.name, "line": item.lineno}
                                    if mdoc:
                                        method["docstring"] = mdoc
                                    methods.append(method)
                            if methods:
                                cls["methods"] = methods
                            classes.append(cls)
                        elif isinstance(node, ast.FunctionDef):
                            fdoc = ast.get_docstring(node)
                            func = {"name": node.name, "line": node.lineno}
                            if fdoc:
                                func["docstring"] = fdoc
                            functions.append(func)
                    if imports:
                        outline["imports"] = imports
                    if classes:
                        outline["classes"] = classes
                    if functions:
                        outline["functions"] = functions
                    logger.debug(
                        "Parsed Python file outline",
                        path=path,
                        imports=len(imports),
                        classes=len(classes),
                        functions=len(functions),
                    )
                except Exception as e:
                    logger.error("Error parsing Python file", path=path, error=str(e))
                    outline = {"error": str(e)}
                result[path] = strip_empty(outline)

            # Format output based on requested format
            if output_format == "markdown":
                return format_python_outline_as_markdown(result)
            return result
        except Exception as e:
            logger.error("Error in python_outline tool", error=str(e))
            if output_format == "markdown":
                error_dict: dict[str, dict[str, str]] = {"error": {"error": str(e)}}
                return format_python_outline_as_markdown(error_dict)
            return {"error": str(e)}
