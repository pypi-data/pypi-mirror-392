"""Encoding utilities for data transformation."""

import base64
from typing import Union


def encode_base64(data: bytes) -> str:
    """
    Encode binary data to base64 string.

    Args:
        data: Binary data to encode

    Returns:
        Base64 encoded string
    """
    return base64.b64encode(data).decode('ascii')


def decode_base64(encoded: str) -> bytes:
    """
    Decode base64 string to binary data.

    Args:
        encoded: Base64 encoded string

    Returns:
        Decoded binary data
    """
    return base64.b64decode(encoded)


def split_into_chunks(data: str, chunk_size: int) -> list[str]:
    """
    Split string into fixed-size chunks.

    Args:
        data: String to split
        chunk_size: Size of each chunk

    Returns:
        List of string chunks
    """
    return [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]


def split_into_lines(data: str, line_length: int = 76) -> list[str]:
    """
    Split string into lines of specified length.

    Args:
        data: String to split
        line_length: Maximum length of each line (default: 76, standard for base64)

    Returns:
        List of lines
    """
    return split_into_chunks(data, line_length)
