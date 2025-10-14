"""
Test suite for backend services
"""
import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock
from PIL import Image
import numpy as np

from app.services.storage import StorageService
from app.services.transcription import TranscriptionService
from app.services.caption_renderer import CaptionRenderer
from app.services.video_processor import VideoProcessor
from app.models.schemas import CaptionSegment, CaptionStyle

class TestStorageService:
    """Test storage service functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.storage = StorageService()
        self.test_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_generate_unique_filename(self):
        """Test unique filename generation"""
        filename = self.storage.generate_unique_filename("test.mp4")
        assert filename.endswith(".mp4")
        assert "test" in filename
        assert len(filename) > len("test.mp4")
        
        # Test with prefix
        filename_with_prefix = self.storage.generate_unique_filename("test.mp4", "video")
        assert filename_with_prefix.startswith("video_")
        assert filename_with_prefix.endswith(".mp4")
    
    def test_ensure_directory_exists(self):
        """Test directory creation"""
        test_path = os.path.join(self.test_dir, "new_dir")
        self.storage.ensure_directory_exists(test_path)
        assert os.path.exists(test_path)
        assert os.path.isdir(test_path)
    
    def test_get_file_hash(self):
        """Test file hash calculation"""
        test_file = os.path.join(self.test_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test content")
        
        hash1 = self.storage.get_file_hash(test_file)
        hash2 = self.storage.get_file_hash(test_file)
        
        assert hash1 == hash2
        assert len(hash1) == 32  # MD5 hash length
        
        # Different content should produce different hash
        with open(test_file, "w") as f:
            f.write("different content")
        
        hash3 = self.storage.get_file_hash(test_file)
        assert hash1 != hash3
    
    def test_get_file_size(self):
        """Test file size calculation"""
        test_file = os.path.join(self.test_dir, "test.txt")
        content = "test content"
        
        with open(test_file, "w") as f:
            f.write(content)
        
        size = self.storage.get_file_size(test_file)
        assert size == len(content.encode('utf-8'))
    
    def test_delete_file(self):
        """Test file deletion"""
        test_file = os.path.join(self.test_dir, "test.txt")
        
        # Create file
        with open(test_file, "w") as f:
            f.write("test content")
        
        assert os.path.exists(test_file)
        
        # Delete file
        result = self.storage.delete_file(test_file)
        assert result is True
        assert not os.path.exists(test_file)
        
        # Try to delete non-existent file
        result = self.storage.delete_file("non_existent.txt")
        assert result is False

class TestCaptionRenderer:
    """Test caption renderer functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.renderer = CaptionRenderer()
    
    def test_hex_to_rgb_conversion(self):
        """Test hex to RGB conversion"""
        # Test valid hex colors
        assert self.renderer._hex_to_rgb("#FFFFFF") == (255, 255, 255)
        assert self.renderer._hex_to_rgb("#000000") == (0, 0, 0)
        assert self.renderer._hex_to_rgb("#FF0000") == (255, 0, 0)
        assert self.renderer._hex_to_rgb("#00FF00") == (0, 255, 0)
        assert self.renderer._hex_to_rgb("#0000FF") == (0, 0, 255)
        
        # Test hex without #
        assert self.renderer._hex_to_rgb("FFFFFF") == (255, 255, 255)
        
        # Test invalid hex (should return white as fallback)
        assert self.renderer._hex_to_rgb("invalid") == (255, 255, 255)
    
    def test_text_wrapping(self):
        """Test text wrapping functionality"""
        font = self.renderer._load_font("Arial", 24)
        
        # Test short text (no wrapping needed)
        short_text = "Hello world"
        wrapped = self.renderer._wrap_text(short_text, font, 1000)
        assert wrapped == ["Hello world"]
        
        # Test long text (wrapping needed)
        long_text = "This is a very long text that should be wrapped into multiple lines when the width is limited"
        wrapped = self.renderer._wrap_text(long_text, font, 200)
        assert len(wrapped) > 1
        assert all(len(line) > 0 for line in wrapped)
    
    def test_caption_image_creation(self):
        """Test caption image creation"""
        style = CaptionStyle(
            font_type="Arial",
            font_size=24,
            font_color="#FFFFFF",
            stroke_color="#000000",
            stroke_width=2,
            padding=10,
            position="bottom"
        )
        
        # Create caption image
        caption_img = self.renderer.create_caption_image(
            "Test caption",
            1920,  # video width
            1080,  # video height
            style
        )
        
        assert isinstance(caption_img, Image.Image)
        assert caption_img.size[0] == 1920  # width
        assert caption_img.size[1] > 0  # height
    
    def test_caption_position_calculation(self):
        """Test caption position calculation"""
        video_height = 1080
        caption_height = 100
        
        # Test top position
        y_pos = self.renderer.get_caption_position(video_height, caption_height, "top", 20)
        assert y_pos == 20
        
        # Test center position
        y_pos = self.renderer.get_caption_position(video_height, caption_height, "center", 20)
        expected_center = (video_height - caption_height) // 2
        assert y_pos == expected_center
        
        # Test bottom position
        y_pos = self.renderer.get_caption_position(video_height, caption_height, "bottom", 20)
        expected_bottom = video_height - caption_height - 20
        assert y_pos == expected_bottom

class TestVideoProcessor:
    """Test video processor functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.processor = VideoProcessor()
    
    def test_caption_position_calculation(self):
        """Test caption position calculation"""
        video_height = 1080
        caption_height = 100
        padding = 20
        
        # Test top position
        y_pos = self.processor._calculate_caption_position(video_height, caption_height, "top", padding)
        assert y_pos == padding
        
        # Test center position
        y_pos = self.processor._calculate_caption_position(video_height, caption_height, "center", padding)
        expected_center = (video_height - caption_height) // 2
        assert y_pos == expected_center
        
        # Test bottom position
        y_pos = self.processor._calculate_caption_position(video_height, caption_height, "bottom", padding)
        expected_bottom = video_height - caption_height - padding
        assert y_pos == expected_bottom
    
    def test_word_timing_split(self):
        """Test word timing split functionality"""
        segment = CaptionSegment(
            start_time=0.0,
            end_time=10.0,
            text="Hello world test",
            confidence=0.95
        )
        
        word_timings = self.processor._split_segment_into_words(segment)
        
        assert len(word_timings) == 3  # "Hello", "world", "test"
        assert word_timings[0]["word"] == "Hello"
        assert word_timings[1]["word"] == "world"
        assert word_timings[2]["word"] == "test"
        
        # Check timing
        assert word_timings[0]["start"] == 0.0
        assert word_timings[2]["end"] == 10.0
        
        # Check that timings are sequential
        for i in range(len(word_timings) - 1):
            assert word_timings[i]["end"] <= word_timings[i + 1]["start"]

class TestTranscriptionService:
    """Test transcription service functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        # Mock Whisper model to avoid loading actual model in tests
        with patch('app.services.transcription.whisper.load_model') as mock_load:
            mock_model = Mock()
            mock_load.return_value = mock_model
            self.service = TranscriptionService()
    
    def test_model_info(self):
        """Test model information retrieval"""
        info = self.service.get_model_info()
        
        assert "model_name" in info
        assert "available_models" in info
        assert isinstance(info["available_models"], list)
    
    def test_segment_conversion(self):
        """Test Whisper result to segment conversion"""
        # Mock Whisper result
        whisper_result = {
            "segments": [
                {
                    "start": 0.0,
                    "end": 5.0,
                    "text": "Hello world",
                    "avg_logprob": -0.5
                },
                {
                    "start": 5.0,
                    "end": 10.0,
                    "text": "How are you?",
                    "avg_logprob": -0.3
                }
            ]
        }
        
        segments = self.service._convert_to_segments(whisper_result)
        
        assert len(segments) == 2
        assert segments[0].start_time == 0.0
        assert segments[0].end_time == 5.0
        assert segments[0].text == "Hello world"
        assert segments[0].confidence == -0.5
        
        assert segments[1].start_time == 5.0
        assert segments[1].end_time == 10.0
        assert segments[1].text == "How are you?"
        assert segments[1].confidence == -0.3

class TestIntegration:
    """Integration tests for services"""
    
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
        
        assert style.font_type == "Arial"
        assert style.font_size == 24
        assert style.font_color == "#FFFFFF"
        assert style.stroke_color == "#000000"
        assert style.stroke_width == 2
        assert style.padding == 10
        assert style.position == "bottom"
    
    def test_caption_segment_validation(self):
        """Test caption segment validation"""
        segment = CaptionSegment(
            start_time=0.0,
            end_time=5.0,
            text="Hello world",
            confidence=0.95
        )
        
        assert segment.start_time == 0.0
        assert segment.end_time == 5.0
        assert segment.text == "Hello world"
        assert segment.confidence == 0.95
    
    @pytest.mark.asyncio
    async def test_storage_operations(self):
        """Test async storage operations"""
        storage = StorageService()
        
        # Test async file operations
        test_content = b"test file content"
        filename = "test_async.txt"
        
        # This would normally be async, but we'll test the sync parts
        file_path = os.path.join(tempfile.gettempdir(), filename)
        
        try:
            # Test file operations
            with open(file_path, 'wb') as f:
                f.write(test_content)
            
            file_size = storage.get_file_size(file_path)
            assert file_size == len(test_content)
            
            file_hash = storage.get_file_hash(file_path)
            assert len(file_hash) == 32
            
            # Cleanup
            storage.delete_file(file_path)
            assert not os.path.exists(file_path)
            
        except Exception as e:
            # Cleanup on error
            if os.path.exists(file_path):
                storage.delete_file(file_path)
            raise e

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
