from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "VocaMatch AI Microservice"
    OPENAI_API_KEY: str
    INTERNAL_API_KEY: str # Shared secret with the Django Backend

    class Config:
        env_file = ".env"

settings = Settings()