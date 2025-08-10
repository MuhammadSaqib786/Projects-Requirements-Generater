from fastapi import APIRouter, HTTPException
from fastapi.responses import ORJSONResponse
from datetime import datetime
from app.schemas import GenerateRequest, GenerateResponse
from app.services.ai_provider import get_provider

router = APIRouter()

@router.get("/health", response_class=ORJSONResponse)
async def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat() + "Z"}

@router.post("/generate", response_model=GenerateResponse, response_class=ORJSONResponse)
async def generate(req: GenerateRequest):
    provider = get_provider()
    try:
        data = await provider.generate(req)
        return data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
