"""
Comprehensive test suite for the Reely API
"""
import pytest
import asyncio
import os
import tempfile
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient

from app.main import app
from app.core.config import settings
from app.models.schemas import CaptionStyle, ProcessingStatus
from app.services.storage import StorageService
from app.services.transcription import TranscriptionService
from app.services.video_processor import VideoProcessor

# Test client
client = TestClient(app)

@pytest.fixture
def mock_database():
    """Mock database for testing"""
    with patch('app.api.dependencies.database') as mock_db:
        mock_collection = AsyncMock()
        mock_db.get_collection.return_value = mock_collection
        yield mock_db, mock_collection

@pytest.fixture
def sample_video_data():
    """Sample video data for testing"""
    return {
        "video_id": "test-video-123",
        "filename": "test-video.mp4",
        "status": "completed",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:05:00Z",
        "original_path": "/uploads/test-video.mp4",
        "processed_path": "/processed/test-video-captioned.mp4",
        "metadata": {
            "duration": 120.5,
            "width": 1920,
            "height": 1080,
            "fps": 30.0,
            "format": "mp4",
            "size_bytes": 1024000
        },
        "transcription": [
            {
                "start_time": 0.0,
                "end_time": 5.0,
                "text": "Hello, welcome to our video.",
                "confidence": 0.95
            }
        ],
        "caption_style": {
            "font_type": "Arial",
            "font_size": 24,
            "font_color": "#FFFFFF",
            "stroke_color": "#000000",
            "stroke_width": 2,
            "padding": 10,
            "position": "bottom"
        }
    }

class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Welcome to Reely API"
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Reely API"
    
    def test_api_health_endpoint(self, mock_database):
        """Test API health endpoint"""
        mock_db, mock_collection = mock_database
        mock_db.client.admin.command = AsyncMock(return_value={"ok": 1})
        
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"

class TestVideoUpload:
    """Test video upload functionality"""
    
    def test_upload_without_file_or_url(self):
        """Test upload without file or URL"""
        response = client.post("/api/upload")
        assert response.status_code == 422  # Validation error
    
    def test_upload_with_invalid_file_type(self):
        """Test upload with invalid file type"""
        with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
            temp_file.write(b"test content")
            temp_file.flush()
            
            with open(temp_file.name, "rb") as f:
                response = client.post(
                    "/api/upload",
                    files={"video_file": ("test.txt", f, "text/plain")},
                    data={
                        "font_type": "Arial",
                        "font_size": "24",
                        "font_color": "#FFFFFF",
                        "stroke_color": "#000000",
                        "stroke_width": "2",
                        "padding": "10",
                        "position": "bottom"
                    }
                )
                assert response.status_code == 400
                assert "Unsupported video format" in response.json()["detail"]
    
    def test_upload_with_valid_file(self, mock_database):
        """Test upload with valid video file"""
        mock_db, mock_collection = mock_database
        mock_collection.insert_one = AsyncMock()
        mock_collection.update_one = AsyncMock()
        
        # Mock file operations
        with patch('app.services.storage.storage_service') as mock_storage:
            mock_storage.save_uploaded_file = AsyncMock(return_value="/uploads/test.mp4")
            mock_storage.generate_unique_filename.return_value = "test.mp4"
            
            # Mock Celery task
            with patch('app.tasks.worker.process_video_task') as mock_task:
                mock_task.delay.return_value = Mock(id="task-123")
                
                with tempfile.NamedTemporaryFile(suffix=".mp4") as temp_file:
                    temp_file.write(b"fake video content")
                    temp_file.flush()
                    
                    with open(temp_file.name, "rb") as f:
                        response = client.post(
                            "/api/upload",
                            files={"video_file": ("test.mp4", f, "video/mp4")},
                            data={
                                "font_type": "Arial",
                                "font_size": "24",
                                "font_color": "#FFFFFF",
                                "stroke_color": "#000000",
                                "stroke_width": "2",
                                "padding": "10",
                                "position": "bottom"
                            }
                        )
                        assert response.status_code == 200
                        data = response.json()
                        assert "video_id" in data
                        assert data["status"] == "pending"
    
    def test_upload_with_url(self, mock_database):
        """Test upload with video URL"""
        mock_db, mock_collection = mock_database
        mock_collection.insert_one = AsyncMock()
        mock_collection.update_one = AsyncMock()
        
        # Mock URL download
        with patch('app.services.storage.storage_service') as mock_storage:
            mock_storage.download_video_from_url = AsyncMock(return_value="/uploads/test.mp4")
            mock_storage.generate_unique_filename.return_value = "test.mp4"
            
            # Mock Celery task
            with patch('app.tasks.worker.process_video_task') as mock_task:
                mock_task.delay.return_value = Mock(id="task-123")
                
                response = client.post(
                    "/api/upload",
                    data={
                        "video_url": "https://example.com/video.mp4",
                        "font_type": "Arial",
                        "font_size": "24",
                        "font_color": "#FFFFFF",
                        "stroke_color": "#000000",
                        "stroke_width": "2",
                        "padding": "10",
                        "position": "bottom"
                    }
                )
                assert response.status_code == 200
                data = response.json()
                assert "video_id" in data
                assert data["status"] == "pending"

class TestVideoManagement:
    """Test video management endpoints"""
    
    def test_get_videos_empty(self, mock_database):
        """Test getting videos when none exist"""
        mock_db, mock_collection = mock_database
        mock_collection.count_documents = AsyncMock(return_value=0)
        mock_collection.find.return_value.to_list = AsyncMock(return_value=[])
        
        response = client.get("/api/videos")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["videos"]) == 0
    
    def test_get_videos_with_data(self, mock_database, sample_video_data):
        """Test getting videos with data"""
        mock_db, mock_collection = mock_database
        mock_collection.count_documents = AsyncMock(return_value=1)
        mock_collection.find.return_value.to_list = AsyncMock(return_value=[sample_video_data])
        
        response = client.get("/api/videos")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["videos"]) == 1
        assert data["videos"][0]["video_id"] == "test-video-123"
    
    def test_get_video_details(self, mock_database, sample_video_data):
        """Test getting video details"""
        mock_db, mock_collection = mock_database
        mock_collection.find_one = AsyncMock(return_value=sample_video_data)
        
        response = client.get("/api/video/test-video-123")
        assert response.status_code == 200
        data = response.json()
        assert data["video_id"] == "test-video-123"
        assert data["filename"] == "test-video.mp4"
    
    def test_get_video_not_found(self, mock_database):
        """Test getting non-existent video"""
        mock_db, mock_collection = mock_database
        mock_collection.find_one = AsyncMock(return_value=None)
        
        response = client.get("/api/video/non-existent")
        assert response.status_code == 404
        assert "Video not found" in response.json()["detail"]
    
    def test_delete_video(self, mock_database):
        """Test deleting video"""
        mock_db, mock_collection = mock_database
        mock_collection.find_one = AsyncMock(return_value={
            "video_id": "test-video-123",
            "original_path": "/uploads/test.mp4",
            "processed_path": "/processed/test.mp4"
        })
        mock_collection.delete_one = AsyncMock()
        
        # Mock file deletion
        with patch('app.services.storage.storage_service') as mock_storage:
            mock_storage.delete_file.return_value = True
            
            response = client.delete("/api/video/test-video-123")
            assert response.status_code == 200
            assert "deleted successfully" in response.json()["message"]

class TestCaptionProcessing:
    """Test caption processing functionality"""
    
    def test_create_captions(self, mock_database):
        """Test creating captions for existing video"""
        mock_db, mock_collection = mock_database
        mock_collection.find_one = AsyncMock(return_value={
            "video_id": "test-video-123",
            "status": "completed",
            "original_path": "/uploads/test.mp4"
        })
        mock_collection.update_one = AsyncMock()
        
        # Mock Celery task
        with patch('app.tasks.worker.process_video_task') as mock_task:
            mock_task.delay.return_value = Mock(id="task-123")
            
            response = client.post(
                "/api/caption",
                json={
                    "video_id": "test-video-123",
                    "caption_style": {
                        "font_type": "Arial",
                        "font_size": 24,
                        "font_color": "#FFFFFF",
                        "stroke_color": "#000000",
                        "stroke_width": 2,
                        "padding": 10,
                        "position": "bottom"
                    }
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["video_id"] == "test-video-123"
            assert data["status"] == "processing"

class TestServices:
    """Test service classes"""
    
    def test_storage_service(self):
        """Test storage service functionality"""
        storage = StorageService()
        
        # Test filename generation
        filename = storage.generate_unique_filename("test.mp4")
        assert filename.endswith(".mp4")
        assert "test" in filename
        
        # Test directory creation
        storage.ensure_directory_exists("./test_dir")
        assert os.path.exists("./test_dir")
        os.rmdir("./test_dir")
    
    def test_caption_style_validation(self):
        """Test caption style validation"""
        # Valid style
        style = CaptionStyle(
            font_type="Arial",
            font_size=24,
            font_color="#FFFFFF",
            stroke_color="#000000",
            stroke_width=2,
            padding=10,
            position="bottom"
        )
        assert style.font_size == 24
        assert style.font_color == "#FFFFFF"
        
        # Invalid font size
        with pytest.raises(ValueError):
            CaptionStyle(font_size=100)  # Too large
        
        # Invalid stroke width
        with pytest.raises(ValueError):
            CaptionStyle(stroke_width=15)  # Too large

class TestErrorHandling:
    """Test error handling"""
    
    def test_invalid_video_format(self):
        """Test handling of invalid video format"""
        with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
            temp_file.write(b"not a video")
            temp_file.flush()
            
            with open(temp_file.name, "rb") as f:
                response = client.post(
                    "/api/upload",
                    files={"video_file": ("test.txt", f, "text/plain")},
                    data={"font_type": "Arial"}
                )
                assert response.status_code == 400
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields"""
        response = client.post("/api/upload", data={})
        assert response.status_code == 422  # Validation error
    
    def test_database_connection_error(self):
        """Test handling of database connection errors"""
        with patch('app.api.dependencies.database') as mock_db:
            mock_db.get_collection.side_effect = Exception("Database connection failed")
            
            response = client.get("/api/videos")
            assert response.status_code == 500

# Integration tests
class TestIntegration:
    """Integration tests"""

    @pytest.mark.asyncio
    async def test_full_workflow(self, mock_database):
        """Test complete video processing workflow"""
        mock_db, mock_collection = mock_database
        
        # Mock all database operations
        mock_collection.insert_one = AsyncMock()
        mock_collection.update_one = AsyncMock()
        mock_collection.find_one = AsyncMock(return_value={
            "video_id": "test-123",
            "status": "processing",
            "original_path": "/uploads/test.mp4"
        })
        
        # Mock file operations
        with patch('app.services.storage.storage_service') as mock_storage:
            mock_storage.save_uploaded_file = AsyncMock(return_value="/uploads/test.mp4")
            mock_storage.generate_unique_filename.return_value = "test.mp4"
            
            # Mock video processing
            with patch('app.services.video_processor.video_processor') as mock_processor:
                mock_processor.extract_audio.return_value = "/processed/test.wav"
                mock_processor.get_video_metadata.return_value = {
                    "duration": 120,
                    "width": 1920,
                    "height": 1080,
                    "fps": 30,
                    "format": "mp4",
                    "size_bytes": 1024000
                }
                mock_processor.create_captioned_video.return_value = "/processed/test-captioned.mp4"
                
                # Mock transcription
                with patch('app.services.transcription.transcription_service') as mock_transcription:
                    from app.models.schemas import CaptionSegment
                    mock_transcription.transcribe_audio = AsyncMock(return_value=[
                        CaptionSegment(
                            start_time=0.0,
                            end_time=5.0,
                            text="Hello world",
                            confidence=0.95
                        )
                    ])
                    
                    # Mock Celery task
                    with patch('app.tasks.worker.process_video_task') as mock_task:
                        mock_task.delay.return_value = Mock(id="task-123")
                        
                        # Upload video
                        with tempfile.NamedTemporaryFile(suffix=".mp4") as temp_file:
                            temp_file.write(b"fake video content")
                            temp_file.flush()
                            
                            with open(temp_file.name, "rb") as f:
                                upload_response = client.post(
                                    "/api/upload",
                                    files={"video_file": ("test.mp4", f, "video/mp4")},
                                    data={"font_type": "Arial"}
                                )
                                assert upload_response.status_code == 200
                                
                                video_id = upload_response.json()["video_id"]
                                
                                # Check video status
                                status_response = client.get(f"/api/video/{video_id}/status")
                                assert status_response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"])