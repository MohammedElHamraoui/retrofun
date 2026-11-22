# src/retrofun/seeders/import_orders.py
import csv
from decimal import Decimal

from sqlalchemy import select

from retrofun.models import Customer, Order, Product

# ✅ Import shared utilities
from retrofun.seeders.base import get_data_dir, get_db_session, parse_timestamp


def main() -> None:
    data_dir = get_data_dir()
    csv_path = data_dir / "orders.csv"

    # ✅ Clean session management
    with get_db_session() as session:
        # Pre-load Customers to avoid N+1 queries
        customers_by_name = {c.name: c for c in session.scalars(select(Customer)).all()}

        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row_num, row in enumerate(reader, start=2):
                customer_name = row["name"]
                customer = customers_by_name.get(customer_name)

                if not customer:
                    print(
                        f"⚠️ Warning: Row {row_num} - Customer '{customer_name}' "
                        "not found. Skipping."
                    )
                    continue

                # ✅ Clean timestamp parsing
                created_at = parse_timestamp(row["timestamp"])

                # 3. Accumulate items and total FIRST
                items_data = []
                total_amount = Decimal("0.00")

                for i in range(1, 4):
                    product_name = row.get(f"product{i}")
                    if not product_name or not product_name.strip():
                        continue

                    product = session.execute(
                        select(Product).filter_by(name=product_name)
                    ).scalar_one_or_none()

                    if not product:
                        print(f"Warning: Product '{product_name}' not found.")
                        continue

                    unit_price = Decimal(row[f"unit_price{i}"])
                    quantity = int(row[f"quantity{i}"])

                    total_amount += unit_price * quantity
                    items_data.append((product.id, unit_price, quantity))

                # 4. Create the Order with the final total in ONE INSERT
                order = Order(
                    customer_id=customer.id,
                    created_at=created_at,
                    total_amount=total_amount,
                )
                session.add(order)


if __name__ == "__main__":
    main()
