"""
Airgap Transfer - Bi-directional file transfer for air-gapped environments.

This package provides tools for transferring files to and from isolated
environments using keyboard input simulation and QR code video streams.
"""

from .__version__ import __version__, __author__, __license__

# Lazy imports to avoid dependency issues
__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "KeyboardTransfer",
    "QREncoder",
    "QRDecoder",
    "SenderPackager",
]


def __getattr__(name):
    """Lazy import modules to avoid requiring all dependencies."""
    if name == "KeyboardTransfer":
        from .keyboard import KeyboardTransfer
        return KeyboardTransfer
    elif name == "QREncoder":
        from .qrcode import QREncoder
        return QREncoder
    elif name == "QRDecoder":
        from .qrcode import QRDecoder
        return QRDecoder
    elif name == "SenderPackager":
        from .installer import SenderPackager
        return SenderPackager
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
