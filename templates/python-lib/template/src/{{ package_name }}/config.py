from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    db_port: int = 5432
    api_key: str
    optional_setting: str | None = None
    env_value_1: str


settings = Settings()
