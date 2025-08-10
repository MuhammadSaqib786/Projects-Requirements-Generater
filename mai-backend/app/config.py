from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    ai_provider: str = "github"
    github_token: str | None = None
    github_model_id: str = "deepseek/DeepSeek-V3-0324"
    github_endpoint: str = "https://models.github.ai/inference"
    cors_origins: List[str] = ["*"]
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

settings = Settings()
