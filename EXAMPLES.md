# Examples

This file collects beginner-friendly examples for common workflows. Run these from PowerShell in the project folder.

## Create the `.env` file (PowerShell)

Create the parent folder and write the `DATABASE_URL` in one step:

```powershell
New-Item -ItemType Directory -Path "$env:USERPROFILE\credentials\db_connect" -Force
Set-Content -Path "$env:USERPROFILE\credentials\db_connect\.env" -Value "DATABASE_URL=postgresql://neondb_owner:YOUR_PASSWORD_HERE@host:5432/neondb?sslmode=require"
```

Or copy the example file:

```powershell
copy .env.example $env:USERPROFILE\credentials\db_connect\.env
```

## Run a simple query

```powershell
python -m db_connection
```

This runs the default query: `SELECT version(), current_database(), current_user();` (the CLI prints the result).

## Run a SQL file

```powershell
python -m db_connection --query-file query.sql
```

## Check PostgreSQL version and info

Get the PostgreSQL version:

```powershell
python -m db_connection --query "SELECT version();"
```

Get the current database and user:

```powershell
python -m db_connection --query "SELECT current_database(), current_user;"
```

Get version details in a more readable format:

```powershell
python -m db_connection --query "SELECT pg_version();"
```

## Create a `users` table (SQL file)

Create `create_users.sql` with:

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

## Insert JSON data (single row)

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

## Insert CSV data (multiple rows)

Create `users.csv` and `insert_users.sql` then run:

```powershell
python -m db_connection --query-file insert_users.sql --data-file users.csv --data-format csv
```

## List all user tables

```powershell
python -m db_connection --query "SELECT table_schema, table_name FROM information_schema.tables WHERE table_type='BASE TABLE' AND table_schema NOT IN ('pg_catalog','information_schema');"
```

## Show table column names

Replace `users` with your table name:

```powershell
python -m db_connection --query "SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='public' AND table_name='users';"
```

## Create a temporary demo table

You can use the example file `create_temp_demo.sql` in the repo, or run inline:

```powershell
python -m db_connection --query-file create_temp_demo.sql
# or
python -m db_connection --query "CREATE TABLE IF NOT EXISTS temp_demo (id SERIAL PRIMARY KEY, name TEXT, created_at TIMESTAMP DEFAULT now());"
```

## Drop the demo table

```powershell
python -m db_connection --query-file drop_temp_demo.sql
# or
python -m db_connection --query "DROP TABLE IF EXISTS temp_demo;"
```

## Create a `sample` JSONB table and insert `sample.json`

There is a `sample.json` in this repo. The steps below create the table, insert the file, then demonstrate queries to inspect nested fields (`binTypes`, `zones`, `nodes`, etc.).

1) Create the table (we provide `create_sample_table.sql`):

```powershell
python -m db_connection --query-file create_sample_table.sql
```

2) Insert `sample.json` directly (no wrapping needed):

```powershell
python -m db_connection --query "INSERT INTO sample (content) VALUES (%(content)s::jsonb)" --data-file sample.json --data-format json
```

3) Basic verification — check rows and a top-level field:

```powershell
python -m db_connection --query "SELECT COUNT(*) FROM sample;"
python -m db_connection --query "SELECT id, content->'meta'->>'name' AS meta_name FROM sample;"
```

4) Inspect nested JSON content (examples):

- Pretty-print the full JSON stored in the first row:

```powershell
python -m db_connection --query "SELECT jsonb_pretty(content) FROM sample LIMIT 1;"
```

- List top-level keys:

```powershell
python -m db_connection --query "SELECT jsonb_object_keys(content) FROM sample;"
```

- Show `binTypes` keys (the available bin types):

```powershell
python -m db_connection --query "SELECT jsonb_object_keys(content->'binTypes') FROM sample;"
```

- Count zones and show the first 5 zone entries (pretty-printed):

```powershell
python -m db_connection --query "SELECT jsonb_array_length(content->'zones') FROM sample;"
python -m db_connection --query "SELECT jsonb_pretty(elem) FROM sample, jsonb_array_elements(content->'zones') AS elem LIMIT 5;"
```

- Count nodes and show a few node entries:

```powershell
python -m db_connection --query "SELECT jsonb_array_length(content->'nodes') FROM sample;"
python -m db_connection --query "SELECT jsonb_pretty(elem) FROM sample, jsonb_array_elements(content->'nodes') AS elem LIMIT 5;"
```

- Extract a scalar value (example: settings.snap):

```powershell
python -m db_connection --query "SELECT (content->'settings'->>'snap')::numeric AS snap FROM sample;"
```

5) Remove the example table when finished:

```powershell
python -m db_connection --query "DROP TABLE IF EXISTS sample;"
```

## Update nested JSON fields (modify stored JSONB data)

Once you have JSON stored in a JSONB column, you can modify nested fields using PostgreSQL's `jsonb_set` operator.

**Example: Update a field in a nested object**

Suppose you want to change the `speed_limit_mps` field in an edge object:

```powershell
python -m db_connection --query "UPDATE sample SET content = jsonb_set(content, '{edges,0,speed_limit_mps}', '3.0') WHERE id = 1;"
```

Verify the update:

```powershell
python -m db_connection --query "SELECT (content->'edges'->>0)::jsonb->>'speed_limit_mps' FROM sample WHERE id = 1;"
```

**Example: Add a new field to a nested object**

Add a `last_updated` timestamp to the metadata:

```powershell
python -m db_connection --query "UPDATE sample SET content = jsonb_set(content, '{meta,last_updated}', to_jsonb(now()::text)) WHERE id = 1;"
```

Verify:

```powershell
python -m db_connection --query "SELECT content->'meta'->>'last_updated' FROM sample WHERE id = 1;"
```

**Example: Append a new edge object to the array**

Add a new edge with the structure you showed:

```powershell
python -m db_connection --query "UPDATE sample SET content = jsonb_set(content, '{edges,-1}', '{\"a\": \"WPT_EAST_CORRIDOR\", \"b\": \"WPT_AISLE_1213\", \"ramp\": false, \"distance_m\": 7.5, \"traffic_class\": \"forklift_only\", \"width_m\": 3.5, \"direction\": \"bidirectional\", \"speed_limit_mps\": 2.0, \"vertical_clearance_m\": 14.0, \"surface\": \"concrete_sealed\"}'::jsonb) WHERE id = 1;"
```

Verify the append:

```powershell
python -m db_connection --query "SELECT jsonb_array_length(content->'edges') FROM sample WHERE id = 1;"
```

**Notes on JSONB update syntax:**
- `jsonb_set(jsonb, path_array, value)` sets a value at a JSON path.
- Path syntax: `'{key1, key2, index}'` for nested objects and arrays.
- Use `-1` as the array index to append.
- Use `to_jsonb()` to convert PostgreSQL values (like `now()`) to JSON.
- For large updates, consider using `jsonb_insert` or replacing the entire column.

## Quick verification queries

- Count rows:

```powershell
python -m db_connection --query "SELECT COUNT(*) FROM sample;"
```

- Find rows matching meta.name:

```powershell
python -m db_connection --query "SELECT id FROM sample WHERE content->'meta'->>'name' = 'OUTLET WAREHOUSE';"
```

## Notes

- These examples are beginner-friendly and safe to run; they use `IF NOT EXISTS` and `IF EXISTS` where appropriate.
- For more advanced usage or automation, refer to the CLI help: `python -m db_connection --help`.

## Resources for PostgreSQL Beginners

- **PostgreSQL Official Documentation**: https://www.postgresql.org/docs/
- **Common SQL Commands**: https://www.postgresql.org/docs/current/sql-commands.html
- **PostgreSQL Tutorial**: https://www.postgresql.org/docs/current/tutorial.html
- **JSONB Data Type**: https://www.postgresql.org/docs/current/datatype-json.html
- **PostgreSQL Function Reference**: https://www.postgresql.org/docs/current/functions.html
- **Query Optimization Tips**: https://www.postgresql.org/docs/current/sql-syntax.html
