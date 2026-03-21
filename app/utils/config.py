import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Personalized Learning Path Generator"
    
    # JWT Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 1 week
    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATASET_DIR: str = os.path.join(os.path.dirname(BASE_DIR), "dataset")
    APP_DATA_DIR: str = os.path.join(BASE_DIR, "data")
    
    # LLM Settings
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "phi3")
    HF_FALLBACK_MODEL: str = "HuggingFaceH4/zephyr-7b-beta"
    
    # Embeddings
    EMBEDDINGS_MODEL: str = "all-MiniLM-L6-v2"

    class Config:
        env_file = ".env"

settings = Settings()

# Ensure directories exist
os.makedirs(settings.DATASET_DIR, exist_ok=True)
os.makedirs(settings.APP_DATA_DIR, exist_ok=True)
