#!/usr/bin/env python3
"""
Example: Keyboard Transfer

This example demonstrates how to use the KeyboardTransfer class to
transfer files via simulated keyboard input.
"""

from airgap_transfer import KeyboardTransfer


def main():
    # Example 1: Basic transfer
    print("Example 1: Basic keyboard transfer")
    print("-" * 60)

    transfer = KeyboardTransfer("test.txt", output_path="/tmp/transferred.txt")
    print(f"Source: {transfer.file_path}")
    print(f"Target: {transfer.output_path}")

    # Generate script without executing
    script = transfer.generate_script()
    print(f"\nGenerated script length: {len(script)} characters")
    print(f"First 200 characters:\n{script[:200]}...")

    # Example 2: Using speed presets
    print("\n\nExample 2: Speed presets")
    print("-" * 60)

    fast_transfer = KeyboardTransfer.from_speed_preset(
        "test.txt",
        speed="fast"
    )
    print(f"Fast mode - char delay: {fast_transfer.char_delay}s")

    slow_transfer = KeyboardTransfer.from_speed_preset(
        "test.txt",
        speed="slow"
    )
    print(f"Slow mode - char delay: {slow_transfer.char_delay}s")

    # Example 3: Execute transfer (commented out to avoid requiring X server)
    print("\n\nExample 3: Execute transfer")
    print("-" * 60)
    print("To execute a transfer:")
    print("""
    transfer = KeyboardTransfer("myfile.pdf")
    stats = transfer.send(countdown=5, auto_execute=True)
    print(f"Transfer completed in {stats['elapsed_time']:.1f} seconds")
    print(f"Average speed: {stats['chars_per_second']:.0f} chars/sec")
    """)


if __name__ == "__main__":
    main()
