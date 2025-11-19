"Expose Gen2 scripts and helpers as a package."

from .demo_ego_blur_gen2 import main
from .predictor import ClassID, EgoblurDetector

__all__ = ["ClassID", "EgoblurDetector", "main"]

