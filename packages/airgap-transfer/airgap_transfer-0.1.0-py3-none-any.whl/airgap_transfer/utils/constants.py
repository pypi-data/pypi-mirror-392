"""Constants used throughout the airgap-transfer package."""

# Default timing parameters for keyboard transfer
DEFAULT_CHAR_DELAY = 0.005  # seconds between characters
DEFAULT_LINE_DELAY = 0.03   # seconds between lines
DEFAULT_COUNTDOWN = 5       # seconds before transfer starts

# Speed presets for keyboard transfer
SPEED_PRESETS = {
    "slow": {"char_delay": 0.01, "line_delay": 0.05},
    "normal": {"char_delay": 0.005, "line_delay": 0.03},
    "fast": {"char_delay": 0.002, "line_delay": 0.01},
}

# QR code parameters
DEFAULT_QR_CHUNK_SIZE = 800  # bytes per QR code
DEFAULT_QR_ERROR_CORRECTION = "H"  # High error correction
DEFAULT_QR_BOX_SIZE = 10
DEFAULT_QR_BORDER = 4
DEFAULT_FIRST_FRAME_DURATION = 3  # seconds

# Video decoding parameters
DEFAULT_SAMPLE_RATE = 1  # process every N frames
