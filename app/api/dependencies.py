from fastapi import Header, HTTPException, status
from app.core.config import settings

async def verify_internal_api_key(x_internal_key: str = Header(...)):
    if x_internal_key != settings.INTERNAL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Internal API Key",
        )