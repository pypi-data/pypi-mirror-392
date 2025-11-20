"""Top-level package for NileRedQuant."""

from __future__ import annotations

try:
    from importlib.metadata import version, PackageNotFoundError  # Py>=3.8
except Exception:  # pragma: no cover
    version = None

    class PackageNotFoundError(Exception): ...


try:
    __version__ = version("nileredquant") if version else "0.0.0"
except PackageNotFoundError:
    __version__ = "0.0.0"

__author__ = """Mia Žganjar"""
__email__ = "zganjar.mia@gmail.com"

from . import analyse, qc, standard_curve, utils

__all__ = [
    "analyse",
    "qc",
    "standard_curve",
    "utils",
    "__version__",
]
