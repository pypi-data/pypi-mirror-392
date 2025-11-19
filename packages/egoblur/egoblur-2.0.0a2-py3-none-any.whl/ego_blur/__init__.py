"""
Public package interface for EgoBlur demos.

This package re-exports the most common classes used by downstream code and
provides a stable module name for the Python package that will be distributed
on PyPI.
"""

from gen2.script import ClassID, EgoblurDetector, main as gen2_main

__all__ = ["ClassID", "EgoblurDetector", "gen2_main"]

