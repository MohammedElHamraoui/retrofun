import uuid
from typing import TYPE_CHECKING

import fastuuid7
from sqlalchemy import String, Uuid
from sqlalchemy.orm import Mapped, WriteOnlyMapped, mapped_column, relationship

from retrofun.models import NamedRetroFunBase

if TYPE_CHECKING:
    from retrofun.models import BlogUser, Order, ProductReview


class Customer(NamedRetroFunBase[uuid.UUID]):
    __tablename__ = "customers"

    # Define the concrete UUID type here
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=fastuuid7.uuid7,
    )

    # ... other fields ...
    address: Mapped[str | None] = mapped_column(String(128))
    phone: Mapped[str | None] = mapped_column(String(32))

    # orders: Mapped[list(order)]
    orders: WriteOnlyMapped["Order"] = relationship(back_populates="customer")

    product_reviews: WriteOnlyMapped["ProductReview"] = relationship(back_populates="customer")

    blog_users: WriteOnlyMapped["BlogUser"] = relationship(back_populates="customer")
