import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from retrofun.models.base import RetroFunBase

if TYPE_CHECKING:
    from retrofun.models import BlogArticle, BlogSession


class BlogView(RetroFunBase[int]):
    __tablename__ = "blog_views"

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("blog_articles.id"))
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("blog_sessions.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )
    article: Mapped["BlogArticle"] = relationship(back_populates="views")
    session: Mapped["BlogSession"] = relationship(back_populates="views")
