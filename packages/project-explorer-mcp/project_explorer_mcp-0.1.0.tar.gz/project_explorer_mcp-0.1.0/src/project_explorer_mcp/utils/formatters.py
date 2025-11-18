"""Formatting utility functions for the project explorer MCP server."""


def format_python_outline_as_markdown(data: dict) -> str:
    """Converts python_outline JSON data to markdown format.

    Args:
        data: Dictionary with file paths as keys and outline data as values.

    Returns:
        Markdown formatted string.
    """
    lines = []

    for path, outline in data.items():
        lines.append(f"## {path}\n")

        # Handle error case
        if isinstance(outline, dict) and "error" in outline:
            lines.append(f"**Error:** {outline['error']}\n")
            continue

        # Module docstring
        if isinstance(outline, dict) and "docstring" in outline:
            lines.append(f"**Module docstring:**\n{outline['docstring']}\n")

        # Imports
        if isinstance(outline, dict) and "imports" in outline:
            lines.append("### Imports\n")
            for imp in outline["imports"]:
                line_num = imp.get("line", "")
                lines.append(f"- `{imp['name']}` (line {line_num})")
            lines.append("")

        # Classes
        if isinstance(outline, dict) and "classes" in outline:
            lines.append("### Classes\n")
            for cls in outline["classes"]:
                line_num = cls.get("line", "")
                lines.append(f"#### `{cls['name']}` (line {line_num})\n")
                if "docstring" in cls:
                    lines.append(f"{cls['docstring']}\n")
                if "methods" in cls:
                    lines.append("**Methods:**")
                    for method in cls["methods"]:
                        method_line = method.get("line", "")
                        lines.append(f"- `{method['name']}` (line {method_line})")
                        if "docstring" in method:
                            lines.append(f"  - {method['docstring']}")
                    lines.append("")

        # Functions
        if isinstance(outline, dict) and "functions" in outline:
            lines.append("### Functions\n")
            for func in outline["functions"]:
                line_num = func.get("line", "")
                lines.append(f"#### `{func['name']}` (line {line_num})\n")
                if "docstring" in func:
                    lines.append(f"{func['docstring']}\n")

        lines.append("---\n")

    return "\n".join(lines).strip()


def format_markdown_outline_as_markdown(data: dict) -> str:
    """Converts markdown_outline JSON data to markdown format.

    Args:
        data: Dictionary with file paths as keys and heading lists as values.

    Returns:
        Markdown formatted string.
    """
    lines = []

    for path, headings in data.items():
        lines.append(f"## {path}\n")

        # Handle error case
        if headings and isinstance(headings[0], dict) and "error" in headings[0]:
            lines.append(f"**Error:** {headings[0]['error']}\n")
            continue

        if not headings:
            lines.append("*No headings found*\n")
            continue

        lines.append("### Document Structure\n")
        for heading in headings:
            level = heading.get("level", 1)
            text = heading.get("text", "")
            line_num = heading.get("line", "")
            indent = "  " * (level - 1)
            lines.append(f"{indent}- **H{level}:** {text} (line {line_num})")

        lines.append("\n---\n")

    return "\n".join(lines).strip()
