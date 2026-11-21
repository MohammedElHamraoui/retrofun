# src/retrofun/db/base.py
import json
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from retrofun.config.settings import settings


class Base(DeclarativeBase):
    metadata = MetaData(
        schema=settings.postgres_schema,
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        },
    )


class BaseEntity(Base):
    __abstract__ = True

    def to_dict(self) -> dict[str, Any]:
        """Converts any inherited SQLAlchemy model instance into a clean dictionary."""
        result: dict[str, Any] = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, UUID):
                value = str(value)
            elif isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, Decimal):
                value = str(value)  # ✅ Changed from float(value) to str(value)
            result[column.name] = value
        return result

    def __repr__(self) -> str:
        # return json.dumps(self.to_dict(), ensure_ascii=False)
        # Concise representation for console output
        class_name = self.__class__.__name__
        # Get the first 2-3 identifying columns (e.g., id, name)
        identifiers = [c.name for c in self.__table__.columns if c.primary_key or c.name == "name"]
        attrs = ", ".join(f"{k}={getattr(self, k)!r}" for k in identifiers if hasattr(self, k))
        return f"<{class_name}({attrs})>"
