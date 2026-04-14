import json
from openai import RateLimitError
from tenacity import retry, wait_random_exponential, stop_after_attempt
from app.services.openai_client import client
from app.schemas.requests import UserProfile
# Import the correct, single MatchResponse schema
from app.schemas.responses import MatchResponse 
from fastapi import HTTPException

# Add a retry decorator to handle OpenAI rate limits gracefully during bulk requests
@retry(
    wait=wait_random_exponential(min=1, max=10),
    stop=stop_after_attempt(5),
    retry_error_callback=lambda retry_state: retry_state.outcome.result()
)
async def calculate_compatibility(user_a: UserProfile, user_b: UserProfile) -> MatchResponse:
    """
    Calculates the compatibility between two users and returns a single match response.
    This function is designed to be called concurrently.
    """
    # CORRECTED PROMPT: Uses the new fields from the UserProfile model
    prompt = f"""
    You are an expert AI matchmaker for the VocaMatch app. 
    Analyze the following two user profiles and determine their compatibility based on personality, interests, and stated answers.
    
    User A (ID: {user_a.user_id}, Name: {user_a.name}, Age: {user_a.age}, Location: "{user_a.location}")
    - Interests: {', '.join(user_a.interests)}
    - Voice Intro says: "{user_a.voice_intro_text}"
    - Answers to Questions: {user_a.answers}
    
    User B (ID: {user_b.user_id}, Name: {user_b.name}, Age: {user_b.age}, Location: "{user_b.location}")
    - Interests: {', '.join(user_b.interests)}
    - Voice Intro says: "{user_b.voice_intro_text}"
    - Answers to Questions: {user_b.answers}
    
    Return a JSON object strictly following this format:
    {{
        "compatibility_score": <integer from 1 to 100>,
        "matching_reason": "<A compelling 2-sentence explanation of why they are or aren't a good match, focusing on shared interests and personality alignment.>"
    }}
    """
    
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a matchmaking AI that only outputs valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        result_dict = json.loads(response.choices[0].message.content)
        # CORRECTED RETURN: Returns the correct Pydantic model instance
        return MatchResponse(**result_dict)
    
    except RateLimitError as e:
        # Re-raise the rate limit error so Tenacity can catch it and retry
        raise e
        
    except Exception as e:
        # For all other errors, raise an HTTPException
        raise HTTPException(status_code=500, detail=f"AI Matching failed for user {user_b.user_id}: {str(e)}")