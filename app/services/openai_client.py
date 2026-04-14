from openai import AsyncOpenAI
from app.core.config import settings

# Global async client to be used across services
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)