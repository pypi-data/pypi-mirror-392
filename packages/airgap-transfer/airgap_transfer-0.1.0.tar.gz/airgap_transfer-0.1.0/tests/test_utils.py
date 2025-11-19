"""Tests for utility functions."""

import pytest
from pathlib import Path

from airgap_transfer.utils import (
    encode_base64,
    decode_base64,
    split_into_chunks,
    split_into_lines,
    calculate_file_checksum,
)


class TestEncodingUtils:
    """Test encoding utility functions."""

    def test_encode_base64(self):
        """Test base64 encoding."""
        data = b"Hello, World!"
        encoded = encode_base64(data)

        assert isinstance(encoded, str)
        assert len(encoded) > 0
        # Base64 only contains valid characters
        assert all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=" for c in encoded)

    def test_decode_base64(self):
        """Test base64 decoding."""
        original = b"Hello, World!"
        encoded = encode_base64(original)
        decoded = decode_base64(encoded)

        assert decoded == original

    def test_encode_decode_roundtrip(self):
        """Test encode/decode roundtrip."""
        test_data = [
            b"",
            b"A",
            b"Hello",
            b"Hello, World!",
            bytes(range(256)),
        ]

        for data in test_data:
            encoded = encode_base64(data)
            decoded = decode_base64(encoded)
            assert decoded == data

    def test_encode_empty_bytes(self):
        """Test encoding empty bytes."""
        encoded = encode_base64(b"")
        assert encoded == ""

    def test_decode_empty_string(self):
        """Test decoding empty string."""
        decoded = decode_base64("")
        assert decoded == b""


class TestChunkingUtils:
    """Test chunking utility functions."""

    def test_split_into_chunks(self):
        """Test splitting string into chunks."""
        data = "ABCDEFGHIJ"
        chunks = split_into_chunks(data, 3)

        assert chunks == ["ABC", "DEF", "GHI", "J"]

    def test_split_into_chunks_exact_fit(self):
        """Test chunking with exact fit."""
        data = "ABCDEF"
        chunks = split_into_chunks(data, 3)

        assert chunks == ["ABC", "DEF"]

    def test_split_into_chunks_single_char(self):
        """Test chunking with single character chunks."""
        data = "ABC"
        chunks = split_into_chunks(data, 1)

        assert chunks == ["A", "B", "C"]

    def test_split_into_chunks_larger_than_data(self):
        """Test chunking with chunk size larger than data."""
        data = "ABC"
        chunks = split_into_chunks(data, 10)

        assert chunks == ["ABC"]

    def test_split_into_chunks_empty_string(self):
        """Test chunking empty string."""
        chunks = split_into_chunks("", 3)

        assert chunks == []

    def test_split_into_lines(self):
        """Test splitting into lines."""
        data = "A" * 200
        lines = split_into_lines(data, 76)

        assert len(lines) == 3
        assert len(lines[0]) == 76
        assert len(lines[1]) == 76
        assert len(lines[2]) == 48

    def test_split_into_lines_default(self):
        """Test split_into_lines with default line length."""
        data = "A" * 100
        lines = split_into_lines(data)

        # Default is 76
        assert all(len(line) <= 76 for line in lines)


class TestChecksumUtils:
    """Test checksum utility functions."""

    def test_calculate_file_checksum(self, tmp_path):
        """Test calculating file checksum."""
        test_file = tmp_path / "test.txt"
        test_file.write_bytes(b"Hello, World!")

        checksum = calculate_file_checksum(str(test_file))

        assert isinstance(checksum, str)
        assert len(checksum) == 64  # SHA256 produces 64 hex characters

    def test_calculate_file_checksum_consistency(self, tmp_path):
        """Test that same file produces same checksum."""
        test_file = tmp_path / "test.txt"
        test_file.write_bytes(b"Hello, World!")

        checksum1 = calculate_file_checksum(str(test_file))
        checksum2 = calculate_file_checksum(str(test_file))

        assert checksum1 == checksum2

    def test_calculate_file_checksum_different_files(self, tmp_path):
        """Test that different files produce different checksums."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"

        file1.write_bytes(b"Content 1")
        file2.write_bytes(b"Content 2")

        checksum1 = calculate_file_checksum(str(file1))
        checksum2 = calculate_file_checksum(str(file2))

        assert checksum1 != checksum2

    def test_calculate_file_checksum_empty_file(self, tmp_path):
        """Test checksum of empty file."""
        empty_file = tmp_path / "empty.txt"
        empty_file.write_bytes(b"")

        checksum = calculate_file_checksum(str(empty_file))

        # Empty file should still have a valid checksum
        assert isinstance(checksum, str)
        assert len(checksum) == 64

    def test_calculate_file_checksum_large_file(self, tmp_path):
        """Test checksum of larger file."""
        large_file = tmp_path / "large.bin"
        large_file.write_bytes(b"X" * 10000)

        checksum = calculate_file_checksum(str(large_file))

        assert isinstance(checksum, str)
        assert len(checksum) == 64

    def test_calculate_file_checksum_not_found(self):
        """Test checksum with non-existent file."""
        with pytest.raises(FileNotFoundError):
            calculate_file_checksum("/nonexistent/file.txt")


class TestConstants:
    """Test that constants are defined."""

    def test_default_char_delay_exists(self):
        """Test DEFAULT_CHAR_DELAY constant exists."""
        from airgap_transfer.utils import DEFAULT_CHAR_DELAY

        assert isinstance(DEFAULT_CHAR_DELAY, float)
        assert DEFAULT_CHAR_DELAY > 0

    def test_default_line_delay_exists(self):
        """Test DEFAULT_LINE_DELAY constant exists."""
        from airgap_transfer.utils import DEFAULT_LINE_DELAY

        assert isinstance(DEFAULT_LINE_DELAY, float)
        assert DEFAULT_LINE_DELAY > 0

    def test_default_countdown_exists(self):
        """Test DEFAULT_COUNTDOWN constant exists."""
        from airgap_transfer.utils import DEFAULT_COUNTDOWN

        assert isinstance(DEFAULT_COUNTDOWN, int)
        assert DEFAULT_COUNTDOWN > 0

    def test_speed_presets_exist(self):
        """Test SPEED_PRESETS constant exists."""
        from airgap_transfer.utils import SPEED_PRESETS

        assert isinstance(SPEED_PRESETS, dict)
        assert "fast" in SPEED_PRESETS
        assert "normal" in SPEED_PRESETS
        assert "slow" in SPEED_PRESETS

    def test_qr_constants_exist(self):
        """Test QR-related constants exist."""
        from airgap_transfer.utils import (
            DEFAULT_QR_CHUNK_SIZE,
            DEFAULT_QR_BOX_SIZE,
            DEFAULT_QR_BORDER,
        )

        assert isinstance(DEFAULT_QR_CHUNK_SIZE, int)
        assert isinstance(DEFAULT_QR_BOX_SIZE, int)
        assert isinstance(DEFAULT_QR_BORDER, int)
