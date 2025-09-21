from fastapi import APIRouter
from app.services.scoring import score
router = APIRouter()
@router.post("/debug")
def debug_score(features: dict) -> dict:
    return {"score": score(features)}
