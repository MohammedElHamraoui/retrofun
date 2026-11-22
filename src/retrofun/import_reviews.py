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
        # Pre-load Customers and Products to avoid N+1 queries
        customers_by_name = {c.name: c for c in session.scalars(select(Customer)).all()}
        products_by_name = {p.name: p for p in session.scalars(select(Product)).all()}

        # Fetch existing reviews to prevent IntegrityError on the composite PK
        existing_reviews: set[tuple[int, uuid.UUID]] = {
            (pid, cid)
            for pid, cid in session.execute(
                select(ProductReview.product_id, ProductReview.customer_id)
            )
        }

        # Process the CSV
        with open(data_dir / "reviews.csv", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            # ✅ FIX: Use enumerate to define row_num
            for row_num, row in enumerate(reader, start=2):
                customer_name = row["customer"]
                product_name = row["product"]

                c = customers_by_name.get(customer_name)
                p = products_by_name.get(product_name)

                if not c:
                    print(
                        f"⚠️ Warning: Row {row_num} - Customer '{customer_name}' "
                        "not found. Skipping."
                    )
                    continue
                if not p:
                    print(
                        f"⚠️ Warning: Row {row_num} - Product '{product_name}' not found. Skipping."
                    )
                    continue

                # Validate rating
                rating = int(row["rating"])
                if not (1 <= rating <= 5):
                    print(f"⚠️ Warning: Row {row_num} has invalid rating {rating}. Skipping.")
                    continue

                # Validate against composite PK
                if (p.id, c.id) in existing_reviews:
                    print(
                        f"⚠️ Warning: Row {row_num} - Duplicate review for '{p.name}' by "
                        "'{c.name}'. Skipping."
                    )
                    continue

                # Parse timestamp
                naive_dt = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
                created_at = naive_dt.replace(tzinfo=UTC)

                # Create and add the review
                r = ProductReview(
                    customer_id=c.id,
                    product_id=p.id,
                    created_at=created_at,
                    rating=rating,
                    comment=row["comment"] or None,
                )
                session.add(r)

                # Track in memory
                existing_reviews.add((p.id, c.id))


if __name__ == "__main__":
    main()
