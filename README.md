# **connection_db** is a lightweight Python utility written to establish and verify a connection to a Neon-hosted PostgreSQL database (project: Hail_Mary, AWS US West 2 — Oregon).

The immediate need was practical: Neon provisions a serverless Postgres instance that scales to zero when inactive, which means the first connection after an idle period wakes the compute node. Before building any application logic on top of it, I needed confidence that the connection string, credentials, and pooler configuration were all working correctly end-to-end from my local WinPython development environment.

`connection_db` handles that verification step — it reads the database connection parameters from a `.env` file (host, database name, role, password, and pooler host), attempts a connection, and confirms the database is reachable and responding. Keeping credentials out of the source code and in environment variables from the start enforces the same discipline the production deployment will require, and makes it straightforward for a second developer to connect by supplying their own `.env` without touching the codebase.

This is the foundation layer for a larger warehouse routing and slotting system. Getting the database connection right and documented first means every subsequent component — schema creation, data ingestion, the routing engine — has a known-good, reproducible starting point.

# PostgreSQL Connection App

A professional PostgreSQL CLI built for usability, secure credentials, and beginner-friendly workflows.

## Getting Started

If you are new to Python or database CLI tools, open `GETTING_STARTED.md` for a step-by-step beginner guide.

## Setup

1. Install dependencies with the same Python interpreter you will use to run the CLI:

```powershell
python -m pip install -r requirements.txt
```

If you have multiple Python installations, make sure `python --version` matches the interpreter you want to use.

2. Copy the example credentials file to the default location:

```powershell
copy .env.example C:\Users\%USERNAME%\credentials\db_connect\.env
```

3. Edit the `.env` file and replace `YOUR_PASSWORD_HERE` with your real PostgreSQL credentials.

## DATABASE_URL format

The `DATABASE_URL` uses the standard PostgreSQL URI format:

```text
postgresql://<user>:<password>@<host>:<port>/<database>?sslmode=require
```

Example values:

- host: `ep-round-star-afetxr0p.c-2.us-west-2.aws.neon.tech`
- database: `neondb`
- user: `neondb_owner`
- password: your secret password
- port: `5432` (default for PostgreSQL)

If you are connecting through a query pooler or proxy, put the pooler host in the same URL:

```text
postgresql://neondb_owner:YOUR_PASSWORD_HERE@pooler-host.example.com:5432/neondb?sslmode=require
```

## Usage

Run the packaged CLI:

```powershell
python -m db_connection
```

Show help:

```powershell
python -m db_connection --help
```

Run a SQL file:

```powershell
python -m db_connection --query-file query.sql
```

Pass JSON or CSV data:

```powershell
python -m db_connection --query "INSERT INTO users (name, email) VALUES (%(name)s, %(email)s)" --data-file user.json
```

```powershell
python -m db_connection --query-file insert_users.sql --data-file users.csv --data-format csv
```

## Examples

Beginner-friendly examples (create tables, insert JSON/CSV, inspect tables, and verification commands) are consolidated in [EXAMPLES.md](EXAMPLES.md). Open that file for step-by-step PowerShell-ready commands.


Override the `.env` location:

```powershell
python -m db_connection --env-file C:\path\to\custom\.env
```

Override the database URL directly:

```powershell
python -m db_connection --database-url "postgresql://..."
```

## Professional notes

- Keep secrets out of Git by using `.env` and `.env.example`.
- The default `.env` path is `C:\Users\<your-user>\credentials\db_connect\.env`.
- If you want a beginner guide, see `GETTING_STARTED.md`.

## Dependencies

- `typer`
- `rich`
- `python-dotenv`
- `psycopg`
