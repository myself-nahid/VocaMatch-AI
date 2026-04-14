import asyncio
from fastapi import APIRouter
from app.schemas.requests import BulkMatchRequest
from app.schemas.responses import BulkMatchResponse, MatchResult
from app.services.match_service import calculate_compatibility

router = APIRouter()

@router.post("/score/bulk", response_model=BulkMatchResponse)
async def bulk_score_users(payload: BulkMatchRequest):
    """
    Scores one main user against a list of candidates concurrently.
    """
    main_user = payload.main_user
    candidates = payload.potential_matches
    
    # 1. Create a list of async tasks for OpenAI
    tasks =[
        calculate_compatibility(main_user, candidate) 
        for candidate in candidates
    ]
    
    # 2. Run all tasks concurrently. return_exceptions=True prevents one failed API call from crashing the batch.
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 3. Map the results back to the respective candidate IDs
    results =[]
    for candidate, response in zip(candidates, responses):
        if isinstance(response, Exception):
            # If OpenAI failed for this specific candidate (e.g., rate limit)
            results.append(MatchResult(
                candidate_id=candidate.user_id,
                compatibility_score=0,
                matching_reason="Match calculation failed.",
                error=str(response)
            ))
        else:
            # Success!
            results.append(MatchResult(
                candidate_id=candidate.user_id,
                compatibility_score=response.compatibility_score,
                matching_reason=response.matching_reason
            ))
            
    return BulkMatchResponse(results=results)