#!/usr/bin/env python3
"""
Example: QR Code Encoding

This example demonstrates how to encode files as QR code sequences.

Note: Requires QR code dependencies:
    pip install airgap-transfer[qrcode]
"""

import sys

try:
    from airgap_transfer import QREncoder
except ImportError as e:
    print(f"Error: {e}")
    print("\nPlease install QR code dependencies:")
    print("    pip install airgap-transfer[qrcode]")
    sys.exit(1)


def main():
    # Example 1: Get encoding statistics
    print("Example 1: Get encoding statistics")
    print("-" * 60)

    encoder = QREncoder("test.txt", chunk_size=800, first_frame_duration=3)

    # Prepare data to get statistics
    encoder._prepare_data()
    stats = encoder.get_stats()

    print(f"File: {stats['file_path']}")
    print(f"File size: {stats['file_size']} bytes")
    print(f"Encoded size: {stats['encoded_size']} bytes")
    print(f"Chunk size: {stats['chunk_size']} bytes")
    print(f"Total QR codes: {stats['total_chunks']}")
    print(f"QR version: {stats['qr_version']}")

    # Example 2: Encode to stream
    print("\n\nExample 2: Encode to stream")
    print("-" * 60)
    print("To encode a file to stdout:")
    print("""
    encoder = QREncoder("myfile.pdf")
    encoder.encode_to_stream(sys.stdout.buffer)
    """)

    print("\nTo pipe to ffplay:")
    print("""
    python example.py | ffplay -framerate 1 -f image2pipe -i -
    """)

    print("\nOr use the CLI:")
    print("""
    airgap qr-encode myfile.pdf | ffplay -framerate 1 -f image2pipe -i -
    """)


if __name__ == "__main__":
    main()
