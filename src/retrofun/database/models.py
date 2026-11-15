# src/retrofun/database/models.py

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from retrofun.database.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    manufacturer: Mapped[str] = mapped_column(String(64), index=True)
    year: Mapped[int] = mapped_column(index=True)
    country: Mapped[str | None] = mapped_column(String(32))
    cpu: Mapped[str | None] = mapped_column(String(32))

    def __repr__(self) -> str:
        return f"Product({self.id}, {self.name})"
