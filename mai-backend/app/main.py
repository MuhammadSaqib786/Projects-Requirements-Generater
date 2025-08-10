from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from app.config import settings
from app.routers import generate
from app.routers import debug 
from app.routers import exporter 

app = FastAPI(title="Mai Backend", default_response_class=ORJSONResponse)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate.router, prefix="/api")
app.include_router(debug.router, prefix="/api")
app.include_router(exporter.router, prefix="/api") 