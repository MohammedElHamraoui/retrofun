# src/retrofun/db.py
"""Connection smoke test: uv run python -m retrofun.db"""

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
        ).fetchone() # type: ignore
        print(f"database={db} user={user} schema={schema}")


if __name__ == "__main__":
    pool.open(wait=True)
    try:
        check()
    finally:
        pool.close()
