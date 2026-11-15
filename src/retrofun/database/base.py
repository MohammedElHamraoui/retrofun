# src/retrofun/database/base.py
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

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


engine = create_engine(
    settings.sqlalchemy_url,
    pool_size=5,  # persistent connections
    max_overflow=10,  # burst → 15 total
    pool_pre_ping=True,  # validate before checkout
    pool_recycle=1800,  # retire connections after 30 min
    # echo=True,  # for debugging in need
)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
