import json
from app.services.openai_client import client
from app.schemas.requests import UserProfile
from app.schemas.responses import MatchResponse
from fastapi import HTTPException

async def calculate_compatibility(user_a: UserProfile, user_b: UserProfile) -> MatchResponse:
    prompt = f"""
    You are an expert AI matchmaker for the VocaMatch app. 
    Analyze the following two user profiles and determine their compatibility based on personality and preferences.
    
    User A (ID: {user_a.user_id}):
    Preferences: {user_a.preferences}
    Answers: {user_a.answers}
    
    User B (ID: {user_b.user_id}):
    Preferences: {user_b.preferences}
    Answers: {user_b.answers}
    
    Return a JSON object strictly following this format:
    {{
        "compatibility_score": <integer from 1 to 100>,
        "matching_reason": "<A compelling 2-sentence explanation of why they are or aren't a good match>"
    }}
    """
    
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo", # Change to gpt-4 or gpt-4o for better reasoning if budget allows
            messages=[
                {"role": "system", "content": "You are a matchmaking AI that only outputs valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        result_dict = json.loads(response.choices[0].message.content)
        return MatchResponse(**result_dict)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Matching failed: {str(e)}")