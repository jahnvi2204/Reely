"""
Celery worker for asynchronous video processing tasks
"""
import os
import logging
from celery import Celery
from celery.signals import worker_ready, worker_shutdown
from datetime import datetime
import uuid

from app.core.config import settings
from app.services.video_processor import video_processor
from app.services.transcription import transcription_service
from app.services.storage import storage_service
from app.models.schemas import CaptionStyle, ProcessingStatus
from app.models import VideoDocument

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Choose broker/backend based on mode (avoid Redis in debug/eager)
USE_EAGER = settings.debug or os.getenv("CELERY_EAGER", "0") == "1"
BROKER_URL = "memory://" if USE_EAGER else settings.celery_broker_url
RESULT_BACKEND = "cache+memory://" if USE_EAGER else settings.celery_result_backend

# Initialize Celery
celery_app = Celery(
    'reely_worker',
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=['app.tasks.worker']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    task_soft_time_limit=3300,  # 55 minutes
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

# Enable in-process execution for local/dev (no Redis needed)
if USE_EAGER:
    celery_app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
    )


@celery_app.task(bind=True, name='process_video')
def process_video_task(self, video_id: str, video_path: str, caption_style: dict):
    """Main task for processing video with captions"""
    try:
        logger.info(f"Starting video processing task for video_id: {video_id}")
        
        # Update task status
        self.update_state(
            state='PROGRESS',
            meta={'current_step': 'extracting_audio', 'progress': 10}
        )
        
        # Extract audio
        audio_filename = f"{video_id}_audio.wav"
        audio_path = os.path.join(settings.processed_dir, audio_filename)
        video_processor.extract_audio(video_path, audio_path)
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current_step': 'transcribing_audio', 'progress': 30}
        )
        
        # Transcribe audio
        caption_segments = transcription_service.transcribe_audio(audio_path, video_id)
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current_step': 'creating_captions', 'progress': 60}
        )
        
        # Create captioned video
        caption_style_obj = CaptionStyle(**caption_style)
        output_filename = f"{video_id}_captioned.mp4"
        output_path = os.path.join(settings.processed_dir, output_filename)
        
        video_processor.create_captioned_video(
            video_path,
            caption_segments,
            caption_style_obj,
            output_path
        )
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current_step': 'finalizing', 'progress': 90}
        )
        
        # Get video metadata
        metadata = video_processor.get_video_metadata(video_path)
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current_step': 'completed', 'progress': 100}
        )
        
        # Return result
        result = {
            'video_id': video_id,
            'status': 'completed',
            'processed_path': output_path,
            'audio_path': audio_path,
            'transcription': [seg.dict() for seg in caption_segments],
            'metadata': metadata,
            'caption_style': caption_style_obj.dict()
        }
        
        logger.info(f"Video processing completed for video_id: {video_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing video {video_id}: {e}")
        
        # Update task state with error
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'current_step': 'failed'}
        )
        
        raise


@celery_app.task(bind=True, name='transcribe_audio_only')
def transcribe_audio_task(self, video_id: str, audio_path: str):
    """Task for audio transcription only"""
    try:
        logger.info(f"Starting audio transcription for video_id: {video_id}")
        
        # Update task status
        self.update_state(
            state='PROGRESS',
            meta={'current_step': 'transcribing', 'progress': 50}
        )
        
        # Transcribe audio
        caption_segments = transcription_service.transcribe_audio(audio_path, video_id)
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current_step': 'completed', 'progress': 100}
        )
        
        result = {
            'video_id': video_id,
            'status': 'completed',
            'transcription': [seg.dict() for seg in caption_segments]
        }
        
        logger.info(f"Audio transcription completed for video_id: {video_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error transcribing audio {video_id}: {e}")
        
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'current_step': 'failed'}
        )
        
        raise


@celery_app.task(bind=True, name='create_captions_only')
def create_captions_task(self, video_id: str, video_path: str, transcription: list, caption_style: dict):
    """Task for creating captions only (when transcription already exists)"""
    try:
        logger.info(f"Starting caption creation for video_id: {video_id}")
        
        # Update task status
        self.update_state(
            state='PROGRESS',
            meta={'current_step': 'creating_captions', 'progress': 50}
        )
        
        # Convert transcription back to objects
        from app.models.schemas import CaptionSegment
        caption_segments = [CaptionSegment(**seg) for seg in transcription]
        
        # Create captioned video
        caption_style_obj = CaptionStyle(**caption_style)
        output_filename = f"{video_id}_captioned.mp4"
        output_path = os.path.join(settings.processed_dir, output_filename)
        
        video_processor.create_captioned_video(
            video_path,
            caption_segments,
            caption_style_obj,
            output_path
        )
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current_step': 'completed', 'progress': 100}
        )
        
        result = {
            'video_id': video_id,
            'status': 'completed',
            'processed_path': output_path,
            'caption_style': caption_style_obj.dict()
        }
        
        logger.info(f"Caption creation completed for video_id: {video_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error creating captions {video_id}: {e}")
        
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'current_step': 'failed'}
        )
        
        raise


@celery_app.task(bind=True, name='cleanup_files')
def cleanup_files_task(self, file_paths: list):
    """Task for cleaning up temporary files"""
    try:
        logger.info(f"Starting cleanup task for {len(file_paths)} files")
        
        cleaned_count = 0
        for file_path in file_paths:
            if storage_service.delete_file(file_path):
                cleaned_count += 1
        
        result = {
            'status': 'completed',
            'cleaned_files': cleaned_count,
            'total_files': len(file_paths)
        }
        
        logger.info(f"Cleanup completed: {cleaned_count}/{len(file_paths)} files")
        return result
        
    except Exception as e:
        logger.error(f"Error in cleanup task: {e}")
        raise


@worker_ready.connect
def worker_ready_handler(sender=None, **kwargs):
    """Handler for when worker is ready"""
    logger.info("Celery worker is ready")


@worker_shutdown.connect
def worker_shutdown_handler(sender=None, **kwargs):
    """Handler for when worker is shutting down"""
    logger.info("Celery worker is shutting down")
    # Cleanup any resources
    video_processor.cleanup_temp_files()


# Task status tracking
def get_task_status(task_id: str) -> dict:
    """Get status of a Celery task"""
    try:
        task = celery_app.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            return {
                'status': 'pending',
                'progress': 0,
                'current_step': 'queued'
            }
        elif task.state == 'PROGRESS':
            return {
                'status': 'processing',
                'progress': task.info.get('progress', 0),
                'current_step': task.info.get('current_step', 'processing')
            }
        elif task.state == 'SUCCESS':
            return {
                'status': 'completed',
                'progress': 100,
                'current_step': 'completed',
                'result': task.result
            }
        elif task.state == 'FAILURE':
            return {
                'status': 'failed',
                'progress': 0,
                'current_step': 'failed',
                'error': str(task.info)
            }
        else:
            return {
                'status': 'unknown',
                'progress': 0,
                'current_step': 'unknown'
            }
            
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        return {
            'status': 'error',
            'progress': 0,
            'current_step': 'error',
            'error': str(e)
        }
