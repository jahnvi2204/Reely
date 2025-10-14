"""
Pydantic schemas for API request/response models
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ProcessingStatus(str, Enum):
    """Video processing status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class CaptionStyle(BaseModel):
    """Caption styling configuration"""
    font_type: str = Field(default="Arial", description="Font family name")
    font_size: int = Field(default=24, ge=8, le=72, description="Font size in pixels")
    font_color: str = Field(default="#FFFFFF", description="Font color in hex format")
    stroke_color: str = Field(default="#000000", description="Stroke/outline color in hex format")
    stroke_width: int = Field(default=2, ge=0, le=10, description="Stroke width in pixels")
    padding: int = Field(default=10, ge=0, le=50, description="Padding around text in pixels")
    position: str = Field(default="bottom", description="Caption position: top, bottom, center")


class VideoUploadRequest(BaseModel):
    """Request model for video upload"""
    video_url: Optional[str] = Field(None, description="Public video URL to process")
    caption_style: Optional[CaptionStyle] = Field(default_factory=CaptionStyle, description="Caption styling options")


class VideoUploadResponse(BaseModel):
    """Response model for video upload"""
    video_id: str = Field(description="Unique identifier for the video")
    status: ProcessingStatus = Field(description="Current processing status")
    message: str = Field(description="Status message")
    created_at: datetime = Field(description="Upload timestamp")


class CaptionSegment(BaseModel):
    """Individual caption segment with timing"""
    start_time: float = Field(description="Start time in seconds")
    end_time: float = Field(description="End time in seconds")
    text: str = Field(description="Caption text")
    confidence: Optional[float] = Field(None, description="Transcription confidence score")


class VideoMetadata(BaseModel):
    """Video metadata information"""
    duration: float = Field(description="Video duration in seconds")
    width: int = Field(description="Video width in pixels")
    height: int = Field(description="Video height in pixels")
    fps: float = Field(description="Frames per second")
    format: str = Field(description="Video format")
    size_bytes: int = Field(description="File size in bytes")


class VideoInfo(BaseModel):
    """Complete video information"""
    video_id: str = Field(description="Unique video identifier")
    filename: str = Field(description="Original filename")
    status: ProcessingStatus = Field(description="Processing status")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    
    # File paths
    original_path: Optional[str] = Field(None, description="Path to original video")
    processed_path: Optional[str] = Field(None, description="Path to processed video with captions")
    audio_path: Optional[str] = Field(None, description="Path to extracted audio")
    
    # Metadata
    metadata: Optional[VideoMetadata] = Field(None, description="Video metadata")
    
    # Transcription
    transcription: Optional[List[CaptionSegment]] = Field(None, description="Transcribed segments")
    caption_style: Optional[CaptionStyle] = Field(None, description="Applied caption styling")
    
    # Error information
    error_message: Optional[str] = Field(None, description="Error message if processing failed")
    
    # Processing progress
    progress_percentage: int = Field(default=0, ge=0, le=100, description="Processing progress percentage")


class VideoListResponse(BaseModel):
    """Response model for video list endpoint"""
    videos: List[VideoInfo] = Field(description="List of videos")
    total: int = Field(description="Total number of videos")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Number of videos per page")


class CaptionRequest(BaseModel):
    """Request model for caption processing"""
    video_id: str = Field(description="Video identifier")
    caption_style: Optional[CaptionStyle] = Field(default_factory=CaptionStyle, description="Caption styling options")
    regenerate: bool = Field(default=False, description="Whether to regenerate transcription")


class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str = Field(description="Error type")
    message: str = Field(description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class ProcessingProgress(BaseModel):
    """Processing progress update"""
    video_id: str = Field(description="Video identifier")
    status: ProcessingStatus = Field(description="Current status")
    progress_percentage: int = Field(ge=0, le=100, description="Progress percentage")
    current_step: str = Field(description="Current processing step")
    estimated_time_remaining: Optional[int] = Field(None, description="Estimated time remaining in seconds")
