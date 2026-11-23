# src/retrofun/seeders/import_reviews.py
import csv
import uuid

from sqlalchemy import select

from retrofun.models import Customer, Product, ProductReview
from retrofun.seeders.base import get_data_dir, get_db_session, parse_timestamp


def main() -> None:
    data_dir = get_data_dir()
    csv_path = data_dir / "reviews.csv"

    with get_db_session() as session:
        customers_by_name = {c.name: c for c in session.scalars(select(Customer)).all()}
        products_by_name = {p.name: p for p in session.scalars(select(Product)).all()}

        existing_reviews: set[tuple[int, uuid.UUID]] = {
            (pid, cid)
            for pid, cid in session.execute(
                select(ProductReview.product_id, ProductReview.customer_id)
            )
        }

        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row_num, row in enumerate(reader, start=2):
                customer_name = row["customer"]
                product_name = row["product"]

                c = customers_by_name.get(customer_name)
                p = products_by_name.get(product_name)

                if not c:
                    print(
                        f"⚠️ Warning: Row {row_num} - Customer '{customer_name}' "
                        f"not found. Skipping."
                    )
                    continue
                if not p:
                    print(
                        f"⚠️ Warning: Row {row_num} - Product '{product_name}' not found. Skipping."
                    )
                    continue

                rating = int(row["rating"])
                if not (1 <= rating <= 5):
                    print(f"⚠️ Warning: Row {row_num} has invalid rating {rating}. Skipping.")
                    continue

                if (p.id, c.id) in existing_reviews:
                    print(
                        f"⚠️ Warning: Row {row_num} - Duplicate review for '{p.name}' by "
                        f"'{c.name}'. Skipping."
                    )
                    continue

                created_at = parse_timestamp(row["timestamp"])
                comment = row["comment"].strip() if row.get("comment") else None

                r = ProductReview(
                    customer_id=c.id,
                    product_id=p.id,
                    created_at=created_at,
                    rating=rating,
                    comment=comment,
                )
                session.add(r)

                existing_reviews.add((p.id, c.id))


if __name__ == "__main__":
    main()
