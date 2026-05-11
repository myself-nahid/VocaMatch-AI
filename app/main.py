from contextlib import asynccontextmanager
import json
from fastapi import FastAPI, Request
from app.api.routes import matching, vapi_webhook # Ensure vapi_webhook is here
from app.services.vapi_service import vapi_manager
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Automatically ensure the Vapi Assistant is set up on startup
    try:
        assistant_id = await vapi_manager.ensure_assistant_exists()
        app.state.assistant_id = assistant_id
    except Exception as e:
        print(f"⚠️ Warning: Could not auto-set Vapi Assistant: {e}")
    yield

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# --- 🟢 ADD THIS MIDDLEWARE TO DEBUG 422 ERRORS 🟢 ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    if request.method == "POST":
        body = await request.body()
        print("\n" + "🚀" * 30)
        print("INCOMING POST DATA:")
        try:
            # Print the JSON in a pretty format
            print(json.dumps(json.loads(body), indent=2))
        except:
            print(body.decode())
        print("🚀" * 30 + "\n")
    
    response = await call_next(request)
    return response
# ---------------------------------------------------

# Include ONLY the routes we need for the Vapi version
app.include_router(vapi_webhook.router, prefix="/api/v1/vapi", tags=["Vapi"])
app.include_router(matching.router, prefix="/api/v1/match", tags=["Matching"])

@app.get("/health")
async def health():
    return {
        "status": "online",
        "assistant_id": getattr(app.state, "assistant_id", "not_set")
    }