"""
Gen1 demo package exposing the original EgoBlur Gen1 demo script.

This module intentionally re-exports the ``main`` entry point so it can be
referenced directly by setuptools console scripts.
"""

from .script.demo_ego_blur_gen1 import main

__all__ = ["main"]

