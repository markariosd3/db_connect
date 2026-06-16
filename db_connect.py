"""Top-level shim to run the package CLI.

Prefer running the package with `python -m db_connection`.
This file keeps `python db_connect.py` working as a convenience wrapper.
"""

from db_connection.cli import app


if __name__ == "__main__":
    app()
