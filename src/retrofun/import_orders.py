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
            # Check if a customer with this name already exists
            stmt = select(Customer).filter_by(name=row["name"])
            customer = session.execute(stmt).scalar_one_or_none()

            if not customer:
                customer = Customer(name=row["name"], address=row["address"], phone=row["phone"])
                session.add(customer)
                session.flush()  # Forces the DB to generate the UUID and assign it to customer.id

            # 3. Create the Order using the existing or newly created customer.id
            order = Order(
                customer_id=customer.id,
                created_at=created_at,
                total_amount=Decimal("0.00"),
            )
            session.add(order)
            session.flush()  # Get order.id immediately

            total_amount = Decimal("0.00")

            # 4. Create OrderItems for up to 3 products
            for i in range(1, 4):
                product_name = row.get(f"product{i}")
                if not product_name or product_name.strip() == "":
                    continue

                product = session.execute(
                    select(Product).filter_by(name=product_name)
                ).scalar_one_or_none()

                if not product:
                    print(f"Warning: Product '{product_name}' not found.")
                    continue

                unit_price = Decimal(row[f"unit_price{i}"])
                quantity = int(row[f"quantity{i}"])

                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    unit_price=unit_price,
                    quantity=quantity,
                )
                session.add(order_item)
                total_amount += unit_price * quantity

            # 5. Update the Order's total amount
            order.total_amount = total_amount


if __name__ == "__main__":
    seed_orders()
