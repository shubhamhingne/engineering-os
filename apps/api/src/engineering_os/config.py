"""Environment-driven settings (12-factor)."""
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"           # "development" | "production"
    database_url: str = "sqlite:///./engineering_os.db"
    cors_origins: str = "http://localhost:3000"

    # AI: provider is selected here; the core depends only on the port (Principle 5).
    ai_provider: str = "fake"          # "fake" | "anthropic"
    anthropic_api_key: str = ""
    ai_model: str = "claude-sonnet-4-6"

    # GitHub publishing — legacy single-token fallback. The user OAuth flow (below) supersedes it:
    # publishing credentials now come from the authenticated session via the CredentialProvider.
    github_token: str = ""

    # Identity & federation (Alpha-0.8). When the OAuth client id/secret are unset, a deterministic
    # fake provider is used so local dev and tests need no GitHub app.
    github_oauth_client_id: str = ""
    github_oauth_client_secret: str = ""
    oauth_redirect_uri: str = "http://localhost:8000/api/v1/auth/github/callback"
    web_url: str = "http://localhost:3000"          # where to send the browser after login
    session_cookie: str = "eos_session"
    cookie_secure: bool = False                       # True behind HTTPS in production

    # Encryption of third-party tokens at rest (BR-02). REQUIRED in production: any high-entropy
    # secret. When unset, a deterministic insecure dev key is used and a warning is logged — tokens
    # are still never stored as plaintext.
    token_encryption_key: str = ""

    # Abuse protection (BR-05). Off in dev/tests; the production profile turns it on.
    rate_limit_enabled: bool = False
    rate_limit_per_minute: int = 30        # per client, per limited route group

    # Resilience: retry attempts for transient external-call failures (AI providers, GitHub).
    external_retry_attempts: int = 3

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @model_validator(mode="after")
    def _enforce_production_profile(self) -> "Settings":
        """In production, fail fast on insecure defaults (BR-07) rather than starting unsafely."""
        if self.is_production:
            problems = []
            if not self.token_encryption_key:
                problems.append("TOKEN_ENCRYPTION_KEY must be set")
            if self.database_url.startswith("sqlite"):
                problems.append("DATABASE_URL must not be SQLite")
            if problems:
                raise ValueError("insecure production config: " + "; ".join(problems))
            # Secure-by-default in production.
            self.cookie_secure = True
            self.rate_limit_enabled = True
        return self


settings = Settings()
