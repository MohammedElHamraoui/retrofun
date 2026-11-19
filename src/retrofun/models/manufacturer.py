from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from retrofun.models import NamedRetroFunBase

if TYPE_CHECKING:
    from retrofun.models import Product


class Manufacturer(NamedRetroFunBase[int]):
    __tablename__ = "manufacturers"

    # Define the concrete ID type here
    id: Mapped[int] = mapped_column(primary_key=True)

    products: Mapped[list["Product"]] = relationship(back_populates="manufacturer")
