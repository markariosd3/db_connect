from __future__ import annotations

from typing import Any

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
            cursor.execute(query, data)
        elif isinstance(data, list):
            if len(data) == 0:
                raise ValueError("Data file is empty; there is nothing to execute.")

            if all(isinstance(item, dict) for item in data):
                cursor.executemany(query, data)
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


def connect_and_execute(database_url: str, query: str, data: Any | None, dry_run: bool) -> list[tuple]:
    """Open a connection, run the query, and return the result rows."""
    if dry_run:
        return []

    with psycopg.connect(database_url, autocommit=True) as conn:
        with conn.cursor() as cur:
            return execute_query(cur, query, data)
