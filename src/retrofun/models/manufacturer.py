from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from retrofun.models import RetroFunBase

if TYPE_CHECKING:
    from retrofun.models import Product


class Manufacturer(RetroFunBase):
    __tablename__ = "manufacturers"

    products: Mapped[list["Product"]] = relationship(back_populates="manufacturer")
