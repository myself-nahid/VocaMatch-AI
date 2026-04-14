from fastapi import APIRouter
from app.schemas.requests import MatchRequest
from app.schemas.responses import MatchResponse
from app.services.match_service import calculate_compatibility

router = APIRouter()

@router.post("/score", response_model=MatchResponse)
async def score_users(payload: MatchRequest):
    """
    Receives two user profiles from Django, calculates compatibility, and returns the score.
    """
    return await calculate_compatibility(payload.user_a, payload.user_b)