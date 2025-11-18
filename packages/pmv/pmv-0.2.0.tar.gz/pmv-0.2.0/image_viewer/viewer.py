"""Main image viewer TUI implementation."""

from typing import List, Optional

from .terminal import TerminalHelper
from .processor import ImageProcessor
from .kitty import KittyGraphicsProtocol
from .cache import ImageCache


class ImageViewer:
    """TUI image viewer with keyboard navigation."""
    
    # UI layout constants
    HEADER_LINES = 4  # separator + title + controls + separator
    FOOTER_LINES = 2  # separator + status
    
    def __init__(self, image_paths: List[str], image_names: Optional[List[str]] = None):
        """
        Initialize the image viewer.
        
        Args:
            image_paths: List of file paths to images
            image_names: Optional list of display names for images
        """
        self.image_paths = image_paths
        self.image_names = image_names or [f"Image {i+1}" for i in range(len(image_paths))]
        self.current_index = 0
        
        # Initialize cache
        self.cache = ImageCache()
        self.cache.set_image_paths(image_paths)
        
        # Interaction state
        self._reset_view_state()

        # Preload first image
        self.cache.load(0)

    def _reset_view_state(self):
        """Reset zoom/pan state to defaults for current image."""
        self.zoom = 1.0  # 1.0 means full image
        self.pan_x = 0   # pixels from left
        self.pan_y = 0   # pixels from top
    
    @classmethod
    def from_preloaded_images(cls, image_data: List[bytes], image_names: List[str]):
        """
        Create a viewer from preloaded image data (e.g., PDF pages).
        
        Args:
            image_data: List of image bytes
            image_names: List of display names for each image
            
        Returns:
            ImageViewer instance with preloaded images
        """
        # Create instance with dummy paths
        viewer = cls.__new__(cls)
        viewer.image_paths = [f"preloaded_{i}" for i in range(len(image_data))]
        viewer.image_names = image_names
        viewer.current_index = 0
        
        # Initialize cache with preloaded data
        viewer.cache = ImageCache()
        viewer.cache.set_image_paths(viewer.image_paths)
        viewer.cache.set_preloaded_images({i: img_bytes for i, img_bytes in enumerate(image_data)})
        
        # Initialize interaction state
        viewer._reset_view_state()
        
        return viewer
    
    def run(self):
        """Run the main viewer loop."""
        if not self.image_paths:
            print("No images to display.")
            return
        
        while True:
            # Get current terminal info
            term_info = TerminalHelper.get_terminal_info()
            
            # Clear and redraw
            TerminalHelper.clear_screen()
            
            # Display UI
            self._display_header(term_info.columns)
            self._display_current_image(term_info)
            self._display_footer(term_info.columns)
            
            # Get user input
            key = TerminalHelper.get_key_input()
            
            # Handle key press
            action = self._handle_key(key)
            
            if action == "quit":
                TerminalHelper.clear_screen()
                break
            elif action == "print_path":
                TerminalHelper.clear_screen()
                print(self.image_paths[self.current_index])
                break
    
    def _display_header(self, cols: int):
        """
        Display the header with title and controls.
        
        Args:
            cols: Terminal width in columns
        """
        print("=" * cols)
        print(f"📷 [{self.current_index + 1}/{len(self.image_paths)}] {self.image_names[self.current_index]}")
        print(
            "Controls: p/n prev/next | +/- zoom | arrows & j/k/l/; pan | ENTER/SPACE print path | q quit"
        )
        print("=" * cols)
    
    def _display_footer(self, cols: int):
        """
        Display the footer with status.
        
        Args:
            cols: Terminal width in columns
        """
        print("=" * cols)
    
    def _display_current_image(self, term_info):
        """
        Display the current image centered in the terminal.
        
        Args:
            term_info: TerminalInfo with terminal dimensions
        """
        # Load current image (PNG bytes)
        image_bytes = self.cache.load(self.current_index)
        
        # Calculate available space in rows/cols
        available_rows = max(1, term_info.rows - self.HEADER_LINES - self.FOOTER_LINES)
        available_cols = max(1, term_info.columns)
        
        # Image dimensions in pixels
        img_w, img_h = ImageProcessor.get_image_dimensions(image_bytes)
        if img_w <= 0 or img_h <= 0:
            return
        
        # Compute max pixels available
        max_w_px = available_cols * term_info.cell_width
        max_h_px = available_rows * term_info.cell_height
        
        # First, compute the "fit to screen" scale (what makes the full image fit)
        fit_scale = min(max_w_px / img_w, max_h_px / img_h)
        
        # Apply zoom on top of the fit scale
        # zoom=1.0 means "fit to screen"
        # zoom=2.0 means "2x the fit size" (magnified)
        effective_scale = fit_scale * self.zoom
        
        # Compute desired display size based on effective scale
        desired_w_px = int(img_w * effective_scale)
        desired_h_px = int(img_h * effective_scale)
        
        # Clamp width and height independently to terminal boundaries
        disp_w_px = max(1, min(desired_w_px, max_w_px))
        disp_h_px = max(1, min(desired_h_px, max_h_px))
        
        # The source rectangle represents what portion of the image we display
        # Compute source dimensions based on what actually fits
        src_w = max(1, min(img_w, int(disp_w_px / effective_scale)))
        src_h = max(1, min(img_h, int(disp_h_px / effective_scale)))
        
        # Clamp pan so source rect stays within the image
        max_pan_x = max(0, img_w - src_w)
        max_pan_y = max(0, img_h - src_h)
        self.pan_x = max(0, min(self.pan_x, max_pan_x))
        self.pan_y = max(0, min(self.pan_y, max_pan_y))
        
        # Convert display pixels to terminal cells, being careful with rounding
        image_cols = max(1, min(available_cols, disp_w_px // max(1, term_info.cell_width)))
        image_rows = max(1, min(available_rows, disp_h_px // max(1, term_info.cell_height)))
        
        # Calculate centering offsets in cells (which row/col to start at)
        col_offset = max(0, (available_cols - image_cols) // 2)
        row_offset = max(0, (available_rows - image_rows) // 2)
        
        # Move cursor to starting position (accounting for header)
        # Move down by row_offset rows after the header
        for _ in range(row_offset):
            print()
        
        # Move cursor right by col_offset columns using spaces
        if col_offset > 0:
            print(' ' * col_offset, end='')
        
        # Display cropped+scaled image via Kitty at current cursor position
        KittyGraphicsProtocol.display_image(
            image_bytes,
            columns=image_cols,
            rows=image_rows,
            src_x=self.pan_x,
            src_y=self.pan_y,
            src_w=src_w,
            src_h=src_h,
        )
    
    def _handle_key(self, key: str) -> Optional[str]:
        """
        Handle a key press and return an action.
        
        Args:
            key: The key character or escape sequence
            
        Returns:
            Action string: "quit", "print_path", or None for continue
        """
        # Quit
        if key in ('q', 'Q', '\x1b', '\x03'):  # q, ESC, or Ctrl+C
            return "quit"
        
        # Print path and exit
        if key in ('\r', '\n', ' '):  # Enter or Space
            return "print_path"
        
        # Previous / Next image
        if key in ('n', 'N'):
            self._navigate_next()
            self._reset_view_state()
            return None
        if key in ('p', 'P'):
            self._navigate_previous()
            self._reset_view_state()
            return None

        # Zoom in / out
        if key in ('+', '='):
            self._zoom(1.2)
            return None
        if key in ('-', '_'):
            self._zoom(1/1.2)
            return None

        # Pan with arrows or j/k/l/;
        if key in ('\x1b[A', 'k', 'K'):  # up
            self._pan(0, -1)
            return None
        if key in ('\x1b[B', 'j', 'J'):  # down
            self._pan(0, 1)
            return None
        if key in ('\x1b[D', 'l', 'L'):  # left
            self._pan(-1, 0)
            return None
        if key in ('\x1b[C', ';', ':'):  # right
            self._pan(1, 0)
            return None
        
        return None
    
    def _navigate_next(self):
        """Navigate to the next image and preload the following one."""
        self.current_index = (self.current_index + 1) % len(self.image_paths)
        
        # Preload next image
        next_index = (self.current_index + 1) % len(self.image_paths)
        self.cache.preload(next_index)
    
    def _navigate_previous(self):
        """Navigate to the previous image and preload the one before it."""
        self.current_index = (self.current_index - 1) % len(self.image_paths)
        
        # Preload previous image
        prev_index = (self.current_index - 1) % len(self.image_paths)
        self.cache.preload(prev_index)

    def _zoom(self, factor: float):
        """Apply multiplicative zoom, clamped to sensible range."""
        self.zoom = max(1.0, min(8.0, self.zoom * factor))

    def _pan(self, dx: int, dy: int):
        """Pan by a step relative to current zoom (in pixels)."""
        # Pan step is 10% of the current visible source rectangle
        img_bytes = self.cache.load(self.current_index)
        img_w, img_h = ImageProcessor.get_image_dimensions(img_bytes)
        src_w = int(img_w / self.zoom)
        src_h = int(img_h / self.zoom)
        step_x = max(1, src_w // 10)
        step_y = max(1, src_h // 10)
        self.pan_x += dx * step_x
        self.pan_y += dy * step_y
