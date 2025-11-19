#!/usr/bin/env python3
"""
Airgap Transfer - QR Code Sender (Standalone Version)
Version: {version}
Generated: {timestamp}

Minimal QR code sender for air-gapped environments.
This is a standalone script with no external dependencies except qrcode and Pillow.

Usage:
    python3 qr_sender.py <file_path> [first_frame_duration]

Examples:
    # Pipe to ffplay for display
    python3 qr_sender.py myfile.pdf 5 | ffplay -framerate 1 -f image2pipe -i -

    # Save as video
    python3 qr_sender.py myfile.pdf 5 | ffmpeg -framerate 1 -f image2pipe -i - output.mp4

Requirements:
    - Python 3.8+
    - qrcode[pil] library: pip install qrcode[pil]
"""

import base64
import math
import sys
from io import BytesIO
from pathlib import Path

try:
    import qrcode
    import qrcode.constants
except ImportError:
    print("ERROR: qrcode library not installed.", file=sys.stderr)
    print("Install with: pip install qrcode[pil]", file=sys.stderr)
    sys.exit(1)


# Constants
DEFAULT_CHUNK_SIZE = 800
DEFAULT_FIRST_FRAME_DURATION = 3
DEFAULT_BOX_SIZE = 10
DEFAULT_BORDER = 4


def encode_file_to_qr_stream(
    file_path: str,
    first_frame_duration: int = DEFAULT_FIRST_FRAME_DURATION,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    box_size: int = DEFAULT_BOX_SIZE,
    border: int = DEFAULT_BORDER,
):
    """
    Encode a file as a series of QR code PNG images and output to stdout.

    Args:
        file_path: Path to file to encode
        first_frame_duration: How many times to repeat the first frame
        chunk_size: Bytes per QR code chunk
        box_size: Size of each QR code box
        border: Border size around QR code
    """
    # Read and encode file
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"ERROR: File not found: {{file_path}}", file=sys.stderr)
        sys.exit(1)

    with open(file_path, 'rb') as f:
        file_data = f.read()

    file_size = len(file_data)
    encoded_data = base64.b64encode(file_data).decode('ascii')
    total_chunks = math.ceil(len(encoded_data) / chunk_size)

    # Print info to stderr (so it doesn't interfere with stdout pipe)
    print(f"File: {{file_path.name}}", file=sys.stderr)
    print(f"Size: {{file_size}} bytes", file=sys.stderr)
    print(f"Encoded: {{len(encoded_data)}} bytes (base64)", file=sys.stderr)
    print(f"Chunks: {{total_chunks}}", file=sys.stderr)
    print(f"First frame duration: {{first_frame_duration}} frames", file=sys.stderr)
    print("", file=sys.stderr)

    # Prepare all QR data strings
    qr_data_list = []
    for i in range(total_chunks):
        start = i * chunk_size
        end = min((i + 1) * chunk_size, len(encoded_data))
        chunk = encoded_data[start:end]
        qr_data = f"{{i+1}}/{{total_chunks}}|{{chunk}}"
        qr_data_list.append(qr_data)

    # Determine QR version from longest data (for consistent sizing)
    max_data = max(qr_data_list, key=len)
    temp_qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    temp_qr.add_data(max_data)
    temp_qr.make(fit=True)
    qr_version = temp_qr.version

    print(f"QR Version: {{qr_version}}", file=sys.stderr)
    print("Generating QR codes...", file=sys.stderr)
    print("", file=sys.stderr)

    # Generate and output QR codes
    for i, qr_data in enumerate(qr_data_list):
        # Create QR code with fixed version
        qr = qrcode.QRCode(
            version=qr_version,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=box_size,
            border=border,
        )
        qr.add_data(qr_data)
        qr.make(fit=False)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to PNG bytes
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG')
        img_data = img_buffer.getvalue()

        # First frame: repeat for specified duration
        if i == 0:
            for _ in range(first_frame_duration):
                sys.stdout.buffer.write(img_data)
        else:
            sys.stdout.buffer.write(img_data)

        # Progress to stderr
        if (i + 1) % 10 == 0 or (i + 1) == total_chunks:
            print(f"Progress: {{i+1}}/{{total_chunks}} QR codes generated", file=sys.stderr)

    print("", file=sys.stderr)
    print("Done! QR code stream output to stdout.", file=sys.stderr)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 qr_sender.py <file_path> [first_frame_duration]", file=sys.stderr)
        print("", file=sys.stderr)
        print("Arguments:", file=sys.stderr)
        print("  file_path              File to encode and send", file=sys.stderr)
        print("  first_frame_duration   How long to display first frame (default: 3)", file=sys.stderr)
        print("", file=sys.stderr)
        print("Examples:", file=sys.stderr)
        print("  # Display QR codes with ffplay", file=sys.stderr)
        print("  python3 qr_sender.py myfile.pdf 5 | ffplay -framerate 1 -f image2pipe -i -", file=sys.stderr)
        print("", file=sys.stderr)
        print("  # Save as video", file=sys.stderr)
        print("  python3 qr_sender.py myfile.pdf 5 | ffmpeg -framerate 1 -f image2pipe -i - output.mp4", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    first_frame_duration = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_FIRST_FRAME_DURATION

    encode_file_to_qr_stream(file_path, first_frame_duration)


if __name__ == "__main__":
    main()
