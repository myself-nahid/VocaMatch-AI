from pydantic import BaseModel
from typing import List, Optional

class MatchResponse(BaseModel):
    compatibility_score: int
    matching_reason: str

class MatchResult(BaseModel):
    candidate_id: str
    compatibility_score: int
    # --- NEW FIELDS FOR UI INDICATORS ---
    match_level: str        # e.g., "Excellent Match", "Good Match", "Low Compatibility"
    match_color: str        # e.g., "#4CAF50" (Green), "#FF9800" (Orange), "#9E9E9E" (Grey)
    is_special_match: bool  # True if the score is very high (e.g., > 85)
    # ------------------------------------
    matching_reason: str
    # error: Optional[str] = None

class BulkMatchResponse(BaseModel):
    results: List[MatchResult]

class TranscriptionResponse(BaseModel):
    text: str