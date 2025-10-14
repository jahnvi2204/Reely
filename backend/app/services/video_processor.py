"""
Video processing service for audio extraction and caption overlay
"""
import os
import logging
from typing import List, Optional, Tuple
from pathlib import Path
"""Lazy import of heavy video libraries to avoid import-time failures in test envs"""
import tempfile

from app.core.config import settings
from app.models.schemas import CaptionSegment, CaptionStyle
from app.services.caption_renderer import caption_renderer
from app.services.storage import storage_service

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Service for video processing operations"""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "reely_processing"
        self.temp_dir.mkdir(exist_ok=True)
    
    def extract_audio(self, video_path: str, output_path: str) -> str:
        """Extract audio from video file"""
        try:
            from moviepy.editor import VideoFileClip
            logger.info(f"Extracting audio from {video_path}")
            
            with VideoFileClip(video_path) as video:
                audio = video.audio
                if audio is None:
                    raise ValueError("No audio track found in video")
                
                audio.write_audiofile(output_path, verbose=False, logger=None)
                audio.close()
            
            logger.info(f"Audio extracted to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error extracting audio: {e}")
            raise
    
    def get_video_metadata(self, video_path: str) -> dict:
        """Get video metadata information"""
        try:
            from moviepy.editor import VideoFileClip
            with VideoFileClip(video_path) as video:
                metadata = {
                    "duration": video.duration,
                    "width": video.w,
                    "height": video.h,
                    "fps": video.fps,
                    "format": Path(video_path).suffix.lower(),
                    "size_bytes": os.path.getsize(video_path)
                }
            
            logger.info(f"Video metadata extracted: {metadata}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error getting video metadata: {e}")
            raise
    
    def create_captioned_video(
        self,
        video_path: str,
        caption_segments: List[CaptionSegment],
        caption_style: CaptionStyle,
        output_path: str
    ) -> str:
        """Create video with captions overlaid"""
        try:
            from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
            logger.info(f"Creating captioned video: {output_path}")
            
            with VideoFileClip(video_path) as video:
                # Get video dimensions
                video_width, video_height = video.size
                
                # Create caption clips
                caption_clips = []
                
                for segment in caption_segments:
                    # Create caption image
                    caption_img = caption_renderer.create_caption_image(
                        segment.text,
                        video_width,
                        video_height,
                        caption_style
                    )
                    
                    # Save caption image temporarily
                    temp_img_path = self.temp_dir / f"caption_{segment.start_time}.png"
                    caption_img.save(temp_img_path)
                    
                    # Create text clip
                    caption_clip = ImageClip(str(temp_img_path), duration=segment.end_time - segment.start_time)
                    caption_clip = caption_clip.set_start(segment.start_time)
                    
                    # Position caption
                    y_position = self._calculate_caption_position(
                        video_height,
                        caption_img.height,
                        caption_style.position,
                        caption_style.padding
                    )
                    caption_clip = caption_clip.set_position(('center', y_position))
                    
                    caption_clips.append(caption_clip)
                
                # Composite video with captions
                final_video = CompositeVideoClip([video] + caption_clips)
                
                # Write final video
                final_video.write_videofile(
                    output_path,
                    codec='libx264',
                    audio_codec='aac',
                    verbose=False,
                    logger=None
                )
                
                # Clean up
                final_video.close()
                for clip in caption_clips:
                    clip.close()
            
            logger.info(f"Captioned video created: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating captioned video: {e}")
            raise
    
    def create_word_highlighted_video(
        self,
        video_path: str,
        caption_segments: List[CaptionSegment],
        caption_style: CaptionStyle,
        output_path: str
    ) -> str:
        """Create video with word-level highlighting"""
        try:
            from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
            logger.info(f"Creating word-highlighted video: {output_path}")
            
            with VideoFileClip(video_path) as video:
                video_width, video_height = video.size
                caption_clips = []
                
                for segment in caption_segments:
                    # Split segment into words with timing
                    word_timings = self._split_segment_into_words(segment)
                    
                    for word_timing in word_timings:
                        # Create highlighted caption
                        caption_img = caption_renderer.create_word_highlighted_caption(
                            segment.text,
                            word_timing["word"],
                            video_width,
                            video_height,
                            caption_style
                        )
                        
                        # Save caption image
                        temp_img_path = self.temp_dir / f"highlight_{word_timing['start']}.png"
                        caption_img.save(temp_img_path)
                        
                        # Create clip
                        caption_clip = ImageClip(
                            str(temp_img_path),
                            duration=word_timing["end"] - word_timing["start"]
                        )
                        caption_clip = caption_clip.set_start(word_timing["start"])
                        
                        # Position caption
                        y_position = self._calculate_caption_position(
                            video_height,
                            caption_img.height,
                            caption_style.position,
                            caption_style.padding
                        )
                        caption_clip = caption_clip.set_position(('center', y_position))
                        
                        caption_clips.append(caption_clip)
                
                # Composite video
                final_video = CompositeVideoClip([video] + caption_clips)
                
                # Write final video
                final_video.write_videofile(
                    output_path,
                    codec='libx264',
                    audio_codec='aac',
                    verbose=False,
                    logger=None
                )
                
                # Clean up
                final_video.close()
                for clip in caption_clips:
                    clip.close()
            
            logger.info(f"Word-highlighted video created: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating word-highlighted video: {e}")
            raise
    
    def _split_segment_into_words(self, segment: CaptionSegment) -> List[dict]:
        """Split caption segment into word-level timings"""
        try:
            words = segment.text.split()
            word_count = len(words)
            segment_duration = segment.end_time - segment.start_time
            
            # Simple word timing calculation
            # In a real implementation, you'd use Whisper's word-level timestamps
            word_timings = []
            time_per_word = segment_duration / word_count
            
            for i, word in enumerate(words):
                start_time = segment.start_time + (i * time_per_word)
                end_time = segment.start_time + ((i + 1) * time_per_word)
                
                word_timings.append({
                    "word": word,
                    "start": start_time,
                    "end": end_time
                })
            
            return word_timings
            
        except Exception as e:
            logger.error(f"Error splitting segment into words: {e}")
            return []
    
    def _calculate_caption_position(
        self,
        video_height: int,
        caption_height: int,
        position: str,
        padding: int = 20
    ) -> int:
        """Calculate Y position for caption"""
        try:
            if position.lower() == "top":
                return padding
            elif position.lower() == "center":
                return (video_height - caption_height) // 2
            else:  # bottom
                return video_height - caption_height - padding
                
        except Exception as e:
            logger.warning(f"Error calculating caption position: {e}")
            return video_height - caption_height - padding
    
    def resize_video(self, video_path: str, output_path: str, max_width: int = 1920) -> str:
        """Resize video to maximum width while maintaining aspect ratio"""
        try:
            from moviepy.editor import VideoFileClip
            logger.info(f"Resizing video: {video_path}")
            
            with VideoFileClip(video_path) as video:
                # Calculate new dimensions
                width, height = video.size
                if width <= max_width:
                    # No resize needed
                    video.write_videofile(output_path, verbose=False, logger=None)
                    return output_path
                
                # Calculate new height maintaining aspect ratio
                new_height = int((height * max_width) / width)
                
                # Resize video
                resized_video = video.resize((max_width, new_height))
                resized_video.write_videofile(output_path, verbose=False, logger=None)
                resized_video.close()
            
            logger.info(f"Video resized: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error resizing video: {e}")
            raise
    
    def compress_video(self, video_path: str, output_path: str, quality: str = "medium") -> str:
        """Compress video for smaller file size"""
        try:
            from moviepy.editor import VideoFileClip
            logger.info(f"Compressing video: {video_path}")
            
            # Quality settings
            quality_settings = {
                "low": {"bitrate": "500k", "crf": 28},
                "medium": {"bitrate": "1000k", "crf": 23},
                "high": {"bitrate": "2000k", "crf": 18}
            }
            
            settings = quality_settings.get(quality, quality_settings["medium"])
            
            with VideoFileClip(video_path) as video:
                video.write_videofile(
                    output_path,
                    codec='libx264',
                    audio_codec='aac',
                    bitrate=settings["bitrate"],
                    verbose=False,
                    logger=None
                )
            
            logger.info(f"Video compressed: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error compressing video: {e}")
            raise
    
    def create_thumbnail(self, video_path: str, output_path: str, timestamp: float = 1.0) -> str:
        """Create thumbnail from video at specified timestamp"""
        try:
            from moviepy.editor import VideoFileClip
            from PIL import Image
            logger.info(f"Creating thumbnail from {video_path}")
            
            with VideoFileClip(video_path) as video:
                # Ensure timestamp is within video duration
                timestamp = min(timestamp, video.duration - 0.1)
                
                # Get frame at timestamp
                frame = video.get_frame(timestamp)
                
                # Convert to PIL Image
                img = Image.fromarray(frame)
                
                # Save thumbnail
                img.save(output_path)
            
            logger.info(f"Thumbnail created: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating thumbnail: {e}")
            raise
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            for file_path in self.temp_dir.glob("*"):
                if file_path.is_file():
                    file_path.unlink()
            logger.info("Temporary files cleaned up")
        except Exception as e:
            logger.warning(f"Error cleaning up temp files: {e}")


# Global video processor instance
video_processor = VideoProcessor()
