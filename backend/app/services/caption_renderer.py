"""
Caption rendering service for creating styled captions
"""
import os
import logging
from typing import List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from pathlib import Path

from app.models.schemas import CaptionSegment, CaptionStyle

logger = logging.getLogger(__name__)


class CaptionRenderer:
    """Service for rendering captions with custom styling"""
    
    def __init__(self):
        self.font_cache = {}
        self.default_fonts = self._get_default_fonts()
    
    def _get_default_fonts(self) -> List[str]:
        """Get list of available system fonts"""
        try:
            # Try to find common font paths
            font_paths = [
                "/System/Library/Fonts/Arial.ttf",  # macOS
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
                "C:/Windows/Fonts/arial.ttf",  # Windows
                "C:/Windows/Fonts/calibri.ttf",  # Windows
            ]
            
            available_fonts = []
            for font_path in font_paths:
                if os.path.exists(font_path):
                    available_fonts.append(font_path)
            
            # If no system fonts found, use PIL's default
            if not available_fonts:
                available_fonts.append("default")
            
            return available_fonts
            
        except Exception as e:
            logger.warning(f"Error finding fonts: {e}")
            return ["default"]
    
    def _load_font(self, font_type: str, font_size: int) -> ImageFont.ImageFont:
        """Load font with caching"""
        cache_key = f"{font_type}_{font_size}"
        
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]
        
        try:
            # Try to load custom font
            if font_type.lower() != "default" and font_type.lower() != "arial":
                font_path = self._find_font_path(font_type)
                if font_path:
                    font = ImageFont.truetype(font_path, font_size)
                else:
                    # Fallback to default
                    font = ImageFont.load_default()
            else:
                # Use system default font
                font_path = self.default_fonts[0] if self.default_fonts[0] != "default" else None
                if font_path:
                    font = ImageFont.truetype(font_path, font_size)
                else:
                    font = ImageFont.load_default()
            
            self.font_cache[cache_key] = font
            return font
            
        except Exception as e:
            logger.warning(f"Error loading font {font_type}: {e}, using default")
            font = ImageFont.load_default()
            self.font_cache[cache_key] = font
            return font
    
    def _find_font_path(self, font_name: str) -> Optional[str]:
        """Find font file path by name"""
        try:
            # Common font directories
            font_dirs = [
                "/System/Library/Fonts/",  # macOS
                "/usr/share/fonts/",  # Linux
                "C:/Windows/Fonts/",  # Windows
            ]
            
            for font_dir in font_dirs:
                if os.path.exists(font_dir):
                    for file in os.listdir(font_dir):
                        if font_name.lower() in file.lower() and file.endswith(('.ttf', '.otf')):
                            return os.path.join(font_dir, file)
            
            return None
            
        except Exception as e:
            logger.warning(f"Error finding font {font_name}: {e}")
            return None
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        try:
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except Exception as e:
            logger.warning(f"Error converting color {hex_color}: {e}")
            return (255, 255, 255)  # Default to white
    
    def _wrap_text(self, text: str, font: ImageFont.ImageFont, max_width: int) -> List[str]:
        """Wrap text to fit within max_width"""
        try:
            words = text.split()
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                bbox = font.getbbox(test_line)
                text_width = bbox[2] - bbox[0]
                
                if text_width <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        # Single word is too long, add it anyway
                        lines.append(word)
            
            if current_line:
                lines.append(' '.join(current_line))
            
            return lines
            
        except Exception as e:
            logger.error(f"Error wrapping text: {e}")
            return [text]
    
    def create_caption_image(
        self, 
        text: str, 
        video_width: int, 
        video_height: int, 
        style: CaptionStyle,
        max_width_ratio: float = 0.8
    ) -> Image.Image:
        """Create caption image with specified styling"""
        try:
            # Calculate dimensions
            max_width = int(video_width * max_width_ratio)
            
            # Load font
            font = self._load_font(style.font_type, style.font_size)
            
            # Wrap text
            lines = self._wrap_text(text, font, max_width)
            
            # Calculate text dimensions
            line_height = style.font_size + 4  # Add some spacing
            total_height = len(lines) * line_height + style.padding * 2
            
            # Create image
            caption_img = Image.new('RGBA', (video_width, total_height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(caption_img)
            
            # Convert colors
            font_color = self._hex_to_rgb(style.font_color)
            stroke_color = self._hex_to_rgb(style.stroke_color)
            
            # Draw text lines
            y_offset = style.padding
            for line in lines:
                bbox = font.getbbox(line)
                text_width = bbox[2] - bbox[0]
                x_offset = (video_width - text_width) // 2
                
                # Draw stroke/outline
                if style.stroke_width > 0:
                    for dx in range(-style.stroke_width, style.stroke_width + 1):
                        for dy in range(-style.stroke_width, style.stroke_width + 1):
                            if dx*dx + dy*dy <= style.stroke_width*style.stroke_width:
                                draw.text(
                                    (x_offset + dx, y_offset + dy),
                                    line,
                                    font=font,
                                    fill=stroke_color
                                )
                
                # Draw main text
                draw.text(
                    (x_offset, y_offset),
                    line,
                    font=font,
                    fill=font_color
                )
                
                y_offset += line_height
            
            return caption_img
            
        except Exception as e:
            logger.error(f"Error creating caption image: {e}")
            raise
    
    def create_word_highlighted_caption(
        self,
        text: str,
        current_word: str,
        video_width: int,
        video_height: int,
        style: CaptionStyle,
        highlight_color: str = "#FFFF00"
    ) -> Image.Image:
        """Create caption with word highlighting"""
        try:
            # Calculate dimensions
            max_width = int(video_width * 0.8)
            
            # Load font
            font = self._load_font(style.font_type, style.font_size)
            
            # Wrap text
            lines = self._wrap_text(text, font, max_width)
            
            # Calculate text dimensions
            line_height = style.font_size + 4
            total_height = len(lines) * line_height + style.padding * 2
            
            # Create image
            caption_img = Image.new('RGBA', (video_width, total_height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(caption_img)
            
            # Convert colors
            font_color = self._hex_to_rgb(style.font_color)
            stroke_color = self._hex_to_rgb(style.stroke_color)
            highlight_rgb = self._hex_to_rgb(highlight_color)
            
            # Draw text lines with highlighting
            y_offset = style.padding
            for line in lines:
                words = line.split()
                x_offset = style.padding
                
                for word in words:
                    # Determine color
                    word_color = highlight_rgb if word.lower() == current_word.lower() else font_color
                    
                    # Draw stroke/outline
                    if style.stroke_width > 0:
                        stroke_col = stroke_color if word_color == font_color else font_color
                        for dx in range(-style.stroke_width, style.stroke_width + 1):
                            for dy in range(-style.stroke_width, style.stroke_width + 1):
                                if dx*dx + dy*dy <= style.stroke_width*style.stroke_width:
                                    draw.text(
                                        (x_offset + dx, y_offset + dy),
                                        word,
                                        font=font,
                                        fill=stroke_col
                                    )
                    
                    # Draw main text
                    draw.text(
                        (x_offset, y_offset),
                        word,
                        font=font,
                        fill=word_color
                    )
                    
                    # Move to next word position
                    bbox = font.getbbox(word)
                    x_offset += (bbox[2] - bbox[0]) + 4  # Add space between words
                
                y_offset += line_height
            
            return caption_img
            
        except Exception as e:
            logger.error(f"Error creating highlighted caption: {e}")
            raise
    
    def get_caption_position(
        self, 
        video_height: int, 
        caption_height: int, 
        position: str,
        padding: int = 20
    ) -> int:
        """Calculate Y position for caption based on position setting"""
        try:
            if position.lower() == "top":
                return padding
            elif position.lower() == "center":
                return (video_height - caption_height) // 2
            else:  # bottom
                return video_height - caption_height - padding
                
        except Exception as e:
            logger.warning(f"Error calculating position: {e}")
            return video_height - caption_height - 20  # Default to bottom
    
    def cleanup_font_cache(self):
        """Clean up font cache"""
        self.font_cache.clear()


# Global caption renderer instance
caption_renderer = CaptionRenderer()
