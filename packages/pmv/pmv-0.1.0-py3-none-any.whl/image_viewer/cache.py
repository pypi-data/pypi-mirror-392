"""Image caching system for lazy loading."""

from typing import Dict
from PIL import Image, ImageDraw
import io

from .processor import ImageProcessor


class ImageCache:
    """Manages lazy loading and caching of images."""
    
    def __init__(self):
        """Initialize the image cache."""
        self._cache: Dict[int, bytes] = {}
        self._image_paths: list[str] = []
    
    def set_image_paths(self, paths: list[str]):
        """
        Set the list of image paths to manage.
        
        Args:
            paths: List of file paths to images
        """
        self._image_paths = paths
        self._cache.clear()
    
    def set_preloaded_images(self, images: Dict[int, bytes]):
        """
        Set preloaded image data directly into the cache.
        Useful for in-memory images like PDF pages.
        
        Args:
            images: Dictionary mapping index to image bytes
        """
        self._cache.update(images)
    
    def load(self, index: int) -> bytes:
        """
        Load an image by index, using cache if available.
        Creates an error placeholder if loading fails.
        
        Args:
            index: Index of the image in the paths list
            
        Returns:
            Image data as PNG bytes
        """
        if index not in self._cache:
            try:
                self._cache[index] = ImageProcessor.load_from_file(self._image_paths[index])
            except Exception as e:
                # Create an error placeholder image
                error_img = Image.new('RGB', (800, 400), color='black')
                draw = ImageDraw.Draw(error_img)
                draw.text((50, 180), f"Error loading image:\n{str(e)}", fill='white')
                buffer = io.BytesIO()
                error_img.save(buffer, format='PNG')
                self._cache[index] = buffer.getvalue()
        
        return self._cache[index]
    
    def preload(self, index: int):
        """
        Preload an image in the background (adds to cache if not present).
        Silently fails if loading errors occur.
        
        Args:
            index: Index of the image to preload
        """
        if index not in self._cache and 0 <= index < len(self._image_paths):
            try:
                self.load(index)
            except Exception:
                pass  # Silently fail - error will be handled when user navigates to it
    
    def clear(self):
        """Clear all cached images."""
        self._cache.clear()
    
    def get_cache_size(self) -> int:
        """
        Get the number of cached images.
        
        Returns:
            Number of images currently in cache
        """
        return len(self._cache)
