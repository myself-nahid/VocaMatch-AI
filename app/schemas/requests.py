from pydantic import BaseModel, field_validator
from typing import List, Optional, Dict

class UserAnswer(BaseModel):
    question: str
    answer: str

class UserProfile(BaseModel):
    user_id: str
    name: str
    age: int
    image_url: Optional[str] = None
    location: str
    interests: List[str]
    voice_intro_text: str
    conversation: Optional[str] = "" # Renamed to match Django
    answers: Optional[List[UserAnswer]] = [] # Added to match Django

    @field_validator('interests', mode='before')
    @classmethod
    def split_interests(cls, v):
        # If Django sends ["A,B,C"], this turns it into ["A", "B", "C"]
        if isinstance(v, list) and len(v) == 1 and "," in v[0]:
            return [i.strip() for i in v[0].split(",")]
        return v

class BulkMatchRequest(BaseModel):
    main_user: UserProfile
    potential_matches: List[UserProfile]