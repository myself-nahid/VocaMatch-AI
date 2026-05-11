from fastapi import APIRouter, Request
from app.core.config import settings
from app.services.match_service import client
import httpx
import json

router = APIRouter()

def find_key_recursive(data, target_key):
    """
    Recursively searches for a key in a deeply nested dictionary or list.
    """
    if isinstance(data, dict):
        if target_key in data:
            return data[target_key]
        for key, value in data.items():
            result = find_key_recursive(value, target_key)
            if result:
                return result
    elif isinstance(data, list):
        for item in data:
            result = find_key_recursive(item, target_key)
            if result:
                return result
    return None

async def generate_pro_bio(transcript: str) -> str:
    if not transcript or len(transcript) < 20:
        return "A new member of the VocaMatch community."
    
    prompt = f"""
    Based on this interview transcript, write a short, engaging dating profile bio (max 3 sentences). 
    Write it in the third person. Focus on their personality and what they value.
    Transcript: {transcript}
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional dating profile writer."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except:
        return transcript[:200]

@router.post("/webhook")
async def handle_vapi_webhook(request: Request):
    try:
        payload = await request.json()
        message = payload.get("message", {})
        message_type = message.get("type")

        if message_type == "end-of-call-report":
            # 1. Get the transcript
            transcript = message.get("transcript", "").strip()
            
            # 2. Find the User ID anywhere in the payload
            user_id = find_key_recursive(payload, "userId") or find_key_recursive(payload, "user_id")

            # --- 🟢 TRANSCRIPT PRINTING SECTION 🟢 ---
            print("\n" + "█"*60, flush=True)
            print(f"📄 SENDING TO DJANGO (User ID: {user_id or 'NOT FOUND'})", flush=True)
            print("─"*60, flush=True)
            print(f"TRANSCRIPT CONTENT:\n{transcript}", flush=True)
            print("█"*60 + "\n", flush=True)
            # ----------------------------------------

            if not user_id:
                print(f"⚠️  REJECTED: Could not find userId in JSON payload.", flush=True)
                return {"status": "error", "message": "No userId found"}

            if not transcript:
                print(f"⚠️  SKIPPED: User {user_id} hung up without speaking.", flush=True)
                return {"status": "skipped", "reason": "empty transcript"}

            # 3. Generate the AI Bio
            print(f"🤖 Generating AI bio for {user_id}...", flush=True)
            ai_bio = await generate_pro_bio(transcript)

            # 4. Prepare and Send to Django
            django_payload = {
                "user_id": str(user_id),
                "transcript": transcript,
                "ai_generated_bio": ai_bio
            }
            
            await forward_to_django(django_payload)
        
        return {"status": "success"}

    except Exception as e:
        print(f"🔥 Webhook Error: {e}", flush=True)
        return {"status": "error", "detail": str(e)}

async def forward_to_django(payload: dict):
    django_url = f"{settings.DJANGO_BASE_URL}/api/v1/auth/ai-save-conversation/"
    async with httpx.AsyncClient() as client:
        try:
            print(f"🚀 Forwarding to Django URL: {django_url}", flush=True)
            response = await client.post(
                django_url,
                json=payload,
                headers={"x-internal-key": settings.INTERNAL_API_KEY}
            )
            print(f"✅ Django Response: {response.status_code} - {response.text}", flush=True)
        except Exception as e:
            print(f"❌ Django Connection Failed: {e}", flush=True)