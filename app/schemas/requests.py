from pydantic import BaseModel
from typing import List, Dict, Optional

class UserProfile(BaseModel):
    user_id: str
    name: str
    age: int
    location: str
    interests: List[str]
    voice_intro_text: str
    image_url: Optional[str] = None
    answers: Optional[List[Dict[str, str]]] =[]

class BulkMatchRequest(BaseModel):
    main_user: UserProfile
    potential_matches: List[UserProfile] # A batch of candidates