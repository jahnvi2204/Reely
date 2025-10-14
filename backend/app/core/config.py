"""
Configuration settings for the Reely API
"""
import os
from typing import List
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    from pydantic import BaseSettings  # type: ignore
    SettingsConfigDict = dict  # fallback for older pydantic


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Pydantic v2 settings: ignore unknown keys in .env to avoid crashes
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra='ignore')
    
    # Database Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "reely_db"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    
    # AWS S3 Configuration
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    s3_bucket_name: str = "reely-videos"
    
    # Application Settings
    secret_key: str = "your-secret-key-here"
    debug: bool = True
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # File Storage
    upload_dir: str = "./uploads"
    processed_dir: str = "./processed"
    max_file_size_mb: int = 500
    
    # Transcription Settings
    whisper_model: str = "base"
    transcription_cache_ttl: int = 86400  # 24 hours
    
    # Video Processing
    video_formats: List[str] = ["mp4", "avi", "mov", "mkv", "webm"]
    audio_formats: List[str] = ["mp3", "wav", "aac", "m4a"]
    
    # Celery Configuration
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # Firebase Admin Credentials
    firebase_credentials_path: str = ""  # Path to service account JSON
    
    # Remove legacy Config (Pydantic v1) to avoid conflict with model_config


# Global settings instance
settings = Settings()

# Ensure directories exist
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.processed_dir, exist_ok=True)
