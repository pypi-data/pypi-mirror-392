"""QR code encoder for file transfer via video stream."""

import math
import sys
from io import BytesIO
from pathlib import Path
from typing import Optional, BinaryIO, Callable

try:
    import qrcode
    import qrcode.constants
except ImportError:
    raise ImportError(
        "QR code dependencies not installed. "
        "Install with: pip install airgap-transfer[qrcode]"
    )

from ..utils import (
    encode_base64,
    DEFAULT_QR_CHUNK_SIZE,
    DEFAULT_QR_BOX_SIZE,
    DEFAULT_QR_BORDER,
    DEFAULT_FIRST_FRAME_DURATION,
)


class QREncoder:
    """
    Encode files as QR code sequences for video transfer.

    Splits files into chunks, encodes each as a QR code, and outputs
    PNG images that can be piped to video players or recording tools.
    """

    def __init__(
        self,
        file_path: str,
        chunk_size: int = DEFAULT_QR_CHUNK_SIZE,
        first_frame_duration: int = DEFAULT_FIRST_FRAME_DURATION,
        box_size: int = DEFAULT_QR_BOX_SIZE,
        border: int = DEFAULT_QR_BORDER,
    ):
        """
        Initialize QR code encoder.

        Args:
            file_path: Path to file to encode
            chunk_size: Bytes per QR code chunk
            first_frame_duration: Duration of first frame in seconds
            box_size: Size of each QR code box
            border: Border size around QR code

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        self.file_path = Path(file_path)
        self.chunk_size = chunk_size
        self.first_frame_duration = first_frame_duration
        self.box_size = box_size
        self.border = border

        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Statistics
        self._file_size = 0
        self._encoded_size = 0
        self._total_chunks = 0
        self._qr_version = None

    def _prepare_data(self) -> tuple[list[str], int]:
        """
        Read and prepare file data for encoding.

        Returns:
            Tuple of (qr_data_list, qr_version)
        """
        # Read and encode file
        with open(self.file_path, 'rb') as f:
            file_data = f.read()

        self._file_size = len(file_data)
        encoded_data = encode_base64(file_data)
        self._encoded_size = len(encoded_data)
        self._total_chunks = math.ceil(len(encoded_data) / self.chunk_size)

        # Prepare all QR data strings
        qr_data_list = []
        for i in range(self._total_chunks):
            start = i * self.chunk_size
            end = min((i + 1) * self.chunk_size, len(encoded_data))
            chunk = encoded_data[start:end]
            qr_data = f"{i+1}/{self._total_chunks}|{chunk}"
            qr_data_list.append(qr_data)

        # Determine QR version from longest data
        max_data = max(qr_data_list, key=len)
        temp_qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=self.box_size,
            border=self.border,
        )
        temp_qr.add_data(max_data)
        temp_qr.make(fit=True)
        self._qr_version = temp_qr.version

        return qr_data_list, self._qr_version

    def _generate_qr_image(self, qr_data: str, version: int) -> bytes:
        """
        Generate QR code image as PNG bytes.

        Args:
            qr_data: Data to encode
            version: QR code version (for consistent sizing)

        Returns:
            PNG image data as bytes
        """
        qr = qrcode.QRCode(
            version=version,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=self.box_size,
            border=self.border,
        )
        qr.add_data(qr_data)
        qr.make(fit=False)  # Don't auto-adjust, use fixed version

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to PNG bytes
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG')
        return img_buffer.getvalue()

    def encode_to_stream(
        self,
        output_stream: BinaryIO = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> None:
        """
        Encode file to QR code PNG stream.

        Args:
            output_stream: Output stream (defaults to stdout)
            progress_callback: Optional callback(current_chunk, total_chunks)
        """
        if output_stream is None:
            output_stream = sys.stdout.buffer

        # Prepare data
        qr_data_list, qr_version = self._prepare_data()

        # Generate QR codes
        for i, qr_data in enumerate(qr_data_list):
            img_data = self._generate_qr_image(qr_data, qr_version)

            # First frame: repeat for specified duration
            if i == 0:
                for _ in range(self.first_frame_duration):
                    output_stream.write(img_data)
            else:
                output_stream.write(img_data)

            # Progress callback
            if progress_callback:
                progress_callback(i + 1, self._total_chunks)

    def get_stats(self) -> dict:
        """
        Get encoding statistics.

        Returns:
            Dictionary with encoding stats
        """
        return {
            "file_path": str(self.file_path),
            "file_size": self._file_size,
            "encoded_size": self._encoded_size,
            "chunk_size": self.chunk_size,
            "total_chunks": self._total_chunks,
            "qr_version": self._qr_version,
            "first_frame_duration": self.first_frame_duration,
        }
