"""
Storage service for handling file operations and cloud storage
"""
import os
import hashlib
import aiofiles
import httpx
from typing import Optional, BinaryIO
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """Service for handling file storage operations"""
    
    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.processed_dir = Path(settings.processed_dir)
        self.s3_client = None
        
        # Initialize S3 client if AWS credentials are provided
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region
            )
    
    async def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """Save uploaded file to local storage"""
        try:
            file_path = self.upload_dir / filename
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
            
            logger.info(f"File saved locally: {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"Error saving uploaded file: {e}")
            raise
    
    async def download_video_from_url(self, url: str, filename: str) -> str:
        """Download video from URL and save locally"""
        try:
            async with httpx.AsyncClient() as client:
                async with client.stream('GET', url) as response:
                    response.raise_for_status()
                    
                    file_path = self.upload_dir / filename
                    async with aiofiles.open(file_path, 'wb') as f:
                        async for chunk in response.aiter_bytes():
                            await f.write(chunk)
            
            logger.info(f"Video downloaded from URL: {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"Error downloading video from URL: {e}")
            raise
    
    async def save_processed_video(self, video_content: bytes, filename: str) -> str:
        """Save processed video to local storage"""
        try:
            file_path = self.processed_dir / filename
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(video_content)
            
            logger.info(f"Processed video saved: {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"Error saving processed video: {e}")
            raise
    
    def get_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of file for caching purposes"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating file hash: {e}")
            raise
    
    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        try:
            return os.path.getsize(file_path)
        except Exception as e:
            logger.error(f"Error getting file size: {e}")
            raise
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file from local storage"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"File deleted: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    async def upload_to_s3(self, file_path: str, s3_key: str) -> Optional[str]:
        """Upload file to S3 bucket"""
        if not self.s3_client:
            logger.warning("S3 client not initialized, skipping upload")
            return None
        
        try:
            self.s3_client.upload_file(file_path, settings.s3_bucket_name, s3_key)
            s3_url = f"https://{settings.s3_bucket_name}.s3.{settings.aws_region}.amazonaws.com/{s3_key}"
            logger.info(f"File uploaded to S3: {s3_url}")
            return s3_url
        except ClientError as e:
            logger.error(f"Error uploading to S3: {e}")
            raise
    
    async def download_from_s3(self, s3_key: str, local_path: str) -> str:
        """Download file from S3 bucket"""
        if not self.s3_client:
            raise ValueError("S3 client not initialized")
        
        try:
            self.s3_client.download_file(settings.s3_bucket_name, s3_key, local_path)
            logger.info(f"File downloaded from S3: {local_path}")
            return local_path
        except ClientError as e:
            logger.error(f"Error downloading from S3: {e}")
            raise
    
    def generate_unique_filename(self, original_filename: str, prefix: str = "") -> str:
        """Generate unique filename with timestamp"""
        import uuid
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        name, ext = os.path.splitext(original_filename)
        
        if prefix:
            return f"{prefix}_{timestamp}_{unique_id}{ext}"
        return f"{timestamp}_{unique_id}_{name}{ext}"
    
    def ensure_directory_exists(self, directory: str) -> None:
        """Ensure directory exists, create if not"""
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    def get_available_space(self) -> int:
        """Get available disk space in bytes"""
        try:
            statvfs = os.statvfs(self.upload_dir)
            return statvfs.f_frsize * statvfs.f_bavail
        except Exception as e:
            logger.error(f"Error getting available space: {e}")
            return 0


# Global storage service instance
storage_service = StorageService()
