"""Kitty terminal graphics protocol helper.

Implements core lifecycle operations:
 - Transmit (raw/PNG) image data with proper chunking (<=4096, non-final chunks multiple of 4)
 - Display (put) previously transmitted images with sizing/cropping
 - Image/placement ids (i / I / p)
 - Query protocol support and transmission medium availability (a=q)
 - Delete images/placements (a=d with d modifiers)
 - Optional compression (o=z)
 - Cursor movement policy (C=1)
 - Virtual placements for Unicode placeholders (U=1) and placeholder emission helper
 - Relative placements (P,Q,H,V)
 - Basic animation frame transmission/control (a=f / a=a / a=c)

Note: Interaction responses are read opportunistically (non-blocking) and returned to caller; robust parsing is terminal-dependent.
"""

from __future__ import annotations

import sys
import base64
import zlib
import select
import os
import re
from typing import Optional, List, Tuple


ESC = "\x1b"
APC_START = f"{ESC}_G"
APC_END = f"{ESC}\\"


class KittyProtocolError(RuntimeError):
    pass


class KittyGraphicsProtocol:
    CHUNK_SIZE = 4096
    RESPONSE_RE = re.compile(r"\x1b_Gi=(?P<i>\d+)(?:,p=(?P<p>\d+))?;(?P<msg>[A-Z0-9:]+.*?)\x1b\\")

    @staticmethod
    def _encode_payload(data: bytes, compress: bool) -> Tuple[str, Optional[str]]:
        if compress:
            data = zlib.compress(data)
            return base64.b64encode(data).decode("ascii"), "z"
        return base64.b64encode(data).decode("ascii"), None

    @staticmethod
    def _chunk_base64(b64: str) -> List[str]:
        chunks: List[str] = []
        pos = 0
        length = len(b64)
        while pos < length:
            # Determine next end respecting max size
            end = min(pos + KittyGraphicsProtocol.CHUNK_SIZE, length)
            chunk = b64[pos:end]
            if end < length and (len(chunk) % 4) != 0:
                # Back off to nearest multiple of 4 to satisfy spec for non-final chunks
                back = len(chunk) % 4
                end -= back
                chunk = b64[pos:end]
            chunks.append(chunk)
            pos = end
        return chunks

    @staticmethod
    def _write_escape(control: str, payload: str) -> None:
        sys.stdout.write(f"{APC_START}{control};{payload}{APC_END}")
        sys.stdout.flush()

    @staticmethod
    def _read_responses(timeout: float = 0.02) -> List[str]:
        responses: List[str] = []
        try:
            ready = select.select([sys.stdin], [], [], timeout)[0]
        except Exception:
            return responses  # Non-selectable stdin or error
        if ready:
            try:
                buf = getattr(sys.stdin, "buffer", None)
                if buf is not None and hasattr(buf, "read1"):
                    data = buf.read1(8192)
                else:
                    data = sys.stdin.read()  # Fallback (may block less due to select)
            except Exception:
                return responses
            if not data:
                return responses
            if isinstance(data, str):
                text = data
            else:
                text = data.decode(errors="ignore")
            for m in KittyGraphicsProtocol.RESPONSE_RE.finditer(text):
                responses.append(m.group(0))
        return responses

    @staticmethod
    def transmit_image(
        image_bytes: bytes,
        *,
        format: int = 100,
        width: int | None = None,
        height: int | None = None,
        image_id: int | None = None,
        image_number: int | None = None,
        placement_id: int | None = None,
        action: str = "T",  # "T" transmit+display, "t" transmit only
        columns: int | None = None,
        rows: int | None = None,
        src_x: int | None = None,
        src_y: int | None = None,
        src_w: int | None = None,
        src_h: int | None = None,
        cursor_move: bool = True,
        z_index: int | None = None,
        compress: bool = False,
        quiet: int = 0,
    ) -> List[str]:
        if image_id is not None and image_number is not None:
            raise ValueError("Specify at most one of image_id or image_number")
        payload_b64, compression_key = KittyGraphicsProtocol._encode_payload(image_bytes, compress)
        chunks = KittyGraphicsProtocol._chunk_base64(payload_b64)
        responses: List[str] = []
        for idx, chunk in enumerate(chunks):
            control_parts = []
            if idx == 0:
                control_parts.append(f"a={action}")
                control_parts.append(f"f={format}")
                if width is not None:
                    control_parts.append(f"s={int(width)}")
                if height is not None:
                    control_parts.append(f"v={int(height)}")
                if image_id is not None:
                    control_parts.append(f"i={int(image_id)}")
                if image_number is not None:
                    control_parts.append(f"I={int(image_number)}")
                if placement_id is not None:
                    control_parts.append(f"p={int(placement_id)}")
                if columns is not None:
                    control_parts.append(f"c={int(columns)}")
                if rows is not None:
                    control_parts.append(f"r={int(rows)}")
                if src_x is not None:
                    control_parts.append(f"x={int(src_x)}")
                if src_y is not None:
                    control_parts.append(f"y={int(src_y)}")
                if src_w is not None:
                    control_parts.append(f"w={int(src_w)}")
                if src_h is not None:
                    control_parts.append(f"h={int(src_h)}")
                if not cursor_move:
                    control_parts.append("C=1")
                if z_index is not None:
                    control_parts.append(f"z={int(z_index)}")
                if compression_key:
                    control_parts.append(f"o={compression_key}")
                if quiet:
                    control_parts.append(f"q={int(quiet)}")
            else:
                # Subsequent chunks only need m key (and possibly a=f for animation frames)
                pass
            # More chunks indicator
            control_parts.append(f"m={(0 if idx == len(chunks)-1 else 1)}")
            control = ",".join(control_parts)
            KittyGraphicsProtocol._write_escape(control, chunk)
        responses.extend(KittyGraphicsProtocol._read_responses())
        return responses

    @staticmethod
    def put(
        image_id: int,
        *,
        placement_id: int | None = None,
        columns: int | None = None,
        rows: int | None = None,
        src_x: int | None = None,
        src_y: int | None = None,
        src_w: int | None = None,
        src_h: int | None = None,
        cursor_move: bool = True,
        z_index: int | None = None,
        quiet: int = 0,
    ) -> List[str]:
        parts = ["a=p", f"i={int(image_id)}"]
        if placement_id is not None:
            parts.append(f"p={int(placement_id)}")
        if columns is not None:
            parts.append(f"c={int(columns)}")
        if rows is not None:
            parts.append(f"r={int(rows)}")
        if src_x is not None:
            parts.append(f"x={int(src_x)}")
        if src_y is not None:
            parts.append(f"y={int(src_y)}")
        if src_w is not None:
            parts.append(f"w={int(src_w)}")
        if src_h is not None:
            parts.append(f"h={int(src_h)}")
        if not cursor_move:
            parts.append("C=1")
        if z_index is not None:
            parts.append(f"z={int(z_index)}")
        if quiet:
            parts.append(f"q={int(quiet)}")
        control = ",".join(parts)
        KittyGraphicsProtocol._write_escape(control, "")
        return KittyGraphicsProtocol._read_responses()

    @staticmethod
    def query_support() -> bool:
        # Minimal dummy query per spec
        dummy = base64.b64encode(b"AAAA").decode("ascii")
        KittyGraphicsProtocol._write_escape("a=q,f=24,s=1,v=1,m=0", dummy)
        responses = KittyGraphicsProtocol._read_responses(0.1)
        return any(";OK" in r or "Gi=" in r for r in responses)

    @staticmethod
    def delete(
        *,
        mode: str = "i",  # one of spec d values (i,I,a,A,p,P,x,X,y,Y,z,Z,c,C,n,N,r,R,f,F,q,Q)
        image_id: int | None = None,
        placement_id: int | None = None,
        x: int | None = None,
        y: int | None = None,
        z_index: int | None = None,
        range_start: int | None = None,
        range_end: int | None = None,
        free: bool = False,
        quiet: int = 0,
    ) -> List[str]:
        # Uppercase mode frees data
        mval = mode.upper() if free else mode.lower()
        parts = ["a=d", f"d={mval}"]
        if image_id is not None:
            parts.append(f"i={int(image_id)}")
        if placement_id is not None:
            parts.append(f"p={int(placement_id)}")
        if x is not None:
            parts.append(f"x={int(x)}")
        if y is not None:
            parts.append(f"y={int(y)}")
        if z_index is not None:
            parts.append(f"z={int(z_index)}")
        if range_start is not None and range_end is not None and mval in {"r","R"}:
            parts.append(f"x={int(range_start)}")
            parts.append(f"y={int(range_end)}")
        if quiet:
            parts.append(f"q={int(quiet)}")
        control = ",".join(parts)
        KittyGraphicsProtocol._write_escape(control, "")
        return KittyGraphicsProtocol._read_responses()

    @staticmethod
    def create_virtual_placement(
        image_id: int,
        columns: int,
        rows: int,
        placement_id: int | None = None,
        quiet: int = 2,
    ) -> List[str]:
        parts = ["a=p", f"i={int(image_id)}", "U=1", f"c={int(columns)}", f"r={int(rows)}"]
        if placement_id is not None:
            parts.append(f"p={int(placement_id)}")
        if quiet:
            parts.append(f"q={int(quiet)}")
        control = ",".join(parts)
        KittyGraphicsProtocol._write_escape(control, "")
        return KittyGraphicsProtocol._read_responses()

    @staticmethod
    def relative_placement(
        image_id: int,
        placement_id: int,
        parent_image_id: int,
        parent_placement_id: int,
        offset_cols: int = 0,
        offset_rows: int = 0,
        quiet: int = 0,
    ) -> List[str]:
        parts = [
            "a=p",
            f"i={int(image_id)}",
            f"p={int(placement_id)}",
            f"P={int(parent_image_id)}",
            f"Q={int(parent_placement_id)}",
        ]
        if offset_cols:
            parts.append(f"H={int(offset_cols)}")
        if offset_rows:
            parts.append(f"V={int(offset_rows)}")
        if quiet:
            parts.append(f"q={int(quiet)}")
        control = ",".join(parts)
        KittyGraphicsProtocol._write_escape(control, "")
        return KittyGraphicsProtocol._read_responses()

    @staticmethod
    def transmit_frame(
        frame_bytes: bytes,
        *,
        image_id: int,
        format: int = 32,
        width: int,
        height: int,
        offset_x: int = 0,
        offset_y: int = 0,
        replace: bool = False,
        base_frame: int | None = None,
        edit_frame: int | None = None,
        gap_ms: int | None = None,
        compress: bool = False,
    ) -> List[str]:
        payload_b64, compression_key = KittyGraphicsProtocol._encode_payload(frame_bytes, compress)
        chunks = KittyGraphicsProtocol._chunk_base64(payload_b64)
        responses: List[str] = []
        for idx, chunk in enumerate(chunks):
            parts = ["a=f", f"i={int(image_id)}", f"f={format}"]
            if idx == 0:
                parts.append(f"s={int(width)}")
                parts.append(f"v={int(height)}")
                if offset_x or offset_y:
                    parts.append(f"x={int(offset_x)}")
                    parts.append(f"y={int(offset_y)}")
                if replace:
                    parts.append("X=1")  # composition mode simple overwrite for frame data
                if base_frame is not None:
                    parts.append(f"c={int(base_frame)}")
                if edit_frame is not None:
                    parts.append(f"r={int(edit_frame)}")
                if gap_ms is not None:
                    parts.append(f"z={int(gap_ms)}")
                if compression_key:
                    parts.append(f"o={compression_key}")
            parts.append(f"m={(0 if idx == len(chunks)-1 else 1)}")
            control = ",".join(parts)
            KittyGraphicsProtocol._write_escape(control, chunk)
        responses.extend(KittyGraphicsProtocol._read_responses())
        return responses

    @staticmethod
    def control_animation(
        image_id: int,
        *,
        state: int | None = None,  # 1 stop, 2 wait, 3 run
        current_frame: int | None = None,
        loops: int | None = None,
        frame_gap_ms: int | None = None,
        frame_index: int | None = None,
    ) -> List[str]:
        parts = ["a=a", f"i={int(image_id)}"]
        if state is not None:
            parts.append(f"s={int(state)}")
        if current_frame is not None:
            parts.append(f"c={int(current_frame)}")
        if loops is not None:
            parts.append(f"v={int(loops)}")
        if frame_gap_ms is not None:
            parts.append(f"z={int(frame_gap_ms)}")
        if frame_index is not None:
            parts.append(f"r={int(frame_index)}")
        control = ",".join(parts)
        KittyGraphicsProtocol._write_escape(control, "")
        return KittyGraphicsProtocol._read_responses()

    @staticmethod
    def compose_frames(
        image_id: int,
        source_frame: int,
        dest_frame: int,
        *,
        width: int | None = None,
        height: int | None = None,
        src_x: int = 0,
        src_y: int = 0,
        dest_x: int = 0,
        dest_y: int = 0,
        overwrite: bool = False,
    ) -> List[str]:
        parts = ["a=c", f"i={int(image_id)}", f"r={int(dest_frame)}", f"c={int(source_frame)}"]
        if width is not None:
            parts.append(f"w={int(width)}")
        if height is not None:
            parts.append(f"h={int(height)}")
        if src_x:
            parts.append(f"X={int(src_x)}")
        if src_y:
            parts.append(f"Y={int(src_y)}")
        if dest_x:
            parts.append(f"x={int(dest_x)}")
        if dest_y:
            parts.append(f"y={int(dest_y)}")
        if overwrite:
            parts.append("C=1")
        control = ",".join(parts)
        KittyGraphicsProtocol._write_escape(control, "")
        return KittyGraphicsProtocol._read_responses()

    @staticmethod
    def placeholder_cells(image_id: int, rows: int, cols: int) -> str:
        # Simplified: emit grid with foreground color = image_id mod 256
        fg = image_id % 256
        lines = []
        for r in range(rows):
            line = []
            for c in range(cols):
                line.append(f"\x1b[38;5;{fg}m\U0010EEEE\x1b[39m")
            lines.append("".join(line))
        return "\n".join(lines)

    # Backwards compatible convenience wrapper
    @staticmethod
    def display_image(
        image_bytes: bytes,
        columns: int | None = None,
        rows: int | None = None,
        src_x: int | None = None,
        src_y: int | None = None,
        src_w: int | None = None,
        src_h: int | None = None,
    ) -> List[str]:
        return KittyGraphicsProtocol.transmit_image(
            image_bytes,
            columns=columns,
            rows=rows,
            src_x=src_x,
            src_y=src_y,
            src_w=src_w,
            src_h=src_h,
            action="T",
            format=100,
        )

