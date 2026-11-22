# RetroFun

A modern PostgreSQL + Python learning project demonstrating robust, production-grade database architecture.

> **Inspiration:** This project is heavily inspired by the teachings of [SQLAlchemy 2 In Practice](https://www.amazon.com/SQLAlchemy-Practice-program-relational-databases-ebook/dp/B0BVJRKS54), but modernized to leverage the latest, most efficient tools in the Python ecosystem.

## 🛠️ Modern Tech Stack

- **Python 3.13+**: Leveraging the latest language features and performance improvements.
- **`uv`**: Ultra-fast package management and project execution (replacing traditional `pip`/`venv`).
- **SQLAlchemy 2.0**: Strictly typed ORM using modern `Mapped[]` annotations and `select()` constructs.
- **Alembic**: Deterministic, schema-qualified migrations with custom autogenerate filtering to prevent noise.
- **`psycopg` 3**: Modern, high-performance PostgreSQL driver with built-in connection pooling.
- **`pydantic-settings`**: Type-safe, `.env`-driven configuration (zero hardcoded secrets).
- **`fastuuid7`**: Time-ordered, sortable UUIDv7 primary keys for optimal database indexing.
- **`ruff` + `mypy --strict`**: Uncompromising, automated code quality and type safety.

## 🚀 Quickstart

1. **Install dependencies** (requires [uv](https://docs.astral.sh/uv/)):

   ```bash
   uv sync
   ```

2. **Configure your environment**:
   Create a `.env` file at the root of the project (see [docs/postgres-setup.md](docs/postgres-setup.md) for details).

   ```env
   POSTGRES_USER=retrofun
   POSTGRES_PASSWORD=your_secure_password
   POSTGRES_HOST=127.0.0.1
   POSTGRES_PORT=5432
   POSTGRES_DB=retrofundb
   ```

3. **Verify database connection**:

   ```bash
   uv run python -m retrofun.db.db
   ```

4. **Apply database migrations**:

   ```bash
   uv run alembic upgrade head
   ```

5. **Seed the database** (optional):

   ```bash
   uv run python -m retrofun.import_products
   uv run python -m retrofun.import_orders
   uv run python -m retrofun.import_reviews
   ```

6. **Run the demo queries**:

   ```bash
   uv run retrofun
   ```

## 📚 Documentation

- [Database Setup & Search Path](docs/postgres-setup.md)
- [Domain Models & Architecture](docs/models.md)
- [Deferred Optimizations & Triggers](docs/deferred.md)

## 🧹 Maintenance

Keep the codebase pristine with the included Makefile targets:

```bash
make format      # Run ruff format and fix
make ci-check    # Run ruff check, mypy strict, and format verification
make demo        # Run the main query demonstration script
```
