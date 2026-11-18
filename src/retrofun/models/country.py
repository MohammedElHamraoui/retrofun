from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from retrofun.models import RetroFunBase
from retrofun.models.product_country import ProductCountry

if TYPE_CHECKING:
    from retrofun.models import Product


class Country(RetroFunBase):
    __tablename__ = "countries"

    products: Mapped[list["Product"]] = relationship(
        secondary=ProductCountry, back_populates="countries"
    )
