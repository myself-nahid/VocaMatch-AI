import httpx
from app.core.config import settings

class VapiManager:
    def __init__(self):
        self.base_url = "https://api.vapi.ai" 
        self.headers = {
            "Authorization": f"Bearer {settings.VAPI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        self.questions_list =[
            "How important is it to you that a potential match communicates regularly?",
            "In a relationship, how much weight do you put on your partner being truly reliable and dependable?",
            "Do you value spontaneity and adventure in a partner, or do you prefer a more predictable routine?",
            # "How do you feel about a partner being involved in charitable activities or caring deeply about social causes?",
            # "How important is it for you to be with someone who is creative or at least appreciates the arts?",
            # "When looking for a partner, how much do you value ambition and a strong sense of drive?",
            # "How central is physical and emotional intimacy to your vision of a successful relationship?",
            # "How important is it that your partner has a strong sense of adventure and loves trying new things with you?",
            # "How much do you value a partner having a solid support system of friends and family around them?",
            # "How important are clear privacy boundaries to you within a committed relationship?",
            # "When disagreements happen, how important is it to you that your partner resolves conflict calmly and constructively?",
            "How much do you value openness to new experiences and a willingness to step out of a comfort zone?",
            "Finally, how important is spending dedicated, quality time together to you?"
        ]

        self.system_prompt = (
            "ROLE: You are 'elliot', an exclusive Matchmaking Consultant for VocaMatch. "
            "TONE: Warm, empathetic, highly professional, and curious. Speak like a human expert, not a bot. "
            
            "CONVERSATION RULES:\n"
            "1. NEVER use numbers like 'Question 1' or mention how many topics are left. Transitions must be seamless and conversational.\n"
            "2. ACTIVE LISTENING: When a user answers, briefly validate their feelings. "
            "For example, 'I completely agree, consistent communication builds such a strong foundation.'\n"
            "3. ENCOURAGEMENT: If a user gives a very short answer like 'Yes,' gently ask for a little more detail. "
            "Say something like, 'That makes sense. Is there a specific reason why that's a priority for you?'\n"
            "4. FLOW: Ask exactly one topic at a time. Do not rush. Gently guide them through the topics provided in your list.\n"
            "5. CLOSING: Once all topics are covered, wrap up warmly by saying you have a wonderful sense of who they are and that their profile is ready.\n\n"
            
            "INTERVIEW TOPICS TO GUIDE THE CONVERSATION:\n" + "\n".join(self.questions_list)
        )

    async def ensure_assistant_exists(self):
        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(f"{self.base_url}/assistant", headers=self.headers)
                if res.status_code != 200:
                    print(f"❌ Vapi API Error: {res.text}")
                    return None
                
                assistants = res.json()
                assistant_id = None
                for assistant in assistants:
                    if assistant.get("name") == settings.VAPI_ASSISTANT_NAME:
                        assistant_id = assistant['id']
                        break

                # --- UPDATED FIRST MESSAGE ---
                first_message = (
                    "Hello! Welcome to VocaMatch. I'm your personal matchmaking consultant. "
                    "I'd love to chat for a few minutes to get a true sense of who you are and what you value in a partner. "
                    "To start us off, how important is it to you that a potential match communicates regularly?"
                )

                payload = {
                    "name": settings.VAPI_ASSISTANT_NAME,
                    "firstMessage": first_message,
                    "model": {
                        "provider": "openai",
                        "model": "gpt-4o",
                        "messages":[{"role": "system", "content": self.system_prompt}],
                        "temperature": 0.6
                    },
                    "voice": {"provider": "vapi", "voiceId": "elliot"},
                    "transcriber": {"provider": "deepgram", "model": "nova-2", "language": "en-US"},
                    "serverUrl": "https://7bf5-162-4-34-65.ngrok-free.app/api/v1/vapi/webhook",
                    "serverUrlSecret": settings.VAPI_SECRET,
                    "serverMessages": ["end-of-call-report", "status-update", "hang"]
                }

                if assistant_id:
                    print(f"🔄 Updating Assistant '{settings.VAPI_ASSISTANT_NAME}' for professional tone...")
                    await client.patch(f"{self.base_url}/assistant/{assistant_id}", json=payload, headers=self.headers)
                    return assistant_id
                else:
                    print(f"🚀 Creating Assistant '{settings.VAPI_ASSISTANT_NAME}'...")
                    create_res = await client.post(f"{self.base_url}/assistant", json=payload, headers=self.headers)
                    if create_res.status_code == 201:
                        return create_res.json().get('id')
                    else:
                        print(f"❌ Creation Failed: {create_res.text}")
                        return None
            except Exception as e:
                print(f"❌ Vapi Manager Error: {e}")
                return None

vapi_manager = VapiManager()