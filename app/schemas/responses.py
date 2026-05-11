from pydantic import BaseModel
from typing import List, Optional

# --- ADD THIS CLASS ---
class TranscriptionResponse(BaseModel):
    text: str
# ----------------------

class MatchResult(BaseModel):
    candidate_id: str
    image_url: Optional[str] = None
    compatibility_score: int
    match_level: str
    match_color: str
    is_special_match: bool
    matching_reason: str
    error: Optional[str] = None

class BulkMatchResponse(BaseModel):
    results: List[MatchResult]