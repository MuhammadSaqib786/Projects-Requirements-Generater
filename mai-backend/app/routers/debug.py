from fastapi import APIRouter
from app.config import settings

router = APIRouter()

@router.get("/debug/env")
def dbg():
    return {
        "ai_provider": settings.ai_provider,
        "github_model_id": settings.github_model_id,
        "github_endpoint": settings.github_endpoint,
        "github_token_present": bool(settings.github_token),
    }
