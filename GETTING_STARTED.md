# Getting Started with db_connection

This guide is for beginners who want a simple, safe way to connect to PostgreSQL.

## 1. Install Python

Make sure you have Python 3.11 or newer installed. You can verify this with:

```powershell
python --version
```

## 2. Install dependencies

Open PowerShell in the project folder and install the required packages:

```powershell
python -m pip install -r requirements.txt
```

## 3. Create a credentials file

Create this file on Windows:

```text
C:\Users\<your-user>\credentials\db_connect\.env
```

Then add a single line with your connection URL:

```text
DATABASE_URL=postgresql://neondb_owner:YOUR_PASSWORD_HERE@host/db?sslmode=require
```

Do not commit the `.env` file to Git.

## 4. Examples

All step-by-step examples (creating tables, inserting JSON/CSV, listing tables, verification queries, and more) have been moved to [EXAMPLES.md](EXAMPLES.md). Open that file for beginner-friendly, PowerShell-ready commands.

## 11. Need help?

Use the built-in help screen:

```powershell
python -m db_connection --help
```

This project is designed to be easy to use while keeping credentials secure.
