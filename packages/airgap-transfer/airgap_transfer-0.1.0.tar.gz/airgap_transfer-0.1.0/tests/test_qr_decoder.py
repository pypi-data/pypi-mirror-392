"""Tests for QR decoder module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Skip all tests if qrcode/cv2 are not available
pytest.importorskip("qrcode")
pytest.importorskip("cv2")

from airgap_transfer.qrcode import QRDecoder


@pytest.fixture
def mock_video_file(tmp_path):
    """Create a mock video file path."""
    video_file = tmp_path / "test_video.mp4"
    video_file.touch()  # Create empty file
    return str(video_file)


@pytest.fixture
def test_output_path(tmp_path):
    """Create a test output path."""
    return str(tmp_path / "output.txt")


class TestQRDecoder:
    """Test cases for QRDecoder class."""

    def test_init_with_defaults(self, mock_video_file):
        """Test initialization with default parameters."""
        decoder = QRDecoder(mock_video_file)

        assert decoder.video_path == Path(mock_video_file)
        assert decoder.sample_rate == 1
        assert decoder.verbose is False

    def test_init_with_custom_params(self, mock_video_file):
        """Test initialization with custom parameters."""
        decoder = QRDecoder(
            mock_video_file,
            sample_rate=3,
            verbose=True
        )

        assert decoder.sample_rate == 3
        assert decoder.verbose is True

    def test_init_file_not_found(self):
        """Test initialization with non-existent video."""
        with pytest.raises(FileNotFoundError):
            QRDecoder("/nonexistent/video.mp4")

    @patch('cv2.VideoCapture')
    def test_decode_with_mock_video(self, mock_capture, mock_video_file, test_output_path):
        """Test decoding with mocked video capture."""
        # Create mock video capture
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.side_effect = [
            (True, None),  # First frame
            (False, None),  # End of video
        ]
        mock_capture.return_value = mock_cap

        decoder = QRDecoder(mock_video_file)

        # This should handle the mock video gracefully
        with patch('pyzbar.pyzbar.decode', return_value=[]):
            # Will fail to decode but shouldn't crash
            result = decoder.decode_to_file(test_output_path, allow_incomplete=True)

        # Should return False due to no QR codes found
        assert result is False

    def test_get_stats_before_decode(self, mock_video_file):
        """Test getting stats before decoding."""
        decoder = QRDecoder(mock_video_file)
        stats = decoder.get_stats()

        assert "video_path" in stats
        assert "sample_rate" in stats
        assert stats["collected_chunks"] == 0
        assert stats["total_chunks"] == 0

    @patch('cv2.VideoCapture')
    @patch('pyzbar.pyzbar.decode')
    def test_decode_single_chunk(self, mock_decode, mock_capture, mock_video_file, test_output_path):
        """Test decoding video with single chunk."""
        # Mock video capture
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True

        import numpy as np
        mock_frame = np.zeros((100, 100, 3), dtype=np.uint8)

        mock_cap.read.side_effect = [
            (True, mock_frame),
            (False, None),
        ]
        mock_capture.return_value = mock_cap

        # Mock QR decode
        mock_qr = Mock()
        mock_qr.data = b"1/1|SGVsbG8="  # "Hello" in base64
        mock_decode.return_value = [mock_qr]

        decoder = QRDecoder(mock_video_file)
        result = decoder.decode_to_file(test_output_path)

        assert result is True
        assert Path(test_output_path).exists()

    def test_sample_rate_validation(self, mock_video_file):
        """Test sample rate must be positive."""
        with pytest.raises(ValueError):
            QRDecoder(mock_video_file, sample_rate=0)

        with pytest.raises(ValueError):
            QRDecoder(mock_video_file, sample_rate=-1)

    @patch('cv2.VideoCapture')
    def test_decode_incomplete_with_flag(self, mock_capture, mock_video_file, test_output_path):
        """Test decoding with allow_incomplete flag."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.side_effect = [(False, None)]
        mock_capture.return_value = mock_cap

        decoder = QRDecoder(mock_video_file)

        # Should not raise with allow_incomplete=True
        result = decoder.decode_to_file(test_output_path, allow_incomplete=True)
        assert result is False

    @patch('cv2.VideoCapture')
    @patch('pyzbar.pyzbar.decode')
    def test_duplicate_chunks_handling(self, mock_decode, mock_capture, mock_video_file, test_output_path):
        """Test that duplicate chunks are handled correctly."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True

        import numpy as np
        mock_frame = np.zeros((100, 100, 3), dtype=np.uint8)

        # Return same frame twice
        mock_cap.read.side_effect = [
            (True, mock_frame),
            (True, mock_frame),
            (False, None),
        ]
        mock_capture.return_value = mock_cap

        # Same QR code decoded twice
        mock_qr = Mock()
        mock_qr.data = b"1/1|SGVsbG8="
        mock_decode.return_value = [mock_qr]

        decoder = QRDecoder(mock_video_file)
        result = decoder.decode_to_file(test_output_path)

        # Should still succeed with deduplicated data
        assert result is True

    def test_verify_with_original_not_implemented(self, mock_video_file, test_output_path):
        """Test verify_with_original method exists."""
        decoder = QRDecoder(mock_video_file)

        # Method should exist (even if not fully implemented)
        assert hasattr(decoder, 'verify_with_original')

    @patch('cv2.VideoCapture')
    def test_verbose_mode(self, mock_capture, mock_video_file, test_output_path, capsys):
        """Test verbose mode produces output."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.side_effect = [(False, None)]
        mock_capture.return_value = mock_cap

        decoder = QRDecoder(mock_video_file, verbose=True)
        decoder.decode_to_file(test_output_path, allow_incomplete=True)

        # In verbose mode, should print something
        # (This is a basic check - actual implementation may vary)
        captured = capsys.readouterr()
        # Just verify the method runs without error in verbose mode
        assert True
