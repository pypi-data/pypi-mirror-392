"""Tests for QR encoder module."""

import pytest
from pathlib import Path
from io import BytesIO
from unittest.mock import Mock, patch

# Skip all tests if qrcode is not available
pytest.importorskip("qrcode")

from airgap_transfer.qrcode import QREncoder
from airgap_transfer.utils import DEFAULT_QR_CHUNK_SIZE


@pytest.fixture
def test_file(tmp_path):
    """Create a temporary test file."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello, QR World!" * 10)
    return str(test_file)


@pytest.fixture
def small_file(tmp_path):
    """Create a very small test file."""
    test_file = tmp_path / "small.txt"
    test_file.write_text("Hi")
    return str(test_file)


@pytest.fixture
def large_file(tmp_path):
    """Create a larger test file that will span multiple chunks."""
    test_file = tmp_path / "large.bin"
    # Create file larger than default chunk size
    test_file.write_bytes(b"X" * (DEFAULT_QR_CHUNK_SIZE * 3))
    return str(test_file)


class TestQREncoder:
    """Test cases for QREncoder class."""

    def test_init_with_defaults(self, test_file):
        """Test initialization with default parameters."""
        encoder = QREncoder(test_file)

        assert encoder.file_path == Path(test_file)
        assert encoder.chunk_size == DEFAULT_QR_CHUNK_SIZE
        assert encoder.first_frame_duration == 3

    def test_init_with_custom_params(self, test_file):
        """Test initialization with custom parameters."""
        chunk_size = 500
        duration = 10
        box_size = 15
        border = 5

        encoder = QREncoder(
            test_file,
            chunk_size=chunk_size,
            first_frame_duration=duration,
            box_size=box_size,
            border=border,
        )

        assert encoder.chunk_size == chunk_size
        assert encoder.first_frame_duration == duration
        assert encoder.box_size == box_size
        assert encoder.border == border

    def test_init_file_not_found(self):
        """Test initialization with non-existent file."""
        with pytest.raises(FileNotFoundError):
            QREncoder("/nonexistent/file.txt")

    def test_encode_small_file(self, small_file):
        """Test encoding a small file."""
        encoder = QREncoder(small_file)
        output = BytesIO()

        encoder.encode_to_stream(output)

        # Output should contain PNG data
        data = output.getvalue()
        assert len(data) > 0
        assert data[:8] == b'\x89PNG\r\n\x1a\n'  # PNG signature

    def test_encode_with_progress_callback(self, test_file):
        """Test encoding with progress callback."""
        encoder = QREncoder(test_file)
        output = BytesIO()

        progress_calls = []

        def progress_callback(current, total):
            progress_calls.append((current, total))

        encoder.encode_to_stream(output, progress_callback=progress_callback)

        # Verify progress was called
        assert len(progress_calls) > 0
        # Verify last call shows completion
        assert progress_calls[-1][0] == progress_calls[-1][1]

    def test_get_stats(self, test_file):
        """Test getting encoding statistics."""
        encoder = QREncoder(test_file)
        output = BytesIO()

        # Need to encode first to populate stats
        encoder.encode_to_stream(output)

        stats = encoder.get_stats()

        assert "file_path" in stats
        assert "file_size" in stats
        assert "encoded_size" in stats
        assert "total_chunks" in stats
        assert "qr_version" in stats
        assert stats["file_size"] > 0
        assert stats["total_chunks"] > 0

    def test_multiple_chunks(self, large_file):
        """Test encoding file that spans multiple chunks."""
        encoder = QREncoder(large_file, chunk_size=100)
        output = BytesIO()

        encoder.encode_to_stream(output)

        stats = encoder.get_stats()
        # With chunk size 100 and file size > 300, should have multiple chunks
        assert stats["total_chunks"] > 1

    def test_first_frame_duration(self, small_file):
        """Test that first frame is repeated."""
        encoder = QREncoder(small_file, first_frame_duration=3)
        output = BytesIO()

        encoder.encode_to_stream(output)

        data = output.getvalue()
        # With duration=3 and 1 chunk, should have ~4 PNG images
        # (3 for first frame + 1 for actual frame)
        # Count PNG signatures
        png_count = data.count(b'\x89PNG\r\n\x1a\n')
        assert png_count >= 3

    def test_encode_binary_file(self, tmp_path):
        """Test encoding binary file."""
        binary_file = tmp_path / "test.bin"
        binary_file.write_bytes(bytes(range(256)))

        encoder = QREncoder(str(binary_file))
        output = BytesIO()

        encoder.encode_to_stream(output)

        data = output.getvalue()
        assert len(data) > 0

    def test_chunk_size_affects_total_chunks(self, test_file):
        """Test that chunk size affects number of chunks."""
        encoder_large_chunks = QREncoder(test_file, chunk_size=1000)
        output1 = BytesIO()
        encoder_large_chunks.encode_to_stream(output1)
        stats1 = encoder_large_chunks.get_stats()

        encoder_small_chunks = QREncoder(test_file, chunk_size=100)
        output2 = BytesIO()
        encoder_small_chunks.encode_to_stream(output2)
        stats2 = encoder_small_chunks.get_stats()

        # Smaller chunks should result in more total chunks
        assert stats2["total_chunks"] > stats1["total_chunks"]

    def test_qr_version_consistency(self, test_file):
        """Test that QR version is determined correctly."""
        encoder = QREncoder(test_file)
        output = BytesIO()

        encoder.encode_to_stream(output)

        stats = encoder.get_stats()
        # QR version should be a positive integer
        assert stats["qr_version"] is not None
        assert isinstance(stats["qr_version"], int)
        assert stats["qr_version"] > 0

    def test_encode_empty_file(self, tmp_path):
        """Test encoding an empty file."""
        empty_file = tmp_path / "empty.txt"
        empty_file.write_text("")

        encoder = QREncoder(str(empty_file))
        output = BytesIO()

        # Should still work, producing at least one QR code
        encoder.encode_to_stream(output)

        data = output.getvalue()
        assert len(data) > 0
