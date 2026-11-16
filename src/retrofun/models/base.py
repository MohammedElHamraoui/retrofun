import json

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from retrofun.db import BaseEntity


class RetroFunBase(BaseEntity):  # BaseDomainModel
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), index=True, unique=True)

    def __repr__(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)
