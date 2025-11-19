"""Checksum utilities for file verification."""

import hashlib
from pathlib import Path
from typing import Union


def calculate_sha256(data: bytes) -> str:
    """
    Calculate SHA256 checksum of data.

    Args:
        data: Binary data to hash

    Returns:
        Hexadecimal SHA256 hash string
    """
    return hashlib.sha256(data).hexdigest()


def calculate_file_checksum(file_path: Union[str, Path]) -> str:
    """
    Calculate SHA256 checksum of a file.

    Args:
        file_path: Path to the file

    Returns:
        Hexadecimal SHA256 hash string
    """
    file_path = Path(file_path)
    with open(file_path, 'rb') as f:
        return calculate_sha256(f.read())


def verify_checksum(data: bytes, expected_checksum: str) -> bool:
    """
    Verify data against expected checksum.

    Args:
        data: Binary data to verify
        expected_checksum: Expected SHA256 hash

    Returns:
        True if checksums match, False otherwise
    """
    actual = calculate_sha256(data)
    return actual.lower() == expected_checksum.lower()


def compare_files(file1: Union[str, Path], file2: Union[str, Path]) -> bool:
    """
    Compare two files using SHA256 checksums.

    Args:
        file1: Path to first file
        file2: Path to second file

    Returns:
        True if files are identical, False otherwise
    """
    hash1 = calculate_file_checksum(file1)
    hash2 = calculate_file_checksum(file2)
    return hash1 == hash2
