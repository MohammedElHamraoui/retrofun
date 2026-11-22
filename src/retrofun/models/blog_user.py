import uuid
from typing import TYPE_CHECKING

import fastuuid7
from sqlalchemy import ForeignKey, Uuid
from sqlalchemy.orm import Mapped, WriteOnlyMapped, mapped_column, relationship

from retrofun.models.base import RetroFunBase

if TYPE_CHECKING:
    from retrofun.models import BlogSession, Customer


class BlogUser(RetroFunBase[uuid.UUID]):
    __tablename__ = "blog_users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=fastuuid7.uuid7,
    )
    customer_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("customers.id"), index=True)

    customer: Mapped["Customer | None"] = relationship(back_populates="blog_users")
    sessions: WriteOnlyMapped["BlogSession"] = relationship(back_populates="user")
