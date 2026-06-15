from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from . import __version__
from .config import default_env_path, get_database_url, load_env_file
from .data import load_data_file, load_query
from .db import connect_and_execute

app = typer.Typer(
    help="Professional PostgreSQL CLI with .env support, query-file loading, and JSON/CSV data injection.",
    context_settings={"help_option_names": ["-h", "--help"]},
)


def setup_logging(verbose: bool, console: Console) -> logging.Logger:
    handler = RichHandler(console=console, markup=True)
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(message)s",
        handlers=[handler],
    )
    logger = logging.getLogger("db_connection")
    return logger


def version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    env_file: Path = typer.Option(
        default_env_path(),
        "-e",
        "--env-file",
        help="Path to the .env file containing DATABASE_URL.",
    ),
    database_url: Optional[str] = typer.Option(
        None,
        "-d",
        "--database-url",
        help="PostgreSQL connection URL. Overrides .env values.",
    ),
    query: str = typer.Option(
        "SELECT version(), current_database(), current_user();",
        "-q",
        "--query",
        help="SQL query to run after connecting to the database.",
    ),
    query_file: Optional[Path] = typer.Option(
        None,
        "--query-file",
        exists=False,
        file_okay=True,
        dir_okay=False,
        help="Path to a SQL file to execute.",
    ),
    data_file: Optional[Path] = typer.Option(
        None,
        "--data-file",
        exists=False,
        file_okay=True,
        dir_okay=False,
        help="Path to a JSON or CSV file with query parameters.",
    ),
    data_format: Optional[str] = typer.Option(
        None,
        "--data-format",
        help="Force the data file format: json or csv.",
    ),
    dry_run: bool = typer.Option(
        False,
        "-n",
        "--dry-run",
        help="Validate configuration and query without executing against the database.",
    ),
    verbose: bool = typer.Option(
        False,
        "-v",
        "--verbose",
        help="Enable debug logging.",
    ),
    no_color: bool = typer.Option(
        False,
        "--no-color",
        help="Disable colorized terminal output.",
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version information and exit.",
    ),
) -> None:
    if ctx.invoked_subcommand is not None:
        return

    console = Console(no_color=no_color)
    logger = setup_logging(verbose, console)
    console.print("[bold magenta]PostgreSQL connection tool[/bold magenta]")

    if database_url:
        console.print("[cyan]Using database URL from command line override.[/cyan]")
    else:
        if not load_env_file(env_file):
            console.print(
                f"[yellow]Environment file not found at {env_file}."
                " Provide --database-url or create the file and try again.[/yellow]"
            )
        else:
            console.print(f"[cyan]Loaded credentials from {env_file}[/cyan]")

    try:
        resolved_url = get_database_url(database_url)
        loaded_query = load_query(query, query_file)
        loaded_data = None
        if data_file is not None:
            loaded_data = load_data_file(data_file, data_format)
            console.print(
                f"[cyan]Loaded data from {data_file} ({data_format or 'inferred'}).[/cyan]"
            )

        if dry_run:
            console.print("[green]Dry run complete. Query and data have been validated.[/green]")
            raise typer.Exit()

        console.print("[green]Connecting to PostgreSQL database...[/green]")
        rows = connect_and_execute(resolved_url, loaded_query, loaded_data, dry_run)

        if rows:
            table = Table(show_header=True, header_style="bold blue")
            column_count = len(rows[0])
            for index in range(column_count):
                table.add_column(f"column_{index + 1}")
            for row in rows:
                table.add_row(*[str(value) for value in row])
            console.print(table)
        else:
            console.print("[green]Query executed successfully. No rows returned.[/green]")

    except Exception as error:
        logger.exception("Failed to execute the database command.")
        console.print(f"[red]Error:[/red] {error}")
        raise typer.Exit(code=1)


@app.command()
def examples() -> None:
    """Show SQL usage examples."""
    console = Console()
    
    console.print("[bold magenta]PostgreSQL Connection Tool - Examples[/bold magenta]\n")
    
    console.print("[bold cyan]0. Create .env File[/bold cyan]")
    console.print("   Create: C:\\Users\\<your-user>\\credentials\\db_connect\\.env")
    console.print("[green]Content:[/green]")
    console.print("   DATABASE_URL=postgresql://neondb_owner:YOUR_PASSWORD_HERE@host/db?sslmode=require")
    console.print("   [dim](Do not commit .env to Git)[/dim]\n")
    
    console.print("[bold cyan]1. Simple Query[/bold cyan]")
    console.print("   [yellow]python -m db_connection[/yellow]")
    console.print("   Runs: SELECT version(), current_database(), current_user();\n")
    
    console.print("[bold cyan]2. Run SQL from File[/bold cyan]")
    console.print("   [yellow]python -m db_connection --query-file query.sql[/yellow]")
    console.print("   SQL File: SELECT now();\n")
    
    console.print("[bold cyan]3. Create Table[/bold cyan]")
    console.print("   [yellow]python -m db_connection --query-file create_users.sql[/yellow]")
    console.print("[green]SQL:[/green]")
    console.print("   CREATE TABLE IF NOT EXISTS users (")
    console.print("     id SERIAL PRIMARY KEY,")
    console.print("     name TEXT NOT NULL,")
    console.print("     email TEXT NOT NULL UNIQUE")
    console.print("   );\n")
    
    console.print("[bold cyan]4. Insert with JSON Data[/bold cyan]")
    console.print("   [yellow]python -m db_connection --query \"INSERT INTO users (name, email) VALUES (%(name)s, %(email)s)\" --data-file user.json[/yellow]")
    console.print("[green]JSON:[/green]")
    console.print("   {")
    console.print("     \"name\": \"Alice\",")
    console.print("     \"email\": \"alice@example.com\"")
    console.print("   }\n")
    
    console.print("[bold cyan]5. Insert with CSV Data[/bold cyan]")
    console.print("   [yellow]python -m db_connection --query-file insert_users.sql --data-file users.csv --data-format csv[/yellow]")
    console.print("[green]CSV:[/green]")
    console.print("   name,email")
    console.print("   Alice,alice@example.com")
    console.print("   Bob,bob@example.com\n")
    
    console.print("[bold cyan]6. Update with JSON[/bold cyan]")
    console.print("   [yellow]python -m db_connection --query \"UPDATE users SET email = %(email)s WHERE id = %(id)s\" --data-file update_user.json[/yellow]\n")
    
    console.print("[bold cyan]7. Update with CSV[/bold cyan]")
    console.print("   [yellow]python -m db_connection --query-file update_users.sql --data-file update_users.csv --data-format csv[/yellow]\n")
    
    console.print("[bold cyan]8. Join Query[/bold cyan]")
    console.print("   [yellow]python -m db_connection --query-file select_users_roles.sql[/yellow]")
    console.print("[green]SQL:[/green]")
    console.print("   SELECT u.id AS user_id,")
    console.print("          u.name AS user_name,")
    console.print("          u.email,")
    console.print("          r.name AS role_name")
    console.print("   FROM users u")
    console.print("   INNER JOIN roles r ON u.id = r.id;\n")
    
    console.print("[bold cyan]9. Validate Without Executing[/bold cyan]")
    console.print("   [yellow]python -m db_connection --query-file query.sql --dry-run[/yellow]")
    console.print("   Validates config and query without database execution.\n")
