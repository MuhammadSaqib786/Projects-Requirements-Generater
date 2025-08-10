from app.config import settings
from app.services.providers.dummy import DummyProvider
from app.services.providers.github_openai import GitHubOpenAIProvider

def get_provider():
    name = (settings.ai_provider or "dummy").lower()
    if name in ("github_openai", "openai", "gpt4o"):
        return GitHubOpenAIProvider()
    return DummyProvider()
