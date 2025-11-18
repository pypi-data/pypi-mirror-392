#!/usr/bin/env python3
"""
Image Viewer - A TUI image viewer for Kitty terminal with keyboard navigation.
"""

import sys
import os
import argparse
from pathlib import Path
from typing import List

from image_viewer import ImageViewer, TerminalHelper
from image_viewer.pdf_processor import PDFProcessor


# Supported image extensions
SUPPORTED_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', 
    '.webp', '.tiff', '.tif', '.ico', '.ppm', 
    '.pgm', '.pbm', '.pnm', '.svg'
}


def check_kitty_support() -> bool:
    """
    Check if the terminal supports Kitty graphics protocol.
    
    Returns:
        True if Kitty protocol is supported, False otherwise.
    """
    # Check if running in Kitty terminal
    if os.environ.get('TERM') == 'xterm-kitty' or os.environ.get('KITTY_WINDOW_ID'):
        return True
    
    # Try to query terminal for graphics support
    # Send device attributes query
    try:
        # This is a more robust check but may not work in all cases
        term = os.environ.get('TERM', '')
        if 'kitty' in term.lower():
            return True
    except Exception:
        pass
    
    return False


def get_images_from_folder(folder_path: Path) -> List[Path]:
    """
    Get all supported image files from a folder.
    
    Args:
        folder_path: Path to the folder to scan.
    
    Returns:
        List of image file paths, sorted alphabetically.
    """
    if not folder_path.is_dir():
        raise ValueError(f"Not a directory: {folder_path}")
    
    image_files = []
    for file_path in folder_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            image_files.append(file_path)
    
    # Sort alphabetically
    return sorted(image_files)


def collect_image_paths(paths: List[str]) -> List[Path]:
    """
    Collect all image paths from the given arguments.
    Expands folders to their contained images.
    
    Args:
        paths: List of file or folder paths.
    
    Returns:
        List of image file paths.
    """
    all_images = []
    
    for path_str in paths:
        path = Path(path_str)
        
        if not path.exists():
            print(f"⚠️  Warning: Path does not exist: {path_str}", file=sys.stderr)
            continue
        
        if path.is_file():
            # Check if it's a supported image format
            if path.suffix.lower() in SUPPORTED_EXTENSIONS:
                all_images.append(path)
            else:
                print(f"⚠️  Warning: Unsupported file format: {path_str}", file=sys.stderr)
        
        elif path.is_dir():
            # Scan folder for images
            try:
                folder_images = get_images_from_folder(path)
                if folder_images:
                    print(f"📁 Found {len(folder_images)} image(s) in: {path_str}")
                    all_images.extend(folder_images)
                else:
                    print(f"⚠️  Warning: No images found in folder: {path_str}", file=sys.stderr)
            except Exception as e:
                print(f"❌ Error scanning folder {path_str}: {e}", file=sys.stderr)
    
    return all_images


def main():
    """Main entry point for the image viewer application."""
    parser = argparse.ArgumentParser(
        description='Image Viewer - Display images in Kitty terminal with TUI navigation.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Controls:
  Arrow Keys / a,d / h,l  Navigate between images
  q / ESC                 Quit viewer

Supported formats:
  JPEG, PNG, GIF, BMP, WEBP, TIFF, and more

Examples:
  %(prog)s image1.jpg image2.png
  %(prog)s images/               # View all images in folder
  %(prog)s *.jpg                 # View all JPEGs
  %(prog)s folder/ img1.png      # Mix folders and files

Requirements:
  - Kitty terminal (https://sw.kovidgoyal.net/kitty/)
  - Use --skip-check to bypass terminal compatibility check
        """
    )
    
    parser.add_argument(
        'paths',
        nargs='*',
        help='Path(s) to image file(s) or folder(s) containing images'
    )
    
    parser.add_argument(
        '--skip-check',
        action='store_true',
        help='Skip Kitty terminal compatibility check (use at your own risk)'
    )
    
    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        help='Recursively scan folders for images'
    )
    
    parser.add_argument(
        '--pdf',
        action='store_true',
        help='Treat input as a PDF file and convert each page to an image'
    )
    
    args = parser.parse_args()
    
    # Check for Kitty terminal support
    if not args.skip_check:
        if not check_kitty_support():
            print("❌ Error: Kitty terminal not detected!", file=sys.stderr)
            print("\nThis application requires Kitty terminal to display images.", file=sys.stderr)
            print("Get Kitty at: https://sw.kovidgoyal.net/kitty/", file=sys.stderr)
            print("\nIf you're sure you're using Kitty, use --skip-check to bypass this check.", file=sys.stderr)
            sys.exit(1)
        print("✅ Kitty terminal detected.")
    else:
        print("⚠️  Skipping terminal compatibility check...")
    
    # Check if paths were provided
    if not args.paths:
        parser.print_help()
        print("\n❌ Error: No paths specified.", file=sys.stderr)
        sys.exit(1)
    
    # Handle PDF mode
    if args.pdf:
        if len(args.paths) != 1:
            print("❌ Error: PDF mode requires exactly one PDF file.", file=sys.stderr)
            sys.exit(1)
        
        pdf_path = Path(args.paths[0])
        
        if not pdf_path.exists():
            print(f"❌ Error: PDF file not found: {pdf_path}", file=sys.stderr)
            sys.exit(1)
        
        if not pdf_path.is_file():
            print(f"❌ Error: Path is not a file: {pdf_path}", file=sys.stderr)
            sys.exit(1)
        
        if pdf_path.suffix.lower() != '.pdf':
            print(f"❌ Error: File is not a PDF: {pdf_path}", file=sys.stderr)
            sys.exit(1)
        
        if not PDFProcessor.is_pdf_supported():
            print("❌ Error: PDF support not available!", file=sys.stderr)
            print("\nInstall required dependencies:", file=sys.stderr)
            print("  pip install pdf2image", file=sys.stderr)
            print("  System package: poppler-utils (on Debian/Ubuntu: apt install poppler-utils)", file=sys.stderr)
            sys.exit(1)
        
        print(f"\n📄 Converting PDF to images: {pdf_path.name}")
        
        try:
            # Convert PDF pages to image bytes
            pdf_image_bytes = PDFProcessor.convert_pdf_to_images(str(pdf_path))
            
            print(f"✅ Converted {len(pdf_image_bytes)} page(s) from PDF")
            print("🚀 Launching image viewer...\n")
            
            # Create page names
            page_names = [f"{pdf_path.name} - Page {i+1}" for i in range(len(pdf_image_bytes))]
            
            # Create viewer with preloaded PDF pages
            viewer = ImageViewer.from_preloaded_images(pdf_image_bytes, page_names)
            viewer.run()
            
        except ImportError as e:
            print(f"❌ Error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error processing PDF: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            sys.exit(1)
        
        sys.exit(0)
    
    # Regular image mode - check that we're not mixing with PDF
    for path_str in args.paths:
        path = Path(path_str)
        if path.is_file() and path.suffix.lower() == '.pdf':
            print("❌ Error: Cannot mix PDF files with images. Use --pdf flag for PDF viewing.", file=sys.stderr)
            sys.exit(1)
    
    # Collect all image paths
    print("\n📂 Scanning for images...")
    
    if args.recursive:
        # Implement recursive scanning
        all_paths = []
        for path_str in args.paths:
            path = Path(path_str)
            if path.is_dir():
                # Recursively find all images
                for ext in SUPPORTED_EXTENSIONS:
                    all_paths.extend(path.rglob(f"*{ext}"))
            else:
                all_paths.append(path)
        image_paths = [p for p in all_paths if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS]
        image_paths = sorted(set(image_paths))  # Remove duplicates and sort
    else:
        image_paths = collect_image_paths(args.paths)
    
    if not image_paths:
        print("\n❌ No valid images found to display.", file=sys.stderr)
        sys.exit(1)
    
    print(f"\n📷 Found {len(image_paths)} image(s) total.")
    print("🚀 Launching image viewer with lazy loading...\n")
    
    # Pass image paths instead of loading all images upfront
    image_path_strings = [str(path) for path in image_paths]
    image_names = [path.name for path in image_paths]
    
    # Launch the TUI viewer with lazy loading
    try:
        viewer = ImageViewer(image_path_strings, image_names)
        viewer.run()
    except KeyboardInterrupt:
        TerminalHelper.clear_screen()
        print("\n👋 Interrupted. Exiting.")
        sys.exit(0)
    except Exception as e:
        TerminalHelper.clear_screen()
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
