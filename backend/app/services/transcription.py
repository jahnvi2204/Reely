"""
Transcription service using OpenAI Whisper for audio-to-text conversion
"""
import os
import whisper
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.core.config import settings
from app.models.schemas import CaptionSegment
from app.services.storage import storage_service
from pathlib import Path

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Service for audio transcription using OpenAI Whisper"""
    
    def __init__(self):
        self.model = None
        self.model_name = settings.whisper_model
        self.executor = ThreadPoolExecutor(max_workers=2)
        # Defer model load to first use to keep imports fast and tests lightweight
    
    def _load_model(self):
        """Load Whisper model"""
        try:
            logger.info(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading Whisper model: {e}")
            raise
    
    async def transcribe_audio(self, audio_path: str, video_id: str) -> List[CaptionSegment]:
        """Transcribe audio file and return caption segments"""
        try:
            # Check cache first
            cached_result = await self._get_cached_transcription(audio_path)
            if cached_result:
                logger.info(f"Using cached transcription for video {video_id}")
                return cached_result
            
            logger.info(f"Starting transcription for video {video_id}")
            
            # Run transcription in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor, 
                self._transcribe_audio_sync, 
                audio_path
            )
            
            # Convert to caption segments
            segments = self._convert_to_segments(result)
            
            # Cache the result
            await self._cache_transcription(audio_path, segments)
            
            logger.info(f"Transcription completed for video {video_id}")
            return segments
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise
    
    def _transcribe_audio_sync(self, audio_path: str) -> Dict[str, Any]:
        """Synchronous transcription method"""
        try:
            if self.model is None:
                self._load_model()
            result = self.model.transcribe(
                audio_path,
                word_timestamps=True,
                verbose=False
            )
            return result
        except Exception as e:
            logger.error(f"Error in synchronous transcription: {e}")
            raise
    
    def _convert_to_segments(self, whisper_result: Dict[str, Any]) -> List[CaptionSegment]:
        """Convert Whisper result to caption segments"""
        segments = []
        
        try:
            for segment in whisper_result.get("segments", []):
                caption_segment = CaptionSegment(
                    start_time=segment["start"],
                    end_time=segment["end"],
                    text=segment["text"].strip(),
                    confidence=segment.get("avg_logprob", None)
                )
                segments.append(caption_segment)
            
            logger.info(f"Converted {len(segments)} segments from transcription")
            return segments
            
        except Exception as e:
            logger.error(f"Error converting segments: {e}")
            raise
    
    async def _get_cached_transcription(self, audio_path: str) -> Optional[List[CaptionSegment]]:
        """Check if transcription is cached"""
        try:
            file_hash = storage_service.get_file_hash(audio_path)
            
            # In a real implementation, you would query MongoDB here
            # For now, we'll implement a simple file-based cache
            cache_dir = Path(settings.processed_dir) / "cache"
            cache_dir.mkdir(exist_ok=True)
            
            cache_file = cache_dir / f"{file_hash}.json"
            
            if cache_file.exists():
                import json
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                
                # Check if cache is still valid
                cache_time = datetime.fromisoformat(cached_data["created_at"])
                if datetime.now() - cache_time < timedelta(seconds=settings.transcription_cache_ttl):
                    logger.info(f"Found valid cached transcription: {cache_file}")
                    return [CaptionSegment(**seg) for seg in cached_data["segments"]]
                else:
                    # Cache expired, remove file
                    cache_file.unlink()
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking cache: {e}")
            return None
    
    async def _cache_transcription(self, audio_path: str, segments: List[CaptionSegment]) -> None:
        """Cache transcription result"""
        try:
            file_hash = storage_service.get_file_hash(audio_path)
            
            cache_dir = Path(settings.processed_dir) / "cache"
            cache_dir.mkdir(exist_ok=True)
            
            cache_file = cache_dir / f"{file_hash}.json"
            
            cache_data = {
                "file_hash": file_hash,
                "model_used": self.model_name,
                "created_at": datetime.now().isoformat(),
                "segments": [seg.dict() for seg in segments]
            }
            
            import json
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.info(f"Transcription cached: {cache_file}")
            
        except Exception as e:
            logger.error(f"Error caching transcription: {e}")
    
    def get_available_models(self) -> List[str]:
        """Get list of available Whisper models"""
        return whisper.available_models()
    
    def change_model(self, model_name: str) -> None:
        """Change the Whisper model"""
        try:
            if model_name not in whisper.available_models():
                raise ValueError(f"Model {model_name} not available")
            
            logger.info(f"Changing Whisper model to: {model_name}")
            self.model = whisper.load_model(model_name)
            self.model_name = model_name
            logger.info("Model changed successfully")
            
        except Exception as e:
            logger.error(f"Error changing model: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about current model"""
        return {
            "model_name": self.model_name,
            "available_models": whisper.available_models(),
            "model_size": whisper._MODELS[self.model_name] if self.model_name in whisper._MODELS else "unknown"
        }
    
    async def transcribe_with_timestamps(self, audio_path: str, video_id: str) -> Dict[str, Any]:
        """Transcribe with detailed word-level timestamps"""
        try:
            # Check cache first
            cached_result = await self._get_cached_transcription(audio_path)
            if cached_result:
                return {"segments": cached_result, "cached": True}
            
            logger.info(f"Starting detailed transcription for video {video_id}")
            
            # Run transcription in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                self._transcribe_with_word_timestamps,
                audio_path
            )
            
            # Convert to segments
            segments = self._convert_to_segments(result)
            
            # Cache the result
            await self._cache_transcription(audio_path, segments)
            
            return {"segments": segments, "cached": False}
            
        except Exception as e:
            logger.error(f"Error in detailed transcription: {e}")
            raise
    
    def _transcribe_with_word_timestamps(self, audio_path: str) -> Dict[str, Any]:
        """Transcribe with word-level timestamps"""
        try:
            if self.model is None:
                self._load_model()
            result = self.model.transcribe(
                audio_path,
                word_timestamps=True,
                verbose=False
            )
            return result
        except Exception as e:
            logger.error(f"Error in word-level transcription: {e}")
            raise
    
    def cleanup(self):
        """Cleanup resources"""
        if self.executor:
            self.executor.shutdown(wait=True)


# Global transcription service instance (lazy-loaded model)
transcription_service = TranscriptionService()
