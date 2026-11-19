# src/retrofun/models/product_review.py
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from retrofun.db.base import BaseEntity

if TYPE_CHECKING:
    from retrofun.models import Customer, Product


class ProductReview(BaseEntity):
    __tablename__ = "product_reviews"  # ✅ Standardized naming

    # ✅ Enforce rating bounds at the database level
    __table_args__ = (CheckConstraint("rating >= 1 AND rating <= 5", name="rating_range"),)

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        primary_key=True,
    )

    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("customers.id"),
        primary_key=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

    # ✅ Explicit mapped_column to support table_args constraints
    rating: Mapped[int] = mapped_column()

    comment: Mapped[str | None] = mapped_column(Text)

    product: Mapped["Product"] = relationship(back_populates="reviews")
    customer: Mapped["Customer"] = relationship(back_populates="product_reviews")
