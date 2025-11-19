"""CLI command for QR code encoding."""

import sys
import argparse
from ..qrcode import QREncoder
from ..utils import DEFAULT_QR_CHUNK_SIZE, DEFAULT_FIRST_FRAME_DURATION


def register_subcommand(subparsers) -> None:
    """Register the 'qr-encode' subcommand."""
    parser = subparsers.add_parser(
        "qr-encode",
        help="Encode files as QR code video stream",
        description="Encode files as a sequence of QR codes for video transfer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Pipe to ffplay for live display
  airgap qr-encode myfile.pdf | ffplay -framerate 1 -f image2pipe -i -

  # Save as video file
  airgap qr-encode myfile.pdf | ffmpeg -framerate 1 -f image2pipe -i - output.mp4

  # Adjust first frame delay
  airgap qr-encode myfile.pdf --first-frame-delay 5 | ffplay -framerate 1 -f image2pipe -i -

  # Custom chunk size
  airgap qr-encode myfile.pdf --chunk-size 600 | ffplay -framerate 1 -f image2pipe -i -

Note:
  Output is written to stdout as PNG image stream.
  Progress and info messages are written to stderr.
        """,
    )

    parser.add_argument(
        "file",
        help="File to encode",
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=DEFAULT_QR_CHUNK_SIZE,
        help=f"Bytes per QR code (default: {DEFAULT_QR_CHUNK_SIZE})",
    )

    parser.add_argument(
        "--first-frame-delay",
        type=int,
        default=DEFAULT_FIRST_FRAME_DURATION,
        help=f"First frame duration in seconds (default: {DEFAULT_FIRST_FRAME_DURATION})",
    )

    parser.set_defaults(func=_qr_encode_command)


def _qr_encode_command(args) -> int:
    """Execute the qr-encode command."""
    # Create encoder
    encoder = QREncoder(
        args.file,
        chunk_size=args.chunk_size,
        first_frame_duration=args.first_frame_delay,
    )

    # Print info to stderr
    print("=" * 70, file=sys.stderr)
    print("Airgap Transfer - QR Code Encoder", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print(f"\nFile: {encoder.file_path}", file=sys.stderr)

    # Progress callback
    def progress(current, total):
        print(f"Generating QR codes: {current}/{total}", file=sys.stderr, end='\r')

    # Encode to stdout
    encoder.encode_to_stream(
        output_stream=sys.stdout.buffer,
        progress_callback=progress,
    )

    # Print stats to stderr
    stats = encoder.get_stats()
    print(file=sys.stderr)
    print("-" * 70, file=sys.stderr)
    print("✓ Encoding complete!", file=sys.stderr)
    print(f"File size: {stats['file_size']:,} bytes", file=sys.stderr)
    print(f"Encoded size: {stats['encoded_size']:,} bytes", file=sys.stderr)
    print(f"Total QR codes: {stats['total_chunks']}", file=sys.stderr)
    print(f"QR version: {stats['qr_version']}", file=sys.stderr)
    print(f"First frame duration: {stats['first_frame_duration']} seconds", file=sys.stderr)
    print("=" * 70, file=sys.stderr)

    return 0
