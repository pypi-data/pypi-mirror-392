"""QR code decoder for extracting files from video recordings."""

import re
import sys
from pathlib import Path
from typing import Optional, Callable

try:
    import cv2
    from pyzbar.pyzbar import decode as pyzbar_decode, ZBarSymbol
except ImportError:
    raise ImportError(
        "QR code dependencies not installed. "
        "Install with: pip install airgap-transfer[qrcode]"
    )

from ..utils import decode_base64, DEFAULT_SAMPLE_RATE


class QRDecoder:
    """
    Decode files from QR code video recordings.

    Extracts QR codes from video frames, reassembles the original file,
    and verifies integrity.
    """

    def __init__(
        self,
        video_path: str,
        sample_rate: int = DEFAULT_SAMPLE_RATE,
        verbose: bool = True,
    ):
        """
        Initialize QR code decoder.

        Args:
            video_path: Path to video file
            sample_rate: Process every Nth frame
            verbose: Enable verbose output

        Raises:
            FileNotFoundError: If video file doesn't exist
        """
        self.video_path = Path(video_path)
        self.sample_rate = sample_rate
        self.verbose = verbose

        if not self.video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        # Statistics
        self._chunks_collected = 0
        self._total_chunks = None
        self._frames_processed = 0
        self._frames_total = 0

    def _log(self, message: str) -> None:
        """Log message to stderr if verbose mode is enabled."""
        if self.verbose:
            print(message, file=sys.stderr)

    def decode_to_file(
        self,
        output_path: str,
        allow_incomplete: bool = False,
        progress_callback: Optional[Callable[[int, int, int], None]] = None,
    ) -> bool:
        """
        Decode video and save to file.

        Args:
            output_path: Output file path
            allow_incomplete: Allow incomplete data (missing chunks)
            progress_callback: Optional callback(frames_processed, total_frames, chunks_collected)

        Returns:
            True if successful, False otherwise
        """
        # Open video
        cap = cv2.VideoCapture(str(self.video_path))
        if not cap.isOpened():
            self._log(f"Error: Cannot open video file {self.video_path}")
            return False

        # Get video info
        self._frames_total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        self._log(f"Video info:")
        self._log(f"  Total frames: {self._frames_total}")
        self._log(f"  FPS: {fps:.2f}")
        self._log(f"  Sample rate: every {self.sample_rate} frames")

        # Process video
        chunks = {}
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Sample frames
            if frame_idx % self.sample_rate == 0:
                self._frames_processed += 1

                # Convert to grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Decode QR codes
                decoded_objects = pyzbar_decode(gray, symbols=[ZBarSymbol.QRCODE])

                if decoded_objects:
                    decoded_data = decoded_objects[0].data.decode('utf-8', errors='ignore')

                    try:
                        # Parse format: index/total|chunk_data
                        match = re.match(r'(\d+)/(\d+)\|(.*)', decoded_data, re.DOTALL)
                        if not match:
                            self._log(f"Warning: Frame {frame_idx} format mismatch")
                            frame_idx += 1
                            continue

                        chunk_index = int(match.group(1))
                        chunk_total = int(match.group(2))
                        chunk_data = match.group(3)

                        # Save total chunks
                        if self._total_chunks is None:
                            self._total_chunks = chunk_total
                            self._log(f"Detected total chunks: {self._total_chunks}")
                        elif self._total_chunks != chunk_total:
                            self._log(f"Warning: Frame {frame_idx} total chunks mismatch")
                            frame_idx += 1
                            continue

                        # Save chunk (avoid duplicates)
                        if chunk_index not in chunks:
                            chunks[chunk_index] = chunk_data
                            self._chunks_collected = len(chunks)

                            self._log(
                                f"Frame {frame_idx}: Decoded chunk {chunk_index}/{chunk_total} "
                                f"({self._chunks_collected}/{self._total_chunks} collected)"
                            )

                            # Check if all chunks collected
                            if self._chunks_collected == self._total_chunks:
                                self._log(f"All {self._total_chunks} chunks collected!")
                                cap.release()
                                return self._reconstruct_file(
                                    chunks, output_path, allow_incomplete
                                )

                    except Exception as e:
                        self._log(f"Warning: Frame {frame_idx} decode error: {e}")

            frame_idx += 1

            # Progress callback
            if progress_callback and frame_idx % 30 == 0:
                progress_callback(
                    frame_idx,
                    self._frames_total,
                    self._chunks_collected
                )

        cap.release()

        # Check completeness
        if self._total_chunks is None:
            self._log("Error: No valid QR codes detected")
            return False

        if self._chunks_collected < self._total_chunks:
            missing = [
                i for i in range(1, self._total_chunks + 1)
                if i not in chunks
            ]
            self._log(
                f"Warning: Only collected {self._chunks_collected}/{self._total_chunks} chunks"
            )
            self._log(f"Missing chunks: {missing[:10]}{'...' if len(missing) > 10 else ''}")

            if not allow_incomplete:
                self._log("Error: Incomplete data, cannot reconstruct file")
                return False

        # Reconstruct file
        return self._reconstruct_file(chunks, output_path, allow_incomplete)

    def _reconstruct_file(
        self,
        chunks: dict,
        output_path: str,
        allow_incomplete: bool = False
    ) -> bool:
        """
        Reconstruct file from chunks.

        Args:
            chunks: Dictionary of {chunk_index: chunk_data}
            output_path: Output file path
            allow_incomplete: Allow missing chunks

        Returns:
            True if successful, False otherwise
        """
        self._log("\nReconstructing file...")

        # Check for missing chunks
        missing_chunks = [
            i for i in range(1, self._total_chunks + 1)
            if i not in chunks
        ]
        if missing_chunks and not allow_incomplete:
            self._log("Error: Missing chunks, cannot reconstruct")
            return False

        # Concatenate chunks in order
        encoded_data = ""
        for i in range(1, self._total_chunks + 1):
            if i in chunks:
                encoded_data += chunks[i]
            elif allow_incomplete:
                self._log(f"Warning: Skipping missing chunk {i}")

        self._log(f"Concatenated base64 length: {len(encoded_data)} chars")

        # Decode base64
        try:
            file_data = decode_base64(encoded_data)
            self._log(f"Decoded file size: {len(file_data)} bytes")

            # Write to file
            with open(output_path, 'wb') as f:
                f.write(file_data)

            self._log(f"\nSuccess! File saved to: {output_path}")
            return True

        except Exception as e:
            self._log(f"Error: Base64 decode failed: {e}")

            # Try cleaning if incomplete
            if allow_incomplete:
                try:
                    # Remove non-base64 characters
                    clean_data = ''.join(
                        c for c in encoded_data
                        if c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
                    )
                    # Add padding
                    padding = (4 - len(clean_data) % 4) % 4
                    clean_data += '=' * padding

                    file_data = decode_base64(clean_data)

                    with open(output_path, 'wb') as f:
                        f.write(file_data)

                    self._log("Warning: Decoded using cleaned data (may be incomplete)")
                    self._log(f"File saved to: {output_path}")
                    return True

                except Exception as e2:
                    self._log(f"Error: Cleanup decode also failed: {e2}")

            return False

    def get_stats(self) -> dict:
        """
        Get decoding statistics.

        Returns:
            Dictionary with decoding stats
        """
        return {
            "video_path": str(self.video_path),
            "frames_processed": self._frames_processed,
            "frames_total": self._frames_total,
            "chunks_collected": self._chunks_collected,
            "total_chunks": self._total_chunks,
            "sample_rate": self.sample_rate,
        }
