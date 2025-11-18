"""PDF processing utilities for converting PDF pages to images."""

import io
from typing import List
from pathlib import Path

try:
    from pdf2image import convert_from_path
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

from PIL import Image


class PDFProcessor:
    """Handles PDF to image conversion."""
    
    @staticmethod
    def is_pdf_supported() -> bool:
        """
        Check if PDF processing is supported.
        
        Returns:
            True if pdf2image is installed, False otherwise
        """
        return PDF_SUPPORT
    
    @staticmethod
    def convert_pdf_to_images(pdf_path: str, dpi: int = 200) -> List[bytes]:
        """
        Convert a PDF file to a list of PNG image bytes, one per page.
        
        Args:
            pdf_path: Path to the PDF file
            dpi: Resolution for rendering PDF pages (default 200)
            
        Returns:
            List of PNG image bytes, one per page
            
        Raises:
            ImportError: If pdf2image is not installed
            FileNotFoundError: If the PDF file doesn't exist
            ValueError: If the path is not a file
        """
        if not PDF_SUPPORT:
            raise ImportError(
                "pdf2image is not installed. "
                "Install it with: pip install pdf2image\n"
                "Note: You also need poppler-utils installed on your system."
            )
        
        path = Path(pdf_path)
        
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if not path.is_file():
            raise ValueError(f"Path is not a file: {pdf_path}")
        
        # Convert PDF pages to PIL Images
        try:
            pages = convert_from_path(pdf_path, dpi=dpi)
        except Exception as e:
            raise RuntimeError(f"Failed to convert PDF: {e}")
        
        # Convert each page to PNG bytes
        image_bytes_list = []
        for page in pages:
            # Convert to RGB if necessary
            if page.mode == 'RGBA':
                background = Image.new('RGB', page.size, (255, 255, 255))
                background.paste(page, mask=page.split()[-1])
                page = background
            elif page.mode != 'RGB':
                page = page.convert('RGB')
            
            # Save to PNG format in memory
            buffer = io.BytesIO()
            page.save(buffer, format='PNG')
            image_bytes_list.append(buffer.getvalue())
        
        return image_bytes_list
