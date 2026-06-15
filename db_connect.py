from db_connection.cli import app


if __name__ == "__main__":
    app()


def format_text(text: str, color: str, use_color: bool) -> str:
    if use_color:
        return f"{color}{text}{Style.RESET_ALL}"
    return text


def load_environment(env_file: str, use_color: bool) -> Path | None:
    env_path = Path(env_file)
    if not env_path.exists():
        print(
            format_text(
                f"Warning: .env file not found at {env_file}.", Fore.YELLOW, use_color
            )
        )
        return None

    load_dotenv(dotenv_path=env_path, override=False)
    print(
        format_text(
            f"Loaded environment from {env_path.resolve()}", Fore.CYAN, use_color
        )
    )
    return env_path.resolve()


def get_database_url(cli_database_url: str | None) -> str:
    if cli_database_url:
        return cli_database_url

    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError(
            "DATABASE_URL is not set. Provide -d/--database-url or add DATABASE_URL to a .env file."
        )
    return url


def load_query(args: argparse.Namespace) -> str:
    if args.query_file:
        query_path = Path(args.query_file)
        if not query_path.exists():
            raise FileNotFoundError(f"Query file not found: {query_path}")
        return query_path.read_text(encoding="utf-8")
    return args.query


def infer_format(file_path: Path, forced_format: str | None) -> str:
    if forced_format:
        return forced_format
    if file_path.suffix.lower() == ".json":
        return "json"
    if file_path.suffix.lower() == ".csv":
        return "csv"
    raise ValueError(
        "Could not infer data format from file extension. Use --data-format json|csv."
    )


def load_data(data_file: str, data_format: str | None) -> object:
    path = Path(data_file)
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")

    format_name = infer_format(path, data_format)
    if format_name == "json":
        return json.loads(path.read_text(encoding="utf-8"))

    with path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        return [row for row in reader]


def execute_query(cur: psycopg.Cursor, query: str, data: object | None) -> list[tuple]:
    if data is None:
        cur.execute(query)
    elif isinstance(data, dict):
        cur.execute(query, data)
    elif isinstance(data, list):
        if len(data) == 0:
            raise ValueError("Data file is empty; no parameters to use.")

        if all(isinstance(item, dict) for item in data):
            cur.executemany(query, data)
        elif all(isinstance(item, (list, tuple)) for item in data):
            cur.executemany(query, data)
        else:
            cur.executemany(query, [(item,) for item in data])
    else:
        cur.execute(query, (data,))

    if cur.description:
        return cur.fetchall()
    return []


def main() -> None:
    args = parse_args()
    use_color = not args.no_color

    print(format_text("PostgreSQL CLI connection tester", Fore.MAGENTA, use_color))
    if args.database_url:
        print(format_text("Using database URL provided on the command line.", Fore.CYAN, use_color))
    else:
        loaded = load_environment(args.env_file, use_color)
        if loaded is None:
            print(
                format_text(
                    "No .env file loaded. Provide a connection URL with -d/--database-url.",
                    Fore.RED,
                    use_color,
                )
            )

    try:
        database_url = get_database_url(args.database_url)
        query = load_query(args)
        data = None
        if args.data_file:
            data = load_data(args.data_file, args.data_format)
            print(
                format_text(
                    f"Loaded data from {args.data_file} ({args.data_format or 'inferred'}).",
                    Fore.CYAN,
                    use_color,
                )
            )

        print(format_text("Connecting to PostgreSQL database...", Fore.GREEN, use_color))

        with psycopg.connect(database_url, autocommit=True) as conn:
            with conn.cursor() as cur:
                rows = execute_query(cur, query, data)

                print(
                    format_text(
                        "Connection successful. Query results:", Fore.GREEN, use_color
                    )
                )
                if rows:
                    for row in rows:
                        print(format_text(str(row), Fore.WHITE, use_color))
                else:
                    print(format_text("No rows returned.", Fore.YELLOW, use_color))

    except Error as exc:
        print(format_text("Failed to connect to the database:", Fore.RED, use_color), exc)
        raise
    except (ValueError, FileNotFoundError) as exc:
        print(format_text(str(exc), Fore.RED, use_color))
        raise


if __name__ == "__main__":
    main()
