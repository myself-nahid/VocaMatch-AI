from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "VocaMatch AI"
    OPENAI_API_KEY: str
    INTERNAL_API_KEY: str
    VAPI_SECRET: str
    DJANGO_BASE_URL: str
    VAPI_API_KEY: str
    VAPI_ASSISTANT_NAME: str = "VocaMatch AI Interviewer"

    class Config:
        env_file = ".env"

settings = Settings()