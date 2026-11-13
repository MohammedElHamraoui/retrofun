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
retrofundb=# CREATE ROLE retrofun WITH PASSWORD '*****' LOGIN;
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
retrofundb=> CREATE TABLE my_table (id integer);
CREATE TABLE

retrofundb=> DROP TABLE my_table ;
DROP TABLE
```

### Why did this work?
Even though we didn't specify `retrofun.my_table`, the table was successfully created inside the `retrofun` schema. This happens because PostgreSQL's default `search_path` is set to `"$user", public`. 

Because our current user is `retrofun`, the `"$user"` variable dynamically resolves to the `retrofun` schema. PostgreSQL looks there first, finds it, and creates the table inside it. The `AUTHORIZATION` clause we used earlier simply ensured that `retrofun` has full ownership and DDL privileges over that schema.

---

## 💡 CLI Pro-Tips & Python Integration

### Bypassing Password Prompts in Scripts
If you ever need to automate the connection via bash (e.g., in a deployment script), use the `PGPASSWORD` environment variable rather than plain text in the SQL:

```bash
PGPASSWORD='*****' psql -U retrofun -d retrofundb -h 127.0.0.1 -c "SELECT current_schema();"
```
*(Note: Using `-h 127.0.0.1` forces a TCP connection, which bypasses the `peer` OS-user authentication check and uses password auth instead).*

### Permanent Search Path
If you want to guarantee that `retrofun` never accidentally creates objects in the `public` schema, you can lock their `search_path` permanently at the role level:

```sql
ALTER ROLE retrofun IN DATABASE retrofundb SET search_path = retrofun;
```

## Connecting from Python (`uv` / `pyproject.toml`)
Since this is a Python project, you will likely connect using `psycopg` and `SQLAlchemy`. **Never hardcode the database password in your Python code.** 

A driver that is extremely popular and has proven to be very stable is `psycopg`, which you can install with this command:

```bash
uv add psycopg[binary,pool]
```
To connect to your database from Python you will later need to know the connection details:
   - **`Hostname`**: localhost (127.0.0.1)
   - **`Port`**: 5432
   - **`Database`**: retrofundb
   - **`Username`**: retrofun
   - **`Password`**: *****
   - **`Python driver`**: psycopg

When using SQLAlchemy, a database to connect to is represented by a URL that has the following structure:

```python
{dialect}{+driver}://{username}:{password}@{hostname}:{port}/{database}
```

Instead, create a `.env` file at the root of your project (and ensure it is in your `.gitignore`):

```env
# .env
DATABASE_URL="postgresql+psycopg://retrofun:*****@127.0.0.1:5432/retrofundb"
```

You can then load this in your Python app using `python-dotenv` or `pydantic-settings` to establish your database connection securely.

### python-dotenv

The `python-dotenv` package allows an application to read variables from a `.env` file. Install it with `uv`:

```bash
$ uv add python-dotenv
```

Below you can see an example of how to read the `DATABASE_URL` variable from a Python program. Copy this code to a file named `db.py` in the project directory to try it out on your computer.

Listing 1 `db.py`: Display the database URL

```python
# src/retrofun/database/db.py
import os
from dotenv import load_dotenv

load_dotenv()

print("Database URL:", os.environ["DATABASE_URL"])
```

Run this example to ensure that you have configured your database URL correctly:

```bash
$ uv run python -m retrofun.database.db
Database URL: postgresql+psycopg://retrofun:*****@127.0.0.1:5432/retrofundb
```
> **Note** `python-doten` is a learning step that's been superseded.
> 
### Pydantic Settings
To manage PostgreSQL configuration in Python using pydantic-settings, use `BaseSettings` paired with Pydantic's built-in `PostgresDsn` type. This automatically validates connection strings, parses individual URL components, and loads credentials safely from environment variables or a `.env` file.

#### 1. Direct DSN Configuration (Recommended for hosted platforms that inject a single URL)

If you supply a single connection URL (such as DATABASE_URL) in your environment or .env file, type the field as PostgresDsn. Pydantic accepts standard schemes like postgres://, postgresql://, and driver-specific schemes like postgresql+asyncpg:// or postgresql+psycopg://.

Listing 2 `config.settings.py`: Display the database URL

```python
# src/retrofun/config/settings.py
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Reads DATABASE_URL from the environment or .env file
    database_url: PostgresDsn

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

# Convert PostgresDsn back to a standard string for SQLAlchemy or Psycopg
db_url_str = str(settings.database_url)
print("Database URL:", db_url_str)
```
Run this example to ensure that you have configured your database URL correctly:

```bash
$ uv run python -m retrofun.config.settings
Database URL: postgresql+psycopg://retrofun:*****@127.0.0.1:5432/retrofundb
```

• **Automatic validation.** Pydantic raises a ValidationError at startup if the host is missing or the URL scheme is invalid.
• **Parsed attributes.** `PostgresDsn` is a multi-host URL type. Access `.scheme` and `.path` directly; access credentials via `settings.database_url.hosts()` — a list of dicts with `username`, `password`, `host`, `port`. Use `hosts()[0]` for a single-host DSN.

#### 2. Building the DSN from Individual Variables.

If your deployment provides separate environment variables (`POSTGRES_USER`, `POSTGRES_PASSWORD`, etc.) instead of a single URL, use a `@computed_field` with `PostgresDsn.build` to assemble them cleanly.

```python
# src/retrofun/config/settings.py
from urllib.parse import quote_plus

from pydantic import Field, PostgresDsn, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_user: str = "retrofun"
    postgres_password: SecretStr  # required — no default, fails fast if missing
    postgres_host: str = "127.0.0.1"  # force TCP, avoids the peer-auth trap
    postgres_port: int = Field(default=5432, ge=1, le=65535)
    postgres_db: str = "retrofundb"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @computed_field
    @property
    def database_url(self) -> PostgresDsn:
        """Canonical DSN — for raw psycopg / psycopg_pool."""
        pw = quote_plus(self.postgres_password.get_secret_value())
        return PostgresDsn.build(
            scheme="postgresql",
            username=self.postgres_user,
            password=pw,
            host=self.postgres_host,
            port=self.postgres_port,
            path=self.postgres_db,
        )

    @property
    def sqlalchemy_url(self) -> str:
        """Dialect-qualified URL — for SQLAlchemy's create_engine()."""
        return str(self.database_url).replace("postgresql://", "postgresql+psycopg://", 1)


settings = Settings()  # type: ignore

if __name__ == "__main__":
    u = settings.database_url
    h = u.hosts()[0]  # PostgresDsn is multi-host; credentials live per-host
    print(f"Database URL: {u.scheme}://{h['username']}:***@{h['host']}:{h['port']}{u.path}")
    print(
        f"SQLAlchemy URL: {u.scheme}+psycopg://{h['username']}:***@{h['host']}:{h['port']}{u.path}"
    )
```

Run this example to ensure that you have configured your database URL correctly:

```bash
$ uv run python -m retrofun.config.settings
Database URL: postgresql://retrofun:***@127.0.0.1:5432/retrofundb
SQLAlchemy URL: postgresql+psycopg://retrofun:***@127.0.0.1:5432/retrofundb
```

Key Setup Tips

• **Installation.** Install the separate settings package via `uv add pydantic-settings`, as `BaseSettings` is decoupled from core `pydantic` in Pydantic v2.
• **String conversion.** PostgresDsn is a Pydantic `Url` object rather than a plain str. Always wrap it in `str`(psycopg → `database_url`; SQLAlchemy → `sqlalchemy_url` ) before passing it to create_engine(), create_async_engine(), or psycopg.connect().
• **Driver compatibility.** If a hosting provider injects `postgres://` and your ORM requires `postgresql+psycopg://`, you can normalize it using a `@field_validator` or rebuild the URL using `PostgresDsn.build`.

For the **RetroFun Project** we use the Option 2 *Building the DSN from Individual Variables*

### Connection Pooling (`psycopg_pool`)

The `pool` extra in `uv add psycopg[binary,pool]` installs `psycopg_pool`, a connection pool for Psycopg 3. Opening a PostgreSQL connection is expensive — each one requires a TCP handshake, authentication, and a dedicated backend process on the server — so a pool opens a small set of connections once and reuses them, which becomes essential as soon as concurrent clients or API endpoints hit the database. In `retrofun.database.db`, the pool is built from `settings.database_url` with `min_size=1` and `max_size=5`, and created with `open=False` so that importing the module never touches the network. Calling `pool.open(wait=True)` establishes the initial connections in background workers — retrying with exponential backoff if the server is unreachable — and raises `PoolTimeout` if they are not ready within the timeout (30 seconds by default). The `with pool.connection() as conn` block then borrows a connection and, on exit, commits or rolls back any open transaction and returns the connection to the pool for reuse instead of closing it.

**Listing 3** `db.py`: Pooled connection smoke test

```python
# src/retrofun/database/db.py
"""Connection smoke test: uv run python -m retrofun.database.db"""

from psycopg_pool import ConnectionPool

from retrofun.config.settings import settings

pool = ConnectionPool(
    conninfo=str(settings.database_url),
    min_size=1,
    max_size=5,
    open=False,  # never connect at import time
)


def check() -> None:
    with pool.connection() as conn:
        db, user, schema = conn.execute(
            "SELECT current_database(), current_user, current_schema()"
        ).fetchone()  # type: ignore
        print(f"database={db} user={user} schema={schema}")


if __name__ == "__main__":
    pool.open(wait=True)
    try:
        check()
    finally:
        pool.close()
```

Run this example to verify the whole chain — settings, DSN, pool, and the role's `search_path`:

```bash
$ uv run python -m retrofun.database.db
database=retrofundb user=retrofun schema=retrofun
```

The `schema=retrofun` in the output confirms that this fresh login picked up the `ALTER ROLE ... IN DATABASE ... SET search_path` default.

> **Debugging note:** if `pool.open(wait=True)` raises `PoolTimeout`, the traceback is only a symptom — read the `error connecting in 'pool-1'` log lines above it, which carry the real server error (for example, a malformed database name in the DSN). During development you can fail faster with `ConnectionPool(..., timeout=5, kwargs={"connect_timeout": 3})`.
