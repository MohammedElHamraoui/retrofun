# Deferred Optimizations & Architectural Posture

> **Core Posture:** Sync everywhere, `def` endpoints, threadpool absorbs the load. Migrate to async only when a profiler tells you to.

This document tracks conscious architectural deferrals. We are intentionally choosing simplicity to maximize our "uncertainty budget" for product validation. These items are not forgotten; they are waiting for explicit, measurable triggers.

## 🟢 What We Are NOT Deferring (The Non-Negotiables)

*These are the minimum viable safeguards required before real users touch the system.*

- **Schema Migrations:** Alembic + `alembic check` in CI. (Already implemented).
- **Data Durability:** Nightly `pg_dump` via cron or managed backups.
- **Error Visibility:** FastAPI default exception handlers + basic log file.
- **Basic Auth:** A simple bearer token or basic user table. Customer data is never world-readable.

---

## 🟡 Deferred Optimizations (Waiting for Triggers)

### 1. Async SQLAlchemy (`asyncpg` / `AsyncSession`)

- **Current State:** Synchronous `SessionLocal` with `def` FastAPI endpoints.
- **Why Deferred:** Premature async adds massive cognitive overhead and ecosystem friction for a CRUD PoC. The threadpool (~40 concurrent threads) is more than enough for current scale.
- **Trigger to Un-punt:**
  1. App log shows p95 latency > 200ms *and*
  2. Threadpool utilization consistently > 70%.

### 2. Caching Layer (Redis)

- **Current State:** Direct database queries.
- **Why Deferred:** Caching introduces cache-invalidation bugs and infrastructure complexity.
- **Trigger to Un-punt:** `pg_stat_statements` shows the exact same heavy query profile appearing in > 50% of requests.

### 3. Background Task Queue (Celery / arq / taskiq)

- **Current State:** Synchronous request/response cycle.
- **Why Deferred:** Adds a message broker dependency and operational complexity.
- **Trigger to Un-punt:** The first user-facing operation (e.g., report generation, bulk import) takes > 2 seconds to complete.

### 4. Upgrade to Python 3.14

- **Current State:** Python 3.13.
- **Why Deferred:** The 5–15% speedup is marginal for a PoC. Python 3.14 still has sharp edges with AI/ML dependencies (`numpy`/`LangChain`/`torch` version conflicts and missing wheels).
- **Trigger to Un-punt:**
  1. Target AI libraries officially list 3.14 in their `requires-python` metadata, **and**
  2. A fresh `uv sync` resolves all AI dependencies without `numpy`/`torch` conflicts.

### 5. Infrastructure Scaling (Kubernetes / Read Replicas)

- **Current State:** Single PostgreSQL instance, standard deployment.
- **Why Deferred:** Over-engineering for a PoC with zero users.
- **Trigger to Un-punt:**
  1. We have > 3 distinct microservices, **or**
  2. Write operations exceed 1,000/s, **or**
  3. A customer on a different continent complains about latency.

---

## 🧠 The Decision Framework

When proposing a new architectural addition, ask:

1. **Is it reversible?** If yes, we can probably defer it.
2. **Does it solve a problem we have *today*, or a problem we *imagine* we will have?** If it's the latter, defer it.
3. **Does it steal hours from fixing actual bugs or watching real users?** If yes, defer it.
