from uuid import UUID

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from retrofun.db import BaseEntity


# PEP 695: Type parameters are declared in brackets.
# No need for `TypeVar` or `Generic` imports anymore.
class RetroFunBase[IDType: (int, UUID)](BaseEntity):
    """Base for all domain models. Provides JSON serialization."""

    __abstract__ = True

    # NOTE: Do NOT define `id` here. Let the concrete models define it.


class NamedRetroFunBase[IDType: (int, UUID)](RetroFunBase[IDType]):
    """Base for domain models that are uniquely identified by a name."""

    __abstract__ = True

    name: Mapped[str] = mapped_column(String(64), index=True, unique=True)
