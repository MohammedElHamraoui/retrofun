from datetime import datetime
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

    def to_dict(self) -> dict[str,Any]:
        """
        Converts any inherited SQLAlchemy model instance into a clean dictionary,
        safely serializing types like UUID and datetime.
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)

            # Normalize common non-JSON-native types if needed
            if isinstance(value, UUID):
                value = str(value)
            elif isinstance(value, datetime):
                value = value.isoformat()

            result[column.name] = value
        return result
