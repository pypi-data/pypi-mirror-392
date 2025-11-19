"""Tests for CLI commands."""

import pytest
from unittest.mock import patch, MagicMock
import sys
from io import StringIO

from airgap_transfer.cli import main


@pytest.fixture
def test_file(tmp_path):
    """Create a temporary test file."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("CLI test content")
    return str(test_file)


class TestCLIMain:
    """Test cases for main CLI entry point."""

    def test_main_no_args(self, capsys):
        """Test main with no arguments shows help."""
        with pytest.raises(SystemExit):
            main.main([])

    def test_main_help(self, capsys):
        """Test main with --help."""
        with pytest.raises(SystemExit) as exc_info:
            main.main(["--help"])

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "airgap" in captured.out.lower()

    def test_main_version(self, capsys):
        """Test main with --version."""
        with pytest.raises(SystemExit) as exc_info:
            main.main(["--version"])

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "0.1.0" in captured.out or "version" in captured.out.lower()


class TestSendCommand:
    """Test cases for 'send' command."""

    def test_send_help(self, capsys):
        """Test send command help."""
        with pytest.raises(SystemExit) as exc_info:
            main.main(["send", "--help"])

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "send" in captured.out.lower()

    @patch('airgap_transfer.keyboard.sender.KeyboardTransfer.send')
    def test_send_basic(self, mock_send, test_file):
        """Test basic send command."""
        result = main.main(["send", test_file])

        # Should call send method
        mock_send.assert_called_once()
        assert result == 0

    @patch('airgap_transfer.keyboard.sender.KeyboardTransfer.send')
    def test_send_with_countdown(self, mock_send, test_file):
        """Test send with custom countdown."""
        result = main.main(["send", test_file, "--countdown", "10"])

        mock_send.assert_called_once()
        # Check countdown was passed
        call_kwargs = mock_send.call_args[1]
        assert call_kwargs.get("countdown") == 10
        assert result == 0

    @patch('airgap_transfer.keyboard.sender.KeyboardTransfer.send')
    def test_send_with_output(self, mock_send, test_file):
        """Test send with output path."""
        result = main.main(["send", test_file, "--output", "/tmp/output.txt"])

        assert result == 0

    def test_send_file_not_found(self):
        """Test send with non-existent file."""
        result = main.main(["send", "/nonexistent/file.txt"])

        # Should return non-zero exit code
        assert result != 0


class TestQREncodeCommand:
    """Test cases for 'qr-encode' command."""

    def test_qr_encode_help(self, capsys):
        """Test qr-encode command help."""
        with pytest.raises(SystemExit) as exc_info:
            main.main(["qr-encode", "--help"])

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "qr-encode" in captured.out.lower() or "encode" in captured.out.lower()

    @patch('airgap_transfer.qrcode.encoder.QREncoder.encode_to_stream')
    def test_qr_encode_basic(self, mock_encode, test_file):
        """Test basic qr-encode command."""
        result = main.main(["qr-encode", test_file])

        mock_encode.assert_called_once()
        assert result == 0

    def test_qr_encode_file_not_found(self):
        """Test qr-encode with non-existent file."""
        result = main.main(["qr-encode", "/nonexistent/file.txt"])

        assert result != 0


class TestQRDecodeCommand:
    """Test cases for 'qr-decode' command."""

    def test_qr_decode_help(self, capsys):
        """Test qr-decode command help."""
        with pytest.raises(SystemExit) as exc_info:
            main.main(["qr-decode", "--help"])

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "qr-decode" in captured.out.lower() or "decode" in captured.out.lower()

    @patch('airgap_transfer.qrcode.decoder.QRDecoder.decode_to_file')
    def test_qr_decode_basic(self, mock_decode, test_file, tmp_path):
        """Test basic qr-decode command."""
        mock_decode.return_value = True

        output_file = str(tmp_path / "output.txt")
        result = main.main(["qr-decode", test_file, output_file])

        mock_decode.assert_called_once()
        assert result == 0

    def test_qr_decode_missing_args(self):
        """Test qr-decode with missing arguments."""
        with pytest.raises(SystemExit):
            main.main(["qr-decode"])


class TestInstallCommand:
    """Test cases for 'install' command."""

    def test_install_help(self, capsys):
        """Test install command help."""
        with pytest.raises(SystemExit) as exc_info:
            main.main(["install", "--help"])

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "install" in captured.out.lower()

    def test_install_show(self, capsys):
        """Test install --show command."""
        result = main.main(["install", "--show"])

        captured = capsys.readouterr()
        assert "Bundle Information" in captured.out or "bundle" in captured.out.lower()
        assert result == 0

    @patch('airgap_transfer.installer.packager.SenderPackager.generate')
    def test_install_generate(self, mock_generate, tmp_path, capsys):
        """Test install --generate command."""
        mock_generate.return_value = tmp_path

        result = main.main(["install", "--generate", "--output", str(tmp_path)])

        mock_generate.assert_called_once()
        assert result == 0

    @patch('airgap_transfer.installer.packager.SenderPackager.generate_standalone')
    def test_install_generate_standalone(self, mock_standalone, tmp_path, capsys):
        """Test install --generate --standalone command."""
        output_file = tmp_path / "standalone.py"
        mock_standalone.return_value = output_file

        result = main.main([
            "install",
            "--generate",
            "--standalone",
            "--output",
            str(output_file)
        ])

        mock_standalone.assert_called_once()
        assert result == 0

    def test_install_no_action(self, capsys):
        """Test install with no action specified."""
        result = main.main(["install"])

        captured = capsys.readouterr()
        assert "No action specified" in captured.out or result != 0


class TestUtilityFunctions:
    """Test utility functions in CLI."""

    def test_import_main_module(self):
        """Test that main module can be imported."""
        from airgap_transfer.cli import main as cli_main

        assert hasattr(cli_main, "main")
        assert callable(cli_main.main)

    def test_all_subcommands_registered(self):
        """Test that all subcommands are registered."""
        # This is a basic check that subcommands exist
        with pytest.raises(SystemExit):
            main.main(["--help"])

        # If we get here without import errors, subcommands are registered


class TestErrorHandling:
    """Test error handling in CLI."""

    def test_invalid_subcommand(self, capsys):
        """Test invalid subcommand."""
        with pytest.raises(SystemExit) as exc_info:
            main.main(["invalid-command"])

        assert exc_info.value.code != 0

    @patch('airgap_transfer.keyboard.sender.KeyboardTransfer.send')
    def test_keyboard_transfer_error(self, mock_send, test_file, capsys):
        """Test handling of keyboard transfer errors."""
        mock_send.side_effect = Exception("Transfer failed")

        result = main.main(["send", test_file])

        # Should handle error gracefully
        assert result != 0

    @patch('airgap_transfer.installer.packager.SenderPackager.generate')
    def test_installer_error(self, mock_generate, capsys):
        """Test handling of installer errors."""
        mock_generate.side_effect = Exception("Generation failed")

        result = main.main(["install", "--generate"])

        assert result != 0
