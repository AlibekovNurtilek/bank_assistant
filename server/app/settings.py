from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./app.db"
    db_echo: bool = False
    session_secret: str = "CHANGE_ME"   # 🔐 замени через .env
    debug: bool = True                  # в проде False
    knowledge_base_dir: Path | None = None 

    model_config = SettingsConfigDict(env_file=".env", env_prefix="")

settings = Settings()
