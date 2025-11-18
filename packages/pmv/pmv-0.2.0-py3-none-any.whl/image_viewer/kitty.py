"""Kitty terminal graphics protocol implementation."""

import sys
import base64


class KittyGraphicsProtocol:
    """Handles communication with Kitty terminal using its graphics protocol."""
    
    CHUNK_SIZE = 4096
    
    @staticmethod
    def display_image(
        image_bytes: bytes,
        columns: int | None = None,
        rows: int | None = None,
        src_x: int | None = None,
        src_y: int | None = None,
        src_w: int | None = None,
        src_h: int | None = None,
    ):
        """
        Display an image using Kitty graphics protocol with optional sizing and placement.
        
        Args:
            image_bytes: PNG image data as bytes
            columns: Desired width in terminal columns (c)
            rows: Desired height in terminal rows (r)
            src_x: Source rectangle X position (x)
            src_y: Source rectangle Y position (y)
            src_w: Source rectangle width (w)
            src_h: Source rectangle height (h)
        """
        # Encode the image data into Base64
        b64_data = base64.b64encode(image_bytes).decode('ascii')
        
        # Split the base64 string into chunks
        chunks = [
            b64_data[i:i + KittyGraphicsProtocol.CHUNK_SIZE]
            for i in range(0, len(b64_data), KittyGraphicsProtocol.CHUNK_SIZE)
        ]
        
        # Transmit the data using the Kitty protocol
        for i, chunk in enumerate(chunks):
            payload = {'m': 1}  # m=1 means more data is coming
            
            if i == 0:
                # First chunk includes action (a=T) and format (f=100 for PNG)
                payload.update({'a': 'T', 'f': 100})
                # Include sizing/placement if provided
                if columns is not None:
                    payload['c'] = int(columns)
                if rows is not None:
                    payload['r'] = int(rows)
                # Source rectangle in pixels
                if src_x is not None:
                    payload['x'] = int(src_x)
                if src_y is not None:
                    payload['y'] = int(src_y)
                if src_w is not None:
                    payload['w'] = int(src_w)
                if src_h is not None:
                    payload['h'] = int(src_h)
            
            if i == len(chunks) - 1:
                # Last chunk must have m=0 to signal the end
                payload['m'] = 0
            
            # Construct the control data string (e.g., "a=T,f=100,m=1")
            control_data = ",".join([f"{key}={value}" for key, value in payload.items()])
            
            # Construct and print the full escape sequence for the chunk
            # Structure: ESC_G <control_data> ; <payload> ESC \
            sys.stdout.write(f"\x1b_G{control_data};{chunk}\x1b\\")
            sys.stdout.flush()
        
        # Don't add extra newline - let caller control cursor position
        sys.stdout.flush()
