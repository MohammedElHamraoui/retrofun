# src/retrofun/import_reviews.py
import csv
import uuid
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select

from retrofun.db import SessionLocal
from retrofun.models import Customer, Product, ProductReview


def main() -> None:
    data_dir = Path(__file__).parents[2] / "raw_data"

    with SessionLocal() as session, session.begin():
        # 1. Pre-load all Customers and Products into dictionaries to avoid N+1 queries
        customers_by_name = {c.name: c for c in session.scalars(select(Customer)).all()}
        products_by_name = {p.name: p for p in session.scalars(select(Product)).all()}

        # 2. Fetch existing reviews to prevent IntegrityError on the composite PK
        existing_reviews: set[tuple[int, uuid.UUID]] = set(
            session.execute(select(ProductReview.product_id, ProductReview.customer_id)).all()
        )

        # 3. Process the CSV
        with open(data_dir / "reviews.csv") as f:
            reader = csv.DictReader(f)
            for row in reader:
                customer_name = row["customer"]
                product_name = row["product"]

                c = customers_by_name.get(customer_name)
                p = products_by_name.get(product_name)

                # Validate that both the customer and product exist
                if not c:
                    print(f"⚠️ Warning: Customer '{customer_name}' not found. Skipping.")
                    continue
                if not p:
                    print(f"⚠️ Warning: Product '{product_name}' not found. Skipping.")
                    continue

                # Validate against the composite PK constraint (1 review per customer per product)
                if (p.id, c.id) in existing_reviews:
                    print(
                        f"⚠️ Warning: Duplicate review for '{product_name}' by "
                        "'{customer_name}'. Skipping."
                    )
                    continue

                # Parse the timestamp (make it UTC-aware)
                naive_dt = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
                created_at = naive_dt.replace(tzinfo=UTC)

                # Create and add the review
                r = ProductReview(
                    customer_id=c.id,
                    product_id=p.id,
                    created_at=created_at,
                    rating=int(row["rating"]),
                    comment=row["comment"] or None,
                )
                session.add(r)

                # Track it in memory so we don't accidentally add a duplicate later in the CSV
                existing_reviews.add((p.id, c.id))


if __name__ == "__main__":
    main()
