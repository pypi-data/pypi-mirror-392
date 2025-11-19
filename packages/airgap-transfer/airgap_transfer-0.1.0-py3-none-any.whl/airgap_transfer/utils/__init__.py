"""Utility functions for airgap-transfer."""

from .checksum import (
    calculate_sha256,
    calculate_file_checksum,
    verify_checksum,
    compare_files,
)
from .encoding import (
    encode_base64,
    decode_base64,
    split_into_chunks,
    split_into_lines,
)
from .constants import (
    DEFAULT_CHAR_DELAY,
    DEFAULT_LINE_DELAY,
    DEFAULT_COUNTDOWN,
    SPEED_PRESETS,
    DEFAULT_QR_CHUNK_SIZE,
    DEFAULT_QR_ERROR_CORRECTION,
    DEFAULT_QR_BOX_SIZE,
    DEFAULT_QR_BORDER,
    DEFAULT_FIRST_FRAME_DURATION,
    DEFAULT_SAMPLE_RATE,
)

__all__ = [
    # Checksum functions
    "calculate_sha256",
    "calculate_file_checksum",
    "verify_checksum",
    "compare_files",
    # Encoding functions
    "encode_base64",
    "decode_base64",
    "split_into_chunks",
    "split_into_lines",
    # Constants
    "DEFAULT_CHAR_DELAY",
    "DEFAULT_LINE_DELAY",
    "DEFAULT_COUNTDOWN",
    "SPEED_PRESETS",
    "DEFAULT_QR_CHUNK_SIZE",
    "DEFAULT_QR_ERROR_CORRECTION",
    "DEFAULT_QR_BOX_SIZE",
    "DEFAULT_QR_BORDER",
    "DEFAULT_FIRST_FRAME_DURATION",
    "DEFAULT_SAMPLE_RATE",
]
