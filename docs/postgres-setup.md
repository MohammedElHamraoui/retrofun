# Postgres Database Setup

This document outlines the foundational steps to set up an isolated PostgreSQL environment for the `retrofun` project.

## Prerequisites
- PostgreSQL installed and running.
- `psql` CLI tool available in your PATH.
- Superuser access (usually the `postgres` OS user).

## Step 1: Database and User Setup (As Superuser)

First, ensure you are connected as a superuser (like `postgres`), then run the following setup commands:

```sql
-- Create the database
postgres=# CREATE DATABASE retrofundb;
CREATE DATABASE

-- Connect to the new database
postgres=# \c retrofundb
You are now connected to database "retrofundb" as user "postgres".

-- Create the user (role with login privileges)
retrofundb=# CREATE ROLE retrofun WITH PASSWORD 'SuperSecret' LOGIN;
CREATE ROLE

-- Create the schema and set the user as the owner
retrofundb=# CREATE SCHEMA retrofun AUTHORIZATION retrofun;
CREATE SCHEMA
```

## Step 2: Switch Context to the New User

Instead of opening a new terminal and dealing with OS-level authentication prompts, we can seamlessly switch users within our current `psql` session using the `\c` command:

```sql
-- Switch to the retrofundb database, authenticating as the retrofun user
retrofundb=# \c retrofundb retrofun
Password for user retrofun: ********
You are now connected to database "retrofundb" as user "retrofun".
```

## Step 3: Verify the Setup

Now, let's create a table without explicitly specifying a schema:

```sql
retrofundb=> CREATE TABLE mytable (id integer);
CREATE TABLE

retrofundb=> DROP TABLE my_table ;
DROP TABLE
```

### Why did this work?
Even though we didn't specify `retrofun.mytable`, the table was successfully created inside the `retrofun` schema. This happens because PostgreSQL's default `search_path` is set to `"$user", public`. 

Because our current user is `retrofun`, the `"$user"` variable dynamically resolves to the `retrofun` schema. PostgreSQL looks there first, finds it, and creates the table inside it. The `AUTHORIZATION` clause we used earlier simply ensured that `retrofun` has full ownership and DDL privileges over that schema.

---

## 💡 CLI Pro-Tips & Python Integration

### Bypassing Password Prompts in Scripts
If you ever need to automate the connection via bash (e.g., in a deployment script), use the `PGPASSWORD` environment variable rather than plain text in the SQL:

```bash
PGPASSWORD='SuperSecret' psql -U retrofun -d retrofundb -h 127.0.0.1 -c "SELECT current_schema();"
```
*(Note: Using `-h 127.0.0.1` forces a TCP connection, which bypasses the `peer` OS-user authentication check and uses password auth instead).*

### Permanent Search Path
If you want to guarantee that `retrofun` never accidentally creates objects in the `public` schema, you can lock their `search_path` permanently at the role level:

```sql
ALTER ROLE retrofun IN DATABASE retrofundb SET search_path = retrofun;
```

### Connecting from Python (`uv` / `pyproject.toml`)
Since this is a Python project, you will likely connect using `psycopg` or `SQLAlchemy`. **Never hardcode the database password in your Python code.** 

Instead, create a `.env` file at the root of your project (and ensure it is in your `.gitignore`):

```env
# .env
DATABASE_URL="postgresql://retrofun:SuperSecret@127.0.0.1:5432/retrofundb"
```

You can then load this in your Python app using `python-dotenv` or `pydantic-settings` to establish your database connection securely.
