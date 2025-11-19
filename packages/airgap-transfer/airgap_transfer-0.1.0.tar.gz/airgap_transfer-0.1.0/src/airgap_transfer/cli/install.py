"""CLI command for installing sender tools to air-gapped environments."""

import argparse
import sys
from pathlib import Path


def register_subcommand(subparsers) -> None:
    """Register the 'install' subcommand."""
    parser = subparsers.add_parser(
        "install",
        help="Install sender tools to air-gapped environment",
        description="Generate and transfer sender tools to isolated environments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate sender package
  airgap install --generate

  # Generate to specific directory
  airgap install --generate --output ./sender-bundle

  # Generate standalone script
  airgap install --generate --standalone --output qr_sender.py

  # Show bundle information
  airgap install --show

  # Transfer to remote via keyboard
  airgap install --transfer

Workflow:
  1. Generate the installation bundle: airgap install --generate
  2. Transfer to air-gapped environment: airgap install --transfer
  3. In the remote environment, run: bash install.sh
        """,
    )

    parser.add_argument(
        "--generate",
        action="store_true",
        help="Generate sender package",
    )

    parser.add_argument(
        "--output",
        default="./sender-bundle",
        help="Output directory or file path (default: ./sender-bundle)",
    )

    parser.add_argument(
        "--standalone",
        action="store_true",
        help="Generate standalone single-file script",
    )

    parser.add_argument(
        "--transfer",
        action="store_true",
        help="Transfer installation bundle via keyboard",
    )

    parser.add_argument(
        "--show",
        action="store_true",
        help="Show information about the bundle",
    )

    parser.add_argument(
        "--countdown",
        type=int,
        default=5,
        help="Countdown seconds before transfer (default: 5)",
    )

    parser.set_defaults(func=_install_command)


def _install_command(args) -> int:
    """Execute the install command."""
    from ..installer import SenderPackager

    print("=" * 70)
    print("Airgap Transfer - Install Sender Tools")
    print("=" * 70)
    print()

    # Handle --show
    if args.show:
        packager = SenderPackager(args.output)
        info = packager.get_bundle_info()

        print("Bundle Information:")
        print(f"  Version: {info['version']}")
        print(f"  Output directory: {info['output_dir']}")
        print(f"  Templates: {info['templates_dir']}")
        print()
        print("Files in bundle:")
        for filename in info['files']:
            print(f"  - {filename}")
        print()
        print("To generate the bundle, run:")
        print("  airgap install --generate")
        print("=" * 70)
        return 0

    # Handle --generate with --standalone
    if args.generate and args.standalone:
        try:
            packager = SenderPackager()
            output_file = packager.generate_standalone(args.output)

            print(f"✓ Generated standalone sender script:")
            print(f"  {output_file}")
            print()
            print("Transfer to air-gapped environment:")
            print(f"  airgap send {output_file}")
            print()
            print("Usage in air-gapped environment:")
            print(f"  python3 {output_file.name} myfile.pdf 5 | ffplay -framerate 1 -f image2pipe -i -")
            print("=" * 70)
            return 0

        except Exception as e:
            print(f"✗ Error generating standalone script: {e}", file=sys.stderr)
            return 1

    # Handle --generate (full bundle)
    if args.generate:
        try:
            packager = SenderPackager(args.output)
            bundle_path = packager.generate()

            print(f"✓ Generated sender installation bundle:")
            print(f"  {bundle_path.absolute()}")
            print()
            print("Contents:")
            for item in bundle_path.iterdir():
                size = item.stat().st_size
                print(f"  - {item.name} ({size:,} bytes)")
            print()
            print("Next steps:")
            print("1. Transfer the bundle to air-gapped environment:")
            print(f"   airgap install --transfer")
            print()
            print("2. Or manually transfer files:")
            print(f"   airgap send {bundle_path}/qr_sender.py")
            print(f"   airgap send {bundle_path}/install.sh")
            print()
            print("3. In the air-gapped environment, run:")
            print("   bash install.sh")
            print("=" * 70)
            return 0

        except FileExistsError as e:
            print(f"✗ Error: {e}", file=sys.stderr)
            print("  Use --output to specify a different directory", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"✗ Error generating bundle: {e}", file=sys.stderr)
            return 1

    # Handle --transfer
    if args.transfer:
        try:
            packager = SenderPackager(args.output)

            # Check if bundle exists
            if not packager.output_dir.exists():
                print(f"✗ Bundle not found at: {packager.output_dir}")
                print()
                print("Generate the bundle first:")
                print("  airgap install --generate")
                print("=" * 70)
                return 1

            print("Starting transfer of installation bundle via keyboard...")
            print()
            packager.transfer_to_remote(countdown=args.countdown)
            print("=" * 70)
            return 0

        except ImportError as e:
            print(f"✗ Error: {e}", file=sys.stderr)
            print("  Install keyboard dependencies: pip install airgap-transfer", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"✗ Error during transfer: {e}", file=sys.stderr)
            return 1

    # No action specified
    print("No action specified. Use one of:")
    print("  --generate    Generate sender package")
    print("  --standalone  Generate standalone script")
    print("  --transfer    Transfer via keyboard")
    print("  --show        Show bundle information")
    print()
    print("For more information, run:")
    print("  airgap install --help")
    print("=" * 70)

    return 1
