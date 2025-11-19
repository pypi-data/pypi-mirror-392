"""Pytest configuration and shared fixtures."""

import pytest
import sys
from pathlib import Path

# Add src to path for testing
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def fixtures_dir():
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def test_files_dir(fixtures_dir):
    """Return path to test files directory."""
    return fixtures_dir / "test_files"


@pytest.fixture
def sample_text_file(test_files_dir):
    """Return path to sample text file."""
    return test_files_dir / "test.txt"


@pytest.fixture
def sample_multiline_file(test_files_dir):
    """Return path to sample multiline text file."""
    return test_files_dir / "test_multiline.txt"


@pytest.fixture
def sample_small_binary(test_files_dir):
    """Return path to small binary file."""
    return test_files_dir / "test_small.bin"


@pytest.fixture
def sample_medium_binary(test_files_dir):
    """Return path to medium binary file."""
    return test_files_dir / "test_medium.bin"
