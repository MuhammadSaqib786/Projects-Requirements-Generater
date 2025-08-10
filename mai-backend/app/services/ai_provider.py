from app.config import settings
from app.services.providers.github_models import GitHubModelsProvider
from app.services.providers.dummy import DummyProvider

def get_provider():
    name = (settings.ai_provider or "dummy").lower()
    if name == "github":
        return GitHubModelsProvider()
    return DummyProvider()
