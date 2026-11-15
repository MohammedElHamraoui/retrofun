from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Assuming your database URL comes from a Pydantic Settings configuration
from retrofun.config import settings

# 1. Create the SQLAlchemy engine
# pool_pre_ping=True prevents dropped connections by testing them before use
engine = create_engine(
    settings.sqlalchemy_url,
    pool_size=5,  # persistent connections
    max_overflow=10,  # burst → 15 total
    pool_pre_ping=True,  # validate before checkout
    pool_recycle=1800,  # retire connections after 30 min
    # echo=True,  # for debugging in need
)

# 2. Configure the session factory
SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


# 3. Define the FastAPI dependency for session injection
def get_db() -> Generator[Session]:
    """
    Dependency function that yields a database session per request,
    ensuring it is safely closed after the request completes—even if exceptions occur.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
