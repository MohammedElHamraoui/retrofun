import json
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Inherit from BaseEntity to get to_dict() without being forced to define an 'id'
from retrofun.db import BaseEntity

if TYPE_CHECKING:
    from retrofun.models import Order, Product


class OrderItem(BaseEntity):
    __tablename__ = "order_items"  # "order_items" is the standard naming convention

    # 1. Composite Primary Key (No surrogate 'id' needed)
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id"), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), primary_key=True)

    # 2. Use Decimal for currency to avoid floating-point math errors
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    # 3. Good practice: provide a default quantity
    quantity: Mapped[int] = mapped_column(default=1, server_default=text("1"))

    # 4. Don't forget the relationships to navigate the object graph!
    order: Mapped["Order"] = relationship(back_populates="order_items")
    product: Mapped["Product"] = relationship(back_populates="order_items")

    def __repr__(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)
