from pydantic import BaseModel
from typing import List, Optional

class MatchResponse(BaseModel):
    compatibility_score: int
    matching_reason: str

class MatchResult(BaseModel):
    candidate_id: str
    compatibility_score: int
    matching_reason: str
    # error: Optional[str] = None

class BulkMatchResponse(BaseModel):
    results: List[MatchResult]

class TranscriptionResponse(BaseModel):
    text: str