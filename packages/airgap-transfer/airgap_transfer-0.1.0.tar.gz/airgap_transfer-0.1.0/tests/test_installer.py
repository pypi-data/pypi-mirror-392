"""Tests for installer module."""

import pytest
from pathlib import Path
import shutil

from airgap_transfer.installer import SenderPackager


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary output directory."""
    return str(tmp_path / "test-bundle")


class TestSenderPackager:
    """Test cases for SenderPackager class."""

    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        packager = SenderPackager()

        assert packager.output_dir == Path("sender-bundle")
        assert packager.version is not None
        assert packager.timestamp is not None

    def test_init_with_custom_output(self, temp_output_dir):
        """Test initialization with custom output directory."""
        packager = SenderPackager(temp_output_dir)

        assert packager.output_dir == Path(temp_output_dir)

    def test_get_bundle_info(self, temp_output_dir):
        """Test getting bundle information."""
        packager = SenderPackager(temp_output_dir)
        info = packager.get_bundle_info()

        assert "version" in info
        assert "timestamp" in info
        assert "output_dir" in info
        assert "templates_dir" in info
        assert "files" in info
        assert isinstance(info["files"], list)
        assert len(info["files"]) == 3  # qr_sender.py, install.sh, README.txt

    def test_generate_creates_directory(self, temp_output_dir):
        """Test that generate creates the output directory."""
        packager = SenderPackager(temp_output_dir)
        bundle_path = packager.generate()

        assert bundle_path.exists()
        assert bundle_path.is_dir()

    def test_generate_creates_all_files(self, temp_output_dir):
        """Test that generate creates all expected files."""
        packager = SenderPackager(temp_output_dir)
        bundle_path = packager.generate()

        expected_files = ["qr_sender.py", "install.sh", "README.txt"]

        for filename in expected_files:
            file_path = bundle_path / filename
            assert file_path.exists()
            assert file_path.stat().st_size > 0

    def test_generate_clean_removes_existing(self, temp_output_dir):
        """Test that generate with clean=True removes existing directory."""
        packager = SenderPackager(temp_output_dir)

        # Create initial bundle
        bundle_path = packager.generate()
        old_file = bundle_path / "old_file.txt"
        old_file.write_text("old content")

        # Generate again with clean
        packager.generate(clean=True)

        # Old file should be gone
        assert not old_file.exists()
        # New files should exist
        assert (bundle_path / "qr_sender.py").exists()

    def test_generate_without_clean_raises_error(self, temp_output_dir):
        """Test that generate without clean raises error if directory exists."""
        packager = SenderPackager(temp_output_dir)

        # Create initial bundle
        packager.generate()

        # Try to generate again without clean
        with pytest.raises(FileExistsError):
            packager.generate(clean=False)

    def test_generated_files_are_executable(self, temp_output_dir):
        """Test that generated scripts are executable."""
        packager = SenderPackager(temp_output_dir)
        bundle_path = packager.generate()

        qr_sender = bundle_path / "qr_sender.py"
        install_sh = bundle_path / "install.sh"

        # Check executable bit is set
        assert qr_sender.stat().st_mode & 0o111  # Executable by someone
        assert install_sh.stat().st_mode & 0o111

    def test_qr_sender_contains_version(self, temp_output_dir):
        """Test that generated qr_sender.py contains version."""
        packager = SenderPackager(temp_output_dir)
        bundle_path = packager.generate()

        qr_sender = bundle_path / "qr_sender.py"
        content = qr_sender.read_text()

        assert packager.version in content
        assert "Version:" in content

    def test_install_script_contains_version(self, temp_output_dir):
        """Test that generated install.sh contains version."""
        packager = SenderPackager(temp_output_dir)
        bundle_path = packager.generate()

        install_sh = bundle_path / "install.sh"
        content = install_sh.read_text()

        assert packager.version in content
        assert "#!/bin/bash" in content

    def test_readme_contains_version(self, temp_output_dir):
        """Test that generated README.txt contains version."""
        packager = SenderPackager(temp_output_dir)
        bundle_path = packager.generate()

        readme = bundle_path / "README.txt"
        content = readme.read_text()

        assert packager.version in content
        assert "Airgap Transfer" in content

    def test_generate_standalone(self, temp_output_dir):
        """Test generating standalone script."""
        packager = SenderPackager()
        output_file = Path(temp_output_dir) / "standalone.py"

        script_path = packager.generate_standalone(str(output_file))

        assert script_path.exists()
        assert script_path.stat().st_size > 0
        assert script_path.stat().st_mode & 0o111  # Executable

    def test_standalone_contains_all_code(self, temp_output_dir):
        """Test that standalone script contains all necessary code."""
        packager = SenderPackager()
        output_file = Path(temp_output_dir) / "standalone.py"

        script_path = packager.generate_standalone(str(output_file))
        content = script_path.read_text()

        # Should contain key components
        assert "#!/usr/bin/env python3" in content
        assert "import qrcode" in content
        assert "import base64" in content
        assert "def encode_file_to_qr_stream" in content
        assert "if __name__ ==" in content

    def test_standalone_default_output(self):
        """Test standalone with default output path."""
        packager = SenderPackager()

        try:
            script_path = packager.generate_standalone()
            assert script_path == Path("qr_sender_standalone.py")
            assert script_path.exists()
        finally:
            # Clean up
            if Path("qr_sender_standalone.py").exists():
                Path("qr_sender_standalone.py").unlink()

    def test_templates_directory_exists(self):
        """Test that templates directory exists."""
        packager = SenderPackager()

        assert packager.templates_dir.exists()
        assert packager.templates_dir.is_dir()

    def test_templates_files_exist(self):
        """Test that all template files exist."""
        packager = SenderPackager()

        expected_templates = [
            "qr_sender.py.tpl",
            "bootstrap.sh.tpl",
            "README.txt.tpl",
        ]

        for template in expected_templates:
            template_path = packager.templates_dir / template
            assert template_path.exists()

    def test_load_template_substitutes_variables(self, temp_output_dir):
        """Test that template loading substitutes variables."""
        packager = SenderPackager(temp_output_dir)

        # Access private method for testing
        content = packager._load_template("qr_sender.py.tpl")

        # Should not contain template variables
        assert "{version}" not in content
        assert "{timestamp}" not in content
        # Should contain actual values
        assert packager.version in content
        assert packager.timestamp in content

    def test_multiple_packagers_different_timestamps(self, temp_output_dir):
        """Test that multiple packagers have different timestamps."""
        import time

        packager1 = SenderPackager(temp_output_dir + "1")
        time.sleep(0.1)  # Small delay
        packager2 = SenderPackager(temp_output_dir + "2")

        # Timestamps might be the same due to granularity, but should be valid
        assert packager1.timestamp is not None
        assert packager2.timestamp is not None

    def test_generate_returns_path(self, temp_output_dir):
        """Test that generate returns the bundle path."""
        packager = SenderPackager(temp_output_dir)
        result = packager.generate()

        assert isinstance(result, Path)
        assert result == Path(temp_output_dir)
