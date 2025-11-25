from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    mongodb_uri: str
    openweathermap_api_key: str
    gemini_api_key: str = ""  # Optional: for AI chat assistant
    model_path: str = "models/crop_disease_model.onnx"
    
    class Config:
        env_file = ".env"
        protected_namespaces = ('settings_',)


@lru_cache
def get_settings() -> Settings:
    return Settings()
