"""
Gen2 demo package exposing the EgoBlur Gen2 helpers.

Re-export the primary ``main`` entry point implemented in
``gen2.script.demo_ego_blur_gen2`` so that it can be used by console
scripts and other callers.
"""

from .script.demo_ego_blur_gen2 import main

__all__ = ["main"]

