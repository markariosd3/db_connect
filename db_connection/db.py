from __future__ import annotations

from typing import Any

import json
import re
import psycopg


def execute_query(cursor: psycopg.Cursor, query: str, data: Any | None) -> list[tuple]:
    """Execute a SQL statement with optional parameters and return any fetched rows.

    Some PostgreSQL-compatible servers reject multi-expression `SELECT a, b, c` forms.
    In that case we retry by executing each expression separately and returning a
    single combined row so the caller still gets a useful result.
    """
    try:
        if data is None:
            cursor.execute(query)
        elif isinstance(data, dict):
            # If the provided JSON file is the document itself (not a
            # mapping of parameter names), and the query expects a single
            # named parameter (e.g. %(content)s), wrap the JSON document
            # into that parameter name so users can pass `sample.json`
            # directly.
            placeholder_names = re.findall(r"%\(([A-Za-z0-9_]+)\)s", query)
            params: dict[str, Any]
            if placeholder_names:
                # If the dict already contains the named placeholders,
                # use it (but convert nested structures to JSON strings).
                if set(placeholder_names).issubset(set(data.keys())):
                    params = _prepare_params_for_jsonb(data)
                elif len(placeholder_names) == 1:
                    # Wrap whole document into the single placeholder.
                    params = {placeholder_names[0]: json.dumps(data)}
                else:
                    # Fall back to trying the dict as-is.
                    params = _prepare_params_for_jsonb(data)
            else:
                params = _prepare_params_for_jsonb(data)
            cursor.execute(query, params)
        elif isinstance(data, list):
            if len(data) == 0:
                raise ValueError("Data file is empty; there is nothing to execute.")
            if all(isinstance(item, dict) for item in data):
                # Prepare each dict for executemany (convert nested
                # structures to JSON strings where necessary).
                prepared = [_prepare_params_for_jsonb(item) for item in data]
                cursor.executemany(query, prepared)
            elif all(isinstance(item, (list, tuple)) for item in data):
                cursor.executemany(query, data)
            else:
                cursor.executemany(query, [(item,) for item in data])
        else:
            cursor.execute(query, (data,))
    except psycopg.errors.SyntaxError as orig_err:
        # Fallback: if the query is a simple SELECT with comma-separated
        # expressions, try running each expression individually and combine
        # their scalar results into a single tuple.
        m = re.match(r"^\s*SELECT\s+(.*?);?\s*$", query, re.I | re.S)
        if m and "," in m.group(1):
            parts = [p.strip() for p in m.group(1).split(",")]
            values = []
            for expr in parts:
                # Try the expression as-is first, then try without trailing
                # parentheses (e.g. `current_user()` -> `current_user`) if it fails.
                tried = False
                try:
                    cursor.execute(f"SELECT {expr}")
                    row = cursor.fetchone()
                    values.append(row[0] if row is not None else None)
                    tried = True
                except psycopg.errors.SyntaxError:
                    if expr.endswith("()"):
                        alt = expr[:-2]
                        try:
                            cursor.execute(f"SELECT {alt}")
                            row = cursor.fetchone()
                            values.append(row[0] if row is not None else None)
                            tried = True
                        except psycopg.errors.SyntaxError:
                            tried = False
                if not tried:
                    # Can't recover for this expression; re-raise original error
                    raise orig_err
            return [tuple(values)]
        # Re-raise if we can't handle the syntax error
        raise

    if cursor.description is None:
        return []
    return cursor.fetchall()


def _prepare_params_for_jsonb(params: dict[str, Any]) -> dict[str, Any]:
    """Convert any dict/list values in a parameter mapping to JSON strings.

    This helps psycopg adapt complex Python structures when the query
    expects a `jsonb` value.
    """
    out: dict[str, Any] = {}
    for k, v in params.items():
        if isinstance(v, (dict, list)):
            out[k] = json.dumps(v)
        else:
            out[k] = v
    return out


def connect_and_execute(database_url: str, query: str, data: Any | None, dry_run: bool) -> list[tuple]:
    """Open a connection, run the query, and return the result rows."""
    if dry_run:
        return []

    with psycopg.connect(database_url, autocommit=True) as conn:
        with conn.cursor() as cur:
            return execute_query(cur, query, data)
