from sqlalchemy.orm import Mapped, WriteOnlyMapped, mapped_column, relationship

from retrofun.models import BlogArticle
from retrofun.models.base import NamedRetroFunBase


class Language(NamedRetroFunBase[int]):
    __tablename__ = "languages"

    id: Mapped[int] = mapped_column(primary_key=True)

    blog_articles: WriteOnlyMapped["BlogArticle"] = relationship(back_populates="language")
