from fastapi import FastAPI, Depends
from app.api.routes import matching, transcription
from app.api.dependencies import verify_internal_api_key
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI Microservice for VocaMatch Handling Whisper & Matching",
    version="1.0.0",
    # Protect all routes globally with the internal API key dependency
    dependencies=[Depends(verify_internal_api_key)] 
)

# Include Routers
app.include_router(matching.router, prefix="/api/v1/match", tags=["Matching"])
app.include_router(transcription.router, prefix="/api/v1/audio", tags=["Transcription"])

@app.get("/health", dependencies=[]) # Overriding dependencies so load balancers can hit this freely
async def health_check():
    return {"status": "healthy"}