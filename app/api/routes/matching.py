import asyncio
from fastapi import APIRouter
from app.schemas.requests import BulkMatchRequest
from app.schemas.responses import BulkMatchResponse
from app.services.match_service import calculate_compatibility

router = APIRouter()

@router.post("/score/bulk", response_model=BulkMatchResponse)
async def score_bulk(payload: BulkMatchRequest):
    tasks = [calculate_compatibility(payload.main_user, cand) for cand in payload.potential_matches]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter exceptions and return results
    valid_results = [res for res in results if not isinstance(res, Exception)]
    return BulkMatchResponse(results=valid_results)