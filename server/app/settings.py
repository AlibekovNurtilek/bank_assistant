from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./app.db"
    db_echo: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_prefix="")

settings = Settings()
