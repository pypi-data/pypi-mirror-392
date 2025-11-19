"""
Installer module for generating standalone sender packages.

This module provides tools to create installation bundles that can be
transferred to air-gapped environments.
"""

from .packager import SenderPackager

__all__ = ["SenderPackager"]
