from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secret_key: str
    postgres_hostname: str
    postgres_port: int
    postgres_password: str
    postgres_name: str
    postgres_username: str
    algorithm: str
    access_token_expire_minutes: int
    allowed_origins: str

    model_config = SettingsConfigDict(
        env_file=".env.dev", case_sensitive=False, extra="ignore"
    )


settings = Settings()  # ty: ignore[missing-argument]
