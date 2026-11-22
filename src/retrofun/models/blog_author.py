from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, WriteOnlyMapped, mapped_column, relationship

from retrofun.models.base import NamedRetroFunBase

if TYPE_CHECKING:
    from retrofun.models import BlogArticle


class BlogAuthor(NamedRetroFunBase[int]):
    __tablename__ = "blog_authors"

    id: Mapped[int] = mapped_column(primary_key=True)

    articles: WriteOnlyMapped["BlogArticle"] = relationship(back_populates="author")
