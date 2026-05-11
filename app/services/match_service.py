import json
from openai import AsyncOpenAI
from app.core.config import settings
from app.schemas.requests import UserProfile
from app.schemas.responses import MatchResult

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def calculate_compatibility(user_a: UserProfile, user_b: UserProfile) -> MatchResult:
    # Build a summary of their answers for the AI
    answers_a = "\n".join([f"Q: {a.question} A: {a.answer}" for a in user_a.answers])
    answers_b = "\n".join([f"Q: {b.question} A: {b.answer}" for b in user_b.answers])

    prompt = f"""
    You are a relationship psychologist. Analyze these two profiles:

    --- USER A ---
    Name: {user_a.name}
    Interests: {', '.join(user_a.interests)}
    Interview Transcript: {user_a.conversation}
    Survey Answers:
    {answers_a}

    --- USER B ---
    Name: {user_b.name}
    Interests: {', '.join(user_b.interests)}
    Interview Transcript: {user_b.conversation}
    Survey Answers:
    {answers_b}

    Return JSON:
    {{
        "compatibility_score": <int 1-100>,
        "matching_reason": "<3 sentence expert analysis>"
    }}
    """
    
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    data = json.loads(response.choices[0].message.content)
    score = data["compatibility_score"]
    
    # Determine UI Indicators
    level, color, special = ("Low", "#9E9E9E", False)
    if score >= 85: level, color, special = ("Excellent", "#4CAF50", True)
    elif score >= 60: level, color, special = ("Good", "#8BC34A", False)
    elif score >= 40: level, color, special = ("Fair", "#FF9800", False)

    return MatchResult(
        candidate_id=user_b.user_id,
        image_url=user_b.image_url, # Now matches perfectly
        compatibility_score=score,
        match_level=level,
        match_color=color,
        is_special_match=special,
        matching_reason=data["matching_reason"]
    )