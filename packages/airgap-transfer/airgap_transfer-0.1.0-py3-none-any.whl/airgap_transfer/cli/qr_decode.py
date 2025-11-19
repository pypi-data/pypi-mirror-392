"""CLI command for QR code decoding."""

import sys
import argparse
from ..qrcode import QRDecoder
from ..utils import DEFAULT_SAMPLE_RATE, compare_files


def register_subcommand(subparsers) -> None:
    """Register the 'qr-decode' subcommand."""
    parser = subparsers.add_parser(
        "qr-decode",
        help="Decode files from QR code video",
        description="Extract and decode files from QR code video recordings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic decoding
  airgap qr-decode recording.mp4 output.pdf

  # Faster processing (sample every 2 frames)
  airgap qr-decode recording.mp4 output.pdf --sample-rate 2

  # Verify against original
  airgap qr-decode recording.mp4 output.pdf --verify original.pdf

  # Allow incomplete data
  airgap qr-decode recording.mp4 output.pdf --allow-incomplete

  # Quiet mode
  airgap qr-decode recording.mp4 output.pdf --quiet
        """,
    )

    parser.add_argument(
        "video",
        help="Video file containing QR codes",
    )

    parser.add_argument(
        "output",
        help="Output file path",
    )

    parser.add_argument(
        "--sample-rate",
        type=int,
        default=DEFAULT_SAMPLE_RATE,
        help=f"Process every Nth frame (default: {DEFAULT_SAMPLE_RATE})",
    )

    parser.add_argument(
        "--verify",
        metavar="ORIGINAL",
        help="Verify against original file",
    )

    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="Allow incomplete data (missing chunks)",
    )

    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Quiet mode (minimal output)",
    )

    parser.set_defaults(func=_qr_decode_command)


def _qr_decode_command(args) -> int:
    """Execute the qr-decode command."""
    # Create decoder
    decoder = QRDecoder(
        args.video,
        sample_rate=args.sample_rate,
        verbose=not args.quiet,
    )

    if not args.quiet:
        print("=" * 70, file=sys.stderr)
        print("Airgap Transfer - QR Code Decoder", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        print(f"\nVideo: {decoder.video_path}", file=sys.stderr)
        print(f"Output: {args.output}", file=sys.stderr)
        print(file=sys.stderr)

    # Progress callback
    def progress(frames, total, chunks):
        if not args.quiet:
            percent = (frames / total) * 100 if total > 0 else 0
            print(
                f"Progress: {frames}/{total} frames ({percent:.1f}%) - "
                f"Chunks collected: {chunks}",
                file=sys.stderr,
                end='\r'
            )

    # Decode video
    success = decoder.decode_to_file(
        args.output,
        allow_incomplete=args.allow_incomplete,
        progress_callback=progress if not args.quiet else None,
    )

    if not success:
        print("\nDecoding failed", file=sys.stderr)
        return 1

    # Print stats
    if not args.quiet:
        stats = decoder.get_stats()
        print(file=sys.stderr)
        print("-" * 70, file=sys.stderr)
        print("✓ Decoding complete!", file=sys.stderr)
        print(f"Frames processed: {stats['frames_processed']}/{stats['frames_total']}", file=sys.stderr)
        print(f"Chunks collected: {stats['chunks_collected']}/{stats['total_chunks']}", file=sys.stderr)
        print(f"Output file: {args.output}", file=sys.stderr)
        print("=" * 70, file=sys.stderr)

    # Verify if requested
    if args.verify:
        if not args.quiet:
            print(f"\nVerifying against: {args.verify}", file=sys.stderr)

        if compare_files(args.verify, args.output):
            print("✓ Files match! Transfer successful.", file=sys.stderr)
        else:
            print("✗ Files do not match!", file=sys.stderr)
            return 1

    return 0
