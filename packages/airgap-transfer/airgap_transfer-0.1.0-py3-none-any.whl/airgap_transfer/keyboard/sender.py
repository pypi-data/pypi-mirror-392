"""Keyboard-based file transfer sender."""

import time
from pathlib import Path
from typing import Optional, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from pynput.keyboard import Controller, Key

from ..utils import (
    encode_base64,
    calculate_file_checksum,
    split_into_lines,
    DEFAULT_CHAR_DELAY,
    DEFAULT_LINE_DELAY,
    DEFAULT_COUNTDOWN,
    SPEED_PRESETS,
)


def _lazy_import_pynput():
    """Lazy import pynput to avoid X server requirement at import time."""
    try:
        from pynput.keyboard import Controller, Key
        return Controller, Key
    except ImportError as e:
        raise ImportError(
            "pynput is required for keyboard transfer. "
            "Install with: pip install pynput\n"
            f"Original error: {e}"
        ) from e


class KeyboardTransfer:
    """
    Transfer files to remote terminals by simulating keyboard input.

    This class generates a self-contained bash script that decodes and verifies
    the transferred file, then types it into the active terminal window.
    """

    def __init__(
        self,
        file_path: str,
        output_path: Optional[str] = None,
        char_delay: float = DEFAULT_CHAR_DELAY,
        line_delay: float = DEFAULT_LINE_DELAY,
    ):
        """
        Initialize keyboard file transfer.

        Args:
            file_path: Path to the file to transfer
            output_path: Remote output file path (defaults to same filename)
            char_delay: Delay between characters in seconds
            line_delay: Delay between lines in seconds

        Raises:
            FileNotFoundError: If the source file doesn't exist
        """
        self.file_path = Path(file_path)
        self.output_path = output_path or self.file_path.name
        self.char_delay = char_delay
        self.line_delay = line_delay
        self._keyboard = None  # Lazy initialization
        self._Controller = None
        self._Key = None

        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

    @property
    def keyboard(self):
        """Lazy-load pynput Controller."""
        if self._keyboard is None:
            Controller, _ = _lazy_import_pynput()
            self._keyboard = Controller()
        return self._keyboard

    @property
    def Key(self):
        """Lazy-load pynput Key."""
        if self._Key is None:
            _, Key = _lazy_import_pynput()
            self._Key = Key
        return self._Key

    @classmethod
    def from_speed_preset(
        cls,
        file_path: str,
        output_path: Optional[str] = None,
        speed: str = "normal",
    ) -> "KeyboardTransfer":
        """
        Create a KeyboardTransfer instance using a speed preset.

        Args:
            file_path: Path to the file to transfer
            output_path: Remote output file path
            speed: Speed preset ("slow", "normal", or "fast")

        Returns:
            KeyboardTransfer instance

        Raises:
            ValueError: If speed preset is invalid
        """
        if speed not in SPEED_PRESETS:
            raise ValueError(
                f"Invalid speed preset: {speed}. "
                f"Choose from: {', '.join(SPEED_PRESETS.keys())}"
            )

        preset = SPEED_PRESETS[speed]
        return cls(
            file_path=file_path,
            output_path=output_path,
            char_delay=preset["char_delay"],
            line_delay=preset["line_delay"],
        )

    def generate_script(self) -> str:
        """
        Generate the bash script for file transfer.

        Returns:
            Complete bash script as string
        """
        # Read and encode file
        with open(self.file_path, 'rb') as f:
            file_data = f.read()

        checksum = calculate_file_checksum(self.file_path)
        encoded = encode_base64(file_data)

        # Split into lines (76 chars per line, standard for base64)
        data_lines = '\n'.join(split_into_lines(encoded, 76))

        # Generate bash script
        script = f'''bash << 'END_OF_SCRIPT'
OUTPUT_FILE="{self.output_path}"
EXPECTED_CHECKSUM="{checksum}"

echo "========================================"
echo "Decoding file: $OUTPUT_FILE"
echo "========================================"

# Decode Base64 data
cat << 'END_OF_BASE64' | base64 -d > "$OUTPUT_FILE"
{data_lines}
END_OF_BASE64

# Verify checksum
if command -v sha256sum > /dev/null 2>&1; then
    ACTUAL_CHECKSUM=$(sha256sum "$OUTPUT_FILE" | awk '{{print $1}}')
elif command -v shasum > /dev/null 2>&1; then
    ACTUAL_CHECKSUM=$(shasum -a 256 "$OUTPUT_FILE" | awk '{{print $1}}')
else
    echo "Warning: No checksum tool found, skipping verification"
    ACTUAL_CHECKSUM="$EXPECTED_CHECKSUM"
fi

# Display results
echo ""
if [ "$ACTUAL_CHECKSUM" = "$EXPECTED_CHECKSUM" ]; then
    echo "✓ File transfer successful! Checksum verified"
    echo "File saved to: $OUTPUT_FILE"
    ls -lh "$OUTPUT_FILE"
else
    echo "✗ Error: Checksum mismatch!"
    echo "Expected: $EXPECTED_CHECKSUM"
    echo "Actual: $ACTUAL_CHECKSUM"
fi
echo "========================================"
END_OF_SCRIPT
'''
        return script

    def _type_char_safe(self, char: str) -> None:
        """
        Safely type a single character, handling special cases.

        Args:
            char: Character to type
        """
        if char.isupper():
            # Handle uppercase letters with shift
            self.keyboard.press(self.Key.shift)
            time.sleep(0.001)
            self.keyboard.press(char.lower())
            time.sleep(0.001)
            self.keyboard.release(char.lower())
            self.keyboard.release(self.Key.shift)
        else:
            # pynput handles other characters automatically
            self.keyboard.type(char)

    def _type_text(
        self,
        text: str,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> None:
        """
        Type text by simulating keyboard input.

        Args:
            text: Text to type
            progress_callback: Optional callback(current_line, total_lines)
        """
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        lines = text.split('\n')
        total_lines = len(lines)

        for i, line in enumerate(lines):
            # Progress callback
            if progress_callback and i % 50 == 0:
                progress_callback(i + 1, total_lines)

            # Type each character
            for char in line:
                self._type_char_safe(char)
                time.sleep(self.char_delay)

            # Press Enter (except for last line)
            if i < total_lines - 1:
                self.keyboard.press(self.Key.enter)
                time.sleep(0.015)
                self.keyboard.release(self.Key.enter)
                time.sleep(self.line_delay)

        # Final progress update
        if progress_callback:
            progress_callback(total_lines, total_lines)

    def send(
        self,
        countdown: int = DEFAULT_COUNTDOWN,
        auto_execute: bool = True,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> dict:
        """
        Execute the file transfer.

        Args:
            countdown: Countdown seconds before starting
            auto_execute: Whether to automatically press Enter to execute
            progress_callback: Optional callback(current_line, total_lines)

        Returns:
            Dictionary with transfer statistics
        """
        # Generate script
        script = self.generate_script()

        # Countdown
        for i in range(countdown, 0, -1):
            if progress_callback:
                progress_callback(countdown - i, countdown)
            time.sleep(1)

        # Type the script
        start_time = time.time()
        self._type_text(script, progress_callback)

        # Auto-execute if requested
        if auto_execute:
            time.sleep(0.5)  # Brief delay to ensure typing is complete
            self.keyboard.press(self.Key.enter)
            time.sleep(0.015)
            self.keyboard.release(self.Key.enter)

        elapsed_time = time.time() - start_time

        # Return statistics
        return {
            "file_path": str(self.file_path),
            "output_path": self.output_path,
            "file_size": self.file_path.stat().st_size,
            "script_length": len(script),
            "elapsed_time": elapsed_time,
            "chars_per_second": len(script) / elapsed_time if elapsed_time > 0 else 0,
            "auto_executed": auto_execute,
        }
