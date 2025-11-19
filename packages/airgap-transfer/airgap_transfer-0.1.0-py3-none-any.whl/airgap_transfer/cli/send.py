"""CLI command for keyboard-based file transfer."""

import argparse
from ..keyboard import KeyboardTransfer
from ..utils import SPEED_PRESETS, DEFAULT_COUNTDOWN


def register_subcommand(subparsers) -> None:
    """Register the 'send' subcommand."""
    parser = subparsers.add_parser(
        "send",
        help="Transfer files via keyboard input simulation",
        description="Transfer files to remote terminals by simulating keyboard input",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic transfer
  airgap send myfile.pdf

  # Specify remote output path
  airgap send myfile.pdf --output /tmp/received.pdf

  # Use speed preset
  airgap send myfile.pdf --fast
  airgap send myfile.pdf --slow

  # Custom timing
  airgap send myfile.pdf --char-delay 0.01 --line-delay 0.05

  # Disable auto-execute (manual Enter press required)
  airgap send myfile.pdf --no-auto-execute

  # Custom countdown
  airgap send myfile.pdf --countdown 10
        """,
    )

    parser.add_argument(
        "file",
        help="File to transfer",
    )

    parser.add_argument(
        "-o", "--output",
        help="Remote output file path (default: same filename)",
    )

    # Speed presets
    speed_group = parser.add_mutually_exclusive_group()
    speed_group.add_argument(
        "--fast",
        action="store_true",
        help="Fast mode (for local VMs)",
    )
    speed_group.add_argument(
        "--slow",
        action="store_true",
        help="Slow mode (for high-latency remote desktops)",
    )

    # Custom timing
    parser.add_argument(
        "--char-delay",
        type=float,
        help="Delay between characters in seconds",
    )
    parser.add_argument(
        "--line-delay",
        type=float,
        help="Delay between lines in seconds",
    )

    # Transfer options
    parser.add_argument(
        "--countdown",
        type=int,
        default=DEFAULT_COUNTDOWN,
        help=f"Countdown before transfer starts (default: {DEFAULT_COUNTDOWN})",
    )
    parser.add_argument(
        "--no-auto-execute",
        action="store_true",
        help="Don't automatically press Enter to execute",
    )

    parser.set_defaults(func=_send_command)


def _send_command(args) -> int:
    """Execute the send command."""
    # Determine speed preset
    speed = None
    if args.fast:
        speed = "fast"
    elif args.slow:
        speed = "slow"

    # Create transfer instance
    if speed and not (args.char_delay or args.line_delay):
        # Use speed preset
        transfer = KeyboardTransfer.from_speed_preset(
            args.file,
            args.output,
            speed=speed,
        )
    else:
        # Use custom or default timing
        kwargs = {}
        if args.char_delay:
            kwargs["char_delay"] = args.char_delay
        if args.line_delay:
            kwargs["line_delay"] = args.line_delay

        transfer = KeyboardTransfer(
            args.file,
            args.output,
            **kwargs,
        )

    # Print header
    print("=" * 70)
    print("Airgap Transfer - Keyboard Transfer")
    print("=" * 70)
    print(f"\nSource file: {transfer.file_path}")
    print(f"Target file: {transfer.output_path}")
    print(f"File size: {transfer.file_path.stat().st_size:,} bytes")

    # Generate script to show stats
    script = transfer.generate_script()
    print(f"Script length: {len(script):,} characters")
    print(f"Script lines: {len(script.splitlines())}")

    # Instructions
    print(f"\nPlease switch to the remote terminal within {args.countdown} seconds")
    print()
    print("=" * 70)
    print("IMPORTANT!")
    print("=" * 70)
    print("In the remote terminal:")
    print()
    print("  1. Ensure terminal is at a clean prompt (e.g., $ or ➜)")
    print("  2. Do not type anything, just keep terminal focused")
    print("  3. Wait for automatic input and execution")
    print()
    print("The script will automatically:")
    print("  - Decode the file")
    print("  - Verify checksum")
    print("  - Display results")
    print()
    if args.no_auto_execute:
        print("Note: You will need to press Enter manually to execute")
    else:
        print("You don't need to do anything, just wait!")
    print("=" * 70)
    print()

    # Progress callback
    def progress(current, total):
        if current % 50 == 0 or current == total:
            percent = (current / total) * 100 if total > 0 else 0
            print(f"Progress: {percent:.1f}% ({current}/{total} lines)", end='\r')

    # Execute transfer
    stats = transfer.send(
        countdown=args.countdown,
        auto_execute=not args.no_auto_execute,
        progress_callback=progress,
    )

    # Print results
    print()
    print("-" * 70)
    print("✓ Transfer complete!")
    print(f"Elapsed time: {stats['elapsed_time']:.1f} seconds")
    print(f"Average speed: {stats['chars_per_second']:.0f} chars/second")
    print()
    print("=" * 70)
    print("Next steps:")
    print("=" * 70)
    if stats['auto_executed']:
        print("Command executed automatically. Check the remote terminal for results!")
    else:
        print("Press Enter in the remote terminal to execute the command")
    print("=" * 70)

    return 0
