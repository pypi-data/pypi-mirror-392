"""A Python module for the Syside license checker."""

import importlib.metadata
from syside_license._syside_license_core import check

try:
    __version__ = importlib.metadata.version("syside_license")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"

__all__ = ["check"]
