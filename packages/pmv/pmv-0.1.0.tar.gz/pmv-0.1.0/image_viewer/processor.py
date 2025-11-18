"""Image processing utilities for loading and manipulating images."""

import io
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw


class ImageProcessor:
    """Handles image loading, processing, and manipulation."""
    
    @staticmethod
    def load_from_file(image_path: str) -> bytes:
        """
        Load an image from a file path and convert it to PNG bytes.
        Supports multiple image formats (JPEG, PNG, GIF, BMP, WEBP, etc.).
        
        Args:
            image_path: Path to the image file
            
        Returns:
            The image data as PNG bytes
            
        Raises:
            FileNotFoundError: If the image file doesn't exist
            ValueError: If the path is not a file
        """
        path = Path(image_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        if not path.is_file():
            raise ValueError(f"Path is not a file: {image_path}")
        
        # Open the image with Pillow (supports many formats)
        img = Image.open(path)
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create a white background for transparent images
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            if img.mode in ('RGBA', 'LA'):
                background.paste(img, mask=img.split()[-1])
                img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Save to PNG format in memory
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    @staticmethod
    def fit_to_dimensions(image_bytes: bytes, max_width: int, max_height: int) -> bytes:
        """
        Resize an image to fit within specified dimensions while maintaining aspect ratio.
        Only downscales images that are too large.
        
        Args:
            image_bytes: Original image data as bytes
            max_width: Maximum width in pixels
            max_height: Maximum height in pixels
            
        Returns:
            Resized image as PNG bytes
        """
        # Open the image
        img = Image.open(io.BytesIO(image_bytes))
        
        # Get original dimensions
        orig_width, orig_height = img.size
        
        # Calculate scaling to ensure image fits within bounds
        width_scale = max_width / orig_width
        height_scale = max_height / orig_height
        
        # Use the smaller scale to ensure image fits in both dimensions
        scale = min(width_scale, height_scale)
        
        # Only resize if scale is less than 1 (image is too large)
        if scale < 1.0:
            new_width = int(orig_width * scale)
            new_height = int(orig_height * scale)
            
            # Ensure dimensions are at least 1 pixel
            new_width = max(1, new_width)
            new_height = max(1, new_height)
            
            # Resize image with high quality
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            if img.mode in ('RGBA', 'LA'):
                background.paste(img, mask=img.split()[-1])
                img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Save to PNG format in memory
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    @staticmethod
    def get_image_dimensions(image_bytes: bytes) -> Tuple[int, int]:
        """
        Get the dimensions of an image from its bytes.
        
        Args:
            image_bytes: Image data as bytes
            
        Returns:
            Tuple of (width, height) in pixels
        """
        img = Image.open(io.BytesIO(image_bytes))
        return img.size
    
    @staticmethod
    def create_demo_gradient(width: int = 800, height: int = 400) -> bytes:
        """
        Create a demo gradient image for testing.
        
        Args:
            width: Image width in pixels
            height: Image height in pixels
            
        Returns:
            PNG image bytes
        """
        img = Image.new('RGB', (width, height), color='black')
        draw = ImageDraw.Draw(img)
        
        # Draw a blue gradient
        for i in range(width):
            blue = int(255 * (i / width))
            draw.line((i, 0, i, height), fill=(0, 0, blue))
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
