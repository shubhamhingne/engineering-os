"""Environment-driven settings (12-factor)."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./engineering_os.db"
    cors_origins: str = "http://localhost:3000"

    # AI: provider is selected here; the core depends only on the port (Principle 5).
    ai_provider: str = "fake"          # "fake" | "anthropic"
    anthropic_api_key: str = ""
    ai_model: str = "claude-sonnet-4-6"

    # GitHub publishing (a real OAuth/user-token flow arrives in Alpha-0.7)
    github_token: str = ""


settings = Settings()
