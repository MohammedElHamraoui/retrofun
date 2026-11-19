# src/retrofun/import_orders.py
import csv
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import select

from retrofun.db import SessionLocal
from retrofun.models import Customer, Order, OrderItem, Product


def seed_orders() -> None:
    data_dir = Path(__file__).parents[2] / "raw_data"

    with SessionLocal() as session, session.begin(), open(data_dir / "orders.csv") as f:
        reader = csv.DictReader(f)

        for row in reader:
            # 1. Handle the timestamp (make it UTC-aware)
            naive_dt = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
            created_at = naive_dt.replace(tzinfo=UTC)

            # 2. FIND OR CREATE the Customer
            stmt = select(Customer).filter_by(name=row["name"])
            customer = session.execute(stmt).scalar_one_or_none()

            if not customer:
                customer = Customer(
                    name=row["name"],
                    address=row["address"],
                    phone=row["phone"],
                )
                session.add(customer)
                session.flush()  # Forces the DB to generate the UUID and assign it to customer.id

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
            session.flush()  # Get order.id immediately

            # 5. Insert OrderItems
            for prod_id, unit_price, quantity in items_data:
                session.add(
                    OrderItem(
                        order_id=order.id,
                        product_id=prod_id,
                        unit_price=unit_price,
                        quantity=quantity,
                    )
                )


if __name__ == "__main__":
    seed_orders()
