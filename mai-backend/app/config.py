from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    # choose: github_openai | dummy
    ai_provider: str = "github_openai"

    # GitHub Models (OpenAI SDK)
    github_token: str | None = None
    github_endpoint: str = "https://models.github.ai/inference"
    github_model_id: str = "openai/gpt-4o-mini"

    cors_origins: List[str] = ["*"]

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

settings = Settings()
