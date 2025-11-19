"""Main CLI entry point for airgap-transfer."""

import sys
import argparse
from .. import __version__


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="airgap",
        description="Bi-directional file transfer for air-gapped and isolated environments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Subcommands:
  send        Transfer files via keyboard input
  qr-encode   Encode files as QR code video stream
  qr-decode   Decode files from QR code video
  install     Install sender tools to air-gapped environment

Examples:
  airgap send myfile.pdf
  airgap qr-encode myfile.pdf | ffplay -framerate 1 -f image2pipe -i -
  airgap qr-decode recording.mp4 output.pdf
  airgap install --generate

For detailed help on each subcommand:
  airgap send --help
  airgap qr-encode --help
  airgap qr-decode --help
  airgap install --help
        """,
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"airgap-transfer {__version__}",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="subcommands",
        description="Available subcommands",
    )

    # Import and register subcommands (lazy import to avoid dependency issues)
    # Only import the modules when the parser is being built
    try:
        from . import send
        send.register_subcommand(subparsers)
    except ImportError as e:
        # If send fails, it's a critical error since it only needs pynput
        pass

    try:
        from . import qr_encode
        qr_encode.register_subcommand(subparsers)
    except ImportError:
        # QR encode requires optional dependencies
        pass

    try:
        from . import qr_decode
        qr_decode.register_subcommand(subparsers)
    except ImportError:
        # QR decode requires optional dependencies
        pass

    try:
        from . import install
        install.register_subcommand(subparsers)
    except ImportError:
        pass

    # Parse arguments
    args = parser.parse_args()

    # Execute subcommand
    if not args.command:
        parser.print_help()
        return 1

    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        if hasattr(args, 'debug') and args.debug:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
