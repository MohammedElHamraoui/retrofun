# src/retrofun/models/product.py

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from retrofun.models import RetroFunBase

if TYPE_CHECKING:
    from retrofun.models import Manufacturer


class Product(RetroFunBase):
    __tablename__ = "products"

    manufacturer_id: Mapped[int] = mapped_column(ForeignKey("manufacturers.id"), index=True)
    year: Mapped[int] = mapped_column(index=True)
    country: Mapped[str | None] = mapped_column(String(32))
    cpu: Mapped[str | None] = mapped_column(String(32))

    manufacturer: Mapped["Manufacturer"] = relationship(back_populates="products", lazy="joined")
