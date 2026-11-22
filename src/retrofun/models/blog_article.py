from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, WriteOnlyMapped, mapped_column, relationship

from retrofun.models.base import RetroFunBase

if TYPE_CHECKING:
    from retrofun.models import BlogAuthor, BlogView, Product


class BlogArticle(RetroFunBase[int]):
    __tablename__ = "blog_articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(128), index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("blog_authors.id"), index=True)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"), index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

    author: Mapped["BlogAuthor"] = relationship(back_populates="articles")
    product: Mapped["Product | None"] = relationship(back_populates="blog_articles")

    views: WriteOnlyMapped["BlogView"] = relationship(back_populates="article")
