# src/retrofun/models/order.py
import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

import fastuuid7
from sqlalchemy import DateTime, ForeignKey, Numeric, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from retrofun.models.base import RetroFunBase

if TYPE_CHECKING:
    from retrofun.models import Customer, OrderItem


class Order(RetroFunBase[uuid.UUID]):
    __tablename__ = "orders"

    # Define the concrete UUID type here
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=fastuuid7.uuid7,
    )

    # An order doesn't have a name, but it has other specific attributes
    # Let the database handle the time.
    # PostgreSQL's RETURNING clause will fetch it back to Python automatically.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("customers.id"),
        index=True,
    )
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    customer: Mapped["Customer"] = relationship(back_populates="orders")
    order_items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )
