import uuid
from typing import TYPE_CHECKING

import fastuuid7
from sqlalchemy import ForeignKey, Uuid
from sqlalchemy.orm import Mapped, WriteOnlyMapped, mapped_column, relationship

from retrofun.models.base import RetroFunBase
from retrofun.models.blog_view import BlogView

if TYPE_CHECKING:
    from retrofun.models import BlogUser


class BlogSession(RetroFunBase[uuid.UUID]):
    __tablename__ = "blog_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=fastuuid7.uuid7,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("blog_users.id"), index=True)

    user: Mapped["BlogUser"] = relationship(back_populates="sessions")

    views: WriteOnlyMapped["BlogView"] = relationship(back_populates="session")
