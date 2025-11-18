"""OpenAPI parsing utilities for the project explorer MCP server."""

import json
from collections.abc import Iterable, Mapping, MutableMapping
from pathlib import Path
from typing import Any

import yaml
from loguru import logger


def load_openapi_spec(path: Path) -> MutableMapping[str, Any]:
    """Load OpenAPI spec from JSON or YAML file.

    Args:
        path: Path to the spec file.

    Returns:
        Parsed document as a dict-like object.

    Raises:
        ValueError: if the file cannot be parsed.
    """
    text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
        logger.debug("Loaded JSON OpenAPI document", path=str(path))
        return data
    except json.JSONDecodeError:
        logger.debug("Not JSON, trying YAML", path=str(path))

    try:
        data = yaml.safe_load(text)
        logger.debug("Loaded YAML OpenAPI document", path=str(path))
        if not isinstance(data, dict):
            raise ValueError("YAML document did not produce a mapping")
        return data
    except Exception as exc:  # broad to wrap yaml errors
        raise ValueError(f"Failed to parse specification: {exc}") from exc


def iter_openapi_operations(
    spec: Mapping[str, Any],
) -> Iterable[dict[str, str | list[str] | None]]:
    """Yield operations found in the OpenAPI spec.

    For each operation yields a dict with keys: method, path, operation_id,
    summary.
    """
    # OpenAPI 3.x and Swagger 2.0 both use top-level 'paths'
    paths = spec.get("paths")
    if not isinstance(paths, Mapping):
        logger.debug("No 'paths' mapping found in spec", spec_keys=list(spec.keys()))
        return

    for raw_path, methods in paths.items():
        if not isinstance(methods, Mapping):
            continue
        for method, operation in methods.items():
            # HTTP verbs in OpenAPI are lower-case (get/post/put/...)
            if method.lower() not in {
                "get",
                "post",
                "put",
                "delete",
                "patch",
                "options",
                "head",
                "trace",
            }:
                # skip parameters or vendor extensions under a path
                continue

            if not isinstance(operation, Mapping):
                continue

            operation_id = operation.get("operationId")
            summary = operation.get("summary")
            description = operation.get("description")

            # Prefer a brief summary, fall back to first line of description
            brief: str | None
            if summary:
                brief = str(summary).strip()
            elif description:
                brief = str(description).strip().splitlines()[0]
            else:
                brief = None

            yield {
                "method": method.upper(),
                "path": raw_path,
                "operation_id": operation_id if operation_id is not None else None,
                "summary": brief,
                "tags": operation.get("tags", []),
            }


def get_openapi_operation_details(
    spec: Mapping[str, Any], selectors: Iterable[str], expand_refs: bool = False
) -> list[dict[str, Any]]:
    """Return full operation records for selectors.

    Selectors can be one of:
    - operationId (exact match)
    - "METHOD /path" (e.g. "GET /users/{id}")
    - just a path (e.g. "/users/{id}") which will match all methods on that path

    Returned records include: method, path, operation_id, summary, description,
    parameters, requestBody, responses.
    """
    results: list[dict[str, str | None]] = []

    paths = spec.get("paths")
    if not isinstance(paths, Mapping):
        return results

    # build lookup by operationId for quick access
    opid_index: dict[str, dict[str, Any]] = {}

    def resolve_ref(ref: str) -> Any:
        """Resolve a local JSON Reference (e.g. '#/components/schemas/IssueBean')."""
        if not isinstance(ref, str) or not ref.startswith("#/"):
            return None
        parts = ref.lstrip("#/").split("/")
        node: Any = spec
        for p in parts:
            if isinstance(node, Mapping):
                node = node.get(p)
            else:
                return None
        return node

    def summarize_schema(
        schema: Any, depth: int = 0, local_expand_refs: bool = False
    ) -> Any:
        """Return a short summary or expanded schema depending on expand_refs.

        If expand_refs is False, returns small strings like 'object{a,b}' or 'array[type]'
        If expand_refs is True, returns resolved mappings (up to a depth limit).
        """
        use_expand = local_expand_refs or expand_refs
        if schema is None:
            return None

        # Handle $ref
        if isinstance(schema, Mapping) and schema.get("$ref"):
            ref = schema.get("$ref")
            if isinstance(ref, str) and use_expand:
                resolved = resolve_ref(ref)
                # prevent infinite recursion
                if resolved is not None and depth < 3:
                    return summarize_schema(resolved, depth + 1, local_expand_refs)
                return resolved or ref
            return ref

        if isinstance(schema, Mapping):
            stype = schema.get("type")
            desc = schema.get("description")
            default_val = schema.get("default")
            result = {"type": stype}
            if desc:
                result["description"] = desc
            if default_val is not None:
                result["default"] = default_val
            if stype == "object":
                props = schema.get("properties") or {}
                if use_expand:
                    # expand properties with descriptions
                    props_expanded = {}
                    for k, v in props.items():
                        sub = summarize_schema(v, depth + 1, local_expand_refs)
                        if isinstance(sub, dict):
                            props_expanded[k] = sub
                        else:
                            props_expanded[k] = {"type": sub}
                        # add description if available
                        if isinstance(v, dict) and v.get("description"):
                            props_expanded[k]["description"] = v["description"]
                        # add default if available
                        if isinstance(v, dict) and v.get("default") is not None:
                            props_expanded[k]["default"] = v["default"]
                    result["properties"] = props_expanded
                else:
                    # non-expanded short form
                    if isinstance(props, Mapping):
                        keys = list(props.keys())[:5]
                        result["properties"] = (
                            f"{{{', '.join(keys)}{', ...' if len(props) > 5 else ''}}}"
                        )
                    else:
                        result["properties"] = "{}"
            elif stype == "array":
                items = schema.get("items")
                item_sum = summarize_schema(items, depth + 1, local_expand_refs)
                if use_expand:
                    result["items"] = item_sum
                else:
                    result["items"] = item_sum or "?"
            return result

    for raw_path, methods in paths.items():
        if not isinstance(methods, Mapping):
            continue
        for method, operation in methods.items():
            if not isinstance(operation, Mapping):
                continue
            method_upper = method.upper()
            operation_id = operation.get("operationId")
            summary = operation.get("summary")
            description = operation.get("description")
            # parameters, requestBody, responses
            params = []
            for p in operation.get("parameters") or []:
                if not isinstance(p, Mapping):
                    continue
                pname = p.get("name")
                pin = p.get("in")
                preq = p.get("required") or False
                pdesc = p.get("description")
                pschema = summarize_schema(p.get("schema"))
                params.append(
                    {
                        "name": pname,
                        "in": pin,
                        "required": bool(preq),
                        "schema": pschema,
                        "description": str(pdesc).strip() if pdesc else None,
                    }
                )

            request_body = None
            if "requestBody" in operation and operation.get("requestBody"):
                rb = operation.get("requestBody")
                if isinstance(rb, Mapping):
                    # OpenAPI 3 requestBody may have description and content mapping
                    rb_desc = rb.get("description")
                    content = {}
                    for ctype, media in (rb.get("content") or {}).items():
                        if isinstance(media, Mapping):
                            schema = media.get("schema")
                            schema_summary = summarize_schema(
                                schema, local_expand_refs=True
                            )
                            content[ctype] = schema_summary
                    request_body = {
                        "description": str(rb_desc).strip() if rb_desc else None,
                        "content": content,
                    }

            responses = {}
            for code, resp in (operation.get("responses") or {}).items():
                if not isinstance(resp, Mapping):
                    continue
                rdesc = resp.get("description")
                rcontent = {}
                for ctype, media in (resp.get("content") or {}).items():
                    if isinstance(media, Mapping):
                        schema = media.get("schema")
                        schema_summary = summarize_schema(
                            schema, local_expand_refs=True
                        )
                        rcontent[ctype] = schema_summary
                responses[code] = {
                    "description": str(rdesc).strip() if rdesc else None,
                    "content": rcontent,
                }
            record = {
                "method": method_upper,
                "path": raw_path,
                "operation_id": operation_id if operation_id is not None else None,
                "summary": str(summary).strip() if summary else None,
                "description": str(description).strip() if description else None,
                "parameters": params,
                "requestBody": request_body,
                "responses": responses,
            }

            if operation_id:
                opid_index[str(operation_id)] = record

    for sel in selectors:
        sel = sel.strip()
        if not sel:
            continue

        # METHOD + path
        if " " in sel:
            maybe_method, maybe_path = sel.split(" ", 1)
            method = maybe_method.upper()
            path = maybe_path
            # find exact match
            for raw_path, methods in paths.items():
                if raw_path != path:
                    continue
                if not isinstance(methods, Mapping):
                    continue
                op = methods.get(method.lower())
                if isinstance(op, Mapping):
                    results.append(
                        {
                            "method": method,
                            "path": raw_path,
                            "operation_id": op.get("operationId"),
                            "summary": op.get("summary"),
                            "description": op.get("description"),
                        }
                    )
                    break
            continue

        # operationId
        if sel in opid_index:
            results.append(opid_index[sel])
            continue

        # treat as path: return all methods under the path
        path = sel
        for raw_path, methods in paths.items():
            if raw_path != path:
                continue
            if not isinstance(methods, Mapping):
                continue
            for method, operation in methods.items():
                if not isinstance(operation, Mapping):
                    continue
                results.append(
                    {
                        "method": method.upper(),
                        "path": raw_path,
                        "operation_id": operation.get("operationId"),
                        "summary": operation.get("summary"),
                        "description": operation.get("description"),
                    }
                )

    return results


def format_openapi_details(records: Iterable[Mapping[str, Any]]) -> str:
    """Format detailed operation records into text with full description."""
    out_lines: list[str] = []
    for r in records:
        method = r.get("method") or ""
        path = r.get("path") or ""
        opid = r.get("operation_id") or "-"
        summary = r.get("summary") or "-"
        description = r.get("description") or "-"
        out_lines.append(f"{method} {path}  ({opid})")
        out_lines.append(f"Summary: {summary}")
        out_lines.append("Description:")
        out_lines.extend([line.rstrip() for line in str(description).splitlines()])
        # Parameters
        params = r.get("parameters") or []
        if params:
            out_lines.append("")
            out_lines.append("Parameters:")
            for p in params:
                pname = p.get("name")
                pin = p.get("in")
                preq = p.get("required")
                pschema = p.get("schema")
                pdesc = p.get("description")
                out_lines.append(
                    f" - {pname} (in: {pin}) required={preq} schema={pschema}"
                )
                if pdesc:
                    out_lines.append(f"   {pdesc}")

        # Request body
        rb = r.get("requestBody")
        if rb:
            out_lines.append("")
            out_lines.append("Request Body:")
            if rb.get("description"):
                out_lines.append(f"  {rb.get('description')}")
            for ctype, schema in (rb.get("content") or {}).items():
                out_lines.append(f"  - {ctype}: {schema}")

        # Responses
        resps = r.get("responses") or {}
        if resps:
            out_lines.append("")
            out_lines.append("Responses:")
            for code, info in resps.items():
                out_lines.append(f" {code}: {info.get('description')}")
                for ctype, schema in (info.get("content") or {}).items():
                    out_lines.append(f"    - {ctype}: {schema}")
        out_lines.append("-" * 80)
    return "\n".join(out_lines)


def format_openapi_details_markdown(records: Iterable[Mapping[str, Any]]) -> str:
    """Format detailed operation records into markdown with full description."""
    lines = []
    lines.append("# OpenAPI Operation Details")
    lines.append("")

    for r in records:
        method = r.get("method") or ""
        path = r.get("path") or ""
        opid = r.get("operation_id") or "-"
        summary = r.get("summary") or "-"
        description = r.get("description") or "-"

        lines.append(f"## {method} {path}")
        lines.append("")
        if opid != "-":
            lines.append(f"**Operation ID:** {opid}")
            lines.append("")
        lines.append(f"**Summary:** {summary}")
        lines.append("")
        lines.append("**Description:**")
        lines.append("")
        lines.extend(
            [
                f"{line.rstrip()}"
                for line in str(description).splitlines()
                if line.strip()
            ]
        )
        lines.append("")

        # Parameters
        params = r.get("parameters") or []
        if params:
            lines.append("### Parameters")
            lines.append("")
            lines.append("| Name | In | Required | Schema | Description |")
            lines.append("|------|----|----------|--------|-------------|")
            for p in params:
                pname = p.get("name") or ""
                pin = p.get("in") or ""
                preq = "Yes" if p.get("required") else "No"
                pschema = p.get("schema") or ""
                pdesc = p.get("description") or ""
                lines.append(f"| {pname} | {pin} | {preq} | `{pschema}` | {pdesc} |")
            lines.append("")

        # Request body
        rb = r.get("requestBody")
        if rb:
            lines.append("### Request Body")
            lines.append("")
            if rb.get("description"):
                lines.append(f"{rb.get('description')}")
                lines.append("")
            lines.append("**Content Types:**")
            lines.append("")
            for ctype, schema in (rb.get("content") or {}).items():
                lines.append(f"- `{ctype}`: `{schema}`")
            lines.append("")

        # Responses
        resps = r.get("responses") or {}
        if resps:
            lines.append("### Responses")
            lines.append("")
            for code, info in resps.items():
                lines.append(f"#### {code}")
                lines.append("")
                if info.get("description"):
                    lines.append(f"{info.get('description')}")
                    lines.append("")
                if info.get("content"):
                    lines.append("**Content Types:**")
                    lines.append("")
                    for ctype, schema in info.get("content", {}).items():
                        lines.append(f"- `{ctype}`: `{schema}`")
                    lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines).strip()


def format_openapi_text(ops: Iterable[Mapping[str, str | None]]) -> str:
    """Format operations as a human-readable table-like text."""
    rows = []
    for op in ops:
        method = op.get("method") or ""
        path = op.get("path") or ""
        opid = op.get("operation_id") or "-"
        summary = op.get("summary") or "-"
        rows.append(f"{method:6} {path:40} {opid:30} {summary}")

    header = f"{'METHOD':6} {'PATH':40} {'OPERATION_ID':30} SUMMARY"
    return "\n".join([header, "-" * 100] + rows)


def format_openapi_markdown(ops: Iterable[Mapping[str, str | list | None]]) -> str:
    """Format operations as a markdown table."""
    lines = []
    lines.append("# OpenAPI Operations")
    lines.append("")
    lines.append("| Method | Path | Operation ID | Summary | Tags |")
    lines.append("|--------|------|--------------|---------|------|")

    for op in ops:
        method = op.get("method") or ""
        path = op.get("path") or ""
        opid = op.get("operation_id") or "-"
        summary = op.get("summary") or "-"
        tags = op.get("tags", [])
        tags_str = ", ".join(tags) if tags else "-"
        lines.append(f"| {method} | `{path}` | {opid} | {summary} | {tags_str} |")

    return "\n".join(lines)
