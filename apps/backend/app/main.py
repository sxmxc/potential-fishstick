"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.routes import events, health, incidents, scoring

app = FastAPI(title="signal-os API", version="0.1.0")

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(scoring.router, prefix="/scoring", tags=["scoring"])
app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
