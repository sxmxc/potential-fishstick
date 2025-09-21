from fastapi import FastAPI
from app.api.routes import health, scoring
app = FastAPI(title="signal-os API", version="0.1.0")
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(scoring.router, prefix="/scoring", tags=["scoring"])
