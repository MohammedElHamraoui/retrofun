from urllib.parse import quote_plus

from pydantic import Field, PostgresDsn, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_user: str = "retrofun"
    postgres_password: SecretStr  # required — no default, fails fast if missing
    postgres_host: str = "127.0.0.1"  # force TCP, avoids the peer-auth trap
    postgres_port: int = Field(default=5432, ge=1, le=65535)
    postgres_db: str = "retrofundb"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> PostgresDsn:
        """Canonical DSN — for raw psycopg / psycopg_pool."""
        pw = quote_plus(self.postgres_password.get_secret_value())
        return PostgresDsn.build(
            scheme="postgresql",
            username=self.postgres_user,
            password=pw,
            host=self.postgres_host,
            port=self.postgres_port,
            path=self.postgres_db,
        )

    @property
    def sqlalchemy_url(self) -> str:
        """Dialect-qualified URL — for SQLAlchemy's create_engine()."""
        return str(self.database_url).replace("postgresql://", "postgresql+psycopg://", 1)


# postgres_password is populated from the environment / .env at runtime;
# mypy's synthesized __init__ can't see pydantic-settings' sources.
settings = Settings()  # type: ignore[call-arg]

if __name__ == "__main__":
    u = settings.database_url
    h = u.hosts()[0]  # PostgresDsn is multi-host; credentials live per-host
    print(f"Database URL: {u.scheme}://{h['username']}:***@{h['host']}:{h['port']}{u.path}")
    print(
        f"SQLAlchemy URL: {u.scheme}+psycopg://{h['username']}:***@{h['host']}:{h['port']}{u.path}"
    )
