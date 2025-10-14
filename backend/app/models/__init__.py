"""
Database models for MongoDB collections
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    # Pydantic v2: schema modification via __modify_schema__ is not supported


class CaptionSegmentDB(BaseModel):
    """Database model for caption segments"""
    start_time: float
    end_time: float
    text: str
    confidence: Optional[float] = None


class CaptionStyleDB(BaseModel):
    """Database model for caption styling"""
    font_type: str = "Arial"
    font_size: int = 24
    font_color: str = "#FFFFFF"
    stroke_color: str = "#000000"
    stroke_width: int = 2
    padding: int = 10
    position: str = "bottom"


class VideoMetadataDB(BaseModel):
    """Database model for video metadata"""
    duration: float
    width: int
    height: int
    fps: float
    format: str
    size_bytes: int


class VideoDocument(BaseModel):
    """Main video document model for MongoDB"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    video_id: str = Field(unique=True, index=True)
    filename: str
    status: str = "pending"  # pending, processing, completed, failed
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # File paths
    original_path: Optional[str] = None
    processed_path: Optional[str] = None
    audio_path: Optional[str] = None
    
    # Metadata
    metadata: Optional[VideoMetadataDB] = None
    
    # Transcription
    transcription: Optional[List[CaptionSegmentDB]] = None
    caption_style: Optional[CaptionStyleDB] = None
    
    # Error information
    error_message: Optional[str] = None
    
    # Processing progress
    progress_percentage: int = 0
    current_step: Optional[str] = None
    
    # Processing task information
    celery_task_id: Optional[str] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )


class TranscriptionCache(BaseModel):
    """Cache model for transcription results"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    video_hash: str = Field(unique=True, index=True)  # Hash of video content
    transcription: List[CaptionSegmentDB]
    model_used: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )


class ProcessingTask(BaseModel):
    """Model for tracking processing tasks"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    video_id: str = Field(index=True)
    task_id: str = Field(unique=True, index=True)
    task_type: str  # upload, transcribe, caption, process
    status: str = "pending"  # pending, running, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    progress: int = 0
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )
