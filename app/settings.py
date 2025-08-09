from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Provide application settings from environment."""

    database_url: str = 'postgresql+asyncpg://postgres:postgres@localhost:5432/lyrics_app'
    secret_key: str = 'dev-secret'  # noqa: S105
    debug: bool = False

    admin_bootstrap_email: str | None = None
    admin_bootstrap_password: str | None = None
    admin_bootstrap_password_hash: str | None = None

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
    )


settings = Settings()
