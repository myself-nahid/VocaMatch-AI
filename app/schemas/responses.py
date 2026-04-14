from pydantic import BaseModel

class MatchResponse(BaseModel):
    compatibility_score: int
    matching_reason: str

class TranscriptionResponse(BaseModel):
    text: str