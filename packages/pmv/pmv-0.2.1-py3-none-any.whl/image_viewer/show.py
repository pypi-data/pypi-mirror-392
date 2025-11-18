"""Backward-compatible wrappers for the Image Viewer package."""

from typing import List, Optional

from .viewer import ImageViewer
from .processor import ImageProcessor
from .terminal import TerminalHelper


def display_images_tui(image_paths: List[str], image_names: Optional[List[str]] = None):
    """
    Display multiple images in a TUI with keyboard navigation.
    Convenience wrapper around ImageViewer.
    """
    viewer = ImageViewer(image_paths, image_names)
    viewer.run()


def load_image_to_bytes(image_path: str) -> bytes:
    """Legacy wrapper for ImageProcessor.load_from_file()."""
    return ImageProcessor.load_from_file(image_path)


def create_demo_image(width: int = 800, height: int = 400) -> bytes:
    """Legacy wrapper for ImageProcessor.create_demo_gradient()."""
    return ImageProcessor.create_demo_gradient(width, height)


def clear_screen():
    """Legacy wrapper for TerminalHelper.clear_screen()."""
    TerminalHelper.clear_screen()
