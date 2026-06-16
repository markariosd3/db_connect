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

## 4. Run a simple query

Use the default command:

```powershell
python db_connect.py
```

If the environment file is in the default location, it will load automatically.

## 5. Use a SQL file

Create a small SQL file, for example `query.sql`:

```sql
SELECT now();
```

Then run:

```powershell
python -m db_connection --query-file query.sql
```

## 6. Create a new table and load data

### 6.1 Create the table

Create `create_users.sql`:

```sql
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE
);
```

Run:

```powershell
python -m db_connection --query-file create_users.sql
```

### 6.2 Insert JSON data

Create `user.json`:

```json
{
  "name": "Alice",
  "email": "alice@example.com"
}
```

Run:

```powershell
python -m db_connection --query "INSERT INTO users (name, email) VALUES (%(name)s, %(email)s)" --data-file user.json
```

### 6.3 Insert CSV data

Create `users.csv`:

```csv
name,email
Alice,alice@example.com
Bob,bob@example.com
```

Create `insert_users.sql`:

```sql
INSERT INTO users (name, email) VALUES (%(name)s, %(email)s);
```

Run:

```powershell
python -m db_connection --query-file insert_users.sql --data-file users.csv --data-format csv
```

## 7. Update rows using JSON or CSV data

### 7.1 Update with JSON

Create `update_user.json`:

```json
{
  "id": 1,
  "email": "alice.updated@example.com"
}
```

Run:

```powershell
python -m db_connection --query "UPDATE users SET email = %(email)s WHERE id = %(id)s" --data-file update_user.json
```

### 7.2 Update with CSV

Create `update_users.csv`:

```csv
id,email
1,alice.updated@example.com
2,bob.updated@example.com
```

Create `update_users.sql`:

```sql
UPDATE users SET email = %(email)s WHERE id = %(id)s;
```

Run:

```powershell
python -m db_connection --query-file update_users.sql --data-file update_users.csv --data-format csv
```

## 8. Select data with a join

Create a second table, `roles`:

```sql
CREATE TABLE IF NOT EXISTS roles (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL
);
```

Run:

```powershell
python -m db_connection --query-file create_roles.sql
```

Add a join query file, `select_users_roles.sql`:

```sql
SELECT u.id AS user_id,
       u.name AS user_name,
       u.email,
       r.name AS role_name
FROM users u
INNER JOIN roles r ON u.id = r.id;
```

Run:

```powershell
python -m db_connection --query-file select_users_roles.sql
```

## 9. Delete a table

Create `drop_users.sql`:

```sql
DROP TABLE IF EXISTS users;
```

Run:

```powershell
python -m db_connection --query-file drop_users.sql
```

Create `drop_roles.sql`:

```sql
DROP TABLE IF EXISTS roles;
```

Run:

```powershell
python -m db_connection --query-file drop_roles.sql
```

## 10. Inspect and manage tables

This section shows a few useful commands to inspect tables in the database, get column names, and create or remove a temporary table for testing.

### 10.1 List all user tables

Run:

```powershell
python -m db_connection --query "SELECT table_schema, table_name FROM information_schema.tables WHERE table_type='BASE TABLE' AND table_schema NOT IN ('pg_catalog','information_schema');"
```

### 10.2 Show table field names

Replace `users` with the table you want to inspect:

```powershell
python -m db_connection --query "SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='public' AND table_name='users';"
```

### 10.3 Create a temporary demo table

Create `create_temp_demo.sql`:

```sql
CREATE TABLE IF NOT EXISTS temp_demo (
  id SERIAL PRIMARY KEY,
  name TEXT,
  created_at TIMESTAMP DEFAULT now()
);
```

Run:

```powershell
python -m db_connection --query-file create_temp_demo.sql
```

Or run inline:

```powershell
python -m db_connection --query "CREATE TABLE IF NOT EXISTS temp_demo (id SERIAL PRIMARY KEY, name TEXT, created_at TIMESTAMP DEFAULT now());"
```

### 10.4 Drop the demo table

Create `drop_temp_demo.sql`:

```sql
DROP TABLE IF EXISTS temp_demo;
```

Run:

```powershell
python -m db_connection --query-file drop_temp_demo.sql
```

Or run inline:

```powershell
python -m db_connection --query "DROP TABLE IF EXISTS temp_demo;"
```

### 10.5 Create a table and insert `sample.json` (beginner-friendly)

This project includes a `sample.json` file. The steps below create a simple `jsonb` table, show how to wrap `sample.json` into a named parameter the CLI understands, insert the file, and verify the result.

1) Create the table file `create_sample_json_table.sql` with this content:

```sql
CREATE TABLE IF NOT EXISTS sample_json (
  id SERIAL PRIMARY KEY,
  content JSONB NOT NULL
);
```

2) Run the create script (this makes the table in your database):

```powershell
python -m db_connection --query-file create_sample_json_table.sql
```

3) Wrap `sample.json` so the CLI sends it as a named parameter called `content`.
   Run this Python one-liner from PowerShell (it reads `sample.json` and writes `sample_wrapped.json`):

```powershell
python -c "import json; data=json.load(open('sample.json')); json.dump({'content': json.dumps(data)}, open('sample_wrapped.json','w'), indent=2)"
```

4) Insert the wrapped JSON into the table:

```powershell
python -m db_connection --query "INSERT INTO sample_json (content) VALUES (%(content)s::jsonb)" --data-file sample_wrapped.json --data-format json
```

5) Verify the insert (this example extracts the `meta.name` field from the stored JSON):

```powershell
python -m db_connection --query "SELECT id, content->'meta'->>'name' AS meta_name FROM sample_json;"
```

6) When finished, drop the table:

```powershell
python -m db_connection --query "DROP TABLE IF EXISTS sample_json;"
```

## 11. Need help?

Use the built-in help screen:

```powershell
python -m db_connection --help
```

This project is designed to be easy to use while keeping credentials secure.
