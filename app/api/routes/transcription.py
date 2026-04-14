from fastapi import APIRouter, UploadFile, File
from app.schemas.responses import TranscriptionResponse
from app.services.speech_service import transcribe_audio

router = APIRouter()

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe(file: UploadFile = File(...)):
    """
    Receives voice intro/answers from Django, transcribes using Whisper, and returns text.
    """
    text = await transcribe_audio(file)
    return TranscriptionResponse(text=text)