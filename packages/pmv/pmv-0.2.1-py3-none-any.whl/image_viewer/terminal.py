"""Terminal helper utilities for managing terminal operations."""

import sys
import struct
import termios
import tty
import fcntl
from dataclasses import dataclass
from typing import Tuple


@dataclass
class TerminalInfo:
    """Information about terminal dimensions."""
    columns: int
    rows: int
    cell_width: int
    cell_height: int


class TerminalHelper:
    """Helper class for terminal operations and information."""
    
    @staticmethod
    def get_terminal_size() -> Tuple[int, int]:
        """
        Get the terminal size in columns and rows.
        
        Returns:
            Tuple of (columns, rows)
        """
        try:
            # Use ioctl to get window size
            size = struct.unpack('hh', fcntl.ioctl(0, termios.TIOCGWINSZ, '1234'))
            return size[1], size[0]  # columns, rows
        except Exception:
            # Fallback to environment variables or defaults
            import os
            cols = int(os.environ.get('COLUMNS', 80))
            rows = int(os.environ.get('LINES', 24))
            return cols, rows
    
    @staticmethod
    def get_cell_size() -> Tuple[int, int]:
        """
        Get the terminal cell size in pixels.
        
        Returns:
            Tuple of (cell_width, cell_height) in pixels
        """
        try:
            # Use ioctl TIOCGWINSZ to get pixel dimensions
            size_data = fcntl.ioctl(0, termios.TIOCGWINSZ, b'\x00' * 8)
            rows, cols, xpixels, ypixels = struct.unpack('HHHH', size_data)
            
            if xpixels > 0 and ypixels > 0 and cols > 0 and rows > 0:
                cell_width = xpixels // cols
                cell_height = ypixels // rows
                return cell_width, cell_height
        except Exception:
            pass
        
        # Fallback to common defaults
        return 10, 20
    
    @staticmethod
    def get_terminal_info() -> TerminalInfo:
        """
        Get comprehensive terminal information.
        
        Returns:
            TerminalInfo dataclass with dimensions
        """
        cols, rows = TerminalHelper.get_terminal_size()
        cell_width, cell_height = TerminalHelper.get_cell_size()
        return TerminalInfo(cols, rows, cell_width, cell_height)
    
    @staticmethod
    def clear_screen():
        """Clear the terminal screen and move cursor to top."""
        sys.stdout.write('\x1b[2J\x1b[H')
        sys.stdout.flush()
    
    @staticmethod
    def get_key_input() -> str:
        """
        Get a single key press from stdin in raw mode.
        Handles escape sequences for arrow keys.
        
        Returns:
            The key character or escape sequence
        """
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            
            # Handle escape sequences (arrow keys)
            if ch == '\x1b':
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    return f'\x1b[{ch3}'
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
