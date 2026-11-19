# src/retrofun/models/product.py

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, WriteOnlyMapped, mapped_column, relationship

from retrofun.models.base import NamedRetroFunBase
from retrofun.models.product_country import ProductCountry

if TYPE_CHECKING:
    from retrofun.models import Country, Manufacturer, OrderItem, ProductReview


class Product(NamedRetroFunBase[int]):
    __tablename__ = "products"

    # Define the concrete ID type here
    id: Mapped[int] = mapped_column(primary_key=True)

    manufacturer_id: Mapped[int] = mapped_column(ForeignKey("manufacturers.id"), index=True)
    year: Mapped[int] = mapped_column(index=True)
    cpu: Mapped[str | None] = mapped_column(String(32))

    manufacturer: Mapped["Manufacturer"] = relationship(back_populates="products", lazy="joined")
    countries: Mapped[list["Country"]] = relationship(
        secondary=ProductCountry, back_populates="products"
    )

    order_items: WriteOnlyMapped["OrderItem"] = relationship(back_populates="product")

    reviews: WriteOnlyMapped["ProductReview"] = relationship(back_populates="product")
