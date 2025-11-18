"""
Image display module for Kitty terminal graphics protocol.

This module provides a convenient interface for displaying images in Kitty terminal.
All functionality has been refactored into separate modules for better organization.

For backward compatibility, this module re-exports the main classes and functions.
"""

from typing import List, Optional

# Import all classes from refactored modules
from image_viewer import (
    TerminalHelper,
    TerminalInfo,
    ImageProcessor,
    KittyGraphicsProtocol,
    ImageCache,
    ImageViewer,
)

# Re-export all classes for backward compatibility
__all__ = [
    'TerminalHelper',
    'TerminalInfo',
    'ImageProcessor',
    'KittyGraphicsProtocol',
    'ImageCache',
    'ImageViewer',
    'display_images_tui',
    'load_image_to_bytes',
    'clear_screen',
    'create_demo_image',
]


# Convenient wrapper functions for backward compatibility
def display_images_tui(image_paths: List[str], image_names: Optional[List[str]] = None):
    """
    Display multiple images in a TUI with keyboard navigation.
    This is a convenience wrapper around ImageViewer.
    
    Args:
        image_paths: List of file paths to images
        image_names: Optional list of display names for images
    """
    viewer = ImageViewer(image_paths, image_names)
    viewer.run()


def load_image_to_bytes(image_path: str) -> bytes:
    """
    Legacy wrapper for ImageProcessor.load_from_file().
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Image data as PNG bytes
    """
    return ImageProcessor.load_from_file(image_path)


def create_demo_image(width: int = 800, height: int = 400) -> bytes:
    """
    Legacy wrapper for ImageProcessor.create_demo_gradient().
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        
    Returns:
        PNG image bytes
    """
    return ImageProcessor.create_demo_gradient(width, height)


def clear_screen():
    """Legacy wrapper for TerminalHelper.clear_screen()."""
    TerminalHelper.clear_screen()


if __name__ == "__main__":
    print("This module is meant to be imported. Use main.py to run the image viewer.")