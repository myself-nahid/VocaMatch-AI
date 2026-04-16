import asyncio
from fastapi import APIRouter
from app.schemas.requests import BulkMatchRequest
from app.schemas.responses import BulkMatchResponse, MatchResult
from app.services.match_service import calculate_compatibility

router = APIRouter()

def get_visual_indicators(score: int):
    """ Helper to determine UI elements based on the score """
    if score >= 85:
        return "Excellent Match", "#4CAF50", True   # Green + Star
    elif score >= 60:
        return "Great Match", "#8BC34A", False      # Light Green
    elif score >= 40:
        return "Fair Match", "#FF9800", False       # Orange
    else:
        return "Low Compatibility", "#9E9E9E", False # Grey

@router.post("/score/bulk", response_model=BulkMatchResponse)
async def bulk_score_users(payload: BulkMatchRequest):
    main_user = payload.main_user
    candidates = payload.potential_matches
    
    tasks = [calculate_compatibility(main_user, candidate) for candidate in candidates]
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    results = []
    for candidate, response in zip(candidates, responses):
        if isinstance(response, Exception):
            results.append(MatchResult(
                candidate_id=candidate.user_id,
                compatibility_score=0,
                match_level="Error",
                match_color="#000000",
                is_special_match=False,
                matching_reason="Match calculation failed.",
                error=str(response)
            ))
        else:
            # Get visual flags based on the score
            level, color, is_special = get_visual_indicators(response.compatibility_score)
            
            results.append(MatchResult(
                candidate_id=candidate.user_id,
                compatibility_score=response.compatibility_score,
                match_level=level,
                match_color=color,
                is_special_match=is_special,
                image_url=candidate.image_url,
                matching_reason=response.matching_reason
            ))
            
    return BulkMatchResponse(results=results)