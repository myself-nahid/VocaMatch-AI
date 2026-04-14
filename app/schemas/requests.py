from pydantic import BaseModel
from typing import List, Dict

class UserProfile(BaseModel):
    user_id: str
    preferences: str
    answers: List[Dict[str, str]] # e.g., [{"question": "...", "answer": "..."}]

class MatchRequest(BaseModel):
    user_a: UserProfile
    user_b: UserProfile