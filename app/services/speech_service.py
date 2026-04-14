import os
import tempfile
from fastapi import UploadFile, HTTPException
from app.services.openai_client import client

async def transcribe_audio(audio_file: UploadFile) -> str:
    # OpenAI Whisper requires a file extension to identify format (e.g., .m4a, .wav)
    file_ext = os.path.splitext(audio_file.filename)[1]
    
    if not file_ext:
        file_ext = ".m4a" # Default fallback
        
    # We must save the stream to a temporary file locally so OpenAI SDK can read it
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
        temp_file.write(await audio_file.read())
        temp_file_path = temp_file.name

    try:
        with open(temp_file_path, "rb") as file_to_transcribe:
            response = await client.audio.transcriptions.create(
                model="whisper-1",
                file=file_to_transcribe,
                response_format="text"
            )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    finally:
        # Crucial: Clean up the file to maintain statelessness and save disk space
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)