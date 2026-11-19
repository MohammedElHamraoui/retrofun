# Models

## Architecture Summary

This document defines the domain model for the RetroFun project. It follows a **code-first SQLAlchemy 2.0** architecture where Python classes are the single source of truth, and the PostgreSQL schema is a derived artifact managed via Alembic.

### Core Principles

- **Layered Bases:** Infrastructure (`retrofun.db`) provides the declarative machinery, metadata configuration, and serialization (`to_dict`); Domain (`retrofun.models`) defines the business entities.
- **Generic Identity:** The base hierarchy (`RetroFunBase`, `NamedRetroFunBase`) uses PEP 695 type parameters (`[IDType: (int, UUID)]`) to support both `int` and `UUID` primary keys without boilerplate.
- **Deterministic Schema:** All DDL is qualified to the `retrofun` schema with deterministic constraint naming (`pk_`, `fk_`, `ix_`) to ensure stable Alembic autogeneration.

### Current Entities & Relationships

- `Manufacturer` (1) ── (0..*) `Product`: One-to-many relationship.
- `Product` (*) ── (*) `Country`: Many-to-many relationship via the `products_countries` association table.
- `Customer` (1) ── (0..*) `Order`: One-to-many relationship.
- `Order` (1) ── (1..*) `OrderItem`: One-to-many relationship (composition).
- `Product` (1) ── (0..*) `OrderItem`: One-to-many relationship.

The ORM models are the **source of truth** for the database schema. PostgreSQL is a derived artifact: `Base.metadata.create_all()` emits DDL from these classes, and Alembic compares migrations against `Base.metadata`.

```text
Python class → Table object → CREATE TABLE DDL → PostgreSQL
```

Never edit the database by hand and expect the models to follow.

## Class diagram

```mermaid
classDiagram
    direction TB

    class DeclarativeBase {
        <<SQLAlchemy>>
    }
    class Base {
        <<declarative>>
        +MetaData metadata
    }
    class BaseEntity {
        <<abstract>>
        +to_dict() dict
    }
    class RetroFunBase {
        <<abstract>>
        +IDType id
    }
    class NamedRetroFunBase {
        <<abstract>>
        +str name
    }
    class Manufacturer {
        <<entity>>
    }
    class Country {
        <<entity>>
    }
    class Customer {
        <<entity>>
        +UUID id
        +str? address
        +str? phone
    }
    class Product {
        <<entity>>
        +int manufacturer_id
        +int year
        +str? cpu
    }
    class Order {
        <<entity>>
        +UUID id
        +datetime created_at
        +UUID customer_id
        +Decimal total_amount
    }
    class OrderItem {
        <<entity>>
        +UUID order_id
        +int product_id
        +Decimal unit_price
        +int quantity
    }
    class products_countries {
        <<association>>
        +int product_id
        +int country_id
    }

    DeclarativeBase <|-- Base
    Base <|-- BaseEntity
    BaseEntity <|-- RetroFunBase
    RetroFunBase <|-- NamedRetroFunBase
    NamedRetroFunBase <|-- Manufacturer
    NamedRetroFunBase <|-- Country
    NamedRetroFunBase <|-- Customer
    RetroFunBase <|-- Product
    RetroFunBase <|-- Order
    BaseEntity <|-- OrderItem
    Manufacturer "1" --> "0..*" Product : products
    Product "0..*" --> "*" products_countries
    Country "0..*" --> "*" products_countries
    Customer "1" --> "0..*" Order : orders
    Order "1" *-- "1..*" OrderItem : order_items
    Product "1" --> "0..*" OrderItem : order_items

    class ProductReview {
        <<entity>>
        +int product_id
        +UUID customer_id
        +datetime created_at
        +int rating
        +str? comment
    }
    Product "1" --> "0..*" ProductReview : reviews
    Customer "1" --> "0..*" ProductReview : product_reviews
```

`?` marks a nullable column. Inherited members are not repeated on subclasses. `*--` denotes composition (OrderItem is owned by Order).

## Layer responsibilities

| Layer | Module | Responsibility |
| --- | --- | --- |
| `DeclarativeBase` | SQLAlchemy | Provides the declarative machinery |
| `Base` | `retrofun.db.base` | Owns `MetaData`: schema + constraint naming convention |
| `BaseEntity` | `retrofun.db.base` | Abstract. **Serializable Base**. Provides `to_dict()` and `__repr__` for all models (including `OrderItem` which lacks a standard PK). |
| `RetroFunBase[IDType]` | `retrofun.models.base` | Abstract. Generic domain base with `id: Mapped[IDType]`, JSON `__repr__` |
| `NamedRetroFunBase[IDType]` | `retrofun.models.base` | Abstract. Adds `name: Mapped[str]` with unique index |
| `Manufacturer` | `retrofun.models.manufacturer` | Concrete entity → `retrofun.manufacturers` |
| `Country` | `retrofun.models.country` | Concrete entity → `retrofun.countries` |
| `Customer` | `retrofun.models.customer` | Concrete entity → `retrofun.customers` (UUID PK) |
| `Product` | `retrofun.models.product` | Concrete entity → `retrofun.products` |
| `Order` | `retrofun.models.order` | Concrete entity → `retrofun.orders` (UUID PK) |
| `OrderItem` | `retrofun.models.orderitem` | Concrete entity → `retrofun.order_items` (composite PK, no `id`) |
| `products_countries` | `retrofun.models.product_country` | Association table for Product ↔ Country M2M |
| `ProductReview` | `retrofun.models.product_review` | Concrete entity → `retrofun.product_reviews` (composite PK, inherits `BaseEntity`) |

## Entities

### Product

Table `retrofun.products` · seeded from `raw_data/products.csv` (149 rows).

| Column | Python annotation | PostgreSQL | Nullable | Index / constraint |
| --- | --- | --- | --- | --- |
| `id` | `Mapped[int]` | `integer` | no | PK `pk_products`, sequence `products_id_seq` |
| `name` | `Mapped[str]` | `varchar(64)` | no | **UNIQUE** index `ix_retrofun_products_name` |
| `manufacturer_id` | `Mapped[int]` | `integer` | no | FK → `manufacturers(id)`, index `ix_retrofun_products_manufacturer_id` |
| `year` | `Mapped[int]` | `integer` | no | index `ix_retrofun_products_year` |
| `cpu` | `Mapped[str \| None]` | `varchar(32)` | yes | — |

*Note: `country` was removed during normalization. See `products_countries` below.*

### Manufacturer

Table `retrofun.manufacturers`.

| Column | Python annotation | PostgreSQL | Nullable | Index / constraint |
| --- | --- | --- | --- | --- |
| `id` | `Mapped[int]` | `integer` | no | PK `pk_manufacturers`, sequence `manufacturers_id_seq` |
| `name` | `Mapped[str]` | `varchar(64)` | no | **UNIQUE** index `ix_retrofun_manufacturers_name` |

Manufacturer names were previously duplicated across every product row. Extracting them removes that redundancy and makes a rename a single-row update.

### Country

Table `retrofun.countries`.

| Column | Python annotation | PostgreSQL | Nullable | Index / constraint |
| --- | --- | --- | --- | --- |
| `id` | `Mapped[int]` | `integer` | no | PK `pk_countries`, sequence `countries_id_seq` |
| `name` | `Mapped[str]` | `varchar(64)` | no | **UNIQUE** index `ix_retrofun_countries_name` |

Countries are extracted from the CSV's `country` column (split by `/` for joint production).

### Customer

Table `retrofun.customers`.

| Column | Python annotation | PostgreSQL | Nullable | Index / constraint |
| --- | --- | --- | --- | --- |
| `id` | `Mapped[uuid.UUID]` | `uuid` | no | PK `pk_customers` |
| `name` | `Mapped[str]` | `varchar(64)` | no | **UNIQUE** index `ix_retrofun_customers_name` |
| `address` | `Mapped[str \| None]` | `varchar(128)` | yes | — |
| `phone` | `Mapped[str \| None]` | `varchar(32)` | yes | — |

Uses `uuid.uuid7` (time-ordered UUID) for primary key, generated on the Python side via `fastuuid7`.

### Order

Table `retrofun.orders`.

| Column | Python annotation | PostgreSQL | Nullable | Index / constraint |
| --- | --- | --- | --- | --- |
| `id` | `Mapped[uuid.UUID]` | `uuid` | no | PK `pk_orders` |
| `created_at` | `Mapped[datetime]` | `timestamptz` | no | index `ix_retrofun_orders_created_at`, `server_default=func.now()` |
| `customer_id` | `Mapped[uuid.UUID]` | `uuid` | no | FK → `customers(id)`, index `ix_retrofun_orders_customer_id` |
| `total_amount` | `Mapped[Decimal]` | `numeric(10, 2)` | no | — |

Uses `uuid.uuid7` for primary key. `created_at` is generated by the database server to avoid clock skew.

### OrderItem

Table `retrofun.order_items`. Uses a **composite primary key** — no surrogate `id` column.

| Column | Python annotation | PostgreSQL | Nullable | Index / constraint |
| --- | --- | --- | --- | --- |
| `order_id` | `Mapped[uuid.UUID]` | `uuid` | no | PK, FK → `orders(id)` |
| `product_id` | `Mapped[int]` | `integer` | no | PK, FK → `products(id)` |
| `unit_price` | `Mapped[Decimal]` | `numeric(10, 2)` | no | — |
| `quantity` | `Mapped[int]` | `integer` | no | `server_default=1` |

Composite Primary Key: `pk_order_items` (`order_id`, `product_id`). Inherits from `BaseEntity` (not `RetroFunBase`) because it has no single `id` column.

### products_countries (Association Table)

Table `retrofun.products_countries`. Implements the Many-to-Many relationship between `Product` and `Country`.

| Column | Python annotation | PostgreSQL | Nullable | Index / constraint |
| --- | --- | --- | --- | --- |
| `product_id` | `Mapped[int]` | `integer` | no | PK, FK → `products(id)` |
| `country_id` | `Mapped[int]` | `integer` | no | PK, FK → `countries(id)` |

Composite Primary Key: `pk_products_countries` (`product_id`, `country_id`).

### ProductReview

Table `retrofun.product_reviews`. Composite PK `(product_id, customer_id)` — a
customer reviews a product **at most once**. Inherits `BaseEntity` (no surrogate `id`).

| Column | Python annotation | PostgreSQL | Nullable | Index / constraint |
| --- | --- | --- | --- | --- |
| `product_id` | `Mapped[int]` | `integer` | no | PK, FK → `products(id)` |
| `customer_id` | `Mapped[uuid.UUID]` | `uuid` | no | PK, FK → `customers(id)` |
| `created_at` | `Mapped[datetime]` | `timestamptz` | no | index, `server_default=now()` |
| `rating` | `Mapped[int]` | `integer` | no | `ck_product_reviews_rating_range` (1–5) |
| `comment` | `Mapped[str \| None]` | `text` | yes | — |

## Relationships

### One-to-Many: Manufacturer ↔ Product

`Manufacturer` 1 ── 0..* `Product`

- FK: `fk_products_manufacturer_id_manufacturers`
- `ON DELETE` is **not specified** → PostgreSQL default `NO ACTION`. Deleting a manufacturer that still has products raises `IntegrityError`. This is aggregation, not composition: products are not owned by their manufacturer.

### Many-to-Many: Product ↔ Country

`Product` *──* `Country` via `products_countries`

- Implemented using `secondary=ProductCountry` in the `relationship()` definition.
- `back_populates` is set on both sides (`Product.countries` and `Country.products`).
- `ON DELETE` is **not specified** → default `NO ACTION`.

### One-to-Many: Customer ↔ Order

`Customer` 1 ── 0..* `Order`

- FK: `fk_orders_customer_id_customers`
- `Customer.orders` uses `WriteOnlyMapped` to prevent accidental lazy-loading of large order lists.
- `ON DELETE` is **not specified** → default `NO ACTION`.

### Composition: Order ↔ OrderItem

`Order` 1 ── 1..* `OrderItem` (composition — OrderItems are owned by their Order)

- FK: `fk_order_items_order_id_orders`
- `ON DELETE` is **not specified** → default `NO ACTION`. Consider `ON DELETE CASCADE` if OrderItems should be deleted when their Order is deleted.
- `OrderItem` inherits from `BaseEntity` (not `RetroFunBase`) because it has no single `id` column — it uses a composite PK.

### One-to-Many: Product ↔ OrderItem

`Product` 1 ── 0..* `OrderItem`

- FK: `fk_order_items_product_id_products`
- `ON DELETE` is **not specified** → default `NO ACTION`.

## Conventions

**Schema.** `Base.metadata` is built with `schema=settings.postgres_schema` (default `retrofun`), so DDL is schema-qualified (`CREATE TABLE retrofun.products`) regardless of the connecting role's `search_path`. `settings.version_table_schema` ensures Alembic's `alembic_version` table also lands in the `retrofun` schema.

**Constraint names.** Deterministic names keep Alembic autogenerate stable:

| Key | Pattern | Example |
| --- | --- | --- |
| `ix` | `ix_%(column_0_label)s` | `ix_retrofun_products_name` |
| `uq` | `uq_%(table_name)s_%(column_0_name)s` | `uq_products_name` |
| `ck` | `ck_%(table_name)s_%(constraint_name)s` | `ck_product_reviews_rating_range` |
| `fk` | `fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s` | `fk_products_manufacturer_id_manufacturers` |
| `pk` | `pk_%(table_name)s` | `pk_products` |

## Session semantics

`SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)`.

- Objects stay readable **after** the session closes — no `DetachedInstanceError` when returning them from a function or serializing to JSON.
- No refresh `SELECT` after every commit.
- Trade-off: columns populated by `server_default` are **not** loaded after commit; call `session.refresh(obj)` when you need them.
- Relationship lazy-loads still fail on detached instances — eager-load inside the session.

`BaseEntity.to_dict()` returns `dict[str, Any]`, normalizing `UUID` and `datetime` to strings. On a transient instance (before flush) `id` is `None`:

```python
c64 = Product(name="Commodore 64", manufacturer_id=1)
c64.to_dict()  # {'id': None, 'name': 'Commodore 64', ..., 'year': None, ...}
```

SQLAlchemy does not enforce NOT NULL at construction — only at flush.

## Data Type Guidance

### 🔀 `default=` vs `server_default=` — not the same thing

| Keyword | Where applied | Persists in migration? | Fires on ORM INSERT? | Fires on raw INSERT? |
| --- | --- | --- | --- | --- |
| `default=` | Python-side, SQLAlchemy ORM | ❌ No | ✅ Yes | ❌ No |
| `server_default=` | DB-side, DDL `DEFAULT` | ✅ Yes | ✅ Yes (via DB) | ✅ Yes |
| `onupdate=` | Python-side, SQLAlchemy ORM | ❌ No | ✅ Yes | ❌ No |

If your model has `default=X` but your migration has `server_default=X`, **`alembic check` reports drift** and CI's `migrate-check` job fails. If you need both ORM-side and DB-side behavior, use both keywords — they compose.

**Example: Timestamps**
For `created_at` fields, prefer `server_default=func.now()`. This ensures the timestamp is set by the database server (avoiding clock skew) and is available even if rows are inserted via raw SQL or external tools.

**Example: UUIDs**
For UUID primary keys, prefer Python-side `default=uuid.uuid7` (time-ordered). PostgreSQL's `RETURNING` clause automatically fetches the generated value back to Python after INSERT, so no extra round-trip is needed.

## Regenerate and verify

`pyreverse` ships with pylint (dev dependency):

```bash
uv run pyreverse -o mmd -p retrofun src/retrofun
```

Writes `classes_retrofun.mmd` and `packages_retrofun.mmd`. Compare against the hand-maintained diagram above and keep whichever stays accurate.

```bash
uv run alembic upgrade head   # Apply migrations
uv run python -m retrofun.import_products   # Load CSV data
uv run python -m retrofun.main              # Query playground
```

```sql
\d+ retrofun.products
\d+ retrofun.manufacturers
\d+ retrofun.countries
\d+ retrofun.products_countries
\d+ retrofun.customers
\d+ retrofun.orders
\d+ retrofun.order_items
\d+ retrofun.product_reviews

SELECT conname, contype FROM pg_constraint
WHERE conrelid = 'retrofun.products'::regclass;

SELECT count(*) FROM retrofun.products;       -- expect 149
SELECT count(*) FROM retrofun.manufacturers;
SELECT count(*) FROM retrofun.countries;
SELECT count(*) FROM retrofun.products_countries;
SELECT count(*) FROM retrofun.customers;
SELECT count(*) FROM retrofun.orders;
SELECT count(*) FROM retrofun.order_items;
SELECT count(*) FROM retrofun.product_reviews;
SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint
WHERE conrelid = 'retrofun.product_reviews'::regclass AND contype = 'c';
```

The diagram is the *design*; the database is the *reality*. Compare when they might have drifted.

## Open items

- Consider `ON DELETE CASCADE` for `Order → OrderItem` if OrderItems should be deleted when their Order is deleted (currently `NO ACTION`). *Resolved: Order → OrderItem uses cascade='all, delete-orphan' to enforce strict composition*
