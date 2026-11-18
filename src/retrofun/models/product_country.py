from sqlalchemy import Column, ForeignKey, Table

from retrofun.db import Base

ProductCountry = Table(
    "products_countries",
    Base.metadata,
    Column("product_id", ForeignKey("products.id"), primary_key=True, nullable=False),
    Column("country_id", ForeignKey("countries.id"), primary_key=True, nullable=False),
)
