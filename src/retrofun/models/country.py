from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from retrofun.models import NamedRetroFunBase
from retrofun.models.product_country import ProductCountry

if TYPE_CHECKING:
    from retrofun.models import Product


class Country(NamedRetroFunBase[int]):
    __tablename__ = "countries"

    # Define the concrete ID type here
    id: Mapped[int] = mapped_column(primary_key=True)

    products: Mapped[list["Product"]] = relationship(
        secondary=ProductCountry, back_populates="countries"
    )
