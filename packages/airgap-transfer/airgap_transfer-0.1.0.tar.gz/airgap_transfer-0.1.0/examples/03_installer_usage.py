#!/usr/bin/env python3
"""
Example: Using the Installer Module

This example demonstrates how to use the SenderPackager to generate
standalone installation bundles for air-gapped environments.
"""

from airgap_transfer import SenderPackager


def example_generate_bundle():
    """Generate a complete installation bundle."""
    print("=" * 70)
    print("Example 1: Generate Installation Bundle")
    print("=" * 70)
    print()

    # Create packager instance
    packager = SenderPackager(output_dir="./my-sender-bundle")

    # Get bundle information before generating
    info = packager.get_bundle_info()
    print("Bundle Information:")
    print(f"  Version: {info['version']}")
    print(f"  Output: {info['output_dir']}")
    print(f"  Files: {', '.join(info['files'])}")
    print()

    # Generate the bundle
    print("Generating bundle...")
    bundle_path = packager.generate(clean=True)

    print(f"✓ Bundle generated at: {bundle_path}")
    print()
    print("Contents:")
    for item in bundle_path.iterdir():
        size = item.stat().st_size
        print(f"  - {item.name} ({size:,} bytes)")
    print()


def example_generate_standalone():
    """Generate a standalone single-file sender."""
    print("=" * 70)
    print("Example 2: Generate Standalone Script")
    print("=" * 70)
    print()

    packager = SenderPackager()

    # Generate standalone script
    print("Generating standalone script...")
    script_path = packager.generate_standalone("./qr_sender_standalone.py")

    print(f"✓ Standalone script generated: {script_path}")
    print(f"  Size: {script_path.stat().st_size:,} bytes")
    print()
    print("Transfer to air-gapped environment:")
    print(f"  airgap send {script_path}")
    print()


def example_transfer_workflow():
    """Demonstrate the complete transfer workflow (informational only)."""
    print("=" * 70)
    print("Example 3: Complete Transfer Workflow")
    print("=" * 70)
    print()

    print("Step 1: Generate the installation bundle")
    print("  packager = SenderPackager('./sender-bundle')")
    print("  bundle_path = packager.generate()")
    print()

    print("Step 2: Transfer to air-gapped environment")
    print("  Option A - Via CLI:")
    print("    airgap install --transfer")
    print()
    print("  Option B - Via Python API:")
    print("    packager.transfer_to_remote(countdown=5)")
    print()

    print("Step 3: In the air-gapped environment")
    print("  bash install.sh")
    print()

    print("Step 4: Use the sender in air-gapped environment")
    print("  python3 ~/airgap_tools/qr_sender.py myfile.pdf 5 | ffplay -framerate 1 -f image2pipe -i -")
    print()


def main():
    """Run all examples."""
    # Example 1: Generate full bundle
    example_generate_bundle()

    print()
    input("Press Enter to continue to next example...")
    print()

    # Example 2: Generate standalone
    example_generate_standalone()

    print()
    input("Press Enter to continue to next example...")
    print()

    # Example 3: Show workflow
    example_transfer_workflow()

    print()
    print("=" * 70)
    print("Examples Complete!")
    print("=" * 70)
    print()
    print("To clean up generated files:")
    print("  rm -rf my-sender-bundle qr_sender_standalone.py")
    print()


if __name__ == "__main__":
    main()
