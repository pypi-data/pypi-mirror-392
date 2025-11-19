"""Tests for keyboard sender module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from airgap_transfer.keyboard import KeyboardTransfer
from airgap_transfer.utils import DEFAULT_CHAR_DELAY, DEFAULT_LINE_DELAY


@pytest.fixture
def test_file(tmp_path):
    """Create a temporary test file."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello, World!\nTest content.")
    return str(test_file)


@pytest.fixture
def small_binary_file(tmp_path):
    """Create a small binary test file."""
    test_file = tmp_path / "test.bin"
    test_file.write_bytes(b"\x00\x01\x02\x03\x04\x05")
    return str(test_file)


class TestKeyboardTransfer:
    """Test cases for KeyboardTransfer class."""

    def test_init_with_defaults(self, test_file):
        """Test initialization with default parameters."""
        transfer = KeyboardTransfer(test_file)

        assert transfer.file_path == Path(test_file)
        assert transfer.char_delay == DEFAULT_CHAR_DELAY
        assert transfer.line_delay == DEFAULT_LINE_DELAY
        assert transfer.output_path == Path(test_file).name

    def test_init_with_custom_output(self, test_file):
        """Test initialization with custom output path."""
        output = "/tmp/output.txt"
        transfer = KeyboardTransfer(test_file, output_path=output)

        assert transfer.output_path == output

    def test_init_with_custom_delays(self, test_file):
        """Test initialization with custom delays."""
        char_delay = 0.01
        line_delay = 0.05
        transfer = KeyboardTransfer(
            test_file,
            char_delay=char_delay,
            line_delay=line_delay
        )

        assert transfer.char_delay == char_delay
        assert transfer.line_delay == line_delay

    def test_init_file_not_found(self):
        """Test initialization with non-existent file."""
        with pytest.raises(FileNotFoundError):
            KeyboardTransfer("/nonexistent/file.txt")

    def test_generate_script(self, test_file):
        """Test bash script generation."""
        transfer = KeyboardTransfer(test_file)
        script = transfer.generate_script()

        # Check script contains key elements
        assert "#!/bin/bash" in script
        assert "base64 -d" in script
        assert "sha256sum" in script or "shasum" in script
        assert transfer.output_path in script

    def test_generate_script_with_binary_file(self, small_binary_file):
        """Test script generation with binary file."""
        transfer = KeyboardTransfer(small_binary_file)
        script = transfer.generate_script()

        assert "#!/bin/bash" in script
        assert len(script) > 100  # Script should have content

    def test_apply_speed_preset_fast(self, test_file):
        """Test applying fast speed preset."""
        transfer = KeyboardTransfer(test_file)
        transfer.apply_speed_preset("fast")

        assert transfer.char_delay == 0.002
        assert transfer.line_delay == 0.01

    def test_apply_speed_preset_slow(self, test_file):
        """Test applying slow speed preset."""
        transfer = KeyboardTransfer(test_file)
        transfer.apply_speed_preset("slow")

        assert transfer.char_delay == 0.01
        assert transfer.line_delay == 0.05

    def test_apply_speed_preset_normal(self, test_file):
        """Test applying normal speed preset."""
        transfer = KeyboardTransfer(test_file)
        transfer.apply_speed_preset("normal")

        assert transfer.char_delay == 0.005
        assert transfer.line_delay == 0.03

    def test_apply_speed_preset_invalid(self, test_file):
        """Test applying invalid speed preset."""
        transfer = KeyboardTransfer(test_file)
        with pytest.raises(ValueError):
            transfer.apply_speed_preset("invalid")

    @patch('airgap_transfer.keyboard.sender._lazy_import_pynput')
    def test_send_with_mock(self, mock_import, test_file):
        """Test send method with mocked keyboard controller."""
        # Mock pynput
        mock_controller = MagicMock()
        mock_key = MagicMock()
        mock_import.return_value = (lambda: mock_controller, mock_key)

        transfer = KeyboardTransfer(test_file)

        # Mock time.sleep to speed up test
        with patch('time.sleep'):
            # Send without auto execute to avoid actual key presses
            transfer.send(countdown=0, auto_execute=False)

        # Verify controller was used
        assert mock_controller.type.called or mock_controller.press.called

    def test_get_stats(self, test_file):
        """Test getting transfer statistics."""
        transfer = KeyboardTransfer(test_file)
        stats = transfer.get_stats()

        assert "file_path" in stats
        assert "file_size" in stats
        assert "output_path" in stats
        assert "char_delay" in stats
        assert "line_delay" in stats
        assert stats["file_size"] > 0

    def test_script_contains_checksum(self, test_file):
        """Test that generated script contains checksum verification."""
        transfer = KeyboardTransfer(test_file)
        script = transfer.generate_script()

        # Should contain checksum calculation
        assert "sha256sum" in script or "shasum" in script
        # Should contain expected checksum value
        assert len(script) > 200  # Checksum adds significant length

    def test_multiple_transfers_same_file(self, test_file):
        """Test creating multiple transfers from the same file."""
        transfer1 = KeyboardTransfer(test_file, output_path="/tmp/out1.txt")
        transfer2 = KeyboardTransfer(test_file, output_path="/tmp/out2.txt")

        script1 = transfer1.generate_script()
        script2 = transfer2.generate_script()

        # Scripts should be different due to different output paths
        assert script1 != script2
        assert "/tmp/out1.txt" in script1
        assert "/tmp/out2.txt" in script2
